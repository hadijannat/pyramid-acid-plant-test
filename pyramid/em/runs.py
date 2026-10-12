"""The tasks of the electromagnetic package: what to run, how one task runs, and what the cached runs say.

A task is (case, solver, cell, part): the dipole solver's wavelengths are split into runs of neighbours, and a
time-domain case with the study's constant imaginary permittivity takes three runs at three conductivities.
Every finished task is a file in results/em/cache/. This is a module of its own because a process pool cannot
find functions that live in a package's __main__.

Which runs decide (the controller's ruling of 2026-10-12 on the benchmark gate). The sphere is judged against Mie
for each solver at every cell a run of that solver uses (SPHERE). A verdict rests only on runs at a cell where
that solver's sphere is within 2 percent across the band: a third of the coarse cell for the dipole solver and a
fifth for the time-domain solver (DECIDING). The runs at the next coarser cell (COMPARED) are the resolution
check: they decide nothing, and a claim is conditional when they fall on the other side of its criterion. The
convergence and reproduction gates compare the pyramid's extinction between cells and with the study, and stay at
the coarse cell and its half, where the sphere is outside the limit: the ruling repeats the deciding runs only.
"""
import hashlib
import multiprocessing
import time
from pathlib import Path

import numpy as np

from pyramid.em import cases, dda, fdtd, keep, metrics, mie, shapes
from pyramid.ledger import LedgerError, load
from pyramid.screening import Result
from pyramid.simkit import RESULTS

CACHE = RESULTS / "em" / "cache"
CHUNKS = 9            # the dipole solver's wavelengths are split into this many runs of neighbours
GROUPS = 3            # time-domain runs per case with the study's constant imaginary permittivity
FLUX_LIMIT = 2.0      # below this cell size (m) a time-domain run of a pyramid keeps only the chamber and summit sums
CHECKPOINT = 240.0    # seconds between the states a time-domain run leaves behind: the most a killed run loses
SPHERE = {"dda": ("coarse", "production", "fine"), "fdtd": ("coarse", "production", "fine", "benchmark")}
DECIDING = {"dda": "fine", "fdtd": "benchmark"}       # the cell of each solver's deciding runs
COMPARED = {"dda": "production", "fdtd": "fine"}      # the next coarser cell: the resolution check
SOLVER = {"dda": "dipole", "fdtd": "time-domain"}
READS = ("paper.", "em.", "emx.", "pyr.", "kc.", "qc.", "gg.")    # every ledger id the package reads begins so


def stamp(ledger) -> str:
    """Tie the cache to the ledger lines the runs can read; a cache made for other values is refused, not reused.

    A task's file name carries its case, solver, cell and part and none of the values behind them, so without
    this an edited permittivity would be answered from the runs of the old one. Returns the digest.
    """
    lines = sorted((id, x.value, x.low, x.high) for id, x in ledger.quantities.items() if id.startswith(READS))
    digest, mark = hashlib.sha256(repr(lines).encode()).hexdigest(), CACHE / "inputs.sha256"
    CACHE.mkdir(parents=True, exist_ok=True)
    if not mark.exists():
        mark.write_text(digest + "\n")
    elif mark.read_text().strip() != digest:
        raise LedgerError(f"{CACHE} holds runs made for other ledger values (ids beginning {', '.join(READS)}): "
                          "move it aside and repeat `python -m pyramid.em --certified`")
    return digest

# The ledger ids behind the deciding numbers. The viewer shows a number under a claim when the claim depends on
# every id the number reads, so these are also what the claims' depends_on must hold.
STUDY = ("paper.height", "paper.base_side", "paper.eps_real", "paper.eps_imag", "paper.wavelength_min",
         "paper.wavelength_max", "emx.cell_coarse")
