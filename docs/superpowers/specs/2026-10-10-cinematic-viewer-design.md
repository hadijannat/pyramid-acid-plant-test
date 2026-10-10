# Cinematic viewer: design

Date: 2026-10-10. Status: for the project owner's review. Supersedes the display parts of two earlier specs (section 13).

## 1. Context and decisions

Plan A delivered a viewer that animates the claimed cycle as a schematic: flat-shaded spaces inside a translucent pyramid, one camera pose per step, a side panel and a timeline bar. The project owner wants a full-screen, visually impressive Three.js and WebGL scene that serves three audiences at once: a visitor who opens it from the README, a speaker who drives it in a talk, and the project itself as an analysis instrument.

Decisions the owner made on 2026-10-10:

- **Purpose:** all three audiences, in one scene with two modes: a cinematic default and an inspector overlay.
- **Look:** hybrid. A physically based exterior and plateau for establishing shots; a luminous schematic interior once the camera is inside.
- **Tour:** a guided tour with captions: authored camera paths through the 31 steps, a caption per step with the claim and its verdict, the actors animating; scrub, pause and orbit at any time.
- **Instruments:** verdict and numbers; cutaway and layers; the chemistry display; Results mode.
- **Sequencing:** this spec absorbs the display parts of the chemistry-display spec and of the process-simulation spec. The King's Chamber geometry rebuild stays a separate small plan; the process-simulation model stays its own spec and writes to the results contract defined here.
- **Architecture:** a rewrite of `viewer/` as small ES modules around one state store. No build step, pinned CDN three.js, nothing installed.

The project's rules bind the pretty version as they bound the plain one: every number has a source, nothing is drawn that the data files do not carry, mechanisms the hypothesis leaves unspecified stay visible as placeholders, and the fixed notice says what the scene is.

## 2. Goals and non-goals

Goals:

1. A full-screen scene that reads as a place from outside and as a legible process from inside, at 60 frames per second on a recent laptop and acceptably on a phone.
2. A guided tour of the claimed cycle that a visitor can watch end to end without touching anything, and can interrupt at any moment.
3. An inspector that shows, for any step or space, exactly what the plan A panel showed, plus a section plane, layer controls, the chemistry display and Results mode.
4. A results data contract, with a committed fixture, that the process-simulation model and the field solvers write to and this viewer reads.
5. A public URL on GitHub Pages.

Non-goals:

- Any change to the ledger's physical quantities, the screening or the geometry (except the cycle file and a species file, which are display data).
- New physical content in the scene: no block courses, no neighbouring monuments, no casing, no terrain, because the ledger holds none of their dimensions.
- Virtual reality, multi-user features, analytics.
- A build toolchain. Modules are served as written.

## 3. Architecture

### 3.1 Modules

```
viewer/
  index.html            full-screen canvas, HUD mounts, the import map (three 0.170.0, pinned)
  app.js                boot: load data, create the store, mount render, tour and hud, start the loop
  store.js              the state and subscribe()
  data/load.js          fetch and validate claims.json, cycle.json, manifest.json, results/<case>/*
  render/renderer.js    WebGLRenderer, EffectComposer, quality tiers, resize, the frame loop
  render/environment.js sky, sun, ground, fog, weather
  render/materials.js   procedural stone, glass cutaway, the schematic interior set, hatching
  render/model.js       glTF loading, mesh registry, picking, section plane, per-space visibility
  render/actors.js      one factory per actor type (water, gas, lightning, placeholder, coat, field, species label)
  tour/camera.js        spline camera paths, easing, user override and resume
  tour/player.js        clock, play, pause, scrub, step changes, look and weather transitions
  hud/cinematic.js      caption card, progress strip, hints
  hud/inspector.js      panels: step, space, layers, cutaway, chemistry, results, step list, quality
  hud/plots.js          time series as inline SVG
  style.css
```

`panel.js`, `timeline.js` and `scene.js` are removed; their logic lives in the modules above.

### 3.2 The store

One plain object with `subscribe(fn)` and `set(patch)`; subscribers receive the previous and next state and react to the keys they own.

