# 09 - Independent recomputation and cross-file consistency check

Date: 2026-10-10. Scope: every derived estimate in files 01 to 07, recomputed from the Parameters-table inputs of those files; then a list of places where two files give different values for the same physical quantity.

How this was done
- I read the Parameters tables first, wrote one script that computes each quantity from the raw inputs with my own formulas, ran it, and only then read the first-pass working sections (02 sec. 4, 03 sec. 3, 04 sec. 4, 05 sec. 4, 07 sec. 4.2) and compared. For file 01 the inputs and the volume table sit side by side, so that comparison was not blind; the arithmetic is still independent.
- Tool: python3, standard library only. Scripts: `recompute.py` and `extra.py`, throwaway scripts not kept in the project; the ledger and the `pyramid` packages are the reproducible record.
- Constants used here: 1 in = 0.0254 m; g = 9.80665 m/s2; water density 998.2 kg/m3 (20 C); R = 8.3145 J/mol/K; 1 atm = 101 325 Pa; eps0 = 8.854e-12 F/m; mu0 = 4 pi e-7 H/m; c0 = 2.998e8 m/s. The first pass used 1000 kg/m3 and 9.81, which is why some of my pressures are 0.2 percent lower.
- "Agree" means within the uncertainty the first pass itself stated, or within 3 percent where none was stated. "Partly" means the arithmetic reproduces but a label, range or input choice is wrong or too narrow.
- This file checks arithmetic and internal consistency. It does not re-verify the sourced inputs, except for four spot checks listed in section 5. A recomputed value is only as good as its inputs.
- The advisor (second-reviewer) tool was rate-limited in this session, so this file has had no independent review either.

---

## 1. Result in brief

1. No first-pass arithmetic is wrong by more than a rounding step. Of the 51 rows below, 43 agree outright, 7 reproduce but need a corrected label, range or input choice, and 1 (well shaft) is a cross-file conflict.
2. Nine items need correction or a changed label (details in the table):
   - (01) The Subterranean Chamber "upper bound" of 414 to 459 m3 is not an upper bound. It uses floor depths of 140 and 155 in; Petrie's deepest floor is 198 in below the roof, which gives a bounding box of 586 m3. On re-reading Petrie s.37 the 155 in figure is a knob of rock beside the pit, not a "main floor".
   - (01) The "Gallery plan area 44 to 88 m2" used for the syringe scaling is the plan projection of the whole gallery, not the free-surface area. A horizontal water surface in a prism inclined at 26.3 deg has area S/tan(theta) = 13.6/0.494 = 27.6 m2 at most. File 03 used about 25 m2, which is right.
   - (01) The original pit depth is given as "about 1 to 1.7 m" in the text and as 1.7 + 1.0 = 2.7 m in the volume table. Petrie's figures (ledge at 67 in, about 40 in below it) give 2.7 m, bottom at about -34.6 m.
   - (02) The piston-force range 0.58 to 0.95 MN is for a piston parked at -25 m. The stroke counts in the same file sweep the passage to its end at -30 m, where the force is 0.64 to 1.01 MN.
   - (02) Pit bottom "-36 to -41 m" does not follow from the inputs: Petrie's 30 ft below the -31.85 m floor is -41.0 m, Haase's 11 m is -42.9 m, Vyse's 50 ft is -47.1 m.
   - (03) The summary says dissolved-oxygen supply takes "weeks to years" for a full batch. The file's own working, and mine, give about 3 to 30 years for a full batch and about 2.5 months to 2.3 years for a 10 percent batch. "Weeks" needs an agitated surface (transfer coefficient near 1e-4 m/s), which the file does not assume.
   - (04) The summary quotes eps'' = 13 to 67 "at 1 MHz". Those values are for 0.90 MHz (the 333 m resonance), as the working section says. At 1.00 MHz it is 12 to 60.
   - (04) The collection-area formula used is the one for a flat-roofed rectangular block. For a pyramid whose faces are steeper than the 1:3 construction line, the apex alone governs and the area is pi (3H)^2 = 0.61 km2, not 1.07 km2. The strike rate falls by a factor 1.75. The upper end of the first-pass range (0.5 per year) also rests on a ground-flash density of 0.5 per km2 per year, which is 2.5 times the only sourced figure (0.2, total lightning, national mean).
   - (05) Two 2 dB slips in the shaft link budget: the low ends should read 102 dB (13 kHz) and 236 dB (40 kHz), as the file's own table adds up.
3. Two cross-file inconsistencies change a conclusion's wording rather than a number:
   - File 07 judges the "acid-filled pit as circuit breaker" using 56 to 76 S/m (15 to 31 wt percent acid). File 03 caps the product at 0.24 wt percent, which conducts at about 1 S/m (my estimate from recalled limiting ionic conductivities; order of magnitude only).
   - File 03's acid ceiling (0.024 mol/L) assumes a King's Chamber of pure SO2. If the oxygen must arrive in the same gallery-volume of gas that the "syringe" draws, the stoichiometric SO2 fraction is 29.5 percent and the ceiling is 0.012 mol/L.
4. Direction of the corrections: the piston-force, oxygen-time, acid-ceiling and lightning corrections each go against the hypothesis, by small factors (6 percent, a wording change, a factor 2 and a factor 1.75). The Subterranean Chamber, pit and free-surface corrections do not change any verdict. None of the corrections helps the hypothesis, and I found no first-pass number that was overstated against it; the one over-generous figure was the strike-rate upper bound. Two results remain favourable to the hypothesis and survive recomputation: the gallery-to-passage volume ratio is 4.3, within 10 percent of "four strokes" under the most generous stroke definition, and a perched water table above about 20 m asl (25 m asl if the pit is in its original state) would remove the suction objection.

---

## 2. Recomputation table

Inputs are named with the file they come from. First-pass values are quoted from the file named in the same cell.

### 2.1 Internal volumes (file 01 section F; also 02 sec. 4.3, 03 sec. 2f)

