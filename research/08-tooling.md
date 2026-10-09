# 08 - Tooling: open-source multiphysics stack for testing the "Land of Chem" sulfuric-acid hypothesis

Research date: 2026-10-09/10. Target machine: Apple M4 Max (arm64), 14 cores, 36 GB RAM, macOS (Darwin 27). Present: Python 3.12 (pyenv), uv, Homebrew, Docker CLI, Node 22, Bun. Absent: gmsh, OpenFOAM, Elmer, ParaView, Blender.
Method: web pages and papers opened in this session only. Nothing was installed or run. "verified = true" means I read that figure in the cited source this session; anything else is marked false and says why.

---

## 1. Summary

- Every physics in the hypothesis has a free solver that runs on this Mac, but **not one of them is a one-command native install for everything**. The realistic choice is between a native-first hybrid and a Linux VM/container.
- **Free-surface flow**: OpenFOAM is viable three ways. (a) OpenFOAM.app gives a native arm64 build of the ESI/Keysight line (v2606, v2512) via Homebrew tap [1]. (b) The Foundation line (v14, July 2026) officially supports macOS only through a Multipass Ubuntu VM with arm64 packages [2][3]. (c) ESI Docker images have linux/arm64 builds, newest tag 2512 [5].
- **The main solver gap**: stock volume-of-fluid solvers do not carry dissolved species or reactions. interFoam is two incompressible isothermal immiscible fluids [45]; icoReactingMultiphaseInterFoam is a phase-change solver despite its name [46]. The stock solver that does offer species, in-phase reactions and interphase mass transfer is the Foundation's Euler-Euler `multiphaseEuler` [48][49], which is not a sharp-interface VOF solver and is not native on macOS. Testing the claim "the gas dissolves instead of being pushed back" therefore needs either that solver in a VM, or a custom species-transfer extension of a VOF solver.
- **Electromagnetics / acoustics / piezo / heat**: FEniCSx has conda-forge osx-arm64 builds including complex-scalar variants [17][18]; MEEP has osx-arm64 conda builds [22][23]; Firedrake officially supports ARM Macs [20]. Elmer has the most ready-made physics modules [15] but no macOS binary route was found: it is a source build [12], and the macOS instructions carry a warning that they may be out of date. openEMS states its Homebrew formula is broken [24].
- **Kinetics**: Cantera 3.2.0 installs by pip or conda on arm64 [26][27][29] but ships no sulfur mechanism [30]. Sulfur libraries exist in the RMG database [31] and need conversion.
- **CAD/meshing**: gmsh 4.15.2 has an arm64 wheel and Homebrew bottle [6][7]; build123d 0.13.0 and CadQuery 2.8.0 are pip-installable on Python 3.12 but pin incompatible OCP versions, so pick one [8][9].
- **Mesh size**: the four main chambers total about 1,130 m3 (computed from surveyed dimensions [51][53]). A 10 cm base mesh with local refinement (roughly 3-8 M cells) fits in 36 GB; a uniform 5 cm mesh (about 12 M cells) is borderline; uniform 2.5 cm (about 96 M) does not fit.
- **Hard limit found**: full-wave acoustics at ultrasonic frequency in air at chamber scale needs about 10^9-10^10 unknowns and is out of reach on this machine by orders of magnitude. Only audio-range chamber acoustics (up to roughly 1-3 kHz) is feasible as a full 3D solve.
- **Coupling**: the hypothesis is a one-directional chain (electric field -> strain -> sound -> rate change -> flow/absorption). One-way file hand-off is sufficient for a first test. preCICE (Homebrew, arm64) [34] is available if two-way coupling is later needed, but it has no Elmer adapter [35].
- **Validation cases available**: Balezin et al. 2018 is fully specified in the paper and small enough to reproduce [50]; the ScanPyramids muon papers give a Geant4 forward-model recipe [51][52]. No peer-reviewed airflow or thermal CFD of the Great Pyramid interior was found.
- **Existing 3D models**: no openly licensed, dimensionally reliable interior model was found. Best plan is to build parametric CAD from survey text.

---

## 2. Parameters

### 2.1 Tool availability on macOS arm64

