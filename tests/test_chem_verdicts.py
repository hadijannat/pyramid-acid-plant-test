"""The chem results and the five verdict rules, each driven through the statuses it can return."""
import dataclasses

import pytest

from pyramid import chem, ledger, simkit, verdicts
from pyramid.chem import feed


@pytest.fixture(scope="module")
def led() -> ledger.Ledger:
    return ledger.load()


@pytest.fixture(scope="module")
def results(led) -> dict:
    return chem.results(led)


def with_quantities(led, changes: dict[str, tuple[float, float, float]]):
    """Verdicts after replacing (value, low, high) of some ledger quantities and recomputing every result."""
    quantities = dict(led.quantities)
    for id, (value, low, high) in changes.items():
        quantities[id] = dataclasses.replace(quantities[id], value=value, low=low, high=high)
    altered = dataclasses.replace(led, quantities=quantities)
    return chem.verdicts(altered, chem.results(altered))


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
    # 09 row 26: 13 320 mol; 07 section 4.4: 0.3475 t of hydrogen sulfide per tonne of sulfuric acid.
    assert value("chem.h2s_per_batch") == pytest.approx(13320, rel=0.001)
    assert value("chem.h2s_mass_per_batch") / (value("chem.h2s_per_batch") * 0.09808) == pytest.approx(0.3475, abs=2e-4)
    assert value("chem.h2s_flux") == pytest.approx(13319.4 / 86400, rel=1e-4)
    assert value("chem.h2s_mass_per_year") == pytest.approx(453.9 * 365.25, rel=1e-3)
    # 60 ppmv fills 1 / 6e-5 King's Chambers with the sulfur of one: 320.4 m3 / 6e-5 = 5.34e6 m3.
    assert value("chem.cave_air_per_batch") == pytest.approx(320.4 / 6e-5, rel=1e-9)
    assert feed.flux({"site.atm_pressure": 101325.0, "kc.volume": 320.4, "chem.temperature": 293.15,
                      "rx.cycle_time": 3600.0}) == pytest.approx(3.70, rel=0.001)


def test_s19_follows_the_capture_against_the_90_and_50_percent_lines(led):
    status, basis = with_quantities(led, {})["S19"]
    assert status == "conditional"
    for text in ("a cycle of 24 h (the hypothesis states none; 1 h to 1 yr is taken as its range)",
                 "87 percent of the sulfur dioxide", "(0 to 97 percent over the ranges of the inputs)",
                 "neither always at the 90 percent", "could hold 98 percent at equilibrium",
                 "gas-side coefficient 0.003 to 10 mm/s, assumed", "neither of which the hypothesis gives"):
        assert text in basis, basis

    # Convecting gas over stirred water for a day: 96 percent or more at every end of the ranges.
    stirred = {"rx.kg_gas": fixed(1e-2), "chem.kl_surface": fixed(1e-4), "rx.cycle_time": fixed(86400.0)}
    status, basis = with_quantities(led, stirred)["S19"]
    assert status == "pass"
    assert "(96 percent at the least), at least the 90 percent" in basis and "under the 50 percent" not in basis

    # Still gas for an hour: a tenth of a percent at most.
    status, basis = with_quantities(led, {"rx.kg_gas": fixed(3e-6), "rx.cycle_time": fixed(3600.0)})["S19"]
    assert status == "fail"
    assert "0 percent of the sulfur dioxide" in basis and "below the 50 percent under which" in basis


def test_s22_fails_on_the_nitrogen_and_otherwise_follows_the_pace_of_uptake(led):
    status, basis = with_quantities(led, {})["S22"]
    assert status == "fail"
    for text in ("draws 573 m3 of gas", "holds 320 m3", "at least 44 percent of the gas over the water is the "
                 "outside air of S14 (39 percent at the least)", "push 33 percent of the gas back (29 to 37 percent",
                 "54 percent of a mixture", "under 2.0 percent of the gas (2.4 percent at most)",
                 "oxygen for 0.8 percent of the sulfur, while S14 to S17 carry air into the Gallery",
                 "states no gas fraction and no stroke"):
        assert text in basis, basis

    # Were nitrogen as soluble as the gas space it leaves, nothing would have to go back, and the pace would decide.
    soluble = {"rx.henry_n2": fixed(1e-3)}
    status, basis = with_quantities(led, soluble)["S22"]
    assert status == "conditional"
    assert "1.1 times the rate at which the water displaces it (0.00042 to 6.1e+02 times" in basis
    assert "depends on the cycle time and the stirring" in basis

    stirred = {"rx.kg_gas": fixed(1e-2), "chem.kl_surface": fixed(1e-4), "rx.cycle_time": fixed(86400.0)}
    status, basis = with_quantities(led, soluble | stirred)["S22"]
    assert status == "pass" and "nothing is forced back at any end of the ranges" in basis
    # Fast uptake does not help while the nitrogen stays: the ledger's solubility with the same stirring still fails.
    assert with_quantities(led, stirred)["S22"][0] == "fail"


