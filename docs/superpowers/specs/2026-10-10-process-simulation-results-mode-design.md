# Process simulation and Results mode: design

Date: 2026-10-10. Status: draft for review.

## 1. Context

Plan A delivered a ledger of sourced quantities, a screening table of single-point calculations with verdicts, a parametric geometry, and a viewer that animates the cycle as the source video claims it. The viewer's fixed notice says, correctly, that the animation is not a simulation result. The project owner wants the viewer to show simulation results as well, because the work is meant to be a scientific contribution.

A screening calculation tests one number. A simulation solves the governing equations forward in time, so it can show how a process succeeds or fails: how high the water gets, what the liquid holds after an hour or a year, where the drawn gas comes from. This design adds that.

Decisions already made by the project owner:

- Results come from two sources built in parallel: this time-resolved process simulation of the whole cycle, and the field solvers of the piece 1 spec (sections 5.5 and 6). Both feed one Results mode in the viewer.
- The simulation runs with the tools already installed (Python, numpy, scipy).

## 2. Goals and non-goals

Goals:

1. A time-resolved model of the claimed cycle: water, gas, dissolved species, heat and wall chemistry, in the surveyed spaces.
2. Three readings of every run, as the piece 1 spec requires: literal (as stated), favourable (best physically admissible assumptions), and required (what an undefined input would have to be for a criterion to pass).
3. Uncertainty from the ledger's ranges on every reported result.
4. A verdict from the simulation for each claim the screening could not decide, against the criterion already committed for it.
5. A Results mode in the viewer that shows the computed state in the 3D model, with time series, the criterion, the verdict and the provenance of the run.

Non-goals:

- Three-dimensional flow or field solutions. Those are the field-solver plan and the later hydraulics piece; this model treats each space as well mixed and each opening as a link.
- New physical data. Every rate constant, property and dimension comes from the ledger; where the ledger lacks one, the plan adds a sourced entry or a swept, labelled assumption.
- Any change to the claim animation. The Claim mode stays as it is.

## 3. The model

### 3.1 Form

A compartment network. Each surveyed space is a node holding water, gas and dissolved species; each opening between spaces is a link with an elevation, an area and a loss coefficient from the ledger. The state is integrated in time with scipy's stiff solvers. Each physics is one module of pure functions from state to rates, so each can be tested alone:

```
pyramid/process/
  network.py      nodes, links, level-volume and surface-area curves from the geometry
  hydraulics.py   heads, link flows, check valves, pump, leak-off
  gas.py          gas inventories per node, flow through shafts and grooves as the liquid moves
  transfer.py     gas-liquid transfer across each free surface (two-film, Henry constants)
  aqueous.py      dissolved sulfur dioxide speciation, oxidation, pH
  gasphase.py     sulfur dioxide to trioxide, by the mechanism options of 3.3
  heat.py         energy balance and temperature
  wall.py         calcite attack and the growth of the gypsum layer
  cycle.py        the sequence of the claimed steps as boundary conditions
  run.py          cases, sweeps, outputs, manifest
```

### 3.2 State and equations

- **Water:** the volume in each node. Level follows from the geometry's level-volume curve; flow in a link follows from the head difference and the link's loss; a check valve passes one way only; leak-off through joints and stone uses the ledger's aperture and conductivity ranges.
- **Pump:** the hypothesis names no pump. The model imposes the claimed stroke as a moving boundary in the Descending Passage and reports the force, pressure and work it needs; it does not assume a device that could supply them.
- **Gas:** moles of sulfur dioxide, oxygen, nitrogen, sulfur trioxide and water vapour in the King's Chamber, the antechamber and the Gallery's gas space. Gas moves as the liquid volume changes, through every opening the survey records, in proportion to each opening's conductance. The share that arrives through the antechamber is an output.
- **Transfer:** each gas crosses the free surface at a rate set by its transfer coefficient, the surface area at the current level, and the Henry-law driving force.
- **Aqueous chemistry:** dissolved sulfur dioxide, bisulfite and sulfite in equilibrium; oxidation to sulfate by the ledger's rate laws, limited by dissolved oxygen; pH from charge balance.
- **Heat:** enthalpies of dissolution and reaction into the water's heat capacity, with conduction into the stone.
- **Walls:** acid consumed by calcite at the lesser of the surface rate and the transport rate through a gypsum layer that grows as it forms and redissolves on a fresh-water fill.

