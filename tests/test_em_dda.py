"""The coupled-dipole solver on coarse lattices: against Mie, against energy conservation and reciprocity."""
import numpy as np
import pytest

from pyramid.em import cases, dda, mie, shapes
from pyramid.ledger import load

LEDGER = load()
TABLE = cases.table(LEDGER)
EPS = 5 + 0.1j


@pytest.fixture(scope="module")
def ball():
    return dda.Lattice(shapes.build(TABLE["B0"], LEDGER.q, 6.25))     # 16 cells to the radius


def test_extinction_of_a_sphere_follows_mie_on_a_coarse_lattice(ball):
    for wavelength in (300.0, 400.0, 500.0, 600.0):
        solved = dda.solve(ball, EPS, 1.0, wavelength, cases.DOWN)
        exact = mie.cross_sections(100.0, EPS, [wavelength])[:, 0]
        assert solved["extinction"] == pytest.approx(exact[0], rel=0.05)
        assert solved["absorption"] == pytest.approx(exact[2], rel=0.05)


def test_extinction_is_scattering_plus_absorption(ball):
    # the optical theorem against the far field integrated over all directions plus the loss in the dipoles
    solved = dda.solve(ball, EPS, 1.0, 300.0, cases.DOWN)
    scattered = dda.scattering(ball, solved["moments"], 300.0)
    assert solved["absorption"] > 0
    assert solved["extinction"] == pytest.approx(scattered + solved["absorption"], rel=0.02)


def test_a_small_sphere_holds_the_electrostatic_field(ball):
    # far below resonance the field inside a sphere is uniform, 3 / (eps + 2) of the applied one
    solved = dda.solve(ball, EPS, 1.0, 20000.0, cases.DOWN)
    intensity = np.sum(np.abs(solved["field"]) ** 2, axis=0)
    assert intensity[14:18, 14:18, 14:18].mean() == pytest.approx(abs(3 / (EPS + 2)) ** 2, rel=0.02)


def test_extinction_is_the_same_from_above_and_from_below():
    # reciprocity: the forward amplitude, and with it the extinction, does not change when the wave is reversed
    lattice = dda.Lattice(shapes.build(TABLE["R1"], LEDGER.q, 10.0))
    down = dda.solve(lattice, EPS, 1.0, 300.0, cases.DOWN)
    up = dda.solve(lattice, EPS, 1.0, 300.0, cases.UP)
    assert up["extinction"] == pytest.approx(down["extinction"], rel=1e-3)
    assert up["absorption"] != pytest.approx(down["absorption"], rel=1e-3)      # the split between the two does


def test_spectrum_reports_the_regions_and_the_section():
    model = shapes.build(TABLE["R1"], LEDGER.q, 10.0)
    out = dda.spectrum(model, [400.0, 420.0], lambda w: (EPS, 1.0), cases.DOWN)
    assert out["extinction"].shape == (2,) and out["section"].shape == (2, *model.masonry.shape[1:])
    assert {"mean.kings", "max.kings", "mean.summit"} <= set(out)
    assert np.all(out["mean.kings"] > 0) and np.all(out["max.kings"] > 0)
    assert out["products"][1] < out["products"][0]                 # the neighbour's solution is a good start
