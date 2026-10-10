# Plan A handover: foundation, ledger, geometry, viewer

Date: 2026-10-10. Plan: `2026-10-10-foundation-ledger-geometry-viewer.md`. Spec: `../specs/2026-10-10-foundation-em-reply-design.md` (milestones M1 to M3).

This file records what the execution of plan A decided and left open, for the plans that build on it. It replaces the execution workspace, which is deleted when a plan finishes.

## Outcome

All 17 tasks were implemented, each reviewed against its brief. The whole-branch review (commits 55d0c3e to 8e9a2a4) found no Critical and five Important issues; one fix wave (e3c3afa, b4d1c10, f2fbeb0) addressed them, and one scoped re-review confirmed every finding addressed with no new Critical or Important issue. The suite stands at 260 passed and 1 expected failure. The re-review recomputed `t0.sulfate_yield_day` from the ledger alone over all 256 corners of its input ranges: 0.024730 (0.021461 to 0.027693), equal to the committed result.

## Decisions for the project owner

1. **S20, `fail` or `conditional`.** The rule fixes the batch at a King's Chamber of pure sulfur dioxide, the literal reading of steps S03 and S13. The hypothesis states no gas fraction. With a batch of 55 percent of a chamber or less, the favourable corner clears the 5 percent line, and by the convention used for S30 the word would be `conditional`. Whatever the fraction, one day's oxygen (158.1 mol dissolved plus 6.6 mol through the still surface) can make at most about 330 mol of acid.
2. **S09, `conditional` or `fail`.** The criterion was reworded on 2026-10-10 to test this step's own statement (water standing at reservoir level). By the first wording's letter, which tested the pump of S10, it would be `fail`.
3. **`dp.rock_entry_distance`.** Left at 31.94 m, unverified, range 29.57 to 34.32 m. Decide it with plan B's bedrock interface, after reading on Petrie's page which station is the joint of masonry and rock.
4. **Two assumptions of the fidelity spec.** Equal beam layers of about 1.79 m between the relieving compartments; the coffer placed by rule one coffer width from the west wall.
5. **Thresholds.** The 25 percent, one day, one second and +20 dB lines are judgement calls listed in the plan's closing notes.

## Rulings made during execution

Each line: what was decided, why, and what it costs if wrong.

