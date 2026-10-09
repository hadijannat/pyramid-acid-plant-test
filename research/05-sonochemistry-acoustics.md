# 05 - Sonochemistry and acoustics

Domain brief for the "Land of Chem" simulation. Scope: the acoustic-catalyst claim (ultrasound turning SO2 + O2 gas into SO3 in the antechamber), the acoustic character of the antechamber, and the ultrasonic flow/level-meter reading of the Queen's Chamber south-shaft blocking stone.

Conventions: `verified = yes` means I read that figure in the cited source during this session (page fetch, PDF page read, or abstract text). `verified = no` means recalled, taken from a search-result snippet, or from a source I could not open. "Derived" rows are my own arithmetic from verified inputs; the working is shown in section 4. Source numbers [S#] refer to section 7.

---

## 1. Summary

1. **What the hypothesis says (transcripts [S36]).** Lightning and telluric currents set up an electric field around the granite King's Chamber and antechamber; quartz in the granite responds by the inverse piezoelectric effect and emits ultrasound; that ultrasound, concentrated in the antechamber, converts SO2 and O2 gas to SO3 (Part 1 at 00:12:19-00:13:25; Part 2 at 00:00:00-00:02:32 and 00:09:28-00:09:53; full episode at 00:50:07-00:51:13 and 00:58:48-01:01:16). Separately, the Tura-limestone blocking slab with two copper pins in the Queen's Chamber south shaft is read as a non-invasive ultrasonic flow/level meter, with a possible receiver in the north shaft; the speaker labels this part as speculative and "just for fun" (Part 2 at 00:22:07-00:25:04; full episode 01:21:08-01:24:12). **No frequency, intensity, field strength, duty cycle or receiver is specified anywhere in the three transcripts.**

2. **Accepted mechanism of sonochemistry.** Chemical effects of ultrasound arise from acoustic cavitation - nucleation, growth and violent collapse of bubbles in a liquid - not from sound acting on molecules directly [S2, S3]. Suslick states that "cavitation can take place only in liquids" and that reactions therefore do not generally occur when solids or solid-gas systems are sonicated [S3]. Hot-spot conditions are about 5000 K and 1000 atm with heating/cooling above 1e10 K/s, lasting well under a microsecond [S2, S3]. Working intensities are about 1 W/cm2 (cleaning baths) to 10-500 W/cm2 (horns), typically near 20 kHz [S3].

3. **Gas-phase evidence.** I searched for peer-reviewed evidence of ultrasound driving a homogeneous gas-phase oxidation with no liquid present and found none. The nearest real phenomena are (a) aqueous ultrasound-assisted S(IV)/SO2 chemistry, which is well documented but requires a liquid [S15-S20]; (b) acoustic-wave-modulated heterogeneous catalysis, where MHz bulk or surface acoustic waves on a single-crystal ferroelectric (LiNbO3) carrying a 100 nm Pd or Ag film change catalytic selectivity [S21] - a surface-lattice effect needing an engineered catalyst film, not sound in a gas; (c) physical uses of airborne power ultrasound (agglomeration, defoaming, drying) [S14]. None of these is the process described.

4. **Order-of-magnitude result (section 4).** Using the measured apparent piezoelectric coefficient of granite (1.4e-15 C/N [S12]) and the most generous sustained field I can justify (air breakdown, about 3 MV/m, assumed), the granite leaf would radiate about 76 dB SPL (about 4e-9 W/cm2) at 40 kHz into the antechamber. Nucleating cavitation in a liquid film from the gas side would need roughly 189 dB in the air (about 870 W/cm2), at the limit of linear acoustics; the best engineered airborne sources reach about 172 dB (10 W/cm2) [S14]. The gap is about 113 dB, i.e. 11 orders of magnitude in intensity. For dry gas there is no threshold to aim at because no mechanism is known; the acoustic temperature swing at 76 dB is about 1.5e-4 K.

5. **Antechamber acoustics.** I found no published acoustic measurement of the antechamber of any kind. Published or semi-published acoustic work concerns the King's Chamber only, and the room-acoustic part of it is trade-press or commercial, not peer-reviewed [S24, S25]. The peer-reviewed measurements inside the pyramid are ultrasonic non-destructive testing of the King's Chamber granite [S8] and ambient-vibration seismology [S26]; neither is a room-acoustics study. An EVA London 2026 conference paper titled as a comparative impulse-response study inside the pyramid exists in an index [S33] but I could not open it.

6. **Flow/level meter.** Real clamp-on transit-time and Doppler meters need a transducer acoustically coupled (gel/solid contact) to a liquid-filled pipe wall, an electronic drive and a receiver [S23]. Real long-range ultrasonic level sensors work through open air at low frequency (13 kHz for 60 m range) and must face the liquid surface perpendicularly [S22]. The proposed geometry - a 5-9 cm limestone slab about 63 m up a 20 cm shaft whose lower end was never cut through to the chamber [S1, S28] - gives a through-path loss of roughly 234-252 dB at 40 kHz and 100-118 dB at 13 kHz before spreading, bends and transduction losses (section 4.5). MHz frequencies used by pipe flow meters are excluded outright (about 160 dB/m in air [S5]). A through-transmission arrangement could at most act as a one-point level switch at the height of the shaft mouths, not a flow meter or continuous level gauge.

7. **What supports the hypothesis, stated fairly.** (i) Sonochemistry is real and can oxidise dissolved S(IV); (ii) quartz is piezoelectric and granite shows a small measurable bulk effect [S11, S12]; (iii) the south-shaft slab is very probably fine Tura-type limestone and carries two copper fittings, and the 2002 Pyramid Rover reported a similar pinned slab in the north shaft [S28] - which matches the form of the speaker's prediction that metal parts would be found there, although it predates the prediction by two decades and does not discriminate between a sensor and a symmetric architectural feature; (iv) the shafts really were left closed at the chamber end [S1].

---

## 2. Parameters

### 2.1 Geometry relevant to acoustics

| name | value | unit | uncertainty | source | verified |
|---|---|---|---|---|---|
| Antechamber length (N-S) | 116.30 (2.954) | in (m) | Petrie mean | [S1] sec. 48 | yes |
| Antechamber breadth (E-W) | 65.00 (1.651) | in (m) | Petrie mean; wider above the wainscots | [S1] sec. 48 | yes |
| Antechamber height | 149.35 (3.793) | in (m) | Petrie mean | [S1] sec. 48 | yes |
| Antechamber gross volume | 18.5 | m3 | about +/-15 % (leaf, wainscot offsets, grooves not subtracted) | derived from [S1] | derived |
| Antechamber gross surface | 44.7 | m2 | about +/-15 % | derived from [S1] | derived |
| Granite leaf thickness | 15.16-16.20 (0.385-0.411) | in (m) | range as measured | [S1] sec. 50 | yes |
| Granite leaf width between ledges | 40.6-41.2 (1.03-1.05) | in (m) | range | [S1] sec. 50 | yes |
| South-wall vertical grooves | 4; depth up to 2.8 in; Petrie judged they did not reach down to the passage top | - | two of four largely broken away | [S1] sec. 49 | yes |
| King's Chamber length x breadth | 412.59 x about 206 (10.48 x 5.23) | in (m) | Petrie | [S1] sec. 51-52 | yes |
| King's Chamber height | about 5.8 | m | secondary (Wikipedia citing Maragioglio & Rinaldi) | [S29] | yes (secondary) |
| Queen's Chamber shaft cross-section | N: about 8 wide x 8.6 high; S: 8.8 high (about 0.20-0.22) | in (m) | - | [S1] sec. 44 | yes |
| QC shaft horizontal run, then slope | N: 76 in then about 37 deg 28 min; S: 80.0 in then about 38 deg 28 min | - | - | [S1] sec. 44 | yes |
| QC shafts cut through to chamber? | No - a plate of stone was left in the wall | - | thickness not given by Petrie | [S1] sec. 44 | yes |
| Thickness of stone left at chamber end | about 5 (0.13) | in (m) | from an 1878 periodical quoted in a search result | search snippet | no |
| Distance to first blocking slab, south shaft | 65 (robot climb, 1993); 63.6 +/- 0.4 (Djedi write-up) | m | sources differ by about 1.5 m | [S29]; snippet of [S28] | 65 m yes (secondary); 63.6 m no |
| South blocking slab face and thickness | 20 x 20 cm; 5-9 cm by impact-echo (Pyramid Rover); roughly 60 mm (Djedi) | cm | - | [S28]; snippet | 5-9 cm yes; 60 mm no |
| Slab material | finer limestone than the shaft walls, judged probably Tura | - | visual judgement, no lab analysis reported | [S28] | yes |
| Cavity behind south slab | about 19 cm to a rough second block | cm | - | [S28] | yes |
| North shaft: slab with copper pins | reported by Pyramid Rover (2002), similar stone and workmanship | - | single write-up by a Djedi team member | [S28] | yes (single source) |
| North shaft course | bends at about 17-18 m to pass the Grand Gallery | m | secondary | [S29, S31] | yes (secondary) |
| Height of QC shaft mouths above floor | not found | - | - | - | - |

### 2.2 Acoustic and material properties

| name | value | unit | uncertainty | source | verified |
|---|---|---|---|---|---|
| Air absorption, 10 kHz (20 C, 50 % RH, 101.325 kPa, ISO 9613-1) | 0.159 | dB/m | strongly T- and RH-dependent | [S4] Table 2 | yes |
| Air absorption, 20 kHz (same conditions) | 0.525 | dB/m | same | [S4] Table 2 | yes |
| Air absorption, 30 kHz | 0.936 | dB/m | same | [S4] Table 2 | yes |
| Air absorption, 40 kHz | 1.318 | dB/m | same | [S4] Table 2 | yes |
| Air absorption, 13 kHz | about 0.25 | dB/m | my interpolation between 10 and 20 kHz | derived from [S4] | derived |
| Air absorption, 100 kHz (20 C, 60 % RH) | about 2.1 (graph); maximum 6.3 at 57 C (text) | dB/m | graph read +/-10 %; I expect up to about 3.3 from the f-squared classical term plus relaxation (recalled), so use 2-3.5 | [S5] Fig. 2b and text | yes (graph) |
| Air absorption, 500 kHz (20 C, 60 % RH) | about 40 | dB/m | graph read | [S5] Fig. 3a | yes (graph) |
| Air absorption, 1 MHz (20 C, 60 % RH) | about 160 | dB/m | graph read; rises to about 240 at 80 C | [S5] Fig. 3b | yes (graph) |
| Characteristic impedance of air | 428 | Pa s/m | about 413-428 depending on T | [S5] text | yes |
| Characteristic impedance of water | 1.5e6 | Pa s/m | - | [S5] text | yes |
| Granite (dry lab core) density | 2616 | kg/m3 | one lithology | [S6] | yes |
| Granite P / S velocity | 4610 / 2410 | m/s | SD 1310 / 210 | [S6] | yes |
| Granite Qp / Qs (0.1-1 MHz, dry, unconfined) | 14.2 +/- 4.4 / 12.2 +/- 1.1 | - | small cracked core; in-situ blocks probably higher | [S6] | yes |
| Granite P attenuation at 1 MHz | 48.1 | 1/m (Np/m; consistent with pi f /(Q v)) | - | [S6] | yes |
| Granite P attenuation at 40 kHz | 2.4-17 | dB/m | Q = 100 down to Q = 14, alpha = 8.686 pi f /(Q v) | derived from [S6, S7] | derived |
| King's Chamber granite, in-situ shear velocity | 3035 +/- 90 | m/s | mean of 45 blocks | [S8] | yes (abstract) |
| King's Chamber granite, ultrasonic echo penetration | about 3 | m | shear-wave array; frequency not stated in the record I read | [S8] | yes (abstract) |
| Dry rock 1/Q, typical | below 0.02 (Q above 50) | - | general statement, mainly sandstone data | [S7] | yes |
| Limestone Q (ultrasonic) | not found | - | - | - | - |
| Limestone (soft building stone) P velocity / density | 2315-2517 / 1580-1680 | m/s / kg/m3 | Sardinian stone, not Tura | [S9] | yes |
| Tura limestone velocity, density, Q | not found | - | I assume 3.7e6-1.3e7 Pa s/m impedance | - | no |
| Tura/Mokattam quarry limestone composition | 96-99 % calcite, 0.5-2.5 % quartz | wt % | pooled six quarry sites; single 1984 study by an author with a contested thesis on casing stones | [S10] | yes |
| Alpha-quartz piezoelectric constant e11 | 0.153 (PE-EMIS) to 0.175 (other methods) | C/m2 | 14 % spread among seven data sets | [S11] Table II | yes |
| Alpha-quartz c11(E), density, relative permittivity k11 | 86.7 GPa; 2647 kg/m3; 4.42 | - | - | [S11] | yes |
| Alpha-quartz d11 | about 1.8-2.3 | pm/V (= pC/N) | e11/c11 gives 1.8 (PE-EMIS) to 2.0 (older data sets); 2.3 is the handbook value recalled; 2.0 used in section 4 | derived from [S11] / memory | derived / no |
| Quartz electromechanical coupling k2 = e2/(c eps) | about 0.9 % | - | derived | derived from [S11] | derived |
| Granite apparent piezoelectric coefficient | 1.4e-15 | C/N | about three orders below single-crystal quartz; quasi-static stress-unloading test | [S12] | yes (abstract) |
| Cavitation hot spot | about 5000 K; about 1000 atm; above 1e10 K/s; under 1 microsecond | - | effective values | [S2, S3] | yes |
| Sonochemical working intensity | about 1 (baths); 10-500 (horn probes); 50 at 20 kHz in a cited experiment | W/cm2 | - | [S3] | yes |
| Cavitation threshold, water, 25 kHz | 2.5 (air-saturated tap) to 6.5 (degassed) | atm | Strasberg 1959 as cited | [S13] | yes (secondary) |
| Cavitation threshold, water, 60 kHz | 3.5-4.6 | atm | Blake 1949 as cited | [S13] | yes (secondary) |
| Same thresholds as plane-wave intensity p2/(2 rho c) | about 2-15 at 25 kHz | W/cm2 | my conversion; Suslick's 1 W/cm2 bath figure shows real systems cavitate lower | derived | derived |
| Best engineered airborne power ultrasound | up to 172 dB (10 W/cm2), 7-40 kHz, stepped-plate piezo transducers | - | focused field near the radiator | [S14] | yes |
| Air breakdown field (used as field ceiling) | about 3 | MV/m | recalled; not looked up this session | memory | no |

### 2.3 Aqueous ultrasound + SO2 / S(IV) literature (the "generous reading")

| study | frequency | power / intensity | finding | source | verified |
|---|---|---|---|---|---|
| Owusu & Adewuyi 2006, bubble column, NO + SO2 into water | 20 kHz | intensity varied (values not in abstract) | NO conversion 60-85 %; SO2 (52-4930 ppm) completely removed; sulfate pathways discussed | [S16] | yes (abstract) |
| Luo et al. 2021, US + sulfite | 20 kHz | 650 W | about 2.9-fold faster As(III) oxidation than ultrasound alone; sulfite radical formed by sonolysis | [S15] | yes (abstract) |
| Zhu et al. 2024, red-mud slurry scrubbing | 28 kHz | 0.4 W/cm2 | desulfurization kept above 95 % for 250 min; attributed to OH radicals from cavitation plus emulsification | [S17] | yes (abstract) |
| Liu et al. 2018, US/Fe2+/heat-activated persulfate | 28 kHz better than 40 kHz | power density varied | ultrasound helps NO; SO2 is completely removed in most systems tested even without it | [S18] | yes (abstract) |
| Wei et al. 2017, US-activated persulfate | not in abstract | - | persulfate dissociation about three orders faster than silent control; interface temperature about 340 K | [S19] | yes (abstract) |
| Chen et al. 2020, pilot spray column + ultrasonic wave | not in abstract | - | SO2, SO3 aerosol and fly-ash removal up by 8.7, 5.3 and 6.6 % (physical, in a wet column) | [S20] | yes (abstract) |
| Inoue et al. 2000, gas-solid catalysis on LiNbO3 | 3.5 MHz thickness resonance | not stated | ethylene selectivity 56 to 86 % (Ag), 31 to 97 % (Pd) in ethanol decomposition; reverts when switched off | [S21] | yes (abstract) |

### 2.4 Published acoustic or vibration observations inside the Great Pyramid

| observation | value | status | source | verified |
|---|---|---|---|---|
| King's Chamber swept-sine test (200 to 10 Hz, TEF analyser) | strong mode near 90 Hz; strong resonance near 30 Hz; low-frequency content from a few Hz to about 20 Hz; 16 Hz attributed to wind over the shafts | trade-magazine memoir, no data tables, accelerometer data unusable; **anecdotal** | [S24] | yes |
| King's Chamber impulse responses (2011) | decay tail of about 13 s (vendor description); equipment not stated | commercial product page; **not peer-reviewed** | [S25] | yes |
| King's Chamber resonance near 117 Hz or near 121 Hz | - | conference paper [S32] and J. S. Reid, both seen only as search snippets | [S32] | no |
| Comparative impulse-response study of several chambers (2026) | content unknown | conference paper; DOI resolves to a host that refused the fetch | [S33] | no |
| King's Chamber granite, ultrasonic shear-wave echo imaging | 3035 +/- 90 m/s; reflectors to about 3 m | **peer-reviewed** (Scientific Reports 2026); NDT, not room acoustics | [S8] | yes (abstract) |
| Whole-structure ambient vibration (HVSR, 37 points) | fundamental 2.0-2.6 Hz, mean about 2.3 Hz; soil about 0.6 Hz | **peer-reviewed** (Scientific Reports 2026); seismology | [S26] | yes (abstract) |
| Antechamber - any acoustic measurement | none found | - | - | - |
| Grand Gallery - any acoustic measurement | none found | - | - | - |
| Any ultrasonic airborne measurement anywhere in the pyramid | none found | - | - | - |
| Megalithic chambers (UK/Ireland), 95-120 Hz resonance | six sites, none Egyptian | peer-reviewed (JASA 1996); often mis-cited for the pyramid | [S27] | yes (abstract) |

Computed for orientation (rigid-wall axial modes, c = 343 m/s, f = c/2L): antechamber 58 Hz (length), 104 Hz (breadth), 45 Hz (height); King's Chamber 16.4 Hz, 32.8 Hz, 29.6 Hz. The King's Chamber values are consistent with Danley's reported resonance around 30 Hz and modes under 20 Hz [S24], which is weak support that the room behaves as an ordinary hard-walled rectangular cavity.

---

## 3. Claim-by-claim assessment

Verdict vocabulary: supported / partly supported / no evidence / contradicted / untestable / undefined by hypothesis.

**C1. Ultrasound from the granite converts SO2 and O2 gas to SO3 in the antechamber (the acoustic-catalyst claim).**
Verdict: **contradicted** (by the accepted mechanism), with **no evidence** found for the specific process.
Sonochemistry is a cavitation phenomenon and cavitation needs a liquid [S2, S3]. Ultrasound wavelengths (cm to tens of micrometres) are far larger than molecules, so sound does not couple to bonds directly [S3]. I found no peer-reviewed report of ultrasound driving a gas-phase oxidation without a liquid or an engineered catalyst surface. Section 4 shows the acoustic energy available per molecule is far below thermal energy even at the highest airborne levels ever engineered. Note also that a catalyst lowers an activation barrier without being an energy source; sound is an energy input, so the word catalyst is a loose label here.

**C2. The sonochemistry literature substantiates ultrasound as a driver of chemical reactions.**
Verdict: **partly supported**. True for liquids and liquid-solid slurries [S2, S3, S15-S19]; it does not transfer to a gas volume. The two papers shown on screen in the video are not identified in the transcript, so I could not check them individually.

**C3. There is real ultrasound-assisted SO2 / sulfite chemistry.**
Verdict: **supported, in water only**. Ultrasound at 20-40 kHz and roughly 0.4 W/cm2 upward generates OH and sulfite/sulfate radicals and improves gas-liquid mass transfer [S15-S19]. Two cautions for the simulation: enhancement factors are modest (about 3-fold in [S15]); and SO2 uptake is already complete in most absorbing liquids without ultrasound [S18], so ultrasound is not the rate-limiting need for SO2.

**C4. Granite in an electric field emits ultrasound by the inverse piezoelectric effect.**
Verdict: **partly supported** in principle, **undefined by hypothesis** in magnitude. Single-crystal quartz is piezoelectric (e11 about 0.15-0.17 C/m2 [S11]). In granite the grains are randomly oriented and the measured bulk coefficient is about 1.4e-15 C/N, three orders below quartz [S12]. Emission at ultrasonic frequency needs an alternating field at that frequency; a lightning stroke is a transient and telluric currents are quasi-static, and the transcripts name no oscillating source. The radio-frequency modelling paper cited in the video concerns electromagnetic wavelengths of hundreds of metres [S34, not opened]; it says nothing about acoustics.

**C5. The antechamber is widely reported to have the strongest acoustic properties in the pyramid.**
Verdict: **no evidence**. I found no measurement of the antechamber - peer-reviewed, trade or commercial. All located acoustic reports concern the King's Chamber [S24, S25].

**C6. The antechamber concentrates and amplifies ultrasound.**
Verdict: **contradicted by calculation** (no measurement exists either way). A passive room adds no energy. At 40 kHz air absorption alone (1.318 dB/m [S4]) gives an equivalent absorption area of about 22 m2 in an 18.5 m3 room, so the reverberant field is only about 3 dB above the free-field level 1 m from the same source (section 4.3). No focusing geometry is identified. At audible modal frequencies (45-104 Hz) ordinary resonant build-up would occur, but that is not ultrasound.

**C7. The em-piezo mechanism can supply chemically relevant ultrasonic intensity.**
Verdict: **undefined by hypothesis**; my bounded estimate says no by about 11 orders of magnitude (section 4.2-4.4).

**C8. The south-shaft blocking slab is Tura limestone.**
Verdict: **partly supported**. The Djedi/Pyramid Rover teams judged the slab and the last lining block to be a finer limestone, most likely Tura, on visual grounds [S28]. No laboratory analysis is reported.

**C9. Tura limestone has a much higher quartz content than Giza bedrock, making it a piezoelectric transducer.**
Verdict: **no evidence** for the comparison; **contradicted** for the transducer inference. The one compositional source I opened gives 0.5-2.5 % quartz and 96-99 % calcite for Tura/Mokattam quarry stone [S10]; I did not find a matched figure for Giza bedrock (this belongs to the materials brief). A few percent of randomly oriented quartz grains in a calcite matrix cannot give a larger bulk piezoelectric response than granite, which itself is about a thousand times weaker than quartz [S12]. No piezoelectric measurement on Tura limestone was found.

**C10. The copper pins draw the electric field into the slab.**
Verdict: **no evidence**. The fittings are judged copper from their colour, are bent down against the front face, and continue to the back; the investigating team regards them as handles or decoration [S28, S29]. They connect to no conductor, so they are not electrodes in a circuit. Whether they would enhance a quasi-static field locally is an electrostatics question for the EM brief.

**C11. Ultrasonic flow meters are non-invasive, like the sealed shaft.**
Verdict: **partly supported**. Clamp-on meters do stay outside the pipe, but they need transducers pressed onto the wall with couplant, a pipe full of liquid, and either two transducers bracketing an oblique path through the flow (transit-time) or scatterers in the liquid (Doppler) [S23]. None of these conditions maps onto a slab 63 m from the chamber behind an air column and an uncut wall.

**C12. The slab monitored liquid flow or level in the Queen's Chamber, with a receiver in the north shaft.**
Verdict: **contradicted** (link budget, section 4.5). Flow measurement is **undefined by hypothesis** (no conduit, no flow path, no time base). For level, a through-path from south slab to north slab loses at least 234-252 dB at 40 kHz and 100-118 dB at 13 kHz, against a source that I estimate at about 50-60 dB SPL. At most the arrangement behaves as a single-point switch that changes state when liquid reaches the shaft-mouth height.

**C13. Finding metal components in the north shaft would confirm the receiver.**
Verdict: **partly supported as an observation, not as an inference**. A pinned slab in the north shaft was already reported in 2002 [S28]. A matching pair is what a symmetric architectural or ritual feature would also show. The discriminating test is acoustic coupling to the chamber, not the presence of copper.

**C14. The Queen's Chamber shafts were never open to the chamber.**
Verdict: **supported**. Petrie records that both mouths were covered by stone left in the wall [S1]; they were opened in 1872 [S29].

**C15. Modern ultrasound machines work by applying voltage to a piezoelectric element.**
Verdict: **supported** (general statement; modern devices use poled ceramics with coupling far above quartz, driven by tuned electronics at a chosen frequency - which is the part the hypothesis leaves out).

---

## 4. Worked estimates

All arithmetic by hand; two or three significant figures.

### 4.1 What intensity would be needed

There is no documented threshold for an ultrasonic chemical effect in a dry gas, so I bound the problem three ways.

(a) *Adiabatic temperature swing in the gas.* For a sound wave, dT = T0 (gamma - 1)/gamma x (p'/p0); with T0 = 293 K, gamma = 1.4, p0 = 101 325 Pa, dT = 83.7 K x (p'/p0).

| level in air | p rms (Pa) | p peak (Pa) | dT peak (K) |
|---|---|---|---|
| 76 dB (estimate B below) | 0.128 | 0.181 | 1.5e-4 |
| 139 dB (estimate A below) | 183 | 258 | 0.21 |
| 172 dB (best engineered [S14]) | 7960 | 11 300 | 9.3 |

Time-averaged Arrhenius enhancement for a sinusoidal temperature swing is I0(x) with x = Ea dT /(R T0^2). Taking Ea = 100 kJ/mol as an illustrative barrier (assumption; the kinetics brief owns the real value): at 172 dB, x = 1.30 and I0 = 1.47; at 76 dB, x = 2e-5 and the enhancement is 1 + 1e-10. So even the strongest airborne ultrasound raises a room-temperature gas-phase rate by under 50 %, of a rate that is effectively zero.

(b) *Energy per molecule.* Energy density w = p_rms^2/(rho c^2). At 172 dB, w = 449 J/m3; with 2.50e25 molecules/m3 that is 1.8e-23 J = 1.1e-4 eV per molecule, about 0.4 % of kT (0.025 eV) and four orders below a typical bond-making barrier.

(c) *Cavitating a liquid film or droplets from the gas side* (the most charitable variant: wet walls or mist in the antechamber). Intensity transmission air to water is T = 4 Z1 Z2/(Z1 + Z2)^2 = 4 x 428/1.5e6 = 1.14e-3 (-29.4 dB) using impedances from [S5]. To deposit the 1 W/cm2 at which baths cavitate [S3] needs about 870 W/cm2 in the air, i.e. 189 dB. A sound wave whose pressure amplitude equals one atmosphere carries p^2/(2 rho c) = 1.2e7 W/m2 = 1200 W/cm2 (191 dB rms), so the requirement sits at the physical ceiling of airborne sound and 17 dB above the engineering record [S14].

**Requirement adopted for pass/fail: at least 189 dB (about 870 W/cm2) in the antechamber air for the wet-film variant; no finite requirement can be defined for the dry-gas variant.**

### 4.2 What the em-piezo mechanism could supply

Model: a slab of thickness L in a uniform field E across it. Inverse piezoelectric strain S = d E; surface displacement xi = d E L = d V. Surface velocity u = 2 pi f xi. Plane-wave radiation into air: p_rms = rho c u / sqrt(2), I = p_rms^2/(rho c), with rho c = 428 Pa s/m [S5].

Assumptions (all favourable to the hypothesis and flagged): field held at air breakdown, E = 3 MV/m (recalled value); field alternating at 40 kHz (no such source is proposed); slab = granite leaf, L = 0.40 m [S1], so V = 1.2 MV; quasi-static response.

| case | d (m/V) | xi (m) | u at 40 kHz (m/s) | p rms (Pa) | SPL (dB) | I (W/cm2) |
|---|---|---|---|---|---|---|
| A. Leaf treated as one perfectly oriented quartz crystal (absolute ceiling, not physical for granite) | 2.0e-12 (from e11/c11 [S11]) | 2.4e-6 | 0.60 | 183 | 139 | 7.8e-3 |
| B. Leaf with the measured granite coefficient | 1.4e-15 [S12] | 1.7e-9 | 4.2e-4 | 0.128 | 76 | 3.8e-9 |

Corrections not applied: (i) at 40 kHz the leaf is about 3.5 wavelengths thick (lambda = 4610/40 000 = 0.115 m [S6]), so a uniform field mostly cancels and the true off-resonance displacement is nearer d E lambda/(2 pi), about 27 dB lower; (ii) at a thickness resonance the response can rise by up to about 20 log10(Q), i.e. +23 dB for Q = 14 [S6] to +40 dB for Q = 100; the first thickness resonance of the leaf is near c/2L = 5.8 kHz, which is audible, not ultrasonic; (iii) the granite coefficient in [S12] is a quasi-static "apparent" value partly screened by charge migration with 1.5-4 s time constants, so the kHz value could differ. These leave case B within roughly 50-115 dB SPL. I carry 76 dB forward.

### 4.3 Room build-up in the antechamber at 40 kHz

Diffuse-field energy balance: w = 4P/(c A), with A = S alpha_wall + 4 m V. Energy attenuation coefficient m = 1.318/4.343 = 0.304 1/m [S4]; 4 m V = 4 x 0.304 x 18.5 = 22.5 m2. Wall term with an assumed alpha_wall = 0.02 on 44.7 m2: 0.9 m2. A = 23.4 m2 - air absorption dominates, so the result is insensitive to the wall finish.

- Mean free path 4V/S = 1.66 m; loss per traverse 2.2 dB from air alone.
- Room gain relative to free field at 1 m from the same source: (4/A)/(1/4 pi) = 0.171/0.0796 = 2.1, i.e. +3 dB. This is the entire concentration effect available at 40 kHz.
- Acoustic power needed to hold a level: P = w c A/4. For 160 dB (w = 28 J/m3): 57 kW. For 172 dB (w = 449 J/m3): 0.9 MW. (At these levels the wave is strongly nonlinear - shock-formation distance rho c^3/(beta omega p) is about 1.4 cm at 172 dB and 40 kHz with beta = 1.2 assumed - so linear estimates are optimistic.)
- Acoustic power supplied in case B: 3.8e-5 W/m2 over all 44.7 m2 of wall (generous) = 1.7e-3 W, giving a reverberant level of about 85 dB.

### 4.4 Comparison

| quantity | value |
|---|---|
| Supplied (case B, measured granite coefficient, breakdown-limited field, 40 kHz) | 76-85 dB SPL; 4e-9 to 3e-8 W/cm2; about 1e-4 to 2e-3 W acoustic |
| Supplied (case A, impossible single-crystal ceiling) | 139 dB; 8e-3 W/cm2 |
| Best engineered airborne source [S14] | 172 dB; 10 W/cm2 |
| Needed to cavitate a wet film from the gas side | about 189 dB; about 870 W/cm2 |
| Gap, case B to requirement | about 104-113 dB = 10 to 11 orders of magnitude in intensity |
| Gap, case A to requirement | about 50 dB = 5 orders |

### 4.5 Link budget for the "flow/level meter"

Path assumed from the transcript: south slab radiates down 63 m of air-filled 0.2 m shaft; crosses the stone left at the chamber wall (about 0.13 m, unverified); crosses the chamber (5.2 m N-S [S29]); crosses the stone at the north wall; travels up the north shaft (longer, with bends) to a second slab.

Interface transmissions (intensity), T = 4 Z1 Z2/(Z1 + Z2)^2:
- air to soft limestone (Z = 3.7e6-4.2e6 from [S9]): 4.1e-4 to 4.7e-4, i.e. -33 to -34 dB;
- air to dense stone (Z about 1.2e7-1.3e7; granite value from [S6], dense limestone assumed): 1.4e-4, i.e. -38.5 dB;
- limestone to water: 0.37 to 0.81, i.e. -4 to -1 dB.

Per stone barrier: about -35 to -43 dB if liquid stands against its chamber face; about -68 to -78 dB (frequency-averaged) if air is on both sides. A coherent half-wave plate resonance could recover up to roughly 20 dB at isolated frequencies for a low-loss plate; a 1D transfer-matrix run should resolve this.

| frequency | air absorption (dB/m) | two air legs, 2 x 63 m (dB) | two wet barriers (dB) | total, liquid at shaft-mouth height (dB) | total, chamber dry at that height (dB) |
|---|---|---|---|---|---|
| 13 kHz | about 0.25 | 32 | 70-86 | 100-118 | 168-188 |
| 20 kHz | 0.525 | 66 | 70-86 | 136-152 | 202-222 |
| 40 kHz | 1.318 | 166 | 70-86 | 236-252 | 302-322 |
| 100 kHz | 2-3.5 | 250-440 | 70-86 | 320-530 | - |
| 1 MHz | about 160 | about 20 000 | 70-86 | not meaningful | - |

Omitted (all make it worse): beam spreading across the chamber from a 0.2 m aperture, visco-thermal and roughness losses of a rough-walled multimode duct (the first cross mode cuts on at c/2a = 860 Hz; about 180 modes propagate at 13 kHz and 1700 at 40 kHz), the north-shaft bends, and both transduction efficiencies.

Source strength of the slab, same method as 4.2 with L = 0.06 m, V = 180 kV and the granite coefficient generously lent to limestone: xi = 2.5e-10 m; at 40 kHz u = 6.3e-5 m/s, 60 dB SPL; at 13 kHz 50 dB SPL. Received level: about -176 dB SPL at 40 kHz, about -50 dB SPL at 13 kHz. Both are far below any acoustic noise floor.

What real instruments need, for contrast: a 60 m ultrasonic level transducer runs at 13 kHz with a 5 degree beam, is driven at up to 250 V peak, is loud enough to carry a hearing-protection warning, and must look straight down an unobstructed air path at the liquid surface [S22]. Clamp-on flow meters use coupled transducer pairs on a full pipe [S23] and, by vendor listings seen only in search snippets, 0.5-2 MHz elements.

Information content: even with an ideal source and receiver, the through-signal depends on level only through the 66-70 dB step when liquid covers the shaft-mouth faces. That is a point-level switch, not a level gauge, and carries no flow information.

---

## 5. What a simulation of this domain needs

### 5.1 Governing equations

1. **Audio-band cavity acoustics (below about 0.5-1 kHz).** Helmholtz equation in the air volumes, del2 p + k^2 p = 0 with complex k = omega/c - i alpha(omega), alpha from ISO 9613-1; impedance or fully coupled elastic boundaries. Modal (eigenvalue) form for chamber resonances.
2. **Vibro-acoustics of the granite.** Linear elastodynamics rho u_tt = div sigma with complex moduli (Q), coupled to the air by continuity of normal velocity and traction.
3. **Piezoelectric source term.** T = cE S - e^T E; D = e S + eps E, with an *effective* e tensor for polycrystalline granite. Because the effective tensor is near zero for random fabric, treat it as a scanned parameter from 0 up to the single-crystal value, anchored at the measured 1.4e-15 C/N [S12]. The driving E(x, t) comes from the EM brief.
4. **Ultrasonic band (above about 10 kHz).** Do not mesh wavelengths. Use (a) the diffuse-field energy balance dW/dt = P - (c A / 4V) W with A = S alpha + 4 m V; (b) geometric ray/beam tracing with air absorption if spatial detail is wanted; (c) 1D transfer-matrix (layered-media) models for slab and wall transmission with complex wavenumbers; (d) multimode duct propagation with visco-thermal wall loss for the shafts.
5. **Nonlinear check.** Compare propagation distance with the shock-formation distance x_s = rho c^3/(beta omega p); if x_s is shorter than the room, linear results overestimate the field.
6. **Chemistry coupling.** Feed the acoustic temperature and pressure oscillation into the kinetics as k(T0 + dT sin(omega t)); the mean enhancement is I0(Ea dT / R T0^2). For any liquid phase present, compare the transmitted intensity with a cavitation threshold; only if it is exceeded does a sonochemical source term (radical yield per joule) switch on.

### 5.2 Solver choice

- A Helmholtz/modal FEM is the right tool for the audible chamber modes: the King's Chamber's first modes are 16-33 Hz and the antechamber's 45-104 Hz, well below the Schroeder frequency (about 2000 sqrt(T/V): roughly 400 Hz for the King's Chamber if the 13 s vendor decay figure is right, roughly 800 Hz for the antechamber with an assumed 3 s).
- The same FEM is the wrong tool at ultrasonic frequency. At 40 kHz lambda = 8.6 mm; six linear elements per wavelength in 18.5 m3 means 18.5/(1.43e-3)^3 = 6e9 elements for the antechamber alone (8e8 at 20 kHz). Use the energy and transfer-matrix models of 5.1 item 4, optionally with small 2D FEM patches to validate interface transmission.

