"""Benchmarks for the wall model: parabolic growth, Tier 0's saturation share, the ten-cycle bookkeeping."""
import itertools
import math

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

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


def test_a_still_fill_strips_the_layer_only_if_it_stands_long_enough(q):
    # The margin goes as the root of the fresh water's dwell f: a quarter of the acid's time halves it.
    assert walls.still_margin(q | {"rx.fresh_dwell": 0.25}) == pytest.approx(walls.still_margin(q) / 2, rel=1e-9)
    # At equal dwell the fill dissolves 3.16 times the layer, so it just strips it at f = 1 / 3.16^2 = 0.100.
    assert walls.dwell_to_strip(q) == pytest.approx(1 / 3.1614**2, rel=1e-4)
    assert walls.still_margin(q | {"rx.fresh_dwell": walls.dwell_to_strip(q)}) == pytest.approx(1.0, rel=1e-9)
    for dwell in (1e-4, 0.3):  # the threshold is the same whatever dwell the ledger holds
        assert walls.dwell_to_strip(q | {"rx.fresh_dwell": dwell}) == pytest.approx(walls.dwell_to_strip(q), rel=1e-9)


def test_still_acid_thins_a_layer_and_cannot_strip_it(q):
    c, s = 101325 * 320.4 / (8.314462618 * 293.15) / 573.0, 0.015 * 998.2  # 23.2 and 15.0 mol/m3
    # Gypsum into acid that holds c of sulfate and no calcium: x (c + x) = (s rho)^2, the positive root.
    x = (math.sqrt(c * c + 4 * s * s) - c) / 2
    assert x == pytest.approx(7.33, rel=0.005) and x * (c + x) == pytest.approx(s * s, rel=1e-12)
    assert walls.acid_takes(q) == pytest.approx(x, rel=1e-9)
    # Less than the calcium at which Tier 0's batch saturates on calcite, (s rho)^2 / c = 9.64 mol/m3, which
    # counts no sulfate from the gypsum itself; and that in turn less than fresh water takes.
    assert walls.saturation_share(q) * c == pytest.approx(s * s / c, rel=1e-9)
    assert s * s / c == pytest.approx(9.64, rel=0.005) and walls.acid_takes(q) < s * s / c < s

    # dd/dt = a / (2 d) - b / (2 sqrt(t)): beneath, the acid that crosses the layer; outside, diffusion into still
    # acid, which takes b sqrt(t) in all. From a bare start d = k sqrt(t) with k^2 + b k - a = 0.
    day = 86400.0
    a = 7.39e-5 * 4.54e-14 * 2 * c  # m2/s
    b = 2 * x * math.sqrt(1e-9 / math.pi) * 7.39e-5  # m per root second
    full = math.sqrt(a * day)  # the layer that grows undisturbed, 3.67 micrometres
    assert b * math.sqrt(day) / full == pytest.approx(1.55, abs=0.005)  # alone, the acid would take 1.55 layers
    left = (math.sqrt(b * b + 4 * a) - b) / 2 * math.sqrt(day) / full
    assert left == pytest.approx(0.4905, abs=0.0005)
    assert walls.left_under_acid(q) == pytest.approx(left, rel=1e-9)

    def rate(t, d):
        return a / (2 * d) - b / (2 * math.sqrt(t))

    def end_and_least(thickness):  # integrated over a day from a microsecond in; tolerance 1 percent below
        d = solve_ivp(rate, (1e-6, day), [thickness], method="LSODA", rtol=1e-10, atol=1e-18).y[0]
        return d[-1] / full, d.min() / full

    assert end_and_least(1e-9)[0] == pytest.approx(left, rel=0.01)  # a nanometre comes up to the same solution
    ended, least = end_and_least(full)  # a whole cycle's layer is thinned to half and never near nothing
    assert ended == pytest.approx(0.511, abs=0.005) and least == pytest.approx(0.418, abs=0.005)
    # The length of the cycle cancels, and however much the acid takes a share of the layer stands.
    assert walls.left_under_acid(q | {"rx.cycle_time": 3600.0}) == pytest.approx(left, rel=1e-9)
    assert 0 < walls.left_under_acid(q | {"rx.ion_diffusivity": 1e-6}) < 0.03


def test_counting_bisulfate_the_acid_takes_more_gypsum_than_fresh_water(led):
    # What acid_takes leaves out. With the ledger's second dissociation constant the batch's free sulfate y obeys
    # Ka2 = H+ y / HSO4-. Free of calcium, H+ = c + y and HSO4- = c - y: 26 percent of the sulfate is free (03 V8).
    # With x of gypsum dissolved, y = (s rho)^2 / x, H+ = c - x + y and HSO4- = c + x - y.
    def counted(c, s, ka2):
        return brentq(lambda x: (c - x + s * s / x) * s * s / x - ka2 * (c + x - s * s / x),
                      2 * s * s / (c + math.hypot(c, 2 * s)), 5 * s)  # from the root without bisulfate upward

    ids = walls.DEPOSIT + ("chem.ka2_sulfuric",)
    q = {i: led.q(i) for i in ids}
    c, s, ka2 = walls._strength(q), walls._solubility(q), q["chem.ka2_sulfuric"]
    assert brentq(lambda y: (c + y) * y - ka2 * (c - y), 0.0, c) / c == pytest.approx(0.26, abs=0.005)
    assert counted(c, s, ka2) / s == pytest.approx(1.11, abs=0.005)
    assert walls.acid_takes(q) / s == pytest.approx(0.49, abs=0.005)
    # At every corner of the ranges the acid takes more than fresh water (1.10 to 1.16 times), and acid_takes less
    # (0.45 to 0.58 times). Taking more thins the layer further and still leaves a share of it standing.
    for corner in itertools.product(*(set(led.rng(i)) for i in ids)):
        q = dict(zip(ids, corner))
        c, s = walls._strength(q), walls._solubility(q)
        assert 0.45 < walls.acid_takes(q) / s < 0.59 and 1.09 < counted(c, s, q["chem.ka2_sulfuric"]) / s < 1.17


def test_a_whole_batch_cannot_lay_down_what_one_fresh_fill_dissolves(q):
    c, s = 101325 * 320.4 / (8.314462618 * 293.15) / 573.0, 0.015 * 998.2
    # Wholly neutralised, the batch keeps s rho of its sulfate dissolved: (c - s) x 573 m3 = 4.74e3 mol of gypsum
    # at the most, against the 8.58e3 mol of 03 check V17. The same as c / (2 s rho) = 0.78 being under one.
    assert (c - s) * 573.0 == pytest.approx(4740, rel=0.002) and s * 573.0 == pytest.approx(8580, rel=0.002)
    assert walls.deposit_over_fill(q) == pytest.approx((c - s) / s, rel=1e-9)
    assert walls.deposit_over_fill(q) == pytest.approx(0.552, abs=0.001)
    assert walls.deposit_over_fill(q | {"kc.volume": 100.0}) == 0.0  # a batch under the solubility deposits nothing


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

    # So does the ledger's own layer under a still fill that stands a hundredth as long as the acid, a tenth of
    # the 0.100 at which it would be stripped: the fill takes 0.32 of a cycle's layer each time.
    run = walls.cycles(q | {"rx.fresh_dwell": 0.01}, "still")
    assert run["after_fill"][0] == pytest.approx((1 - 0.316) * walls.layer_per_cycle(q), rel=0.005)
    assert all(b > a > 0 for a, b in zip(run["after_fill"], run["after_fill"][1:]))
    assert walls.bare_loss(q) < run["loss"][-1] < 1.1 * walls.bare_loss(q)  # the wall is bare only once
