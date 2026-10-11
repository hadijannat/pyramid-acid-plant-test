"""The hypothesis's two electrical sources on the pyramid: a telluric far field and a lightning stroke at the summit.

The scene: the pyramid as a square body of masonry (its designed shape, cut off at today's platform) on a half-space
of bedrock, the air insulating; inside it the King's Chamber as an insulating cavity lined with a granite shell.

Assumptions:
- conduction is steady. The telluric field varies over seconds to hours, far slower than the relaxation times of
  the stone (Tier 0), so that case is exact in this respect. The stroke is taken at its peak current as if it were
  steady: induction, which is left out, pushes current towards the faces and lowers the field at the chamber
  (04 section 4.5), so the conduction value is the generous one; ionisation near the attachment is left out too;
- the granite is a shell of one assumed thickness round the chamber; the relieving chambers, the antechamber and
  the other passages and chambers are left out;
- the masonry is homogeneous: joints, the casing and a wetter skin are not drawn;
- an ore body is a pair of vertical sheets in line with the far field, one each side of the pyramid, ending at its
  base edges, so that what they gather is delivered across the base: the arrangement that most favours the claim.
  A sheet thinner than a cell is drawn as that cell with the sheet's conductance added;
- the outer faces lie 3 km away: the far field is imposed there for the telluric case and the potential of a point
  current on a half-space for the stroke.
"""
import math

import numpy as np

from pyramid.electro import conduction

GEOMETRY = (
    "pyr.base_side", "pyr.height_original", "pyr.height_present", "kc.west_wall.x", "kc.east_wall.x",
    "kc.south_wall.y", "kc.north_wall.y", "kc.floor.z", "kc.ceiling.z",
)
SHELL = "elec.granite_shell_thickness"
MATERIALS = ("em.limestone_resistivity", "plateau.host_resistivity", "em.granite_conductivity")
SHEETS = ("elec.ore_sheet_thickness", "elec.ore_sheet_depth", "plateau.vein_leakage_length")
EXTENT = 3000.0  # m, half-width and depth of the block of ground that is solved: numerical, 13 base sides
RATIO = 1.25  # growth of the cells away from the chamber: numerical


class Scene:
    """The grid and what fills each cell."""

    def __init__(self, q, h, sheet_resistivity=None):
        shell = q[SHELL]
        boxes = [(q["kc.west_wall.x"], q["kc.east_wall.x"]), (q["kc.south_wall.y"], q["kc.north_wall.y"]),
                 (q["kc.floor.z"], q["kc.ceiling.z"])]
        tops = (EXTENT, EXTENT, q["pyr.height_present"])
        self.edges = [
            conduction.graded_axis([a - shell, a, b, b + shell], h, -EXTENT, top, RATIO, snap=(0.0,) * (axis == 2))
            for axis, ((a, b), top) in enumerate(zip(boxes, tops))
        ]
        x, y, z = np.meshgrid(*conduction.centres(self.edges), indexing="ij")
        self.half_base = q["pyr.base_side"] / 2
        self.apex = q["pyr.height_original"]
        self.ground = z < 0
        self.masonry = (z > 0) & (np.maximum(np.abs(x), np.abs(y)) < self.half_base * (1 - z / self.apex))
        inside = [(c > a) & (c < b) for c, (a, b) in zip((x, y, z), boxes)]
        near = [(c > a - shell) & (c < b + shell) for c, (a, b) in zip((x, y, z), boxes)]
        self.cavity = inside[0] & inside[1] & inside[2]
        self.granite = near[0] & near[1] & near[2] & ~self.cavity
        self.sigma = np.where(self.ground, 1 / q["plateau.host_resistivity"], 0.0)
        self.sigma[self.masonry] = 1 / q["em.limestone_resistivity"]
        self.sigma[self.granite] = q["em.granite_conductivity"]
        self.sigma[self.cavity] = 0.0
        self.volume = np.einsum("i,j,k->ijk", *[np.diff(e) for e in self.edges])
        # the masonry beside the chamber, between its floor and its ceiling: the field the granite sits in
        self.beside = self.masonry & ~self.granite & ~self.cavity & inside[2]
        self.section = int(np.searchsorted(self.edges[0], (boxes[0][0] + boxes[0][1]) / 2)) - 1  # x through the chamber
        if sheet_resistivity is not None:
            # the column of cells holding x = 0, where the two sheets stand; conductance added, not replaced
            column = int(np.searchsorted(self.edges[0], 0.0, side="right")) - 1
            reach = self.half_base + q["plateau.vein_leakage_length"]
            sheet = self.ground[column] & (np.abs(y[column]) > self.half_base) & (np.abs(y[column]) < reach) \
                & (z[column] > -q["elec.ore_sheet_depth"])
            width = np.diff(self.edges[0])[column]
            self.sigma[column][sheet] += q["elec.ore_sheet_thickness"] / (sheet_resistivity * width)

    def summit(self):
        """The masonry cells of the topmost layer: the model's summit platform."""
        top = np.zeros_like(self.masonry)
        top[:, :, -1] = self.masonry[:, :, -1]
        return top

    def granite_field(self, strength):
        """(peak, volume mean) of a field strength over the granite cells."""
        return float(strength[self.granite].max()), float(np.average(strength[self.granite], weights=self.volume[self.granite]))