1. execute in the existing checkout on branch design/tiered-feasibility-model, no separate worktree; the owner chose execution "on the existing branch" and the branch is not main; if wrong, the commits can be moved to a worktree branch with no loss.
2. implementers and task reviewers run on sonnet, the final whole-branch review on opus; the plan carries complete code but has never been executed, so first-run debugging is expected and the cheapest tier would cost more turns; if wrong, cost only.
3. implementers apply the smallest correction when real tool behaviour differs from the plan and record it as a deviation; they stop on any mismatch of an expected physical number; the plan was checked against stand-ins, not real gmsh, pytest or a browser; if wrong, a deviation is visible in the report and the review.
4. Task 3's E18 criterion text keeps research/05's "about 12 K or about 174 dB" although the ledger barrier is now 150 kJ/mol; it quotes the research criterion and the verdict rule reports both barriers; if wrong, one sentence of criterion text misleads a reader of the panel.
5. plan-mandated simplifications of the geometry (one block for the relieving chambers, no coffer, no antechamber fittings, flat bedrock) stand, as the spec's section 5.3 now lists them; if wrong, case V2 of the solver plan needs the detail added.
6. commit trailers keep "Claude Opus 5.5" as the plan's commit commands state, although implementer subagents run on Sonnet; the session's attribution instruction names Opus 5.5 and the committed code was authored during planning on that model; if wrong, trailers can be rewritten before any push.
7. accept both Task 1 findings and fix them, although the brief's code mandates the lenient loader; the spec makes the ledger the single source of truth with a verified flag, so `verified: "false"` loading as true is a provenance defect; cost if wrong: a few extra validation lines; side effect: tests/test_ledger.py gains cases, so every total quoted in later tasks that includes that file is higher by the number added (carried in later dispatches).
8. the commit trailer stays "Claude Opus 5.5" for the rest of this plan, although the session's attribution reminder has changed to name a different model; the plan's commit commands and every commit so far use that line, and a mid-plan switch would leave the branch's trailers inconsistent; if wrong, trailers can be rewritten before any push.
9. accept both Task 7 findings; the screening is meant to be rerun after ledger edits, so a basis that can contradict its status or a pass awarded at the favourable range end is a real defect even though every committed verdict is correct today; cost if wrong: a few sentences and four rule conditions; the 22 statuses must not change.
10. before review, fix five ledger provenance defects the gate exposed; ap.plug_width's high (39.9 in) is a mean, Petrie prints 38.2 and 41.6, so high becomes 41.6 in and the note says the value is research/01's weighted mean; gg.slot_width and dp.rock_entry_distance notes state the printed figures (and dp.rock_entry_distance becomes verified); kc.south_wall.y and kc.west_wall.x cite s.55 not s.64; values unchanged except that one range end, so no geometry test number moves; cost if wrong: five ledger lines and a regenerated manifest.
11. the implementer's use of pdftoppm and sips (already installed) to render page crops, instead of the Read tool alone, is accepted; nothing was installed and the page images were read at a resolution the Read tool could not give; the reviewer still judges it.
12. run one comments-only fix round for the four undocumented simplifications (straight QC north shaft; Gallery/Queen's passage 1.573 m3 overlap; a misleading comment in _kc_shaft; the Gallery swept at the north end's x, relieving block centred on the King's Chamber, Big Void in the Gallery plane); the spec requires simplifications to be flagged in code, and the geometry is the public model; cost if wrong: one small dispatch and re-review.
13. accept both Task 13 findings; write_msh is the solver plan's meshing entry point, so the defects would appear there as wrong convergence studies or a crash; cost if wrong: one mesh.clear() call, a docstring and two tests.
14. accept the Task 14 finding; regenerate viewer/data on a clean tree and commit the data alone so the manifest records 660fb22; the plan header and spec require the manifest's commit to contain the generator; cost if wrong: one data commit. Plan B's rerun with field slices must likewise regenerate on a clean tree after its code commit.
15. the implementer's deviation in view.frame() (bounding-sphere fit instead of the brief's 0.85 x box-diagonal distance) stands; the reviewer measured the brief's formula leaving the near base corner outside the view (NDC y -1.17 at the pane's aspect, -1.58 at 5:4) and the fit keeps direction, target, near/far and the interface; cost if wrong: a looser default view (about 40 percent slack), restorable by three lines.
16. the implementer's deviation `view.select(null)` after the model swap stands; it is the smallest fix for the stale inspector Task 15's review predicted, verified in both swap directions; cost if wrong: one line.
17. accept the Task 17 finding (scroll-margin on the inspector card) and ride two honesty-relevant minors along: a "None in the ledger" line where a space has no claims, and a heading that marks a pending step's figures as screening quantities without a verdict; the viewer is the public face of the project and a figure under a PENDING badge should not read as a result; cost if wrong: a few lines of CSS and text.
18. the final review covers 55d0c3e..HEAD (the execution range: all code, data and generated results) rather than the merge base with main (678464d), which would add the 9,600-line plan, the spec and the research verification to the diff; those documents were reviewed during planning and the reviewer is pointed at the spec and the plan header directly; cost if wrong: a document-level inconsistency between plan text and code goes unseen by the final reviewer.
19. S09 keeps `conditional` and its criterion is reworded with a dated note; the first wording tested S10's pump, not this step's statement (water standing at reservoir level holds if the reservoir exists); cost if wrong: one verdict word; the owner may prefer `fail` by the first wording's letter.
20. S20's rule must evaluate its criterion (yield within one day against the 5 and 50 percent lines) through a new result t0.sulfate_yield_day; expected verdict moves from conditional to fail; the spec fixes criteria before runs and the old rule compared a supply time with a figure in no criterion; cost if wrong: one result and one rule; "one day" as the cycle stays a judgement call because the hypothesis states no cycle time.
21. S30's rule must evaluate its criterion on the ceiling results in mol/L with the three-way convention; expected verdict moves from undefined to conditional with a basis saying the pass line is unreachable at any gas fraction; same reason; cost if wrong: one rule.
22. the claims.json contract gains `verified` and `note` on each space quantity (a change to the plan header's data contract); the inspector otherwise presents assumed values under a source's name on the public page; cost if wrong: two JSON keys.
23. a README.md is added (regeneration commands, tests, viewer) although the plan lists none; the final review found no documented way to regenerate; cost if wrong: one short file.
24. dp.rock_entry_distance stays at 31.94 m, unverified, as the final review advises (no code reads it; its range brackets both readings); decided with the solver plan's bedrock-interface work.
25. S20 stays `fail`; the rule fixes the batch at a King's Chamber of pure sulfur dioxide, which is the literal reading of steps S03 and S13 ("full of sulfur dioxide"), and the printed basis says "of a full batch"; cost if wrong: the hypothesis states no gas fraction, and with a batch of 55 percent of a chamber or less the favourable corner clears the 5 percent line, so by the convention used for S30 the word would be `conditional`. Queued as an owner decision; the process-simulation plan sweeps the gas fraction and should report the fraction-independent figure (one day's oxygen makes at most about 330 mol of acid).

## Carried to later plans

From the whole-branch review's triage of the minor findings:

