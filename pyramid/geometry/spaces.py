"""One builder per interior space. Each takes the ledger and returns the tag of one OCC volume.

Frame: origin at the pyramid's centre on the pavement; X east, Y north, Z up; metres.
Call these inside frame.session().
"""
import math

import gmsh

from pyramid.ledger import Ledger

occ = gmsh.model.occ

OVERLAP = 0.05  # m. How far a part is pushed into the part it joins, so that a fuse has a volume to merge.


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
