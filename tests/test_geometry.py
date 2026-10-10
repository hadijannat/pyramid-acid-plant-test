"""Tests for the geometry: the gmsh session, the builders of the spaces, the model and its self-checks."""
import dataclasses
import functools
import math

import gmsh
import pytest

from pyramid import ledger
from pyramid.geometry import frame
from pyramid.geometry import model
from pyramid.geometry import spaces

occ = gmsh.model.occ


@functools.cache
def led() -> ledger.Ledger:
    """The ledger kept in the repository, loaded once per test run."""
    return ledger.load()


@pytest.fixture
def gm():
    """A fresh gmsh session for one test."""
    with frame.session():
        yield


def volume(tag: int) -> float:
    return occ.getMass(3, tag)


def box(tag: int) -> tuple:
    """(xmin, ymin, zmin, xmax, ymax, zmax) of a volume."""
    return occ.getBoundingBox(3, tag)


def test_inch_converts_inches_to_metres():
    assert frame.IN == 0.0254
    assert frame.inch(9068.8) == pytest.approx(230.34752)  # Petrie's base side


def test_session_opens_gmsh_quietly_and_always_closes_it():
    assert not gmsh.isInitialized()
    with frame.session():
        assert gmsh.isInitialized()
        assert gmsh.option.getNumber("General.Terminal") == 0
    assert not gmsh.isInitialized()
    with pytest.raises(RuntimeError, match="boom"):
        with frame.session():
            raise RuntimeError("boom")
    assert not gmsh.isInitialized()


def test_pointed_pyramid_volume_is_base_squared_times_height_over_three(gm):
    tag = model.pyramid_solid(230.0, 138.75)  # the 2018 study's pyramid
    assert volume(tag) == pytest.approx(230.0 ** 2 * 138.75 / 3, rel=1e-3)  # 2 446 625 m3
    assert box(tag) == pytest.approx((-115.0, -115.0, 0.0, 115.0, 115.0, 138.75), abs=1e-3)


def test_truncated_pyramid_is_the_frustum_under_the_cut(gm):
    base, apex, top = 230.3475, 146.7104, 137.3759  # casing base, original height, present top
    tag = model.pyramid_solid(base, apex, top)
    side = base * (1 - top / apex)  # the platform the cut leaves
    assert side == pytest.approx(14.656, abs=1e-3)
    frustum = top / 3 * (base ** 2 + base * side + side ** 2)
    assert frustum == pytest.approx(2594148.2, abs=0.5)
    assert volume(tag) == pytest.approx(frustum, rel=1e-3)
    assert box(tag) == pytest.approx((-base / 2, -base / 2, 0.0, base / 2, base / 2, top), abs=1e-3)
    # the missing top: 668 m3 less than the pointed pyramid
    assert base ** 2 * apex / 3 - volume(tag) == pytest.approx(668.3, abs=1.0)


def test_bedrock_block_hangs_under_the_pavement(gm):
    tag = model.bedrock_block(230.3475, 60.0)
    assert volume(tag) == pytest.approx(230.3475 ** 2 * 60.0)  # 3 183 598 m3
    assert box(tag) == pytest.approx((-115.17375, -115.17375, -60.0, 115.17375, 115.17375, 0.0), abs=1e-3)


def test_variants_are_the_nine_switches_with_their_defaults():
    names = [field.name for field in dataclasses.fields(model.Variants)]
    assert names == ["casing", "kc_shafts_open", "kc_shaft_ends_level", "portcullis", "grooves_connected",
                     "ascending_plugs", "pit_excavated", "big_void_inclined", "apex_truncated"]
    assert dataclasses.astuple(model.Variants()) == (True, True, False, True, False, True, False, False, True)
    with pytest.raises(dataclasses.FrozenInstanceError):
        model.Variants().casing = False