SURVEYED = ("pyr.base_side", "pyr.height_original", "pyr.height_present")
CHAMBERS = ("kc.west_wall.x", "kc.east_wall.x", "kc.south_wall.y", "kc.north_wall.y", "kc.floor.z", "kc.ceiling.z",
            "qc.west_wall.x", "qc.east_wall.x", "qc.north_wall.y", "qc.width_ns", "qc.floor.z", "qc.wall_height",
            "qc.ridge_height", "gg.south_end.x", "gg.south_end.y", "gg.south_end.z", "gg.north_end.x", "gg.north_end.y",
            "gg.north_end.z", "gg.width", "gg.roof_width", "gg.height", "emx.granite_shell", "em.granite_eps",
            "em.granite_conductivity")
E19_MODELLED = STUDY + ("paper.kc.centre.z",)
E19_REALISM = SURVEYED + CHAMBERS + ("em.limestone_resistivity", "em.limestone_eps", "paper.wavelength_min",
                                     "paper.wavelength_max", "emx.cell_coarse")
E20_SUMMIT = SURVEYED + ("emx.summit_depth", "emx.cell_coarse", "paper.eps_real", "paper.eps_imag",
                         "paper.wavelength_min", "paper.wavelength_max")

ASSUMPTIONS = [
    "The wave travels along the axis and is polarised east-west; field ratios are over the incident intensity, also on ground.",
    "Chambers are air; the study's chambers are read as pyramid.geometry reads them (length east-west, offset to the south).",
    "A cell cut by a surface answers along the surface with its mean permittivity and across it with its mean inverse permittivity.",
    "A time-domain run has one conductivity; the study's constant imaginary permittivity is interpolated from three runs.",
    "Extinction in the time-domain solver is scattered power through a closed box plus power absorbed in the body; on ground the body is what stands above z = 0.",
    "The ground is the masonry's material; V2 keeps the study's outer pyramid; the V3 apexes are the surveyed pyramid whole and cut at the present top, with the study's chambers.",
    "V4 is the truncated surveyed pyramid with the surveyed King's and Queen's Chambers and Grand Gallery, a granite shell of emx.granite_shell, permittivity em.limestone_eps.",
    "The band maximum of a metric is its largest value on the 5 m wavelength grid.",
    "A verdict rests only on runs at a cell where that solver's benchmark sphere is within 2 percent of the exact one across the band; the next coarser cell is the resolution check and a claim is conditional when it falls on the other side.",
    "Where both solvers decide a part (R1 against its control) and fall on different sides, the part is conditional.",
    "The convergence and reproduction gates compare the pyramid's extinction at the coarse cell and its half, where the sphere is outside the benchmark limit; only the deciding runs were repeated at the finer cells.",
]


def cells(q) -> dict:
    coarse = q("emx.cell_coarse")
    return {"coarse": coarse, "production": coarse / 2, "fine": coarse / 3, "benchmark": coarse / 5}


def path(task) -> Path:
    name, solver, cell, part = task
    return CACHE / f"{name}_{solver}_{cell:.4f}_{part}.npz"


def parts(case, solver) -> int:
    return CHUNKS if solver == "dda" else GROUPS if case.eps_imag is not None else 1


def deciding(ledger) -> dict:
    """The cases E19 and E20 are decided on, per solver: each is run at that solver's deciding cell."""
    low, middle, high = cases.measured_conductivities(ledger)
    v4 = [f"{prefix}V4.sig{sigma:.1e}" for sigma in (low, middle, high) for prefix in ("", "C0.")]
    v4 += [f"V4.eps{eps:g}.sig{low:.1e}" for eps in ledger.rng("em.limestone_eps")]
    return {"dda": ["R1", "C0.R1"], "fdtd": ["R1", "C0.R1", "V3.truncated.ground", "V3.pointed.ground"] + v4}


