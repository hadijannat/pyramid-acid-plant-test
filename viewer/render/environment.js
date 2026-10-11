// Sky, sun, ground and fog, and the cross-fades between the exterior and the interior look and between
// clear weather and storm. mix.interior and mix.storm run from 0 to 1 and are applied every frame. The ground
// and the fog go with mix.interior only while the camera is inside the model (cameraInside, from app.js), so an
// interior step filmed from outside keeps its plateau.
import * as THREE from 'three';
import { Sky } from 'three/addons/objects/Sky.js';

export const FADE_SECONDS = 1.5;   // display choice: look and weather cross-fade time

// display choice: the two weathers the mix moves between (sun elevation in degrees above the horizon)
const CLEAR = { elevation: 40, intensity: 3, turbidity: 2, exposure: 0.5, fog: 0.00025, fogColour: 0xc9d3dc };
const STORM = { elevation: 6, intensity: 0.4, turbidity: 18, exposure: 0.3, fog: 0.0009, fogColour: 0x50565e };
const AZIMUTH = -35;         // display choice: degrees from south towards east; the sun stands in the south-south-west
const SKY_SCALE = 50000;     // display choice: the sky box only has to enclose the camera; its shader draws it at the far plane
const SUN_DISTANCE = 400;    // display choice: metres from the pyramid's axis to the shadow camera
const SHADOW_HALF = 200;     // display choice: the shadow camera covers a 400 m box around the pyramid
const GROUND_SIZE = 20000;   // display choice: the plateau plane, 20 km across, its edge lost in the fog
const SAND = 0xd8b47a;       // display choice: warm enough to read as sand under the blue sky light
const ENV_STEP = 0.05;       // display choice: the environment map is rebuilt when the storm mix has moved this far

export function createEnvironment(scene, rendererApi, store) {
  const { renderer } = rendererApi;
  const lerp = THREE.MathUtils.lerp;

  const sky = new Sky();
  sky.scale.setScalar(SKY_SCALE);
  scene.add(sky);

  const sun = new THREE.DirectionalLight(0xffffff, CLEAR.intensity);
  Object.assign(sun.shadow.camera, {
    left: -SHADOW_HALF, right: SHADOW_HALF, top: SHADOW_HALF, bottom: -SHADOW_HALF, near: 1, far: 2 * SUN_DISTANCE,
  });
  sun.shadow.camera.updateProjectionMatrix();
  sun.shadow.bias = -0.0005;   // display choice: no shadow acne on the faces
  scene.add(sun, sun.target);   // the target stays at the origin: the pyramid's axis at pavement level
  scene.add(new THREE.HemisphereLight(0xdfe8f0, 0x8a7a5a, 0.6));   // display choice: sky light and sand bounce

  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(GROUND_SIZE, GROUND_SIZE).rotateX(-Math.PI / 2),
    new THREE.MeshStandardMaterial({
      color: SAND, roughness: 1, transparent: true,
      polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1,   // behind any face at pavement level
    }),
  );
  ground.receiveShadow = true;
  scene.add(ground);

  scene.fog = new THREE.FogExp2(CLEAR.fogColour, CLEAR.fog);
  const fogClear = new THREE.Color(CLEAR.fogColour);
  const fogStorm = new THREE.Color(STORM.fogColour);

  // The environment map: the sky alone, rendered into a PMREM, as in three.js's ocean example.
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envScene = new THREE.Scene();
  let envTarget = null;
  let envStorm = 0;   // the storm mix the current map was made at

  function rebuildEnvironment() {
    envTarget?.dispose();
    envScene.add(sky);
    envTarget = pmrem.fromScene(envScene);
    scene.add(sky);
    scene.environment = envTarget.texture;
    envStorm = mix.storm;
  }

  const mix = { interior: 0, storm: 0 };
  const target = { interior: 0, storm: 0 };
  let inside = 0;   // 0..1, eases toward the cameraInside that app.js passes to update() every frame
  function aim(state) {
    target.interior = state.interior ? 1 : 0;
    target.storm = state.weather === 'storm' ? 1 : 0;
  }
  aim(store.get());
  store.subscribe((next, prev, changed) => {
    if (changed.has('interior') || changed.has('weather')) aim(next);
  });

  const sunDirection = new THREE.Vector3();

  function apply() {
    const k = mix.storm;
    const elevation = lerp(CLEAR.elevation, STORM.elevation, k);
    sunDirection.setFromSphericalCoords(1, THREE.MathUtils.degToRad(90 - elevation), THREE.MathUtils.degToRad(AZIMUTH));
    sky.material.uniforms.sunPosition.value.copy(sunDirection);
    sky.material.uniforms.turbidity.value = lerp(CLEAR.turbidity, STORM.turbidity, k);
    sun.position.copy(sunDirection).multiplyScalar(SUN_DISTANCE);
    sun.intensity = lerp(CLEAR.intensity, STORM.intensity, k);
    renderer.toneMappingExposure = lerp(CLEAR.exposure, STORM.exposure, k);
    scene.fog.color.lerpColors(fogClear, fogStorm, k);
    const gone = mix.interior * inside;   // the plateau goes only while an interior step is seen from inside
    scene.fog.density = lerp(CLEAR.fog, STORM.fog, k) * (1 - gone);   // no haze between an inside camera and the spaces
    ground.material.opacity = 1 - gone;
    ground.material.depthWrite = gone === 0;   // a fading ground must not hide the spaces under the plateau
    ground.visible = gone < 1;
    const settled = k !== envStorm && (k === 0 || k === 1);   // the last map of a fade is made at its end value
    if (Math.abs(k - envStorm) > ENV_STEP || settled) rebuildEnvironment();
  }

  // Each mix, and inside, moves toward its goal at 1 / FADE_SECONDS per second, or at once under reduced motion.
  // cameraInside: true when the camera position lies inside the model's bounds (app.js tests it every frame).
  function update(dt, cameraInside) {
    const step = store.get().reducedMotion ? 1 : dt / FADE_SECONDS;
    const ease = (value, goal) => (Math.abs(goal - value) <= step ? goal : value + Math.sign(goal - value) * step);
    mix.interior = ease(mix.interior, target.interior);
    mix.storm = ease(mix.storm, target.storm);
    inside = ease(inside, cameraInside ? 1 : 0);
    apply();
  }

  apply();               // first: Sky's sunPosition starts at (0, 0, 0), and an environment map built from it is NaN
  rebuildEnvironment();
  rendererApi.setQuality(store.get().quality);   // sizes the new sun's shadow map for the current tier
  return { mix, update, sun, ground, sky };
}
