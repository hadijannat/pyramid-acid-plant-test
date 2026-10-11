// Boot: read the URL, load the data, create the store and the scene, start the loop.
// Each task adds its block above "start", in the boot order of the plan header.
import { DEFAULT_STATE, createStore, readUrl } from './store.js';
import { loadData } from './data/load.js';
import { createRenderer } from './render/renderer.js';
import { createEnvironment } from './render/environment.js';
import { createMaterials } from './render/materials.js';
import { frameModel, loadModel } from './render/model.js';

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

  // ---- start (Task 4): stays the last block, so everything frame() reads exists before the first frame
  function frame(dt) {
    environment.update(dt, model.contains(rendererApi.camera.position));
    materials.update(dt);
    model.setInterior(environment.mix.interior);
  }
  rendererApi.start(frame);
}

boot().catch(error => {
  fail(error.message);
  console.error(error);
});
