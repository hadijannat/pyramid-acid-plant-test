"""Tests for the exporters: STEP, the gmsh mesh and the viewer's glb."""
import functools

import gmsh
import pytest
import trimesh

from pyramid import ledger
from pyramid.geometry import export, frame, model

PAPER_NODES = {"paper_kings_chamber", "paper_queens_chamber", "paper_lower_chamber", "masonry"}


@functools.cache
def led() -> ledger.Ledger:
    return ledger.load()


def bounds(scene: trimesh.Scene, node: str) -> list[float]:
    """(xmin, ymin, zmin, xmax, ymax, zmax) of the mesh that hangs on one node of a loaded glb."""
    _, geometry = scene.graph.get(node)
    return scene.geometry[geometry].bounds.ravel().tolist()


def test_to_viewer_turns_z_up_into_y_up():
    assert export.to_viewer(1, 2, 3) == (1, 3, -2)


def test_glb_of_the_paper_model_reloads_with_one_node_per_solid(tmp_path):
    path = tmp_path / "paper.glb"
    with frame.session():
        export.write_glb(model.build(led(), level="paper"), path)
    scene = trimesh.load(path, force="scene")
    assert set(scene.graph.nodes_geometry) == PAPER_NODES
    # viewer coordinates: the 2018 King's Chamber is 35 to 46 m up (viewer Y) and 2.5 to 7.5 m south (viewer +Z)
    assert bounds(scene, "paper_kings_chamber") == pytest.approx([-5.5, 35.0, 2.5, 5.5, 46.0, 7.5], abs=1e-3)
    assert bounds(scene, "masonry") == pytest.approx([-115.0, 0.0, -115.0, 115.0, 138.75, 115.0], abs=1e-3)


def test_glb_of_the_survey_model_has_every_space_and_masonry_and_bedrock(tmp_path):
    path = tmp_path / "interior.glb"
    with frame.session():
        built = model.build(led())
        export.write_glb(built, path)
        names = set(built.spaces)
    scene = trimesh.load(path, force="scene")
    assert len(names) == 19
    assert set(scene.graph.nodes_geometry) == names | {"masonry", "bedrock"}
    # the top of the Grand Gallery's roof, 51.5 m, is its highest viewer Y; its north wall, y 41.32, its lowest viewer Z
    gallery = bounds(scene, "grand_gallery")
    assert (gallery[4], gallery[2]) == pytest.approx((51.5006, -41.3207), abs=1e-3)
    assert bounds(scene, "bedrock")[1] == pytest.approx(-60.0, abs=1e-3)


def test_step_file_holds_every_solid(tmp_path):
    path = tmp_path / "paper.step"
    with frame.session():
        export.write_step(model.build(led(), level="paper"), path)
    assert path.read_text().startswith("ISO-10303-21")
    with frame.session():
        gmsh.model.occ.importShapes(str(path))
        gmsh.model.occ.synchronize()
        volumes = sorted(gmsh.model.occ.getMass(3, tag) for _, tag in gmsh.model.getEntities(3))
    # three chambers and the masonry; ratios, because a STEP reader may rescale the length unit
    assert len(volumes) == 4
    assert [v / volumes[0] for v in volumes] == pytest.approx(
        [1.0, 150.0 / 133.952, 605.0 / 133.952, 2445870.0 / 133.952], rel=1e-6)


def test_msh_file_holds_named_groups_of_tetrahedra(tmp_path):
    path = tmp_path / "paper.msh"
    with frame.session():
        export.write_msh(model.build(led(), level="paper"), path, size=30.0)
    with frame.session():
        gmsh.open(str(path))
        names = {gmsh.model.getPhysicalName(3, tag) for _, tag in gmsh.model.getPhysicalGroups(3)}
        tetrahedra, _ = gmsh.model.mesh.getElementsByType(4)  # type 4: 4-node tetrahedron
    assert names == PAPER_NODES
    assert len(tetrahedra) > 100
