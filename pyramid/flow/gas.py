"""Gas: where the volume that the draining Gallery displaces comes from (S14, S17).

The Gallery's gas space is one node below outside pressure by dp. Each path into it carries a flow that rises with
dp; at every water level dp is where the paths together carry the drain rate. The paths are the antechamber opening
in series with the two King's Chamber shafts (orifice and friction losses, flow as sqrt(dp)), the masonry joints
(laminar slots, flow as dp) and the closed chamber behind Davison's passage, which only gives up the gas it holds.

The Gallery drains from full, and the antechamber opening, at the top of the Great Step, then lies under water:
until the surface has fallen to the opening's top, gas enters there only by the suction in excess of the water
standing over it. So the draw is summed over the water level. solve() is the general solver; split() is the closed
form of its case of one orifice and one leak, which the sum over levels uses, and the tests hold one against the
other.
"""
import math
from functools import lru_cache

import numpy as np
from scipy.optimize import brentq

from pyramid.flow.network import OPENING_IDS, SHAFT_IDS, at_the_foot, gallery_openings, quantity, shaft_conductance
from pyramid.screening import G


def orifice(conductance: float, density: float, head: float = 0.0):
    """Flow law of a quadratic loss: Q = conductance sqrt(2 (dp - head) / density), conductance = area / sqrt(K), m2.

    head is the pressure of the water standing over a submerged opening, Pa: no gas enters until dp exceeds it.
    """
    return lambda dp: conductance * math.sqrt(2 * max(0.0, dp - head) / density)


def slot(length: float, aperture: float, path: float, viscosity: float):
    """Flow law of laminar flow between parallel faces: Q = length aperture^3 dp / (12 viscosity path)."""
    return lambda dp: length * aperture**3 * dp / (12 * viscosity * path)


def in_series(*conductances: float) -> float:
    """Conductance of quadratic losses in series: their loss coefficients add, so 1/C^2 = sum of 1/C_i^2."""
    if min(conductances) <= 0:
        return 0.0
    return 1 / math.sqrt(sum(1 / c**2 for c in conductances))


def solve(paths, total: float, cap: float) -> tuple[float, list[float]]:
    """The pressure difference at which the paths together carry `total`, and each path's flow there.

    Every path's flow rises with dp, so the root is unique and bisection (Brent) finds it. If even `cap`, the most
    suction a draining water column can apply, does not draw `total`, the paths carry what they carry at the cap.
    """
    def carried(dp):
        return sum(path(dp) for path in paths)

    if carried(cap) <= total:
        dp = cap
    else:
        dp = brentq(lambda dp: carried(dp) - total, 0.0, cap, xtol=1e-13, rtol=1e-15)
    return dp, [path(dp) for path in paths]


def split(total: float, conductance: float, density: float, slope: float, heads, cap: float):
    """One orifice under water and one leak that is linear in dp, sharing `total`: (dp, orifice flow, leak flow).

    heads: the water pressure over the orifice at each level, Pa (an array); slope: the leak's flow per pascal.
    conductance sqrt(2 (dp - head) / density) + slope dp = total is a quadratic in u = sqrt(dp - head). Where the
    leak carries `total` at a dp below the head, the orifice passes nothing. As in solve(), dp stops at `cap`.
    """
    heads = np.asarray(heads, dtype=float)
    k = conductance * math.sqrt(2 / density)
    if k == 0 and slope == 0:
        dp = np.full_like(heads, cap)  # nothing is open: the water hangs at the most it can pull
    else:
        spare = np.maximum(total - slope * heads, 0.0)  # what the leak has not supplied when dp reaches the head
        root = k + np.sqrt(k * k + 4 * slope * spare)
        u = np.divide(2 * spare, root, out=np.zeros_like(spare), where=root > 0)  # the positive root; fits slope = 0
        dp = np.minimum(np.where(spare > 0, heads + u * u, total / slope if slope > 0 else cap), cap)
    return dp, k * np.sqrt(np.maximum(dp - heads, 0.0)), slope * dp


# The Gallery's section (as Tier 0 builds it), its slope and the levels of the antechamber opening.
_POCKET = ("gg.slot_width", "gg.ramp_height", "gg.width", "gg.first_lap_height", "gg.height", "gg.overhang",
           "gg.laps", "gg.floor_length", "gg.angle", "gg.south_end.z", "ante.floor.z", "ante.low_passage.height")