- Task 4: record a dirty tree in the manifest, and stop `extra` overwriting provenance keys. This is required in Plan B's provenance task, before any solver result.
- Task 5: say in the `_evaluate` docstring that the corner method is exact only for monotone functions.
- Task 9: confirm the paper-level layout against the study's Fig. 1. Document that `session()` does not nest and that `build()` leaves the model unsynchronised. Give `_carve` a readable error.
- Task 10: give `_join` a readable error. Set a naming rule for the grotto and well-shaft overlap after fragmenting.
- Task 12: `check()` reads the stored volume, not the live mass, and its "closed solid" message overclaims. Both matter once Plan B transforms solids after the build.
- Task 13: the docstrings on whole-session scope. The xfail is replaced by a passing fragment test, so its `match=` needs no change.
- Task 14: seven results sit under no claim. The two skin depths bear on E19 and S06; the rest belong to pieces 2 and 3.
- Task 16: alternative-reading water uses the default model's curves (only the pit differs), for piece 3.
- Task 17: number formatting, and ranges without units, before public showing.
- Task 8: the "was:" wording in the record header, and the four "printed value" cells, when the ledger is next touched.
- Task 7: S28's pit ratio and the 1e3 line, for piece 5.

From the re-review of the fix wave:

- S30's pass test reads only the oxygen-limited ceiling. `min(oxygen.low, sulfur.low)` closes it. It cannot be reached while the ratio of the King's Chamber volume to the Gallery volume exceeds 0.295 (the ledger gives 0.52 to 0.61).
- S30's least-fraction clause can print above 100 percent if the central ceiling falls under the fail line while the high end does not.
- The stale-output test detects a changed ledger. It does not detect a changed formula with the ledger unchanged.
- S20's rule needs a comment naming the full-batch assumption beside the one-day comment.

## What the field-solver plan needs

**The King's Chamber region.** None of the listed simplifications is a defect of this plan's deliverable. Spec 5.3 names each, the code flags each, and a test pins the block. Which one matters depends on the piece:

- **Relieving chambers.** The block is 5.92 m of summed void hung from the surveyed apex (64.10 m). The 9.35 m between it and the ceiling (48.84 m) is the five beam layers lumped under the voids instead of interleaved. This is acceptable for M1 to M3 and for cases R1 to R3, which use the paper level. It is not acceptable under the label "real chamber geometry", because E19's metric is the volume-mean field in the King's Chamber and the block sits in the wrong place relative to it.
- **Coffer, antechamber fittings, gabled roof.** These are far below the 200 to 600 m wavelengths and do not matter to the field cases. They matter to piece 2's acoustics (S07's granite leaf, E13's upper cavity). Do not spend Plan B on them.
- **The viewer** draws the block with no marker. The spec asks for flags in code only, so this is a recommendation: add a one-line model note per simplified space to the inspector, with the fix for Important 3.

**Before case V2:**

1. **A granite region.** Masonry is one solid, and the ledger holds no extents for the granite shell or beams. V2's stated purpose is "granite around the King's Chamber". Add sourced ledger entries and a solid.
2. **The stack above the ceiling as beams and voids from the ceiling up.** Use sourced levels (Maragioglio and Rinaldi's plates, or Vyse's section). Failing that, use an equal-beam split flagged as assumed, with a sensitivity run against the present block to show how far the King's Chamber metric moves.
3. **A conformal survey mesh.** Fuse the connected air first (it forms 7 pieces), then fragment with masonry and bedrock. Fragmenting the solids as they stand leaves slivers of 0.0007 and 0.0009 m3 from the 5 cm joins. Name the groups from the parent map. `write_msh` cannot do this today, because the model's tags go stale after a fragment.
4. **A way to build a subset of spaces.** V2 is "chambers and Grand Gallery". The 0.2 m shafts cannot be resolved on MEEP's uniform grid and they bloat a finite-element mesh.
5. **A geometry route for MEEP.** MEEP reads neither STEP nor msh. The glb will not serve for inside tests, because its winding is unchecked by design.
6. **A ground.** The paper level has none, and its lower chamber lies below the base. The survey bedrock is the footprint only, 60 m deep and flat. R3 and V4 need a half-space out to the absorbing layers, following the rock interface.
7. **Local mesh sizing.** `write_msh` takes one global size.

**Before field overlays (M5):**

- Give the `field` actor a caption and an extent, and decide where the slices belong. Either attach them to E19 and E20, or caption them on S04 and S06 as "2018 study's case, plane wave; does not model lightning or ground currents".
- Add a card for evidence claims, or E19 and E20 verdicts will have nowhere to show.

**Smaller items:**

- Pin the paper mesh's conformity with a no-duplicate-nodes test. It holds today through the kernel's behaviour, not by contract.
- Derive `viewer_data.SPACES` labels from `model.SURVEY` and `PAPER`. They are equal today but held twice.
