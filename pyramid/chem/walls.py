"""The limestone wall under the acid and its gypsum layer over ten fill and drain cycles (claim S23).

Assumptions:
- Each cycle puts fresh water on the wall, makes Tier 0's strongest batch in it, lets it stand for the cycle
  time and drains it.
- Bare limestone neutralises acid until the batch is saturated with gypsum (Tier 0's share); only then can a
  layer form.
- The layer then grows only as fast as acid diffuses through it (03 section 4.1 item 7), with the measured
  diffusivity of the ledger and the whole acidity of the batch, two hydrogen ions per sulfur, outside it. One
  mole of calcite dissolves for each mole of gypsum laid down.
- The fresh water of the next cycle takes gypsum off the wall, and nothing grows while it stands: up to its
  solubility if it comes to saturation (03 check V17), and at the least what diffusion alone carries into still
  water in the time it stands. That time the hypothesis does not give: it is rx.fresh_dwell, a share of the time
  the acid stands, whose value is the ledger's drain time over its cycle time and whose range runs from the
  shortest drain in the longest cycle to a dwell equal to the acid's.
- The acid of the next batch cannot strip a layer. Free of calcium it is undersaturated, and a layer that covers
  the wall keeps it so, because the batch saturates only on calcium from bare limestone; but the layer grows from
  beneath as the acid dissolves it from outside, the faster the thinner it is. Gypsum dissolving into the acid
  adds its own sulfate to the batch's; calcium and sulfate diffuse alike (rx.ion_diffusivity).
- How much the acid takes is counted twice. With all the batch's sulfate free, as Tier 0 counts it, the acid takes
  the least and the most of the layer is left; with the bisulfate of the ledger's second dissociation constant it
  takes more than fresh water does and about half as much is left. Concentrations stand for activities in both.
- The batch is stronger than the solubility of gypsum (c over s rho is 1.14 at the least over the ledger's
  ranges). A weaker batch could grow no layer, and the layer and the shares of it below would mean nothing.
- The wall is the Gallery's wetted area in the ledger; the Queen's Chamber is left out.
"""
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from pyramid.screening import _SO2, _so2_moles

LAYER = _SO2 + ("gg.volume", "chem.gypsum_h_diffusivity", "chem.gypsum_molar_volume", "rx.cycle_time")
FILL = ("chem.gypsum_solubility", "hydro.water_density", "gg.volume", "gg.wall_area", "chem.gypsum_molar_volume")
STILL = ("chem.gypsum_solubility", "hydro.water_density", "rx.ion_diffusivity", "rx.cycle_time",
         "chem.gypsum_molar_volume", "rx.fresh_dwell")
DEPOSIT = _SO2 + ("gg.volume", "chem.gypsum_solubility", "hydro.water_density")
ACID = LAYER + ("chem.gypsum_solubility", "hydro.water_density", "rx.ion_diffusivity")
BISULFATE = ACID + ("chem.ka2_sulfuric",)
LOSS = LAYER + ("gg.wall_area", "chem.gypsum_solubility", "hydro.water_density", "chem.calcite_molar_volume")
WALL = tuple(dict.fromkeys(LOSS + STILL + BISULFATE))  # every input of the wall model, once
H_PER_SULFUR = 2  # H2SO4 gives two hydrogen ions, and CaCO3 takes two: stoichiometry


def _strength(q) -> float:
    """Sulfate of the strongest batch, mol/m3: Tier 0's sulfur ceiling."""
    return _so2_moles(q) / q["gg.volume"]


def _solubility(q) -> float:
    """Gypsum that water holds, from mol/kg of water to mol/m3."""
    return q["chem.gypsum_solubility"] * q["hydro.water_density"]


def saturation_share(q) -> float:
    """Share of the batch bare limestone neutralises before gypsum saturates: [Ca] = (s rho)^2 / c, as Tier 0."""
    strength = _strength(q)
    return min(strength, _solubility(q) ** 2 / strength) / strength


def growth_product(q) -> float:
    """Vm D C in m2/s: the square of the layer thickness grows by this much each second."""
    return q["chem.gypsum_molar_volume"] * q["chem.gypsum_h_diffusivity"] * H_PER_SULFUR * _strength(q)


def thickness(product: float, seconds, start: float = 0.0):
    """Layer thickness after `seconds` of diffusion-limited growth from `start`: d^2 = d0^2 + Vm D C t.

    The acid flux through the layer is D C / d; two hydrogen ions make one gypsum, so dd/dt = Vm D C / (2 d).
    """
    return np.sqrt(start * start + product * np.asarray(seconds, dtype=float))


def grow(times, product: float, start: float):
    """The same growth integrated in time, from a layer that already has some thickness."""
    solution = solve_ivp(lambda _, d: product / (2 * d), (0.0, float(times[-1])), [start], t_eval=times,
                         method="LSODA", rtol=1e-10, atol=1e-16)
    return solution.y[0]


def layer_per_cycle(q) -> float:
    """Thickness, m, of the layer that grows on a wall bare at the start of one cycle."""
    return float(thickness(growth_product(q), q["rx.cycle_time"]))


def fill_dissolves(q) -> float:
    """Thickness of gypsum, m, that one Gallery of fresh water takes off the wall in coming to saturation."""
    return _solubility(q) * q["gg.volume"] / q["gg.wall_area"] * q["chem.gypsum_molar_volume"]


