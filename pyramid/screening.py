"""Tier 0 screening: sourced hand calculations, a first verdict per claim, and the table."""
import math
from dataclasses import dataclass
from itertools import product

from pyramid.ledger import Ledger

G = 9.80665  # standard gravity, m/s2
R = 8.314462618  # molar gas constant, J/mol/K
O2_PER_SO2 = 0.5  # stoichiometry of SO2 + 1/2 O2 -> SO3: a reaction coefficient, not a measurement


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
