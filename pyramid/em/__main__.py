"""python -m pyramid.em: run the cases in both solvers, apply the gates, and decide E19 and E20 if the gates allow.

  --quick         B0 and R1 on the coarse grid only: a smoke check of both solvers
  --case NAME     only cases whose name starts with NAME (may be repeated)
  --seconds N     stop working after N seconds; finished tasks are cached, unfinished ones resume on the next call
  --workers N     parallel processes (at most 10)
  --report        do not compute: evaluate what is cached
  --solver, --cell  only tasks of one solver (dda, fdtd) or one cell size (coarse, production, fine)

Every finished task is a file in results/em/cache/, so a call only does what is missing. The gates come first
(benchmark, convergence, reproduction): the variants and controls are run, and the two claims decided, only
when all three pass. If one fails the summary carries the gates and the reproduction numbers and no verdict.
"""
import argparse
import json
import multiprocessing
import os
import time
from pathlib import Path

import numpy as np

from pyramid.em import cases, metrics, mie
from pyramid.em.runs import ASSUMPTIONS, CACHE, band_max, cells, collect, evaluate, path, plan, work
from pyramid.ledger import load
from pyramid.simkit import write_results


def figures(ledger, summary: dict, out_dir: Path):
    """The spectra against Mie and against the study's peaks, and the axial section at the R1 maximum."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    q, size = ledger.q, cells(ledger.q)
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {"Software": None, "Creation Time": None}
    wavelengths = cases.wavelengths(q)
    exact = mie.cross_sections(q("emx.sphere_radius"), q("paper.eps_real") + 1j * q("paper.eps_imag"), np.arange(200.0, 600.5, 1.0))[0]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(np.arange(200.0, 600.5, 1.0), exact / 1e6, "k-", lw=1, label="Mie")
    for solver, style in (("dda", "o"), ("fdtd", "s")):
        for cell in ("production", "fine"):
            r = collect(ledger, "B0", solver, size[cell])
            if r is not None:
                ax.plot(r["wavelengths"], r["extinction"] / 1e6, style, ms=3, mfc="none" if cell == "fine" else None,
                        label=f"{solver}, {size[cell]:.3g} m cell")
    ax.set(xlabel="wavelength, m", ylabel="extinction, km2", title="B0: sphere of radius 100 m, 5 + 0.1i")
    ax.legend()
    fig.savefig(out_dir / "b0_extinction.png", dpi=130, bbox_inches="tight", metadata=meta)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    for name, solver, style in (("R1", "dda", "C0-"), ("R1", "fdtd", "C0--"), ("R2", "dda", "C1-"), ("R2", "fdtd", "C1--"), ("R3", "fdtd", "C2--")):
        r = collect(ledger, name, solver, size["production"])
        if r is not None:
            ax.plot(r["wavelengths"], r["extinction"] / 1e6, style, label=f"{name}, {solver}")
    for key, marker in (("peak1", "v"), ("peak2", "v"), ("ground_peak", "^")):
        ax.plot(q(f"paper.{key}.wavelength"), q(f"paper.{key}.extinction") / 1e6, "k" + marker, ms=8)
    ax.plot([], [], "kv", label="study, free space (read from Fig. 1)")
    ax.plot([], [], "k^", label="study, on ground (read from Fig. 5b)")
    ax.set(xlabel="wavelength, m", ylabel="extinction, km2", title=f"The study's pyramid, {size['production']:.3g} m cell")
    ax.legend(fontsize=7)
    fig.savefig(out_dir / "reproduction_extinction.png", dpi=130, bbox_inches="tight", metadata=meta)
    plt.close(fig)

    for name, solver in (("R1", "fdtd"), ("R1", "dda"), ("R3", "fdtd")):
        r = collect(ledger, name, solver, size["production"])
        if r is None:
            continue
        at = int(np.argmax(r["extinction"]))
        y0, y1, z0, z1 = (float(v) for v in r["section_extent"])
        peak = float(np.percentile(r["section"][at], 99.5))
        fig, ax = plt.subplots(figsize=(6, 4))
        image = ax.imshow(r["section"][at].T, origin="lower", extent=(y0, y1, z0, z1), cmap="viridis", vmin=0, vmax=peak)
        fig.colorbar(image, label="|E|^2 / |E0|^2")
        ax.set(xlabel="y (north), m", ylabel="z, m", title=f"{name} ({solver}): axial section x = 0 at {r['wavelengths'][at]:.0f} m")
        stem = f"section_{name.lower()}_{solver}"
        fig.savefig(out_dir / f"{stem}.png", dpi=130, bbox_inches="tight", metadata=meta)
        plt.close(fig)
        (out_dir / f"{stem}.json").write_text(json.dumps(
            {"case": name, "solver": solver, "plane": "x = 0", "axes": ["y", "z"], "extent_m": [y0, y1, z0, z1],
             "wavelength_m": float(r["wavelengths"][at]), "quantity": "|E|^2 / |E0|^2", "colour_max": peak,
             "cell_m": size["production"]}, indent=2) + "\n")

    if summary["verdicts"]:                                    # the variants are drawn only once they may be read
        low, middle, high = cases.measured_conductivities(ledger)
        fig, ax = plt.subplots(figsize=(7, 4))
        table = cases.table(ledger)
        for eps in sorted({c.eps for n, c in table.items() if n.startswith("V1.R1")}):
            rows = sorted((c.sigma, band_max(r, "mean.kings")) for n, c in table.items() if n.startswith(f"V1.R1.eps{eps:g}.")
                          and (r := collect(ledger, n, "fdtd", size["production"])) is not None)
            ax.loglog(*zip(*rows), "o-", label=f"V1 free space, permittivity {eps:g}")
        for prefix, label in (("", "V4"), ("C0.", "V4's control cube")):
            rows = [(s, band_max(r, "mean.kings")) for s in (low, middle, high)
                    if (r := collect(ledger, f"{prefix}V4.sig{s:.1e}", "fdtd", size["production"])) is not None]
            ax.loglog(*zip(*rows), "s--", label=label)
        ax.axhline(metrics.FACTOR, color="k", lw=0.5)
        ax.set(xlabel="conductivity, S/m", ylabel="King's Chamber, band-maximum volume mean of |E|^2 / |E0|^2")
        ax.legend(fontsize=7)
        fig.savefig(out_dir / "kings_chamber_against_conductivity.png", dpi=130, bbox_inches="tight", metadata=meta)
        plt.close(fig)
        fig, ax = plt.subplots(figsize=(7, 4))
        for name, label in (("V3.pointed.ground", "pointed, 146.71 m"), ("V3.truncated.ground", "truncated, 137.4 m"), ("R3", "the study's, 138.75 m")):
            r = collect(ledger, name, "fdtd", size["production"])
            if r is not None:
                ax.plot(r["wavelengths"], r["mean.summit"], label=label)
        ax.set(xlabel="wavelength, m", ylabel="summit metric: volume mean of |E|^2 / |E0|^2", title="On ground, wave from above")
        ax.legend()
        fig.savefig(out_dir / "summit_metric.png", dpi=130, bbox_inches="tight", metadata=meta)
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(prog="python -m pyramid.em")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--seconds", type=float, default=np.inf)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--solver", choices=cases.SOLVERS)
    parser.add_argument("--cell", choices=("coarse", "production", "fine"))
    args = parser.parse_args()
    ledger, deadline = load(), time.time() + args.seconds
    CACHE.mkdir(parents=True, exist_ok=True)
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[name] = "1"                                 # the pool is the parallelism
    summary = None
    for stage in (("quick",) if args.quick else ("gates", "variants")):
        if stage == "variants" and not (summary["gates"] and all(g["passed"] for g in summary["gates"])):
            break
        todo = [t for t in plan(ledger, stage) if not path(t).exists()
                and (not args.case or any(t[0].startswith(c) for c in args.case))
                and args.solver in (None, t[1]) and (args.cell is None or t[2] == cells(ledger.q)[args.cell])]
        todo.sort(key=lambda t: (t[2], t[1] != "dda"))         # the small cells take longest: start them first
        if todo and not args.report:
            print(f"{stage}: {len(todo)} tasks", flush=True)
            with multiprocessing.get_context("spawn").Pool(min(10, args.workers, len(todo))) as pool:
                for task, finished, seconds in pool.imap_unordered(work, [(t, deadline) for t in todo]):
                    print(f"  {'done   ' if finished else 'paused '} {task[0]} {task[1]} {task[2]:.3g} m part {task[3]}  {seconds:.0f} s", flush=True)
        summary = evaluate(ledger)
        if any(not path(t).exists() for t in plan(ledger, stage)):
            break
    for gate in summary["gates"]:
        print(("PASS " if gate["passed"] else "FAIL ") + gate["gate"] + ": " + gate["numbers"])
    for claim, (status, basis) in summary["verdicts"].items():
        print(claim, status, "-", basis)
    for note in summary["notes"]:
        print(note)
    if not args.quick:
        out_dir = write_results("em", ledger, summary["results"], summary["verdicts"],
                                {"assumptions": ASSUMPTIONS, "gates": summary["gates"], "notes": summary["notes"],
                                 "cells_m": cells(ledger.q), "run_seconds": summary["runs"]})
        figures(ledger, summary, out_dir / "figures")


if __name__ == "__main__":
    main()
