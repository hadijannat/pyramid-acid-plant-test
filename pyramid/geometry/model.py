"""The parametric model of the pyramid: variant switches, the built model, build().

Frame: origin at the pyramid's centre on the pavement; X east, Y north, Z up; metres.
Everything here must be called inside frame.session().
"""
from dataclasses import dataclass

import gmsh

from pyramid.geometry import spaces
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


# Level "survey", in build order: space name -> (label, ledger id of the volume it is checked against).
SURVEY = {
    "descending_passage": ("Descending Passage", "dp.volume"),
    "subterranean_chamber": ("Subterranean Chamber", "sub.volume"),
    "pit": ("Pit", "pit.volume"),
    "south_passage": ("South passage", "sp.volume"),
    "well_shaft": ("Well shaft", "ws.volume"),
    "grotto": ("Grotto", None),
    "ascending_passage": ("Ascending Passage", "ap.volume_above_plugs"),
    "queens_passage": ("Queen's Chamber passage", "qp.volume"),
    "queens_chamber": ("Queen's Chamber", "qc.volume_with_niche"),
    "qc_shaft_north": ("Queen's Chamber north shaft", "qcs.volume"),
    "qc_shaft_south": ("Queen's Chamber south shaft", "qcs.volume"),
    "grand_gallery": ("Grand Gallery", "gg.volume"),
    "antechamber": ("Antechamber", "ante.volume"),
    "kings_chamber": ("King's Chamber", "kc.volume_with_passage"),
    "kc_shaft_north": ("King's Chamber north shaft", "kcs.north.volume"),
    "kc_shaft_south": ("King's Chamber south shaft", "kcs.south.volume"),
    "relieving_chambers": ("Relieving chambers", "rc.volume"),
    "big_void": ("Big Void", "bv.volume"),
    "north_face_corridor": ("North Face Corridor", "nfc.volume"),
}


def _outline(ledger: Ledger, level: str, variants: Variants) -> tuple[float, float, float | None]:
    """Base side, apex height and cut-off level (None for a pointed top) of the model's pyramid."""
    q = ledger.q
    if level == "paper":
        return q("paper.base_side"), q("paper.height"), None
    half, apex = spaces.faces(ledger, variants.casing)
    return 2 * half, apex, q("pyr.height_present") if variants.apex_truncated else None


def _build_survey(ledger: Ledger, variants: Variants) -> Model:
    """Every surveyed space, the masonry round them and the bedrock under them."""
    q, v = ledger.q, variants
    to_casing = v.casing and v.kc_shafts_open  # else the King's Chamber shafts stop at the core face
    tags = {
        "descending_passage": spaces.descending_passage(ledger),
        "subterranean_chamber": spaces.subterranean_chamber(ledger),
        "pit": spaces.pit(ledger, v.pit_excavated),
        "south_passage": spaces.south_passage(ledger),
        "well_shaft": spaces.well_shaft(ledger),
        "grotto": spaces.grotto(ledger),
        "ascending_passage": spaces.ascending_passage(ledger, v.ascending_plugs),
        "queens_passage": spaces.queens_passage(ledger),
        "queens_chamber": spaces.queens_chamber(ledger),
        "qc_shaft_north": spaces.qc_shaft_north(ledger),
        "qc_shaft_south": spaces.qc_shaft_south(ledger),
        "grand_gallery": spaces.grand_gallery(ledger),
        "antechamber": spaces.antechamber(ledger, v.portcullis, v.grooves_connected),
        "kings_chamber": spaces.kings_chamber(ledger),
        "kc_shaft_north": spaces.kc_shaft_north(ledger, to_casing, v.kc_shaft_ends_level),
        "kc_shaft_south": spaces.kc_shaft_south(ledger, to_casing, v.kc_shaft_ends_level),
        "relieving_chambers": spaces.relieving_chambers(ledger),
        "big_void": spaces.big_void(ledger, v.big_void_inclined),
        "north_face_corridor": spaces.north_face_corridor(ledger),
    }
    volume_ids = {name: volume_id for name, (_, volume_id) in SURVEY.items()}
    if v.pit_excavated:
        volume_ids["pit"] = "pit.volume_excavated"
    if not v.ascending_plugs:
        volume_ids["ascending_passage"] = "ap.volume_gross"
    built = {name: Space(name, SURVEY[name][0], tag, occ.getMass(3, tag), volume_ids[name])
             for name, tag in tags.items()}
    pyramid = pyramid_solid(*_outline(ledger, "survey", v))
    bedrock = bedrock_block(q("pyr.base_side"), q("site.base_elevation_asl"))
    return Model("survey", v, built, _carve(pyramid, built), _carve(bedrock, built))


