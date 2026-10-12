"""The metrics, the gates and the rules for E19 and E20, driven on made-up numbers."""
import numpy as np
import pytest

from pyramid.em import metrics, mie


def test_region_mean_is_volume_weighted_and_the_maximum_ignores_slivers():
    intensity = np.array([[[1.0, 3.0, 100.0]], [[2.0, 2.0, 50.0]]]).reshape(2, 1, 1, 3)
    weights = np.array([1.0, 0.5, 0.01]).reshape(1, 1, 3)        # the third cell is a sliver of the region
    mean, peak = metrics.region_stats(intensity, weights)
    assert mean == pytest.approx([(1 + 1.5 + 1) / 1.51, (2 + 1 + 0.5) / 1.51])
    assert peak == pytest.approx([3.0, 2.0])


def test_the_field_across_a_wall_is_larger_on_the_air_side():
    field = np.array([1.0, 2.0, 0.0]).reshape(3, 1)              # across the wall (x) and along it (y)
    normal = np.array([1.0, 0.0, 0.0]).reshape(3, 1)
    assert metrics.side_intensity(field, normal, 5.0) == pytest.approx([5.0**2 + 2.0**2])
    assert metrics.side_intensity(field, 0 * normal, 5.0) == pytest.approx([1.0 + 4.0])    # an uncut cell


def test_peaks_are_found_between_the_samples():
    x = np.arange(200.0, 601.0, 5.0)
    y = 9e4 * np.exp(-((x - 332.0) / 40) ** 2) + 13e4 * np.exp(-((x - 231.0) / 25) ** 2)
    found = metrics.peaks(x, y)
    assert [p[0] for p in found] == pytest.approx([231.0, 332.0], abs=0.5)
    assert found[0][1] == pytest.approx(13e4, rel=5e-3)
    assert metrics.band_maximum(x, y)[0] == pytest.approx(231.0, abs=0.5)
    assert metrics.band_maximum(x, 1 / x) == (200.0, 1 / 200.0)  # a spectrum that only falls peaks at the band's end


def test_normalised_difference_of_two_spectra():
    a = np.array([1.0, 2.0, 3.0])
    assert metrics.nrmsd(a, a) == 0.0
    assert metrics.nrmsd(a, 1.1 * a) == pytest.approx(0.1 / 1.05)


def test_three_constant_conductivity_runs_recover_the_constant_imaginary_permittivity():
    # A time-domain run has one conductivity, so its imaginary permittivity grows with the wavelength. The exact
    # sphere shows what that costs (several percent of extinction) and that interpolating three runs removes it.
    wavelengths = np.arange(200.0, 601.0, 25.0)
    exact = mie.cross_sections(100.0, 5 + 0.1j, wavelengths)[0]
    matched = (200.0, np.sqrt(200.0 * 600.0), 600.0)
    losses = np.array([0.1 * wavelengths / at for at in matched])
    runs = np.array([mie.cross_sections(100.0, 5 + 1j * loss, wavelengths)[0] for loss in losses])
    assert np.max(np.abs(runs[1] / exact - 1)) > 0.03            # one run alone would use up the 2 percent gate
    assert metrics.interpolate_loss(runs, losses, 0.1) == pytest.approx(exact, rel=2e-3)
    with pytest.raises(ValueError):
        metrics.interpolate_loss(runs[:1], losses[:1], 0.1)


def test_the_benchmark_is_judged_per_solver_and_cell_and_passes_only_on_the_deciding_cells():
    band, exact = np.array([200.0, 300.0, 400.0]), np.array([1.0, 2.0, 3.0])
    slope = np.array([15.0, -1.0, 0.5])                          # the first wavelength sits on a narrow line
    row = lambda solver, cell, factors: metrics.sphere_row(solver, cell, band, exact * factors, exact, slope)   # noqa: E731
    rows = [row("dda", 2.5, [1.027, 0.991, 1.0]), row("dda", 1.667, [1.019, 0.996, 1.0]),
            row("fdtd", 2.5, [1.03, 1.0303, 1.02]), row("fdtd", 1.0, [1.015, 1.012, 1.0])]
    assert [r["passed"] for r in rows] == [False, True, False, True]
    assert rows[0]["worst"] == pytest.approx(0.027) and "worst +2.70% at 200 m" in rows[0]["numbers"]
    assert "-0.90% at 300 m at worst over the 2 wavelengths where it changes less than 2" in rows[0]["numbers"]
    assert "worst +3.03% at 300 m" in rows[2]["numbers"]         # not on a line: an error of the whole spectrum
    wanted = [("dda", 2.5), ("dda", 1.667), ("fdtd", 2.5), ("fdtd", 1.667), ("fdtd", 1.0)]
    gate = metrics.benchmark_gate(rows, wanted, {"dda": 1.667, "fdtd": 1.0})
    assert gate["passed"]                                        # within the limit where the runs decide
    assert "fdtd at 2.5 m: worst +3.03%" in gate["numbers"] and "decide nothing" in gate["numbers"]
    assert "fdtd at 1.67 m: not run" in gate["numbers"] and "dda 1.67 m, fdtd 1 m" in gate["numbers"]
    assert [(c["solver"], c["cell_m"], c["passed"]) for c in gate["cells"]] == [
        ("dda", 2.5, False), ("dda", 1.667, True), ("fdtd", 2.5, False), ("fdtd", 1.0, True)]
    # the case that occurred: the sphere within the limit only at a finer cell than the runs that decide
    assert not metrics.benchmark_gate(rows, wanted, {"dda": 2.5, "fdtd": 2.5})["passed"]
    assert not metrics.benchmark_gate(rows, wanted, {"dda": 1.667, "fdtd": 2.5})["passed"]
    assert not metrics.benchmark_gate(rows[:3], wanted, {"dda": 1.667, "fdtd": 1.0})["passed"]   # a deciding sphere not run


