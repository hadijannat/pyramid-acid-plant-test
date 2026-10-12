"""The chem results and the five verdict rules, each driven through the statuses it can return."""
import dataclasses

import pytest

from pyramid import chem, ledger, simkit, verdicts
from pyramid.chem import feed, transfer


@pytest.fixture(scope="module")
def led() -> ledger.Ledger:
    return ledger.load()


@pytest.fixture(scope="module")
def results(led) -> dict:
    return chem.results(led)


def altered(led, changes: dict[str, tuple[float, float, float]]):
    """The ledger with (value, low, high) of some quantities replaced."""
    quantities = dict(led.quantities)
    for id, (value, low, high) in changes.items():
        quantities[id] = dataclasses.replace(quantities[id], value=value, low=low, high=high)
    return dataclasses.replace(led, quantities=quantities)


def with_quantities(led, changes: dict[str, tuple[float, float, float]]):
    """Verdicts after replacing some ledger quantities and recomputing every result."""
    changed = altered(led, changes)
    return chem.verdicts(changed, chem.results(changed))


def fixed(value: float) -> tuple[float, float, float]:
    return value, value, value


def test_results_are_described_and_stay_within_their_corners(led, results):
    assert len(results) == len(chem.QUANTITIES)
    for id, label, unit, formula, inputs, fn in chem.QUANTITIES:
        r = results[id]
        assert id.startswith("chem.") and unit in ledger.UNITS and label and formula
        assert all(i in led.quantities for i in inputs), id
        assert r.low <= r.value <= r.high, id
        # Each quantity is monotone in each input, so no draw inside the ranges may leave the corners.
        for draw in simkit.sample(led, inputs, 200, seed=3):
            assert r.low * (1 - 1e-12) <= fn(draw) <= r.high * (1 + 1e-12), id


