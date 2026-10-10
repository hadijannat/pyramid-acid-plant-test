// Side panel: the current step's claim and verdict, the space inspector, and the list of steps.

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

// Four significant figures; powers of ten for the very large and the very small; null is an open bound.
function fmt(value) {
  if (value === null) return 'no bound';
  const size = Math.abs(value);
  return size !== 0 && (size >= 1e6 || size < 1e-3) ? value.toExponential(2) : String(+value.toPrecision(4));
}

const withUnit = (value, unit) => (unit === '1' ? fmt(value) : `${fmt(value)} ${unit}`);   // '1' marks a pure number

export function createPanel(root, claims, cycle, { onJump, onClose }) {
  const claimOf = new Map(claims.claims.map(claim => [claim.id, claim]));
  const stepCard = el('section', 'card');
  stepCard.id = 'step-card';
  const spaceCard = el('section', 'card');
  spaceCard.id = 'space-card';
  spaceCard.hidden = true;
  const list = el('nav');
  list.id = 'step-list';
  list.setAttribute('aria-label', 'All steps, coloured by verdict');
  root.replaceChildren(stepCard, spaceCard, list);

  // A small button that jumps to a step, coloured by the step's verdict.
  function chip(id) {
    const button = el('button', `chip status-${claimOf.get(id).status}`, id);
    button.type = 'button';
    button.addEventListener('click', () => onJump(id));
    return button;
  }

  const chips = new Map();
  for (const step of cycle.steps) {
    const button = chip(step.id);
    button.title = `${step.title} (${claimOf.get(step.id).status})`;
    chips.set(step.id, button);
    list.append(button);
  }

  function showStep(id) {
    const claim = claimOf.get(id);
    const step = cycle.steps.find(candidate => candidate.id === id);
    for (const [key, button] of chips) {
      if (key === id) button.setAttribute('aria-current', 'step'); else button.removeAttribute('aria-current');
    }
    const head = el('header');
    head.append(el('h2', '', `${id} ${step.title}`), el('span', `badge status-${claim.status}`, claim.status));
    const numbers = el('table', 'numbers');
    for (const number of claim.numbers) {
      const row = numbers.insertRow();
      row.insertCell().textContent = number.label;
      row.insertCell().textContent = withUnit(number.value, number.unit);
      row.insertCell().textContent = number.low === number.high ? '' : `${fmt(number.low)} to ${fmt(number.high)}`;
    }
    stepCard.replaceChildren(
      head,
      el('p', 'statement', claim.statement),
      el('p', 'meta', `Source ${claim.timestamp} · Tier ${claim.tier} · Piece ${claim.piece} · ${claim.subsystem}`),
      el('p', 'basis', claim.basis),
      // a pending claim's figures are screening numbers, not a verdict; say so over the table
      ...(claim.status === 'pending' && claim.numbers.length ? [el('h3', '', 'Screening figures, no verdict')] : []),
      numbers,
      el('p', 'criterion', `Criterion: ${claim.criterion}`),
    );
  }

  function showSpace(name) {
    const space = name ? claims.spaces[name] : null;
    spaceCard.hidden = !space;
    if (!space) return;
    const close = el('button', '', 'Close');
    close.type = 'button';
    close.addEventListener('click', onClose);
    const head = el('header');
    head.append(el('h2', '', space.label), close);

    const quantities = el('ul', 'quantities');
    for (const quantity of space.quantities) {
      const item = el('li');
      item.append(
        el('code', '', quantity.id), ' ', withUnit(quantity.value, quantity.unit),
        el('div', 'source', quantity.source),
      );
      quantities.append(item);
    }

    const involved = el('ul', 'involved');
    for (const id of space.claims) {
      const claim = claimOf.get(id);
      const item = el('li');
      // a step can be jumped to; an evidence claim (E01 to E40) is not on the timeline
      item.append(chips.has(id) ? chip(id) : el('span', `chip status-${claim.status}`, id), ' ', claim.statement);
      involved.append(item);
    }
    if (!space.claims.length) involved.append(el('li', '', 'None in the ledger.'));

    spaceCard.replaceChildren(
      head,
      el('h3', '', 'Ledger quantities'), quantities,
      el('h3', '', 'Claims that involve it'), involved,
    );
    spaceCard.scrollIntoView({ block: 'nearest' });
  }

  return { showStep, showSpace };
}
