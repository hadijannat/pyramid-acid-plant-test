"""python -m pyramid.em: run the cases in both solvers, apply the gates, and decide E19 and E20 if the gates allow.

  (no option)     compute what is missing of the gate cases and the variants, evaluate, write results/em/
  --certified     compute only the deciding runs that are missing (see below); exit 0 when all of them are cached
  --quick         B0 and R1 on the coarse grid only: a smoke check of both solvers
  --case NAME     only cases whose name starts with NAME (may be repeated)
  --seconds N     stop working after N seconds; finished tasks are cached, unfinished ones resume on the next call
  --workers N     parallel processes (at most 10, at most 8 with --certified; 1 runs the tasks in this process)
  --report        do not compute: evaluate what is cached
  --solver, --cell  only tasks of one solver (dda, fdtd) or one cell size (coarse, production, fine, benchmark)

Every finished task is a file in results/em/cache/, so a call only does what is missing. The gates come first
(benchmark, convergence, reproduction): the variants and controls are run only when they pass. If one fails the
summary carries the gates and the reproduction numbers and no verdict.

The two claims are decided on the runs at the cells where each solver's benchmark sphere is within 2 percent of
the exact one (runs.DECIDING). Those runs are long (the time-domain ones take a quarter of an hour to an hour
each), so they are computed only by --certified: one cache file per task, a line per finished task, safe to stop,
to kill and to call again (a task goes on from the state it last left). Until they are all cached the summary
names the missing ones and holds no verdict.
"""
import argparse
import json
import multiprocessing
import os
import sys
import time
from pathlib import Path

import numpy as np

from pyramid.em import cases, metrics, mie, runs
from pyramid.simkit import save_figure
from pyramid.ledger import load
from pyramid.simkit import write_results