| name | value | unit | uncertainty | source | verified |
|---|---|---|---|---|---|
| OpenFOAM.app: OpenFOAM versions packaged | v2606 and v2512 current; older v2112-v2506 | - | - | [1] | true |
| OpenFOAM.app: architecture / OS | Apple silicon only; macOS 14 or later tested | - | older macOS untested by author | [1] | true |
| OpenFOAM.app: install | `brew install gerlero/openfoam/openfoam` (or `@2606`, `@2512`) | - | not run | [1] | true |
| OpenFOAM.app: licence | GPL-3.0; not endorsed by OpenCFD | - | - | [1] | true |
| OpenFOAM.app: caveats | no ParaView; read-only case-sensitive disk image; not notarized; Apple Clang not GCC | - | - | [1] | true |
| OpenFOAM.app: Foundation versions | not supported | - | - | [1] | true |
| OpenFOAM Foundation latest | v14, released 14 July 2026 | - | - | [2] | true |
| OpenFOAM Foundation on macOS | Multipass Ubuntu VM; arm64 packages on Apple silicon | - | - | [2][3] | true |
| OpenFOAM ESI/Keysight latest | v2606 (June 2026); macOS = compile from source or Docker | - | - | [4] | true |
| Docker `opencfd/openfoam-default` | tags 2306 to 2512 have linux/arm64; `latest` = 2512 | - | no 2606 tag seen on the page | [5] | true |
| gmsh (PyPI) | 4.15.2, released 2026-03-24, wheel `macosx_12_0_arm64` | - | - | [6] | true |
| gmsh (Homebrew) | 4.15.2, arm64 bottles incl. sonoma, sequoia, tahoe, "golden gate"; GPL-2.0-or-later | - | - | [7] | true |
| build123d | 0.13.0 (2026-09-21), Apache-2.0, Python >=3.11,<3.15, needs `cadquery-ocp-novtk >=8.0,<8.1` | - | - | [8] | true |
| CadQuery | 2.8.0 (2026-06-21), Apache 2.0, Python >=3.11, needs `cadquery-ocp >=7.9.3.1,<8.0` | - | - | [9] | true |
| cadquery-ocp arm64 wheels | latest 8.0.1.1.0; arm64 wheels seen for 7.8.1.1 (cp310-cp312) | - | 8.x arm64 wheel filenames not seen (page truncated) | [10] | true (as stated) |
| Elmer latest release | v26.2 (28 Apr), v26.2.1 correction (29 Apr); GPL v2 / LGPL v2.1 | - | year 2026 inferred from page context, not printed; release asset names did not load | [11][13] | true (version, day); inferred (year) |
| Elmer on macOS | source build: Homebrew gcc + cmake (+ open-mpi); ElmerGUI needs Qt4 from a third-party tap | - | page warns "instructions may be out of date"; arm64 not mentioned | [12] | true |
| Elmer macOS CI | workflow `build-macos-homebrew.yaml` exists in the repo | - | workflow content and pass status not read | [14] | true |
| Elmer Homebrew formula / conda-forge package | `formulae.brew.sh/formula/elmerfem` and `anaconda.org/conda-forge/elmerfem` both returned 404 | - | a package under another name is not excluded | this session | true (404s observed) |
| Elmer Docker | `docker/elmer.dockerfile`: `FROM ubuntu:latest`, MPI + MUMPS on, Hypre and GUI off, no arch restriction | - | arm64 build not tested | [16b] | true |
| DOLFINx (FEniCSx) conda-forge | 0.11.0 (page updated 2026-06-23); osx_arm64 builds for py3.11/3.12 x mpich/openmpi x real/complex; LGPL-3.0-or-later | - | - | [17][18] | true |
| DOLFINx Docker | images support arm64 and amd64; real/complex switch scripts | - | - | [19] | true |
| Firedrake | docs for 2026.10.1.dev0; ARM Macs officially supported; Homebrew deps + own PETSc build + pip; complex via `--scalar-type complex` | - | - | [20] | true |
| MEEP (pymeep) | 1.35.0 on conda-forge (page updated 2026-10-09), GPL-2.0-or-later | - | - | [21] | true |
| MEEP platforms | docs: binary serial and parallel packages for Linux and macOS, x86 and ARM; feedstock builds osx_arm64 (mpich, nompi; py3.11-3.14) | - | - | [22][23] | true |
| openEMS on macOS | Homebrew formula declared broken and unmaintained; manual build required | - | - | [24] | true |
| Palace (AWS, MFEM-based) | Spack or source; aarch64 BLAS covered; macOS not mentioned on install page | - | macOS status unknown | [25] | true (as stated) |
| Cantera | 3.2.0; BSD-3-Clause; pip wheels for Python 3.10-3.14 | - | arm64 wheel filename for 3.2.0 not seen (2.6.0 had `macosx_11_0_arm64`) | [26][27][28] | true |
| Cantera conda-forge | osx_arm64 built for Python 3.10-3.14 | - | - | [29] | true |
| Cantera bundled mechanisms | 23 YAML files; none named for sulfur (gri30, h2o2, air, nasa_gas, ...) | - | file contents not opened | [30] | true |
| RMG-database sulfur kinetics libraries | 12 folders incl. GlarborgBozzelli, GlarborgH2S, GlarborgMarshall, GlarborgNS, Sendt | - | licence and format not confirmed | [31] | true |
| ck2yaml | converts Chemkin-II input + thermo (+ transport) to Cantera YAML | - | - | [32] | true |
| Reaktoro (aqueous equilibrium/kinetics) | 2.13.0 on conda-forge, LGPL-2.1-only | - | osx-arm64 build not confirmed | [33] | true |
| preCICE (Homebrew) | 3.4.1, arm64 bottles, LGPL-3.0-or-later; deps open-mpi, petsc, python@3.14 | - | - | [34] | true |
| preCICE adapters | OpenFOAM, FEniCS/FEniCSx, CalculiX, deal.II, code_aster, DuMuX, DUNE, G+Smo, Nutils, SU2; Elmer not listed | - | - | [35] | true |
| Elmer<->OpenFOAM file coupling | modules Elmer2OpenFoamIO / OpenFOAM2ElmerIO; one scalar field; file IO; serial interpolation | - | - | [15] ch. 66 | true |
| EOF-Library (Elmer<->OpenFOAM, MPI) | GPL-3.0; Docker tag `eof_elmer84_of6`; manual install Linux only | - | version age inferred from tag | [36] | true |
| ParaView | 6.2.0, `ParaView-6.2.0-MPI-OSX11.0-Python3.12-arm64.dmg` | - | - | [37] | true |
| Blender | 5.2.2 arm64 (`blender-5.2.2-macos-arm64.dmg`) | - | - | [38] | true |
| PyVista | 0.49.0, MIT, Python >=3.10, vtk >=9.3.1,<9.8 | - | - | [39] | true |
| PyVista glTF export | `Plotter.export_gltf`; VTK exporter handles PolyData only | - | - | [40] | true |
| PyVista HTML export | `export_html` needs trame; deprecated since 0.49.0 in favour of `plotter.trame.export_html` | - | - | [41] | true |
| three.js | `three` 0.186.1, MIT | - | - | [42] | true |
| vtk.js | `@kitware/vtk.js` 37.4.1, BSD-3-Clause; readers named: obj, stl, vtp, vti | - | - | [43][44] | true |

### 2.2 Solver capability facts