Mass of each element and total energy are conserved by construction and checked on every run.

### 3.3 Mechanism options for the gas-phase step

The claimed conversion of sulfur dioxide to trioxide in the antechamber has no known mechanism at the stated conditions. The model does not invent one. It runs three labelled options:

- **Literal:** the uncatalysed gas-phase rate from the ledger.
- **Assumed conversion:** a conversion fraction swept from 0 to 1, which shows what the rest of the chain would deliver if the step worked to that degree.
- **Nitrogen-oxide route:** the lead-chamber chemistry with the nitrogen-oxide level as a swept input, from the level lightning could supply to the level the route needs.

### 3.4 Undefined inputs

Every input the hypothesis leaves undefined (reservoir level, stroke time, drain time and path, gas fraction in the King's Chamber, cycle time, aeration) is a named parameter with a default taken from the research files' stated scenario, a range, and a label saying it is not specified by the hypothesis. Results report which of them a conclusion depends on.

## 4. Cases, uncertainty and verdicts

- **Cases:** `literal`, `favourable` and `required`, each a small committed file naming its parameter choices.
- **Uncertainty:** a seeded sample over the ledger's ranges (and the undefined inputs' ranges) for each case; every reported result carries its median and its 5 to 95 percent band, and the seed is recorded.
- **Required:** for each criterion that fails, a search for the value of each undefined input at which it would pass, reported with what that value would mean physically.
- **Verdicts:** claims the screening left `pending` that this model can decide get a status from the committed criterion, by the convention already in use: `pass` only if the criterion holds across the band, `fail` only if it fails across the band, `conditional` between, `undefined` where the deciding input is not specified. Criteria are not edited after the first production run without a dated note.

## 5. Validation

No result is used for a verdict until its module passes its benchmark:

| Module | Benchmark |
|---|---|
| hydraulics | draining of a tank through an orifice (analytic); two communicating vessels reaching a common level |
| gas | volume drawn equals volume drained; split between two openings equals the ratio of their conductances |
| transfer | approach to Henry-law equilibrium in a closed vessel (analytic time constant) |
| aqueous | a published half-life for catalysed sulfite oxidation, reproduced from the ledger's rate law |
| heat | adiabatic temperature rise at complete reaction equals the screening result |
| wall | parabolic growth of a diffusion-limited layer (analytic) |
| whole model | every screening quantity the model also computes agrees with the screening at the same inputs; element and energy balances close |

## 6. Outputs

Each run writes, under `results/process/<case>/`: the time series, a summary of the reported results with their bands, the verdicts, and a provenance manifest (commit, ledger digest, seed, versions). A viewer export writes a down-sampled copy under `viewer/data/results/`. Generated files are regenerated on a clean tree after the code commit, as the README says.

## 7. Results mode in the viewer

A switch between **Claim** and **Results** at the top of the page.

- **Results, scene:** the same geometry, with each space filled to its computed level, the liquid coloured by its computed composition, and each gas space labelled with its computed mole fractions. The timeline is the model's time.
- **Results, panel:** for the current case, the time series of the quantity each claim's criterion names (drawn in the page without a plotting library), the criterion, the verdict with its band, and which undefined inputs it depends on.
- **Field results:** the same mode shows the field solvers' maps when they exist, each with its extent, its case name and a caption saying what the case does and does not model. This replaces the field placeholder of the Claim mode.
- **Notice:** in Results mode the fixed notice reads "Simulation result: <case>", with the commit and ledger digest of the run one click away. In Claim mode it is unchanged.
- **Comparison:** a step where the claim and the result differ shows both, for example the claimed water level as an outline and the computed level filled.

## 8. Testing

Module benchmarks as in section 5; conservation checks; a regression test on the committed summary of each case; contract tests on the viewer's result files; browser checks of the Results mode for three steps (a hydraulic one, a reaction one, a gas one) at desktop and phone width.

## 9. Order of work

1. Network from the geometry; hydraulics with its benchmarks.
2. Gas and transfer.
3. Aqueous chemistry, heat and walls.
4. Cases, sweeps, required-value search, verdicts.
5. Viewer export and Results mode.

Milestones 1 to 4 do not touch the viewer and can run beside the fidelity work; milestone 5 follows it.