def test_paper_level_is_the_2018_pyramid_with_its_three_box_chambers(gm):
    built = model.build(led(), level="paper")
    assert (built.level, built.variants, built.bedrock) == ("paper", model.Variants(), None)
    assert list(built.spaces) == ["paper_kings_chamber", "paper_queens_chamber", "paper_lower_chamber"]
    volumes = {name: space.volume for name, space in built.spaces.items()}
    assert volumes == pytest.approx({
        "paper_kings_chamber": 605.0,     # 11 x 5 x 11 m
        "paper_queens_chamber": 150.0,    # 5 x 5 x 6 m
        "paper_lower_chamber": 133.952,   # 5.2 x 5.6 x 4.6 m
    })
    for name, (key, _) in model.PAPER.items():  # each volume is the product of its three ledger dimensions
        q = led().q
        assert volumes[name] == pytest.approx(q(f"{key}.length") * q(f"{key}.width") * q(f"{key}.height"))
    chamber = built.spaces["paper_kings_chamber"]
    assert (chamber.name, chamber.label, chamber.volume_id) == (
        "paper_kings_chamber", "King's Chamber (2018 study's model)", None)
    # the reading this plan records: 11 m east-west, 5 m north-south, 11 m high,
    # centre 5 m south of the axis and 40.5 m above the base
    assert box(chamber.tag) == pytest.approx((-5.5, -7.5, 35.0, 5.5, -2.5, 46.0), abs=1e-4)
    assert box(built.spaces["paper_lower_chamber"].tag)[5] == pytest.approx(-27.5, abs=1e-4)  # wholly under the base
    # masonry: the pointed pyramid less the two chambers that lie inside it
    assert volume(built.masonry) == pytest.approx(2446625.0 - 605.0 - 150.0, abs=1.0)


def test_build_rejects_an_unknown_level(gm):
    with pytest.raises(ValueError, match="unknown level: 'sketch'"):
        model.build(led(), level="sketch")


def test_package_reexports_the_model():
    import pyramid.geometry as geometry
    assert (geometry.build, geometry.Variants, geometry.Model, geometry.Space) == (
        model.build, model.Variants, model.Model, model.Space)


def test_ledger_holds_the_grotto_placeholder():
    side = led().quantities["grotto.plan_side"]
    assert (side.value, side.unit, side.verified) == (1.04, "m", False)
    assert side.note.startswith("assumed for the model")


C45 = math.cos(math.radians(45))


@pytest.mark.parametrize("end, expected", [
    # rising to the north: the far end is 7.071 m north and 7.071 m up
    ((0.0, 10 * C45, 10 * C45), (-0.5, -0.3536, 0.0, 0.5, 7.0711, 7.4246)),
    # rising to the south: the mirror image, with the roof still above the floor
    ((0.0, -10 * C45, 10 * C45), (-0.5, -7.0711, 0.0, 0.5, 0.3536, 7.4246)),
    # falling to the south: the floor ends 7.071 m down, the roof starts 0.354 m above the start
    ((0.0, -10 * C45, -10 * C45), (-0.5, -7.4246, -7.0711, 0.5, 0.0, 0.3536)),
])
def test_duct_runs_from_start_to_end_with_its_roof_up(gm, end, expected):
    tag = spaces._duct((0.0, 0.0, 0.0), end, 1.0, 0.5)  # 10 m long, 1 m wide, 0.5 m high
    assert box(tag) == pytest.approx(expected, abs=1e-3)
    assert volume(tag) == pytest.approx(10 * 1.0 * 0.5)


def test_duct_can_be_centred_on_its_axis_and_lengthened(gm):
    # a vertical shaft 4 m deep, 0.6 m east-west by 0.8 m north-south, about its axis
    shaft = spaces._duct((0.0, 0.0, 0.0), (0.0, 0.0, -4.0), 0.6, 0.8, centred=True)
    assert box(shaft) == pytest.approx((-0.3, -0.4, -4.0, 0.3, 0.4, 0.0), abs=1e-3)
    # a level duct 2 m long heading north, carried 0.5 m further
    longer = spaces._duct((1.0, 2.0, 3.0), (1.0, 4.0, 3.0), 1.0, 1.0, extend=0.5)
    assert box(longer) == pytest.approx((0.5, 2.0, 3.0, 1.5, 4.5, 4.0), abs=1e-3)


