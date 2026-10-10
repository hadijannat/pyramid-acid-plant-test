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
