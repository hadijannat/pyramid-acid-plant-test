"""Frequency domain: the body as a lattice of coupled point dipoles (a volume-integral solver), in free space.

Each filled cell is a dipole with the lattice-dispersion-relation polarisability (Draine and Goodman 1993); every
dipole feels the incident wave and the fields of all the others. The products with the free-space Green's tensor
are convolutions on the lattice, done with FFTs on a zero-padded grid, and the system is solved with restarted
GMRES. Extinction comes from the optical theorem, absorption from the polarisations, and the field in an empty
cell (a chamber) is the incident wave plus the dipoles' fields there.

Assumptions: time dependence exp(-i w t); a cell cut by a surface holds one dipole at its centre, which answers
a field along the surface with the volume mean of the permittivity and a field across it with the mean of its
inverse (shapes.Model.mixing); the wave travels along z and is polarised along x; no ground (there is no
half-space Green's tensor here: cases with ground belong to the time-domain solver).

Accuracy: the error falls a little faster than the cell size (the surface cells set it). The benchmark sphere,
whose resonance lines are sharp at this permittivity, is 9.4, 2.8 and 1.5 percent off Mie at its worst
wavelength at cells of 5, 2.5 and 1.667 m, so the 2 percent benchmark is met at the fine cell only; the
pyramid's smooth spectrum changes by 0.02 percent at its peak between 5 and 2.5 m.
"""
import time

import numpy as np
from scipy import fft
from scipy.sparse.linalg import LinearOperator, gmres

from pyramid.em import metrics

B1, B2, B3 = -1.891531, 0.1648469, -1.7700004     # coefficients of the lattice dispersion relation
TOLERANCE = 1e-5                                  # relative residual of the linear solve
RESTART = 60                                      # Krylov vectors kept: memory against products
PAIRS = ((0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2))


def polarisability(eps, k: float, cell: float, s: float = 0.0):
    """alpha / eps0 of one cell (m3). s is the sum of (direction_j polarisation_j)^2: zero for a wave along an axis."""
    static = 3 * cell**3 * (eps - 1) / (eps + 2)                                        # Clausius-Mossotti
    kd = k * cell
    return static / (1 + static / (4 * np.pi * cell**3) * ((B1 + eps * B2 + eps * B3 * s) * kd**2 - 2j / 3 * kd**3))


class Lattice:
    """The filled cells of a model and the padded grid on which the dipole fields are summed."""

    def __init__(self, model, dtype=np.complex128):
        self.model, self.cell, self.shape, self.dtype = model, model.cell, model.masonry.shape, dtype
        filled = model.masonry + (0 if model.granite is None else model.granite)
        self.occupied = filled > 1e-6
        self.pad = tuple(fft.next_fast_len(2 * n - 1) for n in self.shape)      # no wrap-around between cells
        self.index = np.ravel_multi_index(np.nonzero(self.occupied), self.pad)
        self.z = model.centres(2)
        self.offsets = [self.cell * np.where(np.arange(m) < n, np.arange(m), np.arange(m) - m).astype(float)
                        for n, m in zip(self.shape, self.pad)]

    def kernel(self, k: float) -> np.ndarray:
        """The six independent components of the Green's tensor (without its 1/4 pi), transformed."""
        x, y, z = np.meshgrid(*self.offsets, indexing="ij", sparse=True)
        r2 = x**2 + y**2 + z**2
        r2[0, 0, 0] = 1.0                                   # a dipole does not act on itself; zeroed below
        r = np.sqrt(r2)
        wave = np.exp(1j * k * r) / r
        near = 1 / r2 - 1j * k / r
        same, both = wave * (k**2 - near), wave * (3 * near - k**2) / r2
        same[0, 0, 0] = both[0, 0, 0] = 0.0
        out = np.empty((6, *self.pad), dtype=self.dtype)
        for n, (a, b) in enumerate(PAIRS):
            part = both * (x, y, z)[a] * (x, y, z)[b]
            if a == b:
                part += same
            out[n] = fft.fftn(part.astype(self.dtype), workers=1)
        return out

    def fields(self, kernel: np.ndarray, p: np.ndarray) -> np.ndarray:
        """The dipoles' field (times 4 pi) at every cell of the model, from the dipole moments p (3, filled cells)."""
        source = np.zeros((3, int(np.prod(self.pad))), dtype=self.dtype)
        source[:, self.index] = p
        source = fft.fftn(source.reshape(3, *self.pad), axes=(1, 2, 3), workers=1)
        out = np.empty((3, *self.shape), dtype=self.dtype)
        nx, ny, nz = self.shape
        for a in range(3):
            total = sum(kernel[PAIRS.index((min(a, b), max(a, b)))] * source[b] for b in range(3))
            out[a] = fft.ifftn(total, workers=1)[:nx, :ny, :nz]
        return out


