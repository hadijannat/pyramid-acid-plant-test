// Boot: fetch the data, create the scene, the panel and the timeline, wire them together.
import { createPanel } from './panel.js';
import { createScene } from './scene.js';
import { createTimeline } from './timeline.js';

async function getJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
  return response.json();
}

const [claims, cycle] = await Promise.all([getJSON('data/claims.json'), getJSON('data/cycle.json')]);
document.getElementById('notice').textContent = cycle.notice;

const view = createScene(document.getElementById('stage'));
await view.load('data/interior.glb');
view.frame();

// The panel comes first: the timeline reports its first step while it is being created.
let timeline;
const panel = createPanel(document.getElementById('panel'), claims, cycle, {
  onJump: id => timeline.gotoId(id),
  onClose: () => view.select(null),
});

const startAt = location.hash.slice(1);   // read it before the timeline starts rewriting the fragment
timeline = createTimeline(view, cycle, document.getElementById('timeline'), {
  fields: claims.manifest.fields,
  onStep: id => {
    panel.showStep(id);
    history.replaceState(null, '', '#' + id);
  },
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
  view.select(null);    // load() drops the pick without telling us; close the inspector and the label with it
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

// A click on a space names it under the view and opens it in the inspector.
const picked = document.getElementById('picked');
view.onPick = name => {
  picked.textContent = name ? `${claims.spaces[name].label} (${name})` : '';
  panel.showSpace(name);
};

window.viewer = { view, timeline, panel, claims, cycle };   // for checks from the browser console
