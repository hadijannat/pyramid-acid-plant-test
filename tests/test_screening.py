"""Tests for the Tier 0 screening.

Each quantity is compared, to 2 percent, with the value printed in section 2 of
research/09-recomputation.md. Where a row of 09 used an input that differs from the ledger's
value, the case replaces that input, so the comparison is still with a number 09 prints.
"""
import dataclasses
import json
import math

import pytest

from pyramid import ledger, screening


@pytest.fixture(scope="module")
def led() -> ledger.Ledger:
    """The ledger kept in the repository."""
    return ledger.load()


@pytest.fixture(scope="module")
def results(led) -> dict[str, screening.Result]:
    return screening.all_results(led)


def at(led, result_id, overrides):
    """One quantity's function at the ledger values, with some inputs replaced by those a row of 09 used."""
    inputs, fn = {row[0]: row[4:] for row in screening.QUANTITIES}[result_id]
    return fn({i: led.q(i) for i in inputs} | overrides)


def test_range_covers_every_corner_of_the_input_ranges():
    def q(id, value, low, high):
        return ledger.Quantity(id, value, "m", low, high, "test", False, "test")

    tiny = ledger.Ledger({"a": q("a", 10.0, 9.0, 12.0), "b": q("b", 4.0, 3.0, 5.0)}, {}, "")
    value, low, high = screening._evaluate(tiny, ("a", "b"), lambda v: v["a"] - v["b"])
    # The least difference pairs the low of a with the high of b. All-low gives 6 and all-high gives 7,
    # so taking only those two would miss both ends of the range.
    assert (value, low, high) == (6.0, 4.0, 9.0)


def test_kings_chamber_volume_is_a_described_result_with_a_range(results):
    r = results["t0.kc_volume"]
    assert r.value == pytest.approx(320.4, rel=0.02)  # 09 row 12
    assert r.low == pytest.approx(10.4676 * 5.2316 * 5.7887)  # every dimension at its low
    assert r.high == pytest.approx(10.4798 * 5.2398 * 5.9004)  # every dimension at its high
    assert (r.id, r.unit, r.inputs) == ("t0.kc_volume", "m3", ("kc.length", "kc.width", "kc.height"))
    assert r.label == "King's Chamber volume, floor to ceiling"
    assert r.formula == "V = length x width x height"


# Each case: (result id, inputs replaced to match the row of 09, the value 09 prints, in SI units).
STATICS_CASES = [
    ("t0.gg_volume", {}, 575.0),  # row 10: section 13.61 m2 x 42.38 m, less the Great Step
    ("t0.gallery_fill_pressure", {}, 0.798e6),  # row 17: 81.5 m of head
    ("t0.gallery_fill_pressure", {"dp.south_end.z": -30.4}, 0.802e6),  # row 17: from the chamber floor
    ("t0.piston_force_passage_end", {}, 1.010e6),  # row 18: Gallery full
    ("t0.piston_force_passage_end", {"gg.roof_top.z": 21.66}, 0.640e6),  # row 18: water at the Gallery's foot
    ("t0.piston_force_entrance", {}, 0.428e6),  # row 18
    ("t0.lifting_work", {}, 260e6),  # row 21: from pavement level
]


@pytest.mark.parametrize(("result_id", "overrides", "expected"), STATICS_CASES)
def test_volume_pressure_force_and_work_match_09(led, result_id, overrides, expected):
    assert at(led, result_id, overrides) == pytest.approx(expected, rel=0.02)


STROKE_AND_SUCTION_CASES = [
    ("t0.strokes_full_passage", {}, 4.32),  # row 20, Gallery only, three stroke definitions (conflict K6)
    ("t0.strokes_below_junction", {}, 5.90),
    ("t0.strokes_below_pavement", {}, 6.76),
    # row 22: a piston at the passage end breaks even with water at 19.9 m asl; the flood peak is 14 m asl
    ("t0.suction_margin", {}, 14.0 - 19.9),
    # 02 working W2: base at 58 m asl and a 17 m asl flood leave 11.0 m of lift against the 10.1 m limit
    ("t0.suction_margin", {"site.base_elevation_asl": 58.0, "hydro.ok_flood_peak_asl": 17.0}, 10.1 - 11.0),
]


