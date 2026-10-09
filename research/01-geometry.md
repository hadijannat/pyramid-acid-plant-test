# 01 - Survey geometry of the Great Pyramid and its surroundings

Research date: 2026-10-09/10. Domain: geometry needed to build a 3D CAD/mesh for a neutral multiphysics test of Geoffrey Drumm's "Land of Chem" sulfuric-acid hypothesis.

Conventions used throughout
- CAD frame: origin = pyramid centre at pavement (base) level. X = east, Y = north, Z = up. Metres. Petrie's inches are converted with 1 in = 0.0254 m (British inch; Petrie's own scale error is negligible at this precision).
- All known passages lie in a N-S vertical plane about 7.29 m EAST of the pyramid's N-S axis (Petrie: 287.0 +/- 0.8 in) [2]. The King's Chamber extends west of that plane; the Subterranean Chamber is almost centred on the pyramid's N-S axis.
- "verified = true" means I read the figure in the cited source in this session. Two reading routes were used and are distinguished in the Source column: (PDF) = I read the page image myself; (WF) = the figure was returned by the WebFetch extraction model reading the source page, which refused to return verbatim text, so every (WF) number carries a residual transcription risk. (WF) numbers are marked true only where two extractions agreed or the number closes arithmetically with others; otherwise false.
- "computed" = my own arithmetic from the stated inputs (formula shown). Not a survey value.

---

## Summary

1. Petrie's 1880-82 survey [1][2] is sufficient to place every known chamber and passage to about +/-0.03-0.08 m in the frame above. Haase 2004 [8] fills the main gap (the well/service shaft, 60.3 m long in seven segments). ScanPyramids papers [5][6] give the two muon-detected voids. Maragioglio & Rinaldi 1965 (the best drawings) could not be opened (PDF exceeds the fetch size limit) and Gantenbrink's own site is gone, so shaft lengths/outer ends rest on older surveys and secondary pages.
2. Computed internal volumes (air or water): Descending Passage 133 m3; Subterranean Chamber <= 460 m3 bounding box (true open volume unknown, probably 250-350 m3); well shaft ~29 m3; Ascending Passage ~44 m3 free (plus ~5.5 m3 of granite plugs); Queen's passage ~51 m3; Queen's Chamber 164 m3 (+ ~5 m3 niche); Grand Gallery ~570 m3; Antechamber ~18.5 m3 gross; King's Chamber 320 m3; four small shafts 2.6-3.4 m3 each; relieving chambers ~330 m3 (rough); North Face Corridor ~40 m3; Big Void >= ~400 m3 (order of magnitude only).
3. Claim check, geometry only:
   - "King's Chamber shafts end horizontally": PARTLY SUPPORTED. Perring's 1837-39 survey, as cited by Thomas 1953 [9] and repeated by Badawy 1964 [10], records the southern channel turning to run level for about the last 10 ft (3 m); the northern is only presumed. Petrie's 1881 theodolite angles show the southern mouth still at about 45 deg with a clear line to the sky, and the northern outlet already forced open and unmeasured in its outer 2 m [2], so either the level stretch was lost between 1837 and 1881 or Perring has been over-read. The casing is gone, so the original exit through the casing is unknown.
   - "Antechamber sealed by three granite blocks; four grooves the only gas path": slots for three portcullis slabs and fragments of drilled granite slabs exist [8]; but Petrie found the four south-wall grooves shallow out and stop above the doorway [2], i.e. they were not ducts into the King's Chamber passage. PARTLY SUPPORTED (blocks) / CONTRADICTED (grooves as designed gas duct).
   - "Queen's Chamber shafts never open": SUPPORTED (about 5 in / 13 cm of stone left uncut; found 1872) [11][2].
   - "Grand Gallery is a syringe": the gallery is a constant-section corbelled prism with at least five openings; the plan resemblance is real but a syringe needs a sealed barrel. UNTESTABLE from geometry alone; a CFD/leakage question.
   - "Big Void sits where a heat exchanger would": the hypothesis does not define where one "would" sit. Published position: centre 40-50 m above the Queen's Chamber floor (Z about 61-71 m), at least 30 m long, i.e. roughly 10-20 m of masonry above the highest point of the gallery roof [5]. UNDEFINED BY HYPOTHESIS.
   - "Never had a capstone": NO EVIDENCE EITHER WAY from survey. The top 9.35 m is missing [1]; no pyramidion has been found.