def test_headline_numbers(results):
    def value(id):
        return results[id].value

    assert value("chem.capture_share") == pytest.approx(0.866, abs=0.001)
    assert value("chem.capture_equilibrium") == pytest.approx(0.982, abs=0.001)
    assert value("chem.least_air") == pytest.approx(1 - 320.4 / 573.0)
    assert value("chem.forced_back_least_air") == pytest.approx(0.333, abs=0.001)
    assert value("chem.forced_back_stoichiometric") == pytest.approx(0.541, abs=0.001)
    assert results["chem.forced_back_least_air"].low == pytest.approx(0.289, abs=0.001)
    assert value("chem.gypsum_layer_per_cycle") == pytest.approx(3.67e-6, rel=0.005)
    assert value("chem.wall_loss_ten_cycles") == pytest.approx(10 * value("chem.wall_loss_per_cycle"))
    # A still fill against the layer a bare wall grows in one cycle: 3.161 times at equal dwell, so 3.161 x
    # sqrt(0.0417) = 0.646 at the ledger's dwell, its drain time over its cycle time; at the favourable corner 2.277
    # times at equal dwell, so 2.277 x sqrt(1.9e-5) = 0.0099 for the shortest dwell taken. It strips that layer from
    # a dwell of 1 / 3.161^2 = 0.100 (1 / 2.277^2 = 0.193 at most), whatever dwell the ledger holds.
    assert value("chem.still_margin") == pytest.approx(3.1614 * 0.0417**0.5, abs=0.0005)
    assert value("chem.still_margin") == pytest.approx(0.6456, abs=0.0005)
    assert results["chem.still_margin"].low == pytest.approx(2.2765 * 0.000019**0.5, abs=0.00001)
    assert results["chem.still_margin"].low == pytest.approx(0.00992, abs=0.00001)
    assert results["chem.still_margin"].high == pytest.approx(23.1, abs=0.05)
    assert value("chem.fresh_dwell_to_strip") == pytest.approx(0.1001, abs=0.0001)
    assert results["chem.fresh_dwell_to_strip"].high == pytest.approx(1 / 2.277**2, abs=0.0005)
    # Still acid leaves 49 percent of the layer at most (7 to 61), 26 percent with the bisulfate counted (4 to 35).
    left, counted = results["chem.layer_left_under_acid"], results["chem.layer_left_counting_bisulfate"]
    assert (left.value, left.low, left.high) == pytest.approx((0.4905, 0.0740, 0.6101), abs=0.0001)
    assert (counted.value, counted.low, counted.high) == pytest.approx((0.2649, 0.0381, 0.3468), abs=0.0001)
    assert left.label.startswith("Most of a cycle's layer that stands under still acid")
    # The most a batch can deposit: 4740 of the 8580 mol a fill dissolves, 5882 of 7736 mol at the most; and above
    # nothing at every corner, so the batch is always strong enough to grow a layer at all.
    assert value("chem.deposit_over_fill") == pytest.approx(4740 / 8580, abs=0.001)
    assert results["chem.deposit_over_fill"].high == pytest.approx(5882 / 7736, abs=0.001)
    assert results["chem.deposit_over_fill"].low == pytest.approx(0.138, abs=0.001)
    # 09 row 26: 13 320 mol; 07 section 4.4: 0.3475 t of hydrogen sulfide per tonne of sulfuric acid.
    assert value("chem.h2s_per_batch") == pytest.approx(13320, rel=0.001)
    assert value("chem.h2s_mass_per_batch") / (value("chem.h2s_per_batch") * 0.09808) == pytest.approx(0.3475, abs=2e-4)
    assert value("chem.h2s_flux") == pytest.approx(13319.4 / 86400, rel=1e-4)
    assert value("chem.h2s_mass_per_year") == pytest.approx(453.9 * 365.25, rel=1e-3)
    # 60 ppmv fills 1 / 6e-5 King's Chambers with the sulfur of one: 320.4 m3 / 6e-5 = 5.34e6 m3.
    assert value("chem.cave_air_per_batch") == pytest.approx(320.4 / 6e-5, rel=1e-9)
    assert feed.flux({"site.atm_pressure": 101325.0, "kc.volume": 320.4, "chem.temperature": 293.15,
                      "rx.cycle_time": 3600.0}) == pytest.approx(3.70, rel=0.001)


def test_the_fresh_dwell_note_gives_what_the_ledgers_fill_time_would_add(led, results):
    # The ledger carries a fill time (flow.fill_time), and the note of rx.fresh_dwell says so and what the dwell and
    # the still-fill margin would be with it added: (3600 + 3600) / 86400 = 0.083, and 0.646 x sqrt(0.0833 / 0.0417)
    # = 0.91, since the margin goes as the square root of the dwell.
    note, dwell = led.quantities["rx.fresh_dwell"].note, led.q("rx.fresh_dwell")
    with_fill = (led.q("hydro.drain_time") + led.q("flow.fill_time")) / led.q("rx.cycle_time")
    margin = results["chem.still_margin"].value
    assert dwell == pytest.approx(led.q("hydro.drain_time") / led.q("rx.cycle_time"), abs=5e-5)
    assert "holds no fill time" not in note and "flow.fill_time" in note
    for text in (f"{led.q('hydro.drain_time') + led.q('flow.fill_time'):.0f} s in {led.q('rx.cycle_time'):.0f} s, "
                 f"{with_fill:.3f} of the acid's",
                 f"dissolve {margin * (with_fill / dwell) ** 0.5:.2f} of the layer one cycle grows where it dissolves "
                 f"{margin:.2f} at this value"):
        assert text in note, note
    assert margin * (with_fill / dwell) ** 0.5 < 1  # so the note's "both below the 1" holds