@pytest.mark.parametrize(("result_id", "overrides", "expected"), STROKE_AND_SUCTION_CASES)
def test_stroke_counts_and_suction_margin_match_09(led, result_id, overrides, expected):
    assert at(led, result_id, overrides) == pytest.approx(expected, rel=0.02)


def test_suction_margin_stays_negative_over_the_whole_range(results):
    margin = results["t0.suction_margin"]
    assert margin.low == pytest.approx(-8.43, abs=0.02)  # base 62 m asl, flood 13.5 m asl
    assert margin.high == pytest.approx(-0.37, abs=0.02)  # base 58 m asl, flood 17.5 m asl: still short


FLOW_CASES = [
    # Row 23 prints 25 Pa for a one-hour drain, to two figures and from 570 m3. With the ledger's 573 m3 and
    # 1.204 kg/m3: v_n = (573 / 3600) / (0.0510 + 0.0483 sqrt(19 / 14.5)) = 1.50 m/s, and
    # 19 x 1.204 x 1.50^2 / 2 = 25.7 Pa.
    ("t0.shaft_draw_pressure", {}, 25.7),
    ("t0.shaft_draw_pressure", {"hydro.drain_time": 600.0}, 930.0),  # row 23: 0.93 kPa for a ten-minute drain
    ("t0.joint_leak_rate", {"hydro.joint_aperture": 0.0005}, 2.07),  # row 24: 0.5 mm joints
    ("t0.joint_leak_rate", {"hydro.joint_aperture": 0.0001}, 0.0166),  # row 24: 0.1 mm
    ("t0.joint_leak_rate", {"hydro.joint_aperture": 0.00005}, 0.00207),  # row 24: 0.05 mm
]


@pytest.mark.parametrize(("result_id", "overrides", "expected"), FLOW_CASES)
def test_shaft_air_flow_and_leak_off_match_09(led, result_id, overrides, expected):
    assert at(led, result_id, overrides) == pytest.approx(expected, rel=0.02)


GEOMETRY_AND_HYDRAULICS = [
    "t0.kc_volume", "t0.gg_volume", "t0.gallery_fill_pressure", "t0.piston_force_passage_end",
    "t0.piston_force_entrance", "t0.lifting_work", "t0.strokes_full_passage", "t0.strokes_below_junction",
    "t0.strokes_below_pavement", "t0.suction_margin", "t0.shaft_draw_pressure", "t0.joint_leak_rate",
]


def test_the_twelve_geometric_and_hydraulic_results_come_first_and_in_order(results):
    assert list(results)[:12] == GEOMETRY_AND_HYDRAULICS
    for r in results.values():
        assert math.isfinite(r.low) and math.isfinite(r.high), r.id
        assert r.low <= r.value <= r.high, r.id


YEAR = 3.156e7  # seconds

CHEMISTRY_CASES = [
    ("t0.so2_inventory", {}, 13320.0),  # row 26
    ("t0.so2_inventory", {"chem.temperature": 298.0}, 13100.0),  # row 26: at 298 K
    ("t0.acid_ceiling_sulfur", {}, 23.2),  # row 27: 0.0232 mol/L in 573 m3 of water
    ("t0.acid_ceiling_sulfur", {"gg.volume": 550.0}, 24.2),  # row 27: 0.0242 mol/L in 550 m3
    ("t0.acid_ceiling_oxygen", {}, 12.3),  # row 27: 0.0123 mol/L, the stricter ceiling
    ("t0.temperature_rise", {}, 1.82),  # row 28: in 573 m3
    ("t0.temperature_rise", {"gg.volume": 550.0}, 1.89),  # row 28: in 550 m3
    ("t0.oxygen_supply_time", {}, 2.7 * YEAR),  # row 33: full batch, the favourable transfer coefficient
    ("t0.gas_phase_lifetime", {}, 2.8e17),  # row 30
]


