"""Tier 0 screening: sourced hand calculations, a first verdict per claim, and the table."""
import json
import math
from dataclasses import asdict, dataclass
from itertools import product

from pyramid import REPO_ROOT
from pyramid.ledger import Ledger, load
from pyramid.provenance import write_manifest

G = 9.80665  # standard gravity, m/s2
R = 8.314462618  # molar gas constant, J/mol/K
O2_PER_SO2 = 0.5  # stoichiometry of SO2 + 1/2 O2 -> SO3: a reaction coefficient, not a measurement
YEAR = 365.25 * 24 * 3600  # seconds in a year, for readable verdict sentences


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


# --- Chemistry ------------------------------------------------------------------------------

_SO2 = ("site.atm_pressure", "kc.volume", "chem.temperature")


def _so2_moles(q) -> float:
    """Ideal-gas amount of pure sulfur dioxide that fills the King's Chamber at one atmosphere."""
    return q["site.atm_pressure"] * q["kc.volume"] / (R * q["chem.temperature"])


@quantity(
    "t0.so2_inventory",
    "Sulfur dioxide the King's Chamber holds if filled with the pure gas",
    "mol",
    "n = p V / (R T)",
    _SO2,
)
def so2_inventory(q):
    return _so2_moles(q)


@quantity(
    "t0.acid_ceiling_sulfur",
    "Acid strength ceiling set by the sulfur in one King's Chamber of gas",
    "mol/m3",
    "c = n_SO2 / V_gallery",
    _SO2 + ("gg.volume",),
)
def acid_ceiling_sulfur(q):
    return _so2_moles(q) / q["gg.volume"]


@quantity(
    "t0.acid_ceiling_oxygen",
    "Acid strength ceiling if the oxygen must arrive in the same Gallery-volume of drawn gas",
    "mol/m3",
    "c = x p / (R T); x = 1 / (1 + 0.5 / x_O2), the sulfur dioxide share of a stoichiometric mixture with air",
    ("site.atm_pressure", "chem.temperature", "chem.o2_fraction"),
)
def acid_ceiling_oxygen(q):
    so2_share = 1 / (1 + O2_PER_SO2 / q["chem.o2_fraction"])
    # One Gallery-volume of gas dissolves in one Gallery-volume of water, so the volume cancels.
    return so2_share * q["site.atm_pressure"] / (R * q["chem.temperature"])


@quantity(
    "t0.temperature_rise",
    "Adiabatic temperature rise of the Gallery water for the largest batch",
    "K",
    "dT = -dH c / (rho cp); c = n_SO2 / V_gallery",
    _SO2 + ("gg.volume", "chem.dh_so2_to_sulfate", "hydro.water_density", "chem.water_cp"),
)
def temperature_rise(q):
    concentration = _so2_moles(q) / q["gg.volume"]
    return -q["chem.dh_so2_to_sulfate"] * concentration / (q["hydro.water_density"] * q["chem.water_cp"])


@quantity(
    "t0.oxygen_supply_time",
    "Time for the oxygen of one full batch to cross the still water surface in the Gallery",
    "s",
    "t = (0.5 n_SO2 - c_O2 V_gallery) / (k_L c_O2 A); c_O2 = H x_O2 p; A = S / tan(a)",
    _SO2 + _GG_SECTION + ("gg.angle", "gg.volume", "chem.henry_o2", "chem.o2_fraction", "chem.kl_surface"),
)
def oxygen_supply_time(q):
    dissolved = q["chem.henry_o2"] * q["chem.o2_fraction"] * q["site.atm_pressure"]  # mol/m3 at air saturation
    surface = _gg_section(q) / math.tan(math.radians(q["gg.angle"]))  # level water in the inclined Gallery
    shortfall = O2_PER_SO2 * _so2_moles(q) - dissolved * q["gg.volume"]
    return shortfall / (q["chem.kl_surface"] * dissolved * surface)