def test_descending_passage_runs_between_its_two_surveyed_ends(gm):
    q = led().q
    tag = spaces.descending_passage(led())
    x0, y0, z0, x1, y1, z1 = box(tag)
    slope, height = math.radians(q("dp.angle")), q("dp.height")
    # the floor at the entrance (y 101.854, z 16.972) and at the south end (y 7.772, z -29.997)
    assert y1 == pytest.approx(q("dp.entrance.y"), abs=0.08)
    assert z1 - height * math.cos(slope) == pytest.approx(q("dp.entrance.z"), abs=0.08)
    assert y0 + height * math.sin(slope) == pytest.approx(q("dp.south_end.y"), abs=0.08)
    assert z0 == pytest.approx(q("dp.south_end.z"), abs=0.08)
    assert (y1, z0) == pytest.approx((101.854, -29.9974), abs=1e-3)
    assert (x0, x1) == pytest.approx((6.7624, 7.8172), abs=1e-3)  # 1.055 m wide about the passage plane
    assert volume(tag) == pytest.approx(133.10, abs=0.05)  # 105.155 m x 1.0549 m x 1.1999 m
    low, high = led().rng("dp.volume")
    assert low <= volume(tag) <= high


def test_subterranean_chamber_has_its_ramped_floor_its_recess_and_its_entrance_passage(gm):
    q = led().q
    tag = spaces.subterranean_chamber(led())
    x0, y0, z0, x1, y1, z1 = box(tag)
    assert (x0, x1) == pytest.approx((-6.3754, 7.6912), abs=1e-3)  # 14.067 m east-west about x = 0.658
    assert y0 == pytest.approx(-9.2952, abs=1e-3)  # the south wall
    assert y1 == pytest.approx(q("dp.south_end.y"), abs=0.08)  # the passage starts at the foot of the slope
    assert z1 == pytest.approx(q("sub.roof_centre.z"), abs=1e-3)  # the roof, -26.822
    assert z0 == pytest.approx(-31.8516, abs=1e-3)  # the floor of the recess, 198 in under the roof
    assert volume(tag) == pytest.approx(330.25, abs=0.2)  # 317.94 chamber + 5.32 recess + 6.99 passage
    low, high = led().rng("sub.volume")
    assert low <= volume(tag) <= high


def test_pit_before_1837_and_as_excavated(gm):
    q = led().q
    old, dug = spaces.pit(led()), spaces.pit(led(), excavated=True)
    # set diagonally at the centre of the chamber's east half: 1.9 m sides, 2.687 m corner to corner
    assert box(old)[:2] == pytest.approx((2.8310, -6.4997), abs=1e-3)
    assert box(old)[3:5] == pytest.approx((5.5180, -3.8127), abs=1e-3)
    assert (box(old)[2], box(old)[5]) == pytest.approx((q("pit.original_bottom.z"), -31.8516), abs=1e-3)
    assert box(dug)[2] == pytest.approx(q("pit.excavated_bottom.z"), abs=1e-3)  # -42.1
    assert volume(old) == pytest.approx(8.136, abs=0.01)  # 1.9^2 x 1.702 + 1.4^2 x 1.017
    assert volume(dug) == pytest.approx(22.895, abs=0.01)  # 1.9^2 x 1.702 + 1.4^2 x 8.547
    for key, value in (("pit.volume", volume(old)), ("pit.volume_excavated", volume(dug))):
        low, high = led().rng(key)
        assert low <= value <= high


def test_south_passage_runs_from_the_chamber_wall_to_its_surveyed_dead_end(gm):
    q = led().q
    tag = spaces.south_passage(led())
    x0, y0, z0, x1, y1, z1 = box(tag)
    assert y0 == pytest.approx(q("sp.south_end.y"), abs=1e-3)  # -25.705
    assert z0 == pytest.approx(q("sp.north_end.z"), abs=1e-3)  # -30.963, the floor at the chamber
    assert y1 == pytest.approx(-9.2952, abs=0.01)  # the chamber's south wall; the tilted roof edge is 7 mm past it
    assert (x0, x1) == pytest.approx((6.8765, 7.5965), abs=1e-3)
    assert volume(tag) == pytest.approx(8.862, abs=0.01)  # 16.41 m x 0.72 m x 0.75 m
    low, high = led().rng("sp.volume")
    assert low <= volume(tag) <= high


