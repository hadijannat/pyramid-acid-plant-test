"""Benchmarks for the aqueous model: speciation, the iron law's half-life, the element balances, Tier 0's ceiling."""
import math

import numpy as np
import pytest

from pyramid import ledger, screening
from pyramid.chem import aqueous


@pytest.fixture(scope="module")
def led() -> ledger.Ledger:
    return ledger.load()


@pytest.fixture(scope="module")
def q(led) -> dict[str, float]:
    ids = set(aqueous.EQUILIBRIUM + aqueous.BATCH + aqueous.GAS)
    return {i: led.q(i) for i in ids}


def test_speciation_reproduces_the_checks_of_03(q):
    # V6: at pH 1.7 the sulfite share is 1.22e-6. Concentrations are in mol/m3, so pH 1.7 is 19.95 mol/m3.
    h = 10 ** -1.7 * 1000
    molecular, bisulfite, sulfite = aqueous.fractions(h, q)
    assert sulfite == pytest.approx(1.22e-6, rel=0.01)
    assert molecular + bisulfite + sulfite == pytest.approx(1.0)
    # V5: 0.0232 mol/L of sulfur(IV) leaves 0.0113 mol/L undissociated, in balance with 0.0085 atm.
    h = aqueous.hydrogen(23.2, 0.0, q)
    undissociated = aqueous.fractions(h, q)[0] * 23.2
    assert undissociated == pytest.approx(11.3, rel=0.01)
    assert undissociated / q["chem.henry_so2"] / 101325 == pytest.approx(0.0085, rel=0.02)
    # The charge balance closes: hydrogen ions equal bisulfite plus twice sulfite.
    _, bisulfite, sulfite = aqueous.fractions(h, q)
    assert h == pytest.approx(23.2 * (bisulfite + 2 * sulfite), rel=1e-10)
    # V7: 0.0232 mol/L of sulfuric acid stands at pH 1.53 with log K = 1.988 for the bisulfate.
    assert -math.log10(aqueous.hydrogen(0.0, 23.2, q) / 1000) == pytest.approx(1.53, abs=0.01)
    assert aqueous.hydrogen(0.0, 0.0, q) == 0.0


def test_first_order_oxidation_reproduces_the_half_life_of_the_iron_law(q):
    # At a fixed pH of 1.7 and with oxygen to spare the ledger's law is first order in sulfur(IV):
    # k [Fe] x sulfite share = 1200 m3/mol/s x 0.01 mol/m3 x 1.22e-6 = 1.47e-5 per second, a half-life of 13 h.
    h = 10 ** -1.7 * 1000
    ka1, ka2 = 10 ** -1.9 * 1000, 10 ** -7.2 * 1000
    sulfite = ka1 * ka2 / (h * h + ka1 * h + ka1 * ka2)
    expected = math.log(2) / (1200.0 * 0.01 * sulfite)
    assert expected == pytest.approx(13.1 * 3600, rel=0.01)

    run = aqueous.oxidise(q, 2 * expected, n=201, h=h, oxygen=False)
    assert run["t"][100] == pytest.approx(expected)
    assert run["s4"][100] / run["s4"][0] == pytest.approx(0.5, rel=0.01)  # tolerance 1 percent
    assert run["s4"][200] / run["s4"][0] == pytest.approx(0.25, rel=0.01)
    # V6's rate at 0.02 mol/L: 2.9e-7 mol/L/s, which is 2.9e-4 mol/m3/s.
    assert aqueous.rate_constant(h, q) * 20.0 == pytest.approx(2.9e-4, rel=0.02)


def test_sulfur_and_oxygen_balance_over_a_cycle_to_1e_9(q):
    run = aqueous.oxidise(q, 86400.0)
    sulfur = run["s4"] + run["s6"]
    assert np.abs(sulfur / sulfur[0] - 1).max() < 1e-9
    # Oxygen: what is dissolved plus half a mole in each mole of sulfate, less what crossed the surface.
    oxygen = run["o2"] + 0.5 * run["s6"] - run["crossed"]
    assert np.abs(oxygen - oxygen[0]).max() < 1e-9 * sulfur[0]
    assert run["s4"][0] == pytest.approx(13319.4 / 573.0, rel=1e-4)  # the batch starts at Tier 0's sulfur ceiling
    assert run["o2"][0] == pytest.approx(0.276, rel=0.01)  # air saturation, 03 check V13
    assert run["o2"].min() > -1e-9