@quantity(
    "t0.gas_phase_lifetime",
    "Shortest possible lifetime of sulfur dioxide against uncatalysed oxidation in air",
    "s",
    "t = 1 / (k n_O2); k = Z exp(-E / (R T)); E = dfH(SO3) + dfH(O) - dfH(SO2); n_O2 = x_O2 p / (k_B T)",
    (
        "chem.collision_prefactor", "chem.dfh_so3", "chem.dfh_o_atom", "chem.dfh_so2", "chem.kinetics_temperature",
        "chem.o2_fraction", "site.atm_pressure", "chem.boltzmann",
    ),
)
def gas_phase_lifetime(q):
    barrier = q["chem.dfh_so3"] + q["chem.dfh_o_atom"] - q["chem.dfh_so2"]  # SO2 + O2 -> SO3 + O
    rate = q["chem.collision_prefactor"] * math.exp(-barrier / (R * q["chem.kinetics_temperature"]))
    oxygen = q["chem.o2_fraction"] * q["site.atm_pressure"] / (q["chem.boltzmann"] * q["chem.kinetics_temperature"])
    return 1 / (rate * oxygen)


# --- Electricity ----------------------------------------------------------------------------


@quantity(
    "t0.lightning_strikes",
    "Direct lightning strikes on the pyramid per year, at most",
    "1/yr",
    "N = N_g pi (3 H)^2 C_d, the collection area of a pointed structure; N_g counts all lightning",
    ("em.flash_density", "em.collection_slope", "pyr.height_original", "em.location_factor"),
)
def lightning_strikes(q):
    radius = q["em.collection_slope"] * q["pyr.height_original"]
    return q["em.flash_density"] * math.pi * radius**2 * q["em.location_factor"]


@quantity(
    "t0.relaxation_limestone",
    "Charge relaxation time of the limestone masonry",
    "s",
    "tau = eps0 eps_r rho",
    ("em.eps0", "em.limestone_eps", "em.limestone_resistivity"),
)
def relaxation_limestone(q):
    return q["em.eps0"] * q["em.limestone_eps"] * q["em.limestone_resistivity"]


@quantity(
    "t0.relaxation_granite",
    "Charge relaxation time of the granite, driest measured case",
    "s",
    "tau = eps0 eps_r / sigma",
    ("em.eps0", "em.granite_eps", "em.granite_conductivity"),
)
def relaxation_granite(q):
    return q["em.eps0"] * q["em.granite_eps"] / q["em.granite_conductivity"]


_SKIN = ("em.mu0", "em.eps0", "em.limestone_eps", "em.limestone_resistivity")


def _skin_depth(q, frequency: float) -> float:
    """Depth at which a wave in the limestone falls to 1/e, from the general lossy-medium formula."""
    omega = 2 * math.pi * frequency
    loss_tangent = 1 / (q["em.limestone_resistivity"] * omega * q["em.eps0"] * q["em.limestone_eps"])
    attenuation = (
        omega
        * math.sqrt(q["em.mu0"] * q["em.eps0"] * q["em.limestone_eps"] / 2)
        * math.sqrt(math.sqrt(1 + loss_tangent**2) - 1)
    )
    return 1 / attenuation


@quantity(
    "t0.skin_depth_resonance",
    "Skin depth in the masonry at the 2018 study's first resonance",
    "m",
    "1/delta = w sqrt(mu0 eps0 eps_r / 2) sqrt(sqrt(1 + t^2) - 1); t = 1 / (rho w eps0 eps_r); "
    "w = 2 pi c0 / wavelength",
    _SKIN + ("em.c0", "paper.peak1.wavelength"),
)
def skin_depth_resonance(q):
    return _skin_depth(q, q["em.c0"] / q["paper.peak1.wavelength"])


@quantity(
    "t0.skin_depth_lightning",
    "Skin depth in the masonry at a lightning return-stroke frequency",
    "m",
    "1/delta = w sqrt(mu0 eps0 eps_r / 2) sqrt(sqrt(1 + t^2) - 1); t = 1 / (rho w eps0 eps_r); w = 2 pi f",
    _SKIN + ("em.lightning_frequency",),
)
def skin_depth_lightning(q):
    return _skin_depth(q, q["em.lightning_frequency"])


# --- Piezoelectricity and acoustics ---------------------------------------------------------


@quantity(
    "t0.piezo_displacement",
    "Surface displacement of the granite in a lightning-level field",
    "m",
    "u = d E L",
    ("em.granite_piezo_d", "em.piezo_field_lightning", "em.piezo_thickness"),
)
def piezo_displacement(q):
    return q["em.granite_piezo_d"] * q["em.piezo_field_lightning"] * q["em.piezo_thickness"]


@quantity(
    "t0.piezo_intensity",
    "Sound intensity that displacement radiates into air during the stroke's rise",
    "W/m2",
    "I = Z_air v^2 / 2; v = d E L / t_rise",
    ("em.granite_piezo_d", "em.piezo_field_lightning", "em.piezo_thickness", "em.pulse_rise_time", "ac.air_impedance"),
)
def piezo_intensity(q):
    speed = piezo_displacement(q) / q["em.pulse_rise_time"]
    return q["ac.air_impedance"] * speed**2 / 2


