// Camera ride: a step's keyframes as two centripetal Catmull-Rom curves, one for the camera's
// position and one for the point it looks at, ridden with ease-in-out over the step. A press on
// the canvas hands the camera to the orbit controls; resume() or the next step takes it back.
// While the prologue waits for Play, the camera drifts slowly about its target (spec 5.2).
import * as THREE from 'three';

export const RESUME_SECONDS = 1;   // display choice: the glide back onto the path after resume()
const DRIFT_SPEED = 0.3;           // display choice: OrbitControls.autoRotateSpeed, one turn in about 200 s at 60 frames a second

const ease = k => k * k * (3 - 2 * k);   // smoothstep: ease in and out

export function createRide(camera, controls, store) {
  let positions = null;   // CatmullRomCurve3 through the camera positions
  let targets = null;     // CatmullRomCurve3 through the points looked at, one per position
  let first = null;       // the step's first keyframe: where a cut lands
  let riding = true;
  let drifting = false;   // the prologue's drift: OrbitControls turns the camera, the ride leaves it alone
  let glide = null;       // { position, target, k } while the camera comes back to the path
  const position = new THREE.Vector3();
  const target = new THREE.Vector3();
  controls.autoRotateSpeed = DRIFT_SPEED;

  function place(keyframe) {
    camera.position.fromArray(keyframe.position);
    controls.target.fromArray(keyframe.target);
  }

  function setRiding(on) {
    riding = on;
    store.set({ riding: on });   // the HUD shows "Resume ride" while it is false
  }

  // keyframes: [{position, target}, ...] in viewer coordinates. from: the pose the camera has now,
  // prepended so the move into the step is continuous; null starts the path on its own first keyframe.
  function setPath(keyframes, { from = null } = {}) {
    const points = key => keyframes.map(keyframe => new THREE.Vector3().fromArray(keyframe[key]));
    const ps = points('position');
    const ts = points('target');
    if (from) {
      ps.unshift(from.position.clone());
      ts.unshift(from.target.clone());
    }
    positions = new THREE.CatmullRomCurve3(ps, false, 'centripetal');
    targets = new THREE.CatmullRomCurve3(ts, false, 'centripetal');
    first = keyframes[0];
    glide = null;
    setRiding(true);   // the next step takes the camera back from the user (spec 5.1)
    if (!from || store.get().reducedMotion) place(first);   // reduced motion: steps cut instead of fly
  }

  function update(dt, u) {
    if (!riding || drifting || !positions || store.get().reducedMotion) return;
    const s = ease(u);
    positions.getPoint(s, position);   // getPoint, not getPointAt: both curves pass their keyframes at the same s
    targets.getPoint(s, target);
    if (glide) {   // from where the user or the drift left the camera to the moving point of the path
      glide.k = Math.min(1, glide.k + dt / RESUME_SECONDS);
      const k = ease(glide.k);
      position.lerpVectors(glide.position, position, k);
      target.lerpVectors(glide.target, target, k);
      if (glide.k === 1) glide = null;
    }
    camera.position.copy(position);
    controls.target.copy(target);
  }

  function pause() {
    glide = null;
    setRiding(false);
  }

  function resume() {
    if (riding) return;
    setRiding(true);
    if (store.get().reducedMotion) {
      if (first) place(first);
      return;
    }
    glide = { position: camera.position.clone(), target: controls.target.clone(), k: 0 };
  }

  // The player's switch for the prologue's drift: on while the prologue waits for Play, off when play
  // starts or the step changes. Switched off, the camera glides from where the drift left it to the path;
  // a step change lays a new path just after, which drops that glide.
  function drift(on) {
    on = on && !store.get().reducedMotion;   // reduced motion: the camera holds still
    if (on === drifting) return;
    drifting = on;
    controls.autoRotate = on;
    if (!on && riding) glide = { position: camera.position.clone(), target: controls.target.clone(), k: 0 };
  }

  // The pose now, which the player passes as the next path's "from".
  const pose = () => ({ position: camera.position.clone(), target: controls.target.clone() });

  controls.domElement.addEventListener('pointerdown', pause);
  controls.domElement.addEventListener('touchstart', pause, { passive: true });

  return { setPath, update, pause, resume, pose, drift, get riding() { return riding; } };
}