```
{
  mode: 'cinematic' | 'inspector',
  case: 'claim' | <case id>,          // 'claim' draws cycle.json; a case id draws results/<case>/
  stepIndex, t, playing,               // t in seconds into the cycle (claim) or model time (results)
  quality: 'low' | 'medium' | 'high',
  layers: { masonry: 0..1, bedrock: 0..1, spaces: Set<space id> },
  cutaway: { on, axis: 'ns' | 'ew' | 'z', position: 0..1 },
  picked: space id | null,
  reading: 'survey' | 'alternative',
  hud: { visible: true | false },
  reducedMotion: boolean,
}
```

Modes change which HUD is mounted and which layers are forced, never the scene graph. Camera, time and layers are shared, so switching modes never moves the camera or resets the step.

### 3.3 Data flow

`app.js` loads the data and creates the store. `tour/player.js` advances `t` and sets `stepIndex`. `render/actors.js` reads the step's actors and asks one question of a source: what is the state of space X at time t. In claim mode the answer comes from `cycle.json` (the actor's `from` and `to` and the level-volume curves); in results mode from `results/<case>/levels.json` and `composition.json`. `hud/*` render from the store and the loaded data only. `window.viewer` exposes the store and a `state()` summary for browser checks, as plan A's viewer did.

## 4. Rendering

### 4.1 Exterior

The masonry mesh carries a procedural limestone material: triplanar value noise in the fragment shader for grain and weathering, flat shading, no block courses. A plateau ground plane at pavement level extends to the horizon in a sand colour. The three.js `Sky` addon with a sun provides the background and, through a PMREM environment map, the ambient light; one directional shadow map covers the pyramid and the ground; distance fog softens the horizon. No neighbouring monument is drawn.

Weather is a store value the tour sets from each step's `scene.weather`: `clear` or `storm`. Storm lowers the sun, darkens the sky and enables the lightning actor's flashes. Only the steps whose claim states a storm carry `storm`.

### 4.2 Interior

When a step's `scene.interior` is true, the player cross-fades over the camera move: the masonry material becomes dark glass with a Fresnel edge glow, the ground fades out, and the spaces switch to the schematic set:

- air spaces: pale emissive surfaces;
- water: the clipped volume of plan A, with a slow in-shader ripple and a brighter band within 0.3 m of the free surface;
- gas: a view-dependent haze (Fresnel density, drifting noise) and, on the high tier, a sparse particle cloud inside the space's bounds, at most 4,000 points in a step;
- lightning: the authored bolt as a fat line (`Line2`) with bloom, two strokes per step as now;
- placeholders: the 4 m dashed cube and label, unchanged in meaning and drawn in every tier;
- coat: an outline skin on the coated spaces;
- species labels: CSS2D labels with the formulas present in a space, hatched species marked (section 6.3).

### 4.3 Post-processing and colour

`EffectComposer`: render pass, `UnrealBloomPass` (threshold high enough that stone never blooms; initial strength 0.6, radius 0.4, threshold 0.85, display choices to be tuned), SMAA. ACES filmic tone mapping, sRGB output. Verdict colours (pass, fail, conditional, undefined, pending) are used only on badges, chips and the progress strip, never on scene materials.

### 4.4 Cutaway

Clipping planes on the masonry and bedrock materials only; spaces and actors are never clipped. Three preset orientations (north-south, east-west, horizontal) and a position slider over the model's bounds.

### 4.5 Quality tiers

| Tier | Pixel ratio cap | Shadows | Bloom | Particles |
|---|---|---|---|---|
| high | 2 | 2048 map | yes | yes |
| medium | 1.5 | 1024 map | yes | no |
| low | 1 | none | no | no |

The viewer starts at `medium`, measures frame times for two seconds, and moves to `high` if the median is under 10 ms or to `low` if it is over 25 ms. The inspector's quality control overrides it; the choice is remembered in `localStorage` (a per-viewer convenience, read in a try block). A query flag `?quality=low` forces a tier for tests. WebGL 2 is required; without it the page shows a message and the notice.