### 5.3 Boundary and initial conditions

- Stone walls: near-rigid; normal-incidence absorption of order 0.01-0.05 (assumed; no in-situ data). Openings: the antechamber's passages to the Grand Gallery and King's Chamber (and whether the portcullis slabs are in place) set the radiation loss in the audio band.
- Air state: temperature, humidity and, importantly, gas composition. In the hypothesis the gas is an SO2/air mixture, possibly warm and humid; SO2 has its own vibrational relaxation absorption, so air values are a lower bound on attenuation (not quantified here).
- Source: surface normal velocity on granite faces from the piezoelectric model, or a parametric SPL sweep from 60 to 190 dB.
- Shaft link: source velocity on the slab face; lossy rough duct; layered barrier; chamber fill level as the scanned variable.

### 5.4 Key dimensionless numbers

| number | definition | value here |
|---|---|---|
| Helmholtz number | k L = 2 pi f L / c | about 2200 for L = 2.95 m at 40 kHz |
| Schroeder ratio | f / f_Schroeder | about 50-100 at 40 kHz (fully statistical) |
| Absorption per mean free path | alpha x 4V/S | 2.2 dB at 40 kHz |
| Impedance ratio | Z_air / Z_stone | 3.5e-5 (granite) to 1.2e-4 (soft limestone) |
| Electromechanical coupling | k2 = e2/(c eps) | 9e-3 for quartz; of order 1e-9 or less for granite if e scales by 1e-3 |
| Acoustic Mach number | u / c | 1.2e-6 (case B); 0.08 at 172 dB |
| Shock-formation ratio | room size / x_s | well below 1 for case B; about 200 at 172 dB |
| Arrhenius modulation | x = Ea dT /(R T0^2) | 2e-5 (case B); 1.3 at 172 dB |
| Mechanical quality factor | Q | 14 (lab granite) to above 50 (typical dry rock) |