def solve(lattice: Lattice, eps_masonry: complex, eps_granite: complex, wavelength: float, direction: int,
          start=None) -> dict:
    """One wavelength: cross-sections (m2) and the mean field in every cell, for a unit incident field.

    direction is -1 for a wave travelling down the axis, +1 for up; start is a first guess (a neighbour's solution).
    """
    k, cell, occupied = 2 * np.pi / wavelength, lattice.cell, lattice.occupied
    mixing = lattice.model.mixing(eps_masonry, eps_granite)
    mean, inverse, normal = mixing[0][occupied], mixing[1][occupied], mixing[2][:, occupied]
    along, across = polarisability(mean, k, cell), polarisability(1 / inverse, k, cell)
    kernel = lattice.kernel(k)
    incident = np.exp(1j * k * direction * lattice.z)                     # x component, per layer
    rhs = np.zeros((3, along.size), dtype=lattice.dtype)
    rhs[0] = np.broadcast_to(incident, lattice.shape)[occupied]
    count = [0]

    def moments(x):                                                       # the dipole a driving field x raises
        return along * x + (across - along) * normal * np.sum(normal * x, axis=0)

    def product(x):
        count[0] += 1
        x = x.reshape(3, -1)
        return (x - lattice.fields(kernel, moments(x))[:, occupied] / (4 * np.pi)).ravel()

    size = rhs.size
    x, info = gmres(LinearOperator((size, size), matvec=product, dtype=rhs.dtype), rhs.ravel(), x0=start,
                    rtol=TOLERANCE, restart=RESTART, maxiter=60)
    if info != 0:
        raise RuntimeError(f"the dipole system did not converge at {wavelength} m (gmres info {info})")
    x = x.reshape(3, -1)
    p = moments(x)
    extinction = k * float(np.sum(np.conj(rhs[0]) * p[0]).imag)
    absorption = k * float(np.sum((p * np.conj(x)).imag) - k**3 / (6 * np.pi) * np.sum(np.abs(p) ** 2))
    field = lattice.fields(kernel, p) / (4 * np.pi)
    field[0] += incident
    p_across = normal * np.sum(normal * p, axis=0)
    volume = cell**3
    field[:, occupied] = (p - p_across) / ((mean - 1) * volume) + p_across / ((1 / inverse - 1) * volume)
    return {"extinction": extinction, "absorption": absorption, "field": field, "moments": p, "driving": x.ravel(),
            "products": count[0], "mixing": mixing}


def scattering(lattice: Lattice, p: np.ndarray, wavelength: float, polar: int = 24) -> float:
    """Scattering cross-section (m2) by integrating the dipoles' far field over all directions.

    Independent of the optical theorem: it is what the energy-conservation test compares with. Costs
    directions x dipoles, so it is for small lattices.
    """
    k = 2 * np.pi / wavelength
    position = np.array([lattice.model.centres(a)[i] for a, i in enumerate(np.nonzero(lattice.occupied))])
    mu, weight = np.polynomial.legendre.leggauss(polar)
    phi = 2 * np.pi * np.arange(2 * polar) / (2 * polar)
    total = 0.0
    for m, w in zip(mu, weight):
        sin = np.sqrt(1 - m**2)
        n = np.array([sin * np.cos(phi), sin * np.sin(phi), np.full_like(phi, m)])       # (3, directions)
        amplitude = np.exp(-1j * k * n.T @ position) @ p.T                               # (directions, 3)
        transverse = amplitude - n.T * np.sum(n.T * amplitude, axis=1, keepdims=True)
        total += w * np.sum(np.abs(transverse) ** 2) * (2 * np.pi / phi.size)
    return float(k**4 * total / (16 * np.pi**2))


def section(model, intensity: np.ndarray) -> np.ndarray:
    """|E|^2 / |E0|^2 on the axial section x = 0 (the mean of the two layers of cells that meet there), as (y, z)."""
    i = int(round(-model.origin[0] / model.cell))
    return intensity[i - 1:i + 1].mean(axis=0)


def region_metrics(model, field: np.ndarray, mixing, eps_masonry) -> dict:
    """{region: (volume mean, maximum)} of |E|^2 / |E0|^2 from the mean field in every cell (3, nx, ny, nz).

    In a cell cut by a wall the chamber's share is the field on the air side and the summit's the masonry side.
    """
    _, inverse, normal = mixing
    return {name: metrics.region_value(name, field[(slice(None), *slices)], normal[(slice(None), *slices)],
                                       inverse[slices], weights, eps_masonry)
            for name, (slices, weights) in model.regions.items()}


def spectrum(model, wavelengths, permittivity, direction: int, dtype=np.complex128, partial=None,
             deadline: float = np.inf) -> dict | None:
    """The solver over a run of wavelengths, each started from its neighbour's solution.

    permittivity(wavelength) gives (masonry, granite). Returns arrays over the wavelengths: extinction and
    absorption (m2), region means and maxima, the axial section, the number of products. With a `partial` path
    the rows done so far are kept there when the clock passes `deadline` (None is returned) and picked up again.
    """
    lattice, start, rows = Lattice(model, dtype), None, []
    names = [f"{kind}.{name}" for name in model.regions for kind in ("mean", "max")]
    if partial is not None and partial.exists():
        with np.load(partial, allow_pickle=True) as kept:
            start, rows = kept["driving"], list(kept["rows"])
    for wavelength in wavelengths[len(rows):]:
        if time.time() > deadline:
            if rows:
                np.savez(partial, driving=start, rows=np.array(rows + [None], dtype=object)[:-1])
            return None
        eps_masonry, eps_granite = permittivity(wavelength)
        solved = solve(lattice, eps_masonry, eps_granite, wavelength, direction, start)
        start = solved["driving"]
        found = region_metrics(model, solved["field"], solved["mixing"], eps_masonry)
        rows.append({"extinction": solved["extinction"], "absorption": solved["absorption"],
                     "products": solved["products"],
                     "section": section(model, np.sum(np.abs(solved["field"]) ** 2, axis=0)).astype(np.float32)}
                    | {f"mean.{name}": value[0] for name, value in found.items()}
                    | {f"max.{name}": value[1] for name, value in found.items()})
    if partial is not None:
        partial.unlink(missing_ok=True)
    out = {key: np.array([row[key] for row in rows]) for key in ("extinction", "absorption", "products", "section", *names)}
    out["scattering"] = out["extinction"] - out["absorption"]
    out["wavelengths"] = np.asarray(wavelengths, float)
    out["section_extent"] = np.array([model.edges(1)[0], model.edges(1)[-1], model.edges(2)[0], model.edges(2)[-1]])
    return out
