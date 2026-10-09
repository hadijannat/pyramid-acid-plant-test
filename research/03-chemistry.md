# 03 - Reaction chemistry and thermodynamics of the "Great Pyramid sulfuric-acid plant" hypothesis

Prepared 2026-10-09/10. Scope: the chemical chain claimed by Geoffrey Drumm ("Land of Chem") in the three local transcripts. Every figure is tagged with a source number from the list at the end. `verified = yes` means I read that figure in the cited source in this session; `no` means it is recalled, derived by me, or taken from a search snippet or secondary page, and the note says which. Hand arithmetic is mine and is labelled "derived".

---

## 1. Summary

**What the speaker says about the sulfur source (full episode, 00:09-00:36).** His original idea was mined native sulfur burned to SO2, as in a modern sulfur-burning acid plant (00:11:20, 00:32:32). His current idea is that hydrogen sulfide rises from caves below the plateau, citing one geology paper (Badawy 2021 [26]); the H2S is converted to SO2 in an unspecified three-step sequence assigned to the three satellite pyramids, justified by a US patent [27]; the SO2 enters the King's Chamber (which he calls the furnace chamber) through a hole in the floor near the sarcophagus. He states on tape that the connection of that hole to the satellite pyramids is only a hypothesis (00:17:46). The Bent Pyramid section assigns it urea or nitric acid production, not sulfur chemistry. No quantities, concentrations, temperatures, cycle times, ultrasound frequency or intensity are given anywhere.

**Headline findings.**