### 5.5 Pass/fail criteria (pre-registered so the result can go either way)

1. **Acoustic catalyst, wet-film variant.** PASS if, for inputs inside the bounded ranges (granite e_eff up to the measured value times 10; field up to breakdown; any frequency 20 kHz-1 MHz; resonance allowed), the steady-state SPL in the antechamber gas reaches 189 dB or the intensity transmitted into a liquid film reaches a cavitation threshold of 1 W/cm2. FAIL otherwise. Hand estimate: 76-85 dB, failing by more than 100 dB.
2. **Acoustic catalyst, dry-gas variant.** PASS if the time-averaged Arrhenius enhancement I0(x) reaches 2 for the kinetics brief's SO2 oxidation barrier (requires dT of roughly 12 K or more, about 174 dB). FAIL otherwise. Report the enhancement actually obtained.
3. **Concentration and amplification.** Compute room gain (antechamber level minus free-field level at 1 m for the same source power) from 20 to 100 kHz. PASS if at least 20 dB somewhere in the ultrasonic band; hand estimate is about 3 dB at 40 kHz.
4. **Strongest acoustics of any chamber.** Audio-band FEM: compare modal Q and decay time of antechamber, King's Chamber and Grand Gallery. This is a ranking, and can only be validated against field impulse responses, which do not exist publicly for the antechamber.
5. **Flow/level meter.** PASS if the through-path signal-to-noise ratio at the north slab is at least 10 dB with the bounded source, and the received signal varies monotonically with liquid level over a useful range. Hand estimate: fails by more than 150 dB at 40 kHz and more than 100 dB at 13 kHz; level response is a single step.
6. **Sanity benchmark.** The audio model should reproduce King's Chamber modes near 16, 30 and 33 Hz and the reported strong response near 30 and 90 Hz [S24]; the ultrasonic energy model should reproduce Table 2 of [S4] in a test box.

