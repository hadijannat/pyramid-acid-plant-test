# Completing the simulations: design

Date: 2026-10-11. Status: decided by the project owner on 2026-10-11 ("complete all remaining simulations"; three questions answered); written up here and built without a further review stop, as the owner chose.

## 1. What "remaining" means

After the Tier 0 screening, 49 of the 71 claims were `pending`. They are not all simulations. By what can decide them:

| Bucket | Claims | Decided by |
|---|---|---|
| Geometric premises | E11, E12, E15, E25, E32, S15 | rules over ledger quantities and the survey record (`premises`) |
| Documentary checks | E02, E03, E04, E06, E07, E08, E09, E10, E16, E26, E27, E28, E30, E31, E33, E34, E35, E36, E37, E39 | an authored register of what the research files found (`evidence`) |
| Undefined by the criterion's own words | S02, S26 | `evidence` |
| No test exists | S05, E05, E23, E24, E40 | `evidence`, with the new word `not_testable` |
| Water and gas movement | S03, S08, S13, S14, S17 | reduced flow models (`flow`) |
| Chemistry and feed | S01, E01, S19, S22, S23 | reduced chemical models (`chem`) |
| Lightning, ground current, room acoustics | S04, E21, S06, E13 | conduction and modal models (`electro`) |
| The 2018 electromagnetic study | E19, E20 | full-wave field solvers (`em`) |

Tier 0 verdicts stand. A package decides only the claims listed for it, and `pyramid.verdicts.merged` refuses a result that would overrule Tier 0 or another package.

## 2. Decisions

- **A sixth verdict word, `not_testable`** (owner): for a claim whose own criterion says no computation or document can decide it. The vocabulary is now pass, fail, conditional, undefined, pending, not_testable.
- **Field solvers, both routes** (owner): two independent in-house solvers now, a frequency-domain volume-integral solver and a time-domain FDTD, in numpy and scipy only, because MEEP and FEniCSx are not on PyPI and conda is not installed. A cross-check with MEEP and FEniCSx follows when Miniforge is installed. Section 5.5 of the foundation spec is amended accordingly; its cases and criteria (section 6) are unchanged and gate the in-house solvers exactly as written.
- **Piece 2 without a separate review stop** (owner): the design for S04, S06, E13 and E21 is the research files' model definitions (`04` sections 5.2 to 5.4, `05` section 5.5) and the criteria committed in `ledger/claims.yaml`. Section 4 below states the models.
- **Documentary verdicts** (ruling): `pass` when the criterion's condition is met by a source the research files read; `fail` when a source that would show it was read and does not, or contradicts it; `conditional` when it is partly met, or rests on a secondary source or on a measurement nobody has made; `undefined` when the claim names no source that could be checked, or the hypothesis leaves the deciding matter unspecified. Each basis begins with the research file's own standing (for example "No evidence found:") so absence is never reported as contradiction.
- **`undefined` or `conditional`** (ruling, 2026-10-12): `undefined` when the criterion cannot be evaluated at all without an input the hypothesis does not state (no number can be put on either side of its test); `conditional` when the ledger carries that input with an honest range, the criterion is evaluated across it, and the outcome differs between the ends: the basis then names the input and the value at which the outcome turns. This is the line Tier 0 already drew (S10 and S31 undefined; S12 conditional).
- **Package granularity** (ruling): the process-simulation spec's modules are built as two packages, `flow` (network, hydraulics, gas movement) and `chem` (transfer, aqueous chemistry, heat, walls, feed), so they can be built side by side; a later step composes them into the time-resolved cycle the viewer's Results mode reads.

## 3. Common shape of a package

A package `pyramid/<name>/` computes `Result`s (the Tier 0 dataclass) and verdicts, and `python -m pyramid.<name>` writes `results/<name>/summary.json`, `manifest.json` and figures through `pyramid.simkit.write_results`. Every physical number comes from the ledger; a number the hypothesis does not state is a ledger entry marked "not specified by the hypothesis" with a range, and a verdict that hinges on it is `undefined` or `conditional`, never decided by the default. Every module passes an analytic benchmark before its results are used. Verdict rules evaluate the committed criterion; a threshold the criterion leaves open is taken from the research file it cites and named as a judgement call in the basis.

## 4. Models

- **premises**: the survey values in the ledger against each geometric criterion; the two readings of a disputed feature (for example the antechamber grooves) are the two ends of the three-way rule.
- **evidence**: `ledger/evidence.yaml`, one entry per claim with status, basis, sources and whether the source was read at source.
- **flow**: hydrostatics of the filled system (what reservoir level and volume the fill needs; whether water stays out of the King's Chamber with the Gallery full); a conductance network for the gas drawn as the Gallery drains (what share comes down the King's Chamber shafts and through the antechamber, at what pressure difference); retention of dense sulfur dioxide in the King's Chamber with two open shafts.
- **chem**: two-film transfer of sulfur dioxide and oxygen across the Gallery's free surface; dissolved sulfur(IV) speciation and iron-catalysed oxidation limited by oxygen; the non-condensable gas the rising water must displace; calcite attack and a gypsum layer over ten fill and drain cycles; the hydrogen sulfide flux a batch needs against documented seeps.
- **electro**: a three-dimensional steady conduction solver (finite volumes, scipy sparse) for a telluric far field over a ground with conductive sheets and for a lightning current injected at the summit; the field these give in the King's Chamber granite against the field the piezoelectric and acoustic chain needs; modal quality factor and decay time of the antechamber, King's Chamber and Grand Gallery.
- **em**: the cases and criteria of the foundation spec's section 6, with a Mie benchmark, a volume-integral solver and an FDTD solver.

## 5. After the packages

One step merges them, regenerates every result on the merged ledger, feeds the merged verdicts to the tier table and the viewer, and writes a results report with figures. The time-resolved cycle and the viewer's Results mode (the cinematic viewer spec, sections 6.4 and 7.3) follow as their own plan.