def test_well_shaft_joins_the_gallery_foot_to_the_descending_passage(gm):
    q = led().q
    x, corners = spaces._well_axis(led())
    assert x == pytest.approx(5.0116, abs=1e-3)
    # Haase's first three segments end "a good metre above base"; the fourth runs down at 45 deg
    assert corners[3] == pytest.approx((37.0829, 1.3802), abs=1e-3)
    assert corners[4] == pytest.approx((18.3445, -17.3582), abs=1e-3)
    # the closing segment lands on the surveyed lower mouth, within 10 percent of Haase's 9.50 m
    assert corners[5] == pytest.approx((13.9057, -26.2648), abs=1e-3)
    assert math.dist(corners[4], corners[5]) == pytest.approx(q("ws.seg5.length"), rel=0.10)  # 9.95 m
    tag = spaces.well_shaft(led())  # joining parts that do not touch would raise
    x0, y0, z0, x1, y1, z1 = box(tag)
    assert z1 == pytest.approx(q("ws.top.z") + q("ws.upper_side"), abs=1e-3)  # 22.41, roof of the level run
    assert x1 == pytest.approx(q("gg.north_end.x") - q("gg.slot_width") / 2, abs=1e-3)  # 6.767, the slot
    assert (x0, y1) == pytest.approx((4.6566, 40.7766), abs=1e-3)
    assert (y0, z0) == pytest.approx((13.552, -26.618), abs=0.01)  # the link at the lower mouth
    assert volume(tag) == pytest.approx(29.26, abs=0.05)  # 29.68 m3 of parts less 0.42 m3 where they overlap
    low, high = led().rng("ws.volume")
    assert low <= volume(tag) <= high  # 23.0 to 34.6


def test_grotto_wraps_the_lined_stretch_of_the_well_shaft(gm):
    q = led().q
    tag = spaces.grotto(led())
    x0, y0, z0, x1, y1, z1 = box(tag)
    assert ((x0 + x1) / 2, (y0 + y1) / 2) == pytest.approx((5.0116, 37.0829), abs=1e-3)  # on the shaft's axis
    assert (x1 - x0, y1 - y0) == pytest.approx((1.04, 1.04), abs=1e-3)
    assert (z0, z1) == pytest.approx((3.530, 5.530), abs=1e-3)  # standing on the 2.15 m rock-cut stretch
    assert z1 < q("site.bedrock_z_at_well_shaft")  # under the rock surface Haase gives, 5.70 m
    assert volume(tag) == pytest.approx(1.04 * 1.04 * 2.0)


def test_ledger_holds_the_upper_system_additions():
    floor = led().quantities["nfc.floor.z"]
    assert (floor.value, floor.unit, floor.verified) == (18.31, "m", False)
    assert floor.note.startswith("assumed for the model")
    assert led().rng("ap.volume_above_plugs") == (40.5, 43.0)
    assert led().rng("qc.volume_with_niche") == (166.6, 171.8)
    assert led().rng("kc.volume_with_passage") == (321.5, 325.3)
    # two of them are sums of figures the ledger already holds
    assert led().q("qc.volume_with_niche") == pytest.approx(led().q("qc.volume") + led().q("qc.niche.volume"))
    assert led().q("kc.volume_with_passage") == pytest.approx(led().q("kc.volume") + 3.0)


def test_faces_give_the_casing_and_the_core():
    half, apex = spaces.faces(led())
    assert (half, apex) == pytest.approx((115.17375, 146.7104))
    core_half, core_apex = spaces.faces(led(), casing=False)
    assert (core_half, core_apex) == pytest.approx((114.31905, 144.3618), abs=1e-3)
    # the core face passes through the edge of the present top platform, 5.532 m from the centre
    top = led().q("pyr.height_present")
    assert core_half * (1 - top / core_apex) == pytest.approx(led().q("pyr.top_platform_half_width"))
    # at the level of the entrance the casing face stands where Petrie puts the entrance, 101.85 m north
    entrance = half * (1 - led().q("dp.entrance.z") / apex)
    assert entrance == pytest.approx(led().q("dp.entrance.y"), abs=0.01)


def test_stepped_outline_goes_up_the_left_side_and_down_the_right():
    assert spaces._stepped([(1.0, 0.5), (2.0, 1.5)]) == [
        (-0.5, 0.0), (-0.5, 0.5), (-1.0, 0.5), (-1.0, 1.5), (1.0, 1.5), (1.0, 0.5), (0.5, 0.5), (0.5, 0.0)]


