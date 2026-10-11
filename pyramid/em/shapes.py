"""The bodies of the electromagnetic cases as fill fractions on a regular grid of cubic cells.

Frame: x east, y north, z up, origin at the centre of the base, as in pyramid.geometry. A grid plane lies on
x = 0, y = 0 and z = 0, so the base (and the ground surface) is never inside a cell.

Assumptions: a cell cut by a surface carries the fraction of it that is filled, and the solvers give it the
volume-weighted permittivity; chambers are air; the study's chambers are read as pyramid.geometry reads them
(length east-west, width north-south, centre offset to the south, centre.z the height of the centre); the
surveyed Queen's Chamber is a box as high as the mean of its wall and ridge heights; the Grand Gallery is a
sloping slab of its mean width; passages, shafts, the antechamber, the relieving chambers and the surveyed
Subterranean Chamber are left out (all thinner than a cell or outside the claims); the granite is a shell
round the King's Chamber box (emx.granite_shell).
"""
from dataclasses import dataclass

import numpy as np

Z_SAMPLES = 8        # midpoint samples per cell along the axis a sloping surface is integrated over


@dataclass
class Model:
    """A case on a grid: fractions of each cell that are masonry and granite, and the regions the metrics use."""
    cell: float
    origin: np.ndarray               # the low corner of cell (0, 0, 0), m
    masonry: np.ndarray              # (nx, ny, nz) fraction of the cell that is masonry (below z = 0: ground)
    granite: np.ndarray | None
    regions: dict                    # name -> (slices of the cell box, weights there: the fraction that is the region)

    def edges(self, axis: int) -> np.ndarray:
        return self.origin[axis] + self.cell * np.arange(self.masonry.shape[axis] + 1)

    def centres(self, axis: int) -> np.ndarray:
        return self.origin[axis] + self.cell * (np.arange(self.masonry.shape[axis]) + 0.5)


def overlap(edges: np.ndarray, low, high) -> np.ndarray:
    """Length of [low, high] inside each cell of a row of cells; low and high may be arrays (one row each)."""
    low, high = np.asarray(low, dtype=float)[..., None], np.asarray(high, dtype=float)[..., None]
    return np.clip(np.minimum(edges[1:], high) - np.maximum(edges[:-1], low), 0.0, None)


def box(edges, low, high) -> np.ndarray:
    """Fraction of each cell inside the box low..high (exact: the three axes separate)."""
    ox, oy, oz = (overlap(edges[a], low[a], high[a]) / (edges[a][1] - edges[a][0]) for a in range(3))
    return ox[:, None, None] * oy[None, :, None] * oz[None, None, :]


def _samples(edges: np.ndarray, low: float, high: float):
    """Midpoints and weights (fraction of a cell each) of Z_SAMPLES slices of every cell, clipped to low..high."""
    a, b = np.clip(edges[:-1], low, high), np.clip(edges[1:], low, high)
    t = (np.arange(Z_SAMPLES) + 0.5) / Z_SAMPLES
    return a[:, None] + (b - a)[:, None] * t, np.repeat(((b - a) / Z_SAMPLES / (edges[1] - edges[0]))[:, None], Z_SAMPLES, 1)


def pyramid(edges, base: float, height: float, low: float = 0.0, high: float | None = None) -> np.ndarray:
    """Fraction of each cell inside a square pyramid (apex at `height`) between the levels low and high.

    Exact across each level (a square), midpoint rule up the axis.
    """
    z, w = _samples(edges[2], low, min(height, height if high is None else high))
    half = base / 2 * (1 - z / height)                                    # half-width of the square at each level
    ox = overlap(edges[0], -half, half) / (edges[0][1] - edges[0][0])     # (nz, samples, nx)
    oy = overlap(edges[1], -half, half) / (edges[1][1] - edges[1][0])
    return np.einsum("ksx,ksy,ks->xyk", ox, oy, w)


def sphere(edges, radius: float) -> np.ndarray:
    """Fraction of each cell inside a sphere at the origin: exact chords along x, midpoint rule in y and z."""
    (y, wy), (z, wz) = _samples(edges[1], -radius, radius), _samples(edges[2], -radius, radius)
    chord = np.sqrt(np.clip(radius**2 - y[:, :, None, None] ** 2 - z[None, None, :, :] ** 2, 0.0, None))
    ox = overlap(edges[0], -chord, chord) / (edges[0][1] - edges[0][0])   # (ny, s, nz, s, nx)
    return np.einsum("jsktx,js,kt->xjk", ox, wy, wz)


def sloping_slab(edges, south, north, width: float, height: float) -> np.ndarray:
    """Fraction of each cell inside a slab whose floor runs from the point `south` to `north` (x, y, z each)."""
    y, w = _samples(edges[1], south[1], north[1])
    t = (y - south[1]) / (north[1] - south[1])
    x, floor = south[0] + t * (north[0] - south[0]), south[2] + t * (north[2] - south[2])
    ox = overlap(edges[0], x - width / 2, x + width / 2) / (edges[0][1] - edges[0][0])
    oz = overlap(edges[2], floor, floor + height) / (edges[2][1] - edges[2][0])
    return np.einsum("jsx,jsz,js->xjz", ox, oz, w)


