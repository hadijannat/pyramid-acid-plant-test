// Camera ride: a step flies from where the camera is to its first keyframe in at most
// TRANSITION_SECONDS, then holds that framing with a slow orbit about the point it looks at (one
// keyframe) or rides two centripetal Catmull-Rom curves through its keyframes, one for the camera's
// position and one for the point it looks at, with ease-in-out (more than one: the prologue). A step
// with the same camera as the hold before it carries the orbit on without a flight. A press on the
// canvas hands the camera to the orbit controls; resume() or the next step takes it back. While the
// prologue waits for Play, the camera sways a few degrees to and fro about its target (spec 5.2): a turn
// without a bound left the camera far from the path, and Play then whipped it back.
import * as THREE from 'three';

export const RESUME_SECONDS = 1;          // display choice: the glide back onto the path after resume()
export const TRANSITION_SECONDS = 1.5;    // display choice: the flight into a step's first keyframe takes at most this
export const HOLD_DRIFT = 0.5;            // display choice: degrees per second of orbit about the target while a step holds
export const SAME_CAMERA_EPSILON = 0.5;   // display choice: metres; a first keyframe this close to the previous hold's, in position and in target, is the same camera
const SWAY_DEGREES = 8;            // display choice: how far the waiting prologue turns to either side of the pose it waits in
const SWAY_SECONDS = 40;           // display choice: one sway there and back; at most 1.3 degrees per second
const UP = new THREE.Vector3(0, 1, 0);

const ease = k => k * k * (3 - 2 * k);   // smoothstep: ease in and out
const azimuth = v => Math.atan2(v.x, v.z);   // angle about the vertical, in the sense applyAxisAngle(UP, angle) turns