def test_convergence_gate():
    assert metrics.convergence_gate({"dda": (1.00e5, 1.02e5), "fdtd": (1.0e5, 0.98e5)})["passed"]
    assert not metrics.convergence_gate({"dda": (1.00e5, 1.02e5), "fdtd": (1.0e5, 1.04e5)})["passed"]


def test_reproduction_gate_checks_wavelengths_values_and_agreement():
    targets = {"peak1": (333.0, 9e4), "peak2": (230.0, 13e4), "ground": (250.0, 12e4)}
    good = {"dda": [(228.0, 12e4), (340.0, 10e4)], "fdtd": [(232.0, 14e4), (330.0, 8e4)]}
    gates = metrics.reproduction_gate(good, (262.0, 11e4), targets, {"R1": 0.04, "R2": 0.05})
    assert [g["passed"] for g in gates] == [True, True, True, True]
    off = {"dda": [(228.0, 12e4), (360.0, 10e4)], "fdtd": [(232.0, 17e4)]}       # 360 m is 8 percent off; 17 is 31 percent high
    gates = metrics.reproduction_gate(off, (290.0, 11e4), targets, {"R1": 0.04, "R2": 0.12})
    assert [g["passed"] for g in gates] == [False, False, False, False]
    assert not metrics.reproduction_gate({"dda": []}, None, targets, {})[0]["passed"]   # no peak, no ground run


FINE, NEXT = "the solver at its deciding cell", "the solver at the next coarser cell"


def test_e19_runs_through_its_statuses():
    low, high = 6.7e-4, 3.3e-3
    holds = [(FINE, 9.0, 3.0, True), (NEXT, 8.0, 3.5, False)]    # R1 at least twice its control at both cells
    fails_real = [(FINE, [("", low, 0.4, 0.3), ("", high, 0.01, 0.02)], True),
                  (NEXT, [("", low, 0.5, 0.3), ("", high, 0.01, 0.02)], False)]
    status, basis = metrics.e19(holds, fails_real, " Not varied: the shell.")
    assert status == "fail" and "0.4" in basis and "9.00" in basis and basis.endswith(" Not varied: the shell.")
    assert f"9.00 against 3.00 in its control cube (3.00 times) in {FINE}; at the next coarser cell, which decides nothing: 8.00" in basis
    passes_real = [(FINE, [("", low, 9.0, 2.0), ("", high, 5.0, 2.0)], True), (NEXT, [("", low, 8.0, 2.0), ("", high, 4.5, 2.0)], False)]
    assert metrics.e19(holds, passes_real)[0] == "pass"
    drops = [(FINE, [("", low, 4.0, 1.0), ("", high, 1.0, 0.4)], True)]          # at least 2 at the low end only
    status, basis = metrics.e19(holds, drops)
    assert status == "conditional" and "drops below 2 at about 1.5e-03" in basis
    weak_control = [(FINE, [("", low, 4.0, 3.0), ("", high, 3.0, 2.5)], True)]   # above 2, but not twice the control
    assert metrics.e19(holds, weak_control)[0] == "conditional"
    not_modelled = [(FINE, 4.0, 3.0, True), (NEXT, 4.0, 3.0, False)]
    assert metrics.e19(not_modelled, passes_real)[0] == "conditional"            # the parts disagree
    assert metrics.e19(not_modelled, fails_real)[0] == "fail"
    split = [(FINE, 7.0, 3.0, True), (NEXT, 5.0, 3.0, False)]    # the deciding cell says twice, the next coarser does not
    assert metrics.e19(split, passes_real)[0] == "conditional"
    solvers = [("one solver", 7.0, 3.0, True), ("the other", 5.0, 3.0, True)]    # two deciding runs on different sides
    assert metrics.e19(solvers, passes_real)[0] == "conditional"
    split_real = [(FINE, [("", low, 2.2, 0.5)], True), (NEXT, [("", low, 1.8, 0.5)], False)]   # and of the value 2
    assert metrics.e19(holds, split_real)[0] == "conditional"
    other_eps = [(FINE, [("", low, 0.4, 0.3), ("eps 9", low, 2.4, None)], True)]  # fails only if every permittivity fails
    assert metrics.e19(holds, other_eps)[0] == "conditional"
    all_eps = [(FINE, [("", low, 9.0, 2.0), ("", high, 5.0, 2.0), ("eps 5", low, 8.0, None), ("eps 9", low, 7.0, None)], True)]
    assert metrics.e19(holds, all_eps)[0] == "pass"              # the other permittivities need no control to pass
    weak_eps = [(FINE, [("", low, 9.0, 2.0), ("", high, 5.0, 2.0), ("eps 9", low, 1.5, None)], True)]
    assert metrics.e19(holds, weak_eps)[0] == "conditional"


def test_e20_runs_through_its_statuses():
    status, basis = metrics.e20([(FINE, 1.2, 1.0, None, True), (NEXT, 1.3, 1.0, 1.1, False)])
    assert status == "fail" and "1.30 times; 1.10 for the study's apex" in basis
    assert f"(1.20 times) in {FINE}; at the next coarser cell, which decides nothing:" in basis   # no study apex at that cell
    assert metrics.e20([(FINE, 2.4, 1.0, 1.1, True), (NEXT, 2.1, 1.0, 1.1, False)])[0] == "pass"
    for cut in ((2.4, 1.9), (1.9, 2.4)):                         # either way round: the two cells on different sides
        status, basis = metrics.e20([(FINE, cut[0], 1.0, 1.1, True), (NEXT, cut[1], 1.0, 1.1, False)])
        assert status == "conditional" and "different sides" in basis
