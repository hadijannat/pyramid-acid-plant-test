"""Sulfur(IV) in the Gallery water: speciation, pH, iron-catalysed oxidation; the gas the water cannot take (S22).

Assumptions:
- Concentrations stand for activities, as in 03 check V7; acid-base steps are instantaneous; water's own
  ionisation is left out, so the pH is that of an acid solution.
- The batch is Tier 0's largest: the sulfur of one King's Chamber of the pure gas in one Gallery of water under
  air, with the still surface and the oxygen supply of Tier 0.
- Oxidation follows the ledger's iron law, R = k [Fe(III)] [SO3 2-], which carries no oxygen term; it is cut off
  as the dissolved oxygen runs out.
- S22 credits the rising water with all it could take: every mole of sulfur dioxide, every mole of oxygen the
  oxidation can use, and nitrogen and oxygen up to their solubility in water that arrives free of dissolved gas.
- A full stroke is taken for the least air: the Gallery draws its own volume of gas and the King's Chamber holds
  less, so the rest is the outside air of S14.
"""
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from pyramid.chem.transfer import solubility
from pyramid.screening import _OXYGEN, _SO2, LITRE, O2_PER_SO2, R, _oxygen, _so2_moles

SPECIATION = ("chem.pka1_so2", "chem.pka2_so2")
EQUILIBRIUM = _SO2 + ("gg.volume", "chem.henry_so2") + SPECIATION
OXIDATION = _SO2 + ("gg.volume", "chem.fe_rate_constant", "chem.fe_concentration") + SPECIATION
YIELD = _OXYGEN  # the inputs of Tier 0's oxygen supply
BATCH = tuple(dict.fromkeys(YIELD + OXIDATION + ("chem.ka2_sulfuric",)))  # every input of the batch run
MIXTURE = ("chem.o2_fraction", "chem.henry_o2", "rx.henry_n2", "chem.temperature")
THRESHOLD = ("chem.o2_fraction", "rx.henry_n2", "chem.temperature")
GAS = ("kc.volume", "gg.volume") + MIXTURE
OXYGEN_CUT = 1e-3  # numerical, not physical: the share of air saturation below which the oxidation is switched off


def fractions(h: float, q) -> tuple[float, float, float]:
    """Shares of dissolved sulfur(IV) present as SO2.H2O, HSO3- and SO3 2- at hydrogen-ion concentration h, mol/m3."""
    ka1, ka2 = 10 ** -q["chem.pka1_so2"] * LITRE, 10 ** -q["chem.pka2_so2"] * LITRE  # from mol/L to mol/m3
    total = h * h + ka1 * h + ka1 * ka2
    return h * h / total, ka1 * h / total, ka1 * ka2 / total


def hydrogen(s4: float, s6: float, q) -> float:
    """Hydrogen-ion concentration, mol/m3, of water holding s4 of sulfur(IV) and s6 of sulfate: the charge balance."""
    if s4 + s6 <= 0:
        return 0.0
    k2 = q["chem.ka2_sulfuric"] if s6 else 0.0  # the bisulfate constant matters only where there is sulfate

    def excess(h):  # positive charge less negative charge
        _, bisulfite, sulfite = fractions(h, q)
        sulfate = s6 * (h + 2 * k2) / (h + k2) if s6 else 0.0
        return h - s4 * (bisulfite + 2 * sulfite) - sulfate

    return brentq(excess, 0.0, 2 * (s4 + s6), xtol=1e-14, rtol=1e-13)


def capture_at_equilibrium(q) -> float:
    """Share of the largest batch that the water of the half-full Gallery holds at equilibrium, with dissociation."""
    batch, half, m = _so2_moles(q), q["gg.volume"] / 2, solubility(q)

    def excess(dissolved):  # gas concentration less the one the water's undissociated share balances
        total = dissolved / half
        return (batch - dissolved) / half - fractions(hydrogen(total, 0.0, q), q)[0] * total / m

    return brentq(excess, 0.0, batch, xtol=1e-9 * batch) / batch


def rate_constant(h: float, q) -> float:
    """First-order constant of the iron law on total sulfur(IV), 1/s: k [Fe(III)] times the sulfite share."""
    return q["chem.fe_rate_constant"] * q["chem.fe_concentration"] * fractions(h, q)[2]