def plan(ledger, stage: str) -> list[tuple]:
    """The tasks of a stage: (case, solver, cell, part)."""
    size, table = cells(ledger.q), cases.table(ledger)
    want = []
    if stage == "quick":
        want = [("B0", s, size["coarse"]) for s in cases.SOLVERS] + [("R1", s, size["coarse"]) for s in cases.SOLVERS]
    elif stage == "certified":         # the deciding runs, and the sphere at the cell the time-domain ones are compared with
        want += [(name, solver, size[DECIDING[solver]]) for solver, names in deciding(ledger).items() for name in names]
        want += [("B0", "fdtd", size["fine"])]
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
    """Run one task to its cache file (module level: the pool pickles it). Returns (task, finished, seconds).

    Safe to stop and to kill: the cache file appears whole or not at all, a time-domain run leaves its state every
    CHECKPOINT seconds and a dipole run after every wavelength, and the next call goes on from there. A task that
    finds the clock past its deadline does not start, and one whose calling process has died stops at its next state.
    """
    task, deadline = job
    name, solver, cell, part = task
    began, target = time.time(), path(task)
    if began > deadline or target.exists():
        return task, target.exists(), 0.0
    state, clock, caller = target.with_suffix(".state.npz"), target.with_suffix(".time.npy"), multiprocessing.parent_process()
    before = float(np.load(clock)) if clock.exists() else 0.0     # what earlier calls spent on this task

    def saved():                                                  # a state was written: keep the time spent beside it
        keep(clock, lambda handle: np.save(handle, before + time.time() - began))
        if caller is not None and not caller.is_alive():          # an orphaned worker would double the next call's load
            raise SystemExit(f"{target.name}: the calling process is gone")

    ledger = load()
    q, case = ledger.q, cases.table(ledger)[name]
    wavelengths, model = cases.wavelengths(q), shapes.build(case, q, cell)
    if solver == "dda":
        chunk = np.array_split(wavelengths, CHUNKS)[part]

        def permittivity(w):
            masonry = case.eps + 1j * (case.eps_imag if case.eps_imag is not None else cases.loss(case.sigma, w, q))
            return masonry, q("em.granite_eps") + 1j * cases.loss(q("em.granite_conductivity"), w, q)

        out = dda.spectrum(model, chunk, permittivity, case.direction,
                           np.complex64 if cell < FLUX_LIMIT else np.complex128, state, deadline, saved)
    else:
        if case.eps_imag is not None:
            low, high = wavelengths.min(), wavelengths.max()
            sigma = cases.conductivity(case.eps_imag, (low, np.sqrt(low * high), high)[part], q)
        else:
            sigma = case.sigma
        out = fdtd.run(model, case, q, wavelengths, sigma, state, deadline - time.time(),
                       flux=cell >= FLUX_LIMIT or case.body == "sphere",       # the benchmark is all cross-sections
                       every=CHECKPOINT, saved=saved)
        if out is not None:
            out["sigma"] = np.array(sigma)
    if out is not None:
        out["seconds"] = np.array(before + time.time() - began)
        keep(target, lambda handle: np.savez(handle, **out))
        clock.unlink(missing_ok=True)
    else:
        keep(clock, lambda handle: np.save(handle, before + time.time() - began))
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
    q, size = ledger.q, cells(ledger.q)
    got = lambda name, solver, cell: collect(ledger, name, solver, size[cell])        # noqa: E731
    wavelengths = cases.wavelengths(q)
    exact = mie.cross_sections(q("emx.sphere_radius"), q("paper.eps_real") + 1j * q("paper.eps_imag"), wavelengths)[0]
    results, gates, notes, runs = {}, [], [], {}

    def add(id, label, value, low, high, unit, formula, inputs):
        results[id] = Result(f"em.{id}", label, float(value), float(min(low, value)), float(max(high, value)), unit, formula, inputs)

    study = STUDY[2:]
    # --- benchmark: the sphere at every cell a run of each solver uses ---
    rows, unjudged = [], []
    fine_grid = np.arange(wavelengths.min(), wavelengths.max() + 0.5, 1.0)
    sphere = mie.cross_sections(q("emx.sphere_radius"), q("paper.eps_real") + 1j * q("paper.eps_imag"), fine_grid)[0]
    slope = np.gradient(np.log(sphere), np.log(fine_grid))             # how steep the exact spectrum is
    wanted = [(solver, cell) for solver, sizes in SPHERE.items() for cell in sizes]
    for solver, cell in wanted:
        r = got("B0", solver, cell)
        if r is None:
            unjudged.append(lacking(ledger, "B0", solver, size[cell]))
            continue
        runs[f"B0 {solver} {size[cell]:.3g} m"] = r["seconds"]
        row = metrics.sphere_row(solver, size[cell], r["wavelengths"], r["extinction"],
                                 np.interp(r["wavelengths"], wavelengths, exact), np.interp(r["wavelengths"], fine_grid, slope))
        rows.append(row)
        add(f"b0_deviation_{solver}_{size[cell]:.3g}".replace(".", "p"),
            f"B0: worst deviation of the {solver} extinction from Mie at a {size[cell]:.3g} m cell", row["worst"], 0, row["worst"],
            "1", "max |sigma_ext / Mie - 1| over the band", study + ("emx.sphere_radius",))
    gates.append(metrics.benchmark_gate(rows, [(s, size[c]) for s, c in wanted], {s: size[c] for s, c in DECIDING.items()}))

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
        finer = got("R1", "dda", DECIDING["dda"])              # the same maxima at the dipole solver's deciding cell, for
        for n, (at, value) in enumerate([] if finer is None else metrics.peaks(finer["wavelengths"], finer["extinction"]), 1):
            tag = f"dda_{size[DECIDING['dda']]:.3g}".replace(".", "p")      # information: the gates stay at the cells above
            add(f"r1_peak{n}_wavelength_{tag}", f"R1: extinction maximum {n} (dda, {size[DECIDING['dda']]:.3g} m cell), wavelength",
                at, at, at, "m", "local maximum of the extinction spectrum", geometry)
            add(f"r1_peak{n}_extinction_{tag}", f"R1: extinction maximum {n} (dda, {size[DECIDING['dda']]:.3g} m cell)", value, value,
                value, "m2", "extinction cross-section at that maximum", geometry)
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
        verdicts, missing = decide(ledger, got, add, unjudged)
        notes += missing
    return {"results": results, "gates": gates, "verdicts": verdicts, "notes": notes, "runs": runs}