@pytest.mark.parametrize(("result_id", "overrides", "expected"), CHEMISTRY_CASES)
def test_chemistry_quantities_match_09(led, result_id, overrides, expected):
    assert at(led, result_id, overrides) == pytest.approx(expected, rel=0.02)


ELECTRICITY_CASES = [
    ("t0.lightning_strikes", {}, 0.12),  # row 41: 0.2 flashes per km2 per year on the apex-governed area
    ("t0.lightning_strikes", {"em.flash_density": 5e-8}, 0.03),  # row 41: 0.05 per km2 per year
    ("t0.lightning_strikes", {"em.flash_density": 1.0}, 0.608e6),  # row 41: the collection area itself, in m2
    ("t0.relaxation_limestone", {"em.limestone_resistivity": 300.0}, 18.6e-9),  # row 40
    ("t0.relaxation_limestone", {"em.limestone_resistivity": 1500.0}, 93.0e-9),  # row 40
    ("t0.relaxation_granite", {}, 5.3e-3),  # row 40: 1e-8 S/m
    ("t0.relaxation_granite", {"em.granite_conductivity": 1e-4}, 0.53e-6),  # row 40: 1e-4 S/m
    ("t0.relaxation_granite", {"em.granite_eps": 24.0}, 21e-3),  # row 40 note: low-frequency permittivity
    ("t0.skin_depth_resonance", {}, 12.9),  # 04 section 4.2, verification note: 500 ohm m at 0.90 MHz
    ("t0.skin_depth_resonance", {"em.limestone_resistivity": 300.0}, 9.7),  # row 39
    ("t0.skin_depth_resonance", {"em.limestone_resistivity": 1500.0}, 26.4),  # row 39
    ("t0.skin_depth_lightning", {}, 35.6),  # row 39: 100 kHz in 500 ohm m
    ("t0.skin_depth_lightning", {"em.lightning_frequency": 1e4}, 112.5),  # row 39: 10 kHz
]


@pytest.mark.parametrize(("result_id", "overrides", "expected"), ELECTRICITY_CASES)
def test_electrical_quantities_match_09(led, result_id, overrides, expected):
    assert at(led, result_id, overrides) == pytest.approx(expected, rel=0.02)


def test_the_ledger_holds_the_frequency_of_the_shaft_link(led):
    frequency = led.quantities["ac.link_frequency"]
    assert (frequency.value, frequency.unit, frequency.verified) == (13000.0, "Hz", False)
    assert "research/05-sonochemistry-acoustics.md" in frequency.source
    # S25 is the claim this frequency screens, and a tier 0 claim names the quantities its calculation reads
    assert "ac.link_frequency" in led.claims["S25"].depends_on


ACOUSTICS_CASES = [
    ("t0.piezo_displacement", {}, 1.40e-12),  # row 43: 1.40 pm
    ("t0.piezo_intensity", {}, 1.62e-11),  # row 43: 1.62e-15 W/cm2
    ("t0.leaf_sound_level", {}, 75.8),  # row 46: with 413 Pa s/m
    ("t0.leaf_sound_level", {"ac.air_impedance": 428.0, "ante.leaf_thickness": 0.40}, 76.1),  # row 46: as 05 has it
    ("t0.required_sound_level", {}, 189.4),  # row 47
    ("t0.slab_source_level", {}, 50.0),  # row 50: source level at 13 kHz
    ("t0.slab_source_level", {"ac.link_frequency": 40000.0}, 60.0),  # row 50: at 40 kHz
    ("t0.shaft_link_loss", {}, 102.0),  # row 50: wet link at 13 kHz through soft stone
    ("t0.shaft_link_loss", {"ac.soft_limestone_impedance": 1.3e7}, 118.0),  # row 50: through dense stone
    ("t0.shaft_link_loss", {"ac.absorption_13khz": 0.127}, 85.0),  # 05 section 4.5 note: warm, humid air
]


@pytest.mark.parametrize(("result_id", "overrides", "expected"), ACOUSTICS_CASES)
def test_piezoelectric_and_acoustic_quantities_match_09(led, result_id, overrides, expected):
    assert at(led, result_id, overrides) == pytest.approx(expected, rel=0.02)


