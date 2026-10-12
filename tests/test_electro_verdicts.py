"""The four verdict rules of electro, each driven through the statuses it can return."""
import dataclasses
import math

import pytest

from pyramid import electro, ledger, simkit, verdicts


@pytest.fixture(scope="module")
def led() -> ledger.Ledger:
    return ledger.load()


@pytest.fixture(scope="module")
def conduction(led):
    """The three-dimensional results on a coarse grid (4 m cells at the chamber), solved once."""
    return electro.conduction_results(led, h=4.0)


@pytest.fixture(scope="module")
def results(led, conduction):
    return conduction | electro.chain_results(led, conduction) | electro.room_results(led)


def altered(led, changes: dict[str, tuple[float, float, float]]) -> ledger.Ledger:
    """A copy of the ledger with (value, low, high) of some quantities replaced."""
    quantities = dict(led.quantities)
    for id, (value, low, high) in changes.items():
        quantities[id] = dataclasses.replace(quantities[id], value=value, low=low, high=high)
    return dataclasses.replace(led, quantities=quantities)


def with_quantities(led, conduction, changes):
    """Verdicts on an altered ledger; the conduction results are kept, since no change here touches their inputs."""
    other = altered(led, changes)
    assert not set(changes) & set(electro.MODEL + electro.FAR_FIELDS + electro.STROKES + electro.sources.SHEETS)
    return electro.verdicts(other, conduction | electro.chain_results(other, conduction) | electro.room_results(other))


def with_results(led, results, **replaced):
    changed = {f"electro.{name}": dataclasses.replace(results[f"electro.{name}"], value=v, low=lo, high=hi)
               for name, (v, lo, hi) in replaced.items()}
    return electro.verdicts(led, results | changed)


def test_the_package_decides_its_four_claims_and_only_those(led, results):
    decided = electro.verdicts(led, results)
    assert set(decided) == {"S04", "E21", "S06", "E13"} == set(electro.RULES)
    assert all(id.startswith("electro.") and result.id == id for id, result in results.items())
    for result in results.values():
        assert result.low <= result.value <= result.high, result.id
        assert all(i in led.quantities for i in result.inputs), result.id
    for status, basis in decided.values():
        assert status == "fail" and "—" not in basis


def test_the_results_merge_with_tier_0(led, results, tmp_path):
    simkit.write_results("electro", led, results, electro.verdicts(led, results),
                         {"assumptions": electro.ASSUMPTIONS}, root=tmp_path)
    merged, decided, source = verdicts.merged(led, root=tmp_path)
    assert all(source[claim] == "electro" and decided[claim][0] == "fail" for claim in electro.RULES)
    assert "electro.needed_field_gas_solid" in merged and "t0.skin_depth_lightning" in merged


def test_s04_compares_the_telluric_field_with_what_the_chain_needs(led, conduction, results):
    status, basis = electro.verdicts(led, results)["S04"]
    field, needed = results["electro.telluric_field"], results["electro.needed_field_gas_solid"]
    # the favourable end: the extreme far field, 0.02 V/m, times the largest ratio the model finds, of order one
    assert field.high == pytest.approx(0.02 * results["electro.telluric_granite_ratio"].high)
    assert 0.02 < field.high < 0.1 and needed.low == pytest.approx(2.674e7, rel=1e-3)
    assert status == "fail"
    sustained = results["electro.needed_field_sustained"]
    # Tier 0's S07 chain at its generous end needs 2.07e6 V/m, less than the pulse chain's 2.67e7: both stand in the
    # basis, each with the orders of magnitude the field falls short of it, computed here from the same results
    assert sustained.low == pytest.approx(2.069e6, rel=1e-3) and sustained.low < needed.low
    for text in ("1e-07 to 2e-02 V/m", "a judgement call", "in the masonry at chamber level",
                 f"is {math.log10(needed.low / field.high):.1f} orders of magnitude below the 2.7e+07 V/m at which "
                 "Tier 0's single-pulse piezoelectric chain, a field applied across 1 m of granite within the 5 "
                 "microsecond rise of a stroke, first reaches a documented acoustic effect with every input at its "
                 "generous end, the line this rule takes for non-negligible as a judgement call; a charge held by "
                 "such a field is short by the same factor.",
                 "Tier 0's S07 chain, a sustained drive of 1 MHz across the antechamber's granite leaf for which no "
                 "source is proposed, reaches the same effect at 2.1e+06 V/m, and the field is "
                 f"{math.log10(sustained.low / field.high):.1f} orders of magnitude below that too."):
        assert text in basis, basis
    assert "most generous" not in basis
    # 13 times between the two chains is 1.1 orders between the two shortfalls
    assert math.log10(needed.low / sustained.low) == pytest.approx(1.11, abs=0.01)
    assert results["electro.telluric_masonry_ratio"].high < 1 and results["electro.telluric_summit_ratio"].high < 0.1

    # a field that reaches the need over part of its range only
    status, basis = with_results(led, results, telluric_field=(1e3, 1.0, 1e9))["S04"]
    assert status == "conditional" and "neither always below 2.7e+07 V/m nor always above 2.8e+10 V/m" in basis
    # a field above the need at its least generous
    status, basis = with_results(led, results, telluric_field=(1e11, 1e11, 1e11))["S04"]
    assert status == "pass" and "is above the 2.8e+10 V/m" in basis and "short by" not in basis
    assert "with every input at its least generous end" in basis and "S07" not in basis
    # a field between the two chains' needs still fails by the pulse chain, and the basis does not call it below both
    status, basis = with_results(led, results, telluric_field=(1e7, 1e7, 1e7))["S04"]
    assert status == "fail" and "below that too" not in basis
    assert "reaches the same effect at 2.1e+06 V/m, which the field reaches at the favourable end." in basis

    # the same three through the ledger: a granite a great deal more piezoelectric than any measured
    assert with_quantities(led, conduction, {"em.granite_piezo_d": (1e4, 1e4, 1e4)})["S04"][0] == "pass"
    assert with_quantities(led, conduction, {"em.granite_piezo_d": (1e-15, 1e-15, 1e4)})["S04"][0] == "conditional"
    assert with_quantities(led, conduction, {"em.granite_piezo_d": (7e-13, 7e-13, 7e-13)})["S04"][0] == "fail"


