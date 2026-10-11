"""Steady conduction, div(sigma grad phi) = 0, by finite volumes on a graded Cartesian grid.

Assumptions:
- one potential per cell, at its centre; the conductance of a face is the two half-cells in series (harmonic mean),
  which is exact for a potential that is linear in each cell;
- a cell of zero conductivity is insulating and is left out of the system, so no current crosses its faces;
- an outer face carries no current unless a potential is given for it;
- a point current enters at the centre of its cell.
"""
import math

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import LinearOperator, cg

AXES = "xyz"


def graded_axis(fine, h, lo, hi, ratio=1.25, snap=()):
    """Cell edges: the points of `fine` joined by equal cells no wider than h, then cells growing by `ratio` to lo and hi.

    Each value in `snap` replaces the edge nearest to it, so that a surface falls on a cell boundary.
    """
    edges = [fine[0]]
    for a, b in zip(fine, fine[1:]):
        n = max(1, math.ceil((b - a) / h - 1e-9))
        edges += [a + (b - a) * i / n for i in range(1, n + 1)]

    def grow(span):
        steps = []
        while sum(steps) < span:
            steps.append(h * ratio ** len(steps))
        offsets = np.cumsum(steps)
        return offsets * span / offsets[-1]  # stretched so that the last edge lands on the boundary

    below = fine[0] - grow(fine[0] - lo)[::-1] if fine[0] > lo else []
    above = fine[-1] + grow(hi - fine[-1]) if hi > fine[-1] else []
    edges = np.concatenate([below, edges, above]).astype(float)
    for point in snap:
        edges[np.argmin(np.abs(edges - point))] = point
    return edges


def centres(edges):
    """The cell centres along each axis."""
    return [(e[1:] + e[:-1]) / 2 for e in edges]


def _shaped(values, axis):
    return np.asarray(values).reshape([-1 if a == axis else 1 for a in range(3)])


def _face_area(edges, axis):
    """Area of the faces normal to `axis`, broadcastable over the grid."""
    a, b = [i for i in range(3) if i != axis]
    return _shaped(np.diff(edges[a]), a) * _shaped(np.diff(edges[b]), b)


def _half_resistance(edges, sigma, axis):
    """Resistance times area of half a cell along `axis`; infinite in an insulating cell."""
    half = _shaped(np.diff(edges[axis]), axis) / 2
    return np.where(sigma > 0, half / np.where(sigma > 0, sigma, 1.0), np.inf)


def _slab(axis, where):
    """Index of the cells on each side of the inner faces ('lo', 'hi') or of the first or last layer (0, -1)."""
    index = [slice(None)] * 3
    index[axis] = {"lo": slice(None, -1), "hi": slice(1, None)}.get(where, where)
    return tuple(index)


def _inner_conductance(edges, sigma, axis):
    half = _half_resistance(edges, sigma, axis)
    return _face_area(edges, axis) / (half[_slab(axis, "lo")] + half[_slab(axis, "hi")])


def _boundary(edges, sigma, face):
    """(axis, layer index, conductance from the cell centres of that layer to the outer face)."""
    axis, layer = AXES.index(face[0]), 0 if face[1] == "-" else -1
    conductance = _face_area(edges, axis) / _half_resistance(edges, sigma, axis)
    return axis, _slab(axis, layer), np.broadcast_to(conductance, sigma.shape)[_slab(axis, layer)]


def solve(edges, sigma, dirichlet=None, sources=(), rtol=1e-10, maxiter=20000):
    """The potential at the cell centres (nan in insulating cells).

    edges: the cell edges along x, y and z. sigma: conductivity per cell, S/m. dirichlet: {face: potential}, the faces
    named 'x-', 'x+', 'y-', 'y+', 'z-', 'z+', the potential a number or an array over that face. sources: (i, j, k,
    current in A) per point source.
    """
    dirichlet = dirichlet or {}
    sigma = np.asarray(sigma, dtype=float)
    active = sigma > 0
    index = np.full(sigma.shape, -1)
    index[active] = np.arange(active.sum())
    n = int(active.sum())
    diagonal, rhs = np.zeros(n), np.zeros(n)
    rows, cols, vals = [], [], []
    for axis in range(3):
        g = _inner_conductance(edges, sigma, axis)
        joined = g > 0
        i, j, g = index[_slab(axis, "lo")][joined], index[_slab(axis, "hi")][joined], g[joined]
        rows += [i, j]
        cols += [j, i]
        vals += [-g, -g]
        diagonal += np.bincount(i, g, n) + np.bincount(j, g, n)
    for face, potential in dirichlet.items():
        _, layer, g = _boundary(edges, sigma, face)
        cells = index[layer]
        held = cells >= 0
        diagonal += np.bincount(cells[held], g[held], n)
        rhs += np.bincount(cells[held], (g * potential)[held], n)
    if not dirichlet:
        raise ValueError("no potential is given on any face, so the potential is fixed only up to a constant")
    for i, j, k, current in sources:
        rhs[index[i, j, k]] += current
    rows, cols, vals = [np.concatenate(part + [extra]) for part, extra in
                        ((rows, np.arange(n)), (cols, np.arange(n)), (vals, diagonal))]
    matrix = coo_matrix((vals, (rows, cols)), shape=(n, n)).tocsr()
    # ponytail: a diagonal preconditioner; iterations grow with the grid's size and grading. Upgrade path: an
    # incomplete Cholesky or a multigrid cycle if the grids grow beyond a few hundred thousand cells.
    jacobi = LinearOperator((n, n), matvec=lambda v: v / diagonal)
    solution, info = cg(matrix, rhs, rtol=rtol, atol=0.0, maxiter=maxiter, M=jacobi)
    if info != 0:
        raise RuntimeError(f"conjugate gradients stopped without converging (info {info})")
    phi = np.full(sigma.shape, np.nan)
    phi[active] = solution
    return phi


def field(edges, sigma, phi, dirichlet=None):
    """E = -grad phi at the cell centres, as (Ex, Ey, Ez): each the mean of J / sigma over the cell's two faces."""
    sigma = np.asarray(sigma, dtype=float)
    filled = np.nan_to_num(phi)
    out = []
    for axis in range(3):
        area = _face_area(edges, axis)
        inner = _inner_conductance(edges, sigma, axis) * (filled[_slab(axis, "lo")] - filled[_slab(axis, "hi")]) / area
        density = np.zeros(sigma.shape)  # the sum over each cell's two faces of the current density along +axis
        density[_slab(axis, "lo")] += inner
        density[_slab(axis, "hi")] += inner
        for face, potential in (dirichlet or {}).items():
            if AXES.index(face[0]) != axis:
                continue
            _, layer, g = _boundary(edges, sigma, face)
            outward = g * (filled[layer] - potential) / np.broadcast_to(area, sigma.shape)[layer]
            density[layer] += outward if face[1] == "+" else -outward
        with np.errstate(divide="ignore", invalid="ignore"):
            out.append(np.where(sigma > 0, density / (2 * sigma), np.nan))
    return tuple(out)


def magnitude(components):
    """|E| from its three components."""
    return np.sqrt(sum(c**2 for c in components))