def test_the_yield_is_capped_by_the_oxygen_as_tier_0_has_it(led, q):
    tier0 = screening.all_results(led)
    assert aqueous.yield_ceiling(q, screening.DAY) == pytest.approx(tier0["t0.sulfate_yield_day"].value, rel=1e-6)
    assert aqueous.oxidise(q, 86400.0)["s4"][0] == pytest.approx(tier0["t0.acid_ceiling_sulfur"].value, rel=1e-6)
    # The iron law would oxidise the batch in hours (half-life 5.9 h at the start), so the oxygen decides: the run
    # ends just under the ceiling, short by the oxygen still dissolved at the cut-off.
    assert aqueous.half_life(q) == pytest.approx(5.9 * 3600, rel=0.02)
    run = aqueous.oxidise(q, 86400.0)
    made = run["s6"][-1] / run["s4"][0]
    assert made <= aqueous.yield_ceiling(q, 86400.0)
    assert made == pytest.approx(tier0["t0.sulfate_yield_day"].value, rel=0.01)


def test_equilibrium_capture_of_the_largest_batch(q):
    share = aqueous.capture_at_equilibrium(q)
    # Without dissociation the half-full Gallery holds 1 / (1 + 1 / (H R T)) = 96.9 percent; dissociation adds to it.
    assert 1 / (1 + 1 / (0.013 * 8.314462618 * 293.15)) < share < 1
    assert share == pytest.approx(0.981, abs=0.003)


def test_the_gas_the_rising_water_must_push_back(q):
    # Emptying the whole Gallery draws 573 m3 and the King's Chamber holds 320.4 m3: 44.1 percent of the gas is air.
    air = aqueous.least_air(q)
    assert air == pytest.approx(1 - 320.4 / 573.0)
    # Its nitrogen is 0.7905 x 0.441 = 34.9 percent of the gas; the oxygen (9.2 percent) is all used by the 55.9
    # percent of sulfur dioxide; gas-free water holds H R T = 6.4e-6 x 8.314 x 293.15 = 1.56 percent of nitrogen.
    held = 6.4e-6 * 8.314462618 * 293.15
    assert aqueous.forced_back(q, air) == pytest.approx(0.7905 * air - held, rel=1e-9)
    assert aqueous.forced_back(q, air) == pytest.approx(0.333, abs=0.001)
    # The stoichiometric mixture of Tier 0 is 29.5 percent sulfur dioxide: 55.7 percent nitrogen.
    stoichiometric = aqueous.stoichiometric_air(q)
    assert 1 - stoichiometric == pytest.approx(0.295, abs=0.001)
    assert aqueous.forced_back(q, stoichiometric) == pytest.approx(0.7905 * stoichiometric - held, rel=1e-9)
    # With more air than that, oxygen is left over as well: pure air goes back but for what dissolves.
    left = 1.0 - held * 0.7905 - 1.3e-5 * 8.314462618 * 293.15 * 0.2095
    assert aqueous.forced_back(q, 1.0) == pytest.approx(left, rel=1e-9)
    # Nothing goes back only below 2 percent of air, which carries oxygen for under 1 percent of the sulfur.
    limit = aqueous.air_without_pushback(q)
    assert limit == pytest.approx(held / 0.7905) and limit == pytest.approx(0.0197, abs=0.0002)
    assert aqueous.forced_back(q, limit) == pytest.approx(0.0, abs=1e-12)
    assert aqueous.forced_back(q, 0.0) == 0.0 and aqueous.forced_back(q, 1.01 * limit) > 0
    assert aqueous.sulfur_oxidisable(q, limit) == pytest.approx(0.0084, abs=0.0002)
    assert aqueous.sulfur_oxidisable(q, stoichiometric) == pytest.approx(1.0)
