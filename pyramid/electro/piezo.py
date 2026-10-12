"""The field the granite would need: Tier 0's piezoelectric chain run backwards.

Tier 0 (screening.piezo_intensity, after 04 section 4.6 scenario 1) turns a field E in the granite into sound in the
air: strain d E, displacement d E L, velocity d E L / t_rise, intensity Z v^2 / 2. Intensity goes as E squared, so the
field that reaches a given intensity is the square root of that intensity over the intensity at 1 V/m.

Assumptions (Tier 0's own, all generous to the hypothesis):
- the whole thickness answers in phase within the stroke's rise time, though sound crosses only a few centimetres
  of granite in that time;
- every part of the strain reaches one face, and the face radiates a plane wave;
- no resonance: a single pulse does not build one up (04 section 4.6).

That is the single-pulse chain, the one a return stroke can drive. Tier 0 has a second chain, for S07
(screening.leaf_sound_level, after 05 section 4.2): a sustained alternating field across the antechamber's granite
leaf, velocity 2 pi f d E L, for which no source is proposed. With every input at its generous end it reaches the
same intensity at a lower field than the pulse chain does, so needed_field_sustained gives its figure to be set
beside the pulse chain's.
"""
import math

from pyramid import screening

CHAIN = ("em.granite_piezo_d", "em.piezo_thickness", "em.pulse_rise_time", "ac.air_impedance")
GAS_SOLID = CHAIN + ("ac.gas_solid_intensity",)
WET_FILM = CHAIN + ("ac.cavitation_intensity", "ac.water_impedance", "ac.reference_pressure")
SUSTAINED = ("em.granite_piezo_d", "ante.leaf_thickness", "ac.drive_frequency", "ac.air_impedance",
             "ac.reference_pressure", "ac.gas_solid_intensity")


def _field_for(q, intensity: float) -> float:
    at_one_volt_per_metre = screening.piezo_intensity({**q, "em.piezo_field_lightning": 1.0})
    return math.sqrt(intensity / at_one_volt_per_metre)


def needed_field_gas_solid(q) -> float:
    """Field, V/m, at which the chain radiates the weakest intensity known to move a gas-solid catalytic rate."""
    return _field_for(q, q["ac.gas_solid_intensity"])


def needed_field_sustained(q) -> float:
    """Field, V/m, at which Tier 0's S07 chain, the leaf under a sustained drive, radiates that same intensity."""
    at_one_volt_per_metre = screening.leaf_sound_level({**q, "em.air_breakdown_field": 1.0})  # dB
    level = 10 * math.log10(q["ac.gas_solid_intensity"] * q["ac.air_impedance"] / q["ac.reference_pressure"] ** 2)
    return 10 ** ((level - at_one_volt_per_metre) / 20)  # the level goes as 20 log10 of the field


def needed_field_wet_film(q) -> float:
    """Field, V/m, at which the chain radiates Tier 0's level for cavitating a wet film from the gas side."""
    level = screening.required_sound_level(q)  # dB in air, the loss on entering the liquid included
    return _field_for(q, q["ac.reference_pressure"] ** 2 * 10 ** (level / 10) / q["ac.air_impedance"])
