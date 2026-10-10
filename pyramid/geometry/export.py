"""Write a built model out: STEP for CAD, a gmsh mesh for solvers, glb for the viewer.

Call the writers inside the frame.session() that built the model, with that model alone in the session.
Run as `uv run python -m pyramid.geometry.export` to write the STEP files of both levels.
"""
from pathlib import Path

import gmsh
import numpy as np
import trimesh

from pyramid import REPO_ROOT
from pyramid.geometry.frame import session
from pyramid.geometry.model import Model, build, check
from pyramid.ledger import load
from pyramid.provenance import write_manifest

occ = gmsh.model.occ


def to_viewer(x: float, y: float, z: float) -> tuple[float, float, float]:
    """Project frame (X east, Y north, Z up) to the viewer's Y-up frame."""
    return x, z, -y


def _solids(model: Model) -> dict[str, int]:
    """Name -> volume tag: every space, then the masonry, then the bedrock if the model has one."""
    solids = {name: space.tag for name, space in model.spaces.items()}
    solids["masonry"] = model.masonry
    if model.bedrock is not None:
        solids["bedrock"] = model.bedrock
    return solids


def _surface_mesh(tag: int) -> tuple[np.ndarray, np.ndarray]:
    """Vertices (n, 3) and triangles (m, 3) of the surface mesh that bounds one volume."""
    tags, points, triangles = [], [], []
    for _, surface in gmsh.model.getBoundary([(3, tag)], oriented=False):
        node_tags, xyz, _ = gmsh.model.mesh.getNodes(2, surface, includeBoundary=True, returnParametricCoord=False)
        tags.append(node_tags)
        points.append(np.reshape(xyz, (-1, 3)))
        triangles.append(gmsh.model.mesh.getElementsByType(2, surface)[1])  # type 2: 3-node triangle
    tags, first = np.unique(np.concatenate(tags), return_index=True)
    return np.concatenate(points)[first], np.searchsorted(tags, np.concatenate(triangles)).reshape(-1, 3)


def write_glb(model: Model, path: Path) -> None:
    """The model as binary glTF in viewer coordinates: one named node per space, plus "masonry" and "bedrock"."""
    occ.synchronize()
    gmsh.model.mesh.clear()
    gmsh.model.mesh.generate(2)
    scene = trimesh.Scene()
    for name, tag in _solids(model).items():
        vertices, faces = _surface_mesh(tag)
        # ponytail: triangle winding is as gmsh gives it, not checked to face outward; the viewer draws both sides.
        mesh = trimesh.Trimesh([to_viewer(*vertex) for vertex in vertices], faces, process=False)
        scene.add_geometry(mesh, node_name=name, geom_name=name)
    Path(path).write_bytes(scene.export(file_type="glb"))


def write_step(model: Model, path: Path) -> None:
    """Every solid of the model as one STEP file. The path must end in .step."""
    occ.synchronize()
    gmsh.write(str(path))


def write_msh(model: Model, path: Path, size: float) -> None:
    """A tetrahedral mesh with elements up to `size` metres, one named physical group per solid.

    Meshes from scratch on every call, so `size` always applies, and replaces any earlier groups.

    ponytail: nothing here makes the mesh conformal, and it cannot mesh the survey model as it is.
    Tetrahedral meshing of the survey model fails on its overlapping and coincident boundaries
    ("Invalid boundary mesh (overlapping facets)"), so fragment the model (occ.fragment) first;
    the solver plan does. The paper model meshes as it is, each solid on its own.
    """
    occ.synchronize()
    gmsh.model.mesh.clear()
    gmsh.model.removePhysicalGroups(gmsh.model.getPhysicalGroups(3))
    for name, tag in _solids(model).items():
        gmsh.model.addPhysicalGroup(3, [tag], name=name)
    gmsh.option.setNumber("Mesh.MeshSizeMax", size)
    gmsh.model.mesh.generate(3)
    gmsh.write(str(path))


def main() -> None:
    """Build and check both levels; write results/geometry/{survey.step,paper.step,manifest.json}."""
    ledger = load()
    out_dir = REPO_ROOT / "results" / "geometry"
    out_dir.mkdir(parents=True, exist_ok=True)
    failed = {}
    for level in ("survey", "paper"):
        with session():  # one model per session: write_step writes everything in the session
            model = build(ledger, level)
            failed[level] = check(model, ledger)
            write_step(model, out_dir / f"{level}.step")
        outcome = "; ".join(failed[level]) or "every self-check passed"
        print(f"{level}: {(out_dir / f'{level}.step').relative_to(REPO_ROOT)}, {len(model.spaces)} spaces, {outcome}")
    write_manifest(out_dir, "geometry", ledger, {"files": [f"{level}.step" for level in failed],
                                                 "failed_self_checks": failed})


if __name__ == "__main__":
    main()
