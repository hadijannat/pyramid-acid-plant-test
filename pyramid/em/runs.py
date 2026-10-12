"""The tasks of the electromagnetic package: what to run, how one task runs, and what the cached runs say.

A task is (case, solver, cell, part): the dipole solver's wavelengths are split into runs of neighbours, and a
time-domain case with the study's constant imaginary permittivity takes three runs at three conductivities.
Every finished task is a file in results/em/cache/. This is a module of its own because a process pool cannot
find functions that live in a package's __main__.
"""
import time
from pathlib import Path

import numpy as np

from pyramid.em import cases, dda, fdtd, metrics, mie, shapes
from pyramid.ledger import load
from pyramid.screening import Result
from pyramid.simkit import RESULTS

CACHE = RESULTS / "em" / "cache"
CHUNKS = 9            # the dipole solver's wavelengths are split into this many runs of neighbours
GROUPS = 3            # time-domain runs per case with the study's constant imaginary permittivity
FLUX_LIMIT = 2.0      # below this cell size (m) a time-domain run of a pyramid keeps only the chamber and summit sums

ASSUMPTIONS = [
    "The wave travels along the axis and is polarised east-west; field ratios are over the incident intensity, also on ground.",
    "Chambers are air; the study's chambers are read as pyramid.geometry reads them (length east-west, offset to the south).",
    "A cell cut by a surface answers along the surface with its mean permittivity and across it with its mean inverse permittivity.",
    "A time-domain run has one conductivity; the study's constant imaginary permittivity is interpolated from three runs.",
    "Extinction in the time-domain solver is scattered power through a closed box plus power absorbed in the body; on ground the body is what stands above z = 0.",
    "The ground is the masonry's material; V2 keeps the study's outer pyramid; the V3 apexes are the surveyed pyramid whole and cut at the present top, with the study's chambers.",
    "V4 is the truncated surveyed pyramid with the surveyed King's and Queen's Chambers and Grand Gallery, a granite shell of emx.granite_shell, permittivity em.limestone_eps.",
    "The band maximum of a metric is its largest value on the 5 m wavelength grid.",
]


def cells(q) -> dict:
    coarse = q("emx.cell_coarse")
    return {"coarse": coarse, "production": coarse / 2, "fine": coarse / 3, "benchmark": coarse / 5}


def path(task) -> Path:
    name, solver, cell, part = task
    return CACHE / f"{name}_{solver}_{cell:.4f}_{part}.npz"


def parts(case, solver) -> int:
    return CHUNKS if solver == "dda" else GROUPS if case.eps_imag is not None else 1


def plan(ledger, stage: str) -> list[tuple]:
    """The tasks of a stage: (case, solver, cell, part)."""
    size, table = cells(ledger.q), cases.table(ledger)
    want = []
    if stage == "quick":
        want = [("B0", s, size["coarse"]) for s in cases.SOLVERS] + [("R1", s, size["coarse"]) for s in cases.SOLVERS]
    elif stage == "gates":
        want += [("B0", "dda", size[c]) for c in ("coarse", "production", "fine")]
        want += [("B0", "fdtd", size[c]) for c in ("coarse", "production", "benchmark")]
        want += [("R1", s, size[c]) for s in cases.SOLVERS for c in ("coarse", "production")]
        want += [("R2", s, size["production"]) for s in cases.SOLVERS] + [("R3", "fdtd", size["production"])]
    else:
        done = {"B0", "R1", "R2", "R3"}
        want += [(name, "fdtd", size["production"]) for name in table if name not in done]
        want += [(name, "dda", size["production"]) for name in ("C0.R1",)]
        low, _, high = cases.measured_conductivities(ledger)
        fine = ["R1", "C0.R1", "V3.truncated.ground", "V3.pointed.ground", "R3"]
        fine += [f"{prefix}V4.sig{sigma:.1e}" for sigma in (low, high) for prefix in ("", "C0.")]
        want += [(name, "fdtd", size["fine"]) for name in fine]
    return [(name, solver, cell, part) for name, solver, cell in want for part in range(parts(table[name], solver))]


