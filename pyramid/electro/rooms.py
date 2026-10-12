"""Audio-band acoustics of three rooms as hard-walled boxes: modes, decay time and modal quality factor (E13).

Assumptions:
- each room is a rectangular box for its modes, f = (c / 2) sqrt((nx / Lx)^2 + (ny / Ly)^2 + (nz / Lz)^2); the Grand
  Gallery's box is its sloping floor length, its width above the ramps and its vertical height;
- the decay is Sabine's, T60 = 24 ln(10) V / (c A), with A = alpha S + 4 m V. It is a statistical formula
  used down to the lowest modes; ponytail: its ceiling is a factor of about two on a single mode's decay, and the
  upgrade path is a modal damping sum or a Helmholtz solve with wall impedances (05 section 5.1);
- the loss is the walls' and the air's, as the task asks. The wall absorption is the ledger's one assumed value for
  stone, the same in the three rooms: no measurement tells them apart;
- the passage mouths are a sensitivity case, not part of the ranking: a mouth then absorbs all that reaches it (the
  open-window rule, which overstates the loss at wavelengths much longer than the mouth; 05 section 5.3 names the
  openings as what sets the loss). The antechamber has two, the King's Chamber one, the Gallery two; their section
  is a recalled figure in the ledger. Open mouths lower the antechamber's standing in both measures;
- air absorbs as frequency squared, the classical law, scaled to the ledger's 13 kHz value; ponytail: this
  under-reads below a few kHz, where the walls carry the loss anyway; the upgrade path is ISO 9613-1.
"""
import math
from itertools import product

AIR = ("ac.sound_speed_air", "ac.wall_absorption", "ac.absorption_13khz", "ac.link_frequency")
PASSAGE = ("ante.low_passage.width", "ante.low_passage.height")
REFERENCE = "ante.height"  # the antechamber's longest side sets the frequency at which the three decays are compared
ROOMS = {
    "antechamber": {
        "label": "antechamber", "dims": ("ante.length", "ante.width", "ante.height"),
        "volume": "ante.volume", "area": "ante.surface_area", "openings": 2,
    },
    "kings_chamber": {
        "label": "King's Chamber", "dims": ("kc.length", "kc.width", "kc.height"),
        "volume": None, "area": None, "openings": 1,
    },
    "grand_gallery": {
        "label": "Grand Gallery", "dims": ("gg.floor_length", "gg.width", "gg.height"),
        "volume": "gg.volume", "area": "gg.wall_area", "openings": 2,
    },
}
NEPER = 10 / math.log(10)  # dB per neper of energy, 4.343


def inputs(room: str) -> tuple[str, ...]:
    spec = ROOMS[room]
    own = spec["dims"] + tuple(i for i in (spec["volume"], spec["area"]) if i)
    return tuple(dict.fromkeys(own + AIR + (REFERENCE,)))


ALL = tuple(dict.fromkeys(sum((inputs(room) for room in ROOMS), ())))  # one draw of each input for the three rooms


def modes(dims, speed: float, top: float) -> list[tuple[float, tuple[int, int, int]]]:
    """The modes of a hard-walled box below `top` Hz, lowest first, as (frequency, (nx, ny, nz))."""
    counts = [range(int(2 * top * length / speed) + 1) for length in dims]
    found = []
    for n in product(*counts):
        frequency = speed / 2 * math.sqrt(sum((k / length) ** 2 for k, length in zip(n, dims)))
        if 0 < frequency <= top:
            found.append((frequency, n))
    return sorted(found)


def lowest_mode(q, room: str) -> float:
    """c / (2 L) for the longest side."""
    return q["ac.sound_speed_air"] / (2 * max(q[i] for i in ROOMS[room]["dims"]))


def reference_frequency(q) -> float:
    """The antechamber's lowest mode: the lowest frequency at which all three rooms have modes."""
    return q["ac.sound_speed_air"] / (2 * q[REFERENCE])


def air_attenuation(q, frequency: float) -> float:
    """Energy attenuation of air, 1/m: frequency squared, scaled to the ledger's absorption at 13 kHz."""
    return q["ac.absorption_13khz"] * (frequency / q["ac.link_frequency"]) ** 2 / NEPER


def volume_and_area(q, room: str) -> tuple[float, float]:
    spec = ROOMS[room]
    a, b, c = (q[i] for i in spec["dims"])
    volume = q[spec["volume"]] if spec["volume"] else a * b * c
    area = q[spec["area"]] if spec["area"] else 2 * (a * b + a * c + b * c)
    return volume, area


def absorption_area(q, room: str, frequency: float, open_passages: bool = False) -> float:
    volume, area = volume_and_area(q, room)
    mouths = ROOMS[room]["openings"] * q[PASSAGE[0]] * q[PASSAGE[1]] if open_passages else 0.0
    return q["ac.wall_absorption"] * area + mouths + 4 * air_attenuation(q, frequency) * volume


def decay_time(q, room: str, frequency: float, open_passages: bool = False) -> float:
    """Sabine's time for the sound to fall by 60 dB, s."""
    volume, _ = volume_and_area(q, room)
    return 24 * math.log(10) * volume / (q["ac.sound_speed_air"] * absorption_area(q, room, frequency, open_passages))


def quality_factor(q, room: str, frequency: float, open_passages: bool = False) -> float:
    """Q = 2 pi f T60 / (6 ln 10): the energy of a mode falls by e in T60 / (6 ln 10)."""
    return 2 * math.pi * frequency * decay_time(q, room, frequency, open_passages) / (6 * math.log(10))


def _others(room: str = "antechamber") -> list[str]:
    return [other for other in ROOMS if other != room]


def decay_lead(q, open_passages: bool = False) -> float:
    """The antechamber's decay time over the longest of the other two, at the antechamber's lowest mode."""
    f = reference_frequency(q)
    return decay_time(q, "antechamber", f, open_passages) / max(decay_time(q, o, f, open_passages) for o in _others())


def quality_lead(q, open_passages: bool = False) -> float:
    """The quality factor of the antechamber's lowest mode over the highest of the other two rooms' lowest modes."""
    def own(room):
        return quality_factor(q, room, lowest_mode(q, room), open_passages)

    return own("antechamber") / max(own(o) for o in _others())