| # | Quantity | Inputs used (source file) | First-pass value | Recomputed | Agree? | Note |
|---|---|---|---|---|---|---|
| 1 | Descending Passage length and volume | s.64 end coordinates; section 41.53 x 47.24 in (01 B, C) | 105.15 m; 133 m3; 35.7 above / 97.4 below the junction (01) | 105.15 m; 1.2657 m2; 133.1 m3; 35.7 / 97.4 m3 | yes | Part below pavement level: 30.00/sin 26.52 = 67.2 m, 85.0 m3 (02 uses this). Part in bedrock (71 to 75 m): 90 to 95 m3. |
| 2 | Horizontal passage to Subterranean Chamber | 346 in x 31.6-33.3 in x 38 in (01 C) | 6.9 m3 (01) | 6.8 to 7.2 m3 | yes | Height is a single-extraction figure. |
| 3 | Subterranean Chamber bounding box | 553.8 x 325.9 in plan; floor 140 / 155 / 198 in below roof (01 C; 02 2.1) | 414 to 459 m3 "upper bound only"; likely 250 to 350 (01). About 300, range 250 to 470 (02) | 414 (140 in); 458 (155 in); 586 (198 in) m3 | partly | Arithmetic reproduces. The label is wrong: the true bounding box is 586 m3. Baseline 300 +/- 100 is still reasonable because the west half is uncut rock. |
| 4 | South blind passage | 646 in x 26.0-30.1 in x 0.75 m (01 C) | 8.9 m3 (01) | 8.1 to 9.4 m3 | yes | |
| 5 | Well shaft length and volume | Haase segments 1.40+7.96+7.90+5.20+26.50+9.50+1.85 m with sections (01 C) | 60.31 m, 28.8 m3 (01); about 50 m, 25 m3 (02) | 60.31 m; 28.8 m3 | yes (01); 02 differs | See conflict K2. |
| 6 | Ascending Passage | 1546.8 in x 41.6 x 47.3 in; plugs 178.5 in x 38.2-39.9 x 47.3 in (01 C) | gross 49.9; plugs 5.5; free 44.3 m3 (01); 45 (02) | 49.9; 5.3 to 5.5; 44.4 to 44.6 m3 | yes | |
| 7 | Queen's passage | 1307.0 in x 1.05 x 1.17 m + 216.9 in x 1.05 x 1.68 m (01 C) | 50.5 m3 (01); 51 (02) | 50.5 m3 | yes | Section is secondary (Wikipedia citing M&R). |
| 8 | Queen's Chamber | 205.85 x 226.47 x 184.47 in box + gable 0.5 x 205.85 x 60.63 x 226.47 in (01 C) | 164.1 m3 + niche 5.1 (01); 167 incl. niche 3 (02) | 164.1 m3 (box 140.9 + gable 23.2); niche 5.1 | yes | |
| 9 | Queen's Chamber shaft, each | 63.6 m x 8.6 x 8.0 in (01 C) | 2.8 m3 (01) | 2.82 m3; section 0.0444 m2 | yes | |
| 10 | Grand Gallery | ramp slot 41.2 x 23.86 in; 82.42 in to first lap at 2.29 m; seven laps to 8.6 m, overhang 20.55 in per side; floor 1883.6 in at 26 deg 16' 40"; roof 1648.4 in horizontal (01 C) | 573 m3 (01); 570 +/- 40 (02); about 550 +/- 15 % (03) | section 13.61 m2; mean horizontal length 42.38 m; gross 577; minus step 1.7: 575 m3 | yes | Bracket 558 to 577 by other reasonable readings of the same inputs. Would be 643 if 8.6 m were measured perpendicular to the slope; Petrie's 334 to 344 in is vertical, so that reading is excluded. Lap heights are assumed equal. |
| 11 | Antechamber gross volume and surface | 116.30 x 65.00 x 149.35 in (01 C; 05 2.1) | 18.5 m3 (01, 05); 44.7 m2 (05) | 18.50 m3; 44.7 m2 | yes | |
| 12 | King's Chamber | 412.25 x 206.13 x 230.1 in (01 C) | 320.4 m3 (01); about 320 (03) | 320.4 m3; 319.3 net of coffer stone; 327.2 if the 235 in wall-base height is used | yes | Use floor-to-ceiling for gas volume. |
| 13 | King's Chamber shafts | 71.0 m x 9.05 x 8.73 in; 53.1 m x 8.5 x 8.8 in; shaft line to casing plane (01 C) | 3.6 and 2.6 m3; lengths 68-70 + 1.5-2.6 m and 51.7 + 1.5-1.7 m; exit Z 80 +/- 1 m (01) | 3.62 and 2.56 m3; sloping 69.3 and 51.9 m plus 1.5 m level (70.8 and 53.4 m); exits Z 80.2 to 81.1 m (N) and 80.8 m (S) | yes | |
| 14 | Other voids | NFC 9.06 x 2.02 x 2.18; Big Void 30 x gallery section; Khafre 557.9 x 195.8 x (206.4 + 19.0) in; relieving chambers (01 C, D, E) | 39.9; at least about 400; 403; about 330 m3 (01) | 39.9 (31.9 with CEA dimensions); 408; 403; 326 m3 | yes | |
| 15 | Total to be filled before the gallery is full | rows 5 to 8 and 10 | about 866 (01); about 860 (02) | 868 m3 | yes | |
| 16 | Largest free-surface area in the gallery | section 13.61 m2; slope 26.28 deg | "plan area 44 to 88 m2" used as A(z) (01 sim section); about 25 m2 (03 C5) | 13.61/tan 26.28 = 27.6 m2 (for water levels between +30.3 and +42.9 m; smaller near both ends) | 03 yes; 01 no | Area ratios for gas draw become about 280 (two King's Chamber shafts, 0.099 m2) and about 1000 to 1100 (four grooves), not 440 to 880 and 1800 to 3500. |

### 2.2 Hydraulics (file 02 section 4; file 01 derived checks)

| # | Quantity | Inputs used (source file) | First-pass value | Recomputed | Agree? | Note |
|---|---|---|---|---|---|---|
| 17 | Hydrostatic pressure to fill the gallery to its roof | roof +51.5 m; passage end -30.0; chamber floor -30.4 / -31.9 (01 B; 02 2.1) | 0.80 MPa, 81.5 m head; 0.82 MPa at -31.9 (02). 5.1 bar at Z = 0; 8.0 bar at chamber floor; 2.9 bar at gallery foot (01) | 0.798 MPa (81.5 m); 0.802 (-30.4); 0.816 (-31.9); 5.04 bar at Z = 0; 2.92 bar at +21.66 | yes | |
| 18 | Force on a piston in the descending passage | A = 1.266 m2; water surface +21.66 or +51.5 m (02 4.2) | 0.58 to 0.95 MN, piston at -25 m; 0.64 MN at Z = 0 (02) | piston at -25 m: 0.578 to 0.948 MN; at passage end -30 m: 0.640 to 1.010 MN; at junction +4.39: 0.584 MN (gallery full); at entrance +16.97: 0.428 MN | partly | Quote "0.43 to 1.01 MN with the gallery full, depending on piston position". A full-length stroke, which the stroke count assumes, ends at 1.01 MN (103 tonnes-force). |
| 19 | Gravity plunger check | granite 2650 kg/m3; slope 26.52 deg; friction 0.5 (02 4.2) | 32.9 kN per m; down-slope 14.7 kN/m; friction 14.7 kN/m; 65 m of granite for 950 kN (02) | 32.9; 14.7; 14.7 kN/m; 64.6 m (68.7 m for 1.01 MN) | yes | Density and friction are assumed, not sourced. |
| 20 | Pump stroke counts | rows 1, 10, 15 | 01: 4.3 (gallery / full passage); 5.9 (gallery / below junction); 6.5 and 8.9 (all spaces). 02: 4.3; 6.7 (gallery / below pavement); 6.5; 10.1 (all / below pavement) | gallery only: 4.32 / 5.90 / 6.76 / 6.1-6.4 (full / below junction / below pavement / bedrock part); all spaces: 6.52 / 8.91 / 10.2 / 9.1-9.7 | yes | 01 and 02 use different "lower stroke" definitions; both are right for their definition. See K6. |
| 21 | Ideal lifting work | volumes and centroids (gallery 36.2 m, Queen's Chamber 23.9 m) (02 4.3) | 260 MJ from pavement level; about 510 MJ from -30 m; about 640 MJ from -46 m (02) | 260 MJ; 523 MJ (from -31 m); 651 MJ (from -46 m); 710 MJ (from -53 m, Old Kingdom low water) | yes | My gallery centroid: mid-floor 32.28 m + section centroid 3.92 m = 36.2 m, same as 02. |
| 22 | Suction-lift margin | atmospheric pressure, vapour pressure 2.34 kPa; base 60 m asl; chamber floor -30.4 to -31.9 m; water tables 7 to 14 (Old Kingdom) and 15 to 17 m asl (modern) (02 2.2) | limit 10.1 m; lift needed 14 to 23 m (Old Kingdom), 11 to 15 m (modern) (02) | limit 10.1 m at 20 C (9.9 at 30 C); lift 14.1 to 22.6 m and 11.1 to 14.6 m; margin -4.0 to -12.5 m and -1.0 to -4.5 m | yes | Added: the original pit bottom (-34.6 m, 25.4 m asl) is 8 to 18 m above every documented non-perched water table (7 to 17 m asl), so the pit as first cut did not reach it. Break-even table for a piston at the passage end: 19.9 m asl in theory, about 22 to 24 m asl in practice. |
| 23 | Air flow through the King's Chamber shafts while the gallery drains | shaft areas 0.0508 and 0.0484 m2; loss coefficients 19 and 14.5; 570 m3 (02 4.5) | 1.5 and 1.7 m/s; 26 Pa for a 1 h drain; 0.9 kPa for 10 min; under 1 Pa for 6 h (02) | 1.48 and 1.71 m/s; 25 Pa; 0.93 kPa; 0.7 Pa. Independent single-duct estimate with f = 0.04: 20 Pa | yes | Friction factor 0.05 is assumed. |
| 24 | Leak-off and piston-gap leakage | cubic law, 1350 m of joint, gradient 15; gap 1 mm x 4.5 m x 1 m at 0.75 MPa (02 4.6) | 2 m3/s, 17 L/s, 2 L/s; 5 min, 9.5 h, 3 d; gap 0.28 m3/s; Darcy 0.14 to 14 L/s (02) | 2.07 m3/s, 16.6 L/s, 2.07 L/s; 4.6 min, 9.5 h, 3.2 d; 0.281 m3/s; 0.135 to 13.5 L/s | yes | Wall area: I get about 1000 m2 for the gallery (walls 729 + floor and roof 148 + ramp sides and soffits about 100 + ends 27), against 800 to 900 used in 02 and 03. |
| 25 | Hydraulic ram delivered fraction | efficiency 0.6; fall 30 m; lift 81.5 m (02 4.7) | q/Q = 0.22; about 3000 m3 spilled per 860 m3 delivered (02) | 0.221; 3030 m3 | yes | |

### 2.3 Chemistry (file 03 sections 2 and 3)

| # | Quantity | Inputs used (source file) | First-pass value | Recomputed | Agree? | Note |
|---|---|---|---|---|---|---|
| 26 | SO2 the King's Chamber can hold | 320.4 m3 (01); 1 atm; 293.15 K | 1.33e4 mol, about 850 kg; 1.3 t H2SO4 (03) | 13 320 mol; 853 kg SO2; 1306 kg H2SO4 (13 100 mol at 298 K) | yes | |
| 27 | Acid-concentration ceiling | row 26; water 550 m3 (03) or 573 m3 (01) | 0.024 mol/L = 0.24 wt %, pH about 1.5 (03) | 0.0242 mol/L, 0.238 wt %, pH 1.52 in 550 m3; 0.0232 in 573 m3; 0.0153 if spread over all 868 m3 of filled space | yes | Stricter, self-consistent ceiling: if SO2 and its oxygen arrive in one gallery-volume of drawn gas, x(SO2) = 1/(1 + 0.5/0.2095) = 0.295, n = 7030 mol, 0.0123 mol/L, pH 1.77. Ka2 = 0.0102 is recalled, not sourced. |
| 28 | Adiabatic temperature rise and batch heat | dH = -326.7 kJ/mol; cp 4.18 kJ/kg/K (03 2a) | 78 K per mol/L; 1.9 K; 7.5 K if all heat goes into the first quarter fill; 4.3e9 J (03) | 78.2 K per mol/L; 1.89 K (1.82 K in 573 m3); 7.6 K; 4.35e9 J = 1209 kWh | yes | If the second proton stays largely undissociated at this strength, dH is nearer -304 to -310 kJ/mol and the rise is about 1.8 K. At the stricter ceiling of row 27: 0.96 K. |
| 29 | Reaction enthalpies and equilibrium constant | formation enthalpies and entropies (03 2a) | -98.9; -132.4; -95.4; -326.7; -518.0; +150.2 kJ/mol; log10 Kp 12.42 (298 K), 12.31 (300 K) (03) | -98.96; -132.39; -95.35; -326.70; -518.04; +150.22; 12.43; 12.32 | yes | My Kp uses dH and dS at 298 K, not the JANAF log Kf difference; the 0.01 difference is rounding. |
| 30 | Upper bound on the uncatalysed gas-phase rate | prefactor 1e-10 cm3/s; barrier 150.2 kJ/mol; 300 K; O2 at 20.95 % of 1 atm (03 2b) | k at most 7e-37 cm3/molecule/s; lifetime at least 3e17 s, about 1e10 yr (03) | 7.0e-37; [O2] = 5.13e18 cm-3; 2.8e17 s = 8.8e9 yr; shortfall against a 1 h half-life: 13.7 orders | yes | |
| 31 | SO3 hydration and OH lifetimes | Jayne and Lovejoy rate forms; 50 % RH at 298 K; OH 1e6 cm-3 (03 2b) | 20 to 30 microseconds; about 12 days (03) | 19 and 29 microseconds; 11.1 to 12.3 days | yes | Rate forms are from search snippets (03 says so). |
| 32 | Dissolved oxygen against demand | Henry constant 1.3e-5 mol/m3/Pa; O2 at 0.2095 atm (03 2d) | 0.28 mol/m3; about 150 mol in 550 m3; about 2 % of a maximal batch; air needed about 760 m3 (03) | 0.276 mol/m3; 152 mol (158 in 573 m3); 2.3 to 2.4 % of the 6660 mol O2 demand; 765 m3 of air, 1.33 gallery volumes | yes | |
| 33 | Time to supply the oxygen through the free surface | transfer coefficient 1e-6 to 1e-5 m/s (assumed in 03); surface 25 m2 (03) or 27.6 m2 (row 16) | summary: "weeks to years for a full batch"; body: "years" (full), "months" (10 % batch) (03) | full batch: 2.7 to 30 yr; 10 % batch: 77 days to 2.3 yr | partly | The body text is right; the summary's "weeks" is too optimistic by its own inputs. The transfer coefficient is the controlling unsourced input: 1e-4 m/s (agitated or flowing surface) would give 100 days for a full batch. |
| 34 | Aqueous checks | pKa1 1.9, pKa2 7.2; H = 1.3 mol/L/atm; Fe(III) law (03 2d) | SO2 partial pressure about 0.9 % over 0.024 mol/L; Fe-catalysed rate about 3e-7 mol/L/s, about a day (03) | 0.92 %; 2.9e-7 mol/L/s; 0.8 day | yes | |
| 35 | Gypsum-armour arithmetic | D = 1.71e-15 to 4.54e-14 m2/s; 10 micrometre layer; pH 1.5; solubility 0.015 mol/kg (03 2e) | flux 5e-9 to 1.4e-7 mol/m2/s; under 0.1 % of a batch per day; Ca about 0.01 mol/L; 40 % of acid consumed; 8000 mol gypsum per fresh fill; 0.7 mm (03) | 5.4e-9 to 1.4e-7; 0.04 % per day; 0.0094 mol/L; 39 %; 8250 mol; 0.68 mm | yes | Gypsum molar volume 74.7 cm3/mol is recalled. |
| 36 | HCl partial pressure over the dilute mixture | effective Henry constant 2.0e6 mol2/L2/atm (03 2d) | about 1e-7 atm (03) | 1.25e-7 atm for 0.05 mol/L H+ in 5 mol/L chloride; 1.5e-8 to 9e-8 atm at the row-27 acid strength | yes | |

### 2.4 Electromagnetics and piezoelectricity (file 04 section 4; file 07 section 4.2)

| # | Quantity | Inputs used (source file) | First-pass value | Recomputed | Agree? | Note |
|---|---|---|---|---|---|---|
| 37 | Frequencies and the paper's equivalent conductivity | 200 to 600 m; eps'' = 0.1 (04) | 0.50 to 1.50 MHz; 2.8e-6 to 8.3e-6 S/m (04) | 0.500 to 1.499 MHz; 2.78e-6 to 8.34e-6 S/m | yes | |
| 38 | Imaginary permittivity implied by measured resistivity | 300 to 1500 ohm m (04) | summary: "13 to 67 at 1 MHz"; working: 67 to 13 at 0.90 MHz (04) | 66.6 to 13.3 at 0.90 MHz; 59.9 to 12.0 at 1.00 MHz | partly | Label slip in the summary only. |
| 39 | Skin depths | general lossy-medium formula, eps' = 7 (04); good-conductor formula (07) | 9.7 m and 26 m at 0.90 MHz; 2.4 km with the paper's values; 36 m (100 kHz, 500 ohm m); 110 m (10 kHz) (04). 50 m at 10 kHz and 5 m at 1 MHz for 100 ohm m (07) | 9.7 and 26.4 m; 2.37 km; 35.6 m; 112.5 m; 50.3 m and 5.0 m (5.1 m with the full formula) | yes | The good-conductor formula would give 20.5 m instead of 26 m at 1500 ohm m; 04 correctly used the general formula there. |
| 40 | Charge-relaxation times | tau = eps0 epsr rho; limestone epsr 7; granite epsr 6 (04) | 19 ns, 93 ns, 62 microseconds; 0.5 microseconds to 5 ms (04) | 18.6 ns, 93.0 ns, 62.0 microseconds; 0.53 microseconds to 5.3 ms | yes | With the low-frequency Aswan value epsr = 24 the slowest case is 21 ms; still far below storm time scales. |
| 41 | Lightning collection area and strikes per year | L = W = 230.3 m, H = 146.6 m; block formula; Ng 0.05 to 0.5 (04) | 1.07e6 m2 (0.98e6 for 138.75 m); 0.05 to 0.5 strikes per year (04) | block formula: 1.066e6 and 0.981e6 m2 (reproduces). Apex-governed area for a pyramid: 0.608e6 m2 (0.552e6 for the present truncated top). Strikes: 0.03 to 0.12 per year (apex area) or 0.05 to 0.21 (block area) for Ng 0.05 to 0.2 | partly | One strike every 8 to 33 years on the better-founded area. The first-pass upper end needs Ng = 0.5, which has no source. The 1:3-line definition was seen only in a search summary of a secondary copy of the standard; the geometric consequence is mine. |
| 42 | Lightning and telluric fields in the rock | 30 kA and 200 kA; 300 to 1500 ohm m; 163 m square section at +43 m (04 4.5) | 4.8 kA/m2 and 1.4 to 7 MV/m at 1 m; 2.4 m ionisation radius; 1.1 A/m2 and 0.34 to 1.7 kV/m at chamber level; 2.3 to 11 kV/m at 200 kA; telluric 23 mV and 4.6 V across the base; 3e-3 J/m3, about 8 kJ (04) | 4.77 kA/m2; 1.43 to 7.2 MV/m; 2.44 m; 1.13 A/m2; 0.34 to 1.70 kV/m; 2.3 to 11.3 kV/m; 23 mV; 4.6 V; 3.1e-3 J/m3; 8.0 kJ | yes | |
| 43 | Piezoelectric displacement and radiated intensity (04 scenarios) | d = 1.4e-15 C/N; E = 1 kV/m or 3 MV/m; L = 1 m; air 413 Pa s/m (04 4.6) | 1.4 pm; 1.6e-15 W/cm2 (5 microsecond rise); 4.2 nm and 5.8e-9 W/cm2 at 20 kHz and 3 MV/m; 3.9e10 V/m for 1 W/cm2 in air (04) | 1.40 pm; 1.62e-15 W/cm2; 4.20 nm; 5.75e-9 W/cm2; 3.96e10 V/m. All nine cells of both scenario tables reproduce | yes | Sinusoidal equivalents at 1 kV/m: 6.4e-16 W/cm2 at 20 kHz, 2.6e-15 at 40 kHz. Shortfall against 1 W/cm2: 14.6 to 15.2 orders (lightning case), 8.2 orders (breakdown-field case). |
| 44 | Vein conductivity contrast for a 100 m leakage length | lambda = sqrt(sigma_v A ln(2 lambda/a)/(2 pi sigma_h)); A = 0.03 m2 (07 4.2) | sigma_v/sigma_h about 3e5; vein below about 3e-4 ohm m in 100 ohm m rock (07) | 2.75e5; 3.6e-4 ohm m | yes | Sensitivity: 3.9e3 for a 10 m leakage length; 3.2e4 for A = 0.3 m2; 5.7e6 for 500 m. With file 04's in-situ host values (300 to 1500 ohm m) the vein threshold is 1e-3 to 5e-3 ohm m. |
| 45 | Acid conductivity used for the pits | 1.800, 1.494, 1.310 ohm cm (07) | 55.6, 66.9, 76.3 S/m (07) | 55.6, 66.9, 76.3 S/m | yes (arithmetic) | Not the hypothesis's acid. At the row-27 ceiling the conductivity is about 1 S/m. See K17. |

### 2.5 Acoustics and sonochemistry (file 05 section 4)

| # | Quantity | Inputs used (source file) | First-pass value | Recomputed | Agree? | Note |
|---|---|---|---|---|---|---|
| 46 | Sound level from the granite leaf at the breakdown field | d = 1.4e-15 C/N; 3 MV/m; L = 0.40 m; 40 kHz; air 428 Pa s/m (05 4.2) | 1.7 nm; 4.2e-4 m/s; 0.128 Pa rms; 76 dB; 3.8e-9 W/cm2. Single-crystal ceiling: 139 dB, 7.8e-3 W/cm2 (05) | 1.68 nm; 4.22e-4 m/s; 0.128 Pa; 76.1 dB; 3.82e-9 W/cm2 (75.8 dB with 413 Pa s/m); ceiling 139.2 dB, 7.8e-3 W/cm2 | yes | Correction factors also reproduce: -26.8 dB for 3.5 wavelengths of thickness; +23 to +40 dB at resonance for Q 14 to 100. |
| 47 | Level needed to cavitate a wet film from the gas side | air-to-water intensity transmission 4 Z1 Z2/(Z1+Z2)^2; 1 W/cm2 in the liquid (05 4.1) | T = 1.14e-3 (-29.4 dB); about 870 W/cm2 in air; 189 dB; gap 104 to 113 dB (05) | 1.141e-3; 877 W/cm2; 189.4 dB; gap 104 to 113 dB | yes | Using the measured pressure thresholds in the same file (2.5 to 6.5 atm at 25 kHz) instead of the 1 W/cm2 bath figure gives 193 to 201 dB, which exceeds one atmosphere of pressure amplitude in air and cannot be reached at all. The 189 dB criterion is the lenient one. |
| 48 | Acoustic temperature swing and Arrhenius factor | dT = T0 (gamma-1)/gamma x p'/p0; Ea = 100 kJ/mol (05 4.1) | 1.5e-4 K at 76 dB; 9.3 K at 172 dB; factor 1.47 at 172 dB; 449 J/m3; 1.1e-4 eV per molecule (05) | 1.50e-4 K; 9.30 K; 1.47; 448 J/m3; 1.1e-4 eV | yes | |
| 49 | Room build-up in the antechamber at 40 kHz | 1.318 dB/m; V = 18.5 m3; S = 44.7 m2 (05 4.3) | absorption area 23.4 m2; gain +3 dB; 57 kW for 160 dB; 0.9 MW for 172 dB; reverberant level 85 dB (05) | 23.4 m2; +3.3 dB; 56.6 kW; 0.90 MW; 84.8 dB | yes | |
| 50 | Ultrasonic path loss, Queen's Chamber shaft link | air absorption 0.25 / 0.525 / 1.318 dB/m; 63 m legs; stone impedance 3.7e6 to 1.3e7 (05 4.5) | wet path: 100 to 118 dB at 13 kHz, 234 to 252 dB at 40 kHz (text) or 236 to 252 (table); dry: 168 to 188 and 302 to 322 dB (05) | one way along the south shaft, air only: 15.9 dB (13 kHz), 33.4 dB (20 kHz), 83.8 dB (40 kHz). Full link as 05 defines it: 102 to 118 dB and 236 to 252 dB wet; 168 to 188 and 302 to 322 dB dry | yes (2 dB slips) | Interfaces reproduce: air to soft limestone -33.3 to -33.9 dB; air to dense stone -38.6 dB; stone to water -0.9 to -4.2 dB. Source level 60 dB (40 kHz) and 50 dB (13 kHz) reproduce. |
| 51 | Minor acoustic quantities | (05 2.2, 4, 5) | granite attenuation 2.4 to 17 dB/m at 40 kHz; quartz d11 1.8 to 2.0 pm/V; k2 about 0.9 %; modes 58 / 104 / 45 Hz and 16.4 / 32.8 / 29.6 Hz; cavitation 2 to 15 W/cm2 (05) | 2.37 to 16.7 dB/m; 1.76 to 2.02 pm/V; 0.86 %; 58.1 / 103.9 / 45.2 and 16.4 / 32.8 / 29.6 Hz; 2.2 to 14.7 W/cm2 | yes | |

---

## 3. Cross-file conflicts and which value to use

| # | Quantity | Values found (file) | Use | Why |
|---|---|---|---|---|
| K1 | Grand Gallery volume | 573 (01); 570 +/- 40 (02); about 550 +/- 15 % (03) | 573 m3, +/- 8 % | 01 is the owning file and uses Petrie's dimensions; 03 used 8.6 m and 2.1 m from memory. All three overlap. Recomputed 575. |
| K2 | Well shaft length and volume | 60.3 m, 28.8 m3 (01); about 50 m (47 to 58), 25 m3 (02) | 60.3 m, 28.8 m3 | 01 read Haase 2004 in full and summed seven segments; 02 used a Wikipedia summary. |
| K3 | Subterranean Chamber volume | bounding 414 to 459, likely 250 to 350 (01); about 300, 250 to 470 (02) | 300 m3 baseline; sweep 200 to 450; hard geometric ceiling 586 m3 | Neither file's upper figure is a true bound (row 3). No scan exists. |
| K4 | Pit depth and bottom level | original "1 to 1.7 m" (01 text) and 1.7 + 1.0 m (01 table); excavated 9 to 15 m (01); bottom -36 to -41 m (02) | original bottom -34.6 m (ledge -33.55 m plus about 1.0 m); excavated state -41 m (Petrie, about 30 ft), -43 m (Haase, 11 m), -47 m (Vyse, 50 ft, secondary) | Petrie s.37 re-read this session: ledge 67 in down at 1321 in under the pavement; about 40 in below it originally. For the ancient state only the original figure matters. |
| K5 | Descending Passage section and length | 1.266 m2, 105.15 m (01); 1.27 (1.20 to 1.27) m2, 105.2 m (02) | 1.266 m2; 105.15 m | Same source; 01 has the directly read section. Difference is 0.3 %. |
| K6 | "Lower" pump stroke | below the Ascending junction, 76.9 m, 97.4 m3 (01); below pavement level, 67.2 m, 85 m3, called "bedrock part" (02) | State three definitions in every table: full 133 m3; below junction 97.4 m3; below pavement 85.0 m3 | Both are legitimate. "Bedrock part" is a third thing (71 to 75 m, 90 to 95 m3) because rock starts a little above pavement level. |
| K7 | Queen's Chamber volume | 164.1 + niche 5.1 (01); 167 including niche about 3 (02) | 164.1 + 5.1 m3 | 01 integrates the niche from Petrie's widths. |
| K8 | Gallery free-surface area | 44 to 88 m2 (01); about 25 m2 (03) | at most 27.6 m2; take A(z) from the CAD | Row 16. |
| K9 | Gallery wetted wall area | about 800 m2 and about 900 m2 (02); about 900 m2 (03) | about 1000 m2, or from the CAD | My estimate from the section perimeter; the first-pass figures are 10 to 20 % low. Low impact. |
| K10 | King's Chamber length | 412.40 / 412.11 in, adopt 10.471 m (01, 03); 412.59 in, 10.48 m (05) | 10.471 m | Re-read this session: 412.59 is Petrie's s.51 raw north-wall average; 412.40 and 412.11 are the s.52 corrected means. Difference 9 mm. |
| K11 | King's Chamber height | 5.844 m floor to ceiling (01); about 235 in = 5.97 m wall base to ceiling (03); about 5.8 m (04 from memory, 05 secondary) | 5.844 m for gas volume and room modes; 5.97 m for the granite wall height | Petrie levels re-read: floor 1691.4 to 1693.7, wall base 1686.3 to 1688.5, ceiling 1921.6 to 1923.7 in. |
| K12 | Pyramid height | original 146.71 m, present platform 137.36 to 137.39 m, missing 9.35 m (01); 146.6 and 138.75 m (04); 146.6 and 138.5 m, "about 8 m missing" (06) | original 146.71 +/- 0.18 m; present platform 137.4 m; 138.75 m only when replicating the 2018 paper | 01 is Petrie's survey; 04 and 06 are memory or secondary. Why the commonly quoted 138.5 to 138.8 m sits 1.1 to 1.4 m above Petrie's platform level was not checked. |
| K13 | Base side | 230.348 m (01); 230.33 m (02); 230.3 m (04); 230 m (paper's model) | 230.35 m for the CAD; 230 m for the replication case | Spread is 2 cm; immaterial. |
| K14 | Characteristic impedance of air | 413 Pa s/m (04, memory); 428 Pa s/m (05, from a paper) | 413 at 20 C (1.204 kg/m3 x 343.2 m/s) | 428 is the 0 C value. Effect 0.15 dB. Recompute for the real gas (SO2-air is denser). |
| K15 | Granite wave speed and density | 5800 m/s, 2650 to 2680 kg/m3 (04, memory); 4610 m/s, 2616 kg/m3 (05, laboratory core); shear 3035 +/- 90 m/s in situ (05, 06) | anchor on the in-situ shear speed; sweep P speed 4600 to 5800 m/s | Only the shear value is specific to the King's Chamber. Changes thickness resonances by 25 % (leaf: 5.8 to 7.3 kHz). |
| K16 | Piezo "gap" headline | 8 to 15 orders (04: 1 kV/m pulse or 20 kHz at 3 MV/m, L = 1 m, against 1 to 10 W/cm2 in the liquid); 10 to 11 orders (05: 40 kHz at 3 MV/m, L = 0.40 m, against 870 W/cm2 in air) | One shared table: source 3.8e-9 to 5.8e-9 W/cm2 at the breakdown field; 1e-15 W/cm2 for a lightning-level field; requirement stated both ways | The two files agree on the source to within a factor 1.5; they differ in the target. Not a contradiction, but the public reply should quote one definition. |
| K17 | Conductivity of the acid in the pits | 56 to 76 S/m at 15 to 31 wt % (07); product at most 0.24 wt % (03) | about 1 S/m at the chemistry ceiling; sweep 0.1 to 5 S/m | 07 used the lowest concentration its source tabulates. My 1.25 S/m uses limiting ionic conductivities recalled from memory; fetch a table before coding. Contrast with damp limestone (0.01 to 0.025 S/m) is then about 40 to 100, not thousands. |
| K18 | Limestone resistivity | 300 to 1500 ohm m, 80 to 300 in the first metre, pyramid north face (04); 40 to over 1200 surface layer, 40 to 100 saturated, 1000 to 3000 dry facies, plateau (07) | 04's values for the masonry; 07's for bedrock and ground; sweep both | Different bodies measured by different surveys; not a true conflict. 07's source re-read this session and confirmed. |
| K19 | Relative permittivity | limestone 5 + 0.1i (paper), 7 (speaker; dry, 100 MHz); granite 9 (speaker), 4 to 6 at 100 MHz, 24 to 3.5 for Aswan granite over 100 Hz to 10 MHz, 6 used for relaxation (04) | frequency-dependent: Aswan granite 24 (100 Hz) falling to 3.5 (10 MHz); limestone 7 +/- 2; 5 + 0.1i only for the replication | The speaker's 7 and 9 are inside measured ranges; the paper did not use them. |
| K20 | Modern water table | 15 to 15.5 m (Sphinx), 16 to 17 m (Nazlet El-Samman) (02); 15 to 15.8 m, 14.5 to 17 m (07) | 14.5 to 17 m, mean about 15 m asl; perched 22 to 48 m only in the Menkaure area | Same paper, read differently. Re-read this session: all four ranges are in it. The paper does not name the datum explicitly. |
| K21 | Distance to the Queen's Chamber south-shaft slab | 63.6 +/- 0.4 m (04, 06); 65 m or 63.6 m (05); 59 to 65 m (06 alternates); 60 to 65 m (01) | 63.6 +/- 0.4 m; slab 60 mm (5 to 9 cm) | 06 read the Djedi figure in a source; the others are press or snippets. |
| K22 | King's Chamber shaft slopes | N 31 deg 33', S 45 deg 13' 40" (01, 02, 06); N 32.6, S 45 (Gantenbrink, secondary, 01); N 31, S 44.5 (Badawy; Petrie's own caveat in 06) | Petrie's means with +/- 1 deg | Affects exit height by under 1 m (row 13). |
| K23 | Gypsum solubility | 2.0 to 2.5 g/L (02, secondary); about 2 g/L (06, memory); 0.015 mol/kg, about 2.6 g/L as dihydrate (03, read from a figure) | 0.015 mol/kg at 25 C | The same number on two bases: 0.015 mol/kg is 2.0 g/L as CaSO4 and 2.6 g/L as the dihydrate. |
| K24 | Limestone density | 1.99 to 2.31 g/cm3 measured backing stone (02); 2.2 (01, muography model); about 2.5 (06, round figure for casing); 1.58 to 1.68 (05, Sardinian stone) | 2.0 to 2.3 for core masonry; do not use 05's figure for Giza except as a soft-stone bound on impedance | Only 02's is a measurement on Khufu's stone. |
| K25 | Acid-ceiling water volume | 550 m3 (03); 573 m3 (01); 860 to 868 m3 if every filled space dilutes it (01, 02) | report all three: 0.024, 0.023, 0.015 mol/L | The hypothesis does not say which water receives the gas. |
| K26 | Khafre burial chamber plan | 14.17 x 4.97 m (01, 07); about 14.15 x 5 m (06, secondary) | 14.17 x 4.97 m | Petrie. |
| K27 | North Face Corridor section | 2.02 x 2.18 m and 1.87 x 1.85 m (01); about 2.0 x 2.0 m (06, abstract); about 2.5 x 2.5 m by resistivity (06) | 01's two muography sets as the range | 01 read the paper body. |

Quantities checked and found consistent across files: Queen's Chamber dimensions and levels (01, 02, 06); antechamber dimensions (01, 05); coffer dimensions (01, 06); King's Chamber shaft sections (01, 02, 06); thickness of stone left at the Queen's Chamber shaft mouths, about 5 in (01, 05, 06); Tura and Mokattam limestone composition (04, 05); granite piezoelectric coefficient 1.4e-15 C/N (04, 05); air breakdown field 3 MV/m (04, 05, both from memory); Mokattam dip 5 to 10 deg SE (02, 07); Big Void minimum length 30 m (01, 06).

---

## 4. Formulas (enough to repeat each row by hand)

Geometry
- F1. Passage volume = sloping length x perpendicular section area. Sloping length from end coordinates: sqrt(dy^2 + dz^2).
- F2. Gabled chamber = L x W x wall height + 0.5 x span x (ridge - wall height) x length along the ridge.
- F3. Inclined prism (Grand Gallery): V = vertical transverse section area x mean horizontal length. Section = slot width x ramp height + wall width x (first-lap height - ramp height) + lap height x sum of the seven lap widths, with lap width k = 2.093 - k x (2 x 20.55 in / 7). Floor horizontal length = sloping floor length x cos(slope).
- F4. Free-surface area of level water in a prism inclined at theta: A = vertical section area / tan(theta), when the surface runs from floor to roof.
- F5. Shaft exit on the casing: solve d0 + s cos(a) = half-base - z/tan(face slope) with z = z0 + s sin(a); s is the sloping length, a the shaft angle, d0 the horizontal start distance from the centre (negative on the far side).

Hydraulics
- F6. Hydrostatic gauge pressure p = rho g (z_surface - z).
- F7. Piston force F = p A, with A the section perpendicular to the passage axis. Plunger: weight per metre = A rho_stone g; driving component x sin(slope); friction mu x weight x cos(slope).
- F8. Stroke count N = volume to fill / swept volume; swept volume = stroke length x A.
- F9. Ideal lifting work W = rho g x sum over spaces of V x (centroid height - source level).
- F10. Maximum suction lift = (p_atm - p_vapour)/(rho g). Lift demanded = pump level - water-table level, both in m asl; chamber level asl = base elevation + level relative to the pavement.
- F11. Duct loss: dp = K rho_air v^2/2 with K = f L/D_h + minor losses; two parallel ducts share the flow so that K1 v1^2 = K2 v2^2.
- F12. Joint leakage (cubic law): flow per metre of joint = rho g b^3 i/(12 mu). Slot flow past a piston: Q = perimeter x b^3 x dp/(12 mu x length). Darcy: Q = K A i.
- F13. Hydraulic ram: delivered fraction q/Q = efficiency x fall / lift.

Chemistry
- F14. Ideal gas: n = p V/(R T).
- F15. Concentration c = n / water volume; weight percent = 98.08 c / 10 (dilute); pH from c + x with x^2 + (c + Ka2) x - Ka2 c = 0.
- F16. Reaction enthalpy = sum of product formation enthalpies - sum of reactant formation enthalpies. Adiabatic rise = (-dH) c / (rho cp).
- F17. Equilibrium: log10 K = -(dH - T dS)/(2.3026 R T).
- F18. Rate ceiling: k at most Z exp(-E/(R T)) with collision-limit Z = 1e-10 cm3/molecule/s; lifetime = 1/(k [O2]); [O2] = 0.2095 p/(kB T).
- F19. Dissolved oxygen: c* = H x p(O2). Surface supply rate = kL x c* x A; time = (0.5 n(SO2) - c* V_water)/(kL c* A).
- F20. Stoichiometric SO2 fraction in an SO2-air mixture: 1/(1 + 0.5/0.2095).
- F21. Weak-acid speciation: sulfite fraction = Ka1 Ka2/([H+]^2 + Ka1 [H+] + Ka1 Ka2). Diffusive flux through a layer: J = D c/thickness. HCl: p = [H+][Cl-]/H'.

Electromagnetics
- F22. f = c0/wavelength. Conductivity and loss: sigma = 2 pi f eps0 eps''; resistivity = 1/sigma.
- F23. Skin depth, general: 1/delta = 2 pi f sqrt(mu0 eps0 eps'/2) x sqrt(sqrt(1 + t^2) - 1), with t = 1/(rho 2 pi f eps0 eps'). Good-conductor limit: delta = 503.3 sqrt(rho/f) metres.
- F24. Charge relaxation time tau = eps0 epsr rho.
- F25. Collection area, rectangular block: A = L W + 2 (3H)(L + W) + pi (3H)^2. Pointed structure with sides steeper than 1 in 3: A = pi (3H)^2. Strikes per year = Ng x A (km2) x location factor.
- F26. Current density under a strike: J = I/(2 pi r^2) near the attachment point, I/area at depth; E = rho J. Telluric voltage = field x 0.230 km. Energy density = 0.5 eps0 epsr E^2.
- F27. Leaky-wire length: lambda = sqrt(sigma_v A ln(2 lambda/a)/(2 pi sigma_h)), a = sqrt(A/pi); solved for sigma_v/sigma_h = 2 pi lambda^2/(A ln(2 lambda/a)).

Acoustics
- F28. Converse piezoelectric displacement u = d E L (= d x voltage). Surface velocity v = 2 pi f u (sinusoid) or u/rise time (pulse). Intensity I = 0.5 Z v^2; p_rms = Z v/sqrt(2); level = 20 log10(p_rms/20 micropascal).
- F29. Intensity transmission between media: T = 4 Z1 Z2/(Z1 + Z2)^2; in dB, -10 log10 T. Pressure amplitude from intensity: p = sqrt(2 Z I).
- F30. Acoustic temperature swing dT = T0 (gamma - 1)/gamma x p'/p0. Mean Arrhenius factor = I0(Ea dT/(R T0^2)).
- F31. Diffuse field: absorption area A = S alpha + 4 m V with m = (dB/m)/4.343; energy density w = 4 P/(c A); room gain over free field at 1 m = (4/A) x 4 pi.
- F32. Link budget = air absorption (dB/m x path length) + sum of interface losses from F29. Rock attenuation = 8.686 pi f/(Q v) dB/m. Axial room mode = c/(2 L).

---

## 5. Spot checks of inputs made this session

These were needed to settle conflicts; they are not a full source audit. All four were read through the page-extraction tool, which paraphrases, so they carry the same transcription risk the first-pass authors flagged.

1. Petrie 1883, ch. 7, s.37 (ronaldbirdsall.com/gizeh/petrie/c7.html): chamber walls 325.9 (E), 553.5 (N), 554.1 (S) in; floor 140 in below the roof in the east, 198 in round the pit, a rock knob at 155 in; pit ledge 67 in down, 265 in below the roof, 1321 in under the pavement; lower shaft originally about 40 in; about 30 ft deep when Petrie saw it; water in it after heavy rain. Confirms 01 and 02 except that "155" is a knob, not a floor.
2. Petrie 1883, ch. 7, s.51-55: wall means N 412.40, S 412.11, E 206.29, W 205.97 in; 412.59 is the s.51 north-wall average; floor 1691.4 to 1693.7, wall base 1686.3 to 1688.5, ceiling 1921.6 to 1923.7 in. Confirms 01; explains 05's 412.59.
3. Sharafeldin et al. 2019 (gi.copernicus.org/articles/8/29/2019/): water table about 15 m on average, range 14.5 to 17 m; Sphinx 15 to 15.5 and 15.5 to 15.8 m; Nazlet El-Samman 16 to 17 m; perched 22 to 48 m in the Menkaure area; borehole MW6 water at 15 m under 65 m ground; resistivities 40 to over 1200, 40 to 100, 1000 to 3000 ohm m. Confirms both 02 and 07.
4. Collection-area definition: a web search returned, from a secondary copy of the lightning-risk standard, that the area is bounded by a line of slope 1 in 3 touching the upper parts of the structure and rotated round it, and that complex shapes need a graphical method. I did not open the standard. Unverifiable beyond that summary; the pyramid consequence in row 41 is my geometry.

---

## 6. Still open

1. Individual lap heights of the Grand Gallery. The 573 m3 figure assumes seven equal laps and a first-lap height from a secondary source; +/- 8 %.
2. True open volume of the Subterranean Chamber. No scan; 200 to 450 m3 is a guess bounded above by 586 m3.
3. Ground-flash density for the Giza grid cell. Row 41 spans a factor of four on the sourced input alone, and ten with the unsourced upper value.
4. The lightning-risk standard's own text on complex or pointed structures (current edition, Annex A) was not opened.
5. Free-surface oxygen transfer coefficient for still water in a closed chamber. Assumed 1e-6 to 1e-5 m/s in 03 and here; it sets row 33 linearly.
6. Conductivity of 0.1 to 1 wt % sulfuric acid from a primary table; Ka2 of sulfuric acid; gypsum molar volume; limiting ionic conductivities. All recalled, none fetched.
7. Base elevation (60 +/- 2 m asl) and the Old Kingdom water table under Khufu (a model estimate at the valley floor, not a measurement under the pyramid). Together they set the suction margin of row 22 to about +/- 3 m.
8. Excavated pit depth (9, 11 or 15 m) and whether Vyse's 50 ft is measured from the chamber floor. The 15 m reading would put the 1837 bottom within a metre of the 1837 water level quoted in 02, which is itself from a snippet.
9. Granite piezoelectric coefficient at kilohertz frequencies and the P-wave speed of Aswan granite. Rows 43 and 46 scale linearly with the first.
10. Acoustic impedance and attenuation of Tura limestone (row 50 uses a soft Sardinian stone and an assumed dense value).
11. Queen's passage and low-passage sections are secondary or from memory (rows 7, 14).
12. Quantities the hypothesis does not define and that no recomputation can fix: stroke length, which spaces fill, SO2 fraction and source rate, drain time, ultrasound frequency and required intensity, pit acid strength.
13. This file was not second-reviewed (advisor tool rate-limited).