def section_bands(q) -> list[tuple[float, float, float]]:
    """The Gallery's vertical section as (from, to, width) above the local floor, m: slot, lower wall, the laps."""
    laps = int(q["gg.laps"])
    lap_height = (q["gg.height"] - q["gg.first_lap_height"]) / laps
    narrowing = 2 * q["gg.overhang"] / laps  # width lost at each lap, both sides together
    bands = [(0.0, q["gg.ramp_height"], q["gg.slot_width"]),
             (q["gg.ramp_height"], q["gg.first_lap_height"], q["gg.width"])]
    for k in range(1, laps + 1):
        low = q["gg.first_lap_height"] + (k - 1) * lap_height
        bands.append((low, low + lap_height, q["gg.width"] - k * narrowing))
    return bands


def pocket_share(q, level: float) -> float:
    """Share of the Gallery that lies above `level`, m above the pavement: the gas pocket under the sloping roof.

    The Gallery is its section carried along the slope. With the surface h0 above the floor's upper end, the
    pocket reaches (y - h0) / tan(a) down the Gallery at the height y of the section, so its volume is the
    integral of w(y) (y - h0) dy / tan(a), set against S l cos(a). Good while the pocket stops short of the
    north wall, which it does down to the level of the floor's upper end and below.
    """
    # ponytail: no end walls and no Great Step, so the whole is 584 m3 against the ledger's 573; the south wall's
    # overhang would take about 3 percent off the pocket. Build both from pyramid.geometry if that matters.
    h0 = level - q["gg.south_end.z"]
    bands = section_bands(q)
    moment = sum(w * ((high - h0) ** 2 - (max(low, h0) - h0) ** 2) / 2 for low, high, w in bands if high > h0)
    slope = math.radians(q["gg.angle"])
    whole = sum(w * (high - low) for low, high, w in bands) * q["gg.floor_length"] * math.cos(slope)
    return moment / math.tan(slope) / whole


def opening_depth(q) -> float:
    """Water over the top of the antechamber opening with the Gallery full to its roof: m."""
    return q["gg.south_end.z"] + q["gg.height"] - q["ante.floor.z"] - q["ante.low_passage.height"]


STEPS = 512  # water levels between the roof and the opening's top; a test sets them against eight times as many


@lru_cache(maxsize=None)
def _phase(pocket: tuple[float, ...], steps: int = STEPS):
    """The draw by water level: (water over the opening's top in m, share of the Gallery displaced there).

    First the roof, where the draw starts and nothing is displaced yet; then `steps` levels down to the opening's
    top, each with the share of the Gallery between its edges; last the rest, displaced with the opening clear.
    """
    q = dict(zip(_POCKET, pocket))
    top = q["ante.floor.z"] + q["ante.low_passage.height"]
    # ponytail: the opening passes gas freely from the moment the surface reaches its top, though it is 1.1 m
    # tall and a further 5 percent of the Gallery drains while it is partly covered. Open it in steps if needed.
    edges = np.linspace(top + opening_depth(q), top, steps + 1)
    displaced = np.array([pocket_share(q, level) for level in edges])
    depths = np.concatenate(([opening_depth(q)], (edges[:-1] + edges[1:]) / 2 - top, [0.0]))
    return depths, np.concatenate(([0.0], np.diff(displaced), [1 - displaced[-1]]))


def summed(total, conductance, density, slope, cap, water, pocket, submerged=True, steps=STEPS):
    """(dp at the start, dp with the opening clear, the orifice's share of the whole draw, the leak's share)."""
    depths, shares = _phase(pocket, steps)
    heads = water * G * depths if submerged else np.zeros_like(depths)
    dp, through, leak = split(total, conductance, density, slope, heads, cap)
    carried = through + leak
    parts = [np.divide(flow, carried, out=np.zeros_like(carried), where=carried > 0) for flow in (through, leak)]
    return float(dp[0]), float(dp[-1]), float(shares @ parts[0]), float(shares @ parts[1])


_summed_once = lru_cache(maxsize=None)(summed)  # many corners of the ledger's ranges are the same draw