## 5. The tour

### 5.1 Paths

Each step carries `path`, two to four keyframes of `position` and `target` in the ledger frame; `viewer_data.py` converts them to viewer coordinates as it converts the single camera today. The player builds a centripetal Catmull-Rom spline through the previous step's last keyframe and the step's keyframes, and rides it over the step's duration with ease-in-out. Any pointer or touch on the canvas pauses the ride where it is and hands the camera to the orbit controls; *Resume*, or the next step, rejoins the path.

### 5.2 Prologue

`cycle.yaml` gains a `prologue`: a path and a duration (6 s) for a flight from far outside to the entrance face. It carries no claim; its caption is the project title and the notice. The page does not autoplay: the camera drifts slowly on the prologue's first keyframe until the visitor presses *Play the claimed cycle*.

### 5.3 Captions and progress

The cinematic HUD is one card: step id and title; the claim as stated (`claims.json` statement); the verdict badge and the basis sentence; below it a strip of 31 ticks coloured by verdict, the current one enlarged. Dragging the strip scrubs. Nothing else is on screen in cinematic mode.

### 5.4 Scene state

Each step carries `scene: {interior: bool, weather: 'clear' | 'storm'}`. Look and weather cross-fade when they change between steps. A Python test asserts that `interior` is true exactly when the step's camera target (the first keyframe's) lies inside the masonry's bounding box, so the flag cannot drift from the camera.

### 5.5 Controls

| Input | Action |
|---|---|
| Space | play or pause |
| Left, Right | previous or next step |
| drag on the strip | scrub |
| I | toggle the inspector |
| F | fullscreen (Fullscreen API) |
| H | hide or show the HUD (the notice stays) |
| Esc | back to cinematic mode |
| pointer on canvas | orbit; pauses the ride |

Deep links: `#S16` as now; `?mode=inspector`, `?case=<id>`, `?quality=<tier>`.

## 6. The inspector

`I` or the corner button mounts translucent dark panels over the same scene: step and space cards on the left, instruments on the right, each collapsible. On a phone the panels become a bottom sheet.

### 6.1 Verdict and numbers

The step card: the claim as stated, the criterion, the verdict badge, the basis, the deciding results as a table (value, range, unit) using plan A's rule (a claim shows the results whose inputs lie within its `depends_on`), sources and timestamps. The space card: label, ledger quantities with value, range, unit, source and note, unverified values tagged, and the claims the space takes part in as chips that jump to their step. The step list: the 31 steps with verdict chips. All text is set with `textContent`.

### 6.2 Cutaway and layers