def work(job) -> tuple:
    """Run one task to its cache file (module level: the pool pickles it). Returns (task, finished, seconds)."""
    task, deadline = job
    name, solver, cell, part = task
    began, ledger = time.time(), load()
    q, case = ledger.q, cases.table(ledger)[name]
    wavelengths, model = cases.wavelengths(q), shapes.build(case, q, cell)
    target, state = path(task), path(task).with_suffix(".state.npz")
    if solver == "dda":
        chunk = np.array_split(wavelengths, CHUNKS)[part]

        def permittivity(w):
            masonry = case.eps + 1j * (case.eps_imag if case.eps_imag is not None else cases.loss(case.sigma, w, q))
            return masonry, q("em.granite_eps") + 1j * cases.loss(q("em.granite_conductivity"), w, q)

        out = dda.spectrum(model, chunk, permittivity, case.direction,
                           np.complex64 if cell < FLUX_LIMIT else np.complex128, state, deadline)
    else:
        if case.eps_imag is not None:
            low, high = wavelengths.min(), wavelengths.max()
            sigma = cases.conductivity(case.eps_imag, (low, np.sqrt(low * high), high)[part], q)
        else:
            sigma = case.sigma
        out = fdtd.run(model, case, q, wavelengths, sigma, state, deadline - time.time(),
                       flux=cell >= FLUX_LIMIT or case.body == "sphere")       # the benchmark is all cross-sections
        if out is not None:
            out["sigma"] = np.array(sigma)
    if out is not None:
        out["seconds"] = np.array(time.time() - began + (float(np.load(target.with_suffix(".time.npy"))) if target.with_suffix(".time.npy").exists() else 0.0))
        target.with_suffix(".time.npy").unlink(missing_ok=True)
        np.savez(target, **out)
    else:
        spent = time.time() - began + (float(np.load(target.with_suffix(".time.npy"))) if target.with_suffix(".time.npy").exists() else 0.0)
        np.save(target.with_suffix(".time.npy"), spent)
    return task, out is not None, time.time() - began


def collect(ledger, name: str, solver: str, cell: float) -> dict | None:
    """A case's arrays over its wavelengths from its cached parts, or None if a part is missing."""
    case = cases.table(ledger)[name]
    files = [path((name, solver, cell, part)) for part in range(parts(case, solver))]
    if not all(f.exists() for f in files):
        return None
    loaded = [dict(np.load(f)) for f in files]
    seconds = float(sum(part["seconds"] for part in loaded))
    skip = {"wavelengths", "seconds", "steps", "sigma", "section_extent", "products"}
    if solver == "dda":
        out = {key: np.concatenate([part[key] for part in loaded]) for key in loaded[0] if key not in skip - {"wavelengths"}}
    elif case.eps_imag is None:
        out = {key: value for key, value in loaded[0].items() if key not in skip - {"wavelengths"}}
    else:                                                      # three conductivities to one imaginary permittivity
        out = {"wavelengths": loaded[0]["wavelengths"]}
        losses = np.array([cases.loss(float(part["sigma"]), out["wavelengths"], ledger.q) for part in loaded])
        for key in loaded[0]:
            if key not in skip:
                out[key] = metrics.interpolate_loss([part[key] for part in loaded], losses, case.eps_imag)
    out["section_extent"], out["seconds"] = loaded[0]["section_extent"], seconds
    return out


def band_max(result: dict, key: str) -> float:
    return float(np.max(result[key]))


