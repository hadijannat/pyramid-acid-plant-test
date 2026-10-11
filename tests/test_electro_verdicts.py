"""The four verdict rules of electro, each driven through the statuses it can return."""
import dataclasses

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
    for text in ("1e-07 to 2e-02 V/m", "orders of magnitude below the 2.7e+07 V/m", "a judgement call",
                 "a charge held by such a field is short by the same factor", "in the masonry at chamber level"):
        assert text in basis, basis
    assert results["electro.telluric_masonry_ratio"].high < 1 and results["electro.telluric_summit_ratio"].high < 0.1

    # a field that reaches the need over part of its range only
    status, basis = with_results(led, results, telluric_field=(1e3, 1.0, 1e9))["S04"]
    assert status == "conditional" and "neither always below 2.7e+07 V/m nor always above 2.8e+10 V/m" in basis
    # a field above the need at its least generous
    status, basis = with_results(led, results, telluric_field=(1e11, 1e11, 1e11))["S04"]
    assert status == "pass" and "is above the 2.8e+10 V/m" in basis and "short by" not in basis

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
    for text in ("0.003 ohm m", "0.1 to 10 m thick, 10 to 300 m deep and up to 500 m long, all assumed",
                 "orders of magnitude below the 2.7e+07 V/m", "over 1.3e+09 m"):
        assert text in basis, basis

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
    for text in ("A stroke of 30 kA", "200 kA design maximum", "needs 2.7e+07 V/m at its most generous",
                 "8.9 times the 3e+06 V/m at which air breaks down", "the conduction value and no more",
                 "skin depths", "would bring that peak to the breakdown field, which caps it below the need"):
        assert text in basis, basis

    # however resistive the core is taken to be, the breakdown field caps the peak below the need
    assert with_results(led, results, lightning_granite_field=(1e6, 1e3, 1e9))["S06"][0] == "fail"
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
    # hand values: T60 = 0.161 V / A with A = alpha S + mouths: antechamber 18.5 / (0.02 x 44.7 + 2 x 1.167) = 0.92 s,
    # King's Chamber 320.4 / (0.02 x 293.3 + 1.167) = 7.3 s; at the favourable end 21.3 / (0.01 x 38 + 2.334) = 1.3 s
    # against 320 / (0.05 x 293 + 1.167) = 3.2 s
    for text in ("antechamber 0.9 s (0.5 to 1.3)", "King's Chamber 7.3 s (3.2 to 12.7)", "45.2, 16.4, 3.6 Hz",
                 "ranks last of three in decay time and second in modal quality factor",
                 "it decays in 1.3 s against at least 3.2 s for the King's Chamber", "2.6 times longer (1.9 to 3.8)",
                 "No acoustic measurement of the antechamber exists"):
        assert text in basis, basis

    # with every passage shut the ranking turns on the wall absorptions, which are assumed
    shut = {"ante.low_passage.width": (0.0, 0.0, 0.0)}
    status, basis = with_quantities(led, conduction, shut)["E13"]
    assert status == "conditional" and "at the favourable end only" in basis
    # a room far larger than the antechamber, with the walls' absorption known, would rank first
    vast = shut | {"ante.volume": (2000.0, 2000.0, 2000.0), "ac.wall_absorption": (0.02, 0.02, 0.02)}
    status, basis = with_quantities(led, conduction, vast)["E13"]
    assert status == "pass" and "ranks first of three in decay time and first in modal quality factor" in basis