def test_s19_follows_the_capture_against_the_90_and_50_percent_lines(led):
    status, basis = with_quantities(led, {})["S19"]
    assert status == "conditional"
    for text in ("a cycle of 24 h (the hypothesis states none; 1 h to 1 yr is taken as its range)",
                 "87 percent of the sulfur dioxide", "(0.1 to 97 percent over the ranges of the inputs)",
                 "neither always at the 90 percent", "could hold 98 percent at equilibrium",
                 "gas-side coefficient 0.003 to 10 mm/s, assumed",
                 "liquid-film coefficient 0.001 to 0.01 mm/s, assumed with no source",
                 "none of which the hypothesis gives; the 87 percent is for a gas-side coefficient of 1.5 mm/s and a "
                 "liquid-film coefficient of 0.01 mm/s.",
                 # the values at which the outcome turns, and what a stated cycle would leave open
                 "At those two coefficients the share passes 50 percent after 7.8 h and passes 90 percent after 28 h, "
                 "with a time constant of 11 h toward the 96.9 percent that the water holds by Henry's law alone, "
                 "without the dissociation counted in the 98 percent; in a cycle of 24 h it runs from 2 to 94 percent "
                 "over the ranges of the other inputs, the two coefficients among them, so stating a cycle of that "
                 "length would not settle the claim without them.",
                 # the assumption that the rise takes the whole cycle, and the share if it takes the ledger's fill time
                 "The model gives the gas the whole cycle over the half-full Gallery, though it stands over the water "
                 "only until the water has risen (S18): in a contact of the 1 h that the ledger carries for one fill, "
                 "a time the hypothesis does not state either, the share is 9 percent (0.014 to 94 percent over fills "
                 "of 10 minutes to 24 h and the ranges of the other inputs)."):
        assert text in basis, basis
    # the numbers in those two sentences are the computed ones
    q = {i: led.q(i) for i in transfer.CAPTURE}
    others = tuple(i for i in transfer.CAPTURE if i != "rx.cycle_time")
    assert [f"{transfer.time_to_capture(q, line) / 3600:.2g}" for line in (0.50, 0.90)] == ["7.8", "28"]
    _, low, high = simkit.corners(led, others, lambda v: transfer.capture_share(v | {"rx.cycle_time": 86400.0}))
    assert (low, high) == pytest.approx((0.0202, 0.9430), abs=0.0005) and low < 0.5 and high > 0.9
    in_rise, least, most = simkit.corners(led, others + ("flow.fill_time",), lambda v: transfer.capture_share(
        v | {"rx.cycle_time": v["flow.fill_time"]}))
    assert in_rise == pytest.approx(0.0865, abs=0.0005) and least == pytest.approx(0.000142, rel=0.01)
    assert most == pytest.approx(high)  # the longest fill is a day, the ledger's cycle
    assert (led.q("flow.fill_time"), *led.rng("flow.fill_time")) == (3600.0, 600.0, 86400.0)
    # the word does not rest on which of the two times is taken: a cycle no longer than the fill is conditional too
    hour = with_quantities(led, {"rx.cycle_time": (3600.0, 600.0, 86400.0)})["S19"]
    assert hour[0] == "conditional" and "9 percent of the sulfur dioxide crosses" in hour[1]

    # The liquid film alone moves the share across the 50 percent line, which is why the basis names it: at its
    # slow end, a tenth of the ledger's value, a convecting gas and a one-day cycle give 23 percent, not 87.
    slow_film = chem.results(altered(led, {"chem.kl_surface": fixed(1e-6), "rx.cycle_time": fixed(86400.0),
                                           "rx.kg_gas": fixed(1.5e-3)}))["chem.capture_share"]
    assert slow_film.value == pytest.approx(0.23, abs=0.01) and slow_film.high < 0.5

    # Convecting gas over stirred water for a day: 96 percent or more at every end of the ranges.
    stirred = {"rx.kg_gas": fixed(1e-2), "chem.kl_surface": fixed(1e-4), "rx.cycle_time": fixed(86400.0)}
    status, basis = with_quantities(led, stirred)["S19"]
    assert status == "pass"
    assert "(96 percent at the least), at least the 90 percent" in basis and "under the 50 percent" not in basis
    assert "The model gives the gas the whole cycle" in basis and "At those two coefficients" not in basis

    # Still gas for an hour: a tenth of a percent at most.
    status, basis = with_quantities(led, {"rx.kg_gas": fixed(3e-6), "rx.cycle_time": fixed(3600.0)})["S19"]
    assert status == "fail"
    assert "0.1 percent of the sulfur dioxide crosses" in basis and "(0.1 to 0.1 percent" in basis
    assert "below the 50 percent under which" in basis
    assert "The model gives the gas the whole cycle" in basis and "At those two coefficients" not in basis


