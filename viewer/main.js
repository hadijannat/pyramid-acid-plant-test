// Boot: fetch the data, create the scene, wire the toolbar.
import { createScene } from './scene.js';

async function getJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
  return response.json();
}

const [claims, cycle] = await Promise.all([getJSON('data/claims.json'), getJSON('data/cycle.json')]);
const view = createScene(document.getElementById('stage'));
await view.load('data/interior.glb');
view.frame();

// Toolbar: masonry on or off, the two readings of the survey, one checkbox per space.
function onToggle(id, apply) {
  const button = document.getElementById(id);
  button.addEventListener('click', () => {
    const on = button.getAttribute('aria-pressed') !== 'true';
    button.setAttribute('aria-pressed', String(on));
    apply(on);
  });
}
onToggle('toggle-masonry', on => { view.setVisible('masonry', on); view.setVisible('bedrock', on); });
onToggle('toggle-geometry', alternative => view.load(alternative ? 'data/interior_alt.glb' : 'data/interior.glb'));

const toggles = document.getElementById('space-toggles');
for (const name of view.spaces.keys()) {
  const box = Object.assign(document.createElement('input'), { type: 'checkbox', checked: true });
  box.addEventListener('change', () => view.setVisible(name, box.checked));
  const label = document.createElement('label');
  label.append(box, ' ', claims.spaces[name].label);
  toggles.append(label);
}

const picked = document.getElementById('picked');
view.onPick = name => { picked.textContent = name ? `${claims.spaces[name].label} (${name})` : ''; };

window.viewer = { view, claims, cycle };   // for checks from the browser console
