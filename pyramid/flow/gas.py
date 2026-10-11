"""Gas: where the volume that the draining Gallery displaces comes from (S14, S17).

The Gallery's gas space is one node below outside pressure by dp. Each path into it carries a flow that rises with
dp; solve() finds the dp at which the paths together carry the drain rate. The paths are the antechamber opening in
series with the two King's Chamber shafts (orifice and friction losses, flow as sqrt(dp)), the masonry joints
(laminar slots, flow as dp) and the closed chamber behind Davison's passage, which only gives up the gas it holds.
"""
import math
from functools import lru_cache

from scipy.optimize import brentq

from pyramid.flow.network import OPENING_IDS, SHAFT_IDS, at_the_foot, gallery_openings, quantity, shaft_conductance
from pyramid.screening import G


def orifice(conductance: float, density: float):
    """Flow law of a quadratic loss: Q = conductance sqrt(2 dp / density), conductance = area / sqrt(K) in m2."""
    return lambda dp: conductance * math.sqrt(2 * dp / density)


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


_DRAW = ("gg.volume", "hydro.drain_time", "hydro.air_density", "ante.groove_connected_area", "flow.slab_leak_area",
         "flow.discharge_coefficient", "site.atm_pressure", "hydro.vapour_pressure", "hydro.joint_aperture",
         "hydro.joint_length", "flow.joint_path_length", "hydro.air_kinematic_viscosity", "rc.davison.length",
         "rc.davison.width", "rc.davison.height") + SHAFT_IDS


def opening_area(q) -> float:
    """Open area of the antechamber path with the slabs down: the grooves plus the leak round the slabs, m2."""
    return q["ante.groove_connected_area"] + q["flow.slab_leak_area"]


def antechamber_conductance(q, area: float) -> float:
    """The antechamber opening and, behind the King's Chamber, its two shafts: one path to the outside air."""
    return in_series(q["flow.discharge_coefficient"] * area, shaft_conductance(q))


def draw(q, area: float | None = None, joints: bool = True) -> tuple[float, float, float, float]:
    """One steady draw: (dp in Pa, share through the antechamber path, share through joints, share from storage).

    area replaces the open area of the antechamber path; joints=False leaves only the surveyed openings.
    """
    return _draw(tuple(sorted(q.items())), area, joints)


@lru_cache(maxsize=None)
def _draw(items, area, joints):
    q = dict(items)
    total = q["gg.volume"] / q["hydro.drain_time"]
    density = q["hydro.air_density"]
    # ponytail: air throughout, as in Tier 0's shaft pressure. While the chamber's sulfur dioxide passes the
    # antechamber its conductance is lower by up to sqrt(2.2); carry the gas density per path if that matters.
    paths = [orifice(antechamber_conductance(q, opening_area(q) if area is None else area), density)]
    if joints:
        viscosity = density * q["hydro.air_kinematic_viscosity"]
        paths.append(slot(q["hydro.joint_length"], q["hydro.joint_aperture"], q["flow.joint_path_length"], viscosity))
    # 02 section 4.4: a hanging water column gives way at its vapour pressure, so this is the most it can pull.
    dp, flows = solve(paths, total, q["site.atm_pressure"] - q["hydro.vapour_pressure"])
    # A closed chamber gives up, once, the gas its pressure drop releases: V dp / p. The chamber behind Davison's
    # passage is the only closed space above the water (the four above it were first reached in 1837).
    chamber = q["rc.davison.length"] * q["rc.davison.width"] * q["rc.davison.height"]
    stored = min(1.0, chamber * dp / q["site.atm_pressure"] / q["gg.volume"])
    carried = sum(flows)
    through = [(1 - stored) * flow / carried if carried > 0 else 0.0 for flow in flows]
    return dp, through[0], through[1] if joints else 0.0, stored


@quantity(
    "draw_pressure",
    "Pressure of the Gallery's gas space below the outside air while it drains, joints leaking",
    "Pa",
    "dp solves C sqrt(2 dp / rho) + l_joints b^3 dp / (12 mu l_path) = V_gallery / t_drain; "
    "1/C^2 = 1/(Cd a)^2 + 1/(A_n / sqrt(K_n) + A_s / sqrt(K_s))^2; a = a_grooves + a_slab_leak",
    _DRAW,
)
def draw_pressure(q):
    return draw(q)[0]