---

## 6. Open questions

1. **Frequency, field strength and waveform are not defined by the hypothesis.** Without an oscillating drive at ultrasonic frequency the inverse piezoelectric effect produces a static strain, not sound. The EM brief should state the spectral content of lightning-induced fields inside the masonry and whether anything above 20 kHz survives.
2. **Bishop 1981 (Tectonophysics 77:297-321) and Tuck, Stacey & Starkey 1977 (Tectonophysics 39:T7-T11)** on piezoelectric fabric in quartz-bearing rocks were not opened (paywalled); only bibliographic details were seen. They bound how far above 1.4e-15 C/N an Aswan granite with preferred quartz orientation could go. No piezoelectric measurement on Aswan granite or Tura limestone was found.
3. **Quartz content of Tura limestone versus Giza bedrock** - only one pooled figure found [S10]; no matched pair. Passed to the materials brief.
4. **Ultrasonic Q of limestone and of Aswan granite in situ** - not found. The laboratory granite Q of 14 [S6] is probably pessimistic for metre-scale blocks; the [S8] full text (frequency used, signal-to-noise) would calibrate it.
5. **Thickness of stone originally left at the Queen's Chamber shaft mouths and the height of the mouths above the floor** - Petrie does not give the thickness; the 5 inch figure is from a search snippet of an 1878 periodical. Gantenbrink's own survey pages were not reached.
6. **Richardson et al. 2013 (J. Field Robotics 30:323-348, DOI 10.1002/rob.21451)** returned HTTP 403; slab thickness, pin geometry and the exact distance are therefore from a team member's web write-up [S28] and search snippets.
7. **EVA London 2026 impulse-response paper [S33] and EVA 2023 paper [S32]** could not be opened. If [S33] contains impulse responses for the antechamber it would be the first measurement and should replace my computed modes.
8. **Which sonochemistry papers are shown in the video** (including the one said to describe the field as a black art) - not identifiable from the transcripts.
9. **Absorption of ultrasound in SO2/air/H2O mixtures at the hypothesised temperature** - not searched; expected to exceed air values.
10. **Non-cavitational sonochemistry.** A 2019 discussion paper by Vinatoru and Mason asks whether sonochemistry can occur without cavitation; I saw only a search summary [S35]. It concerns liquids, but the simulation team should read it before closing the question.
11. **Air breakdown field and the nonlinearity coefficient of air** were used from memory and should be sourced.
12. **Is a liquid phase present in the antechamber in the hypothesis?** The transcripts describe gas only, with water confined to the Grand Gallery side. If the modellers wish to test the wet-film variant they are extending the hypothesis, and should say so.