_PIEZO_LEVEL = ("em.granite_piezo_d", "em.air_breakdown_field", "ac.air_impedance", "ac.reference_pressure")


def _piezo_level(q, thickness: float, frequency: float) -> float:
    """Sound level in dB that a slab radiates into air when driven at the air-breakdown field."""
    speed = 2 * math.pi * frequency * q["em.granite_piezo_d"] * q["em.air_breakdown_field"] * thickness
    return 20 * math.log10(q["ac.air_impedance"] * speed / math.sqrt(2) / q["ac.reference_pressure"])


def _transmission_loss(z1: float, z2: float) -> float:
    """Intensity lost in dB on crossing from a medium of impedance z1 into one of impedance z2."""
    return -10 * math.log10(4 * z1 * z2 / (z1 + z2) ** 2)


@quantity(
    "t0.leaf_sound_level",
    "Sound level from the antechamber's granite leaf driven at the air-breakdown field",
    "dB",
    "L = 20 log10(Z_air v / sqrt(2) / p_ref); v = 2 pi f d E L_leaf",
    _PIEZO_LEVEL + ("ante.leaf_thickness", "ac.drive_frequency"),
)
def leaf_sound_level(q):
    return _piezo_level(q, q["ante.leaf_thickness"], q["ac.drive_frequency"])


@quantity(
    "t0.required_sound_level",
    "Sound level in air needed to cavitate a wet film from the gas side",
    "dB",
    "L = 10 log10(I_cav Z_air / p_ref^2) - 10 log10(4 Z_air Z_water / (Z_air + Z_water)^2)",
    ("ac.cavitation_intensity", "ac.air_impedance", "ac.water_impedance", "ac.reference_pressure"),
)
def required_sound_level(q):
    # the level of a wave in air that carries the cavitation intensity, plus what is lost on entering the liquid
    carried = 10 * math.log10(q["ac.cavitation_intensity"] * q["ac.air_impedance"] / q["ac.reference_pressure"] ** 2)
    return carried + _transmission_loss(q["ac.air_impedance"], q["ac.water_impedance"])


@quantity(
    "t0.slab_source_level",
    "Sound level from the Queen's Chamber shaft slab driven at the air-breakdown field",
    "dB",
    "L = 20 log10(Z_air v / sqrt(2) / p_ref); v = 2 pi f d E L_slab, with the granite coefficient lent to limestone",
    _PIEZO_LEVEL + ("qcs.slab_thickness", "ac.link_frequency"),
)
def slab_source_level(q):
    return _piezo_level(q, q["qcs.slab_thickness"], q["ac.link_frequency"])


@quantity(
    "t0.shaft_link_loss",
    "Path loss from the south slab to the north slab of the Queen's Chamber shafts at 13 kHz",
    "dB",
    "loss = alpha (l_south + l_north) + 2 (T(air, stone) + T(stone, water)); "
    "T(a, b) = -10 log10(4 Z_a Z_b / (Z_a + Z_b)^2); soft limestone, liquid at both shaft mouths",
    (
        "ac.absorption_13khz", "qcs.south.length_to_slab", "qcs.north.length_to_slab", "ac.air_impedance",
        "ac.soft_limestone_impedance", "ac.water_impedance",
    ),
)
def shaft_link_loss(q):
    air = q["ac.absorption_13khz"] * (q["qcs.south.length_to_slab"] + q["qcs.north.length_to_slab"])
    stone = q["ac.soft_limestone_impedance"]
    barrier = _transmission_loss(q["ac.air_impedance"], stone) + _transmission_loss(stone, q["ac.water_impedance"])
    return air + 2 * barrier  # two barriers: the stone left uncut at each shaft mouth


@quantity(
    "t0.vein_contrast",
    "Vein-to-rock conductivity contrast a vein needs to carry current over the link length",
    "1",
    "K = 2 pi l^2 / (A ln(2 l / a)); a = sqrt(A / pi)",
    ("plateau.vein_leakage_length", "plateau.vein_area"),
)
def vein_contrast(q):
    length, area = q["plateau.vein_leakage_length"], q["plateau.vein_area"]
    radius = math.sqrt(area / math.pi)
    return 2 * math.pi * length**2 / (area * math.log(2 * length / radius))