def test_s23_follows_what_a_fill_dissolves_against_the_layer_a_cycle_grows(led):
    status, basis = with_quantities(led, {})["S23"]
    assert status == "fail"
    for text in ("neutralise 41 percent of the strongest batch", "reaches 3.7 micrometres in a cycle of 24 h",
                 "(0.1 to 74 micrometres over the ranges of the inputs)", "can dissolve 0.63 mm of gypsum, 173 times "
                 "that layer (7.7 times at the least)", "dissolves 3.2 times the layer by diffusion alone (2.5 times "
                 "at the least)", "every fill strips it", "loses up to 0.21 mm per cycle and 2.1 mm in ten in bringing "
                 "each batch to saturation (1.6 to 4.9 mm", "not on the cycle time"):
        assert text in basis, basis

    # A layer a hundred times more permeable at its fast end grows ten times thicker: still water no longer strips it.
    fast, slow = 4.54e-12, 1.71e-15
    status, basis = with_quantities(led, {"chem.gypsum_h_diffusivity": (fast, slow, fast)})["S23"]
    assert status == "conditional"
    assert "dissolves only 0.32 times the layer by diffusion alone (0.25 to 23 times" in basis
    assert "depends on how the fresh water moves against the wall" in basis and "every fill strips it" not in basis

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
    assert s01.startswith("One full batch needs") and "60 ppmv" in s01
    assert e01.startswith("No opened source gives a measured hydrogen sulfide flux")
    assert "the passing clause is not met" in e01
    hourly = with_quantities(led, {"rx.cycle_time": fixed(3600.0)})["S01"][1]
    assert "3.7 mol/s and 3979 t a year at one batch every 1 h" in hourly


def test_the_package_decides_only_its_five_claims_and_merges_with_tier_0(led, results, tmp_path):
    decided = chem.verdicts(led, results)
    assert set(decided) == {"S01", "E01", "S19", "S22", "S23"}
    assert {claim: status for claim, (status, _) in decided.items()} == {
        "S01": "undefined", "E01": "undefined", "S19": "conditional", "S22": "fail", "S23": "fail"}
    for _, basis in decided.values():
        assert "—" not in basis and basis.endswith(".")
    simkit.write_results("chem", led, results, decided, {"assumptions": ["test"]}, root=tmp_path)
    merged_results, merged, source = verdicts.merged(led, root=tmp_path)
    assert all(source[claim] == "chem" and merged[claim] == decided[claim] for claim in decided)
    assert merged_results["chem.capture_share"] == results["chem.capture_share"]
    assert source["S20"] == "tier0"  # Tier 0's verdict on the oxidation stands


def test_the_viewer_shows_the_numbers_once_the_claims_gain_the_listed_inputs(led, results):
    from pyramid import viewer_data

    gained = chem.depends_on(led)
    assert set(gained) == set(chem.RULES)
    assert gained["S01"] == gained["E01"] == ["site.atm_pressure", "kc.volume", "chem.temperature", "rx.cycle_time",
                                              "rx.h2s_cave_air"]
    assert "rx.kg_gas" in gained["S19"] and "chem.henry_so2" not in gained["S19"]  # the claim already names it
    assert "rx.henry_n2" in gained["S22"] and "rx.ion_diffusivity" in gained["S23"]
    claims = {id: dataclasses.replace(claim, depends_on=claim.depends_on + tuple(gained.get(id, ())))
              for id, claim in led.claims.items()}
    decided = chem.verdicts(led, results)
    payload = viewer_data.claims_payload(dataclasses.replace(led, claims=claims), results, decided)
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