VEIN_CASES = [
    ("t0.vein_contrast", {}, 2.75e5),  # row 44: 100 m link, 0.03 m2 section
    ("t0.vein_contrast", {"plateau.vein_leakage_length": 10.0}, 3.9e3),  # row 44: sensitivity cases
    ("t0.vein_contrast", {"plateau.vein_area": 0.3}, 3.2e4),
    ("t0.vein_contrast", {"plateau.vein_leakage_length": 500.0}, 5.7e6),
]


@pytest.mark.parametrize(("result_id", "overrides", "expected"), VEIN_CASES)
def test_vein_contrast_matches_09(led, result_id, overrides, expected):
    assert at(led, result_id, overrides) == pytest.approx(expected, rel=0.02)


def test_the_ledger_holds_the_boiling_point_of_water(led):
    boiling = led.quantities["chem.water_boiling_point"]
    assert (boiling.value, boiling.unit, boiling.verified) == (373.15, "K", False)
    assert "research/03-chemistry.md" in boiling.source
    # S21 is the claim this temperature screens, and a tier 0 claim names the quantities its calculation reads
    assert "chem.water_boiling_point" in led.claims["S21"].depends_on


ATM = 101325.0  # pascals in one atmosphere, the unit 09 prints row 36 in

DECIDING_CASES = [
    ("t0.ram_delivered_fraction", {}, 0.221),  # row 25: efficiency 0.6, fall 30 m, lift 81.5 m
    # 02 section 2.4: a 2 m fall and a 10 m lift at 70 percent deliver 14 percent
    (
        "t0.ram_delivered_fraction",
        {"hydro.ram_efficiency": 0.7, "dp.south_end.z": -2.0, "gg.roof_top.z": 8.0},
        0.14,
    ),
    ("t0.pit_clearance", {}, 25.4 - 14.0),  # row 22: the original pit bottom at 25.4 m asl, the flood peak at 14
    ("t0.pit_clearance", {"hydro.ok_flood_peak_asl": 17.0}, 8.4),  # 02 section 2.2: above the 17 m asl flood peak
    # row 28: 7.6 K if all the heat goes into the first quarter of a 550 m3 fill; 80 K lie between 20 C and boiling
    ("t0.boiling_margin", {"gg.volume": 550.0}, 80.0 - 7.6),
    ("t0.boiling_margin", {"hydro.claimed_strokes": 1.0}, 80.0 - 1.82),  # row 28: 1.82 K in the whole 573 m3
    # row 35: 39 percent at 03's rounded 0.024 mol/L, which is one King's Chamber of gas in 555 m3 of water
    ("t0.gypsum_saturation_loss", {"gg.volume": 555.0}, 0.39),
    # 03 C10: a tenth of the gas gives 0.0024 mol/L, and all of that acid is spent before gypsum saturates
    ("t0.gypsum_saturation_loss", {"gg.volume": 555.0, "kc.volume": 32.04}, 1.0),
    ("t0.hcl_partial_pressure", {}, 1.25e-7 * ATM),  # row 36: 0.05 mol/L H+ in 5 mol/L chloride
    # at 172 dB with the ledger's barrier, the 150.22 kJ/mol of the direct gas reaction (not a row of 09)
    ("t0.arrhenius_gain", {}, 2.21),
    ("t0.arrhenius_gain", {"ac.arrhenius_barrier": 100000.0}, 1.47),  # row 48: at 172 dB with 09's 100 kJ/mol
    ("t0.arrhenius_gain", {"ac.best_airborne_level": 76.0}, 1.0),  # row 48: a swing of 1.5e-4 K changes nothing
]


@pytest.mark.parametrize(("result_id", "overrides", "expected"), DECIDING_CASES)
def test_claim_deciding_quantities_match_09(led, result_id, overrides, expected):
    assert at(led, result_id, overrides) == pytest.approx(expected, rel=0.02)