def telluric(q, h=1.0, sheet_resistivity=None):
    """The scene in a far field of 1 V/m along north-south: (scene, potential, field strength)."""
    scene = Scene(q, h, sheet_resistivity)
    _, cy, _ = conduction.centres(scene.edges)
    y = scene.edges[1]
    # the far field's own potential, -y, on every outer face of the ground: exact for the undisturbed half-space
    far = {"y-": -y[0], "y+": -y[-1], "x-": -cy[:, None], "x+": -cy[:, None], "z-": -cy[None, :]}
    phi = conduction.solve(scene.edges, scene.sigma, far)
    return scene, phi, conduction.magnitude(conduction.field(scene.edges, scene.sigma, phi, far))


def telluric_summary(q, h=1.0, sheet_resistivity=None):
    """Field strengths per unit far field: the granite's peak and mean, the masonry beside it, the summit masonry."""
    scene, _, strength = telluric(q, h, sheet_resistivity)
    peak, mean = scene.granite_field(strength)
    summit, beside = (float(np.average(strength[cells], weights=scene.volume[cells]))
                      for cells in (scene.summit(), scene.beside))
    return {"granite_peak": peak, "granite_mean": mean, "masonry": beside, "summit": summit,
            "largest": max(peak, summit)}


def lightning(q, h=1.0):
    """The scene with 1 A entering over the summit platform: (scene, potential, field strength)."""
    scene = Scene(q, h)
    cx, cy, cz = conduction.centres(scene.edges)
    x, y, z = scene.edges

    def far(a, b, c):  # a point current of 1 A on a half-space of bedrock: rho / (2 pi r)
        return q["plateau.host_resistivity"] / (2 * math.pi * np.sqrt(a**2 + b**2 + c**2))

    held = {
        "x-": far(x[0], cy[:, None], cz[None, :]), "x+": far(x[-1], cy[:, None], cz[None, :]),
        "y-": far(cx[:, None], y[0], cz[None, :]), "y+": far(cx[:, None], y[-1], cz[None, :]),
        "z-": far(cx[:, None], cy[None, :], z[0]),
    }
    top = scene.summit()
    area = np.where(top, scene.volume, 0.0)[:, :, -1]
    sources = [(i, j, top.shape[2] - 1, area[i, j] / area.sum()) for i, j in zip(*np.nonzero(area))]
    phi = conduction.solve(scene.edges, scene.sigma, held, sources)
    return scene, phi, conduction.magnitude(conduction.field(scene.edges, scene.sigma, phi, held))


def uniform_spreading(q):
    """04 section 4.5's estimate, per ampere: the stroke spread evenly over the pyramid's section at chamber level."""
    level = (q["kc.floor.z"] + q["kc.ceiling.z"]) / 2
    side = q["pyr.base_side"] * (1 - level / q["pyr.height_original"])
    return q["em.limestone_resistivity"] / side**2


def lightning_summary(q, h=1.0):
    """Field strengths per ampere: the granite's peak and mean, the masonry beside it, peak over even spreading."""
    scene, _, strength = lightning(q, h)
    peak, mean = scene.granite_field(strength)
    beside = float(np.average(strength[scene.beside], weights=scene.volume[scene.beside]))
    return {"granite_peak": peak, "granite_mean": mean, "masonry": beside, "multiple": peak / uniform_spreading(q)}


def chamber_depth(q):
    """Distance from the centre of the King's Chamber to the nearest face of the pyramid, m."""
    half, apex = q["pyr.base_side"] / 2, q["pyr.height_original"]
    level = (q["kc.floor.z"] + q["kc.ceiling.z"]) / 2
    offset = max(abs(q["kc.west_wall.x"] + q["kc.east_wall.x"]), abs(q["kc.south_wall.y"] + q["kc.north_wall.y"])) / 2
    return (half * (1 - level / apex) - offset) * apex / math.hypot(apex, half)  # times the sine of the face slope
