# Chemistry display and King's Chamber region: design

Follow-on to plan A of piece 1. Date: 2026-10-10. Status: draft for review.

## 1. Context

Plan A delivered the ledger, the Tier 0 screening, the parametric geometry and a viewer that animates the claimed cycle. The project owner then raised two gaps in what the viewer shows:

1. The chemical compounds the source video walks through are not visible in the scene. Gases are tinted spaces in three colours with no names, liquid is one blue whatever the video calls it, and the compounds appear only as words in the side panel.
2. The King's Chamber region differs from the real structure: the five relieving chambers are one block hung 9.35 m above the chamber ceiling, there is no gabled roof and no coffer.

The final review of plan A agreed that the second gap must be closed before the solver plan's "real chamber geometry" case, because that case measures the field in the King's Chamber and the block sits in the wrong place relative to it.

Decisions already made by the project owner:

- **Compounds from failed steps:** every compound appears where and when the video puts it. A product of a step whose verdict is `fail` or `undefined` is drawn hatched with "claimed" on its label.
- **Scope:** the chemistry display and the King's Chamber rebuild go into one follow-on plan.

## 2. Goals and non-goals

Goals:

1. Every compound the video names is visible in the scene, by name and formula, in the space and step where the video puts it.
2. The reaction steps show their equation as the video states it, beside the step's verdict.
3. A viewer can tell at a glance which compounds rest on a step the screening rejects.
4. The relieving chambers are five compartments stacked from the King's Chamber ceiling upward, the top one gabled, and the coffer stands in the chamber.

Non-goals:

- A granite material region around the King's Chamber. It needs sourced extents and belongs to the solver plan.
- The antechamber's fittings (wainscots, slots, granite leaf). The height of the leaf's underside has no sourced value.
- Davison's passage from the Grand Gallery to the lowest compartment. Its mouth is in the ledger; its route is not.
- Any new verdict. This plan changes what is drawn, not what is computed.
- A computed view of the chemistry. That is the Results mode of the process-simulation design (`2026-10-10-process-simulation-results-mode-design.md`); in the Claim mode the owner chose marking.

## 3. Part A: the chemistry display

### 3.1 Species table

A new authored file, `ledger/species.yaml`, with one entry per compound the video names: `id`, `formula` (with subscripts as Unicode characters, for display), `name`, `phase` (`gas`, `liquid` or `solid`), `colour`, and `produced_by` (the step id that makes it in the claimed cycle, or none for inputs).

| id | formula | name | phase | produced by |
|---|---|---|---|---|
| `h2s` | H₂S | hydrogen sulfide | gas | none (S01 says it rises from below) |
| `so2` | SO₂ | sulfur dioxide | gas | S02 |
| `air` | O₂ + N₂ | air | gas | none |
| `so3` | SO₃ | sulfur trioxide | gas | S16 |
| `water` | H₂O | water | liquid | none |
| `sulfurous_acid` | H₂SO₃ | sulfurous acid | liquid | S19 |
| `sulfuric_acid` | H₂SO₄ | dilute sulfuric acid | liquid | S20 |
| `calcium_sulfate` | CaSO₄ | calcium sulfate | solid | S23 |
| `hydrogen_chloride` | HCl | hydrogen chloride | gas | S27 |

Limestone (CaCO₃) and sodium chloride (NaCl) appear only inside equations, not as drawn species: the first is the wall itself and the second is outside the modelled interior.

### 3.2 The cycle file

`ledger/cycle.yaml` changes in four ways:

- Each step gains `species`, the list of species ids its statement involves. The legend is built from this list, so a step that happens outside the modelled interior (hydrogen sulfide rising under the plateau in S01, its conversion in the satellite pyramids in S02, the hydrogen chloride of S27) still shows its compounds, with the note "outside the modelled interior" in place of a label in the scene.
- Each `gas` and `water` actor gains `species`, a list of species ids, taken from that step's statement in `ledger/claims.yaml`. The actor's `color` field is removed; the colour comes from the species table. A mixture is drawn in the colour of its first-listed species and labelled with all of them.
- A new actor type, `coat`, draws the calcium sulfate layer of step S23 as an outline on `grand_gallery` and `queens_chamber`.
- Each step whose subsystem is `reaction`, plus S02 and S27, gains `reaction`: the equation as the video states it and the timestamp, or the text "not stated by the hypothesis" where the video names a conversion without giving it (S02's three steps).

Equations, as stated:

| Step | Equation |
|---|---|
| S16 | 2 SO₂ + O₂ → 2 SO₃ |
| S19 | SO₂ + H₂O → H₂SO₃ |
| S20 | 2 H₂SO₃ + O₂ → 2 H₂SO₄ |
| S21 | SO₃ + H₂O → H₂SO₄ (into dilute acid) |
| S23 | CaCO₃ + H₂SO₄ → CaSO₄ + H₂O + CO₂ |
| S27 | H₂SO₄ + 2 NaCl → Na₂SO₄ + 2 HCl |

Where the video gives a reaction in words only, the equation is the balanced form of those words and the panel says "as described in the video"; nothing is added that the video does not claim.

### 3.3 The marking rule

`pyramid/viewer_data.py` computes, for every species, the verdict of the step that produces it. In `cycle.json` each actor's species carry that status. The viewer then draws:

- `fail` or `undefined`: hatched, with "claimed" after the formula on the label and in the legend;
- `conditional`: plain, with a "conditional" tag in the legend;
- `pass`, `pending` or no producing step: plain.

The rule looks only at the step that produces the species. With the verdicts as they stand after plan A's final fixes, sulfur trioxide (S16, fail) and dilute sulfuric acid (S20, fail) are hatched wherever they appear, and everything else is plain.

### 3.4 What the page shows

- **Scene:** a label on each occupied space with the formulas present; liquid coloured by species; the coat outline in S23.
- **Legend:** a small box listing the current step's species with colour, name, formula and marking. It is empty on steps with no compound.
- **Panel:** for a reaction step, the equation and its timestamp above the verdict's deciding sentence.
- **Notice:** unchanged. The fixed notice still says the animation shows the claim.

All text is set as text, never as markup.

### 3.5 Contract changes

`cycle.json`: every step gains `species` and `gas` and `water` actors lose `color` and gain `species` (each a list of `{id, formula, name, phase, colour, status}`); steps may carry `reaction` (`{equation, timestamp, note}`); a new actor type `coat` with `space`. `claims.json` is unchanged.

## 4. Part B: the King's Chamber region

### 4.1 Relieving chambers

The single space `relieving_chambers` is replaced by five: `relieving_davison`, `relieving_wellington`, `relieving_nelson`, `relieving_arbuthnot` and `relieving_campbell`, from the lowest up. Each is a box with its own length (east-west), width (north-south) and mean height from the ledger, centred in plan on the King's Chamber.

The ledger gives the compartments' sizes and the level of the top (69 ft 3 in above the King's Chamber floor) but not the level of each compartment. The stack is therefore placed by one stated rule: the height between the chamber ceiling and the top, less the four lower compartments' heights and the top compartment's ridge height, is shared equally between the five layers of roofing beams. With the ledger's values that gives layers about 1.79 m thick. The figure is added to the ledger as `rc.beam_layer_thickness`, marked unverified with a note beginning "assumed for the model", and a test ties it to the computation.

**Campbell's chamber** is gabled. The ledger's height range for it runs from the height at the eaves to the height at the centre, so the compartment is a prism whose walls rise to the lower figure and whose ridge, running east-west, reaches the higher one. The limestone gable beams themselves stay part of the masonry.

### 4.2 Coffer

The coffer's outside and inside dimensions are in the ledger; its position is not, beyond "west end". It is placed by a stated rule: long axis north-south, centred between the north and south walls, standing on the floor one coffer width from the west wall. The coffer's stone is removed from the `kings_chamber` space, so the space's volume falls by the ledger's 1.155 m³ and the open box shows as a recess in the room. The rule is stated in the code and in the inspector's note for the space.

### 4.3 Contract changes

- Survey-level space names: 23 instead of 19 (`relieving_chambers` replaced by the five names above), in the same build order with the five in place of the one.
- The glTF files have 25 nodes instead of 21.
- `Space.volume_id` for the five compartments is none; `check()` compares their summed volume with `rc.volume`.
- The derived ledger target `kc.volume_with_passage` falls by the coffer's stone volume.
- No variant switch is added or changed.

The spec of piece 1 (section 5.3) is amended: the relieving chambers and the coffer leave its list of simplifications; the equal beam layers and the coffer's position join it as assumptions.

## 5. Testing

- **Species and cycle:** every species id used by an actor is in the table; every `gas` and `water` actor has at least one species; every reaction step has an equation or the explicit "not stated" text; the payload's key sets match section 3.5.
- **Marking:** a test drives the producing step's verdict through each status and asserts the species' status in the payload.
- **Geometry:** each compartment's volume from its ledger dimensions; the stack's bottom at the chamber ceiling plus one beam layer and its ridge at the surveyed top; the compartments do not touch one another or the King's Chamber; `kings_chamber` volume against the updated target; `check()` returns no failure for the default and the alternative model; the switch test still passes.
- **Browser:** at 1280 px, the King's Chamber region shows five compartments, the gable and the coffer; steps S03, S16, S17, S19, S20, S21 and S23 show the species labels and legend; sulfur trioxide and dilute sulfuric acid are hatched and marked "claimed"; the panel shows each reaction step's equation; no console error.

Generated files (`viewer/data`, `results/geometry`) are regenerated on a clean tree after the code commit, as the README says.

## 6. Order of work

Part B first, because it changes the space names the viewer data depends on; then Part A; then one regeneration.