def test_e21_adds_the_ore_sheets_and_the_voltage_they_could_gather(led, conduction, results):
    status, basis = electro.verdicts(led, results)["E21"]
    ratio, plain = results["electro.ore_ratio"], results["electro.telluric_granite_ratio"]
    gather = results["electro.ore_gather_length"]
    assert plain.value < ratio.value < ratio.high < 10  # sheets raise the field by a factor of order one
    # needed voltage over the extreme far field: 2.674e7 V/m x 1 m / 0.02 V/m = 1.34e9 m
    assert gather.low == pytest.approx(2.674e7 * 1.0 / 0.02, rel=1e-3)
    assert status == "fail"
    field, needed, sustained = (results[f"electro.{name}"] for name in
                                ("ore_field", "needed_field_gas_solid", "needed_field_sustained"))
    for text in ("0.003 ohm m", "0.1 to 10 m thick, 10 to 300 m deep and up to 500 m long, all assumed",
                 f"is {math.log10(needed.low / field.high):.1f} orders of magnitude below the 2.7e+07 V/m at which "
                 "Tier 0's single-pulse piezoelectric chain",
                 "reaches the same effect at 2.1e+06 V/m, and the field is "
                 f"{math.log10(sustained.low / field.high):.1f} orders of magnitude below that too.",
                 "over 1.3e+09 m to offer the pulse chain its voltage"):
        assert text in basis, basis
    assert "most generous" not in basis

    assert with_results(led, results, ore_field=(1e3, 1.0, 1e9))["E21"][0] == "conditional"
    assert with_results(led, results, ore_field=(1e11, 1e11, 1e11))["E21"][0] == "pass"
    # sheets no longer than those swept that could offer the chain its voltage keep the claim open, drawn or not
    assert with_results(led, results, ore_gather_length=(400.0, 400.0, 400.0))["E21"][0] == "conditional"
    assert with_quantities(led, conduction, {"em.granite_piezo_d": (1e4, 1e4, 1e4)})["E21"][0] == "pass"
    assert with_quantities(led, conduction, {"em.granite_piezo_d": (1e-15, 1e-15, 1e4)})["E21"][0] == "conditional"