ALL_IDS = GEOMETRY_AND_HYDRAULICS + [
    "t0.so2_inventory", "t0.acid_ceiling_sulfur", "t0.acid_ceiling_oxygen", "t0.temperature_rise",
    "t0.oxygen_supply_time", "t0.gas_phase_lifetime", "t0.lightning_strikes", "t0.relaxation_limestone",
    "t0.relaxation_granite", "t0.skin_depth_resonance", "t0.skin_depth_lightning", "t0.piezo_displacement",
    "t0.piezo_intensity", "t0.leaf_sound_level", "t0.required_sound_level", "t0.slab_source_level",
    "t0.shaft_link_loss", "t0.vein_contrast", "t0.ram_delivered_fraction", "t0.pit_clearance",
    "t0.boiling_margin", "t0.gypsum_saturation_loss", "t0.hcl_partial_pressure", "t0.arrhenius_gain",
]


def test_all_36_results_are_present_ordered_and_well_formed(led, results):
    assert list(results) == ALL_IDS
    assert len(results) == 36
    for r in results.values():
        assert math.isfinite(r.low) and math.isfinite(r.high), r.id
        assert r.low <= r.value <= r.high, r.id
        assert r.label and r.unit and r.formula, r.id
        assert "|" not in r.label + r.formula, r.id  # the table writer uses | to separate columns
        assert set(r.inputs) <= set(led.quantities), r.id


@pytest.fixture(scope="module")
def decided(led, results) -> dict[str, tuple[str, str]]:
    return screening.verdicts(led, results)


def with_results(led, results, **replaced):
    """Verdicts after replacing (value, low, high) of some results, named without their t0. prefix."""
    changed = dict(results)
    for name, (value, low, high) in replaced.items():
        changed[f"t0.{name}"] = dataclasses.replace(results[f"t0.{name}"], value=value, low=low, high=high)
    return screening.verdicts(led, changed)


# Each case: (claim, status, the deciding number with its unit as the basis must print it).
HYDRAULIC_VERDICTS = [
    ("S09", "conditional", "21.7 m"),  # 02 C4: true only if a reservoir is connected
    ("S10", "undefined", "1.01 MN"),  # 02 C5 and its list of undefined items: no actuator, no seal
    ("S11", "fail", "5.9 m"),  # 02 C7: contradicted, unchanged by the verification pass
    ("S12", "conditional", "4.3 strokes"),  # 02 C6: one narrow exception, the full-passage stroke
    ("S18", "conditional", "4.3 strokes"),
]


@pytest.mark.parametrize(("claim", "status", "number"), HYDRAULIC_VERDICTS)
def test_hydraulic_verdicts_follow_the_research(decided, claim, status, number):
    got_status, basis = decided[claim]
    assert got_status == status
    assert number in basis
    assert basis.endswith(".") and ". " not in basis  # one sentence


def test_every_claim_gets_a_verdict_and_a_claim_without_a_rule_keeps_its_status(led, decided):
    assert list(decided) == list(led.claims)
    assert len(decided) == 71
    for status, basis in decided.values():
        assert status in ledger.STATUSES
        assert basis.endswith(".")
    # E19 is reserved for the field solver (spec section 6), so the screening must not decide it.
    assert decided["E19"] == ("pending", "No Tier 0 rule; tested in piece 1.")


def test_hydraulic_rules_can_go_either_way(led, results):
    # A perched water table would leave a positive margin, and the suction step must then pass.
    assert with_results(led, results, suction_margin=(2.0, 1.0, 3.0))["S11"][0] == "pass"
    assert with_results(led, results, suction_margin=(-1.0, -2.0, 0.5))["S11"][0] == "conditional"
    # Near four strokes under every stroke definition passes; under none of them fails.
    near_four = {"strokes_below_junction": (4.5, 4.4, 4.6), "strokes_below_pavement": (4.8, 4.7, 4.9)}
    assert with_results(led, results, **near_four)["S12"][0] == "pass"
    assert with_results(led, results, strokes_full_passage=(6.0, 5.9, 6.1))["S18"][0] == "fail"