def paper_chambers(q) -> dict:
    """The study's three box chambers as (low corner, high corner)."""
    boxes = {}
    for name, key in (("kings", "paper.kc"), ("queens", "paper.qc"), ("lower", "paper.lower")):
        length, width, height = q(f"{key}.length"), q(f"{key}.width"), q(f"{key}.height")
        y, z = -q(f"{key}.axis_offset"), q(f"{key}.centre.z")
        boxes[name] = ((-length / 2, y - width / 2, z - height / 2), (length / 2, y + width / 2, z + height / 2))
    return boxes


def survey_chambers(q) -> dict:
    """The surveyed King's and Queen's Chambers as boxes."""
    queens_top = q("qc.floor.z") + (q("qc.wall_height") + q("qc.ridge_height")) / 2   # a gable has its mean height
    return {
        "kings": ((q("kc.west_wall.x"), q("kc.south_wall.y"), q("kc.floor.z")),
                  (q("kc.east_wall.x"), q("kc.north_wall.y"), q("kc.ceiling.z"))),
        "queens": ((q("qc.west_wall.x"), q("qc.north_wall.y") - q("qc.width_ns"), q("qc.floor.z")),
                   (q("qc.east_wall.x"), q("qc.north_wall.y"), queens_top)),
    }


def body_volume(case) -> float:
    """Volume of a case's outer solid, m3 (the frustum when the apex is cut off)."""
    if case.body == "sphere":
        return 4 / 3 * np.pi * case.base**3
    if case.body == "cube":
        return case.base**3
    cut = 1 - case.top / case.height
    return case.base**2 * case.height / 3 * (1 - cut**3)


def build(case, q, cell: float) -> Model:
    """The case's fill fractions and metric regions on a grid of the given cell size; q is ledger.q."""
    def span(low, high):                       # whole cells from a grid plane at 0, with a hair of tolerance
        return np.floor(low / cell + 1e-9) * cell, np.ceil(high / cell - 1e-9) * cell

    chambers = {"paper": paper_chambers, "survey": survey_chambers, "none": lambda q: {}}[case.chambers](q)
    if not case.ground:
        chambers.pop("lower", None)            # 29.8 m below the base: outside a body that floats in free space
    half = case.base if case.body == "sphere" else case.base / 2
    top = {"sphere": case.base, "cube": case.base, "pyramid": case.top}[case.body]
    bottom = -case.base if case.body == "sphere" else min([0.0] + [low[2] - 2 * cell for low, _ in chambers.values()])
    bounds = [span(-half, half), span(-half, half), span(bottom, top)]
    origin = np.array([low for low, _ in bounds])
    edges = [low + cell * np.arange(round((high - low) / cell) + 1) for low, high in bounds]

    if case.body == "sphere":
        solid = sphere(edges, case.base)
    elif case.body == "cube":
        solid = box(edges, (-half, -half, 0.0), (half, half, case.base))
    else:
        solid = pyramid(edges, case.base, case.height, 0.0, case.top)
    if case.ground:
        solid = solid + box(edges, (-np.inf, -np.inf, -np.inf), (np.inf, np.inf, 0.0))   # the half-space below

    regions, void, granite = {}, np.zeros_like(solid), None
    for name, (low, high) in chambers.items():
        regions[name] = box(edges, low, high)
        void += regions[name]
    if case.chambers == "survey":
        south = tuple(q(f"gg.south_end.{a}") for a in "xyz")
        north = tuple(q(f"gg.north_end.{a}") for a in "xyz")
        regions["gallery"] = sloping_slab(edges, south, north, (q("gg.width") + q("gg.roof_width")) / 2, q("gg.height"))
        void += regions["gallery"]
        low, high = chambers["kings"]
        shell = q("emx.granite_shell")
        granite = box(edges, [v - shell for v in low], [v + shell for v in high]) - regions["kings"]
        granite = np.clip(granite - regions["gallery"], 0.0, None)        # the Gallery's top end reaches the shell
    masonry = np.clip(solid - void - (0 if granite is None else granite), 0.0, 1.0)
    if case.body == "pyramid" and case.top >= q("pyr.height_present") - 1e-6:
        summit_top = q("pyr.height_present")
        regions["summit"] = pyramid(edges, case.base, case.height, summit_top - q("emx.summit_depth"), summit_top)
    return Model(cell, origin, masonry.astype(np.float32), None if granite is None else granite.astype(np.float32),
                 {name: _crop(weights) for name, weights in regions.items()})


def _crop(weights: np.ndarray):
    """(slices, weights) of the smallest cell box that holds every non-zero weight."""
    hit = [np.flatnonzero(weights.any(axis=tuple(b for b in range(3) if b != a))) for a in range(3)]
    slices = tuple(slice(int(h[0]), int(h[-1]) + 1) for h in hit)
    return slices, weights[slices].astype(np.float32)