1. Thermodynamics allows it, kinetics does not. SO2 + 1/2 O2 -> SO3 is exothermic (-98.9 kJ/mol) and at 300 K the equilibrium constant is about 2 x 10^12 bar^-1/2 [3][4]. But the uncatalysed gas-phase reaction has no accessible pathway at ambient temperature: the only direct channel (SO2 + O2 -> SO3 + O) is endothermic by about 150 kJ/mol [6][8], giving a lifetime of at least ~10^10 years (derived upper bound on rate). Industry needs a vanadium catalyst at roughly 400-600 deg C [7], or nitrogen oxides in the lead-chamber process [15].
2. Ultrasound cannot stand in for the catalyst in a gas. Sonochemistry works through cavitation, which occurs only in liquids [13]. The hypothesis places the "acoustic catalyst" in a gas-filled antechamber.
3. The wet route (SO2 -> dissolved S(IV) -> sulfate by air) is real chemistry but slow under the stated conditions: the uncatalysed reaction is vanishingly slow in acid [12], metal-ion catalysis helps but is self-limiting as pH falls [11], and dissolved-oxygen supply through a quiescent free surface is the hard limit (derived: weeks to years for a full batch).
4. Stoichiometry caps the product at very dilute acid: a King's Chamber full of pure SO2 at 1 atm holds about 1.3 x 10^4 mol, giving at most ~0.024 mol/L (0.24 wt%) H2SO4 in a Grand-Gallery volume of water (derived; geometry approximate). Bulk temperature rise is then at most ~2 K, so the claimed risk of the solution boiling over, and the need for a heat exchanger, are not supported at that scale. [Verification 2026-10-10: recomputed with the 01-geometry volumes (King's Chamber 320.4 m3, Grand Gallery 573 m3): 1.33 x 10^4 mol, 0.023 mol/L (was: 0.024), 1.7-1.8 K. If the oxygen has to come from air drawn in the same gallery stroke, the ceiling is about 0.012 mol/L. See the verification section, V7 and V8.]
5. Gypsum armouring is genuine and well documented: it can slow acid attack on calcite by orders of magnitude and some studies report complete passivation [19][22]. Other work shows a continuing, parabolic (t^-1/2) attack [20][21]. Gypsum is not insoluble (about 0.015 mol/kg in water, slightly more in dilute H2SO4 [23]); at the very low sulfate levels implied here armouring may not form at all, and fresh-water fills would re-dissolve it (derived). [Verification 2026-10-10: "may not form at all" is too strong. Column experiments at pH 2 with 14-47 mmol/L sulfate did end with gypsum-passivated, chemically inert calcite, but only after about 120 to 7000 h of continuous acid supply, longest at the lowest sulfate [41]. Read this as "forms slowly, after substantial acid has been neutralised". See V9.]
6. Calcium sulfate and halite in the chambers are non-diagnostic: gypsum mortar, natural salts and visitor humidity are documented alternative sources (secondary sources only; see section 3).
7. NaCl + dilute H2SO4 at ambient temperature releases essentially no HCl gas (derived from Henry's-law data [10]: ~10^-7 atm). The industrial Mannheim route needs concentrated acid and 600-700 deg C for the second step [17].

Overall: several individual statements are true in isolation (reactions are exothermic, SO2 is very soluble, gypsum armours calcite, concentrated H2SO4 + NaCl gives HCl). The chain as described fails at its first reaction step for want of any known mechanism, and the downstream steps are limited by oxygen supply, stoichiometry and limestone neutralisation. [Verification 2026-10-10: wording qualified. Low-temperature routes from SO2 to sulfuric acid do exist (nitrogen-oxide carrier chemistry, metal-ion-catalysed aqueous oxidation); what has no known mechanism is the claimed one, gas-phase oxidation driven by airborne ultrasound. The known routes are not claimed by the speaker and are quantified in the verification section, "Steelman".] A simulation can still be built to quantify each of these and should be allowed to pass if the numbers come out otherwise.

---

## 2. Parameters

### 2a. Thermodynamics

| name | value | unit | uncertainty | source | verified |
|---|---|---|---|---|---|
| dfH(SO2, g, 298 K) | -296.81 (CODATA); -296.84 (JANAF) | kJ/mol | +/-0.20 | [1][6] | yes |
| dfH(SO3, g, 298 K) | -395.77 | kJ/mol | JANAF, reviewed 1965 | [2][4] | yes |
| S(SO2,g) / S(SO3,g) / S(O2,g) | 248.22 / 256.77 / 205.15 | J/mol/K | +/-0.05 | [1][2][6] | yes |
| dH(SO2 + 1/2 O2 -> SO3, g, 298 K) | -98.9 (-98.92 at 298.15 K; -98.93 at 300 K) | kJ/mol | +/-0.3 | derived from [3][4] | values yes; arithmetic re-derived 2026-10-10 from JANAF rows re-read that day (V1) |
| log10 Kp, SO2 + 1/2 O2 = SO3 at 298 / 300 / 400 / 500 K | 12.42 / 12.31 / 8.00 / 5.41 (Kp(300 K) = 2.05e12) | Kp in bar^-1/2 | +/-0.05 | difference of JANAF log Kf [3][4] | values yes; re-derived 2026-10-10 (V1) |
| log10 Kp at 600 / 700 / 800 / 900 / 1000 K | 3.69 / 2.46 / 1.54 / 0.83 / 0.26 | Kp in bar^-1/2 | +/-0.05 | [3][4] | 600-800 K re-derived 2026-10-10 (3.686 / 2.456 / 1.537); 900 and 1000 K not re-read |
| dfH(H2SO4, liquid, 298 K) | -813.99 | kJ/mol | not stated | [5] | yes |
| dfH(H2O, l) / dfH(H2O, g) | -285.830 / -241.826 | kJ/mol | +/-0.040 | [6] | yes |
| dfH(SO4^2-, aq) / dfH(HSO4-, aq) | -909.34 / -886.9 | kJ/mol | +/-0.40 / +/-1.0 | [6] | yes |
| dfH(O, g) / dfH(H2S, g) / dfH(HCl, g) | +249.18 / -20.6 / -92.31 | kJ/mol | +/-0.10 / 0.5 / 0.10 | [6] | yes |
| dH(SO3(g) + H2O(l) -> H2SO4(l)) | -132.4 | kJ/mol | +/-1 | derived [2][5][6] | arithmetic mine |
| dH(H2SO4(l) -> 2H+ + SO4^2-, infinite dilution) | -95.4 | kJ/mol | +/-1 | derived [5][6] | arithmetic mine |
| dH(SO2(g) + 1/2 O2 + H2O(l) -> 2H+ + SO4^2-(aq)) | -326.7 | kJ/mol | +/-1 | derived [1][6] | arithmetic mine |
| dH(SO2(g) -> SO2(aq)) | -24 to -26 | kJ/mol | from d ln H/d(1/T) = 2900-3145 K | derived [10][11] | arithmetic mine |
| dH(H2S + 3/2 O2 -> SO2 + H2O(g)) | -518.0 | kJ/mol | +/-0.6 | derived [6] | arithmetic mine |
| Adiabatic temperature rise of water per mol/L H2SO4 made in situ from SO2 gas | 78 (dilute limit, product counted as SO4^2-); about 73 if the product is counted as HSO4-, which is the main form below pH 2 | K per (mol/L) | assumes cp 4.18 kJ/kg/K (standard constant, not fetched) | derived | derived; recomputed 2026-10-10: 326.70 / (4.181 x 0.998) = 78.3; HSO4- case 304.3 kJ/mol (V8) |

### 2b. Gas-phase kinetics

| name | value | unit | uncertainty | source | verified |
|---|---|---|---|---|---|
| dH0 for SO3 + O -> SO2 + O2 | -151.1 (JANAF, quoted); -155.5 (computed) | kJ/mol | +/-0.7 | [8] | yes |
| k(SO3 + O -> SO2 + O2) | 2.8e4 T^2.57 exp(-122.3 kJ/mol / RT) | cm3/mol/s | ab initio TST; stated valid T > 1000 K | [8] | yes |
| Barrier heights on SO3 + O surface | 139 (triplet abstraction), 123 (singlet elimination) | kJ/mol | CBS-QB3 | [8] | yes |
| Endothermicity of SO2 + O2 -> SO3 + O at 298 K | +150.2 | kJ/mol | +/-0.3 | derived [2][6] | arithmetic mine |
| Upper bound on k(SO2 + O2 -> SO3 + O) at 300 K | <= 7e-37 (collision-limit estimate); <= 3e-38 by detailed balance (added 2026-10-10) | cm3/molecule/s | first figure assumes prefactor 1e-10 and zero excess barrier; second is K_eq(300 K) = 9.6e-29 (from JANAF dfG, dG = +160.9 kJ/mol) times a gas-kinetic reverse rate of 3e-10 | derived | derived; recomputed 2026-10-10 (7.1e-37). The NIST Chemical Kinetics Database returns no record for this direction and ten for the reverse [38] (V2) |
| Resulting SO2 lifetime in air at 300 K, 1 atm | >= 3e17 s (about 1e10 years); >= 2e11 years by detailed balance; about 1e18 years using the only low-temperature reverse-rate measurement [38]; about 5e29 years extrapolating [8] | s | lower bounds; [O2] = 5.1e18 cm-3 | derived | derived; recomputed 2026-10-10 (2.8e17 s = 8.8e9 yr) (V2) |
| k(SO3 + O -> SO2 + O2), low-temperature measurement (added 2026-10-10) | 2.32e-16 exp(-4049 J/mol / RT), 300-500 K (Jacob and Winkler 1972), i.e. 4.6e-17 at 300 K | cm3/molecule/s | Hindiyarti et al. [8] suggest low-temperature data of this kind may reflect adduct formation, so treat as an upper limit for the abstraction channel | [38] | yes (NIST database record; original paper not opened) |
| k(OH + SO2 + M), 298 K, 1 atm | 1.04e-12 (Sun et al.); 9.4e-13 (IUPAC) and 9.5e-13 (NASA) as quoted there | cm3/molecule/s | up to ~30% between evaluations | [9] | Sun value yes; IUPAC (9.38e-13) and NASA (9.50e-13) re-read 2026-10-10 as quoted in [9]; the IUPAC datasheet URL still returns 404. The older IUPAC 2004 evaluation [39] gives k0 = 4.5e-31 (T/300)^-3.9 [N2], k_inf = 1.3e-12 (T/300)^-0.7, Fc = 0.525 (V3) |
| SO2 lifetime against OH in sunlit boundary layer | "a few days" at [OH] = 1e6 cm-3; about 12 days by my arithmetic | - | OH is photochemical; near zero in a dark chamber | [9] + derived | statement yes; arithmetic recomputed 2026-10-10: 11.1 d (Sun), 12.3 d (IUPAC) (V3) |
| Total atmospheric SO2 lifetime, all sinks (added 2026-10-10) | 13 h summer / 48 h winter (model), 19 +/- 7 h / 58 +/- 20 h (in situ), eastern US; 0.6-2.6 d global means in earlier work | - | sinks are gas-phase OH, dry deposition (measured velocities generally <= 0.4 cm/s) and in-cloud aqueous oxidation (H2O2) | [40] | yes (V3) |
| Other gas-phase SO2 oxidants, 298 K (added 2026-10-10) | HO2 + SO2: < 1e-18; NO3 + SO2: < 1e-19; O + SO2 + M: k0 = 1.4e-33 [N2] | cm3/molecule/s (cm6/molecule2/s for the last) | upper limits; the O-atom route needs an O-atom source | [39] | yes |
| SO3 + 2 H2O -> H2SO4 + H2O first-order loss | 3.9e-41 exp(6830.6/T) [H2O]^2 (Jayne 1997); 2.26e-43 T exp(6544/T) [H2O]^2 (Lovejoy 1996) | s-1, [H2O] in molecule/cm3 | factor ~1.5 between the two at 300 K | [31] | Jayne expression yes, read 2026-10-10 in the IUPAC 2004 datasheet [39] as (3.9 +/- 0.8)e-41 exp(6830/T) [H2O]^2, 283-370 K; IUPAC preferred value 5.7e4 s-1 at 298 K and 50% RH. Lovejoy expression still no (V4) |
| SO3 lifetime in humid air (50% RH, 298 K) | about 18-20 (was: ~20-30) | microseconds | 17.5 from the IUPAC preferred value; 19.5 from the Jayne expression with [H2O] = 3.85e17 cm-3 | derived | derived from a value read in [39] (V4) |
| 2 NO + O2 -> 2 NO2 (added 2026-10-10; needed for the NOx sensitivity case) | 2.0e-38 at 298 K; 3.3e-39 exp(530/T), 270-600 K | cm6/molecule2/s | second order in NO, so the NO re-oxidation time scales as 1/[NO]: about 20 s at 1 vol% NO, 2.4 d at 1 ppm, 6.5 yr at 1 ppb (derived) | [39] | yes; times derived |

### 2c. Industrial benchmarks

| name | value | unit | uncertainty | source | verified |
|---|---|---|---|---|---|
| Contact-process catalyst | vanadium pentoxide | - | - | [7] | yes |
| Representative converter condition | 9 vol% SO2 in, 430 deg C, 98% conversion | - | single absorption 95-98%; dual absorption >= 99.7% | [7] | yes |
| Typical converter temperature window | 420-620, typically ~450 | deg C | - | [16] | no (Wikipedia, citing Lapina et al.) |
| Absorbing acid strength | 98-99 | wt% H2SO4 | - | [7] | yes |
| Acid mist origin | SO3 + water vapour below the SO3 dew point; mist is too stable to be removed in the absorber | - | - | [7] | yes |
| Mist particle size | 30 wt% < 2 um (98% acid plants); 85-95 wt% < 2 um (oleum plants) | - | - | [7] | yes |
| Lead-chamber process: role of NOx | NO2 required for a reasonable rate; nitrosylsulfuric acid is the carrier | - | - | [15] | yes as of 2026-10-10, from the 1911 Britannica article [42]: nitrogen oxides act as the oxygen carrier via nitrosyl-sulphuric acid, which liquid water decomposes; without a carrier the direct SO2 + O + H2O reaction goes "only to a very small extent" (V10) |
| Lead-chamber product strength | 60-70, preferably 66-67 (chamber acid); 78-80 (Glover tower) (was: 62-70; up to 78) | wt% | - | [42] (was [15]) | yes (corrected from [42]) |
| Lead-chamber nitre make-up (added 2026-10-10) | as low as 2 parts nitre per 100 parts sulfur burned, with tower recovery | mass ratio | about 0.75 mol N per 100 mol S if the nitre is sodium nitrate (derived; 0.63 if potassium nitrate); the circulating NOx inventory is larger and was not sourced | [42] | yes (ratio); molar conversion derived |
| Lead-chamber gas temperature | about 60 maximum entering chambers | deg C | single patent snippet | search result only | no; [42] gives no number, only that air-cooling of the chamber walls matters. Still unverified |
| Patent US 9,108,846 steps | (1) H2S -> SO2 by combustion >= 900 deg C or catalysed >= 200 deg C; (2) SO2 -> SO3 over vanadium catalyst at 390-430 deg C, >= 98.7% conversion; (3) condense H2SO4 at 60-120 deg C | - | - | [27] | yes; re-read 2026-10-10. The claims do include heat exchangers (glass-tube exchanger in the condensation step), so the speaker's "three steps with a heat exchanger" describes the patent correctly; it is the mapping of those steps onto H2S -> SO2 alone that fails |
| Mannheim process | step 1 NaCl + H2SO4 -> NaHSO4 + HCl, exothermic near room temperature; step 2 NaCl + NaHSO4 -> Na2SO4 + HCl at 600-700 deg C | - | acid concentration not stated on page | [17] | no (Wikipedia, citing Riegel 1974) |

### 2d. Gas-liquid equilibria and aqueous kinetics

| name | value | unit | uncertainty | source | verified |
|---|---|---|---|---|---|
| Henry solubility of SO2, 298 K | 1.3e-2 (range 1.1e-2 to 1.5e-2) | mol/(m3 Pa); equals ~1.3 mol/L/atm | d ln H/d(1/T) = 2900 K (range 2800-3400) | [10] | yes; re-read 2026-10-10: the four most recent review entries all give 1.3e-2 and 2900 K; 1.3e-2 x 101325 / 1000 = 1.32 mol/L/atm (V5) |
| H(SO2)(T) | 1.23 exp[3145 (1/T - 1/298)] | mol/L/atm | - | [11] | yes |
| pKa1, pKa2 of SO2.H2O | 1.9, 7.2 | - | - | [11] | yes |
| Henry solubility of O2, 298 K | 1.3e-5 | mol/(m3 Pa) | d ln H/d(1/T) = 1500 K | [10] | yes |
| Dissolved O2 at air saturation, 298 K | 0.28 | mol/m3 | - | derived [10] | derived; recomputed 2026-10-10 (0.276; O2 Henry value 1.3e-5 re-read) |
| Effective Henry constant of HCl (with dissociation) | 2.0e7 | mol^2/(m^6 Pa); equals ~2.0e6 mol^2/L^2/atm | T-dependence exp[9000 (1/T - 1/T0)] | [10] | yes; re-read 2026-10-10 and cross-checked against tabulated HCl partial pressures [43]: it predicts 8.9e-8 atm over 2 wt% HCl at 25 deg C, the table gives 1.1e-7 atm (V11) |
| Partial pressure of HCl over aqueous HCl (added 2026-10-10) | 2 wt%: 4.4e-5 mmHg at 20 deg C, 8.4e-5 at 25 deg C; 20 wt%: 0.32 mmHg at 25 deg C | mmHg | stated accuracy 15-20% at low strengths | [43] Table 2-10 | yes |
| Uncatalysed S(IV) + O2 | no agreed rate law; described as vanishingly slow in acid | - | disputed whether it exists at all | [12] | yes (qualitative); the Connick et al. rate law [34] remains unverifiable (only bibliographic data reachable) |
| Fe(III)-catalysed S(IV) oxidation | R = 1.2e6 [Fe(III)][SO3^2-], pH < 5 | mol/L/s | inhibited by ionic strength; calibrated for dilute atmospheric water | [11] | yes (as compiled in review; original Hoffmann & Calvert 1985 not opened); constant and pH range re-read 2026-10-10 (V6) |
| Fe(III)-catalysed S(IV) oxidation, alternative law (added 2026-10-10) | pH < 3.6: R = 6 [Fe(III)][S(IV)] [H+]^-1 x 10^(-2 sqrt(I)/(1+sqrt(I))) / (1 + 150 [S(VI)]^(2/3)); pH 3.6-5: R = 1e9 [Fe(III)]^2 [S(IV)]; pH 5-6: 1e-3 [S(IV)]; pH > 6: 1e-4 [S(IV)] | mol/L/s | Martin and Hill 1987 / Martin et al. 1991 as compiled in [11]; the review says it was checked only at pH 2 and 25 deg C and within concentration limits far below batch conditions | [11] | partly: constants 6, 150, 1e9, 1e-3, 1e-4 and the pH bands read; the H+ exponent (-1) and the square root on I were not legible in the extraction and are from memory of the standard textbook form |
| Mn(II)-catalysed S(IV) oxidation | R = 1e3 [Mn(II)][S(IV)] for [S(IV)] < 1e-4 mol/L; R = 680 [Mn(II)]^2 above that, i.e. zero order in S(IV) (was: "different law above (constant 680)") | mol/L/s | ionic-strength factor 10^(-4.07 sqrt(I)/(1+sqrt(I))) (square root assumed; extraction showed I only); known only up to I = 1 mol/L | [11] | low-S(IV) form yes; high-S(IV) form read on a second extraction 2026-10-10 as k times Mn(II) squared with no S(IV) term, consistent with the stated units L/mol/s, but the source text was garbled, so treat as probable (V6) |
| Fe(III) + Mn(II) synergy (added 2026-10-10) | -d[S(IV)]/dt = 750 [Mn(II)][S(IV)] + 2600 [Fe(III)][S(IV)] + 1.0e10 [Mn(II)][Fe(III)][S(IV)] (Martin and Good 1991); or 3.72e7 [H+]^-0.74 [Mn(II)][Fe(III)][S(IV)] for pH 2.6-4.2 and 2.51e13 [H+]^0.67 [Mn(II)][Fe(III)][S(IV)] for pH 4.2-6.5 (Ibusuki and Takeuchi 1987) | mol/L/s | first form as used for cloud water in [44]; both outside the batch pH (about 1.5) | [44]; [11] | yes (as quoted in [44] and [11]; originals not opened) |
| S(IV) + H2O2 | k = 7.45e7 exp[-4000 (1/T - 1/298)], rate roughly pH-independent above pH ~1.5 | L/mol/s | - | [11] | yes |
| Sonochemical efficiency (KI dosimetry, large reactor, 35-170 kHz) | 7.8e-10 to 4.4e-9 | mol/J | liquid phase only | [14] | yes (abstract) |
| Cavitation medium | liquids only; lab probes 10-500 W/cm2, cleaning baths ~1 W/cm2 | - | - | [13] | yes |

### 2e. Limestone, gypsum, stone decay

| name | value | unit | uncertainty | source | verified |
|---|---|---|---|---|---|
| Calcite dissolution, acid mechanism (Palandri & Kharaka) | log k = -0.30, E = 14.4 kJ/mol, n(H+) = 1 | k in mol/m2/s at 25 deg C (units per Reaktoro docs via search, not stated on the PHREEQC page) | surface-reaction limit; real rates are transport-limited | [18] | values yes; units no |
| Calcite neutralisation rate, transport-limited fit | r = 10^-2.61 Re^0.31 m_H^0.87 | units not stated in the abstract | fit to Alkattan et al. 1998 | [21] | yes (form and coefficients) |
| Gypsum-armoured calcite rate law | r = 10^-1.96 t^-0.53 (theory: t^-0.5) | units not stated in the abstract | pH 1.5-3.5, up to 1.0 M Na2SO4, Iceland spar | [20][21] | yes; [21] re-read in full 2026-10-10 (text extracted from the PDF): coefficients, pH and sulfate range confirmed; units still not stated (V9) |
| Diffusivity of H+ through growing gypsum layer | 1.71e-15 to 4.54e-14 | m2/s | - | [20][21] | yes; re-read 2026-10-10 |
| Gypsum overgrowth on calcite in H2SO4 | reported to passivate the surface completely; nucleates instantaneously; epitaxial (lattice match) | - | acid strength not given in abstract; a later paper [22] describes the experiments as pH 1 and 2 in mixed HCl / Li2SO4 solutions (added 2026-10-10) | [19] | yes (abstract, re-read 2026-10-10); conditions secondary via [22]; sulfate concentration still unknown |
| AFM study, pH ~2-6, sulfate 6e-3 to 3.1e-2 mol/L | full coating and passivation only in gypsum-equilibrated solutions; isolated protuberances in undersaturated Na2SO4 solutions | - | imaging lasted about 40 min for calcite; the authors note growth may have stopped through passivation or through equilibrium | [22] | yes; re-read 2026-10-10 on the journal site (the PMC copy was blocked) |
| Gypsum pre-treatment of calcite (added 2026-10-10) | soaking in 0.1 M sulphuric acid for 21 h lowered the calcite dissolution rate constant by "almost one order of magnitude" | - | channel flow cell; slowed, not stopped | [45] | yes (abstract) |
| Calcite columns fed pH 2 sulfate solutions with 250-1500 ppm Fe(III) (added 2026-10-10) | columns became chemically inert; gypsum was the passivating phase; time to passivation 122 to 7030 h, rising as sulfate falls: 4503 mg/L -> 504 h; 3323 mg/L -> 122-489 h; 2061 mg/L -> 2443-3506 h; 1386 mg/L -> 7030 h | h | grains 1-5 mm, constant flow; until passivation the columns raised pH from 2 to about 6-7, i.e. kept neutralising | [41] | yes (abstract, discussion and results table read from the PDF text) |
| Sulfate level above which gypsum may form in limestone drains (added 2026-10-10) | > 2000 mg/L (attributed to Hedin and Watzlaf 1994); another guide says > 1500 mg/L | mg/L SO4 | the batch ceiling here is about 1200-2200 mg/L | [46] | secondary only (guidance page read; primary not opened) |
| Gypsum solubility product and molar volumes (added 2026-10-10) | log K = -4.55; molar volume gypsum 73.9, calcite 36.9 cm3/mol; log K (H+ + SO4^2- = HSO4-) = 1.988 | - | replaces three "from memory" values in section 3 and open question 11 | [47] | yes |
| Bare calcite dissolution rate (AFM) | 1.45e-6 (near neutral); 5.5e-6 (pH 4.8) | mol/m2/s | - | [22] | yes |
| Gypsum solubility in water, 298 K | ~0.015 | mol/kg water (about 2.6 g/L as dihydrate) | literature scatter 0.0147-0.0182 M per search | [23] Fig. 3b | yes (read from figure) |
| Gypsum solubility in H2SO4, 298 K | rises to ~0.020 near 1 mol/kg acid, falls to ~0.007 at 4.7 mol/kg | mol/kg water | +/-5% | [23] Fig. 3b | yes (read from figure) |
| Limestone / marble recession under ambient acid deposition | 25-45 / 15-30 | um/yr | ~30% of dissolution attributed to acid deposition, ~70% to CO2-equilibrated rain | [24] | yes (abstract) |
| Iron/aluminium-armoured limestone effectiveness | 55-98% (HCl titration), 90% (container test) of unarmoured | % | Fe/Al hydroxide armour, not gypsum | [30] | no (search snippet) |
| Constant-flow AMD test, pH 2.9 | gypsum rind under 10-30 um Fe-Al coating within 48 h; alkalinity generation stopped | - | influent 150 mg/L Fe, acidity 1000 mg/L as CaCO3; with pulsed flow and CO2 the armouring was largely suppressed and most grains dissolved | [29] | yes as of 2026-10-10 (abstract on the USGS publication page; thickness given there as 10-30 um) |

### 2f. Geometry and batch quantities used here (approximate; defer to the geometry file)

| name | value | unit | uncertainty | source | verified |
|---|---|---|---|---|---|
| King's Chamber plan | ~412.4 x ~206.0 | inch | Petrie's means | [28] | yes |
| King's Chamber wall base to ceiling | ~235 (1686.3-1688.5 to 1921.6-1923.7 above pavement) | inch | floor sits a few inches above wall base | [28] | yes (levels); height derived |
| King's Chamber gas volume | 320.4 (319.2 net of the coffer solid) (was: ~320) | m3 | +/-0.5% per 01-geometry table F | 01-geometry.md table F (10.471 x 5.236 x 5.844 m) | derived; taken from the geometry file 2026-10-10, not re-derived from Petrie here |
| Grand Gallery roof length | 1648.4 horizontal, 1838.6 sloping | inch | - | [28] | yes |
| Grand Gallery top width; slope | 40.9-41.3 inch; 26 deg 12' 50" | - | - | [28] | yes |
| Grand Gallery volume | 573 (was: ~550) | m3 | +/-8% per 01-geometry table F (was: +/-15%; uses 8.6 m height and 2.1 m base width from memory) | 01-geometry.md table F | derived; taken from the geometry file 2026-10-10 |
| Queen's Chamber salt incrustation noted in 1880-82 survey | yes | - | - | [28] | yes |
| Max SO2 inventory, King's Chamber at 1 atm, 293 K, pure SO2 | 1.33e4 | mol (about 850 kg SO2) | upper bound; real fraction undefined by hypothesis | derived | derived; recomputed 2026-10-10: 41.57 mol/m3 x 319.2 m3 = 1.327e4 mol = 850 kg (V7) |
| Max acid per batch | 1.33e4 mol = 1.3 t H2SO4 (100% basis) | - | upper bound | derived | derived; recomputed 2026-10-10 |
| Max product strength, sulfur-limited (in 573 m3 water) | 0.023 mol/L = 0.23 wt%, pH ~1.5 (was: 0.024 mol/L = 0.24 wt% in ~550 m3) | - | 0.021-0.025 over the +/-8% gallery volume; 0.017 if the Queen's Chamber and its passage (220 m3) are filled too; 0.002 mol/L if SO2 is 10 vol% | derived | derived; recomputed 2026-10-10; pH 1.53 with log K(HSO4-) = 1.988 [47], no activity correction (V7) |
| Max product strength, oxygen-limited (added 2026-10-10) | about 0.012 mol/L = 0.12 wt% | - | one 573 m3 gallery stroke of a stoichiometric SO2-air mixture (29.5 vol% SO2) holds 7.0e3 mol SO2; dissolved O2 in the fill water adds about 0.3e3 mol | derived | derived 2026-10-10 (V7) |
| Air needed for stoichiometric O2 | ~760 | m3 | exceeds one gallery stroke (573 m3; was ~550) | derived | derived; recomputed 2026-10-10 (762 m3) |
| Bulk adiabatic temperature rise at max strength | ~1.8 (was: ~1.9); 1.7 if the product is counted as 26% SO4^2- and 74% HSO4- | K | about 7 K if all heat went into the first quarter fill (was: ~7.5) | derived | derived; recomputed 2026-10-10 with 573 m3 (V8) |
| Total heat per maximal batch | ~4.3e9 J (about 1200 kWh) | - | 4.1e9 J with the speciation above | derived | derived; recomputed 2026-10-10 (4.34e9 J) |
| Horizontal free-surface area of water standing in the inclined gallery (added 2026-10-10) | about 27 | m2 | vertical section 13.59 m2 / tan(26.28 deg); supports the ~25 m2 used in C5 | derived from 01-geometry.md | derived |

---

## 3. Claim-by-claim assessment

Verdict vocabulary: supported / partly supported / no evidence / contradicted / untestable / undefined by hypothesis.

### C1. Hydrogen sulfide rises from below Giza and is the sulfur source
- Said: full episode 00:20:49-00:33:31; the speaker presents it as established fact rather than speculation.
- Evidence: Badawy 2021 [26] exists and does argue for hypogene sulfuric-acid speleogenesis in the Middle Eocene beds, with H2S ascending from Cretaceous reservoirs, based on field work, microscopy, XRD and XRF of natroalunite, gypsum, aluminium-phosphate-sulfate, halloysite and Fe/Mn oxides. The abstract frames this as paleokarst, a past geological process. I found no measured present-day H2S concentration or flux at Giza, and none is in the abstract. "Hydrothermal vents" do not appear in the abstract.
- Verdict: **partly supported**. A peer-reviewed paper supports past H2S-driven speleogenesis; it does not show an exploitable gas supply at any historical time.
- Chemistry note: the same paper implies natural gypsum in the bedrock, which is an alternative origin for calcium sulfate found on site.

### C2. H2S is converted to SO2 in three steps in the three satellite pyramids
- Said: 00:14:18, 00:15:51, 00:33:49-00:35:14, citing a patent.
- Evidence: US 9,108,846 [27] has three steps, but they are the whole H2S-to-H2SO4 process: H2S oxidation to SO2 (one step; combustion at >= 900 deg C or catalysed at >= 200 deg C), vanadium-catalysed SO2 oxidation at 390-430 deg C, and acid condensation at 60-120 deg C. Nothing in it runs at ambient temperature without a catalyst. H2S + 3/2 O2 -> SO2 + H2O is strongly exothermic (-518 kJ/mol, derived from [6]) and is ordinary combustion.
- Verdict: **undefined by hypothesis** for the mechanism (no chemistry is specified for the satellite pyramids); the mapping of the patent's three steps onto the H2S-to-SO2 conversion alone is **contradicted** by the patent text.

### C3. SO2 + O2 -> SO3 at ambient temperature in the antechamber, with ultrasound as the catalyst
- Said: clip 1 00:12:19-00:13:25; clip 2 00:09:28.
- Thermodynamics: favourable. Kp(300 K) ~ 2e12 bar^-1/2 [3][4].
- Kinetics: the only direct homogeneous channel is endothermic by 150 kJ/mol [6][8]; even assuming every sufficiently energetic collision reacts, the SO2 lifetime is >= ~1e10 years (derived). The published high-temperature rate expression [8], if extrapolated far outside its stated range, gives a rate tens of orders of magnitude lower still. In the real atmosphere the gas-phase sink is the photochemical OH radical, with a lifetime of days [9]; OH is absent in a dark sealed chamber. To convert half the SO2 in one hour needs a first-order rate near 2e-4 s-1, at least 13 orders of magnitude above the upper bound.
- Ultrasound: sonochemistry arises from cavitation, and "cavitation can take place only in liquids" [13]; sound does not couple to molecules directly because acoustic wavelengths are vastly larger than molecular dimensions [13]. No source was found reporting ultrasound-driven gas-phase SO2 oxidation. Ultrasound would in any case be an energy input, not a catalyst.
- What would help the hypothesis: nitrogen oxides (lead-chamber chemistry [15]) or a hot solid catalyst [7]. Neither is claimed.
- Verdict: **contradicted** (rate and mechanism), while the thermodynamic direction is **supported**.
- [Verification 2026-10-10: verdict unchanged. Bound reproduced (7.1e-37 cm3/molecule/s, 8.8e9 yr) and tightened by detailed balance (>= 2e11 yr); the NIST kinetics database has no record of the forward reaction [38]. Lightning-made NOx is 4-5 orders of magnitude short of what carrier chemistry needs (V2, V12).]

### C4. Residual SO2 dissolves readily in the rising water as sulfurous acid
- Evidence: H = 1.3 mol/L/atm at 298 K [10], pKa1 1.9 [11]. Derived: 550 m3 of water in equilibrium with 0.024 mol/L total S(IV) leaves only ~0.9% SO2 partial pressure, so water capacity is ample (>= 99% uptake at equilibrium). Whether uptake is fast depends on gas-side transport over metres of quiescent gas, which the CFD must resolve.
- Verdict: **supported** for equilibrium capacity; rate is **untested** (simulation output).

### C5. Sulfurous acid "oxidizes very quickly in air" to dilute sulfuric acid
- Said: clip 1 00:15:22 and 00:17:46; clip 2 00:10:05.
- Evidence: the uncatalysed reaction with O2 is disputed and is "clearly vanishingly slow in acidic solutions" [12]. Catalysis by Fe(III) and Mn(II) is well established [11]. Using the review's Fe(III) law at pH 1.7 with 0.02 mol/L S(IV) and 1e-5 mol/L Fe(III), I derive ~3e-7 mol/L/s, a chemical timescale of roughly a day; this extrapolates a law calibrated for micromolar atmospheric water and the review warns of ionic-strength inhibition, so it is an order-of-magnitude guide only. The rate falls as the product acid lowers pH, because the reactive sulfite fraction collapses. In clouds the fast oxidants are H2O2 and O3, not O2 [11].
- Oxygen supply (derived): air-saturated water holds 0.28 mol O2/m3 [10], so 550 m3 carries ~150 mol O2, enough for ~300 mol S(IV), about 2% of a maximal batch. The rest must cross the free surface; with a quiescent-surface transfer coefficient of 1e-6 to 1e-5 m/s (assumed, not sourced) and ~25 m2 of surface, a full batch takes years and a 10%-SO2 batch months. Industrial scrubbers use forced air sparging for this reason (general knowledge, not sourced here).
- Verdict: **partly supported**: air oxidation of dissolved S(IV) to sulfate is real and metal-catalysed; the claimed speed, and the idea that the intermediate disappears almost at once, are **contradicted** for acidic, unstirred, unsparged water.
- [Verification 2026-10-10: verdict kept but re-based. The "roughly a day" above is the slow end: the alternative Martin law gives 0.2-3 h at the same iron level, and 1e-4 mol/L Mn(II) gives about 5 h (V6). Chemistry is therefore not the limit if iron or manganese is present at 1e-5 mol/L or more. Oxygen is: 2-28 yr through a still 27 m2 surface (V13), and at most 0.012 mol/L of product from the air of one gallery stroke (V7). Under vigorous aeration the speed claim is untested, not contradicted.]

### C6. SO3 then dissolves into the dilute acid; direct dissolution in water is too violent; hence four slow fill stages
- True parts: SO3 hydration is strongly exothermic (-132 kJ/mol to liquid acid, about -228 kJ/mol to dilute solution; derived from [2][5][6]). Industry does not absorb SO3 in water.
- Why industry really avoids water: SO3 meets water vapour and forms a stable sub-micron sulfuric acid mist that absorbers cannot capture [7]; gas-phase SO3 hydration takes tens of microseconds in humid air ([31], unverified). The remedy is 98-99% acid [7], whose water vapour pressure is negligible. A 0.2% acid has essentially the vapour pressure of water, so it offers none of that benefit. The intermediate dilute-acid step therefore does not correspond to the industrial logic.
- Violence at this scale: bulk temperature rise is ~2 K for the largest possible batch (derived), so there is nothing to boil over. The four-stage fill is not needed for thermal control; it would matter only for gas-liquid contact time.
- Moot point: per C3 there is no SO3 to absorb.
- Verdict: **partly supported** (exothermic, water avoided industrially); the stated rationale is **contradicted**.

### C7. The Grand Gallery reaction is extremely exothermic and motivates a heat exchanger (the Big Void)
- Per mole it is strongly exothermic: -327 kJ per mol SO2 taken to dilute sulfate (derived). Per batch it is small: at most ~4.3e9 J into ~550 t of water plus masonry, about 2 K. Reaching the boiling point from 20 deg C would need roughly 1 mol/L of acid made in situ, about 40 times more SO2 than the King's Chamber holds at 1 atm (derived).
- Verdict: **contradicted** at the stated geometry (the adjective holds per mole, the engineering need does not). The speaker himself rates the heat-exchanger idea at about 30% and labels it speculative.

### C8. Rising water does not push gas back because the gases dissolve completely
- SO2 can dissolve (C4). But air is ~79% nitrogen, and oxygen and nitrogen are sparingly soluble (O2: 1.3e-5 mol/m3/Pa [10]; 550 m3 of water holds ~150 mol O2 against thousands of moles in the gas). The inert bulk of the indrawn air must be displaced back through the antechamber and shafts as the water rises, carrying any unreacted SO2 and mist with it.
- Verdict: **contradicted** for the non-condensable fraction.

### C9. Calcium sulfate in the Grand Gallery / Queen's Chamber is direct evidence of dilute sulfuric acid
- Salt incrustation in the Queen's Chamber is real and was recorded by Petrie in 1880-82 [28]. The 1978 analysis quoted from Dunn (calcium carbonate, sodium chloride, calcium sulfate) was not located in primary form (search snippet only [36]).
- Alternatives documented at search level only (not opened): gypsum-based mortar in Khufu's pyramid and halite migrating to surfaces under humidity (Regourd et al. 1988 [32]; a 2020 Heritage Science survey), and a conservation account attributing salt growth to visitor humidity. Badawy [26] itself documents natural replacive gypsum in the local bedrock.
- CaCO3 + H2SO4 does give gypsum, so the mineral is consistent with the hypothesis but does not discriminate between sources. Sulfur and oxygen isotopes, trace elements, and the spatial pattern (uniform tide-line versus joint-controlled efflorescence) would discriminate; no such data were found.
- The speaker's corollary (no calcium chloride, so no HCl) is weak: calcium chloride is deliquescent and would not persist as a crust (general knowledge, not sourced).
- Verdict: **no evidence either way** (consistent but non-diagnostic).

### C10. Calcium sulfate is "insoluble in dilute sulfuric acid", forms a coating and halts the attack
- Support: this is standard school chemistry: marble in dilute sulfuric acid stops fizzing because the sulfate formed is "only very slightly soluble" and coats the chips [25]. Booth et al. report a gypsum overlayer that "completely passivates the surface" [19]; Offeddu et al. saw total passivation in gypsum-saturated acid [22]; epitaxial fit makes the layer adherent [19][21].
- Qualifications: (a) gypsum is sparingly soluble, not insoluble: ~0.015 mol/kg in water and slightly more (up to ~0.020) in dilute H2SO4 [23]. (b) Rimstidt and Huminicki measured continued attack through the layer decaying as t^-0.53, with H+ diffusivity 1.7e-15 to 4.5e-14 m2/s [20][21]: slowed, not stopped. (c) Coatings formed "at low pH where sulfate concentrations were high" (up to 1 M) [21]; in undersaturated sulfate solutions of 6-31 mmol/L only isolated gypsum bumps formed [22]. The hypothesis's product (<= 24 mmol/L sulfate) sits in that weakly armouring range.
- Derived consequences: with a coherent 10 um layer and pH 1.5, H+ flux is ~5e-9 to 1.4e-7 mol/m2/s, a loss of well under 0.1% of a batch per day over ~900 m2 of wall, so a formed armour would protect the acid on a batch timescale. Before armour forms, bulk gypsum saturation needs roughly 0.01 mol/L Ca, consuming ~40% of the acid at 0.024 mol/L and all of it at 0.0024 mol/L (concentration-product estimate). Each fresh-water fill can dissolve up to ~8000 mol gypsum, equivalent to a ~0.7 mm layer over the gallery walls (uses a gypsum molar volume from memory), so the armour would not survive the described fill-drain cycle.
- Verdict: **partly supported**: armouring is real and can be near-total in strong sulfate; calling the salt insoluble and the reaction stopped overstates it, and durability under repeated fresh-water filling at this dilution is doubtful.
- [Verification 2026-10-10: verdict kept, slightly more favourable to the claim. Calcite columns fed pH 2 solutions with 14-47 mmol/L sulfate did end up inert through gypsum, after 122-7030 h, the time lengthening steeply as sulfate falls [41]; mine water at pH 2.9 armoured limestone in 48 h [29]; a 21 h soak in 0.1 M acid cut the dissolution rate constant nearly tenfold [45]. Recomputed: bulk gypsum saturation after 47% of the acid is neutralised at 0.023 mol/L (was ~40% at 0.024), 92% at 0.012 mol/L; fresh fill dissolves up to 8.7e3 mol, 0.68 mm; gypsum molar volume 73.9 cm3/mol now sourced [47] (V9, V17).]

### C11. Pits in the Queen's Chamber walls record armour chipping and renewed attack
- Mechanistically plausible (gypsum has roughly twice the molar volume of calcite, so layers can spall; general knowledge, not sourced). Pitting of limestone has many causes, including salt crystallisation. No measurements located.
- Verdict: **no evidence either way**.

### C12. Khafre's pyramid converted the sulfuric acid to hydrochloric acid with sodium chloride, releasing hydrogen chloride gas
- Industrial reality: concentrated acid; first step near room temperature, second at 600-700 deg C [17].
- Dilute case (derived from [10]): p(HCl) = [H+][Cl-]/2.0e6 atm. For 0.05 mol/L H+ in 5 mol/L chloride brine this is ~1e-7 atm (activity corrections might raise it several-fold). No HCl gas evolves. What forms is a mixed acidic brine of H+, Na+, Cl-, HSO4-/SO4^2-; it is not hydrochloric acid free of sodium sulfate, and separation would need distillation.
- Halite in the chambers is non-diagnostic (same reasoning as C9; halite is also reported in the Great Pyramid's Queen's Chamber).
- Verdict: **contradicted** for HCl gas from dilute acid at ambient temperature; an acidic chloride solution by simple mixing is trivially possible.
- [Verification 2026-10-10: verdict unchanged. The Henry's-law estimate was checked against tabulated HCl partial pressures: 1.1e-7 atm over 2 wt% HCl at 25 deg C, and about 1e-3 atm only above 22 wt% [43]. The batch mixture is equivalent to at most 0.17 wt% HCl; in saturated brine the estimate is 1e-7 to 6e-7 atm (V11).]

### C13. The process is very similar to the modern contact process
- The contact process: burn sulfur in dried air, oxidise SO2 over vanadium pentoxide at ~430 deg C with staged heat removal, absorb SO3 in 98-99% acid [7]. The hypothesis has no furnace heat, no solid catalyst, wet gas, and absorption into water. The shared elements are only the overall stoichiometry and the use of air.
- The explanation that the name refers to gas contacting the solution was not checked against a source here.
- Verdict: **contradicted** in its operative features; **supported** only at the level of overall stoichiometry.

### C14. Product is dilute sulfuric acid useful for metallurgy and leaching
- Derived ceiling: 0.002-0.024 mol/L (0.02-0.24 wt%) per batch, about 1.3 t of acid at the very most, before losses to limestone and to alkalinity in the feed water. Copper leaching is listed as a real use of sulfuric acid [7]; what strength leaching needs was not sourced here.
- Verdict: **undefined by hypothesis** (no target strength or throughput stated); the ceiling is a simulation input.
- [Verification 2026-10-10: ceiling recomputed with the geometry-file volumes: 0.023 mol/L sulfur-limited (was 0.024), 0.012 mol/L if the oxygen comes from one gallery stroke of air, 0.017 mol/L if the Queen's Chamber and its passage fill as well (V7).]

### C15. Sulfates in Great Pyramid boat pits, chlorides in Khafre boat pits
- No published analysis located. Verdict: **no evidence either way** (outside this file's sourcing; flagged for the evidence domain).

---

## 4. What a simulation of this domain needs

### 4.1 Governing equations (chemistry side)
1. **Gas phase** (antechamber, King's Chamber, gallery headspace): variable-density species transport with buoyancy, d(rho Y_i)/dt + div(rho u Y_i) = div(rho D_i grad Y_i) + w_i. SO2 is 2.2 times denser than air (molar masses), so stratification and gravity drainage of SO2 from the King's Chamber down the gallery must be resolved. Chemistry: SO2 + O (+M), SO2 + OH (+M) [9], HOSO2 + O2, SO3 + O [8], SO3 + 2 H2O [31]. Expect w_SO3 ~ 0 unless a radical or NOx source is imposed; keep the mechanism in so the code can show that rather than assume it.
2. **Optional sensitivity cases**: (a) NOx-catalysed lead-chamber chemistry [15] with a prescribed NOx mole fraction; (b) a prescribed OH or O-atom source to ask "how large would a radical source have to be?"; (c) liquid-phase sonochemical oxidant source S = eta * P_acoustic with eta = 1e-10 to 5e-9 mol/J [14]. These are not part of the hypothesis as told; they bound what would be needed.
3. **Gas-liquid interface**: two-film flux N_i = K_G,i (p_i - C_i/H_i*), with H*(SO2) = H (1 + Ka1/[H+] + Ka1 Ka2/[H+]^2) [11], H(O2) [10], and an enhancement factor from the Hatta number for S(IV) oxidation in the liquid film.
4. **Aqueous phase**: instantaneous acid-base speciation (SO2.H2O / HSO3- / SO3^2-, HSO4- / SO4^2-, carbonate system), kinetic S(IV) oxidation R = R_Fe + R_Mn (+ R_H2O2) with the forms in [11], O2 transport, charge balance for pH. Use Pitzer activity coefficients once ionic strength exceeds ~0.1 [23].
5. **SO3 / mist** (only if SO3 is ever present): gas-phase hydration to H2SO4 vapour, then nucleation and condensation to aerosol (general dynamic equation, or a lumped "mist" scalar with settling and wall deposition). Industry data show the mist is sub-2 um [7].
6. **Energy**: rho cp dT/dt + ... = sum(-dH_j r_j), with the enthalpies of table 2a, coupled to conduction into limestone and granite.
7. **Limestone wall**: bare flux J = min(k_s a_H^n, k_mt C_H) with k_s from [18] and transport form from [21]; gypsum saturation index at the wall from a Pitzer or PHREEQC model [23][18]; when SI > 0 grow a layer delta(t) and switch to J_H = D_eff (C_H,bulk - C_H,wall)/delta with D_eff = 1.7e-15 to 4.5e-14 m2/s [20]; on fresh-water contact dissolve gypsum toward 0.015 mol/kg [23]. Track Ca^2+, CO2 release (gas evolution), wall recession.
8. **HCl sub-model**: vapour-liquid equilibrium p_HCl = a_H a_Cl / H'(T) with H' from [10]; no kinetics needed.

### 4.2 Boundary and initial conditions that must be parameterised (the hypothesis does not fix them)
- SO2 mole fraction in the King's Chamber at t = 0: sweep 0.01 to 1.0.
- Temperature 15-30 deg C; relative humidity 50-100%.
- Water chemistry of the feed: alkalinity, Fe, Mn, chloride, sulfate. Natural alkalinity alone can neutralise millimolar acid (not sourced here; see open questions).
- Dissolved and leachable Fe/Mn from limestone, mortar and iron-oxide veins: sweep 1e-7 to 1e-4 mol/L.
- Cycle timing: fill and drain rates, dwell times (from the hydraulics domain).
- Wall state: bare limestone, pre-armoured, or mortar-lined.
- Ultrasound: frequency, pressure amplitude, and whether any liquid is present in the insonified region.

### 4.3 Key dimensionless numbers
- Gas-phase Damkohler number Da_g = k_gas * t_residence (expected < 1e-13 for the homogeneous route).
- Liquid Damkohler / Hatta number Ha = sqrt(k_ox D_O2)/k_L for S(IV) oxidation.
- Oxygen supply ratio: (O2 deliverable through the surface in one cycle + dissolved O2) / (0.5 * S(IV) inventory).
- Stoichiometric air ratio: air volume drawn per stroke / air volume required (derived ~0.7 or less for pure SO2).
- Gas-side Sherwood and Peclet numbers for SO2 uptake; Richardson number for dense-gas stratification.
- Gypsum saturation index at the wall; armour Thiele-type ratio k_s * delta / D_eff.
- Acid neutralisation number: wall H+ uptake in one cycle / H+ inventory.
- Dimensionless temperature rise dT_ad / (T_boil - T_0).

### 4.4 Pass / fail criteria (proposed; thresholds are judgement calls and should be agreed before running)
| metric | pass (supports) | marginal | fail (contradicts) | prior expectation from this review |
|---|---|---|---|---|
| Gas-phase SO2 -> SO3 conversion per pass through antechamber, no added catalyst, heat or NOx | >= 10% | 0.1-10% | < 0.1% | effectively zero |
| Overall S(IV) -> S(VI) yield within one stated cycle | >= 50% | 5-50% | < 5% | few % (O2-limited) unless strongly catalysed and agitated |
| Sulfur capture into liquid (any oxidation state) | >= 90% | 50-90% | < 50% | likely high at equilibrium; rate unknown |
| Product H2SO4 strength at draw-off | >= 0.05 mol/L | 0.005-0.05 | < 0.005 mol/L | <= 0.023 mol/L sulfur-limited, <= 0.012 mol/L oxygen-limited, before wall losses (was: <= 0.024 mol/L) |
| Fraction of acid surviving wall contact for one cycle | >= 80% | 20-80% | < 20% | depends on armour state; bare wall likely fails at low strength |
| Armour durability over 10 fill/drain cycles with fresh water | layer persists | partial | stripped each cycle | likely stripped |
| Bulk temperature rise | >= 20 K (would justify a heat exchanger) | 5-20 K | < 5 K | 1.7-1.8 K (was: ~2 K) |
| p(HCl) over the Khafre mixture | >= 1e-3 atm | 1e-5 to 1e-3 | < 1e-5 atm | ~1e-7 atm (1e-7 to 6e-7 in saturated brine; verified against tabulated data 2026-10-10) |

The hypothesis as told needs the first two rows to pass. The simulation should report each row separately with the sensitivity cases of 4.1(2) clearly labelled as additions to the hypothesis.

### 4.5 Open, usable mechanisms and tools
- **Gas-phase SOx**: Glarborg-group sulfur chemistry; rate data for SO3 + H/O/OH in [8] (opened). A community list of SOx sub-mechanisms for Cantera (Glarborg, Leeds, Alzueta, Rasmussen 2007) exists [35] but was seen only as a search result; file locations and licences were not verified. Cantera's `ck2yaml` converts CHEMKIN files (search result only).
- **Atmospheric gas phase**: OH + SO2 fall-off parameters in [9] (k0 = 3.03e-31 (T/300)^-4.10 cm6 s-1, k_inf = 2.0e-12 cm3 s-1, Fc = 0.58, all read in [9]).
- **Aqueous S(IV)**: compiled rate laws in Tilgner et al. 2021 [11] (open access).
- **Minerals and electrolytes**: USGS PHREEQC with `RATE_PARAMETERS_PK` [18]; Pitzer model for CaSO4-H2SO4-H2O in [23] (CC BY). Reaktoro implements the Palandri-Kharaka form (search result only).
- **Armour layer**: diffusion model and coefficients in [20][21].

---

## 5. Open questions

1. Is there any measurement of present-day or historical H2S flux at Giza? None found. Badawy's full text was not accessible (publisher and mirrors returned 403); only the Crossref abstract was read.
2. What chemistry does the hypothesis assign to each satellite pyramid? Not defined in the relevant transcript sections.
3. Uncatalysed S(IV) + O2 rate law (Connick et al. 1995, Inorg. Chem. 34, 4543, doi 10.1021/ic00122a009): not found in an openable source. The high-S(IV) Mn(II) rate law in [11] came through garbled and needs checking against Martin and Hill 1987.
4. Units of the rate fits in [20][21] are not stated in the abstracts; the 2008 Applied Geochemistry paper by Huminicki and Rimstidt was not located.
5. Acid concentration used by Booth et al. [19] (full text not opened). This decides whether "complete passivation" applies at 0.02 mol/L.
6. Primary record of the 1978 Queen's Chamber salt analysis: not found. Regourd et al. 1988 on pyramid mortars: abstract seen only through search.
7. Sonochemical efficiency versus frequency from Koda et al. 2003: not opened. Cavitation threshold for the frequencies and amplitudes the acoustics domain predicts: not sourced here.
8. Lead-chamber operating temperature from a primary handbook: not found (only a patent snippet at ~60 deg C).
9. HCl partial-pressure tables over dilute acid (Perry's; Fritz and Fuget 1956): not opened; the figure here is derived from the Henry's-law compilation.
10. Feed-water alkalinity and Fe/Mn content (Nile or plateau groundwater), and the Fe/Mn content of the gallery limestone and mortar: not sourced; they control both neutralisation and catalysis.
11. Diffusivity of SO2 in air, free-surface mass-transfer coefficients, molar volumes of calcite and gypsum, Ka2 of sulfuric acid: used from memory in derived estimates; fetch from a handbook before coding.
12. Whether lightning-generated NOx could reach the chambers in meaningful amounts (the only known ambient-temperature gas-phase catalytic route): not investigated.
13. SO2 uptake by damp limestone and mortar surfaces (sulfation) before the gas reaches the water: a USGS wind-tunnel study exists (search result) but was not opened.
14. Advisor review could not be obtained in this session (tool rate-limited), so this file has had no second-reader check.

[Verification 2026-10-10: a second-reader pass has now been done; see "Verification pass (2026-10-10)" at the end of the file. Resolved or partly resolved: question 5 (Booth et al. worked at pH 1 and 2 per [22]; sulfate level still unknown), question 11 (molar volumes and Ka2 sourced from [47]; SO2 diffusivity and transfer coefficients still unsourced), question 12 (lightning NOx investigated and found irrelevant, V12). Still open: 1-4, 6-10, 13, and the list at the end of the verification section.]

---

## 6. Sources

Opened in this session unless marked otherwise.

1. NIST Chemistry WebBook, sulfur dioxide, gas-phase thermochemistry. https://webbook.nist.gov/cgi/cbook.cgi?ID=C7446095&Mask=1
2. NIST Chemistry WebBook, sulfur trioxide, gas-phase thermochemistry. https://webbook.nist.gov/cgi/cbook.cgi?ID=C7446119&Mask=1
3. NIST-JANAF Thermochemical Tables, SO2(g). https://janaf.nist.gov/tables/O-034.html
4. NIST-JANAF Thermochemical Tables, SO3(g). https://janaf.nist.gov/tables/O-058.html
5. NIST-JANAF Thermochemical Tables, H2SO4(cr,l). https://janaf.nist.gov/tables/H-075.html
6. CODATA Key Values for Thermodynamics (Cox, Wagman, Medvedev 1989). https://www.codata.info/resources/databases/key1.html
7. US EPA, AP-42 Fifth Edition, Section 8.10 Sulfuric Acid (7/93). https://www.epa.gov/sites/default/files/2020-09/documents/8.10_sulfuric_acid.pdf
8. Hindiyarti L., Glarborg P., Marshall P. (2007) Reactions of SO3 with the O/H radical pool under combustion conditions. J. Phys. Chem. A 111, 3984-3991. doi:10.1021/jp067499p. Read via https://digital.library.unt.edu/ark:/67531/metadc499072/m2/1/high_res_d/article3.pdf (pages 1-3)
9. Sun W. et al. (2022) Kinetics of OH + SO2 + M. Atmos. Chem. Phys. 22, 4969-4984. https://acp.copernicus.org/articles/22/4969/2022/ (doi:10.5194/acp-22-4969-2022)
10. Sander R., compilation of Henry's law constants (web version): SO2 https://henrys-law.org/henry/casrn/7446-09-5 ; HCl https://henrys-law.org/henry/casrn/7647-01-0 ; O2 https://henrys-law.org/henry/casrn/7782-44-7
11. Tilgner A. et al. (2021) Acidity and the multiphase chemistry of atmospheric aqueous particles and clouds. Atmos. Chem. Phys. 21, 13483-13536. https://acp.copernicus.org/articles/21/13483/2021/ (doi:10.5194/acp-21-13483-2021). First 100k characters read.
12. Kerezsi I. (2006) Photochemical phenomena in the redox reactions of sulfite ion, PhD thesis summary, University of Debrecen. https://dea.lib.unideb.hu/server/api/core/bitstreams/c31dd05a-0e5b-4ad3-ab18-3dc267356ffe/content (pages 1-6)
13. Suslick K. S., The Chemistry of Ultrasound (Britannica Yearbook of Science and the Future article, author's copy). https://suslick.scs.illinois.edu/sonochembrittanica.html
14. Son Y., Lim M., Khim J. (2009) Investigation of acoustic cavitation energy in a large-scale sonoreactor. Ultrason. Sonochem. 16, 552-556. doi:10.1016/j.ultsonch.2008.12.004. Abstract at https://pure.korea.ac.kr/en/publications/investigation-of-acoustic-cavitation-energy-in-a-large-scale-sono/
15. Wikipedia, Lead chamber process (secondary). https://en.wikipedia.org/wiki/Lead_chamber_process
16. Wikipedia, Contact process (secondary). https://en.wikipedia.org/wiki/Contact_process
17. Wikipedia, Mannheim process (secondary). https://en.wikipedia.org/wiki/Mannheim_process
18. USGS PHREEQC version 3 documentation, RATE_PARAMETERS_PK (values of Palandri and Kharaka 2004, USGS OFR 2004-1068). https://water.usgs.gov/water-resources/software/PHREEQC/documentation/phreeqc3-html/rate-parameters_pk.htm
19. Booth J., Hong Q., Compton R., Prout K., Payne R. (1997) Gypsum overgrowths passivate calcite to acid attack. J. Colloid Interface Sci. 192, 207-214. doi:10.1006/jcis.1997.4978. Abstract at https://ora.ox.ac.uk/objects/uuid:331c418e-e930-48d1-9c87-32eac1006538
20. Huminicki D. M. C., Rimstidt J. D. (2005) GSA Abstracts with Programs 37(7), p. 50. https://gsa.confex.com/gsa/2005AM/webprogram/Paper94063.html
21. Rimstidt J. D., Huminicki D. M. C. (2006) The effect of gypsum coatings and hydrodynamic factors on ALD performance. West Virginia Mine Drainage Task Force Symposium. https://wvmdtaskforce.com/wp-content/uploads/2016/01/06-rimstidt.pdf
22. Offeddu F. G., Cama J., Soler J. M., Putnis C. V. (2014) Direct nanoscale observations of the coupled dissolution of calcite and dolomite and the precipitation of gypsum. Beilstein J. Nanotechnol. 5, 1245-1253. doi:10.3762/bjnano.5.138. https://pmc.ncbi.nlm.nih.gov/articles/PMC4142853/
23. Shen L., Sippola H., Li X., Lindberg D., Taskinen P. (2020) Thermodynamic modeling of calcium sulfate hydrates in a CaSO4-H2SO4-H2O system from 273.15 to 473.15 K up to 5 m sulfuric acid. J. Chem. Eng. Data 65, 2310-2324. doi:10.1021/acs.jced.9b00829. https://acris.aalto.fi/ws/portalfiles/portal/43016883/CHEM_Shen_et_al_2020_Thermodynamic_Modeling_JourChemEData.pdf (pages 1-9)
24. Baedecker P. A., Reddy M. M., Reimann K. J., Sciammarella C. A. (1992) Effects of acidic deposition on the erosion of carbonate stone (NAPAP). Atmos. Environ. 26B, 147-158. doi:10.1016/0957-1272(92)90018-N. Abstract at https://pubs.usgs.gov/publication/70017266
25. Clark J., Chemguide, acids and carbonates (school-level). https://chemguide.co.uk/14to16/acids/carbonates.html
26. Badawy H. S. (2021) Development of sulfuric acid speleogenetic deposits within cavernous Middle Eocene beds: inference on hydrocarbon gas seepages, Giza Pyramids Plateau, Egypt. Acta Geologica Sinica (English Edition) 95(3), 946-961. doi:10.1111/1755-6724.14512. Abstract read via https://api.crossref.org/works/10.1111/1755-6724.14512 (publisher page returned 403)
27. US Patent 9,108,846 B2, Method for preparing sulfuric acid by using hydrogen sulfide (Shanghai Keyontechs). https://patents.google.com/patent/US9108846
28. Petrie W. M. F. (1883) The Pyramids and Temples of Gizeh, chapter 7 (online transcription). https://www.ronaldbirdsall.com/gizeh/petrie/c7.html (first 100k characters)
29. Hammarstrom J. M., Sibrell P. L., Belkin H. E. (2003) Applied Geochemistry 18, 1705-1721. doi:10.1016/S0883-2927(03)00105-7. NOT opened; search snippet only. https://pubs.usgs.gov/publication/70024876
30. Ziemkiewicz P. F., Skousen J. G., Brant D. L., Sterner P. L., Lovett R. J. (1997) J. Environ. Qual. 26(4), 1017-1024. NOT opened; search snippet only.
31. Lovejoy E. R., Hanson D. R., Huey L. G. (1996) Kinetics and products of the gas-phase reaction of SO3 with water, J. Phys. Chem.; and Jayne et al. (1997). NOT opened (403); rate expressions from search snippets.
32. Regourd M., Kerisel J., Deletie P., Haguenauer B. (1988) Microstructure of mortars from three Egyptian pyramids. Cem. Concr. Res. 18, 81-90. NOT opened; search snippet only.
33. Koda S., Kimura T., Kondo T., Mitome H. (2003) Ultrason. Sonochem. 10, 149-156. NOT opened; search snippet only.
34. Connick R. E. et al. (1995) Inorg. Chem. 34, 4543. doi:10.1021/ic00122a009. NOT opened; rate law not found.
35. Cantera community wiki listing SOx sub-mechanisms (charlesreid1.com/wiki/Cantera/Mechanisms/SOx). NOT opened; search snippet only.
36. Goodreads quote page attributed to C. Dunn, The Giza Power Plant, on the 1978 salt analysis. NOT opened (403); search snippet only.
37. Local transcripts: clip 1 (`history-drops/...-podcast-pyramid-history-ancient/transcript.md`), clip 2 (`history-drops/...-podcast-science-history-ancient/transcript.md`), full episode (`danny-jones/new-scans-expose-an-unfortunate-secret-under-the-pyramids-geoffrey-drumm/transcript.md`, 00:00-01:37), all under `/Users/aeroshariati/Pyramid/youtube-transcript/`.

Sources added in the verification pass of 2026-10-10 (all opened that day unless marked):

38. NIST Chemical Kinetics Database (kinetics.nist.gov), reaction searches by CAS number. SO3 + O -> SO2 + O2: ten records, including Jacob and Winkler 1972 (300-500 K) and Hindiyarti et al. 2007. https://kinetics.nist.gov/kinetics/ReactionSearch?r0=7446119&r1=17778802&r2=0&r3=0&r4=0&p0=7446095&p1=7782447&p2=0&p3=0&p4=0&expandResults=true& . SO2 + O2 -> SO3 + O: zero records (same URL pattern with reactants and products swapped). SO3 + H2O -> H2SO4: four records.
39. Atkinson R., Baulch D. L., Cox R. A., Crowley J. N., Hampson R. F., Hynes R. G., Jenkin M. E., Rossi M. J., Troe J. (2004) Evaluated kinetic and photochemical data for atmospheric chemistry: Volume I, gas phase reactions of Ox, HOx, NOx and SOx species. Atmos. Chem. Phys. 4, 1461-1738. https://acp.copernicus.org/articles/4/1461/2004/acp-4-1461-2004.pdf (text extracted from the PDF; summary table and data sheets I.A3.53 and I.A4.119 read; DOI not read).
40. Lee C., Martin R. V., van Donkelaar A., Lee H., Dickerson R. R., Hains J. C., Krotkov N., Richter A., Vinnikov K., Schwab J. J. (2011) SO2 emissions and lifetimes: estimates from inverse modeling using in situ and global, space-based (SCIAMACHY and OMI) observations. J. Geophys. Res. 116, D06304. doi:10.1029/2010JD014758. Read via https://carppond.iup.uni-bremen.de/doas/paper/jgr_11_lee.pdf
41. Soler J. M., Boi M., Mogollon J. L., Cama J., Ayora C., Nico P. S., Tamura N., Kunz M. The passivation of calcite by acid mine water. Column experiments with Fe(III)-SO4-H+ and Fe(III)-Cl-H+ solutions at pH 2. Author manuscript, Lawrence Berkeley National Laboratory, https://escholarship.org/uc/item/3t90m2zh (PDF text read; the journal of record is not named in this copy and is not asserted here).
42. Encyclopaedia Britannica, 11th edition (1911), "Sulphuric Acid", Wikisource transcription. https://en.wikisource.org/wiki/1911_Encyclop%C3%A6dia_Britannica/Sulphuric_Acid
43. Perry's Chemical Engineers' Handbook, Section 2 "Physical and Chemical Data", Table 2-10, Partial pressures of HCl over aqueous solutions of HCl (copyright 1999 McGraw-Hill; edition number not read). Read from a course copy at https://terpconnect.umd.edu/~nsw/chbe301/chap02.pdf (text extracted from the PDF).
44. Alexander B., Park R. J., Jacob D. J., Gong S. (2009) Transition metal-catalyzed oxidation of atmospheric sulfur: global implications for the sulfur budget. J. Geophys. Res. 114, D02309. doi:10.1029/2008JD010486. Read via the Harvard DASH copy (equation 3 quotes Martin and Good 1991).
45. Wilkins S. J., Compton R. G., Viles H. A., Taylor M. P. (2002) A new technique to evaluate and quantify modified solution kinetics of calcareous materials after sulphuric acid pre-treatment and urban exposure. Studies in Conservation 47(2), 88-94. Abstract at https://researchers.mq.edu.au/en/publications/a-new-technique-to-evaluate-and-quantify-modified-solution-kineti/ (DOI not shown there).
46. Geological Survey of Finland (GTK), Mine Closure guide, "Anoxic limestone drains (ALD)" (secondary; attributes the 2000 mg/L sulfate figure to Hedin and Watzlaf 1994, not opened). https://mineclosure.gtk.fi/anoxic-limestone-drains-ald/ . The 1500 mg/L figure from an ITRC guidance page was seen only in a search summary.
47. USGS PHREEQC version 3 database file `phreeqc.dat`, current GitHub copy. https://raw.githubusercontent.com/usgs-coupled/phreeqc3/master/database/phreeqc.dat (entries for Gypsum, Calcite and HSO4- read directly from the file).
48. Schumann U., Huntrieser H. (2007) The global lightning-induced nitrogen oxides source. Atmos. Chem. Phys. 7, 3823-3907. doi:10.5194/acp-7-3823-2007 (abstract page).
49. Adams J. W., Rodriguez D., Cox R. A. (2005) The uptake of SO2 on Saharan dust: a flow tube study. Atmos. Chem. Phys. 5, 2679-2689. doi:10.5194/acp-5-2679-2005 (abstract page).
50. Baltrusaitis J., Cwiertny D., Grassian V. (2007) Adsorption of sulfur dioxide on hematite and goethite particle surfaces. Phys. Chem. Chem. Phys. 9(41), 5542-5554. Abstract at https://baltrusaitislab.lehigh.edu/publications/adsorption-sulfur-dioxide-hematite-and-goethite-particle-surfaces
51. Spiker E., Hosker R., Weintraub V., Sherwood S. (1995) Laboratory study of SO2 dry deposition on limestone and marble: effects of humidity and surface variables. Water, Air, and Soil Pollution 85(4), 2679-2685. doi:10.1007/BF01186239. Abstract at https://pubs.usgs.gov/publication/70018824
52. Verification arithmetic: `verify03.py` and `gyp.py`, Python standard library only, kept outside the project in the session scratchpad (`/private/tmp/claude-501/-Users-aeroshariati-Pyramid/4a93d66c-12de-49a2-8aa6-a84a56de75a2/scratchpad/chem/`). The scratchpad is temporary; the working is reproduced in the verification section so the numbers do not depend on it.

---

## Verification pass (2026-10-10)

Second-reader check of this file. Scope: the load-bearing numbers and the seven items the brief singled out (gas-phase rate, equilibrium, Henry's constant, aqueous rate laws, stoichiometric ceiling and temperature rise, gypsum armouring, HCl partial pressure), plus a steelman of low-temperature routes. Status vocabulary: **confirmed** (read in an opened source this session, or independently recomputed from values so read), **corrected**, **unverifiable** (with the reason), **wrong**. Sources [38]-[52] were added to section 6. Where a web extraction was unreliable the PDF was fetched and its text extracted locally, and that is stated. An advisor review was again unavailable (rate-limited), so this pass is one reviewer's work.

### Checks

| # | Item | First-pass value | Status | Evidence and working | Source |
|---|---|---|---|---|---|
| V1 | Equilibrium constant and enthalpy of SO2 + 1/2 O2 = SO3 at 300 K | log10 Kp = 12.31; dH = -98.9 kJ/mol | confirmed | JANAF rows re-read: log Kf(SO3) = 64.573, log Kf(SO2) = 52.260 at 300 K, difference 12.313, Kp = 2.05e12 bar^-1/2. dfH 298.15 K: -395.765 - (-296.842) = -98.92 kJ/mol; at 300 K -98.93. Cross-check from dfG(300 K): -370.862 + 300.145 = -70.717 kJ/mol, giving log10 K = 12.313. | [3][4] |
| V2 | Uncatalysed gas-phase SO2 + O2 at 300 K is effectively zero | k <= 7e-37 cm3/molecule/s; lifetime >= ~1e10 yr | confirmed, and the bound is conservative | Endothermicity re-derived from JANAF: -395.765 + 249.173 + 296.842 = +150.25 kJ/mol; dG(300 K) = +160.91 kJ/mol, so K_eq = 9.6e-29. First-pass bound reproduced: 1e-10 x exp(-150200/(8.314 x 300)) = 7.1e-37; with [O2] = 5.13e18 cm-3 the lifetime is 2.8e17 s = 8.8e9 yr. Detailed balance with a gas-kinetic reverse rate (3e-10) gives k <= 2.9e-38 and >= 2e11 yr. With the one low-temperature reverse-rate measurement on record (4.6e-17 at 300 K) the lifetime is about 1e18 yr. The NIST database holds ten records for SO3 + O -> SO2 + O2 and none for the forward direction. Hindiyarti's expression, barriers (139 and 123 kJ/mol) and -151.1 / -155.5 kJ/mol were re-read from the PDF pages. | [3][4], JANAF O(g) table (janaf.nist.gov/tables/O-001.html), [8][38] |
| V3 | Real-atmosphere SO2 sinks and lifetimes | OH route "a few days", ~12 d by arithmetic | confirmed; total-lifetime figure added | k(OH + SO2, 298 K, 1 atm) = 1.04e-12 (Sun), 9.38e-13 (IUPAC) and 9.50e-13 (NASA) as quoted by Sun; at [OH] = 1e6 cm-3 that is 11.1-12.3 d. The observed total lifetime is much shorter: 13 h (summer) and 48 h (winter) modelled, 19 +/- 7 h and 58 +/- 20 h from in situ data over the eastern US; 0.6-2.6 d global means; the sinks are OH, dry deposition (velocities generally 0.4 cm/s or less) and in-cloud oxidation by H2O2. So most atmospheric SO2 is removed by wet chemistry and surfaces, not by the gas-phase radical route. None of these sinks is the homogeneous thermal reaction of V2. | [9][40] |
| V4 | SO3 + water rate and SO3 lifetime in humid air | Jayne and Lovejoy expressions (snippets); 20-30 microseconds | corrected (lifetime), Jayne expression confirmed | IUPAC 2004 data sheet I.A4.119: first-order loss (3.9 +/- 0.8)e-41 exp(6830/T) [H2O]^2 s-1 (283-370 K, Jayne et al.), preferred value 5.7e4 s-1 at 298 K and 50% RH, i.e. 17.5 microseconds. Recomputed with [H2O] = 3.85e17 cm-3: 5.1e4 s-1, 19.5 microseconds. Table updated to 18-20 (was 20-30). The Lovejoy expression was not found in an opened source. | [39] |
| V5 | Henry's constant of SO2 | 1.3e-2 mol/(m3 Pa), 2900 K | confirmed | Sander compilation re-read: the four JPL-evaluation entries give 1.3e-2 and 2900 K; other entries 1.1e-2 to 1.5e-2. Equals 1.32 mol/L/atm. C4 check: 0.0232 mol/L total S(IV) with pKa1 1.9 leaves 0.0113 mol/L molecular SO2, in equilibrium with 0.0085 atm, so the "~0.9%" figure stands. | [10] |
| V6 | Aqueous S(IV) oxidation rate laws with Fe and Mn | Fe: 1.2e6 [Fe(III)][SO3^2-], ~3e-7 mol/L/s, "roughly a day"; Mn: 1e3 [Mn][S(IV)], high-S(IV) form garbled | confirmed (Fe law, first-pass arithmetic); corrected (Mn high-S(IV) law); first-pass timescale is the slow end of the published range | Hoffmann-Calvert law and pH < 5 range re-read; at pH 1.7 the sulfite fraction is 1.22e-6, so R = 1.2e6 x 1e-5 x 0.02 x 1.22e-6 = 2.9e-7 mol/L/s (19 h). The alternative Martin law compiled in the same review (6 [Fe][S(IV)]/[H+] with ionic-strength and sulfate inhibition) gives 2.6e-5 mol/L/s initially and about 2e-6 once 0.02 mol/L sulfate has formed, i.e. 0.2-3 h. Mn above 1e-4 mol/L S(IV): R = 680 [Mn(II)]^2, zero order in S(IV); at I = 0.05 this gives 19 d for 1e-5 mol/L Mn and 0.2 d for 1e-4 mol/L. Synergy law 750 [Mn][S] + 2600 [Fe][S] + 1.0e10 [Mn][Fe][S] read in [44]. pH dependence: uncatalysed route negligible in acid; Fe route falls as 1/[H+] (Martin) or with the sulfite fraction (Hoffmann-Calvert, roughly 1/[H+]^2 below pH 1.9); the Mn laws carry no explicit pH term; the mixed law of Ibusuki and Takeuchi rises as [H+]^-0.74 over pH 2.6-4.2. Every law is being used 2-3 orders of magnitude above its tested S(IV) range and below or at the edge of its pH range. | [11][44] |
| V7 | Stoichiometric ceiling on acid strength | 1.33e4 mol; 0.024 mol/L (0.24 wt%) in ~550 m3 | corrected | Volumes from 01-geometry table F: King's Chamber 320.4 m3 less 1.16 m3 coffer solid; Grand Gallery 573 m3 +/- 8%. n = 101325 x 319.2 / (8.314 x 293.15) = 1.327e4 mol (850 kg SO2). In 573 m3 of water: 0.0232 mol/L = 0.227 wt% (0.021-0.025 over the volume uncertainty; 0.017 if the Queen's Chamber, niche and passage, 220 m3, fill too). pH 1.53 with log K(HSO4-) = 1.988, no activity correction. New, tighter case: oxygen must come from air in the same stroke; a stoichiometric mixture is 29.5 vol% SO2, so one 573 m3 stroke carries 7.0e3 mol SO2 and yields at most 0.012 mol/L (plus about 0.3e3 mol from dissolved O2). Assumptions: pure SO2 at 1 atm and 293 K in the chamber, complete capture and oxidation, no wall losses, one batch per fill. | 01-geometry.md; [47] |
| V8 | Temperature rise | ~1.9 K; 78 K per mol/L | corrected (small) | dH to dilute sulfate re-derived: -909.34 + 296.81 + 285.83 = -326.70 kJ/mol; to bisulfate -304.3. Heat = 1.327e4 x 326.7 kJ = 4.34e9 J into 573 m3 x 998 kg/m3 x 4.181 kJ/kg/K = 1.81 K; 1.72 K with 26% sulfate / 74% bisulfate. Boiling from 20 deg C would need about 1.0 mol/L made in situ, 44 times the sulfur-limited ceiling. SO3 route: -132.39 and -95.35 kJ/mol re-derived. Masonry heat capacity ignored (would lower the rise). | [1][5][6] |
| V9 | Gypsum armouring: stops or slows at ~0.02 mol/L acid | "can slow by orders of magnitude; some report complete passivation; at this dilution may not form at all" | confirmed in substance; one statement softened | Rimstidt and Huminicki re-read in full: coatings formed at low pH where sulfate was high, rate decays as t^-0.53, never zero, D(H+) = 1.71e-15 to 4.54e-14 m2/s; coatings adhere and cannot be flushed. Booth: complete passivation claimed; conditions pH 1-2 in HCl / Li2SO4 (via [22]). Wilkins: 0.1 M acid for 21 h cut the rate constant nearly tenfold, not to zero. Offeddu: full coating only in gypsum-saturated solution; isolated growths at 6-31 mmol/L sulfate when undersaturated; runs lasted about 40 min. New and most relevant: Soler et al. columns at pH 2 became inert through gypsum, after 122-489 h at 3323 mg/L sulfate, 2443-3506 h at 2061 mg/L and 7030 h at 1386 mg/L, neutralising acid until then. Hammarstrom: pH 2.9 mine water armoured limestone within 48 h and alkalinity generation stopped (Fe-Al coat over a gypsum rind). Answer: at 12-23 mmol/L sulfate a coating slows attack and can eventually make calcite inert, but only after weeks to months of acid supply and substantial neutralisation. Derived: bulk gypsum saturation is reached after 47% of the acid is neutralised at 0.023 mol/L (was ~40%), 66% at 0.017 and 92% at 0.012 mol/L (Davies activity coefficients, log K = -4.55, no ion pairing). | [19][21][22][29][41][45][47] |
| V10 | Lead-chamber data | chamber acid 62-70%, Glover up to 78% (Wikipedia); gas temperature ~60 deg C (snippet) | corrected (strengths); unverifiable (temperature) | 1911 Britannica: chamber acid 60-70%, preferably 66-67%; Glover-tower acid 78-80%; nitre loss as low as 2 parts per 100 of sulfur burned; nitrogen oxides are the oxygen carrier and the direct reaction without one goes "only to a very small extent". No chamber temperature is given there; the 60 deg C figure remains a patent snippet. | [42] |
| V11 | HCl partial pressure over dilute H2SO4 + NaCl | ~1e-7 atm | confirmed | Effective Henry constant 2.0e7 mol2/(m6 Pa) = 2.03e6 mol2/L2/atm re-read. Check against tabulated data: predicted 8.9e-8 atm over 2 wt% HCl (0.559 mol/kg, mean activity coefficient 0.76 from memory) versus 8.4e-5 mmHg = 1.1e-7 atm tabulated at 25 deg C. Batch mixture: 0.05 x 5 / 2.03e6 = 1.2e-7 atm as first pass; with saturated brine (6.1 mol/kg) and an activity-coefficient product of about 4 (Harned-rule estimate from memory, unverified) 4e-7 to 6e-7 atm. For scale, 1e-3 atm needs more than 22 wt% HCl (tabulated 0.68 mmHg = 8.9e-4 atm). The batch has at most 0.046 mol/L of acid equivalents, i.e. 0.17 wt% as HCl. | [10][43] |
| V12 | Lightning NOx as a lead-chamber catalyst source (open question 12) | not investigated | new result: quantitatively irrelevant | A typical flash makes 15 (2-40) x 10^25 NO molecules, about 250 mol, spread along kilometres of channel. A gallery stroke draws at most 573 m3 of gas; even at 100 ppb NOx (generous; no near-surface storm value was sourced) that is 2.4e-3 mol. Chamber practice lost about 2 parts nitre per 100 sulfur even with recovery, i.e. about 100 mol N per 1.33e4 mol S as make-up alone, so the shortfall is at least 4-5 orders of magnitude. The carrier cycle also stalls at trace level: 2 NO + O2 is second order in NO (2.0e-38 cm6/molecule2/s), so NO re-oxidation takes 20 s at 1 vol%, 2.4 d at 1 ppm and 6.5 yr at 1 ppb. | [39][42][48] |
| V13 | Oxygen supply through the free surface (C5) | ~150 mol dissolved; ~25 m2; "years" for a full batch | confirmed (arithmetic); transfer coefficient still unsourced | O2 saturation 1.3e-5 x 0.2095 x 101325 = 0.276 mol/m3; 573 m3 holds 158 mol, enough for 316 mol S(IV) (2.4% of the sulfur-limited batch). Free surface in the inclined gallery = 13.59 m2 / tan 26.28 deg = 27.5 m2. Flux at k_L = 1e-6, 1e-5, 1e-4 m/s: 0.66, 6.6, 66 mol O2/day, i.e. 28, 2.8, 0.3 yr for 6.6e3 mol O2. The k_L range is an assumption; no source was opened for it. Chemical enhancement does not rescue the still-surface case: for zero-order O2 consumption r in an oxygen-starved liquid the film flux cannot fall below sqrt(2 D C* r), which is 1e-6 to 4e-6 mol/m2/s for r = 1e-3 to 1.3e-2 mol/m3/s (the Martin-law rates of V6; D(O2) = 2.1e-9 m2/s from memory). That equals the physical flux at k_L of about 4e-6 to 1.4e-5 m/s, so fast catalysis removes the slowest case (28 yr) but leaves 2-8 yr for an undisturbed surface. With the slower Hoffmann-Calvert rate there is no enhancement at k_L = 1e-5 m/s. | [10]; 01-geometry.md |
| V14 | Patent US 9,108,846 (C2) | three steps at >= 900 or >= 200, 390-430, 60-120 deg C | confirmed | Claims re-read: step 1 combustion at >= 900 deg C for H2S >= 8 mol%, otherwise catalysed from >= 200 deg C; step 2 at 390-430 deg C to >= 98.7% conversion (vanadium catalyst per the description); step 3 cooling to 60-120 deg C. Heat exchangers are claimed for the cooling steps. No step is ambient and uncatalysed. | [27] |
| V15 | Surface route on iron oxides and mineral dust (steelman) | not covered | new result: real but capacity-limited | Initial uptake coefficient of SO2 on Saharan dust (6.6 +/- 0.8)e-5 (BET basis, 298 K), declining with time and largely irreversible. On hematite and goethite SO2 adsorbs as sulfite and sulfate up to a saturation coverage; O2 converts it to sulfate on hematite and roughly doubles uptake; humidity weakens that gain. This is stoichiometric surface loading, not turnover: a monolayer is of order 1e-6 to 1e-5 mol per m2 of true surface (my estimate, unsourced), so even 1e6 m2 of internal surface holds about ten moles at most against 1e4 mol per batch. Once the surface is wet the process is the aqueous Fe route of V6. | [49][50] |
| V16 | Uncatalysed S(IV) + O2 rate law (Connick et al. 1995) | "not found in an openable source" | unverifiable | Only the Crossref record could be opened (title, authors, Inorg. Chem. 34(18), 4543-4553); it carries no abstract. The qualitative statement from [12] stands as the only support. | [34] |
| V17 | Calcite and gypsum constants used from memory | molar volumes, Ka2 of sulfuric acid, gypsum solubility | confirmed | phreeqc.dat: gypsum log K -4.55 and 73.9 cm3/mol; calcite 36.9 cm3/mol (ratio 2.0, as assumed in C11); log K for bisulfate formation 1.988. Palandri-Kharaka calcite line re-read as -0.3, 14.4, 1; units still not stated on that page. A fresh 573 m3 fill can dissolve up to 573 x 15.2 = 8.7e3 mol gypsum, 0.68 mm over 940 m2 (first pass: ~8000 mol, ~0.7 mm). | [18][47] |
| V18 | Items not re-checked or still unverified | - | unverifiable / not attempted | Lead-chamber gas temperature (see V10); Lovejoy 1996 expression; Mannheim temperatures [17] (not re-checked); Ziemkiewicz et al. [30] (not opened); contact-process window [16]; units of the fits in [20][21]; the H+ exponent and the square root on ionic strength in the Martin and Mn laws (extraction ambiguous); SO2 deposition velocity on damp limestone (the abstract [51] gives humidity trends but no number). | - |

### Steelman: could any low-temperature route work?

1. **Nitrogen-oxide carrier (lead-chamber chemistry).** This is the one proven route from SO2, air and water to sulfuric acid without a hot solid catalyst, and it was still a standard industrial process when [42] was written. It needs nitrogen oxides at process level: make-up alone was about 0.75 mol N per 100 mol S with recovery towers [42], and the cycle turns over through 2 NO + O2, whose rate collapses at low NO (V12) [39]. Lightning does not supply it: 250 mol NO per flash is dispersed through cubic kilometres [48], and the air drawn in one stroke would carry milligram quantities (V12). The route becomes possible only if a concentrated nitrate or nitric-acid source is added to the hypothesis. The speaker assigns nitric acid to the Bent Pyramid as one option but does not bring it to Giza, so this is an addition, not part of the claim. Industry ran it in lead vessels to 60-70% acid [42]; in a water-filled limestone gallery it would give dilute acid subject to the wall losses of C10. The simulation's NOx sensitivity case (4.1, item 2a) should therefore sweep NOx mole fraction from 1e-9 to 1e-2 and report the threshold at which the cycle turns over within one batch dwell; the prior expectation is that it needs at least 1e-4.
2. **Metal-ion-catalysed aqueous oxidation.** Real, and the chemistry may be faster than this file first said: hours rather than a day at 1e-5 mol/L Fe(III) on the Martin law, or with 1e-4 mol/L Mn(II) (V6). Iron and manganese at those levels are plausible in acid that has touched limestone and iron-oxide veins (no measurement sourced; open question 10). This is the strongest point in the hypothesis's favour found in this pass. Its limits are oxygen and sulfur supply, not kinetics: 0.012 mol/L at most if the oxygen comes from one stroke of air (V7), and years through an undisturbed 27 m2 surface (V13). Whether pumping, cascading down the passages or bubbling through the grooves could aerate the water enough is a hydraulics question the chemistry cannot settle; it needs an effective k_L a three to four orders of magnitude above a still surface to finish in a day.
3. **Iron-oxide and dust surfaces in the dark.** SO2 does oxidise to sulfate on hematite with O2, without light [50], and dust takes it up irreversibly [49]. The surface saturates; it is a sink of about ten moles at most, not a catalyst (V15).
4. **Radical and photochemical routes.** OH converts SO2 with a lifetime of 11-12 days at a global-average boundary-layer OH of 1e6 cm-3 [9]; the chambers are dark; each SO2 consumes one OH unless NO is present to recycle HO2, so a batch would need of order 1e4 mol of radicals. HO2 and NO3 react with SO2 at less than 1e-18 and 1e-19 cm3/molecule/s [39]. Not viable.
5. **Damp limestone as a sink.** SO2 deposits on limestone increasingly with humidity, and on wet stone the rate is limited by air-side transport [51]. With outdoor deposition velocities of up to 0.4 cm/s [40] and a gallery volume-to-wall ratio of about 0.6 m, wall uptake could strip SO2 in minutes to hours (derived; indoor still-air values would be lower, and none was sourced). This would put calcium sulfite and sulfate on the walls, which fits the mineral evidence, but it removes sulfur from the acid product and consumes the wall.
6. **Armouring.** The literature gives the hypothesis more than the first pass allowed: gypsum can render calcite inert even at 14-22 mmol/L sulfate and pH 2 [41]. The cost is time and acid (V9), and the armour is soluble in each fresh-water fill (V17).

Net: no route found makes sulfuric acid in the gas phase at ambient temperature with ultrasound. Two wet routes are chemically sound (item 1 with an added NOx source, item 2 with aeration), and the simulation should carry both as labelled sensitivity cases so that it can pass if the transport numbers allow.

### Verdict changes

| Claim | First-pass verdict | After verification | Reason |
|---|---|---|---|
| C3 (gas-phase SO2 -> SO3 with ultrasound) | contradicted (rate and mechanism); thermodynamics supported | unchanged; evidence stronger | Bound reproduced and tightened by detailed balance; no forward-rate record exists in the NIST database (V1, V2). The "what would help" line should add that lightning NOx is 4-5 orders short (V12). |
| C5 (sulfurous acid oxidises quickly in air) | partly supported; speed contradicted for acidic, unstirred, unsparged water | partly supported; softened on kinetics, tightened on stoichiometry | With >= 1e-5 mol/L Fe(III) or >= 1e-4 mol/L Mn(II) the chemical timescale is hours, so "slow chemistry" is not the objection (V6). The objection is oxygen: years through a still surface (V13), untested under agitation, and a ceiling of 0.012 mol/L from one stroke of air (V7). |
| C10 (gypsum coat halts attack) | partly supported; durability doubtful; summary said armour "may not form at all" at this dilution | partly supported; "may not form at all" withdrawn | Passivation to inertness is documented at 14-22 mmol/L sulfate and pH 2, but after 2400-7000 h and with neutralisation continuing until then (V9). "Insoluble" remains wrong (V17). |
| C14 (dilute acid product) | undefined by hypothesis; ceiling 0.002-0.024 mol/L | undefined by hypothesis; ceiling 0.012 mol/L (oxygen-limited) to 0.023 mol/L (sulfur-limited) | Recomputed with the geometry-file volumes (V7). |
| C2, C4, C6, C7, C8, C12, C13 | as stated | unchanged | C2: patent re-read (V14). C4: Henry constant confirmed (V5). C6: SO3 hydration lifetime 18-20 microseconds (V4). C7: 1.7-1.8 K (V8). C12: tabulated HCl pressures agree with the Henry's-law estimate (V11). |
| C1, C9, C11, C15 | as stated | not re-examined here | These rest on the geology and archaeology files. |

Pass/fail table (4.4): the priors for "Product H2SO4 strength at draw-off" and "Bulk temperature rise" have been updated in place (old values kept as "was:"). The prior for "Fraction of acid surviving wall contact" should note that a previously armoured wall may pass while a bare or freshly rinsed wall is expected to lose a large fraction: the transport-limited fit in [21] gives of order 1e-4 mol/m2/s at 0.03 mol/kg H+ (derived, units assumed to be mol/m2/s), which over 940 m2 would neutralise a batch in a day or two.

### Still open after this pass

1. Connick et al. 1995 rate law for the uncatalysed reaction (V16).
2. Lead-chamber gas temperature and circulating NOx fraction from a primary handbook (Lunge) (V10).
3. Clean transcription of the Martin and Hill laws: H+ exponent, square root on ionic strength, validity limits (V6). The originals (Atmos. Environ. 1987, 1991) were not reachable.
4. Sulfate concentration used by Booth et al.; full text of Huminicki and Rimstidt 2008 (units, sulfate threshold for coating); primary source for the 2000 mg/L threshold (V9).
5. A sourced air-water transfer coefficient for the gallery free surface under the stated pumping, and whether any step aerates the water (V13). This single number decides C5.
6. Fe and Mn concentrations in the feed water and leached from Mokattam limestone and mortar at pH 1.5-2 (decides V6).
7. SO2 deposition velocity onto damp limestone in still air (steelman item 5).
8. Activity coefficient of trace HCl in concentrated NaCl brine (used from memory in V11; changes the result by a small factor only).
9. Mannheim-process temperatures [17] and Ziemkiewicz et al. [30] were not re-checked.
