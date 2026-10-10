"""One builder per interior space. Each takes the ledger and returns the tag of one OCC volume.

Frame: origin at the pyramid's centre on the pavement; X east, Y north, Z up; metres.
Call these inside frame.session().
"""
import math

import gmsh

from pyramid.ledger import Ledger

occ = gmsh.model.occ

OVERLAP = 0.05  # m. How far a part is pushed into the part it joins, so that a fuse has a volume to merge.
MARGIN = 1.0    # m. How far a cutting tool reaches past the solid it cuts, so that no two faces coincide.


# ---- helpers -------------------------------------------------------------------------------

def _point(led: Ledger, key: str) -> tuple[float, float, float]:
    """A surveyed point stored as three entries: key.x, key.y, key.z."""
    return led.q(f"{key}.x"), led.q(f"{key}.y"), led.q(f"{key}.z")


def _box(x0, y0, z0, x1, y1, z1) -> int:
    """Axis-aligned box between two opposite corners."""
    return occ.addBox(min(x0, x1), min(y0, y1), min(z0, z1), abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def _duct(start, end, width, height, centred=False, extend=0.0) -> int:
    """Straight duct in a north-south vertical plane: a box pitched about the X axis.

    start and end are (x, y, z) points with the same x, on the centre line of the duct's floor
    or, with centred=True, on its axis. The section is width (east-west) by height (square to
    the slope). extend lengthens the far end.
    """
    x, y0, z0 = start
    _, y1, z1 = end
    run, rise = y1 - y0, z1 - z0
    length = math.hypot(run, rise) + extend
    way = 1.0 if run >= 0 else -1.0  # +1 heading north, -1 heading south
    tag = occ.addBox(-width / 2, min(0.0, way * length), -height / 2 if centred else 0.0, width, length, height)
    # The box lies along +Y or -Y, so that pitching it by less than a right angle keeps its roof up.
    occ.rotate([(3, tag)], 0, 0, 0, 1, 0, 0, math.atan2(way * rise, way * run))
    occ.translate([(3, tag)], x, y0, z0)
    return tag


def _prism(points, vector) -> int:
    """Volume swept by a planar polygon (its corners in order) moved along vector."""
    corners = [occ.addPoint(*p) for p in points]
    edges = [occ.addLine(a, b) for a, b in zip(corners, corners[1:] + corners[:1])]
    face = occ.addPlaneSurface([occ.addCurveLoop(edges)])
    return next(tag for dim, tag in occ.extrude([(2, face)], *vector) if dim == 3)


def _join(parts) -> int:
    """Fuse volumes that overlap or share a face into one volume and return its tag."""
    out, _ = occ.fuse([(3, parts[0])], [(3, tag) for tag in parts[1:]])
    [(_, tag)] = out  # more than one volume here means two parts do not touch
    return tag


# ---- lower system --------------------------------------------------------------------------

def descending_passage(led: Ledger) -> int:
    """From the original entrance on the casing face to the foot of the slope, between its two surveyed ends."""
    q = led.q
    start = _point(led, "dp.entrance")
    # ponytail: the mouth is square to the slope, so the roof edge stands 0.31 m outside the casing face
    # (0.16 m3). Cut the duct with the pyramid when a solver needs the true mouth.
    return _duct(start, (start[0], q("dp.south_end.y"), q("dp.south_end.z")), q("dp.width"), q("dp.height"))


def _sub_walls(led: Ledger) -> tuple[float, float, float, float]:
    """West, east, south and north walls of the Subterranean Chamber."""
    q = led.q
    x, y = q("sub.roof_centre.x"), q("sub.roof_centre.y")
    return (x - q("sub.length_ew") / 2, x + q("sub.length_ew") / 2,
            y - q("sub.width_ns") / 2, y + q("sub.width_ns") / 2)


def _pit_plan(led: Ledger) -> tuple[float, float]:
    """Plan position of the pit.

    ponytail: no source read gives it, so it stands at the centre of the chamber's east half,
    where the floor is worked. Move it when Maragioglio and Rinaldi's plates are read.
    """
    q = led.q
    return q("sub.roof_centre.x") + q("sub.length_ew") / 4, q("sub.roof_centre.y")


def _diagonal_shaft(x, y, side, bottom, top) -> int:
    """Vertical square shaft set diagonally: its corners point north, east, south and west."""
    tag = _box(x - side / 2, y - side / 2, bottom, x + side / 2, y + side / 2, top)
    occ.rotate([(3, tag)], x, y, 0, 0, 0, 1, math.pi / 4)
    return tag


def subterranean_chamber(led: Ledger) -> int:
    """The chamber, the recess round the pit, and the level passage that enters it from the north."""
    q = led.q
    west, east, south, north = _sub_walls(led)
    roof = q("sub.roof_centre.z")
    floor = roof - q("sub.floor_depth_east")
    # ponytail: the irregular floor is two planes. It is level at the surveyed depth of the east
    # part, then climbs through the uncut western half to the surveyed clearance under the roof.
    # Replace with the real floor when a scan of the chamber exists.
    section = [(west, south, roof), (east, south, roof), (east, south, floor),
               (q("sub.roof_centre.x"), south, floor), (west, south, roof - q("sub.west_rock_clearance"))]
    chamber = _prism(section, (0, north - south, 0))
    # The best-worked floor, round the pit, is deeper: a recess with the pit's own plan.
    x, y = _pit_plan(led)
    recess = _diagonal_shaft(x, y, q("pit.side"), roof - q("sub.floor_depth_pit"), floor + OVERLAP)
    # The entrance passage runs from the foot of the Descending Passage to the north wall.
    start = _point(led, "dp.south_end")
    passage = _duct(start, (start[0], north, q("dp.horizontal_end.z")),
                    q("dp.horizontal.width"), q("dp.horizontal.height"), extend=OVERLAP)
    return _join([chamber, recess, passage])


def pit(led: Ledger, excavated: bool = False) -> int:
    """The pit as it stood before 1837, or with excavated=True as Perring left it in 1838."""
    q = led.q
    x, y = _pit_plan(led)
    ledge = q("pit.ledge.z")
    bottom = q("pit.excavated_bottom.z" if excavated else "pit.original_bottom.z")
    upper = _diagonal_shaft(x, y, q("pit.side"), ledge, q("sub.roof_centre.z") - q("sub.floor_depth_pit"))
    lower = _diagonal_shaft(x, y, q("pit.lower_side"), bottom, ledge + OVERLAP)
    return _join([upper, lower])


def south_passage(led: Ledger) -> int:
    """The blind passage that runs south from the Subterranean Chamber."""
    q = led.q
    x = q("sp.north_end.x")
    # ponytail: it runs due south; the surveyed 0.2 m drift to the west over its length is dropped.
    # Its surveyed floor is 0.58 m below the modelled chamber floor, so it meets the chamber over a strip
    # 0.17 m high. Lower the chamber floor at its south-east corner when a scan of the chamber exists.
    return _duct((x, _sub_walls(led)[2], q("sp.north_end.z")), (x, q("sp.south_end.y"), q("sp.south_end.z")),
                 q("sp.width"), q("sp.height"))


def _well_axis(led: Ledger) -> tuple[float, list[tuple[float, float]]]:
    """East coordinate of the well shaft, and the (y, z) corners of its axis from the top down.

    The corners are: the floor of the level run in the Gallery, the feet of Haase's segments
    1 to 4, and the centre of the lower mouth in the west wall of the Descending Passage.
    """
    q = led.q
    x = q("gg.north_end.x") - q("gg.slot_width") / 2 - q("ws.seg0.length") - q("ws.upper_side") / 2
    y = q("gg.north_end.y") - (q("ws.mouth_near_edge") + q("ws.mouth_far_edge")) / 2
    z = q("ws.top.z")
    corners = [(y, z)]
    for segment, vertical in ((1, True), (2, False), (3, True), (4, False)):
        length = q(f"ws.seg{segment}.length")
        slope = math.pi / 2 if vertical else math.radians(q(f"ws.seg{segment}.angle"))
        y, z = y - length * math.cos(slope), z - length * math.sin(slope)
        corners.append((y, z))
    # The lower mouth: on the axis of the Descending Passage, the surveyed distance below the entrance.
    _, top_y, top_z = _point(led, "dp.entrance")
    slope = math.atan2(top_z - q("dp.south_end.z"), top_y - q("dp.south_end.y"))
    down, half = q("ws.lower_mouth_distance"), q("dp.height") / 2
    corners.append((top_y - down * math.cos(slope) - half * math.sin(slope),
                    top_z - down * math.sin(slope) + half * math.cos(slope)))
    return x, corners


def well_shaft(led: Ledger) -> int:
    """The well shaft from the foot of the Grand Gallery to the Descending Passage."""
    q = led.q
    x, corners = _well_axis(led)
    side, low = q("ws.upper_side"), math.sqrt(q("ws.lower_area"))
    y, z = corners[0]
    # The level run west from the slot between the Gallery's ramps, over the head of the shaft.
    parts = [_box(x - side / 2, y - side / 2, z, q("gg.north_end.x") - q("gg.slot_width") / 2, y + side / 2, z + side)]
    corners[0] = (y, z + side / 2)  # the first vertical starts inside the level run
    # ponytail: Haase's segments 1 to 4 are built as printed. The fifth is whatever closes the chain
    # on the surveyed lower mouth (9.95 m at 63.5 deg against his "about 9.50 m at 75 deg"),
    # because the chain built from all his figures ends under the passage floor, 2.0 m from that mouth.
    sections = [(side, side), (side, side), (q("ws.seg3.side_a"), q("ws.seg3.side_b")),
                (q("ws.seg4.width"), q("ws.seg4.height")), (low, low)]
    for (y0, z0), (y1, z1), (width, height) in zip(corners, corners[1:], sections):
        parts.append(_duct((x, y0, z0), (x, y1, z1), width, height, centred=True))
    # The level link east into the west wall of the Descending Passage.
    y, z = corners[-1]
    parts.append(_box(x - low / 2, y - low / 2, z - low / 2,
                      q("dp.entrance.x") - q("dp.width") / 2, y + low / 2, z + low / 2))
    return _join(parts)


def grotto(led: Ledger) -> int:
    """The Grotto: a cavity round the lined stretch of the well shaft's third segment."""
    q = led.q
    x, corners = _well_axis(led)
    y, foot = corners[3]
    half = q("grotto.plan_side") / 2
    bottom = foot + q("ws.seg3.rock_cut_length")  # the lined stretch stands on the rock-cut one
    return _box(x - half, y - half, bottom, x + half, y + half, bottom + q("grotto.height"))


# ---- upper system --------------------------------------------------------------------------

def _stepped(tiers) -> list[tuple[float, float]]:
    """Outline of a symmetric stepped section as (offset from the centre line, height) corners.

    tiers lists (width, height of its top) from the bottom up; the first tier starts at height 0.
    """
    left, bottom = [], 0.0
    for width, top in tiers:
        left += [(-width / 2, bottom), (-width / 2, top)]
        bottom = top
    return left + [(-u, v) for u, v in reversed(left)]


def faces(led: Ledger, casing: bool = True) -> tuple[float, float]:
    """Half the base side, and the height at which the four faces meet.

    casing=True gives the original casing faces. casing=False gives the core faces, which pass
    through the surveyed core base and the edge of the present top platform. At height z a face
    stands half * (1 - z / apex) from the centre.
    """
    q = led.q
    if casing:
        return q("pyr.base_side") / 2, q("pyr.height_original")
    half = q("pyr.core_base_side") / 2
    return half, q("pyr.height_present") * half / (half - q("pyr.top_platform_half_width"))


def ascending_passage(led: Ledger, plugs: bool = True) -> int:
    """The Ascending Passage up to the north wall of the Grand Gallery.

    plugs=True leaves only the open part above the three granite plugs.
    ponytail: the 1.9 m stub below the plugs, a pocket in the roof of the Descending Passage, is
    left out, because one space is one solid.
    """
    q = led.q
    x, wall, top = _point(led, "ap.end")
    y, z = q("ap.start.y"), q("ap.start.z")
    slope = math.atan2(top - z, y - wall)
    if plugs:
        up = q("ap.plug_start") + q("ap.plug_length")
        y, z = y - up * math.cos(slope), z + up * math.sin(slope)
    width, height = q("ap.width"), q("ap.height")
    # Carried on past the end of the floor until the roof is past the wall too (by OVERLAP, so that the
    # cut does not run along an edge of the duct), then cut off at the wall.
    duct = _duct((x, y, z), (x, wall, top), width, height, extend=height * math.tan(slope) + OVERLAP)
    beyond = _box(x - width, wall - MARGIN, top - MARGIN, x + width, wall, top + 2 * MARGIN)
    out, _ = occ.cut([(3, duct)], [(3, beyond)])
    [(_, tag)] = out
    return tag


def queens_passage(led: Ledger) -> int:
    """The level passage from the foot of the Grand Gallery to the Queen's Chamber, with its floor step."""
    q = led.q
    x, half = q("pyr.passage_plane_x"), q("qp.width") / 2
    north, south = q("gg.north_end.y"), q("qc.north_wall.y")
    step = north - q("qp.step_distance")
    high, low = q("qp.floor_north.z"), q("qp.floor_south.z")
    return _join([
        _box(x - half, step, high, x + half, north, high + q("qp.height_north")),
        _box(x - half, south, low, x + half, step, low + q("qp.height_south")),
    ])


def queens_chamber(led: Ledger) -> int:
    """The gabled chamber with the corbelled niche in its east wall."""
    q = led.q
    north, east, floor = q("qc.north_wall.y"), q("qc.east_wall.x"), q("qc.floor.z")
    south, west = north - q("qc.width_ns"), east - q("qc.length_ew")
    middle = (north + south) / 2
    eave, ridge = floor + q("qc.wall_height"), floor + q("qc.ridge_height")
    gable = [(west, north, floor), (west, south, floor), (west, south, eave), (west, middle, ridge),
             (west, north, eave)]
    room = _prism(gable, (east - west, 0, 0))
    # ponytail: no source read places the niche along the wall or gives the level of each overlap.
    # It is centred on the wall and its overlaps are spaced evenly up to the surveyed level at
    # which it reaches its top width.
    laps = round(q("qc.niche.overlaps"))
    wide, narrow, level = q("qc.niche.width_base"), q("qc.niche.width_top"), q("qc.niche.top_width_level")
    tiers = [(wide - k * (wide - narrow) / laps, (k + 1) * level / laps) for k in range(laps)]
    tiers.append((narrow, q("qc.niche.height")))
    outline = [(east - OVERLAP, middle + u, floor + v) for u, v in _stepped(tiers)]
    niche = _prism(outline, (q("qc.niche.depth") + OVERLAP, 0, 0))
    return _join([room, niche])


def _qc_shaft(led: Ledger, side: str) -> int:
    """A Queen's Chamber shaft: level from behind the stone left at the wall, then inclined up to its slab."""
    q = led.q
    way = 1.0 if side == "north" else -1.0
    wall = q("qc.north_wall.y") - (0.0 if side == "north" else q("qc.width_ns"))
    # ponytail: no source read places the mouths. They are centred on their walls, at the level
    # from which the shaft, carried on, meets the casing at Petrie's projected exit level.
    x = q("qc.east_wall.x") - q("qc.length_ew") / 2
    slope = math.radians(q(f"qcs.{side}.angle"))
    knee = wall + way * q(f"qcs.{side}.horizontal_length")
    half, apex = faces(led)
    exit_z = q(f"qcs.{side}.projected_exit.z")
    z = exit_z - (half * (1 - exit_z / apex) - way * knee) * math.tan(slope)
    rest = q(f"qcs.{side}.length_to_slab") - q(f"qcs.{side}.horizontal_length")
    end = (x, knee + way * rest * math.cos(slope), z + rest * math.sin(slope))
    width, height = q("qcs.width"), q(f"qcs.{side}.height")
    return _join([
        _duct((x, wall + way * q("qcs.stone_left"), z), (x, knee, z), width, height, centred=True),
        _duct((x, knee, z), end, width, height, centred=True),
    ])


def qc_shaft_north(led: Ledger) -> int:
    return _qc_shaft(led, "north")


def qc_shaft_south(led: Ledger) -> int:
    return _qc_shaft(led, "south")


def _gallery_tiers(led: Ledger) -> list[tuple[float, float]]:
    """The Grand Gallery's vertical section, bottom up: slot between the ramps, walls, then the laps."""
    q = led.q
    laps = round(q("gg.laps"))
    width, first, top = q("gg.width"), q("gg.first_lap_height"), q("gg.height")
    tiers = [(q("gg.slot_width"), q("gg.ramp_height")), (width, first)]
    # ponytail: the laps get equal heights; Petrie's lap table is garbled in both copies read.
    tiers += [(width - 2 * k * q("gg.overhang") / laps, first + k * (top - first) / laps) for k in range(1, laps + 1)]
    return tiers


def grand_gallery(led: Ledger) -> int:
    """The corbelled vertical section at the north wall, swept up the slope to the south wall."""
    q = led.q
    x, north, low = _point(led, "gg.north_end")
    south, high = q("gg.south_end.y"), q("gg.south_end.z")
    # ponytail: the end walls are vertical; their own corbelling (about 1.2 percent of the volume) is dropped.
    outline = [(x + u, north, low + v) for u, v in _stepped(_gallery_tiers(led))]
    gallery = _prism(outline, (0, south - north, high - low))
    # The Great Step is solid from its face to the south wall, up to its top.
    # ponytail: the swept section keeps its ramps as far as the south wall. Over the last 0.96 m they
    # rise above the top of the Step (by up to 0.48 m) and are left standing on it: 0.24 m3.
    reach = q("gg.width") / 2 + MARGIN
    step = _box(x - reach, south - MARGIN, low, x + reach, q("gg.step_face.y"), q("gg.step_top.z"))
    out, _ = occ.cut([(3, gallery)], [(3, step)])
    [(_, tag)] = out
    return tag


def antechamber(led: Ledger, portcullis: bool = True, grooves_connected: bool = False) -> int:
    """The Antechamber with the low passage that enters it from the Grand Gallery.

    portcullis=True: the southernmost slab stands against the south wall, so the void stops one
    slab thickness short of that wall. grooves_connected=True then adds one duct through the
    slab, at the top of the doorway to the King's Chamber.
    """
    q = led.q
    x, half = q("ante.x"), q("ante.width") / 2
    north, south = q("ante.north_end.y"), q("ante.south_end.y")
    floor, roof = q("ante.floor.z"), q("ante.roof.z")
    low_half, lintel = q("ante.low_passage.width") / 2, floor + q("ante.low_passage.height")
    # ponytail: a gross box. The wainscots, the slots, the granite leaf and the two northern slabs
    # (no source read gives their positions) are not modelled.
    slab_face = south + (q("ante.slab_thickness") if portcullis else 0.0)
    parts = [
        _box(x - half, slab_face, floor, x + half, north, roof),
        _box(x - low_half, north - OVERLAP, floor, x + low_half, q("gg.south_end.y"), lintel),
    ]
    if portcullis and grooves_connected:
        # ponytail: one square duct with the total section the four grooves could have. Their
        # run-outs (0.105 m wide, 5 mm deep at most) are finer than any mesh this model feeds.
        side = math.sqrt(q("ante.groove_connected_area"))
        parts.append(_box(x - side / 2, south, lintel - side, x + side / 2, slab_face + OVERLAP, lintel))
    return _join(parts)


def kings_chamber(led: Ledger) -> int:
    """The King's Chamber with the low passage that enters it from the Antechamber."""
    q = led.q
    floor, north, east = q("kc.floor.z"), q("kc.north_wall.y"), q("kc.east_wall.x")
    room = _box(q("kc.west_wall.x"), q("kc.south_wall.y"), floor, east, north, q("kc.ceiling.z"))
    # The passage's east side is flush with the chamber's east wall (surveyed within 3 mm of it).
    passage = _box(east - q("ante.low_passage.width"), north - OVERLAP, floor,
                   east, q("ante.south_end.y"), floor + q("ante.low_passage.height"))
    # ponytail: the coffer is not modelled; no source read gives its position on the floor.
    return _join([room, passage])


def _kc_shaft(led: Ledger, side: str, to_casing: bool, level_end: bool) -> int:
    """A King's Chamber shaft: level from the chamber wall, then inclined to the face.

    to_casing=False stops it at the core face: the casing is absent, or closes the shaft.
    level_end=True makes its last stretch level, as Perring drew the southern outlet.
    """
    q = led.q
    way = 1.0 if side == "north" else -1.0
    wall = q(f"kc.{side}_wall.y")
    x = q("kc.east_wall.x") - q("kcs.mouth_from_east_wall")
    width, height = q(f"kcs.{side}.width"), q(f"kcs.{side}.height")
    z = q("kc.floor.z") + q("kcs.mouth_height") + height / 2  # level of the axis at the mouth
    slope = math.radians(q(f"kcs.{side}.angle"))
    level = q("kcs.horizontal_length")
    flat = q("kcs.level_end_length") if level_end else 0.0
    # Length of the incline, so that the axis ends on the face: its distance from the centre
    # there is half * (1 - height / apex).
    half, apex = faces(led, to_casing)
    rest = (half * (1 - z / apex) - way * wall - level - flat) / (math.cos(slope) + half / apex * math.sin(slope))
    axis = [(x, wall, z), (x, wall + way * level, z)]
    axis.append((x, axis[-1][1] + way * rest * math.cos(slope), z + rest * math.sin(slope)))
    if level_end:
        axis.append((x, axis[-1][1] + way * flat, axis[-1][2]))
    return _join([_duct(a, b, width, height, centred=True) for a, b in zip(axis, axis[1:])])


def kc_shaft_north(led: Ledger, to_casing: bool = True, level_end: bool = False) -> int:
    return _kc_shaft(led, "north", to_casing, level_end)


def kc_shaft_south(led: Ledger, to_casing: bool = True, level_end: bool = False) -> int:
    return _kc_shaft(led, "south", to_casing, level_end)


def relieving_chambers(led: Ledger) -> int:
    """The five compartments above the King's Chamber, as one block.

    ponytail: Davison's plan, the sum of the five mean heights, the top at the surveyed apex.
    The granite floors between the compartments are left out, because no source read gives a
    level for the four lower ones. Split it when Maragioglio and Rinaldi's plates are read.
    """
    q = led.q
    x = (q("kc.east_wall.x") + q("kc.west_wall.x")) / 2
    y = (q("kc.north_wall.y") + q("kc.south_wall.y")) / 2
    a, b = q("rc.davison.length") / 2, q("rc.davison.width") / 2
    top = q("kc.floor.z") + q("rc.apex_above_kc_floor")
    height = sum(q(f"rc.{name}.height") for name in ("davison", "wellington", "nelson", "arbuthnot", "campbell"))
    return _box(x - a, y - b, top - height, x + a, y + b, top)


def big_void(led: Ledger, inclined: bool = False) -> int:
    """The Big Void: a plain box of the Gallery's width and section area, level or parallel to the Gallery."""
    q = led.q
    x, width, length = q("pyr.passage_plane_x"), q("gg.width"), q("bv.length")
    y, z = q("bv.south_end.y") + length / 2, q("bv.centre.z")
    slope = math.radians(q("bv.incline_angle")) if inclined else 0.0
    dy, dz = length / 2 * math.cos(slope), length / 2 * math.sin(slope)
    # Inclined, it rises to the south about the same centre, as the Gallery does.
    return _duct((x, y + dy, z - dz), (x, y - dy, z + dz), width, q("bv.section_area") / width, centred=True)


def north_face_corridor(led: Ledger) -> int:
    """The North Face Corridor: a level cuboid over the Descending Passage, behind the chevrons."""
    q = led.q
    x, half, floor = q("dp.entrance.x"), q("nfc.width") / 2, q("nfc.floor.z")
    roof = floor + q("nfc.height")
    # ponytail: no source read places the chevrons. They are taken to stand on the core face at the
    # level of the corridor's roof, which keeps the whole cuboid behind that face.
    core_half, core_apex = faces(led, casing=False)
    north = core_half * (1 - roof / core_apex) - q("nfc.start_offset")
    return _box(x - half, north - q("nfc.length"), floor, x + half, north, roof)
