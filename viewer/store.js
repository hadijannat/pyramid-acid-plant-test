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