| name | value | unit | uncertainty | source | verified |
|---|---|---|---|---|---|
| interFoam scope | transient, 2 incompressible, isothermal, immiscible phases | - | page does not mention species or reactions | [45] | true |
| icoReactingMultiphaseInterFoam scope | N incompressible, non-isothermal immiscible fluids with phase change, VOF | - | no species/reaction statement in header; open user bug reports on condensation (search result only) | [46] | true |
| Foundation `incompressibleVoF` | 2 incompressible isothermal immiscible fluids (supersedes interFoam) | - | - | [47][48] | true |
| Foundation `compressibleVoF` | 2 compressible non-isothermal immiscible fluids | - | no species/reactions stated | [47][48] | true |
| Foundation `multiphaseEuler` | any number of compressible phases, common pressure; optional multiple species, in-phase reactions, momentum/heat/mass transfer | - | Euler-Euler, not sharp-interface VOF | [48] | true |
| `multiphaseEuler` tutorials | include bubbleColumnEvaporatingDissolving, bubbleColumnEvaporatingReacting | - | physics inferred from names; case files not opened | [49] | true |
| Foundation `foamMultiRun` | runs any modular solver across multiple regions (conjugate heat transfer with `solid`) | - | - | [47] | true |
| Elmer Models Manual | dated 20 Jan 2026, for Elmer 26.1; chapters: Heat (1), Navier-Stokes (2), Advection-Diffusion (3), Linear Elasticity (6), Helmholtz (12), Linearized N-S frequency domain (13), Wave Equation (14), Electrostatics (16), Static Current Conduction (17), Vectorial Helmholtz for EM waves (20), Electromagnetic Waves (21), Level-Set (32), Elmer-OpenFOAM file IO (66) | - | - | [15] | true |
| Elmer piezoelectric support | test case `fem/tests/piezo`: StatElecSolve + Stress Analysis, `Piezo Material = True`, `Piezo Material Coefficients(2,4)`, 2D, steady state | - | absent from the Electrostatics chapter (read in full) and the Linear Elasticity theory pages 52-54; the elasticity keyword pages 55-59 were not read, so it may be documented there; harmonic/3D use not confirmed | [16][15] | true |
| DOLFINx demos | Helmholtz (real and complex); EM scattering with PML; waveguide modes; elasticity; Stokes; DG Navier-Stokes | - | no ready-made piezo or VOF demo listed | [19b] | true |

### 2.3 Geometry figures used for mesh sizing

