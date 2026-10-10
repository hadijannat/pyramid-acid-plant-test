"""Tests for the geometry: the gmsh session, the builders of the spaces, the model and its self-checks."""
import dataclasses
import functools

import gmsh
import pytest

from pyramid import ledger
from pyramid.geometry import frame
from pyramid.geometry import model

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
