"""North-south elevation of the interior, drawn from the viewer's glTF model.

Run: uv run python -m pyramid.elevation  ->  docs/figures/interior-elevation.svg

The figure is a projection of the same meshes the viewer renders (viewer frame:
x east, y up, z south), so it cannot disagree with the model.
"""

from pathlib import Path

import matplotlib
import numpy as np
import trimesh
from matplotlib.collections import PolyCollection
from scipy.spatial import ConvexHull

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GLB = ROOT / "viewer" / "data" / "interior.glb"
OUT = ROOT / "docs" / "figures" / "interior-elevation.svg"

# label text -> (space, text position, optional point the leader should aim near); metres north, metres up
LABELS = {
    "Subterranean Chamber": ("subterranean_chamber", (-48, -29)),
    "Descending Passage": ("descending_passage", (78, -26)),
    "Ascending Passage": ("ascending_passage", (62, 30)),
    "Well shaft": ("well_shaft", (30, -45), (36, -20)),
    "Queen's Chamber": ("queens_chamber", (-48, 24)),
    "Grand Gallery": ("grand_gallery", (58, 56)),
    "Antechamber": ("antechamber", (-52, 36)),
    "King's Chamber": ("kings_chamber", (-60, 46)),
    "Relieving chambers": ("relieving_chambers", (-78, 64)),
    "Big Void (muon image)": ("big_void", (-5, 84)),
    "King's Chamber shafts": ("kc_shaft_north", (62, 86), (45, 75)),
    "Queen's Chamber shafts": ("qc_shaft_south", (-75, 5), (-10, 30)),
    "North Face Corridor": ("north_face_corridor", (108, 34)),
}


def project(mesh: trimesh.Trimesh) -> np.ndarray:
    """Triangles as (n, 3, 2) arrays of (metres north, metres up)."""
    v = mesh.vertices[mesh.faces]
    return np.stack([-v[:, :, 2], v[:, :, 1]], axis=-1)


def draw(ax, scene, labels: dict = LABELS) -> dict:
    """The bedrock, the masonry, the spaces and their labels on `ax`; returns the spaces' meshes by name."""
    spaces = {k: g for k, g in scene.geometry.items() if k not in ("masonry", "bedrock")}
    assert len(spaces) == 19, sorted(spaces)
    # Masonry and bedrock are convex in this projection, so their hulls are their silhouettes.
    for name, colour in (("bedrock", "#c9c1b3"), ("masonry", "#e6e0d4")):
        pts = project(scene.geometry[name]).reshape(-1, 2)
        ax.add_collection(PolyCollection([pts[ConvexHull(pts).vertices]], facecolors=colour, edgecolors="none"))
    # ponytail: a filled triangle soup with no edges is each space's silhouette; no boolean union needed.
    for g in spaces.values():
        # A stroke in the fill colour keeps the 0.2 m shafts visible at page scale.
        ax.add_collection(PolyCollection(project(g), facecolors="#1f6fb2", edgecolors="#1f6fb2", linewidths=1.0))

    for text, (space, (tx, ty), *hint) in labels.items():
        pts = project(spaces[space]).reshape(-1, 2)
        near = np.array(hint[0]) if hint else (pts.min(0) + pts.max(0)) / 2
        target = pts[np.argmin(((pts - near) ** 2).sum(1))]
        ax.annotate(text, xy=target, xytext=(tx, ty), fontsize=9, color="#333",
                    ha="center", va="center",
                    arrowprops=dict(arrowstyle="-", color="#777", lw=0.7, shrinkB=2))
    return spaces


def frame(ax) -> None:
    """The limits, axis labels and spines every figure drawn on the elevation shares."""
    ax.set_xlim(-125, 135)
    ax.set_ylim(-66, 146)
    ax.set_aspect("equal")
    ax.set_xlabel("metres north of the pyramid's centre")
    ax.set_ylabel("metres above the pavement")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def main(out: Path = OUT) -> None:
    plt.rcParams["svg.hashsalt"] = "pyramid"   # the same model gives the same file, byte for byte
    scene = trimesh.load(GLB)
    fig, ax = plt.subplots(figsize=(13, 6.8))
    draw(ax, scene)
    frame(ax)
    ax.set_title("Great Pyramid, north-south elevation: the interior as modelled from Petrie's 1883 survey", fontsize=11)
    ax.text(0.99, 0.02, "masonry shown to the present top; spaces projected east-west; from pyramid.geometry via viewer/data/interior.glb",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#666")

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", metadata={"Date": None}, facecolor="white")   # white: readable on a dark page
    print("wrote", out)


if __name__ == "__main__":
    main()