def test_ascending_passage_stops_at_the_gallery_wall_and_above_the_plugs(gm):
    q = led().q
    open_part, whole = spaces.ascending_passage(led()), spaces.ascending_passage(led(), plugs=False)
    for tag in (open_part, whole):
        x0, y0, z0, x1, y1, z1 = box(tag)
        assert y0 == pytest.approx(q("ap.end.y"), abs=1e-3)  # cut off at the Gallery's north wall, 41.321
        assert z1 == pytest.approx(22.9934, abs=1e-3)  # the roof where it meets that wall
        assert (x0, x1) == pytest.approx((6.7615, 7.8181), abs=1e-3)
    # without plugs the floor starts where it meets the floor of the Descending Passage
    assert box(whole)[2] == pytest.approx(q("ap.start.z"), abs=1e-3)  # 4.392
    # with plugs it starts 6.42 m up the slope, at the top of the plugs
    assert box(open_part)[2] == pytest.approx(7.2121, abs=1e-3)
    assert volume(whole) == pytest.approx(50.25, abs=0.05)  # 39.29 m x 1.2694 m2 + 0.37 under the roof at the wall
    assert volume(open_part) == pytest.approx(42.10, abs=0.05)  # 32.87 m x 1.2694 m2 + 0.37
    for key, value in (("ap.volume_gross", volume(whole)), ("ap.volume_above_plugs", volume(open_part))):
        low, high = led().rng(key)
        assert low <= value <= high


def test_queens_passage_steps_down_before_the_chamber(gm):
    tag = spaces.queens_passage(led())
    # from the Gallery's north wall (41.321) to the chamber's (2.591); floor 21.707 dropping to 21.207
    assert box(tag) == pytest.approx((6.7648, 2.5908, 21.2065, 7.8148, 41.3207, 22.8865), abs=1e-3)
    assert volume(tag) == pytest.approx(50.54, abs=0.02)  # 33.20 x 1.05 x 1.17 + 5.53 x 1.05 x 1.68
    low, high = led().rng("qp.volume")
    assert low <= volume(tag) <= high


def test_queens_chamber_is_gabled_and_has_its_niche(gm):
    q = led().q
    tag = spaces.queens_chamber(led())
    # west wall, south wall, floor; back of the niche (east wall 7.823 + 1.041), north wall, ridge
    assert box(tag) == pytest.approx((2.0709, -2.6378, 21.1938, 8.8646, 2.5908, 27.4193), abs=1e-3)
    assert box(tag)[5] == pytest.approx(q("qc.ridge.z"), abs=0.076)  # Petrie's ridge level, 27.399
    assert volume(tag) == pytest.approx(169.31, abs=0.05)  # 140.92 box + 23.16 gable + 5.22 niche
    low, high = led().rng("qc.volume_with_niche")
    assert low <= volume(tag) <= high


@pytest.mark.parametrize("side, way, start, far, top, expected_volume", [
    ("north", 1.0, 2.7178, 53.3765, 60.1278, 2.81),
    ("south", -1.0, -2.7648, -52.9452, 61.0842, 2.88),
])
def test_queens_chamber_shaft_starts_behind_the_wall_and_aims_at_petries_exit_level(
        gm, side, way, start, far, top, expected_volume):
    q = led().q
    tag = getattr(spaces, f"qc_shaft_{side}")(led())
    x0, y0, z0, x1, y1, z1 = box(tag)
    near_y, far_y = (y0, y1) if way > 0 else (y1, y0)
    assert near_y == pytest.approx(start, abs=1e-3)  # 0.127 m of stone left between it and the chamber
    assert (far_y, z1) == pytest.approx((far, top), abs=0.01)
    assert (x0 + x1) / 2 == pytest.approx(4.947, abs=1e-3)  # centred on its wall
    # carried on from its upper end, the axis meets the casing at Petrie's projected level
    slope, height = math.radians(q(f"qcs.{side}.angle")), q(f"qcs.{side}.height")
    end_y, end_z = way * far_y - height / 2 * math.sin(slope), z1 - height / 2 * math.cos(slope)
    half, apex = spaces.faces(led())
    more = (half * (1 - end_z / apex) - end_y) / (math.cos(slope) + half / apex * math.sin(slope))
    assert end_z + more * math.sin(slope) == pytest.approx(q(f"qcs.{side}.projected_exit.z"), abs=0.01)
    assert volume(tag) == pytest.approx(expected_volume, abs=0.02)
    low, high = led().rng("qcs.volume")
    assert low <= volume(tag) <= high