# --- Quantities that decide the remaining tier 0 claims -------------------------------------


@quantity(
    "t0.ram_delivered_fraction",
    "Share of its drive water that a hydraulic ram delivers to the Gallery roof",
    "1",
    "q/Q = efficiency x fall / lift; fall = -z_passage_end, from a supply at pavement level; "
    "lift = z_gallery_roof - z_passage_end",
    ("hydro.ram_efficiency", "dp.south_end.z", "gg.roof_top.z"),
)
def ram_delivered_fraction(q):
    fall = -q["dp.south_end.z"]  # the ram sits at the passage's foot and its supply stands at the pavement, Z = 0
    lift = q["gg.roof_top.z"] - q["dp.south_end.z"]
    return q["hydro.ram_efficiency"] * fall / lift


@quantity(
    "t0.pit_clearance",
    "Height of the pit bottom, as it stood before 1837, above the Old Kingdom flood peak",
    "m",
    "h = z_base_asl + z_pit_bottom - z_flood_asl; positive means the pit ends above the water",
    ("site.base_elevation_asl", "pit.original_bottom.z", "hydro.ok_flood_peak_asl"),
)
def pit_clearance(q):
    return q["site.base_elevation_asl"] + q["pit.original_bottom.z"] - q["hydro.ok_flood_peak_asl"]


@quantity(
    "t0.boiling_margin",
    "Margin to boiling if the first of the claimed fills takes the whole heat of the largest batch",
    "K",
    "margin = T_boil - T_water - N dT; dT = -dH c / (rho cp); c = n_SO2 / V_gallery; N = number of claimed fills",
    _SO2 + (
        "gg.volume", "chem.dh_so2_to_sulfate", "hydro.water_density", "chem.water_cp", "hydro.claimed_strokes",
        "chem.water_boiling_point",
    ),
)
def boiling_margin(q):
    # The heat that warms the whole Gallery by dT warms the first of N equal fills by N dT.
    first_fill_rise = q["hydro.claimed_strokes"] * temperature_rise(q)
    return q["chem.water_boiling_point"] - q["chem.temperature"] - first_fill_rise


@quantity(
    "t0.gypsum_saturation_loss",
    "Share of the strongest batch that bare limestone neutralises before gypsum can coat it",
    "1",
    "x = min(1, (s rho / c)^2); c = n_SO2 / V_gallery; gypsum saturates at [Ca] = (s rho)^2 / c, "
    "and each calcium ion dissolved has neutralised one molecule of acid",
    _SO2 + ("gg.volume", "chem.gypsum_solubility", "hydro.water_density"),
)
def gypsum_saturation_loss(q):
    solubility = q["chem.gypsum_solubility"] * q["hydro.water_density"]  # from mol/kg of water to mol/m3
    acid = _so2_moles(q) / q["gg.volume"]
    return min(1.0, (solubility / acid) ** 2)  # the wall cannot neutralise more than all of the acid


@quantity(
    "t0.hcl_partial_pressure",
    "Hydrogen chloride pressure over the dilute acid and salt mixture",
    "Pa",
    "p = [H+] [Cl-] / H_effective",
    ("chem.khafre_h", "chem.khafre_chloride", "chem.henry_hcl_effective"),
)
def hcl_partial_pressure(q):
    return q["chem.khafre_h"] * q["chem.khafre_chloride"] / q["chem.henry_hcl_effective"]


def _bessel_i0(x: float) -> float:
    """Modified Bessel function of the first kind and order zero, summed from its power series."""
    # 30 terms are exact to rounding for x below about 10, and x is at most 2.0 here; use scipy.special.i0 beyond that
    return sum((x * x / 4) ** k / math.factorial(k) ** 2 for k in range(30))


@quantity(
    "t0.arrhenius_gain",
    "Speed-up of a dry-gas reaction by the temperature swing of the strongest airborne ultrasound",
    "1",
    "gain = I0(E dT / (R T^2)); dT = T (gamma - 1) / gamma x p_peak / p_atm; p_peak = sqrt(2) p_ref 10^(L / 20)",
    (
        "ac.best_airborne_level", "ac.reference_pressure", "ac.heat_capacity_ratio", "chem.temperature",
        "site.atm_pressure", "ac.arrhenius_barrier",
    ),
)
def arrhenius_gain(q):
    peak = math.sqrt(2) * q["ac.reference_pressure"] * 10 ** (q["ac.best_airborne_level"] / 20)
    gamma, temperature = q["ac.heat_capacity_ratio"], q["chem.temperature"]
    swing = temperature * (gamma - 1) / gamma * peak / q["site.atm_pressure"]  # adiabatic, in kelvin
    return _bessel_i0(q["ac.arrhenius_barrier"] * swing / (R * temperature**2))