| name | value | unit | uncertainty | source | verified |
|---|---|---|---|---|---|
| Pyramid height / base (muography paper) | 139 / 230 | m | rounded | [51] | true |
| Grand Gallery | 8.6 high x 46.7 long x 2.1 to 1.0 wide | m | - | [51] | true |
| Grand Gallery roof length (Petrie) | 1838.6 sloping (= 46.70 m) | in | - | [53] sec. 46 | true |
| Antechamber | 116.30 x 65.00 x 149.35 (= 2.954 x 1.651 x 3.793 m) | in | Petrie gives +/- on individual readings | [53] sec. 48 | true |
| King's Chamber | 412.4 x about 206.2; height about 235 by subtraction (= 10.47 x 5.24 x 5.97 m) | in | height is derived from floor/ceiling levels, not stated directly | [53] sec. 51-52 | true (L, W); derived (H) |
| Queen's Chamber | 205.85 x 226.47; walls 184.47, ridge 245.1 (= 5.23 x 5.75 x 4.69 to 6.23 m) | in | - | [53] sec. 41 | true |
| King's Chamber air channels | about 8.4-9.2 wide x 8.7-8.9 high (= about 0.22 m square) | in | - | [53] sec. 56 | true |
| Queen's Chamber channels | about 8 x 8.6; first 76-80 in horizontal | in | - | [53] sec. 44 | true |
| Big Void | length > 30 m; cross-section similar to Grand Gallery; about 21 m above ground (centre 40-50 m above Queen's Chamber floor) | m | shape and inclination unknown | [51] | true |
| North Face Corridor | about 9 m long, about 2.0 x 2.0 m section; bottom about 20 m above ground | m | Nagoya: 9.06 +/- 0.07 long; CEA: 9.23 +/- 0.48 | [52] | true |
| Balezin model: pyramid | height 138.75, base 230 | m | idealised pointed pyramid | [50] | true |
| Balezin model: "King's Chamber" | 11 x 5 x 11; centre 5 m off axis, 40.5 m above base | m | idealised | [50] | true |
| Balezin model: "Queen's Chamber" | 5 x 5 x 6; centre 2.5 m off axis, 20.8 m above base | m | idealised | [50] | true |
| Balezin model: permittivity | 5 + 0.1i for pyramid and substrate (literature range 4-6 cited) | - | authors found no measured Giza data | [50] | true |
| Balezin model: wavelength range | 200-600 | m | - | [50] | true |
| Balezin model: resonances, free space | about 333 and about 230 | m | read from text | [50] | true |
| Balezin model: resonance, on substrate | one broad maximum about 250 | m | - | [50] | true |
| Balezin model: incident field | 1 V/m plane wave, x-polarised, along the axis | V/m | linear model | [50] | true |
| Muon forward model densities | limestone 2.2, granite 2.75 around King's Chamber | g/cm3 | [52] tested 1.8-2.6 and kept 2.2 | [51][52] | true |
| Muon forward model code | Geant4 10.2 (2017); Geant4 10.4.2 plus two fast in-house simulators (2023) | - | - | [51][52] | true |

### 2.4 Derived sizing (my arithmetic; inputs above)

| name | value | unit | uncertainty | source | verified |
|---|---|---|---|---|---|
| Volume: Grand Gallery | about 620 (8.6 x 46.7 x mean width 1.55) | m3 | trapezoid idealisation, +/- 15% | computed from [51] | derived |
| Volume: King's Chamber | about 328 | m3 | - | computed from [53] | derived |
| Volume: Queen's Chamber | about 164 | m3 | gable idealised | computed from [53] | derived |
| Volume: Antechamber (gross box) | about 18.5 | m3 | ignores granite leaf and wainscots | computed from [53] | derived |
| Sum of four chambers | about 1,130 | m3 | - | sum | derived |
| Design fluid volume incl. passages and shafts | 1,500 (allowance) | m3 | passages not sourced this session; +/- 30% | assumption | false |
| Cells, uniform 10 cm | 1.5 | million | scales with volume | 1500 / 0.1^3 | derived |
| Cells, uniform 5 cm | 12 | million | - | 1500 / 0.05^3 | derived |
| Cells, uniform 2.5 cm | 96 | million | - | 1500 / 0.025^3 | derived |
| Cells, uniform 2 cm | 188 | million | - | 1500 / 0.02^3 | derived |
| OpenFOAM memory rule of thumb | 1 to 2 | GB per million cells | forum posts for icoFoam (about 1) and general (about 2); threads returned HTTP 403, seen only as search snippets | [59] | false |
| Memory at 10 cm / 5 cm / 2.5 cm | 1.5-3 / 12-24 / 96-192 | GB | from the unverified rule | derived | false |
| Cells across a 0.22 m air shaft at 10 / 5 / 2.5 cm | 2 / 4 / 9 | cells | need about 8-10 for a pipe-flow profile (engineering practice, not sourced) | derived | false |
| Speed of sound in air | 343 | m/s | standard 20 C value, not fetched | textbook | false |
| Acoustic nodes, antechamber, 10 nodes per wavelength | 4.6e5 at 1 kHz; 5.7e7 at 5 kHz; 3.7e9 at 20 kHz | nodes | scales with f^3 | 18.5 / (c/10f)^3 | derived |
| Acoustic nodes, King's Chamber, 10 per wavelength | 6.5e4 at 200 Hz; 8.1e6 at 1 kHz; 6.5e10 at 20 kHz | nodes | - | 328 / (c/10f)^3 | derived |
| EM reproduction (Balezin) mesh | order 1e5 tetrahedra (lambda/10 = 9 m in rock, 20 m in air, box about 830 x 830 x 740 m) | elements | chambers refined to about 1 m add little | derived from [50] | derived |

Reading of the derived rows: a 10 cm base mesh refined twice near shafts, the antechamber slots and the free surface (to 2.5 cm) is the practical target; my estimate is 3-8 M cells and well under 20 GB if the 1-2 GB per million rule holds. That rule must be measured on a small case before committing.

---

## 3. Claim-by-claim assessment (tooling-relevant claims)

Status vocabulary: SUPPORTED / PARTLY SUPPORTED / CONTRADICTED / NO EVIDENCE EITHER WAY / NOT DEFINED BY THE HYPOTHESIS.

1. **"They created a model of the Great Pyramid in COMSOL Multiphysics with radio-wavelength input."** SUPPORTED with a correction. The paper used CST Microwave Studio and COMSOL independently and a discrete-dipole code as a third check; the plotted fields come from CST. Wavelengths were 200-600 m [50].

2. **"The electric field concentrates directly around the King's Chamber and antechamber when the wave comes from above."** PARTLY SUPPORTED. In the free-space case, at the shorter wavelengths (230 m, 200 m) the electric-field maximum moves to the pyramid centre and the paper reports accumulation in the King's Chamber. But (a) the antechamber is not in the model; (b) in the case the authors call more realistic, with a substrate, the pyramid mostly scatters the wave into the ground and the field maxima sit just under the base; chamber intensities there are a few times the incident intensity; (c) it is a linear scattering result for a 1 V/m plane wave, not a statement about lightning [50].

3. **"With the vector from below, an intense field builds at the top and excludes the capstone; this substantiates telluric charging."** Three parts, three statuses [50].
   - The observation: SUPPORTED. For a wave incident from the base side the paper reports the electric field concentrating in the apex region, with no accumulation in the King's Chamber. Scope: this is the free-space case only (pyramid in homogeneous space, no ground); the substrate case was run only with incidence from above.
   - "Excludes the capstone": NO EVIDENCE EITHER WAY. The model is an idealised pointed pyramid 138.75 m high. A capstone was never modelled and the paper says nothing about one.
   - "Substantiates telluric charging / a lightning target": NO EVIDENCE EITHER WAY. A radio-frequency plane wave is a different physical source from a near-DC ground current, so the result neither supports nor refutes it. It needs its own conduction model (claim 5).

4. **"The model used limestone with a dielectric constant of seven; red granite is nine."** CONTRADICTED for the first part: the paper used 5 + 0.1i, citing a literature range of 4-6, and has no granite in it [50]. The granite value is NO EVIDENCE EITHER WAY in this file (belongs to the materials domain).

5. **"It is a simple modification to change the input vector to telluric voltage from below or high-voltage lightning from above."** CONTRADICTED as "simple", SUPPORTED as "possible". Near-DC ground current is a conduction problem (Laplace equation in conductivity), not a wave-scattering problem; lightning is a transient current source needing either a time-domain full-wave solve or an electro-quasi-static solve with conductivity. Both need conductivities that the 2018 model does not contain, and neither inherits its resonances. Open tools exist for both (Elmer static current conduction [15]; FEniCSx; MEEP time domain [22]). The outcome is not predictable from the published result.

6. **"Someone with COMSOL could very easily model this entire system."** PARTLY SUPPORTED. Each sub-physics has a working open solver on this machine (section 2). Three parts cannot be run as stated: the "acoustic catalyst" has no stated mechanism or rate law (NOT DEFINED); ultrasonic acoustics in air at chamber scale exceeds 36 GB by orders of magnitude (section 2.4); pump, valve and seal geometry and all cycle times are unspecified (NOT DEFINED).

7. **"Lowering the water in the Grand Gallery pulls air down the shafts and gas through the antechamber grooves, like a syringe."** NO EVIDENCE EITHER WAY; directly testable. A two-phase VOF run (interFoam class [45]) with the shafts as open boundaries answers it. It depends on parameters the hypothesis does not give: drain rate, leak-tightness of every other opening (ascending passage, Queen's Chamber passage, well shaft), and the flow area of the antechamber path.

8. **"The gas does not get pushed back when the water rises because it dissolves immediately."** NO EVIDENCE EITHER WAY; testable but not with a stock VOF solver. It needs interphase species transfer with a solubility law and liquid-side reaction. Stock options: Foundation `multiphaseEuler` [48][49]; otherwise a custom extension. Note for the model set-up: the drawn-in gas is mostly air, and the hypothesis does not say where the non-reacting part goes when the level rises (NOT DEFINED).

9. **"Four pump activations fill the Grand Gallery; slow filling controls the reaction."** NOT DEFINED quantitatively. A stroke would have to displace on the order of 150 m3 (620 m3 / 4, from section 2.4) plus dead volume. Pump geometry, stroke time and sealing are not given, so the simulation must treat them as swept parameters.

10. **"The red granite produces ultrasound under an electric field (inverse piezoelectric effect), which converts SO2 and O2 to SO3."** Tooling view only: the electro-elastic-acoustic part is computable given a piezoelectric tensor for the rock (Elmer has a piezo keyword in a test case [16]; FEniCSx can assemble the coupled form). The chemical step is NOT DEFINED: no solver can evaluate a rate enhancement that has no stated mechanism. A neutral test is possible by asking the inverse question: what rate multiplier would be required, and is the computed acoustic energy density anywhere near what sonochemistry literature needs (other domain files).

11. **"The Big Void is a heat exchanger (about 30 percent probability by the speaker's own estimate)."** NOT DEFINED. The muon data give a void more than 30 m long with a Grand-Gallery-like cross-section and no known connection [51]. Without a stated fluid path it can only be modelled as conduction through masonry (conjugate heat transfer, e.g. `foamMultiRun` with `solid` [47]).

12. **"The Queen's Chamber shaft block with copper pins is an ultrasonic flow meter."** NOT DEFINED (offered as speculation in the source). No frequency, signal path or receiver is specified.

13. **Implicit claim that a 3D animation demonstrates feasibility.** NO EVIDENCE EITHER WAY. An animation carries no conservation laws. The simulation proposed here is the first quantitative test.

---

## 4. What a simulation of this domain needs

### 4.1 Governing equations mapped to solvers

| step in the hypothesis | equations | candidate solver on this Mac | size on this Mac |
|---|---|---|---|
| Water filling/draining, syringe draw of gas | incompressible (or weakly compressible gas) two-phase Navier-Stokes + volume-fraction transport; gravity; surface tension negligible at this scale | OpenFOAM v2606 `interFoam` / `compressibleInterFoam` (native app [1]); Foundation `incompressibleVoF` / `compressibleVoF` (VM [3]) | 3-8 M cells, fits |
| Gas mixing and species transport | species advection-diffusion in gas; buoyancy (SO2 is denser than air) | Foundation `multicomponentFluid` (single phase) [47]; passive scalars in a VOF solver | fits |
| Absorption into rising water with reaction | interfacial solubility jump + mass-transfer + liquid reaction source | Foundation `multiphaseEuler` [48][49]; or custom VOF + species-transfer solver | fits; development effort is the cost |
| Heat release and conduction into masonry | energy equation, conjugate heat transfer | `foamMultiRun` + `solid` [47]; Elmer HeatSolve [15]; FEniCSx | fits |
| RF scattering (Balezin reproduction) | time-harmonic Maxwell, open boundary (PML) | FEniCSx complex build [17][19b]; Elmer VectorHelmholtz [15]; MEEP FDTD [22] | order 1e5 elements, trivial |
| Lightning transient | Maxwell in time domain with conductivity, or electro-quasi-static continuity equation | MEEP [22]; Elmer EM Waves / static current [15]; FEniCSx | fits at metre resolution |
| Telluric / ground current | steady conduction, div(sigma grad phi) = 0 | Elmer Static Current Conduction [15]; FEniCSx | trivial |
| Inverse piezoelectric response of granite | coupled linear elasticity + electrostatics with piezo tensor | FEniCSx (write the mixed form); Elmer StressSolve + StatElecSolve with Piezo keywords [16] | fits |
| Sound in chamber air | Helmholtz (frequency domain) or wave equation | Elmer HelmholtzSolve [15]; FEniCSx Helmholtz demo [19b] | audio range only; ultrasound infeasible |
| Gas-phase kinetics / equilibrium | stiff ODE system, 0-D or 1-D reactors | Cantera 3.2.0 [26] + converted sulfur mechanism [31][32] | trivial |
| Aqueous chemistry and limestone attack | speciation + mineral kinetics | Reaktoro [33]; Cantera with a custom YAML | trivial |

### 4.2 Boundary and initial conditions that the tooling must be able to express

- Shaft outlets: total-pressure inlet/outlet open to atmosphere (OpenFOAM `totalPressure` / `pressureInletOutletVelocity` class of conditions; not checked in docs this session).
- Water inlet/outlet: time-varying flow rate or hydrostatic head from an external reservoir level; this is where the undefined pump enters, as a parameter.
- Walls: no-slip; optional leak-path patches with a prescribed loss coefficient to represent imperfect seals.
- Gas source in the King's Chamber: prescribed SO2 mass flow or initial concentration field.
- EM: plane-wave port + PML (validation case); current-injection boundary at apex and remote ground (lightning); potential difference across the ground block (telluric).
- Piezo: electric potential mapped from the EM step; free or roller mechanical boundaries on the granite blocks.
- Acoustic: wall-normal velocity mapped from the solid step; impedance walls.
- Kinetics: temperature, pressure and composition taken from CFD probes.

### 4.3 Key dimensionless numbers (to be computed once parameters exist)

- Reynolds and Froude numbers of the filling/draining flow; Courant number (sets the VOF time step).
- Bond/Weber number (confirms surface tension is negligible at metre scale).
- Richardson or densimetric Froude number for the dense-gas layer.
- Peclet number for gas mixing; Hatta number and Damkohler number for absorption with reaction.
- Biot/Fourier numbers for heat soak into masonry.
- Electrical size L/lambda (decides quasi-static versus full-wave); charge relaxation time epsilon/sigma against the source rise time.
- Helmholtz number k*a and elements per wavelength for acoustics (sets feasibility, section 2.4).

### 4.4 Coupling verdict

The causal chain in the hypothesis runs one way. Flow does not feed back on the electromagnetic field, and chemistry does not feed back on the acoustics at first order. Therefore:

- Solve piezo + elasticity (and, where affordable, acoustics) monolithically inside one FEM code.
- Solve flow + species + heat inside one OpenFOAM solver.
- Pass fields between codes as files (VTK/XDMF, interpolated with PyVista or meshio; meshio not checked this session). Elmer documents exactly this for OpenFOAM [15] ch. 66.
- Use preCICE [34] only if a later question requires feedback (for example acoustic streaming driving gas mixing while the level moves). It has OpenFOAM and FEniCSx adapters but none for Elmer [35].

### 4.5 Pass/fail criteria for the tooling layer (proposed, not sourced)

1. **EM validation gate**: reproduce Balezin free-space extinction peaks at about 333 m and 230 m and the single broad substrate maximum near 250 m [50], with two different codes (for example FEniCSx and MEEP) agreeing with each other. Suggested tolerance: peak wavelength within 5 percent.
2. **CFD verification gate**: global mass conservation error below 0.1 percent per cycle; grid-convergence index below 5 percent on gas volume drawn per drain stroke across three meshes; a U-tube/syringe case checked against the hydrostatic analytic answer.
3. **Kinetics gate**: converted sulfur mechanism reproduces a published SO2 oxidation data set (data to be supplied by the chemistry domain file) before it is used.
4. **Geometry gate**: parametric CAD chamber dimensions within survey uncertainty of [53]; optional muon-opacity projection of the CAD (straight-line density integrals) compared qualitatively with published radiographs [51][52].
5. **Hypothesis-level outcome metrics** (the simulation can come out either way): fraction of gas drawn through the antechamber path versus other openings; fraction of SOx absorbed versus expelled per fill stroke; electric field and strain in the granite per unit source current; acoustic pressure in the antechamber at the frequencies that can be resolved; required versus available rate enhancement for SO2 to SO3.

---

## 5. Candidate stacks

### Stack A - Native-first hybrid (recommended starting point)
- CAD/mesh: build123d (or CadQuery, not both in one environment [8][9]) + gmsh from pip into a uv venv on Python 3.12 [6].
- Flow: OpenFOAM v2606 through OpenFOAM.app via Homebrew tap [1].
- EM/piezo/acoustics/heat: FEniCSx from conda-forge, complex build [17][18]; MEEP from conda-forge as an independent time-domain check [21][23].
- Kinetics: Cantera 3.2.0 [26] + RMG sulfur library converted [31][32].
- Visualisation: ParaView 6.2.0 arm64 [37], PyVista [39], glTF to three.js [40][42].
- Coupling: files.
- For: everything native arm64, no VM memory split, fewest moving parts. Against: ESI-line VOF solvers lack species transfer and reaction, so claim 8 needs custom solver work; FEniCSx requires writing the piezo and acoustic weak forms; conda (miniforge) must be added because FEniCSx and MEEP are not on PyPI in a supported form (not checked for PyPI wheels this session). Risks: OpenFOAM.app is a community build, unnotarized, Apple Clang.

### Stack B - Linux VM with Foundation OpenFOAM and Elmer
- Flow and absorption: OpenFOAM Foundation v14 in the official Multipass Ubuntu arm64 VM [2][3], using `incompressibleVoF`/`compressibleVoF` for hydraulics and `multiphaseEuler` for species, reaction and mass transfer [48][49].
- EM/piezo/acoustics/heat: Elmer 26.2 built in the same Ubuntu environment (its Dockerfile recipe: MPI + MUMPS [16b]) for its ready-made modules [15].
- Kinetics, CAD, visualisation: as Stack A on the host.
- For: widest out-of-the-box physics coverage; Linux arm64 is the mainstream build target for both codes. Against: the VM must be given a fixed share of the 36 GB; shared-folder I/O; `multiphaseEuler` is Euler-Euler rather than sharp-interface; Elmer piezo is documented only by a 2D steady test case [16]. Risks: Elmer arm64 Linux build not confirmed this session.

### Stack C - Containerised, pinned images
- `opencfd/openfoam-default:2512` (linux/arm64) [5], `dolfinx/dolfinx:stable` (arm64, complex switch) [19], Elmer from its Dockerfile [16b], preCICE available if needed [34].
- For: reproducible, versions pinned, easiest to hand to another machine or cloud node when 36 GB runs out. Against: only the Docker CLI is present, so a container engine must be added first; newest ESI image is one release behind; GUI tools still run on the host; same memory-split and bind-mount costs as Stack B.

### Recommendation
Start with Stack A and keep the tool count minimal: build123d + gmsh, OpenFOAM.app v2606, FEniCSx, Cantera, ParaView/PyVista. Run the Balezin reproduction and the pure-hydraulics syringe test first, because both are well defined and can already falsify or support claims 2, 3 and 7. Add the Foundation v14 VM from Stack B only when the absorption question (claim 8) is reached and a custom species-transfer extension of interFoam looks more expensive than running `multiphaseEuler`. Skip preCICE, Elmer, openEMS and Blender until a specific question needs them. Do not attempt ultrasonic full-wave acoustics in air; bound it analytically and resolve only the audio-range modes.

---

## 6. Existing models and prior simulations

| item | what it is | licence / availability | use here |
|---|---|---|---|
| Balezin et al. 2018, J. Appl. Phys. 124, 034903 [50] | RF scattering model (CST, COMSOL, DDA); geometry and material fully stated in text | paper copyright AIP; model not distributed but reproducible from the text | EM validation case |
| Morishima et al. 2017, Nature 552, 386 (arXiv:1711.01576) [51] | Big Void discovery; Geant4 10.2 forward model; known chambers modelled from Dormion's survey | arXiv preprint readable; 3D model and data not public | geometry cross-check; muon forward-model recipe |
| Procureur et al. 2023, Nat. Commun. 14 [52] | North Face Corridor; Geant4 10.4.2 + fast simulators; 3D model from laser scans and photogrammetry (Cairo Univ., HIP, Emissive) | article CC BY 4.0; raw data from authors subject to Egyptian ministry approval; code on request | geometry cross-check |
| Bross et al. 2022, arXiv:2202.08184 [55] | proposed muon tomography of the Great Pyramid | preprint; simulation details not read (abstract only) | possible forward-model reference |
| Fermilab workshop slides on a Khufu interior CAD model [60] | interior CAD for muon simulation | could not open (HTTP 403) | unverified lead |
| SketchUp 3D Warehouse "Great Pyramid - Grande pyramide - Khufu (Cheops)" by stahlmanDesign [56] | interior chambers and shafts, stated as based on Gantenbrink's measurements; 2,913 polygons; modified 2014 | no model-specific licence stated; Trimble terms apply | visual reference only; not survey grade |
| Sketchfab "The Great Pyramid of Giza" by ianicolo [57] | photogrammetry from video; 360k triangles | CC BY 4.0, downloadable | exterior context only (interior not indicated) |
| Harvard Giza Project "Giza 3D" [58] | curated models incl. a Khufu pyramid model | no downloads stated; all rights reserved | reference only |
| Petrie 1883, "The Pyramids and Temples of Gizeh", ch. 7 (web transcription) [53] | primary survey dimensions | 1883 text; licence of the transcription not checked | basis for parametric CAD |
| Landreau et al. 2024, PLoS ONE 19(8) e0306690 [54] | hydraulic-lift hypothesis for Djoser's Step Pyramid; simple numerical lift model in R, no CFD | CC BY 4.0; code on request | closest peer-reviewed precedent for pyramid hydraulics modelling |
| Airflow/thermal CFD of the Great Pyramid interior | - | not found in two searches | open question |
| Cadman subterranean-chamber pump scale models | physical models, 1999-2000 | only secondary/promotional descriptions found; no measured data | not usable as validation |
| Gantenbrink "Upuaut" shaft CAD drawings (historically cheops.org) | robot survey drawings of the shafts, cited by the SketchUp model | not found: the domain now serves unrelated content | open lead |
| GeoChemFoam 5.1 [61] | OpenFOAM-based reactive multiphase package; README cites a VOF species-transfer scheme | GPL-3.0; OpenFOAM version, platform and solver names not stated in README | candidate for claim 8, unconfirmed |

---

## 7. Open questions

1. Does Elmer 26.2 build and pass its tests on macOS arm64? A Homebrew CI workflow exists [14] but its status was not read, and the macOS instructions say they may be out of date [12].
2. Which container/VM engine will be used? Only the Docker CLI is present. Stack B and C depend on this and on how much of the 36 GB is given to the guest.
3. Real OpenFOAM memory per million cells for the chosen solver on this machine. The 1-2 GB figure is from forum posts I could not open [59]; measure on a 1 M and 2 M cell case.
4. Sharp-interface VOF with dissolved species and reaction: choose between Foundation `multiphaseEuler` and a custom/community species-transfer solver. I did not confirm a maintained community solver that builds against v2606. GeoChemFoam 5.1 is GPL-3.0 and cites a VOF species-transfer scheme, but its README does not state the OpenFOAM version it needs, its solver names or its platforms [61].
5. Sulfur kinetics: format and licence of the RMG sulfur libraries [31], and whether any published low-temperature gas-phase or aqueous S(IV) oxidation mechanism is downloadable in Chemkin or Cantera form. Not found this session.
6. Passage, well-shaft, subterranean-chamber and shaft-length dimensions were not sourced here; the 1,500 m3 design volume is an allowance. The geometry domain file should supply them.
7. No openly licensed, survey-grade 3D model of the interior was found. Is the ScanPyramids/Dassault model obtainable on request?
8. Piezoelectric tensor for Aswan granite (a rock with randomly oriented quartz grains) is required before the piezo step can be run; without it the step is a parameter sweep.
9. The hypothesis does not define: acoustic frequency, the catalytic mechanism, pump and valve geometry, cycle times, seal locations, SO2 supply rate, or where the non-reacting gas goes. Each must be an explicit swept parameter or the corresponding claim stays untestable.
10. No airflow or thermal CFD of the Great Pyramid interior was found for validation; measured shaft airflow or chamber temperature data would have to come from conservation literature.
11. arm64 wheel availability for the newest cadquery-ocp 8.x and for Cantera 3.2.0 on PyPI was not seen directly (pages truncated); conda-forge builds are confirmed for Cantera [29].
12. Inference not verified: the Homebrew bottle label "golden gate" [7][34][37] corresponds to this machine's macOS (Darwin 27).

---

## 8. Sources

All opened 2026-10-09/10 unless marked "not opened".

1. OpenFOAM.app (gerlero), README. https://github.com/gerlero/openfoam-app
2. OpenFOAM Foundation download page. https://openfoam.org/download/
3. OpenFOAM 14 for macOS. https://openfoam.org/download/14-macos/
4. OpenFOAM v2606 release announcement. https://www.openfoam.com/news/main-news/openfoam-v2606
5. Docker Hub, opencfd/openfoam-default tags. https://hub.docker.com/r/opencfd/openfoam-default/tags
6. gmsh on PyPI. https://pypi.org/project/gmsh/
7. gmsh Homebrew formula. https://formulae.brew.sh/formula/gmsh
8. build123d PyPI metadata. https://pypi.org/pypi/build123d/json
9. CadQuery PyPI metadata. https://pypi.org/pypi/cadquery/json
10. cadquery-ocp PyPI metadata. https://pypi.org/pypi/cadquery-ocp/json
11. Elmer FEM repository README. https://github.com/ElmerCSC/elmerfem
12. Elmer macOS compilation instructions. https://github.com/ElmerCSC/elmerfem/blob/devel/compilation_instructions/macOS.md
13. Elmer releases. https://github.com/ElmerCSC/elmerfem/releases
14. Elmer CI workflows. https://github.com/ElmerCSC/elmerfem/tree/devel/.github/workflows
15. Elmer Models Manual, 20 January 2026 (for Elmer 26.1); read: contents, ch. 1, 6 (pp. 52-54), 16, 66. https://www.nic.funet.fi/pub/sci/physics/elmer/doc/ElmerModelsManual.pdf
16. Elmer piezo test case. https://github.com/ElmerCSC/elmerfem/tree/devel/fem/tests/piezo and https://raw.githubusercontent.com/ElmerCSC/elmerfem/devel/fem/tests/piezo/piezo.sif
16b. Elmer Dockerfile. https://raw.githubusercontent.com/ElmerCSC/elmerfem/devel/docker/elmer.dockerfile
17. fenics-dolfinx on conda-forge. https://anaconda.org/conda-forge/fenics-dolfinx
18. fenics-dolfinx feedstock (build matrix). https://github.com/conda-forge/fenics-dolfinx-feedstock
19. DOLFINx README (install routes, Docker). https://github.com/FEniCS/dolfinx
19b. DOLFINx demos. https://docs.fenicsproject.org/dolfinx/main/python/demos.html ; installation notes https://docs.fenicsproject.org/dolfinx/main/python/installation.html
20. Firedrake installation. https://www.firedrakeproject.org/install.html
21. pymeep on conda-forge. https://anaconda.org/conda-forge/pymeep
22. MEEP installation docs. https://meep.readthedocs.io/en/latest/Installation/
23. pymeep feedstock (build matrix). https://github.com/conda-forge/pymeep-feedstock
24. openEMS ready-made packages page. https://docs.openems.de/en/latest/install/package.html (index: https://docs.openems.de/en/latest/install/index.html)
25. Palace installation. https://awslabs.github.io/palace/stable/install/
26. Cantera 3.2.0 install overview. https://cantera.org/stable/install/index.html
27. Cantera pip install page. https://cantera.org/stable/install/pip.html
28. Cantera PyPI metadata. https://pypi.org/pypi/Cantera/json
29. cantera feedstock (build matrix). https://github.com/conda-forge/cantera-feedstock
30. Cantera bundled data directory. https://github.com/Cantera/cantera/tree/main/data
31. RMG-database sulfur kinetics libraries. https://github.com/ReactionMechanismGenerator/RMG-database/tree/main/input/kinetics/libraries/Sulfur
32. Cantera ck2yaml tutorial. https://cantera.org/stable/userguide/ck2yaml-tutorial.html
33. Reaktoro on conda-forge. https://anaconda.org/conda-forge/reaktoro
34. preCICE Homebrew formula. https://formulae.brew.sh/formula/precice
35. preCICE installation overview. https://precice.org/installation-overview.html
36. EOF-Library. https://github.com/jvencels/EOF-Library
37. ParaView Homebrew cask. https://formulae.brew.sh/cask/paraview
38. Blender Homebrew cask. https://formulae.brew.sh/cask/blender
39. PyVista PyPI metadata. https://pypi.org/pypi/pyvista/json
40. PyVista Plotter.export_gltf. https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.export_gltf
41. PyVista Plotter.export_html. https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.export_html
42. three.js npm metadata. https://registry.npmjs.org/three/latest
43. vtk.js npm metadata. https://registry.npmjs.org/@kitware/vtk.js/latest
44. vtk.js documentation. https://kitware.github.io/vtk-js/docs/
45. OpenFOAM (ESI) interFoam documentation. https://doc.openfoam.com/2312/tools/processing/solvers/rtm/multiphase/interFoam/
46. OpenFOAM (ESI) API, icoReactingMultiphaseInterFoam. https://api.openfoam.com/2506/icoReactingMultiphaseInterFoam_8C.html
47. CFD Direct, modular solvers. https://cfd.direct/openfoam/free-software/modular-solvers/
48. OpenFOAM v13 User Guide, solver modules. https://doc.cfd.direct/openfoam/user-guide-v13/solvers-modules
49. OpenFOAM-dev multiphaseEuler tutorials. https://github.com/OpenFOAM/OpenFOAM-dev/tree/master/tutorials/multiphaseEuler
50. Balezin M., Baryshnikova K. V., Kapitanova P., Evlyukhin A. B. (2018). Electromagnetic properties of the Great Pyramid: First multipole resonances and energy concentration. J. Appl. Phys. 124, 034903. https://doi.org/10.1063/1.5026556 (all 7 pages of the published PDF read from a hosted copy; the publisher page returned HTTP 403).
51. Morishima K. et al. (2017). Discovery of a big void in Khufu's Pyramid by observation of cosmic-ray muons. Nature 552, 386-390. Read as arXiv:1711.01576v2, pp. 1-3, 5-6. https://arxiv.org/abs/1711.01576
52. Procureur S. et al. (2023). Precise characterization of a corridor-shaped structure in Khufu's Pyramid by observation of cosmic-ray muons. Nat. Commun. 14. https://doi.org/10.1038/s41467-023-36351-0 (read at https://pmc.ncbi.nlm.nih.gov/articles/PMC9981702/)
53. Petrie W. M. F. (1883). The Pyramids and Temples of Gizeh, ch. 7, web transcription. https://www.ronaldbirdsall.com/gizeh/petrie/c7.html (first 100,000 characters read via extraction; figures should be re-checked against the text by the geometry file)
54. Landreau X. et al. (2024). On the possible use of hydraulic force to assist with building the step pyramid of Saqqara. PLoS ONE 19(8): e0306690. https://doi.org/10.1371/journal.pone.0306690
55. Bross A. D. et al. (2022). Tomographic Muon Imaging of the Great Pyramid of Giza. arXiv:2202.08184 (abstract page only). https://arxiv.org/abs/2202.08184
56. SketchUp 3D Warehouse model by stahlmanDesign. https://embed-3dwarehouse-classic.sketchup.com/model/fc021e56e7a7dc2cc734a011697d5590/Great-Pyramid-Grande-pyramide-Khufu-Cheops
57. Sketchfab model by ianicolo. https://sketchfab.com/3d-models/the-great-pyramid-of-giza-4a251113722f4d969b6cf2ca5f35c502
58. Harvard Giza Project, Giza 3D. https://giza.fas.harvard.edu/giza3d/
59. CFD Online forum threads on RAM per million cells (HTTP 403; seen only as search-result snippets, not opened). https://cfd-online.com/Forums/openfoam-solving/153523-question-ram.html ; https://www.cfd-online.com/Forums/main/192759-ram-large-number-cells-cfd-simulation.html
60. Fermilab workshop presentation on Khufu interior modelling (HTTP 403, not opened). https://indico.fnal.gov/event/45292/contributions/196203/attachments/134679/166762/Workshop_Presentation.pdf
61. GeoChemFoam 5.1 README. https://github.com/GeoChemFoam/GeoChemFoam-5.1

Transcripts consulted (local): History Drops clip part 1 and part 2 in full; Danny Jones full episode, lines 90-244 and a keyword scan of 00:00-1:37.
