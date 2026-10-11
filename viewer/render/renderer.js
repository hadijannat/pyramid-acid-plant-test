// WebGL renderer, camera, orbit controls, label layer, post-processing, quality tiers and the frame loop.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CSS2DRenderer } from 'three/addons/renderers/CSS2DRenderer.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

// display choice: what each quality tier spends on the picture
export const TIERS = {
  low:    { pixelRatio: 1,   shadowMap: 0,    bloom: false, particles: false },
  medium: { pixelRatio: 1.5, shadowMap: 1024, bloom: true,  particles: false },
  high:   { pixelRatio: 2,   shadowMap: 2048, bloom: true,  particles: true },
};
const FOV = 45;   // display choice: vertical angle of view in degrees, on a stage at least 5:4 wide
const NEAR = 0.5;   // display choice: metres
const FAR = 40000;  // display choice: metres, beyond the plateau's edge
// display choice: the threshold is a luminance before exposure; sunlit sand reads about 0.8 and the clear sky
// away from the sun up to 2.6, so neither blooms, while the sun's disc and halo (above 5) do
const BLOOM = { strength: 0.6, radius: 0.4, threshold: 3 };
const MAX_DT = 0.1;   // seconds: a tab that was in the background resumes with a long gap
// display choice: how far the scene moves up, as a fraction of the HUD card's inset (0.5 would centre the
// frame in the free area; 0.75 lifts it further, so labels near the frame's bottom clear the card)
const INSET_SHIFT = 0.75;

export function createRenderer(stage, store) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.localClippingEnabled = true;   // water and gas skins are clipped by planes on their materials
  stage.append(renderer.domElement);

  const labels = new CSS2DRenderer();   // HTML labels that follow points of the scene
  labels.domElement.className = 'labels';
  stage.append(labels.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(FOV, 1, NEAR, FAR);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  // Render, bloom, antialias, then tone mapping and sRGB: the renderer applies those two only when it
  // draws to the screen, and the passes before draw into render targets.
  const composer = new EffectComposer(renderer);
  const bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), BLOOM.strength, BLOOM.radius, BLOOM.threshold);
  composer.addPass(new RenderPass(scene, camera));
  composer.addPass(bloom);
  composer.addPass(new SMAAPass(1, 1));   // sized by composer.setSize in resize()
  composer.addPass(new OutputPass());

  let inset = 0;   // pixels at the stage's bottom that the HUD card covers

  function resize() {
    const width = stage.clientWidth;
    const height = stage.clientHeight;
    if (!width || !height) return;
    renderer.setSize(width, height);
    composer.setSize(width, height);
    labels.setSize(width, height);
    project();
  }

  // The lens for the stage's size and the HUD's inset; the CSS2D labels share the camera, so they follow.
  function project() {
    const width = stage.clientWidth;
    const height = stage.clientHeight;
    if (!width || !height) return;
    camera.aspect = width / height;
    // A stage narrower than 5:4 (a phone) keeps the width of view of a 5:4 one by opening the
    // vertical angle, so a step's camera shows the same stretch of the passages on every screen.
    const half = Math.tan(THREE.MathUtils.degToRad(FOV / 2)) * Math.max(1, 1.25 / camera.aspect);
    camera.fov = THREE.MathUtils.radToDeg(2 * Math.atan(half));
    // The window slides down a picture of the stage's own size by INSET_SHIFT of the inset, so the scene's centre
    // sits above the middle of what the card leaves free and labels authored near the frame's bottom clear the
    // card; scale and aspect are unchanged.
    // ponytail: the top INSET_SHIFT * inset pixels of an authored frame leave the stage; a frame authored near
    // its top edge would need its keyframes moved, or the whole frame shrunk into the free part at a scale cost.
    if (inset > 0) camera.setViewOffset(width, height, 0, INSET_SHIFT * inset, width, height);
    else camera.clearViewOffset();
    camera.updateProjectionMatrix();
  }

  // The HUD calls this with its card's height (0 while hidden): the scene's centre moves above the card.
  function setInset(bottomPx) {
    inset = Math.max(0, bottomPx);
    project();   // the canvas keeps its size: no render target is rebuilt
  }
  const observer = new ResizeObserver(resize);
  observer.observe(stage);

  function setQuality(tier) {
    const { pixelRatio, shadowMap, bloom: glow } = TIERS[tier];
    const ratio = Math.min(pixelRatio, window.devicePixelRatio);
    renderer.setPixelRatio(ratio);
    composer.setPixelRatio(ratio);
    renderer.shadowMap.enabled = shadowMap > 0;
    scene.traverse(object => {   // the environment's sun; point lights never cast shadows here
      if (!object.isDirectionalLight) return;
      object.castShadow = shadowMap > 0;
      object.shadow.mapSize.set(shadowMap, shadowMap);
      object.shadow.map?.dispose();   // rebuilt at the new size on the next frame
      object.shadow.map = null;
    });
    bloom.enabled = glow;
    resize();
  }

  const clock = new THREE.Clock();
  let samples = null;   // frame times in ms while measure() runs

  function start(onFrame) {
    clock.start();
    renderer.setAnimationLoop(() => {
      const delta = clock.getDelta();
      if (samples) samples.push(delta * 1000);
      api.lastDt = Math.min(delta, MAX_DT);
      onFrame(api.lastDt);
      controls.update();
      composer.render(api.lastDt);
      labels.render(scene, camera);
    });
  }

  // The median frame time over a stretch of wall-clock time; NaN if no frame was drawn (a hidden page).
  // ponytail: one measurement at a time; a call made while another runs takes over the sampling.
  // Give each call its own sample array if two callers ever need to overlap.
  function measure(seconds) {
    return new Promise(resolve => {
      const times = [];
      samples = times;
      setTimeout(() => {
        if (samples === times) samples = null;
        times.sort((a, b) => a - b);
        resolve(times.length ? times[Math.floor(times.length / 2)] : NaN);
      }, seconds * 1000);
    });
  }

  const unsubscribe = store.subscribe((next, prev, changed) => {
    if (changed.has('quality')) setQuality(next.quality);
  });

  function dispose() {
    renderer.setAnimationLoop(null);
    observer.disconnect();
    unsubscribe();
    controls.dispose();
    composer.dispose();
    renderer.dispose();
    renderer.domElement.remove();
    labels.domElement.remove();
  }

  const api = { renderer, camera, controls, labels, scene, composer, resize, setQuality, setInset, start, measure, lastDt: 0, dispose };
  setQuality(store.get().quality);
  return api;
}
