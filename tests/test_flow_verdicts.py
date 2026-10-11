"""The five flow verdicts: each rule is driven through the statuses it can return, on altered copies of the ledger."""
import dataclasses
import json

import pytest

from pyramid import flow, ledger, screening, simkit, verdicts
from pyramid.flow import __main__ as production


@pytest.fixture(scope="module")
def led() -> ledger.Ledger:
    return ledger.load()


def judge(led, changes=None, **replaced):
    """Verdicts after replacing (value, low, high) of some ledger quantities, or some results outright."""
    quantities = dict(led.quantities)
    for id, (value, low, high) in (changes or {}).items():
        quantities[id] = dataclasses.replace(quantities[id], value=value, low=low, high=high)
    altered = dataclasses.replace(led, quantities=quantities)
    results = flow.all_results(altered)
    for name, fields in replaced.items():
        results[f"flow.{name}"] = dataclasses.replace(results[f"flow.{name}"], **fields)
    return flow.verdicts(altered, results)


def has(basis, *texts):
    for text in texts:
        assert text in basis, basis


def test_the_package_decides_its_five_claims_and_no_other(led):
    decided = judge(led)
    assert set(decided) == {"S03", "S08", "S13", "S14", "S17"}
    assert not set(decided) & set(screening.RULES)  # Tier 0 verdicts stand
    assert {claim: status for claim, (status, _) in decided.items()} == {
        "S03": "conditional", "S08": "conditional", "S13": "fail", "S14": "conditional", "S17": "conditional"}
    for _, basis in decided.values():
        assert "—" not in basis and "nan" not in basis and "inf" not in basis.replace("inflow", "")


def test_every_result_is_a_finite_number_built_from_ledger_quantities(led):
    results = flow.all_results(led)
    assert len(results) == len(flow.network.QUANTITIES) == 27
    for result in results.values():
        assert result.id.startswith("flow.") and result.unit in ledger.UNITS
        assert result.low <= result.value <= result.high < float("inf"), result.id
        assert set(result.inputs) <= set(led.quantities), result.id


def test_new_ledger_quantities_carry_their_flags(led):
    new = {id: quantity for id, quantity in led.quantities.items() if id.startswith("flow.")}
    assert len(new) == 8
    for quantity in new.values():
        assert not quantity.verified
        assert quantity.note.startswith(("from memory:", "assumed for the model:", "not specified by the hypothesis:",
                                         "computed:")), quantity.id
    assert new["flow.slab_leak_area"].value == pytest.approx(led.q("ante.slab_clearance") * led.q("ante.slab_width"))


def test_s03_sets_the_half_time_against_the_interval(led):
    status, basis = judge(led)["S03"]
    assert status == "conditional"
    has(basis, "by diffusion in 361 (271 to 460) years", "no wind below 29 (23 to 43) m/s", "2.2 times as dense",
        "against 516 (472 to 551) Pa", "through the 202 cm2 of grooves and one slab's clearance",
        "half the charge is gone in about 32 minutes", "In the 30 m/s at the top of the assumed wind range the "
        "half-time falls to 15 minutes", "10 minutes to 30 days", "held only below 9 m/s",
        "by diffusion alone, which is a limit of the model", "does not state")

    # winds that never reach the 23 m/s which can lift the gas leave the shafts to diffusion, centuries against
    # 30 days, but the charge still runs out of the antechamber path at the chamber's floor
    calm = {"flow.wind_speed": (5.0, 0.0, 20.0)}
    status, basis = judge(led, calm)["S03"]
    assert status == "conditional"
    has(basis, "Up to the 20 m/s of the assumed wind range the shafts keep half the charge for 104 years or more",
        "half the charge is gone in about 32 minutes")
    assert "falls to" not in basis

    # it passes only with those winds and that path shut, and the shut path alone does not pass it in a storm
    shut = {"ante.groove_connected_area": (0.0, 0.0, 0.0), "flow.slab_leak_area": (0.0, 0.0, 0.0)}
    status, basis = judge(led, calm | shut)["S03"]
    assert status == "pass"
    has(basis, "Even in a wind of 20 m/s the half-time is", "days or more")
    assert "falls to" not in basis and "gone in about" not in basis
    assert judge(led, shut)["S03"][0] == "conditional"

    # the storm and the open path both pass if the draw follows within the 15 minutes the charge lasts in them
    assert judge(led, {"flow.delivery_to_draw_interval": (600.0, 300.0, 900.0)})["S03"][0] == "pass"
    assert judge(led, {"flow.delivery_to_draw_interval": (1800.0, 1500.0, 2100.0)})["S03"][0] == "conditional"

    # an interval longer than even diffusion allows fails it
    status, basis = judge(led, {"flow.delivery_to_draw_interval": (1e12, 1e12, 1e13)})["S03"]
    assert status == "fail"
    has(basis, "Yet the half-time is", "at the most, shorter than")


