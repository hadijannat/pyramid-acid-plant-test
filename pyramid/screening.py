"""Tier 0 screening: sourced hand calculations, a first verdict per claim, and the table."""
import math
from dataclasses import dataclass
from itertools import product

from pyramid.ledger import Ledger

G = 9.80665  # standard gravity, m/s2


@dataclass(frozen=True)
class Result:
    id: str
    label: str
    value: float
    low: float
    high: float
    unit: str
    formula: str
    inputs: tuple[str, ...]


# One row per Tier 0 quantity: (id, label, unit, formula, inputs, function).
QUANTITIES: list[tuple] = []


def quantity(id: str, label: str, unit: str, formula: str, inputs: tuple[str, ...]):
    """Register a pure function of {ledger id: number} as a Tier 0 quantity."""

    def register(fn):
        QUANTITIES.append((id, label, unit, formula, inputs, fn))
        return fn

    return register


def _evaluate(ledger: Ledger, inputs: tuple[str, ...], fn) -> tuple[float, float, float]:
    """fn at the ledger values, then its least and greatest value over every low/high combination."""
    value = fn({i: ledger.q(i) for i in inputs})
    corners = [fn(dict(zip(inputs, corner))) for corner in product(*(set(ledger.rng(i)) for i in inputs))]
    return value, min(value, *corners), max(value, *corners)


def all_results(ledger: Ledger) -> dict[str, Result]:
    results = {}
    for id, label, unit, formula, inputs, fn in QUANTITIES:
        value, low, high = _evaluate(ledger, inputs, fn)
        results[id] = Result(id, label, value, low, high, unit, formula, inputs)
    return results


# --- Geometry -------------------------------------------------------------------------------


@quantity(
    "t0.kc_volume",
    "King's Chamber volume, floor to ceiling",
    "m3",
    "V = length x width x height",
    ("kc.length", "kc.width", "kc.height"),
)
def kc_volume(q):
    return q["kc.length"] * q["kc.width"] * q["kc.height"]


_GG_SECTION = (
    "gg.slot_width", "gg.ramp_height", "gg.width", "gg.first_lap_height", "gg.height", "gg.overhang", "gg.laps",
)


def _gg_section(q) -> float:
    """Vertical cross-section of the Grand Gallery in m2: ramp slot, lower wall, then the corbel laps."""
    laps = int(q["gg.laps"])
    lap_height = (q["gg.height"] - q["gg.first_lap_height"]) / laps
    narrowing = 2 * q["gg.overhang"] / laps  # width lost at each lap, both sides together
    lap_widths = sum(q["gg.width"] - k * narrowing for k in range(1, laps + 1))
    return (
        q["gg.slot_width"] * q["gg.ramp_height"]
        + q["gg.width"] * (q["gg.first_lap_height"] - q["gg.ramp_height"])
        + lap_height * lap_widths
    )


@quantity(
    "t0.gg_volume",
    "Grand Gallery volume from its surveyed section",
    "m3",
    "V = S (l_floor cos(a) + l_roof) / 2 - V_step; S = slot + lower wall + seven laps; "
    "V_step = (h_step - l_step tan(a) / 2) l_step w",
    _GG_SECTION + ("gg.floor_length", "gg.angle", "gg.roof_length_horizontal", "gg.step_height", "gg.step_length"),
)
def gg_volume(q):
    slope = math.radians(q["gg.angle"])
    mean_length = (q["gg.floor_length"] * math.cos(slope) + q["gg.roof_length_horizontal"]) / 2
    # The Great Step stands on the sloping floor, so its height above the floor shrinks towards the south wall.
    step = (q["gg.step_height"] - q["gg.step_length"] * math.tan(slope) / 2) * q["gg.step_length"] * q["gg.width"]
    return _gg_section(q) * mean_length - step


# --- Hydraulics -----------------------------------------------------------------------------


@quantity(
    "t0.gallery_fill_pressure",
    "Water pressure at the foot of the Descending Passage with the Gallery full",
    "Pa",
    "p = rho g (z_gallery_roof - z_passage_end)",
    ("hydro.water_density", "gg.roof_top.z", "dp.south_end.z"),
)
def gallery_fill_pressure(q):
    return q["hydro.water_density"] * G * (q["gg.roof_top.z"] - q["dp.south_end.z"])


_PISTON = ("hydro.water_density", "gg.roof_top.z", "dp.width", "dp.height")


def _piston_force(q, z_piston: float) -> float:
    """Force on a piston that fills the Descending Passage at height z_piston, with the Gallery full."""
    return q["hydro.water_density"] * G * (q["gg.roof_top.z"] - z_piston) * q["dp.width"] * q["dp.height"]


@quantity(
    "t0.piston_force_passage_end",
    "Force on a piston at the foot of the Descending Passage, Gallery full",
    "N",
    "F = rho g (z_gallery_roof - z_passage_end) w h",
    _PISTON + ("dp.south_end.z",),
)
def piston_force_passage_end(q):
    return _piston_force(q, q["dp.south_end.z"])


@quantity(
    "t0.piston_force_entrance",
    "Force on a piston at the entrance of the Descending Passage, Gallery full",
    "N",
    "F = rho g (z_gallery_roof - z_entrance) w h",
    _PISTON + ("dp.entrance.z",),
)
def piston_force_entrance(q):
    return _piston_force(q, q["dp.entrance.z"])