def build(ledger: Ledger, level: str = "survey", variants: Variants = Variants()) -> Model:
    """Build the model at one level. Must be called inside frame.session()."""
    if level == "paper":
        return _build_paper(ledger, variants)
    if level == "survey":
        return _build_survey(ledger, variants)
    raise ValueError(f"unknown level: {level!r}")


# ---- self-checks ---------------------------------------------------------------------------

VOID_TOL = 0.02  # the volume cut out of the pyramid must match the spaces inside it this closely

# Surveyed coordinates that are an extreme of their space's bounding box:
# (ledger id, space, index into (xmin, ymin, zmin, xmax, ymax, zmax)).
CONTROLS = [
    ("dp.entrance.y", "descending_passage", 4),
    ("dp.south_end.z", "descending_passage", 2),
    ("dp.south_end.y", "subterranean_chamber", 4),
    ("sub.roof_centre.z", "subterranean_chamber", 5),
    ("sp.south_end.y", "south_passage", 1),
    ("sp.north_end.z", "south_passage", 2),
    ("ap.end.y", "ascending_passage", 1),
    ("qc.west_wall.x", "queens_chamber", 0),
    ("qc.floor.z", "queens_chamber", 2),
    ("qc.north_wall.y", "queens_chamber", 4),
    ("qc.ridge.z", "queens_chamber", 5),
    ("gg.south_end.y", "grand_gallery", 1),
    ("gg.north_end.z", "grand_gallery", 2),
    ("gg.north_end.y", "grand_gallery", 4),
    ("gg.roof_top.z", "grand_gallery", 5),
    ("ante.floor.z", "antechamber", 2),
    ("gg.south_end.y", "antechamber", 4),
    ("ante.roof.z", "antechamber", 5),
    ("kc.west_wall.x", "kings_chamber", 0),
    ("kc.south_wall.y", "kings_chamber", 1),
    ("kc.floor.z", "kings_chamber", 2),
    ("kc.east_wall.x", "kings_chamber", 3),
    ("ante.south_end.y", "kings_chamber", 4),
    ("kc.ceiling.z", "kings_chamber", 5),
]


def _below(tag: int, z: float) -> float:
    """Volume of the part of a solid that lies below the level z."""
    x0, y0, z0, x1, y1, z1 = occ.getBoundingBox(3, tag)
    if z <= z0:
        return 0.0
    if z >= z1:
        return occ.getMass(3, tag)
    slab = occ.addBox(x0 - 1, y0 - 1, z0 - 1, x1 - x0 + 2, y1 - y0 + 2, z - z0 + 1)
    out, _ = occ.intersect(occ.copy([(3, tag)]), [(3, slab)])
    volume = sum(occ.getMass(3, part) for _, part in out)
    occ.remove(out, recursive=True)
    return volume


def check(model: Model, ledger: Ledger) -> list[str]:
    """Self-checks of a built model. Returns human-readable failures; an empty list means all passed."""
    q, v = ledger.q, model.variants
    failures = []
    boxes = {name: occ.getBoundingBox(3, space.tag) for name, space in model.spaces.items()}

    for name, space in model.spaces.items():
        if space.volume <= 0:
            failures.append(f"{name}: not a closed solid (volume {space.volume:.3f} m3)")
        if space.volume_id:
            low, high = ledger.rng(space.volume_id)
            if not low <= space.volume <= high:
                failures.append(f"{name}: volume {space.volume:.2f} m3 is outside {space.volume_id} ({low} to {high})")

    if model.level == "survey":
        pit_bottom = "pit.excavated_bottom.z" if v.pit_excavated else "pit.original_bottom.z"
        for key, name, i in CONTROLS + [(pit_bottom, "pit", 2)]:
            low, high = ledger.rng(key)  # for a surveyed point: Petrie's stated error
            if not low <= boxes[name][i] <= high:
                failures.append(f"{key}: {name} is at {boxes[name][i]:.3f} m, outside the surveyed {low} to {high} m")

    base, apex, top = _outline(ledger, model.level, v)
    roof = apex if top is None else top
    floor = float("-inf") if model.bedrock is None else -q("site.base_elevation_asl")
    for name, (x0, y0, z0, x1, y1, z1) in boxes.items():
        if min(x0, y0) < -base / 2 or max(x1, y1) > base / 2 or z1 > roof or z0 < floor:
            failures.append(f"{name}: reaches outside the bounding region of the pyramid and bedrock")

    pyramid = base ** 2 * apex / 3 * (1 if top is None else 1 - (1 - top / apex) ** 3)
    removed = pyramid - occ.getMass(3, model.masonry)
    inside = sum(space.volume - _below(space.tag, 0.0) for space in model.spaces.values())
    if abs(removed - inside) > VOID_TOL * inside:
        failures.append(f"masonry: {removed:.1f} m3 was cut out of the pyramid, but the spaces above the "
                        f"pavement hold {inside:.1f} m3")
    return failures