def test_grand_gallery_is_the_corbelled_section_swept_up_the_slope(gm):
    q = led().q
    # the section: slot 1.0465 x 0.606, walls 2.0935 apart up to the first lap at 2.29 m, seven laps up to 8.6 m
    tiers = spaces._gallery_tiers(led())
    assert len(tiers) == 9
    assert tiers[-1] == pytest.approx((q("gg.roof_width"), q("gg.height")), abs=0.01)  # 1.05 m wide under the roof
    area = sum(width * (top - bottom) for (width, top), bottom in zip(tiers, [0.0] + [top for _, top in tiers]))
    assert area == pytest.approx(13.605, abs=0.005)
    tag = spaces.grand_gallery(led())
    # west and east walls; south wall; floor at the north wall; north wall; top of the roof at the south wall
    assert box(tag) == pytest.approx((6.2430, -1.5672, 21.6560, 8.3366, 41.3207, 51.5006), abs=1e-3)
    assert box(tag)[5] == pytest.approx(q("gg.roof_top.z"), abs=0.076)
    assert volume(tag) == pytest.approx(582.57, abs=0.3)  # 13.605 m2 x 42.888 m = 583.50, less 0.93 for the Great Step
    low, high = led().rng("gg.volume")
    assert low <= volume(tag) <= high


def test_antechamber_stops_at_the_last_slab_unless_the_portcullis_is_absent(gm):
    q = led().q
    closed = spaces.antechamber(led())
    opened = spaces.antechamber(led(), portcullis=False)
    grooved = spaces.antechamber(led(), grooves_connected=True)
    # from the Gallery's south wall to one slab thickness (0.535 m) short of the antechamber's south wall
    assert box(closed) == pytest.approx((6.3983, -5.3019, 42.9920, 8.0493, -1.5672, 46.7741), abs=1e-3)
    assert box(opened)[1] == pytest.approx(q("ante.south_end.y"), abs=1e-3)  # -5.837, the south wall itself
    assert box(grooved)[1] == pytest.approx(q("ante.south_end.y"), abs=1e-3)  # the groove duct reaches it
    assert volume(closed) == pytest.approx(16.615, abs=0.01)  # 15.07 box + 1.54 passage from the Gallery
    assert volume(opened) == pytest.approx(19.955, abs=0.01)  # 18.41 box + 1.54
    # the groove duct adds its section, 0.002 m2, times the slab thickness
    assert volume(grooved) - volume(closed) == pytest.approx(0.002 * 0.535, abs=1e-4)
    low, high = led().rng("ante.volume")
    assert all(low <= volume(tag) <= high for tag in (closed, opened, grooved))


def test_kings_chamber_fills_its_surveyed_planes_and_keeps_its_entrance_passage(gm):
    q = led().q
    tag = spaces.kings_chamber(led())
    planes = (q("kc.west_wall.x"), q("kc.south_wall.y"), q("kc.floor.z"),
              q("kc.east_wall.x"), q("ante.south_end.y"), q("kc.ceiling.z"))
    assert planes == pytest.approx((-2.7356, -13.6398, 42.9971, 7.7470, -5.8369, 48.8353))
    assert box(tag) == pytest.approx(planes, abs=1e-3)
    assert volume(tag) == pytest.approx(323.37, abs=0.05)  # 320.37 chamber + 3.00 passage
    low, high = led().rng("kc.volume_with_passage")
    assert low <= volume(tag) <= high


