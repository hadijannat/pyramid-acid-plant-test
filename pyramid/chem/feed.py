"""The hydrogen sulfide the cycle needs, against what the plateau is known to supply (claims S01 and E01).

Assumptions:
- One mole of hydrogen sulfide per mole of sulfur dioxide: nothing is lost in the conversion of S02, which the
  hypothesis does not describe.
- The batch is Tier 0's largest, one King's Chamber of the pure gas per cycle; a weaker charge needs less in
  proportion.
- 07 gives no flux for any seep or spring. Its one analogue is a concentration in cave air, so the only
  comparison on offer is the volume of such air that carries the sulfur of one batch.
"""
from pyramid.screening import _SO2, YEAR, R, _so2_moles

FEED = _SO2 + ("chem.molar_mass_h2s", "rx.cycle_time")
CAVE_AIR = _SO2 + ("rx.h2s_cave_air",)


def batch_moles(q) -> float:
    """Hydrogen sulfide for one batch, mol: Tier 0's sulfur dioxide inventory, mole for mole."""
    return _so2_moles(q)


def batch_mass(q) -> float:
    """The same in kg."""
    return _so2_moles(q) * q["chem.molar_mass_h2s"]


def flux(q) -> float:
    """Hydrogen sulfide the cycle needs, mol/s: one batch per cycle time."""
    return _so2_moles(q) / q["rx.cycle_time"]


def yearly_mass(q) -> float:
    """The same over a year, kg."""
    return batch_mass(q) * YEAR / q["rx.cycle_time"]


def cave_air_per_batch(q) -> float:
    """Volume of cave air at the analogue's ceiling that holds the sulfur of one batch, m3."""
    # The ideal-gas factors cancel: the pure gas fills one King's Chamber, the dilute gas 1 / x of them.
    return _so2_moles(q) / (q["rx.h2s_cave_air"] * q["site.atm_pressure"] / (R * q["chem.temperature"]))
