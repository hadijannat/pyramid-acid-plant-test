"""The time-domain solver on small grids: the injected plane wave, the absorbing layers, Fresnel, energy, Mie."""
from dataclasses import replace

import numpy as np
import pytest

from pyramid.em import cases, fdtd, mie, shapes
from pyramid.ledger import load

LEDGER = load()
Q = LEDGER.q
SPEED, IMPEDANCE = cases.constants(Q)
BAND = np.arange(200.0, 601.0, 50.0)
SMALL = replace(cases.table(LEDGER)["B0"], base=50.0)          # a sphere of half the benchmark's radius


def empty(ground: bool, cells: int = 6, cell: float = 5.0):
    """A block of nothing (of ground below z = 0): the solver's own padding does the rest."""
    model = shapes.build(replace(SMALL, base=cells * cell / 2, ground=ground), Q, cell)
    model.masonry[...] = 0
    if ground:
        model.masonry[:, :, model.centres(2) < 0] = 1
    return model


def solver(model, sigma=0.0, ground=False, dtype=np.float64, **kw):
    return fdtd.Run(model, 5.0, sigma, 6.0, 0.0, ground, cases.DOWN, BAND, SPEED, IMPEDANCE, dtype=dtype, **kw)


def step(run, steps):
    for _ in range(steps):
        run.one_step()
        if run.step % run.stride == 0:
            run._accumulate()


def test_plane_wave_in_empty_space_stays_inside_the_injection_surface():
    run = solver(empty(False))
    (ia, ib), (ja, jb), (ka, kb) = run.inject
    outside, inside = 0.0, 0.0
    for _ in range(12):
        step(run, 50)
        outside = max(outside, np.abs(run.e[0][:ia - 1]).max(), np.abs(run.e[0][:, :, kb + 2:]).max(),
                      np.abs(run.e[0][:, :, :ka - 1]).max(), np.abs(run.e[1]).max(), np.abs(run.e[2]).max())
        inside = max(inside, np.abs(run.e[0][ia + 2:ib - 2, ja + 2:jb - 2, ka + 2:kb - 2]).max())
    assert inside > 0.5 and outside < 1e-10 * inside             # far below -40 dB: nothing leaks, nothing to reflect
    out = run.results()
    assert np.abs(out["scattering"]).max() < 1e-6 and np.abs(out["absorption"]).max() < 1.0   # m2, of nothing
    # the wave inside is the unit plane wave; averaging a field to the cell centre costs cos^2(k d / 2)
    expected = np.cos(np.pi * run.cell / BAND) ** 2
    assert out["section"].reshape(len(BAND), -1).min(axis=1) == pytest.approx(expected, rel=1e-3)
    assert out["section"].reshape(len(BAND), -1).max(axis=1) == pytest.approx(expected, rel=1e-3)


def test_absorbing_layers_reflect_below_minus_40_db():
    # a point source in a small box against the same source in a box whose walls are too far to matter
    records = []
    for cells in (6, 46):
        run = solver(empty(False, cells, 10.0))
        run.lines[0]["cb"][:] = 0.0                              # no plane wave
        centre = run.n[0] // 2
        probes = [(centre, centre, centre + 10), (centre + 9, centre + 9, centre + 9)]   # 2 and 3 cells from the layers
        record = []
        for _ in range(260):
            run.one_step()
            run.e[2][centre, centre, centre] += run.pulse(run.step * run.dt)
            record.append([run.e[2][p] for p in probes])
        records.append(np.array(record))
    small, large = records
    reflected = np.abs(small - large).max(axis=0) / np.abs(large).max(axis=0)
    assert np.all(reflected < 0.01), reflected                    # -40 dB in amplitude


def test_a_half_space_reflects_as_fresnel_says_and_the_grid_reproduces_it():
    sigma = cases.conductivity(0.1, 346.0, Q)
    run = solver(empty(True), sigma, ground=True)
    (ia, ib), (ja, jb), (ka, kb) = run.inject
    outside, inside = 0.0, 0.0
    for _ in range(14):
        step(run, 50)
        outside = max(outside, np.abs(run.e[0][:ia - 1]).max(), np.abs(run.e[2]).max(), np.abs(run.e[0][:, :, kb + 2:]).max())
        inside = max(inside, np.abs(run.e[0][ia + 2:ib - 2, ja + 2:jb - 2, ka + 2:kb - 2]).max())
    assert outside < 1e-10 * inside                               # the layered wave of the 1D grid is exact in 3D
    index = np.sqrt(5.0 + 1j * cases.loss(sigma, BAND, Q))
    fresnel = (1 - index) / (1 + index)
    at_surface = run.sums["line_e"][:, run.k0] / run.sums["incident"]   # total over incident at z = 0
    assert np.all(np.abs(at_surface - 1 - fresnel) < 0.02 * np.abs(fresnel))


@pytest.fixture(scope="module")
def ball():
    model = shapes.build(SMALL, Q, 5.0)
    sigma = cases.conductivity(0.1, 346.0, Q)
    out = {}
    for dtype in (np.float32, np.float64):
        run = solver(model, sigma, dtype=dtype)
        assert run.advance()
        out[dtype] = run.results()
    return sigma, out


def test_a_small_sphere_follows_mie_and_conserves_energy(ball):
    sigma, out = ball
    result = out[np.float32]
    exact = mie.cross_sections(50.0, 5 + 1j * cases.loss(sigma, BAND, Q), BAND)      # at the run's own loss
    # ten cells to the radius: the error falls with the cell (about first order), and is 6 percent at worst here
    assert result["extinction"] == pytest.approx(exact[0], rel=0.08)
    assert result["scattering"] == pytest.approx(exact[1], rel=0.08)
    assert np.all(result["absorption"] > 0)
    # extinction from the interference of incident and scattered field against scattered plus absorbed power
    assert result["cross"] == pytest.approx(result["extinction"], rel=0.02)


def test_single_precision_does_not_move_the_benchmark(ball):
    _, out = ball
    assert out[np.float32]["extinction"] == pytest.approx(out[np.float64]["extinction"], rel=1e-3)
    assert out[np.float32]["steps"] == out[np.float64]["steps"]


def test_a_run_resumes_from_its_checkpoint(tmp_path):
    model = shapes.build(SMALL, Q, 10.0)
    whole, first = solver(model, 1e-5, dtype=np.float32), solver(model, 1e-5, dtype=np.float32)
    step(whole, 240)
    step(first, 120)
    first.save(tmp_path / "state.npz")
    second = solver(model, 1e-5, dtype=np.float32)
    second.load(tmp_path / "state.npz")
    step(second, 120)
    assert second.step == whole.step == 240
    assert all(np.array_equal(a, b) for a, b in zip(second.e + second.h, whole.e + whole.h))
    assert np.array_equal(second.sums["scatter.2.1.ea"], whole.sums["scatter.2.1.ea"])


def test_the_region_metrics_come_out_of_a_run():
    case = replace(cases.table(LEDGER)["R1"])
    run = fdtd.Run(shapes.build(case, Q, 10.0), 5.0, 5e-6, 6.0, 0.0, False, cases.DOWN, BAND, SPEED, IMPEDANCE, flux=False)
    step(run, 300)
    out = run.results()
    assert "extinction" not in out and {"mean.kings", "max.kings", "mean.queens", "mean.summit", "section"} <= set(out)
    assert out["mean.kings"].shape == BAND.shape and np.all(out["mean.kings"] > 0)
    y0, y1, z0, z1 = out["section_extent"]
    assert y0 < -115 and y1 > 115 and z0 < 0 and z1 > 138.75      # the section covers the whole body