def test_s22_fails_on_the_nitrogen_and_otherwise_follows_the_pace_of_uptake(led):
    status, basis = with_quantities(led, {})["S22"]
    assert status == "fail"
    for text in ("Emptying the whole Gallery draws 573 m3 of gas into it", "holds 320 m3",
                 "at least 44 percent of the gas over the water is outside air, come down the shafts of S14 or in "
                 "through the masonry joints (39 percent at the least)",
                 "push 33 percent of the gas back (29 to 37 percent",
                 "54 percent of a mixture", "under 2.0 percent of the gas (2.4 percent at most)",
                 "oxygen for 0.8 percent of the sulfur, while S14 to S17 carry air into the Gallery",
                 "states no gas fraction, and the whole Gallery is taken as emptied because S18 raises the water "
                 "again in the four activations with which S12 fills it. Taking the least air that emptying the whole "
                 "Gallery admits, not a gas without air, as the end most favourable to the hypothesis is a judgement "
                 "call."):
        assert text in basis, basis
    assert "stroke" not in basis  # S12 and S18 keep that word for one activation, a quarter of the Gallery

    # Were nitrogen as soluble as the gas space it leaves, nothing would have to go back, and the pace would decide.
    soluble = {"rx.henry_n2": fixed(1e-3)}
    status, basis = with_quantities(led, soluble)["S22"]
    assert status == "conditional"
    assert "1.1 times the rate at which the water displaces it (0.00042 to 6.1e+02 times" in basis
    assert "depends on the cycle time and the stirring" in basis and basis.endswith("is a judgement call.")

    stirred = {"rx.kg_gas": fixed(1e-2), "chem.kl_surface": fixed(1e-4), "rx.cycle_time": fixed(86400.0)}
    status, basis = with_quantities(led, soluble | stirred)["S22"]
    assert status == "pass" and "nothing is forced back at any end of the ranges" in basis
    assert basis.endswith("is a judgement call.")
    # Fast uptake does not help while the nitrogen stays: the ledger's solubility with the same stirring still fails.
    assert with_quantities(led, stirred)["S22"][0] == "fail"


