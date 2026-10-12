"""The 2018 electromagnetic study, re-run with two in-house field solvers (claims E19 and E20).

mie       the exact series for a sphere, the benchmark
shapes    the bodies as fill fractions on a regular grid, from the ledger
dda       frequency domain: coupled dipoles (a volume-integral solver), free space only
fdtd      time domain: a Yee grid with absorbing layers and a plane wave over air and ground
cases     the case table of the foundation spec's section 6
metrics   extinction spectra, chamber ratios, the summit metric, the gates, the rules for E19 and E20
runs      the task plan, the cache, and the path from cached runs to gates and verdicts
"""
import os
from pathlib import Path


def keep(path: Path, write) -> None:
    """Write a file through a temporary one: a write that is cut short never leaves a broken file under the final name."""
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as handle:
        write(handle)
    os.replace(tmp, path)
