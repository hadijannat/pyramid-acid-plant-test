# 04 - Electromagnetics, lightning, telluric currents and piezoelectricity

Domain: the "electricity" part of Geoffrey Drumm's Land of Chem hypothesis for the Great Pyramid.
Compiled 2026-10-09/10. Every number carries a source tag [n] (see Sources) and a verified flag.
"verified = yes" means I read that figure in the cited source during this session. "no" means it comes from memory or from a search-result snippet of a page I could not open, and says which.

**Second review, 2026-10-10.** An independent verification pass re-opened the load-bearing sources and redid the arithmetic. Corrections are marked inline as "[V: ...]" with the old value kept in a "was:" note; the full check list is in the section "Verification pass (2026-10-10)" at the end. First-pass text has not been deleted.

---

## 1. Summary

**What the transcript claims** (full episode, 00:58:48 to 01:14:09 and 01:15:50 to 01:37:19): a 2018 Journal of Applied Physics paper is presented as proof that the pyramid concentrates electric field around the King's Chamber when energy arrives from above and at a flat, capstone-free top when it arrives from below, and therefore as substantiation of a two-source power system: telluric currents from below and lightning from above. The charged top is said to attract negative cloud-to-ground lightning; limestone (dielectric constant 7) and red granite (9) are said to store the field like a capacitor; the field is said to drive the inverse piezoelectric effect in the granite, giving ultrasound that catalyses SO2 to SO3; Tura limestone is said to be quartz-rich, making the "Gantenbrink door" an ultrasonic transducer; iron-oxide veins are wiring and electrolyte-filled boat pits are circuit breakers.

**What I found.**