def half_life(q) -> float:
    """Seconds for the iron law to halve the sulfur(IV) of the largest batch at its starting pH, oxygen permitting."""
    strength = _so2_moles(q) / q["gg.volume"]
    return math.log(2) / rate_constant(hydrogen(strength, 0.0, q), q)


def yield_ceiling(q, seconds: float) -> float:
    """Share of the largest batch the oxygen held and crossing the still surface can oxidise: Tier 0's ceiling."""
    held, per_second, needed = _oxygen(q)
    return min(1.0, (held + per_second * seconds) / needed)


def oxidise(q, seconds: float, n: int = 200, h: float | None = None, oxygen: bool = True) -> dict:
    """The largest batch over time, mol/m3: sulfur(IV), sulfate, dissolved oxygen, oxygen that crossed the surface.

    h fixes the hydrogen-ion concentration; oxygen=False lifts the oxygen limit. Both serve the benchmark.
    """
    held, per_second, _ = _oxygen(q)
    volume = q["gg.volume"]
    saturation, renewal = held / volume, per_second / held  # mol/m3 at air saturation; k_L A / V in 1/s

    def rate(_, y):
        s4, s6, dissolved, _ = y
        made = rate_constant(hydrogen(s4, s6, q) if h is None else h, q) * s4
        if oxygen:
            made *= max(dissolved, 0.0) / (max(dissolved, 0.0) + OXYGEN_CUT * saturation)
        crossing = renewal * (saturation - dissolved)
        return [-made, made, crossing - O2_PER_SO2 * made, crossing]

    times = np.linspace(0.0, seconds, n)
    start = [_so2_moles(q) / volume, 0.0, saturation, 0.0]
    solution = solve_ivp(rate, (0.0, seconds), start, t_eval=times, method="LSODA", rtol=1e-10, atol=1e-12)
    return {"t": times, "s4": solution.y[0], "s6": solution.y[1], "o2": solution.y[2], "crossed": solution.y[3]}


def least_air(q) -> float:
    """Least share of air in the gas of a full stroke: the Gallery draws more than the King's Chamber holds."""
    return max(0.0, 1 - q["kc.volume"] / q["gg.volume"])


def stoichiometric_air(q) -> float:
    """Share of air in the mixture that carries the oxygen for all its sulfur dioxide, as Tier 0's oxygen ceiling."""
    return 1 - 1 / (1 + O2_PER_SO2 / q["chem.o2_fraction"])


def _capacity(q, henry: str) -> float:
    """Moles of a gas that water holds per mole of gas space it replaces, at the same pressure: H R T."""
    return q[henry] * R * q["chem.temperature"]


def forced_back(q, air: float) -> float:
    """Share of the gas above the water that the rising water must push back, for a given share of air in it."""
    oxygen, nitrogen, sulfur = q["chem.o2_fraction"] * air, (1 - q["chem.o2_fraction"]) * air, 1 - air
    oxygen -= min(oxygen, O2_PER_SO2 * sulfur)  # the oxidation uses all it can
    left = oxygen + nitrogen
    if left <= 0:
        return 0.0
    # One Gallery of water rises through one Gallery of gas, so the volume cancels. The gas left over ends at one
    # atmosphere, each part at its share of it, and the water holds each up to its solubility at that pressure.
    return sum(max(0.0, part - _capacity(q, henry) * part / left)
               for part, henry in ((nitrogen, "rx.henry_n2"), (oxygen, "chem.henry_o2")))


def air_without_pushback(q) -> float:
    """Largest share of air for which nothing is pushed back: its nitrogen just dissolves in the gas-free water.

    Holds while the oxidation uses all the oxygen, which it does for any share below the stoichiometric one.
    """
    return min(1.0, _capacity(q, "rx.henry_n2") / (1 - q["chem.o2_fraction"]))


def sulfur_oxidisable(q, air: float) -> float:
    """Share of the sulfur dioxide that the oxygen of this share of air can oxidise."""
    if air >= 1:  # no sulfur dioxide left to oxidise
        return 1.0
    return min(1.0, q["chem.o2_fraction"] * air / (O2_PER_SO2 * (1 - air)))