def figures(ledger, summary: dict, out_dir: Path):
    """The spectra against Mie and against the study's peaks, and the axial section at the R1 maximum."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    q, size = ledger.q, runs.cells(ledger.q)
    out_dir.mkdir(parents=True, exist_ok=True)
    eps = q("paper.eps_real") + 1j * q("paper.eps_imag")
    fine_grid = np.arange(q("paper.wavelength_min"), q("paper.wavelength_max") + 0.5, 1.0)
    fig, (ax, below) = plt.subplots(2, 1, figsize=(7, 6.5), sharex=True)
    ax.plot(fine_grid, mie.cross_sections(q("emx.sphere_radius"), eps, fine_grid)[0] / 1e6, "k-", lw=1, label="Mie")
    for solver, marker in (("dda", "o"), ("fdtd", "s")):
        for cell in runs.SPHERE[solver]:                       # every cell the sphere was run at
            r = runs.collect(ledger, "B0", solver, size[cell])
            if r is None:
                continue
            decides = cell == runs.DECIDING[solver]
            label = f"{solver}, {size[cell]:.3g} m cell" + (" (the deciding runs' cell)" if decides else "")
            if decides:
                ax.plot(r["wavelengths"], r["extinction"] / 1e6, marker, ms=3, mfc="none", label=label)
            exact = mie.cross_sections(q("emx.sphere_radius"), eps, r["wavelengths"])[0]
            below.plot(r["wavelengths"], 100 * (r["extinction"] / exact - 1), marker + ("-" if decides else ":"), ms=2, lw=0.8,
                       label=label)
    for limit in (-metrics.BENCHMARK, metrics.BENCHMARK):
        below.axhline(100 * limit, color="k", lw=0.5)
    ax.set(ylabel="extinction, km2", title=f"B0: sphere of radius {q('emx.sphere_radius'):g} m, {eps.real:g} + {eps.imag:g}i")
    below.set(xlabel="wavelength, m", ylabel=f"deviation from Mie, percent (limit {metrics.BENCHMARK:.0%})")
    ax.legend(fontsize=7)
    below.legend(fontsize=6, ncol=2)
    save_figure(fig, out_dir / "b0_extinction.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    for name, solver, style in (("R1", "dda", "C0-"), ("R1", "fdtd", "C0--"), ("R2", "dda", "C1-"), ("R2", "fdtd", "C1--"), ("R3", "fdtd", "C2--")):
        r = runs.collect(ledger, name, solver, size["production"])
        if r is not None:
            ax.plot(r["wavelengths"], r["extinction"] / 1e6, style, label=f"{name}, {solver}")
    for key, marker in (("peak1", "v"), ("peak2", "v"), ("ground_peak", "^")):
        ax.plot(q(f"paper.{key}.wavelength"), q(f"paper.{key}.extinction") / 1e6, "k" + marker, ms=8)
    ax.plot([], [], "kv", label="study, free space (read from Fig. 1)")
    ax.plot([], [], "k^", label="study, on ground (read from Fig. 5b)")
    ax.set(xlabel="wavelength, m", ylabel="extinction, km2", title=f"The study's pyramid, {size['production']:.3g} m cell")
    ax.legend(fontsize=7)
    save_figure(fig, out_dir / "reproduction_extinction.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    for name, solver in (("R1", "fdtd"), ("R1", "dda"), ("R3", "fdtd")):
        r = runs.collect(ledger, name, solver, size["production"])
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
        save_figure(fig, out_dir / f"{stem}.png", dpi=130, bbox_inches="tight")
        plt.close(fig)
        (out_dir / f"{stem}.json").write_text(json.dumps(
            {"case": name, "solver": solver, "plane": "x = 0", "axes": ["y", "z"], "extent_m": [y0, y1, z0, z1],
             "wavelength_m": float(r["wavelengths"][at]), "quantity": "|E|^2 / |E0|^2", "colour_max": peak,
             "cell_m": size["production"]}, indent=2) + "\n")

    if summary["verdicts"]:                                    # the variants are drawn only once they may be read
        decides, compared = size[runs.DECIDING["fdtd"]], size[runs.COMPARED["fdtd"]]
        low, middle, high = cases.measured_conductivities(ledger)
        fig, ax = plt.subplots(figsize=(7, 4))
        table = cases.table(ledger)
        for eps in sorted({c.eps for n, c in table.items() if n.startswith("V1.R1")}):
            rows = sorted((c.sigma, runs.band_max(r, "mean.kings")) for n, c in table.items() if n.startswith(f"V1.R1.eps{eps:g}.")
                          and (r := runs.collect(ledger, n, "fdtd", size["production"])) is not None)
            ax.loglog(*zip(*rows), "o-", label=f"the study's pyramid in free space (V1), permittivity {eps:g}, "
                                                f"{size['production']:.3g} m cell: decides nothing")
        for prefix, label in (("", "the surveyed pyramid on ground (V4)"), ("C0.", "its control cube (C0)")):
            rows = [(s, runs.band_max(r, "mean.kings")) for s in (low, middle, high)
                    if (r := runs.collect(ledger, f"{prefix}V4.sig{s:.1e}", "fdtd", decides)) is not None]
            ax.loglog(*zip(*rows), "s--", label=f"{label}, {decides:.3g} m cell (decides)")
        ax.axhline(metrics.FACTOR, color="k", lw=0.5, label=f"the criterion's {metrics.FACTOR:g}")
        ax.axvspan(low, high, color="tab:green", alpha=0.15, label="masonry measured in place")
        ax.set(xlabel="conductivity of the masonry, S/m", ylabel="King's Chamber, band-maximum volume mean of |E|^2 / |E0|^2",
               title="E19: the intensity in the King's Chamber against the masonry's conductivity")
        ax.legend(fontsize=7)
        save_figure(fig, out_dir / "kings_chamber_against_conductivity.png", dpi=130, bbox_inches="tight")
        plt.close(fig)
        fig, ax = plt.subplots(figsize=(7, 4))
        apexes = (("V3.pointed.ground", f"pointed, {q('pyr.height_original'):.2f} m", "C0"),
                  ("V3.truncated.ground", f"truncated, {q('pyr.height_present'):.1f} m", "C1"),
                  ("R3", f"the study's, {q('paper.height'):g} m", "C2"))
        for name, label, colour in apexes:
            for cell, style in ((decides, "-"), (compared, ":")):
                r = runs.collect(ledger, name, "fdtd", cell)
                if r is not None:
                    ax.plot(r["wavelengths"], r["mean.summit"], colour + style, label=f"{label}, {cell:.3g} m cell")
        ax.set(xlabel="wavelength, m", ylabel="summit metric: volume mean of |E|^2 / |E0|^2",
               title=f"On ground, wave from above (solid: the deciding {decides:.3g} m cell)")
        ax.legend(fontsize=7)
        save_figure(fig, out_dir / "summit_metric.png", dpi=130, bbox_inches="tight")
        plt.close(fig)


def compute(todo: list, workers: int, deadline: float):
    """Run the tasks, yielding (task, finished, seconds) as each ends. One worker runs them in this process."""
    jobs = [(task, deadline) for task in todo]
    if workers == 1:
        yield from map(runs.work, jobs)
    else:
        with multiprocessing.get_context("spawn").Pool(workers) as pool:
            yield from pool.imap_unordered(runs.work, jobs)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m pyramid.em")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--certified", action="store_true")
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--seconds", type=float, default=np.inf)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--solver", choices=cases.SOLVERS)
    parser.add_argument("--cell", choices=("coarse", "production", "fine", "benchmark"))
    args = parser.parse_args(argv)
    ledger, deadline = load(), time.time() + args.seconds
    inputs = runs.stamp(ledger)                                # refuses a cache made for other ledger values
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[name] = "1"                                 # the pool is the parallelism

    def missing(stage: str, chosen: bool = True) -> list:
        """The tasks of a stage without a cache file; `chosen` narrows them to the options given."""
        return [t for t in runs.plan(ledger, stage) if not runs.path(t).exists() and (not chosen or (
            (not args.case or any(t[0].startswith(c) for c in args.case))
            and args.solver in (None, t[1]) and (args.cell is None or t[2] == runs.cells(ledger.q)[args.cell])))]

    def run(stage: str):
        todo = missing(stage)
        todo.sort(key=lambda t: (t[2], t[1] != "dda"))         # the small cells take longest: start them first
        if todo and not args.report:
            print(f"{stage}: {len(todo)} tasks", flush=True)
            limit = 8 if stage == "certified" else 10
            for n, (task, finished, seconds) in enumerate(compute(todo, max(1, min(limit, args.workers, len(todo))), deadline), 1):
                print(f"  [{n}/{len(todo)}] {'done   ' if finished else 'paused '} {task[0]} {task[1]} {task[2]:.3g} m part {task[3]}  "
                      f"{seconds:.0f} s", flush=True)

    if args.certified:                                         # the long runs, and nothing else
        # macOS keeps the freed blocks of a run's start-up arrays: a 1 m worker then holds 4 to 5.2 GB in place of
        # 1.5 to 1.6 GB (measured), at 8 workers more than this machine has. Without that cache a step takes about
        # 40 percent longer; MallocLargeCache=1 in the environment keeps it. The results do not depend on it.
        os.environ.setdefault("MallocLargeCache", "0")
        run("certified")
        left = missing("certified", chosen=False)
        print(f"certified: {len(left)} of {len(runs.plan(ledger, 'certified'))} tasks are not cached"
              + ("; call again to go on" if left else "; python -m pyramid.em now evaluates them"), flush=True)
        return 1 if left else 0
    summary = None
    for stage in (("quick",) if args.quick else ("gates", "variants")):
        if stage == "variants" and not (summary["gates"] and all(g["passed"] for g in summary["gates"])):
            break
        run(stage)
        summary = runs.evaluate(ledger)
        if missing(stage, chosen=False):
            break
    for gate in summary["gates"]:
        print(("PASS " if gate["passed"] else "FAIL ") + gate["gate"] + ": " + gate["numbers"])
    for claim, (status, basis) in summary["verdicts"].items():
        print(claim, status, "-", basis)
    for note in summary["notes"]:
        print(note)
    if not args.quick:
        if len(summary["verdicts"]) < len(runs.CLAIMS):        # a summary without a verdict would replace one that has it
            print("results/em is left as it is: a claim is undecided until its runs are cached", flush=True)
            return 1
        out_dir = write_results("em", ledger, summary["results"], summary["verdicts"],
                                {"assumptions": runs.ASSUMPTIONS, "gates": summary["gates"], "notes": summary["notes"],
                                 "cells_m": runs.cells(ledger.q), "run_seconds": summary["runs"], "cache_inputs": inputs})
        figures(ledger, summary, out_dir / "figures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
