"""Water: what a reservoir would have to be (S08) and what a full Gallery does to the King's Chamber (S13).

simulate() moves water between prismatic vessels through orifices; the quantities are closed forms of the same
orifice law, so that their ranges can be taken over every corner of the inputs.
"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from pyramid.flow.network import FILLED_IDS, SHAFT_IDS, quantity, shaft_conductance
from pyramid.screening import G, R


def simulate(areas, levels, links, t_end: float, until=None, steps: int = 200):
    """Levels against time of prismatic vessels joined by orifices: (times, levels[time][vessel]).

    areas: plan area of each vessel in m2 (math.inf holds its level); levels: the starting levels in m;
    links: (i, j, sill, cda), an orifice of effective area cda at height sill from vessel i to vessel j, or to
    the open air when j is None; until: (vessel, level) stops the run when that vessel reaches that level.
    """
    areas = np.asarray(areas, dtype=float)

    def rate(_, z):
        dz = np.zeros_like(z)
        for i, j, sill, cda in links:
            up = max(z[i], sill)
            down = sill if j is None else max(z[j], sill)
            flow = cda * math.copysign(math.sqrt(2 * G * abs(up - down)), up - down)  # from i to j, Torricelli
            dz[i] -= flow / areas[i]
            if j is not None:
                dz[j] += flow / areas[j]
        return dz

    events = None
    if until is not None:
        vessel, level = until

        def events(_, z):
            return z[vessel] - level

        events.terminal = True
    solution = solve_ivp(rate, (0.0, t_end), np.asarray(levels, dtype=float), events=events, rtol=1e-10, atol=1e-12,
                         t_eval=np.linspace(0.0, t_end, steps + 1))
    times, history = solution.t, solution.y.T
    if until is not None and solution.t_events[0].size:  # close the series with the moment the level was reached
        times = np.append(times, solution.t_events[0][0])
        history = np.vstack([history, solution.y_events[0][0]])
    return times, history


# --- S08: the reservoir ---------------------------------------------------------------------


@quantity(
    "documented_water_below_chamber",
    "Depth of the highest documented water below the foot of the Descending Passage",
    "m",
    "gap = z_base_asl + z_passage_end - max(z_flood_peak_asl, z_water_table_asl); positive means no water arrives",
    ("site.base_elevation_asl", "dp.south_end.z", "hydro.ok_flood_peak_asl", "hydro.modern_water_table_asl"),
)
def documented_water_below_chamber(q):
    water = max(q["hydro.ok_flood_peak_asl"], q["hydro.modern_water_table_asl"])
    return q["site.base_elevation_asl"] + q["dp.south_end.z"] - water


@quantity(
    "reservoir_level_vessels",
    "Level above sea level that a reservoir must hold to fill the Gallery by communicating vessels alone",
    "m",
    "z_asl = z_base_asl + z_gallery_roof",
    ("site.base_elevation_asl", "gg.roof_top.z"),
)
def reservoir_level_vessels(q):
    return q["site.base_elevation_asl"] + q["gg.roof_top.z"]


@quantity(
    "fill_volume",
    "Water one fill takes: the Gallery, the Queen's Chamber and its passage, the Ascending Passage and the well shaft",
    "m3",
    "V = V_gallery + V_queens + V_niche + V_queens_passage + V_ascending + V_well_shaft",
    FILLED_IDS,
)
def fill_volume(q):
    return sum(q[id] for id in FILLED_IDS)


@quantity(
    "prime_volume",
    "Water that first fills the Subterranean Chamber and the Descending Passage up to pavement level",
    "m3",
    "V = V_chamber + (-z_passage_end / sin(a)) w h",
    ("sub.volume", "dp.south_end.z", "dp.angle", "dp.width", "dp.height"),
)
def prime_volume(q):
    below_pavement = -q["dp.south_end.z"] / math.sin(math.radians(q["dp.angle"]))
    return q["sub.volume"] + below_pavement * q["dp.width"] * q["dp.height"]


@quantity(
    "fill_inflow",
    "Inflow that delivers one fill in the fill time",
    "m3/s",
    "Q = V_fill / t_fill",
    FILLED_IDS + ("flow.fill_time",),
)
def fill_inflow(q):
    return fill_volume(q) / q["flow.fill_time"]


# --- S13: the full Gallery against the King's Chamber ---------------------------------------

_HEAD = ("gg.roof_top.z", "ante.floor.z")
_LOOSE = ("ante.slab_clearance", "ante.slab_width", "ante.groove_connected_area")
_FLOOR = ("kc.length", "kc.width", "ante.length", "ante.width", "ante.passage_to_kc.length", "ante.low_passage.width")


def loose_area(q) -> float:
    """Open area past the slabs as the one surviving fragment gives it, plus the grooves: m2."""
    return q["ante.slab_clearance"] * q["ante.slab_width"] + q["ante.groove_connected_area"]


def flood_area(q) -> float:
    """Floor that the water covers south of the slabs: King's Chamber, its passage and the antechamber, m2."""
    return (q["kc.length"] * q["kc.width"] + q["ante.length"] * q["ante.width"]
            + q["ante.passage_to_kc.length"] * q["ante.low_passage.width"])


