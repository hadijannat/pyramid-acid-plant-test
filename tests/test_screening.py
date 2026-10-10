"""Tests for the Tier 0 screening.

Each quantity is compared, to 2 percent, with the value printed in section 2 of
research/09-recomputation.md. Where a row of 09 used an input that differs from the ledger's
value, the case replaces that input, so the comparison is still with a number 09 prints.
"""
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