OTHER_VERDICTS = [
    ("S07", "fail", "76 dB"),  # 04 C6 and 05 C7: short by many orders of magnitude
    ("S16", "fail", "2.8e+17 s"),  # 03 C3: contradicted on rate and mechanism
    ("S20", "conditional", "2.7 to 28 years"),  # 03 C5 after verification: oxygen supply, not chemistry, limits
    ("S24", "fail", "1.8 K"),  # 03 C7: contradicted at the stated geometry
    ("S25", "fail", "-52 dB"),  # 05 C12: contradicted by the link budget
    ("S28", "conditional", "2.7e+05 times"),  # 07 C11 after verification: doubtful, not settled
    ("S29", "conditional", "2.7e+05 times"),  # 07 section 4.2 after verification: measurement needed
    ("S30", "undefined", "23 mol/m3"),  # 03 C14: no target strength or gas fraction stated
    ("S31", "undefined", "0.12 times per year"),  # criterion: no required rate stated
    ("E22", "fail", "5.3 ms"),  # 04 C5: contradicted on the function
    ("E38", "conditional", "2.7e+05 times"),
]


@pytest.mark.parametrize(("claim", "status", "number"), OTHER_VERDICTS)
def test_remaining_verdicts_follow_the_research(decided, claim, status, number):
    got_status, basis = decided[claim]
    assert got_status == status
    assert number in basis
    assert basis.endswith(".") and ". " not in basis  # one sentence


def test_remaining_rules_can_go_either_way(led, results):
    def status(claim, **replaced):
        return with_results(led, results, **replaced)[claim][0]

    assert status("S07", leaf_sound_level=(195.0, 191.0, 199.0)) == "pass"
    assert status("S07", leaf_sound_level=(150.0, 100.0, 195.0)) == "conditional"
    assert status("S16", gas_phase_lifetime=(3600.0, 3600.0, 3600.0)) == "pass"  # a one-hour lifetime
    assert status("S16", gas_phase_lifetime=(1e7, 1e7, 1e7)) == "conditional"  # 0.2 percent in six hours
    assert status("S20", oxygen_supply_time=(3600.0, 1800.0, 7200.0)) == "pass"
    assert status("S24", temperature_rise=(25.0, 22.0, 30.0)) == "pass"
    assert status("S24", temperature_rise=(4.0, 3.0, 6.0)) == "conditional"
    assert status("S25", shaft_link_loss=(30.0, 28.0, 32.0)) == "pass"
    assert status("S25", shaft_link_loss=(50.0, 45.0, 55.0)) == "conditional"
    assert status("S30", acid_ceiling_sulfur=(2.0, 1.0, 3.0)) == "fail"
    assert status("E22", relaxation_granite=(5.0, 2.0, 9.0)) == "pass"
    assert status("E22", relaxation_granite=(0.05, 0.01, 0.5)) == "conditional"
    assert status("E38", vein_contrast=(1e-6, 1e-6, 1e-6)) == "pass"  # any vein would do
    assert status("E38", vein_contrast=(5e6, 5e6, 5e6)) == "fail"  # beyond the best measured hematite


LAST_VERDICTS = [
    ("S21", "pass", "72.7 K"),  # 03 C6: nothing to boil over, with or without the step
    ("S27", "fail", "1.2e-07 atm"),  # 03 C12: contradicted for the gas, unchanged by the verification pass
    ("E14", "fail", "2022 m3"),  # 02 C13 and section 4.7: the chamber has no outfall
    ("E17", "fail", "11.4 m"),  # 02 C8 after verification: the wet fill shows no ancient link
    # the owner's decision of 2026-10-10: both barriers and both gains (05 C2 holds for liquids; 03 section 2b)
    (
        "E18",
        "conditional",
        "2.2 times if its barrier is the 150 kJ/mol of the direct gas reaction and 1.5 times if it is 100 kJ/mol",
    ),
    ("E29", "conditional", "41 percent"),  # 03 C10 after verification: depends on the state of the coat
]


