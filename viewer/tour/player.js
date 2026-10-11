// Cycle clock: the prologue and the 31 steps on one time line. A step change builds the step's
// actors, lays the camera's path from where the camera is, and sets the scene flags and the address.

// entries[0] is the prologue; entries[k] for k >= 1 is the step of index k - 1.
export function timelineOf(cycle) {
  const prologue = {
    id: 'prologue', duration: cycle.prologue.duration, path: cycle.prologue.path,
    scene: { interior: false, weather: 'clear' }, actors: [],
  };
  const entries = [prologue, ...cycle.steps];
  const starts = [];   // starts[k]: seconds from the start of the prologue to the start of entries[k]
  let total = 0;
  for (const entry of entries) { starts.push(total); total += entry.duration; }
  return { entries, starts, total };
}

// claims is in the signature as the plan header lists it; the clock does not read it.
export function createPlayer({ store, cycle, actors, ride, claims }) {
  const { entries, starts, total } = timelineOf(cycle);
  let t = 0;              // seconds from the start of the prologue
  let u = 0;              // 0 to 1 within the current entry
  let index = null;       // -1 the prologue, 0..30 the steps; null before the first entry
  let playing = false;
  let water = new Map();  // space -> the current step's water actor

  // Claim mode's answer to "how full is this space now": the step's own from and to, at u.
  const source = {
    fraction(space) {
      const actor = water.get(space);
      return actor ? actor.from + (actor.to - actor.from) * u : 0;
    },
  };

  function enter(i) {
    const entry = entries[i + 1];
    // While playing, the new path starts where the camera is: one continuous flight. Paused (Next, Back, a deep
    // link, a scrub) or at boot, it starts on its own first keyframe, so a paused jump shows the step's own view.
    const from = playing ? ride.pose() : null;
    index = i;
    water = new Map(entry.actors.filter(actor => actor.type === 'water').map(actor => [actor.space, actor]));
    actors.build(i < 0 ? null : entry);
    ride.drift(i < 0 && !playing);   // before setPath: the new path replaces the glide that ending a drift starts
    ride.setPath(entry.path, { from, duration: entry.duration });
    store.set({ stepIndex: i, interior: entry.scene.interior, weather: entry.scene.weather });
    setAddress(i < 0 ? '#' : '#' + entry.id);
  }

  function setAddress(hash) {
    try {
      history.replaceState(null, '', hash);
    } catch {
      // browsers throttle rapid replacements while the strip is scrubbed (Safari throws); the next step catches up
    }
  }

  function locate() {   // the entry at time t, and how far into it
    let k = entries.length - 1;
    while (k > 0 && starts[k] > t) k--;
    u = Math.min(1, (t - starts[k]) / entries[k].duration);
    if (k - 1 !== index) enter(k - 1);
  }

  function apply(dt) {
    actors.update({ u, dt, source });
    ride.update(dt, u);
  }

  // ponytail: store.t is written on seek, play and pause, not every frame (every subscriber would run
  // each frame); player.state().t is the live clock. Write it per frame once a V2 panel needs it live.
  function setPlaying(on) {
    playing = on;
    ride.drift(index === -1 && !on);   // spec 5.2: the prologue drifts while it waits for Play
    store.set({ playing: on, t });
  }

  function tick(dt) {   // dt arrives clamped to 0.1 s by the renderer's loop
    if (playing) {
      t = Math.min(total, t + dt);
      locate();
      if (t === total) setPlaying(false);
    }
    apply(dt);
  }

  function seek(seconds) {
    t = Math.max(0, Math.min(total, seconds));
    locate();
    store.set({ t });
    apply(0);   // the actors and the camera take the new time at once, not on the next frame
  }

  function play() {
    if (t >= total) seek(0);
    setPlaying(true);
  }

  function pause() {
    setPlaying(false);
  }

  function goto(i) {   // -1 the prologue, 0..30 a step; anything else is ignored
    if (Number.isInteger(i) && i >= -1 && i < entries.length - 1) seek(starts[i + 1]);
  }

  function gotoId(id) {
    const k = entries.findIndex(entry => entry.id === id);
    if (k > 0) return goto(k - 1);
    goto(-1);          // an unknown id (#S99, #foo, none) opens the prologue
    setAddress('#');   // already on the prologue enter() does not run, so the unknown id would stay in the address
  }

  const state = () => ({ id: entries[index + 1].id, u: +u.toFixed(3), playing, t: +t.toFixed(3) });

  locate();   // enter the prologue now: the camera, the actors, the drift and the store are set before the first frame
  return { play, pause, toggle: () => (playing ? pause() : play()), seek, goto, gotoId, tick, total, state };
}