@quantity(
    "shaft_share",
    "Share of the displaced volume that comes down the King's Chamber shafts and through the antechamber, "
    "joints leaking",
    "1",
    "share = Q_antechamber / (Q_antechamber + Q_joints), less the gas given up by Davison's chamber",
    _DRAW,
)
def shaft_share(q):
    return draw(q)[1]


_PASSAGE = ("ante.low_passage.width", "ante.low_passage.height")


def passage_area(q) -> float:
    """The antechamber passage as surveyed, with no slab in it: m2."""
    return q["ante.low_passage.width"] * q["ante.low_passage.height"]


@quantity(
    "antechamber_share",
    "Share of the displaced volume drawn through the antechamber passage as surveyed, the masonry gas-tight",
    "1",
    "share = 1 - V_davison dp / (p_atm V_gallery); a = w_passage h_passage; the three openings at the Gallery's "
    "foot are under water",
    _DRAW + _PASSAGE,
)
def antechamber_share(q):
    return draw(q, area=passage_area(q), joints=False)[1]


@quantity(
    "slabs_absent_share",
    "Share drawn through the antechamber passage as surveyed, joints leaking",
    "1",
    "as flow.shaft_share with a = w_passage h_passage",
    _DRAW + _PASSAGE,
)
def slabs_absent_share(q):
    return draw(q, area=passage_area(q))[1]


@quantity(
    "slabs_down_share",
    "Share drawn through the antechamber path with the slabs down, the masonry gas-tight",
    "1",
    "share = 1 - V_davison dp / (p_atm V_gallery) if the path is open, else 0; a = a_grooves + a_slab_leak",
    _DRAW,
)
def slabs_down_share(q):
    return draw(q, joints=False)[1]


def flip_aperture(q, share: float, area: float | None = None) -> float:
    """Joint aperture at which the antechamber path's share falls to `share`: m (storage and the cap left out)."""
    conductance = antechamber_conductance(q, opening_area(q) if area is None else area)
    if conductance == 0:
        return 0.0
    total = q["gg.volume"] / q["hydro.drain_time"]
    dp = q["hydro.air_density"] / 2 * (share * total / conductance) ** 2
    viscosity = q["hydro.air_density"] * q["hydro.air_kinematic_viscosity"]
    slope = (1 - share) * total / dp  # the joints' flow per pascal that leaves the path this share
    return (12 * viscosity * q["flow.joint_path_length"] * slope / q["hydro.joint_length"]) ** (1 / 3)


_FLIP = tuple(id for id in _DRAW if id not in ("hydro.joint_aperture", "site.atm_pressure", "hydro.vapour_pressure",
                                               "rc.davison.length", "rc.davison.width", "rc.davison.height"))


@quantity(
    "joint_aperture_half",
    "Joint aperture at which half the displaced volume still comes down the shafts, the slabs down",
    "m",
    "b = (12 mu l_path (Q / 2) / (l_joints dp))^(1/3); dp = (rho / 2) (Q / (2 C))^2; Q = V_gallery / t_drain",
    _FLIP,
)
def joint_aperture_half(q):
    return flip_aperture(q, 0.5)


@quantity(
    "joint_aperture_nine_tenths",
    "Joint aperture at which nine tenths of the displaced volume still passes the antechamber passage as surveyed",
    "m",
    "b = (12 mu l_path (Q / 10) / (l_joints dp))^(1/3); dp = (rho / 2) (0.9 Q / C)^2; Q = V_gallery / t_drain; "
    "a = w_passage h_passage",
    _FLIP + _PASSAGE,
)
def joint_aperture_nine_tenths(q):
    return flip_aperture(q, 0.9, passage_area(q))


def flip_drain_time(q) -> float:
    """Drain time above which more than half the gas comes down the shafts, the slabs down: s.

    Equal flows through the path, C sqrt(2 dp / rho), and the joints, c dp, meet at Q = 4 C^2 / (rho c).
    """
    conductance = antechamber_conductance(q, opening_area(q))
    viscosity = q["hydro.air_density"] * q["hydro.air_kinematic_viscosity"]
    slope = q["hydro.joint_length"] * q["hydro.joint_aperture"] ** 3 / (12 * viscosity * q["flow.joint_path_length"])
    return q["gg.volume"] * q["hydro.air_density"] * slope / (4 * conductance**2)


@quantity(
    "foot_seal_depth",
    "Depth of water over the Gallery's foot openings that the draw's suction could hold up",
    "m",
    "d = dp / (rho_water g): gas can rise through a foot opening only under less water than this",
    _DRAW + ("hydro.water_density",),
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
