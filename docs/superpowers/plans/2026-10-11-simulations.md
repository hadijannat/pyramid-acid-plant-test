# Simulations Implementation Plan: deciding the 49 pending claims

> **For agentic workers:** this plan is executed by a Workflow: one implementer per package in its own git worktree, an adversarial review, one fix pass and a scoped re-review, then a merge by the controller. Each task below is a complete brief.

**Goal:** Give every one of the 49 claims that Tier 0 left `pending` a verdict that follows from its committed criterion: by rules over the survey, by an evidence register, by reduced flow, chemical and electrical models, and by full-wave field solvers.

**Architecture:** Six packages (`premises`, `evidence`, `flow`, `chem`, `electro`, `em`), each computing `Result`s and verdicts from the ledger and writing `results/<package>/summary.json` through `pyramid.simkit`. `pyramid.verdicts.merged` joins them with Tier 0 and refuses any overruling. Packages share nothing but the ledger, `simkit` and read-only use of `pyramid.screening` and `pyramid.geometry`.

**Tech Stack:** Python 3.12, numpy, scipy, matplotlib, PyYAML, pytest; the existing `pyramid` package. Nothing is installed.

**Spec:** `docs/superpowers/specs/2026-10-11-simulations-design.md`; for `em` also `docs/superpowers/specs/2026-10-10-foundation-em-reply-design.md` sections 5.5 and 6; for `flow` and `chem` also `docs/superpowers/specs/2026-10-10-process-simulation-results-mode-design.md` sections 3 to 5.

## Global Constraints

