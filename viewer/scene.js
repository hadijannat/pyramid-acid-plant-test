// three.js scene: renderer, camera, controls, lights, model loading, show and hide, picking.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { CSS2DRenderer } from 'three/addons/renderers/CSS2DRenderer.js';

// Display choices, not physical quantities.
const FOV = 45;   // vertical angle of view in degrees, on a stage at least 5:4 wide
const SPACE_COLOUR = 0xece5d3;
const PICKED_GLOW = 0x6b5a2a;
const SHELL = {
  masonry: { color: 0xb9a888, opacity: 0.16 },
  bedrock: { color: 0x7d7568, opacity: 0.1 },
};

export function createScene(stage) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });   // the page background shows through
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.localClippingEnabled = true;   // timeline.js clips the water with a plane on its material
  stage.prepend(renderer.domElement);

  const labels = new CSS2DRenderer();   // HTML labels that follow points of the scene
  labels.domElement.className = 'labels';
  stage.append(labels.domElement);

  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x40444a, 2));
  const sun = new THREE.DirectionalLight(0xffffff, 1.5);
  sun.position.set(1, 2, 1.5);
  scene.add(sun);

  const camera = new THREE.PerspectiveCamera(FOV, 1, 1, 5000);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  const spaces = new Map();   // space name -> Mesh, for the model now shown
  const shell = new Map();    // 'masonry' and 'bedrock' -> Mesh
  const hidden = new Set();   // names switched off; kept when the model is swapped
  const loader = new GLTFLoader();
  const raycaster = new THREE.Raycaster();
  let model = null;
  let picked = null;

  const view = {
    scene, camera, controls, spaces, shell,
    load, frame, setVisible, pickAt, select,
    onPick: null, onFrame: null,
  };

  async function load(url) {
    const gltf = await loader.loadAsync(url);
    if (model) {
      scene.remove(model);
      model.traverse(object => {
        if (object.isMesh) { object.geometry.dispose(); object.material.dispose(); }
      });
    }
    model = gltf.scene;
    spaces.clear();
    shell.clear();
    picked = null;
    model.traverse(object => {
      if (!object.isMesh) return;
      const look = SHELL[object.name];
      if (look) {
        object.material = new THREE.MeshStandardMaterial({
          ...look, transparent: true, depthWrite: false, side: THREE.DoubleSide, flatShading: true,
          roughness: 1, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1,
        });
        object.renderOrder = 2;   // drawn after the water and gas inside it
        shell.set(object.name, object);
      } else {
        object.material = new THREE.MeshStandardMaterial({
          color: SPACE_COLOUR, side: THREE.DoubleSide, flatShading: true, roughness: 0.9,
        });
        spaces.set(object.name, object);
      }
      object.visible = !hidden.has(object.name);
    });
    scene.add(model);
  }

  // Point the camera at the whole pyramid from the south-east: back off until the masonry's bounding
  // sphere fits the narrower of the vertical and horizontal angles of view.
  function frame() {
    const sphere = new THREE.Box3().setFromObject(shell.get('masonry')).getBoundingSphere(new THREE.Sphere());
    const vertical = THREE.MathUtils.degToRad(camera.fov / 2);
    const half = Math.min(vertical, Math.atan(Math.tan(vertical) * camera.aspect));
    const reach = sphere.radius / Math.sin(half);
    controls.target.copy(sphere.center);
    camera.position.set(1, 0.4, 0.5).normalize().multiplyScalar(reach).add(sphere.center);
    camera.near = reach / 1000;
    camera.far = reach * 10;
    camera.updateProjectionMatrix();
  }

  function setVisible(name, on) {
    if (on) hidden.delete(name); else hidden.add(name);
    const mesh = spaces.get(name) || shell.get(name);
    if (mesh) mesh.visible = on;
  }

  // The name of the nearest visible space under a point of the window, or null.
  function pickAt(clientX, clientY) {
    const rect = renderer.domElement.getBoundingClientRect();
    const point = new THREE.Vector2(
      (clientX - rect.left) / rect.width * 2 - 1,
      1 - (clientY - rect.top) / rect.height * 2,
    );
    raycaster.setFromCamera(point, camera);
    const visible = [...spaces.values()].filter(mesh => mesh.visible);
    const hit = raycaster.intersectObjects(visible, false)[0];
    return hit ? hit.object.name : null;
  }

  function select(name) {
    if (picked) picked.material.emissive.setHex(0x000000);
    picked = spaces.get(name) || null;
    if (picked) picked.material.emissive.setHex(PICKED_GLOW);
    if (view.onPick) view.onPick(picked ? name : null);
  }

  // A press and release in nearly the same place is a click and picks; anything longer is an orbit drag.
  let pressedAt = null;
  renderer.domElement.addEventListener('pointerdown', event => { pressedAt = [event.clientX, event.clientY]; });
  renderer.domElement.addEventListener('pointerup', event => {
    if (pressedAt && Math.hypot(event.clientX - pressedAt[0], event.clientY - pressedAt[1]) < 5) {
      select(pickAt(event.clientX, event.clientY));
    }
    pressedAt = null;
  });

  new ResizeObserver(() => {
    const width = stage.clientWidth;
    const height = stage.clientHeight;
    if (!width || !height) return;
    renderer.setSize(width, height);
    labels.setSize(width, height);
    camera.aspect = width / height;
    // A stage narrower than 5:4 (a phone) keeps the width of view of a 5:4 one by opening the
    // vertical angle, so a step's camera shows the same stretch of the passages on every screen.
    const half = Math.tan(THREE.MathUtils.degToRad(FOV / 2)) * Math.max(1, 1.25 / camera.aspect);
    camera.fov = THREE.MathUtils.radToDeg(2 * Math.atan(half));
    camera.updateProjectionMatrix();
  }).observe(stage);

  const clock = new THREE.Clock();
  renderer.setAnimationLoop(() => {
    const dt = Math.min(clock.getDelta(), 0.1);   // a tab that was in the background resumes with a long gap
    if (view.onFrame) view.onFrame(dt);
    controls.update();
    renderer.render(scene, camera);
    labels.render(scene, camera);
  });

  return view;
}
