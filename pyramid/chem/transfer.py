"""Two-film transfer of sulfur dioxide from the Gallery gas into the Gallery water (claims S19 and S22).

Assumptions:
- The Gallery is taken half full, the mean of the rise of S18: the gas of S17 above, the water below, meeting at
  the level surface Tier 0 uses (vertical section / tan(slope)).
- Each phase is mixed; the resistance sits in a gas film and a liquid film in series (two-film theory).
- The water takes the undissociated gas in proportion to its pressure (Henry). The dissociation that lets the
  water hold more enters only the equilibrium share (aqueous.capture_at_equilibrium).
- Sulfur dioxide carried out with the air the rising water displaces (S22) is not deducted from the capture.
- The gas is given the whole cycle (rx.cycle_time) over the half-full Gallery, as if the rise lasted that long.
  The gas of S19 stands over the water only until the water has risen, and the ledger's own time for one fill
  (flow.fill_time) is shorter, so S19's basis also gives the share for a contact of that length.
"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from pyramid.screening import _GG_SECTION, R, _gg_section

SURFACE = _GG_SECTION + ("gg.angle",)
CAPTURE = SURFACE + ("gg.volume", "chem.henry_so2", "chem.temperature", "chem.kl_surface", "rx.kg_gas",
                     "rx.cycle_time")


def surface(q) -> float:
    """Level water surface in the inclined Gallery, m2, as Tier 0 takes it for the oxygen supply."""
    return _gg_section(q) / math.tan(math.radians(q["gg.angle"]))


def solubility(q) -> float:
    """Dissolved over gaseous sulfur dioxide concentration at equilibrium, H R T, dimensionless."""
    return q["chem.henry_so2"] * R * q["chem.temperature"]


def overall_coefficient(k_gas: float, k_liquid: float, m: float) -> float:
    """Gas film and liquid film in series, m/s on the gas concentration; m is the solubility ratio."""
    return 1 / (1 / k_gas + 1 / (m * k_liquid))


def time_constant(k: float, area: float, v_gas: float, v_liquid: float, m: float) -> float:
    """Seconds for the distance from Henry equilibrium to fall by e in a closed vessel."""
    return 1 / (k * area * (1 / v_gas + 1 / (m * v_liquid)))


def equilibrium_share(v_gas: float, v_liquid: float, m: float) -> float:
    """Share of the gas that ends in the liquid of a closed vessel."""
    return 1 / (1 + v_gas / (m * v_liquid))


def captured(t, k: float, area: float, v_gas: float, v_liquid: float, m: float):
    """Share of the gas in the liquid after t seconds, starting with all of it in the gas: the closed form."""
    tau = time_constant(k, area, v_gas, v_liquid, m)
    return equilibrium_share(v_gas, v_liquid, m) * (1 - np.exp(-np.asarray(t, dtype=float) / tau))


def integrate(times, k: float, area: float, v_gas: float, v_liquid: float, m: float):
    """(gas, liquid) shares at `times`, integrated from one unit of gas over clean liquid."""

    def rate(_, n):
        flux = k * area * (n[0] / v_gas - n[1] / (m * v_liquid))  # per second, from gas to liquid
        return [-flux, flux]

    solution = solve_ivp(rate, (0.0, float(times[-1])), [1.0, 0.0], t_eval=times, method="LSODA",
                         rtol=1e-10, atol=1e-13)
    if not solution.success:
        raise RuntimeError(solution.message)
    return solution.y[0], solution.y[1]


def _vessel(q) -> tuple[float, float, float, float]:
    """(overall coefficient, surface, half the Gallery volume, solubility ratio) for the half-full Gallery."""
    m = solubility(q)
    return overall_coefficient(q["rx.kg_gas"], q["chem.kl_surface"], m), surface(q), q["gg.volume"] / 2, m


def capture_share(q) -> float:
    """Share of the sulfur dioxide that reaches the water of the half-full Gallery within one cycle."""
    k, area, half, m = _vessel(q)
    return float(captured(q["rx.cycle_time"], k, area, half, half, m))


def time_to_capture(q, share: float) -> float:
    """Seconds for the water of the half-full Gallery to take `share` of the gas; inf if it never holds that much.

    The closed form inverted. Its ceiling is equilibrium_share, Henry's law alone, not the larger share that
    dissociation lets the water hold (aqueous.capture_at_equilibrium).
    """
    k, area, half, m = _vessel(q)
    reach = share / equilibrium_share(half, half, m)
    return -time_constant(k, area, half, half, m) * math.log1p(-reach) if reach < 1 else math.inf


def uptake_pace(q) -> float:
    """Uptake rate over displacement rate for a fill that lasts one cycle: K A t / V (00 section 7)."""
    k, area, _, _ = _vessel(q)
    return k * area * q["rx.cycle_time"] / q["gg.volume"]


def capture_series(q, k_gas: float, n: int = 200):
    """(times, captured share) over one cycle for one gas-side coefficient, integrated in time."""
    k, area, half, m = _vessel(q | {"rx.kg_gas": k_gas})
    times = np.linspace(0.0, q["rx.cycle_time"], n)
    return times, integrate(times, k, area, half, half, m)[1]
