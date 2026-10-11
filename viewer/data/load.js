// Fetch and check the three files the page draws from. A file that is missing, or that lacks a key the
// page reads, stops the page with the file's name and the reason (app.js shows it in #message).

const CYCLE_KEYS = ['notice', 'prologue', 'steps', 'curves'];
const PROLOGUE_KEYS = ['duration', 'path'];
const STEP_KEYS = ['id', 'title', 'duration', 'path', 'scene', 'species', 'actors'];
const CLAIMS_KEYS = ['claims', 'spaces', 'manifest'];
const CLAIM_KEYS = ['id', 'statement', 'status', 'basis'];

async function getJSON(url) {
  const response = await fetch(url).catch(error => {
    throw new Error(`${url}: ${error.message}`);
  });
  if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
  try {
    return await response.json();
  } catch {
    throw new Error(`${url}: not valid JSON`);
  }
}

// Throws "<where>missing key <key>" for the first key the object lacks.
function need(object, keys, where) {
  for (const key of keys) {
    if (object === null || typeof object !== 'object' || !(key in object)) {
      throw new Error(`${where}missing key ${key}`);
    }
  }
}

export function validateCycle(cycle) {
  need(cycle, CYCLE_KEYS, 'cycle.json: ');
  need(cycle.prologue, PROLOGUE_KEYS, 'cycle.json: prologue: ');
  if (!Array.isArray(cycle.steps)) throw new Error('cycle.json: steps is not a list');
  cycle.steps.forEach((step, i) => {
    const name = step && step.id ? step.id : `step ${i + 1}`;
    need(step, STEP_KEYS, `cycle.json: ${name}: `);
  });
  return cycle;
}

export function validateClaims(claims) {
  need(claims, CLAIMS_KEYS, 'claims.json: ');
  if (!Array.isArray(claims.claims)) throw new Error('claims.json: claims is not a list');
  for (const claim of claims.claims) {
    need(claim, CLAIM_KEYS, `claims.json: ${claim && claim.id ? claim.id : 'a claim'}: `);
  }
  return claims;
}

// Fetch one file and validate it; a validation error gains the base, so it names the file as fetched.
async function fetchChecked(base, name, validate) {
  const data = await getJSON(base + name);
  try {
    return validate(data);
  } catch (error) {
    throw new Error(base + error.message);   // 'cycle.json: missing key steps' -> 'data/cycle.json: missing key steps'
  }
}

export async function loadData(base = 'data/') {
  // One file after another, so the failure reported is always that of the first file that fails.
  const cycle = await fetchChecked(base, 'cycle.json', validateCycle);
  const claims = await fetchChecked(base, 'claims.json', validateClaims);
  const manifest = await getJSON(`${base}manifest.json`);
  // The file lists the claims; the page looks them up by id (claims.claims.S07.statement).
  claims.claims = Object.fromEntries(claims.claims.map(claim => [claim.id, claim]));
  return { claims, cycle, manifest };
}