4. Two geometric facts that the fluid model must respect: (a) the pavement is at Z = 0 while the Queen's Chamber floor is at Z = +21.2 m and the top of the Grand Gallery roof at about Z = +51.5 m, so any "external reservoir" at ground level gives zero static head for filling them; (b) Grand Gallery volume / Descending Passage volume = 4.3, which is numerically close to Drumm's "four pump activations", but only if the whole passage is the swept volume and nothing else (Queen's Chamber, passages) is filled.
5. Exploration status at 2026-10-10: I found no report that the Big Void has been entered or drilled. The North Face Corridor was seen by endoscope on 24 Feb 2023. Hawass's promised "2026 announcement" could not be confirmed as delivered (news items seen only as search summaries).

---

## Parameters

### A. Exterior

| name | value | unit | uncertainty | source | verified |
|---|---|---|---|---|---|
| Base side, original casing at pavement (mean of 4) | 9068.8 = 230.348 | in / m | +/-0.5 in (+/-0.013 m); sides N 9069.4, E 9067.7, S 9069.5, W 9068.6 | Petrie s.21 [1] (WF) | true |
| Base side, other surveys | 230.253-230.454 (Cole 1925); 230.295-230.373 and 230.378-230.436 (Dash 2015, east/west attribution differs between reports) | m | few cm | Search summaries of Legon 1988 / press on Dash [19] | false (secondary, not opened) |
| Core masonry base side (mean) | 9001.5 = 228.64 | in / m | mean diff 1.0 in | Petrie s.20 [1] (WF) | true |
| Azimuth of casing sides (mean) | -3' 43" (west of north) | arc | +/-12" | Petrie s.21 [1] (WF) | true |
| Face slope (adopted mean) | 51 deg 52' | deg | +/-2' ; N face weighted mean 51 deg 50' 40" | Petrie s.24-25 [1] (WF) | true |
| Original height (computed by Petrie from base and angle) | 5776.0 = 146.71 | in / m | +/-7.0 in (+/-0.18 m) | Petrie s.25 [1] (WF) | true |
| Present top platform level | 5407.9-5409.2 = 137.36-137.39 | in / m | - | Petrie s.25 [1] (WF) | true |
| Present top platform half-widths (core, centre to edge) | N 224.5, E 214.1, S 215.0, W 217.6 (about 11.0-11.2 m square) | in | +/-0.3-1.0 | Petrie s.25 [1] (WF) | true |
| Missing height above present top | 368 = 9.35 | in / m | +/-7 in | computed 5776.0-5408.5 | computed |
| Casing thickness | about 62 +/- 8 (top of base course) to 108 +/- 8 (bottom) on N base; about 71 +/- 5 near the top | in | as stated | Petrie s.25-26 [1] (WF) | true |
| Casing joint width (mean) | 0.020 | in | - | Petrie s.26 [1] (WF) | true |
| Pavement thickness | 17-27 (21 where Vyse found it) = 0.43-0.69 | in / m | - | Petrie s.27 [1] (WF) | true |
| Pavement bed edge from casing foot | 529-628 = 13.4-16.0 | in / m | varies by side | Petrie s.27 [1] (WF) | true |
| Socket levels below pavement | NE -28.5, SE -39.9, SW -23.0, NW -32.8 | in | - | Petrie s.22 [1] (WF) | true |
| Number of courses remaining / lowest course height | 203 / 1.49 m | - | - | Wikipedia [12] | false (secondary) |
| Pyramidion (capstone) | none found; classical authors describe a platform at the top | - | - | Wikipedia [12] | false (secondary) |
| Geographic position of complex | 29 deg 58' 34" N, 31 deg 07' 58" E | - | - | Wikipedia [16] | false (secondary) |

### B. Interior coordinates (Petrie section 64 summary table, converted)

Petrie columns: horizontal distance from N base; N or S of centre; E of centre; level above pavement. (WF) extraction; the extraction model flagged the scanned columns as misaligned, but the rows close arithmetically (e.g. 524.1 + 4010.0 = 4534.1 = half of 9068.8 within 0.3), so I treat them as verified.

| Point | Y (N+) in | Y m | X (E+) in | X m | Z in | Z m | Petrie +/- (in) |
|---|---|---|---|---|---|---|---|
| Original entrance, floor at casing face | +4010.0 | +101.85 | +287.0 | +7.29 | +668.2 | +16.97 | 0.3 / 0.8 / 0.1 |
| S end of Descending Passage (floor) | +306 | +7.77 | +286.4 | +7.27 | -1181 | -30.00 | 2 / 1 / 1 |
| S end of N subterranean horizontal passage | -40 | -1.02 | +286.3 | +7.27 | -1178 | -29.92 | 2 / 1 / 1 |
| Subterranean Chamber centre, ROOF | -203 | -5.16 | +25.9 | +0.66 | -1056 | -26.82 | 2 / 2 / 2 |
| N end of S blind passage | -366 | -9.30 | +284.9 | +7.24 | -1219 | -30.96 | 2 / 1 / 1.5 |
| S (dead) end of S blind passage | -1012 | -25.70 | +277.1 | +7.04 | -1213 | -30.81 | 3 / - / 2 |
| Beginning of Ascending Passage (floor meets Descending Passage floor) | +3016.3 | +76.61 | +286.6 | +7.28 | +172.9 (see note) | +4.39 | 0.3 / 0.8 / 0.2 |
| End of Ascending Passage = N wall of Grand Gallery (floor) | +1626.8 | +41.32 | +287 | +7.29 | +852.6 | +21.66 | 0.8 / 1.5 / 0.3 |
| Queen's Chamber NE corner, floor | +102.0 | +2.59 | +308 (E wall) | +7.82 | +834.4 | +21.19 | 0.8 / 3 / 0.4 |
| Queen's Chamber roof ridge, W end | +0.3 | +0.01 | +72 (W) | +1.83 | +1078.7 | +27.40 | 0.8 / 3 / 0.6 |
| Grand Gallery virtual S end of floor (at S wall) | -61.7 | -1.57 | +284.4 | +7.22 | +1689.0 | +42.90 | 0.9 / 3 / 0.5 |
| Top of Great Step, at step face | -0.4 | -0.01 | +284.4 | +7.22 | +1694.1 | +43.03 | 0.9 / 3 / 0.7 |
| Antechamber N end, floor | -113.7 | -2.89 | same plane | +7.2 | +1692.6 | +42.99 | 0.9 / - / 0.6 |
| Antechamber S end, roof | -229.8 | -5.84 | same plane | +7.2 | +1841.5 | +46.77 | 0.9 / - / 0.6 |
| King's Chamber floor at N wall | -330.9 | -8.40 | - | - | +1692.8 | +43.00 | 0.9 / - / 0.6 |
| King's Chamber wall base, NE corner | -330.6 | -8.40 | +305.0 (E wall) | +7.75 | +1688.5 | +42.89 | 0.9 / 3 / 0.6 |
| King's Chamber S wall / W wall | -537.0 | -13.64 | -107.7 (W wall) | -2.74 | - | - | 0.8 / 3 |
| King's Chamber ceiling | - | - | - | - | +1921.6 to +1923.7 | +48.81 to +48.86 | 0.6 |

Source for all rows: Petrie s.55 and s.64 [2] (WF). verified = true with the (WF) caveat. Correction by closure: the first extraction of the s.64 table returned +179.9 for the beginning of the Ascending Passage; that does not close (852.6 - 679.7 = 172.9; and 668.2 - 993.7 x tan 26.52 deg = 172.3). A second extraction confirmed that Petrie's s.39 uses 172.9 as the starting level, so +172.9 in is adopted. Treat any single-extraction number in this file with the same suspicion until checked against the printed book. Note the Queen's Chamber W wall: chamber length 226.47 in from the E wall at +308 puts the W wall at X = +81.5 in (+2.07 m), which disagrees by 9.5 in with Petrie's "72 +/- 3" for the W roof point; use +2.07 m for the wall and treat +/-0.25 m as the E-W uncertainty of this chamber.

### C. Passages and chambers (dimensions)

| name | value | unit | uncertainty | source | verified |
|---|---|---|---|---|---|
| Descending Passage angle | 26 deg 31' 23" (whole length); built part alone 26 deg 26' 42" (queried by Petrie) | deg | +/-5" (queried) | Petrie s.36 [2] (WF) | true |
| Descending Passage azimuth | -3' 44" whole; -5' 49" built part | arc | +/-10" / +/-7" | Petrie s.36 [2] (WF) | true |
| Descending Passage cross-section | 41.53 wide x 47.24 high (perpendicular to slope) = 1.055 x 1.200 m | in | mean diff 0.07 / 0.05 in | Petrie s.30 comparison table [1] (WF) | true |
| Descending Passage sloping length, original entrance to S end | 4139.9 = 105.15 (Petrie's rough pole figure: about 4143) | in / m | +/-2 in | computed from s.64 coordinates: sqrt(3703.9^2 + 1849.2^2); cross-check atan(1849.2/3703.9) = 26.53 deg | computed |
| Descending Passage: masonry / rock split | rock reached at about 1164-1351 in (29.6-34.3 m) from the original entrance (floor/roof), so about 30-34 m in masonry and about 71-75 m in bedrock | m | +/-2 m (which surface is meant) | Petrie s.35 [2] (WF); Wikipedia gives 28 m + 72 m [12] | true for Petrie stations (single extraction: treat as +/-2 m) |
| Junction with Ascending Passage, distance down the floor from original entrance | 1110.64 = 28.21 (Haase: ceiling opening about 27.40 m) | in / m | +/-0.1 in | Petrie s.38 [2] (WF); Haase [8] (PDF) | true |
| Horizontal passage to Subterranean Chamber | length 346 in = 8.79 m; width 31.6-33.3 in (0.80-0.85 m); height about 38 in (0.97 m) by Petrie's floor/roof levels, 0.91-0.95 m per Wikipedia | - | height uncertain (table alignment) | Petrie s.37 [2] (WF); [12] | length/width true; height false |
| Side recess off that passage ("S chamber" in Petrie's table) | about 70 x 72 in in plan (1.8 x 1.8 m) | in | rough | Petrie s.37 [2] (WF) | true |
| Subterranean Chamber plan | E-W 553.5 (N wall) / 554.1 (S wall) = 14.06-14.07 m; N-S 325.9 = 8.28 m (W end 329.6?) | in / m | walls vary +/-0.7 in | Petrie s.37 [2] (WF) | true |
| Subterranean Chamber roof level | -1056 = -26.82 | in / m | +/-2 (roof flat to +/-3) | Petrie s.37, s.64 [2] (WF) | true |
| Subterranean Chamber floor | very irregular: E part about 140 in below roof (Z about -30.4 m); "main" floor 155 in below roof; best-worked floor round the pit 198 in below roof (Z about -31.9 m); W half is uncut rock bosses rising to within 10 in of the roof | in | large | Petrie s.37 [2] (WF) | true (single extraction; descriptive) |
| Subterranean Chamber depth as usually quoted | a little over 30 m below base (Haase); about 27 m (Wikipedia, citing M&R, probably the roof) | m | - | Haase [8] (PDF); [12] | true / false |
| Pit in Subterranean Chamber floor | square, set diagonally; sides about 68-82.5 in (1.7-2.1 m); a ledge at 67 in depth (1321 in below pavement = -33.55 m) with a smaller shaft (sides 53-60 in) below; ORIGINAL depth of the smaller shaft about 40 in per Vyse (as reported by Petrie); deepened by Perring; roughly 30 ft deep in 1881 (Petrie); up to 11 m (Haase); Vyse dug to 50 ft (Wikipedia) | - | sources disagree on excavated depth: 9-15 m | Petrie s.37 [2] (WF); Haase [8] (PDF); [12] | true (Petrie, Haase); false (50 ft) |
| S blind passage | length 646 in = 16.41 m (stations 672 to 1318); Haase gives 16.41 m: straight for 11 m, slight bend W, then S; width 26.0-30.1 in (0.66-0.76 m); about 0.75 m square (Wikipedia citing Vyse); ends blind in rock | - | sides wander 6-8 in | Petrie s.37 [2] (WF); Haase [8] (PDF); [12] | true (length); false (height) |
| Ascending Passage angle | mean 26 deg 2' 30"; lower 300 in 26 deg 12.5'; passage+gallery mean 26 deg 12' 50" | deg | plug-block angle +/-2' | Petrie s.38-39 [2] (WF) | true |
| Ascending Passage floor length (to Gallery N wall) | 1546.8 = 39.29 (horizontal 1389.5; vertical 679.7) | in / m | - | Petrie s.38-39 [2] (WF) | true |
| Ascending Passage cross-section | 41.6 wide at top narrowing to 38.2 at the plugs; 47.3 high (Haase: 1.05 x 1.20 m narrowing to 0.97 m) | in | - | Petrie s.38 [2] (WF); Haase [8] (PDF) | true |
| Granite plugs | three blocks still in place; present plugged length about 178.5 in = 4.53 m (floor stations 74.2 to 252.7 from the junction); originally about 24 in longer; block lengths 1.57, 1.67, 1.0 m (Wikipedia) | - | - | Petrie s.38 [2] (WF); Haase [8] (PDF); [12] | true; block lengths false |
| Girdle stones | at about 206.3-208.9 in (10 cubits) spacing | in | - | Petrie s.38 [2] (WF) | true |
| Queen's passage length (Gallery N-wall doorway to chamber N wall) | 1523.9 = 38.71 | in / m | - | Petrie s.40 [2] (WF) | true |
| Queen's passage floor step | at 1307.0 in (33.20 m) from the doorway; floor drops about 19.7 in (0.50 m), from +854.6 to +834.9 | in | - | Petrie s.40 [2] (WF) | true |
| Queen's passage section | width 2 cubits (1.05 m); height 1.17 m, then 1.68 m after the step | m | - | Wikipedia citing M&R [12] | false (secondary) |
| Queen's Chamber | N-S 205.85 (5.229 m); E-W 226.47 (5.752 m); side-wall height 184.47 (4.686 m); ridge 245.1 (6.226 m); gable ends are the E and W walls; roof slabs slope about 30 deg 10'-30 deg 48' | in | wall lengths vary about 0.2 in | Petrie s.41-42 [2] (WF) | true |
| Queen's Chamber floor / apex level | +834.4 / +1078.7 to +1080.1 = +21.19 / +27.40 | in / m | +/-0.4 / 0.6 | Petrie s.40, s.64 [2] (WF) | true |
| Queen's Chamber niche (E wall) | 41 in deep (2 cubits), 62 in wide at base narrowing by four 1/4-cubit overlaps to 20 in at 156 in, roofed at 184 in | in | +/-0.3 | Petrie s.43 [2] (WF) | true |
| Queen's Chamber shafts, section and horizontal start | N: 8.6 high x about 8 wide, horizontal 76 in then rising; S: 8.8 high, horizontal 80.0 in then rising (about 0.21-0.22 m square; 1.93 / 2.03 m level) | in | - | Petrie s.44 [2] (WF) | true |
| Queen's Chamber shafts, slope | N mean 37 deg 28'; S mean 38 deg 28' | deg | goniometer | Petrie s.44 [2] (WF) | true |
| Queen's Chamber shafts, stone left uncut at chamber wall | "five inches" (about 13 cm); tube 9 x 8 in | in | another secondary page gives 13-17 cm; Drumm says 3-5 in | Smyth 1877 as quoted by Sakovich [11] (PDF); [14] | true (as quoted) |
| Queen's Chamber shafts, upper ends | blocked by limestone slabs with two copper pins; S blocking stone about 63.6 m from the chamber (press), reached by Upuaut-2 in 1993 after about 60-65 m; a second stone behind a small cavity (2002, 2011); N shaft bends sharply at about 18 m to pass the Gallery | m | press-level | NBC/Leeds/Wikipedia summaries [13][16][19] | false (secondary) |
| Queen's Chamber shafts, where they would exit if continued | N face at Z = 2641.3 in (67.09 m); S face at Z = 2679.1 in (68.05 m) | in | Petrie's projection, no outlet found | Petrie s.44 [2] (WF) | true |
| Grand Gallery floor length on slope | 1815.5 (46.11 m) to the step face; 1883.6 (47.84 m) to the S wall | in | - | Petrie s.45 [2] (WF) | true |
| Grand Gallery roof length | 1838.6 sloping (46.70 m); 1648.4 horizontal (41.87 m) | in | - | Petrie s.46 [2] (WF) | true |
| Grand Gallery slope / azimuth | 26 deg 16' 40" / +1' 20" | - | - | Petrie s.45 [2] (WF) | true |
| Grand Gallery size as used by ScanPyramids | 8.6 high x 46.7 long x 2.1 to 1.0 wide | m | - | Morishima et al. [5] (PDF) | true |
| Grand Gallery widths | 82.42 between walls above ramps (2.093 m); 2 cubits (about 41.2 in, 1.05 m) between ramps; roof 40.9 (N) - 41.3 (S); seven laps, total overhang 20.55 in per side | in | - | Petrie s.30 [1], s.46 [2] (WF) | true |
| Grand Gallery ramps (benches) | 52 cm wide and high (Haase); Petrie ramp height 23.86 in | - | - | Haase [8] (PDF); Petrie s.30 [1] (WF) | true |
| Grand Gallery first corbel height | 2.29 above floor | m | - | Wikipedia [12] | false (secondary) |
| Grand Gallery ramp holes and niches | 28 holes per side (Wikipedia); Haase: 25 opposed pairs, recesses about 52 x 18 cm, niches about 67 x 20 cm; Petrie: long holes 23.32 in, short 20.51 in | - | counts differ (which holes are counted) | [12]; Haase [8] (PDF); Petrie s.46 [2] (WF) | true (Haase, Petrie) |
| Groove along third lap | 172.1-179.0 in vertically above floor; about 0.6-0.8 in deep | in | - | Petrie s.46 [2] (WF) | true |
| Great Step | height 34.92 (E) - 35.80 (W) = 0.89-0.91 m; N-S length 61.0-61.5 = 1.55-1.56 m; face 0.4 +/- 0.8 in S of the pyramid's E-W mid-plane; top +1693.2 (E side at S doorway) | in | +/-0.6-0.8 | Petrie s.46 [2] (WF) | true |
| Davison's-chamber passage mouth (top of Gallery E wall) | about 26.3 wide x 29.4 high | in | - | Petrie s.62 [2] (WF) | true (single extraction) |
| Passage Gallery to Antechamber | length 52.02 in = 1.32 m | in | - | Petrie s.47 [2] (WF) | true |
| Low passages (Gallery-Antechamber and Antechamber-King's Chamber) section | about 41.4 wide x 43.7 high (1.05 x 1.11 m) | in | - | recalled from Petrie pl. xii / standard literature; not seen this session | false (memory) |
| Antechamber | length N-S 116.30 (2.954 m); breadth E-W 65.00 (1.651 m) above the wainscots; height 149.35 (3.793 m); 48.46-48.76 between the granite wainscot grooves | in | - | Petrie s.48, s.50 [2] (WF) | true |
| Antechamber wainscots | granite, on E and W walls; E top flat at about 103.2 in above floor; W top carries three semicircular hollows | in | - | Petrie s.49 [2] (WF); height from secondary page [15] | hollows true; height false |
| Portcullis slots | three per side; about 55 cm wide (Haase), "one cubit" in a secondary page; said to run from the wainscot top to the floor; maximum width of the blocking slabs 1.21 m | - | depth into wall and exact floor termination not found | Haase [8] (PDF); [15] | 55 cm and 1.21 m true; "to the floor" false (secondary) |
| Granite leaf | two stones; thickness 15.16-16.20 in; between ledges 40.6-41.2 in; top 51.24-59.0 in below the ceiling; it does not reach the floor (people pass beneath it) | in | height of underside above floor not found | Petrie s.50 [2] (WF) | true (underside statement from general knowledge: false) |
| S-wall vertical grooves | four; about 10.5 cm wide, semicircular (Haase); depth 2.8 in at 8-10 in above the doorway reducing to 1.75-2.0 in at 5 in above it; Petrie concluded they died out to a flat surface above the doorway rather than reaching the passage roof; wall there now broken | - | - | Petrie s.49 [2] (WF); Haase [8] (PDF) | true |
| Granite slab fragments attributed to the portcullises | at the pyramid entrance: 82 x 114 x 53.5 cm, about 1.2 t, three bore holes 7.1-7.6 cm, reconstructed width about 1.19 m; in the Grotto: 1.04 x 0.61 x 0.52 m with two bore holes about 18 cm apart | cm | - | Haase [8] (PDF) | true |
| Passage Antechamber to King's Chamber | length 100.8 in = 2.56 m (stations 168.10 to 268.9) | in | - | Petrie s.47 [2] (WF) | true |
| King's Chamber | E-W 412.40 (N wall) / 412.11 (S wall); N-S 206.29 (E) / 205.97 (W); adopt 10.471 x 5.236 m; floor to ceiling about 230.1 in = 5.844 m (from levels); wall base is about 5 in below the floor | in | chamber slightly enlarged by shaking: opened joints total 0.14-0.41 in per wall | Petrie s.51-55 [2] (WF) | true |
| King's Chamber floor / ceiling level | +1691.4 to +1693.7 / +1921.6 to +1923.7 = +42.96-43.02 / +48.81-48.86 | in / m | +/-0.6 | Petrie s.55 [2] (WF) | true |
| King's Chamber roof beams | nine granite beams, widths 45-63 in; all cracked across near the S side; cracks daubed with cement | - | - | Petrie s.51-53 [2] (WF) | true |
| Coffer | outside 89.62 x 38.50 x 41.31; inside 78.06 x 26.81 x 34.42; contents 72,030 in3 (1.180 m3); solid 70,500 in3 (1.155 m3); overall 142,530 in3 (2.336 m3) | in | about 60-100 in3 | Petrie s.59, s.61 [2] (WF) | true |
| King's Chamber floor disturbance | floor dug away underneath only at the west end, below the coffer; no original shaft described | - | - | Petrie s.54 [2] (WF) | true |
| King's Chamber shafts: mouths | about 3 ft above floor; both run level for about 5 ft before turning up (Perring, via Thomas); mouth section 18 and 21 cm wide x 14 cm high, 2.5 m from E wall (Wikipedia) | - | - | Thomas 1953 [9] (PDF); [12][13] | true (Thomas); false (Wikipedia) |
| King's Chamber shafts: section in masonry | N: 8.9-9.2 wide x 8.72-8.74 high; S: 8.35-8.65 wide x 8.7-8.9 high (about 0.22 x 0.22 m); Perring: N 22.5 x 23 cm | in | - | Petrie s.56 [2] (WF); Badawy [10] (PDF) | true |
| King's Chamber N shaft slope (outermost surviving part, measured from outside) | 32 deg 4' 45" (84-180 in from outer end); 31 deg 37' 15" (180-300); 30 deg 43' 15" (300-372); mean 31 deg 33' | deg | - | Petrie s.56 [2] (WF) | true |
| King's Chamber S shaft slope (from outer end inward, 120-in steps to 840 in) | 45 deg 25' 6"; 45 deg 30' 7"; 45 deg 25' 57"; 45 deg 25' 14"; 45 deg 15' 19"; 45 deg 7' 42"; 44 deg 26' 18"; mean 45 deg 13' 40"; curves more than its own width to the east | deg | - | Petrie s.56 [2] (WF) | true |
| King's Chamber shafts: other angle figures | N 31 deg, S 44.5 deg (Badawy); N 32.6 deg average over 56.7 m, last 11 m 31.2 deg, S 45 deg over 42 m (Gantenbrink via secondary page) | deg | - | Badawy [10] (PDF); [14] | true / false |
| King's Chamber shafts: lengths | N 233 ft (71.0 m); S 174 ft 3 in (53.1 m) (Vyse 1840, via search extract). My check from Petrie coordinates and angles: N about 68-70 m sloping + about 1.5-2.6 m level; S about 51.7 m + about 1.5-1.7 m level, to the original casing plane | m | +/-2 m | [19] (Vyse via search summary); computed | false (secondary) / computed |
| King's Chamber shafts: exit level on the original casing plane | about 80 +/- 1 m (3139-3174 in), both shafts at about the same level | m | depends on slope used (31.55-32.5 deg N; 45.2 deg S) | computed: intersect shaft line with face y = 4534.4 - 0.7857 z | computed |
| King's Chamber shafts: outer ends | S channel "turned abruptly to run parallel with the ground" for about the last 10 ft (Perring pl. 4, per Thomas); N presumed alike; the outer 47 ft 6 in of the N channel had been forced open before 1837 (Perring, via search extract); Petrie's 1881 angles show no flattening at the then-present outer ends; Vyse wrote that it ascended in one line to the outside (search extract) | - | sources conflict | Thomas [9] (PDF); Badawy [10] (PDF); Petrie s.56 [2] (WF); [19] | true (Thomas, Badawy, Petrie); false (Vyse, Perring extracts) |
| Relieving chambers | five compartments above the King's Chamber; lowest (Davison's) 38 ft 4 in x 17 ft 1 in, height 2 ft 6 in-3 ft 6 in; Wellington's 2 ft 2 in-3 ft 8 in; Nelson's 2 ft-4 ft 10 in; Lady Arbuthnot's 1 ft 4 in-4 ft 5 in; Campbell's (gabled limestone roof) 5 ft 10 in-8 ft 7 in at centre; King's Chamber floor to Campbell's roof 69 ft 3 in (21.1 m), so apex about Z = +64 m | ft | - | Vyse 1840 via search extract [19]; plan lengths 460-481 x 196-247 in in Petrie s.62 [2] (WF) | false (secondary); Petrie plan true |
| Well / service shaft, upper mouth | in the W ramp of the Gallery, 55 cm from the Gallery N wall (Petrie: 21.8-49.0 in from N wall); starts about 21.70 m above base | - | - | Haase [8] (PDF); Petrie s.46 [2] (WF) | true |
| Well shaft segments, top to bottom | (0) level run west 1.40 m; (1) vertical 7.96 m, 71 x 71 cm, in masonry; (2) about 65 deg to the south, 7.90 m, in masonry; (3) vertical about 5.20 m, 66 x 68 cm, of which over 2 m is lined with ten courses of small blocks through the Grotto and 2.15 m is rock-cut; (4) 45 deg to the south, 26.50 m, 76 cm high x 56-64 cm wide, starting a good metre above base; (5) 75 deg, about 9.50 m; (6) level link about 1.85 m into the W wall of the Descending Passage | m | total 60.31 m (sum); Haase gives the total as more than 60 m | Haase [8] (PDF) | true |
| Well shaft lower mouth | W wall of Descending Passage, just under 98 m from the original entrance (so about 7 m above the passage end, Z about -26.8 m); original section about 79 x 79 cm; shaft runs parallel to and about 1.40 m west of the passage | - | - | Haase [8] (PDF); Z computed | true |
| Bedrock surface under the pyramid at the well shaft | 5.70 m above base, about 78 m south of the N base edge | m | - | Haase [8] (PDF) | true |
| Grotto | natural gravel/sand-filled cavity crossed by segment 3; contains a drilled granite block (see above); no room dimensions given | - | - | Haase [8] (PDF) | true |
| Al-Ma'mun (robbers') tunnel | enters about 7 m above base; about 27 m long | m | - | Wikipedia [12] | false (secondary) |

### D. Muon-detected voids (ScanPyramids)

| name | value | unit | uncertainty | source | verified |
|---|---|---|---|---|---|
| Big Void: length | at least 30 | m | lower bound | Morishima et al. 2017 [5] (PDF) | true |
| Big Void: cross-section | "similar to the Grand Gallery" (muon excess of the same order) | - | not measured | [5] (PDF) | true |
| Big Void: position | above the Grand Gallery, in its vertical plane; centre 40-50 m above the Queen's Chamber floor, i.e. Z about +61 to +71 m; KEK: starts near the pyramid centre and extends north to tan = 0.8 | m | +/-5 m; horizontal or inclined, one or several voids, all left open by the authors | [5] (PDF); Z computed with QC floor +21.19 | true |
| Big Void: significance | Nagoya 13.7 and 12.7 sigma (statistical); KEK > 10 sigma (H1), > 7 (H2); CEA 5.8 sigma (8.4 for the Gallery as control) | sigma | - | [5] (PDF) | true |
| Model accuracy used by ScanPyramids | about 0.3 m internal structures, about 1 m external casing; densities 2.2 g/cm3 limestone, 2.6-2.75 granite | - | - | [5] (PDF) | true |
| North Face Corridor: length | 9.06 +/- 0.07 (Nagoya); 9.23 +/- 0.48 (CEA) | m | as stated | Procureur et al. 2023 [6] (WF) | true |
| North Face Corridor: section | width 2.02 +/- 0.06, height 2.18 +/- 0.17 (Nagoya); 1.87 +/- 0.11 x 1.85 +/- 0.12 (CEA) | m | as stated; cuboid assumed | [6] (WF) | true |
| North Face Corridor: position and slope | starts 0.84 +/- 0.05 m (Nagoya) / 0.45 +/- 0.22 m (CEA) behind the chevrons over the original entrance; slope -0.3 +/- 1.5 deg (horizontal); no continuation larger than 1 m x 1 m to the south; no connection to the Big Void seen | - | - | [6] (WF) | true |
| North Face Corridor: direct observation | 5 mm endoscope through a chevron joint on 24 Feb 2023; press: gabled ceiling, about 9 m x 2 m | - | - | search summary of press; borescope "early 2023" in Schumacher et al. [7] (WF) | false (press) / true (borescope) |
| Big Void: exploration to date | no entry, drilling or endoscopy reported up to 2026-10-10 | - | absence of evidence | searches [19] | false (search only) |

### E. Surroundings

| name | value | unit | uncertainty | source | verified |
|---|---|---|---|---|---|
| East boat pit, north ("N trench") | axis 2130.2 in (54.11 m) long, running N-S; axis 1080.6-1085.5 in (27.4-27.6 m) east of the E base (X about +142.7 m); from Y = +35.05 to +89.16 m; dug more than 220 in (5.6 m) below rock surface without reaching bottom | in | - | Petrie s.29 [1] (WF) | true |
| East boat pit, south ("S trench") | axis 2093.7 in (53.18 m); 1122.9-1125.5 in (28.5-28.6 m) east of the E base (X about +143.7 m); from Y = -35.32 to -87.13 m; width 205-206 in (5.2 m) at outer end, 134.2 in (3.41 m) at inner end | in | - | Petrie s.29 [1] (WF) | true |
| Causeway boat pit ("E.N.E. trench") | axis 2112.6 in (53.66 m), bearing about 76 deg E of N; outer end 4213.2 in (107.0 m) from the E base and 848.3 in (21.5 m) N of the E-W centre line; width 152.8 in (3.88 m); bottom about 200 in (5.1 m) below ground | in | - | Petrie s.29 [1] (WF) | true |
| South boat pits | two rectangular rock pits, roofed with limestone slabs up to 15 t; the first (found May 1954) held the dismantled ship: 43.4-43.6 m long, 5.9 m beam; pit dimensions not found this session (commonly quoted about 31 m x 2.6 m x 3.5 m) | m | - | Wikipedia [12][16] | false (secondary; pit size from memory) |
| Trial passages | rock-cut model of the passage system, about 87.4-87.5 m east of the E base, from Y about +31.0 to +56.7 m; Haase: about 22 m long, 10 m deep, about 85 m east; angle 26 deg 32', width 41.46, height 47.37 in | - | - | Petrie s.29-30 [1] (WF); Haase [8] (PDF) | true |
| Basalt pavement (mortuary temple floor) | about 2124-2169 in across (54-55 m), east of the pyramid | in | - | Petrie s.28 [1] (WF) | true |
| Queens' pyramids | G1-a, G1-b, G1-c standing east of the pyramid; G1-d ruined; sizes not found | - | - | Wikipedia [12] | false |
| Khafre pyramid: base / height / slope | 8474.9 in (215.26 m); 5664 +/- 13 in (143.87 m); 53 deg 10' +/- 4' | - | as stated | Petrie s.66-67 [3] (WF) | true |
| Khafre pyramid: centre relative to Great Pyramid centre | 13,931.6 in south (353.86 m) and 13,165.8 in west (334.41 m) | in | - | Petrie triangulation as quoted on a secondary page [15] | false (secondary) |
| Khafre pyramid: site level | bedrock about 10 m higher than Khufu's; NW corner cut about 10 m into rock; lower core is rock left in place | m | - | Wikipedia [16]; Petrie s.68 [3] (WF) | false / true |
| Khafre: burial chamber | 557.9 (N wall) x 195.8 in = 14.17 x 4.97 m, long axis E-W; walls 206.4 in (5.24 m); ridge about 244.4 in (6.21 m); walls cut in rock, gabled roof of limestone beams; about 47 in east of pyramid centre | in | - | Petrie s.73, s.75 [4] (WF) | true |
| Khafre: passages | section 41.29 x 47.29 in; beyond the portcullis 41.59 x 71.06 in; upper entrance 11.54 m up the N face, lower entrance at ground level, both about 12 m east of centre | - | - | Petrie s.73-74 [4] (WF); Wikipedia [16] | true / false |
| Khafre: lower (subsidiary) chamber | 411.9 x 123.1 in (10.46 x 3.13 m) | in | - | Petrie s.78 [4] (WF) | true |
| Khafre: depth of chambers below base | not stated by Petrie in the chapter read; burial chamber is a rock pit roofed at about base level, so about 6-7 m of rock depth for the chamber itself | m | - | inference from [4][16] | false |
| Sphinx | 73 m long, 20 m high, 19 m wide at the haunches; 29.97526 N, 31.13758 E; known cavities are short (rump passage about 4 m up and about 5 m down to groundwater; Perring's bore stuck at 8.2 m) | m | - | Wikipedia [16] | false (secondary) |
| Sphinx position relative to Great Pyramid centre | roughly 440 m south and 330 m east | m | +/-30 m | computed from the Wikipedia coordinates of the Sphinx and a remembered Great Pyramid centre (29.9792 N, 31.1342 E) | false |
| Sphinx enclosure dimensions and floor level | not found | - | - | - | not found |
| Osiris Shaft | beneath Khafre's causeway, about 100 yards from Khafre's mortuary temple; access shaft to an empty hall; a 40 ft shaft to a six-chambered hall; a further 40 ft shaft to the lowest chamber (four rock pillars, sarcophagus pit, standing water); total nearly 100 ft (about 30 m) | ft | journalistic | Schuster, Archaeology 53(5), 2000 [17] (WF) | true (as a secondary description) |
| Khafre causeway length | 494.6 | m | - | Wikipedia [16] | false |

### F. Computed internal volumes

All "computed". Uncertainty is my estimate. Add or subtract as noted for a wet/dry domain.

| Space | Formula and inputs | Volume m3 | Uncertainty |
|---|---|---|---|
| Descending Passage (entrance to S end) | 105.15 m x (1.055 x 1.200 = 1.266 m2) | 133 | +/-3 % |
| - part above the Ascending junction | 28.21 x 1.266 | 35.7 | |
| - part below the junction | 76.94 x 1.266 | 97.4 | |
| Horizontal passage to Subterranean Chamber | 8.79 x 0.83 x 0.95 | 6.9 | +/-15 % |
| Subterranean Chamber, bounding box | 14.06 x 8.28 x (3.56 to 3.94) | 414-459 | upper bound only |
| Subterranean Chamber, likely open volume | W half largely uncut rock; no scan data found | 250-350 | unknown; needs a laser scan |
| Pit (as excavated) | about 1.9 x 1.9 x (9 to 11) upper bound; originally about 1.9 x 1.9 x 1.7 + small shaft 1.4 x 1.4 x 1.0 | up to about 35; originally about 8 | large |
| S blind passage | 16.41 x 0.72 x 0.75 | 8.9 | +/-25 % |
| Well / service shaft | 17.26 x 0.504 + 5.20 x 0.449 + 26.50 x 0.456 + 11.35 x 0.50 | 28.8 | +/-20 % (Grotto excluded) |
| Ascending Passage, gross | 39.29 x (1.057 x 1.201 = 1.269) | 49.9 | +/-3 % |
| - granite plugs in place | 4.53 x (1.013 x 1.201) | -5.5 | |
| - free | | 44.3 | |
| Queen's passage | 33.20 x 1.05 x 1.17 + 5.51 x 1.05 x 1.68 | 50.5 | +/-5 % |
| Queen's Chamber | 5.229 x 5.752 x 4.686 + 0.5 x 5.229 x 1.540 x 5.752 | 164.1 | +/-1 % |
| Queen's Chamber niche (original) | about 1.04 x 1.04 (mean width) x 4.67 | 5.1 | +/-20 % |
| Queen's Chamber shafts, each | about 63.6 x (0.218 x 0.205) | 2.8 | +/-15 % |
| Grand Gallery | vertical section area 13.59 m2 = 1.05 x 0.606 (between ramps) + 2.093 x 1.684 (to first lap) + 0.901 x (1.943 + 1.794 + 1.644 + 1.494 + 1.345 + 1.195 + 1.045) (seven laps), total height 8.6 m; x mean horizontal length 42.3 m; minus Great Step wedge 1.7 | 573 | +/-8 % (lap heights not individually measured here; ramp holes, niches, well mouth excluded) |
| Passage Gallery to Antechamber | 1.32 x 1.05 x 1.11 | 1.5 | +/-10 % |
| Antechamber, gross box | 2.954 x 1.651 x 3.793 | 18.5 | wainscots (about -3.4), slots (+0.4) and leaf (-0.6) give about 15 net |
| Passage Antechamber to King's Chamber | 2.56 x 1.05 x 1.11 | 3.0 | +/-10 % |
| King's Chamber | 10.471 x 5.236 x 5.844 | 320.4 | +/-0.5 %; minus coffer solid 1.16 |
| King's Chamber N shaft | 71.0 x (0.229 x 0.222) | 3.6 | +/-15 % |
| King's Chamber S shaft | 53.1 x (0.216 x 0.224) | 2.6 | +/-15 % |
| Relieving chambers, five | about 11.7 x 5.2 x (0.91 + 0.89 + 1.04 + 0.88) + about 100 for Campbell's | about 330 | +/-30 % |
| North Face Corridor | 9.06 x 2.02 x 2.18 (cuboid; gabled roof would reduce it) | 39.9 | +/-15 % |
| Big Void | >= 30 m x (Gallery-like 13.6 m2) | >= about 400 | order of magnitude |
| Khafre burial chamber | 14.171 x 4.973 x (5.243 + 0.483) | 403 | +/-3 % |

Derived checks for the hypothesis
- V(Grand Gallery) / V(Descending Passage, full length) = 573 / 133 = 4.3.
- V(Grand Gallery) / V(Descending Passage below the Ascending junction) = 573 / 97.4 = 5.9.
- V(Gallery + Queen's Chamber + niche + Queen's passage + free Ascending Passage + well shaft) = about 866 m3, i.e. 6.5 full-passage swept volumes, 8.9 lower-passage swept volumes.
- Hydrostatic levels: pavement Z = 0; Descending Passage entrance +16.97 m; Queen's Chamber floor +21.19 m; Gallery floor +21.66 to +42.90 m; top of Gallery roof at S end about +51.5 m; King's Chamber floor +43.00 m; Subterranean Chamber floor about -30.4 to -31.9 m. Filling the Gallery to its roof implies about 51.5 m of water above the pavement (about 5.1 bar gauge at Z = 0; about 8.0 bar at the Subterranean Chamber floor; about 2.9 bar at the Gallery's N foot).

---

## Claim-by-claim assessment

Each claim is taken from the transcripts (clip 1 at 00:09-00:13 and 00:06-00:08; clip 2 at 00:05-00:08, 00:15, 00:25-00:28; full episode 00:13-00:17, 00:37-00:58).

1. King's Chamber shafts end horizontally on the outside and are "air intakes".
   - What supports it: Thomas 1953 [9] reports, citing Chatley and Perring's Plate 4 (figs 5-6), that the outer end of the southern channel was not square to the face but turned level for approximately the last 10 ft, which Perring thought was meant to keep sand out; she only presumes the same for the northern channel. Badawy 1964 [10] states both shafts bend horizontally at both ends. When Vyse cleared the southern channel in 1837 air flow into the chamber resumed ([10]; Drumm's remark about clearing is historically correct).
   - What cuts against it: Petrie [2] set a theodolite at the then-present outer mouths in 1881 and measured inward. South channel: 45 deg 25' in the first 120 in from the mouth, 45 deg 30' in the next 120 in, easing to 44 deg 26' at 720-840 in; he says the slope of both channels increases toward the outside except just at the S mouth (where it is 5' flatter, not level), and that the sun shone straight down the S channel at noon, which requires an unobstructed 45 deg line to the sky. So no level, roofed stretch existed at the S mouth in 1881. North channel: his angles start 84 in (2.1 m) in from the mouth, the outermost part had been forced open as a working passage (only floor and W side intact), and Perring (search extract [19]) says 47 ft 6 in from the exterior had been forced before 1837; the original N outlet geometry is therefore not recoverable from Petrie. Whether either shaft pierced the casing is unknown because the casing is gone ([12][13]; Edwards as quoted in Sakovich [11]).
   - Reading the two surveys together: either Perring's level 10 ft lay in outer blocks removed between 1837 and 1881 (Vyse cleared this outlet), or Perring's plate has been over-read by later authors. I could not open Perring's plate to decide.
   - Verdict: PARTLY SUPPORTED for a short level stretch at the southern outlet (one 1837-39 survey, seen here only through Thomas's citation, and not confirmed by Petrie in 1881); NO EVIDENCE for the northern outlet (destroyed); "air intake" is a functional reading that geometry cannot settle. The claim that this disproves stellar symbolism is outside this domain. For the model: treat the outer 3 m of each shaft as a parameter (inclined to the face vs level), and treat "open through the casing" as a second parameter.

2. The Antechamber was sealed to the floor by three granite blocks, leaving four grooves as the only gas path.
   - Supports: three pairs of slots about 55 cm wide exist; granite fragments with drilled holes of matching size and spacing exist at the entrance and in the Grotto, so real portcullis slabs very probably existed [8]. The four S-wall grooves sit exactly where the southernmost slab would slide against the S wall.
   - Against: Petrie [2] examined the grooves and concluded they became shallower and stopped above the doorway, leaving flat stone over it, so they were not cut through into the passage to the King's Chamber; Haase [8] matches their 10.5 cm width to the 7.1-7.6 cm rope holes in the slab fragments (rope guides). No slab survives in place, so "gas-tight to the floor" has never been observable. The fourth element (granite leaf) does not reach the floor.
   - Verdict: blocks PARTLY SUPPORTED (existence yes, sealing untestable); grooves as a designed duct CONTRADICTED by Petrie's observation, with the caveat that the stone there is now broken. For the model: run two cases, grooves blind (leakage only) and grooves connected (total duct area about 0.02-0.03 m2 = 4 x about 0.105 m x 0.07 m U-section).

3. The Queen's Chamber shafts were never open to the chamber (3-5 in of stone left).
   - Smyth's account, quoted by Sakovich [11], gives five inches left uncut; Petrie [2] describes the same uncut plate; Thomas [9] repeats Petrie. Opened by Waynman Dixon in 1872 ([12]). Upper ends closed by slabs (secondary [13][16]).
   - Verdict: SUPPORTED as a statement of geometry. The "ultrasound flow meter" interpretation is not a geometric claim.

4. The Grand Gallery is shaped like, and acts as, a syringe.
   - Geometry: constant cross-section along its 46-48 m length; 2.09 m wide at ramp level tapering by seven corbels to 1.05 m at 8.6 m height; entered by 1.05 m-wide passages at both ends [1][2][5]. In plan it is a wide barrel with narrow necks, so the visual analogy holds. But it is not a closed barrel: openings are the Ascending Passage (1.27 m2), the Queen's passage at the N foot, the well-shaft mouth in the W ramp (about 0.5 m2), the Antechamber passage (about 1.17 m2) and the Davison's-chamber passage at the top of the E wall (about 0.67 x 0.75 m) [2][8].
   - Drumm's sentence that it "has to be at a horizontal configuration" contradicts his own point that it is slanted; I read it as a slip for "inclined".
   - Verdict: split. Shape resemblance in plan: PARTLY SUPPORTED (wide barrel, narrow necks; but constant section, corbelled in height, and perforated). Syringe function: UNTESTABLE by geometry alone; it is a free-surface/leakage question. Volume ratio 4.3 to the Descending Passage is noted above.

5. Four pump strokes of the Descending Passage fill the Grand Gallery.
   - Computed ratio 4.3 if the entire 105 m passage is swept and only the Gallery is filled; 5.9 if only the part below the Ascending junction is swept; 6.5-8.9 if the Queen's Chamber and connecting passages are filled too (which the described sequence requires, since water reaches the Gallery through them).
   - Verdict: PARTLY SUPPORTED numerically under the most favourable reading; the hypothesis does not define the stroke length or which spaces fill.

6. An external reservoir round the pyramid fed the Subterranean Chamber; the well shaft is a standpipe; the pit is a shaft to an aquifer; one-way valves existed.
   - Geometry: the only surveyed connections to the Subterranean Chamber are the Descending Passage (entrance at +16.97 m on the N face) and the well shaft (which goes up, into the Gallery). No conduit from pavement level is known. The pit was about 1-1.7 m deep originally (Vyse, per Petrie [2]; Wikipedia gives about 1.5 m) and was deepened to 9-15 m by 19th-century excavators without reaching water or a chamber [2][8][12]; the "sand-filled shaft" is their backfill. Petrie saw rain water stand in it [2]. No valve seats or valve parts are recorded.
   - Verdict: reservoir and inlet UNDEFINED BY HYPOTHESIS / NO EVIDENCE; "pit is an ancient deep shaft" CONTRADICTED by the excavation record; the S passage being a dead end is SUPPORTED (16.41 m, blind) [2][8].

7. The Big Void sits where a heat exchanger would, and is "like a copy of the Grand Gallery right above it".
   - Published: length >= 30 m, cross-section comparable to the Gallery, centre 40-50 m above the Queen's Chamber floor, horizontal or inclined, possibly several voids [5]. That puts its centre about 10-20 m above the highest point of the Gallery roof (about Z +51.5 m) and considerably more above the Gallery's lower end if the void is horizontal. No shaft to or from it is known; the N-face corridor does not appear to connect to it [6].
   - Verdict: "similar size, above the Gallery" SUPPORTED; "where a heat exchanger would be" UNDEFINED BY HYPOTHESIS (no thermal-contact criterion stated). The masonry thickness between Gallery and void is the input the thermal model needs, and it is uncertain to +/-5 m or more.

8. The pyramid never had a capstone.
   - Survey: top 9.35 m missing; present platform about 11 m square at Z about 137.4 m [1]. No pyramidion found; classical writers already describe a platform ([12], secondary).
   - Verdict: NO EVIDENCE EITHER WAY from geometry. The electromagnetic argument in clip 2 is not survey evidence and belongs to the EM domain.

9. A shaft beneath the King's Chamber floor (by the coffer) was a gas inlet from the satellite pyramids.
   - Petrie records only that the floor had been dug under at its west end, below the coffer [2]; this is an excavation in masonry 43 m above ground level. No original lined shaft is described in any source opened. Drumm himself calls the connection a hypothesis (full episode 00:17).
   - Verdict: NO EVIDENCE.

10. Khafre's chambers are no more than 10-15 m into bedrock.
   - Petrie: burial chamber walls rock-cut, 5.24-6.21 m high, roofed with limestone gables at about base level [4]. Levels of the lower passage not found.
   - Verdict: consistent with what was read (PARTLY SUPPORTED); not independently confirmed.

11. A tunnel links the Great Pyramid to the Sphinx enclosure.
   - No survey source opened shows one; the Sphinx's known cavities are a few metres long ([16], secondary). Straight-line distance is of order 540 m.
   - Verdict: NO EVIDENCE.

12. Boat pits interrupt iron veins as "circuit breakers".
   - Geometry only: three large rock trenches east of the pyramid (54.1, 53.2 and 53.7 m long, 3.4-5.2 m wide, more than 5 m deep) and two roofed pits on the south [1][12]. Whether veins cross them is a geology/EM question.
   - Verdict (geometry): pits exist as described; function UNTESTABLE here.

---

## What a simulation of this domain needs

Geometry is the substrate for the other domains, so "governing equations" here are the constraints the CAD/mesh must satisfy and the simple balances that can already be closed from geometry.

Model definition
- One master parametric CAD in the frame above, built from the coordinate table (section B) plus the dimension table (section C). Build each void as a watertight solid; build the masonry as the complement inside a 230.35 m square pyramid of slope 51 deg 52' truncated at Z = 137.4 m (present) or completed to 146.71 m (original, optional pyramidion as a switch).
- Variant switches that must exist because the evidence is not settled: (1) casing on/off, and King's Chamber shafts open/closed through it; (2) outer 3 m of each King's Chamber shaft level vs inclined; (3) portcullis slabs absent / present (three slabs 1.21 m wide x 0.53 m thick, height unknown); (4) S-wall grooves blind vs connected; (5) granite plugs present/absent in the Ascending Passage; (6) Queen's Chamber shafts closed by 0.13 m of stone at the chamber end and by slabs at about 63.6 m; (7) pit original (about 1-1.7 m) vs excavated; (8) Big Void as horizontal or inclined (26.3 deg) prism, 30-40 m x Gallery section, centre Z 61-71 m; (9) North Face Corridor 9.06 x 2.02 x 2.18 m starting 0.84 m behind the chevrons; (10) Al-Ma'mun tunnel (modern) excluded for the "as built" case.
- Bedrock/masonry interface: rock rises to at least +5.70 m at the well shaft [8]; the Descending Passage enters rock about 30-34 m from the entrance [2]. Material assignment (Mokattam limestone bedrock, core limestone, Tura casing, Aswan granite for King's Chamber, Antechamber wainscots, plugs, relieving beams) must follow these interfaces.

Balances that follow directly from geometry (to hand to the fluid domain)
- Continuity for the "syringe": dV_water/dt in the Gallery = sum of volumetric gas inflows through every opening above the water line. With A_gallery(z) from the corbel table, a water-level fall rate w gives Q = A(z) w; gas speed in a duct of area a is Q/a. Example scaling: Gallery plan area is about 42 m x 1.05-2.09 m = 44-88 m2 against two King's Chamber shafts of 0.05 m2 each (ratio about 440-880 per shaft pair) and the four grooves at about 0.025 m2 total (ratio about 1800-3500).
- Hydrostatics: p = rho g (z_surface - z). Required head and wall loads listed above; the model needs a leakage law for unmortared/mortared joints (not a geometry input; joint width 0.5 mm mean on casing [1]).
- Free-surface CFD (VOF) equations and gas transport are for the fluid domain; geometry supplies A(z), connectivity and roughness.

Boundary and initial conditions supplied by this domain
- Elevations of all openings; cross-sections; the connectivity graph: Entrance -> Descending Passage -> {Ascending Passage (plugged) -> Gallery -> {Queen's passage -> Queen's Chamber (shafts blind); Antechamber -> King's Chamber -> two shafts -> outside}; well shaft -> Gallery foot; horizontal passage -> Subterranean Chamber -> {pit; S blind passage}}.
- Outside pressure at shaft outlets at Z about +80 m on N and S faces; entrance at +16.97 m on N face.
- Initial state: all spaces air-filled at ambient; water table position is a hydrogeology input (not found here).

Key dimensionless numbers and ratios (geometry-controlled)
- Scale ratio domain/smallest duct: 230 m / 0.2 m about 1150 (drives mesh strategy: 1D network elements for the four small shafts and the well shaft coupled to 3D chambers).
- Length/hydraulic-diameter of ducts: King's Chamber shafts L/D_h about 53/0.22 = 240 and 71/0.22 = 320; Queen's Chamber shafts about 290; well shaft about 60/0.68 = 90; Descending Passage about 105/1.12 = 94.
- Volume ratios: V_Gallery/V_DescPassage = 4.3; V_Gallery/V_King's = 1.8; V_Gallery/V_Antechamber about 31-38.
- Area ratios for gas draw (above).
- Froude number for the draining Gallery, Fr = w / sqrt(g h), and Reynolds number in the shafts, Re = U D_h / nu, are to be evaluated by the fluid domain using the areas here.
- Slopes: all main passages at tan(theta) about 1/2 (26.0-26.5 deg); shafts 31.5-32.6 deg and 44.4-45.5 deg (King's), 37.5-39.6 deg (Queen's).

Pass/fail criteria for this domain
- Geometric fidelity: every control point in table B reproduced within Petrie's stated +/- (worst case 3 in = 0.076 m); chamber volumes within the uncertainty column of table F; mesh voids watertight and non-intersecting; shaft exits fall on the casing plane at Z = 80 +/- 1 m.
- Hypothesis premises that are purely geometric (each can pass or fail without any physics):
  P1. Is there a continuous modelled water path from the stated source to the Gallery? Fails unless the hypothesis specifies an inlet below Z = 0 or a pump able to deliver at least 51.5 m head.
  P2. Stroke count: N = V_filled / V_swept. Pass if N is within +/-25 % of 4 for a stroke definition the hypothesis commits to in advance. Currently 4.3 (best case) to 8.9.
  P3. Gas path King's Chamber -> Gallery with slabs down: pass only if a connected duct exists in the as-surveyed geometry (blind-groove case fails; connected-groove case passes with a = about 0.025 m2).
  P4. Gallery as a draw-down barrel: pass if, with openings as surveyed, more than a stated fraction (say 90 %) of the displaced volume is drawn through the Antechamber path rather than other openings; needs the CFD but the openings list is fixed here.
  P5. Thermal contact Gallery-Big Void: geometry gives a masonry separation of about 10-20 m (uncertain); the thermal domain sets the criterion.

---

## Open questions

1. Maragioglio & Rinaldi 1965 (text and plates, hosted by the Harvard Giza Project) could not be read: both PDFs exceed the 10 MB fetch limit. They are the best source for: the Antechamber slots (depth, exact floor termination, distance of the third slot from the S wall), the low-passage sections, individual corbel heights in the Gallery, the relieving chambers, the Grotto, and the shaft outlets. Someone should read Tav. 3-7 and the corresponding observations directly.
2. Perring 1839 Plate 4 (figs 4-6) and Vyse 1840 (Heidelberg digital library) were bot-blocked. They are the primary evidence for the level outer stretch of the southern King's Chamber shaft and for the forced outer 47.5 ft of the northern one. The Perring-versus-Petrie conflict on the southern outlet is unresolved here.
3. Gantenbrink's Upuaut survey (lengths, bends, exact slopes, outlet details of all four shafts) not found in primary form: cheops.org now hosts unrelated content and the Wayback Machine is not reachable with the tools allowed. Richardson et al. 2013 (J. Field Robotics 30:323, DOI 10.1002/rob.21451) and Hawass et al. 2010 (ASAE 84) were not opened. The blocking-stone distances (about 63.6 m) and stone thicknesses are therefore press-level.
4. Individual corbel (lap) heights and the exact vertical height of the Gallery at several stations (Petrie's lap table was not recoverable through the extraction tool). The 573 m3 figure assumes equal lap heights.
5. True open volume and floor topography of the Subterranean Chamber; depth and present fill of the pit (9, 11 or 15 m).
6. Height of the underside of the granite leaf above the floor; section of the low passages (41.4 x 43.7 in is from memory).
7. Relieving-chamber geometry: only Vyse's heights via a search extract; no levels per chamber.
8. Big Void: no refined geometry after 2017 was found in a paper I could open; whether it is horizontal or inclined, single or multiple, is still open in [5]. Any 2024-2026 muon update (Nagoya/CEA) was not found.
9. Exploration news: I found only search-engine summaries stating that Z. Hawass said in November 2025 that a new discovery in Khufu's pyramid (described as a roughly 30 m corridor leading to a "door") would be announced in 2026, and that a July 2026 article still treated it as pending. I could not open any of those articles (one timed out, one returned no body, the BAM event page for a 1 Oct 2026 ScanPyramids lecture returned 404). Treat as unconfirmed. The video's statement that a 2026 robot mission into the Queen's Chamber northern shaft and a drilling into the Big Void are "already approved" could not be confirmed or refuted.
10. Recent ScanPyramids papers listed on the TUM project page but not opened: Maier et al. 2026 (ultrasonic testing of the lower King's Chamber wall blocks, Sci Rep 16:19035, DOI 10.1038/s41598-026-54151-6) and Sessa et al. 2026 (stone surfaces of the inner chambers, Sci Rep 16:12586, DOI 10.1038/s41598-026-48805-8); Elkarmoty et al. 2023 (NDT&E Int., DOI 10.1016/j.ndteint.2023.102809). The second may matter to the chemistry domain (surface deposits). I have not verified their contents.
11. South boat-pit dimensions, Sphinx enclosure dimensions and floor level, Osiris Shaft measured levels (Hawass 2007, ASAE), Dash's 2015 base survey (AERAgram 16-2; JEA 102:186-195) and Cole 1925: not opened; values above are secondary or from memory.
12. Position of the water table under the pyramid (needed for the "aquifer" claim): not in this domain's sources; Petrie mentions only rain water in the pit.
13. The diagram Drumm shows for the "horizontal termination" is attributed to Matt Sibson's channel; I could not find the video. It is very likely Perring's Plate 4 or the M&R redrawing of it.

---

## Sources

Opened and read this session
1. W. M. F. Petrie, The Pyramids and Temples of Gizeh (1883), ch. 6 "Outside of the Great Pyramid", s.20-34. http://www.ronaldbirdsall.com/gizeh/petrie/c6.html (read through WebFetch extraction).
2. Petrie 1883, ch. 7 "Inside of the Great Pyramid", s.35-64. http://www.ronaldbirdsall.com/gizeh/petrie/c7.html (WebFetch extraction; s.64 summary table used for coordinates).
3. Petrie 1883, ch. 8 (Second Pyramid, outside), s.66-72. http://www.ronaldbirdsall.com/gizeh/petrie/c8.html
4. Petrie 1883, ch. 9 (Second Pyramid, inside), s.73-78. http://www.ronaldbirdsall.com/gizeh/petrie/c9.html
5. K. Morishima et al., "Discovery of a big void in Khufu's Pyramid by observation of cosmic-ray muons", Nature 552, 386-390 (2017), DOI 10.1038/nature24647; author manuscript arXiv:1711.01576 (PDF pages 1-7 read). https://arxiv.org/abs/1711.01576
6. S. Procureur et al., "Precise characterization of a corridor-shaped structure in Khufu's Pyramid by observation of cosmic-ray muons", Nat. Commun. 14, 1144 (2023), DOI 10.1038/s41467-023-36351-0. https://pmc.ncbi.nlm.nih.gov/articles/PMC9981702/
7. T. Schumacher et al., "Confirmation of the ScanPyramids North Face Corridor ... using multi-modal image fusion from three non-destructive testing techniques", Sci. Rep. 15, 9275 (2025), DOI 10.1038/s41598-025-91115-8. https://pmc.ncbi.nlm.nih.gov/articles/PMC11920056/
8. M. Haase, "Der Serviceschacht der Cheops-Pyramide", Sokar 9 (2/2004), 12-17 (PDF read in full). https://giza.fas.harvard.edu/pubdocs/542/full/ (PDF: https://d1g9lvwdq3dcse.cloudfront.net/images/MFA-images/Giza/GizaImage/full/library/haase_sokar_9_2004.pdf)
9. E. Thomas, "Air channels in the Great Pyramid", Journal of Egyptian Archaeology 39 (1953), 113 (PDF read). https://giza.fas.harvard.edu/pubdocs/407/full/
10. A. Badawy, "The Stellar Destiny of Pharaoh and the So-Called Air-Shafts of Cheops' Pyramid", Mitteilungen des Instituts fuer Orientforschung 10 (1964), 189-206 (pp. 189-193 read). https://d1g9lvwdq3dcse.cloudfront.net/documents/badawy_mio_10_1964.pdf
11. A. P. Sakovich, "Explaining the Shafts in Khufu's Pyramid at Giza", JARCE 42 (2005-2006), 1-12 (pp. 1-2 read; quotes Smyth 1877 p. 392 and Edwards). https://d1g9lvwdq3dcse.cloudfront.net/images/MFA-images/Giza/GizaImage/full/library/sakovich_jarce_42_2005-6.pdf
12. Wikipedia, "Great Pyramid of Giza" (secondary; cites M&R 1965, Dormion 2004, Haase 2004, Vyse 1840, Perring 1839, Lehner 1997). https://en.wikipedia.org/wiki/Great_Pyramid_of_Giza
13. Wikipedia, "Star shaft" (secondary). https://en.wikipedia.org/wiki/Star_shaft
14. "An Overview of the History of Ideas on the Purpose of the Shafts in Khufu's Pyramid" (secondary web page with Gantenbrink figures, uncited). https://sites.google.com/site/okadct/anoverviewofthehistoryofideasontheshafts
15. J. Alison, "Internal dimensions of the Great Pyramid" and "Petrie's survey by triangulation" (secondary pages quoting Petrie). https://home.hiwaay.net/~jalison/gpkc.html ; https://home.hiwaay.net/~jalison/gpsp.html
16. Wikipedia: "Pyramid of Khafre", "Great Sphinx of Giza", "Giza pyramid complex", "Upuaut Project", "Khufu ship" (secondary). https://en.wikipedia.org/wiki/Pyramid_of_Khafre ; https://en.wikipedia.org/wiki/Great_Sphinx_of_Giza ; https://en.wikipedia.org/wiki/Giza_pyramid_complex ; https://en.wikipedia.org/wiki/Upuaut_Project ; https://en.wikipedia.org/wiki/Khufu_ship
17. A. M. H. Schuster, "Tales from the Crypt", Archaeology 53(5), Sept/Oct 2000 (abstract page). https://archive.archaeology.org/0009/abstracts/crypt.html
18. TU Munich, Chair of Non-destructive Testing, "ScanPyramids Project" page (publication list with DOIs up to 2026). https://www.mae.ed.tum.de/zfp/forschungsprojekte/scanpyramids-project/
19. Web-search result summaries only (article bodies NOT opened; everything taken from them is marked verified = false): extracts of Vyse 1840 and Perring 1839 on digi.ub.uni-heidelberg.de; press on the 2015 Dash survey; NBC/Leeds/The Engineer on the Djedi robot; WAM and Tribune India (Nov 2025) on Hawass's statement at the Sharjah book fair (https://www.wam.ae/en/article/bmm4hcn-new-discovery-inside-egypts-pyramid-khufu-revealed).
20. Local transcripts of the three videos (paths in the task statement).

Tried and failed (not used as sources)
- Maragioglio & Rinaldi, L'Architettura delle Piramidi Menfite IV (1965), text and plates: https://giza.fas.harvard.edu/pubdocs/550/full/ and /577/full/ (PDFs larger than the fetch limit).
- Gantenbrink, The Upuaut Project, cheops.org (domain now unrelated; Wayback not reachable).
- Vyse 1840 and Perring 1839 at digi.ub.uni-heidelberg.de (bot protection).
- Nature.com article pages (cookie redirect; PMC copies used instead).
- BAM event page for the 1 Oct 2026 ScanPyramids guest lecture (HTTP 404).
