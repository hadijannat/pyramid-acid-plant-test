// The model: the glTF of the interior, its registry of spaces, the masonry drawn as stone and as glass,
// picking, hidden spaces, the cutaway planes, the interior look, and the swap between the two readings.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const GLASS_OPACITY = 0.55;   // display choice: the masonry's glass at the full interior look
const BEDROCK_GHOST = 0.08;   // display choice: the bedrock's opacity at the full interior look
const VIEW_FROM = new THREE.Vector3(1, 0.4, 0.5).normalize();   // display choice: plan A's view from the south-east

// The alternative reading of the survey is the file beside the survey's: interior.glb, interior_alt.glb.
const fileOf = (url, reading) => (reading === 'alternative' ? url.replace(/\.glb$/, '_alt.glb') : url);

export async function loadModel(url, scene, materials, store) {
  const loader = new GLTFLoader();
  const raycaster = new THREE.Raycaster();
  // The three shell materials outlive a reading swap; each load hands them to the new meshes.
  const look = { stone: materials.stone(), glass: materials.glass(), bedrock: materials.bedrock() };
  const layers = store.get().layers;
  let hidden = layers.hidden;                                          // space names switched off
  let shellLayers = { masonry: layers.masonry, bedrock: layers.bedrock };   // opacities 0 to 1
  let k = 0;            // the interior mix last applied
  let planes = null;    // the cutaway planes, or null
  let loads = 0;        // when two loads overlap, the later one wins

  const model = {
    root: null, spaces: new Map(), shell: { stone: null, glass: null, bedrock: null },
    bounds: new THREE.Box3(), masonryBounds: new THREE.Box3(), apexY: 0,
    pickAt, setHidden, setShell, setInterior, setClipping, dispose,
  };

  async function load(file) {
    const ticket = ++loads;
    const gltf = await loader.loadAsync(file);
    if (ticket !== loads) return;   // a later swap has started; it wins
    drop();
    const found = {};
    gltf.scene.traverse(object => {
      if (!object.isMesh) return;
      if (object.name === 'masonry' || object.name === 'bedrock') {
        found[object.name] = object;
      } else {
        object.material = materials.space();
        model.spaces.set(object.name, object);
      }
    });
    const glass = found.masonry.clone();   // the masonry drawn a second time; clone() shares the geometry
    glass.material = look.glass;
    found.masonry.material = look.stone;
    found.masonry.castShadow = true;
    found.masonry.receiveShadow = true;
    found.bedrock.material = look.bedrock;
    gltf.scene.add(glass);
    model.shell = { stone: found.masonry, glass, bedrock: found.bedrock };
    for (const mesh of Object.values(model.shell)) mesh.renderOrder = 2;   // after the water and gas inside it
    model.root = gltf.scene;
    scene.add(model.root);
    model.root.updateMatrixWorld(true);
    model.masonryBounds.setFromObject(model.shell.stone);
    model.bounds.setFromObject(model.shell.bedrock).union(model.masonryBounds);
    model.apexY = model.masonryBounds.max.y;
    setHidden(hidden);
    setClipping(planes);
    setInterior(k);
  }

  // Take the shown model out. Its geometries go back to the GPU; the shell materials stay for the next one.
  // The actors' skins share the space geometries; they were on the old meshes and are rebuilt on the new.
  function drop() {
    if (!model.root) return;
    scene.remove(model.root);
    for (const mesh of model.spaces.values()) {
      mesh.geometry.dispose();
      mesh.material.dispose();
    }
    model.shell.stone.geometry.dispose();   // the glass shares it
    model.shell.bedrock.geometry.dispose();
    model.spaces.clear();
  }

  // The name of the nearest visible space under a point of the view (normalised device coordinates), or null.
  // The shell is not in the list, so the pick sees through the masonry; skins are children and never hit.
  function pickAt(ndc, camera) {
    raycaster.setFromCamera(ndc, camera);
    const visible = [...model.spaces.values()].filter(mesh => mesh.visible);
    const hit = raycaster.intersectObjects(visible, false)[0];
    return hit ? hit.object.name : null;
  }

  // Remembered, so a reading swap keeps the same spaces hidden.
  function setHidden(names) {
    hidden = names;
    for (const [name, mesh] of model.spaces) mesh.visible = !names.has(name);
  }

  function setShell({ masonry, bedrock }) {
    shellLayers = { masonry, bedrock };
    setInterior(k);
  }

  // k = 0: the stone of the exterior; k = 1: dark glass with the spaces showing through.
  function setInterior(value) {
    k = value;
    const { stone, glass, bedrock } = model.shell;
    look.stone.opacity = (1 - k) * shellLayers.masonry;
    look.glass.uniforms.uOpacity.value = k * GLASS_OPACITY * shellLayers.masonry;
    look.bedrock.opacity = (1 - k) * shellLayers.bedrock + k * BEDROCK_GHOST;
    // An opaque shell writes depth, so its near faces hide its far ones; a fading one draws both of its
    // sides (three.js draws a transparent double-sided mesh back faces first) and hides nothing.
    look.stone.depthWrite = look.stone.opacity >= 1;
    look.bedrock.depthWrite = look.bedrock.opacity >= 1;
    stone.visible = look.stone.opacity > 0;
    glass.visible = look.glass.uniforms.uOpacity.value > 0;
    bedrock.visible = look.bedrock.opacity > 0;
  }

  // Cutaway: the planes clip the masonry and the bedrock only; spaces and actors are never clipped.
  function setClipping(value) {
    planes = value;
    for (const material of Object.values(look)) material.clippingPlanes = planes;
  }

  function dispose() {
    unsubscribe();
    drop();
    model.root = null;
    for (const material of Object.values(look)) material.dispose();
  }

  await load(fileOf(url, store.get().reading));
  const unsubscribe = store.subscribe((next, prev, changed) => {
    if (changed.has('layers')) {
      setHidden(next.layers.hidden);
      setShell(next.layers);
    }
    if (changed.has('reading')) {
      const file = fileOf(url, next.reading);
      load(file).catch(error => console.error(`${file}: ${error.message}`));
    }
  });
  return model;
}

// Point the camera at the whole pyramid from the south-east: back off until the masonry's bounding sphere
// fits the narrower of the vertical and horizontal angles of view (plan A's frame()).
export function frameModel(model, camera, controls) {
  const sphere = model.masonryBounds.getBoundingSphere(new THREE.Sphere());
  const vertical = THREE.MathUtils.degToRad(camera.fov / 2);
  const half = Math.min(vertical, Math.atan(Math.tan(vertical) * camera.aspect));
  const reach = sphere.radius / Math.sin(half);
  controls.target.copy(sphere.center);
  camera.position.copy(VIEW_FROM).multiplyScalar(reach).add(sphere.center);
  camera.near = reach / 1000;   // display choice: plan A's frame rule
  camera.far = Math.max(camera.far, reach * 10);   // never below the renderer's: the sky and the 20 km ground reach further
  camera.updateProjectionMatrix();
}
