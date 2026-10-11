"""The bodies on the grid: volumes against their closed forms, the regions, the case table."""
import numpy as np
import pytest

from pyramid.em import cases, shapes
from pyramid.ledger import load

LEDGER = load()
Q = LEDGER.q
TABLE = cases.table(LEDGER)


def volume(fraction, cell):
    return float(fraction.sum()) * cell**3


def test_sphere_and_pyramid_fill_their_closed_form_volumes():
    for cell in (5.0, 2.5):
        ball = shapes.build(TABLE["B0"], Q, cell)
        assert volume(ball.masonry, cell) == pytest.approx(4 / 3 * np.pi * 100.0**3, rel=2e-3)
    edges = [np.arange(-120.0, 121.0, 5.0), np.arange(-120.0, 121.0, 5.0), np.arange(0.0, 141.0, 5.0)]
    assert volume(shapes.pyramid(edges, 230.0, 138.75), 5.0) == pytest.approx(230.0**2 * 138.75 / 3, rel=1e-3)
    cut = shapes.pyramid(edges, 230.0, 138.75, 0.0, 100.0)       # a frustum: the whole less the similar tip
    assert volume(cut, 5.0) == pytest.approx(230.0**2 * 138.75 / 3 * (1 - (38.75 / 138.75) ** 3), rel=1e-3)


def test_a_box_is_exact_on_a_grid_it_does_not_line_up_with():
    edges = [np.arange(-20.0, 21.0, 3.0)] * 3
    assert volume(shapes.box(edges, (-5.5, -7.5, 1.0), (5.5, -2.5, 12.0)), 3.0) == pytest.approx(11 * 5 * 11, rel=1e-12)


def test_the_study_model_carries_its_chambers_and_the_summit_region():
    r1 = shapes.build(TABLE["R1"], Q, 5.0)
    assert set(r1.regions) == {"kings", "queens", "summit"}      # the third chamber lies below a floating body
    kings, queens = 11 * 5 * 11, 5 * 5 * 6
    assert volume(r1.regions["kings"][1], 5.0) == pytest.approx(kings, rel=1e-6)
    assert volume(r1.masonry, 5.0) == pytest.approx(230.0**2 * 138.75 / 3 - kings - queens, rel=1e-3)
    slices, weights = r1.regions["kings"]
    centre = [r1.centres(a)[s].mean() for a, s in enumerate(slices)]
    assert centre == pytest.approx([0.0, -5.0, 40.5], abs=2.6)   # on the axis east-west, 5 m south, 40.5 m up
    top, depth = Q("pyr.height_present"), Q("emx.summit_depth")

    def side(z):
        return 230.0 * (1 - z / 138.75)

    frustum = depth / 3 * (side(top - depth) ** 2 + side(top - depth) * side(top) + side(top) ** 2)
    assert volume(r1.regions["summit"][1], 5.0) == pytest.approx(frustum, rel=5e-3)


def test_on_ground_the_half_space_is_filled_and_holds_the_third_chamber():
    r3 = shapes.build(TABLE["R3"], Q, 5.0)
    below = r3.centres(2) < 0
    assert "lower" in r3.regions and below.sum() >= 7
    lower = 5.2 * 5.6 * 4.6
    assert volume(1 - r3.masonry[:, :, below], 5.0) == pytest.approx(lower, rel=1e-5)   # ground everywhere but the void


def test_the_control_cube_has_the_volume_of_what_it_controls():
    for name in ("R1", "V4.sig6.7e-04"):
        case, cube = TABLE[name], TABLE[f"C0.{name}"]
        assert cube.body == "cube" and cube.chambers == case.chambers and cube.ground == case.ground
        assert cube.base**3 == pytest.approx(shapes.body_volume(case))
    solid = shapes.build(TABLE["C0.R1"], Q, 5.0)
    assert volume(solid.masonry, 5.0) == pytest.approx(230.0**2 * 138.75 / 3 - 11 * 5 * 11 - 5 * 5 * 6, rel=1e-6)


def test_the_surveyed_chambers_gallery_and_granite():
    model = shapes.build(TABLE["V2.R1"], Q, 2.5)
    assert set(model.regions) == {"kings", "queens", "gallery", "summit"}
    assert volume(model.regions["kings"][1], 2.5) == pytest.approx(Q("kc.volume"), rel=0.01)
    run = Q("gg.north_end.y") - Q("gg.south_end.y")
    slab = (Q("gg.width") + Q("gg.roof_width")) / 2 * Q("gg.height") * run
    assert volume(model.regions["gallery"][1], 2.5) == pytest.approx(slab, rel=2e-3)
    assert slab == pytest.approx(Q("gg.volume"), rel=0.08)       # the slab holds the Gallery's volume within its range
    t = Q("emx.granite_shell")
    shell = (Q("kc.length") + 2 * t) * (Q("kc.width") + 2 * t) * (Q("kc.height") + 2 * t) - Q("kc.volume")
    assert 0.9 * shell < volume(model.granite, 2.5) <= shell * 1.01   # less where the Gallery's top end cuts in
    assert float((model.masonry + model.granite).max()) <= 1 + 1e-6


def test_the_case_table_follows_the_spec():
    assert {"B0", "R1", "R2", "R3", "C0.R1", "C0.R3", "V2.R1", "V2.R3", "V3.pointed.ground", "V3.truncated.up"} <= set(TABLE)
    sweep = [c for name, c in TABLE.items() if name.startswith("V1.")]
    assert len(sweep) == 30 and {c.eps for c in sweep} == {5.0, 7.0, 8.8}
    assert sorted({c.sigma for c in sweep}) == pytest.approx([5e-6, 1e-4, 1 / 1500, 1 / 300, 2e-2])
    # the spec's 6.7e-4 and 3.3e-3 S/m are 1/1500 and 1/300 ohm m, rounded
    assert cases.measured_conductivities(LEDGER)[::2] == pytest.approx((6.7e-4, 3.3e-3), rel=0.02)
    assert TABLE["R1"].direction == cases.DOWN and TABLE["R2"].direction == cases.UP and TABLE["R3"].ground
    pointed, cut = TABLE["V3.pointed.ground"], TABLE["V3.truncated.ground"]
    assert pointed.top == pointed.height == Q("pyr.height_original") and cut.top == Q("pyr.height_present")
    assert cut.height == pointed.height and cut.base == pointed.base == Q("pyr.base_side")
    v4 = TABLE["V4.sig6.7e-04"]
    assert v4.ground and v4.chambers == "survey" and v4.top == Q("pyr.height_present") and v4.eps_imag is None


def test_conductivity_and_imaginary_permittivity_convert_both_ways():
    # sigma / (omega eps0) at 1 MHz, with the ledger's eps0: 5.56e-6 S/m is the study's 0.1
    c, _ = cases.constants(Q)
    sigma = cases.conductivity(0.1, c / 1e6, Q)
    assert sigma == pytest.approx(0.1 * 2 * np.pi * 1e6 * Q("em.eps0"), rel=1e-12)
    assert cases.loss(sigma, c / 1e6, Q) == pytest.approx(0.1)
    assert len(cases.wavelengths(Q)) == 81