export function createRide(camera, controls, store) {
  let positions = null;   // CatmullRomCurve3 through the camera positions (a path of more than one keyframe)
  let targets = null;     // CatmullRomCurve3 through the points looked at, one per position
  let first = null;       // the step's first keyframe: where a cut lands
  let hold = false;       // one keyframe: after the flight in, the camera orbits it slowly
  let origin = null;      // { position, target } the flight into the first keyframe starts from; null: no flight
  let flight = 0;         // seconds of that flight (T)
  let span = 0;           // the step's seconds (D)
  let theta0 = 0;         // radians of orbit the hold starts from: the previous hold's when it carries on
  let riding = true;
  let sway = null;        // { position, target, t } while the prologue waits for Play: the pose it sways about, and its clock
  let glide = null;       // { position, target, k } while the camera comes back to the path
  const start = { position: new THREE.Vector3(), target: new THREE.Vector3() };   // the first keyframe
  const position = new THREE.Vector3();
  const target = new THREE.Vector3();
  const offset = new THREE.Vector3();

  function place(keyframe) {
    camera.position.fromArray(keyframe.position);
    controls.target.fromArray(keyframe.target);
  }

  function setRiding(on) {
    riding = on;
    store.set({ riding: on });   // the HUD shows "Resume ride" while it is false
  }

  // keyframes: [{position, target}, ...] in viewer coordinates; duration: the step's seconds. from: the
  // pose the camera has now, which the flight starts from so the move into the step is continuous;
  // null starts the path on its own first keyframe.
  function setPath(keyframes, { from = null, duration } = {}) {
    const points = key => keyframes.map(keyframe => new THREE.Vector3().fromArray(keyframe[key]));
    const ps = points('position');
    const ts = points('target');
    // The same camera as the hold the camera is riding now (not taken by the user, not gliding back; the
    // prologue, the one path that drifts, is no hold): no flight, and the orbit carries on from its angle.
    const same = Boolean(from) && hold && riding && !glide &&
      ps[0].distanceTo(start.position) < SAME_CAMERA_EPSILON && ts[0].distanceTo(start.target) < SAME_CAMERA_EPSILON;
    const reduced = store.get().reducedMotion;
    theta0 = 0;
    if (same) {
      const angle = azimuth(offset.subVectors(from.position, ts[0])) - azimuth(offset.subVectors(ps[0], ts[0]));
      theta0 = Math.atan2(Math.sin(angle), Math.cos(angle));   // into -pi..pi
    }
    start.position.copy(ps[0]);
    start.target.copy(ts[0]);
    hold = keyframes.length === 1;
    positions = hold ? null : new THREE.CatmullRomCurve3(ps, false, 'centripetal');
    targets = hold ? null : new THREE.CatmullRomCurve3(ts, false, 'centripetal');
    origin = from && !same && !reduced ? { position: from.position.clone(), target: from.target.clone() } : null;
    span = duration;
    flight = origin ? Math.min(TRANSITION_SECONDS, 0.4 * span) : 0;
    first = keyframes[0];
    glide = null;
    setRiding(true);   // the next step takes the camera back from the user (spec 5.1)
    if (!from || reduced) place(first);   // reduced motion: steps cut instead of fly
  }

  // The ride's pose t seconds into the step, into position and target. It depends on t alone, never
  // on the frames before it, so a seek lands where playback would be.
  function poseAt(t) {
    if (t < flight) {   // the flight in, from the pose the step began with
      const k = ease(t / flight);
      position.lerpVectors(origin.position, start.position, k);
      target.lerpVectors(origin.target, start.target, k);
    } else if (hold) {   // the first keyframe turned about the vertical through its target
      const theta = theta0 + THREE.MathUtils.degToRad(HOLD_DRIFT) * (t - flight);
      position.subVectors(start.position, start.target).applyAxisAngle(UP, theta).add(start.target);
      target.copy(start.target);
    } else {
      const s = ease(span > flight ? (t - flight) / (span - flight) : 0);
      positions.getPoint(s, position);   // getPoint, not getPointAt: both curves pass their keyframes at the same s
      targets.getPoint(s, target);
    }
  }

  function update(dt, u) {
    if (!riding || !first || store.get().reducedMotion) return;
    if (sway) {   // the pose the wait began in, turned about the vertical through its target; a time's function, like a hold
      if (!sway.position) Object.assign(sway, pose());   // taken here, after setPath has placed the camera
      sway.t += dt;
      const theta = THREE.MathUtils.degToRad(SWAY_DEGREES) * Math.sin(2 * Math.PI * sway.t / SWAY_SECONDS);
      camera.position.subVectors(sway.position, sway.target).applyAxisAngle(UP, theta).add(sway.target);
      controls.target.copy(sway.target);
      return;
    }
    poseAt(u * span);
    if (glide) {   // from where the user or the sway left the camera to the moving point of the path
      glide.k = Math.min(1, glide.k + dt / RESUME_SECONDS);
      const k = ease(glide.k);
      position.lerpVectors(glide.position, position, k);
      target.lerpVectors(glide.target, target, k);
      if (glide.k === 1) glide = null;
    }
    camera.position.copy(position);
    controls.target.copy(target);
  }

  // A press or a wheel turn hands the camera to the user, who keeps the pose they took: the sway stops too.
  function pause() {
    glide = null;
    sway = null;
    setRiding(false);
  }

  // Back onto the path. On the prologue the sway stays off after a resume until the player switches it on
  // again (a step change, or a pause of the clock): the simplest honest behaviour.
  function resume() {
    if (riding) return;
    setRiding(true);
    if (store.get().reducedMotion) {
      if (first) place(first);
      return;
    }
    glide = { position: camera.position.clone(), target: controls.target.clone(), k: 0 };
  }

  // The player's switch for the prologue's sway: on while the prologue waits for Play, off when play
  // starts or the step changes. Switched off, the camera glides from where the sway left it (at most
  // SWAY_DEGREES from the pose it waited in) to the path; a step change lays a new path just after, which
  // drops that glide.
  function drift(on) {
    on = on && !store.get().reducedMotion;   // reduced motion: the camera holds still
    if (on === Boolean(sway)) return;
    sway = on && riding ? { position: null, target: null, t: 0 } : null;   // a camera the user holds stays theirs
    glide = !on && riding ? { position: camera.position.clone(), target: controls.target.clone(), k: 0 } : null;
  }

  // The pose now, which the player passes as the next path's "from".
  const pose = () => ({ position: camera.position.clone(), target: controls.target.clone() });

  controls.domElement.addEventListener('pointerdown', pause);
  controls.domElement.addEventListener('touchstart', pause, { passive: true });
  controls.domElement.addEventListener('wheel', pause, { passive: true });   // a dolly is the user's too

  return { setPath, update, pause, resume, pose, drift, get riding() { return riding; } };
}