def lacking(ledger, name: str, solver: str, cell: float) -> str:
    """How the notes name a case whose runs are not all cached."""
    count = parts(cases.table(ledger)[name], solver)
    gone = sum(not path((name, solver, cell, part)).exists() for part in range(count))
    return f"{name} {solver} {cell:.3g} m ({gone} of {count} parts)"


def unswept(ledger) -> str:
    """The ranges the E19 runs did not carry, as a sentence for the basis."""
    q, rng = ledger.q, ledger.rng
    low, band = cases.measured_conductivities(ledger)[0], cases.wavelengths(q)
    skin = band / (2 * np.pi * np.sqrt(q("em.limestone_eps") + 1j * cases.loss(low, band, q)).imag)   # the field falls to 1/e
    return (f" Not varied: as modelled is evaluated at the study's permittivity of {q('paper.eps_real'):g} (its range is "
            f"{rng('paper.eps_real')[0]:g} to {rng('paper.eps_real')[1]:g}); V4 has a granite shell of {q('emx.granite_shell'):g} m "
            f"(range {rng('emx.granite_shell')[0]:g} to {rng('emx.granite_shell')[1]:g} m), a granite permittivity of "
            f"{q('em.granite_eps'):g} ({rng('em.granite_eps')[0]:g} to {rng('em.granite_eps')[1]:g}) and a granite conductivity of "
            f"{q('em.granite_conductivity'):.0e} S/m (up to {rng('em.granite_conductivity')[1]:.0e}); the shell is metres thick "
            f"against a skin depth of {skin.min():.0f} to {skin.max():.0f} m in the masonry at {low:.1e} S/m.")


