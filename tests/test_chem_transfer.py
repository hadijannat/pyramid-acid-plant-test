"""Benchmarks for the two-film transfer model: the closed vessel, the sulfur balance, the Gallery numbers."""
import math

import numpy as np
import pytest

from pyramid import ledger
from pyramid.chem import transfer


@pytest.fixture(scope="module")
def q() -> dict[str, float]:
    led = ledger.load()
    return {i: led.q(i) for i in transfer.CAPTURE}


def test_closed_vessel_approaches_henry_equilibrium_with_the_analytic_time_constant():
    # 300 m3 of gas over 250 m3 of liquid across 20 m2, K = 2e-4 m/s, solubility ratio 30.
    k, area, v_gas, v_liquid, m = 2e-4, 20.0, 300.0, 250.0, 30.0
    tau = 1 / (k * area * (1 / v_gas + 1 / (m * v_liquid)))  # 72 115 s
    end = 1 / (1 + v_gas / (m * v_liquid))  # 96.2 percent in the liquid at equilibrium
    assert tau == pytest.approx(72115, rel=1e-4) and end == pytest.approx(0.9615, rel=1e-4)

    times = np.array([0.0, tau, 2 * tau, 30 * tau])
    gas, liquid = transfer.integrate(times, k, area, v_gas, v_liquid, m)
    # After one and two time constants the distance from equilibrium is 1/e and 1/e2 of the start. Tolerance 1 percent.
    assert (end - liquid[1]) / end == pytest.approx(math.exp(-1), rel=0.01)
    assert (end - liquid[2]) / end == pytest.approx(math.exp(-2), rel=0.01)
    assert liquid[3] == pytest.approx(end, rel=1e-6)
    assert gas[3] / v_gas == pytest.approx(liquid[3] / (m * v_liquid), rel=1e-6)  # Henry's law holds at the end
    assert transfer.captured(times, k, area, v_gas, v_liquid, m) == pytest.approx(liquid, abs=1e-8)
    assert np.abs(gas + liquid - 1).max() < 1e-9  # sulfur is conserved over the whole run


def test_the_two_films_add_as_resistances():
    # Gas film 1e-3 m/s; liquid film 1e-5 m/s seen from the gas through a solubility ratio of 30: 3e-4 m/s.
    assert transfer.overall_coefficient(1e-3, 1e-5, 30.0) == pytest.approx(1 / (1000 + 1 / 3e-4))
    assert transfer.overall_coefficient(1e-9, 1e-5, 30.0) == pytest.approx(1e-9, rel=1e-4)  # gas film controls
    assert transfer.overall_coefficient(1e3, 1e-5, 30.0) == pytest.approx(3e-4, rel=1e-4)  # liquid film controls


def test_gallery_capture_in_one_day_at_the_ledger_values(q):
    assert transfer.surface(q) == pytest.approx(27.5, rel=0.01)  # 03 check V13: 13.59 m2 / tan 26.28 deg
    m = 0.013 * 8.314462618 * 293.15  # 31.7
    assert transfer.solubility(q) == pytest.approx(m)
    k = 1 / (1 / 1.5e-3 + 1 / (m * 1e-5))  # 2.62e-4 m/s: the liquid film is the larger resistance
    da = k * transfer.surface(q) * 86400 * (2 / 573.0) * (1 + 1 / m)
    expected = (1 - math.exp(-da)) / (1 + 1 / m)
    assert transfer.capture_share(q) == pytest.approx(expected, rel=1e-9)
    assert transfer.capture_share(q) == pytest.approx(0.86, abs=0.01)
    assert transfer.uptake_pace(q) == pytest.approx(k * transfer.surface(q) * 86400 / 573.0, rel=1e-9)

    # Still gas: diffusion alone over 4 m, 3e-6 m/s, brings 2.5 percent across in a day.
    assert transfer.capture_share(q | {"rx.kg_gas": 3e-6}) == pytest.approx(0.025, abs=0.002)
    # The time series is the same model integrated: its last point is the closed form.
    times, share = transfer.capture_series(q, 1.5e-3)
    assert times[-1] == 86400 and share[-1] == pytest.approx(transfer.capture_share(q), rel=1e-6)
    assert np.all(np.diff(share) > 0)