# --- First verdicts -------------------------------------------------------------------------
# Each rule takes the ledger and the results and returns (status, one-sentence basis).


def _three_way(holds_at_worst: bool, holds_at_best: bool) -> str:
    """pass if the test holds even at the unfavourable end, fail if it fails even at the favourable end."""
    return "pass" if holds_at_worst else "conditional" if holds_at_best else "fail"


def _s09(ledger, r):
    # 01 premise P1: the only stated source is a reservoir at pavement level (Z = 0), which nothing on site attests.
    # No number changes that, so the status is fixed; heights in the ledger are already measured from the pavement.
    return "conditional", (
        f"Water standing at the level of an assumed pavement-level reservoir stops {ledger.q('ws.top.z'):.1f} m "
        f"below the top of the well shaft and {ledger.q('gg.roof_top.z'):.1f} m below the Gallery roof, so the "
        "step holds only with that reservoir and a pump."
    )


def _s10(ledger, r):
    low, high = r["t0.piston_force_entrance"].value, r["t0.piston_force_passage_end"].value
    pressure = r["t0.gallery_fill_pressure"].value
    return "undefined", (
        f"The hypothesis names no actuator or seal for the pump, which must push with {low / 1e6:.2f} to "
        f"{high / 1e6:.2f} MN depending on its position and hold {pressure / 1e6:.2f} MPa with the Gallery full."
    )


def _s11(ledger, r):
    margin = r["t0.suction_margin"]
    status = _three_way(margin.low >= 0, margin.high >= 0)
    return status, (
        f"The suction margin of a pump at the foot of the Descending Passage is {margin.value:.1f} m at the Old "
        f"Kingdom flood peak and {margin.high:.1f} m at the most favourable documented levels, against the 0 m "
        "it needs to draw."
    )


def _four_strokes(ledger, r):
    claimed = ledger.q("hydro.claimed_strokes")
    counts = [r[f"t0.strokes_{stroke}"] for stroke in ("full_passage", "below_junction", "below_pavement")]
    near, upper = 0.75 * claimed, 1.25 * claimed  # within 25 percent of the claimed number
    always_near = [near <= count.low and count.high <= upper for count in counts]  # near over the whole range
    sometimes_near = [count.low <= upper and near <= count.high for count in counts]  # near somewhere in it
    return _three_way(all(always_near), any(sometimes_near)), (
        f"Filling the Gallery alone takes {counts[0].value:.1f} strokes ({counts[0].low:.1f} to {counts[0].high:.1f} "
        "over the ranges of the inputs) if a stroke sweeps the whole Descending Passage, "
        f"{counts[1].value:.1f} ({counts[1].low:.1f} to {counts[1].high:.1f}) if it sweeps the part below the "
        f"Ascending Passage junction and {counts[2].value:.1f} ({counts[2].low:.1f} to {counts[2].high:.1f}) if it "
        f"sweeps the part below the pavement, against the {claimed:.0f} claimed, and the hypothesis fixes no stroke."
    )


def _s07(ledger, r):
    supplied, needed = r["t0.leaf_sound_level"], r["t0.required_sound_level"]
    status = _three_way(supplied.low >= needed.value, supplied.high >= needed.value)
    return status, (
        f"The granite leaf driven at the air-breakdown field radiates {supplied.value:.0f} dB, and "
        f"{supplied.high:.0f} dB with every input at its generous end, against the {needed.value:.0f} dB needed "
        "to cavitate a wet film."
    )


def _s16(ledger, r):
    lifetime = r["t0.gas_phase_lifetime"]
    shortest_pass, longest_pass = ledger.rng("hydro.drain_time")
    most = -math.expm1(-longest_pass / lifetime.low)  # most favourable: longest pass, shortest lifetime
    least = -math.expm1(-shortest_pass / lifetime.high)  # least favourable: shortest pass, longest lifetime
    status = "pass" if least >= 0.10 else "fail" if most < 0.001 else "conditional"
    return status, (
        f"At the collision limit, sulfur dioxide lasts {lifetime.value:.1e} s ({lifetime.value / YEAR:.1e} "
        f"years) against oxygen with no catalyst, so a pass of {shortest_pass / 60:.0f} min to "
        f"{longest_pass / 3600:.0f} h converts a fraction of {most:.0e} at most and {least:.0e} at the least."
    )


