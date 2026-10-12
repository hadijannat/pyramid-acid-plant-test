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
const CANDIDATES = 20;       // display choice: random points tried per particle asked for, at most
const PARTICLE_SIZE = 0.15;  // display choice: metres
const SWAY = 0.25;           // display choice: radians per second of each particle's slow sway
const CHORD = 0.15;          // display choice: a particle sways over this fraction of a chord of its space
// The marking rule in the scene (spec section 6.3): this text follows the formula of a species whose status in
// cycle.json is "claimed"; the "conditional" tag belongs to the inspector's legend (plan V2), not to the scene.
const CLAIMED = ' (claimed)';
const COAT_SPECIES = 'calcium_sulfate';   // the coat of S23 is its calcium sulfate layer (chemistry spec 3.2)
const COAT_OPACITY = 0.25;   // display choice: a faint film of the coat's colour over the coated walls

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

// The triangles of a space's mesh (three corners each, in the mesh's own frame) and its bounding box.
function solidOf(geometry) {
  const position = geometry.attributes.position;
  const { index } = geometry;
  const corners = [];
  for (let i = 0; i < (index ? index.count : position.count); i++) {
    corners.push(new THREE.Vector3().fromBufferAttribute(position, index ? index.getX(i) : i));
  }
  if (!geometry.boundingBox) geometry.computeBoundingBox();
  return { corners, box: geometry.boundingBox };
}

// Three fixed oblique directions, so that a ray seldom runs along a face of the axis-aligned rooms.
const RAYS = [[1, 0.31, 0.17], [-0.23, 1, 0.41], [0.37, -0.29, 1]].map(v => new THREE.Vector3(...v).normalize());
const ray = new THREE.Ray();
const hit = new THREE.Vector3();

// How many triangles the ray from origin along direction crosses within length.
function crossings({ corners }, origin, direction, length = Infinity) {
  ray.set(origin, direction);
  let n = 0;
  for (let i = 0; i < corners.length; i += 3) {
    if (ray.intersectTriangle(corners[i], corners[i + 1], corners[i + 2], false, hit) && hit.distanceTo(origin) <= length) n++;
  }
  return n;
}

// Whether a point lies inside a closed mesh: an odd number of crossings along a ray. The majority of the
// three rays decides, so a ray that grazes an edge or a corner does not flip the answer.
// ponytail: every triangle per ray, fine for the spaces' tens to hundreds of triangles; a BVH if a mesh grows.
function inside(solid, point) {
  let odd = 0;
  for (const direction of RAYS) odd += crossings(solid, point, direction) % 2;
  return odd >= 2;
}

// A uniform point of the space's bounding box that lies inside the mesh, or null for a candidate outside it.
function candidate(solid, out) {
  const { min, max } = solid.box;
  out.set(THREE.MathUtils.lerp(min.x, max.x, Math.random()), THREE.MathUtils.lerp(min.y, max.y, Math.random()),
    THREE.MathUtils.lerp(min.z, max.z, Math.random()));
  return inside(solid, out) ? out : null;
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
  // Each particle sways along a short chord from a point inside the mesh, and only where no wall crosses the
  // chord, so it stays inside. Drawn without the depth test: the opaque walls of its space never hide it.
  // ponytail: candidates are drawn in the bounding box, at most CANDIDATES per particle asked for; a thin slanted
  // shaft fills about one percent of its box and gets fewer particles than asked. Sample along the shaft if that shows.
  function cloud(space, haze, plane, count, colour) {
    const solid = solidOf(model.spaces.get(space).geometry);
    const found = [];   // points inside the mesh
    const trial = new THREE.Vector3();
    for (let tries = 0; found.length < count && tries < CANDIDATES * count; tries++) {
      if (candidate(solid, trial)) found.push(trial.clone());
    }
    const from = new Float32Array(found.length * 3);
    const to = new Float32Array(found.length * 3);
    const phase = new Float32Array(found.length);
    const toward = new THREE.Vector3();
    found.forEach((a, i) => {
      const b = found[Math.floor(Math.random() * found.length)].clone().lerp(a, 1 - CHORD);   // most of the way back to a
      const length = a.distanceTo(b);
      if (length > 0 && crossings(solid, a, toward.subVectors(b, a).divideScalar(length), length) > 0) b.copy(a);
      a.toArray(from, 3 * i);
      b.toArray(to, 3 * i);
      phase[i] = Math.random() * 2 * Math.PI;
    });
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(from.slice(), 3));
    const material = new THREE.PointsMaterial({
      color: colour, size: PARTICLE_SIZE, transparent: true, opacity: 0.9, depthWrite: false,   // display choice
      depthTest: false, blending: THREE.NormalBlending, clippingPlanes: [plane],                     // display choice
    });
    const points = keep(haze, new THREE.Points(geometry, material), geometry, material);
    points.frustumCulled = false;   // the particles move; the bounding sphere of their first positions is stale
    points.renderOrder = 2;         // after the hazes (1): the opaque stripes of a claimed haze must not cover them
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

    // The calcium sulfate layer of S23: a faint film and the edges of the coated space, in that species' colour.
    coat(actor) {
      const species = current.species.find(s => s.id === COAT_SPECIES);
      if (!species) throw new Error(`cycle.json: ${current.id}: a coat needs ${COAT_SPECIES} in the step's species`);
      skin(actor.space, new THREE.MeshBasicMaterial({
        color: species.colour, transparent: true, opacity: COAT_OPACITY, depthWrite: false, side: THREE.DoubleSide,
      }), -3);   // between the water's offset and the gas's
      const source = model.spaces.get(actor.space);
      const geometry = new THREE.EdgesGeometry(source.geometry);
      // transparent so it is sorted with the skins: an opaque line is drawn before every transparent skin, whatever its renderOrder
      const material = new THREE.LineBasicMaterial({ color: species.colour, transparent: true });
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

  // One label per space with water, gas or a coat: the species of every such actor there, in build order (water
  // first; a coat's species leads its space's list), each once, "(claimed)" after a claimed one; a child of the
  // space mesh at the centre of its bounds.
  function labelSpecies(ordered) {
    const present = new Map();   // space -> species payloads
    for (const actor of ordered) {
      if (actor.type === 'coat') {
        const list = present.get(actor.space) ?? [];
        if (!list.some(s => s.id === COAT_SPECIES)) list.unshift(current.species.find(s => s.id === COAT_SPECIES));
        present.set(actor.space, list);
      }
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
