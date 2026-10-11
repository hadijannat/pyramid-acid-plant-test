# Cinematic Viewer V1 Implementation Plan: scene, tour, chemistry display

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the plan A viewer with a full-screen Three.js scene that renders the pyramid as a place from outside and as a luminous schematic from inside, rides authored camera paths through the 31 claimed steps with a caption and verdict per step, and shows every compound the hypothesis names in its space and step, with the products of failed steps marked as claimed.

**Architecture:** `viewer/` is rewritten as small ES modules around one state store (`store.js`): `render/` owns the WebGL renderer, post-processing, environment, materials, model and actors; `tour/` owns the camera ride and the player clock; `hud/` owns the cinematic caption and controls. Everything on screen is driven by `viewer/data/cycle.json` and `claims.json`, which `pyramid/viewer_data.py` generates from the ledger; this plan extends the cycle file with camera paths, scene flags and species, and adds a species table. No build step: modules are served as written and import three.js from a pinned CDN.

**Tech Stack:** three.js 0.170.0 (ES modules from cdn.jsdelivr.net, with `examples/jsm` addons: OrbitControls, GLTFLoader, CSS2DRenderer, EffectComposer, RenderPass, UnrealBloomPass, SMAAPass, Sky, Line2/LineMaterial/LineGeometry), WebGL 2, plain CSS; Python 3.12 with the existing `pyramid` package (PyYAML, numpy, trimesh, gmsh) and pytest.

**Spec:** `docs/superpowers/specs/2026-10-10-cinematic-viewer-design.md` (sections 1 to 5, 6.3, 7.1, 7.2, 8, 9, 10 and milestones 1 to 3 of section 12 are this plan's scope; the inspector, Results mode, the results contract, phone layout and Pages are plan V2). The chemistry display is specified in that spec's section 6.3, which takes it over from `2026-10-10-chemistry-display-kings-chamber-design.md` section 3 (read that section for the species table and the equations).

## Global Constraints

- three.js is imported only from `https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js` and `https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/` through the import map in `viewer/index.html`. No other external asset, script, font or stylesheet. Nothing is installed: no npm, no `uv add`. Ask the project owner before any download or install.
- No build step. Every file under `viewer/` is served as written by `python3 -m http.server 8765 --directory viewer`.
- The notice is the first element in `<body>`, fixed at the top, visible in every mode, in fullscreen and with the HUD hidden. Its text in this plan is always `cycle.notice` ("Animation of the claim. Not a simulation result.").
- Nothing is drawn that the data files do not carry: no block courses, no neighbouring monuments, no casing, no terrain. Mechanisms the hypothesis leaves unspecified stay dashed placeholders with their labels, in every quality tier. The storm sky appears only on steps whose `scene.weather` is `storm`, and only S05 and S06 carry it.
- The verdict colours (`--pass`, `--fail`, `--conditional`, `--undefined`, `--pending` in `style.css`) are used only on badges, chips and the progress strip, never on a scene material.
- Every number shown comes from `claims.json` or `cycle.json`. All DOM text is set with `textContent`; no `innerHTML` anywhere under `viewer/`.
- No physical quantity is hard-coded in JavaScript or Python. Display choices (colours, fade times, bloom strength, the 4 m placeholder cube, the prologue path) are allowed and are marked with a comment `// display choice` or `# display choice`.
- `viewer/` JavaScript stays under 150 KB unminified in total.
- Python: no new dependency. Tests run with `uv run pytest -q -W error` and must pass at every commit. Generated files (`viewer/data/*`) are regenerated on a clean tree after the commit that changes the code or the ledger, and committed separately, so their `manifest.json` records the generating commit (README, "Regenerating the results").
- Commit messages end with the trailer `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- Deliberate simplifications carry a `// ponytail:` (or `# ponytail:`) comment naming the ceiling and the upgrade path.
- Plain prose in comments and docs: no em dashes.

## Review Focus

1. **WebGL 2 missing.** The page shows a one-sentence message under the notice and does nothing else; no exception in the console. (Task 10: browser check with `?nowebgl=1`, which forces the same path.)
2. **A data file is missing or malformed.** `#message` shows the file name and the reason (`data/cycle.json: HTTP 404`, `data/cycle.json: missing key steps`); the notice stays; no blank page. (Task 3: `loadData('nowhere/')` from the console rejects with that message.)
3. **An unknown deep link** (`#S99`, `#foo`) opens the prologue, with no error. (Task 8.)
4. **A space the user hides still has water or gas in it.** The water and gas of a hidden space are hidden with it, and its label too. (Task 6: `model.setHidden(new Set(['grand_gallery']))` during S12 leaves `state().labels` without the Gallery's labels and the water skin invisible.)
5. **A phone-width window (375 px) during the ride.** The canvas resizes, the caption wraps under 100 % width, nothing scrolls horizontally, the notice stays on top. (Task 10: the 375 px browser check.)

## File Structure

```
ledger/
  species.yaml              NEW   the compounds the video names: id, formula, name, phase, colour, produced_by
  cycle.yaml                MOD   top level becomes {prologue, steps}; steps gain path, scene, species, reaction; actors gain species; coat actor
pyramid/
  species.py                NEW   strict loader for species.yaml; status of a species from its producing step's verdict
  viewer_data.py            MOD   cycle_payload converts paths, attaches species payloads with status, validates; manifest loses "fields"
tests/
  test_species.py           NEW
  test_viewer_data.py       MOD   cycle tests rewritten for the new shape; interior flag recomputed from each step's actors and claim spaces
viewer/
  index.html                REWRITE  notice, #stage, #hud, #inspector (empty mount for V2), #message, import map
  style.css                 REWRITE  tokens, full-screen layout, HUD card, strip, phone rules
  app.js                    NEW   boot: load data, store, renderer, environment, materials, model, actors, ride, player, HUD; window.viewer
  store.js                  NEW   createStore, readUrl, DEFAULT_STATE
  data/load.js              NEW   loadData, validateCycle, validateClaims
  render/renderer.js        NEW   createRenderer: WebGLRenderer, camera, OrbitControls, CSS2DRenderer, EffectComposer, tiers, loop, measure
  render/environment.js     NEW   createEnvironment: Sky, sun, PMREM, ground, fog; interior and storm mixes
  render/materials.js       NEW   createMaterials: stone, glass, bedrock, space, water, gas, hatch, update
  render/model.js           NEW   loadModel: glTF, registry, double-drawn masonry, picking, hidden set, clipping, interior mix
  render/actors.js          NEW   createActors: water, gas, lightning, placeholder, field, coat, species labels
  tour/camera.js            NEW   createRide: Catmull-Rom path, easing, pause on input, resume
  tour/player.js            NEW   createPlayer, timelineOf: clock, prologue + 31 steps, step changes, scene flags, hash
  hud/cinematic.js          NEW   mountCinematic: caption card, progress strip, controls, play overlay, keyboard
  main.js scene.js timeline.js panel.js   DELETED in Task 10
viewer/data/                GENERATED  claims.json, cycle.json, manifest.json, interior.glb, interior_alt.glb (regenerated in Task 2)
README.md                   MOD   viewer section (Task 10)
```

## Shared Interfaces

Every task writes against these names and shapes exactly. A task may add private helpers; it may not rename or reshape anything here.

### Python

`pyramid/species.py`

```python
@dataclass(frozen=True)
class Species:
    id: str
    formula: str        # Unicode subscripts, for display: "SO₂"
    name: str
    phase: str          # "gas" | "liquid" | "solid"
    colour: str         # "#rrggbb"
    produced_by: str | None   # a step id of ledger/claims.yaml, or None for an input

SPECIES_FILE = REPO_ROOT / "ledger" / "species.yaml"

def load_species(path: Path = SPECIES_FILE, step_ids: set[str] | None = None) -> dict[str, Species]
    # strict, in the style of pyramid/ledger.py: the file is a list of mappings; unknown keys,
    # missing keys, wrong types, a phase outside the three words, a colour that is not #rrggbb,
    # a duplicate id, or a produced_by not in step_ids (when given) raise LedgerError naming the entry.

def species_status(species: Species, verdicts: dict[str, str]) -> str
    # "claimed" if verdicts[produced_by] in ("fail", "undefined"); "conditional" if it is "conditional";
    # "plain" otherwise (pass, pending, or no producing step).

def species_payload(species: Species, verdicts: dict[str, str]) -> dict
    # {"id", "formula", "name", "phase", "colour", "status"}
```

`ledger/species.yaml` (a list; display colours are display choices):

| id | formula | name | phase | colour | produced_by |
|---|---|---|---|---|---|
| h2s | H₂S | hydrogen sulfide | gas | #9fd3a1 | null |
| so2 | SO₂ | sulfur dioxide | gas | #d9c24a | S02 |
| air | O₂ + N₂ | air | gas | #bcd6e6 | null |
| so3 | SO₃ | sulfur trioxide | gas | #e08a3c | S16 |
| water | H₂O | water | liquid | #2f86d6 | null |
| sulfurous_acid | H₂SO₃ | sulfurous acid | liquid | #4f9fd0 | S19 |
| sulfuric_acid | H₂SO₄ | dilute sulfuric acid | liquid | #c25b5b | S20 |
| calcium_sulfate | CaSO₄ | calcium sulfate | solid | #efe6cf | S23 |
| hydrogen_chloride | HCl | hydrogen chloride | gas | #a8e0a0 | S27 |

`ledger/cycle.yaml` (hand-authored data; Task 2 rewrites it with a one-off script and commits the result):

```yaml
prologue:
  duration: 6.0
  path:                      # project frame, as every camera in this file
    - {position: [620, 520, 150], target: [0, 102, 17]}     # north-east, far out; the entrance is on the north face (project Y north)
    - {position: [380, 330, 90], target: [0, 102, 17]}
    - {position: [230, 210, 45], target: [0, 102, 17]}
steps:
  - id: S01
    title: "..."
    duration: 5.0
    path:                    # 2 to 4 keyframes; the first is plan A's camera
      - {position: [x, y, z], target: [x, y, z]}
      - {position: [x, y, z], target: [x, y, z]}
    scene: {interior: false, weather: clear}     # weather: clear | storm; storm on S05 and S06 only
    species: [so2]           # species ids the step's statement involves; [] allowed
    reaction: {equation: "2 SO₂ + O₂ → 2 SO₃", timestamp: "P2 00:12:34", note: "as stated"}   # reaction steps only
    actors:
      - {type: water, space: grand_gallery, from: 0.0, to: 0.25, species: [water]}
      - {type: gas, path: [kings_chamber, antechamber], species: [so2, air]}
      - {type: placeholder, kind: drain, at: [x, y, z], label: "Gallery drain: not specified by the hypothesis"}
      - {type: lightning}
      - {type: field, slice: "fields/e19_s04.png"}
      - {type: coat, space: grand_gallery}
```

Rules: `path` has 2 to 4 keyframes; the second keyframe of every step is the first orbited by +30 degrees about the vertical axis through its target and brought 10 percent closer (a display choice, generated once by Task 2's script so the yaml stays hand-editable); `scene.interior` is true exactly when the step has an actor of type `water`, `placeholder` or `coat`, or a `gas` actor whose first path space is one of the step's claim `spaces` in `ledger/claims.yaml` (a step that draws, or acts on, something inside the stone is an interior step; a gas tint that merely persists from an earlier step in a space the claim does not name does not count; the camera may stand outside looking in, and the glass cutaway is what lets it see); so S03 and S06 to S26 are interior and S01, S02, S04, S05, S27 to S31 are exterior; `species` ids exist in `species.yaml`; `gas` and `water` actors carry `species` (at least one id) and no `color`; `reaction` is present on exactly S02, S16, S19, S20, S21, S23 and S27, with the equations of the chemistry spec's section 3.2 (S02's equation text is "not stated by the hypothesis"); the `coat` actor appears in S23 on `grand_gallery` and `queens_chamber`.

`pyramid/viewer_data.py`

```python
def cycle_payload(ledger: Ledger, curves: dict[str, list[tuple[float, float]]],
                  species: dict[str, Species], verdicts: dict[str, str]) -> dict
    # {"notice": NOTICE,
    #  "prologue": {"duration": 6.0, "path": [{"position": [...viewer], "target": [...viewer]}, ...]},
    #  "steps": [{"id", "title", "duration", "path": [...viewer], "scene": {"interior", "weather"},
    #             "species": [species_payload...], "reaction"?: {...}, "actors": [...]}, ...],
    #  "curves": curves}
    # Actors: water/gas "species" become lists of species payloads; placeholder "at" converted; others unchanged.
    # Raises LedgerError: "cycle.yaml: S01 is not a claim id", "cycle.yaml: S03: path needs 2 to 4 keyframes",
    # "cycle.yaml: S03: unknown species xyz", "cycle.yaml: S03: gas actor needs species",
    # "cycle.yaml: S03: weather must be clear or storm".
```

`main()` loads species with `load_species(step_ids=set(ledger.claims))`, passes `screening.verdicts(...)` to `cycle_payload`, and no longer writes `manifest.fields` or creates `viewer/data/fields/`.

### JavaScript

All modules are ES modules. Positions are viewer coordinates (x east, y up, z south), as `cycle.json` carries them.

`viewer/store.js`

```js
export const DEFAULT_STATE = {
  mode: 'cinematic',          // 'cinematic' | 'inspector' (inspector is plan V2; the key exists now)
  case: 'claim',              // 'claim' | a case id (V2)
  stepIndex: -1,              // -1 = prologue, 0..30 = steps
  t: 0,                       // seconds from the start of the prologue
  playing: false,
  quality: 'medium',          // 'low' | 'medium' | 'high'
  layers: { masonry: 1, bedrock: 1, hidden: new Set() },   // opacities 0..1; hidden = space names switched off
  cutaway: { on: false, axis: 'ns', position: 0.5 },        // V2 uses it; the key exists now
  picked: null,
  reading: 'survey',          // 'survey' | 'alternative'
  hud: { visible: true },
  reducedMotion: false,       // from matchMedia('(prefers-reduced-motion: reduce)')
  riding: true,               // false while the user has taken the camera
  interior: false,            // the current step's scene.interior
  weather: 'clear',           // the current step's scene.weather
};
export function createStore(initial = DEFAULT_STATE)
  // -> { get(): state, set(patch: object): void, subscribe(fn): unsubscribe }
  // set merges one level deep for the object keys layers, cutaway and hud, replaces everything else,
  // and calls each subscriber synchronously as fn(next, prev, changed: Set<string>) only when a key changed.
export function readUrl(location)
  // -> { stepId: string | null, mode: 'cinematic' | 'inspector', quality: 'low' | 'medium' | 'high' | null, nowebgl: boolean }
  // from location.hash ('#S16' -> 'S16'; '' or unknown form -> null) and location.search (?mode=, ?quality=, ?nowebgl=1)
```

`viewer/data/load.js`

```js
export async function loadData(base = 'data/')
  // -> { claims, cycle, manifest }; rejects with Error(`${base}cycle.json: HTTP 404`) or
  // Error(`${base}cycle.json: missing key steps`) (first missing key named).
  // claims.json stores its claims as a LIST of {id, statement, ...}; loadData re-keys it so that
  // claims.claims is an object by id (claims.claims.S07.statement). claims.spaces is already keyed by name.
  // Among S01 to S31 the statuses today are 1 pass, 6 conditional, 7 fail, 2 undefined, 15 pending;
  // a check that counts ticks derives the expected counts from the data, never from a typed number.
export function validateCycle(cycle)      // throws Error('cycle.json: ...') on a missing key; returns cycle
export function validateClaims(claims)    // same for claims.json ('claims', 'spaces', 'manifest')
```

`viewer/render/renderer.js`

```js
export const TIERS = {
  low:    { pixelRatio: 1,   shadowMap: 0,    bloom: false, particles: false },
  medium: { pixelRatio: 1.5, shadowMap: 1024, bloom: true,  particles: false },
  high:   { pixelRatio: 2,   shadowMap: 2048, bloom: true,  particles: true },
};
export function createRenderer(stage, store)
  // stage: the #stage element. Appends the canvas and the CSS2D layer (div.labels).
  // -> { renderer, camera, controls, labels, scene, composer, resize(), setQuality(tier),
  //      start(onFrame), measure(seconds) -> Promise<medianFrameMs>, lastDt, dispose() }
  // camera: PerspectiveCamera, fov 45, near/far set by frame rules; the 5:4 width rule of plan A on narrow stages.
  // start(onFrame): setAnimationLoop; each frame dt = min(clock delta, 0.1); onFrame(dt); controls.update();
  //   renders through the composer (RenderPass -> UnrealBloomPass when the tier has bloom -> SMAAPass -> OutputPass)
  //   and labels. OutputPass (three/addons/postprocessing/OutputPass.js) comes last: it applies the tone mapping and
  //   the sRGB conversion, without which the composer output is dark and linear in r170.
  // measure(seconds) resolves NaN when no frame was drawn in that time (a hidden page); callers keep the current tier then.
  // setQuality also sets the shadow map size of every DirectionalLight in the scene; the environment calls it once
  //   after adding its sun.
  // setQuality(tier): applies TIERS[tier] (pixel ratio capped by devicePixelRatio, shadow map size, bloom pass enabled).
  // The renderer subscribes to store.quality and calls setQuality itself.
```

`viewer/render/environment.js`

```js
export const FADE_SECONDS = 1.5;     // display choice: look and weather cross-fade time
export function createEnvironment(scene, rendererApi, store)
  // -> { mix: { interior: 0..1, storm: 0..1 }, update(dt, cameraInside), sun, ground, sky }
  // cameraInside: boolean from app.js each frame, true when the camera position lies inside model.bounds; the ground
  // fades out only while the camera is inside (eased over FADE_SECONDS), so an exterior shot of an interior step
  // (S06, filmed from outside during the strike) keeps its plateau.
  // Sky addon with a sun; PMREM environment from the sky; DirectionalLight sun with a shadow map;
  // ground: a plane at y = 0 to the horizon (sand colour, receives shadows); scene.fog.
  // Subscribes to store.interior and store.weather and moves mix.interior / mix.storm toward 0 or 1
  // at 1/FADE_SECONDS per second in update(dt) (instantly when store.reducedMotion).
  // Applies the mixes every frame: sun elevation and intensity, sky turbidity, fog density,
  // ground opacity and fog density both scaled by (1 - mix.interior * inside), where inside eases toward
  // cameraInside: an interior step filmed from outside keeps its plateau and its horizon haze.
```

`viewer/render/materials.js`

```js
export function createMaterials()
  // -> { stone(), glass(), bedrock(), space(), water(plane), gas(plane, colourHex), hatch(material, colourHex), update(dt) }
  // stone(): MeshStandardMaterial, onBeforeCompile adds triplanar value noise (grain) in object space; transparent, opacity 1
  // glass(): ShaderMaterial, Fresnel edge glow, transparent, depthWrite false, side DoubleSide, opacity uniform
  // bedrock(): MeshStandardMaterial, darker stone, transparent
  // space(): MeshStandardMaterial, pale emissive (the schematic interior surface), DoubleSide, flatShading
  // water(plane): MeshStandardMaterial, blue, transparent 0.8, clippingPlanes [plane], onBeforeCompile ripple +
  //   a brighter band within 0.3 m below the free surface (uniform uLevel set by the actor each frame)
  // gas(plane, colourHex): ShaderMaterial, view-dependent (Fresnel) haze with drifting noise, additive blending,
  //   transparent, depthWrite false, clippingPlanes [plane]
  // hatch(material, colourHex): mutates material.onBeforeCompile so the fragment colour alternates with a darker
  //   shade in screen-space diagonal stripes, 8 px pitch, half duty; returns the material
  // update(dt): advances the uTime uniform of every material created here
```

`viewer/render/model.js`

```js
export async function loadModel(url, scene, materials, store)
  // -> model = { root, spaces: Map<name, Mesh>, shell: { stone, glass, bedrock }, bounds: Box3, masonryBounds: Box3, apexY,
  //              pickAt(ndc: Vector2, camera) -> name | null, setHidden(names: Set), setShell({masonry, bedrock}),
  //              setInterior(k), setClipping(planes | null), dispose() }
  // The masonry mesh is drawn twice: shell.stone (materials.stone(), opacity 1 - k) and shell.glass
  // (materials.glass(), opacity k * 0.55); shell.bedrock opacity (1 - k) * layers.bedrock + k * 0.08.
  // setInterior(k) sets those opacities, each also scaled by store.layers.masonry (so setShell({masonry}) has an
  // effect; identical at the default of 1); the environment's mix.interior is passed in every frame by app.js.
  // bounds = masonry ∪ bedrock; masonryBounds = masonry alone; apexY = masonryBounds.max.y.
  // Spaces get materials.space(). setHidden applies store.layers.hidden (mesh.visible), kept across a reload.
  // The model subscribes to store.layers and store.reading (reading swaps interior.glb / interior_alt.glb).
```

`viewer/render/actors.js`

```js
export function createActors({ scene, model, materials, store, cycle, tiers })
  // -> { build(step | null), update({ u, dt, source }), dispose(), state() }
  // build(step): removes the previous step's objects and creates this step's actors (null clears, for the prologue).
  // update({u, dt, source}): u in 0..1 within the step; source = { fraction(space) -> 0..1 } (claim mode: the player's)
  // Actor types: water (clipped skin + uLevel), gas (haze skin above any water in the space; particles on tiers
  //   with particles), lightning (Line2 bolt from the apex, two strokes at u 0.30..0.42 and 0.48..0.56, flash light),
  //   placeholder (4 m dashed cube + CSS2D label, renderOrder 3, depthTest false), field (always the CSS2D label
  //   "Solver result pending" at the masonry centre), coat (outline skin on the space; Task 9),
  //   species labels (one CSS2D label per occupied space: formulas joined by " · ", "(claimed)" after a species
  //   whose status is "claimed"; Task 9).
  // Skins are children of the space mesh (share visibility; picking never sees them).
  // state(): { water: {space: fraction}, levels: {space: y}, labels: [text, ...] }
```

`viewer/tour/camera.js`

```js
export const RESUME_SECONDS = 1;   // display choice
export function createRide(camera, controls, store)
  // -> { setPath(keyframes, { from }), update(dt, u), pause(), resume(), pose(), drift(on), get riding() }
  // pose(): { position: Vector3, target: Vector3 } clones of the camera's current pose, which the player
  // passes as `from` on a step change while playing. The prologue, the very first path, and any jump made
  // while paused (strip, keys, hash) take from: null and cut to the first keyframe.
  // drift(on): the prologue's slow drift (controls.autoRotate, autoRotateSpeed DRIFT_SPEED 0.3, a display choice);
  // no-op under reducedMotion; while drifting update() leaves the camera alone; switching it off glides the
  // camera back onto the path over RESUME_SECONDS. The player owns the switch (on on the prologue while not playing).
  // keyframes: [{position: [x,y,z], target: [x,y,z]}, ...] (viewer coords); from: {position: Vector3, target: Vector3} | null,
  // the previous pose, prepended so the ride is continuous. Two CatmullRomCurve3('centripetal') curves.
  // update(dt, u): while riding, camera.position and controls.target follow the curves at smoothstep(u);
  //   while not riding, nothing. resume(): tweens back to the curve point over RESUME_SECONDS, then riding = true.
  // pointerdown or touchstart on the canvas calls pause() and store.set({riding: false}); resume() sets riding true.
  // reducedMotion: setPath places the camera at the first keyframe at once; update does nothing.
```

`viewer/tour/player.js`

```js
export function timelineOf(cycle)
  // -> { entries: [{ id: 'prologue', duration, path, scene: {interior: false, weather: 'clear'}, actors: [] }, ...cycle.steps],
  //      starts: number[], total: number }
export function createPlayer({ store, cycle, actors, ride, claims })
  // -> { play(), pause(), toggle(), seek(t), goto(index), gotoId(id), tick(dt), total, state() }
  // index: -1 prologue, 0..30 steps (entries[index + 1]). On a step change: actors.build(step or null for the prologue),
  //   ride.drift(index === -1 && !playing), ride.setPath(entry.path, {from: playing ? ride.pose() : null}),
  //   store.set({stepIndex, interior, weather}),
  //   history.replaceState with '#' + id (prologue: '#').
  // tick(dt): if playing, t += dt (stops at total); recomputes index and u; calls actors.update({u, dt, source})
  //   with source.fraction(space) = from + (to - from) * u from the step's water actors (0 for others); ride.update(dt, u).
  // gotoId(id): unknown id -> goto(-1). state(): { id, u, playing, t }.
```

`viewer/hud/cinematic.js`

```js
export function mountCinematic(root, { store, cycle, claims, player, ride })
  // -> { unmount() }
  // Builds, inside root: .caption (step id + title, the claim statement from claims.claims[id].statement,
  // the verdict badge .badge.status-<status>, the basis sentence), .strip (one tick per step, class status-<status>,
  // the current one .current; dragging scrubs through player.seek), .controls (Back, Play/Pause, Next, Resume ride
  // when !store.riding, Fullscreen, Hide HUD), and .overlay with the button "Play the claimed cycle" on the prologue.
  // Keyboard: Space, ArrowLeft, ArrowRight, I (sets store.mode, no effect in V1), F, H, Escape.
  // On the prologue while not playing, controls.autoRotate is on (autoRotateSpeed 0.3, a display choice): the slow
  // drift of spec 5.2; it is switched off when play starts or the step changes (the player owns that switch).
  // Subscribes to the store; all text via textContent; the prologue caption is the title and cycle.notice.
```

`viewer/app.js`

```js
// Boot order: readUrl -> loadData (on failure: #message textContent = error.message; stop) -> createStore
// (quality from URL, else localStorage 'viewer.quality' in a try block, else 'medium'; reducedMotion from matchMedia)
// -> WebGL 2 check (or ?nowebgl=1): on failure #message = "This page needs WebGL 2."; stop
// -> createRenderer -> createEnvironment -> createMaterials -> loadModel -> createActors -> createRide -> createPlayer
// -> mountCinematic -> start(frame) -> measure(2) sets quality unless the URL or localStorage fixed it -> gotoId(stepId).
// frame(dt): environment.update(dt, model.bounds.containsPoint(camera.position)); materials.update(dt);
//            model.setInterior(environment.mix.interior); player.tick(dt).
window.viewer = { store, player, actors, model, environment, state,    // state() merges player.state(), actors.state(),
                  rendererApi, ride, camera, claims, cycle, manifest } // and { mode, quality, interior, weather, riding, lastDt };
                                                                       // the extra keys exist for the browser checks
```

`viewer/index.html` body, in order: `<div id="notice" role="note">`, `<p id="message" role="alert" hidden>`, `<main id="stage">` (canvas and labels are appended by the renderer), `<div id="hud">`, `<div id="inspector" hidden>`, `<script type="module" src="app.js">`.

## Browser checks: how every viewer task verifies itself

Start the server with the Browser pane's `preview_start` and `name: "viewer"` (configured in `.claude/launch.json`), then open `http://localhost:8765/?quality=low` (deterministic, no probe) at a 1280 × 800 viewport. Drive the page with the JavaScript tool through `window.viewer`: `viewer.player.gotoId('S12')`, `viewer.player.seek(t)`, `viewer.store.set({...})`, and read `viewer.state()`. Take a screenshot for anything visual. The page must log no error of its own to the console (the tool's own "probe-console-reader" entry does not count). Each task's steps say what `viewer.state()` must contain.

## Executor notes

- Tasks 1 and 2 are Python and change the data contract; every viewer task reads the regenerated `viewer/data/cycle.json`, so Task 2's regeneration commit must exist before Task 3 starts.
- Tasks 3 to 8 replace the viewer in place. Until Task 7 the page shows the new scene without the cycle player; that is expected within the milestone. The old modules (`main.js`, `scene.js`, `timeline.js`, `panel.js`) are left in place, unreferenced, until Task 10 deletes them.
- Shader code is the riskiest part of this plan. An implementer who finds a shader rejected by the GPU fixes the smallest thing that compiles, keeps the look described, and records the deviation in the report.
- Tests of physical content stay in Python. JavaScript is verified in the browser as described above; there is no JavaScript test runner.

---

### Task 1: Species table and loader

**Files:**
- Create: `ledger/species.yaml`
- Create: `pyramid/species.py`
- Test: `tests/test_species.py` (create)

**Interfaces:**
- Consumes: `LedgerError` and the strict-loader helpers `_entries`, `_get`, `_is_text`, `_known_keys` of `pyramid/ledger.py` (existing, unchanged; same package, so the loader reuses them instead of copying them); `REPO_ROOT` from `pyramid/__init__.py`; in the tests only, `STATUSES` and `load` from `pyramid/ledger.py` and `screening.verdicts`, `screening.all_results` from `pyramid/screening.py`.
- Produces (exactly as the header's Shared Interfaces): `Species` (frozen dataclass: `id`, `formula`, `name`, `phase`, `colour`, `produced_by`), `SPECIES_FILE`, `load_species(path=SPECIES_FILE, step_ids=None) -> dict[str, Species]`, `species_status(species, verdicts: dict[str, str]) -> str` returning `"claimed"`, `"conditional"` or `"plain"`, `species_payload(species, verdicts) -> {"id", "formula", "name", "phase", "colour", "status"}`; and `ledger/species.yaml` with the nine entries of the header's table. Task 2 imports `Species`, `load_species` and `species_payload`.

The loader's error messages (asserted verbatim by the tests) follow `pyramid/ledger.py`'s format, prefixed with the file name the way Task 2's cycle messages are: `species.yaml entry 1: missing id`, `species.yaml: duplicate id: so2`, `species.yaml: so2: unknown key 'color'`, `species.yaml: so2: missing name`, `species.yaml: so2: formula must be text`, `species.yaml: so2: phase must be gas, liquid or solid, not 'plasma'`, `species.yaml: so2: colour must be #rrggbb in lower-case hex, not 'yellow'`, `species.yaml: so2: produced_by S99 is not a step id`, `species.yaml: must be a YAML list of mappings`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_species.py`:

```python
"""Tests for the species table and the marking rule, checked against the plan header's contract."""
import re
from pathlib import Path

import pytest
import yaml

from pyramid import REPO_ROOT, screening
from pyramid.ledger import STATUSES, LedgerError, load
from pyramid.species import SPECIES_FILE, Species, load_species, species_payload, species_status

IDS = ["h2s", "so2", "air", "so3", "water", "sulfurous_acid", "sulfuric_acid", "calcium_sulfate", "hydrogen_chloride"]


def test_the_real_table_has_the_nine_compounds_the_video_names_in_order():
    claims = load().claims
    species = load_species(step_ids=set(claims))
    assert SPECIES_FILE == REPO_ROOT / "ledger" / "species.yaml"
    assert list(species) == IDS
    assert species["so2"] == Species("so2", "SO₂", "sulfur dioxide", "gas", "#d9c24a", "S02")
    # what each step makes in the claimed cycle; the marking rule reads nothing else
    assert {key: entry.produced_by for key, entry in species.items()} == {
        "h2s": None, "so2": "S02", "air": None, "so3": "S16", "water": None,
        "sulfurous_acid": "S19", "sulfuric_acid": "S20", "calcium_sulfate": "S23", "hydrogen_chloride": "S27",
    }
    for entry in species.values():
        assert entry.produced_by is None or entry.produced_by in claims, entry.id
        assert not re.search(r"[0-9]", entry.formula), entry.id   # subscripts are Unicode, never ASCII digits


SO2 = {"id": "so2", "formula": "SO₂", "name": "sulfur dioxide", "phase": "gas", "colour": "#d9c24a", "produced_by": "S02"}


def write(tmp_path: Path, entries) -> Path:
    path = tmp_path / "species.yaml"
    path.write_text(yaml.safe_dump(entries, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def without(entry: dict, key: str) -> dict:
    return {name: value for name, value in entry.items() if name != key}


@pytest.mark.parametrize("entries, message", [
    ([{**SO2, "color": "#d9c24a"}], "species.yaml: so2: unknown key 'color'"),
    ([without(SO2, "name")], "species.yaml: so2: missing name"),
    ([without(SO2, "produced_by")], "species.yaml: so2: missing produced_by"),
    ([without(SO2, "id")], "species.yaml entry 1: missing id"),
    ([{**SO2, "formula": 2}], "species.yaml: so2: formula must be text"),
    ([{**SO2, "phase": "plasma"}], "species.yaml: so2: phase must be gas, liquid or solid, not 'plasma'"),
    ([{**SO2, "colour": "yellow"}], "species.yaml: so2: colour must be #rrggbb in lower-case hex, not 'yellow'"),
    ([{**SO2, "colour": "#D9C24A"}], "species.yaml: so2: colour must be #rrggbb in lower-case hex, not '#D9C24A'"),
    ([SO2, SO2], "species.yaml: duplicate id: so2"),
    ([{**SO2, "produced_by": "S99"}], "species.yaml: so2: produced_by S99 is not a step id"),
    ({"so2": SO2}, "species.yaml: must be a YAML list of mappings"),
])
def test_a_broken_table_is_rejected_naming_the_entry(tmp_path, entries, message):
    with pytest.raises(LedgerError, match=re.escape(message)):
        load_species(write(tmp_path, entries), step_ids={"S02"})


def test_produced_by_is_checked_against_the_steps_only_when_they_are_given(tmp_path):
    loaded = load_species(write(tmp_path, [{**SO2, "produced_by": "S99"}]))
    assert loaded["so2"].produced_by == "S99"


MARKING = [("fail", "claimed"), ("undefined", "claimed"), ("conditional", "conditional"),
           ("pass", "plain"), ("pending", "plain")]


def test_the_marking_cases_cover_every_verdict_word():
    assert sorted(verdict for verdict, _ in MARKING) == sorted(STATUSES)


@pytest.mark.parametrize("verdict, status", MARKING)
def test_a_species_takes_its_status_from_the_verdict_of_the_step_that_produces_it(verdict, status):
    so3 = load_species()["so3"]   # produced by S16
    assert species_status(so3, {"S16": verdict}) == status
    # another step's verdict does not touch it
    assert species_status(so3, {"S16": "pass", "S20": verdict}) == "plain"


def test_an_input_is_plain_whatever_the_verdicts():
    water = load_species()["water"]   # produced_by None
    assert species_status(water, dict.fromkeys(load().claims, "fail")) == "plain"


def test_the_payload_is_the_table_entry_without_produced_by_plus_the_status():
    assert species_payload(load_species()["so3"], {"S16": "fail"}) == {
        "id": "so3", "formula": "SO₃", "name": "sulfur trioxide", "phase": "gas", "colour": "#e08a3c",
        "status": "claimed",
    }


def test_with_the_screening_as_it_stands_the_products_of_failed_steps_are_marked_claimed():
    """S16, S20 and S27 fail in the Tier 0 screening; update this set when a verdict changes."""
    led = load()
    statuses = {claim: status for claim, (status, _) in screening.verdicts(led, screening.all_results(led)).items()}
    marked = {key: species_status(entry, statuses) for key, entry in load_species(step_ids=set(led.claims)).items()}
    assert {key for key, status in marked.items() if status != "plain"} == {"so3", "sulfuric_acid", "hydrogen_chloride"}
    assert {marked[key] for key in ("so3", "sulfuric_acid", "hydrogen_chloride")} == {"claimed"}
```

The last test pins the screening as it stands on 2026-10-10 (S16, S20 and S27 fail; S10 and S31 are undefined but produce nothing). The chemistry spec's section 3.3 names only sulfur trioxide and dilute sulfuric acid because it predates S27's verdict; the rule, not the spec's sentence, decides, so hydrogen chloride is marked too.

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest -q -W error tests/test_species.py`
Expected: a collection error, `ModuleNotFoundError: No module named 'pyramid.species'`, and `1 error`.

- [ ] **Step 3: Write the species table**

Create `ledger/species.yaml`:

```yaml
# The compounds the source video names, for the viewer's chemistry display. Authored by hand.
# Source: docs/superpowers/specs/2026-10-10-chemistry-display-kings-chamber-design.md section 3.1.
#
# Keys: id; formula, with Unicode subscripts, for display; name; phase (gas, liquid or solid);
# colour; produced_by, the step of ledger/claims.yaml that makes the compound in the claimed
# cycle, or null for an input. pyramid/species.py loads this file and marks a compound "claimed"
# when its producing step's verdict is fail or undefined.
#
# The colours are display choices, not data: they tell compounds apart and are never verdicts.
# Limestone (CaCO₃) and sodium chloride (NaCl) appear only inside equations: the first is the
# wall itself, the second is outside the modelled interior.

- {id: h2s, formula: "H₂S", name: "hydrogen sulfide", phase: gas, colour: "#9fd3a1", produced_by: null}
- {id: so2, formula: "SO₂", name: "sulfur dioxide", phase: gas, colour: "#d9c24a", produced_by: S02}
- {id: air, formula: "O₂ + N₂", name: "air", phase: gas, colour: "#bcd6e6", produced_by: null}
- {id: so3, formula: "SO₃", name: "sulfur trioxide", phase: gas, colour: "#e08a3c", produced_by: S16}
- {id: water, formula: "H₂O", name: "water", phase: liquid, colour: "#2f86d6", produced_by: null}
- {id: sulfurous_acid, formula: "H₂SO₃", name: "sulfurous acid", phase: liquid, colour: "#4f9fd0", produced_by: S19}
- {id: sulfuric_acid, formula: "H₂SO₄", name: "dilute sulfuric acid", phase: liquid, colour: "#c25b5b", produced_by: S20}
- {id: calcium_sulfate, formula: "CaSO₄", name: "calcium sulfate", phase: solid, colour: "#efe6cf", produced_by: S23}
- {id: hydrogen_chloride, formula: "HCl", name: "hydrogen chloride", phase: gas, colour: "#a8e0a0", produced_by: S27}
```

- [ ] **Step 4: Write the loader**

Create `pyramid/species.py`:

```python
"""Load ledger/species.yaml, and mark each compound by the verdict of the step that produces it."""
import re
from dataclasses import dataclass
from pathlib import Path

from pyramid import REPO_ROOT
# the strict loader's private helpers, shared with ledger.py on purpose: one set of rules and messages
from pyramid.ledger import LedgerError, _entries, _get, _is_text, _known_keys

SPECIES_FILE = REPO_ROOT / "ledger" / "species.yaml"
PHASES: tuple[str, ...] = ("gas", "liquid", "solid")
_COLOUR = re.compile(r"#[0-9a-f]{6}")


@dataclass(frozen=True)
class Species:
    id: str
    formula: str        # Unicode subscripts, for display: "SO₂"
    name: str
    phase: str          # "gas" | "liquid" | "solid"
    colour: str         # "#rrggbb"
    produced_by: str | None   # a step id of ledger/claims.yaml, or None for an input


def _is_step_or_none(value) -> bool:
    return value is None or _is_text(value)


def load_species(path: Path = SPECIES_FILE, step_ids: set[str] | None = None) -> dict[str, Species]:
    """The species by id, in file order. With step_ids, every produced_by must be one of them."""
    species: dict[str, Species] = {}
    for number, entry in enumerate(_entries(path.read_bytes(), "species.yaml"), start=1):
        key = _get(entry, "id", f"species.yaml entry {number}", _is_text, "text")
        if key in species:
            raise LedgerError(f"species.yaml: duplicate id: {key}")
        where = f"species.yaml: {key}"
        _known_keys(entry, where, Species)
        phase = _get(entry, "phase", where, _is_text, "text")
        if phase not in PHASES:
            raise LedgerError(f"{where}: phase must be gas, liquid or solid, not {phase!r}")
        colour = _get(entry, "colour", where, _is_text, "text")
        if not _COLOUR.fullmatch(colour):
            raise LedgerError(f"{where}: colour must be #rrggbb in lower-case hex, not {colour!r}")
        produced_by = _get(entry, "produced_by", where, _is_step_or_none, "a step id or null")
        if produced_by is not None and step_ids is not None and produced_by not in step_ids:
            raise LedgerError(f"{where}: produced_by {produced_by} is not a step id")
        species[key] = Species(
            id=key,
            formula=_get(entry, "formula", where, _is_text, "text"),
            name=_get(entry, "name", where, _is_text, "text"),
            phase=phase,
            colour=colour,
            produced_by=produced_by,
        )
    return species


def species_status(species: Species, verdicts: dict[str, str]) -> str:
    """'claimed' when the producing step fails or is undefined, 'conditional' when it is conditional, else 'plain'.

    The rule looks only at the step that produces the species: an input (produced_by None) is always plain.
    """
    verdict = verdicts.get(species.produced_by) if species.produced_by else None
    if verdict in ("fail", "undefined"):
        return "claimed"
    if verdict == "conditional":
        return "conditional"
    return "plain"


def species_payload(species: Species, verdicts: dict[str, str]) -> dict:
    """One species as cycle.json carries it: the table entry without produced_by, plus its status."""
    return {
        "id": species.id,
        "formula": species.formula,
        "name": species.name,
        "phase": species.phase,
        "colour": species.colour,
        "status": species_status(species, verdicts),
    }
```

`verdicts` is the verdict word per claim id (`dict[str, str]`). `screening.verdicts` returns `(status, basis)` pairs; callers reduce them with `{claim: status for claim, (status, _) in decided.items()}` (Task 2's `main()` does).

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run pytest -q -W error tests/test_species.py`
Expected: `22 passed`.

Run: `uv run pytest -q -W error`
Expected: `282 passed, 1 xfailed` (260 passed and 1 xfailed before this task, plus these 22), no warnings.

- [ ] **Step 6: Commit**

```bash
git add ledger/species.yaml pyramid/species.py tests/test_species.py
git commit -F - <<'EOF'
Add the species table and its strict loader, with the marking rule

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
```

---

### Task 2: Cycle additions and viewer data

**Files:**
- Modify: `ledger/cycle.yaml` (rewritten once by a one-off script; the script itself is never committed)
- Modify: `pyramid/viewer_data.py`
- Modify: `tests/test_viewer_data.py` (the cycle tests rewritten for the new shape; the claims tests unchanged)
- Regenerate, in a separate commit: `viewer/data/claims.json`, `viewer/data/cycle.json`, `viewer/data/manifest.json`
- Scratch, outside the repository: `rewrite_cycle.py` in your scratchpad directory

**Interfaces:**
- Consumes: Task 1's `Species`, `load_species`, `species_payload` (`pyramid/species.py`); `LedgerError`, `Ledger`, `load` (`pyramid/ledger.py`); `to_viewer(x, y, z)` (it lives in `pyramid/geometry/export.py`, not in `frame.py`); `screening.verdicts(ledger, results) -> dict[str, tuple[str, str]]`.
- Produces (exactly as the header's Shared Interfaces): `ledger/cycle.yaml` as `{prologue, steps}`; `cycle_payload(ledger, curves, species, verdicts) -> {"notice", "prologue", "steps", "curves"}` with the five `LedgerError` messages `cycle.yaml: S01 is not a claim id`, `cycle.yaml: S03: path needs 2 to 4 keyframes`, `cycle.yaml: S03: unknown species xyz`, `cycle.yaml: S03: gas actor needs species`, `cycle.yaml: S03: weather must be clear or storm`; `main()` that loads species with `load_species(step_ids=set(led.claims))`, passes the verdict words to `cycle_payload`, writes no `fields` key into `manifest.json` or `claims.json`'s manifest and creates no `viewer/data/fields/`. The regenerated `viewer/data/cycle.json` (prologue; per step `path`, `scene`, `species` as payloads with `status`, `reaction` on seven steps; gas and water actors with species payloads and no `color`; two `coat` actors in S23) is what every viewer task from Task 3 on reads.

What the one-off script does to each step, from the header's rules and this plan's table:
- `path`: the old `camera` becomes the first keyframe; the second is that camera turned +30 degrees about the vertical axis (project Z) through its target and brought 10 percent closer to the target, `v = p - t; v' = 0.9 * (vx cos 30 - vy sin 30, vx sin 30 + vy cos 30, vz); p2 = t + v'`, rounded to 0.01 m (display choice). `camera` is dropped.
- `scene.interior`: true exactly when the step has an actor of type `water`, `placeholder` or `coat`, or a `gas` actor whose first `path` space is one of the step's claim `spaces` in `ledger/claims.yaml` (a gas tint that only persists in a space the claim does not name does not count). The camera position and the glTF play no part. `scene.weather`: `storm` on S05 and S06, `clear` elsewhere.
- `species` per step (from the step statements of `ledger/claims.yaml`): S01 `[h2s]`; S02 `[h2s, so2]`; S03 `[so2]`; S13 `[so2]`; S14 `[air]`; S15 `[so2, air]`; S16 `[so2, air, so3]`; S17 `[so3, so2, air]`; S19 `[so2, water, sulfurous_acid]`; S20 `[sulfurous_acid, air, sulfuric_acid]`; S21 `[so3, water, sulfuric_acid]`; S22 `[so2, so3, water]`; S23 `[sulfuric_acid, calcium_sulfate]`; S26 `[sulfuric_acid, water]`; S27 `[sulfuric_acid, hydrogen_chloride]`; S28 `[sulfuric_acid, hydrogen_chloride]`; S30 `[sulfuric_acid]`; every other step `[]`.
- `reaction` on exactly S02, S16, S19, S20, S21, S23 and S27: the equation of the chemistry spec's section 3.2, the claim's `timestamp` from `ledger/claims.yaml`, and the note `as stated in the video`; S02 has the equation `not stated by the hypothesis` and the note `the video names a conversion without giving it`.
- Actors: a gas actor's `color` becomes `species` (`"#d9c24a"` to `[so2]`, `"#e08a3c"` to `[so3]`, `"#bcd6e6"` to `[air]`); every water actor gains `species: [water]`, except `grand_gallery` in S19 (`[sulfurous_acid, water]`) and `grand_gallery` in S20 to S26 (`[sulfuric_acid, water]`); S23 gains `{type: coat, space: grand_gallery}` and `{type: coat, space: queens_chamber}`.
- The prologue is the header's, as given. The header comment is kept, with its description of the keys brought up to date.

- [ ] **Step 1: Write the one-off generator, outside the repository**

Save this as `rewrite_cycle.py` in the scratchpad directory your session prompt names (any directory outside the repository; never inside it, never committed). The commands below call that directory `SCRATCH` and set it in the same shell command, since shell variables do not carry over between commands.

```python
"""One-off: rewrite ledger/cycle.yaml from plan A's list of steps into V1's {prologue, steps}.

Run once from the repository root:  uv run python "$SCRATCH/rewrite_cycle.py"
Never committed: from then on ledger/cycle.yaml itself is the hand-edited source.
"""
import json
import math
import re
from pathlib import Path

import numpy as np
import yaml

CYCLE = Path("ledger/cycle.yaml")
CLAIMS = Path("ledger/claims.yaml")

# display choice: the plan header's flight from far out in the north-east towards the entrance on the
# north face (project frame: Y north, so the target [0, 102, 17] is on the north face)
PROLOGUE = {
    "duration": 6.0,
    "path": [
        {"position": [620, 520, 150], "target": [0, 102, 17]},
        {"position": [380, 330, 90], "target": [0, 102, 17]},
        {"position": [230, 210, 45], "target": [0, 102, 17]},
    ],
}
ORBIT_DEGREES = 30.0   # display choice: the second keyframe turns this far about the vertical through the target
CLOSER = 0.9           # display choice: and stands at this fraction of the first keyframe's distance
INSIDE = {"water", "placeholder", "coat"}   # actors drawn inside the stone: a step with one is interior
STORM = {"S05", "S06"}  # the steps whose claim states a storm
# species ids each step's statement in ledger/claims.yaml involves; every other step has none
SPECIES = {
    "S01": ["h2s"], "S02": ["h2s", "so2"], "S03": ["so2"], "S13": ["so2"], "S14": ["air"],
    "S15": ["so2", "air"], "S16": ["so2", "air", "so3"], "S17": ["so3", "so2", "air"],
    "S19": ["so2", "water", "sulfurous_acid"], "S20": ["sulfurous_acid", "air", "sulfuric_acid"],
    "S21": ["so3", "water", "sulfuric_acid"], "S22": ["so2", "so3", "water"],
    "S23": ["sulfuric_acid", "calcium_sulfate"], "S26": ["sulfuric_acid", "water"],
    "S27": ["sulfuric_acid", "hydrogen_chloride"], "S28": ["sulfuric_acid", "hydrogen_chloride"],
    "S30": ["sulfuric_acid"],
}
STATED = "as stated in the video"
# step -> (equation, note): docs/superpowers/specs/2026-10-10-chemistry-display-kings-chamber-design.md section 3.2
REACTIONS = {
    "S02": ("not stated by the hypothesis", "the video names a conversion without giving it"),
    "S16": ("2 SO₂ + O₂ → 2 SO₃", STATED),
    "S19": ("SO₂ + H₂O → H₂SO₃", STATED),
    "S20": ("2 H₂SO₃ + O₂ → 2 H₂SO₄", STATED),
    "S21": ("SO₃ + H₂O → H₂SO₄ (into dilute acid)", STATED),
    "S23": ("CaCO₃ + H₂SO₄ → CaSO₄ + H₂O + CO₂", STATED),
    "S27": ("H₂SO₄ + 2 NaCl → Na₂SO₄ + 2 HCl", STATED),
}
GAS = {"#d9c24a": ["so2"], "#e08a3c": ["so3"], "#bcd6e6": ["air"]}   # plan A's gas colours

HEADER = """\
# Choreography of the claimed cycle for the viewer. Authored by hand; it is not a result.
# A prologue, then one entry per step S01 to S31 of ledger/claims.yaml, in order.
#
# Frame: the project frame (origin at the pyramid's centre on the pavement, X east, Y north,
# Z up, metres). pyramid/viewer_data.py converts every camera keyframe and placeholder position
# to viewer coordinates. For the steps inside the pyramid the camera stands east of the passage
# system and looks west, so north is on the right; the wide views of the steps outside it move
# round the pyramid. Each step's first keyframe has the spaces of its step's claim (the "spaces"
# of ledger/claims.yaml) in view on a stage at least 5:4 wide; the viewer keeps that width of
# view on narrower stages. The one exception is S03, a close view of the King's Chamber and its
# inlet: the two shafts in that claim's list run 80 m up to the faces and cannot share a frame
# with a 4 m placeholder.
#
# Each step is complete in itself: its actors list everything drawn during that step, so the
# viewer can jump to any step. Water that only stays where it is has "from" equal to "to".
#
# Keys:
#   prologue     a flight from far out in the north-east to the entrance on the north face before
#                S01: a duration and a path; it carries no claim (display choice)
#   path         2 to 4 camera keyframes {position, target}, ridden over the step's duration. The
#                first is the step's single camera of plan A. The second was generated once from
#                it: turned 30 degrees about the vertical through the target and brought 10 percent
#                closer (display choice). Both may be edited by hand.
#   scene        interior: true exactly when the step has a water, placeholder or coat actor, or a
#                gas actor whose first path space is one of its claim's "spaces" in
#                ledger/claims.yaml; a tint that only persists in a space the claim does not name
#                does not count. The camera may stand outside: it sees in through the glass look
#                (tests/test_viewer_data.py checks the flag against the actors and the claims).
#                weather: clear, or storm on the steps whose claim states a storm (S05 and S06).
#   species      the ids of ledger/species.yaml that the step's statement involves; [] when none
#   reaction     on S02, S16, S19, S20, S21, S23 and S27: the equation as the video states it, the
#                claim's timestamp and a note; "not stated by the hypothesis" where the video
#                names a conversion without giving it (S02)
#
# Actors:
#   water        fill fraction of the space's volume (0 to 1) at the start and end of the step;
#                species: what the liquid is, the first-listed giving its colour
#   gas          the spaces of the path are tinted one after another; a one-space path is a steady
#                tint; species: what the gas is, the first-listed giving its colour
#   placeholder  a dashed box for something the hypothesis leaves unspecified; its position only
#                marks where the claim has it act and is not survey data
#   lightning    a strike on the top
#   field        a solver field slice; none exists until the second plan, and the viewer says so
#   coat         the calcium sulfate layer the claim puts on the walls of a space (S23)
#
# Numbers that are more than choreography:
#   The quarter steps of the Grand Gallery are the claimed four activations (hydro.claimed_strokes).
#   0.58 (well shaft) and 0.64 (descending passage) put the water at pavement level. The
#   hypothesis gives no reservoir level; pavement level is the assumed, hypothesis-favourable
#   case of research/02-hydraulics.md section 5.3. From the ledger:
#   (ws.volume - ws.volume_above_base) / ws.volume = (28.8 - 12.0) / 28.8 = 0.58, and for the
#   straight Descending Passage -dp.south_end.z / (dp.entrance.z - dp.south_end.z) =
#   30.00 / 46.97 = 0.64 (the 85.0 m3 of dp.volume's 133.1 m3 in that entry's note).
#   tests/test_viewer_data.py recomputes both fractions and the quarter from the ledger.
#   The hypothesis does not say where else the water stands. The Descending Passage is drawn as
#   a vessel communicating with the chamber: swept by the push stroke, refilled by the return
#   stroke. The Ascending Passage and the Queen's passage fill with the first activation because
#   they open below the Gallery's lower end; research/02-hydraulics.md section 4.3 counts them
#   among the spaces to be filled.
#   Steps S13 to S17 share one lowering of the Gallery in five equal parts and steps S18 to S21
#   one refill in four, because the hypothesis describes them as happening together.
#   Steps S01, S02 and S27 to S31 take place outside the Great Pyramid: nothing is drawn.
#
# Species colours are display choices and live in ledger/species.yaml.
"""


def orbited(camera: dict) -> dict:
    """The camera turned ORBIT_DEGREES about the vertical (project Z) through its target, CLOSER to it."""
    target = np.array(camera["target"], dtype=float)
    x, y, z = np.array(camera["position"], dtype=float) - target
    a = math.radians(ORBIT_DEGREES)
    turned = np.array([x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a), z])
    position = target + CLOSER * turned
    return {"position": [round(float(v), 2) + 0.0 for v in position], "target": list(camera["target"])}  # + 0.0: no -0.0


def liquid(step_id: str, space: str) -> list[str]:
    if space == "grand_gallery" and step_id == "S19":
        return ["sulfurous_acid", "water"]
    if space == "grand_gallery" and "S20" <= step_id <= "S26":
        return ["sulfuric_acid", "water"]
    return ["water"]


def actor_of(step_id: str, actor: dict) -> dict:
    actor = dict(actor)
    if actor["type"] == "gas":
        actor["species"] = GAS[actor.pop("color")]
    elif actor["type"] == "water":
        actor["species"] = liquid(step_id, actor["space"])
    return actor


def interior(actors: list[dict], spaces: list[str]) -> bool:
    """Something drawn inside the stone, or a gas that starts in a space the step's claim names."""
    return any(actor["type"] in INSIDE or (actor["type"] == "gas" and actor["path"][0] in spaces)
               for actor in actors)


PLAIN = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
YAML_WORDS = {"true", "false", "null", "yes", "no", "on", "off"}


def scalar(value) -> str:
    """One value in YAML flow style; text is quoted unless it is a plain word that YAML reads back as text."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)   # 5.0 stays a float, 260 an int
    if isinstance(value, list):
        return "[" + ", ".join(scalar(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{key}: {scalar(item)}" for key, item in value.items()) + "}"
    if PLAIN.fullmatch(value) and value.lower() not in YAML_WORDS:
        return value
    return json.dumps(value, ensure_ascii=False)   # a JSON string is a valid YAML double-quoted scalar


def main() -> None:
    old = yaml.safe_load(CYCLE.read_bytes())
    assert isinstance(old, list), "ledger/cycle.yaml is not plan A's list of steps: already rewritten?"
    claims = {claim["id"]: claim for claim in yaml.safe_load(CLAIMS.read_bytes())}
    steps = []
    for entry in old:
        sid, camera = entry["id"], entry["camera"]
        actors = [actor_of(sid, actor) for actor in entry["actors"]]
        if sid == "S23":
            actors += [{"type": "coat", "space": "grand_gallery"}, {"type": "coat", "space": "queens_chamber"}]
        step = {
            "id": sid, "title": entry["title"], "duration": entry["duration"],
            "path": [dict(camera), orbited(camera)],
            "scene": {"interior": interior(actors, claims[sid].get("spaces", [])),
                      "weather": "storm" if sid in STORM else "clear"},
            "species": SPECIES.get(sid, []),
        }
        if sid in REACTIONS:
            equation, note = REACTIONS[sid]
            step["reaction"] = {"equation": equation, "timestamp": claims[sid]["timestamp"], "note": note}
        step["actors"] = actors
        steps.append(step)

    lines = [HEADER, "prologue:", f"  duration: {scalar(PROLOGUE['duration'])}", "  path:"]
    lines += [f"    - {scalar(keyframe)}" for keyframe in PROLOGUE["path"]]
    lines.append("steps:")
    for step in steps:
        lines += [f"  - id: {step['id']}", f"    title: {scalar(step['title'])}",
                  f"    duration: {scalar(step['duration'])}", "    path:"]
        lines += [f"      - {scalar(keyframe)}" for keyframe in step["path"]]
        lines += [f"    scene: {scalar(step['scene'])}", f"    species: {scalar(step['species'])}"]
        if "reaction" in step:
            lines.append(f"    reaction: {scalar(step['reaction'])}")
        if step["actors"]:
            lines.append("    actors:")
            lines += [f"      - {scalar(actor)}" for actor in step["actors"]]
        else:
            lines.append("    actors: []")
    text = "\n".join(lines) + "\n"
    assert yaml.safe_load(text) == {"prologue": PROLOGUE, "steps": steps}, "the YAML written does not read back"
    CYCLE.write_text(text, encoding="utf-8")

    for step in steps:
        flags = ("interior" if step["scene"]["interior"] else "exterior", step["scene"]["weather"])
        print(step["id"], *flags, ",".join(step["species"]) or "-", "reaction" if "reaction" in step else "")


if __name__ == "__main__":
    main()
```

The script checks itself: it refuses a `cycle.yaml` that is already in the new shape, and it asserts that the YAML it writes reads back as exactly the structure it built before writing anything.

- [ ] **Step 2: Write the failing tests**

Replace the whole of `tests/test_viewer_data.py` with the following. The claims tests (down to `test_real_claims_payload_covers_all_71_claims_and_is_strict_json`) are unchanged; the imports gain `to_viewer` and `load_species`; everything from `STEP_IDS` on is rewritten for the new shape, keeping plan A's recomputed fractions.

```python
"""Tests for the viewer data exporters, checked key by key against the plan header's contracts."""
import json
import math
import re

import pytest
import yaml

from pyramid import REPO_ROOT, screening, viewer_data
from pyramid.geometry.export import to_viewer
from pyramid.ledger import STATUSES, Claim, Ledger, LedgerError, Quantity, load
from pyramid.screening import Result
from pyramid.species import load_species

SURVEY_SPACES = [
    "descending_passage", "subterranean_chamber", "pit", "south_passage", "well_shaft", "grotto",
    "ascending_passage", "queens_passage", "queens_chamber", "qc_shaft_north", "qc_shaft_south",
    "grand_gallery", "antechamber", "kings_chamber", "kc_shaft_north", "kc_shaft_south",
    "relieving_chambers", "big_void", "north_face_corridor",
]
PAPER_SPACES = ["paper_kings_chamber", "paper_queens_chamber", "paper_lower_chamber"]
TABLE_C = "research/01-geometry.md table C"
TABLE_F = "research/01-geometry.md table F"


def tiny_ledger() -> Ledger:
    """Five quantities and two claims, built in memory so that every expected value below is exact."""
    quantities = {
        quantity.id: quantity
        for quantity in (
            Quantity("gg.volume", 573.0, "m3", 527.2, 618.8, TABLE_F, False, "computed"),
            Quantity("dp.volume", 133.1, "m3", 129.1, 137.1, TABLE_F, False, "computed"),
            Quantity("kcs.mouth_height", 0.9144, "m", 0.9144, 0.9144, TABLE_C, True),
            Quantity("kcs.north.width", 0.2299, "m", 0.2261, 0.2337, TABLE_C, True),
            Quantity("kcs.south.width", 0.2159, "m", 0.2121, 0.2197, TABLE_C, True),
        )
    }
    claims = {
        "S12": Claim(
            "S12", "Four activations fill the Grand Gallery.", "hydraulic", "F 00:42:41-00:43:10", 0, 3,
            "Pass if the stroke count is within 25 percent of 4.", "pending",
            ("gg.volume", "dp.volume"), ("grand_gallery", "descending_passage"),
        ),
        "S05": Claim(
            "S05", "Operators wait for a storm.", "electrical", "F 01:09:08-01:10:54", 2, 6,
            "No computed verdict.", "pending", (), (),
        ),
    }
    return Ledger(quantities, claims, "0" * 64)


RESULTS = {
    # reads only quantities that S12 depends on: belongs to S12
    "t0.strokes": Result("t0.strokes", "Strokes to fill the gallery", 4.305, 3.845, 4.793, "1",
                         "gg.volume / dp.volume", ("gg.volume", "dp.volume")),
    # reads a quantity that no claim of the tiny ledger depends on: belongs to no claim
    "t0.shaft_width": Result("t0.shaft_width", "North shaft width", 0.2299, 0.2261, 0.2337, "m",
                             "kcs.north.width", ("kcs.north.width",)),
}
VERDICTS = {"S12": ("conditional", "4.3 strokes if the whole passage is swept and nothing else is filled")}


def test_claims_payload_has_the_three_contract_keys_and_a_viewer_manifest():
    led = tiny_ledger()
    payload = viewer_data.claims_payload(led, RESULTS, VERDICTS)
    assert set(payload) == {"manifest", "claims", "spaces"}
    assert payload["manifest"]["case"] == "viewer"
    assert payload["manifest"]["ledger"] == led.digest
    assert {"commit", "versions"} <= set(payload["manifest"])


def test_a_decided_claim_carries_its_verdict_basis_and_numbers():
    payload = viewer_data.claims_payload(tiny_ledger(), RESULTS, VERDICTS)
    assert payload["claims"][0] == {
        "id": "S12",
        "statement": "Four activations fill the Grand Gallery.",
        "subsystem": "hydraulic",
        "timestamp": "F 00:42:41-00:43:10",
        "tier": 0,
        "piece": 3,
        "criterion": "Pass if the stroke count is within 25 percent of 4.",
        "status": "conditional",
        "basis": "4.3 strokes if the whole passage is swept and nothing else is filled",
        "numbers": [
            {"label": "Strokes to fill the gallery", "value": 4.305, "low": 3.845, "high": 4.793, "unit": "1"},
        ],
        "spaces": ["grand_gallery", "descending_passage"],
    }


def test_an_undecided_claim_keeps_its_ledger_status_and_has_no_numbers():
    payload = viewer_data.claims_payload(tiny_ledger(), RESULTS, VERDICTS)
    waiting = payload["claims"][1]
    assert (waiting["id"], waiting["status"], waiting["basis"], waiting["numbers"]) == ("S05", "pending", "", [])


def test_a_bound_that_is_not_finite_becomes_null():
    open_ended = {
        "t0.lifetime": Result("t0.lifetime", "Lifetime", 2.8e17, 2.8e17, math.inf, "s", "1 / (k n)", ("gg.volume",)),
    }
    payload = viewer_data.claims_payload(tiny_ledger(), open_ended, {})
    assert payload["claims"][0]["numbers"] == [
        {"label": "Lifetime", "value": 2.8e17, "low": 2.8e17, "high": None, "unit": "s"},
    ]
    json.dumps(payload, allow_nan=False)  # raises ValueError if an infinity or a NaN is left


def test_space_index_lists_every_header_space_with_its_quantities_and_claims():
    payload = viewer_data.claims_payload(tiny_ledger(), RESULTS, VERDICTS)
    assert list(payload["spaces"]) == SURVEY_SPACES + PAPER_SPACES
    assert payload["spaces"]["grand_gallery"] == {
        "label": "Grand Gallery",
        "quantities": [
            {"id": "gg.volume", "value": 573.0, "unit": "m3", "source": TABLE_F, "verified": False, "note": "computed"},
        ],
        "claims": ["S12"],
    }
    # a shaft gets the quantities both shafts share and its own, never the other shaft's
    north = payload["spaces"]["kc_shaft_north"]
    assert [quantity["id"] for quantity in north["quantities"]] == ["kcs.mouth_height", "kcs.north.width"]
    # "kc." must not match the "kcs." ids of the shafts
    assert payload["spaces"]["kings_chamber"] == {"label": "King's Chamber", "quantities": [], "claims": []}


def test_real_claims_payload_covers_all_71_claims_and_is_strict_json():
    led = load()
    results = screening.all_results(led)
    payload = viewer_data.claims_payload(led, results, screening.verdicts(led, results))
    assert [claim["id"] for claim in payload["claims"]] == list(led.claims)
    assert len(payload["claims"]) == 71
    for claim in payload["claims"]:
        assert claim["status"] in STATUSES, claim["id"]
        assert set(claim["spaces"]) <= set(payload["spaces"]), claim["id"]
    gallery = payload["spaces"]["grand_gallery"]
    assert "S12" in gallery["claims"]
    assert any(quantity["id"] == "gg.volume" for quantity in gallery["quantities"])
    json.dumps(payload, allow_nan=False)
    # the inspector must be able to tell an assumed figure from a sourced one
    for space in payload["spaces"].values():
        for quantity in space["quantities"]:
            assert set(quantity) == {"id", "value", "unit", "source", "verified", "note"}, quantity["id"]
            assert isinstance(quantity["verified"], bool) and isinstance(quantity["note"], str), quantity["id"]
    grotto = {quantity["id"]: quantity for quantity in payload["spaces"]["grotto"]["quantities"]}
    side = grotto["grotto.plan_side"]
    assert side["verified"] is False and side["note"].startswith("assumed for the model")
    # a claim with a verdict shows the figure the verdict was reached on
    for claim in payload["claims"]:
        assert claim["status"] == "pending" or claim["numbers"], claim["id"]


STEP_IDS = [f"S{i:02d}" for i in range(1, 32)]
SUFFIX = "not specified by the hypothesis"
STEP_KEYS = {"id", "title", "duration", "path", "scene", "species", "actors"}
ACTOR_KEYS = {
    "water": {"type", "space", "from", "to", "species"},
    "gas": {"type", "path", "species"},
    "placeholder": {"type", "kind", "at", "label"},
    "lightning": {"type"},
    "field": {"type", "slice"},
    "coat": {"type", "space"},
}
PLACEHOLDER_KINDS = {"pump", "valve", "reservoir", "drain", "gas_inlet"}
STATED = "as stated in the video"
# docs/superpowers/specs/2026-10-10-chemistry-display-kings-chamber-design.md section 3.2
REACTIONS = {
    "S02": ("not stated by the hypothesis", "the video names a conversion without giving it"),
    "S16": ("2 SO₂ + O₂ → 2 SO₃", STATED),
    "S19": ("SO₂ + H₂O → H₂SO₃", STATED),
    "S20": ("2 H₂SO₃ + O₂ → 2 H₂SO₄", STATED),
    "S21": ("SO₃ + H₂O → H₂SO₄ (into dilute acid)", STATED),
    "S23": ("CaCO₃ + H₂SO₄ → CaSO₄ + H₂O + CO₂", STATED),
    "S27": ("H₂SO₄ + 2 NaCl → Na₂SO₄ + 2 HCl", STATED),
}


def authored() -> dict:
    """ledger/cycle.yaml as written by hand, in the project frame."""
    return yaml.safe_load((REPO_ROOT / "ledger" / "cycle.yaml").read_bytes())


def step_of(cycle: dict, step_id: str) -> dict:
    return next(step for step in cycle["steps"] if step["id"] == step_id)


def actors(step_id: str, kind: str) -> list[dict]:
    return [actor for actor in step_of(authored(), step_id)["actors"] if actor["type"] == kind]


def is_point(value) -> bool:
    return isinstance(value, list) and len(value) == 3 and all(isinstance(v, (int, float)) for v in value)


def is_keyframe(value) -> bool:
    return isinstance(value, dict) and set(value) == {"position", "target"} and \
        is_point(value["position"]) and is_point(value["target"])


def test_cycle_has_a_prologue_then_one_entry_per_step_in_order_and_every_id_is_a_claim():
    cycle = authored()
    assert set(cycle) == {"prologue", "steps"}
    assert [step["id"] for step in cycle["steps"]] == STEP_IDS
    assert set(STEP_IDS) <= set(load().claims)


def test_the_prologue_is_a_six_second_flight_with_no_claim():
    prologue = authored()["prologue"]
    assert set(prologue) == {"duration", "path"}
    assert prologue["duration"] == 6.0
    assert len(prologue["path"]) == 3 and all(is_keyframe(keyframe) for keyframe in prologue["path"])


def test_every_step_and_actor_matches_the_contract():
    species = load_species()
    for step in authored()["steps"]:
        where = step["id"]
        assert set(step) == STEP_KEYS | ({"reaction"} if where in REACTIONS else set()), where
        assert isinstance(step["title"], str) and step["title"], where
        assert isinstance(step["duration"], float) and step["duration"] > 0, where
        assert 2 <= len(step["path"]) <= 4, where
        assert all(is_keyframe(keyframe) for keyframe in step["path"]), where
        assert set(step["scene"]) == {"interior", "weather"} and isinstance(step["scene"]["interior"], bool), where
        assert step["scene"]["weather"] in ("clear", "storm"), where
        assert set(step["species"]) <= set(species), where
        for actor in step["actors"]:
            assert set(actor) == ACTOR_KEYS[actor["type"]], (where, actor)
            if actor["type"] in ("water", "gas"):
                assert actor["species"] and set(actor["species"]) <= set(species), (where, actor)
            if actor["type"] in ("water", "coat"):
                assert actor["space"] in SURVEY_SPACES, (where, actor)
            if actor["type"] == "water":
                assert 0.0 <= actor["from"] <= 1.0 and 0.0 <= actor["to"] <= 1.0, (where, actor)
            if actor["type"] == "gas":
                assert actor["path"] and set(actor["path"]) <= set(SURVEY_SPACES), (where, actor)
            if actor["type"] == "placeholder":
                assert actor["kind"] in PLACEHOLDER_KINDS, (where, actor)
                assert is_point(actor["at"]), (where, actor)
                assert actor["label"].endswith(SUFFIX), (where, actor)
            if actor["type"] == "field":
                assert re.fullmatch(r"fields/\w+\.png", actor["slice"]), (where, actor)


INSIDE = {"water", "placeholder", "coat"}   # actors drawn inside the stone


def test_a_step_is_interior_exactly_when_it_draws_inside_the_stone_where_its_claim_acts():
    # the camera may stand outside looking in; the flag follows the actors and the claim, never the camera.
    # A gas counts only when its path starts in a space the claim names: a tint that merely persists
    # elsewhere (the King's Chamber through S04 and S05, whose claims name no space) does not.
    claims = load().claims
    for step in authored()["steps"]:
        spaces = claims[step["id"]].spaces
        inside = any(actor["type"] in INSIDE or (actor["type"] == "gas" and actor["path"][0] in spaces)
                     for actor in step["actors"])
        assert step["scene"]["interior"] is inside, step["id"]


def test_only_the_two_storm_steps_carry_the_storm():
    assert [step["id"] for step in authored()["steps"] if step["scene"]["weather"] == "storm"] == ["S05", "S06"]


def test_the_reaction_steps_carry_the_equation_as_stated_and_the_claims_timestamp():
    claims = load().claims
    cycle = authored()
    assert [step["id"] for step in cycle["steps"] if "reaction" in step] == list(REACTIONS)
    for step_id, (equation, note) in REACTIONS.items():
        assert step_of(cycle, step_id)["reaction"] == {
            "equation": equation, "timestamp": claims[step_id].timestamp, "note": note,
        }, step_id


def test_the_gallery_liquid_turns_to_acid_where_the_claims_put_it():
    liquid = {
        (step["id"], actor["space"]): actor["species"]
        for step in authored()["steps"] for actor in step["actors"] if actor["type"] == "water"
    }
    acid = {("S19", "grand_gallery"): ["sulfurous_acid", "water"]}
    acid |= {(f"S{i}", "grand_gallery"): ["sulfuric_acid", "water"] for i in range(20, 27)}
    for key, species in liquid.items():
        assert species == acid.get(key, ["water"]), key
    assert set(acid) <= set(liquid)


def test_each_kind_of_actor_appears_on_the_step_that_claims_it():
    assert actors("S06", "lightning") == [{"type": "lightning"}]
    slices = [actor["slice"] for actor in actors("S04", "field") + actors("S06", "field")]
    assert slices == ["fields/R2_333m.png", "fields/R1_230m.png"]
    kinds = {step_id: {actor["kind"] for actor in actors(step_id, "placeholder")}
             for step_id in ("S03", "S08", "S09", "S10", "S13", "S26")}
    assert kinds == {
        "S03": {"gas_inlet"}, "S08": {"reservoir"}, "S09": {"valve"},
        "S10": {"pump", "valve"}, "S13": {"drain"}, "S26": {"drain"},
    }
    assert {"type": "gas", "path": ["kings_chamber", "antechamber"], "species": ["so2"]} in actors("S15", "gas")
    assert {"type": "gas", "path": ["antechamber"], "species": ["so3"]} in actors("S16", "gas")
    used = {actor["kind"] for step in authored()["steps"] for actor in step["actors"] if actor["type"] == "placeholder"}
    assert used == PLACEHOLDER_KINDS
    # the calcium sulfate layer of S23, on the two spaces the claim names, and nowhere else
    assert actors("S23", "coat") == [{"type": "coat", "space": "grand_gallery"}, {"type": "coat", "space": "queens_chamber"}]
    coated = [step["id"] for step in authored()["steps"] for actor in step["actors"] if actor["type"] == "coat"]
    assert coated == ["S23", "S23"]


def test_the_gallery_fills_in_four_quarters_drains_and_fills_again():
    gallery = {
        step["id"]: (actor["from"], actor["to"])
        for step in authored()["steps"] for actor in step["actors"]
        if actor["type"] == "water" and actor["space"] == "grand_gallery"
    }
    quarter = 1 / load().q("hydro.claimed_strokes")                  # one of the claimed four activations
    assert gallery["S10"] == (0.0, quarter)                          # the first activation
    assert gallery["S12"] == (quarter, 1.0)                          # the other three
    assert gallery["S13"][0] == 1.0 and gallery["S17"][1] == 0.0     # lowered over S13 to S17
    assert gallery["S18"] == (0.0, quarter)                          # raised again, in four activations,
    assert gallery["S21"][1] == 1.0                                  # over S18 to S21
    assert gallery["S26"] == (1.0, 0.0)                              # withdrawn


def test_water_standing_at_the_reservoir_level_follows_the_ledger():
    """Step S09 leaves the water at pavement level (Z = 0); the two fractions are recomputed from the ledger."""
    led = load()
    reached = {actor["space"]: actor["to"] for actor in actors("S09", "water")}
    below_pavement = (led.q("ws.volume") - led.q("ws.volume_above_base")) / led.q("ws.volume")
    assert reached["well_shaft"] == round(below_pavement, 2)
    # the passage is straight and of one cross-section, so its volume below a level goes with the height
    below_pavement = -led.q("dp.south_end.z") / (led.q("dp.entrance.z") - led.q("dp.south_end.z"))
    assert reached["descending_passage"] == round(below_pavement, 2)


def test_water_levels_join_up_from_one_step_to_the_next():
    previous: dict[str, float] = {}
    for step in authored()["steps"]:
        current = {actor["space"]: actor for actor in step["actors"] if actor["type"] == "water"}
        for space, actor in current.items():
            if space in previous:
                assert actor["from"] == previous[space], (step["id"], space)
        previous = {space: actor["to"] for space, actor in current.items()}


CURVES = {"grand_gallery": [(21.656, 0.0), (51.5, 573.0)]}
# a fixed verdict per producing step, so each marking below is known exactly
MARKS = {"S16": "fail", "S20": "conditional"}
PAYLOAD_KEYS = {"id", "formula", "name", "phase", "colour", "status"}
WATER = {"id": "water", "formula": "H₂O", "name": "water", "phase": "liquid", "colour": "#2f86d6", "status": "plain"}


def payload() -> dict:
    return viewer_data.cycle_payload(load(), CURVES, load_species(), MARKS)


def test_cycle_payload_has_the_contract_keys_the_notice_and_the_curves():
    cycle = payload()
    assert set(cycle) == {"notice", "prologue", "steps", "curves"}
    assert cycle["notice"] == "Animation of the claim. Not a simulation result."
    assert [step["id"] for step in cycle["steps"]] == STEP_IDS
    for step in cycle["steps"]:
        assert set(step) == STEP_KEYS | ({"reaction"} if step["id"] in REACTIONS else set()), step["id"]
        assert all(is_keyframe(keyframe) for keyframe in step["path"]), step["id"]
        for species in step["species"]:
            assert set(species) == PAYLOAD_KEYS, step["id"]
        for actor in step["actors"]:
            assert set(actor) == ACTOR_KEYS[actor["type"]], (step["id"], actor)
            for species in actor.get("species", []):
                assert set(species) == PAYLOAD_KEYS, (step["id"], actor)
    written = json.loads(json.dumps(cycle, allow_nan=False))
    assert written["curves"] == {"grand_gallery": [[21.656, 0.0], [51.5, 573.0]]}


def test_cycle_payload_moves_keyframes_and_placeholders_into_viewer_coordinates():
    cycle = payload()
    # project (x east, y north, z up) becomes viewer (x, z, -y)
    # the prologue's first keyframe, authored as position [620, 520, 150], target [0, 102, 17]
    assert cycle["prologue"]["duration"] == 6.0
    assert cycle["prologue"]["path"][0] == {"position": [620, 150, -520], "target": [0, 17, -102]}
    step = step_of(cycle, "S08")
    # S08's first keyframe, plan A's camera, authored as position [200, 40, 15], target [7, 55, -8]
    assert step["path"][0] == {"position": [200, 15, -40], "target": [7, -8, -55]}
    second = step_of(authored(), "S08")["path"][1]
    assert step["path"][1] == {"position": list(to_viewer(*second["position"])),
                               "target": list(to_viewer(*second["target"]))}
    reservoir = next(actor for actor in step["actors"] if actor["type"] == "placeholder")
    assert reservoir["at"] == [7, 0, -125]   # authored as [7, 125, 0]
    assert reservoir["label"] == "Reservoir: not specified by the hypothesis"
    # a water actor keeps its keys; its species id becomes the species' payload
    assert {"type": "water", "space": "subterranean_chamber", "from": 0.0, "to": 1.0, "species": [WATER]} in step["actors"]
    assert (step["title"], step["duration"]) == ("Reservoir water enters the Subterranean Chamber", 6.0)
    assert step["scene"] == {"interior": True, "weather": "clear"}   # S08 draws water and a placeholder


def test_cycle_payload_marks_each_species_by_the_verdict_of_its_producing_step():
    step = step_of(payload(), "S21")   # species [so3, water, sulfuric_acid]
    assert [(species["id"], species["status"]) for species in step["species"]] == [
        ("so3", "claimed"),                # S16 fail
        ("water", "plain"),                # an input
        ("sulfuric_acid", "conditional"),  # S20 conditional
    ]
    gallery = next(actor for actor in step["actors"] if actor["type"] == "water" and actor["space"] == "grand_gallery")
    assert [(species["id"], species["status"]) for species in gallery["species"]] == [
        ("sulfuric_acid", "conditional"), ("water", "plain"),
    ]
    assert gallery["species"][0]["colour"] == "#c25b5b"   # the liquid's colour comes from the species table


def test_cycle_payload_rejects_a_step_that_is_not_a_claim():
    # the tiny ledger holds only S12 and S05, so the first step of cycle.yaml is unknown to it
    with pytest.raises(LedgerError, match=re.escape("cycle.yaml: S01 is not a claim id")):
        viewer_data.cycle_payload(tiny_ledger(), CURVES, load_species(), {})


def drop_gas_species(step: dict) -> None:
    next(actor for actor in step["actors"] if actor["type"] == "gas").pop("species")


@pytest.mark.parametrize("change, message", [
    (lambda step: step.update(path=step["path"][:1]), "cycle.yaml: S03: path needs 2 to 4 keyframes"),
    (lambda step: step.update(path=step["path"] * 3), "cycle.yaml: S03: path needs 2 to 4 keyframes"),
    (lambda step: step.update(species=["xyz"]), "cycle.yaml: S03: unknown species xyz"),
    (drop_gas_species, "cycle.yaml: S03: gas actor needs species"),
    (lambda step: step["scene"].update(weather="fog"), "cycle.yaml: S03: weather must be clear or storm"),
])
def test_cycle_payload_rejects_a_broken_step_naming_it(tmp_path, monkeypatch, change, message):
    cycle = authored()
    change(step_of(cycle, "S03"))   # one thing broken on one step; everything else as authored
    broken = tmp_path / "cycle.yaml"
    broken.write_text(yaml.safe_dump(cycle, allow_unicode=True, sort_keys=False), encoding="utf-8")
    monkeypatch.setattr(viewer_data, "CYCLE_FILE", broken)
    with pytest.raises(LedgerError, match=re.escape(message)):
        viewer_data.cycle_payload(load(), CURVES, load_species(), {})
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run pytest -q -W error tests/test_viewer_data.py`
Expected: `20 failed, 6 passed`. The six claims tests pass. The cycle tests fail with `TypeError: list indices must be integers or slices, not str` (fifteen of them: plan A's `cycle.yaml` is a list, not `{prologue, steps}`), `TypeError: unhashable type: 'dict'` (the first test's `set(cycle)` of that list) or `TypeError: cycle_payload() takes 2 positional arguments but 4 were given` (four).

- [ ] **Step 4: Run the generator**

From the repository root, with `SCRATCH` set to the directory of Step 1. In the command below, replace `/path/to/your/scratchpad` with the scratchpad directory your session prompt names (any directory outside the repository where you saved `rewrite_cycle.py`):

```bash
SCRATCH=/path/to/your/scratchpad; uv run python "$SCRATCH/rewrite_cycle.py"
```

The script imports nothing from `pyramid` and reads and writes paths relative to the repository root, so it must be run from there.

Expected output, exactly (every line without `reaction` ends in one trailing space, from the empty last field):

```
S01 exterior clear h2s 
S02 exterior clear h2s,so2 reaction
S03 interior clear so2 
S04 exterior clear - 
S05 exterior storm - 
S06 interior storm - 
S07 interior clear - 
S08 interior clear - 
S09 interior clear - 
S10 interior clear - 
S11 interior clear - 
S12 interior clear - 
S13 interior clear so2 
S14 interior clear air 
S15 interior clear so2,air 
S16 interior clear so2,air,so3 reaction
S17 interior clear so3,so2,air 
S18 interior clear - 
S19 interior clear so2,water,sulfurous_acid reaction
S20 interior clear sulfurous_acid,air,sulfuric_acid reaction
S21 interior clear so3,water,sulfuric_acid reaction
S22 interior clear so2,so3,water 
S23 interior clear sulfuric_acid,calcium_sulfate reaction
S24 interior clear - 
S25 interior clear - 
S26 interior clear sulfuric_acid,water 
S27 exterior clear sulfuric_acid,hydrogen_chloride reaction
S28 exterior clear sulfuric_acid,hydrogen_chloride 
S29 exterior clear - 
S30 exterior clear sulfuric_acid 
S31 exterior clear - 
```

Twenty-two steps are interior, S03 and S06 to S26: each draws a water, placeholder or coat actor, or a gas that starts in a space its claim names. S04 and S05 keep plan A's sulfur dioxide tint in the King's Chamber, but their claims name no space, so the tint does not make them interior; S06's claim names `kings_chamber` and `antechamber`, so its King's Chamber tint does, and the storm step S06 rides the glass look. The first interior step is S03 (the King's Chamber close view), which is the first cross-fade the viewer tasks check. S01, S02 and S27 to S31 draw nothing and are exterior.

Run: `git diff --stat ledger/cycle.yaml`
Expected: `1 file changed, 542 insertions(+), 380 deletions(-)`; the file is now 575 lines.

Spot-check the S16 block of `ledger/cycle.yaml`; it reads:

```yaml
  - id: S16
    title: "Sulfur dioxide becomes trioxide in the antechamber"
    duration: 6.0
    path:
      - {position: [30, -8, 48], target: [7, -4.4, 45]}
      - {position: [26.55, 3.14, 47.7], target: [7, -4.4, 45]}
    scene: {interior: true, weather: clear}
    species: [so2, air, so3]
    reaction: {equation: "2 SO₂ + O₂ → 2 SO₃", timestamp: "F 00:46:59-00:47:10", note: "as stated in the video"}
    actors:
      - {type: water, space: subterranean_chamber, from: 1.0, to: 1.0, species: [water]}
      - {type: water, space: pit, from: 1.0, to: 1.0, species: [water]}
      - {type: water, space: south_passage, from: 1.0, to: 1.0, species: [water]}
      - {type: water, space: descending_passage, from: 0.64, to: 0.64, species: [water]}
      - {type: water, space: well_shaft, from: 1.0, to: 1.0, species: [water]}
      - {type: water, space: ascending_passage, from: 1.0, to: 1.0, species: [water]}
      - {type: water, space: queens_passage, from: 1.0, to: 1.0, species: [water]}
      - {type: water, space: queens_chamber, from: 1.0, to: 1.0, species: [water]}
      - {type: water, space: grand_gallery, from: 0.4, to: 0.2, species: [water]}
      - {type: placeholder, kind: drain, at: [7.3, 43, 19], label: "Gallery drain: not specified by the hypothesis"}
      - {type: gas, path: [kings_chamber], species: [so2]}
      - {type: gas, path: [antechamber], species: [so3]}
      - {type: gas, path: [kc_shaft_north], species: [air]}
      - {type: gas, path: [kc_shaft_south], species: [air]}
```

Running the script a second time stops with `AssertionError: ledger/cycle.yaml is not plan A's list of steps: already rewritten?`; to start over, `git checkout -- ledger/cycle.yaml`.

- [ ] **Step 5: Run the tests again**

Run: `uv run pytest -q -W error tests/test_viewer_data.py`
Expected: `9 failed, 17 passed`. Every test of the authored file passes; the nine `cycle_payload` tests still fail with `TypeError: cycle_payload() takes 2 positional arguments but 4 were given`.

- [ ] **Step 6: Write the exporter**

Replace the whole of `pyramid/viewer_data.py` with:

```python
"""Export what the viewer reads: claims.json, cycle.json, the two glb files and a manifest."""
import json
import math

import yaml

from pyramid import REPO_ROOT, provenance, screening
from pyramid.geometry import Variants, build
from pyramid.geometry.export import to_viewer, write_glb
from pyramid.geometry.frame import session
from pyramid.geometry.model import level_volume_curve
from pyramid.ledger import Ledger, LedgerError, load
from pyramid.screening import Result
from pyramid.species import Species, load_species, species_payload

NOTICE = "Animation of the claim. Not a simulation result."
CYCLE_FILE = REPO_ROOT / "ledger" / "cycle.yaml"
OUT_DIR = REPO_ROOT / "viewer" / "data"
WEATHER = ("clear", "storm")

# The alternative reading of the survey (plan header): what interior_alt.glb shows.
ALTERNATIVE = Variants(
    kc_shaft_ends_level=True, grooves_connected=True, pit_excavated=True,
    big_void_inclined=True, apex_truncated=False,
)

# space name -> (label, ledger id prefix, prefix to leave out).
# The two shafts of a pair share one prefix, so each leaves out the other's ids.
SPACES: dict[str, tuple[str, str, str | None]] = {
    "descending_passage": ("Descending Passage", "dp.", None),
    "subterranean_chamber": ("Subterranean Chamber", "sub.", None),
    "pit": ("Pit", "pit.", None),
    "south_passage": ("South passage", "sp.", None),
    "well_shaft": ("Well shaft", "ws.", None),
    "grotto": ("Grotto", "grotto.", None),
    "ascending_passage": ("Ascending Passage", "ap.", None),
    "queens_passage": ("Queen's Chamber passage", "qp.", None),
    "queens_chamber": ("Queen's Chamber", "qc.", None),
    "qc_shaft_north": ("Queen's Chamber north shaft", "qcs.", "qcs.south."),
    "qc_shaft_south": ("Queen's Chamber south shaft", "qcs.", "qcs.north."),
    "grand_gallery": ("Grand Gallery", "gg.", None),
    "antechamber": ("Antechamber", "ante.", None),
    "kings_chamber": ("King's Chamber", "kc.", None),
    "kc_shaft_north": ("King's Chamber north shaft", "kcs.", "kcs.south."),
    "kc_shaft_south": ("King's Chamber south shaft", "kcs.", "kcs.north."),
    "relieving_chambers": ("Relieving chambers", "rc.", None),
    "big_void": ("Big Void", "bv.", None),
    "north_face_corridor": ("North Face Corridor", "nfc.", None),
    "paper_kings_chamber": ("King's Chamber (2018 study's model)", "paper.kc.", None),
    "paper_queens_chamber": ("Queen's Chamber (2018 study's model)", "paper.qc.", None),
    "paper_lower_chamber": ("Lower chamber (2018 study's model)", "paper.lower.", None),
}


def _finite(x: float) -> float | None:
    """JSON has no infinity and no NaN; the viewer prints null as 'no bound'."""
    return x if math.isfinite(x) else None


def claims_payload(ledger: Ledger, results: dict[str, Result],
                   verdicts: dict[str, tuple[str, str]]) -> dict:
    claims = []
    for claim in ledger.claims.values():
        status, basis = verdicts.get(claim.id, (claim.status, ""))
        depends = set(claim.depends_on)
        claims.append({
            "id": claim.id,
            "statement": claim.statement,
            "subsystem": claim.subsystem,
            "timestamp": claim.timestamp,
            "tier": claim.tier,
            "piece": claim.piece,
            "criterion": claim.criterion,
            "status": status,
            "basis": basis,
            # a result belongs to a claim when the claim depends on every quantity the result reads
            "numbers": [
                {"label": result.label, "value": _finite(result.value), "low": _finite(result.low),
                 "high": _finite(result.high), "unit": result.unit}
                for result in results.values()
                if result.inputs and set(result.inputs) <= depends
            ],
            "spaces": list(claim.spaces),
        })
    spaces = {
        name: {
            "label": label,
            "quantities": [
                {"id": quantity.id, "value": quantity.value, "unit": quantity.unit, "source": quantity.source,
                 "verified": quantity.verified, "note": quantity.note}
                for quantity in ledger.quantities.values()
                if quantity.id.startswith(prefix) and not (skip and quantity.id.startswith(skip))
            ],
            "claims": [claim.id for claim in ledger.claims.values() if name in claim.spaces],
        }
        for name, (label, prefix, skip) in SPACES.items()
    }
    return {"manifest": provenance.manifest("viewer", ledger), "claims": claims, "spaces": spaces}


def _viewer_path(path: list[dict]) -> list[dict]:
    """Camera keyframes from the project frame to the viewer's."""
    return [{key: list(to_viewer(*keyframe[key])) for key in ("position", "target")} for keyframe in path]


def cycle_payload(ledger: Ledger, curves: dict[str, list[tuple[float, float]]],
                  species: dict[str, Species], verdicts: dict[str, str]) -> dict:
    """cycle.yaml in viewer coordinates, each species id replaced by its payload with the marking status."""
    cycle = yaml.safe_load(CYCLE_FILE.read_bytes())

    def payloads(ids: list[str], where: str) -> list[dict]:
        for key in ids:
            if key not in species:
                raise LedgerError(f"cycle.yaml: {where}: unknown species {key}")
        return [species_payload(species[key], verdicts) for key in ids]

    prologue = {"duration": cycle["prologue"]["duration"], "path": _viewer_path(cycle["prologue"]["path"])}
    steps = cycle["steps"]
    for step in steps:
        where = step["id"]
        if where not in ledger.claims:
            raise LedgerError(f"cycle.yaml: {where} is not a claim id")
        if not 2 <= len(step["path"]) <= 4:
            raise LedgerError(f"cycle.yaml: {where}: path needs 2 to 4 keyframes")
        if step["scene"]["weather"] not in WEATHER:
            raise LedgerError(f"cycle.yaml: {where}: weather must be clear or storm")
        step["path"] = _viewer_path(step["path"])
        step["species"] = payloads(step["species"], where)
        for actor in step["actors"]:
            if actor["type"] in ("water", "gas"):
                if not actor.get("species"):
                    raise LedgerError(f"cycle.yaml: {where}: {actor['type']} actor needs species")
                actor["species"] = payloads(actor["species"], where)
            elif actor["type"] == "placeholder":
                actor["at"] = list(to_viewer(*actor["at"]))
    # a curve's z is the viewer's Y, so the curves need no conversion
    return {"notice": NOTICE, "prologue": prologue, "steps": steps, "curves": curves}


def main() -> None:
    led = load()
    results = screening.all_results(led)
    decided = screening.verdicts(led, results)
    species = load_species(step_ids=set(led.claims))
    wet = sorted({
        actor["space"]
        for step in yaml.safe_load(CYCLE_FILE.read_bytes())["steps"]
        for actor in step["actors"] if actor["type"] == "water"
    })
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with session():
        model = build(led)
        write_glb(model, OUT_DIR / "interior.glb")
        # the model's volume tags are valid only while this session is open
        curves = {name: level_volume_curve(model, name) for name in wet}
    with session():  # a fresh session, so that nothing of the first model is left in the kernel
        write_glb(build(led, variants=ALTERNATIVE), OUT_DIR / "interior_alt.glb")

    # the marking rule reads the verdict word alone; the basis sentence goes to claims.json
    statuses = {claim: status for claim, (status, _) in decided.items()}
    for name, payload in (("claims.json", claims_payload(led, results, decided)),
                          ("cycle.json", cycle_payload(led, curves, species, statuses))):
        (OUT_DIR / name).write_text(json.dumps(payload, indent=1, allow_nan=False) + "\n")
    provenance.write_manifest(OUT_DIR, "viewer", led)
    for path in sorted(OUT_DIR.iterdir()):
        print(path.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
```

What changed against plan A's file: the `pyramid.species` import and `WEATHER`; `_viewer_path` and the new `cycle_payload`; in `main()`, `cycle.yaml` is read as `{prologue, steps}`, species are loaded and checked against the claim ids before the slow geometry build, the verdict words are passed to `cycle_payload`, and the field-slice code is gone (`(OUT_DIR / "fields").mkdir(...)`, the `extra = {"fields": ...}` glob, `claims["manifest"].update(extra)` and the `extra` argument of `write_manifest`), with `OUT_DIR.mkdir` in its place because `write_glb` needs the folder. `claims_payload` and everything above it are unchanged. Reading the cycle file as bytes lets YAML decode the UTF-8 equations whatever the locale.

- [ ] **Step 7: Run the tests to verify they pass**

Run: `uv run pytest -q -W error tests/test_viewer_data.py tests/test_species.py`
Expected: `48 passed`.

Run: `uv run pytest -q -W error`
Expected: `293 passed, 1 xfailed` (282 passed and 1 xfailed after Task 1; `test_viewer_data.py` goes from 15 tests to 26), no warnings. `test_provenance.py` still passes: neither `parameters.yaml` nor `claims.yaml` changed, so the ledger digest recorded in `viewer/data/manifest.json` still matches.

- [ ] **Step 8: Commit the code and the cycle file**

```bash
git add ledger/cycle.yaml pyramid/viewer_data.py tests/test_viewer_data.py
git commit -F - <<'EOF'
Give the cycle camera paths, scene flags, species and reactions, and export them

ledger/cycle.yaml becomes {prologue, steps}: each step's plan A camera is the first keyframe of
a path, the interior flag follows the step's actors and its claim's spaces, gas and water actors
name their species, and S23 gains the coat. cycle_payload converts the paths and attaches each
species' marking status; the manifest no longer lists field slices.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
```

The scratch script stays where it is, outside the repository; it is not added.

- [ ] **Step 9: Regenerate the viewer data on a clean tree**

Run: `git status --short -- ledger pyramid tests viewer results`
Expected: no output (the tree is clean where the generators read and write).

Plan A's `main()` left an empty `viewer/data/fields/` folder behind; git does not track empty folders, and the new `main()` neither creates nor lists it. Remove it if it is there (`rmdir` refuses a folder that is not empty):

```bash
[ -d viewer/data/fields ] && rmdir viewer/data/fields; true
```

Run the three commands of the README's "Regenerating the results", in order, from the repository root:

```bash
uv run python -m pyramid.screening
uv run python -m pyramid.geometry.export
uv run python -m pyramid.viewer_data
```

Expected output of the third command, exactly:

```
viewer/data/claims.json
viewer/data/cycle.json
viewer/data/interior.glb
viewer/data/interior_alt.glb
viewer/data/manifest.json
```

- [ ] **Step 10: Check the regenerated files**

Run: `git status --short -- ledger pyramid tests viewer results`
Expected:

```
 M results/tier0/manifest.json
 M viewer/data/claims.json
 M viewer/data/cycle.json
 M viewer/data/manifest.json
```

`interior.glb` and `interior_alt.glb` are not listed: the geometry did not change and the meshing is deterministic. `results/tier0/manifest.json` changed only in `timestamp` and `commit` (check with `git diff results/tier0`: no other line differs, and `tier0.json` and `tier0.md` are not listed); this task changes neither the ledger nor the screening, so its results did not change and only the commit stamp would: restore it.

```bash
git checkout -- results/tier0/manifest.json
```

Run:

```bash
uv run python -c "
import json
cycle = json.load(open('viewer/data/cycle.json'))
manifest = json.load(open('viewer/data/manifest.json'))
claims = json.load(open('viewer/data/claims.json'))
print(sorted(cycle), sorted(cycle['prologue']), sorted(cycle['steps'][15]))
print([step['id'] for step in cycle['steps'] if step['scene']['interior']])
print([step['id'] for step in cycle['steps'] if step['scene']['weather'] == 'storm'])
print([(species['formula'], species['status']) for species in cycle['steps'][15]['species']])
print('fields' in manifest, 'fields' in claims['manifest'])
"
```

Expected, exactly:

```
['curves', 'notice', 'prologue', 'steps'] ['duration', 'path'] ['actors', 'duration', 'id', 'path', 'reaction', 'scene', 'species', 'title']
['S03', 'S06', 'S07', 'S08', 'S09', 'S10', 'S11', 'S12', 'S13', 'S14', 'S15', 'S16', 'S17', 'S18', 'S19', 'S20', 'S21', 'S22', 'S23', 'S24', 'S25', 'S26']
['S05', 'S06']
[('SO₂', 'plain'), ('O₂ + N₂', 'plain'), ('SO₃', 'claimed')]
False False
```

So `cycle.json` gains `prologue`, and every step gains `path` (in viewer coordinates), `scene` and `species` (payloads with `status`; S16's sulfur trioxide is `claimed` because S16 fails in the screening), seven steps gain `reaction`, gas and water actors carry species payloads instead of `color`, and S23 carries two `coat` actors; `camera` is gone. `manifest.json` and the manifest inside `claims.json` lose `fields` and record the commit of Step 8: `uv run python -c "import json; print(json.load(open('viewer/data/manifest.json'))['commit'])"` prints the same hash as `git rev-parse HEAD`. `cycle.json` writes the subscripts as JSON escapes (`"SO₂"`), which `JSON.parse` reads back as `SO₂`.

Run: `uv run pytest -q -W error`
Expected: `293 passed, 1 xfailed`.

- [ ] **Step 11: Commit the regenerated data separately**

```bash
git add viewer/data
git commit -F - <<'EOF'
Regenerate the viewer data: paths, scene flags and species in cycle.json

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
```

From this commit on, plan A's viewer (`viewer/main.js`, `viewer/timeline.js`) can no longer play the cycle: its steps have no `camera` and its manifest no `fields`. That is expected; Task 3 starts the replacement and Task 10 deletes the old modules. Every viewer task reads this `cycle.json`, so this commit must exist before Task 3 starts.

### Task 3: Store, data loading, page skeleton, boot

**Files:**
- Create: `viewer/store.js`
- Create: `viewer/data/load.js`
- Create: `viewer/app.js`
- Modify (rewrite in full): `viewer/index.html`
- Modify (rewrite in full): `viewer/style.css`
- Test: the browser checks in Steps 7 to 10 (there is no JavaScript test runner)

**Interfaces:**
- Consumes:
  - `viewer/data/cycle.json` as regenerated by Task 2: `{notice, prologue: {duration, path}, steps: [...], curves}`, with each step carrying `id, title, duration, path, scene, species, actors` (and `reaction` on seven of them).
  - `viewer/data/claims.json`, which Task 2 does not change: `{manifest, claims, spaces}`. Here `claims` is a **list** of 71 entries, each with `id, statement, subsystem, timestamp, tier, piece, criterion, status, basis, numbers, spaces`, and `spaces` maps the 22 space names to `{label, quantities, claims}`.
  - `viewer/data/manifest.json` (Task 2).
  - The header's contracts for `viewer/store.js`, `viewer/data/load.js`, `viewer/index.html` and `viewer/app.js`.
- Produces:
  - `viewer/store.js`: `DEFAULT_STATE`, `createStore(initial)`, `readUrl(location)`, exactly as the header.
  - `viewer/data/load.js`: `loadData(base = 'data/') -> Promise<{claims, cycle, manifest}>`, `validateCycle(cycle)`, `validateClaims(claims)`. `loadData` re-keys `claims.claims` by claim id, so every later task reads `claims.claims[id]` (for example `claims.claims.S07.statement`), as the header's `mountCinematic` contract does.
  - Page elements by id: `notice`, `message`, `stage`, `hud`, `inspector`, in that body order.
  - CSS custom properties on `:root`: `--bg`, `--surface`, `--raised`, `--line`, `--text`, `--muted`, `--accent`, `--notice-height`, and the verdict colours `--pass`, `--fail`, `--conditional`, `--undefined`, `--pending`. Classes `.labels`, `.placeholder-label`, `.pending-label`.
  - `viewer/app.js`: the helpers `fail(text)` and `storedQuality()`. Inside `async function boot()`: `url`, `claims`, `cycle`, `manifest`, `fixedQuality` (null when neither `?quality=` nor localStorage chose a tier), `store`, `stateParts`, `state`, and `window.viewer = { store, claims, cycle, manifest, state }`. `claims`, `cycle` and `manifest` are among the keys the header's `window.viewer` lists for the browser checks.
  - The extension rule every later task follows: the file grows by additions only. Each later task adds its block inside `boot()` under a `// ---- ` heading that names the task, at the place the header's boot order gives it. From Task 4 on, whatever `frame()` reads is created above the line `rendererApi.start(frame);` (above Task 4's last block, `// ---- start (Task 4)`, or just before that line, as each task says); what the header orders after `start(frame)` (the deep link, the quality probe) goes after that line; the WebGL 2 check goes before the renderer is created. Expose objects with `Object.assign(window.viewer, {...})` and add `state()` fields with `stateParts.push(fn)`.

Background for the implementer. This task replaces the page shell. The old `viewer/main.js`, `scene.js`, `timeline.js` and `panel.js` stay on disk, unreferenced, until Task 10 deletes them. After this task the page shows the notice and an empty dark page; the scene arrives in Task 4.

Browser checks follow the header's procedure: the `viewer` preview (`preview_start` with `name: "viewer"`), the URL `http://localhost:8765/?quality=low`, a 1280 x 800 viewport, and the JavaScript tool through `window.viewer`. `python3 -m http.server` sends no cache headers, so after editing a file, fetch the edited files afresh and reload before checking:

```js
await Promise.all(['style.css', 'app.js', 'store.js', 'data/load.js'].map(url => fetch(url, { cache: 'reload' })));
location.reload();
```

A check that runs several statements is wrapped as `await (async () => { ... })()`, so repeated runs never redeclare a name.

- [ ] **Step 1: State what must be observed, and see that it is not there yet**

After this task the page at `http://localhost:8765/?quality=low` must:

1. Have these body children, in order: `#notice` (the first element, fixed at the top, 28 px high, text from `cycle.notice`), `#message` (hidden), `#stage`, `#hud`, `#inspector` (hidden), and the module script `app.js`.
2. Load the three data files and expose `window.viewer = { store, claims, cycle, manifest, state }`, with `claims.claims` keyed by id.
3. Report `viewer.state()` as `{mode: 'cinematic', quality: 'low', interior: false, weather: 'clear', riding: true}`.
4. Log no error of its own to the console.

Run: `preview_start` with name `viewer`, then `navigate` to `http://localhost:8765/?quality=low`, then with `javascript_tool`:

```js
[document.getElementById('message') !== null, typeof window.viewer?.state]
```

Expected now: `[false, "undefined"]`. This is plan A's page, which has no `#message` and no `state()`. Its console may also show errors from plan A's modules reading the data shape Task 2 changed (for example `step.camera`, which became `path`). This task replaces that page.

- [ ] **Step 2: Write `viewer/store.js`**

```js
// The page's state in one object. Modules read it with get(), change it with set(patch), and
// subscribe to hear which keys changed. Nothing else holds state that two modules share.

export const DEFAULT_STATE = {
  mode: 'cinematic',          // 'cinematic' | 'inspector' (inspector is plan V2; the key exists now)
  case: 'claim',              // 'claim' | a case id (V2)
  stepIndex: -1,              // -1 = prologue, 0..30 = steps
  t: 0,                       // seconds from the start of the prologue
  playing: false,
  quality: 'medium',          // 'low' | 'medium' | 'high'
  layers: { masonry: 1, bedrock: 1, hidden: new Set() },   // opacities 0..1; hidden = space names switched off
  cutaway: { on: false, axis: 'ns', position: 0.5 },        // V2 uses it; the key exists now
  picked: null,
  reading: 'survey',          // 'survey' | 'alternative'
  hud: { visible: true },
  reducedMotion: false,       // from matchMedia('(prefers-reduced-motion: reduce)')
  riding: true,               // false while the user has taken the camera
  interior: false,            // the current step's scene.interior
  weather: 'clear',           // the current step's scene.weather
};

const NESTED = ['layers', 'cutaway', 'hud'];   // set() merges these one level deep
const QUALITIES = ['low', 'medium', 'high'];

// A copy that shares no object with the state given, so two stores never share the hidden Set.
function copy(state) {
  return {
    ...state,
    layers: { ...state.layers, hidden: new Set(state.layers.hidden) },
    cutaway: { ...state.cutaway },
    hud: { ...state.hud },
  };
}

// Equality for the values this state holds: primitives, Sets of names, and plain objects of those.
function same(a, b) {
  if (a instanceof Set || b instanceof Set) {
    return a instanceof Set && b instanceof Set && a.size === b.size && [...a].every(item => b.has(item));
  }
  if (a && b && typeof a === 'object' && typeof b === 'object') {
    const keys = new Set([...Object.keys(a), ...Object.keys(b)]);
    return [...keys].every(key => same(a[key], b[key]));
  }
  return Object.is(a, b);
}

// initial: a whole state, shaped as DEFAULT_STATE.
export function createStore(initial = DEFAULT_STATE) {
  let state = copy(initial);
  const subscribers = new Set();
  return {
    get: () => state,
    // Replaces keys, merging layers, cutaway and hud one level deep. A Set is compared by its members,
    // so pass a new Set to change layers.hidden. Subscribers run synchronously, and only on a change.
    set(patch) {
      const next = { ...state };
      const changed = new Set();
      for (const [key, value] of Object.entries(patch)) {
        const merged = NESTED.includes(key) ? { ...state[key], ...value } : value;
        if (same(state[key], merged)) continue;
        next[key] = merged;
        changed.add(key);
      }
      if (!changed.size) return;
      const prev = state;
      state = next;
      for (const fn of [...subscribers]) fn(next, prev, changed);
    },
    subscribe(fn) {
      subscribers.add(fn);
      return () => subscribers.delete(fn);
    },
  };
}

// What the address asks for: '#S16' -> stepId 'S16'; '?mode=inspector', '?quality=low', '?nowebgl=1'.
// Any word after '#' counts as a step id here; the player sends an id it does not know to the prologue.
export function readUrl(location) {
  const hash = /^#(\w+)$/.exec(location.hash || '');
  const query = new URLSearchParams(location.search || '');
  const quality = query.get('quality');
  return {
    stepId: hash ? hash[1] : null,
    mode: query.get('mode') === 'inspector' ? 'inspector' : 'cinematic',
    quality: QUALITIES.includes(quality) ? quality : null,
    nowebgl: query.get('nowebgl') === '1',
  };
}
```

- [ ] **Step 3: Write `viewer/data/load.js`**

The file lives beside the generated data, as the header's file structure places it. `pyramid/viewer_data.py` writes named files into `viewer/data/` and never deletes others, so regeneration leaves it in place.

```js
// Fetch and check the three files the page draws from. A file that is missing, or that lacks a key the
// page reads, stops the page with the file's name and the reason (app.js shows it in #message).

const CYCLE_KEYS = ['notice', 'prologue', 'steps', 'curves'];
const PROLOGUE_KEYS = ['duration', 'path'];
const STEP_KEYS = ['id', 'title', 'duration', 'path', 'scene', 'species', 'actors'];
const CLAIMS_KEYS = ['claims', 'spaces', 'manifest'];
const CLAIM_KEYS = ['id', 'statement', 'status', 'basis'];

async function getJSON(url) {
  const response = await fetch(url).catch(error => {
    throw new Error(`${url}: ${error.message}`);
  });
  if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
  try {
    return await response.json();
  } catch {
    throw new Error(`${url}: not valid JSON`);
  }
}

// Throws "<where>missing key <key>" for the first key the object lacks.
function need(object, keys, where) {
  for (const key of keys) {
    if (object === null || typeof object !== 'object' || !(key in object)) {
      throw new Error(`${where}missing key ${key}`);
    }
  }
}

export function validateCycle(cycle) {
  need(cycle, CYCLE_KEYS, 'cycle.json: ');
  need(cycle.prologue, PROLOGUE_KEYS, 'cycle.json: prologue: ');
  if (!Array.isArray(cycle.steps)) throw new Error('cycle.json: steps is not a list');
  cycle.steps.forEach((step, i) => {
    const name = step && step.id ? step.id : `step ${i + 1}`;
    need(step, STEP_KEYS, `cycle.json: ${name}: `);
  });
  return cycle;
}

export function validateClaims(claims) {
  need(claims, CLAIMS_KEYS, 'claims.json: ');
  if (!Array.isArray(claims.claims)) throw new Error('claims.json: claims is not a list');
  for (const claim of claims.claims) {
    need(claim, CLAIM_KEYS, `claims.json: ${claim && claim.id ? claim.id : 'a claim'}: `);
  }
  return claims;
}

// Fetch one file and validate it; a validation error gains the base, so it names the file as fetched.
async function fetchChecked(base, name, validate) {
  const data = await getJSON(base + name);
  try {
    return validate(data);
  } catch (error) {
    throw new Error(base + error.message);   // 'cycle.json: missing key steps' -> 'data/cycle.json: missing key steps'
  }
}

export async function loadData(base = 'data/') {
  // One file after another, so the failure reported is always that of the first file that fails.
  const cycle = await fetchChecked(base, 'cycle.json', validateCycle);
  const claims = await fetchChecked(base, 'claims.json', validateClaims);
  const manifest = await getJSON(`${base}manifest.json`);
  // The file lists the claims; the page looks them up by id (claims.claims.S07.statement).
  claims.claims = Object.fromEntries(claims.claims.map(claim => [claim.id, claim]));
  return { claims, cycle, manifest };
}
```

- [ ] **Step 4: Write `viewer/index.html`**

The empty `data:` icon stops the browser from requesting `/favicon.ico`, which the server does not have and which would show as a console error. The notice carries its text in the markup as well, so it is on screen even when the data fail to load. `app.js` then sets it from `cycle.notice`.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Great Pyramid: the claimed cycle</title>
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="style.css">
  <script type="importmap">
    {
      "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/"
      }
    }
  </script>
</head>
<body>
  <div id="notice" role="note">Animation of the claim. Not a simulation result.</div>
  <p id="message" role="alert" hidden></p>
  <main id="stage" aria-label="3D view of the pyramid and its interior"></main>
  <div id="hud"></div>
  <div id="inspector" hidden></div>
  <script type="module" src="app.js"></script>
</body>
</html>
```

- [ ] **Step 5: Write `viewer/style.css`**

`#message` and `#inspector` are shown and hidden with the `hidden` attribute. A `display` rule in an author style sheet would override the attribute, so the second rule below makes `hidden` win everywhere.

```css
/* Viewer layout and colours. Plain CSS, no build step. */
:root {
  color-scheme: dark;
  --bg: #15171a;
  --surface: #1c1f23;
  --raised: #262a2f;
  --line: #2f3339;
  --text: #e7e3da;
  --muted: #9da3ab;
  --accent: #c9b891;
  /* verdict colours: badges, chips and the progress strip only, never a scene material */
  --pass: #56b884;
  --fail: #e0655f;
  --conditional: #e3aa45;
  --undefined: #8f949c;
  --pending: #7f9db8;
  --notice-height: 28px;
}

* { box-sizing: border-box; }
[hidden] { display: none !important; }   /* no display rule below may show a hidden element */
html, body { height: 100%; margin: 0; overflow: hidden; }   /* full screen: the page itself never scrolls */
body {
  background: var(--bg);
  color: var(--text);
  font: 14px/1.45 system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

button {
  font: inherit; color: var(--text); background: var(--raised);
  border: 1px solid var(--line); border-radius: 6px; padding: 6px 10px; cursor: pointer;
}
button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

/* the notice: first in the page, fixed over everything, in every mode, in fullscreen and with the HUD hidden */
#notice {
  position: fixed; top: 0; left: 0; right: 0; z-index: 10;
  height: var(--notice-height); line-height: var(--notice-height); padding: 0 8px; text-align: center;
  font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  background: var(--raised); border-bottom: 1px solid var(--line);
}

/* the scene fills the window; the notice lies over its top edge */
#stage { position: fixed; inset: 0; z-index: 0; overflow: hidden; }
#stage canvas { display: block; }
#stage .labels { position: absolute; top: 0; left: 0; pointer-events: none; }

/* the HUD covers the stage below the notice; only its controls take the pointer, so the canvas still orbits */
#hud { position: fixed; inset: var(--notice-height) 0 0 0; z-index: 5; pointer-events: none; }
#hud > * { pointer-events: auto; }

/* why the page stopped: a missing or malformed data file, or no WebGL 2 */
#message {
  position: fixed; top: calc(var(--notice-height) + 16px); left: 16px; right: 16px; z-index: 9;
  max-width: 640px; margin: 0 auto; padding: 12px 16px;
  background: var(--surface); border: 1px solid var(--line); border-left: 3px solid var(--accent); border-radius: 6px;
}

/* labels drawn in the scene by CSS2DRenderer */
.placeholder-label, .pending-label {
  padding: 2px 6px; border-radius: 4px; font-size: 12px; white-space: nowrap;
  background: rgba(21, 23, 26, 0.85); color: var(--text); border: 1px dashed var(--undefined);
}
.pending-label { color: var(--pending); border-color: var(--pending); }

/* phone width: the notice keeps one line; scene labels shrink so they cover less of the view */
@media (max-width: 760px) {
  #notice { font-size: 12px; }
  .placeholder-label, .pending-label { font-size: 11px; }
}
```

- [ ] **Step 6: Write `viewer/app.js`**

`boot()` is an async function, not top-level code, so a failure can stop the page with a plain `return`, and no exception reaches the console. An error nobody expected still lands in `#message`, and in the console for whoever debugs it. The state shown here is the file at the end of this task.

```js
// Boot: read the URL, load the data and create the store; later tasks add the scene.
// Each task adds its block inside boot(), in the boot order of the plan header.
import { DEFAULT_STATE, createStore, readUrl } from './store.js';
import { loadData } from './data/load.js';

const message = document.getElementById('message');

// Say what stopped the page, under the notice.
function fail(text) {
  message.textContent = text;
  message.hidden = false;
}

// The tier an earlier visit saved, or null (localStorage is a per-viewer convenience and may be blocked).
function storedQuality() {
  try {
    const value = localStorage.getItem('viewer.quality');
    return ['low', 'medium', 'high'].includes(value) ? value : null;
  } catch {
    return null;
  }
}

async function boot() {
  const url = readUrl(location);

  // ---- data (Task 3)
  let data;
  try {
    data = await loadData();
  } catch (error) {
    fail(error.message);
    return;
  }
  const { claims, cycle, manifest } = data;
  document.getElementById('notice').textContent = cycle.notice;

  // ---- store (Task 3)
  const fixedQuality = url.quality ?? storedQuality();   // null: nothing asked for a tier, so the probe may choose
  const store = createStore({
    ...DEFAULT_STATE,
    mode: url.mode,
    quality: fixedQuality ?? DEFAULT_STATE.quality,
    reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
  });

  // ---- window.viewer (Task 3): later tasks add objects with Object.assign and state() parts with stateParts.push
  const stateParts = [() => {
    const { mode, quality, interior, weather, riding } = store.get();
    return { mode, quality, interior, weather, riding };
  }];
  const state = () => Object.assign({}, ...stateParts.map(part => part()));
  window.viewer = { store, claims, cycle, manifest, state };
}

boot().catch(error => {
  fail(error.message);
  console.error(error);
});
```

- [ ] **Step 7: Browser check: the page shell, the notice first, the message hidden, the console clean**

Fetch the edited files afresh and reload (the snippet in the background above), then `navigate` to `http://localhost:8765/?quality=low` and run with `javascript_tool`:

```js
({
  order: [...document.body.children].map(element => element.id || element.tagName.toLowerCase()),
  notice: document.getElementById('notice').textContent,
  noticeBox: [document.getElementById('notice').getBoundingClientRect().top, document.getElementById('notice').getBoundingClientRect().height],
  messageHidden: document.getElementById('message').hidden,
  messageDisplay: getComputedStyle(document.getElementById('message')).display,
  inspectorHidden: document.getElementById('inspector').hidden,
  stage: [getComputedStyle(document.getElementById('stage')).position, document.getElementById('stage').clientWidth === innerWidth, document.getElementById('stage').clientHeight === innerHeight],
  title: document.title,
  oldScript: document.querySelector('script[src="main.js"]') !== null,
})
```

Expected:

- `order` begins `["notice", "message", "stage", "hud", "inspector", "script"]`. Anything the Browser pane appends after `script` is not the page's.
- `notice` is `"Animation of the claim. Not a simulation result."`.
- `noticeBox` is `[0, 28]`.
- `messageHidden` is `true` and `messageDisplay` is `"none"`.
- `inspectorHidden` is `true`.
- `stage` is `["fixed", true, true]`.
- `title` is `"Great Pyramid: the claimed cycle"`.
- `oldScript` is `false`.

Then `read_console_messages` with `onlyErrors: true`. Expected: no entry from the page (the tool's own "probe-console-reader" entry does not count). Take a `screenshot`: the notice bar across the top and an empty dark page below it.

- [ ] **Step 8: Browser check: the data are loaded, the claims keyed by id, the state reported**

```js
({
  state: viewer.state(),
  steps: viewer.cycle.steps.length,
  prologueKeyframes: viewer.cycle.prologue.path.length,
  claimIds: Object.keys(viewer.claims.claims).length,
  s07: [typeof viewer.claims.claims.S07.statement, viewer.claims.claims.S07.status, viewer.claims.claims.S07.id],
  spaces: Object.keys(viewer.claims.spaces).length,
  manifest: typeof viewer.manifest.commit,
  hiddenIsSet: viewer.store.get().layers.hidden instanceof Set,
})
```

Expected:

- `state` is `{mode: "cinematic", quality: "low", interior: false, weather: "clear", riding: true}`.
- `steps` is `31` and `prologueKeyframes` is `3`.
- `claimIds` is `71`: 31 steps and 40 evidence claims.
- `s07` is `["string", "fail", "S07"]`.
- `spaces` is `22`.
- `manifest` is `"string"`.
- `hiddenIsSet` is `true`.

- [ ] **Step 9: Browser check: a missing or malformed file names the file and the reason (Review Focus 2)**

The missing file:

```js
await (await import('./data/load.js')).loadData('nowhere/').then(() => 'resolved', error => error.message)
```

Expected: `"nowhere/cycle.json: HTTP 404"`. This check's own request also adds one browser network entry to the console ("Failed to load resource: ... 404" for `nowhere/cycle.json`). That entry belongs to the check, not to the page.

A file that lacks a key. The check swaps `fetch` for a stub that returns a cycle without `steps`, then puts the real one back:

```js
await (async () => {
  const load = await import('./data/load.js');
  const realFetch = window.fetch;
  window.fetch = async () => new Response('{"notice": "x", "prologue": {"duration": 6, "path": []}}');
  let missing;
  try {
    missing = await load.loadData('data/').then(() => 'resolved', error => error.message);
  } finally {
    window.fetch = realFetch;
  }
  const thrown = f => { try { f(); return 'no error'; } catch (error) { return error.message; } };
  return [
    missing,
    thrown(() => load.validateCycle({ ...viewer.cycle, steps: [{ id: 'S03' }] })),
    thrown(() => load.validateClaims({ claims: [], spaces: {} })),
    thrown(() => load.validateClaims({ claims: {}, spaces: {}, manifest: {} })),
    load.validateCycle(viewer.cycle) === viewer.cycle,
  ];
})()
```

Expected: `["data/cycle.json: missing key steps", "cycle.json: S03: missing key title", "claims.json: missing key manifest", "claims.json: claims is not a list", true]`.

- [ ] **Step 10: Browser check: the store and readUrl**

```js
await (async () => {
  const { DEFAULT_STATE, createStore, readUrl } = await import('./store.js');
  const store = createStore();
  const calls = [];
  store.subscribe((next, prev, changed) => calls.push(`${[...changed].join()}:${prev.quality}>${next.quality}`));
  store.set({ quality: 'low' });
  store.set({ quality: 'low' });                          // no change: no call
  store.set({ hud: { visible: false } });                 // merged one level deep
  store.set({ layers: { hidden: new Set(['pit']) } });    // masonry and bedrock stay
  store.set({ layers: { hidden: new Set(['pit']) } });    // an equal Set: no call
  store.set({ stepIndex: 4, t: 12 });
  const s = store.get();
  return {
    calls,
    layers: [s.layers.masonry, s.layers.bedrock, [...s.layers.hidden]],
    hud: s.hud.visible,
    defaultsUntouched: DEFAULT_STATE.layers.hidden.size === 0 && DEFAULT_STATE.quality === 'medium' && DEFAULT_STATE.hud.visible,
    urls: [
      readUrl({ hash: '#S16', search: '' }),
      readUrl({ hash: '', search: '?quality=low' }),
      readUrl({ hash: '', search: '?mode=inspector' }),
      readUrl({ hash: '', search: '?nowebgl=1' }),
      readUrl({ hash: '#', search: '?quality=ultra&mode=other' }),
      readUrl({ hash: '#S99', search: '' }).stepId,
    ],
  };
})()
```

Expected:

```
calls: ["quality:medium>low", "hud:low>low", "layers:low>low", "stepIndex,t:low>low"]
layers: [1, 1, ["pit"]]
hud: false
defaultsUntouched: true
urls: [
  {stepId: "S16", mode: "cinematic", quality: null, nowebgl: false},
  {stepId: null, mode: "cinematic", quality: "low", nowebgl: false},
  {stepId: null, mode: "inspector", quality: null, nowebgl: false},
  {stepId: null, mode: "cinematic", quality: null, nowebgl: true},
  {stepId: null, mode: "cinematic", quality: null, nowebgl: false},
  "S99"
]
```

Then `read_console_messages` with `onlyErrors: true`. Expected: only the one 404 network entry from Step 9's request, and nothing else from the page.

- [ ] **Step 11: Confirm the old modules are unreferenced and the Python suite still passes**

Run: `grep -n "main.js\|scene.js\|timeline.js\|panel.js" viewer/index.html viewer/app.js viewer/store.js viewer/data/load.js`
Expected: no output, exit status 1.

Run: `uv run pytest -q -W error`
Expected: every test passes, with the same count as after Task 2 (this task changes no Python and no data).

- [ ] **Step 12: Commit**

```bash
git add viewer/index.html viewer/style.css viewer/app.js viewer/store.js viewer/data/load.js
git commit -m "Start the cinematic viewer: page shell, state store, data loading and boot" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 4: Renderer and environment

**Files:**
- Create: `viewer/render/renderer.js`
- Create: `viewer/render/environment.js`
- Modify: `viewer/app.js` (two imports, one block, and a last "start" block; the whole file is shown in Step 4)
- Test: the browser checks in Steps 5 to 10

**Interfaces:**
- Consumes:
  - From Task 3: `store` (`get()`, `set()`, `subscribe(fn(next, prev, changed))`) with the keys `quality`, `interior`, `weather`, `reducedMotion`; the `#stage` element; and, in `viewer/app.js`, `boot()`, `stateParts`, `window.viewer` and the block rule.
  - three.js 0.170.0 from the import map: `three`, `three/addons/controls/OrbitControls.js`, `three/addons/renderers/CSS2DRenderer.js`, `three/addons/postprocessing/EffectComposer.js`, `RenderPass.js`, `UnrealBloomPass.js`, `SMAAPass.js`, `OutputPass.js`, and `three/addons/objects/Sky.js`.
- Produces:
  - `viewer/render/renderer.js`: `TIERS` and `createRenderer(stage, store)` exactly as the header. It returns `{ renderer, camera, controls, labels, scene, composer, resize, setQuality, start, measure, lastDt, dispose }`. `scene` is the one scene every later module adds to. `renderer.localClippingEnabled` is `true`, so Tasks 5 and 6 can clip with planes on their materials. `lastDt` is a property updated every frame. `measure(seconds)` resolves with the median frame time in ms, or `NaN` when no frame was drawn (a hidden page); `NaN` leaves Task 10's probe on the tier it has. `setQuality(tier)` sizes the shadow map of every `DirectionalLight` in the scene and switches its `castShadow`.
  - `viewer/render/environment.js`: `FADE_SECONDS` and `createEnvironment(scene, rendererApi, store)` exactly as the header. It returns `{ mix: {interior, storm}, update(dt, cameraInside), sun, ground, sky }`. `cameraInside` is the boolean app.js passes every frame (true when the camera position lies inside `model.bounds`); a private value `inside` eases toward it at 1/`FADE_SECONDS` per second (at once under reduced motion), and the ground's opacity is `1 - mix.interior * inside`, so an interior step filmed from outside (S06) keeps its plateau. The environment owns `renderer.toneMappingExposure`.
  - In `viewer/app.js`: the consts `rendererApi` and `environment`; `window.viewer.rendererApi` and `window.viewer.environment`; `state().lastDt`. The last block `// ---- start (Task 4)` holds `function frame(dt)`, whose body is `environment.update(dt, false);` (no model yet, so the camera is never inside it; Task 5 replaces `false` with `model.bounds.containsPoint(rendererApi.camera.position)`), then the fixed exterior pose, then `rendererApi.start(frame);`. Its comment line and these lines are the anchors later tasks edit against, so keep their text exactly. Tasks 5 to 10 add their blocks by Task 3's extension rule (above `rendererApi.start(frame);` whatever `frame()` reads; after it the deep link and the quality probe) and add their per-frame lines to `frame()` in the header's order: `environment.update(dt, model.bounds.containsPoint(camera.position)); materials.update(dt); model.setInterior(environment.mix.interior); player.tick(dt);`.

Background for the implementer. Three things here go beyond the header's one-line descriptions:

- **The output pass.** In three.js 0.170 the renderer applies tone mapping and the sRGB output transform only when it draws to the screen. `RenderPass` draws into the composer's render target, and neither the bloom pass nor the SMAA pass converts colours. The chain therefore ends with `OutputPass`, which applies `renderer.toneMapping` (ACES filmic) and `renderer.outputColorSpace` (sRGB), as three.js's own bloom and SMAA examples do. The header's chain `RenderPass -> UnrealBloomPass -> SMAAPass` stays as stated, with `OutputPass` after it.
- **Shadow maps per tier.** The renderer cannot see the environment's sun, so `setQuality` walks the scene for `DirectionalLight`s. A point light (Task 6's flash) never casts shadows. `createEnvironment` calls `rendererApi.setQuality(store.get().quality)` once its sun exists, so the sun gets the current tier's map at once.
- **The sky.** The `Sky` addon's vertex shader puts the sky on the far plane, so its scale only has to enclose the camera. The environment map is made the way three.js's ocean example makes it: the sky is moved into a scene of its own for `PMREMGenerator.fromScene`, then put back.

The camera's near and far planes (0.5 m and 40 km) are display choices. They span a passage to the 20 km plateau's horizon, which the fog hides.

The Browser pane may report `document.visibilityState === "hidden"`. The animation loop then stops, and with it the fades and `measure`. Before any check that waits on frames, take a `screenshot` (which brings the pane forward), then wait, then read. If a read still shows no progress and `document.visibilityState` is `"hidden"`, bring the Browser pane to the front and repeat the wait.

- [ ] **Step 1: State what must be observed, and see that it is not there yet**

After this task, at `http://localhost:8765/?quality=low`:

1. A canvas fills `#stage`, under the notice. It shows a sand plateau to a fogged horizon under a daylight sky, seen from the south-east at the fixed pose.
2. `viewer.state().quality` is `"low"`. The tier settings show on the renderer: pixel ratio, shadow map, and the bloom pass on or off.
3. `viewer.store.set({weather: 'storm'})` darkens the sky within 2 s, and `{weather: 'clear'}` brings it back.
4. `viewer.store.set({interior: true})` leaves the ground in place while the camera is outside (Task 4's `frame` passes `cameraInside` false), and fades it out within 2 s once the camera counts as inside.
5. `viewer.rendererApi.measure(1)` resolves to a finite number of milliseconds. `viewer.state().lastDt` is at most 0.1.
6. The console holds no error from the page.

Run: `navigate` to `http://localhost:8765/?quality=low`, then with `javascript_tool`:

```js
[document.querySelector('#stage canvas') !== null, typeof viewer.rendererApi]
```

Expected now: `[false, "undefined"]`.

- [ ] **Step 2: Write `viewer/render/renderer.js`**

```js
// WebGL renderer, camera, orbit controls, label layer, post-processing, quality tiers and the frame loop.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CSS2DRenderer } from 'three/addons/renderers/CSS2DRenderer.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

// display choice: what each quality tier spends on the picture
export const TIERS = {
  low:    { pixelRatio: 1,   shadowMap: 0,    bloom: false, particles: false },
  medium: { pixelRatio: 1.5, shadowMap: 1024, bloom: true,  particles: false },
  high:   { pixelRatio: 2,   shadowMap: 2048, bloom: true,  particles: true },
};
const FOV = 45;   // display choice: vertical angle of view in degrees, on a stage at least 5:4 wide
const NEAR = 0.5;   // display choice: metres
const FAR = 40000;  // display choice: metres, beyond the plateau's edge
const BLOOM = { strength: 0.6, radius: 0.4, threshold: 0.85 };   // display choice: threshold high enough that stone never blooms
const MAX_DT = 0.1;   // seconds: a tab that was in the background resumes with a long gap

export function createRenderer(stage, store) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.localClippingEnabled = true;   // water and gas skins are clipped by planes on their materials
  stage.append(renderer.domElement);

  const labels = new CSS2DRenderer();   // HTML labels that follow points of the scene
  labels.domElement.className = 'labels';
  stage.append(labels.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(FOV, 1, NEAR, FAR);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  // Render, bloom, antialias, then tone mapping and sRGB: the renderer applies those two only when it
  // draws to the screen, and the passes before draw into render targets.
  const composer = new EffectComposer(renderer);
  const bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), BLOOM.strength, BLOOM.radius, BLOOM.threshold);
  composer.addPass(new RenderPass(scene, camera));
  composer.addPass(bloom);
  composer.addPass(new SMAAPass(1, 1));   // sized by composer.setSize in resize()
  composer.addPass(new OutputPass());

  function resize() {
    const width = stage.clientWidth;
    const height = stage.clientHeight;
    if (!width || !height) return;
    renderer.setSize(width, height);
    composer.setSize(width, height);
    labels.setSize(width, height);
    camera.aspect = width / height;
    // A stage narrower than 5:4 (a phone) keeps the width of view of a 5:4 one by opening the
    // vertical angle, so a step's camera shows the same stretch of the passages on every screen.
    const half = Math.tan(THREE.MathUtils.degToRad(FOV / 2)) * Math.max(1, 1.25 / camera.aspect);
    camera.fov = THREE.MathUtils.radToDeg(2 * Math.atan(half));
    camera.updateProjectionMatrix();
  }
  const observer = new ResizeObserver(resize);
  observer.observe(stage);

  function setQuality(tier) {
    const { pixelRatio, shadowMap, bloom: glow } = TIERS[tier];
    const ratio = Math.min(pixelRatio, window.devicePixelRatio);
    renderer.setPixelRatio(ratio);
    composer.setPixelRatio(ratio);
    renderer.shadowMap.enabled = shadowMap > 0;
    scene.traverse(object => {   // the environment's sun; point lights never cast shadows here
      if (!object.isDirectionalLight) return;
      object.castShadow = shadowMap > 0;
      object.shadow.mapSize.set(shadowMap, shadowMap);
      object.shadow.map?.dispose();   // rebuilt at the new size on the next frame
      object.shadow.map = null;
    });
    bloom.enabled = glow;
    resize();
  }

  const clock = new THREE.Clock();
  let samples = null;   // frame times in ms while measure() runs

  function start(onFrame) {
    clock.start();
    renderer.setAnimationLoop(() => {
      const delta = clock.getDelta();
      if (samples) samples.push(delta * 1000);
      api.lastDt = Math.min(delta, MAX_DT);
      onFrame(api.lastDt);
      controls.update();
      composer.render(api.lastDt);
      labels.render(scene, camera);
    });
  }

  // The median frame time over a stretch of wall-clock time; NaN if no frame was drawn (a hidden page).
  // ponytail: one measurement at a time; a call made while another runs takes over the sampling.
  // Give each call its own sample array if two callers ever need to overlap.
  function measure(seconds) {
    return new Promise(resolve => {
      const times = [];
      samples = times;
      setTimeout(() => {
        if (samples === times) samples = null;
        times.sort((a, b) => a - b);
        resolve(times.length ? times[Math.floor(times.length / 2)] : NaN);
      }, seconds * 1000);
    });
  }

  const unsubscribe = store.subscribe((next, prev, changed) => {
    if (changed.has('quality')) setQuality(next.quality);
  });

  function dispose() {
    renderer.setAnimationLoop(null);
    observer.disconnect();
    unsubscribe();
    controls.dispose();
    composer.dispose();
    renderer.dispose();
    renderer.domElement.remove();
    labels.domElement.remove();
  }

  const api = { renderer, camera, controls, labels, scene, composer, resize, setQuality, start, measure, lastDt: 0, dispose };
  setQuality(store.get().quality);
  return api;
}
```

- [ ] **Step 3: Write `viewer/render/environment.js`**

The weather and look values are display choices, not measurements, and nobody has seen them rendered yet. The implementer may tune the look constants (`CLEAR`, `STORM`, `AZIMUTH`, `SAND`, the hemisphere light, and `BLOOM` in `renderer.js`) after seeing them on screen; any tuning is a deviation and is recorded in the report with the old and new values, and the expected numbers in Steps 5 to 7 (`0.5`, `0.00025`, `18`, `0.4`, `0.3`, `0.0009`) are then the tuned constants' values. The plateau is a plane because the ledger holds no terrain. The storm look is drawn only when the store's `weather` is `storm`, which the player (Task 7) sets from `scene.weather` on S05 and S06 alone.

```js
// Sky, sun, ground and fog, and the cross-fades between the exterior and the interior look and between
// clear weather and storm. mix.interior and mix.storm run from 0 to 1 and are applied every frame. The ground
// and the fog go with mix.interior only while the camera is inside the model (cameraInside, from app.js), so an
// interior step filmed from outside keeps its plateau.
import * as THREE from 'three';
import { Sky } from 'three/addons/objects/Sky.js';

export const FADE_SECONDS = 1.5;   // display choice: look and weather cross-fade time

// display choice: the two weathers the mix moves between (sun elevation in degrees above the horizon)
const CLEAR = { elevation: 40, intensity: 3, turbidity: 2, exposure: 0.5, fog: 0.00025, fogColour: 0xc9d3dc };
const STORM = { elevation: 6, intensity: 0.4, turbidity: 18, exposure: 0.3, fog: 0.0009, fogColour: 0x50565e };
const AZIMUTH = -35;         // display choice: degrees from south towards east; the sun stands in the south-south-west
const SKY_SCALE = 50000;     // display choice: the sky box only has to enclose the camera; its shader draws it at the far plane
const SUN_DISTANCE = 400;    // display choice: metres from the pyramid's axis to the shadow camera
const SHADOW_HALF = 200;     // display choice: the shadow camera covers a 400 m box around the pyramid
const GROUND_SIZE = 20000;   // display choice: the plateau plane, 20 km across, its edge lost in the fog
const SAND = 0xc8b48a;       // display choice
const ENV_STEP = 0.05;       // display choice: the environment map is rebuilt when the storm mix has moved this far

export function createEnvironment(scene, rendererApi, store) {
  const { renderer } = rendererApi;
  const lerp = THREE.MathUtils.lerp;

  const sky = new Sky();
  sky.scale.setScalar(SKY_SCALE);
  scene.add(sky);

  const sun = new THREE.DirectionalLight(0xffffff, CLEAR.intensity);
  Object.assign(sun.shadow.camera, {
    left: -SHADOW_HALF, right: SHADOW_HALF, top: SHADOW_HALF, bottom: -SHADOW_HALF, near: 1, far: 2 * SUN_DISTANCE,
  });
  sun.shadow.camera.updateProjectionMatrix();
  sun.shadow.bias = -0.0005;   // display choice: no shadow acne on the faces
  scene.add(sun, sun.target);   // the target stays at the origin: the pyramid's axis at pavement level
  scene.add(new THREE.HemisphereLight(0xdfe8f0, 0x8a7a5a, 0.6));   // display choice: sky light and sand bounce

  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(GROUND_SIZE, GROUND_SIZE).rotateX(-Math.PI / 2),
    new THREE.MeshStandardMaterial({
      color: SAND, roughness: 1, transparent: true,
      polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1,   // behind any face at pavement level
    }),
  );
  ground.receiveShadow = true;
  scene.add(ground);

  scene.fog = new THREE.FogExp2(CLEAR.fogColour, CLEAR.fog);
  const fogClear = new THREE.Color(CLEAR.fogColour);
  const fogStorm = new THREE.Color(STORM.fogColour);

  // The environment map: the sky alone, rendered into a PMREM, as in three.js's ocean example.
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envScene = new THREE.Scene();
  let envTarget = null;
  let envStorm = 0;   // the storm mix the current map was made at

  function rebuildEnvironment() {
    envTarget?.dispose();
    envScene.add(sky);
    envTarget = pmrem.fromScene(envScene);
    scene.add(sky);
    scene.environment = envTarget.texture;
    envStorm = mix.storm;
  }

  const mix = { interior: 0, storm: 0 };
  const target = { interior: 0, storm: 0 };
  let inside = 0;   // 0..1, eases toward the cameraInside that app.js passes to update() every frame
  function aim(state) {
    target.interior = state.interior ? 1 : 0;
    target.storm = state.weather === 'storm' ? 1 : 0;
  }
  aim(store.get());
  store.subscribe((next, prev, changed) => {
    if (changed.has('interior') || changed.has('weather')) aim(next);
  });

  const sunDirection = new THREE.Vector3();

  function apply() {
    const k = mix.storm;
    const elevation = lerp(CLEAR.elevation, STORM.elevation, k);
    sunDirection.setFromSphericalCoords(1, THREE.MathUtils.degToRad(90 - elevation), THREE.MathUtils.degToRad(AZIMUTH));
    sky.material.uniforms.sunPosition.value.copy(sunDirection);
    sky.material.uniforms.turbidity.value = lerp(CLEAR.turbidity, STORM.turbidity, k);
    sun.position.copy(sunDirection).multiplyScalar(SUN_DISTANCE);
    sun.intensity = lerp(CLEAR.intensity, STORM.intensity, k);
    renderer.toneMappingExposure = lerp(CLEAR.exposure, STORM.exposure, k);
    scene.fog.color.lerpColors(fogClear, fogStorm, k);
    const gone = mix.interior * inside;   // the plateau goes only while an interior step is seen from inside
    scene.fog.density = lerp(CLEAR.fog, STORM.fog, k) * (1 - gone);   // no haze between an inside camera and the spaces
    ground.material.opacity = 1 - gone;
    ground.material.depthWrite = gone === 0;   // a fading ground must not hide the spaces under the plateau
    ground.visible = gone < 1;
    const settled = k !== envStorm && (k === 0 || k === 1);   // the last map of a fade is made at its end value
    if (Math.abs(k - envStorm) > ENV_STEP || settled) rebuildEnvironment();
  }

  // Each mix, and inside, moves toward its goal at 1 / FADE_SECONDS per second, or at once under reduced motion.
  // cameraInside: true when the camera position lies inside the model's bounds (app.js tests it every frame).
  function update(dt, cameraInside) {
    const step = store.get().reducedMotion ? 1 : dt / FADE_SECONDS;
    const ease = (value, goal) => (Math.abs(goal - value) <= step ? goal : value + Math.sign(goal - value) * step);
    mix.interior = ease(mix.interior, target.interior);
    mix.storm = ease(mix.storm, target.storm);
    inside = ease(inside, cameraInside ? 1 : 0);
    apply();
  }

  apply();               // first: Sky's sunPosition starts at (0, 0, 0), and an environment map built from it is NaN
  rebuildEnvironment();
  rendererApi.setQuality(store.get().quality);   // sizes the new sun's shadow map for the current tier
  return { mix, update, sun, ground, sky };
}
```

- [ ] **Step 4: Extend `viewer/app.js`**

Replace the two comment lines at the top and add the two imports. Then add the block `// ---- renderer and environment (Task 4)` after the `window.viewer` block, and the last block `// ---- start (Task 4)` after that. The whole file after this step:

```js
// Boot: read the URL, load the data, create the store and the scene, start the loop.
// Each task adds its block above "start", in the boot order of the plan header.
import { DEFAULT_STATE, createStore, readUrl } from './store.js';
import { loadData } from './data/load.js';
import { createRenderer } from './render/renderer.js';
import { createEnvironment } from './render/environment.js';

const message = document.getElementById('message');

// Say what stopped the page, under the notice.
function fail(text) {
  message.textContent = text;
  message.hidden = false;
}

// The tier an earlier visit saved, or null (localStorage is a per-viewer convenience and may be blocked).
function storedQuality() {
  try {
    const value = localStorage.getItem('viewer.quality');
    return ['low', 'medium', 'high'].includes(value) ? value : null;
  } catch {
    return null;
  }
}

async function boot() {
  const url = readUrl(location);

  // ---- data (Task 3)
  let data;
  try {
    data = await loadData();
  } catch (error) {
    fail(error.message);
    return;
  }
  const { claims, cycle, manifest } = data;
  document.getElementById('notice').textContent = cycle.notice;

  // ---- store (Task 3)
  const fixedQuality = url.quality ?? storedQuality();   // null: nothing asked for a tier, so the probe may choose
  const store = createStore({
    ...DEFAULT_STATE,
    mode: url.mode,
    quality: fixedQuality ?? DEFAULT_STATE.quality,
    reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
  });

  // ---- window.viewer (Task 3): later tasks add objects with Object.assign and state() parts with stateParts.push
  const stateParts = [() => {
    const { mode, quality, interior, weather, riding } = store.get();
    return { mode, quality, interior, weather, riding };
  }];
  const state = () => Object.assign({}, ...stateParts.map(part => part()));
  window.viewer = { store, claims, cycle, manifest, state };

  // ---- renderer and environment (Task 4)
  const rendererApi = createRenderer(document.getElementById('stage'), store);
  const environment = createEnvironment(rendererApi.scene, rendererApi, store);
  stateParts.push(() => ({ lastDt: rendererApi.lastDt }));
  Object.assign(window.viewer, { rendererApi, environment });

  // ---- start (Task 4): stays the last block, so everything frame() reads exists before the first frame
  function frame(dt) {
    environment.update(dt, false);   // no model yet, so the camera is never inside it
  }
  // display choice: an exterior pose that shows the empty plateau and the sky
  rendererApi.camera.position.set(320, 120, 260);
  rendererApi.controls.target.set(0, 50, 0);
  rendererApi.start(frame);
}

boot().catch(error => {
  fail(error.message);
  console.error(error);
});
```

The header's `window.viewer` lists `rendererApi`, beside `claims`, `cycle` and `manifest`, among the keys that exist for the browser checks: the checks read the camera, the tier settings and `measure` through it.

- [ ] **Step 5: Browser check at `?quality=low`: canvas, tier, passes, the plateau and sky**

Fetch the edited files afresh and reload:

```js
await Promise.all(['app.js', 'render/renderer.js', 'render/environment.js'].map(url => fetch(url, { cache: 'reload' })));
location.reload();
```

Run `resize_window` with `width: 1280`, `height: 800` (the `fov` expected below needs a stage at least 5:4 wide), `navigate` to `http://localhost:8765/?quality=low`, take a `screenshot` (named `task4-low-clear.png` in the report), then run with `javascript_tool`:

```js
(() => {
  const stage = document.getElementById('stage');
  const canvas = stage.querySelector('canvas');
  const { renderer, composer, camera, scene } = viewer.rendererApi;
  return {
    canvas: [canvas !== null, canvas.clientWidth === stage.clientWidth, canvas.clientHeight === stage.clientHeight],
    labelsLayer: stage.querySelector('div.labels') !== null,
    quality: viewer.state().quality,
    pixelRatio: renderer.getPixelRatio(),
    shadows: [renderer.shadowMap.enabled, viewer.environment.sun.castShadow],
    passes: composer.passes.map(pass => `${pass.constructor.name}:${pass.enabled}`),
    colour: [renderer.toneMapping, renderer.outputColorSpace, renderer.localClippingEnabled],
    fov: camera.fov,
    environmentMap: scene.environment !== null,
    fog: [scene.fog.isFogExp2, scene.fog.density],
    ground: [viewer.environment.ground.material.opacity, viewer.environment.ground.receiveShadow],
    exposure: renderer.toneMappingExposure,
  };
})()
```

Expected:

- `canvas` is `[true, true, true]` and `labelsLayer` is `true`.
- `quality` is `"low"` and `pixelRatio` is `1`.
- `shadows` is `[false, false]`.
- `passes` is `["RenderPass:true", "UnrealBloomPass:false", "SMAAPass:true", "OutputPass:true"]`.
- `colour` is `[4, "srgb", true]`, where 4 is `THREE.ACESFilmicToneMapping`.
- `fov` is `45`, because a 1280 x 800 stage is wider than 5:4.
- `environmentMap` is `true`.
- `fog` is `[true, 0.00025]`.
- `ground` is `[1, true]`.
- `exposure` is `0.5`.

The screenshot shows the notice on top, then a daylight sky over a sand-coloured plain that fades into haze at the horizon. Nothing stands on the plain.

- [ ] **Step 6: Browser check: the storm darkens the sky within 2 s, and clears again**

Take a `screenshot` (`task4-before-storm.png`), then run:

```js
viewer.store.set({ weather: 'storm' });
[viewer.state().weather, viewer.environment.mix.storm]
```

Expected: `["storm", 0]`. The target is set; the mix moves on the next frames.

`computer` with `action: "wait"`, `duration: 2`, then take a `screenshot` (`task4-storm.png`). It must show a visibly darker, hazier sky with the sun low near the horizon, and the plain darker. Then run:

```js
[viewer.environment.mix.storm, viewer.environment.sky.material.uniforms.turbidity.value,
 viewer.environment.sun.intensity, viewer.rendererApi.renderer.toneMappingExposure, viewer.rendererApi.scene.fog.density]
```

Expected: `[1, 18, 0.4, 0.3, 0.0009]`.

Run `viewer.store.set({ weather: 'clear' })`, wait 2 s, then run `viewer.environment.mix.storm`. Expected: `0`. A `screenshot` matches `task4-before-storm.png` again.

- [ ] **Step 7: Browser check: the ground fades only for an interior step seen from inside, and comes back**

Every expression below ends with the same read-out; call it `ground`:

```js
[viewer.environment.mix.interior, viewer.environment.ground.material.opacity, viewer.environment.ground.visible,
 viewer.environment.ground.material.depthWrite, viewer.rendererApi.scene.fog.density]
```

(a) An interior step with the camera outside, as on S06's exterior shot. Task 4's `frame` passes `cameraInside` false. Run:

```js
viewer.store.set({ interior: true });
viewer.state().interior
```

Expected: `true`. Wait 2 s, take a `screenshot` (`task4-interior-outside.png`): the sand plain is still there. Then run the `ground` read-out. Expected: `[1, 1, true, true, 0.00025]`: the interior mix has arrived, the plateau stays.

(b) The camera counts as inside. There is no model in Task 4, so the check stands in for Task 5's bounds test: it wraps `viewer.environment.update`, which `frame` calls through the same object every frame, so that it always passes `true`:

```js
viewer.environment.realUpdate = viewer.environment.realUpdate || viewer.environment.update;
viewer.environment.update = dt => viewer.environment.realUpdate(dt, true);
true
```

Wait 2 s, take a `screenshot` (`task4-interior-inside.png`): the sand plain is gone and only the sky remains. Then run the `ground` read-out. Expected: `[1, 0, false, false, 0]`.

(c) Put the real update back, so the camera counts as outside again, and wait 2 s:

```js
viewer.environment.update = viewer.environment.realUpdate;
delete viewer.environment.realUpdate;
true
```

Then run the `ground` read-out. Expected: `[1, 1, true, true, 0.00025]`. Run `viewer.store.set({ interior: false })`, wait 2 s, and run it once more. Expected: `[0, 1, true, true, 0.00025]`.

- [ ] **Step 8: Browser check: measure, lastDt and the dt clamp**

Take a `screenshot` (the loop must be running), then run:

```js
await (async () => {
  const median = await viewer.rendererApi.measure(1);
  const lastDt = viewer.state().lastDt;
  // a long frame: block the main thread for 300 ms, then read lastDt in the next animation frame
  const start = performance.now();
  while (performance.now() - start < 300) { /* busy */ }
  await new Promise(resolve => requestAnimationFrame(resolve));
  return { median: [typeof median, Number.isFinite(median) && median > 0], lastDt: lastDt > 0 && lastDt <= 0.1, clamped: viewer.state().lastDt };
})()
```

Expected: `{median: ["number", true], lastDt: true, clamped: 0.1}`. The animation loop registered its frame callback before this check ran, so in the frame after the busy wait it runs first and records the clamped 0.3 s gap.

- [ ] **Step 9: Browser check: reduced motion makes the fades instant**

Take a `screenshot`, then run:

```js
await (async () => {
  const nextFrame = () => new Promise(resolve => requestAnimationFrame(resolve));
  viewer.store.set({ reducedMotion: true, weather: 'storm', interior: true });
  await nextFrame();
  const cut = [viewer.environment.mix.storm, viewer.environment.mix.interior];
  viewer.store.set({ weather: 'clear', interior: false });
  await nextFrame();
  const back = [viewer.environment.mix.storm, viewer.environment.mix.interior];
  viewer.store.set({ reducedMotion: false });
  return { cut, back };
})()
```

Expected: `{cut: [1, 1], back: [0, 0]}`.

- [ ] **Step 10: Browser check: `?quality=high`, a tier change from the store, the 5:4 rule at phone width, the console**

`navigate` to `http://localhost:8765/?quality=high`, take a `screenshot` (`task4-high-clear.png`). It shows the same view as at `low`: nothing stands on the plain yet, so no shadow is cast. Then run:

```js
(() => {
  const { renderer, composer } = viewer.rendererApi;
  const read = () => ({
    quality: viewer.state().quality,
    pixelRatio: renderer.getPixelRatio(),
    shadows: [renderer.shadowMap.enabled, viewer.environment.sun.castShadow, viewer.environment.sun.shadow.mapSize.x],
    bloom: composer.passes[1].enabled,
  });
  const high = read();
  viewer.store.set({ quality: 'medium' });
  const medium = read();
  return { high, medium, dpr: devicePixelRatio };
})()
```

Expected, with `dpr` the reported device pixel ratio:

- `high`: `quality` is `"high"`, `pixelRatio` equals `Math.min(2, dpr)`, `shadows` is `[true, true, 2048]` and `bloom` is `true`.
- `medium`: `quality` is `"medium"`, `pixelRatio` equals `Math.min(1.5, dpr)`, `shadows` is `[true, true, 1024]` and `bloom` is `true`.

The 5:4 rule. Run `resize_window` with `preset: "mobile"` (375 x 812), take a `screenshot`, then run:

```js
(() => {
  const stage = document.getElementById('stage');
  const expected = 2 * Math.atan(Math.tan(Math.PI / 8) * 1.25 * stage.clientHeight / stage.clientWidth) * 180 / Math.PI;
  return [stage.clientWidth, stage.querySelector('canvas').clientWidth, Math.abs(viewer.rendererApi.camera.fov - expected) < 0.01,
          document.documentElement.scrollWidth <= innerWidth];
})()
```

Expected: `[375, 375, true, true]`. At 375 x 812 the angle opens to about 96.5 degrees. Run `resize_window` with `preset: "desktop"` to clear the emulation.

Then `read_console_messages` with `onlyErrors: true`. Expected: no entry from the page.

- [ ] **Step 11: Run the Python suite**

Run: `uv run pytest -q -W error`
Expected: every test passes, with the same count as after Task 2 (this task changes no Python and no data).

- [ ] **Step 12: Commit**

```bash
git add viewer/render/renderer.js viewer/render/environment.js viewer/app.js
git commit -m "Render the plateau: renderer with post-processing and quality tiers, sky, sun, ground and fog with interior and storm fades" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 5: Materials and model

**Files:**
- Create: `viewer/render/materials.js`
- Create: `viewer/render/model.js`
- Modify: `viewer/app.js` (imports, `frame(dt)`, the fixed exterior pose of Task 4, one block above the start block)
- Test: browser checks (no JavaScript test runner; see the header's "Browser checks")

**Interfaces:**
- Consumes: from Task 3, `store` (`get`, `set`, `subscribe`; keys `layers`, `reading`, `interior`), `cycle` (the loaded `cycle.json`), `window.viewer` (with `store`, `claims`, `cycle`, `manifest`, `state`); from Task 4, `rendererApi` (the object `createRenderer` returns: `renderer` with `localClippingEnabled` already true, `camera`, `controls`, `scene`, `start`; exposed as `window.viewer.rendererApi`), `environment` (`mix.interior`, `ground`, `update(dt, cameraInside)`: the ground and the fog fade with `mix.interior` only while `cameraInside` is true; exposed as `window.viewer.environment`), and the last block of `boot()` in `app.js`, `// ---- start (Task 4)`, which holds `frame(dt)` (whose body is `environment.update(dt, false);` with its comment), the fixed exterior pose and `rendererApi.start(frame);`; the generated `viewer/data/interior.glb` and `viewer/data/interior_alt.glb` (21 meshes each: 19 spaces, `masonry`, `bedrock`; positions only, no normals, identity node transforms, viewer coordinates).
- Produces: `createMaterials()` with `stone()`, `glass()`, `bedrock()`, `space()`, `water(plane)`, `gas(plane, colourHex)`, `hatch(material, colourHex)`, `update(dt)` exactly as the header; a water material exposes its free-surface uniform as `material.userData.uLevel` (`{ value }`, viewer Y); a gas material's colour is `material.uniforms.uColour`; the glass material's opacity is `material.uniforms.uOpacity`; every `water()` and `gas()` call returns a new material; `hatch` anchors on `#include <tonemapping_fragment>`, adds the uniform `uHatch` and its own program cache key. `loadModel(url, scene, materials, store)` returning `model` exactly as the header; the helper `frameModel(model, camera, controls)` exported from `model.js`; `window.viewer.model`; the `// ---- materials and model (Task 5)` block of `boot()`, with `materials` and `model` in scope for later blocks.

Notes for the implementer. The glTF files carry positions only. Every `MeshStandardMaterial` here sets `flatShading: true` itself (the materials replace GLTFLoader's own), and the two `ShaderMaterial`s derive their normal from `cross(dFdx(v), dFdy(v))` and use `abs(dot(n, v))`, so gmsh's unchecked winding does not matter. Shader code is the riskiest part of this plan: if the GPU rejects a shader, fix the smallest thing that compiles, keep the look described, and record the deviation in the report.

Notes for the browser checks. `python3 -m http.server` sends no cache headers, and a query on the page URL does not change the URLs of the modules it imports, so the browser may reuse the copies it loaded before an edit: before the first check after an edit, run `await Promise.all([...edited files].map(url => fetch(url, { cache: 'reload' })))` in the open page, then `navigate`. The Browser pane may report `document.visibilityState === "hidden"`, which stops the animation loop and with it the fades: take a `screenshot` before every wait (it brings the pane forward), and if a read after the wait shows no progress, bring the pane to the front and wait again. A check that declares names with `const` runs as one JavaScript tool call; if the tool reports a name as already declared, wrap the check in `await (async () => { ...; return <the last expression>; })()`.

- [ ] **Step 1: Run the model check against the page as Task 4 left it (expected failure)**

Start the server with the Browser pane's `preview_start` (`name: "viewer"`), `resize_window` to 1280 x 800, and `navigate` to `http://localhost:8765/?quality=low&v=t5a`. Take a screenshot (the pane only advances frames on a screenshot). Run through the JavaScript tool:

```js
({ model: typeof viewer.model, canvases: document.querySelectorAll('#stage canvas').length })
```

Expected: `{ model: 'undefined', canvases: 1 }`. The plateau and sky show, no pyramid. This is the failure the next steps fix.

- [ ] **Step 2: Write `viewer/render/materials.js`**

```js
// Materials: procedural limestone, dark glass, bedrock, the schematic interior, water, gas, and hatching.
// The glTF carries positions only, no normals: every lit material is flat shaded, the custom shaders take
// their normal from screen-space derivatives, and abs() keeps them blind to gmsh's unchecked winding.
import * as THREE from 'three';

// Display choices, not physical quantities (so are the roughness, opacity and shader weights in the functions below).
const STONE = 0xcdb894;        // display choice: limestone
const BEDROCK = 0x6f675b;      // display choice: darker stone
const SPACE = 0xece5d3;        // display choice: plan A's space colour
const SPACE_GLOW = 0x2e2b24;   // display choice: a faint self-light, so the schematic reads inside the dark glass
const WATER = 0x2f86d6;        // display choice: plan A's water colour
const GLASS_BODY = 0x0e141a;   // display choice: the glass seen face on
const GLASS_EDGE = 0x8fb8dc;   // display choice: the cool glow where the glass is seen edge on
const SHADE = 0.4;             // display choice: a hatching stripe is the actor's colour at 40 percent
// GLSL float literals (written with a decimal point: GLSL does not convert integers).
const GRAIN = '0.06';          // display choice: the stone's brightness varies by 6 percent either way
const BAND = '0.3';            // display choice: metres of brighter water under the free surface
const PITCH = '8.0';           // display choice: hatching stripes repeat every 8 device pixels along a row
// ponytail: device pixels, so the stripes are finer on a high-density screen; divide by the pixel ratio if they read too fine.

// 3D value noise in 0 to 1: hashed values on the integer lattice, smoothly interpolated between them.
const NOISE = /* glsl */ `
float hash3(vec3 p) { return fract(sin(dot(p, vec3(12.9898, 78.233, 37.719))) * 43758.5453); }
float noise3(vec3 p) {
  vec3 i = floor(p);
  vec3 f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(
    mix(mix(hash3(i), hash3(i + vec3(1.0, 0.0, 0.0)), f.x),
        mix(hash3(i + vec3(0.0, 1.0, 0.0)), hash3(i + vec3(1.0, 1.0, 0.0)), f.x), f.y),
    mix(mix(hash3(i + vec3(0.0, 0.0, 1.0)), hash3(i + vec3(1.0, 0.0, 1.0)), f.x),
        mix(hash3(i + vec3(0.0, 1.0, 1.0)), hash3(i + vec3(1.0, 1.0, 1.0)), f.x), f.y),
    f.z);
}
`;

// How edge-on a surface is seen: 0 face on, 1 at the silhouette. view is the fragment's view-space position.
const FRESNEL = /* glsl */ `
float fresnel(vec3 view) {
  vec3 n = normalize(cross(dFdx(view), dFdy(view)));
  return pow(1.0 - abs(dot(n, normalize(-view))), 3.0);
}
`;

// The vertex shader of the glass and the gas: the position in view space and in the world, and clipping.
const VERTEX = /* glsl */ `
varying vec3 vView;
varying vec3 vWorld;
#include <clipping_planes_pars_vertex>
void main() {
  vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
  vView = mvPosition.xyz;
  vWorld = (modelMatrix * vec4(position, 1.0)).xyz;
  gl_Position = projectionMatrix * mvPosition;
  #include <clipping_planes_vertex>
}
`;

export function createMaterials() {
  const time = { value: 0 };   // one uTime uniform, shared by every material made here

  // Limestone: grain and weathering from triplanar value noise in object space, a few percent of brightness.
  function stone() {
    const material = new THREE.MeshStandardMaterial({
      color: STONE, roughness: 0.92, metalness: 0, flatShading: true, side: THREE.DoubleSide,
      transparent: true, opacity: 1,
    });
    material.onBeforeCompile = shader => {
      shader.vertexShader = shader.vertexShader
        .replace('#include <common>', '#include <common>\nvarying vec3 vObject;')
        .replace('#include <begin_vertex>', '#include <begin_vertex>\nvObject = position;');
      shader.fragmentShader = shader.fragmentShader
        .replace('#include <common>', `#include <common>
varying vec3 vObject;
${NOISE}
// 2D noise on the three planes through the point, weighted by how squarely the face meets each plane.
float triplanar(vec3 p, vec3 n) {
  vec3 w = abs(n) / (abs(n.x) + abs(n.y) + abs(n.z));
  return w.x * noise3(vec3(p.yz, 0.0)) + w.y * noise3(vec3(p.zx, 0.0)) + w.z * noise3(vec3(p.xy, 0.0));
}`)
        .replace('#include <map_fragment>', `#include <map_fragment>
{
  vec3 faceNormal = normalize(cross(dFdx(vObject), dFdy(vObject)));
  // display choice: a coarse octave for weathering, a fine one for grain
  float grain = 0.65 * triplanar(vObject * 0.35, faceNormal) + 0.35 * triplanar(vObject * 2.3, faceNormal);
  diffuseColor.rgb *= 1.0 + ${GRAIN} * (2.0 * grain - 1.0);
}`);
    };
    return material;
  }

  // Dark glass with a Fresnel edge glow: the masonry seen from inside. The model sets uOpacity.
  function glass() {
    return new THREE.ShaderMaterial({
      uniforms: {
        uBody: { value: new THREE.Color(GLASS_BODY) },
        uEdge: { value: new THREE.Color(GLASS_EDGE) },
        uOpacity: { value: 0 },
      },
      vertexShader: VERTEX,
      fragmentShader: /* glsl */ `
uniform vec3 uBody;
uniform vec3 uEdge;
uniform float uOpacity;
varying vec3 vView;
#include <clipping_planes_pars_fragment>
${FRESNEL}
void main() {
  #include <clipping_planes_fragment>
  float edge = fresnel(vView);
  gl_FragColor = vec4(mix(uBody, uEdge, edge), uOpacity * (0.3 + 0.7 * edge));
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`,
      transparent: true, depthWrite: false, side: THREE.DoubleSide, clipping: true,
    });
  }

  function bedrock() {
    return new THREE.MeshStandardMaterial({
      color: BEDROCK, roughness: 1, metalness: 0, flatShading: true, side: THREE.DoubleSide,
      transparent: true, opacity: 1,
    });
  }

  // The schematic interior: pale surfaces with a faint self-light.
  function space() {
    return new THREE.MeshStandardMaterial({
      color: SPACE, emissive: SPACE_GLOW, roughness: 0.9, metalness: 0, flatShading: true, side: THREE.DoubleSide,
    });
  }

  // Water: a skin clipped by the plane at the free surface, a slow ripple on its normal, and a brighter band
  // just under the surface. The actor sets material.userData.uLevel.value to the surface's viewer Y.
  function water(plane) {
    const material = new THREE.MeshStandardMaterial({
      color: WATER, roughness: 0.25, metalness: 0, flatShading: true, side: THREE.DoubleSide,
      transparent: true, opacity: 0.8, depthWrite: false, clippingPlanes: [plane],
    });
    const level = { value: -1e6 };   // display choice: far below everything until the actor sets it
    material.userData.uLevel = level;
    material.onBeforeCompile = shader => {
      shader.uniforms.uTime = time;
      shader.uniforms.uLevel = level;
      shader.vertexShader = shader.vertexShader
        .replace('#include <common>', '#include <common>\nvarying vec3 vWorld;')
        .replace('#include <begin_vertex>', '#include <begin_vertex>\nvWorld = (modelMatrix * vec4(position, 1.0)).xyz;');
      shader.fragmentShader = shader.fragmentShader
        .replace('#include <common>', '#include <common>\nuniform float uTime;\nuniform float uLevel;\nvarying vec3 vWorld;')
        .replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
// display choice: ripple amplitude, wavelength and speed
normal = normalize(normal + 0.06 * vec3(sin(vWorld.x * 1.7 + uTime * 1.3), 0.0, cos(vWorld.z * 1.9 + uTime * 1.1)));`)
        .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
float belowSurface = uLevel - vWorld.y;
totalEmissiveRadiance += diffuseColor.rgb * 0.6 * step(0.0, belowSurface) * step(belowSurface, ${BAND});`);
    };
    return material;
  }

  // Gas: a view-dependent haze, denser where the space is seen edge on, broken by drifting noise; additive.
  function gas(plane, colourHex) {
    return new THREE.ShaderMaterial({
      uniforms: { uColour: { value: new THREE.Color(colourHex) }, uTime: time },
      vertexShader: VERTEX,
      fragmentShader: /* glsl */ `
uniform vec3 uColour;
uniform float uTime;
varying vec3 vView;
varying vec3 vWorld;
#include <clipping_planes_pars_fragment>
${NOISE}
${FRESNEL}
void main() {
  #include <clipping_planes_fragment>
  // display choice: noise scale, drift speed and density
  float drift = noise3(vWorld * 0.6 + vec3(0.0, -0.25, 0.1) * uTime);
  float density = (0.25 + 0.75 * fresnel(vView)) * (0.4 + 0.6 * drift);
  gl_FragColor = vec4(uColour * density, density * 0.7);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`,
      transparent: true, depthWrite: false, side: THREE.DoubleSide, blending: THREE.AdditiveBlending,
      clipping: true, clippingPlanes: [plane],
    });
  }

  // Screen-space diagonal stripes over a material: every other band of PITCH pixels takes a darker shade
  // of the colour. Works on the standard materials and on the shader materials above, which all have
  // the tonemapping chunk; the stripes go in just before it, in linear colour.
  function hatch(material, colourHex) {
    const shade = new THREE.Color(colourHex).multiplyScalar(SHADE);
    const previous = material.onBeforeCompile;
    const key = material.customProgramCacheKey();
    material.onBeforeCompile = (shader, renderer) => {
      previous.call(material, shader, renderer);
      shader.uniforms.uHatch = { value: shade };
      shader.fragmentShader = shader.fragmentShader
        .replace('void main() {', 'uniform vec3 uHatch;\nvoid main() {')
        .replace('#include <tonemapping_fragment>', `if (fract((gl_FragCoord.x + gl_FragCoord.y) / ${PITCH}) < 0.5) gl_FragColor.rgb = uHatch;
#include <tonemapping_fragment>`);
    };
    // the wrapper's source is the same for every material it wraps; keep their programs apart
    material.customProgramCacheKey = () => `${key}|hatch`;
    material.needsUpdate = true;
    return material;
  }

  return { stone, glass, bedrock, space, water, gas, hatch, update: dt => { time.value += dt; } };
}
```

- [ ] **Step 3: Write `viewer/render/model.js`**

```js
// The model: the glTF of the interior, its registry of spaces, the masonry drawn as stone and as glass,
// picking, hidden spaces, the cutaway planes, the interior look, and the swap between the two readings.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const GLASS_OPACITY = 0.55;   // display choice: the masonry's glass at the full interior look
const BEDROCK_GHOST = 0.08;   // display choice: the bedrock's opacity at the full interior look
const VIEW_FROM = new THREE.Vector3(1, 0.4, 0.5).normalize();   // display choice: plan A's view from the south-east

// The alternative reading of the survey is the file beside the survey's: interior.glb, interior_alt.glb.
const fileOf = (url, reading) => (reading === 'alternative' ? url.replace(/\.glb$/, '_alt.glb') : url);

export async function loadModel(url, scene, materials, store) {
  const loader = new GLTFLoader();
  const raycaster = new THREE.Raycaster();
  // The three shell materials outlive a reading swap; each load hands them to the new meshes.
  const look = { stone: materials.stone(), glass: materials.glass(), bedrock: materials.bedrock() };
  const layers = store.get().layers;
  let hidden = layers.hidden;                                          // space names switched off
  let shellLayers = { masonry: layers.masonry, bedrock: layers.bedrock };   // opacities 0 to 1
  let k = 0;            // the interior mix last applied
  let planes = null;    // the cutaway planes, or null
  let loads = 0;        // when two loads overlap, the later one wins

  const model = {
    root: null, spaces: new Map(), shell: { stone: null, glass: null, bedrock: null },
    bounds: new THREE.Box3(), masonryBounds: new THREE.Box3(), apexY: 0,
    pickAt, setHidden, setShell, setInterior, setClipping, dispose,
  };

  async function load(file) {
    const ticket = ++loads;
    const gltf = await loader.loadAsync(file);
    if (ticket !== loads) return;   // a later swap has started; it wins
    drop();
    const found = {};
    gltf.scene.traverse(object => {
      if (!object.isMesh) return;
      if (object.name === 'masonry' || object.name === 'bedrock') {
        found[object.name] = object;
      } else {
        object.material = materials.space();
        model.spaces.set(object.name, object);
      }
    });
    const glass = found.masonry.clone();   // the masonry drawn a second time; clone() shares the geometry
    glass.material = look.glass;
    found.masonry.material = look.stone;
    found.masonry.castShadow = true;
    found.masonry.receiveShadow = true;
    found.bedrock.material = look.bedrock;
    gltf.scene.add(glass);
    model.shell = { stone: found.masonry, glass, bedrock: found.bedrock };
    for (const mesh of Object.values(model.shell)) mesh.renderOrder = 2;   // after the water and gas inside it
    model.root = gltf.scene;
    scene.add(model.root);
    model.root.updateMatrixWorld(true);
    model.masonryBounds.setFromObject(model.shell.stone);
    model.bounds.setFromObject(model.shell.bedrock).union(model.masonryBounds);
    model.apexY = model.masonryBounds.max.y;
    setHidden(hidden);
    setClipping(planes);
    setInterior(k);
  }

  // Take the shown model out. Its geometries go back to the GPU; the shell materials stay for the next one.
  // The actors' skins share the space geometries; they were on the old meshes and are rebuilt on the new.
  function drop() {
    if (!model.root) return;
    scene.remove(model.root);
    for (const mesh of model.spaces.values()) {
      mesh.geometry.dispose();
      mesh.material.dispose();
    }
    model.shell.stone.geometry.dispose();   // the glass shares it
    model.shell.bedrock.geometry.dispose();
    model.spaces.clear();
  }

  // The name of the nearest visible space under a point of the view (normalised device coordinates), or null.
  // The shell is not in the list, so the pick sees through the masonry; skins are children and never hit.
  function pickAt(ndc, camera) {
    raycaster.setFromCamera(ndc, camera);
    const visible = [...model.spaces.values()].filter(mesh => mesh.visible);
    const hit = raycaster.intersectObjects(visible, false)[0];
    return hit ? hit.object.name : null;
  }

  // Remembered, so a reading swap keeps the same spaces hidden.
  function setHidden(names) {
    hidden = names;
    for (const [name, mesh] of model.spaces) mesh.visible = !names.has(name);
  }

  function setShell({ masonry, bedrock }) {
    shellLayers = { masonry, bedrock };
    setInterior(k);
  }

  // k = 0: the stone of the exterior; k = 1: dark glass with the spaces showing through.
  function setInterior(value) {
    k = value;
    const { stone, glass, bedrock } = model.shell;
    look.stone.opacity = (1 - k) * shellLayers.masonry;
    look.glass.uniforms.uOpacity.value = k * GLASS_OPACITY * shellLayers.masonry;
    look.bedrock.opacity = (1 - k) * shellLayers.bedrock + k * BEDROCK_GHOST;
    // An opaque shell writes depth, so its near faces hide its far ones; a fading one draws both of its
    // sides (three.js draws a transparent double-sided mesh back faces first) and hides nothing.
    look.stone.depthWrite = look.stone.opacity >= 1;
    look.bedrock.depthWrite = look.bedrock.opacity >= 1;
    stone.visible = look.stone.opacity > 0;
    glass.visible = look.glass.uniforms.uOpacity.value > 0;
    bedrock.visible = look.bedrock.opacity > 0;
  }

  // Cutaway: the planes clip the masonry and the bedrock only; spaces and actors are never clipped.
  function setClipping(value) {
    planes = value;
    for (const material of Object.values(look)) material.clippingPlanes = planes;
  }

  function dispose() {
    unsubscribe();
    drop();
    model.root = null;
    for (const material of Object.values(look)) material.dispose();
  }

  await load(fileOf(url, store.get().reading));
  const unsubscribe = store.subscribe((next, prev, changed) => {
    if (changed.has('layers')) {
      setHidden(next.layers.hidden);
      setShell(next.layers);
    }
    if (changed.has('reading')) {
      const file = fileOf(url, next.reading);
      load(file).catch(error => console.error(`${file}: ${error.message}`));
    }
  });
  return model;
}

// Point the camera at the whole pyramid from the south-east: back off until the masonry's bounding sphere
// fits the narrower of the vertical and horizontal angles of view (plan A's frame()).
export function frameModel(model, camera, controls) {
  const sphere = model.masonryBounds.getBoundingSphere(new THREE.Sphere());
  const vertical = THREE.MathUtils.degToRad(camera.fov / 2);
  const half = Math.min(vertical, Math.atan(Math.tan(vertical) * camera.aspect));
  const reach = sphere.radius / Math.sin(half);
  controls.target.copy(sphere.center);
  camera.position.copy(VIEW_FROM).multiplyScalar(reach).add(sphere.center);
  camera.near = reach / 1000;   // display choice: plan A's frame rule
  camera.far = Math.max(camera.far, reach * 10);   // never below the renderer's: the sky and the 20 km ground reach further
  camera.updateProjectionMatrix();
}
```

- [ ] **Step 4: Extend `viewer/app.js`**

Three exactly located edits to the file as Task 4 left it (everything after the data loading lives in `async function boot()`, in blocks marked `// ---- <name> (Task N)`; the last block, `// ---- start (Task 4)`, holds `frame(dt)` with the single line `environment.update(dt, false);`, the fixed exterior pose and `rendererApi.start(frame);`, and each later task inserts its block above it). `renderer.js` already sets `renderer.localClippingEnabled = true`, which the water and gas skins need.

Edit 4a, imports. Directly below the line

```js
import { createEnvironment } from './render/environment.js';
```

add

```js
import { createMaterials } from './render/materials.js';
import { frameModel, loadModel } from './render/model.js';
```

Edit 4b, the block. Directly above the line `  // ---- start (Task 4): stays the last block, so everything frame() reads exists before the first frame`, insert:

```js
  // ---- materials and model (Task 5)
  const materials = createMaterials();
  const model = await loadModel('data/interior.glb', rendererApi.scene, materials, store);
  frameModel(model, rendererApi.camera, rendererApi.controls);
  Object.assign(window.viewer, { model });

```

Edit 4c, the start block. Below its comment line (unchanged), replace

```js
  function frame(dt) {
    environment.update(dt, false);   // no model yet, so the camera is never inside it
  }
  // display choice: an exterior pose that shows the empty plateau and the sky
  rendererApi.camera.position.set(320, 120, 260);
  rendererApi.controls.target.set(0, 50, 0);
  rendererApi.start(frame);
```

with

```js
  function frame(dt) {
    environment.update(dt, model.bounds.containsPoint(rendererApi.camera.position));
    materials.update(dt);
    model.setInterior(environment.mix.interior);
  }
  rendererApi.start(frame);
```

The first line of `frame` is the header's rule: the ground and the fog fade with the interior look only while the camera stands inside `model.bounds` (masonry and bedrock together), so an interior step filmed from outside keeps its plateau. The fixed exterior pose goes: `frameModel` in 4b replaces it with plan A's bounding-sphere fit from the south-east, which also sets `near` to a thousandth of the distance and never lowers `far` below the renderer's (the sky and the 20 km ground need it). Task 7 expects the start block to hold only `function frame(dt)` and `rendererApi.start(frame);` after this task. The end of `boot()` now reads:

```js
  // ---- renderer and environment (Task 4)
  const rendererApi = createRenderer(document.getElementById('stage'), store);
  const environment = createEnvironment(rendererApi.scene, rendererApi, store);
  stateParts.push(() => ({ lastDt: rendererApi.lastDt }));
  Object.assign(window.viewer, { rendererApi, environment });

  // ---- materials and model (Task 5)
  const materials = createMaterials();
  const model = await loadModel('data/interior.glb', rendererApi.scene, materials, store);
  frameModel(model, rendererApi.camera, rendererApi.controls);
  Object.assign(window.viewer, { model });

  // ---- start (Task 4): stays the last block, so everything frame() reads exists before the first frame
  function frame(dt) {
    environment.update(dt, model.bounds.containsPoint(rendererApi.camera.position));
    materials.update(dt);
    model.setInterior(environment.mix.interior);
  }
  rendererApi.start(frame);
}
```

- [ ] **Step 5: Browser check: the pyramid on the plateau**

In the page Step 1 opened, fetch the edited files afresh:

```js
await Promise.all(['app.js', 'render/materials.js', 'render/model.js'].map(url => fetch(url, { cache: 'reload' })));
```

Then `navigate` to `http://localhost:8765/?quality=low&v=t5b`. Take a screenshot, name it `t5-exterior`: the pyramid stands on the sand plane under the sky, seen from the south-east, its faces a warm limestone with a faint mottled grain (no block courses, no stripes); the low tier draws no shadows. Then run (the first line waits for the model, which loads after the page):

```js
for (let i = 0; i < 100 && !window.viewer?.model; i++) await new Promise(r => setTimeout(r, 100));
const m = viewer.model;
({
  spaces: m.spaces.size,
  gallery: m.spaces.has('grand_gallery'),
  apexY: +m.apexY.toFixed(2),
  bounds: [m.bounds.min.y, +m.bounds.max.y.toFixed(2), +m.bounds.max.x.toFixed(2)],
  stoneOpacity: m.shell.stone.material.opacity,
  stoneVisible: m.shell.stone.visible,
  glassVisible: m.shell.glass.visible,
  sharedGeometry: m.shell.glass.geometry === m.shell.stone.geometry,
})
```

Expected (19 = the 21 meshes of `interior.glb` less `masonry` and `bedrock`; 137.38, -60 and 115.17 are the glTF's own bounds):

```js
{ spaces: 19, gallery: true, apexY: 137.38, bounds: [-60, 137.38, 115.17],
  stoneOpacity: 1, stoneVisible: true, glassVisible: false, sharedGeometry: true }
```

`read_console_messages` with `onlyErrors: true`: no error from the page. A shader compile error shows here as `THREE.WebGLProgram: Shader Error`; fix it before going on.

- [ ] **Step 6: Browser check: the interior cross-fade**

Run `viewer.store.set({ interior: true })`, take a screenshot (it starts the frames), wait 2 seconds (`computer` action `wait`, duration 2), then run:

```js
const m = viewer.model;
({
  mix: viewer.environment.mix.interior,
  stoneVisible: m.shell.stone.visible,
  glassVisible: m.shell.glass.visible,
  glassOpacity: +m.shell.glass.material.uniforms.uOpacity.value.toFixed(2),
  bedrockOpacity: +m.shell.bedrock.material.opacity.toFixed(2),
  ground: viewer.environment.ground.material.opacity,
  cameraInside: m.bounds.containsPoint(viewer.rendererApi.camera.position),
})
```

Expected: `{ mix: 1, stoneVisible: false, glassVisible: true, glassOpacity: 0.55, bedrockOpacity: 0.08, ground: 1, cameraInside: false }` (1.5 s of fade at 1/FADE_SECONDS per second has passed; the framing pose is outside the model, so the plateau stays). Screenshot `t5-interior`: the masonry is dark glass whose edges and grazing faces glow a cool blue, the pale passages and chambers above the plateau show through, the Grand Gallery a bright sloping band, and the sand plain is still there (the spaces under it stay hidden).

Now move the camera inside the model's bounds, keeping the framing pose to come back to:

```js
const { camera, controls } = viewer.rendererApi;
window.t5pose = [camera.position.clone(), controls.target.clone()];
camera.position.set(40, 30, -20);   // inside model.bounds, east of the Grand Gallery
controls.target.set(7, 36, -20);
viewer.model.bounds.containsPoint(camera.position)
```

Expected: `true`. Screenshot, wait 2 seconds, then run `[viewer.environment.ground.material.opacity, viewer.environment.ground.visible, viewer.rendererApi.scene.fog.density]`: expected `[0, false, 0]` (the ground and the fog fade only while the camera is inside). Screenshot `t5-inside`: the glass and the spaces, no plain. Then restore and leave the interior look:

```js
viewer.rendererApi.camera.position.copy(window.t5pose[0]);
viewer.rendererApi.controls.target.copy(window.t5pose[1]);
viewer.store.set({ interior: false });
```

Screenshot, wait 2 seconds, screenshot: the stone and the plain are back; `viewer.environment.ground.material.opacity` reads `1`.

- [ ] **Step 7: Browser check: the reading swap keeps hidden spaces hidden**

```js
viewer.store.set({ layers: { hidden: new Set(['grand_gallery']) } });
viewer.store.set({ reading: 'alternative' });
for (let i = 0; i < 100 && viewer.model.apexY < 140; i++) await new Promise(r => setTimeout(r, 100));
const m = viewer.model;
({
  apexY: +m.apexY.toFixed(2),
  spaces: m.spaces.size,
  galleryVisible: m.spaces.get('grand_gallery').visible,
  kingsVisible: m.spaces.get('kings_chamber').visible,
  inScene: m.root.parent !== null,
})
```

Expected: `{ apexY: 146.71, spaces: 19, galleryVisible: false, kingsVisible: true, inScene: true }` (146.71 is the masonry top of `interior_alt.glb`, the reading without the truncated apex). Take a screenshot `t5-alternative`: the taller, pointed pyramid. Then restore and check:

```js
viewer.store.set({ reading: 'survey', layers: { hidden: new Set() } });
for (let i = 0; i < 100 && viewer.model.apexY > 140; i++) await new Promise(r => setTimeout(r, 100));
({ apexY: +viewer.model.apexY.toFixed(2), galleryVisible: viewer.model.spaces.get('grand_gallery').visible })
```

Expected: `{ apexY: 137.38, galleryVisible: true }`.

- [ ] **Step 8: Browser check: picking at the screen centre, and the cutaway clips the shell only**

Point the camera at the Grand Gallery's bounding-box centre from 40 m east and pick at the centre of the view (normalised device coordinates 0, 0; `pickAt` reads only `x` and `y`, so a plain object serves):

```js
const { camera, controls } = viewer.rendererApi;
const gg = viewer.model.spaces.get('grand_gallery');
gg.geometry.computeBoundingBox();
const centre = gg.geometry.boundingBox.getCenter(gg.position.clone());
camera.position.set(centre.x + 40, centre.y, centre.z);
controls.target.copy(centre);
camera.lookAt(centre);
camera.updateMatrixWorld();
({ picked: viewer.model.pickAt({ x: 0, y: 0 }, camera), sky: viewer.model.pickAt({ x: 0, y: 0.95 }, camera) })
```

Expected: `{ picked: 'grand_gallery', sky: null }` (the ray from the east meets no space before the Gallery's east wall; near the top edge of the view it meets none at all, at the 1280 x 800 viewport of Step 1: a stage narrower than 5:4 opens the vertical angle, and that ray then meets the big void above the Gallery). Then `viewer.model.setHidden(new Set(['grand_gallery']))` and run the same `pickAt({ x: 0, y: 0 }, camera)`: expected `null` (the hidden Gallery is skipped, and no other space of `interior.glb` lies on that ray); restore with `viewer.model.setHidden(new Set())`.

The cutaway clips the shell only (spec 4.4). From a far exterior pose, clip away everything east of the pyramid's north-south axis (three is imported from the import map's own URL, so the plane comes from the page's three):

```js
const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js');
const { camera, controls } = viewer.rendererApi;
const m = viewer.model;
camera.position.set(300, 80, 0);
controls.target.set(0, 40, 0);
m.setClipping([new THREE.Plane(new THREE.Vector3(-1, 0, 0), 0)]);   // keeps x <= 0, the west half
const planes = material => material.clippingPlanes?.length ?? 0;
({
  shell: [m.shell.stone, m.shell.glass, m.shell.bedrock].map(mesh => planes(mesh.material)),
  clippedSpaces: [...m.spaces.values()].filter(mesh => planes(mesh.material) > 0).length,
})
```

Expected: `{ shell: [1, 1, 1], clippedSpaces: 0 }`. Take a screenshot `t5-cutaway`: the east half of the stone and of the bedrock is gone, and the pale spaces stand whole in the opening, the Grand Gallery among them. Then run `viewer.model.setClipping(null); [viewer.model.shell.stone, viewer.model.shell.glass, viewer.model.shell.bedrock].map(mesh => mesh.material.clippingPlanes?.length ?? 0)`: expected `[0, 0, 0]`, and a screenshot shows the whole stone again.

`read_console_messages` with `onlyErrors: true`: no error from the page through Steps 5 to 8.

- [ ] **Step 9: Commit**

```bash
git add viewer/render/materials.js viewer/render/model.js viewer/app.js
git commit -m "$(cat <<'EOF'
Add the procedural materials and the model: stone and glass masonry, picking, hidden spaces, the reading swap

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Actors

**Files:**
- Create: `viewer/render/actors.js`
- Modify: `viewer/app.js` (two imports, one block above the start block)
- Test: browser checks

**Interfaces:**
- Consumes: from Task 4, `TIERS` (exported by `viewer/render/renderer.js`) and `rendererApi.scene`; from Task 5, `materials.water(plane)` (with `material.userData.uLevel`), `materials.gas(plane, colourHex)`, `model.spaces`, `model.apexY`, `model.masonryBounds`, `model.root`, the `materials` and `model` constants of `boot()`; from Task 3, `store` (`quality`, `reducedMotion`), `cycle`, the `stateParts` array of `boot()`, `window.viewer.cycle`; from Task 4, `window.viewer.rendererApi` (`camera`, `controls`) for the checks; from Task 2, `cycle.json` (`steps[i].actors`, `curves`; water and gas actors carry `species` and no `color`; S23 carries `coat` actors).
- Produces: `createActors({ scene, model, materials, store, cycle, tiers })` returning `{ build(step | null), update({ u, dt, source }), dispose(), state() }` exactly as the header, with `state()` = `{ water: {space: fraction}, levels: {space: y}, labels: [text, ...] }`; the helper `levelAt(curve, f)` exported; `window.viewer.actors`; `viewer.state()` now also carries `water`, `levels` and `labels` (Task 6 pushes `actors.state` into `stateParts`). Task 7's player calls `build` on each step change and `update` every tick. Task 9 builds on these internals, which keep their names: `keep(parent, object, ...owned)` (a per-step object; `owned` things are disposed when the step ends), `skin(space, material, offset)` (a `Mesh` child of `model.spaces.get(space)`, `renderOrder` 1), `tag(text, className)` (a `CSS2DObject`), `cloud(space, haze, plane, count)` (Task 9 adds a last parameter, the colour), `shown(object)`, the closure variables `current` (the step built) and `builtOn` (the model root it was built on), the `factories` table, and two marked extension points: the empty `coat()` factory and the comment at the end of `build(step)`.

Behaviour carried over from plan A's `viewer/timeline.js`: water first, so the gas in a space is clipped to what lies above the water in it; a gas path lights up one space after another; the placeholder is the 4 m dashed cube drawn over everything; the bolt's vertices are the same `BOLT` fractions of the masonry height and its two strokes the same windows of the step. What changes: the water's fraction comes from `source.fraction(space)` (the player owns `from` and `to`); the field actor always draws "Solver result pending" (Task 2 dropped `manifest.fields`; a solver slice is a result and belongs to a field case of plan V2); the bolt is a `Line2` with a flash light; gas spaces get a particle cloud on tiers with particles; per-step materials and geometries are disposed at the end of the step; a reading swap rebuilds the step on the new meshes.

Two three.js 0.170.0 facts the code relies on. `Line2` sets its `LineMaterial`'s `resolution` uniform from the renderer's viewport before every draw (`LineSegments2.onBeforeRender`), so the bolt needs no resize hook; with `worldUnits: true` its width is in metres anyway. `PointsMaterial` and `MeshStandardMaterial` carry the clipping chunks themselves, so the particle clouds and the water skins clip by their `clippingPlanes` alone; the gas `ShaderMaterial` of Task 5 has `clipping: true` and the clipping chunks for the same reason. Task 4's renderer sets `localClippingEnabled`. These per-material planes are the actors' own; `model.setClipping` (the cutaway) never touches them.

Notes for the browser checks (as in Task 5). `python3 -m http.server` sends no cache headers and a page query does not change module URLs: before the first check after an edit, run `await Promise.all([...edited files].map(url => fetch(url, { cache: 'reload' })))` in the open page, then `navigate`. If `document.visibilityState` is `"hidden"` the loop stops: take a `screenshot` before every wait, and wait again with the pane in front if a read shows no progress. A check that declares names with `const` runs as one JavaScript tool call; if the tool reports a name as already declared, wrap it in `await (async () => { ...; return <the last expression>; })()`. The steps set `store.interior` by hand: Task 7's player is what sets it from each step's `scene.interior`.

- [ ] **Step 1: Run the actor check against the page as Task 5 left it (expected failure)**

`navigate` to `http://localhost:8765/?quality=low&v=t6a`, take a screenshot, and run:

```js
({ actors: typeof viewer.actors, steps: viewer.cycle.steps.length, s12: viewer.cycle.steps[11].id })
```

Expected: `{ actors: 'undefined', steps: 31, s12: 'S12' }`.

- [ ] **Step 2: Write `viewer/render/actors.js`**

```js
// Actors of a step: water, gas, lightning, placeholders and the pending-field label, ported from plan A's
// timeline.js. build(step) makes the step's objects; update() sets them to the moment u of the step.
import * as THREE from 'three';
import { CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';

// Display choices, not physical quantities (so are the opacities, dash lengths and label offsets below).
const FAR = 1e6;   // display choice: a height far above (or, negated, far below) anything in the model
const HAZE_COLOUR = '#d9dde2';          // display choice: one neutral haze for every gas (Task 9 colours it by species)
const PLACEHOLDER_COLOUR = 0xd9dde2;    // display choice
// display choice: a placeholder is a 4 m dashed cube, a symbol whose size says nothing about what it stands for
const DASHED_BOX = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(4, 4, 4)))
  .computeLineDistances().geometry;
// display choice: the bolt, [east, up, south] of each vertex as fractions of the masonry height, from the apex
const BOLT = [[0.1, 0.6, -0.06], [0.04, 0.47, 0.02], [0.09, 0.36, -0.03], [0.02, 0.24, 0.05],
  [0.06, 0.14, 0], [-0.01, 0.06, 0.02], [0, 0, 0]];
const STROKES = [[0.3, 0.42], [0.48, 0.56]];   // display choice: two brief strokes, as fractions of the step
const BOLT_HEX = 0xfff3b0;   // display choice
const BOLT_GLOW = 4;         // display choice: the bolt is drawn brighter than white, so the bloom catches it
const BOLT_WIDTH = 1.2;      // display choice: metres, so the bolt thins with distance
const FLASH = 6;             // display choice: the flash's intensity; with no fall-off it lights the pyramid alike
const PARTICLES = 4000;      // display choice: the most gas particles in one step, all its spaces together
const PARTICLE_SIZE = 0.15;  // display choice: metres
const SWAY = 0.25;           // display choice: radians per second of each particle's slow sway
const CHORD = 0.15;          // display choice: a particle sways over this fraction of a chord of its space

// The height (viewer Y) at which a space holds the fraction f of its volume.
// curve: [[y, volume below y], ...] with y ascending, as written by level_volume_curve.
export function levelAt(curve, f) {
  const target = f * curve[curve.length - 1][1];
  for (let i = 1; i < curve.length; i++) {
    const [y0, v0] = curve[i - 1];
    const [y1, v1] = curve[i];
    if (v1 >= target) return v1 === v0 ? y0 : y0 + (y1 - y0) * (target - v0) / (v1 - v0);
  }
  return curve[curve.length - 1][0];
}

// Whether an object and all its parents are visible: a label in a hidden space is not on screen.
function shown(object) {
  for (let node = object; node; node = node.parent) if (!node.visible) return false;
  return true;
}

// A point inside the convex hull of a mesh's vertices: a convex combination of four of them, with
// exponential weights, which spread the points evenly over the tetrahedron of the four.
// ponytail: the hull, not the mesh. The Grand Gallery's corbels make its hull a few decimetres wider than the
// space near the roof; test candidates with a parity raycast against the mesh if particles show outside it.
function inside(vertices, out) {
  out.set(0, 0, 0);
  let sum = 0;
  for (let n = 0; n < 4; n++) {
    const i = Math.floor(Math.random() * vertices.count);
    const w = -Math.log(1 - Math.random());
    out.x += w * vertices.getX(i);
    out.y += w * vertices.getY(i);
    out.z += w * vertices.getZ(i);
    sum += w;
  }
  return out.divideScalar(sum);
}

export function createActors({ scene, model, materials, store, cycle, tiers }) {
  let live = [];       // objects that exist only for the current step
  let trash = [];      // what they own and give back to the GPU when the step ends
  let updaters = [];   // functions that set the actors to the current u
  let clouds = [];     // gas particles that sway
  let current = null;  // the step built, or null
  let builtOn = null;  // the model root it was built on; a reading swap replaces the root
  let perSpace = 0;    // particles in each gas space of the current step
  let clock = 0;       // seconds of sway
  const water = new Map();   // space -> { fraction, level } at the current u
  // One flash light for the whole session: adding and removing a light would recompile every material.
  const flash = new THREE.PointLight(BOLT_HEX, 0, 0, 0);   // distance 0, decay 0: no fall-off
  scene.add(flash);

  function keep(parent, object, ...owned) {   // add an object that lives only for the current step
    parent.add(object);
    live.push(object);
    trash.push(...owned);
    return object;
  }

  // A second skin on a space's mesh. As a child of that mesh it shares its position and its visibility
  // (a hidden space hides its water and gas with it), and model.pickAt never sees it.
  function skin(space, material, offset) {
    const source = model.spaces.get(space);
    Object.assign(material, { polygonOffset: true, polygonOffsetFactor: offset, polygonOffsetUnits: offset });
    const mesh = new THREE.Mesh(source.geometry, material);
    mesh.renderOrder = 1;   // after the opaque spaces, before the masonry
    return keep(source, mesh, material);
  }

  function tag(text, className) {
    const element = document.createElement('div');
    element.className = className;
    element.textContent = text;
    return new CSS2DObject(element);
  }

  // A sparse cloud of gas particles in a space, a child of its haze (same visibility, same clipping plane).
  // Each particle sways along a short chord between two points of the space's hull, so it stays inside.
  function cloud(space, haze, plane, count) {
    const vertices = model.spaces.get(space).geometry.attributes.position;
    const from = new Float32Array(count * 3);
    const to = new Float32Array(count * 3);
    const phase = new Float32Array(count);
    const a = new THREE.Vector3();
    const b = new THREE.Vector3();
    for (let i = 0; i < count; i++) {
      inside(vertices, a);
      inside(vertices, b).lerp(a, 1 - CHORD);   // b is moved most of the way back to a
      a.toArray(from, 3 * i);
      b.toArray(to, 3 * i);
      phase[i] = Math.random() * 2 * Math.PI;
    }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(from.slice(), 3));
    const material = new THREE.PointsMaterial({
      color: HAZE_COLOUR, size: PARTICLE_SIZE, transparent: true, opacity: 0.6, depthWrite: false,
      blending: THREE.AdditiveBlending, clippingPlanes: [plane],
    });
    const points = keep(haze, new THREE.Points(geometry, material), geometry, material);
    points.frustumCulled = false;   // the particles move; the bounding sphere of their first positions is stale
    clouds.push({ points, from, to, phase });
  }

  function sway(dt) {
    clock += dt;
    for (const { points, from, to, phase } of clouds) {
      const position = points.geometry.attributes.position;
      for (let i = 0; i < phase.length; i++) {
        const k = 0.5 + 0.5 * Math.sin(clock * SWAY + phase[i]);
        for (let c = 3 * i; c < 3 * i + 3; c++) position.array[c] = from[c] + (to[c] - from[c]) * k;
      }
      position.needsUpdate = true;
    }
  }

  const factories = {
    water(actor) {
      const plane = new THREE.Plane(new THREE.Vector3(0, -1, 0), 0);   // keeps what lies below y = plane.constant
      const material = materials.water(plane);
      const mesh = skin(actor.space, material, -4);
      const curve = cycle.curves[actor.space];
      updaters.push((u, source) => {
        const fraction = source.fraction(actor.space);
        const level = fraction <= 0 ? -FAR : fraction >= 1 ? FAR : levelAt(curve, fraction);
        plane.constant = level;
        material.userData.uLevel.value = level;
        mesh.visible = fraction > 0;
        water.set(actor.space, { fraction, level });
      });
    },

    gas(actor) {
      actor.path.forEach((space, k) => {
        const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), FAR);   // keeps what lies above y = -plane.constant
        const haze = skin(space, materials.gas(plane, HAZE_COLOUR), -2);
        if (perSpace) cloud(space, haze, plane, perSpace);
        updaters.push(u => {
          haze.visible = u >= k / actor.path.length;               // the path lights up one space after another
          plane.constant = -(water.get(space)?.level ?? -FAR);     // only above any water in the same space
        });
      });
    },

    lightning() {
      const top = model.apexY;   // the apex, from the model itself
      const geometry = new LineGeometry()
        .setPositions(BOLT.flatMap(([east, up, south]) => [east * top, top * (1 + up), south * top]));
      const material = new LineMaterial({
        color: new THREE.Color(BOLT_HEX).multiplyScalar(BOLT_GLOW), linewidth: BOLT_WIDTH, worldUnits: true,
      });
      const bolt = keep(scene, new Line2(geometry, material), geometry, material);
      flash.position.set(0, top * 1.3, 0);   // display choice: just above the apex, among the bolt's upper vertices
      updaters.push(u => {
        const on = STROKES.some(([start, end]) => u > start && u < end);
        bolt.visible = on;
        flash.intensity = on && !store.get().reducedMotion ? FLASH : 0;   // reduced motion: the bolt, no flash
      });
    },

    placeholder(actor) {
      // transparent so it is drawn after the shell (renderOrder 2); depthTest false so the stone never hides it
      const material = new THREE.LineDashedMaterial({
        color: PLACEHOLDER_COLOUR, dashSize: 0.7, gapSize: 0.5, depthTest: false, transparent: true,
      });
      const box = keep(scene, new THREE.LineSegments(DASHED_BOX, material), material);
      box.position.fromArray(actor.at);
      box.renderOrder = 3;   // over everything, so the dashes are never hidden inside the stone
      const label = keep(box, tag(actor.label, 'placeholder-label'));
      label.position.y = 3.2;   // display choice: just above the cube
    },

    // In the claim cycle a field actor never has a solver result: say so at the masonry's centre, draw nothing.
    field() {
      keep(scene, tag('Solver result pending', 'pending-label')).position.copy(model.masonryBounds.getCenter(new THREE.Vector3()));
    },

    // Extension point (Task 9, chemistry): the calcium sulfate outline of S23. Until then a coat draws nothing.
    coat() {},
  };

  function clear() {
    for (const object of live) object.removeFromParent();   // a CSS2DObject takes its element out of the page
    for (const thing of trash) thing.dispose();
    live = [];
    trash = [];
    updaters = [];
    clouds = [];
    water.clear();
    flash.intensity = 0;
  }

  function build(step) {
    clear();
    current = step;
    builtOn = model.root;
    if (!step) return;   // the prologue: nothing
    const hazes = step.actors.filter(actor => actor.type === 'gas').reduce((n, actor) => n + actor.path.length, 0);
    // ponytail: the tier is read when the step is built; a quality change shows from the next step on.
    perSpace = tiers[store.get().quality].particles && hazes ? Math.floor(PARTICLES / hazes) : 0;
    // water first: the gas in a space is clipped to what lies above the water in it
    const ordered = [...step.actors].sort((a, b) => (a.type !== 'water') - (b.type !== 'water'));
    for (const actor of ordered) factories[actor.type](actor);
    // Extension point (Task 9, chemistry): one species label per space with water or gas goes here.
  }

  function update({ u, dt, source }) {
    if (current && builtOn !== model.root) build(current);   // the reading was swapped: rebuild on the new meshes
    for (const set of updaters) set(u, source);
    if (!store.get().reducedMotion) sway(dt);
    // a label follows its parents' visibility itself, whatever the CSS2D renderer does with hidden parents
    for (const object of live) if (object.isCSS2DObject) object.visible = shown(object.parent);
  }

  function dispose() {
    clear();
    current = null;
    scene.remove(flash);
    flash.dispose();
  }

  const round = x => +x.toFixed(2);
  const state = () => ({
    water: Object.fromEntries([...water].map(([space, w]) => [space, round(w.fraction)])),
    levels: Object.fromEntries([...water].map(([space, w]) => [space, round(w.level)])),
    labels: live.filter(object => object.isCSS2DObject && shown(object.parent)).map(object => object.element.textContent),
  });

  return { build, update, dispose, state };
}
```

- [ ] **Step 3: Extend `viewer/app.js`**

Edit 3a, imports. Replace the line

```js
import { createRenderer } from './render/renderer.js';
```

with

```js
import { createRenderer, TIERS } from './render/renderer.js';
```

and directly below the model import of Task 5 (`import { frameModel, loadModel } from './render/model.js';`) add:

```js
import { createActors } from './render/actors.js';
```

Edit 3b, the block. Insert directly below the Task 5 block (after its line `  Object.assign(window.viewer, { model });` and the blank line), still above `  // ---- start (Task 4)`:

```js
  // ---- actors (Task 6): Task 7's player builds and updates them; until then the console drives them
  const actors = createActors({ scene: rendererApi.scene, model, materials, store, cycle, tiers: TIERS });
  stateParts.push(actors.state);
  Object.assign(window.viewer, { actors });

```

`stateParts.push(actors.state)` makes `viewer.state()` merge `actors.state()` (`water`, `levels`, `labels`), as the header's `window.viewer.state` requires. `frame(dt)` does not change: Task 7's `player.tick(dt)` calls `actors.update`, and `frame` must not call it as well.

- [ ] **Step 4: Browser check: water in S12 at half volume**

In the page Step 1 opened, run `await Promise.all(['app.js', 'render/actors.js'].map(url => fetch(url, { cache: 'reload' })));`. Then `navigate` to `http://localhost:8765/?quality=low&v=t6b`, take a screenshot, then run (the first line waits for the actors, which exist once the model has loaded; the expected level is recomputed here from the curve with plan A's interpolation, independently of `levelAt`):

```js
for (let i = 0; i < 100 && !window.viewer?.actors; i++) await new Promise(r => setTimeout(r, 100));
const step = viewer.cycle.steps[11];
viewer.actors.build(step);
viewer.actors.update({ u: 0.5, dt: 0, source: { fraction: space => 0.5 } });
const st = viewer.actors.state();
const curve = viewer.cycle.curves.grand_gallery;
const target = 0.5 * curve[curve.length - 1][1];
let expected = curve[curve.length - 1][0];
for (let i = 1; i < curve.length; i++) {
  const [y0, v0] = curve[i - 1];
  const [y1, v1] = curve[i];
  if (v1 >= target) { expected = v1 === v0 ? y0 : y0 + (y1 - y0) * (target - v0) / (v1 - v0); break; }
}
const placeholders = step.actors.filter(a => a.type === 'placeholder').map(a => a.label);
({
  id: step.id,
  water: st.water.grand_gallery,
  level: st.levels.grand_gallery,
  expected: +expected.toFixed(2),
  close: Math.abs(st.levels.grand_gallery - expected) <= 0.01,
  labelsArePlaceholders: JSON.stringify(st.labels) === JSON.stringify(placeholders),
  gallerySkins: viewer.model.spaces.get('grand_gallery').children.filter(c => c.isMesh).length,
})
```

Expected: `{ id: 'S12', water: 0.5, level: 36.18, expected: 36.18, close: true, labelsArePlaceholders: true, gallerySkins: 1 }` (36.18 m is the height that holds half the Gallery's volume on the curve in `cycle.json`; the labels are S12's pump and two valve placeholders).

Now the picture. S12 is an interior step (it has water, gas and placeholder actors, so its `scene.interior` is true), but this task has no player to copy that flag into the store, so switch to the glass look by hand (Task 7's player sets it from the data):

```js
const { camera, controls } = viewer.rendererApi;
const key = viewer.cycle.steps[11].path[0];
camera.position.fromArray(key.position);
controls.target.fromArray(key.target);
viewer.store.set({ interior: true });
```

Take a screenshot, wait 2 seconds, take a screenshot `t6-s12-water`: through the dark glass every water space of S12 stands at half its volume (the check's source gives 0.5 for every space), so the passages and chambers above the plateau hold blue water to about half their height and the Grand Gallery is blue up to about its middle, each with a brighter line at its waterline (S12's first keyframe stands outside `model.bounds`, so the sand plain stays and hides the spaces under it, Task 4's rule); the King's Chamber shows a pale grey haze, and the three dashed placeholder cubes stand with their labels.

- [ ] **Step 5: Browser check: gas and the drain placeholder in S16; particles on the high tier**

```js
const step = viewer.cycle.steps[15];
viewer.actors.build(step);
viewer.actors.update({ u: 0.5, dt: 0, source: { fraction: space => 0.3 } });
const { camera, controls } = viewer.rendererApi;
camera.position.fromArray(step.path[0].position);
controls.target.fromArray(step.path[0].target);
const ante = viewer.model.spaces.get('antechamber');
const st = viewer.actors.state();
({
  id: step.id,
  antechamberHaze: ante.children.some(c => c.isMesh && c.visible),
  drain: st.labels.includes(step.actors.find(a => a.type === 'placeholder' && a.kind === 'drain').label),
  labels: st.labels,
  particles: [...viewer.model.spaces.values()].flatMap(m => m.children).flatMap(s => s.children).filter(o => o.isPoints).length,
})
```

Expected: `{ id: 'S16', antechamberHaze: true, drain: true, labels: ['Gallery drain: not specified by the hypothesis'], particles: 0 }` (no particles on the low tier). Screenshot (the interior look is still on from Step 4), wait 1 second, screenshot `t6-s16-gas`: a pale haze, brighter at its edges and slowly mottled, fills the antechamber and the King's Chamber; the Gallery water stands lower; the dashed drain cube and its label are drawn over everything.

Then `navigate` to `http://localhost:8765/?quality=high&v=t6c`, take a screenshot, and run:

```js
for (let i = 0; i < 100 && !window.viewer?.actors; i++) await new Promise(r => setTimeout(r, 100));
const step = viewer.cycle.steps[15];
viewer.actors.build(step);
viewer.actors.update({ u: 0.99, dt: 0.016, source: { fraction: space => 0.3 } });
const hazes = step.actors.filter(a => a.type === 'gas').reduce((n, a) => n + a.path.length, 0);
const counts = [...viewer.model.spaces.values()].flatMap(m => m.children).flatMap(s => s.children)
  .filter(o => o.isPoints).map(p => p.geometry.attributes.position.count);
({ quality: viewer.store.get().quality, clouds: counts.length, hazes, total: counts.reduce((a, b) => a + b, 0) })
```

Expected: `{ quality: 'high', clouds: 4, hazes: 4, total: 4000 }` (S16's gas paths cover the King's Chamber, the antechamber and the two King's Chamber shafts; 4,000 split four ways). Set `viewer.store.set({ interior: true })`, place the camera at `step.path[0]` as above, screenshot, wait 2 seconds, screenshot `t6-s16-particles`: sparse points glitter inside the antechamber, the King's Chamber and its two shafts and nowhere outside them. Return to `http://localhost:8765/?quality=low&v=t6d` for the remaining steps (a fresh page: the store's `interior` is false again).

- [ ] **Step 6: Browser check: the bolt in S06**

```js
for (let i = 0; i < 100 && !window.viewer?.actors; i++) await new Promise(r => setTimeout(r, 100));
const step = viewer.cycle.steps[5];
const scene = viewer.model.root.parent;
viewer.actors.build(step);
const bolt = () => scene.children.find(o => o.isLine2);
viewer.actors.update({ u: 0.35, dt: 0, source: { fraction: () => 0 } });
const at35 = bolt().visible;
viewer.actors.update({ u: 0.2, dt: 0, source: { fraction: () => 0 } });
const at20 = bolt().visible;
viewer.actors.update({ u: 0.35, dt: 0, source: { fraction: () => 0 } });
const { camera, controls } = viewer.rendererApi;
camera.position.fromArray(step.path[0].position);
controls.target.fromArray(step.path[0].target);
({ id: step.id, at35, at20, labels: viewer.actors.state().labels })
```

Expected: `{ id: 'S06', at35: true, at20: false, labels: ['Solver result pending'] }` (S06's field actor has no solver result). Run `viewer.store.set({ weather: 'storm' })` (S06's own weather; Task 7's player sets it, and S06's interior flag, from the data; here the store's `interior` stays false), take a screenshot, wait 2 seconds, take a screenshot `t6-s06-bolt`: under the darkened sky a jagged yellow-white line, several pixels thick, descends onto the apex of the stone pyramid (the low tier has no bloom; on the medium and high tiers it glows), and the "Solver result pending" label stands at the masonry's centre. Run `viewer.store.set({ weather: 'clear' })`.

- [ ] **Step 7: Browser check: a hidden space hides its water and its labels (Review Focus 4)**

```js
const step = viewer.cycle.steps[11];
viewer.actors.build(step);
const source = { fraction: () => 0.5 };
viewer.actors.update({ u: 0.5, dt: 0, source });
const gg = viewer.model.spaces.get('grand_gallery');
const before = viewer.actors.state().labels;
viewer.model.setHidden(new Set(['grand_gallery']));
viewer.actors.update({ u: 0.5, dt: 0, source });
({
  galleryVisible: gg.visible,
  skins: gg.children.filter(c => c.isMesh).length,
  waterOnScreen: gg.visible && gg.children.some(c => c.isMesh && c.visible),
  labelsBefore: before.length,
  labelsUnchanged: JSON.stringify(viewer.actors.state().labels) === JSON.stringify(before),
  galleryLabels: gg.children.filter(c => c.isCSS2DObject && c.visible).length,
})
```

Expected: `{ galleryVisible: false, skins: 1, waterOnScreen: false, labelsBefore: 3, labelsUnchanged: true, galleryLabels: 0 }`. The Gallery holds no label of its own until Task 9 adds the species labels (which, as children of the space, drop out of `state().labels` by the same `shown()` rule and are hidden by `update()`); S12's three placeholders are not inside the Gallery, so they stay. Place the camera at S12's first keyframe and switch the interior look on, as in Step 4 (`camera.position.fromArray(step.path[0].position)`, `controls.target.fromArray(step.path[0].target)`, `viewer.store.set({ interior: true })`), take a screenshot, wait 2 seconds, take a screenshot `t6-hidden-gallery`: the Gallery and its water are gone, the other passages still hold water. Restore with `viewer.model.setHidden(new Set())`.

- [ ] **Step 8: Browser check: a reading swap rebuilds the step on the new meshes**

```js
viewer.actors.build(viewer.cycle.steps[11]);
viewer.store.set({ reading: 'alternative' });
for (let i = 0; i < 100 && viewer.model.apexY < 140; i++) await new Promise(r => setTimeout(r, 100));
viewer.actors.update({ u: 0.5, dt: 0, source: { fraction: () => 0.5 } });
({
  apexY: +viewer.model.apexY.toFixed(2),
  gallerySkins: viewer.model.spaces.get('grand_gallery').children.filter(c => c.isMesh).length,
  water: viewer.actors.state().water.grand_gallery,
})
```

Expected: `{ apexY: 146.71, gallerySkins: 1, water: 0.5 }`. Restore with `viewer.store.set({ reading: 'survey' })` and poll until `viewer.model.apexY` is back to 137.38 (same loop with `> 140`).

- [ ] **Step 9: Browser check: build(null) clears everything**

```js
viewer.actors.build(viewer.cycle.steps[5]);
viewer.actors.update({ u: 0.35, dt: 0, source: { fraction: () => 0 } });
viewer.actors.build(null);
const scene = viewer.model.root.parent;
({
  state: viewer.actors.state(),
  bolts: scene.children.filter(o => o.isLine2).length,
  skins: [...viewer.model.spaces.values()].reduce((n, m) => n + m.children.length, 0),
  labelsInPage: document.querySelectorAll('.labels .placeholder-label, .labels .pending-label').length,
})
```

Expected: `{ state: { water: {}, levels: {}, labels: [] }, bolts: 0, skins: 0, labelsInPage: 0 }`. Screenshot: no water, gas, bolt, cube or label. `read_console_messages` with `onlyErrors: true`: no error from the page through Steps 4 to 9.

- [ ] **Step 10: Commit**

```bash
git add viewer/render/actors.js viewer/app.js
git commit -m "$(cat <<'EOF'
Port the actors to the new scene: shaded water and gas, gas particles, a Line2 bolt with a flash, placeholders

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
)"
```

### Task 7: Ride and player

**Files:**
- Create: `viewer/tour/camera.js`
- Create: `viewer/tour/player.js`
- Modify: `viewer/app.js` (one import pair, one line in `frame`, one block before the loop starts, two lines after it; exact edits in Step 4)

**Interfaces:**
- Consumes:
  - From Task 2, `viewer/data/cycle.json`: `prologue = { duration, path }`; `steps[i] = { id, title, duration, path, scene: { interior, weather }, species, reaction?, actors }`; `path` is 2 to 4 keyframes `{ position: [x, y, z], target: [x, y, z] }` in viewer coordinates; a water actor is `{ type: 'water', space, from, to, species }`.
  - From Task 3, `viewer/store.js`: `createStore` (the store has `get()`, `set(patch)`, `subscribe(fn)`) with the keys `stepIndex`, `t`, `playing`, `riding`, `interior`, `weather`, `reducedMotion`, `mode`, `quality`; `readUrl(location)` returning `{ stepId, mode, quality, nowebgl }`.
  - From Task 4, `createRenderer(stage, store)` returning `rendererApi` with `camera` (PerspectiveCamera), `controls` (OrbitControls built on the canvas, so `controls.domElement` is the canvas), `start(onFrame)` (the loop clamps `dt` to 0.1 s before calling `onFrame`), `lastDt`; `createEnvironment` returning `environment` with `mix.interior`, `mix.storm`, `update(dt)`.
  - From Task 5, `materials.update(dt)` and `model.setInterior(k)`.
  - From Task 6, `createActors(...)` returning `actors` with `build(step | null)`, `update({ u, dt, source })`, `state()`.
  - The layout Tasks 3 to 6 gave `viewer/app.js`: the imports at the top, among them `readUrl` from `./store.js` and `createActors` from `./render/actors.js`; everything else inside `async function boot()`, with the consts `url` (`readUrl(location)`, read first), `claims` (Task 3's `loadData` re-keys `claims.claims` by id), `cycle`, `store`, `rendererApi`, `environment`, `materials`, `model`, `actors`; `window.viewer`, created in Task 3 as `{ store, claims, cycle, manifest, state }` and extended with `Object.assign(window.viewer, {...})` (Task 4 adds `rendererApi` and `environment`, Task 5 `model`, Task 6 `actors`); `stateParts`, the array of functions whose results `state()` merges (it already yields `{ mode, quality, interior, weather, riding }`, Task 4's `{ lastDt }` and Task 6's `actors.state()`); Task 5's camera framing `frameModel(model, rendererApi.camera, rendererApi.controls);` inside the block `// ---- materials and model (Task 5)`; and as its last section the line `// ---- start (Task 4): stays the last block, so everything frame() reads exists before the first frame`, followed only by `function frame(dt)` (extended by Task 5) and `rendererApi.start(frame);`.
- Produces:
  - `viewer/tour/camera.js`: `RESUME_SECONDS = 1` (display choice) and `createRide(camera, controls, store)` returning `{ setPath(keyframes, { from }), update(dt, u), pause(), resume(), pose(), get riding() }` as the header specifies (`pose()` returns clones of the camera's position and the controls' target, which the player passes as `from`), plus one addition the header does not list: `drift(on)`, the switch for the prologue's slow drift. The header gives the drift to `controls.autoRotate` (`autoRotateSpeed` 0.3, a display choice) and the switch to the player, but the player is not handed the controls; the ride, which holds them, flips `controls.autoRotate`, leaves the camera alone while it drifts, and glides back onto the path when the drift stops.
  - `viewer/tour/player.js`: `timelineOf(cycle)` returning `{ entries, starts, total }` and `createPlayer({ store, cycle, actors, ride, claims })` returning `{ play, pause, toggle, seek, goto, gotoId, tick, total, state }`, as the header specifies, with one precision: the `from` of a new path is the current pose only while the cycle plays (a continuous flight from step to step); when paused (Next, Back, a deep link, a scrub of the strip), on the prologue and on the very first path it is `null`, so the camera cuts to the entry's first keyframe and its pose depends only on the step and `u`: the page opens on the prologue's first keyframe (spec 5.2), and a paused jump shows the new step's own view instead of the old one. The player owns the drift switch: `ride.drift(true)` while the prologue is on and the clock is not playing, `ride.drift(false)` when play starts or the step changes. `claims` is in the signature as the header lists it; the clock does not read it.
  - In `viewer/app.js`: the consts `ride` and `player`, created immediately before `rendererApi.start(frame);`; `window.viewer` gains `player`, `ride` and `camera` (`rendererApi.camera`) beside the `store`, `claims`, `cycle`, `environment`, `model` and `actors` earlier tasks put there; `stateParts` gains `player.state`, so `viewer.state()` merges `player.state()`, `actors.state()` and `{ mode, quality, interior, weather, riding, lastDt }`; right after `rendererApi.start(frame);` come `player.gotoId(url.stepId)` and the `hashchange` listener (Task 8 inserts its block before `rendererApi.start(frame);`; Task 10 adds the quality probe after it).

Background for the implementer. Four facts used below. `CatmullRomCurve3.getPoint(s)` spaces the keyframes evenly in `s`, while `getPointAt(s)` spaces them by arc length; the position and target curves have different lengths, so only `getPoint` keeps a camera position and the target it was authored with at the same `s`. With `controls.autoRotate` on, every `controls.update()` (the renderer's loop calls it after `onFrame`, with no time argument) turns the camera about `controls.target` by `autoRotateSpeed` × 2π / 3600, keeping its distance and height; the ride must leave the camera alone while it drifts, or its next `update` would put it back on the path and the drift would never show. three.js guards the centripetal parameterisation against two equal consecutive points, so a `from` pose equal to the first keyframe is harmless. A synthetic `PointerEvent` dispatched on the canvas makes OrbitControls call `setPointerCapture` for a pointer that is not active, which throws into the console; the checks below therefore press the canvas with a real click through the `computer` tool.

- [ ] **Step 1: State what must be observed, and see that it is not there yet**

After this task:

1. The page opens on the prologue: the camera starts at the prologue's first keyframe and drifts slowly about its target (`controls.autoRotate`, spec 5.2), nothing plays until asked, and the address ends in `#`. Play stops the drift.
2. `viewer.player.play()` flies the prologue and then the steps; each step change rebuilds the actors, starts a new camera path from wherever the camera is (while playing; a paused jump cuts to the step's first keyframe), sets `stepIndex`, `interior` and `weather` in the store, and writes the step id into the address.
3. On an interior step (S09) the environment cross-fades to the interior look; the camera moves along the step's path.
4. A press on the canvas hands the camera to the orbit controls (`riding` false) and the camera no longer follows the path; `viewer.ride.resume()` glides it back and sets `riding` true; the next step also takes it back.
5. S05 and S06 set the storm weather; unknown ids (`S99`, `foo`, none) open the prologue, from `gotoId` and from the address.
6. A long frame advances the clock by at most 0.1 s, because the renderer's loop clamps `dt`.
7. No error from the page in the console.

Run: `preview_start` with name `viewer`, `resize_window` to 1280 × 800, `navigate` to `http://localhost:8765/?quality=low&v=7a`, wait three seconds, then with `javascript_tool`: `typeof window.viewer?.player`
Expected now: `'undefined'`

- [ ] **Step 2: Write `viewer/tour/camera.js`**

```js
// Camera ride: a step's keyframes as two centripetal Catmull-Rom curves, one for the camera's
// position and one for the point it looks at, ridden with ease-in-out over the step. A press on
// the canvas hands the camera to the orbit controls; resume() or the next step takes it back.
// While the prologue waits for Play, the camera drifts slowly about its target (spec 5.2).
import * as THREE from 'three';

export const RESUME_SECONDS = 1;   // display choice: the glide back onto the path after resume()
const DRIFT_SPEED = 0.3;           // display choice: OrbitControls.autoRotateSpeed, one turn in about 200 s at 60 frames a second

const ease = k => k * k * (3 - 2 * k);   // smoothstep: ease in and out

export function createRide(camera, controls, store) {
  let positions = null;   // CatmullRomCurve3 through the camera positions
  let targets = null;     // CatmullRomCurve3 through the points looked at, one per position
  let first = null;       // the step's first keyframe: where a cut lands
  let riding = true;
  let drifting = false;   // the prologue's drift: OrbitControls turns the camera, the ride leaves it alone
  let glide = null;       // { position, target, k } while the camera comes back to the path
  const position = new THREE.Vector3();
  const target = new THREE.Vector3();
  controls.autoRotateSpeed = DRIFT_SPEED;

  function place(keyframe) {
    camera.position.fromArray(keyframe.position);
    controls.target.fromArray(keyframe.target);
  }

  function setRiding(on) {
    riding = on;
    store.set({ riding: on });   // the HUD shows "Resume ride" while it is false
  }

  // keyframes: [{position, target}, ...] in viewer coordinates. from: the pose the camera has now,
  // prepended so the move into the step is continuous; null starts the path on its own first keyframe.
  function setPath(keyframes, { from = null } = {}) {
    const points = key => keyframes.map(keyframe => new THREE.Vector3().fromArray(keyframe[key]));
    const ps = points('position');
    const ts = points('target');
    if (from) {
      ps.unshift(from.position.clone());
      ts.unshift(from.target.clone());
    }
    positions = new THREE.CatmullRomCurve3(ps, false, 'centripetal');
    targets = new THREE.CatmullRomCurve3(ts, false, 'centripetal');
    first = keyframes[0];
    glide = null;
    setRiding(true);   // the next step takes the camera back from the user (spec 5.1)
    if (!from || store.get().reducedMotion) place(first);   // reduced motion: steps cut instead of fly
  }

  function update(dt, u) {
    if (!riding || drifting || !positions || store.get().reducedMotion) return;
    const s = ease(u);
    positions.getPoint(s, position);   // getPoint, not getPointAt: both curves pass their keyframes at the same s
    targets.getPoint(s, target);
    if (glide) {   // from where the user or the drift left the camera to the moving point of the path
      glide.k = Math.min(1, glide.k + dt / RESUME_SECONDS);
      const k = ease(glide.k);
      position.lerpVectors(glide.position, position, k);
      target.lerpVectors(glide.target, target, k);
      if (glide.k === 1) glide = null;
    }
    camera.position.copy(position);
    controls.target.copy(target);
  }

  function pause() {
    glide = null;
    setRiding(false);
  }

  function resume() {
    if (riding) return;
    setRiding(true);
    if (store.get().reducedMotion) {
      if (first) place(first);
      return;
    }
    glide = { position: camera.position.clone(), target: controls.target.clone(), k: 0 };
  }

  // The player's switch for the prologue's drift: on while the prologue waits for Play, off when play
  // starts or the step changes. Switched off, the camera glides from where the drift left it to the path;
  // a step change lays a new path just after, which drops that glide.
  function drift(on) {
    on = on && !store.get().reducedMotion;   // reduced motion: the camera holds still
    if (on === drifting) return;
    drifting = on;
    controls.autoRotate = on;
    if (!on && riding) glide = { position: camera.position.clone(), target: controls.target.clone(), k: 0 };
  }

  // The pose now, which the player passes as the next path's "from".
  const pose = () => ({ position: camera.position.clone(), target: controls.target.clone() });

  controls.domElement.addEventListener('pointerdown', pause);
  controls.domElement.addEventListener('touchstart', pause, { passive: true });

  return { setPath, update, pause, resume, pose, drift, get riding() { return riding; } };
}
```

- [ ] **Step 3: Write `viewer/tour/player.js`**

```js
// Cycle clock: the prologue and the 31 steps on one time line. A step change builds the step's
// actors, lays the camera's path from where the camera is, and sets the scene flags and the address.

// entries[0] is the prologue; entries[k] for k >= 1 is the step of index k - 1.
export function timelineOf(cycle) {
  const prologue = {
    id: 'prologue', duration: cycle.prologue.duration, path: cycle.prologue.path,
    scene: { interior: false, weather: 'clear' }, actors: [],
  };
  const entries = [prologue, ...cycle.steps];
  const starts = [];   // starts[k]: seconds from the start of the prologue to the start of entries[k]
  let total = 0;
  for (const entry of entries) { starts.push(total); total += entry.duration; }
  return { entries, starts, total };
}

// claims is in the signature as the plan header lists it; the clock does not read it.
export function createPlayer({ store, cycle, actors, ride, claims }) {
  const { entries, starts, total } = timelineOf(cycle);
  let t = 0;              // seconds from the start of the prologue
  let u = 0;              // 0 to 1 within the current entry
  let index = null;       // -1 the prologue, 0..30 the steps; null before the first entry
  let playing = false;
  let water = new Map();  // space -> the current step's water actor

  // Claim mode's answer to "how full is this space now": the step's own from and to, at u.
  const source = {
    fraction(space) {
      const actor = water.get(space);
      return actor ? actor.from + (actor.to - actor.from) * u : 0;
    },
  };

  function enter(i) {
    const entry = entries[i + 1];
    // While playing, the new path starts where the camera is: one continuous flight. Paused (Next, Back, a deep
    // link, a scrub) or at boot, it starts on its own first keyframe, so a paused jump shows the step's own view.
    const from = playing ? ride.pose() : null;
    index = i;
    water = new Map(entry.actors.filter(actor => actor.type === 'water').map(actor => [actor.space, actor]));
    actors.build(i < 0 ? null : entry);
    ride.drift(i < 0 && !playing);   // before setPath: the new path replaces the glide that ending a drift starts
    ride.setPath(entry.path, { from });
    store.set({ stepIndex: i, interior: entry.scene.interior, weather: entry.scene.weather });
    try {
      history.replaceState(null, '', i < 0 ? '#' : '#' + entry.id);
    } catch {
      // browsers throttle rapid replacements while the strip is scrubbed (Safari throws); the next step catches up
    }
  }

  function locate() {   // the entry at time t, and how far into it
    let k = entries.length - 1;
    while (k > 0 && starts[k] > t) k--;
    u = Math.min(1, (t - starts[k]) / entries[k].duration);
    if (k - 1 !== index) enter(k - 1);
  }

  function apply(dt) {
    actors.update({ u, dt, source });
    ride.update(dt, u);
  }

  // ponytail: store.t is written on seek, play and pause, not every frame (every subscriber would run
  // each frame); player.state().t is the live clock. Write it per frame once a V2 panel needs it live.
  function setPlaying(on) {
    playing = on;
    ride.drift(index === -1 && !on);   // spec 5.2: the prologue drifts while it waits for Play
    store.set({ playing: on, t });
  }

  function tick(dt) {   // dt arrives clamped to 0.1 s by the renderer's loop
    if (playing) {
      t = Math.min(total, t + dt);
      locate();
      if (t === total) setPlaying(false);
    }
    apply(dt);
  }

  function seek(seconds) {
    t = Math.max(0, Math.min(total, seconds));
    locate();
    store.set({ t });
    apply(0);   // the actors and the camera take the new time at once, not on the next frame
  }

  function play() {
    if (t >= total) seek(0);
    setPlaying(true);
  }

  function pause() {
    setPlaying(false);
  }

  function goto(i) {   // -1 the prologue, 0..30 a step; anything else is ignored
    if (Number.isInteger(i) && i >= -1 && i < entries.length - 1) seek(starts[i + 1]);
  }

  function gotoId(id) {
    const k = entries.findIndex(entry => entry.id === id);
    goto(k > 0 ? k - 1 : -1);   // an unknown id (#S99, #foo, none) opens the prologue
  }

  const state = () => ({ id: entries[index + 1].id, u: +u.toFixed(3), playing, t: +t.toFixed(3) });

  locate();   // enter the prologue now: the camera, the actors, the drift and the store are set before the first frame
  return { play, pause, toggle: () => (playing ? pause() : play()), seek, goto, gotoId, tick, total, state };
}
```

- [ ] **Step 4: Wire the ride and the player into `viewer/app.js`**

Make these four edits. Every other line stays as Tasks 3 to 6 wrote it; in particular Task 5's framing call `frameModel(...)` in its block above the start section stays (it sets the camera's near and far planes; the new block runs after it, so the player's first path puts the camera on the prologue's first keyframe last).

(a) Immediately after the line `import { createActors } from './render/actors.js';` add:

```js
import { createRide } from './tour/camera.js';
import { createPlayer } from './tour/player.js';
```

(b) In `function frame(dt)` (section `// ---- start (Task 4)`), add `player.tick(dt);` as its last line. The player calls `actors.update` and `ride.update` itself, so `frame` does not call `actors.update`. The function then reads exactly:

```js
  function frame(dt) {
    environment.update(dt, model.bounds.containsPoint(rendererApi.camera.position));
    materials.update(dt);
    model.setInterior(environment.mix.interior);
    player.tick(dt);   // the clock; it updates the actors and the ride
  }
```

(c) Immediately before the line `rendererApi.start(frame);` insert this block. It runs after Task 5's framing and before the loop starts, so `frame` never reads `player` while it is still uninitialised. It sits inside the start section, below `function frame(dt)`, rather than above the section as Task 3's block rule says: the loop must not start before `player` exists, and Task 10's finished `app.js` keeps the block in this place.

```js
  // ---- Task 7: the camera ride and the cycle clock
  const ride = createRide(rendererApi.camera, rendererApi.controls, store);
  const player = createPlayer({ store, cycle, actors, ride, claims });   // enters the prologue and sets the hash to '#'
  Object.assign(window.viewer, { player, ride, camera: rendererApi.camera });
  stateParts.push(player.state);

```

(d) Immediately after the line `rendererApi.start(frame);` add:

```js
  player.gotoId(url.stepId);   // url was read first at boot, before the player rewrote the hash
  window.addEventListener('hashchange', () => player.gotoId(readUrl(location).stepId));
```

After the edits, `grep -c "rendererApi.start(" viewer/app.js` prints `1`, `grep -c "createPlayer(" viewer/app.js` prints `1`, and the start section ends:

```js
  // ---- Task 7: the camera ride and the cycle clock
  const ride = createRide(rendererApi.camera, rendererApi.controls, store);
  const player = createPlayer({ store, cycle, actors, ride, claims });   // enters the prologue and sets the hash to '#'
  Object.assign(window.viewer, { player, ride, camera: rendererApi.camera });
  stateParts.push(player.state);

  rendererApi.start(frame);
  player.gotoId(url.stepId);   // url was read first at boot, before the player rewrote the hash
  window.addEventListener('hashchange', () => player.gotoId(readUrl(location).stepId));
```

followed by whatever closes `boot()` as Task 3 wrote it.

- [ ] **Step 5: Verify in the browser: the prologue on load, play into S01**

1. `navigate` to `http://localhost:8765/?quality=low&v=7b`, wait three seconds, take a screenshot, then run:

```js
(() => {
  const d = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
  const s = viewer.state();
  const first = viewer.cycle.prologue.path[0];
  const camera = viewer.camera.position.toArray();
  const controls = viewer.rendererApi.controls;
  return {
    id: s.id, playing: s.playing, t: s.t, interior: s.interior, weather: s.weather, riding: s.riding,
    hash: location.hash, endsWithHash: location.href.endsWith('#'),
    drift: [controls.autoRotate, controls.autoRotateSpeed],
    // the drift turns the camera about the target: its distance to the target and its height stay the first keyframe's
    radius: +(d(camera, first.target) - d(first.position, first.target)).toFixed(3),
    height: +(camera[1] - first.position[1]).toFixed(3),
    target: +d(viewer.ride.pose().target.toArray(), first.target).toFixed(3),
    keys: ['id', 'u', 'playing', 't', 'water', 'levels', 'labels', 'mode', 'quality', 'interior', 'weather', 'riding', 'lastDt']
      .filter(key => !(key in s)),
  };
})()
```

Expected: `{ id: 'prologue', playing: false, t: 0, interior: false, weather: 'clear', riding: true, hash: '', endsWithHash: true, drift: [true, 0.3], radius: 0, height: 0, target: 0, keys: [] }` (`radius`, `height` and `target` each at most 0.01 in size; `keys` lists the header's `state()` keys missing from the merged summary, and must be empty). The screenshot shows the pyramid from far outside on the plateau.

Then check that the camera drifts. Take a screenshot (a hidden pane runs no frames), then run:

```js
(async () => {
  const d = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
  const first = viewer.cycle.prologue.path[0];
  const before = viewer.camera.position.toArray();
  await new Promise(resolve => setTimeout(resolve, 2000));
  const after = viewer.camera.position.toArray();
  return {
    moved: +d(before, after).toFixed(2),
    radius: +(d(after, first.target) - d(first.position, first.target)).toFixed(3),
    height: +(after[1] - first.position[1]).toFixed(3),
    id: viewer.state().id,
  };
})()
```

Expected: `moved` greater than 1 (at 60 frames a second the drift covers about 0.063 rad in 2 s, about 47 m at the first keyframe's horizontal distance of about 748 m from the target; fewer frames, less), `radius` and `height` at most 0.01 in size (the camera stays on the circle of the first keyframe), `id` `'prologue'` (the clock did not start). If `moved` is 0, the pane was hidden: take a screenshot and run it again.

2. The clock, without depending on the frame rate, and the drift switched by the step:

```js
(() => {
  const controls = viewer.rendererApi.controls;
  viewer.player.seek(viewer.cycle.prologue.duration + 0.5);
  const s = viewer.state();
  const result = [s.id, s.interior, viewer.cycle.steps[0].scene.interior, location.hash, viewer.store.get().stepIndex, controls.autoRotate];
  viewer.player.seek(0);
  return [...result, viewer.state().id, controls.autoRotate];
})()
```

Expected: `['S01', false, false, '#S01', 0, false, 'prologue', true]` (a step change stops the drift; back on the prologue, paused, it drifts again).

3. Real time. Take a screenshot (a hidden pane runs no frames), run `viewer.player.play(); viewer.rendererApi.controls.autoRotate`.
Expected: `false` (play stops the drift; the camera glides from where the drift left it back onto the prologue's path over RESUME_SECONDS). `computer` `wait` 8 seconds, take a screenshot, then run `[viewer.state().id, viewer.state().t, viewer.state().interior, viewer.state().playing, viewer.rendererApi.controls.autoRotate]`.
Expected: `['S01', t, false, true, false]` with `t` between 6 and 11 (the prologue lasts `cycle.prologue.duration`, 6 s, and S01 lasts 5 s). The loop advances at most 0.1 s per frame, so a slow frame rate plays slower than the clock: if `t` is still under 6, take another screenshot, wait 3 seconds and read again; the id reads `'S01'` once `t` passes 6. The screenshots show the camera having moved from the far view toward the pyramid. Finish with `viewer.player.pause()`.

- [ ] **Step 6: Verify in the browser: S09 is interior, the look cross-fades, the camera rides the path**

1. Run:

```js
(() => {
  viewer.player.gotoId('S09');
  const s = viewer.state();
  return [s.id, s.interior, viewer.cycle.steps[8].scene.interior, s.weather, location.hash, viewer.store.get().stepIndex];
})()
```

Expected: `['S09', true, true, 'clear', '#S09', 8]`.

2. Take a screenshot, `computer` `wait` 2 seconds, then run `viewer.environment.mix.interior`.
Expected: `1` (the fade runs at 1/FADE_SECONDS per second, FADE_SECONDS = 1.5). If the pane was hidden and it reads less than 1, run `viewer.environment.update(2); viewer.environment.mix.interior`, which must give `1`. A screenshot shows the masonry as dark glass with the spaces inside and no ground.

3. Run:

```js
(() => {
  const d = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
  const step = viewer.cycle.steps[8];
  const start = viewer.cycle.prologue.duration + viewer.cycle.steps.slice(0, 8).reduce((sum, s) => sum + s.duration, 0);
  const at = u => { viewer.player.seek(start + u * step.duration); return viewer.camera.position.toArray(); };
  const p10 = at(0.1);
  const p90 = at(0.9);
  const end = at(0.999);
  return {
    id: viewer.state().id,
    moved: +d(p10, p90).toFixed(2),
    toLast: +d(end, step.path[step.path.length - 1].position).toFixed(3),
  };
})()
```

Expected: `id` `'S09'`, `moved` greater than 1 (the camera at u 0.1 and u 0.9 stands in different places), `toLast` under 0.1 (at the end of the step the camera reaches the step's last keyframe).

- [ ] **Step 7: Verify in the browser: a press on the canvas pauses the ride, resume() and the next step take it back**

1. Run `viewer.player.seek(viewer.cycle.prologue.duration + viewer.cycle.steps.slice(0, 8).reduce((sum, s) => sum + s.duration, 0) + 0.5 * viewer.cycle.steps[8].duration)` (S09 at u 0.5). Take a screenshot, then `computer` `left_click` at the middle of the upper half of the canvas (about x 640, y 240 of a 1280 × 800 screenshot; the canvas has no overlay yet).

2. Run:

```js
(() => {
  const d = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
  const step = viewer.cycle.steps[8];
  const start = viewer.cycle.prologue.duration + viewer.cycle.steps.slice(0, 8).reduce((sum, s) => sum + s.duration, 0);
  const before = viewer.camera.position.toArray();
  viewer.player.seek(start + 0.9 * step.duration);
  return {
    riding: viewer.state().riding, storeRiding: viewer.store.get().riding, rideRiding: viewer.ride.riding,
    stayed: +d(before, viewer.camera.position.toArray()).toFixed(3),
  };
})()
```

Expected: `{ riding: false, storeRiding: false, rideRiding: false, stayed: 0 }`: the camera no longer follows the path when the time moves.

3. Run `viewer.ride.resume(); [viewer.state().riding, viewer.ride.riding]`.
Expected: `[true, true]`.

4. Run `viewer.player.tick(1)` (RESUME_SECONDS is 1; with the clock paused, tick only advances the glide, so this completes it without depending on frames), then:

```js
(() => {
  const d = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
  const step = viewer.cycle.steps[8];
  const start = viewer.cycle.prologue.duration + viewer.cycle.steps.slice(0, 8).reduce((sum, s) => sum + s.duration, 0);
  viewer.player.seek(start + 0.999 * step.duration);
  return +d(viewer.camera.position.toArray(), step.path[step.path.length - 1].position).toFixed(3);
})()
```

Expected: under 0.1: the camera follows the path again.

5. `computer` `left_click` on the canvas again (same place), confirm `viewer.state().riding` is `false`, then run `viewer.player.goto(9); [viewer.state().id, viewer.state().riding]`.
Expected: `['S10', true]`: the next step takes the camera back.

- [ ] **Step 8: Verify in the browser: weather, unknown ids, the address, the dt clamp, the console**

1. Run:

```js
(() => {
  const p = viewer.player;
  const out = {};
  p.gotoId('S05'); out.s05 = [viewer.state().weather, viewer.store.get().weather];
  p.gotoId('S06'); out.s06 = viewer.state().weather;
  p.gotoId('S07'); out.s07 = viewer.state().weather;
  out.stormInData = viewer.cycle.steps.filter(s => s.scene.weather === 'storm').map(s => s.id);
  p.gotoId('S99'); out.s99 = [viewer.state().id, viewer.store.get().stepIndex, location.hash];
  p.gotoId('S12'); p.gotoId('foo'); out.foo = viewer.state().id;
  p.gotoId('S12'); p.gotoId(null); out.none = viewer.state().id;
  return out;
})()
```

Expected: `{ s05: ['storm', 'storm'], s06: 'storm', s07: 'clear', stormInData: ['S05', 'S06'], s99: ['prologue', -1, ''], foo: 'prologue', none: 'prologue' }`. Then run `viewer.player.gotoId('S05')`, take a screenshot, wait 2 seconds and take another: the sky is darker in the second (the storm mix), and no exception is thrown.

2. The address drives the player:

```js
(async () => {
  const settle = () => new Promise(resolve => setTimeout(resolve, 50));
  location.hash = '#S16'; await settle(); const a = viewer.state().id;
  location.hash = '#foo'; await settle(); const b = viewer.state().id;
  return [a, b, location.hash];
})()
```

Expected: `['S16', 'prologue', '']`.

3. The dt clamp lives in the renderer's loop: `player.tick(dt)` adds whatever it is given, and the loop never gives more than 0.1 s. Take a screenshot (the pane must be visible for frames to run), then run:

```js
(async () => {
  const nextFrame = () => Promise.race([
    new Promise(resolve => requestAnimationFrame(resolve)),
    new Promise(resolve => setTimeout(() => resolve('no frame'), 3000)),
  ]);
  viewer.player.seek(20);
  viewer.player.play();
  if (await nextFrame() === 'no frame') return 'no frame: the pane is hidden, take a screenshot and run again';
  const before = viewer.state().t;
  const end = performance.now() + 400;
  while (performance.now() < end) {}   // one forced frame of 0.4 s
  await nextFrame();
  const after = viewer.state().t;
  viewer.player.pause();
  return { lastDt: viewer.state().lastDt, advanced: +(after - before).toFixed(3) };
})()
```

Expected: `lastDt` equal to `0.1` (at most 0.1) and `advanced` at most `0.101`: a 0.4 s frame moved the clock by 0.1 s. Then wait 2 seconds and run `viewer.state().lastDt`: a number greater than 0 and at most 0.1.

4. `read_console_messages` with `onlyErrors: true`.
Expected: no entries from the page.

- [ ] **Step 9: Commit**

```bash
git add viewer/tour/camera.js viewer/tour/player.js viewer/app.js
git commit -m "Ride the camera along each step's path and play the cycle from a prologue" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 8: Cinematic HUD and controls

**Files:**
- Create: `viewer/hud/cinematic.js`
- Modify: `viewer/style.css` (one block appended)
- Modify: `viewer/app.js` (one import, one block; exact edits in Step 4)

**Interfaces:**
- Consumes:
  - From Task 7, `player` (`play`, `pause`, `toggle`, `seek`, `goto`, `gotoId`, `state`), `ride` (`resume`), `timelineOf(cycle)` from `viewer/tour/player.js` (`starts[k]` for `entries[k]`, the prologue at `k = 0`), and in `viewer/app.js` the bindings `ride`, `player` and the statement `rendererApi.start(frame);`.
  - From Task 3, the store keys `stepIndex`, `playing`, `riding`, `hud`, `mode` and `store.subscribe(fn)` calling `fn(next, prev, changed: Set<string>)`; the empty `<div id="hud">` in `viewer/index.html`, outside which the notice sits; the colour tokens of `viewer/style.css`: `--text`, `--muted`, `--line`, `--raised`, `--accent`, `--pass`, `--fail`, `--conditional`, `--undefined`, `--pending`.
  - From Task 3's `loadData`, `claims.claims[id]` with `statement`, `status`, `basis` (the file carries a list; `loadData` re-keys it by id, as the header states); `cycle.notice`; `cycle.steps[i].id` and `.title`.
- Produces:
  - `viewer/hud/cinematic.js`: `mountCinematic(root, { store, cycle, claims, player, ride })` returning `{ unmount() }`, exactly as the header specifies.
  - Inside `#hud`: `.overlay` (the button "Play the claimed cycle"), `.hud-card` holding `.caption` (`h2`, `.statement`, `.verdict` with `.badge.status-<status>` and `.basis`), `.strip` (31 `.tick.status-<status>`, the current one `.current`) and `.controls` (Back, Play or Pause, Next, Resume ride, Fullscreen, Hide HUD); `#hud.hidden` while `store.hud.visible` is false.
  - The keyboard: Space, ArrowLeft, ArrowRight, I, F, H, Escape, handled on `window`.

Background for the implementer. The prologue's slow drift, which the header notes under `mountCinematic`, is Task 7's: the player switches `controls.autoRotate` through `ride.drift`, so the HUD's play button and Space key only call `player.play()` or `player.toggle()`. Verdict colours go on the badge and the strip's ticks only, never on a scene material. The notice is not inside `#hud`, so hiding the HUD leaves it on screen. `requestFullscreen()` called from a key event that a script dispatched is refused with a rejected promise; the HUD catches it, so the checks' synthetic F leaves the console clean. A real drag on the strip is done with the `computer` tool's `left_click_drag`, because the strip captures the pointer and a synthetic pointer has no capture to take.

- [ ] **Step 1: State what must be observed, and see that it is not there yet**

After this task, at 1280 × 800:

1. On the prologue a centred button "Play the claimed cycle" appears; it starts the cycle and disappears while the cycle plays. The caption card shows the page title and the notice text.
2. On a step the card shows the step id and title, the claim as stated in `claims.json`, the verdict badge (class `status-<status>`) and the basis sentence; below it a strip of 31 ticks coloured by verdict, the current one enlarged; a drag on the strip scrubs.
3. The controls: Back, Play or Pause, Next, Resume ride (only while the user holds the camera), Fullscreen, Hide HUD. Space plays or pauses, Left and Right step, H hides and shows the HUD while the notice stays, I flips `store.mode`, Escape sets it to `'cinematic'`, F asks for fullscreen.
4. `#S99` in the address opens the prologue.
5. No error from the page in the console.

Run: `resize_window` to 1280 × 800, `navigate` to `http://localhost:8765/?quality=low&v=8a`, wait three seconds, then: `document.getElementById('hud').children.length`
Expected now: `0`

- [ ] **Step 2: Write `viewer/hud/cinematic.js`**

```js
// Cinematic HUD: one card with the caption (step, claim as stated, verdict, basis), the progress
// strip and the controls; the play overlay on the prologue; the keyboard. Text is set with textContent.
import { timelineOf } from '../tour/player.js';

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function button(text, label, onClick) {
  const node = el('button', '', text);
  node.type = 'button';
  node.setAttribute('aria-label', label);   // every label contains the visible text
  node.addEventListener('click', onClick);
  return node;
}

export function mountCinematic(root, { store, cycle, claims, player, ride }) {
  const steps = cycle.steps;
  const { starts } = timelineOf(cycle);

  // ---- caption: the prologue shows the title and the notice, a step its claim and verdict
  const heading = el('h2');
  const statement = el('p', 'statement');
  const badge = el('span', 'badge');
  const basis = el('p', 'basis');
  const verdict = el('div', 'verdict');
  verdict.append(badge, basis);
  const caption = el('section', 'caption');
  caption.setAttribute('aria-live', 'polite');
  caption.append(heading, statement, verdict);

  // ---- strip: one tick per step, coloured by verdict; a drag scrubs
  const strip = el('div', 'strip');
  strip.tabIndex = 0;
  strip.setAttribute('role', 'slider');
  strip.setAttribute('aria-label', 'Step of the cycle: drag to scrub, Left and Right to step');
  strip.setAttribute('aria-valuemin', '0');
  strip.setAttribute('aria-valuemax', String(steps.length));
  const ticks = steps.map(step => {
    const status = claims.claims[step.id].status;
    const tick = el('span', `tick status-${status}`);
    tick.title = `${step.id} ${step.title} (${status})`;
    strip.append(tick);
    return tick;
  });

  // The ticks are equal, so the pointer's place on the strip names a step and a point inside it.
  function scrubTo(clientX) {
    const box = strip.getBoundingClientRect();
    const x = Math.min(Math.max((clientX - box.left) / box.width, 0), 0.9999) * steps.length;
    const i = Math.floor(x);
    player.seek(starts[i + 1] + (x - i) * steps[i].duration);
  }
  strip.addEventListener('pointerdown', event => {
    player.pause();
    strip.setPointerCapture(event.pointerId);
    scrubTo(event.clientX);
  });
  strip.addEventListener('pointermove', event => {
    if (strip.hasPointerCapture(event.pointerId)) scrubTo(event.clientX);
  });

  // ---- controls
  const toggleHud = () => store.set({ hud: { visible: !store.get().hud.visible } });
  function toggleFullscreen() {
    if (!document.fullscreenEnabled) return;
    const request = document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
    request.catch(() => {});   // refused without a user gesture (a key event sent by a script): nothing to undo
  }
  const backButton = button('Back', 'Back to the previous step', () => player.goto(store.get().stepIndex - 1));
  const playButton = button('Play', 'Play', () => player.toggle());
  const nextButton = button('Next', 'Next step', () => player.goto(store.get().stepIndex + 1));
  const resumeButton = button('Resume ride', 'Resume ride', () => ride.resume());
  const fullscreenButton = button('Fullscreen', 'Fullscreen', toggleFullscreen);
  fullscreenButton.hidden = !document.fullscreenEnabled;   // a browser without the Fullscreen API
  // ponytail: with the HUD hidden only the H key brings it back; V2's phone layout adds a touch control.
  const hideButton = button('Hide HUD', 'Hide HUD (H shows it again)', toggleHud);
  const controls = el('div', 'controls');
  controls.append(backButton, playButton, nextButton, resumeButton, fullscreenButton, hideButton);

  const card = el('div', 'hud-card');
  card.append(caption, strip, controls);
  const overlay = el('div', 'overlay');
  overlay.append(button('Play the claimed cycle', 'Play the claimed cycle', () => player.play()));
  root.replaceChildren(overlay, card);

  // ---- rendering: each part from the store keys it shows
  function renderStep({ stepIndex }) {
    const step = steps[stepIndex];   // undefined on the prologue (-1)
    const claim = step && claims.claims[step.id];
    heading.textContent = step ? `${step.id} ${step.title}` : document.title;
    statement.textContent = step ? claim.statement : cycle.notice;
    verdict.hidden = !step;
    if (step) {
      badge.className = `badge status-${claim.status}`;
      badge.textContent = claim.status;
      basis.textContent = claim.basis;
    }
    ticks.forEach((tick, i) => tick.classList.toggle('current', i === stepIndex));
    strip.setAttribute('aria-valuenow', String(stepIndex + 1));
    strip.setAttribute('aria-valuetext', step ? heading.textContent : 'Prologue');
    backButton.disabled = stepIndex < 0;
    nextButton.disabled = stepIndex >= steps.length - 1;
  }
  function renderPlaying({ stepIndex, playing }) {
    playButton.textContent = playing ? 'Pause' : 'Play';
    playButton.setAttribute('aria-label', playButton.textContent);
    overlay.hidden = stepIndex !== -1 || playing;
  }
  const renderRiding = ({ riding }) => { resumeButton.hidden = riding; };
  const renderHud = ({ hud }) => { root.classList.toggle('hidden', !hud.visible); };

  const unsubscribe = store.subscribe((state, previous, changed) => {
    if (changed.has('stepIndex')) renderStep(state);
    if (changed.has('stepIndex') || changed.has('playing')) renderPlaying(state);
    if (changed.has('riding')) renderRiding(state);
    if (changed.has('hud')) renderHud(state);
  });
  const initial = store.get();
  renderStep(initial);
  renderPlaying(initial);
  renderRiding(initial);
  renderHud(initial);

  // ---- keyboard
  const keys = {
    ' ': () => player.toggle(),
    ArrowLeft: () => player.goto(store.get().stepIndex - 1),
    ArrowRight: () => player.goto(store.get().stepIndex + 1),
    i: () => store.set({ mode: store.get().mode === 'inspector' ? 'cinematic' : 'inspector' }),   // V2 mounts the inspector
    f: toggleFullscreen,
    h: toggleHud,
    Escape: () => store.set({ mode: 'cinematic' }),
  };
  function onKey(event) {
    if (event.ctrlKey || event.metaKey || event.altKey) return;   // the browser's own shortcuts
    const key = event.key || '';
    if (event.target instanceof HTMLButtonElement && (key === ' ' || key === 'Enter')) return;   // a focused button clicks itself
    const action = keys[key.length === 1 ? key.toLowerCase() : key];
    if (!action) return;
    event.preventDefault();   // Space would scroll the page
    action();
  }
  window.addEventListener('keydown', onKey);

  return {
    unmount() {
      unsubscribe();
      window.removeEventListener('keydown', onKey);
      root.replaceChildren();
      root.classList.remove('hidden');
    },
  };
}
```

- [ ] **Step 3: Append the HUD styles to `viewer/style.css`**

Append to the end of `viewer/style.css`:

```css

/* ---- the cinematic HUD (Task 8). Verdict colours appear only on the badge and the strip's ticks. */
#hud.hidden { display: none; }                /* H hides the HUD; the notice sits outside #hud and stays */
#hud [hidden] { display: none !important; }   /* the hidden attribute beats the display rules below */

#hud .hud-card {
  position: fixed; left: 50%; bottom: 16px; z-index: 5; transform: translateX(-50%);
  box-sizing: border-box; width: calc(100% - 32px); max-width: 720px; padding: 16px;
  display: grid; gap: 12px; pointer-events: auto;
  color: var(--text);
  background: rgba(21, 23, 26, 0.78);   /* display choice: dark glass; the text keeps 4.5:1 over a bright sky */
  -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px);
  border: 1px solid var(--line); border-radius: 12px;
}
#hud .caption { max-height: 40vh; overflow-y: auto; overflow-wrap: break-word; }
#hud .caption h2 { margin: 0 0 6px; font-size: 16px; line-height: 1.3; }
#hud .caption p { margin: 0 0 6px; }
#hud .verdict { display: flex; gap: 10px; align-items: flex-start; }
#hud .verdict .basis { margin: 0; color: var(--muted); }
#hud .badge {
  flex: none; padding: 2px 10px; border: 1px solid transparent; border-radius: 999px;
  font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #14161a;
}

#hud .strip { display: flex; gap: 2px; align-items: center; height: 16px; cursor: pointer; touch-action: none; }
#hud .tick {
  flex: 1 1 0; min-width: 0; height: 6px; box-sizing: border-box;
  border: 1px solid transparent; border-radius: 2px;
}
#hud .tick.current { height: 16px; box-shadow: 0 0 0 1px var(--text); }
#hud .badge.status-pass, #hud .tick.status-pass { background: var(--pass); }
#hud .badge.status-fail, #hud .tick.status-fail { background: var(--fail); }
#hud .badge.status-conditional, #hud .tick.status-conditional { background: var(--conditional); }
#hud .badge.status-pending, #hud .tick.status-pending { background: var(--pending); }
#hud .badge.status-undefined, #hud .tick.status-undefined {
  background: transparent; color: var(--undefined); border: 1px dashed var(--undefined);
}

#hud .controls { display: flex; flex-wrap: wrap; gap: 8px; }
#hud button {
  font: inherit; color: var(--text); background: var(--raised);
  border: 1px solid var(--line); border-radius: 6px; padding: 6px 10px; cursor: pointer;
}
#hud button:disabled { opacity: 0.45; cursor: default; }
#hud button:focus-visible, #hud .strip:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

#hud .overlay { position: fixed; inset: 0; z-index: 6; display: grid; place-items: center; pointer-events: none; }
#hud .overlay button { pointer-events: auto; padding: 12px 20px; font-size: 16px; border-color: var(--accent); }

/* phone width: the card spans the bottom edge, with its 16 px gutters inside */
@media (max-width: 760px) {
  #hud .hud-card {
    left: 0; right: 0; bottom: 0; transform: none; width: 100%; max-width: none;
    border-width: 1px 0 0; border-radius: 0;
  }
}
```

- [ ] **Step 4: Mount the HUD in `viewer/app.js`**

Make two edits; every other line stays as Task 7 left it.

(a) Immediately after the line `import { createPlayer } from './tour/player.js';` add:

```js
import { mountCinematic } from './hud/cinematic.js';
```

(b) Immediately before the line `rendererApi.start(frame);` insert:

```js
  // ---- Task 8: the cinematic HUD
  mountCinematic(document.getElementById('hud'), { store, cycle, claims, player, ride });

```

The start section of `viewer/app.js` now ends:

```js
  // ---- Task 7: the camera ride and the cycle clock
  const ride = createRide(rendererApi.camera, rendererApi.controls, store);
  const player = createPlayer({ store, cycle, actors, ride, claims });   // enters the prologue and sets the hash to '#'
  Object.assign(window.viewer, { player, ride, camera: rendererApi.camera });
  stateParts.push(player.state);

  // ---- Task 8: the cinematic HUD
  mountCinematic(document.getElementById('hud'), { store, cycle, claims, player, ride });

  rendererApi.start(frame);
  player.gotoId(url.stepId);   // url was read first at boot, before the player rewrote the hash
  window.addEventListener('hashchange', () => player.gotoId(readUrl(location).stepId));
```

followed by whatever closes `boot()` as Task 3 wrote it.

- [ ] **Step 5: Verify in the browser: the prologue overlay and the start of play**

1. `resize_window` to 1280 × 800, `navigate` to `http://localhost:8765/?quality=low&v=8b`, wait three seconds, take a screenshot, then run:

```js
(() => {
  const q = selector => document.querySelector(selector);
  return {
    overlay: !q('#hud .overlay').hidden && q('#hud .overlay button').getBoundingClientRect().width > 0,
    button: q('#hud .overlay button').textContent,
    heading: q('#hud .caption h2').textContent === document.title,
    statement: q('#hud .caption .statement').textContent === viewer.cycle.notice,
    verdictHidden: q('#hud .caption .verdict').hidden,
    live: q('#hud .caption').getAttribute('aria-live'),
    labelled: [...document.querySelectorAll('#hud button')].every(b => b.getAttribute('aria-label')),
    controls: [...document.querySelectorAll('#hud .controls button')].map(b => b.textContent),
    resumeHidden: q('#hud .controls button[aria-label="Resume ride"]').hidden,
    firstInBody: document.body.firstElementChild.id,
    drift: viewer.rendererApi.controls.autoRotate,
  };
})()
```

Expected: `{ overlay: true, button: 'Play the claimed cycle', heading: true, statement: true, verdictHidden: true, live: 'polite', labelled: true, controls: ['Back', 'Play', 'Next', 'Resume ride', 'Fullscreen', 'Hide HUD'], resumeHidden: true, firstInBody: 'notice', drift: true }` (`drift`: the prologue waits for the button with the camera drifting, Task 7). The screenshot shows the notice along the top, the button in the middle of the window and the glass card at the bottom centre with the title "Great Pyramid: the claimed cycle" and the notice sentence.

2. `find` "Play the claimed cycle", `computer` `left_click` on it, then run `[viewer.state().playing, document.querySelector('#hud .overlay').hidden, document.querySelectorAll('#hud .controls button')[1].textContent, viewer.rendererApi.controls.autoRotate]`.
Expected: `[true, true, 'Pause', false]` (the button plays the cycle and the drift stops). Run `viewer.player.pause()`.

- [ ] **Step 6: Verify in the browser: the S07 caption and the strip**

1. Run:

```js
(() => {
  viewer.player.gotoId('S07');
  const q = selector => document.querySelector(selector);
  const statusOf = id => viewer.claims.claims[id].status;
  const claim = viewer.claims.claims.S07;
  const ticks = [...document.querySelectorAll('#hud .strip .tick')];
  return {
    heading: q('#hud .caption h2').textContent === `S07 ${viewer.cycle.steps[6].title}`,
    statement: q('#hud .caption .statement').textContent === claim.statement,
    badge: q('#hud .badge').className,
    expectedBadge: `badge status-${claim.status}`,
    badgeText: q('#hud .badge').textContent,
    basis: q('#hud .caption .basis').textContent === claim.basis,
    ticks: ticks.length,
    classes: ticks.every((tick, i) => tick.classList.contains(`status-${statusOf(viewer.cycle.steps[i].id)}`)),
    current: ticks.findIndex(tick => tick.classList.contains('current')),
    failTicks: document.querySelectorAll('#hud .strip .tick.status-fail').length,
    failInData: viewer.cycle.steps.filter(s => statusOf(s.id) === 'fail').length,
  };
})()
```

Expected: `heading: true`, `statement: true`, `badge: 'badge status-fail'` equal to `expectedBadge`, `badgeText: 'fail'`, `basis: true`, `ticks: 31`, `classes: true`, `current: 6`, and `failTicks` equal to `failInData` (7 with the `claims.json` this plan starts from: S07 and six other steps are `fail`).

2. Take a screenshot: the card shows "S07" and its title, the claim, a red FAIL badge beside the basis sentence, and the strip with its seventh tick enlarged; the scene behind it carries no verdict colour.

- [ ] **Step 7: Verify in the browser: the keyboard**

1. Run:

```js
(() => {
  const key = k => window.dispatchEvent(new KeyboardEvent('keydown', { key: k, bubbles: true, cancelable: true }));
  const out = {};
  viewer.player.gotoId('S07');
  key('ArrowRight'); out.right = viewer.state().id;
  key('ArrowLeft'); out.left = viewer.state().id;
  key(' '); out.space = viewer.state().playing;
  key(' '); out.space2 = viewer.state().playing;
  key('i'); out.mode = viewer.state().mode;
  key('Escape'); out.escape = viewer.state().mode;
  key('f'); out.f = 'no throw';
  viewer.player.goto(-1); key('ArrowLeft'); out.atStart = viewer.state().id;
  viewer.player.gotoId('S07');
  key('h');
  const notice = document.getElementById('notice').getBoundingClientRect();
  out.hidden = [document.getElementById('hud').classList.contains('hidden'),
    document.querySelector('#hud .hud-card').getClientRects().length, notice.top, notice.height];
  return out;
})()
```

Expected: `{ right: 'S08', left: 'S07', space: true, space2: false, mode: 'inspector', escape: 'cinematic', f: 'no throw', atStart: 'prologue', hidden: [true, 0, 0, 28] }`. Take a screenshot: only the scene and the notice along the top.

2. Run `window.dispatchEvent(new KeyboardEvent('keydown', { key: 'H' })); [document.getElementById('hud').classList.contains('hidden'), document.querySelector('#hud .hud-card').getClientRects().length]`.
Expected: `[false, 1]`. If `document.fullscreenElement` is not `null` (the tool may run scripts as a user gesture, and the synthetic F was then granted), run `document.exitFullscreen()` before going on; the notice was on top either way.

- [ ] **Step 8: Verify in the browser: Resume ride, the buttons, the scrub**

1. Run `viewer.player.gotoId('S12'); document.querySelector('#hud .controls button[aria-label="Resume ride"]').hidden`.
Expected: `true`. Take a screenshot, then `computer` `left_click` on the canvas above the card (about x 640, y 200 of a 1280 × 800 screenshot), then run `[viewer.state().riding, document.querySelector('#hud .controls button[aria-label="Resume ride"]').hidden]`.
Expected: `[false, false]`; a screenshot shows the "Resume ride" button. `find` "Resume ride", `computer` `left_click` on it, then run the same expression.
Expected: `[true, true]`.

2. `find` "Next step", `left_click` it, run `viewer.state().id`: `'S13'`. `find` "Back to the previous step", `left_click` it, run `viewer.state().id`: `'S12'`.

3. Run `(() => { const r = document.querySelector('#hud .strip').getBoundingClientRect(); return [r.left, r.right, r.top + r.height / 2]; })()`, take a screenshot, then `computer` `left_click_drag` from the strip's left end (a few pixels right of `left`, at the strip's height) to its midpoint, in the screenshot's coordinates. Then run `[viewer.state().playing, viewer.state().id, document.querySelector('#hud .strip .tick.current') !== null]`.
Expected: `playing` `false`; `id` the step whose tick lay under the end of the drag, which for the midpoint of 31 equal ticks is S16, give or take a step for the screenshot's scaling; `true`. A screenshot shows that tick enlarged and the caption of that step.

- [ ] **Step 9: Verify in the browser: deep links, the source rules, the console**

1. `navigate` to `http://localhost:8765/?quality=low&v=8c#S99`, wait three seconds, run `[viewer.state().id, location.hash, document.querySelector('#hud .overlay').hidden, document.querySelector('#hud .caption h2').textContent === document.title]`.
Expected: `['prologue', '', false, true]`.

2. `navigate` to `http://localhost:8765/?quality=low&v=8d#S16` (a new query, so the page loads afresh), wait three seconds, run `[viewer.state().id, document.querySelector('#hud .caption h2').textContent.startsWith('S16 '), location.hash]`.
Expected: `['S16', true, '#S16']`.

3. Run: `grep -rn "innerHTML" viewer/hud viewer/tour viewer/app.js; grep -rn $'\xe2\x80\x94' viewer/hud viewer/tour viewer/app.js viewer/style.css`
Expected: no output (no `innerHTML`; the second pattern is the UTF-8 bytes of an em dash, and there is none).

4. `read_console_messages` with `onlyErrors: true`.
Expected: no entries from the page.

- [ ] **Step 10: Commit**

```bash
git add viewer/hud/cinematic.js viewer/style.css viewer/app.js
git commit -m "Caption each step with its claim and verdict, and drive the cycle from a strip, buttons and keys" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 9: Chemistry in the scene

**Files:**
- Modify: `viewer/render/actors.js` (the two extension points Task 6 left: the empty `coat()` factory and the comment at the end of `build(step)`; plus the colour and hatching of the water and gas skins)
- Modify: `viewer/style.css` (one rule, `.species-label`, after the `.pending-label` rule)
- Test: browser checks through `window.viewer` (no JavaScript test runner)

**Interfaces:**
- Consumes: `createActors({ scene, model, materials, store, cycle, tiers })` and its internals `keep(parent, object, ...owned)`, `skin(space, material, offset)`, `tag(text, className)`, `cloud(space, haze, plane, count)`, the `factories` table, the closure variable `current` (the step being built), the two extension points (the empty `coat()` factory and the comment at the end of `build(step)`), and the label visibility rule of `update` and `state` (`shown(object.parent)`) (Task 6); `materials.water(plane)` (a new `MeshStandardMaterial` per call, recoloured with `material.color.set`), `materials.gas(plane, colourHex)`, `materials.hatch(material, colourHex)` (wraps the material's own `onBeforeCompile`, its own program cache key) (Task 5); `model.spaces`, `model.root`, `model.setHidden` (Task 5); the species payloads of `cycle.json` (`{id, formula, name, phase, colour, status}`, on `step.species` and on every water and gas actor's `species`) (Task 2); `viewer.player.gotoId`, `viewer.state()`, `viewer.model`, `viewer.store` (Tasks 3 to 7).
- Produces: `createActors` with the same signature and return shape (and `levelAt` still exported); `state().labels` now also lists the species labels; the CSS class `species-label`. Nothing later renames them.

What this task adds, in the words of the spec (section 6.3) and the header:

1. **Species labels.** After a step's actors are built, one `CSS2DObject` (class `species-label`) per space that has a water or gas actor. Its text is the formulas of the species of every water and gas actor in that space, in build order (water first, as `build` already sorts), each species once, joined by `" · "`; `" (claimed)"` follows a species whose status is `"claimed"`, and nothing follows any other status (the spec tags `"conditional"` species in the inspector's legend, which is plan V2; the status stays in `cycle.json`). The label is a child of the space mesh at the centre of the mesh's geometry bounding box (the mesh's own frame), so it is hidden with the space (Task 6's `update` sets every label's `visible` from its parents, whatever the CSS2D renderer does with hidden parents) and its text drops out of `state().labels` through Task 6's `shown(object.parent)` filter.
2. **Liquid and haze colour.** A water skin takes the colour of its actor's first-listed species (`material.color.set(...)`); a gas skin is created with its actor's first species' colour (`materials.gas(plane, colour)`), replacing Task 6's display constant `HAZE_COLOUR`, which is deleted. The particle cloud of a haze (`cloud`, high tier) takes the same colour.
3. **Hatching.** When an actor's first-listed species has status `"claimed"`, its skin material goes through `materials.hatch(material, colour)` before the skin is created (before the material is first compiled).
4. **Coat.** The `coat` actor (`{type: coat, space}`, only in S23) draws `EdgesGeometry` of the space mesh's geometry as `LineSegments`, a child of the space mesh, `renderOrder` 2, in the colour of `calcium_sulfate` from the step's `species` list.
5. **State.** Species labels are kept with `keep(...)` like every per-step object, so `state().labels` lists them without a change to `state()`.

Exact changes to Task 6's file, in order (Step 3 shows the whole file as it must read afterwards; every other line is Task 6's, unchanged):

- the two-line header comment becomes three lines that name the chemistry (and no longer name plan A's deleted `timeline.js`, which Task 10's grep looks for);
- delete the line `const HAZE_COLOUR = '#d9dde2'; ...`;
- after the line `const CHORD = 0.15; ...` add the comment and the constants `CLAIMED` and `COAT_SPECIES`;
- after the function `tag` add the helpers `mark(material, species)` and `centreOf(space)`;
- `cloud(space, haze, plane, count)` gains a last parameter `colour`, used for the `PointsMaterial` colour in place of `HAZE_COLOUR`;
- in `factories.water`: `const species = actor.species[0];`, `material.color.set(species.colour);` and `skin(actor.space, mark(material, species), -4)`;
- in `factories.gas`: `const species = actor.species[0];`, the haze `skin(space, mark(materials.gas(plane, species.colour), species), -2)` and `cloud(space, haze, plane, perSpace, species.colour)`;
- replace the empty `coat() {}` factory and its extension-point comment with the `coat(actor)` factory;
- add the function `labelSpecies(ordered)` directly above `function build(step)`, and replace the extension-point comment at the end of `build(step)` with `labelSpecies(ordered);`.

- [ ] **Step 1: Run the failing browser check**

Start the server with `preview_start` (`name: "viewer"`), set the viewport with `resize_window` (`width: 1280, height: 800`), and navigate to `http://localhost:8765/?quality=low&v=9a`. Take a screenshot (it forces frames while the pane is hidden), then run with the JavaScript tool:

```js
for (let i = 0; i < 100 && !window.viewer?.player; i++) await new Promise(r => setTimeout(r, 100));   // the model loads first
window.check = {
  cycle: await fetch('data/cycle.json').then(r => r.json()),
  claims: await fetch('data/claims.json').then(r => r.json()),
  step(id) { return this.cycle.steps.find(s => s.id === id); },
  verdict(id) { return this.claims.claims.find(c => c.id === id).status; },   // claims.json lists the claims
  // The species labels a step must show, computed from cycle.json: one per space with water or gas,
  // that space's species in actor order with water first, each once, with the status suffix.
  expected(id) {
    const suffix = status => (status === 'claimed' ? ' (claimed)' : '');   // the scene marks claimed species only
    const present = new Map();
    const ordered = [...this.step(id).actors].sort((a, b) => (a.type !== 'water') - (b.type !== 'water'));
    for (const actor of ordered.filter(a => a.type === 'water' || a.type === 'gas')) {
      for (const space of actor.type === 'water' ? [actor.space] : actor.path) {
        const list = present.get(space) ?? [];
        for (const s of actor.species) if (!list.some(x => x.id === s.id)) list.push(s);
        present.set(space, list);
      }
    }
    return new Map([...present].map(([space, list]) => [space, list.map(s => s.formula + suffix(s.status)).join(' · ')]));
  },
  coats() {
    return ['grand_gallery', 'queens_chamber']
      .map(name => viewer.model.spaces.get(name).children.filter(o => o.isLineSegments).length);
  },
};
viewer.player.gotoId('S16');
const want = check.expected('S16');
({ labels: viewer.state().labels, present: [...want.values()].filter(t => viewer.state().labels.includes(t)).length });
```

Expected now (Task 6 has no species labels): `labels` holds only `"Gallery drain: not specified by the hypothesis"`, and `present` is `0`. Then run `viewer.player.gotoId('S23'); check.coats()`: expected `[0, 0]`. This is the failing state.

- [ ] **Step 2: Add the `.species-label` rule to `viewer/style.css`**

Find this line (kept from plan A by Task 3):

```css
.pending-label { color: var(--pending); border-color: var(--pending); }
```

and insert directly after it:

```css
/* species labels (Task 9): the formulas present in a space; a solid border, unlike the dashed placeholders */
.species-label {
  padding: 2px 6px; border-radius: 4px; font-size: 12px; white-space: nowrap;
  background: rgba(21, 23, 26, 0.85); color: var(--text); border: 1px solid var(--line);
}
@media (max-width: 760px) {
  .species-label { font-size: 11px; }   /* as the placeholder labels on a phone */
}
```

No verdict colour is used: a species label is a scene label, and the "(claimed)" text carries the marking.

- [ ] **Step 3: Write the final `viewer/render/actors.js`**

Replace the file with this content: Task 6's file with exactly the changes listed above. If the committed Task 6 file differs from the unchanged lines below (a reviewer's fix landed after this plan was written), keep the committed lines, apply only the listed changes, and name the difference in the report.

```js
// Actors of a step: water, gas, lightning, placeholders, the pending-field label, and the chemistry (species
// labels, liquids and hazes in their species' colours, hatched claimed products, the coat of S23).
// build(step) makes the step's objects; update() sets them to the moment u of the step.
import * as THREE from 'three';
import { CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';

// Display choices, not physical quantities (so are the opacities, dash lengths and label offsets below).
const FAR = 1e6;   // display choice: a height far above (or, negated, far below) anything in the model
const PLACEHOLDER_COLOUR = 0xd9dde2;    // display choice
// display choice: a placeholder is a 4 m dashed cube, a symbol whose size says nothing about what it stands for
const DASHED_BOX = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(4, 4, 4)))
  .computeLineDistances().geometry;
// display choice: the bolt, [east, up, south] of each vertex as fractions of the masonry height, from the apex
const BOLT = [[0.1, 0.6, -0.06], [0.04, 0.47, 0.02], [0.09, 0.36, -0.03], [0.02, 0.24, 0.05],
  [0.06, 0.14, 0], [-0.01, 0.06, 0.02], [0, 0, 0]];
const STROKES = [[0.3, 0.42], [0.48, 0.56]];   // display choice: two brief strokes, as fractions of the step
const BOLT_HEX = 0xfff3b0;   // display choice
const BOLT_GLOW = 4;         // display choice: the bolt is drawn brighter than white, so the bloom catches it
const BOLT_WIDTH = 1.2;      // display choice: metres, so the bolt thins with distance
const FLASH = 6;             // display choice: the flash's intensity; with no fall-off it lights the pyramid alike
const PARTICLES = 4000;      // display choice: the most gas particles in one step, all its spaces together
const PARTICLE_SIZE = 0.15;  // display choice: metres
const SWAY = 0.25;           // display choice: radians per second of each particle's slow sway
const CHORD = 0.15;          // display choice: a particle sways over this fraction of a chord of its space
// The marking rule in the scene (spec section 6.3): this text follows the formula of a species whose status in
// cycle.json is "claimed"; the "conditional" tag belongs to the inspector's legend (plan V2), not to the scene.
const CLAIMED = ' (claimed)';
const COAT_SPECIES = 'calcium_sulfate';   // the coat of S23 is its calcium sulfate layer (chemistry spec 3.2)

// The height (viewer Y) at which a space holds the fraction f of its volume.
// curve: [[y, volume below y], ...] with y ascending, as written by level_volume_curve.
export function levelAt(curve, f) {
  const target = f * curve[curve.length - 1][1];
  for (let i = 1; i < curve.length; i++) {
    const [y0, v0] = curve[i - 1];
    const [y1, v1] = curve[i];
    if (v1 >= target) return v1 === v0 ? y0 : y0 + (y1 - y0) * (target - v0) / (v1 - v0);
  }
  return curve[curve.length - 1][0];
}

// Whether an object and all its parents are visible: a label in a hidden space is not on screen.
function shown(object) {
  for (let node = object; node; node = node.parent) if (!node.visible) return false;
  return true;
}

// A point inside the convex hull of a mesh's vertices: a convex combination of four of them, with
// exponential weights, which spread the points evenly over the tetrahedron of the four.
// ponytail: the hull, not the mesh. The Grand Gallery's corbels make its hull a few decimetres wider than the
// space near the roof; test candidates with a parity raycast against the mesh if particles show outside it.
function inside(vertices, out) {
  out.set(0, 0, 0);
  let sum = 0;
  for (let n = 0; n < 4; n++) {
    const i = Math.floor(Math.random() * vertices.count);
    const w = -Math.log(1 - Math.random());
    out.x += w * vertices.getX(i);
    out.y += w * vertices.getY(i);
    out.z += w * vertices.getZ(i);
    sum += w;
  }
  return out.divideScalar(sum);
}

export function createActors({ scene, model, materials, store, cycle, tiers }) {
  let live = [];       // objects that exist only for the current step
  let trash = [];      // what they own and give back to the GPU when the step ends
  let updaters = [];   // functions that set the actors to the current u
  let clouds = [];     // gas particles that sway
  let current = null;  // the step built, or null
  let builtOn = null;  // the model root it was built on; a reading swap replaces the root
  let perSpace = 0;    // particles in each gas space of the current step
  let clock = 0;       // seconds of sway
  const water = new Map();   // space -> { fraction, level } at the current u
  // One flash light for the whole session: adding and removing a light would recompile every material.
  const flash = new THREE.PointLight(BOLT_HEX, 0, 0, 0);   // distance 0, decay 0: no fall-off
  scene.add(flash);

  function keep(parent, object, ...owned) {   // add an object that lives only for the current step
    parent.add(object);
    live.push(object);
    trash.push(...owned);
    return object;
  }

  // A second skin on a space's mesh. As a child of that mesh it shares its position and its visibility
  // (a hidden space hides its water and gas with it), and model.pickAt never sees it.
  function skin(space, material, offset) {
    const source = model.spaces.get(space);
    Object.assign(material, { polygonOffset: true, polygonOffsetFactor: offset, polygonOffsetUnits: offset });
    const mesh = new THREE.Mesh(source.geometry, material);
    mesh.renderOrder = 1;   // after the opaque spaces, before the masonry
    return keep(source, mesh, material);
  }

  function tag(text, className) {
    const element = document.createElement('div');
    element.className = className;
    element.textContent = text;
    return new CSS2DObject(element);
  }

  // A product of a step that failed or is undefined (status "claimed") is drawn hatched.
  function mark(material, species) {
    return species.status === 'claimed' ? materials.hatch(material, species.colour) : material;
  }

  function centreOf(space) {   // the centre of a space's bounds, in its mesh's own frame, which its children share
    const geometry = model.spaces.get(space).geometry;
    if (!geometry.boundingBox) geometry.computeBoundingBox();
    return geometry.boundingBox.getCenter(new THREE.Vector3());
  }

  // A sparse cloud of gas particles in a space, a child of its haze (same visibility, same clipping plane).
  // Each particle sways along a short chord between two points of the space's hull, so it stays inside.
  function cloud(space, haze, plane, count, colour) {
    const vertices = model.spaces.get(space).geometry.attributes.position;
    const from = new Float32Array(count * 3);
    const to = new Float32Array(count * 3);
    const phase = new Float32Array(count);
    const a = new THREE.Vector3();
    const b = new THREE.Vector3();
    for (let i = 0; i < count; i++) {
      inside(vertices, a);
      inside(vertices, b).lerp(a, 1 - CHORD);   // b is moved most of the way back to a
      a.toArray(from, 3 * i);
      b.toArray(to, 3 * i);
      phase[i] = Math.random() * 2 * Math.PI;
    }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(from.slice(), 3));
    const material = new THREE.PointsMaterial({
      color: colour, size: PARTICLE_SIZE, transparent: true, opacity: 0.6, depthWrite: false,
      blending: THREE.AdditiveBlending, clippingPlanes: [plane],
    });
    const points = keep(haze, new THREE.Points(geometry, material), geometry, material);
    points.frustumCulled = false;   // the particles move; the bounding sphere of their first positions is stale
    clouds.push({ points, from, to, phase });
  }

  function sway(dt) {
    clock += dt;
    for (const { points, from, to, phase } of clouds) {
      const position = points.geometry.attributes.position;
      for (let i = 0; i < phase.length; i++) {
        const k = 0.5 + 0.5 * Math.sin(clock * SWAY + phase[i]);
        for (let c = 3 * i; c < 3 * i + 3; c++) position.array[c] = from[c] + (to[c] - from[c]) * k;
      }
      position.needsUpdate = true;
    }
  }

  const factories = {
    water(actor) {
      const species = actor.species[0];   // a mixture is drawn in the colour of its first-listed species
      const plane = new THREE.Plane(new THREE.Vector3(0, -1, 0), 0);   // keeps what lies below y = plane.constant
      const material = materials.water(plane);
      material.color.set(species.colour);
      const mesh = skin(actor.space, mark(material, species), -4);
      const curve = cycle.curves[actor.space];
      updaters.push((u, source) => {
        const fraction = source.fraction(actor.space);
        const level = fraction <= 0 ? -FAR : fraction >= 1 ? FAR : levelAt(curve, fraction);
        plane.constant = level;
        material.userData.uLevel.value = level;
        mesh.visible = fraction > 0;
        water.set(actor.space, { fraction, level });
      });
    },

    gas(actor) {
      const species = actor.species[0];   // a mixture is drawn in the colour of its first-listed species
      actor.path.forEach((space, k) => {
        const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), FAR);   // keeps what lies above y = -plane.constant
        const haze = skin(space, mark(materials.gas(plane, species.colour), species), -2);
        if (perSpace) cloud(space, haze, plane, perSpace, species.colour);
        updaters.push(u => {
          haze.visible = u >= k / actor.path.length;               // the path lights up one space after another
          plane.constant = -(water.get(space)?.level ?? -FAR);     // only above any water in the same space
        });
      });
    },

    lightning() {
      const top = model.apexY;   // the apex, from the model itself
      const geometry = new LineGeometry()
        .setPositions(BOLT.flatMap(([east, up, south]) => [east * top, top * (1 + up), south * top]));
      const material = new LineMaterial({
        color: new THREE.Color(BOLT_HEX).multiplyScalar(BOLT_GLOW), linewidth: BOLT_WIDTH, worldUnits: true,
      });
      const bolt = keep(scene, new Line2(geometry, material), geometry, material);
      flash.position.set(0, top * 1.3, 0);   // display choice: just above the apex, among the bolt's upper vertices
      updaters.push(u => {
        const on = STROKES.some(([start, end]) => u > start && u < end);
        bolt.visible = on;
        flash.intensity = on && !store.get().reducedMotion ? FLASH : 0;   // reduced motion: the bolt, no flash
      });
    },

    placeholder(actor) {
      // transparent so it is drawn after the shell (renderOrder 2); depthTest false so the stone never hides it
      const material = new THREE.LineDashedMaterial({
        color: PLACEHOLDER_COLOUR, dashSize: 0.7, gapSize: 0.5, depthTest: false, transparent: true,
      });
      const box = keep(scene, new THREE.LineSegments(DASHED_BOX, material), material);
      box.position.fromArray(actor.at);
      box.renderOrder = 3;   // over everything, so the dashes are never hidden inside the stone
      const label = keep(box, tag(actor.label, 'placeholder-label'));
      label.position.y = 3.2;   // display choice: just above the cube
    },

    // In the claim cycle a field actor never has a solver result: say so at the masonry's centre, draw nothing.
    field() {
      keep(scene, tag('Solver result pending', 'pending-label')).position.copy(model.masonryBounds.getCenter(new THREE.Vector3()));
    },

    // The calcium sulfate layer of S23: the edges of the coated space, in that species' colour.
    coat(actor) {
      const species = current.species.find(s => s.id === COAT_SPECIES);
      if (!species) throw new Error(`cycle.json: ${current.id}: a coat needs ${COAT_SPECIES} in the step's species`);
      const source = model.spaces.get(actor.space);
      const geometry = new THREE.EdgesGeometry(source.geometry);
      const material = new THREE.LineBasicMaterial({ color: species.colour });
      const outline = keep(source, new THREE.LineSegments(geometry, material), geometry, material);
      outline.renderOrder = 2;   // after the water and gas skins
    },
  };

  function clear() {
    for (const object of live) object.removeFromParent();   // a CSS2DObject takes its element out of the page
    for (const thing of trash) thing.dispose();
    live = [];
    trash = [];
    updaters = [];
    clouds = [];
    water.clear();
    flash.intensity = 0;
  }

  // One label per space with water or gas: the species of every such actor there, in build order (water
  // first), each once, "(claimed)" after a claimed one; a child of the space mesh at the centre of its bounds.
  function labelSpecies(ordered) {
    const present = new Map();   // space -> species payloads
    for (const actor of ordered) {
      if (actor.type !== 'water' && actor.type !== 'gas') continue;
      for (const space of actor.type === 'water' ? [actor.space] : actor.path) {
        const list = present.get(space) ?? [];
        for (const species of actor.species) if (!list.some(s => s.id === species.id)) list.push(species);
        present.set(space, list);
      }
    }
    for (const [space, list] of present) {
      const text = list.map(species => species.formula + (species.status === 'claimed' ? CLAIMED : '')).join(' · ');
      keep(model.spaces.get(space), tag(text, 'species-label')).position.copy(centreOf(space));
    }
  }

  function build(step) {
    clear();
    current = step;
    builtOn = model.root;
    if (!step) return;   // the prologue: nothing
    const hazes = step.actors.filter(actor => actor.type === 'gas').reduce((n, actor) => n + actor.path.length, 0);
    // ponytail: the tier is read when the step is built; a quality change shows from the next step on.
    perSpace = tiers[store.get().quality].particles && hazes ? Math.floor(PARTICLES / hazes) : 0;
    // water first: the gas in a space is clipped to what lies above the water in it
    const ordered = [...step.actors].sort((a, b) => (a.type !== 'water') - (b.type !== 'water'));
    for (const actor of ordered) factories[actor.type](actor);
    labelSpecies(ordered);
  }

  function update({ u, dt, source }) {
    if (current && builtOn !== model.root) build(current);   // the reading was swapped: rebuild on the new meshes
    for (const set of updaters) set(u, source);
    if (!store.get().reducedMotion) sway(dt);
    // a label follows its parents' visibility itself, whatever the CSS2D renderer does with hidden parents
    for (const object of live) if (object.isCSS2DObject) object.visible = shown(object.parent);
  }

  function dispose() {
    clear();
    current = null;
    scene.remove(flash);
    flash.dispose();
  }

  const round = x => +x.toFixed(2);
  const state = () => ({
    water: Object.fromEntries([...water].map(([space, w]) => [space, round(w.fraction)])),
    levels: Object.fromEntries([...water].map(([space, w]) => [space, round(w.level)])),
    labels: live.filter(object => object.isCSS2DObject && shown(object.parent)).map(object => object.element.textContent),
  });

  return { build, update, dispose, state };
}
```

- [ ] **Step 4: Run the browser checks**

`python3 -m http.server` sends no cache headers and a page query does not change the URLs of the modules the page imports, so first run, in the page Step 1 opened, `await Promise.all(['render/actors.js', 'style.css'].map(url => fetch(url, { cache: 'reload' })));`. Then navigate to `http://localhost:8765/?quality=low&v=9b`, take a screenshot, and define `window.check` again with the first block of Step 1 (everything up to and including the closing `};` of `window.check`). Then run each check below with the JavaScript tool, taking the named screenshot where one is asked for. A screenshot forces a frame; run the reading part of a check after it.

1. S16, the reaction step that fails. Run `viewer.player.gotoId('S16')` (paused, the camera cuts to the step's first keyframe), take a screenshot, wait 2 s (the look cross-fades to the interior), and take screenshot `t9-S16`: the camera at S16's first keyframe looks at the antechamber; the King's Chamber haze is in the sulfur-dioxide colour and the antechamber haze in the sulfur-trioxide colour with diagonal screen-space stripes about 8 px apart; one species label sits in each occupied space. Then:

```js
const want16 = check.expected('S16');
const labels16 = viewer.state().labels;
({
  id: viewer.state().id,
  every: [...want16.values()].every(text => labels16.includes(text)),
  onePerSpace: labels16.filter(text => [...want16.values()].includes(text)).length === want16.size,
  antechamber: want16.get('antechamber'),
  verdict: check.verdict('S16'),
  so3: check.step('S16').species.find(s => s.id === 'so3').status,
});
```

Expected: `id: 'S16'`, `every: true`, `onePerSpace: true`, `antechamber` ends with `'SO₃ (claimed)'`, `verdict: 'fail'`, `so3: 'claimed'`.

2. A hidden space hides its species label (Review Focus 4), still on S16:

```js
viewer.model.setHidden(new Set(['antechamber']));
const hidden = viewer.state().labels.includes(check.expected('S16').get('antechamber'));
viewer.model.setHidden(new Set());
({ hidden, back: viewer.state().labels.includes(check.expected('S16').get('antechamber')) });
```

Expected: `{ hidden: false, back: true }`.

3. S20, sulfurous acid oxidised (fail). Run `viewer.player.gotoId('S20')` and take screenshot `t9-S20`: the Grand Gallery liquid in the dilute-sulfuric-acid colour (`#c25b5b` in `species.yaml`, a muted red, a species colour and not a verdict colour) with diagonal dark stripes, its label reading the acid, water and air formulas. Then:

```js
const gallery20 = check.expected('S20').get('grand_gallery');
({
  shown: viewer.state().labels.includes(gallery20),
  gallery: gallery20,
  verdict: check.verdict('S20'),
  status: check.step('S20').species.find(s => s.id === 'sulfuric_acid').status,
});
```

Expected: `shown: true`, `gallery` contains `'H₂SO₄ (claimed)'`, `verdict: 'fail'`, `status: 'claimed'`.

4. S19, sulfur dioxide dissolves (pending). Run `viewer.player.gotoId('S19')`, then:

```js
const gallery19 = check.expected('S19').get('grand_gallery');
({ shown: viewer.state().labels.includes(gallery19), gallery: gallery19, claimed: gallery19.includes('(claimed)'), verdict: check.verdict('S19') });
```

Expected: `shown: true`, `gallery` contains `'H₂SO₃'`, `claimed: false`, `verdict: 'pending'`. Screenshot `t9-S19`: the Gallery liquid in the sulfurous-acid colour, no stripes.

5. S23, the coat. Run `viewer.player.gotoId('S23')`, then:

```js
const outline = viewer.model.spaces.get('grand_gallery').children.find(o => o.isLineSegments);
({
  coats: check.coats(),
  colour: '#' + outline.material.color.getHexString(),
  expected: check.step('S23').species.find(s => s.id === 'calcium_sulfate').colour,
});
```

Expected: `coats: [1, 1]`, `colour` equal to `expected` (`'#efe6cf'`). Screenshot `t9-S23`: pale outlines along the edges of the Grand Gallery and the Queen's Chamber. Then `viewer.player.gotoId('S24'); check.coats()`: expected `[0, 0]` (the coat belongs to S23 alone).

6. The reading swap keeps the labels:

```js
viewer.player.gotoId('S16');
viewer.store.set({ reading: 'alternative' });
```

Take a screenshot, wait 2 s, take another (the new model loads and the next frame rebuilds the actors on it), then:

```js
const swapped = [...check.expected('S16').values()].every(text => viewer.state().labels.includes(text));
viewer.store.set({ reading: 'survey' });
swapped;
```

Expected: `true`.

7. Read the console with `read_console_messages` (`onlyErrors: true`): no error from the page (the tool's own "probe-console-reader" entry does not count).

- [ ] **Step 5: Commit**

```bash
git add viewer/render/actors.js viewer/style.css
git commit -F - <<'EOF'
Show the chemistry in the scene: species labels, liquids and hazes in their species' colours, hatched claimed products, the S23 coat

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
```

Expected: one commit with the two files.

### Task 10: Finish: WebGL 2 check, quality probe, reduced motion, cleanup, README, full check

**Files:**
- Modify: `viewer/app.js` (the finished file: WebGL 2 check, quality probe and storage, reduced-motion listener)
- Delete: `viewer/main.js`, `viewer/scene.js`, `viewer/timeline.js`, `viewer/panel.js`
- Modify: `README.md` (the Viewer bullet of "How it is built" and the Viewer section)
- Test: browser checks at 1280 × 800 and 375 × 812; `uv run pytest -q -W error`

**Interfaces:**
- Consumes: the layout Tasks 3 to 8 gave `viewer/app.js` (everything inside `async function boot()`, `const url = readUrl(location)` first, blocks marked `// ---- <name> (Task N)`, `window.viewer` created by Task 3 and extended with `Object.assign`, `stateParts` merged by `state()`, and the last section `// ---- start (Task 4)` with `frame(dt)`, Task 7's ride and player, Task 8's HUD, `rendererApi.start(frame)`, `player.gotoId(url.stepId)` and the `hashchange` listener); `readUrl` (with `quality` and `nowebgl`), `createStore`, `DEFAULT_STATE`, `loadData` (Task 3); `TIERS`, `createRenderer` with `measure(seconds)` (resolves the median frame time in ms, or `NaN` when no frame was drawn), `lastDt`, `camera`, `controls`, `scene`, `start` (Task 4); `createEnvironment` with `mix` and `update` (Task 4); `createMaterials`, `loadModel`, `frameModel` (Task 5); `createActors` (Tasks 6 and 9); `createRide` (Task 7); `createPlayer` with `gotoId`, `goto`, `seek`, `play`, `pause`, `tick`, `state` (Task 7); `mountCinematic` with `.overlay`, `.hud-card`, `.caption` and the `keydown` handler on `window` (Task 8).
- Produces: the finished `viewer/app.js`; `window.viewer = { store, claims, cycle, manifest, state, rendererApi, environment, model, actors, player, ride, camera }` (the twelve keys the header lists; the extra ones exist for the browser checks); the localStorage key `viewer.quality`, written only when a tier is set after boot. V2 builds on these.

- [ ] **Step 1: Run the failing browser checks**

With the server running (`preview_start`, `name: "viewer"`) and the viewport at 1280 × 800 (`resize_window`), navigate to `http://localhost:8765/?nowebgl=1&v=10a`, take a screenshot, wait 2 s, and run:

```js
({
  message: document.getElementById('message').textContent,
  hidden: document.getElementById('message').hidden,
  canvas: document.querySelector('#stage canvas') !== null,
  viewer: typeof window.viewer,
});
```

Expected now (Task 3 parses `nowebgl` but nothing acts on it): `hidden: true`, `canvas: true`, `viewer: 'object'`. Then navigate to `http://localhost:8765/?quality=low&v=10b`, take a screenshot, and run:

```js
localStorage.removeItem('viewer.quality');
viewer.store.set({ quality: 'medium' });
localStorage.getItem('viewer.quality');
```

Expected now: `null` (nothing saves a chosen tier yet). Run `viewer.store.set({ quality: 'low' })` afterwards. This is the failing state.

- [ ] **Step 2: Write the finished `viewer/app.js`**

Replace the file with this content. It is the file as Tasks 3 to 8 left it (every one of their lines unchanged, `frame(dt)` included), with exactly these additions of this task and nothing else changed:

- after the imports, the comment and the three constants `PROBE_SECONDS`, `FAST_MS`, `SLOW_MS`;
- directly below the store block, the block `// ---- reduced motion and a chosen tier (Task 10)`: the `change` listener of the reduced-motion media query, and the store subscriber that saves a tier set after boot to localStorage `viewer.quality` in a try block (the key `storedQuality` already reads);
- directly below that, the block `// ---- WebGL 2 (Task 10, Review Focus 1)`, above the `window.viewer` block, so a page without WebGL 2 builds nothing and defines no `window.viewer`;
- directly below the line `rendererApi.start(frame);`, the block `// ---- Task 10: the quality probe`, above Task 7's `player.gotoId(url.stepId);`.

Read the current file first: if it holds a line that is not here (a reviewer's fix after this plan was written), keep that line in the same place and name it in the report.

```js
// Boot: read the URL, load the data, create the store and the scene, start the loop.
// Each task adds its block above "start", in the boot order of the plan header.
import { DEFAULT_STATE, createStore, readUrl } from './store.js';
import { loadData } from './data/load.js';
import { createRenderer, TIERS } from './render/renderer.js';
import { createEnvironment } from './render/environment.js';
import { createMaterials } from './render/materials.js';
import { frameModel, loadModel } from './render/model.js';
import { createActors } from './render/actors.js';
import { createRide } from './tour/camera.js';
import { createPlayer } from './tour/player.js';
import { mountCinematic } from './hud/cinematic.js';

// The quality probe of spec section 4.5 (Task 10): the median frame time over two seconds at the starting tier.
const PROBE_SECONDS = 2;   // display choice
const FAST_MS = 10;        // display choice: a median under this moves to high
const SLOW_MS = 25;        // display choice: a median over this moves to low

const message = document.getElementById('message');

// Say what stopped the page, under the notice.
function fail(text) {
  message.textContent = text;
  message.hidden = false;
}

// The tier an earlier visit saved, or null (localStorage is a per-viewer convenience and may be blocked).
function storedQuality() {
  try {
    const value = localStorage.getItem('viewer.quality');
    return ['low', 'medium', 'high'].includes(value) ? value : null;
  } catch {
    return null;
  }
}

async function boot() {
  const url = readUrl(location);

  // ---- data (Task 3)
  let data;
  try {
    data = await loadData();
  } catch (error) {
    fail(error.message);
    return;
  }
  const { claims, cycle, manifest } = data;
  document.getElementById('notice').textContent = cycle.notice;

  // ---- store (Task 3)
  const fixedQuality = url.quality ?? storedQuality();   // null: nothing asked for a tier, so the probe may choose
  const store = createStore({
    ...DEFAULT_STATE,
    mode: url.mode,
    quality: fixedQuality ?? DEFAULT_STATE.quality,
    reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
  });

  // ---- reduced motion and a chosen tier (Task 10)
  // The system setting can change while the page is open; the ride and the environment read the store key.
  matchMedia('(prefers-reduced-motion: reduce)')
    .addEventListener('change', event => store.set({ reducedMotion: event.matches }));
  // A tier set after boot (store.set({quality}) from the console now, the inspector's control in V2) is
  // remembered. The probe's choice is not, so a machine is measured afresh on its next visit.
  let probing = false;
  let chosen = false;
  store.subscribe((next, previous, changed) => {
    if (!changed.has('quality') || probing) return;
    chosen = true;
    try {
      localStorage.setItem('viewer.quality', next.quality);
    } catch {
      // storage blocked: the choice lasts until the page is closed
    }
  });

  // ---- WebGL 2 (Task 10, Review Focus 1): without it, one sentence under the notice and nothing else
  if (url.nowebgl || !document.createElement('canvas').getContext('webgl2')) {
    fail('This page needs WebGL 2.');
    return;
  }

  // ---- window.viewer (Task 3): later tasks add objects with Object.assign and state() parts with stateParts.push
  const stateParts = [() => {
    const { mode, quality, interior, weather, riding } = store.get();
    return { mode, quality, interior, weather, riding };
  }];
  const state = () => Object.assign({}, ...stateParts.map(part => part()));
  window.viewer = { store, claims, cycle, manifest, state };

  // ---- renderer and environment (Task 4)
  const rendererApi = createRenderer(document.getElementById('stage'), store);
  const environment = createEnvironment(rendererApi.scene, rendererApi, store);
  stateParts.push(() => ({ lastDt: rendererApi.lastDt }));
  Object.assign(window.viewer, { rendererApi, environment });

  // ---- materials and model (Task 5)
  const materials = createMaterials();
  const model = await loadModel('data/interior.glb', rendererApi.scene, materials, store);
  frameModel(model, rendererApi.camera, rendererApi.controls);
  Object.assign(window.viewer, { model });

  // ---- actors (Task 6): Task 7's player builds and updates them; until then the console drives them
  const actors = createActors({ scene: rendererApi.scene, model, materials, store, cycle, tiers: TIERS });
  stateParts.push(actors.state);
  Object.assign(window.viewer, { actors });

  // ---- start (Task 4): stays the last block, so everything frame() reads exists before the first frame
  function frame(dt) {
    environment.update(dt, model.bounds.containsPoint(rendererApi.camera.position));
    materials.update(dt);
    model.setInterior(environment.mix.interior);
    player.tick(dt);   // the clock; it updates the actors and the ride
  }
  // ---- Task 7: the camera ride and the cycle clock
  const ride = createRide(rendererApi.camera, rendererApi.controls, store);
  const player = createPlayer({ store, cycle, actors, ride, claims });   // enters the prologue and sets the hash to '#'
  Object.assign(window.viewer, { player, ride, camera: rendererApi.camera });
  stateParts.push(player.state);

  // ---- Task 8: the cinematic HUD
  mountCinematic(document.getElementById('hud'), { store, cycle, claims, player, ride });

  rendererApi.start(frame);
  // ---- Task 10: the quality probe. Not awaited: a deep link opens at once. A hidden page draws no frames, so
  // measure() then resolves NaN, and the tier stays as it is (as it does when the visitor chose one meanwhile).
  if (fixedQuality === null) {
    rendererApi.measure(PROBE_SECONDS).then(median => {
      if (chosen || !Number.isFinite(median)) return;
      probing = true;
      store.set({ quality: median < FAST_MS ? 'high' : median > SLOW_MS ? 'low' : 'medium' });
      probing = false;
    });
  }
  player.gotoId(url.stepId);   // url was read first at boot, before the player rewrote the hash
  window.addEventListener('hashchange', () => player.gotoId(readUrl(location).stepId));
}

boot().catch(error => {
  fail(error.message);
  console.error(error);
});
```

- [ ] **Step 3: Run the browser checks of the three additions**

`python3 -m http.server` sends no cache headers and a page query does not change the URLs of the modules a page imports, so first run, in the page Step 1 opened, `await fetch('app.js', { cache: 'reload' });`. Each check then starts from a fresh navigation (the new `v` value marks the load; it does not refetch modules). Take a screenshot before any wait: the pane draws frames only while it is visible.

1. WebGL 2 missing (Review Focus 1). Navigate to `http://localhost:8765/?nowebgl=1&v=10c`, take a screenshot, wait 2 s, and run:

```js
({
  message: document.getElementById('message').textContent,
  hidden: document.getElementById('message').hidden,
  canvas: document.querySelector('#stage canvas') !== null,
  viewer: typeof window.viewer,
  first: document.body.firstElementChild.id,
  notice: document.getElementById('notice').textContent,
});
```

Expected: `{ message: 'This page needs WebGL 2.', hidden: false, canvas: false, viewer: 'undefined', first: 'notice', notice: 'Animation of the claim. Not a simulation result.' }`. Screenshot `t10-nowebgl`: the notice on top and the sentence under it, nothing else. `read_console_messages` (`onlyErrors: true`): no error from the page.

2. A tier from the URL is used and not saved. Navigate to `http://localhost:8765/?quality=low&v=10d`, take a screenshot, and run `localStorage.removeItem('viewer.quality'); viewer.state().quality`: expected `'low'`. Take a screenshot, wait 3 s, take another, and run `({ quality: viewer.state().quality, saved: localStorage.getItem('viewer.quality') })`: expected `{ quality: 'low', saved: null }` (the URL fixed the tier, so no probe ran and nothing was saved).

3. The probe decides when nothing fixed the tier, and its choice is not saved. With storage still empty, navigate to `http://localhost:8765/?v=10e`, take a screenshot, wait 3 s, take another, and run `({ quality: viewer.state().quality, saved: localStorage.getItem('viewer.quality') })`: expected `quality` one of `'low'`, `'medium'`, `'high'` and `saved: null`. Record the tier in the report (the probe times frame intervals, so a 60 Hz display reads about 16.7 ms and stays at `medium`; a 120 Hz display reads about 8.3 ms and moves to `high`).

4. A tier set after boot is saved and fixes the next visit. On the same page run `viewer.store.set({ quality: 'high' }); localStorage.getItem('viewer.quality')`: expected `'high'`. Navigate to `http://localhost:8765/?v=10f`, take a screenshot, wait 3 s, take another, and run `viewer.state().quality`: expected `'high'` (storage fixed it; no probe). Then run `localStorage.removeItem('viewer.quality')` to leave the browser clean.

5. Reduced motion. The Browser pane cannot emulate the `prefers-reduced-motion` media query, so this check sets the store key that `app.js` derives from it; the ride (Task 7) and the environment (Task 4) read only that key. Navigate to `http://localhost:8765/?quality=low&v=10g`, take a screenshot, and run:

```js
viewer.store.get().reducedMotion === matchMedia('(prefers-reduced-motion: reduce)').matches;
```

Expected: `true` (the store follows the media query). Then find the first step change from an exterior step to an interior one, and open the exterior step:

```js
window.check = { cycle: await fetch('data/cycle.json').then(r => r.json()) };
check.steps = check.cycle.steps;
check.i = check.steps.findIndex((s, i) => i > 0 && s.scene.interior && !check.steps[i - 1].scene.interior);
viewer.player.goto(check.i - 1);
({ exterior: check.steps[check.i - 1].id, interior: check.steps[check.i].id, id: viewer.state().id });
```

Expected: `{ exterior: 'S02', interior: 'S03', id: 'S02' }` with the data as committed (the check reads the pair from `cycle.json`). Take a screenshot, wait 2 s (the look settles on the exterior one), and run, with reduced motion on, a played step change into the interior step:

```js
await (async () => {
  const nextFrame = () => new Promise(r => { requestAnimationFrame(r); setTimeout(r, 200); });   // a frame, or 200 ms if the pane is hidden
  viewer.player.goto(check.i - 1);
  viewer.store.set({ reducedMotion: true });
  viewer.player.seek(viewer.state().t + 0.9 * check.steps[check.i - 1].duration);   // near the end of the exterior step
  viewer.player.play();   // the clock runs on into the interior step
  for (let k = 0; k < 120 && viewer.state().id !== check.steps[check.i].id; k++) await nextFrame();
  check.a = viewer.camera.position.toArray();
  await nextFrame();
  await nextFrame();   // two more frames of the loop
  viewer.player.pause();
  const first = check.steps[check.i].path[0].position;
  return {
    id: viewer.state().id,
    mix: viewer.environment.mix.interior,
    atFirst: check.a.every((v, i) => Math.abs(v - first[i]) < 1e-3),   // a millimetre: the orbit damping may still settle
  };
})()
```

Expected: `{ id: 'S03', mix: 1, atFirst: true }` (the interior step of the pair): while playing, the step change cut the camera to the step's first keyframe instead of flying from the exterior pose, and two frames after it the look is already the interior one (without the flag two frames move `mix.interior` by at most 2 × 0.1 / `FADE_SECONDS`, about 0.13). If `id` is still the exterior step, the pane was hidden: bring it to the front and run the block again (it reopens the exterior step first). Then, still paused, move later into the same step:

```js
viewer.player.seek(viewer.state().t + 0.8 * check.steps[check.i].duration);
```

Take a screenshot, wait 1 s, take another, and run:

```js
const b = viewer.camera.position.toArray();
const result = {
  id: viewer.state().id,
  u: viewer.state().u,
  still: check.a.every((v, i) => Math.abs(v - b[i]) < 1e-3),   // a flown camera would be metres away
};
viewer.store.set({ reducedMotion: false });
result;
```

Expected: `id: 'S03'`, `u` above `0.8`, `still: true` (the ride left the camera on the first keyframe; without the flag the seek puts it on the step's path at that `u`, so the positions would differ).

6. `read_console_messages` (`onlyErrors: true`): no error from the page.

- [ ] **Step 4: Delete the plan A modules**

```bash
git rm viewer/main.js viewer/scene.js viewer/timeline.js viewer/panel.js
```

Expected: four `rm 'viewer/...'` lines.

- [ ] **Step 5: Check that nothing refers to them**

```bash
grep -rnE "\b(main|scene|timeline|panel)\.js\b" viewer ledger pyramid tests README.md
```

Expected: no output. Plan A's header comment of `ledger/cycle.yaml` named `viewer/scene.js`; Task 2's script wrote a new header that says "the viewer" instead, and Task 9 dropped the one mention of `timeline.js` in a new module's comment. If a line is printed anyway, it is a comment naming a deleted file: reword it to say what the code or the viewer does, without the file name, run the grep again (expected: no output), and add that file to Step 11's `git add`. A comment edit in `ledger/cycle.yaml` needs no regeneration: the ledger digest covers `parameters.yaml` and `claims.yaml` only (`pyramid/ledger.py`, `load`), and `cycle.json` does not carry comments.

- [ ] **Step 6: Rewrite the viewer's descriptions in `README.md`**

Two replacements: the Viewer bullet of "How it is built" and the paragraph of the Viewer section. Both describe plan A's click-a-space viewer today.

First, in the section "How it is built", replace this line (the Viewer bullet):

```markdown
- **Viewer** ([`viewer/`](viewer/)): a browser scene that animates the cycle exactly as claimed, step by step, with the verdict and the deciding numbers beside each step. Mechanisms the hypothesis leaves unspecified are drawn as dashed, labelled placeholders. A fixed notice reads: *Animation of the claim. Not a simulation result.*
```

with:

```markdown
- **Viewer** ([`viewer/`](viewer/)): a full-screen three.js scene that tours the 31 steps of the cycle exactly as claimed, with each step's claim, verdict and deciding sentence in a caption, and the compounds the hypothesis names labelled in the spaces it puts them in; products of steps that fail or are undefined are marked *claimed*. Mechanisms the hypothesis leaves unspecified are drawn as dashed, labelled placeholders. The inspector, with the deciding numbers of each step and space, comes with the next plan. A fixed notice reads: *Animation of the claim. Not a simulation result.*
```

Then replace this paragraph of the Viewer section (the heading and the server command above it stay):

```markdown
Then open http://localhost:8765/. Step through the 31 claimed steps, switch between the survey reading and an alternative, click any space for the ledger values that define it (unverified values are marked), and read the verdict for the step. It is an animation of the claim, not a simulation result.
```

with:

```markdown
Then open http://localhost:8765/. three.js 0.170.0 loads from the jsDelivr CDN, so the page needs a network connection and a browser with WebGL 2; nothing is installed.

The page is one full-screen scene. From outside, the pyramid stands on a plain sand plateau under a sky. On the steps that act inside the stone, the masonry turns to dark glass and the passages and chambers show through it as a lit schematic; the plateau fades only while the camera is inside the masonry. *Play the claimed cycle* flies in from far outside, then rides a camera path through each of the 31 claimed steps: water rises and falls in the spaces the claim names, gases light up the chambers they pass through, and a storm sky appears only on the two steps whose claim states a storm (S05 and S06), with the lightning strike on the top in S06. The water and gases in each space carry the formulas of the compounds the hypothesis names for them and take those compounds' colours; a product of a step whose verdict is fail or undefined is drawn hatched and labelled *(claimed)*, and the calcium sulfate coat of S23 is outlined. Mechanisms the hypothesis leaves unspecified (the pump, the valves, the reservoir, the drains) are dashed, labelled boxes. A caption gives each step's claim as stated, its verdict and the sentence that decides it, above a strip of 31 ticks coloured by verdict. A fixed notice reads: *Animation of the claim. Not a simulation result.*

| Input | Action |
|---|---|
| Space | play or pause |
| Left, Right | previous or next step |
| drag on the strip | scrub |
| F | fullscreen |
| H | hide or show the caption and controls (the notice stays) |
| Esc | back to the cinematic view |
| I | the inspector (next plan; does nothing yet) |
| pointer on the scene | orbit; this pauses the ride, and *Resume ride* rejoins it |

Deep links: `#S16` opens that step; any other fragment opens the prologue. `?quality=low`, `?quality=medium` or `?quality=high` fixes the rendering tier (pixel ratio, shadows, bloom, gas particles); without it the page times two seconds of frames and picks one. A tier set from the browser console with `viewer.store.set({quality: 'high'})` is remembered in that browser. With the system setting for reduced motion, steps cut instead of flying. `viewer.state()` in the console summarises what the scene shows.

The inspector (step and space cards with the deciding numbers, layers, a cutaway, the chemistry legend and the reaction equations), Results mode for the process model's output, and a public URL come with the next plan ([design](docs/superpowers/specs/2026-10-10-cinematic-viewer-design.md)).
```

- [ ] **Step 7: Check the size budget**

```bash
find viewer -name '*.js' -print0 | xargs -0 cat | wc -c
```

Expected: one number below `150000`: the bytes of every JavaScript file left under `viewer/` after Step 4's deletions, `viewer/data/load.js` and the subfolders included. Record it in the report.

- [ ] **Step 8: Full browser check list at 1280 × 800**

`resize_window` with `width: 1280, height: 800`; navigate to `http://localhost:8765/?quality=low&v=10h`; take a screenshot; define the check helper:

```js
for (let i = 0; i < 100 && !window.viewer?.player; i++) await new Promise(r => setTimeout(r, 100));   // the model loads first
window.check = {
  cycle: await fetch('data/cycle.json').then(r => r.json()),
  step(id) { return this.cycle.steps.find(s => s.id === id); },
  at(id, u) {   // open a step and move to the fraction u of it
    viewer.player.gotoId(id);
    viewer.player.seek(viewer.state().t + u * this.step(id).duration);
    return viewer.state().id;
  },
  bolt() {   // is a lightning stroke drawn now
    let scene = viewer.model.root;
    while (scene.parent) scene = scene.parent;
    let on = false;
    scene.traverse(o => { if (o.isLine2 && o.visible) on = true; });
    return on;
  },
  shown(selector) {   // is an element of the HUD laid out on the page
    const element = document.querySelector(selector);
    return !!element && element.getClientRects().length > 0;
  },
};
```

Then, in order, each check as a JavaScript call, a screenshot with the given name, and a reading call after it:

1. Prologue, no autoplay. Run `({ id: viewer.state().id, playing: viewer.state().playing, overlay: check.shown('.overlay button'), text: document.querySelector('.overlay button')?.textContent, hash: location.hash })`. Expected: `{ id: 'prologue', playing: false, overlay: true, text: 'Play the claimed cycle', hash: '' }`. Screenshot `t10-1280-01-prologue`: the pyramid far off on the plateau under a clear sky, the notice on top, the button.

2. Play. Run `document.querySelector('.overlay button').click()`. Screenshot `t10-1280-02-play`, wait 1 s, and run `({ playing: viewer.state().playing, overlay: check.shown('.overlay button') })`: expected `{ playing: true, overlay: false }`. Take a screenshot, wait `check.cycle.prologue.duration` seconds plus 2 (8 s for 6.0), take another, and run:

```js
(() => {
  const s = viewer.state();
  let k = 0;
  let end = check.cycle.prologue.duration + check.cycle.steps[0].duration;
  while (s.t >= end) end += check.cycle.steps[++k].duration;   // the step the clock is in, from cycle.json
  return { id: s.id, atT: check.cycle.steps[k].id, past: s.t > check.cycle.prologue.duration, playing: s.playing };
})()
```

Expected: `past: true`, `playing: true`, `id` equal to `atT`: `'S01'` when the read comes within S01's 5 s, `'S02'` if the tool calls took longer (the clock ran on through the prologue into the steps). Run `viewer.player.pause()`.

3. Cross-fade on the first interior step. Run:

```js
check.first = check.cycle.steps.findIndex(s => s.scene.interior);
viewer.player.goto(check.first - 1);
({ first: check.cycle.steps[check.first].id, before: check.cycle.steps[check.first - 1].scene.interior });
```

Expected: `before: false`, and `first` the id of the first interior step (`'S03'` with the data as committed; the check reads it from `cycle.json`). Take a screenshot, wait 2 s, run `viewer.environment.mix.interior` (expected `0`), then take a screenshot and immediately run:

```js
viewer.player.goto(check.first);
await new Promise(resolve => {
  const samples = [];
  const start = performance.now();
  (function sample() {
    samples.push(+viewer.environment.mix.interior.toFixed(3));
    if (performance.now() - start < 2500) requestAnimationFrame(sample);
    else resolve({
      id: viewer.state().id, first: samples[0], last: samples.at(-1),
      between: samples.some(k => k > 0.05 && k < 0.95),
      rising: samples.every((k, j) => j === 0 || k >= samples[j - 1]),
    });
  })();
});
```

Expected: `id` the first interior step, `first` below `0.2`, `last: 1`, `between: true` (a fade, not a cut), `rising: true`. Screenshot `t10-1280-03-crossfade`: the masonry as dark glass with the spaces lit inside, the ground gone.

4. Water, S12. Run `check.at('S12', 0.5)`, take a screenshot, wait 2 s (S12 is an interior step, so the look stays the glass one check 3 brought), and take screenshot `t10-1280-04-S12`; then:

```js
const s = viewer.state();
const actor = check.step('S12').actors.find(a => a.type === 'water' && a.space === 'grand_gallery');
({ id: s.id, water: s.water.grand_gallery, expected: actor.from + (actor.to - actor.from) * s.u,
   level: s.levels.grand_gallery, interior: s.interior, flag: check.step('S12').scene.interior });
```

Expected: `id: 'S12'`, `water` within `0.01` of `expected` (0.625 at u 0.5), `level` a finite number, `interior: true` and `flag: true`. `t10-1280-04-S12`: the masonry is dark glass and the Grand Gallery holds blue water to the level of `level`, with a brighter line at its waterline; S12's dashed placeholder cubes stand with their labels. While the camera stands outside `model.bounds` the sand plain stays and hides the spaces below the pavement; the Gallery stands above it.

5. Gas, S16. Run `check.at('S16', 0.5)`; screenshot `t10-1280-05-S16` (the King's Chamber and antechamber hazes, the antechamber's striped); then run `({ id: viewer.state().id, claimed: viewer.state().labels.some(t => t.endsWith('SO₃ (claimed)')), drain: viewer.state().labels.includes('Gallery drain: not specified by the hypothesis') })`: expected `{ id: 'S16', claimed: true, drain: true }`.

6. Storm and bolt, S06. Run `check.at('S06', 0.2)`, take a screenshot, wait 2 s (the storm fades in; S06 is an interior step filmed from outside, so the masonry turns to glass and the plateau stays), and take screenshot `t10-1280-06-S06-u020`; run `({ weather: viewer.state().weather, u: viewer.state().u, bolt: check.bolt() })`: expected `{ weather: 'storm', u: 0.2, bolt: false }`. Run `check.at('S06', 0.35)`; screenshot `t10-1280-07-S06-u035` (the dark storm sky and the bolt from the apex); run `({ u: viewer.state().u, bolt: check.bolt() })`: expected `{ u: 0.35, bolt: true }`. Then `check.at('S07', 0)` and `viewer.state().weather`: expected `'clear'` (only S05 and S06 carry the storm).

7. Hatching, S20. Run `check.at('S20', 0.5)`; screenshot `t10-1280-08-S20` (the Gallery liquid in the acid colour with diagonal stripes); run `viewer.state().labels.some(t => t.includes('H₂SO₄ (claimed)'))`: expected `true`.

8. The low tier. Run `viewer.state().quality`: expected `'low'`.

9. `read_console_messages` (`onlyErrors: true`): no error from the page during the whole list.

10. WebGL 2 missing: navigate to `http://localhost:8765/?nowebgl=1&v=10i`, take a screenshot, wait 2 s, and run `[document.getElementById('message').hidden, document.getElementById('message').textContent]`: expected `[false, 'This page needs WebGL 2.']`. Screenshot `t10-1280-09-nowebgl`.

- [ ] **Step 9: Full browser check list at 375 × 812**

`resize_window` with `preset: "mobile"` (375 × 812, a touch phone), then navigate to `http://localhost:8765/?quality=low&v=10j` (a fresh load, so the page sees the phone width from the start). Take a screenshot, define `window.check` with the block of Step 8, and run checks 1 to 10 of Step 8 exactly as written, naming the screenshots `t10-375-01-prologue` to `t10-375-09-nowebgl`. Before check 10 (which navigates away), run these phone checks (Review Focus 5):

1. During the ride. Run `check.at('S16', 0.1); viewer.player.play()`, take a screenshot, wait 2 s, take screenshot `t10-375-10-ride`, and run:

```js
const card = document.querySelector('#hud .hud-card').getBoundingClientRect();
const caption = document.querySelector('#hud .caption');
const notice = document.getElementById('notice').getBoundingClientRect();
const canvas = document.querySelector('#stage canvas').getBoundingClientRect();
viewer.player.pause();
({
  innerWidth,
  scrollWidth: document.documentElement.scrollWidth,
  card: [card.left, card.right],
  captionFits: caption.scrollWidth <= caption.clientWidth,
  notice: [notice.top, notice.height],
  onTop: !!document.elementFromPoint(innerWidth / 2, 14)?.closest('#notice'),
  canvas: canvas.width,
});
```

Expected: `innerWidth: 375`, `scrollWidth` at most `375` (no horizontal scroll), `card[0]` at least `0` and `card[1]` at most `375` (the caption card lies inside the width), `captionFits: true` (the caption wraps instead of overflowing), `notice: [0, 28]`, `onTop: true` (the notice is the topmost element at the top of the page), `canvas: 375`. In `t10-375-10-ride` the caption text is readable, wraps, and nothing is cut at the right edge.

2. The HUD hidden. Run `window.dispatchEvent(new KeyboardEvent('keydown', { key: 'h' }))` (Task 8's keyboard handler listens on `window`), then run `({ hud: document.getElementById('hud').classList.contains('hidden'), notice: document.getElementById('notice').getBoundingClientRect().height })`: expected `{ hud: true, notice: 28 }`. Screenshot `t10-375-11-hud-hidden`: the scene and the notice only. Run `window.dispatchEvent(new KeyboardEvent('keydown', { key: 'h' }))` again to show the HUD.

Afterwards run `resize_window` with `preset: "desktop"` to leave the pane at its own size.

- [ ] **Step 10: Run the Python tests**

```bash
uv run pytest -q -W error
```

Expected: `293 passed, 1 xfailed`, no warnings: the count Task 2 left (Tasks 3 to 10 change no Python and no data).

- [ ] **Step 11: Commit**

```bash
git add viewer/app.js README.md
git status --short
```

Expected status: `D  viewer/main.js`, `D  viewer/panel.js`, `D  viewer/scene.js`, `D  viewer/timeline.js`, `M  README.md`, `M  viewer/app.js` (plus any file Step 5 reworded and added); nothing else staged, nothing unstaged under `viewer/`. Then:

```bash
git commit -F - <<'EOF'
Finish the cinematic viewer: WebGL 2 check, quality probe, reduced motion; remove plan A's viewer modules; README viewer descriptions

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
```

Expected: one commit; `git status --short` afterwards prints nothing for `viewer/`, `README.md` and `ledger/`.
