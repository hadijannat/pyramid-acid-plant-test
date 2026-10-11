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