def test_s08_reports_the_reservoir_that_must_be_assumed(led):
    status, basis = judge(led)["S08"]
    assert status == "conditional"
    # 60 - 30.0 - 15 = 15 m; 58 - 30.02 - 17.5 = 10.5 m; 62 - 29.97 - 14.5 = 17.5 m
    # deepest floor -26.82 - 5.03 = -31.85 m, 1.85 m under the foot at -30.00 m; pit bottom -34.57 - 0.5 = -35.07 m
    has(basis, "documented at Khufu or beside it", "stands 15 (10 to 18) m below the foot of the Descending Passage",
        "deepest floor lies 1.9 m and the pit's original bottom up to 5.1 m lower than that foot, still above that "
        "water", "Perched water at 22 to 48 m above sea level", "none is reported at Khufu",
        "a reservoir that is assumed",
        "17.0 m above the pavement to use the entrance", "51.5 m above the pavement, 112 (109 to 114) m above sea level",
        "One fill takes 866 (808 to 924) m3", "0.24 m3/s if it takes 1 h", "385 (284 to 536) m3 to prime")

    # water that stands between the foot of the passage and the pit's bottom is not called below both
    status, basis = judge(led, {"hydro.ok_flood_peak_asl": (20.0, 20.0, 27.0)})["S08"]
    assert status == "conditional" and "still above that water" not in basis

    # documented water above the foot of the passage at every corner needs no assumption
    status, basis = judge(led, {"hydro.ok_flood_peak_asl": (40.0, 35.0, 45.0)})["S08"]
    assert status == "pass"
    has(basis, "stands 3 m or more above the foot of the Descending Passage", "without an assumed reservoir")

    # water that reaches it only at the favourable end still rests on the assumption
    assert judge(led, {"hydro.ok_flood_peak_asl": (30.0, 25.0, 35.0)})["S08"][0] == "conditional"


def test_s13_fails_while_the_full_gallery_stands_over_the_antechamber_floor(led):
    status, basis = judge(led)["S13"]
    assert status == "fail"
    # 51.5 - 42.992 = 8.5 m; 998.2 x 9.80665 x 8.508 = 83.3 kPa
    has(basis, "stands 8.5 (8.3 to 8.6) m above the antechamber floor", "presses with 83 kPa",
        "0.16 (0.14 to 0.26) m3/s enter", "after 6 (4 to 7) minutes", "grooves alone after 1.0 h",
        "with the path shut no gas passes either", "release in 53 s", "still rises 2.2 m or more",
        "43.0 m above the pavement", "states no drain route")

    # blind grooves drop the clause about them, not the verdict: the head decides
    status, basis = judge(led, {"ante.groove_connected_area": (0.0, 0.0, 0.0)})["S13"]
    assert status == "fail" and "grooves alone" not in basis

    # were the water never above the antechamber floor it would stay out, and the unstated drain route would
    # be all that is left of the criterion
    status, basis = judge(led, antechamber_water_head={"value": -0.1, "low": -0.2, "high": 0.0})["S13"]
    assert status == "undefined"
    has(basis, "need not enter the King's Chamber", "states no drain route")
    assert judge(led, antechamber_water_head={"value": 0.1, "low": -0.1, "high": 0.2})["S13"][0] == "undefined"


def test_s14_asks_for_more_than_half_down_the_shafts(led):
    status, basis = judge(led)["S14"]
    assert status == "conditional"
    # 51.50 - 42.99 - 1.11 = 7.40 m of water over the opening's top, 998.2 x 9.80665 x 7.40 = 72.4 kPa;
    # 0.69 x (1 - 0.132) = 0.60 and 0.89 x (1 - 0.132) = 0.78: the steady shares less the part displaced under water
    has(basis, "antechamber opening lies 7.4 m under the surface of the full Gallery",
        "until 13.2 (12.7 to 13.3) percent of the Gallery has drained", "72 kPa at the start",
        "in 1 h through 202 cm2 of grooves and one slab's clearance",
        "joints of 0.51 mm leaking along a path of 1.0 m, 60 percent",
        "195 Pa at the start, when the joints alone supply the pocket, and 60 Pa once the opening is clear",
        "10 minutes to 6 h, joints of 0.05 to 0.51 mm and joint paths of 0.3 to 3.0 m",
        "from 20 to 100 percent with that path open", "from 0 percent if the path is shut",
        "from 1 Pa to 99 kPa, the most a water column can pull", "grooves alone the share is 11 percent",
        "one after another, which pass what 108 cm2 passes, 44 percent", "no slab in the passage 78 percent",
        "tighter than 0.64 mm, or the drain slower than 30 minutes", "neither a drain rate")

    open_path = {"ante.groove_connected_area": (0.002, 0.002, 0.002), "flow.slab_leak_area": (0.018, 0.018, 0.018)}
    tight = {"hydro.joint_aperture": (5e-5, 5e-5, 5e-5)}
    status, basis = judge(led, open_path | tight)["S14"]
    assert status == "pass"
    # with tight joints the pocket pulls against the water over the opening from the start, and no drain rate
    # leaves the shafts less than half
    has(basis, "the share runs from 89 to 100 percent with that path open, and from 89 percent",
        "72 kPa at the start and 128 Pa once the opening is clear", "from 1 Pa to 78 kPa. Through",
        "tighter than 0.63 mm; the hypothesis")
    assert "joints alone supply" not in basis and "the most a water column can pull" not in basis
    # the path alone does not settle it: wide joints take most of the gas in a fast drain
    assert judge(led, open_path)["S14"][0] == "conditional"

    shut = {"ante.groove_connected_area": (0.0, 0.0, 0.0), "flow.slab_leak_area": (0.0, 0.0, 0.0)}
    status, basis = judge(led, shut)["S14"]
    assert status == "fail"
    has(basis, "0 percent of the replacement gas comes down", "tighter than 0.00 mm; the hypothesis")