@quantity(
    "antechamber_water_head",
    "Height of the water above the antechamber floor with the Gallery full to its roof",
    "m",
    "h = z_gallery_roof - z_antechamber_floor",
    _HEAD,
)
def antechamber_water_head(q):
    return q["gg.roof_top.z"] - q["ante.floor.z"]


@quantity(
    "kc_holdback_pressure",
    "Gas pressure in the King's Chamber that would hold the water of a full Gallery back",
    "Pa",
    "p = rho g (z_gallery_roof - z_antechamber_floor), above the outside air",
    _HEAD + ("hydro.water_density",),
)
def kc_holdback_pressure(q):
    return q["hydro.water_density"] * G * antechamber_water_head(q)


def ingress_rate(q, area: float) -> float:
    """Water through an opening of this area at the antechamber floor, the Gallery full: m3/s."""
    return q["flow.discharge_coefficient"] * area * math.sqrt(2 * G * antechamber_water_head(q))


@quantity(
    "kc_ingress_rate",
    "Water entering towards the King's Chamber past slabs as loose as the surviving fragment, the Gallery full",
    "m3/s",
    "Q = Cd (c_slab w_slab + a_grooves) sqrt(2 g h)",
    _HEAD + _LOOSE + ("flow.discharge_coefficient",),
)
def kc_ingress_rate(q):
    return ingress_rate(q, loose_area(q))


def flood_time(q, area: float) -> float:
    """Time for the water to rise from the King's Chamber floor to its shaft mouths, the Gallery held full: s.

    dz/dt = k sqrt(H - z) with k = Cd a sqrt(2 g) / A gives t = (2 / k) (sqrt(H) - sqrt(H - d)).
    """
    head = q["gg.roof_top.z"] - q["kc.floor.z"]
    k = q["flow.discharge_coefficient"] * area * math.sqrt(2 * G) / flood_area(q)
    return 2 / k * (math.sqrt(head) - math.sqrt(head - q["kcs.mouth_height"]))


@quantity(
    "kc_flood_time",
    "Time for water to stand at the King's Chamber shaft mouths, slabs as loose as the surviving fragment",
    "s",
    "t = (2 A / (Cd a sqrt(2 g))) (sqrt(H) - sqrt(H - d)); H = z_gallery_roof - z_kc_floor; d = mouth height",
    ("gg.roof_top.z", "kc.floor.z", "kcs.mouth_height", "flow.discharge_coefficient") + _LOOSE + _FLOOR,
)
def kc_flood_time(q):
    return flood_time(q, loose_area(q))


@quantity(
    "kc_gaslock_depth",
    "Least depth of water in the King's Chamber if its shafts were shut and its gas were compressed instead",
    "m",
    "p_atm H_kc / (H_kc - d) = p_atm + rho g (H - d), solved for d; H = z_gallery_roof - z_kc_floor",
    ("site.atm_pressure", "hydro.water_density", "gg.roof_top.z", "kc.floor.z", "kc.height"),
)
def kc_gaslock_depth(q):
    # Boyle's law for the chamber's own gas, none escaping; any gas that escapes lets the water rise further.
    # ponytail: the antechamber's gas (18.5 m3 against 320) is left out; add it to the trapped volume if needed.
    p, r = q["site.atm_pressure"], q["hydro.water_density"] * G
    head, height = q["gg.roof_top.z"] - q["kc.floor.z"], q["kc.height"]
    b = p + r * (head + height)
    return (b - math.sqrt(b * b - 4 * r * r * head * height)) / (2 * r)


def so2_density(q) -> float:
    """Density of pure sulfur dioxide at the site pressure and the interior temperature, ideal gas: kg/m3."""
    return q["site.atm_pressure"] * q["chem.molar_mass_so2"] / (R * q["chem.temperature"])


SO2_IDS = ("site.atm_pressure", "chem.molar_mass_so2", "chem.temperature")


@quantity(
    "kc_vent_time",
    "Time for the open shafts to pass one chamber volume of sulfur dioxide under the hold-back pressure",
    "s",
    "t = V_kc / ((A_n / sqrt(K_n) + A_s / sqrt(K_s)) sqrt(2 p / rho_so2))",
    ("kc.volume", "hydro.water_density") + _HEAD + SHAFT_IDS + SO2_IDS,
)
def kc_vent_time(q):
    # ponytail: the incompressible loss law at 0.8 atmospheres of overpressure; a choked-flow law would change
    # the figure by a factor near one, and the point is seconds against the hours of a fill.
    return q["kc.volume"] / (shaft_conductance(q) * math.sqrt(2 * kc_holdback_pressure(q) / so2_density(q)))
