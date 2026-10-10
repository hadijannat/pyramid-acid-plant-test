# Foundation and electromagnetic reply: design

Piece 1 of 6. Date: 2026-10-10. Status: draft for review.

## 1. Context

The project tests Geoffrey Drumm's "Land of Chem" hypothesis, which holds that the Great Pyramid operated as a sulfuric-acid plant. The hypothesis is extracted step by step in `research/00-hypothesis.md` (steps S01 to S31, evidence claims E01 to E40; E41 and E42 in that file concern the Red Pyramid and the radar-scan discussion and are outside this project). Sourced inputs and a first assessment of each claim are in `research/01` to `research/09`, verified in commit `c4e3c89`.

Decisions already made by the project owner:

- **Purpose:** personal investigation, public demonstration, academic output, and a reply to the proponent, who asks in the source video for someone to model the system in COMSOL.
- **Solvers:** open-source only.
- **Scope:** tiered. Tier 0 is a sourced calculation per step. Tier 1 is a full solver where it can change the answer. Tier 2 is a reduced model with parameter sweeps. One 3D scene sits over all of it.
- **Build order:** (1) foundation and electromagnetic reply, (2) electrical extension, (3) hydraulics, (4) chemistry, (5) plateau network, (6) presentation.

This document specifies piece 1 only.

## 2. Goals and non-goals

Goals:

1. A single source of truth for every number and every claim (the ledger).
2. The Tier 0 screening table, recomputed from the ledger by code.
3. A parametric 3D model of the pyramid's interior with switches for what the survey record leaves open.
4. A browser viewer that animates the cycle as claimed and shows a verdict per step.
5. A reproduction of Balezin et al. 2018 (J. Appl. Phys. 124, 034903), the electromagnetic study the hypothesis cites, in two independent codes.
6. A test of whether that study's field-concentration result, and the "flat top by design" reading of it, survive realistic geometry, loss and ground.

Non-goals for this piece:

- Lightning and ground-current models, and the bound on ultrasound from granite (piece 2). The cases here are wave-scattering cases; whatever they show, they say nothing about slow inputs such as lightning or telluric currents.
- Flow, chemistry, the plateau network, the paper and the public reply (pieces 3 to 6).
- Any statement about what the pyramid was for.

## 3. Principles

- **Neutral test.** A step may pass, fail, hold only under a stated assumption, or be undefined by the hypothesis. All four are legitimate results.
- **Criteria before runs.** Pass criteria live in the claims file and are committed before the first production run. A later change needs a dated note explaining why.
- **Three readings per claim** where they apply: literal (as stated), favourable (best physically admissible assumptions), and required (what would have to be true for the step to work).
- **No hard-coded numbers.** Geometry, screening and solver cases read values from the ledger.
- **Provenance on every result.** Each output records the git commit, a hash of the ledger, mesh statistics and solver versions.
- **Gaps stay visible.** Where the hypothesis does not define an input, the input is a swept parameter and is labelled as such.

Verdict vocabulary, used everywhere: `pass`, `fail`, `conditional`, `undefined`, `pending`.

## 4. Architecture

```
ledger/            parameters.yaml, claims.yaml
pyramid/           Python package
  ledger.py        load and validate the ledger
  screening.py     Tier 0 quantities as pure functions of ledger values
  geometry/        parametric model, variants, exports
  em/              case definitions, MEEP and FEniCSx drivers, metrics
  provenance.py    run manifest
viewer/            static three.js page and its data folder
cases/             one small YAML file per solver run
results/           solver output (large fields ignored by git; summaries committed)
tests/
research/          evidence base (existing)
docs/superpowers/specs/
```

Data flows one way:

```
ledger -> screening -> claims verdicts (Tier 0) ----------------\
ledger -> geometry -> meshes -> EM cases -> metrics -> verdicts -> viewer data
                   -> glTF ---------------------------------------/
```

## 5. Components

### 5.1 Ledger

`ledger/parameters.yaml` holds one entry per quantity: `id`, `value` (SI), `unit`, `range`, `source` (citation plus the research file and section), `verified` (true only if read in an opened source), and an optional `note`. Where the research files disagree, the resolution in `research/09-recomputation.md` is used and the alternatives are recorded in `note`.