- numpy, scipy, matplotlib and PyYAML only. Nothing is installed or downloaded. No web access is needed: every source is a research file in `research/`.
- **Every physical number comes from the ledger** (`ledger.q(id)`, `ledger.rng(id)`). Mathematical constants, unit conversions and stoichiometric coefficients may be written in code with a comment.
- **New ledger quantities** are appended at the END of `ledger/parameters.yaml` under one comment line `# --- <package> (2026-10-11) ---`, with ids in the package's own namespace (`geo.` premises, `flow.`, `rx.` chem, `elec.` electro, `emx.` em), in the file's existing schema (`id, value, unit, low, high, source, verified, note`), with a unit from `pyramid.ledger.UNITS`. `pyramid/ledger.py` is not yours to edit: convert to a unit that is already there, and if none fits, say so in your report and express the quantity in base units the list has. A value read in a research file cites that file and section as `source` and takes that file's verified flag. A value the hypothesis does not state has `verified: false` and a `note` beginning "not specified by the hypothesis:". A modelling assumption has `verified: false` and a `note` beginning "assumed for the model:". A handbook value recalled from memory has `verified: false` and a `note` beginning "from memory:". Give honest ranges; a verdict must hold or fail across them.
- **Criteria are fixed.** A verdict rule evaluates the claim's `criterion` in `ledger/claims.yaml` as written, and that text is never edited. Where a criterion needs a threshold it does not state, take it from the research file the criterion cites, name it a judgement call in a code comment and in the basis sentence. If a criterion cannot be evaluated at all, leave the claim undecided and say why in your report.
- **The three-way convention** (`simkit.three_way`): `pass` only if the criterion holds at the unfavourable end of every input range, `fail` only if it fails even at the favourable end, `conditional` between. `undefined` when the outcome hinges on an input the hypothesis does not specify. "Favourable" always means favourable to the hypothesis.
- **A package decides only the claims listed for it.** Tier 0 verdicts stand; you may report further `Result`s that bear on them.
- **Validation before verdicts.** Each model passes the analytic benchmarks named in its task, as pytest tests whose expected numbers are computed in the test from the closed form, with the tolerance stated.
- **Results.** `python -m pyramid.<package>` computes everything and calls `simkit.write_results("<package>", ledger, results, verdicts, extra)`; `extra` carries `"assumptions": [...]` (one sentence each) and any `"seed"`. Result ids are `<package>.<name>`; `Result.inputs` lists the ledger ids the number depends on. Do not edit `ledger/claims.yaml`: list in your report, per claim, the ledger ids its `depends_on` must gain so the viewer shows your numbers under it; the controller applies them once at the merge. Figures go to `results/<package>/figures/` as PNG (matplotlib Agg backend, no timestamps in the files). Time series go to `results/<package>/*.json`.
- **Do not commit `results/<package>/`.** Production results are regenerated once after all packages are merged, so that their manifests record the merged ledger. Run production in your worktree, quote the headline numbers and the run time in your report.
- **Basis sentences** are built from the numbers (f-strings), state the value and its range, and say only what the numbers support. Plain prose, no em dashes.
- **Files you may touch:** `pyramid/<package>/**` (or `pyramid/<package>.py`), `tests/test_<package>*.py`, the end of `ledger/parameters.yaml`, and what your task names. Nothing else: no viewer file, no `screening.py`, no `ledger.py`, no `claims.yaml`, no README, no other package.
- **Tests** check behaviour with real numbers; the whole suite (`uv run pytest -q -W error`) passes at every commit and stays fast (a package's tests under 30 s; heavy solves take a small grid in tests).
- **Style:** match the repository: short docstrings, comments that say why, `# ponytail:` on a deliberate simplification naming its ceiling and the upgrade path. Each module's docstring lists its assumptions.
- **Git:** you work in your own worktree. First run `git merge-base --is-ancestor <BASE> HEAD` with the BASE commit your dispatch names (if it fails, `git merge <BASE>`), then `git checkout -b sim/<package>`. Commit only your files; every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push.

## Shared Interfaces (already in the repository)

```python
# pyramid/screening.py
@dataclass(frozen=True)
class Result: id: str; label: str; value: float; low: float; high: float; unit: str; formula: str; inputs: tuple[str, ...]
all_results(ledger) -> dict[str, Result]          # the 37 Tier 0 quantities; read them, do not recompute them differently
verdicts(ledger, results) -> dict[str, tuple[str, str]]

# pyramid/simkit.py
three_way(holds_at_worst: bool, holds_at_best: bool) -> str
corners(ledger, inputs: tuple[str, ...], fn) -> (value, low, high)     # exact only where fn is monotone in each input
sample(ledger, ids, n, seed) -> list[dict[str, float]]                 # first draw = the ledger values
band(values) -> (median, p5, p95)
write_results(package, ledger, results, verdicts, extra=None, root=RESULTS) -> Path
read_results(package, root=RESULTS) -> (results, verdicts, manifest) | None

# pyramid/verdicts.py
PACKAGES = ("premises", "evidence", "flow", "chem", "electro", "em")
merged(ledger, root=RESULTS) -> (results, verdicts, source)

# pyramid/ledger.py
load() -> Ledger;  Ledger.q(id) -> float;  Ledger.rng(id) -> (low, high);  Ledger.claims[id] -> Claim(statement, criterion, depends_on, spaces, ...)
STATUSES = ("pass", "fail", "conditional", "undefined", "pending", "not_testable")

# pyramid/geometry (read-only): session(), build(ledger, variants=...), level_volume_curve(model, name), Variants
```

## Report contract (every task)

Write `<package>-report.md` in the folder the dispatch names: what you built; each benchmark with its expected and computed value; each verdict with the numbers that decide it and how the criterion was applied; every new ledger quantity with its source or its "assumed" flag; the assumptions; the production run time; deviations from this brief; anything you could not decide and why. Then return the structured result your dispatch asks for.

---

### Task 1: premises and evidence

**Files:** `pyramid/premises.py`, `pyramid/evidence.py`, `ledger/evidence.yaml`, `tests/test_premises.py`, `tests/test_evidence.py`.

**Claims.** `premises`: E11, E12, E15, E25, E32, S15. `evidence`: E02, E03, E04, E06, E07, E08, E09, E10, E16, E26, E27, E28, E30, E31, E33, E34, E35, E36, E37, E39 (documentary); S02, S26 (their criteria say "undefined until the hypothesis names ..."); S05, E05, E23, E24, E40 (`not_testable`: their criteria say "cannot be simulated" or "analogy only").

**Read:** each claim's `criterion` in `ledger/claims.yaml`; `research/01-geometry.md` (claims 1, 2, 3, 6, 7, premises P3 to P5, the Verification pass), `research/06-evidence-archaeology.md` and `research/07-plateau-geology.md` in full with their verification passes (corrections there override earlier text), `research/03-chemistry.md` check V14 and table 2c (the patent), `research/10-process-gaps-and-purpose.md` section 10.4, `research/petrie-check.md` for the rows you cite.

**premises.** Pure rules over ledger quantities, in the manner of `screening.RULES`: `verdicts(ledger) -> dict[str, tuple[str, str]]` and `results(ledger) -> dict[str, Result]` for the numbers the bases quote (ids `premises.<name>`). For a disputed feature the two readings are the ends of the three-way rule (the survey reading is the default, the alternative reading the favourable end); `pyramid/geometry/model.py`'s `Variants` names the switches. E11: compute where each King's Chamber shaft meets the casing plane from the ledger's shaft geometry and compare with the criterion's Z = 80 +/- 1 m; the level outer end rests on the survey record in `01` claim 1. E12 and S15: Petrie's groove depths (`ante.groove_*`) against a connected duct, and the largest connected area. E15: the south passage's blind end. E25: the thickness of stone that closed the Queen's Chamber shafts against the claim's 3 to 5 in. E32: the published void against "comparable size". Tests drive each rule through its statuses with altered ledger copies (as `tests/test_screening.py` does) and pin the status on the real ledger.

**evidence.** `ledger/evidence.yaml`: a list of `{id, status, basis, sources, verified}`: `status` by the ruling in the design's section 2 (pass, fail, conditional, undefined, not_testable); `basis` one or two sentences that begin with the research file's own standing ("Supported:", "No evidence found:", "Contradicted:", "Partly supported:", "Not specified by the hypothesis:", "No test exists:") and state what was read; `sources` the research file sections; `verified` whether the research file read the deciding source at source. `pyramid/evidence.py`: a strict loader in the style of `pyramid/species.py` (unknown keys, an unknown claim id, a status outside the vocabulary, a claim that is not in this task's evidence list, a missing or duplicate entry all raise `LedgerError` naming the entry), `verdicts(ledger)`, and `main()`. Assert only what the research files state; where they say a source was secondary, an abstract or OCR text, the basis says so. E37 has no four-point measurement behind it: apply the documentary ruling. E07 is decided by the patent text read at source in `03`.

**Commands:** `python -m pyramid.premises` and `python -m pyramid.evidence` each call `simkit.write_results`.

**Tests:** the register covers exactly the 27 evidence claims; every status is in the vocabulary; every basis begins with one of the standing phrases; each loader rejection; `not_testable` appears exactly on S05, E05, E23, E24, E40 and `undefined` on S02 and S26 at least.

---

### Task 2: flow (water and gas movement)

**Files:** `pyramid/flow/__init__.py`, `network.py`, `hydraulics.py`, `gas.py`, `retention.py`, `__main__.py`, `tests/test_flow_*.py`.

**Claims:** S03, S08, S13, S14, S17.

**Read:** the five criteria; `research/02-hydraulics.md` sections 2, 4 and 5 with the verification pass (5.5 holds the tests the criteria cite); `research/01-geometry.md` premises P3 and P4, claim 2 (grooves, slab clearance) and the connectivity graph; `research/09-recomputation.md` rows 13, 16, 17, 21 to 24; `research/00-hypothesis.md` S03, S08, S13 to S17 and section 5 (undefined inputs); the ledger's `hydro.*`, `kcs.*`, `ante.*`, `gg.*`, `kc.*`, `ws.*`, `dp.*`, `site.*` entries; the Tier 0 results `t0.*` that already cover this ground (reuse them, do not contradict them).

**Models.**
- `network.py`: the spaces as nodes with volume, floor and roof levels, and free-surface area against level, from the ledger (and `pyramid.geometry.level_volume_curve` where a curve is needed); the openings between them as links with level, area and loss coefficient.
- `hydraulics.py`: (a) S08: the reservoir surface level and the volume one fill needs, for a fill by communicating vessels alone and for a fill with the claimed pump from a pavement-level reservoir, with the inflow rate for a stated fill time; the evidence-based boundary is no water at base level (`02` C1). (b) S13: with the Gallery full to its roof, the water head at the antechamber passage, the flow of water through any opening that also passes gas (orifice law, the groove area of `01` premise P3 and the slab clearance), the time for the King's Chamber floor to flood, and the gas pressure that would hold the water back against the open shafts; the drain route is one of the hypothesis's undefined inputs.
- `gas.py`: S14 and S17: as the Gallery drains at the rate set by `hydro.drain_time`'s range, a conductance network (orifice and pipe-friction losses; quadratic, solved by Newton iteration or bisection) for the replacement gas: the two King's Chamber shafts into the chamber, the antechamber path (grooves; slab clearance), and every other opening into the Gallery and its connected spaces that `01` lists, each with an area range in the ledger. Report the share of the displaced volume that arrives through the antechamber and through the shafts, and the pressure difference.
- `retention.py`: S03: sulfur dioxide (2.2 times the density of air) in the King's Chamber with two open shafts rising to the faces: loss by molecular diffusion up the shafts and by wind-driven through-flow between the two faces (a pressure coefficient difference times the dynamic pressure, against the shafts' friction), as a retention half-time against wind speed. The interval between delivery and draw is not specified by the hypothesis.

**Benchmarks (tests):** Torricelli draining of a tank through an orifice (time to empty within 1 percent of the closed form); two communicating vessels settling at a common level (mass conserved to 1e-9); gas split between two parallel orifices equal to the ratio of their areas times loss factors (1 percent); volume of gas drawn equals volume of water drained (1e-9); diffusion loss from a well-mixed chamber through a tube matches `V L / (D A)` as time constant (1 percent).

**Verdicts:** each by its criterion and the three-way rule over the ledger ranges (corners where monotone, otherwise `simkit.sample` with a seed and the band). S08's criterion asks for a report: give the level and volume in the basis. Where the deciding input is unspecified by the hypothesis, the status is `undefined` or `conditional` as the convention says, with the value at which the criterion would flip.

**Figures:** water ingress to the King's Chamber against time (S13); share of gas by path against the antechamber's open area (S14, S17); retention half-time against wind speed (S03).

---

### Task 3: chem (chemistry and feed)

**Files:** `pyramid/chem/__init__.py`, `transfer.py`, `aqueous.py`, `walls.py`, `feed.py`, `__main__.py`, `tests/test_chem_*.py`.

**Claims:** S01, E01, S19, S22, S23.

**Read:** the five criteria; `research/03-chemistry.md` sections 2 and 4 with the verification pass (4.4 holds the thresholds the criteria cite; checks V5 to V9, V13, V16 to V18); `research/07-plateau-geology.md` sections 3 and 4.4 with its verification pass (the hydrogen sulfide supply and the seep analogues); `research/09-recomputation.md` rows 26 to 35; `research/00-hypothesis.md` S01, S19 to S23 and section 5; the ledger's `chem.*` entries; the Tier 0 results on the acid ceilings, oxygen supply, sulfate yield, gypsum saturation loss and temperature rise (reuse them, do not contradict them).

**Models.**
- `transfer.py`: two-film transfer across the Gallery's free surface (area from the ledger's Gallery section, as Tier 0 computes it) for sulfur dioxide (gas-film controlled: it is very soluble) and oxygen (liquid-film controlled), integrated in time with scipy over a cycle. S19: the share of the sulfur that reaches the liquid within the cycle, over the range of the gas-side transfer coefficient from stagnant diffusion to natural convection (new ledger entries, flagged as the brief requires) and of the cycle time (one day is Tier 0's judgement call; state it the same way).
- `aqueous.py`: sulfur(IV) speciation (`chem.pka1_so2`, `chem.pka2_so2`), pH by charge balance, iron-catalysed oxidation (`chem.fe_rate_constant`, `chem.fe_concentration`) limited by dissolved oxygen. S22: the gas the rising water must displace: with the air the hypothesis itself draws in, the nitrogen and unused oxygen that cannot dissolve (`chem.henry_o2`; a nitrogen Henry constant flagged as the brief requires) against the volume swept; the share forced back for the stated and the favourable gas compositions.
- `walls.py`: S23: over ten fill and drain cycles with fresh water: acid neutralised by calcite until gypsum saturates (the Tier 0 result), the gypsum the fill water can hold in solution against the gypsum formed (`chem.gypsum_solubility`), the layer thickness that precipitates, its transport resistance (`chem.gypsum_h_diffusivity`, `chem.gypsum_layer_thickness`), and how much of it a fresh-water fill dissolves; the wall loss per cycle and per ten cycles.
- `feed.py`: S01 and E01: the hydrogen sulfide a batch needs (from the Tier 0 sulfur inventory) per cycle and per year for the range of cycle rates, against the fluxes of the documented seeps and springs the research file gives; E01's first clause is documentary (a measured flux under the plateau): `07` records that none was found.

**Benchmarks (tests):** approach to Henry-law equilibrium in a closed vessel with the analytic time constant (1 percent); a first-order oxidation's half-life reproduced from the ledger's rate law (1 percent); parabolic growth of a diffusion-limited layer (1 percent); element balance for sulfur and oxygen closed to 1e-9 over a cycle; each quantity Tier 0 also computes (acid ceiling, sulfate yield in one day, gypsum saturation loss) equal to the Tier 0 value at the same inputs (1e-6 relative).

**Verdicts:** each by its criterion (S19: at least 90 percent captured passes, below 50 percent fails; S22 and S23 as written) and the three-way rule. State in each basis which undefined input the outcome depends on.

**Figures:** sulfur captured against time for the transfer-coefficient range (S19); gas forced back against the air fraction (S22); layer thickness over ten cycles (S23); required hydrogen sulfide flux against the analogues (S01).

---

### Task 4: electro (ground current, lightning, the piezoelectric chain, room acoustics)

**Files:** `pyramid/electro/__init__.py`, `conduction.py`, `sources.py`, `piezo.py`, `rooms.py`, `__main__.py`, `tests/test_electro_*.py`.

**Claims:** S04, E21, S06, E13.

**Read:** the four criteria; `research/04-electromagnetics-piezo.md` sections 4 and 5.2 to 5.4 with the verification pass; `research/05-sonochemistry-acoustics.md` sections 4.3 and 5.5 with section 8; `research/07-plateau-geology.md` section 4.2; `research/09-recomputation.md` rows 37 to 49; the ledger's `em.*`, `ac.*`, `plateau.*`, `kc.*`, `ante.*`, `gg.*`, `pyr.*` entries; the Tier 0 results on relaxation, piezoelectric sound level, skin depth and vein contrast (reuse them).

**Models.**
- `conduction.py`: steady conduction `div(sigma grad phi) = 0` in three dimensions by finite volumes on a graded Cartesian grid (harmonic-mean face conductances, scipy sparse, conjugate gradients with a preconditioner), with Dirichlet or flux boundaries and point current sources. The pyramid is its true square shape on a ground half-space, the air insulating.
- `sources.py`: (a) telluric (S04, E21): a uniform horizontal far field over the criterion's range of 1e-7 to 2e-2 V/m in the ground; the field in the masonry at the summit and in the King's Chamber granite; then with conductive sheets for the ore bodies (`plateau.hematite_resistivity_*`, sheet geometry flagged as assumed and swept). (b) lightning (S06): the stroke current (`em.stroke_current_median`, `em.stroke_current_max`) injected at the summit, quasi-static, with limestone and granite conductivities over their ledger ranges; the peak field in the granite. State the quasi-static assumption against the Tier 0 skin depth at the lightning frequency.
- `piezo.py`: the field in the granite that the piezoelectric and acoustic chain needs to reach the acoustic thresholds of the ledger (`ac.gas_solid_intensity`, `ac.cavitation_intensity`), by inverting the Tier 0 chain (`screening`'s piezoelectric functions) rather than writing a new one.
- `rooms.py`: E13: for the antechamber, the King's Chamber and the Grand Gallery: the rectangular-room modes in the audio band, the decay time from wall absorption (`ac.wall_absorption`) and air absorption, and the modal quality factor; their ranking.

**Benchmarks (tests):** a uniform field in a homogeneous block reproduced to 1e-6; a point current on the surface of a homogeneous half-space against `phi = I rho / (2 pi r)` at several radii (3 percent away from the source and the boundaries); the field inside a conducting sphere in a uniform field against `3 sigma0 / (2 sigma0 + sigma1)` (5 percent on a modest grid); grid refinement changes the King's Chamber field by less than 5 percent; the lowest axial mode of a rectangular room against `c / (2 L)`.

**Verdicts:** S04 and E21 need "non-negligible": take the threshold from `04` section 5.3 and from what `piezo.py` says the chain needs, and name it a judgement call. S06 by its criterion: pass if the peak field in the granite exceeds what the chain needs, fail if it is screened to the conduction value of order kV/m or less. E13: pass if the antechamber ranks first.

**Figures:** potential and field on the north-south section for the telluric and lightning cases; the field in the granite against limestone conductivity with the needed field marked; decay time against frequency for the three rooms.

---

### Task 5: em (the 2018 study in two in-house field solvers)

**Files:** `pyramid/em/__init__.py`, `mie.py`, `shapes.py`, `dda.py`, `fdtd.py`, `cases.py`, `metrics.py`, `__main__.py`, `tests/test_em_*.py`.

**Claims:** E19, E20.

**Read:** `docs/superpowers/specs/2026-10-10-foundation-em-reply-design.md` sections 5.5 and 6: the cases (B0, R1, R2, R3, C0, V1, V2, V3, V4), the metrics and the criteria are binding exactly as written, with the two in-house solvers in the place of MEEP and FEniCSx; `research/04-electromagnetics-piezo.md` (what the study models and reports; sections 2, 5.1 and the verification pass, checks V1 to V6); `research/09-recomputation.md` rows 37 to 39; the ledger's `paper.*` entries (the study's geometry, material, band and the peak values read from its figures), `em.*` and `pyr.*`.

**Solvers.**
- `mie.py`: the Mie series for a homogeneous sphere (extinction, scattering and absorption efficiencies; scipy.special spherical Bessel functions).
- `shapes.py`: voxel masks on a regular grid from the ledger: the sphere; the study's pyramid with its three chambers; the control cube of the pyramid's volume with the chambers at the same heights; the apex variants (pointed at 146.71 m, truncated at 137.4 m, the study's 138.75 m); the surveyed chambers and Gallery as boxes from the ledger with a granite region around the King's Chamber (extent flagged as assumed); a ground slab.
- `dda.py`: the frequency-domain volume-integral (coupled-dipole) solver with FFT-accelerated products and an iterative solver (scipy GMRES or BiCGSTAB); extinction by the optical theorem, absorption from the polarisations, the field at empty cells (chambers) from the solved polarisations. It is a free-space solver and stays one: do not write a half-space Green's function. The cases with ground (R3, V3 on ground, V4) rest on the FDTD solver alone, and the spec's 10 percent agreement between the two solvers is tested on the free-space cases (B0, R1, R2).
- `fdtd.py`: a three-dimensional Yee solver with convolutional PML, a total-field/scattered-field plane-wave source whose incident field is the exact solution for the air and ground half-spaces (a one-dimensional auxiliary grid), a broadband pulse with running Fourier sums at the band's wavelengths, conductive loss; it handles the cases with ground.
- `cases.py`, `metrics.py`: the case table as data built from the ledger; the extinction spectrum over 200 to 600 m; for each chamber the maximum and the volume mean of |E|^2 over the incident |E|^2; the summit metric (the volume mean in the masonry between Z 132.4 m and 137.4 m).

**Gates, in order (spec section 6):** B0 within 2 percent of Mie across the band in both solvers; halving the cell size changes the R1 peak extinction by less than 3 percent; the reproduction criteria (peak wavelengths, peak cross-sections against `paper.peak*`, the two solvers within 10 percent normalised root-mean-square difference over the band). **No variant is interpreted and no verdict is written until these pass**; if one fails, report which, with both solvers' numbers, and leave E19 and E20 undecided.

**Verdicts:** E19 and E20 exactly by the spec's criteria (each case against its control at their own band maxima; the conductivity range 6.7e-4 to 3.3e-3 S/m from the ledger). E19 turns on the volume mean in the King's Chamber, which the spec calls sensitive to resolution and which no gate covers: compute it at two cell sizes for R1 and for V4 (the finer one giving the chamber at least three cells across its smallest side) and report both; if the two cell sizes put the criterion's comparison on different sides (the factor of two against the control, or the value 2), the verdict is `conditional` and the basis gives both values. Do the same for E20's summit metric.

**Running:** `python -m pyramid.em` runs the cases in parallel processes (`multiprocessing`, at most 10 workers) and must finish in under two hours on this machine (14 cores, 36 GB); `python -m pyramid.em --quick` runs B0 and R1 on a coarse grid in under two minutes for a smoke check. State the cell sizes used and why they are fine enough (cells per wavelength in the material). Tests use small grids: the Mie series against tabulated limits (Rayleigh and geometric-optics extinction), the dipole solver against Mie for a small sphere (5 percent on a coarse grid), the FDTD plane wave in empty space (reflection from the PML below -40 dB) and against Fresnel reflection from a half-space (2 percent), energy conservation (extinction equals scattering plus absorption within 2 percent).

**Figures:** extinction spectra of B0 (both solvers against Mie), R1, R2 and R3 against the study's peak values; |E|^2 ratio on the axial section at the R1 peak; the King's Chamber ratio against conductivity (V1, V4) with its control; the summit metric for the three apex variants. Also write the axial-section maps as PNG with a JSON sidecar giving the plane and the extent in metres, for the viewer's Results mode.

Commit in stages (Mie; shapes, cases and metrics; the dipole solver with its benchmark; the FDTD solver with its benchmarks; the runs and verdicts), so that validated work is kept if you run out of room; say in your report exactly where you stopped.