def test_s23_follows_what_a_fill_dissolves_against_the_layer_a_cycle_grows(led):
    status, basis = with_quantities(led, {})["S23"]
    assert status == "conditional"
    for text in ("neutralise 41 percent of the strongest batch", "reaches 3.7 micrometres in a cycle of 24 h",
                 "(0.1 to 74 micrometres over the ranges of the inputs)", "can dissolve 0.63 mm of gypsum, 173 times "
                 "that layer (7.7 times at the least); even the most gypsum a whole batch can lay down is 55 percent "
                 "of what one fill dissolves (76 percent at most), so a fill that comes to saturation strips it",
                 "loses up to 0.21 mm per cycle and 2.1 mm in ten in bringing each batch to saturation (1.6 to 4.9 mm",
                 "A fill that stands still strips the layer a bare wall grows in one cycle by diffusion alone only if "
                 "it stands at least 0.1 times as long as the acid stood (0.19 times at most). The hypothesis does "
                 "not state that time; over the range taken, 1.9e-05 to 1 of the acid's, a still fill dissolves "
                 "0.0099 to 23 times that layer, and 0.65 times at the 0.042 the ledger takes as its value.",
                 "The acid of the next batch does not strip it: still acid dissolves it from outside while it grows "
                 "from beneath and leaves at most 49 percent of it (7 to 61 percent), about 26 percent once the "
                 "batch's bisulfate is counted (4 to 35 percent).",
                 "depends on how long the fresh water stands against the wall and on how it moves, neither of which "
                 "the hypothesis states."):
        assert text in basis, basis
    assert "strips it by diffusion" not in basis  # the basis says which layer a still fill strips

    # The word does not lean on setting the shortest drain against the longest cycle. The shortest drain in a
    # one-day cycle, 600 s in 86400 s, takes 2.277 x sqrt(1 / 144) = 0.19 of the layer at the favourable corner.
    # Only in the shortest cycle, 600 s in 3600 s = 0.167, does it come near the 0.193 at which that corner turns
    # (0.93 of the layer); a dwell from 0.193 up fails the claim, as the cases below show.
    status, basis = with_quantities(led, {"rx.fresh_dwell": fixed(600 / 86400)})["S23"]
    assert status == "conditional" and "a still fill dissolves 0.19 to 1.9 times that layer" in basis
    status, basis = with_quantities(led, {"rx.fresh_dwell": fixed(600 / 3600)})["S23"]
    assert status == "conditional" and "a still fill dissolves 0.93 to 9.4 times that layer" in basis

    # The status follows the fresh water's dwell, which the hypothesis does not state. Taken as equal to the acid's,
    # as the first pass took it without saying so, a still fill strips the layer at every corner and the claim fails.
    status, basis = with_quantities(led, {"rx.fresh_dwell": fixed(1.0)})["S23"]
    assert status == "fail"
    for text in ("a fill that stands still dissolves 3.2 times the layer by diffusion alone (2.28 times at the least, "
                 "over fresh-water dwells from 1 to 1 of the acid's, which the hypothesis does not state), so every "
                 "fill strips it; every cycle then starts on bare stone", "still water would not strip a thicker "
                 "deposit."):
        assert text in basis, basis
    # A quarter of the acid's time still strips it (2.277 / 2 = 1.14 at the least); 0.15 of it, under the 0.193 at
    # which the favourable corner turns, does not (2.277 x sqrt(0.15) = 0.88), and the claim is no longer failed.
    status, basis = with_quantities(led, {"rx.fresh_dwell": fixed(0.25)})["S23"]
    assert status == "fail" and "(1.14 times at the least, over fresh-water dwells from 0.25 to 0.25" in basis
    status, basis = with_quantities(led, {"rx.fresh_dwell": fixed(0.15)})["S23"]
    assert status == "conditional"
    assert "a still fill dissolves 0.88 to 8.9 times that layer, and 1.2 times at the 0.15 the ledger" in basis

    # A layer a hundred times more permeable at its fast end grows ten times thicker: a still fill would have to
    # stand ten times as long as the acid to strip it.
    fast, slow = 4.54e-12, 1.71e-15
    status, basis = with_quantities(led, {"chem.gypsum_h_diffusivity": (fast, slow, fast)})["S23"]
    assert status == "conditional"
    assert "at least 10 times as long as the acid stood (19 times at most)" in basis
    assert "leaves at most 93 percent of it (7 to 95 percent)" in basis and "so every fill strips it" not in basis

    # A layer thicker than any fill dissolves outlasts them all, and the criterion's second half stays open.
    status, basis = with_quantities(led, {"chem.gypsum_h_diffusivity": fixed(1e-6)})["S23"]
    assert status == "conditional"
    assert "the layer outlasts every fill" in basis and "holds no measured bound" in basis


