"""Unit helpers and the gmsh session that every geometry function runs inside."""
from contextlib import contextmanager

import gmsh

IN: float = 0.0254


def inch(x: float) -> float:
    """Inches to metres."""
    return x * IN


@contextmanager
def session():
    """Open gmsh with its terminal output off; close it on the way out, also after an error."""
    gmsh.initialize(readConfigFiles=False)  # a user's saved gmsh options must not change the geometry
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("pyramid")
    try:
        yield
    finally:
        gmsh.finalize()