def evaluate(ledger) -> dict:
    """Gates, numbers and verdicts from what is cached."""
    q, size, table = ledger.q, cells(ledger.q), cases.table(ledger)
    got = lambda name, solver, cell: collect(ledger, name, solver, size[cell])        # noqa: E731
    wavelengths = cases.wavelengths(q)
    exact = mie.cross_sections(q("emx.sphere_radius"), q("paper.eps_real") + 1j * q("paper.eps_imag"), wavelengths)[0]
    results, gates, notes, runs = {}, [], [], {}

    def add(id, label, value, low, high, unit, formula, inputs):
        results[id] = Result(f"em.{id}", label, float(value), float(min(low, value)), float(max(high, value)), unit, formula, inputs)

    study = ("paper.eps_real", "paper.eps_imag", "paper.wavelength_min", "paper.wavelength_max", "emx.cell_coarse")
    # --- benchmark ---
    b0, table_b0 = {}, []
    fine_grid = np.arange(wavelengths.min(), wavelengths.max() + 0.5, 1.0)
    sphere = mie.cross_sections(q("emx.sphere_radius"), q("paper.eps_real") + 1j * q("paper.eps_imag"), fine_grid)[0]
    slope = np.gradient(np.log(sphere), np.log(fine_grid))             # how steep the exact spectrum is
    for solver, sizes in (("dda", ("coarse", "production", "fine")), ("fdtd", ("coarse", "production", "benchmark"))):
        for cell in sizes:
            r = got("B0", solver, cell)
            if r is None:
                continue
            runs[f"B0 {solver} {size[cell]:.3g} m"] = r["seconds"]
            deviation = r["extinction"] / np.interp(r["wavelengths"], wavelengths, exact) - 1
            worst = int(np.argmax(np.abs(deviation)))
            steep = abs(float(np.interp(r["wavelengths"][worst], fine_grid, slope)))
            table_b0.append(f"{solver} at {size[cell]:.3g} m: worst {deviation[worst]:+.2%} at {r['wavelengths'][worst]:.0f} m "
                            f"(the exact spectrum changes {steep:.0f} percent per percent of wavelength there), "
                            f"rms {np.sqrt(np.mean(deviation**2)):.2%}, {np.mean(np.abs(deviation) <= metrics.BENCHMARK):.0%} of the "
                            f"wavelengths within the limit")
            b0[solver] = (r, deviation, size[cell])            # the finest cell run of each solver stands for it
    if set(b0) == set(cases.SOLVERS):
        gate = metrics.benchmark_gate(np.ones(1), {s: 1 + np.max(np.abs(d)) for s, (_, d, _) in b0.items()})
        gate["numbers"] = "; ".join(table_b0) + f" (limit {metrics.BENCHMARK:.0%}, judged at each solver's finest cell)"
        gates.append(gate)
        for solver, (_, deviation, cell) in b0.items():
            add(f"b0_deviation_{solver}", f"B0: worst deviation of the {solver} extinction from Mie", np.max(np.abs(deviation)),
                0, np.max(np.abs(deviation)), "1", f"max |sigma_ext / Mie - 1| over the band, cell {cell:.3g} m", study + ("emx.sphere_radius",))
    else:
        gates.append({"gate": "benchmark: B0 against Mie", "passed": False, "numbers": "not computed: " + "; ".join(table_b0)})

    # --- convergence and reproduction ---
    r1 = {(solver, cell): got("R1", solver, cell) for solver in cases.SOLVERS for cell in ("coarse", "production")}
    r2 = {solver: got("R2", solver, "production") for solver in cases.SOLVERS}
    r3 = got("R3", "fdtd", "production")
    ready = all(v is not None for v in r1.values()) and all(v is not None for v in r2.values()) and r3 is not None
    targets = {"peak1": (q("paper.peak1.wavelength"), q("paper.peak1.extinction")),
               "peak2": (q("paper.peak2.wavelength"), q("paper.peak2.extinction")),
               "ground": (q("paper.ground_peak.wavelength"), q("paper.ground_peak.extinction"))}
    if ready:
        peak = {key: metrics.band_maximum(r["wavelengths"], r["extinction"]) for key, r in r1.items()}
        gates.append(metrics.convergence_gate({s: (peak[(s, "coarse")][1], peak[(s, "production")][1]) for s in cases.SOLVERS}))
        free = {s: metrics.peaks(r1[(s, "production")]["wavelengths"], r1[(s, "production")]["extinction"]) for s in cases.SOLVERS}
        agreement = {"R1": metrics.nrmsd(r1[("dda", "production")]["extinction"], r1[("fdtd", "production")]["extinction"]),
                     "R2": metrics.nrmsd(r2["dda"]["extinction"], r2["fdtd"]["extinction"])}
        if got("B0", "dda", "production") is not None and got("B0", "fdtd", "production") is not None:
            agreement["B0"] = metrics.nrmsd(got("B0", "dda", "production")["extinction"], got("B0", "fdtd", "production")["extinction"])
        ground = metrics.band_maximum(r3["wavelengths"], r3["extinction"])
        gates += metrics.reproduction_gate(free, ground, targets, agreement)
        geometry = ("paper.height", "paper.base_side") + study
        for solver in cases.SOLVERS:
            for n, (at, value) in enumerate(free[solver], 1):
                add(f"r1_peak{n}_wavelength_{solver}", f"R1: extinction maximum {n} ({solver}), wavelength", at, at, at, "m",
                    "local maximum of the extinction spectrum", geometry)
                add(f"r1_peak{n}_extinction_{solver}", f"R1: extinction maximum {n} ({solver})", value, value, value, "m2",
                    "extinction cross-section at that maximum", geometry)
            other = metrics.band_maximum(r2[solver]["wavelengths"], r2[solver]["extinction"])[1]
            add(f"r2_peak_extinction_{solver}", f"R2: band maximum of the extinction ({solver})", other, other, other, "m2",
                "largest extinction cross-section in the band, wave from the base side", geometry)
            for chamber in ("kings", "queens"):
                for case_name, r in (("r1", r1[(solver, "production")]), ("r2", r2[solver])):
                    add(f"{case_name}_{chamber}_mean_{solver}", f"{case_name.upper()}: band-maximum volume-mean intensity ratio, {chamber} ({solver})",
                        band_max(r, f"mean.{chamber}"), band_max(r, f"mean.{chamber}"), band_max(r, f"mean.{chamber}"), "1",
                        "max over the band of the volume mean of |E|^2 / |E0|^2", geometry + ("paper.kc.centre.z",))
                    add(f"{case_name}_{chamber}_max_{solver}", f"{case_name.upper()}: band-maximum peak intensity ratio, {chamber} ({solver})",
                        band_max(r, f"max.{chamber}"), band_max(r, f"max.{chamber}"), band_max(r, f"max.{chamber}"), "1",
                        "max over the band and the chamber of |E|^2 / |E0|^2", geometry + ("paper.kc.centre.z",))
        add("r3_peak_wavelength", "R3: wavelength of the on-ground extinction maximum (fdtd)", ground[0], ground[0], ground[0], "m",
            "largest scattered plus absorbed power over incident intensity", geometry)
        add("r3_peak_extinction", "R3: on-ground extinction maximum (fdtd)", ground[1], ground[1], ground[1], "m2",
            "largest scattered plus absorbed power over incident intensity", geometry)
        for key, r in list(r1.items()) + [((s, "R2"), v) for s, v in r2.items()] + [(("fdtd", "R3"), r3)]:
            runs[f"{'R1' if key[1] in size else key[1]} {key[0]} {size.get(key[1], size['production']):.3g} m"] = r["seconds"]
    else:
        gates.append({"gate": "convergence and reproduction", "passed": False, "numbers": "not computed"})

    # --- gates in order: the first failure stops the interpretation ---
    for i, gate in enumerate(gates):
        if not gate["passed"]:
            for later in gates[i + 1:]:
                later["numbers"] = "not judged, an earlier gate failed; for information: " + later["numbers"]
                later["passed"] = False
            notes.append(f"Stopped at the gate '{gate['gate']}': no variant is interpreted and E19 and E20 stay undecided.")
            break
    verdicts = {}
    if all(g["passed"] for g in gates):
        verdicts, missing = decide(ledger, got, add, runs)
        notes += missing
    return {"results": results, "gates": gates, "verdicts": verdicts, "notes": notes, "runs": runs}