def _s20(ledger, r):
    time = r["t0.oxygen_supply_time"]
    status = "pass" if time.high <= 86400 else "conditional"  # 86400 s: within a day counts as quickly
    if time.value >= YEAR:
        needs = f"{time.value / YEAR:.1f} to {time.high / YEAR:.0f} years"
    else:
        needs = f"{time.value / 3600:.1f} to {time.high / 3600:.1f} h"
    if status == "pass":
        outcome = "within the day that counts as quick"
    elif time.low > 86400:
        outcome = (
            "so quick oxidation holds only if something aerates the water, which the hypothesis does not describe"
        )
    else:
        outcome = (
            "so quick oxidation holds over only part of the ranges of the inputs, and the hypothesis describes no "
            "aeration that would make up the rest"
        )
    return status, (
        f"The oxygen for a full batch needs {needs} to cross the still water surface in the Gallery, {outcome}."
    )


def _s24(ledger, r):
    rise = r["t0.temperature_rise"]
    status = "pass" if rise.low >= 20 else "conditional" if rise.high >= 5 else "fail"
    against = {
        "pass": "at least the 20 K that would justify a heat exchanger",
        "conditional": "which leaves open whether a heat exchanger matters, between the 5 K at which it would start "
        "to and the 20 K that would justify one",
        "fail": "below the 5 K at which a heat exchanger would start to matter",
    }[status]
    return status, (
        f"The largest possible batch warms the Gallery water by {rise.value:.1f} K ({rise.high:.1f} K at most), "
        f"{against}."
    )


def _s25(ledger, r):
    source, loss = r["t0.slab_source_level"], r["t0.shaft_link_loss"]
    received = source.value - loss.value
    worst = source.low - loss.high  # least favourable: weakest source, longest loss
    # Judgement call: the criterion's source (05 section 5.5) allows ten times the measured coefficient, 20 dB more.
    # source.high is not used: it lends the slab a microscope-scale granite value 500 times the bulk one.
    best = source.value + 20 - loss.low
    status = "pass" if worst >= 10 else "conditional" if best >= 10 else "fail"
    return status, (
        f"A slab driven at the air-breakdown field emits {source.value:.0f} dB and the path to the north slab "
        f"loses {loss.value:.0f} dB at {ledger.q('ac.link_frequency') / 1000:.0f} kHz, so the signal arrives at "
        f"{round(received)} dB ({round(worst)} dB at the least), against the 10 dB needed above a 0 dB noise floor."
    )


def _s30(ledger, r):
    sulfur, oxygen = r["t0.acid_ceiling_sulfur"], r["t0.acid_ceiling_oxygen"]
    status = "fail" if sulfur.high < 5 else "undefined"  # 5 mol/m3 is the fail line, 0.005 mol/L
    return status, (
        "The hypothesis gives no gas fraction or target strength, and pure sulfur dioxide at one atmosphere caps "
        f"the product at {sulfur.value:.0f} mol/m3, or {oxygen.value:.0f} mol/m3 if its oxygen comes with the same "
        "draw of air."
    )


def _s31(ledger, r):
    strikes = r["t0.lightning_strikes"]
    return "undefined", (
        f"Direct strikes come at most {strikes.value:.2f} times per year, one every {1 / strikes.value:.0f} years, "
        "and the hypothesis states no cycle rate to compare this with."
    )


def _e22(ledger, r):
    granite, limestone = r["t0.relaxation_granite"], r["t0.relaxation_limestone"]
    # a storm field changes over about 1 s; shorter by an order of magnitude or more fails
    status = "pass" if granite.low >= 1 else "conditional" if granite.high >= 0.1 else "fail"
    return status, (
        f"Charge in the granite relaxes in {granite.value * 1e3:.1f} ms in the driest measured case "
        f"({granite.high * 1e3:.0f} ms at most) and in the limestone in {limestone.value * 1e9:.0f} ns, against a "
        "storm field that changes over seconds."
    )