---

## 7. Sources

Opened and read this session unless marked otherwise.

- [S1] W. M. F. Petrie, *The Pyramids and Temples of Gizeh* (1883), ch. 7, sections 44, 48-56. https://www.ronaldbirdsall.com/gizeh/petrie/c7.html
- [S2] K. S. Suslick research group, "Sonochemistry" overview page, University of Illinois. https://suslick.scs.illinois.edu/sonochemistry.html
- [S3] K. S. Suslick, "The Chemistry of Ultrasound" (Encyclopaedia Britannica yearbook article, hosted by the author). https://suslick.scs.illinois.edu/sonochembrittanica.html
- [S4] A. Dobrucki, B. Zoltogorski, P. Pruchnicki, R. Bolejko, "Sound-absorbing and insulating enclosures for ultrasonic range", *Archives of Acoustics* 35(2):157-164 (2010), Table 2. https://acoustics.ippt.pan.pl/index.php/aa/article/download/240/230
- [S5] A. Vladisauskas, L. Jakevicius, "Absorption of ultrasonic waves in air", *Ultragarsas* 50(1):46-49 (2004). DOI 10.5755/j01.u.50.1.8278. https://www.ultragarsas.ktu.lt/index.php/USnd/article/view/8278
- [S6] W. A. M. Wanniarachchi et al., "Assessment of dynamic material properties of intact rocks using seismic wave attenuation: an experimental study", *R. Soc. Open Sci.* 4:170896 (2017). DOI 10.1098/rsos.170896. https://pmc.ncbi.nlm.nih.gov/articles/PMC5666273/
- [S7] N. Tisato, C. Madonna, E. H. Saenger, "Attenuation of seismic waves in partially saturated Berea sandstone as a function of frequency and confining pressure", *Front. Earth Sci.* 9:641177 (2021). DOI 10.3389/feart.2021.641177
- [S8] B. Maier et al., "Investigation of the lower block rows in the King's Chamber of the Great Pyramid using ultrasonic testing with shear wave arrays", *Scientific Reports* 16 (2026). DOI 10.1038/s41598-026-54151-6. Abstract and metadata read at https://pdxscholar.library.pdx.edu/cengin_fac/768 (publisher page redirected to a login).
- [S9] G. Concu, B. De Nicolo, M. Valdes, "Prediction of building limestone physical and mechanical properties by means of ultrasonic P-wave velocity", *Sci. World J.* 2014:508073. DOI 10.1155/2014/508073
- [S10] J. Davidovits, "X-ray analysis and X-ray diffraction of casing stones from the pyramids of Egypt, and the limestone of the associated quarries", *Science in Egyptology* symposia, Manchester (1984), pp. 511-520; author's summary page. https://geopolymer.org/library/archaeological-papers/a-x-ray-analysis-pyramids-casing-stones-and-their-limestone-quarries
- [S11] M. Xie, W. Bai, F. Li, "Elastic, piezoelectric coefficients, and internal frictions of a single alpha-quartz crystal determined by partial-electrode electromechanical impedance spectroscopy", arXiv:2212.00284 (2022), Table II. https://arxiv.org/abs/2212.00284
- [S12] H. Sasaoka, C. Yamanaka, M. Ikeya, "Measurements of electric potential variation by piezoelectricity of granite", *Geophys. Res. Lett.* 25 (1998). DOI 10.1029/98GL51179. Abstract read at https://earthref.org/ERR/18137/
- [S13] G. Viciconte, P. Guida, T. Truscott, W. L. Roberts, "Towards a general description of the cavitation threshold in acoustic systems", arXiv:2311.13425v2 (2024). https://arxiv.org/html/2311.13425v2
- [S14] J. A. Gallego-Juarez et al., "Advances in the development of power ultrasonic technologies based on the stepped plate transducers", Ultrasonic Industry Association 36th Symposium (2007), slides. https://ultrasonics.org/aws/UIA/asset_manager/get_file/Gallego_2007_UIA.pdf?ver=9716
- [S15] T. Luo et al., "Strengthening arsenite oxidation in water using metal-free ultrasonic activation of sulfite", *Chemosphere* (2021). DOI 10.1016/j.chemosphere.2021.130860 (abstract).
- [S16] S. O. Owusu, Y. G. Adewuyi, "Sonochemical removal of nitric oxide from flue gases", *Ind. Eng. Chem. Res.* (2006). DOI 10.1021/ie0509692 (abstract).
- [S17] H. Zhu et al., "Ultrasonic-enhanced phosphorus sludge excited O3 coupled red mud simultaneous desulfurization and denitrification", *Arabian J. Chem.* (2024). DOI 10.1016/j.arabjc.2024.105728 (abstract).
- [S18] Y. Liu et al., "Simultaneous absorption of SO2 and NO from flue gas using ultrasound/Fe2+/heat coactivated persulfate system", *J. Hazard. Mater.* (2018). DOI 10.1016/j.jhazmat.2017.08.042 (abstract).
- [S19] Z. Wei et al., "Kinetics and mechanism of ultrasonic activation of persulfate: an in situ EPR spin trapping study", *Environ. Sci. Technol.* (2017). DOI 10.1021/acs.est.6b05392 (abstract).
- [S20] Z. Chen et al., "Experimental investigation on the synergetic removal of SO3, SO2, and particulate matter in a gas-liquid flow pattern-controlling column coupled with ultrasonic wave", *Ind. Eng. Chem. Res.* (2020). DOI 10.1021/acs.iecr.9b06033 (abstract).
- [S21] Y. Inoue, Y. Yukawa, N. Saito, H. Nishiyama, "Artificial control of catalytic functions for reaction selectivity by thickness-extensional mode resonance oscillation of acoustic wave", AVS 47th International Symposium (2000), abstract SS1-TuA3. https://www2.avs.org/symposium2000/Papers/Paper_SS1-TuA3.html
- [S22] Siemens Milltronics, *Echomax XLT Operation Manual* 7ML19985QS81 (2004), specifications and mounting pages. https://www.rshydro.co.uk/PDFs/Siemens/XLT%20manual.pdf
- [S23] Fuji Electric France, "Doppler flow meter vs transit time flow meter" (vendor technical article). https://www.fujielectric.fr/en/blog/doppler-flow-meter-vs-transit-time-flow-meter-comparing-ultrasonic-flow-meters-for-optimal-performance/
- [S24] T. Danley, "The Great Pyramid: early reflections and ancient echoes", ProSoundWeb (2024 repost of *Live Sound International*, July/August 2000), pages 1, 2, 4. https://www.prosoundweb.com/the-great-pyramid-early-reflections-ancient-echoes/
- [S25] Audio Ease, Altiverb venue page "Great Pyramid of Giza" (impulse responses recorded May 2011). https://audioease.com/IR/VenuePages/giza.html
- [S26] M. A. El-Gabry et al., "Architectural and geotechnical aspects affecting earthquake resilience for the antique Egyptian Khufu pyramid", *Scientific Reports* (2026). DOI 10.1038/s41598-026-49962-6 (abstract).
- [S27] R. G. Jahn, P. Devereux, M. Ibison, "Acoustical resonances of assorted ancient structures", *J. Acoust. Soc. Am.* (1996). DOI 10.1121/1.414642 (abstract).
- [S28] R. Richardson, Djedi project case-study page, Real Robotics, University of Leeds (2020; based on interviews with the project manager and the mission report). https://www.realrobotics.co.uk/?p=41
- [S29] Wikipedia, "Great Pyramid of Giza", interior sections (secondary; cites Maragioglio & Rinaldi, Gantenbrink, Djedi Project, National Geographic). https://en.wikipedia.org/wiki/Great_Pyramid_of_Giza
- [S30] Wikipedia, "Djedi Project" (used only for the citation of Richardson et al. 2013, *J. Field Robotics* 30(3):323-348, DOI 10.1002/rob.21451; the paper itself returned HTTP 403). https://en.wikipedia.org/wiki/Djedi_Project
- [S31] Ancient Egypt Online, "Great Pyramid: Queen's Chamber" (secondary). https://ancientegyptonline.co.uk/queenschambergp/
- [S32] C. H. Smith, T. Middleton, J. Crossley, "The intentional use of sound design in the Egyptian temples and the Great Pyramid", EVA London 2023. DOI 10.14236/ewic/EVA2023.47. **Not opened (HTTP 403); search snippet only.**
- [S33] C. H. Smith et al., "Resonant Chambers: comparative impulse-response study inside the Great Pyramid of Khufu", EVA London 2026. DOI 10.14236/ewic/eva2026.35. **Not opened (HTTP 403); title from index listing only.**
- [S34] M. Balezin, K. V. Baryshnikova, P. Kapitanova, A. B. Evlyukhin, "Electromagnetic properties of the Great Pyramid: first multipole resonances and energy concentration", *J. Appl. Phys.* 124:034903 (2018). DOI 10.1063/1.5026556. **Abstract seen in search summary only.**
- [S35] M. Vinatoru, T. J. Mason, "Can sonochemistry take place in the absence of cavitation? - A complementary view of how ultrasound can interact with materials" (2019). **Search summary only.** https://pureportal.coventry.ac.uk/en/publications/can-sonochemistry-take-place-in-the-absence-of-cavitation-a-compl/
- [S36] Local transcripts: `/Users/aeroshariati/Pyramid/youtube-transcript/history-drops/incredible-new-evidence-reveals-the-great-pyramids-true-purpose-podcast-pyramid-history-ancient/transcript.md` (Part 1), `.../incredible-new-evidence-reveals-the-great-pyramids-true-purpose-podcast-science-history-ancient/transcript.md` (Part 2), `/Users/aeroshariati/Pyramid/youtube-transcript/danny-jones/new-scans-expose-an-unfortunate-secret-under-the-pyramids-geoffrey-drumm/transcript.md` (full episode, 00:37-01:24).

Searched without a usable result: any peer-reviewed gas-phase (liquid-free) sonochemical oxidation; any acoustic measurement of the antechamber or Grand Gallery; Toksoz, Johnston & Timur 1979 Q tables (bibliographic details only); ISO 9613-1 text (standard is paywalled; values taken from [S4, S5]).
