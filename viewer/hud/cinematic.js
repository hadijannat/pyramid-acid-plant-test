// Cinematic HUD: one card with the caption (step, claim as stated, verdict, basis), the progress
// strip and the controls; the play overlay on the prologue; the keyboard. Text is set with textContent.
import { timelineOf } from '../tour/player.js';

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function button(text, label, onClick) {
  const node = el('button', '', text);
  node.type = 'button';
  node.setAttribute('aria-label', label);   // every label contains the visible text
  node.addEventListener('click', onClick);
  return node;
}

const CARD_GUTTER = 16;   // display choice: the gap under the card in style.css, part of what it covers

export function mountCinematic(root, { store, cycle, claims, player, ride, rendererApi }) {
  const steps = cycle.steps;
  const { starts } = timelineOf(cycle);

  // ---- caption: the prologue shows the title and the notice, a step its claim and verdict.
  // The step id sits in its own line above the title; the heading's text still reads "S07 Title".
  const stepId = el('span', 'step-id');
  const title = document.createTextNode('');
  const heading = el('h2');
  heading.append(stepId, title);
  const statement = el('p', 'statement');
  const badge = el('span', 'badge');
  const basis = el('p', 'basis');
  const verdict = el('div', 'verdict');
  verdict.append(badge, basis);
  const caption = el('section', 'caption');
  caption.setAttribute('aria-live', 'polite');
  caption.append(heading, statement, verdict);

  // ---- strip: one tick per step, coloured by verdict; a drag scrubs
  const strip = el('div', 'strip');
  strip.tabIndex = 0;
  strip.setAttribute('role', 'slider');
  strip.setAttribute('aria-label', 'Step of the cycle: drag to scrub, Left and Right to step');
  strip.setAttribute('aria-valuemin', '0');
  strip.setAttribute('aria-valuemax', String(steps.length));
  const ticks = steps.map(step => {
    const status = claims.claims[step.id].status;
    const tick = el('span', `tick status-${status}`);
    tick.title = `${step.id} ${step.title} (${status.replace('_', ' ')})`;
    strip.append(tick);
    return tick;
  });

  // The ticks are equal, so the pointer's place on the strip names a step and a point inside it.
  function scrubTo(clientX) {
    const box = strip.getBoundingClientRect();
    const x = Math.min(Math.max((clientX - box.left) / box.width, 0), 0.9999) * steps.length;
    const i = Math.floor(x);
    player.seek(starts[i + 1] + (x - i) * steps[i].duration);
  }
  strip.addEventListener('pointerdown', event => {
    player.pause();
    strip.setPointerCapture(event.pointerId);
    scrubTo(event.clientX);
  });
  strip.addEventListener('pointermove', event => {
    if (strip.hasPointerCapture(event.pointerId)) scrubTo(event.clientX);
  });

  // ---- controls
  const toggleHud = () => store.set({ hud: { visible: !store.get().hud.visible } });
  function toggleFullscreen() {
    if (!document.fullscreenEnabled) return;
    const request = document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
    request.catch(() => {});   // refused without a user gesture (a key event sent by a script): nothing to undo
  }
  const backButton = button('Back', 'Back to the previous step', () => player.goto(store.get().stepIndex - 1));
  const playButton = button('Play', 'Play', () => player.toggle());
  const nextButton = button('Next', 'Next step', () => player.goto(store.get().stepIndex + 1));
  const resumeButton = button('Resume ride', 'Resume ride', () => ride.resume());
  const fullscreenButton = button('Fullscreen', 'Fullscreen', toggleFullscreen);
  fullscreenButton.hidden = !document.fullscreenEnabled;   // a browser without the Fullscreen API
  // ponytail: with the HUD hidden only the H key brings it back; V2's phone layout adds a touch control.
  const hideButton = button('Hide HUD', 'Hide HUD (H shows it again)', toggleHud);
  const controls = el('div', 'controls');
  controls.append(backButton, playButton, nextButton, fullscreenButton, hideButton, resumeButton);   // Resume last: it comes and goes

  const card = el('div', 'hud-card');
  card.append(caption, strip, controls);
  const overlay = el('div', 'overlay');
  overlay.append(button('Play the claimed cycle', 'Play the claimed cycle', () => player.play()));
  root.replaceChildren(overlay, card);

  // ---- rendering: each part from the store keys it shows
  function renderStep({ stepIndex }) {
    const step = steps[stepIndex];   // undefined on the prologue (-1)
    const claim = step && claims.claims[step.id];
    stepId.textContent = step ? step.id : '';
    stepId.hidden = !step;
    title.textContent = step ? ` ${step.title}` : document.title;   // the space is collapsed at the line's start
    statement.textContent = step ? claim.statement : cycle.notice;
    verdict.hidden = !step;
    if (step) {
      badge.className = `badge status-${claim.status}`;
      badge.textContent = claim.status.replace('_', ' ');   // "not_testable" reads "not testable"
      basis.textContent = claim.basis;
      basis.title = claim.basis;   // the card clamps a long basis to two lines; the whole of it is one hover away
    }
    ticks.forEach((tick, i) => tick.classList.toggle('current', i === stepIndex));
    strip.setAttribute('aria-valuenow', String(stepIndex + 1));
    strip.setAttribute('aria-valuetext', step ? heading.textContent : 'Prologue');
    backButton.disabled = stepIndex < 0;
    nextButton.disabled = stepIndex >= steps.length - 1;
  }
  function renderPlaying({ stepIndex, playing }) {
    playButton.textContent = playing ? 'Pause' : 'Play';
    playButton.setAttribute('aria-label', playButton.textContent);
    hide(overlay, stepIndex !== -1 || playing);
  }
  // A control that hides while it has the focus hands the focus to Play, so the keyboard keeps its place.
  function hide(node, hidden) {
    if (hidden && node.contains(document.activeElement)) playButton.focus();
    node.hidden = hidden;
  }
  const renderRiding = ({ riding }) => hide(resumeButton, riding);
  // The card covers the bottom of the stage; the renderer lifts the scene's centre above it (0 while hidden).
  function fitInset() {
    const height = card.offsetHeight;   // 0 while #hud is hidden
    rendererApi.setInset(height ? height + CARD_GUTTER : 0);
  }
  const cardObserver = new ResizeObserver(fitInset);   // the caption's height changes with each step
  cardObserver.observe(card);
  function renderHud({ hud }) {
    root.classList.toggle('hidden', !hud.visible);
    fitInset();   // at once, not on the observer's next frame
  }

  const unsubscribe = store.subscribe((state, previous, changed) => {
    if (changed.has('stepIndex')) renderStep(state);
    if (changed.has('stepIndex') || changed.has('playing')) renderPlaying(state);
    if (changed.has('riding')) renderRiding(state);
    if (changed.has('hud')) renderHud(state);
  });
  const initial = store.get();
  renderStep(initial);
  renderPlaying(initial);
  renderRiding(initial);
  renderHud(initial);

  // ---- keyboard
  const keys = {
    ' ': () => player.toggle(),
    ArrowLeft: () => player.goto(store.get().stepIndex - 1),
    ArrowRight: () => player.goto(store.get().stepIndex + 1),
    i: () => store.set({ mode: store.get().mode === 'inspector' ? 'cinematic' : 'inspector' }),   // V2 mounts the inspector
    f: toggleFullscreen,
    h: toggleHud,
    Escape: () => store.set({ mode: 'cinematic' }),
  };
  function onKey(event) {
    if (event.ctrlKey || event.metaKey || event.altKey) return;   // the browser's own shortcuts
    const key = event.key || '';
    if (event.target instanceof HTMLButtonElement && (key === ' ' || key === 'Enter')) return;   // a focused button clicks itself
    const action = keys[key.length === 1 ? key.toLowerCase() : key];
    if (!action) return;
    event.preventDefault();   // Space would scroll the page
    if (event.repeat && key === ' ') return;   // a held Space would flip play and pause on every repeat
    action();
  }
  window.addEventListener('keydown', onKey);

  return {
    unmount() {
      unsubscribe();
      cardObserver.disconnect();
      rendererApi.setInset(0);
      window.removeEventListener('keydown', onKey);
      root.replaceChildren();
      root.classList.remove('hidden');
    },
  };
}