def _veins(ledger, r):
    needed = r["t0.vein_contrast"].value
    host, (host_low, host_high) = ledger.q("plateau.host_resistivity"), ledger.rng("plateau.host_resistivity")
    specular = ledger.rng("plateau.hematite_resistivity_specular")[0]  # the most conductive hematite measured
    earthy_best, earthy = ledger.rng("plateau.hematite_resistivity_earthy")  # the most and the least conductive
    status = _three_way(host_low / earthy >= needed, host_high / specular >= needed)
    return status, (
        f"A vein must conduct {needed:.1e} times better than the rock to carry current "
        f"{ledger.q('plateau.vein_leakage_length'):.0f} m; the best measured specular hematite reaches "
        f"{host / specular:.1e} times in {host:.0f} ohm m rock and {host_high / specular:.1e} times in the most "
        f"resistive {host_high:.0f} ohm m rock, earthy red hematite reaches {host_high / earthy_best:.1e} times at "
        "most, and no Giza vein has been measured."
    )


def _s21(ledger, r):
    margin, rise = r["t0.boiling_margin"], r["t0.temperature_rise"]
    fills = ledger.q("hydro.claimed_strokes")
    status = _three_way(margin.low > 0, margin.high > 0)
    outcome = {
        "pass": "nothing boils over with or without the dilute-acid step",
        "conditional": "boiling over cannot be excluded",
        "fail": "the water boils over",
    }[status]
    return status, (
        f"If the first of the {fills:.0f} claimed fills took the whole heat of the largest batch, it would "
        f"warm by {fills * rise.value:.1f} K and leave a margin of {margin.value:.1f} K below boiling "
        f"({margin.low:.1f} K at the least), so {outcome}."
    )


def _s27(ledger, r):
    pressure, atm = r["t0.hcl_partial_pressure"], ledger.q("site.atm_pressure")
    # the criterion's lines: pass from 1e-3 atm, fail below 1e-5 atm
    status = "pass" if pressure.low >= 1e-3 * atm else "conditional" if pressure.high >= 1e-5 * atm else "fail"
    return status, (
        f"Hydrogen chloride stands at {pressure.value / atm:.1e} atm over the dilute acid and salt mixture, and "
        f"at {pressure.high / atm:.1e} atm over saturated brine, against the 1e-05 atm below which the criterion "
        "fails the claim."
    )


def _e14(ledger, r):
    delivered = r["t0.ram_delivered_fraction"]
    gallery, (gallery_low, gallery_high) = ledger.q("gg.volume"), ledger.rng("gg.volume")
    chamber, (chamber_low, chamber_high) = ledger.q("sub.volume"), ledger.rng("sub.volume")
    spilled = gallery * (1 - delivered.value) / delivered.value
    least = gallery_low * (1 - delivered.high) / delivered.high  # the smallest Gallery and the most efficient ram
    most = gallery_high * (1 - delivered.low) / delivered.low
    # Judgement call: the ram sustains itself if the water that one Gallery fill spills still fits in the chamber.
    status = _three_way(most <= chamber_low, least <= chamber_high)
    return status, (
        f"A ram at the foot of the Descending Passage delivers {100 * delivered.value:.0f} percent of its drive "
        f"water to the Gallery roof, so one Gallery fill spills {spilled:.0f} m3 ({least:.0f} m3 at the least) into "
        f"a chamber of {chamber:.0f} m3 ({chamber_high:.0f} m3 at most) that has no outfall."
    )


def _e17(ledger, r):
    clearance = r["t0.pit_clearance"]
    # The evidence counts only if the old pit reached the water, so a clearance of zero or less is what passes.
    status = _three_way(clearance.high <= 0, clearance.low <= 0)
    today = (
        ledger.q("site.base_elevation_asl") + ledger.q("pit.excavated_bottom.z")
        - ledger.q("hydro.modern_water_table_asl")
    )
    reached = {
        "pass": "it reached a documented water table",
        "conditional": "it may have reached a documented water table",
        "fail": "it reached no documented water table",
    }[status]
    return status, (
        f"The pit as it stood before 1837 had a clearance of {clearance.value:.1f} m over the Old Kingdom flood "
        f"peak ({clearance.low:.1f} m at the least), so {reached}, while the shaft sunk in 1837 and 1838 ends "
        f"{today:.1f} m above today's water table, near enough that modern groundwater cannot be excluded as the "
        "cause of wet fill."
    )