@pytest.mark.parametrize("side, way, expected_volume", [("north", 1.0, 3.61), ("south", -1.0, 2.58)])
def test_kings_chamber_shaft_ends_on_the_face(gm, side, way, expected_volume):
    q = led().q
    build_shaft = getattr(spaces, f"kc_shaft_{side}")
    slope, height = math.radians(q(f"kcs.{side}.angle")), q(f"kcs.{side}.height")

    def far_end(tag, level_end=False):
        """Distance from the centre, and level, of the axis at the outer end, read off the bounding box."""
        x0, y0, z0, x1, y1, z1 = box(tag)
        reach = y1 if way > 0 else -y0
        if level_end:
            return reach, z1 - height / 2
        return reach - height / 2 * math.sin(slope), z1 - height / 2 * math.cos(slope)

    # default: to the casing face, at about 80 m
    tag = build_shaft(led())
    half, apex = spaces.faces(led())
    reach, level = far_end(tag)
    assert reach == pytest.approx(half * (1 - level / apex), abs=1e-3)
    low, high = led().rng("kcs.exit.z")
    assert low <= level <= high  # the axis leaves the casing at 80.27 m (north) and 80.85 m (south); range 79.0 to 81.1
    assert (box(tag)[0] + box(tag)[3]) / 2 == pytest.approx(5.247, abs=1e-3)  # 2.5 m west of the east wall
    assert volume(tag) == pytest.approx(expected_volume, abs=0.02)
    low, high = led().rng(f"kcs.{side}.volume")
    assert low <= volume(tag) <= high

    # closed by the casing, or casing absent: it stops on the core face, about a metre short
    short = build_shaft(led(), to_casing=False)
    core_half, core_apex = spaces.faces(led(), casing=False)
    reach_short, level_short = far_end(short)
    assert reach_short == pytest.approx(core_half * (1 - level_short / core_apex), abs=1e-3)
    assert 0.5 < reach - reach_short < 1.5

    # level outer end: the last 3.05 m run level and still end on the casing face
    flat = build_shaft(led(), level_end=True)
    reach_flat, level_flat = far_end(flat, level_end=True)
    assert reach_flat == pytest.approx(half * (1 - level_flat / apex), abs=1e-3)
    assert level - level_flat > 1.0


def test_relieving_chambers_are_one_block_hung_from_the_surveyed_apex(gm):
    q = led().q
    tag = spaces.relieving_chambers(led())
    x0, y0, z0, x1, y1, z1 = box(tag)
    assert z1 == pytest.approx(q("kc.floor.z") + q("rc.apex_above_kc_floor"), abs=1e-3)  # 64.105
    assert z1 - z0 == pytest.approx(5.918, abs=1e-3)  # the five mean heights added up
    assert z0 > q("kc.ceiling.z")  # clear of the King's Chamber ceiling, 48.835
    assert ((x0 + x1) / 2, (y0 + y1) / 2) == pytest.approx((2.5057, -11.0224), abs=1e-3)  # over the chamber's centre
    assert volume(tag) == pytest.approx(360.05, abs=0.05)  # 11.684 x 5.207 x 5.918
    low, high = led().rng("rc.volume")
    assert low <= volume(tag) <= high


def test_big_void_is_level_or_parallel_to_the_gallery(gm):
    q = led().q
    level = spaces.big_void(led())
    # 30 m from the centre northwards, 2.09 m wide and 6.50 m high about z = 66.19
    assert box(level) == pytest.approx((6.2430, 0.0, 62.9419, 8.3366, 30.0, 69.4381), abs=1e-3)
    tilted = spaces.big_void(led(), inclined=True)
    assert box(tilted) == pytest.approx((6.2430, 0.1135, 56.6320, 8.3366, 29.8865, 75.7480), abs=1e-3)
    low, high = led().rng("bv.volume")
    for tag in (level, tilted):
        assert volume(tag) == pytest.approx(408.0, abs=0.01)  # 30 m x 13.6 m2
        assert low <= volume(tag) <= high
    # inclined, it rises to the south as the Gallery does: its southern half is the higher one
    south_half = spaces._box(0.0, -5.0, 0.0, 20.0, 15.0, 100.0)
    out, _ = occ.intersect([(3, tilted)], [(3, south_half)])
    assert occ.getCenterOfMass(3, out[0][1])[2] > q("bv.centre.z") + 2.0


def test_north_face_corridor_sits_behind_the_core_face_over_the_entrance(gm):
    q = led().q
    tag = spaces.north_face_corridor(led())
    # 2.02 m wide about the passage plane, 9.06 m long, floor at the assumed level 18.31
    assert box(tag) == pytest.approx((6.2798, 88.1932, 18.31, 8.2998, 97.2532, 20.49), abs=1e-3)
    # its upper north edge, the corner nearest the face, is 0.84 m behind the core face
    core_half, core_apex = spaces.faces(led(), casing=False)
    behind = core_half * (1 - box(tag)[5] / core_apex) - box(tag)[4]
    assert behind == pytest.approx(q("nfc.start_offset"), abs=1e-3)
    assert volume(tag) == pytest.approx(39.897, abs=0.01)  # 9.06 x 2.02 x 2.18
    low, high = led().rng("nfc.volume")
    assert low <= volume(tag) <= high