_DRAW = ("gg.volume", "hydro.drain_time", "hydro.air_density", "ante.groove_connected_area", "flow.slab_leak_area",
         "flow.discharge_coefficient", "site.atm_pressure", "hydro.vapour_pressure", "hydro.joint_aperture",
         "hydro.joint_length", "flow.joint_path_length", "hydro.air_kinematic_viscosity", "rc.davison.length",
         "rc.davison.width", "rc.davison.height") + SHAFT_IDS
# The submerged phase needs the Gallery's section and levels and the water's density. Their ranges move the share
# displaced under water by a few percent of itself (flow.submerged_share carries them), and thirteen draw inputs
# already make 8192 corners, so they stay at their ledger values while a draw's range is taken.
_PHASE = _POCKET + ("hydro.water_density",)
SWEPT = _DRAW


def opening_area(q) -> float:
    """Open area of the antechamber path with the slabs down: the grooves plus the leak round the slabs, m2."""
    return q["ante.groove_connected_area"] + q["flow.slab_leak_area"]


def series_area(q) -> float:
    """One opening that passes what the three slabs' clearances pass one after another: m2.

    opening_area counts the clearance of one slab, which is how 01 gives it; three slabs stand in the antechamber's
    slots. The grooves are in the south wall, so they are counted beside the last slab only.
    """
    leak, slabs = q["flow.slab_leak_area"], int(q["ante.slot_count"])
    return in_series(*[leak] * (slabs - 1), leak + q["ante.groove_connected_area"])


def antechamber_conductance(q, area: float) -> float:
    """The antechamber opening and, behind the King's Chamber, its two shafts: one path to the outside air."""
    return in_series(q["flow.discharge_coefficient"] * area, shaft_conductance(q))


def joint_slope(q) -> float:
    """Flow per pascal through the masonry joints, m3/(s Pa): the slot law over the whole joint length."""
    viscosity = q["hydro.air_density"] * q["hydro.air_kinematic_viscosity"]
    return slot(q["hydro.joint_length"], q["hydro.joint_aperture"], q["flow.joint_path_length"], viscosity)(1.0)


def suction_cap(q) -> float:
    """02 section 4.4: a hanging water column gives way at its vapour pressure, so this is the most it can pull."""
    return q["site.atm_pressure"] - q["hydro.vapour_pressure"]


def draw(q, area: float | None = None, joints: bool = True, submerged: bool = True) -> tuple[float, ...]:
    """One draw from the full Gallery: (dp in Pa once the antechamber opening is clear of the water, share through
    the antechamber path, share through joints, share from storage).

    area replaces the open area of the antechamber path; joints=False leaves only the surveyed openings;
    submerged=False is the draw as if the antechamber opening were never under water.
    """
    return _draw(tuple(sorted(q.items())), area, joints, submerged)[:4]


def start_pressure(q, area: float | None = None, joints: bool = True) -> float:
    """dp at the start of the draw, the antechamber opening under the whole depth of water: Pa."""
    return _draw(tuple(sorted(q.items())), area, joints, True)[4]


@lru_cache(maxsize=None)
def _draw(items, area, joints, submerged):
    q = dict(items)
    # ponytail: air throughout, as in Tier 0's shaft pressure. While the chamber's sulfur dioxide passes the
    # antechamber its conductance is lower by up to sqrt(2.2); carry the gas density per path if that matters.
    conductance = antechamber_conductance(q, opening_area(q) if area is None else area)
    start, dp, through, leaked = _summed_once(
        q["gg.volume"] / q["hydro.drain_time"], conductance, q["hydro.air_density"],
        joint_slope(q) if joints else 0.0, suction_cap(q), q["hydro.water_density"],
        tuple(q[id] for id in _POCKET), submerged)
    # A closed chamber gives up the gas its pressure drop releases, V dp / p, and takes it back as dp falls: over
    # the whole draw it has given what the last dp releases. The chamber behind Davison's passage is the only
    # closed space above the water (the four above it were first reached in 1837).
    # ponytail: what it lends while the opening is under water and dp is high is left out. That gas is repaid
    # later, at the later mix, so the antechamber's share is understated by at most V (dp_start - dp) / (p V_g).
    chamber = q["rc.davison.length"] * q["rc.davison.width"] * q["rc.davison.height"]
    stored = min(1.0, chamber * dp / q["site.atm_pressure"] / q["gg.volume"])
    return dp, (1 - stored) * through, (1 - stored) * leaked, stored, start


