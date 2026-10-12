"""The Mie series for a homogeneous sphere in free space: the exact answer the field solvers are held to.

Assumptions: a non-magnetic sphere in vacuum; time dependence exp(-i w t), so an absorbing material has a
positive imaginary permittivity; the series is cut at Wiscombe's term count.
"""
import numpy as np
from scipy.special import spherical_jn, spherical_yn


def efficiencies(eps: complex, x: float) -> tuple[float, float, float]:
    """(Q_ext, Q_sca, Q_abs) of a sphere of relative permittivity eps and size parameter x = 2 pi a / wavelength."""
    m = np.sqrt(complex(eps))
    n = np.arange(1, int(x + 4.0 * x ** (1 / 3) + 2.0) + 1)     # Wiscombe's criterion for the last term
    # Riccati-Bessel functions psi(z) = z j_n(z), xi(z) = z h_n(z), and their derivatives
    jx, djx = spherical_jn(n, x), spherical_jn(n, x, derivative=True)
    yx, dyx = spherical_yn(n, x), spherical_yn(n, x, derivative=True)
    jm, djm = spherical_jn(n, m * x), spherical_jn(n, m * x, derivative=True)
    psi, dpsi = x * jx, jx + x * djx
    xi, dxi = x * (jx + 1j * yx), (jx + 1j * yx) + x * (djx + 1j * dyx)
    psim, dpsim = m * x * jm, jm + m * x * djm
    a = (m * psim * dpsi - psi * dpsim) / (m * psim * dxi - xi * dpsim)
    b = (psim * dpsi - m * psi * dpsim) / (psim * dxi - m * xi * dpsim)
    q_ext = 2.0 / x**2 * float(np.sum((2 * n + 1) * (a + b).real))
    q_sca = 2.0 / x**2 * float(np.sum((2 * n + 1) * (abs(a) ** 2 + abs(b) ** 2)))
    return q_ext, q_sca, q_ext - q_sca


def cross_sections(radius: float, eps, wavelengths) -> np.ndarray:
    """Rows (extinction, scattering, absorption) in m2, one column per wavelength; eps is one value or one each."""
    wavelengths = np.atleast_1d(np.asarray(wavelengths, dtype=float))
    eps = np.broadcast_to(np.asarray(eps, dtype=complex), wavelengths.shape)
    q = np.array([efficiencies(e, 2 * np.pi * radius / w) for e, w in zip(eps, wavelengths)])
    return (np.pi * radius**2 * q).T
