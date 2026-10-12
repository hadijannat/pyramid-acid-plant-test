"""The conduction solver against three closed forms, each computed here."""
import math

import numpy as np
import pytest

from pyramid.electro import conduction


def test_a_graded_axis_keeps_its_fine_points_and_reaches_both_ends():
    edges = conduction.graded_axis([2.0, 5.0], 1.0, -100.0, 40.0, ratio=1.5, snap=(0.0,))
    assert edges[0] == -100.0 and edges[-1] == 40.0 and 0.0 in edges
    assert {2.0, 3.0, 4.0, 5.0} <= set(np.round(edges, 12))
    assert np.all(np.diff(edges) > 0)


def test_a_uniform_field_in_a_homogeneous_block_is_reproduced_on_a_graded_grid():
    # phi = -E0 z between two plates: E = (0, 0, E0) in every cell, whatever the grading. Tolerance 1e-6.
    e0, sigma0 = 0.02, 2e-3
    edges = [conduction.graded_axis([-1.0, 1.0], 0.5, -40.0, 60.0, ratio=1.4) for _ in range(3)]
    sigma = np.full([len(e) - 1 for e in edges], sigma0)
    plates = {"z-": -e0 * edges[2][0], "z+": -e0 * edges[2][-1]}
    phi = conduction.solve(edges, sigma, plates, rtol=1e-13)
    ex, ey, ez = conduction.field(edges, sigma, phi, plates)
    assert np.max(np.abs(ez / e0 - 1)) < 1e-6
    assert np.max(np.abs(ex)) < 1e-6 * e0 and np.max(np.abs(ey)) < 1e-6 * e0
    z = conduction.centres(edges)[2]
    assert np.max(np.abs(phi + e0 * z[None, None, :])) < 1e-6 * e0 * 100


def test_a_point_current_on_a_half_space_gives_i_rho_over_two_pi_r():
    # phi = I rho / (2 pi r) at the surface of a homogeneous half-space. Tolerance 3 percent, away from the source
    # cell (r of at least 5 cells) and from the outer faces (r up to a quarter of the half-width).
    current, rho, h, width = 30e3, 500.0, 1.0, 400.0
    xy = conduction.graded_axis([-h / 2, h / 2], h, -width, width, ratio=1.2)
    z = conduction.graded_axis([-h, 0.0], h, -width, 0.0, ratio=1.2)
    edges = [xy, xy, z]
    sigma = np.full([len(e) - 1 for e in edges], 1 / rho)
    cx, cy, cz = conduction.centres(edges)

    def exact(x, y, depth):
        return current * rho / (2 * math.pi * np.sqrt(x**2 + y**2 + depth**2))

    far = {
        "x-": exact(xy[0], cy[:, None], cz[None, :]), "x+": exact(xy[-1], cy[:, None], cz[None, :]),
        "y-": exact(cx[:, None], xy[0], cz[None, :]), "y+": exact(cx[:, None], xy[-1], cz[None, :]),
        "z-": exact(cx[:, None], cy[None, :], z[0]),
    }
    middle = len(cx) // 2
    phi = conduction.solve(edges, sigma, far, sources=[(middle, middle, len(cz) - 1, current)])
    checked = 0
    for i in range(middle + 1, len(cx)):
        r = cx[i]
        if 5 * h <= r <= width / 4:
            assert phi[i, middle, -1] == pytest.approx(current * rho / (2 * math.pi * r), rel=0.03), r
            checked += 1
    assert checked >= 5


@pytest.mark.parametrize("contrast, n, radius", [(1e-4, 40, 6.0), (10.0, 80, 10.0)])
def test_the_field_inside_a_sphere_in_a_uniform_field(contrast, n, radius):
    # E_inside / E0 = 3 sigma0 / (2 sigma0 + sigma1), uniform in the sphere. Tolerance 5 percent: the staircase
    # surface and the walls are the error. A resistive sphere (the granite's case, 1.5 E0) is 3 percent high on 40
    # cells; a conducting one converges more slowly (6 percent on 40 cells, 4 percent on 80), so it takes 80.
    e0, sigma0 = 1.0, 1e-3
    edges = [np.linspace(-n / 2, n / 2, n + 1)] * 3
    cx, cy, cz = conduction.centres(edges)
    inside = cx[:, None, None] ** 2 + cy[None, :, None] ** 2 + cz[None, None, :] ** 2 < radius**2
    sigma = np.where(inside, contrast * sigma0, sigma0)
    plates = {"z-": e0 * n / 2, "z+": -e0 * n / 2}
    phi = conduction.solve(edges, sigma, plates)
    ez = conduction.field(edges, sigma, phi, plates)[2]
    expected = 3 * sigma0 / (2 * sigma0 + contrast * sigma0) * e0
    core = cx[:, None, None] ** 2 + cy[None, :, None] ** 2 + cz[None, None, :] ** 2 < (radius / 2) ** 2
    assert np.mean(ez[core]) == pytest.approx(expected, rel=0.05)


def test_an_insulating_cell_carries_no_current_and_a_floating_problem_is_refused():
    edges = [np.linspace(0, 4, 5)] * 3
    sigma = np.ones((4, 4, 4))
    sigma[1:3, 1:3, 1:3] = 0.0
    phi = conduction.solve(edges, sigma, {"x-": 1.0, "x+": 0.0})
    assert np.isnan(phi[1, 1, 1]) and np.all(np.isfinite(phi[sigma > 0]))
    assert 0.0 < np.nanmin(phi) and np.nanmax(phi) < 1.0
    with pytest.raises(ValueError, match="up to a constant"):
        conduction.solve(edges, sigma)