def decide(ledger, got, add, runs):
    """E19 and E20 from the variant runs, once the gates have passed."""
    low, middle, high = cases.measured_conductivities(ledger)
    size = cells(ledger.q)
    need = lambda name, cell: got(name, "fdtd", cell)                              # noqa: E731
    kings = lambda r: band_max(r, "mean.kings")                                      # noqa: E731
    modelled, realism, summit, missing = [], [], [], []
    for cell in ("production", "fine"):
        r1, c0 = need("R1", cell), need("C0.R1", cell)
        if r1 is not None and c0 is not None:
            modelled.append((size[cell], kings(r1), kings(c0)))
        rows = []
        for sigma in ((low, middle, high) if cell == "production" else (low, high)):
            v4, c0 = need(f"V4.sig{sigma:.1e}", cell), need(f"C0.V4.sig{sigma:.1e}", cell)
            if v4 is not None and c0 is not None:
                rows.append(("", sigma, kings(v4), kings(c0)))
        if cell == "production":
            for eps in ledger.rng("em.limestone_eps"):
                v4 = need(f"V4.eps{eps:g}.sig{low:.1e}", cell)
                if v4 is not None:
                    rows.append((f"permittivity {eps:g}", low, kings(v4), None))
        if rows:
            realism.append((size[cell], rows))
        cut, whole, own = need("V3.truncated.ground", cell), need("V3.pointed.ground", cell), need("R3", cell)
        if cut is not None and whole is not None and own is not None:
            summit.append((size[cell], band_max(cut, "mean.summit"), band_max(whole, "mean.summit"), band_max(own, "mean.summit")))
    verdicts = {}
    if len(modelled) == 2 and len(realism) == 2 and len(realism[0][1]) == 5 and len(realism[1][1]) == 2:
        verdicts["E19"] = metrics.e19(modelled, realism)
        for cell, r1, c0 in modelled:
            add(f"e19_r1_over_control_{cell:.3g}".replace(".", "p"), f"R1 over its control, King's Chamber volume mean, {cell:.3g} m cell",
                r1 / c0, r1 / c0, r1 / c0, "1", "band maximum in R1 over band maximum in the cube", ("paper.kc.centre.z", "emx.cell_coarse"))
        for cell, rows in realism:
            for label, sigma, v4, c0 in rows:
                add(f"e19_v4_{label.replace(' ', '_') or 'eps7'}_{sigma:.1e}_{cell:.3g}".replace(".", "p").replace("-", "m"),
                    f"V4 King's Chamber volume mean at {sigma:.1e} S/m {label}, {cell:.3g} m cell", v4, v4, v4, "1",
                    "band maximum of the volume mean of |E|^2 / |E0|^2", ("em.limestone_resistivity", "em.limestone_eps", "emx.granite_shell"))
    else:
        missing.append("E19 is undecided: its runs are not all cached.")
    if len(summit) == 2:
        verdicts["E20"] = metrics.e20(summit)
        for cell, cut, whole, own in summit:
            add(f"e20_summit_ratio_{cell:.3g}".replace(".", "p"), f"Summit metric, truncated over pointed apex, on ground, {cell:.3g} m cell",
                cut / whole, cut / whole, cut / whole, "1", "band maximum for the apex cut at the present top over the pointed apex",
                ("pyr.height_present", "pyr.height_original", "pyr.base_side", "emx.summit_depth"))
    else:
        missing.append("E20 is undecided: its runs are not all cached.")
    return verdicts, missing