@quantity(
    "t0.lifting_work",
    "Ideal work to lift one fill from pavement level",
    "J",
    "W = rho g sum(V z_centroid) over the Gallery, the Queen's Chamber with its niche, the Queen's passage, "
    "the Ascending Passage and the well shaft above the pavement",
    (
        "hydro.water_density", "gg.volume", "gg.centroid.z", "qc.volume", "qc.niche.volume", "qc.centroid.z",
        "qp.volume", "qp.centroid.z", "ap.volume", "ap.centroid.z", "ws.volume_above_base",
        "ws.centroid_above_base.z",
    ),
)
def lifting_work(q):
    moments = (
        q["gg.volume"] * q["gg.centroid.z"]
        + (q["qc.volume"] + q["qc.niche.volume"]) * q["qc.centroid.z"]
        + q["qp.volume"] * q["qp.centroid.z"]
        + q["ap.volume"] * q["ap.centroid.z"]
        + q["ws.volume_above_base"] * q["ws.centroid_above_base.z"]
    )
    return q["hydro.water_density"] * G * moments


_STROKE = ("gg.volume", "dp.width", "dp.height")


def _strokes(q, stroke_length: float) -> float:
    """Strokes of a piston sweeping stroke_length of the Descending Passage that equal the Gallery volume."""
    return q["gg.volume"] / (stroke_length * q["dp.width"] * q["dp.height"])


@quantity(
    "t0.strokes_full_passage",
    "Strokes to fill the Gallery if a stroke sweeps the whole Descending Passage",
    "1",
    "N = V_gallery / (l_passage w h)",
    _STROKE + ("dp.length",),
)
def strokes_full_passage(q):
    return _strokes(q, q["dp.length"])


@quantity(
    "t0.strokes_below_junction",
    "Strokes to fill the Gallery if a stroke sweeps the passage below the Ascending Passage junction",
    "1",
    "N = V_gallery / ((l_passage - l_to_junction) w h)",
    _STROKE + ("dp.length", "dp.junction_distance"),
)
def strokes_below_junction(q):
    return _strokes(q, q["dp.length"] - q["dp.junction_distance"])


@quantity(
    "t0.strokes_below_pavement",
    "Strokes to fill the Gallery if a stroke sweeps the passage below pavement level",
    "1",
    "N = V_gallery / ((-z_passage_end / sin(a)) w h)",
    _STROKE + ("dp.south_end.z", "dp.angle"),
)
def strokes_below_pavement(q):
    return _strokes(q, -q["dp.south_end.z"] / math.sin(math.radians(q["dp.angle"])))


@quantity(
    "t0.suction_margin",
    "Suction-lift margin for a pump at the foot of the Descending Passage at the Old Kingdom flood peak",
    "m",
    "margin = (p_atm - p_vapour) / (rho g) - (z_base_asl + z_passage_end - z_flood_asl); negative means no draw",
    (
        "site.atm_pressure", "hydro.vapour_pressure", "hydro.water_density", "site.base_elevation_asl",
        "dp.south_end.z", "hydro.ok_flood_peak_asl",
    ),
)
def suction_margin(q):
    limit = (q["site.atm_pressure"] - q["hydro.vapour_pressure"]) / (q["hydro.water_density"] * G)
    lift = q["site.base_elevation_asl"] + q["dp.south_end.z"] - q["hydro.ok_flood_peak_asl"]
    return limit - lift


@quantity(
    "t0.shaft_draw_pressure",
    "Pressure drop that draws replacement air down both King's Chamber shafts while the Gallery drains",
    "Pa",
    "dp = K_n rho_air v_n^2 / 2; v_n = (V_gallery / t_drain) / (A_n + A_s sqrt(K_n / K_s))",
    (
        "gg.volume", "hydro.drain_time", "kcs.north.width", "kcs.north.height", "kcs.south.width",
        "kcs.south.height", "hydro.kcs_north_loss_coefficient", "hydro.kcs_south_loss_coefficient",
        "hydro.air_density",
    ),
)
def shaft_draw_pressure(q):
    flow = q["gg.volume"] / q["hydro.drain_time"]
    area_north = q["kcs.north.width"] * q["kcs.north.height"]
    area_south = q["kcs.south.width"] * q["kcs.south.height"]
    k_north, k_south = q["hydro.kcs_north_loss_coefficient"], q["hydro.kcs_south_loss_coefficient"]
    # The shafts are in parallel, so they share one pressure drop: K_n v_n^2 = K_s v_s^2.
    speed_north = flow / (area_north + area_south * math.sqrt(k_north / k_south))
    return k_north * q["hydro.air_density"] * speed_north**2 / 2


@quantity(
    "t0.joint_leak_rate",
    "Leak-off through the Gallery's masonry joints if they stand open",
    "m3/s",
    "Q = l_joints rho g b^3 i / (12 mu)",
    (
        "hydro.joint_length", "hydro.water_density", "hydro.joint_aperture", "hydro.leak_gradient",
        "hydro.water_viscosity",
    ),
)
def joint_leak_rate(q):
    per_metre = (
        q["hydro.water_density"] * G * q["hydro.joint_aperture"] ** 3 * q["hydro.leak_gradient"]
        / (12 * q["hydro.water_viscosity"])
    )
    return q["hydro.joint_length"] * per_metre
