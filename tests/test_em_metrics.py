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


def test_benchmark_and_convergence_gates():
    exact = np.array([1.0, 2.0, 3.0])
    assert metrics.benchmark_gate(exact, {"dda": exact * 1.019, "fdtd": exact * 0.99})["passed"]
    failed = metrics.benchmark_gate(exact, {"dda": exact * 1.019, "fdtd": exact * [1, 1, 0.97]})
    assert not failed["passed"] and "3.00%" in failed["numbers"]
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


def test_e19_runs_through_its_statuses():
    low, high = 6.7e-4, 3.3e-3
    holds = [(2.5, 9.0, 3.0), (1.667, 8.0, 3.5)]                 # R1 at least twice its control at both cells
    fails_real = [(2.5, [("", low, 0.4, 0.3), ("", high, 0.01, 0.02)]), (1.667, [("", low, 0.5, 0.3), ("", high, 0.01, 0.02)])]
    status, basis = metrics.e19(holds, fails_real)
    assert status == "fail" and "0.4" in basis and "9.00" in basis
    passes_real = [(2.5, [("", low, 9.0, 2.0), ("", high, 5.0, 2.0)]), (1.667, [("", low, 8.0, 2.0), ("", high, 4.5, 2.0)])]
    assert metrics.e19(holds, passes_real)[0] == "pass"
    drops = [(2.5, [("", low, 4.0, 1.0), ("", high, 1.0, 0.4)])]                 # at least 2 at the low end only
    status, basis = metrics.e19(holds, drops)
    assert status == "conditional" and "drops below 2 at about 1.5e-03" in basis
    weak_control = [(2.5, [("", low, 4.0, 3.0), ("", high, 3.0, 2.5)])]          # above 2, but not twice the control
    assert metrics.e19(holds, weak_control)[0] == "conditional"
    not_modelled = [(2.5, 4.0, 3.0), (1.667, 4.0, 3.0)]
    assert metrics.e19(not_modelled, passes_real)[0] == "conditional"            # the parts disagree
    assert metrics.e19(not_modelled, fails_real)[0] == "fail"
    split = [(2.5, 7.0, 3.0), (1.667, 5.0, 3.0)]                 # the two cell sizes fall on different sides of twice
    assert metrics.e19(split, passes_real)[0] == "conditional"
    split_real = [(2.5, [("", low, 2.2, 0.5)]), (1.667, [("", low, 1.8, 0.5)])]  # and of the value 2
    assert metrics.e19(holds, split_real)[0] == "conditional"
    other_eps = [(2.5, [("", low, 0.4, 0.3), ("eps 9", low, 2.4, None)])]        # fails only if every permittivity fails
    assert metrics.e19(holds, other_eps)[0] == "conditional"


def test_e20_runs_through_its_statuses():
    status, basis = metrics.e20([(2.5, 1.2, 1.0, 1.1), (1.667, 1.3, 1.0, 1.1)])
    assert status == "fail" and "1.20" in basis and "1.30 times" in basis
    assert metrics.e20([(2.5, 2.4, 1.0, 1.1), (1.667, 2.1, 1.0, 1.1)])[0] == "pass"
    status, basis = metrics.e20([(2.5, 2.4, 1.0, 1.1), (1.667, 1.9, 1.0, 1.1)])
    assert status == "conditional" and "different sides" in basis