def test_the_feed_claims_are_undefined_whatever_the_cycle_time(led):
    for cycle in ({}, {"rx.cycle_time": fixed(3600.0)}):
        got = with_quantities(led, cycle)
        assert got["S01"][0] == got["E01"][0] == "undefined"
    s01, e01 = with_quantities(led, {})["S01"][1], with_quantities(led, {})["E01"][1]
    for text in ("13319 mol of hydrogen sulfide, 454 kg", "0.15 mol/s and 166 t a year at one batch every 24 h",
                 "0.00041 to 3.8 mol/s over the cycle times taken", "states no cycle rate",
                 "07 gives no flux for any seep or spring", "5.3 million m3 of cave air"):
        assert text in s01 and text in e01, text
    # the reason that blocks the comparison at every cycle time leads; the unstated cycle rate follows
    lead = ("07 gives no flux for any seep or spring, so a required flux has nothing to be set against at any cycle "
            "time: its one analogue is a concentration, read from an abstract")
    assert s01.startswith(lead) and "cave air (60 ppmv in active sulfuric-acid caves). One full batch needs" in s01
    assert e01.startswith("No opened source gives a measured hydrogen sulfide flux")
    assert "the passing clause is not met. The failing clause cannot be evaluated either. " + lead in e01
    for basis in (s01, e01):
        assert basis.index("07 gives no flux") < basis.index("states no cycle rate")
        assert basis.endswith("the hypothesis states no cycle rate either, so the required flux is itself undefined "
                              "(07 section 4.4).")
    hourly = with_quantities(led, {"rx.cycle_time": fixed(3600.0)})["S01"][1]
    assert "3.7 mol/s and 3979 t a year at one batch every 1 h" in hourly


def test_the_package_decides_only_its_five_claims_and_merges_with_tier_0(led, results, tmp_path):
    decided = chem.verdicts(led, results)
    assert set(decided) == {"S01", "E01", "S19", "S22", "S23"}
    assert {claim: status for claim, (status, _) in decided.items()} == {
        "S01": "undefined", "E01": "undefined", "S19": "conditional", "S22": "fail", "S23": "conditional"}
    for _, basis in decided.values():
        assert "—" not in basis and basis.endswith(".")
    simkit.write_results("chem", led, results, decided, {"assumptions": ["test"]}, root=tmp_path)
    merged_results, merged, source = verdicts.merged(led, root=tmp_path)
    assert all(source[claim] == "chem" and merged[claim] == decided[claim] for claim in decided)
    assert merged_results["chem.capture_share"] == results["chem.capture_share"]
    assert source["S20"] == "tier0"  # Tier 0's verdict on the oxidation stands


def test_the_viewer_shows_the_numbers_now_the_claims_hold_the_listed_inputs(led, results):
    from pyramid import viewer_data

    assert chem.depends_on(led) == {claim: [] for claim in chem.RULES}  # claims.yaml holds every input they read
    assert {"rx.ion_diffusivity", "rx.fresh_dwell", "chem.ka2_sulfuric"} <= set(led.claims["S23"].depends_on)
    payload = viewer_data.claims_payload(led, results, chem.verdicts(led, results))
    shown = {claim["id"]: {number["label"] for number in claim["numbers"]} for claim in payload["claims"]}
    for claim, ids in chem.SHOWN.items():
        assert {results[id].label for id in ids} <= shown[claim], claim


def test_the_production_run_writes_results_series_and_figures(tmp_path):
    from pyramid.chem.__main__ import main

    out = main(root=tmp_path)
    assert out == tmp_path / "chem"
    for name in ("summary.json", "manifest.json", "capture.json", "pushback.json", "layer.json", "feed.json",
                 "oxidation.json", "figures/capture.png", "figures/pushback.png", "figures/layer.png",
                 "figures/feed.png"):
        assert (out / name).stat().st_size > 0, name
    stored_results, stored_verdicts, manifest = simkit.read_results("chem", root=tmp_path)
    assert len(stored_results) == len(chem.QUANTITIES) and set(stored_verdicts) == set(chem.RULES)
    assert len(manifest["assumptions"]) >= 8