def _e18(ledger, r):
    gain = r["t0.arrhenius_gain"]
    barrier, (barrier_low, _) = ledger.q("ac.arrhenius_barrier"), ledger.rng("ac.arrhenius_barrier")
    # The project owner's decision of 2026-10-10: the ledger's barrier is the endothermicity of the direct gas
    # reaction, which t0.gas_phase_lifetime also uses; the low end of its range is the illustrative 100 kJ/mol
    # behind the criterion's 12 K (05 section 5.5); the basis gives the gain at both, for the same temperature.
    at_low = arrhenius_gain({i: ledger.q(i) for i in gain.inputs} | {"ac.arrhenius_barrier": barrier_low})
    status = _three_way(gain.low >= 2, gain.high >= 2)  # the criterion asks for a doubling
    met = "at either" if at_low >= 2 else "only at the higher" if gain.value >= 2 else "at neither"
    return status, (
        f"The strongest airborne ultrasound engineered, {ledger.q('ac.best_airborne_level'):.0f} dB, speeds a "
        f"dry-gas reaction {gain.value:.1f} times if its barrier is the {barrier / 1000:.0f} kJ/mol of the direct "
        f"gas reaction and {at_low:.1f} times if it is {barrier_low / 1000:.0f} kJ/mol, so the doubling the "
        f"criterion asks for is met {met} barrier, and over the ranges of the inputs the gain runs from "
        f"{gain.low:.1f} to {gain.high:.1f} times."
    )


def _e29(ledger, r):
    lost = r["t0.gypsum_saturation_loss"]
    # the criterion's lines: pass if at least 80 percent of the acid survives, fail below 20 percent
    status = "pass" if 1 - lost.high >= 0.8 else "conditional" if 1 - lost.low >= 0.2 else "fail"
    return status, (
        f"Bare limestone neutralises {100 * lost.value:.0f} percent of the strongest possible batch "
        f"({100 * lost.low:.0f} to {100 * lost.high:.0f} percent over the input ranges) before gypsum saturates and "
        f"can coat it, so {100 * (1 - lost.value):.0f} percent of the acid survives one cycle, and more only where "
        "a coat is already in place."
    )


# The thresholds and the choice of status in these rules are judgement calls, reviewed by the project owner.
# They restate the pass and fail lines of the criteria in ledger/claims.yaml, which come from research/01 to 07.
# A claim without a rule keeps the status it has in claims.yaml.
RULES = {
    "S07": _s07,
    "S09": _s09,
    "S10": _s10,
    "S11": _s11,
    "S12": _four_strokes,
    "S16": _s16,
    "S18": _four_strokes,
    "S20": _s20,
    "S21": _s21,
    "S24": _s24,
    "S25": _s25,
    "S27": _s27,
    "S28": _veins,
    "S29": _veins,
    "S30": _s30,
    "S31": _s31,
    "E14": _e14,
    "E17": _e17,
    "E18": _e18,
    "E22": _e22,
    "E29": _e29,
    "E38": _veins,
}


def verdicts(ledger: Ledger, results: dict[str, Result]) -> dict[str, tuple[str, str]]:
    decided = {}
    for claim in ledger.claims.values():
        rule = RULES.get(claim.id)
        decided[claim.id] = (
            rule(ledger, results) if rule else (claim.status, f"No Tier 0 rule; tested in piece {claim.piece}.")
        )
    return decided


# --- Table and command ----------------------------------------------------------------------


def table_markdown(results: dict[str, Result]) -> str:
    lines = ["| Id | Quantity | Value | Low | High | Unit | Formula |", "|---|---|---|---|---|---|---|"]
    for r in results.values():
        lines.append(f"| {r.id} | {r.label} | {r.value:.3g} | {r.low:.3g} | {r.high:.3g} | {r.unit} | {r.formula} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    ledger = load()
    results = all_results(ledger)
    decided = verdicts(ledger, results)
    out_dir = REPO_ROOT / "results" / "tier0"
    out_dir.mkdir(parents=True, exist_ok=True)
    ruled = "".join(f"| {claim} | {decided[claim][0]} | {decided[claim][1]} |\n" for claim in decided if claim in RULES)
    (out_dir / "tier0.md").write_text(
        "# Tier 0 screening\n\n"
        "Generated by `uv run python -m pyramid.screening`. Do not edit by hand.\n\n"
        "## Quantities\n\n" + table_markdown(results) + "\n"
        "## First verdicts\n\n| Claim | Status | Basis |\n|---|---|---|\n" + ruled
    )
    payload = {
        "results": [asdict(result) for result in results.values()],
        "verdicts": {claim: {"status": status, "basis": basis} for claim, (status, basis) in decided.items()},
    }
    (out_dir / "tier0.json").write_text(json.dumps(payload, indent=2) + "\n")
    write_manifest(out_dir, "tier0", ledger)


if __name__ == "__main__":
    main()