@quantity(
    "submerged_share",
    "Share of the Gallery displaced before the falling water surface reaches the top of the antechamber opening",
    "1",
    "share = integral of w(y) (y - h0) dy / (tan(a) S l_floor cos(a)); h0 = z_antechamber_floor + h_passage - "
    "z_floor_south; S = slot + lower wall + seven laps of width w(y)",
    _POCKET,
)
def submerged_share(q):
    return pocket_share(q, q["ante.floor.z"] + q["ante.low_passage.height"])


@quantity(
    "draw_pressure",
    "Pressure of the Gallery's gas space below the outside air once the antechamber opening is clear of the water, "
    "joints leaking",
    "Pa",
    "dp solves C sqrt(2 dp / rho) + l_joints b^3 dp / (12 mu l_path) = V_gallery / t_drain; "
    "1/C^2 = 1/(Cd a)^2 + 1/(A_n / sqrt(K_n) + A_s / sqrt(K_s))^2; a = a_grooves + a_slab_leak",
    _DRAW + _PHASE,
    held=_PHASE,
)
def draw_pressure(q):
    return draw(q)[0]


@quantity(
    "start_pressure",
    "Pressure of the Gallery's gas space below the outside air at the start of the draw, the antechamber opening "
    "under water, joints leaking",
    "Pa",
    "dp solves C sqrt(2 max(0, dp - rho_water g d) / rho) + l_joints b^3 dp / (12 mu l_path) = V_gallery / t_drain; "
    "d = z_floor_south + h_gallery - z_antechamber_floor - h_passage; dp stops at p_atm - p_vapour",
    _DRAW + _PHASE,
    held=_PHASE,
)
def start_pressure_result(q):
    return start_pressure(q)


@quantity(
    "shaft_share",
    "Share of the displaced volume that comes down the King's Chamber shafts and through the antechamber, "
    "joints leaking",
    "1",
    "share = sum over the water levels of dV Q_antechamber / (Q_antechamber + Q_joints), less the gas given up by "
    "Davison's chamber; Q_antechamber = C sqrt(2 max(0, dp - rho_water g d) / rho) while the water stands d over "
    "the opening's top",
    _DRAW + _PHASE,
    held=_PHASE,
)
def shaft_share(q):
    return draw(q)[1]


_PASSAGE = ("ante.low_passage.width", "ante.low_passage.height")  # the height is also one of _PHASE's levels


def passage_area(q) -> float:
    """The antechamber passage as surveyed, with no slab in it: m2."""
    return q["ante.low_passage.width"] * q["ante.low_passage.height"]


@quantity(
    "antechamber_share",
    "Share of the displaced volume drawn through the antechamber passage as surveyed, the masonry gas-tight",
    "1",
    "share = 1 - V_davison dp / (p_atm V_gallery); a = w_passage h_passage; the three openings at the Gallery's "
    "foot are under water, and gas enters the antechamber opening against the water over it",
    _DRAW + _PASSAGE[:1] + _PHASE,
    held=_PHASE,
)
def antechamber_share(q):
    return draw(q, area=passage_area(q), joints=False)[1]


@quantity(
    "slabs_absent_share",
    "Share drawn through the antechamber passage as surveyed, joints leaking",
    "1",
    "as flow.shaft_share with a = w_passage h_passage",
    _DRAW + _PASSAGE[:1] + _PHASE,
    held=_PHASE,
)
def slabs_absent_share(q):
    return draw(q, area=passage_area(q))[1]


@quantity(
    "slabs_down_share",
    "Share drawn through the antechamber path with the slabs down, the masonry gas-tight",
    "1",
    "share = 1 - V_davison dp / (p_atm V_gallery) if the path is open, else 0; a = a_grooves + a_slab_leak",
    _DRAW + _PHASE,
    held=_PHASE,
)
def slabs_down_share(q):
    return draw(q, joints=False)[1]