def test_s06_compares_the_stroke_field_with_the_need_under_the_breakdown_cap(led, conduction, results):
    status, basis = electro.verdicts(led, results)["S06"]
    peak, mean = results["electro.lightning_granite_field"], results["electro.lightning_granite_mean_field"]
    # of order kV/m at the median stroke; never more than the design maximum in the most resistive masonry allows
    assert 1e3 < mean.value < peak.value < 1e4 and peak.high < 2e5
    assert peak.high / peak.value > 200e3 / 30e3  # 200 kA against 30 kA, and 1500 against 500 ohm m besides
    assert results["electro.lightning_shortfall"].low == pytest.approx(2.674e7 / peak.high, rel=1e-3) and \
        results["electro.lightning_shortfall"].low > 100
    assert status == "fail"
    needed, sustained = results["electro.needed_field_gas_solid"], results["electro.needed_field_sustained"]
    even = led.rng("em.piezo_field_lightning")
    assert (even[0] / 1e3, even[1] / 1e3) == pytest.approx((0.07, 11.3))  # 04's even-spreading estimate, in kV/m
    assert sustained.low < led.q("em.air_breakdown_field") < needed.low
    for text in ("A stroke of 30 kA", "200 kA design maximum", "skin depths",
                 "Tier 0's single-pulse piezoelectric chain, a field applied across 1 m of granite within the 5 "
                 "microsecond rise of a stroke, needs 2.7e+07 V/m with every input at its generous end to reach a "
                 f"documented acoustic effect, {needed.low / peak.high:.0f} times the {peak.high / 1e3:.0f} kV/m of "
                 "that corner and 8.9 times the 3e+06 V/m at which air breaks down.",
                 "Tier 0's S07 chain, a sustained drive of 1 MHz across the antechamber's granite leaf for which no "
                 f"source is proposed, reaches the same effect at 2.1e+06 V/m, {sustained.low / peak.high:.0f} times "
                 "that corner and below the breakdown field; a return stroke is a single pulse (04 claim C6), so the "
                 "claim is held to the pulse chain.",
                 "The criterion's fail clause, a field screened to the conduction value of order kV/m or less, is "
                 "read as the field staying below the pulse chain's need at the favourable end, the order kV/m being "
                 "04's own estimate of the conduction value (0.07 to 11 kV/m by even spreading): a judgement call.",
                 "In this model the field in the granite is the conduction value by construction.",
                 "would bring that peak to the breakdown field, which caps it below the pulse chain's need; the "
                 "sustained chain's need lies under that cap."):
        assert text in basis, basis
    assert "most generous" not in basis and "times more than that" not in basis

    # however resistive the core is taken to be, the breakdown field caps the peak below the pulse chain's need; the
    # basis then does not put the sustained chain's need above a corner that has passed it
    status, basis = with_results(led, results, lightning_granite_field=(1e6, 1e3, 1e9))["S06"]
    assert status == "fail" and "reaches the same effect at 2.1e+06 V/m, which that corner reaches and below" in basis
    # a chain that needed less than the breakdown field would leave the claim open, and a field above every need
    # would pass it
    easier = {"em.granite_piezo_d": (1e-9, 1e-12, 1e-9)}  # needs 1.9e4 V/m at the generous end, 1.9e7 at the other
    status, basis = with_quantities(led, conduction, easier)["S06"]
    assert status == "conditional" and "over part of the ranges of the inputs only" in basis
    status, basis = with_quantities(led, conduction, {"em.granite_piezo_d": (1e4, 1e4, 1e4)})["S06"]
    assert status == "pass" and "That exceeds the" in basis and "caps it" not in basis


def test_e13_ranks_the_three_rooms_in_both_measures(led, conduction, results):
    status, basis = electro.verdicts(led, results)["E13"]
    assert status == "fail"
    decay, quality = results["electro.decay_lead"], results["electro.quality_lead"]
    # hand values: the decay times go as V / S, 0.414 m against 1.092 m, a lead of 0.38, and at the antechamber's best
    # (21.3 / 38) / (318.8 / 293) = 0.52; Q of the lowest mode goes as f V / S, a lead of 1.05
    assert decay.value == pytest.approx(0.379, abs=0.002) and decay.high == pytest.approx(0.515, abs=0.003)
    assert quality.low < 1 < quality.value == pytest.approx(1.045, abs=0.002)
    for text in ("antechamber 3.3 s, King's Chamber 8.8 s, Grand Gallery 4.6 s", "45.2, 16.4, 3.6 Hz",
                 "antechamber 69, King's Chamber 66, Grand Gallery 8",
                 "ranks last of three in decay time, with 0.38 of the longest other (0.27 to 0.52",
                 "first in modal quality factor, with 1.05 of the highest other (0.73 to 1.42)",
                 "It is never first in decay time, so it does not rank first in both", "a judgement call",
                 "With the passage mouths open it falls to 0.13 of the longest decay and 0.35 of the highest quality",
                 "No acoustic measurement of the antechamber exists"):
        assert text in basis, basis

    # an antechamber whose volume might be three times the surveyed box could lead in both, at that end only
    status, basis = with_quantities(led, conduction, {"ante.volume": (18.5, 18.5, 60.0)})["E13"]
    assert status == "conditional" and "at the favourable end only" in basis
    # a room far larger than the antechamber would rank first whatever the other inputs
    status, basis = with_quantities(led, conduction, {"ante.volume": (2000.0, 2000.0, 2000.0)})["E13"]
    assert status == "pass" and "ranks first of three in decay time" in basis and "first in modal quality factor" in basis
    # and one first in decay time but never in quality factor fails on that measure
    status, basis = with_results(led, results, decay_lead=(2.0, 1.5, 3.0), quality_lead=(0.5, 0.4, 0.9))["E13"]
    assert status == "fail" and "It is never first in modal quality factor" in basis