@pytest.mark.parametrize(("claim", "status", "number"), LAST_VERDICTS)
def test_last_six_verdicts_follow_the_research(decided, claim, status, number):
    got_status, basis = decided[claim]
    assert got_status == status
    assert number in basis
    assert basis.endswith(".") and ". " not in basis  # one sentence


def test_every_tier_0_claim_has_a_rule(led):
    assert set(screening.RULES) == {claim.id for claim in led.claims.values() if claim.tier == 0}


def test_last_six_rules_can_go_either_way(led, results):
    def status(claim, **replaced):
        return with_results(led, results, **replaced)[claim][0]

    assert status("S21", boiling_margin=(-5.0, -20.0, 10.0)) == "conditional"
    assert status("S21", boiling_margin=(-30.0, -40.0, -20.0)) == "fail"
    assert status("S27", hcl_partial_pressure=(200.0, 150.0, 300.0)) == "pass"  # 1e-3 atm is 101 Pa
    assert status("S27", hcl_partial_pressure=(10.0, 0.5, 20.0)) == "conditional"  # 1e-5 atm is 1.01 Pa
    assert status("E14", ram_delivered_fraction=(0.9, 0.85, 0.95)) == "pass"  # one fill spills 109 m3 at most
    assert status("E14", ram_delivered_fraction=(0.6, 0.55, 0.7)) == "conditional"
    assert status("E17", pit_clearance=(-1.0, -2.0, -0.5)) == "pass"  # the pit ends below the water
    assert status("E17", pit_clearance=(1.0, -1.0, 3.0)) == "conditional"
    assert status("E18", arrhenius_gain=(2.5, 2.2, 3.0)) == "pass"
    assert status("E18", arrhenius_gain=(1.5, 1.4, 1.9)) == "fail"
    assert status("E29", gypsum_saturation_loss=(0.05, 0.02, 0.1)) == "pass"
    assert status("E29", gypsum_saturation_loss=(0.95, 0.9, 1.0)) == "fail"


def test_table_has_one_row_per_result(results):
    lines = screening.table_markdown(results).splitlines()
    assert lines[0] == "| Id | Quantity | Value | Low | High | Unit | Formula |"
    assert lines[1] == "|---|---|---|---|---|---|---|"
    assert len(lines) == 2 + len(results) == 38
    assert [line.split(" | ")[0] for line in lines[2:]] == [f"| {id}" for id in results]
    assert all(line.count("|") == 8 for line in lines)
    assert lines[4] == (
        "| t0.gallery_fill_pressure | Water pressure at the foot of the Descending Passage with the Gallery full "
        "| 7.98e+05 | 7.96e+05 | 8e+05 | Pa | p = rho g (z_gallery_roof - z_passage_end) |"
    )


def test_main_writes_the_table_the_json_and_the_manifest(tmp_path, monkeypatch, led):
    monkeypatch.setattr(screening, "REPO_ROOT", tmp_path)  # write under a temporary folder, not the repository
    screening.main()
    out = tmp_path / "results" / "tier0"
    assert sorted(path.name for path in out.iterdir()) == ["manifest.json", "tier0.json", "tier0.md"]

    text = (out / "tier0.md").read_text()
    assert "| t0.gallery_fill_pressure |" in text
    assert "| S11 | fail | A pump at the foot of the Descending Passage" in text
    assert "| E19 |" not in text  # only claims with a rule are listed

    payload = json.loads((out / "tier0.json").read_text())
    assert [result["id"] for result in payload["results"]] == ALL_IDS
    assert payload["results"][2]["value"] == pytest.approx(0.798e6, rel=0.02)
    assert payload["results"][2]["inputs"] == ["hydro.water_density", "gg.roof_top.z", "dp.south_end.z"]
    assert len(payload["verdicts"]) == 71
    assert payload["verdicts"]["S24"]["status"] == "fail"
    assert payload["verdicts"]["E19"] == {"status": "pending", "basis": "No Tier 0 rule; tested in piece 1."}

    manifest = json.loads((out / "manifest.json").read_text())
    assert (manifest["case"], manifest["ledger"]) == ("tier0", led.digest)
