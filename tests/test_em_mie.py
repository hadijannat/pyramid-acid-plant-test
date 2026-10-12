"""The Mie series against its closed-form limits. Expected numbers are computed here from the limit formulas."""
import numpy as np
import pytest

from pyramid.em import mie


def test_small_sphere_follows_the_rayleigh_formulas():
    eps, x = 5 + 0.1j, 0.02
    polarisability = (eps - 1) / (eps + 2)
    q_ext, q_sca, q_abs = mie.efficiencies(eps, x)
    assert q_sca == pytest.approx(8 / 3 * x**4 * abs(polarisability) ** 2, rel=1e-3)
    assert q_abs == pytest.approx(4 * x * polarisability.imag, rel=1e-3)
    assert q_ext == pytest.approx(q_sca + q_abs)


def test_scattering_grows_as_the_fourth_power_of_size_when_small():
    small, twice = mie.efficiencies(5.0, 0.01)[1], mie.efficiencies(5.0, 0.02)[1]
    assert twice / small == pytest.approx(16.0, rel=1e-3)


def test_large_absorbing_sphere_approaches_the_extinction_paradox():
    # Geometric optics with diffraction: Q_ext tends to 2; the edge term 1.992 x^(-2/3) is the next correction.
    x = 400.0
    q_ext, q_sca, q_abs = mie.efficiencies((1.5 + 0.1j) ** 2, x)
    assert q_ext == pytest.approx(2 + 1.992 * x ** (-2 / 3), rel=0.01)
    assert 0 < q_abs < 1.0 and q_sca > 1.0     # an opaque sphere absorbs at most its own shadow


def test_lossless_sphere_absorbs_nothing():
    for x in (0.5, 1.7, 3.1, 6.0):
        q_ext, q_sca, q_abs = mie.efficiencies(5.0, x)
        assert q_abs == pytest.approx(0.0, abs=1e-10)
        assert q_ext > 0


def test_cross_sections_are_efficiencies_times_the_shadow():
    radius, wavelengths = 100.0, np.array([200.0, 400.0, 600.0])
    sigma = mie.cross_sections(radius, 5 + 0.1j, wavelengths)
    assert sigma.shape == (3, 3)
    for column, wavelength in zip(sigma.T, wavelengths):
        q = mie.efficiencies(5 + 0.1j, 2 * np.pi * radius / wavelength)
        assert column == pytest.approx(np.pi * radius**2 * np.array(q))
    assert np.all(sigma[0] >= sigma[1])            # extinction is scattering plus absorption
