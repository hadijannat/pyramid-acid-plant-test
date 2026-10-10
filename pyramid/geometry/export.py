"""Write a built model out: STEP for CAD, a gmsh mesh for solvers, glb for the viewer.

Call these inside the frame.session() that built the model, with that model alone in the session.
"""
from pathlib import Path

import gmsh
import numpy as np
import trimesh

from pyramid.geometry.model import Model

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

    ponytail: nothing here makes the mesh conformal. Spaces that overlap one another are meshed
    on top of each other, and nodes need not be shared where the masonry meets a space.
    Fragment the model first when a solver needs one conformal mesh.
    """
    occ.synchronize()
    for name, tag in _solids(model).items():
        gmsh.model.addPhysicalGroup(3, [tag], name=name)
    gmsh.option.setNumber("Mesh.MeshSizeMax", size)
    gmsh.model.mesh.generate(3)
    gmsh.write(str(path))
