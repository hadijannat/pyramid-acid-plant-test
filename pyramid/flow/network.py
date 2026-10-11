"""What the flow models share: the spaces a fill must fill, the Gallery's openings, and the list of quantities.

Levels are metres above the pavement, the ledger's datum. Every quantity is a pure function of {ledger id: number};
its range is its least and greatest value over the corners of its inputs' ranges (simkit.corners), which is exact
where the function is monotone in each input whose range is wider than a rounding. The gas shares are not, in the
drain time: a slower drain helps once the antechamber opening is clear of the water and hurts while it is under
it. Their ranges hold the three drain rates 02 evaluates, and a sweep of the rates between moves neither end by
more than 0.002 (tests/test_flow_models.py).
"""
import math
from dataclasses import dataclass

from pyramid import simkit
from pyramid.ledger import Ledger
from pyramid.screening import Result

# One row per quantity, as in the Tier 0 screening: (id, label, unit, formula, inputs, function).
QUANTITIES: list[tuple] = []


def quantity(name: str, label: str, unit: str, formula: str, inputs: tuple[str, ...], held: tuple[str, ...] = ()):
    """Register a pure function of {ledger id: number} as the result flow.<name>.

    `held` inputs stay at their ledger values while the range is taken: every input with a range doubles the
    corners, so a quantity names here those whose ranges it leaves to another result, and says which.
    """

    def register(fn):
        QUANTITIES.append((f"flow.{name}", label, unit, formula, inputs, fn, held))
        return fn

    return register


def all_results(ledger: Ledger) -> dict[str, Result]:
    results = {}
    for id, label, unit, formula, inputs, fn, held in QUANTITIES:
        fixed = {i: ledger.q(i) for i in held}
        swept = tuple(i for i in inputs if i not in fixed)
        value, low, high = simkit.corners(ledger, swept, lambda v: fn(v | fixed))  # noqa: B023 (called at once)
        results[id] = Result(id, label, value, low, high, unit, formula, inputs)
    return results


# The spaces one fill must fill, with the ledger volumes that make them up: the list of research/02 working W3,
# which is also the list of Tier 0's lifting work. The Subterranean Chamber and the Descending Passage lie below.
FILLED = (
    ("Grand Gallery", ("gg.volume",)),
    ("Queen's Chamber with its niche", ("qc.volume", "qc.niche.volume")),
    ("Queen's passage", ("qp.volume",)),
    ("Ascending Passage with the plugs in place", ("ap.volume",)),  # the stub below the plugs is part of it
    ("well shaft", ("ws.volume",)),
)
FILLED_IDS = tuple(id for _, ids in FILLED for id in ids)


@dataclass(frozen=True)
class Opening:
    """One opening in the Gallery's walls: where it is, how large, and what lies behind it."""

    name: str
    level: float  # m above the pavement, at the opening's floor
    height: float  # m, vertical
    area: float  # m2
    leads_to: str


OPENING_IDS = (
    "ap.end.z", "ap.width", "ap.height", "ap.angle", "qp.floor_north.z", "qp.width", "qp.height_north", "ws.top.z",
    "ws.upper_side", "ante.floor.z", "ante.low_passage.width", "ante.low_passage.height", "gg.south_end.z",
    "gg.height", "rc.davison_passage.width", "rc.davison_passage.height", "gg.north_end.z",
)


def gallery_openings(q) -> list[Opening]:
    """The five openings research/01 claim 4 lists, as surveyed (the antechamber passage with no slab in it)."""
    davison, low = q["rc.davison_passage.height"], q["ante.low_passage.height"]
    return [
        # The passage height is measured square to its slope, so the opening stands taller in the Gallery's wall.
        Opening("Ascending Passage", q["ap.end.z"], q["ap.height"] / math.cos(math.radians(q["ap.angle"])),
                q["ap.width"] * q["ap.height"], "the Descending Passage and the entrance, past the granite plugs"),
        Opening("Queen's passage", q["qp.floor_north.z"], q["qp.height_north"], q["qp.width"] * q["qp.height_north"],
                "the Queen's Chamber, whose shafts are blind"),
        # The mouth lies in the west ramp; one shaft side is a generous figure for how high it reaches.
        Opening("well shaft mouth", q["ws.top.z"], q["ws.upper_side"], q["ws.upper_side"] ** 2,
                "the Descending Passage and the entrance"),
        Opening("antechamber passage", q["ante.floor.z"], low, q["ante.low_passage.width"] * low,
                "the King's Chamber and its two shafts to the outside"),
        # 01 places this mouth "at the top of the Gallery E wall" and gives no level: it is set just under the roof.
        Opening("Davison's passage", q["gg.south_end.z"] + q["gg.height"] - davison, davison,
                q["rc.davison_passage.width"] * davison, "Davison's chamber, a closed space"),
    ]


def at_the_foot(q, opening: Opening) -> bool:
    """True for an opening within one passage height of the Gallery's lowest point.

    The water leaves the Gallery downwards, so such an opening stays under water, and passes no gas, until the
    Gallery is all but empty.
    """
    return opening.level < q["gg.north_end.z"] + q["ap.height"]


def shaft_conductance(q) -> float:
    """Q / sqrt(2 dp / rho) of the two King's Chamber shafts in parallel, in m2: the sum of A / sqrt(K)."""
    north = q["kcs.north.width"] * q["kcs.north.height"] / math.sqrt(q["hydro.kcs_north_loss_coefficient"])
    south = q["kcs.south.width"] * q["kcs.south.height"] / math.sqrt(q["hydro.kcs_south_loss_coefficient"])
    return north + south


SHAFT_IDS = (
    "kcs.north.width", "kcs.north.height", "kcs.south.width", "kcs.south.height",
    "hydro.kcs_north_loss_coefficient", "hydro.kcs_south_loss_coefficient",
)