Section plane (on, axis preset, position), masonry and bedrock opacity, per-space checkboxes, the survey or alternative reading, the quality tier, a scale bar (10, 20, 50 or 100 m, chosen from the camera's distance to its target) and a north arrow (from the camera heading), both drawn in the HUD.

### 6.3 Chemistry display

Taken over unchanged from the chemistry-display spec:

- `ledger/species.yaml`: one entry per compound the video names, with `id`, `formula` (Unicode subscripts), `name`, `phase`, `colour`, `produced_by`.
- Each step gains `species`; `gas` and `water` actors drop `color` and gain `species`; a `coat` actor draws the calcium sulfate layer of S23; reaction steps (S02, S16, S19, S20, S21, S23, S27) gain `reaction` with the equation as the video states it, the timestamp, and a note, or the text "not stated by the hypothesis".
- The marking rule, computed in `viewer_data.py`: a species whose producing step's verdict is `fail` or `undefined` is drawn hatched with "claimed" after its formula; `conditional` is tagged; otherwise plain.

In the scene: a formula label on each occupied space; liquid coloured by its first-listed species; hatching as screen-space diagonal stripes (8 px pitch, half duty) over the actor's colour. In the inspector: a legend of the current step's species with colour, name, formula and marking, and the reaction above the verdict. In cinematic mode only the scene labels appear.

### 6.4 Results mode

A Claim / Results switch with a case picker listing `manifest.cases`. In results mode:

- actors read `results/<case>/levels.json` and `composition.json`: water level per space over model time, liquid coloured by its dominant species and labelled with mole fractions, gas spaces labelled with mole fractions; the model's clock replaces the claimed durations, and the progress strip shows model time;
- where a step's claimed level differs from the computed one, the claimed level is drawn as an outline over the computed fill;
- the results panel plots, for each claim in `series.json`, the quantity its criterion names against time, with the median, the 5 to 95 percent band, the criterion lines, the verdict and the undefined inputs it depends on; SVG drawn by `hud/plots.js`, no library;
- a field case draws its slices from its `case.json` at the stated extent with the stated caption; a slice without an extent is not drawn; a step with no slice in the case shows "Solver result pending";
- the notice reads "Simulation result: <case label>" with the case's commit and ledger digest one click away.

The viewer side ships complete against the contract of section 7.3 and a committed fixture case, so it is finished before the model exists; the picker labels the fixture "fixture, not a result".

## 7. Data contracts

### 7.1 `cycle.yaml` and `cycle.json`

Additions: `prologue: {path, duration}`; per step `path` (2 to 4 keyframes), `scene` (`interior`, `weather`), `species` (list of ids), optional `reaction` (`equation`, `timestamp`, `note`); actors: `gas` and `water` carry `species` instead of `color`; new actor type `coat` with `space`. The single `camera` of plan A is removed; its pose becomes the first keyframe, and plan A's tests of the `camera` key are rewritten for `path`. `viewer_data.py` converts every keyframe and placeholder position to viewer coordinates and attaches each species' `status` from the producing step's verdict. Every other existing key keeps its meaning. The `field` actor stays in the claim cycle and, in claim mode, always draws the "Solver result pending" label: a solver's slice is a result and belongs to a field case (section 7.3).

### 7.2 `species.yaml`

As in section 6.3; loaded with the strict loader's conventions (unknown keys rejected, every `produced_by` a known step id, every colour a hex string).

### 7.3 Results, `viewer/data/results/<case>/`

Written by the process-simulation model and by the field-solver plan; validated by `pyramid/results_contract.py`, which both plans import.

| File | Content |
|---|---|
| `case.json` | `{id, label, kind: 'process' \| 'field', description, time_unit, duration, notice, manifest: {commit, ledger, seed, versions}}` |
| `levels.json` | `{times: [...], spaces: {<space>: [fraction, ...]}}` on one shared time grid |
| `composition.json` | `{times, liquid: {<space>: {<species>: [mole fraction, ...]}}, gas: {<space>: {<species>: [...]}}}` |
| `series.json` | `{<claim id>: {quantity, unit, times, median, low, high, criterion: {pass, fail}, status, depends_on_undefined: [...]}}` |
| `fields/` | PNG slices of a field case, listed in that case's `case.json` under `fields: [{file, step, plane, extent: [[x0, y0, z0], [x1, y1, z1]] in viewer metres, caption}]` |

A process case has `levels.json`, `composition.json` and `series.json`; a field case has `fields/` and may have `series.json`. The top-level `manifest.fields` of plan A is dropped.

Rules: all arrays on a time grid have the grid's length; fractions lie in 0 to 1; mole fractions of a space sum to 1 within 1e-6 at each time; `status` uses the project's verdict vocabulary; every space and species id exists in the model and the species table; every field extent lies within the model's bounds. A committed `results/_fixture/` is a process case with 25 time samples of synthetic values for every file, `label: "Fixture, not a result"`, and one claim in `series.json` for each verdict word.

### 7.4 `manifest.json`

Gains `cases`: the list of case directories present, each with `id`, `label` and `kind`. The viewer lists only these.

### 7.5 Geometry

Unchanged by this spec. The King's Chamber rebuild (five relieving compartments, gable, coffer) is its own plan on the Python side; the viewer reads whatever spaces the glTF carries, and its per-space tables key by space id.

## 8. Honesty, accessibility, phone

- The notice is the first element in the DOM and stays visible in both modes, in fullscreen and with the HUD hidden: "Animation of the claim. Not a simulation result." in claim mode, "Simulation result: <case>" in results mode, "Fixture, not a result" for the fixture.
- Placeholders stay dashed and labelled in every tier; the storm sky appears only on steps whose claim states a storm; the plateau is a plane; nothing the ledger does not hold is drawn.
- Scene colours are not verdicts, and the inspector's footer says so.
- Every number on screen comes from `claims.json`, `cycle.json` or a case directory; text is set with `textContent` only.
- Controls are real buttons and inputs with labels, keyboard operable; the caption is an `aria-live` region; `prefers-reduced-motion` disables the camera ride, bloom pulses and particle drift, so steps cut instead of fly; HUD text contrast is at least 4.5:1.
- Phone: `low` or `medium` tier, caption at the bottom, inspector as a bottom sheet, 16 px gutters, no horizontal scroll; checked at 375 px.
- Browser support: current Chrome, Safari and Firefox; WebGL 2 required.

## 9. Performance budget

Interior steps at `high` on a recent laptop: under 16 ms per frame with bloom and particles. The glTF is about 1,900 vertices; the cost is in the full-screen passes, so the tiers scale pixel ratio first. `viewer/` JavaScript stays under 150 KB unminified; no asset is loaded from anywhere but the pinned three.js CDN and the repository.

## 10. Testing

Python: contract tests for `cycle.json` (every step has a path of 2 to 4 keyframes, `scene.interior` agrees with the masonry bounds, species ids exist, reaction steps carry `reaction`), for `species.yaml`, for the results schema against the fixture and against a deliberately broken copy, and for the marking rule driven through every status. Generated files are regenerated on a clean tree after the code commit, as the README says.

Browser, reviewer-driven through `window.viewer` as in plan A: the prologue plays and the page does not autoplay; the cross-fade occurs on the first interior step; a hydraulic step, a reaction step and a gas step are checked at 1280 px and 375 px; the inspector opens without a camera jump; the cutaway clips masonry only; species labels and hatching appear on S16 and S20; results mode loads the fixture and draws its plots and the outline where claim and result differ; `?quality=low` yields the low tier; `prefers-reduced-motion` cuts instead of flying; no console errors from the page.

## 11. Deployment

GitHub Pages from `main`, with a root `index.html` that redirects to `viewer/`, so the URL is `https://hadijannat.github.io/pyramid-acid-plant-test/`. Enabled as the plan's last task, after the owner says go.

## 12. Order of work

Each milestone leaves the viewer working and reviewable.

1. Store, renderer with composer and tiers, environment, materials, model loading; the existing single camera read as a one-keyframe path; the current actors ported. The scene looks new; the tour behaves as before.
2. Paths and prologue in `cycle.yaml`; the spline player; cross-fades; the cinematic HUD; controls and deep links.
3. Actor upgrades and the chemistry display: species table, cycle additions, marking rule, labels, hatching, coat.
4. The inspector: step and space cards, layers, cutaway, scale bar, step list, quality control.
5. Results contract module, fixture, results mode, plots, field slices.
6. Phone layout, accessibility, the performance probe, Pages.

Two implementation plans: V1 covers milestones 1 to 3 (the scene, the tour, the chemistry display) and ends with a public cinematic viewer; V2 covers milestones 4 to 6 (the inspector, Results mode, phone and Pages). V2 is written after V1's final review, against V1's code.

Geometry dependence: none. When the King's Chamber rebuild lands, the five new space ids appear in the per-space tables; nothing else changes.

## 13. Relation to other specs

- `2026-10-10-chemistry-display-kings-chamber-design.md`: Part A (the chemistry display) is absorbed here (section 6.3); Part B (the King's Chamber region) remains that spec's scope.
- `2026-10-10-process-simulation-results-mode-design.md`: section 7 (Results mode in the viewer) is absorbed here (section 6.4); its section 6 (outputs) is replaced by the contract of section 7.3, which the model writes to.
- `2026-10-10-foundation-em-reply-design.md`: the field-solver cases write slices under section 7.3's `fields/` with extents and captions, which closes the final review's request for a captioned, bounded field actor.