def flip_aperture(q, share: float, area: float | None = None) -> float:
    """Joint aperture at which the antechamber path's share of the whole draw falls to `share`: m (storage left
    out)."""
    conductance = antechamber_conductance(q, opening_area(q) if area is None else area)
    if conductance == 0:
        return 0.0
    slope = _flip_slope(share, q["gg.volume"] / q["hydro.drain_time"], conductance, q["hydro.air_density"],
                        suction_cap(q), q["hydro.water_density"], tuple(q[id] for id in _POCKET))
    viscosity = q["hydro.air_density"] * q["hydro.air_kinematic_viscosity"]
    return (12 * viscosity * q["flow.joint_path_length"] * slope / q["hydro.joint_length"]) ** (1 / 3)


@lru_cache(maxsize=None)
def _flip_slope(share, total, conductance, density, cap, water, pocket):
    """The joints' flow per pascal that leaves the path this share: the share falls steadily as the joints open,
    from all of the draw to none of it, so the root is unique."""
    def excess(log_slope):
        return summed(total, conductance, density, math.exp(log_slope), cap, water, pocket)[2] - share

    return math.exp(brentq(excess, math.log(1e-15), math.log(1e3), xtol=1e-10))


_FLIP = tuple(id for id in _DRAW if id not in ("hydro.joint_aperture", "rc.davison.length", "rc.davison.width",
                                               "rc.davison.height"))


@quantity(
    "joint_aperture_half",
    "Joint aperture at which half the displaced volume still comes down the shafts, the slabs down",
    "m",
    "b at which flow.shaft_share is 1/2 before the gas from Davison's chamber is taken off; found by bisection, "
    "the share falling as the joints open",
    _FLIP + _PHASE,
    held=_PHASE,
)
def joint_aperture_half(q):
    return flip_aperture(q, 0.5)


@quantity(
    "joint_aperture_nine_tenths",
    "Joint aperture at which nine tenths of the displaced volume still passes the antechamber passage as surveyed",
    "m",
    "b at which flow.slabs_absent_share is 9/10 before the gas from Davison's chamber is taken off; found by "
    "bisection, the share falling as the joints open; a = w_passage h_passage",
    _FLIP + _PASSAGE[:1] + _PHASE,
    held=_PHASE,
)
def joint_aperture_nine_tenths(q):
    return flip_aperture(q, 0.9, passage_area(q))


def flip_drain_time(q, fastest: float, slowest: float) -> tuple[float, str] | None:
    """Drain time between the two at which half the gas comes down the shafts, the slabs down, and whether more
    than half does in a "slower" or a "faster" drain: (s, word). None if the share does not cross one half there.

    A slower drain helps once the opening is clear and hurts while it is under water, so the share can turn
    round between the two ends; with the ledger's joints it rises all the way.
    """
    def excess(time):
        return draw(q | {"hydro.drain_time": time})[1] - 0.5

    if excess(fastest) * excess(slowest) >= 0:
        return None
    return brentq(excess, fastest, slowest, rtol=1e-9), "slower" if excess(slowest) > 0 else "faster"


@quantity(
    "foot_seal_depth",
    "Depth of water over the Gallery's foot openings that the draw's suction could hold up once the antechamber "
    "opening is clear",
    "m",
    "d = dp / (rho_water g): gas can rise through a foot opening only under less water than this",
    _DRAW + _PHASE,
    held=_POCKET,
)
def foot_seal_depth(q):
    return draw(q)[0] / (q["hydro.water_density"] * G)


@quantity(
    "foot_wedge_share",
    "Share of the Gallery's volume below the tops of the three openings at its foot, at most",
    "1",
    "share < (d^2 / (2 tan(a))) w / V_gallery; d = the tallest foot opening's top above the Gallery's lowest point",
    OPENING_IDS + ("gg.angle", "gg.width", "gg.volume"),
)
def foot_wedge_share(q):
    # The water left when the surface reaches the top of the tallest foot opening is a wedge on the sloping floor;
    # taking the Gallery's full width for it (the slot between the ramps is half as wide) makes this an upper bound.
    depth = max(o.level + o.height for o in gallery_openings(q) if at_the_foot(q, o)) - q["gg.north_end.z"]
    return depth**2 / (2 * math.tan(math.radians(q["gg.angle"]))) * q["gg.width"] / q["gg.volume"]
