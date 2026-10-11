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
  mountCinematic(document.getElementById('hud'), { store, cycle, claims, player, ride });

  rendererApi.start(frame);
  player.gotoId(url.stepId);   // url was read first at boot, before the player rewrote the hash
  window.addEventListener('hashchange', () => player.gotoId(readUrl(location).stepId));
}

boot().catch(error => {
  fail(error.message);
  console.error(error);
});
