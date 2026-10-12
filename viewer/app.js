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

  // ---- actors (Task 6): Task 7's player builds and updates them
  const actors = createActors({ scene: rendererApi.scene, model, materials, store, cycle, tiers: TIERS });
  stateParts.push(actors.state);
  Object.assign(window.viewer, { actors });

  // ---- start (Task 4): stays the last block, so everything frame() reads exists before the first frame
  function frame(dt) {
    environment.update(dt, model.contains(rendererApi.camera.position));
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
  mountCinematic(document.getElementById('hud'), { store, cycle, claims, player, ride, rendererApi });

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
  if (url.t !== null) player.seek(url.t);   // ?t=<seconds>: the tour paused at that moment (how the README's images are made)
  actors.warm();   // the gas clouds of the tour, sampled while the prologue waits, and again if the tier changes
  store.subscribe((state, previous, changed) => { if (changed.has('quality')) actors.warm(); });
  window.addEventListener('hashchange', () => player.gotoId(readUrl(location).stepId));
}

boot().catch(error => {
  fail(error.message);
  console.error(error);
});