def decide(ledger, got, add, unjudged):
    """E19 and E20 from the deciding runs and the cell they are compared with, once the gates have passed.

    Every row is also a number in the results, with its role in the label: the runs at the deciding cell, the next
    coarser cell (the resolution check), and for the time-domain solver the cell above that, for information.
    """
    q, size = ledger.q, cells(ledger.q)
    low, middle, high = cases.measured_conductivities(ledger)
    kings = lambda r: band_max(r, "mean.kings")                                      # noqa: E731
    missing = {"E19": list(unjudged), "E20": list(unjudged)}
    said = {True: "decides", False: "resolution check, decides nothing", None: "for information, decides nothing"}

    def need(claim, name, solver, cell, role):
        r = got(name, solver, cell)
        if r is None and role is not None:                    # a run for information is not waited for
            missing[claim].append(lacking(ledger, name, solver, size[cell]))
        return r

    modelled, realism, summit = [], [], []
    for solver in cases.SOLVERS[::-1]:                        # the time-domain solver first: it decides both parts
        for cell in SPHERE[solver][:0:-1]:                    # finest first; the coarse cell has no variant runs
            role = True if cell == DECIDING[solver] else False if cell == COMPARED[solver] else None
            where, tag = f"the {SOLVER[solver]} solver at a {size[cell]:.3g} m cell", f"{solver}_{size[cell]:.3g}".replace(".", "p")
            label = f"{SOLVER[solver]} solver, {size[cell]:.3g} m cell ({said[role]})"
            r1, c0 = need("E19", "R1", solver, cell, role), need("E19", "C0.R1", solver, cell, role)
            if r1 is not None and c0 is not None:
                ratio = kings(r1) / kings(c0)
                add(f"e19_r1_over_control_{tag}", f"R1 over its control, King's Chamber volume mean, {label}", ratio, ratio, ratio,
                    "1", "band maximum in R1 over band maximum in the cube", E19_MODELLED)
                if role is not None:
                    modelled.append((where, kings(r1), kings(c0), role))
            if solver != "fdtd":                              # the cases with ground belong to the time-domain solver
                continue
            rows = []
            for sigma in ((low, high) if role is False else (low, middle, high)):
                v4, c0 = need("E19", f"V4.sig{sigma:.1e}", solver, cell, role), need("E19", f"C0.V4.sig{sigma:.1e}", solver, cell, role)
                if v4 is not None and c0 is not None:
                    rows.append(("", sigma, kings(v4), kings(c0)))
            for eps in (() if role is False else ledger.rng("em.limestone_eps")):
                v4 = need("E19", f"V4.eps{eps:g}.sig{low:.1e}", solver, cell, role)
                if v4 is not None:
                    rows.append((f"permittivity {eps:g}", low, kings(v4), None))
            own_eps = f"eps{q('em.limestone_eps'):g}"
            for name, sigma, v4, _ in rows:
                add(f"e19_v4_{name.replace(' ', '_') or own_eps}_{sigma:.1e}_{tag}".replace(".", "p").replace("-", "m"),
                    f"V4 King's Chamber volume mean at {sigma:.1e} S/m {name}, {label}", v4, v4, v4, "1",
                    "band maximum of the volume mean of |E|^2 / |E0|^2", E19_REALISM)
            if role is not None:
                realism.append((where, rows, role))
            cut, whole = need("E20", "V3.truncated.ground", solver, cell, role), need("E20", "V3.pointed.ground", solver, cell, role)
            own = got("R3", solver, cell)                     # the study's own apex, for reference where it was run
            if cut is not None and whole is not None:
                cut, whole = band_max(cut, "mean.summit"), band_max(whole, "mean.summit")
                add(f"e20_summit_ratio_{tag}", f"Summit metric, truncated over pointed apex, on ground, {label}", cut / whole,
                    cut / whole, cut / whole, "1", "band maximum for the apex cut at the present top over the pointed apex", E20_SUMMIT)
                if role is not None:
                    summit.append((where, cut, whole, None if own is None else band_max(own, "mean.summit"), role))
    verdicts, notes = {}, []
    for claim, rule in (("E19", lambda: metrics.e19(modelled, realism, unswept(ledger))), ("E20", lambda: metrics.e20(summit))):
        if missing[claim]:
            notes.append(f"{claim} is undecided: these runs are not cached: " + ", ".join(dict.fromkeys(missing[claim]))
                         + ". They are computed by python -m pyramid.em --certified.")
        else:
            verdicts[claim] = rule()
    return verdicts, notes