def test_s17_asks_for_nine_tenths_through_the_antechamber_passage_as_surveyed(led):
    status, basis = judge(led)["S17"]
    assert status == "conditional"
    has(basis, "stay under water until 0.7 percent of it or less is left", "closed chamber",
        "antechamber opening lies 7.4 m under the surface of the full Gallery",
        "until 13.2 (12.7 to 13.3) percent of the Gallery has drained", "72 kPa at the start",
        "With gas-tight masonry nothing else can enter, so 100.0 (99.9 to 100.0) percent",
        "as surveyed, with no slab in it", "1350 m of masonry joints of 0.05 to 0.51 mm",
        "at outside pressure 0.3 to 3.0 m behind the Gallery's face, a leak that is assumed",
        "the share is 78 (38 to 100) percent over drain times of 10 minutes to 6 h",
        "tighter than 0.11 (0.04 to 0.24) mm", "the two shares are 100.0 and 60 percent through 202 cm2",
        "nothing if that path is shut, which is the question of S15")

    # whether the slabs' path is open or shut does not move the verdict: that is S15's question
    shut = {"ante.groove_connected_area": (0.0, 0.0, 0.0), "flow.slab_leak_area": (0.0, 0.0, 0.0)}
    status, basis = judge(led, shut)["S17"]
    assert status == "conditional"
    has(basis, "the two shares are 0.0 and 0 percent through 0 cm2")

    # the ledger's tightest joints no longer carry it: in a slow drain they feed the pocket while the opening is
    # under water, and the share falls under nine tenths with the shortest joint path
    status, basis = judge(led, {"hydro.joint_aperture": (5e-5, 5e-5, 5e-5)})["S17"]
    assert status == "conditional"
    has(basis, "the share is 99 (89 to 100) percent")

    # joints of 0.02 mm, under the 0.04 mm at the low end of the line, leave it over nine tenths at every corner
    status, basis = judge(led, {"hydro.joint_aperture": (2e-5, 2e-5, 2e-5)})["S17"]
    assert status == "pass"
    has(basis, "the share is 100 (98 to 100) percent")

    # joints ten times wider than the widest in the ledger still leave it conditional on gas-tight masonry
    assert judge(led, {"hydro.joint_aperture": (5e-3, 5e-3, 5e-3)})["S17"][0] == "conditional"

    # it fails only if less than nine tenths passed the antechamber even with gas-tight masonry
    lost = {"value": 0.6, "low": 0.5, "high": 0.7}
    assert judge(led, antechamber_share=lost, slabs_absent_share=lost)["S17"][0] == "fail"


def test_production_writes_results_that_merge_with_tier0(led, tmp_path, capsys):
    out = production.main(tmp_path)
    assert "27 results, 5 verdicts" in capsys.readouterr().out
    for name in ("summary.json", "manifest.json", "ingress.json", "shares.json", "retention.json", "openings.json",
                 "figures/s13_ingress.png", "figures/s14_s17_shares.png", "figures/s03_retention.png"):
        assert (out / name).stat().st_size > 0, name
    manifest = json.loads((out / "manifest.json").read_text())
    assert len(manifest["assumptions"]) == 10 and all(line.endswith(".") for line in manifest["assumptions"])
    assert sum("antechamber opening lies under the full Gallery" in line for line in manifest["assumptions"]) == 1
    results, verdict, _ = simkit.read_results("flow", tmp_path)
    assert verdict == flow.verdicts(led, flow.all_results(led))
    _, merged, source = verdicts.merged(led, tmp_path)
    assert {claim for claim, package in source.items() if package == "flow"} == set(verdict)
    assert merged["S13"][0] == "fail" and merged["S09"][0] == "conditional"  # S09 is Tier 0's and stands

    # the water reaches the shaft mouths when the closed form says, and the ceiling in the end
    water = json.loads((out / "ingress.json").read_text())
    case = water["cases"]["grooves and slab clearance"]
    assert case["depth_m"][-1] == pytest.approx(water["chamber_height_m"], rel=1e-6)
    assert results["flow.kc_flood_time"].value < case["time_s"][-1]