`ledger/claims.yaml` holds one entry per hypothesis step and evidence claim: `id`, `statement`, `subsystem`, source timestamp, `tier`, the piece that tests it, `criterion`, `status`, and the ids of the ledger quantities and results it depends on.

`pyramid/ledger.py` loads both files and rejects entries with a missing source, an unrecognised unit, or a reference to an unknown id.

### 5.2 Screening (Tier 0)

`pyramid/screening.py` implements the derived quantities of `research/09-recomputation.md` that decide a Tier 0 claim: 36 of that file's 51 rows, plus the one-day sulfate yield that claim S20's criterion needs, 37 quantities in all (chamber volumes, pressures, piston force, stroke counts, suction margin, gas inventory, acid ceiling, temperature rise, oxygen supply, strike rate, relaxation times, skin depths, piezoelectric displacement and sound level, shaft path loss, vein conductivity contrast). Each is a pure function of ledger values and returns a value with its range. A command writes the Tier 0 table and sets a first verdict on each claim it bears on.

### 5.3 Geometry

Built with gmsh's OpenCASCADE kernel through its Python API, so one tool does CAD and meshing.

- **Frame:** origin at the pyramid's centre on the pavement; X east, Y north, Z up. The passage system lies 7.29 m east of the north-south axis.
- **Level `survey`:** every surveyed space as a solid: entrance and Descending Passage, Subterranean Chamber with pit and blind south passage, well shaft and grotto, Ascending Passage with plugs, Queen's Chamber passage, Queen's Chamber with niche and both shafts, Grand Gallery with its corbels, antechamber with slots and grooves, King's Chamber with coffer and both shafts, relieving chambers, Big Void, North Face Corridor. Masonry is the pyramid minus the spaces. Bedrock is a separate region below the surveyed interface.
- **Level `paper`:** the 2018 study's model exactly: pointed pyramid 138.75 m high on a 230 m base with its three box chambers, dimensions and offsets as recorded in `research/04-electromagnetics-piezo.md` (check V1).
- **Variant switches:** casing on or off; King's Chamber shafts open or closed at the casing; their outer ends level or inclined; portcullis slabs present or absent; south-wall grooves blind or connected (at most about 0.002 m² in total); Ascending Passage plugs present or absent; pit as before 1837 (about 2.7 m) or as excavated (about 11 m); Big Void horizontal or inclined, 30 to 40 m long, centre at Z 61 to 71 m; apex pointed at 146.71 m or truncated at 137.4 m.
- **Exports:** STEP for CAD, gmsh meshes for the solvers, and glTF for the viewer with one named node per space.
- **Self-checks:** control points within Petrie's stated error (worst case 0.076 m); each volume within the ledger's range; every solid closed; every space inside the pyramid or bedrock; a switch changes only the solids it names.

Simplifications in this piece, each flagged in the code and refined when a later piece needs it:

- The five relieving chambers are one block, because no source read gives the levels of the four lower compartments.
- The King's Chamber coffer and the antechamber's fittings (wainscots, slots, granite leaf, the two northern slabs) are not modelled, because no surveyed position was found. The `portcullis` switch closes the antechamber's south end by one slab thickness, and `grooves_connected` opens one duct of the grooves' total area through it.
- Bedrock is a flat-topped block below the pavement. The rock knoll rising inside the pyramid is not modelled.
- The Big Void uses the ledger's central position and a 30 m length; its published ranges are not swept here.
- The grotto's plan size and the North Face Corridor's level have no sourced value. Both are assumed entries marked unverified in the ledger.

**Gate G0, before any CAD:** Petrie's figures reached the research files through a text-extraction tool. Two copies agree, but each ledger entry that cites Petrie is checked against the raw scanned text of the 1883 edition, and the result is recorded entry by entry in `research/petrie-check.md`.

### 5.4 Viewer

A static page using three.js loaded as an ES module from a pinned URL, with no build step. It reads four kinds of data from `viewer/data/`:

- `interior.glb`: the geometry, one named node per space.
- `claims.json`: exported from the claims file with current verdicts and the Tier 0 numbers.
- `cycle.json`: the timeline of the claimed cycle, one entry per step S01 to S31, with camera position, duration and what moves (water level in a named space, pump position, gas path, lightning, field overlay).
- `fields/`: field slices exported from solver results, with their spatial extent.

Behaviour:

- Orbit, pan and zoom; toggle spaces, masonry and geometry variants.
- Play, pause and scrub the claimed cycle. Water levels follow the level-to-volume curves from the geometry, so the animation is geometrically consistent with the surveyed spaces.
- A side panel per step shows the claim in plain words, its source timestamp, its tier, its verdict and the numbers behind the verdict.
- Clicking a space shows its ledger values and the claims that involve it.
- Steps with a solver result can show it in place of the schematic (in this piece: the electromagnetic field slices).
- A persistent label states that the animation shows the claim and is not a simulation result. Steps that fail screening are animated as claimed with the failing number shown beside them.
- Nothing the hypothesis leaves unspecified is drawn as a concrete object. The pump, the valves, the reservoir, the gallery drain and the gas inlet appear as dashed placeholders labelled "not specified by the hypothesis", so the viewer never attributes a mechanism to the proponent that he did not describe.

### 5.5 Electromagnetic module

Two independent codes: MEEP (finite-difference time domain, broadband pulse) and FEniCSx (frequency-domain finite elements with edge elements and absorbing layers, scattered-field formulation). Both read the same case files and the same geometry parameters. The incident field for cases with ground is the exact plane-wave solution for the air and ground half-spaces without the pyramid.

Metrics, computed identically for both codes:

- extinction cross-section against wavelength over 200 to 600 m;
- for each chamber, the maximum and the volume mean of |E|² divided by the incident |E|² (the study's Fig. 4 plots the maximum, which the research notes suggest is an edge value, so both are reported);
- a summit metric: the volume mean of the same ratio in the masonry between Z 132.4 m and 137.4 m. This is the top 5 m of the truncated structure and exists in every apex variant, so the same region is compared each time.

### 5.6 Provenance

`pyramid/provenance.py` writes a manifest beside every result: case file, git commit, ledger hash, mesh statistics, solver and library versions, wall time. A result without a manifest is not used for a verdict.

## 6. Electromagnetic cases and criteria

| Case | Geometry | Material | Excitation | Purpose |
|---|---|---|---|---|
| B0 | Sphere, radius 100 m | permittivity 5 + 0.1i | plane wave | Benchmark against the exact Mie solution |
| R1 | `paper`, free space | 5 + 0.1i | along the axis from the apex side | Reproduce the study's Fig. 1(a) and Fig. 4 |
| R2 | `paper`, free space | 5 + 0.1i | along the axis from the base side | Reproduce Fig. 1(b) and Fig. 4 |
| R3 | `paper` on ground of the same material | 5 + 0.1i | from above | Reproduce Fig. 5 and Fig. 7 |
| C0 | The chambers of the case it controls, at the same heights, inside a cube of the pyramid's volume | as the case it controls | as the case it controls | Control, run for R1, R3 and V4: separates the effect of the pyramid's shape from the effect of any air cavity in a dielectric |
| V1 | R1 and R3 | real permittivity 5, 7 and 8.8; conductivity 5e-6, 1e-4, 6.7e-4, 3.3e-3 and 2e-2 S/m | as R1 and R3 | Does the resonance survive measured rock loss |
| V2 | `survey` chambers and Grand Gallery, granite around the King's Chamber | as R1; granite from the ledger | as R1 and R3 | Real chamber geometry |
| V3 | Apex pointed at 146.71 m, truncated at 137.4 m, and the study's 138.75 m | 5 + 0.1i | free space from both sides; on ground from above | The flat-top claim |
| V4 | V2 with truncated apex, on bedrock | measured loss range | from above | Best estimate of the real structure |

Criteria, fixed now:

- **Benchmark.** B0 matches the Mie extinction spectrum within 2% across the band in both codes. Halving the cell size changes the R1 peak extinction by less than 3%.
- **Reproduction.** Free-space peaks fall within 5% of 333 m and 230 m; the on-ground maximum falls within 10% of 250 m; peak cross-sections fall within 20% of the values read from the study's figures (0.09, 0.13 and 0.12 km²); the two codes' extinction cross-sections agree within 10% (normalised root-mean-square difference over the band). Chamber ratios are sensitive to resolution, so both codes' values are reported side by side and do not gate the reproduction. No variant is interpreted until this passes.
- **E19, "the shape concentrates field at the King's Chamber".** Each case is compared with its control at their own band maxima (peak against peak), never wavelength by wavelength, because the control's resonances fall elsewhere. As modelled: `pass` if the band-maximum volume-mean ratio in the King's Chamber in R1 is at least twice that of its control. Under realism: `pass` if in V4 the volume-mean ratio is at least 2 and at least twice that in its control across the conductivity range measured in the pyramid's masonry (6.7e-4 to 3.3e-3 S/m); `fail` if it is below 2 at 6.7e-4 S/m; otherwise `conditional`, with the conductivity at which it drops below 2 reported.
- **E20, "the flat top is functional and there was never a capstone".** The claim concerns the real structure, so the comparison is the apex truncated at 137.4 m against the apex pointed at 146.71 m; the study's 138.75 m model is reported for reference. `pass` only if the band-maximum summit metric for the truncated apex is at least twice that for the pointed apex in the on-ground case. The free-space case with the wave from below is reported but does not decide the claim, because a wave arriving from below has no counterpart once the ground is present.

## 7. Environment

- **Core (uv, Python 3.12):** numpy, scipy, pyyaml, gmsh, trimesh, matplotlib, pytest. Covers the ledger, screening, geometry, exports and tests.
- **Field solvers (conda-forge):** DOLFINx built for complex numbers, MEEP, MPI. These have no pip packages, so they live in a separate conda environment defined by a committed environment file. This needs Miniforge installed; installation is requested from the project owner when implementation reaches it.
- Versions are pinned and lock files committed. Memory budget for any single solve: 28 GB of the machine's 36 GB.

## 8. Testing

- **Ledger:** every entry has a value, an SI unit and a source; every claim references known ids.
- **Screening:** each quantity reproduces the value in `research/09-recomputation.md` within 2%.
- **Geometry:** the self-checks of section 5.3, run for the default model and for each variant switch.
- **Electromagnetics:** the benchmark and convergence criteria of section 6, with a coarse version of B0 as a fast regression test.
- **Viewer:** the four data files are validated against their expected structure by a test; the page is loaded in a browser and each step of the cycle is checked by eye and by screenshot.

## 9. Risks and fallbacks

| Risk | Response |
|---|---|
| A Petrie figure is wrong in the research notes | Gate G0 (section 5.3) |
| The three-dimensional absorbing-layer formulation in FEniCSx costs too much effort or memory | Use first-order edge elements on a finer mesh; if that fails, replace FEniCSx with Palace as the second code |
| MEEP's grid is uniform, so resolving a 5 m chamber inside a 230 m pyramid approaches the memory budget | Use MEEP at coarser resolution for extinction spectra and peak positions and FEniCSx, with local refinement, for chamber fields; measure memory on a small case before fixing the resolution |
| Values read from the study's figures are imprecise | Wavelengths of the peaks carry the reproduction criterion; magnitudes get a 20% band |
| The study's chamber maxima are edge values | Report maximum and volume mean; criteria use the mean |
| The animation is mistaken for evidence | Persistent label, verdict and failing number shown on every step |

## 10. Milestones

1. **M1:** ledger and screening, with the Tier 0 table generated.
2. **M2:** geometry at both levels, variants, exports, after gate G0.
3. **M3:** viewer with the animated claimed cycle and Tier 0 verdicts.
4. **M4:** field-solver environment, benchmark B0 and reproduction R1 to R3.
5. **M5:** control C0 and variants V1 to V4, verdicts on E19 and E20, field overlays in the viewer.

Two implementation plans: plan A covers M1 to M3; plan B covers M4 and M5 and is written when plan A has landed, because it depends on the geometry outputs.
