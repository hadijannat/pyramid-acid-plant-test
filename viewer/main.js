// Boot: fetch the data, create the scene and the timeline, wire the toolbar.
import { createScene } from './scene.js';
import { createTimeline } from './timeline.js';

async function getJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
  return response.json();
}

const [claims, cycle] = await Promise.all([getJSON('data/claims.json'), getJSON('data/cycle.json')]);
const view = createScene(document.getElementById('stage'));
await view.load('data/interior.glb');
view.frame();

const startAt = location.hash.slice(1);   // read it before the timeline starts rewriting the fragment
const timeline = createTimeline(view, cycle, document.getElementById('timeline'), {
  fields: claims.manifest.fields,
  onStep: id => history.replaceState(null, '', '#' + id),
});
view.onFrame = timeline.tick;
timeline.gotoId(startAt);
window.addEventListener('hashchange', () => timeline.gotoId(location.hash.slice(1)));

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
onToggle('toggle-geometry', async alternative => {
  await view.load(alternative ? 'data/interior_alt.glb' : 'data/interior.glb');
  timeline.rebuild();   // the actors were skins on the old model's meshes
});

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

window.viewer = { view, timeline, claims, cycle };   // for checks from the browser console