def acid_takes(q) -> float:
    """Gypsum, mol/m3, that the strongest batch dissolves while it holds no calcium: x (c + x) = (s rho)^2.

    Gypsum brings its own sulfate, so this is less than the calcium at which Tier 0's batch saturates on calcite,
    (s rho)^2 / c, and always less than what fresh water takes, s rho. All the batch's sulfate counts as free, as
    in Tier 0, so this is the least the acid takes; acid_takes_with_bisulfate counts the bisulfate.
    """
    strength, solubility = _strength(q), _solubility(q)
    return 2 * solubility**2 / (strength + math.hypot(strength, 2 * solubility))  # the positive root, no cancellation


def acid_takes_with_bisulfate(q) -> float:
    """The same with the batch's bisulfate counted by the ledger's second dissociation constant, mol/m3.

    Free of calcium the batch holds most of its sulfate as bisulfate (03 check V8), so less of it stands against
    the calcium. With x of gypsum dissolved the free sulfate is y = (s rho)^2 / x, the charges give H+ = c - x + y
    and the sulfate HSO4- = c + x - y, and Ka2 = H+ y / HSO4- fixes x: more than fresh water takes.
    """
    strength, solubility, ka2 = _strength(q), _solubility(q), q["chem.ka2_sulfuric"]

    def excess(x):
        free = solubility**2 / x
        return (strength - x + free) * free - ka2 * (strength + x - free)

    # One sign change between the root with no bisulfate, where HSO4- is nothing, and the x at which H+ would be:
    # H+ y falls and HSO4- rises all the way.
    return brentq(excess, acid_takes(q), (strength + math.hypot(strength, 2 * solubility)) / 2)


def still_fill_dissolves(q) -> float:
    """The least a fresh fill dissolves, m: diffusion alone into still water for its dwell, 2 s sqrt(D f t / pi)."""
    reach = math.sqrt(q["rx.ion_diffusivity"] * q["rx.fresh_dwell"] * q["rx.cycle_time"] / math.pi)
    return 2 * _solubility(q) * reach * q["chem.gypsum_molar_volume"]


def saturating_margin(q) -> float:
    """What a saturating fill dissolves over the layer one cycle grows."""
    return fill_dissolves(q) / layer_per_cycle(q)


def still_margin(q) -> float:
    """What a still fresh fill dissolves over the layer one cycle grows; the cycle time cancels, its dwell does not."""
    return still_fill_dissolves(q) / layer_per_cycle(q)


def dwell_to_strip(q) -> float:
    """Dwell of still fresh water, as a share of the acid's, at which it just dissolves the layer one cycle grows."""
    return q["rx.fresh_dwell"] / still_margin(q) ** 2  # the margin goes as the root of the dwell


def left_under_acid(q, takes=acid_takes) -> float:
    """Share of a cycle's layer that stands at its end under still acid that dissolves it from outside.

    Outside, diffusion into the still acid takes b sqrt(t) in all, b = 2 x sqrt(D_w / pi) Vm with x = takes(q);
    beneath, the acid that crosses the layer adds Vm D C / (2 d) a second: dd/dt = a / (2 d) - b / (2 sqrt(t)).
    The solution from a bare start is d = k sqrt(t) with k^2 + b k - a = 0, and layers that start thicker or
    thinner come to it. Over the layer that grows undisturbed, sqrt(a t), that is 2 / (r + sqrt(r^2 + 4)) with
    r = b / sqrt(a): always above zero, so the acid thins the layer and cannot strip it. With acid_takes, the
    least the acid takes, this is the most that is left.
    """
    reach = math.sqrt(q["rx.ion_diffusivity"] * q["rx.cycle_time"] / math.pi)
    r = 2 * takes(q) * reach * q["chem.gypsum_molar_volume"] / layer_per_cycle(q)
    return 2 / (r + math.hypot(r, 2))


def deposit_over_fill(q) -> float:
    """The most gypsum a batch can lay down over what one fresh fill dissolves: (c - s rho) V over s rho V.

    A batch wholly neutralised on the wall keeps s rho of its sulfate in solution; the rest is the deposit.
    """
    return max(0.0, _strength(q) / _solubility(q) - 1)


def bare_loss(q) -> float:
    """Limestone, m, dissolved from a bare wall in bringing one fresh batch to gypsum saturation."""
    dissolved = saturation_share(q) * _strength(q) * q["gg.volume"] / q["gg.wall_area"]  # mol of calcite per m2
    return dissolved * q["chem.calcite_molar_volume"]


def loss_per_cycle(q) -> float:
    """Limestone, m, lost in a cycle that starts bare: to saturation, then mole for mole under the layer."""
    return bare_loss(q) + layer_per_cycle(q) * q["chem.calcite_molar_volume"] / q["chem.gypsum_molar_volume"]


def cycles(q, fill: str = "saturating", n: int = 10) -> dict:
    """Layer after each acid dwell and after the fill that follows, and the limestone lost so far, all in m."""
    # ponytail: a layer that survives the fill grows undisturbed through the next acid dwell, the thickest it can
    # be. Still acid would thin it (left_under_acid); integrate that sink here if the series must show it.
    removal = {"saturating": fill_dissolves, "still": still_fill_dissolves}[fill](q)
    product, calcite_per_gypsum = growth_product(q), q["chem.calcite_molar_volume"] / q["chem.gypsum_molar_volume"]
    layer, loss, after_acid, after_fill, lost = 0.0, 0.0, [], [], []
    for _ in range(n):
        if layer == 0.0:
            loss += bare_loss(q)
        grown = float(thickness(product, q["rx.cycle_time"], layer))
        loss += (grown - layer) * calcite_per_gypsum
        after_acid.append(grown)
        layer = max(0.0, grown - removal)
        after_fill.append(layer)
        lost.append(loss)
    return {"after_acid": after_acid, "after_fill": after_fill, "loss": lost}
