"""The parametric model of the pyramid: variant switches, the built model, build().

Frame: origin at the pyramid's centre on the pavement; X east, Y north, Z up; metres.
Everything here must be called inside frame.session().
"""
from dataclasses import dataclass

import gmsh

from pyramid.ledger import Ledger

occ = gmsh.model.occ


@dataclass(frozen=True)
class Variants:
    casing: bool = True
    kc_shafts_open: bool = True
    kc_shaft_ends_level: bool = False
    portcullis: bool = True
    grooves_connected: bool = False
    ascending_plugs: bool = True
    pit_excavated: bool = False
    big_void_inclined: bool = False
    apex_truncated: bool = True


@dataclass(frozen=True)
class Space:
    name: str               # snake_case; becomes the glTF node name
    label: str              # human-readable
    tag: int                # gmsh OCC volume tag
    volume: float           # m3
    volume_id: str | None   # ledger quantity id it is checked against


@dataclass(frozen=True)
class Model:
    level: str                # "survey" or "paper"
    variants: Variants
    spaces: dict[str, Space]  # interior spaces only
    masonry: int              # OCC volume tag of the pyramid minus the spaces
    bedrock: int | None       # OCC volume tag; None at level "paper"


# The 2018 study's three box chambers: space name -> (ledger prefix, label).
PAPER = {
    "paper_kings_chamber": ("paper.kc", "King's Chamber (2018 study's model)"),
    "paper_queens_chamber": ("paper.qc", "Queen's Chamber (2018 study's model)"),
    "paper_lower_chamber": ("paper.lower", "Lower chamber (2018 study's model)"),
}


def pyramid_solid(base: float, apex: float, top: float | None = None) -> int:
    """A square pyramid standing on the pavement, centred on the origin, as one OCC volume.

    base is the side at the pavement and apex the height at which the faces meet. With top
    set, the pyramid is cut off level at that height.
    """
    half = base / 2
    corners = [(-half, -half), (half, -half), (half, half), (-half, half)]
    foot = [occ.addPoint(x, y, 0.0) for x, y in corners]
    around = [occ.addLine(foot[i], foot[(i + 1) % 4]) for i in range(4)]
    faces = [occ.addPlaneSurface([occ.addCurveLoop(around)])]
    if top is None:
        tip = occ.addPoint(0.0, 0.0, apex)
        ridges = [occ.addLine(corner, tip) for corner in foot]
        for i in range(4):
            loop = occ.addCurveLoop([around[i], ridges[(i + 1) % 4], ridges[i]])
            faces.append(occ.addPlaneSurface([loop]))
    else:
        shrink = 1 - top / apex
        head = [occ.addPoint(x * shrink, y * shrink, top) for x, y in corners]
        above = [occ.addLine(head[i], head[(i + 1) % 4]) for i in range(4)]
        ridges = [occ.addLine(foot[i], head[i]) for i in range(4)]
        faces.append(occ.addPlaneSurface([occ.addCurveLoop(above)]))
        for i in range(4):
            loop = occ.addCurveLoop([around[i], ridges[(i + 1) % 4], above[i], ridges[i]])
            faces.append(occ.addPlaneSurface([loop]))
    return occ.addVolume([occ.addSurfaceLoop(faces)])


def bedrock_block(side: float, depth: float) -> int:
    """The rock under the pavement: a block with a square footprint, from -depth up to the pavement.

    ponytail: its top is flat at pavement level. The surveyed rock knoll that rises to 5.7 m
    inside the pyramid is not modelled; add it when a solver needs the rock and the masonry
    to carry different materials.
    """
    return occ.addBox(-side / 2, -side / 2, -depth, side, side, depth)


def _carve(solid: int, cut: dict[str, Space]) -> int:
    """Cut every space out of a solid. The spaces themselves are kept."""
    out, _ = occ.cut([(3, solid)], [(3, space.tag) for space in cut.values()], removeObject=True, removeTool=False)
    [(_, tag)] = out  # more than one volume here means the spaces have split the solid
    return tag


def _build_paper(ledger: Ledger, variants: Variants) -> Model:
    """The 2018 study's model: a pointed pyramid with three box chambers and no bedrock."""
    q = ledger.q
    built = {}
    for name, (key, label) in PAPER.items():
        length, width, height = q(f"{key}.length"), q(f"{key}.width"), q(f"{key}.height")
        # Reading of the 2018 paper, which research/04 leaves open: length runs east-west and
        # width north-south, the centre is offset to the south, centre.z is the centre's height.
        tag = occ.addBox(-length / 2, -q(f"{key}.axis_offset") - width / 2, q(f"{key}.centre.z") - height / 2,
                         length, width, height)
        built[name] = Space(name, label, tag, occ.getMass(3, tag), None)
    pyramid = pyramid_solid(q("paper.base_side"), q("paper.height"))
    return Model("paper", variants, built, _carve(pyramid, built), None)


def build(ledger: Ledger, level: str = "survey", variants: Variants = Variants()) -> Model:
    """Build the model at one level. Must be called inside frame.session()."""
    if level == "paper":
        return _build_paper(ledger, variants)
    raise ValueError(f"unknown level: {level!r}")
