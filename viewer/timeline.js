// Cycle player: play, pause, step and scrub; one camera tween per step; and the actors of each step.
import * as THREE from 'three';
import { CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';

// Display choices, not physical quantities.
const WATER_COLOUR = 0x2f86d6;
const TWEEN_SECONDS = 1;
const FAR = 1e6;   // a height far above (or, negated, far below) anything in the model
// A placeholder is a 4 m dashed cube: a symbol whose size says nothing about what it stands for.
const DASHED_BOX = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(4, 4, 4)))
  .computeLineDistances().geometry;
// Lightning: [east, up, south] of each vertex as fractions of the masonry height, measured from the apex.
const BOLT = [[0.1, 0.6, -0.06], [0.04, 0.47, 0.02], [0.09, 0.36, -0.03], [0.02, 0.24, 0.05],
  [0.06, 0.14, 0], [-0.01, 0.06, 0.02], [0, 0, 0]];

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

export function createTimeline(view, cycle, bar, { fields, onStep }) {
  const steps = cycle.steps;
  const starts = [];   // starts[i]: seconds from the start of the cycle to the start of step i
  let total = 0;
  for (const step of steps) { starts.push(total); total += step.duration; }

  let t = 0;            // seconds into the cycle
  let u = 0;            // 0 to 1 within the current step
  let index = -1;       // current step; -1 until the first render
  let playing = false;
  let tween = null;     // camera move in progress
  let live = [];        // objects that exist only for the current step
  let updaters = [];    // functions that set the actors to the current u
  const water = new Map();   // space -> { fraction, level } at the current u
  const scratch = new THREE.Vector3();

  // ---- the bar
  const make = (tag, properties) => Object.assign(document.createElement(tag), properties);
  const back = make('button', { type: 'button', textContent: 'Back' });
  const playButton = make('button', { type: 'button', textContent: 'Play' });
  const next = make('button', { type: 'button', textContent: 'Next' });
  const scrub = make('input', { type: 'range', min: 0, max: total, step: 0.05, value: 0 });
  scrub.setAttribute('aria-label', 'Position in the cycle');
  const stepLabel = make('span', { id: 'tl-label' });
  const time = make('span', { id: 'tl-time' });
  bar.replaceChildren(back, playButton, next, scrub, stepLabel, time);
  back.addEventListener('click', () => goto(index - 1));
  next.addEventListener('click', () => goto(index + 1));
  playButton.addEventListener('click', () => (playing ? pause() : play()));
  scrub.addEventListener('input', () => { playing = false; seek(Number(scrub.value)); });

  // ---- actors
  // ponytail: per-step objects are dropped, not disposed; they are a few materials and a
  // seven-vertex line. Dispose them in build() once steps carry field textures (second plan).
  function keep(parent, object) {   // add an object that lives only for the current step
    parent.add(object);
    live.push(object);
    return object;
  }

  // A second skin on a space's mesh. As a child of that mesh it shares its position and its
  // visibility, and the picking in scene.js never sees it.
  function skin(space, colour, opacity, plane, offset) {
    const source = view.spaces.get(space);
    const mesh = new THREE.Mesh(source.geometry, new THREE.MeshStandardMaterial({
      color: colour, transparent: true, opacity, depthWrite: false, side: THREE.DoubleSide, flatShading: true,
      clippingPlanes: [plane], polygonOffset: true, polygonOffsetFactor: offset, polygonOffsetUnits: offset,
    }));
    mesh.renderOrder = 1;   // after the opaque spaces, before the masonry
    return keep(source, mesh);
  }

  function tag(text, className) {
    const element = document.createElement('div');
    element.className = className;
    element.textContent = text;
    return new CSS2DObject(element);
  }

  const actors = {
    water(actor) {
      const plane = new THREE.Plane(new THREE.Vector3(0, -1, 0), 0);   // keeps what lies below y = plane.constant
      const mesh = skin(actor.space, WATER_COLOUR, 0.8, plane, -4);
      const curve = cycle.curves[actor.space];
      updaters.push(() => {
        const fraction = actor.from + (actor.to - actor.from) * u;
        const level = fraction <= 0 ? -FAR : fraction >= 1 ? FAR : levelAt(curve, fraction);
        plane.constant = level;
        mesh.visible = fraction > 0;
        water.set(actor.space, { fraction, level });
      });
    },

    gas(actor) {
      actor.path.forEach((space, k) => {
        const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), FAR);   // keeps what lies above y = -plane.constant
        const mesh = skin(space, actor.color, 0.55, plane, -2);
        updaters.push(() => {
          mesh.visible = u >= k / actor.path.length;               // the path lights up one space after another
          plane.constant = -(water.get(space)?.level ?? -FAR);     // only above any water in the same space
        });
      });
    },

    placeholder(actor) {
      const box = keep(view.scene, new THREE.LineSegments(DASHED_BOX, new THREE.LineDashedMaterial({
        color: 0xd9dde2, dashSize: 0.7, gapSize: 0.5, depthTest: false,
      })));
      box.position.fromArray(actor.at);
      box.renderOrder = 3;   // over everything, so the dashes are never hidden inside the stone
      const label = keep(box, tag(actor.label, 'placeholder-label'));
      label.position.y = 3.2;   // just above the cube
    },

    lightning() {
      const top = new THREE.Box3().setFromObject(view.shell.get('masonry')).max.y;   // the apex, from the model itself
      const points = BOLT.map(([east, up, south]) => new THREE.Vector3(east * top, top * (1 + up), south * top));
      // ponytail: a one-pixel line. Use Line2 from three/addons/lines if it reads too thin.
      const bolt = keep(view.scene, new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(points), new THREE.LineBasicMaterial({ color: 0xfff3b0 }),
      ));
      const flash = keep(view.scene, new THREE.AmbientLight(0xfff3b0, 0));
      updaters.push(() => {
        const on = (u > 0.3 && u < 0.42) || (u > 0.48 && u < 0.56);   // two brief strokes
        bolt.visible = on;
        flash.intensity = on ? 3 : 0;
      });
    },

    field(actor) {
      const box = new THREE.Box3().setFromObject(view.shell.get('masonry'));
      const centre = box.getCenter(new THREE.Vector3());
      if (!fields.includes(actor.slice)) {   // no solver result yet: say so and draw nothing
        keep(view.scene, tag('Solver result pending', 'pending-label')).position.copy(centre);
        return;
      }
      const texture = new THREE.TextureLoader().load('data/' + actor.slice);   // the browser's cache makes a revisit cheap
      texture.colorSpace = THREE.SRGBColorSpace;
      // Until the second plan attaches each slice's extent, a slice is drawn on the north-south
      // vertical section through the axis, as wide and as high as the masonry.
      const size = box.getSize(new THREE.Vector3());
      const slice = keep(view.scene, new THREE.Mesh(new THREE.PlaneGeometry(size.z, size.y), new THREE.MeshBasicMaterial({
        map: texture, transparent: true, opacity: 0.85, side: THREE.DoubleSide, depthWrite: false,
      })));
      slice.rotation.y = Math.PI / 2;
      slice.position.copy(centre);
      slice.renderOrder = 1;
    },
  };

  function build(step) {
    for (const object of live) object.removeFromParent();
    live = [];
    updaters = [];
    water.clear();
    // water first: the gas in a space is clipped to what lies above the water in it
    const ordered = [...step.actors].sort((a, b) => (a.type !== 'water') - (b.type !== 'water'));
    for (const actor of ordered) actors[actor.type](actor);
  }

  // ---- time
  function render() {
    let i = steps.length - 1;
    while (i > 0 && starts[i] > t) i--;
    u = Math.min(1, (t - starts[i]) / steps[i].duration);
    if (i !== index) {
      index = i;
      build(steps[i]);
      tween = { position: view.camera.position.clone(), target: view.controls.target.clone(), k: 0 };
      onStep(steps[i].id);
    }
    for (const update of updaters) update();
    scrub.value = t;
    playButton.textContent = playing ? 'Pause' : 'Play';
    stepLabel.textContent = `${steps[i].id} ${steps[i].title}`;
    time.textContent = `${t.toFixed(1)} / ${total.toFixed(1)} s`;
  }

  function tick(dt) {
    if (tween) {   // ease the camera from where it was to the step's view; afterwards the user orbits freely
      tween.k = Math.min(1, tween.k + dt / TWEEN_SECONDS);
      const eased = tween.k * tween.k * (3 - 2 * tween.k);
      const { position, target } = steps[index].camera;
      view.camera.position.lerpVectors(tween.position, scratch.fromArray(position), eased);
      view.controls.target.lerpVectors(tween.target, scratch.fromArray(target), eased);
      if (tween.k === 1) tween = null;
    }
    if (playing) {
      t = Math.min(total, t + dt);
      if (t === total) playing = false;
      render();
    }
  }

  function seek(seconds) {
    t = Math.max(0, Math.min(total, seconds));
    render();
  }

  function goto(i) {
    if (i >= 0 && i < steps.length) seek(starts[i]);
  }

  function at(id, fraction) {
    const i = steps.findIndex(step => step.id === id);
    if (i < 0) return false;
    seek(starts[i] + Math.min(fraction, 0.999) * steps[i].duration);   // 1 would already be the next step
    return true;
  }

  function play() {
    if (t >= total) t = 0;
    playing = true;
    render();
  }

  function pause() {
    playing = false;
    render();
  }

  function rebuild() {
    index = -1;
    render();
  }

  const state = () => ({
    id: steps[index].id,
    u: +u.toFixed(3),
    playing,
    water: Object.fromEntries([...water].map(([space, w]) => [space, +w.fraction.toFixed(2)])),
    levels: Object.fromEntries([...water].map(([space, w]) => [space, +w.level.toFixed(2)])),
    labels: live.filter(object => object.isCSS2DObject).map(object => object.element.textContent),
  });

  render();
  return { play, pause, seek, goto, gotoId: id => at(id, 0), at, rebuild, tick, state };
}
