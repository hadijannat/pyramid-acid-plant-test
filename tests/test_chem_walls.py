"""Benchmarks for the wall model: parabolic growth, Tier 0's saturation share, the ten-cycle bookkeeping."""
import math

import numpy as np
import pytest

from pyramid import ledger, screening
from pyramid.chem import walls


@pytest.fixture(scope="module")
def led() -> ledger.Ledger:
    return ledger.load()


@pytest.fixture(scope="module")
def q(led) -> dict[str, float]:
    return {i: led.q(i) for i in walls.WALL}


def test_a_diffusion_limited_layer_grows_parabolically():
    # Vm D C = 7.39e-5 m3/mol x 4.54e-14 m2/s x 46.5 mol/m3 = 1.56e-16 m2/s, from a layer 1 micrometre thick.
    product, start = 7.39e-5 * 4.54e-14 * 46.5, 1e-6
    times = np.array([0.0, 3600.0, 86400.0, 30 * 86400.0])
    expected = np.sqrt(start**2 + product * times)  # 1.0, 1.25, 3.81 and 20.1 micrometres
    assert expected[2] == pytest.approx(3.81e-6, rel=0.01) and expected[3] == pytest.approx(20.1e-6, rel=0.01)
    assert walls.grow(times, product, start) == pytest.approx(expected, rel=0.01)  # tolerance 1 percent
    assert walls.thickness(product, times, start) == pytest.approx(expected, rel=1e-12)
    # Far beyond the starting thickness the growth is parabolic: four times the time, twice the layer.
    late = walls.grow(np.array([0.0, 1e8, 4e8]), product, start)
    assert late[2] / late[1] == pytest.approx(2.0, rel=0.01)


def test_the_saturation_share_is_tier_0s(led, q):
    tier0 = screening.all_results(led)["t0.gypsum_saturation_loss"]
    assert walls.saturation_share(q) == pytest.approx(tier0.value, rel=1e-6)
    weak = q | {"kc.volume": 100.0}  # a batch too weak ever to saturate: the wall takes all of it
    assert walls.saturation_share(weak) == 1.0


def test_one_cycle_at_the_ledger_values(q):
    strength = 101325 * 320.4 / (8.314462618 * 293.15) / 573.0  # 23.2 mol/m3
    layer = math.sqrt(7.39e-5 * 4.54e-14 * 2 * strength * 86400)  # 3.67 micrometres in one day
    assert walls.layer_per_cycle(q) == pytest.approx(layer, rel=1e-9)
    assert layer == pytest.approx(3.67e-6, rel=0.005)
    # 03 check V17: a fresh fill dissolves 573 m3 x 15 mol/m3 = 8.6e3 mol, 0.63 mm over the ledger's 1000 m2.
    assert walls.fill_dissolves(q) == pytest.approx(0.015 * 998.2 * 573.0 / 1000.0 * 7.39e-5, rel=1e-9)
    assert walls.fill_dissolves(q) == pytest.approx(0.634e-3, rel=0.005)
    # Diffusion alone into still water for a day: 2 x 15.0 mol/m3 x sqrt(1e-9 x 86400 / pi) = 0.157 mol/m2.
    still = 2 * 0.015 * 998.2 * math.sqrt(1e-9 * 86400 / math.pi) * 7.39e-5
    assert walls.still_fill_dissolves(q) == pytest.approx(still, rel=1e-9)
    assert still == pytest.approx(11.6e-6, rel=0.005)
    assert walls.saturating_margin(q) == pytest.approx(173, rel=0.01)
    assert walls.still_margin(q) == pytest.approx(3.16, rel=0.01)
    # The cycle time cancels in the still margin: both the layer and the diffusion grow as the root of time.
    assert walls.still_margin(q | {"rx.cycle_time": 3600.0}) == pytest.approx(walls.still_margin(q), rel=1e-9)
    # Bare wall: 41.5 percent of 23.2 mol/m3 x 573 m3 = 5.5e3 mol of calcite, 0.204 mm over 1000 m2 (09 row 35).
    assert walls.bare_loss(q) == pytest.approx(0.414913 * strength * 573.0 / 1000.0 * 3.69e-5, rel=1e-5)
    assert walls.bare_loss(q) == pytest.approx(0.204e-3, rel=0.005)
    assert walls.loss_per_cycle(q) == pytest.approx(walls.bare_loss(q) + layer * 3.69 / 7.39, rel=1e-9)


def test_ten_cycles_strip_the_layer_each_time_and_keep_dissolving_the_wall(q):
    for fill in ("saturating", "still"):
        run = walls.cycles(q, fill)
        assert len(run["after_acid"]) == len(run["after_fill"]) == len(run["loss"]) == 10
        assert run["after_fill"] == [0.0] * 10  # stripped by every fill
        assert run["after_acid"] == pytest.approx([walls.layer_per_cycle(q)] * 10)
        assert run["loss"] == pytest.approx([walls.loss_per_cycle(q) * (k + 1) for k in range(10)])
    assert walls.cycles(q)["loss"][-1] == pytest.approx(2.06e-3, rel=0.005)  # 2.1 mm of limestone in ten cycles

    # A layer a hundred times more permeable grows ten times thicker, more than a still fill removes: it
    # survives, thickens from cycle to cycle, and the wall is bare only once.
    thick = q | {"chem.gypsum_h_diffusivity": 100 * q["chem.gypsum_h_diffusivity"]}
    run = walls.cycles(thick, "still")
    assert all(layer > 0 for layer in run["after_fill"])
    assert all(b > a for a, b in zip(run["after_fill"], run["after_fill"][1:]))
    first = walls.bare_loss(thick)
    assert first < run["loss"][-1] < 2 * first
    assert walls.cycles(thick, "saturating")["after_fill"] == [0.0] * 10