1. **The paper is real and I read it in full [1].** Balezin, Baryshnikova, Kapitanova and Evlyukhin modelled plane-wave scattering at wavelengths of 200 to 600 m (0.5 to 1.5 MHz) by a homogeneous, weakly lossy dielectric pyramid (permittivity 5 + 0.1i, not 7), in free space and on a substrate of the same material. It reports dipole and quadrupole resonances, a modest field enhancement in the chambers (box-shaped voids, presumably air-filled; the paper does not state their permittivity), and scattering of energy into the substrate under the base. It contains no lightning, no telluric currents, no static charge, no capstone or truncated top, no granite and no piezoelectricity. Its stated aims include removing unfounded speculation about the pyramid's electromagnetic properties. The "from below" case exists only for a pyramid floating in free space; with a ground present only incidence from above was modelled.
2. **A resonance at 0.5 to 1.5 MHz says nothing about quasi-static inputs.** Resonance requires the wavelength to be comparable with the object. Telluric variations have periods of seconds to days (free-space wavelengths of 10^5 km and up) and a thunderstorm's field changes over seconds. At those frequencies the rock behaves as a leaky conductor (charge relaxation time of nanoseconds to milliseconds), the interior field is screened rather than concentrated, and no multipole resonance exists. The governing physics changes from wave scattering to current continuity.
3. **The paper's own low-loss assumption is probably optimistic.** In-situ electrical resistivity tomography on the Great Pyramid's north face gives 300 to 1500 ohm m for the limestone [16]. At 1 MHz that corresponds to an imaginary permittivity of roughly 13 to 67, against the 0.1 assumed in [1] (my calculation, section 4.2). If the bulk is anywhere near the measured surface values the skin depth is 10 to 26 m and the resonances would be heavily damped. This is the single most important sensitivity for a replication. [V: "probably optimistic" is too soft. A second, independent in-situ dataset exists: the 1974 SRI / Ain Shams radio-sounding campaign measured one-way losses of about 6 dB/m at 10 MHz rising to about 25 dB/m at 150 MHz in Giza limestone, with an in-situ dielectric constant of about 8.8 at 50 MHz and about 83 percent relative humidity inside the Menkaure pyramid [31]. That corresponds to a conductivity of about 0.016 S/m at 10 MHz (my calculation, check V4), an imaginary permittivity of roughly 200 to 300 at 1 MHz if the conductivity holds, and a skin depth of 4 to 5 m. Both datasets put the loss two to three and a half orders of magnitude above the paper's 0.1.]
4. **Lightning is rare at Giza.** Egypt has the lowest national-average flash density in Africa, 0.2 flashes per km2 per year of total lightning [9]. With the standard collection-area method the original 146.6 m pyramid has a collection area of about 1.07 km2, so the expected direct-strike rate is of order 0.05 to 0.5 per year (one strike every 2 to 20 years) (section 4.4). A value specific to the Giza grid cell was not found. [V: corrected. The 1.07 km2 figure applies the rectangular-block formula, which assumes a flat roof at full height over the whole footprint. Applying the same 1:3 slope rule to the actual pyramid shape gives a circle of radius 3H, about 0.61 km2 (was: 1.07 km2), so the expected rate is about 0.03 to 0.3 per year, one strike every 3 to 30 years (was: 0.05 to 0.5 per year, every 2 to 20 years). The Giza grid-cell flash density is still not found; see check V7.]
5. **Telluric driving voltages are tiny.** Even the 100-year extreme geoelectric field at high latitude with resistive ground is about 20 V/km, and an order of magnitude less below about 50 degrees geomagnetic latitude [12]. Across the 230 m base that is at most a few volts in the worst case on Earth and millivolts normally.
6. **Granite is a very poor piezoelectric.** Single-crystal quartz has d11 = 2.3 pC/N [5][6]. Measured granite is about 1.4e-15 C/N, three orders of magnitude lower [4]; classic studies found granite responses no larger than the statistical residue of randomly oriented grains [2][3]; the largest value reported for any quartz-rich rock (a vein quartz with strong fabric) is 7 percent of single-crystal [7][8]. Using these, the surface displacement from a lightning-driven field of about 1 kV/m is of order a picometre, and the radiated acoustic intensity in gas is 11 to 15 orders of magnitude below the 1 to 10 W/cm2 used for cavitation-based sonochemistry [18] (section 4.6). Reaching 1 W/cm2 in air from 1 m of granite would need about 4e10 V/m, some four orders above air breakdown. [V: two corrections. (i) "The largest value reported for any quartz-rich rock is 7 percent of single-crystal" is wrong as written: an atomic-force-microscope study of the converse effect reports an apparent coefficient of about 7.0e-13 C/N for a granite sample, about 30 percent of quartz d11 and 500 times the 1.4e-15 C/N bulk value [32]. The abstract does not say whether the probe sat on a single quartz grain; a local-probe value should not be read as a bulk coefficient, but it is the upper published number and is the converse effect, which is what the hypothesis needs. (ii) With that coefficient the shortfall in scenario 1 is about 9 orders, so the range is 9 to 15 orders (was: 11 to 15). The verdict does not change. Intensity scales as the square of the field: each factor of 10 in field is two orders of intensity.]
7. **Tura limestone is not quartz-rich.** X-ray analysis of Tura and Mokattam quarry samples gives 96 to 99 percent calcite and 0.5 to 2.5 percent quartz [17]. [V: figures re-read and confirmed on the source page, but this is one dataset from an author with a stake in the cast-stone debate, and no independent quantitative petrography was opened in either pass. Read the statement as "the only quantitative source found says not quartz-rich".]

**What supports the hypothesis, stated fairly.** (a) The paper does show field enhancement in the chambers for incidence from above and at the upper flanks for incidence from below, exactly as the figures were described. (b) Permittivity values of 7 (dry limestone) and up to 9 or more (Aswan granite at low frequency) are within measured ranges [13][14]. (c) Quartz-bearing rocks do show a small, real piezoelectric response [2][4], and converse-piezoelectric actuation of granite by high-voltage, high-frequency alternating current is an active research topic with some experimental weakening reported [20][21]. (d) Lightning does strike tall structures preferentially, and upward leaders from tall objects are well documented [10]. None of these closes the quantitative gap in point 6. [V: further points in favour found in the second pass. (e) For the wave from the base side the paper's own text says the electric field concentrates in the apex region at all wavelengths, so that part of the speaker's description matches the authors' words (free-space model only). (f) Piezoelectric responses of quartz bodies have been detected at field scale: seismic shots produced electric signals from quartz veins and massive quartz at distances of tens of metres [34][35][36][41], and consistent polarity along a vein indicates a large-scale piezoelectric fabric [37]. These are quartz veins with fabric, the direct effect, and microvolt-level signals; none concerns granite or the converse effect. (g) Lightning fields do reach into rock: coupling through mine overburden has been measured and modelled [38][40], and one 2026 borehole study reports small seismic events at 50 to 140 m depth immediately after a ground flash [39]. (h) A converse-effect coefficient of 7e-13 C/N has been reported for granite at the microscope scale [32]. (i) The in-situ dielectric constant of Giza pyramid limestone at 50 MHz is about 8.8 [31], so the speaker's 7 is at least as defensible as the paper's 5.]

---

## 2. Parameters

| Name | Value | Unit | Uncertainty / range | Source | Verified |
|---|---|---|---|---|---|
| **Balezin et al. 2018 model** | | | | | |
| Wavelength range modelled | 200 to 600 | m | equals 0.50 to 1.50 MHz (my conversion) | [1] | yes |
| Pyramid permittivity used | 5 + 0.1i | - | authors cite literature range 4 to 6; no Giza samples measured | [1] | yes |
| Model height / base side | 138.75 / 230 | m | pointed apex, no truncation, no capstone feature | [1] | yes |
| "King's Chamber" in model | 11 x 5 x 11 | m | centre 5 m off axis, 40.5 m above base; real chamber is about 10.5 x 5.2 x 5.8 m (memory, not verified) | [1] | yes (model) |
| "Queen's Chamber" in model | 5 x 5 x 6 | m | centre 2.5 m off axis, 20.8 m above base | [1] | yes |
| Subterranean chamber in model | 5.2 x 5.6 x 4.6 | m | 2.4 m off axis, 29.8 m below base | [1] | yes |
| Excitation | linearly polarised plane wave along the axis, incident field 1 V/m | - | from apex side and from base side in free space; from above only on substrate | [1] | yes |
| Resonances, free space | about 333 and about 230 | m | extinction cross-section about 0.09 and 0.13 km2 (read from Fig. 1) | [1] | yes |
| Resonance, on substrate | one broad maximum near 250 | m | about 0.12 km2 (read from Fig. 5b) | [1] | yes |
| Peak normalised E intensity in King's Chamber, free space | wave from apex side (k antiparallel to z, solid red): about 35 at 200 m, about 20 near 230 m, about 10 at 250 m, about 3.5 to 4 from 290 to 600 m; wave from base side (k parallel to z, green dash-dot): about 12 at 200 m, minimum about 4.5 to 5 near 260 m, peak about 16 near 355 m, about 4.5 at 600 m; the two curves cross near 270 m | - | [V: corrected after re-reading Fig. 4 at about 4x magnification; was: "apex side about 35 at 200 m, about 3 to 5 above 250 m; base side about 7 to 16"]. Read by eye, about +/-1 unit and +/-10 m; amplitude factor up to about 5.9 | [1] | yes (graph reading, magnified) |
| Peak normalised E intensity in chambers, on substrate | E: King's about 3.2 to 4.6 (peak near 295 m); Queen's about 2.7 to 4.7 (peak near 285 m); under-base chamber about 2.3 to 6.0 (highest at 200 m). H: about 1.6 to 5.7, 2.1 to 6.2 and 3.9 to 7.9 respectively | - | [V: refined after magnified re-read of Fig. 7(b)-(d), which is a low-resolution raster; was: "about 3 to 6", amplitude factor 1.7 to 2.4]. E amplitude factor about 1.5 to 2.4 | [1] | yes (graph reading, magnified) |
| Solvers used by authors | CST Microwave Studio, COMSOL Multiphysics, discrete dipole approximation | - | all three reported to agree | [1] | yes |
| Equivalent conductivity of the paper's loss term | 2.8e-6 to 8.3e-6 | S/m | from sigma = omega eps0 eps''; equals 1.2e5 to 3.6e5 ohm m | derived from [1] | calculation |
| **Rock electrical properties** | | | | | |
| Limestone relative permittivity (100 MHz) | 4 to 8; dry 7; wet 8 | - | compilation values | [13] | yes |
| Granite relative permittivity (100 MHz) | 4 to 6; dry 5; wet 7 | - | compilation values | [13] | yes |
| Aswan granite relative permittivity | 24 down to 3.5 | - | 100 Hz to 10 MHz; strong dispersion below about 10 kHz | [14] | yes (abstract page) |
| Aswan granite conductivity | 1e-8 to 1e-4 | S/m | same frequency range; moisture state not stated on the page | [14] | yes (abstract page) |
| Great Pyramid limestone resistivity, in situ (ERT, north face Chevron) | 300 to 1500; 80 to 300 in the first metre | ohm m | DC, electrodes wetted with fresh water; samples outer few metres only. [V: re-read and confirmed; depth of investigation is about 2 m, not "a few metres"; coupling was a fresh-water-soaked sponge behind 0.2 m steel-mesh electrodes at 0.75 m spacing; the authors' forward model used 500 ohm m for limestone] | [16] | yes |
| Giza limestone RF attenuation, in situ (Menkaure pyramid corridors; Khafre boat-pit roof) | about 6 at 10 to 11 MHz; about 12 at 28 to 36 MHz; 14.75 at 50 MHz; 18.2 at 125 MHz; about 25 at 150 MHz | dB/m, one-way | [V: new row]. Roughly proportional to the square root of frequency; laboratory samples matched only when held near 80 percent relative humidity; no transmission detected through 32 m of bedrock at 10 MHz | [31] | yes (fetch summary of the report's web copy) |
| Giza pyramid limestone dielectric constant, in situ | about 8.8 | - | [V: new row]. From propagation velocity 0.338 c at 50 MHz, Menkaure pyramid; interior relative humidity about 83 percent | [31] | yes (same) |
| Conductivity implied by the RF attenuation | about 0.016 at 10 MHz; 0.03 to 0.05 at 50 to 150 MHz | S/m | [V: new row]. General lossy-medium formula with eps' = 8.77; equals about 60 ohm m at 10 MHz; my calculation (check V4) | derived from [31] | calculation |
| Generic limestone resistivity | porous 100 to 1000; dense 1e3 to 1e6 | ohm m | compilation | [15] | yes |
| Generic igneous rock resistivity | 100 to 1e6 | ohm m | compilation; granite dry values can be far higher | [15] | yes |
| Effect of water on granite resistivity | one monolayer: about x10 lower; several wt percent free water: up to 9 orders lower | - | laboratory | [22] | yes (abstract) |
| Charge relaxation time, limestone | 2e-8 to 9e-8 (300 to 1500 ohm m); up to 6e-5 (1e6 ohm m) | s | tau = eps0 epsr rho, epsr = 7. [V: recomputed, confirmed: 1.9e-8, 9.3e-8, 6.2e-5 s. Lower end is 4e-9 to 5e-9 s for the 60 to 80 ohm m values of [16] (first metre) and [31]] | derived from [13][15][16] | calculation (re-derived) |
| Charge relaxation time, Aswan granite | 5e-7 to 5e-3 | s | epsr = 6, sigma 1e-4 to 1e-8 S/m. [V: recomputed, confirmed. With the low-frequency permittivity of 24 from [14] the upper end is 2e-2 s, so quote 5e-7 to 2e-2 s; still far shorter than a storm's field evolution] | derived from [14] | calculation (re-derived) |
| **Lightning** | | | | | |
| Egypt mean total flash density (IC + CG) | 0.2 | km^-2 yr^-1 | national mean, lowest in Africa; Giza cell value not found. [V: abstract re-read, confirmed: 10 years of data from two satellite detectors. Giza-cell value searched for again and not found in any text source; it must be read from the gridded files, which were not downloaded. Do not treat 0.2 as the Giza value] | [9] | yes (abstract; re-read) |
| Global context: peak annual flash density | 160 | km^-2 yr^-1 | eastern Congo, 0.5 degree grid | [23] | yes (abstract) |
| Thunderstorm days at Cairo | not found | d/yr | open question | - | - |
| Ng from thunder days | Ng approx 0.1 Td | km^-2 yr^-1 | derived for moderate climates | [10][11] | yes |
| Collection area formula | Ad = L W + 2(3H)(L + W) + pi (3H)^2; Nd = Ng Ad Cd 1e-6 | m2; yr^-1 | IEC 62305-2 method as reproduced in a manufacturer guide; pi restored by the fetch tool | [11] | yes (secondary copy) |
| Collection area, original pyramid (230.3 m, 146.6 m) | 6.1e5 [V: corrected; was: 1.07e6] | m2 | [V: the rectangular-block formula gives 1.066e6 m2 and is an upper bound for a flat-roofed block. For a pyramid the 1:3 slope line from the apex reaches 3H = 440 m and encloses every lower point (corner half-diagonal 163 m is less than 3H), so Ad = pi (3H)^2 = 6.08e5 m2; 5.44e5 m2 for today's 138.75 m.] Pyramid dimensions from memory; the standard's own complex-shape rule (Ad' = pi (3 Hp)^2) was seen only in a search snippet of a secondary copy | derived from [11] | calculation (re-derived) |
| Expected direct strikes | about 0.03 to 0.3 [V: corrected; was: about 0.05 to 0.5] | yr^-1 | Ng(CG) 0.05 to 0.5, Cd 1; x2 if hilltop factor Cd = 2 is applied. [V: with the national mean 0.2 total flashes and a cloud-to-ground share of about one third (IC:CG ratio about 2, measured for Australia [42], not Egypt), Ng is about 0.07 and Nd about 0.04 per year, one strike in about 23 years. Giza-cell Ng still unverified] | derived from [9][11] | calculation (re-derived) |
| Median first negative return-stroke peak current | about 30 | kA | subsequent strokes about 12 kA; first-stroke charge about 5 C. [V: still not confirmed in an opened source. A second search again returned 30 kA and 12 kA quoted from TB 549 text, but the two pages I opened (the conference abstract of the brochure and [10]) do not state them; [10] gives a 10 kA median for a sensitive location network, which is a different quantity] | [24] search snippets of CIGRE TB 549 summaries | no (snippet, two independent searches agree) |
| Design maximum, protection level I | 200 kA; 100 C short-stroke charge; 300 C flash charge; 10 MJ/ohm; 10/350 microsecond | - | upper-bound design values, not typical | [10] | yes |
| Strike points per CG flash | 1.5 to 1.7 | - | | [10] | yes |
| Height above which upward flashes become important | about 100 | m | negative downward flashes typical for shorter structures | [10] | yes |
| Soil ionisation critical gradient | 0.3 to 1 (CIGRE reference 0.4) | MV/m | for soil; rock value not found | search snippet | no (snippet) |
| **Telluric / geoelectric field** | | | | | |
| 100-year extreme, high latitude, resistive ground | about 20 | V/km | 10 s peak; about 5 V/km for conductive ground | [12] | yes (abstract) |
| Latitude dependence | about one order of magnitude smaller below about 50 degrees geomagnetic latitude | - | threshold flagged by authors as needing confirmation; Giza's geomagnetic latitude (about 27 N) is from memory | [12] | yes (abstract) |
| Storm-time field at low latitudes | 0.1 to 0.3 | V/km | two storms, coastal stations | search snippet | no (snippet) |
| Quiet-time large-scale field | below 1e-4 | V/km | long submarine cables | search snippet | no (snippet) |
| **Piezoelectricity** | | | | | |
| Quartz d11 | 2.27e-12 +/- 0.01e-12 (interferometric); 2.3e-12 | m/V = C/N | constant to GHz frequencies | [5][6] | yes (abstracts) |
| Quartz d14 | -0.67e-12 | C/N | | [6] | yes (abstract) |
| Granite apparent piezoelectric coefficient | about 1.4e-15 | C/N | "three orders" below quartz; one laboratory study. [V: re-read in two index copies of the abstract and confirmed. It is the direct effect (charge on stress release), an "apparent" value on a laboratory piece whose size the abstract does not give; decay time constant 1.5 to 4.0 s. It is the lowest published granite value found, not a consensus value] | [4] | yes (abstract) |
| Granite apparent piezoelectric coefficient, converse effect, local probe | about 7.0e-13 (+/- 0.1e-13) | C/N | [V: new row; highest published granite value found]. Atomic force microscope with lock-in detection; PZT and quartz as standards, soda glass as control; equals 0.30 of quartz d11 and 500 times the bulk value of [4]; abstract does not say whether the tip sat on one quartz grain, so treat as an upper bound for a grain-scale region, not a bulk coefficient | [32] | yes (abstract, publisher page) |
| Granites and aligned quartzite | never above the statistical effect of finite grain numbers | - | Australian granites; Poughquag quartzite | [2] | yes (abstract; re-read) |
| Largest reported rock value | 7 percent of single crystal (1.6e-13 C/N) | - | coarse vein quartz with fabric, not granite. [V: corrected scope. This is the largest bulk-specimen value found; the largest value of any kind reported for a rock is the 7.0e-13 C/N local-probe figure in the row above [32]. The 7 percent figure itself was not re-opened in this pass] | [7][8] | yes (abstracts, first pass only) |
| Statistical residual for 1 m3 of granite (my estimate) | about 1e-15 to 1e-14 | C/N | d11 / sqrt(N), 25 percent quartz, grain size 5 to 20 mm. [V: arithmetic reproduced (1.6e-15 and 1.3e-14), but the estimate omits the quartz volume fraction; including it gives 4e-16 to 3e-15 C/N. For a 5 cm laboratory cube the same estimate gives 1e-14 to 4e-14 C/N, so the agreement with [4] claimed in C6 is not like-for-like] | derived | calculation (re-derived) |
| Aswan red granite modal quartz | about 20 to 30 | vol percent | feldspar about 60 percent, biotite 5 to 10 percent; page returned 403, snippet only. [V: still unverified for the red granite. A point-counted source I could read gives, for "red Aswan" syenogranite, K-feldspar 36 vol percent and plagioclase about 20 vol percent with quartz present but not quantified; for "black Aswan" granodiorite quartz 22 vol percent; for "Nero Aswan" granodiorite quartz 19 vol percent [33]. Use 20 to 30 as a working range and sweep 15 to 40] | search snippet of [25]; [33] | no for red granite; yes for the granodiorites |
| Tura / Mokattam quarry limestone | calcite 96 to 99; quartz 0.5 to 2.5 | percent | XRD, six sites. [V: re-read and confirmed on the page: six sites, thin section plus chemical X-ray analysis plus XRD. Single source, interested author; no independent quantitative mineralogy opened] | [17] | yes (web summary of 1984 paper; re-read) |
| **Acoustics / sonochemistry** | | | | | |
| Stable cavitation in liquid | 1 to 3 | W/cm2 | [V: re-read on p. 2 of the chapter, confirmed. The chapter's Fig. 1.3 shows the onset threshold in aerated water below 1 W/cm2 at low frequency (roughly 0.1 to 0.3 by eye), so 1 W/cm2 is not a hard floor] | [18] | yes (re-read) |
| Transient cavitation in liquid | above 10 | W/cm2 | about ten times more power needed at 400 kHz than at 10 kHz. [V: both statements re-read on pp. 2 to 3, confirmed] | [18] | yes (re-read) |
| Characteristic impedance of air / water | 413 / 1.48e6 | Pa s/m | standard values | memory | no |
| Granite P-wave speed / density | about 5800 / 2650 to 2680 | m/s; kg/m3 | generic granite; Aswan-specific values not found | memory + snippet | no |
| Air breakdown field | about 3 | MV/m | sea level, uniform field | memory | no |
| **Other** | | | | | |
| "Gantenbrink door" slab | about 60 mm thick, 63.6 +/- 0.4 m up the shaft, fine limestone thought to be Tura, two pins judged copper from colour, small loops on the back | - | Djedi/Pyramid Rover reports; paper [26] not opened | search snippet | no (snippet) |

---

## 3. Claim-by-claim assessment

### C1. The 2018 paper "proves" field concentration around the King's Chamber for energy from above
**Verdict: partly supported, with heavy qualification.**
For plane waves at 200 to 600 m propagating down the axis, the paper shows electric-field maxima moving toward the centre and into the model chamber as the wavelength shortens to 230 to 200 m [1]. That part of the description is accurate. Qualifications:
- The enhancement is modest. Incident field 1 V/m gives at most about 3 V/m on the colour scale; the largest plotted intensity ratio in the chamber is about 35 at 200 m in free space and about 3 to 6 once a ground is included [1].
- The model chamber is an 11 m tall, 5 m wide slot with the incident E field polarised across its narrow dimension (dimensions from the text, orientation from the figures) [1]. If the void is air, continuity of the normal displacement field alone raises E inside a slot in an eps = 5 dielectric by up to a factor of 5 (intensity 25). My inference, not the authors' statement: a good share of the "concentration in the chamber" is this elementary boundary effect rather than focusing. A replication should report the field in the rock next to the chamber as well as in the void.
- As I read Fig. 4 of [1], the chamber's normalised E intensity for the wave from the base side (about 7 to 16) is higher than for the wave from the apex side (about 3 to 5) at every wavelength above roughly 215 m; only near 200 m does the from-above case dominate (about 35). If that reading is right, the neat split "from above goes to the King's Chamber, from below goes to the top" is not what the paper's own summary figure shows. This needs confirming in the replication because I read the curves by eye.
  [V: partly wrong, corrected. Magnified, Fig. 4 shows the two electric-field curves crossing near 270 m, not 215 m (was: "at every wavelength above roughly 215 m"). Below about 270 m, which includes the second resonance near 230 m, the wave from the apex side gives the higher chamber intensity (about 10 at 250 m, 20 near 230 m, 35 at 200 m, against about 5 to 12). Above about 270 m, which includes the first resonance near 333 m, the wave from the base side is higher (about 15 to 16 near 335 to 355 m against about 4). So the first-pass point survives only for the longer-wavelength half of the band, and the speaker's "from above goes to the King's Chamber" is correct for the shorter-wavelength half.]
  [V: a separate inconsistency inside the paper, relevant to replication. Fig. 4 plots the maximum intensity anywhere in the chamber. A value of 15 means about 3.9 V/m, yet the x-z field map for the same case (Fig. 3a, 330 m) shows the chamber region at roughly 1 V/m and the colour scale stops at 3 V/m; likewise 35 means 5.9 V/m in Fig. 2d. The chamber maxima are therefore probably local values at the box edges or corners, or lie outside the plotted plane. Edge values at a sharp dielectric corner depend on the mesh, so the replication should report the volume-averaged chamber field alongside the maximum. This is my inference from the figures, not a statement by the authors.]
- The real chamber is lined with granite, is about 5.8 m high, and sits under five relieving chambers; none of this is in the model.
- It is a simulation with an assumed permittivity. The authors say they found no measured dispersion data for Giza limestone [1].
- "Proves" overstates a first-order numerical study, which the authors themselves call a first step [1].
- [V: the low-loss premise is the weakest link. The authors state that slight deviations of the permittivity only shift the spectrum slightly [1]; measured in-situ losses are not slight deviations (imaginary part 13 to 67 from [16], about 200 to 300 at 1 MHz from [31], against 0.1). Until Model A is re-run with those losses, the fair wording is: the description of the paper is accurate for the shorter wavelengths; whether any chamber enhancement exists in the real, lossy structure is untested and, on the measured losses, doubtful.]

### C2. Field concentrates at the truncated top "excluding the capstone" for energy from below
**Verdict: contradicted as described.**
[V: verdict softened; "contradicted as described" is stronger than the evidence. Revised verdict: **split.** (a) The descriptive part, field near the top for a wave from below, is supported by the authors' own sentence that for incidence from the base side the electric field concentrates in the apex region at all wavelengths, and the plotted maxima do sit on the upper flanks rather than at the very tip [1]. (b) The inference, a truncated top or absent capstone, has no support, because the modelled apex is pointed and truncation was never varied. (c) The case exists only for a pyramid in free space; with a ground only incidence from above was modelled. The bullets below remain valid as the reasons for (b) and (c).]
- The model is a complete pointed pyramid 138.75 m high. There is no truncation and no capstone in the geometry, so the result cannot say anything about either [1].
- For the wave travelling from the base toward the apex the paper's text reports E concentrated in the apex region at all wavelengths and says accumulation in the King's Chamber is not observed in the field maps [1] (although Fig. 4 still plots a chamber intensity ratio of roughly 7 to 16 for this direction; see C1). In the plotted x-z cuts the maxima sit on the two upper flanks. This is the standing-wave pattern of an x-polarised wave in a dielectric wedge, not an effect of a missing capstone (my reading of Fig. 3).
- This case exists only for the pyramid in free space. A wave arriving from below the base would have to travel up through the Earth. When the substrate was added, only incidence from above was modelled [1].
- Basic electrostatics points the other way for static charge: field enhancement is stronger at a sharp apex than on a flat 10 m platform. A quasi-static simulation can quantify this directly.

### C3. The paper substantiates a dual power system (telluric from below, lightning from above)
**Verdict: no evidence; the inference is not valid physics.**
- The paper does not mention lightning, telluric currents, charge, voltage sources or power [1]. One of its two stated objectives is, in the authors' words, "partial removing of unreasonable speculations about electromagnetic properties of the Great Pyramid" [1].
- Frequency mismatch. Resonances were found at about 0.9 MHz and 1.3 MHz [1]. Telluric variations occupy millihertz to hertz. A thundercloud's field varies over seconds to minutes. A return stroke is a pulse with a rise of a few microseconds and a decay of tens of microseconds (snippet values, [24]), so most of its energy is below about 100 kHz, with a weak tail into the MHz band.
- Regime mismatch. Three dimensionless numbers decide the physics: electrical size L/lambda, the ratio of displacement to conduction current omega eps/sigma, and the induction number L/delta. For telluric and thunderstorm fields L/lambda is below 1e-6 and omega eps/sigma is far below 1 for any measured rock conductivity, so the pyramid is a resistive body in a DC current system. No resonance and no focusing can occur.
- The transcript itself concedes the gap: the speaker says the model would have to be re-run with a voltage source and says of the authors "I don't know why they chose radio waves" (full episode, 01:12). That re-run is what this project would do; until then the claim is a proposal, not a result.

### C4. The charged top attracts cloud-to-ground lightning
**Verdict: partly supported in a trivial sense; the proposed mechanism has no evidence.**
- Tall grounded objects are struck more often than flat ground. The standard method gives the original pyramid a collection area of about 1.07 km2, some 20 times its footprint (section 4.4). Objects above about 100 m also launch upward flashes [10].
- Under a negatively charged cloud base every grounded object carries induced positive surface charge. This needs no telluric "charging process".
- Telluric fields are horizontal, alternate in sign and amount to millivolts to at most volts across the base [12]. They cannot build a persistent charge at the summit because rock relaxation times are nanoseconds to milliseconds (section 4.3).
- The rate is low: of order 0.05 to 0.5 strikes per year from Egypt's mean flash density [9]. [V: corrected to about 0.03 to 0.3 per year with the collection area appropriate to a pyramid (section 4.4); the conclusion is unchanged and slightly strengthened. The rate still rests on a national mean, not a Giza-cell value.] The hypothesis needs repeated, schedulable energy input; a few strikes per decade lasting about 100 microseconds each do not provide it. (A separate claim, outside this file, is that the complex itself generated thunderstorms.)
- Context that favours strong electrical effects at the summit: an 1859 account by Werner von Siemens of sparks on the summit during a khamsin dust storm is widely retold. I saw only secondary retellings in search results, not the Poggendorff's Annalen text. Blowing-sand electrification is ordinary atmospheric electricity and does not depend on the building's design.

### C5. Limestone (7) and red granite (9) store electric field like a capacitor
**Verdict: partly supported on the numbers, contradicted on the function.**
- Values: dry limestone 7 and a limestone range of 4 to 8 at 100 MHz are standard compilation values [13]. Granite is 4 to 6 at 100 MHz [13]; Aswan granite was measured from 3.5 at high frequency to 24 at 100 Hz [14], so 9 is plausible in the kilohertz range. Note that the paper used 5 + 0.1i, not 7 [1].
- Function: every dielectric polarises in a field. A capacitor holds charge because its dielectric is an excellent insulator between conductors. Measured Great Pyramid limestone is 300 to 1500 ohm m [16], giving a relaxation time of 20 to 90 ns. Even for 1e6 ohm m it is about 60 microseconds, and for the driest Aswan granite value about 5 ms (section 4.3). Any stored field leaks away long before the next storm.
- Energy scale: at a thunderstorm-level field of 10 kV/m the energy density in eps = 7 rock is 3e-3 J/m3, about 8 kJ for the whole 2.6e6 m3 volume if the field could enter it, which screening prevents (my calculation).

### C6. The field drives the inverse piezoelectric effect in the King's Chamber and antechamber granite, producing ultrasound
**Verdict: contradicted quantitatively (many orders of magnitude), though the effect exists in principle.**
- In principle: quartz is piezoelectric, the converse effect is real, and quartz-rich rocks show measurable responses [3][4].
- Magnitude: granites tested by Tuck and co-workers never exceeded the statistical residue from a finite number of randomly oriented grains, and the authors concluded that piezoelectric fabrics probably do not exist [2]. Bishop found most rocks consistent with that statistical effect and a few (mainly strongly deformed quartz rocks) with a true fabric [3]. Parkhomenko stresses that the effect requires a specific orientation of the polar axes [19]. A direct measurement on granite gives about 1.4e-15 C/N [4]. The best rock on record is 7 percent of single crystal [7][8]. [V: "best rock on record" holds only for bulk specimens; see [32] for a 7.0e-13 C/N local-probe value on granite.]
- Why so low: quartz a-axes are polar. In an igneous rock grains have random orientation, and left- and right-handed crystals occur together, so contributions cancel and the residue scales as one over the square root of the number of grains. For 1 m3 with 25 percent quartz and 5 mm grains that is about 2e6 grains, a factor 7e-4, giving 1.6e-15 C/N, which matches the measured value [4] (my estimate). [V: the arithmetic is right but the match is not evidence. The measurement in [4] was on a laboratory piece, not 1 m3, and the estimate leaves out the quartz volume fraction; done like-for-like (5 cm cube, 2 to 5 mm grains, 25 percent quartz) the statistical residue is 1e-14 to 4e-14 C/N, above the measured 1.4e-15. The scaling argument stands; the numerical agreement is coincidental.]
- [V: published granite coefficients span a factor of 500: 1.4e-15 C/N for a bulk piece under stress release [4] and 7.0e-13 C/N for a microscope-scale converse measurement [32]. A simulation should carry both, as lower and upper bounds, and should not present 1.4e-15 as "the" granite value.]
- Drive: no ultrasonic-frequency field is available. Thunderstorm and telluric fields are quasi-static and screened. A return stroke is a single pulse. The paper's megahertz fields are a few V/m per V/m incident.
- Numbers (section 4.6): a lightning-driven field of about 1 kV/m in the granite gives a strain of about 1e-12 and a displacement of about 1 pm, radiating about 1e-15 W/cm2 into gas for about 100 microseconds. Cavitation-based sonochemistry uses 1 to 10 W/cm2 and above [18].
- For fairness: numerical studies predict that granite samples of centimetre size can be cracked by about 10 kV alternating excitation at a mechanical resonance near 100 kHz [20], and one experimental study reports reduced hardness and dynamic tensile strength after AC treatment [21]. These need a purpose-built high-voltage, high-frequency generator with electrodes on the sample, and they concern stress inside the rock, not sound radiated into a gas. A related simulation found converse-piezoelectric stresses three orders of magnitude below thermal stresses [27].
- [V: what would have to be true for the claim to pass, from the recomputation in section 4.6. Reaching 1 W/cm2 in air from a 1 m granite face at 20 kHz needs a sustained alternating field of 4e10 V/m with the bulk coefficient, 8e7 V/m with the microscope-scale coefficient, and 8e5 V/m if in addition the block is driven exactly on a mechanical resonance with a quality factor of 100 (assumed, not sourced). Only the last combination is below air breakdown, and it needs a continuous narrow-band megavolt-per-metre source, which a lightning pulse is not.]
- A point the hypothesis does not address: sonochemistry works through cavitation in a liquid [18]. The antechamber and King's Chamber are said to hold gas (SO2 and air). There is no cavitation in a gas, so the catalytic mechanism is undefined even if ultrasound were present.

### C7. Tura limestone has a high quartz content; the "Gantenbrink door" with copper pins is an ultrasonic transducer / flow meter
**Verdict: contradicted (quartz content); undefined by the hypothesis (transducer circuit).**
[V: quartz-content verdict softened to "not supported; contradicted by the only quantitative dataset found". The dataset [17] is real and was re-read, but it is a single study by an author with a position in the cast-stone controversy, and no independent quantitative mineralogy of Tura stone, of Giza bedrock, or of the shaft slab itself was opened. A petrological survey of 23 ancient limestone quarries with X-ray fluorescence data exists (Harrell 1992, Archaeometry, DOI 10.1111/j.1475-4754.1992.tb00492.x; abstract only seen) and should be obtained before this is stated as settled.]
- Tura and Mokattam quarry limestone: 96 to 99 percent calcite, 0.5 to 2.5 percent quartz [17]. The source is a 1984 paper by an author who argues for cast stone; the quarry analyses are the conventional part of that work. An independent petrographic source was not opened.
- Whether Tura stone has more quartz than the Giza bedrock limestone was not found; both are high-purity carbonates by [17].
- Bishop measured no piezoelectric effect in rocks with little or no free quartz, such as marble [3]. Detrital quartz grains at 1 to 2 percent in a carbonate matrix are randomly oriented.
- The slab is reported as about 60 mm thick with two pins judged to be copper from their colour and small loops behind (search snippets about [26]; not verified in the paper). A transducer needs a driving source, a return conductor and a piezoelectric element between electrodes. The hypothesis names none of these, and the speaker himself presents the idea as a playful conjecture that depends on what is found in the northern shaft (full episode, 01:23).
- The stated prediction (metal fittings behind the northern-shaft slab) would not discriminate between an electrical and a mechanical or symbolic purpose.

### C8. Iron-oxide veins act as wiring
**Verdict: no evidence either way; not measured.**
- No resistivity measurement of the Giza iron-oxide veins was found. Iron oxides such as hematite and goethite are semiconductors with conductivities many orders below metals, and far below magnetite (search snippet; hematite range in standard tables is very wide; not verified here).
- For a vein to guide current it needs a conductivity far above the host limestone (300 to 1500 ohm m in situ [16]) along a continuous path. This is measurable in the field with standard resistivity or induced-polarisation methods.
- The claimed fulgurite microspheres and "vitrified" veins were not checked in this session; no peer-reviewed report was located (not searched in depth).

### C9. Boat pits filled with electrolyte act as circuit breakers
**Verdict: undefined by the hypothesis; no evidence.**
- Dilute sulfuric or hydrochloric acid is a good ionic conductor (true as chemistry; conductivity value not sourced here).
- The circuit is undefined: source voltage, current, load and return path are not given. With telluric driving fields the available potential difference across the plateau is millivolts to volts [12].
- Acid in a limestone pit would react with the walls (covered in the chemistry file, not here). Sulfate found in pits has ordinary explanations at a site where gypsum mortar was used (memory, not verified here).

---

## 4. Worked estimates

All arithmetic is mine. Inputs are from the parameter table; unverified inputs are flagged there.

### 4.1 Frequencies in the paper
f = c / lambda. 600 m is 0.50 MHz, 333 m is 0.90 MHz, 250 m is 1.20 MHz, 230 m is 1.30 MHz, 200 m is 1.50 MHz.

### 4.2 How lossy is the real pyramid at 1 MHz?
Paper: eps'' = 0.1, so sigma = omega eps0 eps''. At 0.90 MHz: omega eps0 = 5.0e-5 S/m, so sigma = 5.0e-6 S/m (rho = 2.0e5 ohm m).
In situ: rho = 300 to 1500 ohm m [16], so sigma = 3.3e-3 to 6.7e-4 S/m and eps'' = sigma / (omega eps0) = 67 to 13 at 0.90 MHz. Loss tangent with eps' = 7: 9.4 to 1.9.
Skin depth from the general lossy-medium formula, eps' = 7, 0.90 MHz: 9.7 m (300 ohm m), 12.9 m (500 ohm m), 26 m (1500 ohm m). With the paper's values it is about 2.4 km.
Caveats: ERT sampled the outer few metres with wetted electrodes [16]; the core may be drier and more resistive; conductivity generally rises with frequency. The simulation should sweep sigma from 5e-6 to 3e-3 S/m.

[V: all figures in this subsection recomputed and confirmed (5.0e-6 S/m, 2.0e5 ohm m; eps'' 66.6 / 39.9 / 13.3; loss tangent 9.5 / 5.7 / 1.9; skin depth 9.7 / 12.9 / 26.4 m; 2.37 km for the paper's values with eps' = 5). Two additions.
(1) At 80 ohm m, the low end of the first-metre range in [16], eps'' is 250 and the skin depth 4.8 m.
(2) Independent RF evidence [31]: inverting the measured one-way attenuation with the general lossy-medium formula and eps' = 8.77 gives sigma = 0.016 S/m at 10 MHz (loss tangent 3.3, eps'' 29), 0.030 S/m at 50 MHz, 0.034 S/m at 125 MHz and 0.047 S/m at 150 MHz. If 0.012 to 0.016 S/m holds down to 1 MHz, eps'' is 216 to 279, the skin depth 4.1 to 4.7 m and the one-way loss about 1.9 to 2.1 dB/m, that is about 190 dB across 100 m of masonry. The report's own square-root-of-frequency scaling gives the same 1.9 dB/m at 1 MHz.
Caveats on (2): the measurements were in the Menkaure pyramid, the Khafre boat-pit roof and bedrock, not in Khufu's core; interior humidity was about 83 percent; extrapolation from 10 MHz to 1 MHz is mine. The sweep upper limit should be raised to 2e-2 S/m (was: 3e-3) and sigma should be allowed to vary with frequency.]

### 4.3 Can rock "store" field?
tau = eps0 epsr rho. Limestone, epsr 7: 19 ns (300 ohm m), 93 ns (1500 ohm m), 62 microseconds (1e6 ohm m). Aswan granite, epsr 6: 0.5 microseconds (1e-4 S/m) to 5 ms (1e-8 S/m).
A thunderstorm field evolves over seconds or longer, so tau is far smaller than the source time scale: the structure is an equipotential conductor on that time scale and the interior field is close to zero.

### 4.4 Lightning strike rate
Ad = L W + 2(3H)(L + W) + pi (3H)^2 [11].
Original pyramid, L = W = 230.3 m, H = 146.6 m: 53,038 + 405,144 + 607,660 = 1.066e6 m2.
Today, H = 138.75 m: 53,038 + 383,450 + 544,325 = 0.981e6 m2.
Nd = Ng Ad Cd 1e-6. Egypt's national mean of total lightning is 0.2 km^-2 yr^-1 [9]. Only part of total lightning reaches ground (a quarter to a half is a common assumption, memory), and the Cairo and Delta area probably exceeds the national mean because of Mediterranean winter storms. Taking Ng = 0.05 to 0.5: Nd = 0.05 to 0.5 per year with Cd = 1, doubled if the hilltop location factor of 2 is applied.
The 3H rule was developed for ordinary buildings; for objects taller than about 100 m upward-initiated flashes add to the count [10], so treat this as order-of-magnitude.

[V: recomputed. The three terms and both totals above are arithmetically correct (1,065,841 and 980,813 m2), but the formula is for a rectangular block with a flat roof at height H. The method's definition is geometric: the area enclosed on the ground by a line of slope 1:3 touching the upper parts of the structure. For a pyramid a point at height h on a corner edge lies 162.8 (1 - h/H) m from the axis and reaches a further 3h; that sum grows with h and peaks at the apex at 3H = 439.8 m. The collection area is therefore the single circle pi (3H)^2:
- original pyramid, H = 146.6 m: 607,660 m2 (0.61 km2), which is 57 percent of the block value;
- today, H = 138.75 m: 544,325 m2 (0.54 km2).
Nd = Ng x 0.608 km2 x Cd: 0.03 per year for Ng = 0.05; 0.12 for Ng = 0.2; 0.30 for Ng = 0.5 (Cd = 1); double for Cd = 2. With the national mean 0.2 total flashes and a cloud-to-ground share of one third, Ng = 0.07 and Nd = 0.043 per year, about one strike in 23 years (12 years with Cd = 2).
Still unverified: the Giza-cell flash density (only the national mean [9] was read); the cloud-to-ground share for Egypt (the ratio of about 2 is an Australian result [42]); thunderstorm days at Cairo (only a nineteenth-century magazine remark of three or four storm days a year surfaced, in a search snippet, not usable); and the standard's own complex-shape wording (secondary snippet only). Location factors confirmed on p. 36 of [11]: 0.25, 0.5, 1 and 2.]

### 4.5 Where would the current go, and what field results?
- Near the attachment point, half-space estimate J = I / (2 pi r^2). For 30 kA at r = 1 m, J = 4.8 kA/m2 and E = rho J = 1.4 to 7 MV/m for 300 to 1500 ohm m. That exceeds the 0.3 to 1 MV/m ionisation range quoted for soils (snippet), so the first few metres would conduct through arcs and ionised channels along joints and surfaces. Radius where E falls to 0.4 MV/m, rho = 500 ohm m: 2.4 m.
- At the level of the King's Chamber (about 43 m above the base, memory) the horizontal cross-section is about 163 m square, 2.65e4 m2. If the peak current were spread uniformly: J = 1.1 A/m2, E = 0.34 to 1.7 kV/m. For the 200 kA design maximum [10]: 2.3 to 11 kV/m. Real distributions will be non-uniform (surface moisture, joints, transient skin effect: skin depth at 100 kHz and 500 ohm m is about 36 m), which generally reduces the field near the axis.
- Telluric comparison: 0.1 V/km (storm-time, low latitude) is 1e-4 V/m, giving J = 2e-7 A/m2 in 500 ohm m rock and 23 mV across the 230 m base. The 100-year high-latitude extreme of 20 V/km [12] would give 4.6 V across the base; Giza is below the 50 degree threshold, so roughly a tenth of that.

[V: recomputed and confirmed: cross-section at 43 m is 162.7 m square, 2.65e4 m2; 30 kA gives 1.13 A/m2 and 340 to 1,700 V/m for 300 to 1,500 ohm m; 200 kA gives 2.3 to 11.3 kV/m. With the lower resistivities now on the table (60 to 80 ohm m, [16] first metre and [31]) the uniform-spreading field falls to 75 to 90 V/m at 30 kA. So the assumed drive field for section 4.6 spans roughly 0.07 to 11 kV/m; 1 kV/m sits inside that range and is not a lower bound. The field inside a resistive granite body embedded in more conductive limestone can exceed the surrounding field by a geometry-dependent factor (1.5 for a sphere; more for a slab lying across the current path); that factor is not estimated here and is a task for Model B. The 20 V/km and 5 V/km figures and the order-of-magnitude drop below about 50 degrees were re-read in the abstract of [12] and confirmed.]

### 4.6 Strain, displacement and acoustic intensity
Converse effect: strain S = d E; surface displacement u = S L for thickness L (upper bound: uniform field, all strain delivered to one face). Radiated plane-wave intensity I = (1/2) rho c v^2, with v = omega u for sinusoidal drive or u / t_rise for a pulse.

Coefficients: (A) measured granite 1.4e-15 C/N [4]; (B) best rock fabric on record, 7 percent of quartz, 1.6e-13 C/N [7]; (C) perfectly aligned single-crystal quartz, 2.3e-12 C/N [6]. Thickness L = 1 m.

Scenario 1: one lightning return stroke, E = 1 kV/m in the granite, rise time 5 microseconds, duration about 100 microseconds.

| Coefficient | Strain | Displacement | Velocity | Intensity in gas |
|---|---|---|---|---|
| A granite | 1.4e-12 | 1.4e-12 m | 2.8e-7 m/s | 1.6e-11 W/m2 = 1.6e-15 W/cm2 |
| B 7 percent | 1.6e-10 | 1.6e-10 m | 3.2e-5 m/s | 2.1e-7 W/m2 = 2.1e-11 W/cm2 |
| C quartz crystal | 2.3e-9 | 2.3e-9 m | 4.6e-4 m/s | 4.4e-5 W/m2 = 4.4e-9 W/cm2 |

Scenario 2: a hypothetical continuous 20 kHz field at the air-breakdown limit of 3 MV/m. No natural source for this is known; it is the most generous bound that the gas in the chamber could tolerate.

| Coefficient | Strain | Displacement | Velocity | Intensity in gas | Intensity into water |
|---|---|---|---|---|---|
| A granite | 4.2e-9 | 4.2 nm | 5.3e-4 m/s | 5.8e-9 W/cm2 | 2.1e-5 W/cm2 |
| B 7 percent | 4.8e-7 | 0.48 micrometre | 0.060 m/s | 7.5e-5 W/cm2 | 0.27 W/cm2 |
| C quartz crystal | 6.9e-6 | 6.9 micrometre | 0.87 m/s | 1.6e-2 W/cm2 | 56 W/cm2 |

Scenario 3: the paper's fields. 1 V/m incident gives at most about 6 V/m in the chamber [1]. Strain in granite 8e-15. At 1 MHz the acoustic half-wavelength in granite is about 3 mm, so the coherent displacement is about 2e-17 m. Negligible, and no megahertz source existed.

Reverse calculation: 1 W/cm2 in air (160 dB) needs v = 7.0 m/s, which at 20 kHz is u = 55 micrometres. From 1 m of measured granite that needs E = 3.9e10 V/m; from perfect quartz 2.4e7 V/m. Air breaks down near 3e6 V/m.

Comparison: cavitation needs 1 to 3 W/cm2 (stable) or more than 10 W/cm2 (transient) in a liquid [18]. Scenario 1 with real granite is 15 orders of magnitude short; even the unphysical scenario 2 with real granite is 8 orders short in gas.

[V: section 4.6 recomputed independently from S = d E, u = S L, v = u / t_rise or omega u, I = (1/2) Z v^2 with Z = 413 Pa s/m (air) and 1.48e6 (water). Every entry in the three tables and the reverse calculation reproduces to the stated precision (scenario 1, granite: 1.4e-12 strain, 1.4 pm, 2.8e-7 m/s, 1.62e-15 W/cm2; reverse: 6.96 m/s, 55 micrometres, 3.96e10 V/m). Additions:

Coefficient M, granite by atomic force microscope, 7.0e-13 C/N [32]:
- scenario 1: strain 7.0e-10, displacement 0.70 nm, velocity 1.4e-4 m/s, 4.1e-10 W/cm2 in gas (9.4 orders below 1 W/cm2);
- scenario 2: 2.1 micrometres, 0.26 m/s, 1.4e-3 W/cm2 in gas, 5.2 W/cm2 into water;
- reverse: 7.9e7 V/m for 1 W/cm2 in air, about 26 times air breakdown.

Sensitivity to the assumed field (scenario 1, intensity in gas, W/cm2; intensity goes as field squared):

| Field in granite | A bulk 1.4e-15 C/N | M local 7.0e-13 C/N |
|---|---|---|
| 100 V/m | 1.6e-17 | 4.1e-12 |
| 1 kV/m | 1.6e-15 | 4.1e-10 |
| 10 kV/m | 1.6e-13 | 4.1e-8 |
| 100 kV/m | 1.6e-11 | 4.1e-6 |
| 3 MV/m (air breakdown) | 1.5e-8 | 3.6e-3 |

So across the whole physically admissible field range and the whole published coefficient range, a single pulse stays at least 2.4 orders below 1 W/cm2, and at the fields that current spreading actually predicts (0.07 to 11 kV/m) it stays 7 to 17 orders below. The result is insensitive to the choice of 1 kV/m in the sense that no admissible field closes the gap; it is sensitive in the sense that the quoted "15 orders" moves by two orders for every factor of ten in field.

Two assumptions in the first-pass tables favour the hypothesis and should be stated: the pulse intensity uses u / t_rise as if the whole 1 m thickness responded in phase within 5 microseconds, although sound crosses only 29 mm of granite in that time; and scenario 2 treats a 1 m thickness as quasi-static at 20 kHz, although the acoustic wavelength in granite is 0.29 m. Both overstate the displacement. Resonant build-up could work the other way: with a quality factor Q (assumed 100; not sourced) under sustained narrow-band drive the required field falls by Q, to 4e8 V/m (A) or 8e5 V/m (M).

Shortfall statement corrected: scenario 1 is 15 orders short with coefficient A, 11 with B, 9 with M (was: "11 to 15" in the summary).]

Other acoustic notes: a 1 m thick granite block has its fundamental thickness resonance near v / 2L = 2.9 kHz, which is audible sound, not ultrasound; ultrasonic fundamentals need pieces thinner than about 15 cm. A mechanical resonance can multiply the response by the quality factor only under sustained narrow-band drive at that frequency. The thunder shock from a strike would deliver far more acoustic energy to the chamber than any piezoelectric response.

---

## 5. What a simulation of this domain needs

### 5.1 Model A: replicate Balezin et al. (full-wave, frequency domain)
- **Equation:** curl curl E - k0^2 eps_r(r) E = 0 with complex eps_r; scattered-field formulation; perfectly matched layers.
- **Solver:** frequency-domain vector FEM with edge elements, or FDTD with a broadband pulse. Open-source options to evaluate: Palace, Elmer (VectorHelmholtz), NGSolve, FEniCSx, openEMS, Meep. The authors used CST, COMSOL and DDA [1].
- **Geometry and materials for the baseline:** exactly as in section 2 (pointed pyramid 138.75 m by 230 m, eps = 5 + 0.1i, three box chambers, substrate of the same material).
- **Mesh:** wavelength in the rock at 200 m is about 89 m; use at most a tenth of that globally and 0.5 to 1 m near chambers.
- **Validation targets (pass for the replication):** free-space extinction peaks at about 333 m and about 230 m with about 0.09 and 0.13 km2; substrate case one broad maximum near 250 m at about 0.12 km2; chamber intensity ratios as in Fig. 4 and Fig. 7 of [1].
- **Then vary:** conductivity 5e-6 to 3e-3 S/m (section 4.2) [V: extend to 2e-2 S/m and allow frequency dependence, per [31]; also run eps' = 7 and 8.8 as well as 5; report volume-averaged as well as maximum chamber fields]; real chamber dimensions with granite lining and relieving chambers; Grand Gallery; truncated top against pointed top against capstone; oblique incidence and both polarisations; bedrock with a different, wetter permittivity.
- **Pass/fail for claim C1/C2:** report the field enhancement factor in the granite (not only the air) for each variant. The claim survives only if the enhancement persists with measured conductivity and real geometry. The capstone claim passes only if truncation produces a field maximum that a pointed top does not.

### 5.2 Model B: quasi-static thunderstorm field and lightning current (the actual hypothesis)
- **Equations:** electro-quasi-static, div[(sigma + eps d/dt) grad phi] = 0, in air, rock and ground. For the return stroke add induction: either full-wave time domain (FDTD) or a frequency sweep from 100 Hz to 1 MHz followed by an inverse transform, because the skin depth (about 110 m at 10 kHz, 36 m at 100 kHz for 500 ohm m) is comparable with the structure.
- **Boundary and initial conditions:** uniform background field at the top of the air domain (fair weather about 100 V/m, under a storm about 10 kV/m; both from memory and to be sourced); ground at zero potential far away; for the strike, a current source at the summit with a standard waveform (median about 30 kA, design maximum 200 kA with 10/350 microsecond shape [10]). Include a nonlinear ionisation or surface-arc model near the attachment point, or bound the result with and without it.
- **Materials:** limestone 80 to 1500 ohm m measured [16], sweep to 1e6 [V: lower bound 60 ohm m per [31]]; granite sigma 1e-8 to 1e-4 S/m and eps 3.5 to 24 by frequency [14]; moisture state is the dominant unknown [22].
- **Outputs:** E(t) and J(t) in the granite of the King's Chamber and antechamber; surface field at the summit for flat and pointed tops; fraction of current through bulk against surface.
- **Key dimensionless numbers:** omega eps / sigma; L / skin depth; tau_relax / tau_source; L / lambda.
- **Pass/fail for claims C3 to C5:** pass if the peak field in the granite exceeds what Model D needs to reach the acoustic threshold; fail if the interior field is screened to the conduction value of order kV/m or less. The "attraction" claim passes only if a flat top raises the summit field relative to a pointed one.

### 5.3 Model C: telluric (DC conduction)
- **Equation:** div(sigma grad phi) = 0 in a half-space with the pyramid as topography, uniform horizontal far field of 1e-7 to 2e-2 V/m [12].
- **Options:** thin conductive sheets for iron-oxide veins with conductivity as a free parameter; pits filled with electrolyte.
- **Outputs:** potential of the summit relative to the base; current density through the structure; conductivity contrast a vein would need to carry a stated fraction of the current.
- **Pass/fail for claims C3, C8, C9:** pass only if a non-negligible field or charge appears at the summit or in the granite. The expected outcome from current continuity is a lower field in the raised body than in the ground beneath it.

### 5.4 Model D: coupled piezoelectric and acoustic response
- **Equations:** linear piezoelectricity, T = c S - e^T E and D = e S + eps E, with rho u_tt = div T and div D = 0, coupled to linear acoustics in the gas (continuity of normal velocity and pressure at the interface).
- **Material description:** either a grain-resolved polycrystal (about 25 percent quartz, random orientations, equal left- and right-handed fractions, feldspar and mica as non-piezoelectric phases), as in the rock-mechanics literature [20], or an effective tensor with magnitude sampled between the statistical residual and 7 percent of quartz [4][7] [V: extend the upper bound to 7.0e-13 C/N, 30 percent of quartz, per [32]; quartz fraction 15 to 40 percent until the red-granite mode is verified].
- **Drive:** E(t) from Model B.
- **Outputs:** surface velocity spectrum, acoustic intensity and sound pressure level in the antechamber and King's Chamber gas volumes, including room modes.
- **Pass/fail for claim C6:** the hypothesis must first state the intensity and frequency it needs. Using the liquid cavitation thresholds of 1 to 10 W/cm2 [18] as a stand-in, section 4.6 predicts a shortfall of 8 to 15 orders of magnitude. A simulation result within two orders of the threshold with measured granite coefficients would count as support. Separately, the chemistry model must say how ultrasound in a gas, without cavitation, accelerates SO2 oxidation.

---

## 6. Open questions

1. Flash density and thunderstorm days for the Giza grid cell. Only the national mean (0.2 km^-2 yr^-1) was found [9]. The LIS/OTD 0.5 degree and 0.1 degree gridded products [23] would give it directly but were not downloaded (rule 8).
2. Bulk electrical conductivity and permittivity of Great Pyramid core limestone and of Aswan granite at 1 kHz to 1 MHz, as a function of moisture. Only near-surface DC ERT values [16] and one abstract-level Aswan granite range [14] were found.
3. Point-counted modal composition of Aswan monumental granite. The 20 to 30 percent quartz figure is from a search snippet of [25]; the page refused the fetch.
4. Full text of Tuck, Stacey and Starkey 1977 and Bishop 1981: only abstracts were read, so their numerical coefficients for granite are not quoted here. The author list of [2] beyond the first author was not displayed by the index I used.
5. Parkhomenko's tabulated piezoelectric moduli for rocks: not accessed; only the chapter abstract [19].
6. Typical telluric current densities and quiet-time fields from the Lanzerotti and Gregori review [28]: the online text did not load.
7. CIGRE TB 549 values (median 30 kA, charge, action integral) were seen only in search snippets [24]; the brochure is paywalled.
8. Resistivity of the Giza iron-oxide veins and the nature of the reported "fulgurite" microspheres: no measurements or peer-reviewed reports found.
9. Independent petrography of the "Gantenbrink door" slab and of Tura against Giza bedrock limestone; the Djedi paper [26] was not opened.
10. Whether the 11 x 5 x 11 m model chamber and its orientation relative to the polarisation account for most of the reported chamber enhancement, and whether my by-eye reading of Fig. 4 of [1] (chamber intensity higher for the wave from the base side at most wavelengths) is correct. Both are testable in Model A.
11. The hypothesis does not define: the required acoustic intensity and frequency; how gas-phase ultrasound catalyses the reaction; the circuit (source, load, return) for the veins, pits and copper pins; how often lightning must strike.
12. The advisor review tool was rate-limited during this session, so this file has not had an independent second-pass review. [V: a second-pass verification was done on 2026-10-10; see the last section. The advisor tool was rate-limited again in that session, so the verification pass itself has had no further review.]

Status of these questions after the verification pass:
- Q1 remains open. No text source gives the Giza-cell flash density or Cairo thunderstorm days. It must be read from the gridded LIS/OTD files.
- Q2 is partly answered by the SRI / Ain Shams RF measurements [31] (10 to 150 MHz, Menkaure and Khafre, humid interior). Nothing was found between 1 kHz and 1 MHz, and nothing for Khufu's core.
- Q3 remains open for the red granite; quartz 22 and 19 vol percent verified for two Aswan granodiorites [33].
- Q7 remains open (two search runs agree on 30 kA and 12 kA; no opened page states them).
- Q10 is answered in part: the Fig. 4 crossover is near 270 m, not 215 m; the slot-geometry question and the edge-maximum question remain for Model A.
- New Q13: the sample geometry and probe location in the atomic-force-microscope granite measurement [32] (full text not read). This decides whether 7.0e-13 C/N can be used as anything more than a grain-scale upper bound.
- New Q14: conductivity of Khufu's core masonry at 0.5 to 1.5 MHz as a function of moisture. This single number decides whether the resonances in [1] exist in the real structure.
- New Q15: independent quantitative mineralogy of Tura limestone and of the Queen's Chamber shaft slab.

---

## 7. Sources

Read in this session unless marked otherwise.

1. Balezin M., Baryshnikova K. V., Kapitanova P., Evlyukhin A. B. (2018). Electromagnetic properties of the Great Pyramid: First multipole resonances and energy concentration. Journal of Applied Physics 124, 034903. https://doi.org/10.1063/1.5026556 (full published PDF read, all 7 pages, from a third-party copy at https://public.3.basecamp.com/p/h6n96AgLdzgNRmy5kB3oM6Vt/attachments/03e78d0c-9f91-11ee-9b69-1e0199a71503/download/electromagnetic-properties-great-pyramid.pdf; no arXiv version was found).
2. Tuck G. J. et al. (1977). A search for the piezoelectric effect in quartz-bearing rocks. Tectonophysics 39, T7-T11. https://doi.org/10.1016/0040-1951(77)90148-2 (abstract read via the Consensus index, which lists "G. Tuck et al."; the task brief names the co-authors as Stacey and Starkey, which I could not confirm on a page I opened; volume and pages from a library index seen in search results).
3. Bishop J. R. (1981). Piezoelectric effects in quartz-rich rocks. Tectonophysics 77, 297-321. https://doi.org/10.1016/0040-1951(81)90268-7 (abstract read).
4. Sasaoka H. et al. (1998). Measurements of electric potential variation by piezoelectricity of granite. Geophysical Research Letters. https://doi.org/10.1029/98GL51179 (abstract read).
5. Bottom V. E. (1970). Measurement of the piezoelectric coefficient of quartz using the Fabry-Perot dilatometer. Journal of Applied Physics. https://doi.org/10.1063/1.1658392 (abstract read).
6. Carr P. (1967). Measurement of the piezoelectric constant of quartz at gigacycle frequencies. Journal of the Acoustical Society of America. https://doi.org/10.1121/1.1910332 (abstract read). See also Bechmann R. (1958), Elastic and piezoelectric constants of alpha-quartz, Physical Review, https://doi.org/10.1103/PhysRev.110.1060 (abstract only; no numbers in abstract).
7. Ghomshei M. et al. (1988). Piezoelectric pole figure of a vein quartz sample. Textures and Microstructures. https://doi.org/10.1155/TSM.7.303 (abstract read).
8. Ogawa T., Utada H. (2001). Evaluation of coseismic EM signals due to the piezoelectricity of crustal rocks. Japan Earth and Planetary Science Joint Meeting, abstract Eq-014. https://www2.jpgu.org/meeting/2001/pdf/eq/eq-014_e.pdf (read in full).
9. Collier A. et al. (2011). A harmonic model for the temporal variation of lightning activity over Africa. Journal of Geophysical Research. https://doi.org/10.1029/2010JD014455 (abstract read).
10. Diendorfer G. (2006). Lightning properties derived from lightning location systems and tower measurements. Invited talk, INCEMIC 2006. https://www.aldis.at/fileadmin/userdaten/aldis/publication/2006/1_INCEMIC2006_Diendorfer.pdf (pages 1-3 read).
11. DEHN (2014). Lightning Protection Guide, p. 35 (IEC 62305-2 collection-area method). https://resources.ipd.com.au/Flipbook/35_DS702_E_2014_Lightning_Protection_Guide/files/basic-html/page35.html (read via fetch summary; the standard itself, IEC 62305-2, is paywalled).
12. Pulkkinen A., Bernabeu E., Eichner J., Beggan C., Thomson A. W. P. (2012). Generation of 100-year geomagnetically induced current scenarios. Space Weather 10, S04003. https://doi.org/10.1029/2011SW000750 (abstract read at https://nora.nerc.ac.uk/id/eprint/18443/).
13. Martinez A., Byrnes A. P. (2001). Modeling dielectric-constant values of geologic materials. Kansas Geological Survey, Current Research in Earth Sciences, Bulletin 247, Table 1. https://www.kgs.ku.edu/Current/2001/martinez/table1.html (table read; values attributed there to Davis and Annan 1989 and Daniels 1996). This is reference 19 of [1].
14. Gomaa M. M. (2021). Frequency response of electrical properties of some granite samples. Journal of Earth and Space Physics 47(4), 75-86. https://doi.org/10.22059/jesphys.2021.318321.1007287 (abstract page read at https://journals.ut.ac.ir/article_83550.html).
15. US EPA, Environmental Geophysics archive, resistivity methods, Table 1 (after Telford et al. 1976 and others). https://archive.epa.gov/esd/archive-geophysics/web/html/index-7.html (read).
16. Pugacheva P., Allam H., Fath-Elbab M., et al. (2025). Investigation of the North Face Corridor in the Great Pyramid of Giza using Electrical Resistivity Tomography. Scientific Reports 15, 41187. https://doi.org/10.1038/s41598-025-29081-4 (read at https://pmc.ncbi.nlm.nih.gov/articles/PMC12638825/).
17. Davidovits J. (1984). X-ray analysis of pyramids' casing stones and their limestone quarries. Science in Egyptology Symposia, Manchester, pp. 511-520. Web summary: https://geopolymer.org/library/archaeological-papers/a-x-ray-analysis-pyramids-casing-stones-and-their-limestone-quarries (read).
18. Santos H. M., Lodeiro C., Capelo-Martinez J.-L. (2009). The Power of Ultrasound. Chapter 1 in Ultrasound in Chemistry: Analytical Applications, Wiley-VCH. https://application.wiley-vch.de/books/sample/3527319344_c01.pdf (pages 1-6 read).
19. Parkhomenko E. I. (1971). Piezoelectric effects in rocks. Chapter 4 in Electrification Phenomena in Rocks, Plenum. https://doi.org/10.1007/978-1-4757-5067-6_4 (abstract read).
20. Saksala T. (2021). Cracking of granitic rock by high frequency-high voltage-alternating current actuation of piezoelectric properties of quartz mineral: 3D numerical study. International Journal of Rock Mechanics and Mining Sciences. https://doi.org/10.1016/j.ijrmms.2021.104891 (abstract read).
21. Rubio Ruiz R. A., et al. (2024). Progressive weakening of granite by piezoelectric excitation of quartz with alternating current. Rock Mechanics and Rock Engineering. https://doi.org/10.1007/s00603-024-03948-w (abstract read).
22. Olhoeft G. R. (1981). Electrical properties of granite with implications for the lower crust. Journal of Geophysical Research 86(B2), 931-936. https://doi.org/10.1029/JB086iB02p00931 (abstract read at https://pubs.usgs.gov/publication/70012142).
23. Cecil D. et al. (2012, as dated by the index). Gridded lightning climatology from TRMM-LIS and OTD: Dataset description. Atmospheric Research. https://doi.org/10.1016/j.atmosres.2012.06.028 (abstract read).
24. Rakov V. A., et al. (2013). Lightning parameters for engineering applications (CIGRE Technical Brochure 549). Electra summary read at https://www.iee.usp.br/sites/default/files/biblioteca/producao/2013/Artigos%20de%20Periodicos/Rakov%20-%20lightning%20parameters.pdf (no numerical values in that summary; the 30 kA, 12 kA and 5 C figures were seen only in search-result snippets of other summaries and are marked unverified).
25. MDPI Heritage 8(4), 137 (2025), article on Aswan granite. https://www.mdpi.com/2571-9408/8/4/137 (NOT read: HTTP 403; quartz 20 to 30 percent seen in a search snippet only).
26. Richardson R., et al. (2013). The "Djedi" robot exploration of the southern shaft of the Queen's Chamber in the Great Pyramid of Giza, Egypt. Journal of Field Robotics 30(3), 323-348. https://doi.org/10.1002/rob.21451 (NOT read; details from search snippets).
27. Saksala T. (2021). Piezoelectric effect does not contribute in thermal drilling of quartz bearing rocks. IOP Conference Series: Earth and Environmental Science 833, 012097. https://doi.org/10.1088/1755-1315/833/1/012097 (abstract read).
28. Lanzerotti L. J., Gregori G. P. (1986). Telluric currents: the natural environment and interactions with man-made systems. In The Earth's Electrical Environment, National Academies Press. https://nap.nationalacademies.org/read/898/chapter/145 (NOT read: page text failed to load).
29. Aufort J., et al. (2015). Effect of pores and grain size on the elastic and piezoelectric properties of quartz-based materials. American Mineralogist. https://doi.org/10.2138/am-2015-5180CCBY (abstract read; agate comparable to single crystal, sandstone and novaculite weak, porous silica glass none).
30. Transcripts (local): full episode /Users/aeroshariati/Pyramid/youtube-transcript/danny-jones/new-scans-expose-an-unfortunate-secret-under-the-pyramids-geoffrey-drumm/transcript.md (lines 373-461, 478-527, 564-609 read); clip transcripts under /Users/aeroshariati/Pyramid/youtube-transcript/history-drops/ (searched for the same passages).

Added in the verification pass of 2026-10-10 (each opened in that session unless marked):

31. Barakat N., El Dessouki T., El Hennawi H., Moussa A. H., Tolba M. F., Abdel-Wahab S. (Ain Shams University); Dolphin L. T. Jr., Bollen R. L., Johnson D. A., Oetzel G. N., Tanzi J. D. (Stanford Research Institute); Mokhtar G., Hassan A. (Organization of Antiquities); Buckingham S. O. (Lawrence Berkeley Laboratory). Electromagnetic Sounder Experiments at the Pyramids of Giza. Report under NSF Grant GF-38767 on fieldwork of autumn 1974. Web copy: https://www.ldolphin.org/egypt/egypt1/index.html (read through a fetch summary covering the first 100,000 of about 113,800 characters; the publication year, 1975, appears in a library-catalogue search result and not on the page I read).
32. Matsuda T., Yamanaka C., Ikeya M. (2005). Piezoelectric Measurements of Granite as Composite Material Using Atomic Force Microscope. Japanese Journal of Applied Physics 44, 968. https://doi.org/10.1143/JJAP.44.968 (abstract read on the publisher page and in the Consensus index; full text paywalled).
33. Lasheen E. S. R., Rashwan M. A., Osman H., Alamri S., Khandaker M. U., Hanfi M. Y. (2021). Radiological Hazard Evaluation of Some Egyptian Magmatic Rocks Used as Ornamental Stone: Petrography and Natural Radioactivity. Materials 14(23), 7290. https://doi.org/10.3390/ma14237290 (petrography section read at https://pmc.ncbi.nlm.nih.gov/articles/PMC8658492/ through two fetch summaries; point counting; three samples per rock type).
34. Neishtadt N. M. et al. (2006). Application of piezoelectric and seismoelectrokinetic phenomena in exploration geophysics: Review of Russian and Israeli experiences. Geophysics. https://doi.org/10.1190/1.2187714 (abstract read in the Consensus index; co-authors, volume and pages not displayed there).
35. Russell R. D. et al. (1992). Electromagnetic responses from seismically excited targets A: Piezoelectric phenomena at Humboldt, Australia. Exploration Geophysics. https://doi.org/10.1071/eg992281 (abstract read, same index).
36. Sobolev G. A. et al. (1984). Tests of piezoelectric and pulsed-radio methods for quartz vein and base-metal sulfides prospecting at Giant Yellowknife Mine, N.W.T., and Sullivan Mine, Kimberley, Canada. Geophysics. https://doi.org/10.1190/1.1441633 (abstract read, same index).
37. Ghomshei M. et al. (1989). Piezoelectric and a-axes fabric along a quartz vein. Physics of the Earth and Planetary Interiors. https://doi.org/10.1016/0031-9201(89)90084-8 (abstract read, same index).
38. Higgins M. et al. (2010). Measurement and Modeling of the Indirect Coupling of Lightning Transients into the Sago Mine. IEEE Transactions on Electromagnetic Compatibility. https://doi.org/10.1109/temc.2009.2036928 (abstract read, same index).
39. Lin Y.-Y. et al. (2026). Lightning-Induced Implosive Microseismic Events at Depth Detected by Downhole Distributed Acoustic Sensing in Taiwan. Seismological Research Letters. https://doi.org/10.1785/0220250432 (abstract read, same index; a single recent study, not yet replicated).
40. Cooray V. (2001). Underground electromagnetic fields generated by the return strokes of lightning flashes. IEEE Transactions on Electromagnetic Compatibility. https://doi.org/10.1109/15.917942 (abstract read, same index; no numbers in the abstract).
41. Jose B. (dated 2010 by the index). Feasibility of the piezoelectric exploration technique for quartz vein detection. University of British Columbia thesis. https://doi.org/10.14288/1.0052547 (abstract read, same index).
42. Kuleshov Y. et al. (2006). Spatial distribution and frequency of lightning activity and lightning flash density maps for Australia. Journal of Geophysical Research. https://doi.org/10.1029/2005jd006982 (abstract read, same index; used only for the cloud-flash to ground-flash ratio of about 2).

Re-opened in the verification pass: [1] (all 7 pages viewed as page images, Figs. 4 and 7 magnified), [4] (two index copies of the abstract), [9], [10] (5 pages viewed as page images), [11] (pp. 35 and 36), [12], [14], [16], [17], [18] (pp. 1 to 6 viewed as page images). Abstracts of [2], [3], [5], [20], [23], [25] and [27] were seen again in the Consensus index and agree with the first-pass descriptions; the index gives [25] as Fahmy A. et al. (2025), Heritage, DOI 10.3390/heritage8040137, and its abstract names quartz, feldspar and biotite without percentages. Not re-opened: [6] to [8], [13], [15], [19], [21], [22], [24], [26], [28], [29].

---

## Verification pass (2026-10-10)

Scope: the load-bearing numbers and the claim verdicts of this file, checked by a second reader who re-opened sources and redid the arithmetic with an independent script (Python standard library; kept outside the project folder). "Confirmed" means the figure was read in an opened source in this pass. Graph readings were made on page images magnified about four times. Sources seen only as a fetch-tool summary or an index abstract are marked as such. Quotation is avoided; everything is paraphrased.

### Checks

| # | Item | First-pass value | Status | Evidence in this pass | Source |
|---|---|---|---|---|---|
| V1 | Balezin et al. geometry | 138.75 m high, 230 m base, pointed, no capstone or truncation | confirmed | Page 2 gives height 138.75 m and base side 230 m; every figure draws a complete triangle to the apex; the words capstone and truncated do not occur. King's Chamber 11 x 5 x 11 m, 5 m off axis, 40.5 m up; Queen's 5 x 5 x 6 m, 2.5 m off axis, 20.8 m up; third chamber 5.2 x 5.6 x 4.6 m, 2.4 m off axis, 29.8 m below base. Chamber fill is not stated. | [1] pp. 2 to 5 |
| V2 | Balezin et al. material, band, solvers, stated aims | eps = 5 + 0.1i; 200 to 600 m; CST, COMSOL, DDA; aim of removing speculation; "first step" | confirmed | Permittivity 5 + i0.1 with a cited literature range of 4 to 6 and no Giza measurements; same value for the substrate; band 200 to 600 m; resonances near 333 m and 230 m in free space and one broad maximum near 250 m on the substrate; the two stated objectives and the first-step wording are as reported. The authors add that slight permittivity deviations do not change conclusions, that weak absorption follows from the small imaginary part, and that the pyramid mostly scatters energy into the substrate. No lightning, telluric current, charge, granite or piezoelectricity appears anywhere. | [1] pp. 1 to 6 |
| V3 | Balezin et al. excitation and substrate by direction | from apex side and from base side in free space; from above only on substrate | confirmed | Fig. 1 insets: plane wave along the axis, x-polarised, 1 V/m incident, k against z in (a) and along z in (b), both in free space. Fig. 5(a): substrate case with normal incidence from above only. | [1] pp. 3 to 5 |
| V4 | Balezin et al. reported enhancement factors | Fig. 4: apex side 35 at 200 m, 3 to 5 above 250 m; base side 7 to 16; base-side curve higher above about 215 m. Fig. 7: 3 to 6 | corrected | Fig. 4 magnified: apex-side E curve 35 (200 m), about 20 (230 m), 10 (250 m), 3.5 to 4 (290 to 600 m); base-side E curve 12 (200 m), minimum 4.5 to 5 (260 m), peak 16 (355 m), 4.5 (600 m); crossover near 270 m, not 215 m. Fig. 7 E: 3.2 to 4.6, 2.7 to 4.7, 2.3 to 6.0 for the three chambers. Colour scales stop at 3 V/m (free space) and 2 V/m (substrate overview). | [1] Figs. 2 to 4, 6, 7 |
| V5 | In-situ resistivity of Great Pyramid masonry | 300 to 1500 ohm m; 80 to 300 ohm m in first metre | confirmed | Both ranges are in the article; depth of investigation about 2 m; water-soaked sponge coupling; forward model used 500 ohm m; mean contact resistance 1.7 kilohm. | [16] |
| V6 | Loss of the real structure near 1 MHz | eps'' 13 to 67; skin depth 10 to 26 m; "probably optimistic" | confirmed arithmetic; conclusion strengthened | Recomputed: 66.6 / 39.9 / 13.3 and 9.7 / 12.9 / 26.4 m. Independent RF data: 6 dB/m at 10 MHz to 25 dB/m at 150 MHz one-way, eps' about 8.8 at 50 MHz, interior humidity 83 percent; inverted to 0.016 S/m at 10 MHz; extrapolated eps'' 216 to 279 and skin depth 4.1 to 4.7 m at 1 MHz. | [16]; [31]; script |
| V7 | Charge relaxation times | limestone 2e-8 to 9e-8 s, up to 6e-5 s; granite 5e-7 to 5e-3 s | confirmed | 1.86e-8, 9.30e-8, 6.20e-5 s (eps 7); 5.31e-7 and 5.31e-3 s (eps 6). Range widened: 4e-9 s at 65 ohm m; 2.1e-2 s for granite with eps 24. Inputs re-read: Aswan granite 24 to 3.5 and about 1e-8 to 1e-4 S/m over 100 Hz to 1e7 Hz, surface samples, moisture state not given. | [14]; [16]; [31]; script |
| V8 | Flash density at Giza | national mean 0.2 total flashes km^-2 yr^-1; Giza cell not found | national mean confirmed; Giza cell unverifiable | Abstract re-read: lowest national average in Africa is Egypt at 0.2, from 10 years of two satellite detectors. Five further searches found no published Giza or Cairo cell value and no modern thunderstorm-day normal. The gridded 0.5 degree and 0.1 degree products hold the number but need a data download, which was not done. | [9]; [23] abstract |
| V9 | Collection area and strikes per year | 1.07e6 m2; 0.05 to 0.5 per year | corrected | Rectangular formula reproduces 1,065,841 m2 but assumes a flat-roofed block. Envelope of the 1:3 slope rule for the pyramid is a circle of radius 3H: 607,660 m2 (original), 544,325 m2 (today). Strikes: 0.03 to 0.3 per year for Ng 0.05 to 0.5; 0.043 per year for Ng 0.07. Location factors 0.25, 0.5, 1, 2 confirmed. Ng about 0.1 Td, 1.5 to 1.7 strike points per flash, 100 m threshold and protection-level-I maxima confirmed. | [11] pp. 35, 36; [10] pp. 1, 2, 4; script |
| V10 | Bulk piezoelectric coefficient of granite | about 1.4e-15 C/N | confirmed | Abstract in two indexes: apparent coefficient about 1.4e-15 C/N, three orders below single-crystal quartz, from potential pulses on stress release decaying over 1.5 to 4.0 s. One index copy garbles the multiplication sign; the other prints it cleanly. Sample size and granite type are not in the abstract. Quartz d11 = 2.27e-12 m/V re-read in the abstract of [5]. | [4]; [5] |
| V11 | Higher or lower granite values; "largest value for any rock is 7 percent of quartz" | 7 percent of single crystal is the maximum | wrong as stated; corrected | A converse-effect measurement by atomic force microscope reports about 7.0e-13 C/N for granite, 30 percent of d11 and 500 times V10. It is a local-probe value and the abstract does not give the probe location. Abstracts of [2] and [3] re-read: granites never exceeded the statistical effect; most quartz-rich rocks consistent with it, a few with true fabric. No value below 1.4e-15 C/N was found. | [32]; [2]; [3] |
| V12 | Statistical residual estimate and its "match" to V10 | 1.6e-15 C/N for 1 m3, matching the measurement | arithmetic confirmed; inference corrected | N = 2.0e6 and d11 / sqrt(N) = 1.63e-15 reproduce. Including the 25 percent volume fraction gives 4.1e-16. For a 5 cm cube the estimate is 9e-15 to 4e-14, so the comparison with a laboratory measurement is not like-for-like. | script |
| V13 | Piezoelectric displacement and acoustic intensity | 1.4 pm and 1.6e-15 W/cm2 at 1 kV/m; 3.9e10 V/m for 1 W/cm2 | confirmed; sensitivity added | All table entries reproduce. Intensity scales with field squared. Bulk coefficient: 1.6e-17 W/cm2 at 100 V/m to 1.5e-8 at 3 MV/m. Local-probe coefficient: 4.1e-12 to 3.6e-3. Field from current spreading recomputed as 0.07 to 11 kV/m. Cavitation thresholds of 1 to 3 and above 10 W/cm2 re-read. | [18] pp. 2, 3; script |
| V14 | Quartz content of Tura limestone | calcite 96 to 99 percent, quartz 0.5 to 2.5 percent | confirmed, single source | Figures, six sites and methods re-read on the page. Author is the main proponent of cast-stone pyramids; the quarry analyses are the uncontroversial part but remain uncorroborated here. | [17] |
| V15 | Quartz content of Aswan granite | red granite about 20 to 30 vol percent (snippet) | unverifiable for red granite; partly confirmed for related rocks | Point-counted modes: red Aswan syenogranite K-feldspar 36, plagioclase about 20 vol percent, quartz not quantified; black Aswan granodiorite quartz 22; Nero Aswan granodiorite quartz 19. The source cited in the first pass was not re-attempted beyond its index abstract, which gives no percentages. | [33]; [25] abstract |
| V16 | Median first-stroke peak current | about 30 kA (snippet) | unverifiable in an opened source | Two search runs return 30 kA (first) and 12 kA (subsequent) as brochure text; the brochure's conference abstract and [10] do not state them. [10] gives a 10 kA median for a sensitive location network. | [24]; [10] |
| V17 | Geoelectric field extremes | 20 V/km and 5 V/km; tenfold drop below about 50 degrees | confirmed | Abstract re-read: 100-year 10-second maxima of 20 and 5 V/km at high latitude for poorly and well conducting ground; threshold near 50 degrees geomagnetic latitude with about an order of magnitude drop, flagged by the authors as needing confirmation. Giza's geomagnetic latitude remains a from-memory value. | [12] |

### Verdict changes

| Claim | Old verdict | New verdict | Reason |
|---|---|---|---|
| C2 field at a truncated top for energy from below | contradicted as described | split: description supported for the free-space model, capstone inference unsupported, no ground case exists | The authors themselves write that the field concentrates in the apex region for incidence from the base side. The first pass treated the whole claim as contradicted because the model has no truncation; only the inference fails. |
| C1 sub-point on Fig. 4 | from-below chamber intensity higher at every wavelength above about 215 m | higher only above about 270 m; from-above higher from 200 to about 270 m | Magnified re-read of Fig. 4. The headline C1 verdict (partly supported, heavily qualified) is unchanged. |
| Summary point 3 and C1, loss assumption | "probably optimistic" | too soft; two independent in-situ datasets put the loss 2 to 3.5 orders above the model's | SRI / Ain Shams RF attenuation plus the ERT values. Applicability of the resonance result to the real structure is untested and doubtful, not merely uncertain. |
| C4 strike rate | 0.05 to 0.5 per year | 0.03 to 0.3 per year | Collection area for a pyramid is pi (3H)^2, not the rectangular-block value. Verdict wording unchanged. |
| C6 magnitude statements | best rock value is 7 percent of quartz; shortfall 11 to 15 orders | best bulk value 7 percent, best local value 30 percent; shortfall 9 to 15 orders | Atomic-force-microscope converse measurement on granite. Headline verdict (contradicted by many orders) unchanged. |
| C7 quartz content | contradicted | not supported; contradicted by the only quantitative dataset found | Single, interested source; no independent petrography opened. |

C3, C5, C8 and C9 were re-examined against the re-read sources and stand as written.

### Steelman: the strongest published evidence in favour, and what it does and does not reach

1. **Field-scale piezoelectric response of quartz bodies is established.** Soviet, Canadian, Australian and Israeli field work detected electric signals from quartz veins and massive quartz excited by shots or hammer blows, at source distances up to about 55 m underground, at kilohertz frequencies, with antenna signals of microvolts to tens of microvolts [34][35][36][41]. Consistent polarity along a vein, with neutron texture data, indicates a piezoelectric fabric at large scale [37]. Limits: vein quartz and pegmatite, not granite; the direct effect (stress to field), not field to sound; received signals of microvolts to tens of microvolts, so fields of order a microvolt per metre.
2. **A large converse coefficient has been measured on granite at the grain scale** (7.0e-13 C/N) [32]. Limit: local probe, not bulk; a wall of randomly oriented grains averages this down.
3. **Converse-piezoelectric actuation of granite is an active engineering topic.** Simulations predict cracking of centimetre-size specimens at about 10 kV and a specimen resonance near 100 kHz, and weakening at 150 kV and 274 kHz [20 and a 2023 follow-up seen in the index]; one experimental paper reports weakening [21]. Limit: purpose-built high-voltage, high-frequency generators with electrodes on the specimen; the same authors state that experimental validation is still needed.
4. **Lightning fields penetrate rock.** Coupling of lightning transients through mine overburden has been measured and modelled, with the finding that horizontal current channels can induce large voltages on long insulated conductors underground [38]; time-domain theory for underground fields exists [40]; a 2026 borehole study reports seismic impulses at 50 to 140 m depth immediately after a ground flash, with strain rates of order 3e-6 per second [39]. Limit: none of these involves piezoelectric conversion, and [39] is a single unreplicated observation whose mechanism the authors leave open.
5. **The speaker's reading of the paper's from-below case is closer to the authors' text than the first pass allowed** (see C2), and his permittivity of 7 lies between the paper's 5 and the in-situ 8.8 [31].
6. **Electrical phenomena at the summit are historically reported** (the Siemens account). Not re-checked in this pass; still secondary.

Searched for and not found: any peer-reviewed measurement of sound or ultrasound radiated into air by an electrically driven quartz-bearing rock mass at metre scale or larger; any measurement of lightning-induced electric field inside a large masonry structure; any gas-phase SO2 oxidation by airborne ultrasound (this last belongs to the chemistry file and was not searched in depth here).

### Still open after this pass

1. Flash density for the Giza grid cell and thunderstorm days at Cairo. Unverifiable from text sources; needs the gridded files.
2. The 30 kA and 12 kA median currents: confirm in the brochure itself.
3. Modal quartz of Aswan red granite from a point-counted source.
4. Sample geometry of the atomic-force-microscope granite measurement [32].
5. The complex-shape collection-area rule in the standard itself (only a secondary snippet seen); the geometric derivation used here does not depend on it.
6. Conductivity of Khufu's core masonry at 0.5 to 1.5 MHz. The SRI data are from other Giza structures at 10 MHz and above.
7. Whether the chamber maxima in Figs. 4 and 7 of [1] are edge or corner values (my inference from the mismatch with the field maps).
8. Independent mineralogy of Tura limestone and of the shaft slab.
9. The publication year of [31] (not on the page read) and the last 12 percent of that page's text (not covered by the fetch).
10. Quality factor of large granite blocks at kilohertz frequencies (the value of 100 used in the reverse calculation is an assumption).
