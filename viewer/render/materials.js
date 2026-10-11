// Materials: procedural limestone, dark glass, bedrock, the schematic interior, water, gas, and hatching.
// The glTF carries positions only, no normals: every lit material is flat shaded, the custom shaders take
// their normal from screen-space derivatives, and abs() keeps them blind to gmsh's unchecked winding.
import * as THREE from 'three';

// Display choices, not physical quantities (so are the roughness, opacity and shader weights in the functions below).
const STONE = 0xcdb894;        // display choice: limestone
const BEDROCK = 0x6f675b;      // display choice: darker stone
const SPACE = 0xece5d3;        // display choice: plan A's space colour
const WATER = 0x2f86d6;        // display choice: plan A's water colour
const GLASS_BODY = 0x0e141a;   // display choice: the glass seen face on
const GLASS_EDGE = 0x8fb8dc;   // display choice: the cool glow where the glass is seen edge on
const SHADE = 0.4;             // display choice: a hatching stripe is the actor's colour at 40 percent
// GLSL float literals (written with a decimal point: GLSL does not convert integers).
const GRAIN = '0.2';           // display choice: the stone's brightness varies by 20 percent either way
const BAND = '0.3';            // display choice: metres of brighter water under the free surface
const PITCH = '8.0';           // display choice: hatching stripes repeat every 8 device pixels along a row
// ponytail: device pixels, so the stripes are finer on a high-density screen; divide by the pixel ratio if they read too fine.

// 3D value noise in 0 to 1: hashed values on the integer lattice, smoothly interpolated between them.
const NOISE = /* glsl */ `
float hash3(vec3 p) { return fract(sin(dot(p, vec3(12.9898, 78.233, 37.719))) * 43758.5453); }
float noise3(vec3 p) {
  vec3 i = floor(p);
  vec3 f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(
    mix(mix(hash3(i), hash3(i + vec3(1.0, 0.0, 0.0)), f.x),
        mix(hash3(i + vec3(0.0, 1.0, 0.0)), hash3(i + vec3(1.0, 1.0, 0.0)), f.x), f.y),
    mix(mix(hash3(i + vec3(0.0, 0.0, 1.0)), hash3(i + vec3(1.0, 0.0, 1.0)), f.x),
        mix(hash3(i + vec3(0.0, 1.0, 1.0)), hash3(i + vec3(1.0, 1.0, 1.0)), f.x), f.y),
    f.z);
}
`;

// How edge-on a surface is seen: 0 face on, 1 at the silhouette. view is the fragment's view-space position.
const FRESNEL = /* glsl */ `
float fresnel(vec3 view) {
  vec3 n = normalize(cross(dFdx(view), dFdy(view)));
  return pow(1.0 - abs(dot(n, normalize(-view))), 3.0);
}
`;

// The vertex shader of the glass and the gas: the position in view space and in the world, and clipping.
const VERTEX = /* glsl */ `
varying vec3 vView;
varying vec3 vWorld;
#include <clipping_planes_pars_vertex>
void main() {
  vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
  vView = mvPosition.xyz;
  vWorld = (modelMatrix * vec4(position, 1.0)).xyz;
  gl_Position = projectionMatrix * mvPosition;
  #include <clipping_planes_vertex>
}
`;

export function createMaterials() {
  const time = { value: 0 };   // one uTime uniform, shared by every material made here

  // Limestone: grain and weathering from triplanar value noise in object space, a few percent of brightness.
  function stone() {
    const material = new THREE.MeshStandardMaterial({
      color: STONE, roughness: 0.92, metalness: 0, flatShading: true, side: THREE.DoubleSide,
      transparent: true, opacity: 1,
    });
    material.onBeforeCompile = shader => {
      shader.vertexShader = shader.vertexShader
        .replace('#include <common>', '#include <common>\nvarying vec3 vObject;')
        .replace('#include <begin_vertex>', '#include <begin_vertex>\nvObject = position;');
      shader.fragmentShader = shader.fragmentShader
        .replace('#include <common>', `#include <common>
varying vec3 vObject;
${NOISE}
// 2D noise on the three planes through the point, weighted by how squarely the face meets each plane.
float triplanar(vec3 p, vec3 n) {
  vec3 w = abs(n) / (abs(n.x) + abs(n.y) + abs(n.z));
  return w.x * noise3(vec3(p.yz, 0.0)) + w.y * noise3(vec3(p.zx, 0.0)) + w.z * noise3(vec3(p.xy, 0.0));
}`)
        .replace('#include <map_fragment>', `#include <map_fragment>
{
  vec3 faceNormal = normalize(cross(dFdx(vObject), dFdy(vObject)));
  // display choice: a coarse octave for weathering, a finer one for grain, both above a pixel at the framing distance
  float grain = 0.65 * triplanar(vObject * 0.05, faceNormal) + 0.35 * triplanar(vObject * 0.5, faceNormal);
  diffuseColor.rgb *= 1.0 + ${GRAIN} * (2.0 * grain - 1.0);
}`);
    };
    return material;
  }

  // Dark glass with a Fresnel edge glow: the masonry seen from inside. The model sets uOpacity.
  function glass() {
    return new THREE.ShaderMaterial({
      uniforms: {
        uBody: { value: new THREE.Color(GLASS_BODY) },
        uEdge: { value: new THREE.Color(GLASS_EDGE).multiplyScalar(2.5) },   // display choice: bright, under the bloom threshold of 3
        uOpacity: { value: 0 },
      },
      vertexShader: VERTEX,
      fragmentShader: /* glsl */ `
uniform vec3 uBody;
uniform vec3 uEdge;
uniform float uOpacity;
varying vec3 vView;
#include <clipping_planes_pars_fragment>
${FRESNEL}
void main() {
  #include <clipping_planes_fragment>
  float edge = pow(fresnel(vView), 0.6667);   // display choice: flat faces seen at 30 to 60 degrees still show some edge
  gl_FragColor = vec4(mix(uBody, uEdge, edge), uOpacity * (0.75 + 0.5 * edge));   // display choice: a body dark enough to read as glass
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`,
      transparent: true, depthWrite: false, side: THREE.DoubleSide, clipping: true,
    });
  }

  function bedrock() {
    return new THREE.MeshStandardMaterial({
      color: BEDROCK, roughness: 1, metalness: 0, flatShading: true, side: THREE.DoubleSide,
      transparent: true, opacity: 1,
    });
  }

  // The schematic interior: pale surfaces that light themselves, so they read through the dark glass.
  function space() {
    return new THREE.MeshStandardMaterial({
      color: SPACE, emissive: SPACE, emissiveIntensity: 2.5, roughness: 0.9,   // display choice: emissive under the bloom threshold
      metalness: 0, flatShading: true, side: THREE.DoubleSide,
    });
  }

  // Water: a skin clipped by the plane at the free surface, a slow ripple on its normal, and a brighter band
  // just under the surface. The actor sets material.userData.uLevel.value to the surface's viewer Y.
  function water(plane) {
    const material = new THREE.MeshStandardMaterial({
      color: WATER, roughness: 0.25, metalness: 0, flatShading: true, side: THREE.DoubleSide,
      transparent: true, opacity: 0.8, depthWrite: false, clippingPlanes: [plane],
    });
    const level = { value: -1e6 };   // display choice: far below everything until the actor sets it
    material.userData.uLevel = level;
    material.onBeforeCompile = shader => {
      shader.uniforms.uTime = time;
      shader.uniforms.uLevel = level;
      shader.vertexShader = shader.vertexShader
        .replace('#include <common>', '#include <common>\nvarying vec3 vWorld;')
        .replace('#include <begin_vertex>', '#include <begin_vertex>\nvWorld = (modelMatrix * vec4(position, 1.0)).xyz;');
      shader.fragmentShader = shader.fragmentShader
        .replace('#include <common>', '#include <common>\nuniform float uTime;\nuniform float uLevel;\nvarying vec3 vWorld;')
        .replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
// display choice: ripple amplitude, wavelength and speed
normal = normalize(normal + 0.06 * vec3(sin(vWorld.x * 1.7 + uTime * 1.3), 0.0, cos(vWorld.z * 1.9 + uTime * 1.1)));`)
        .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
float belowSurface = uLevel - vWorld.y;
totalEmissiveRadiance += diffuseColor.rgb * 0.6 * step(0.0, belowSurface) * step(belowSurface, ${BAND});`);
    };
    return material;
  }

  // Gas: a view-dependent veil, denser where the space is seen edge on, broken by drifting noise. Normal blending:
  // an additive haze vanishes over the self-lit spaces it lies on.
  function gas(plane, colourHex) {
    return new THREE.ShaderMaterial({
      uniforms: { uColour: { value: new THREE.Color(colourHex) }, uTime: time },
      vertexShader: VERTEX,
      fragmentShader: /* glsl */ `
uniform vec3 uColour;
uniform float uTime;
varying vec3 vView;
varying vec3 vWorld;
#include <clipping_planes_pars_fragment>
${NOISE}
${FRESNEL}
void main() {
  #include <clipping_planes_fragment>
  // display choice: noise scale, drift speed and density
  float drift = noise3(vWorld * 0.6 + vec3(0.0, -0.25, 0.1) * uTime);
  float density = (0.25 + 0.75 * fresnel(vView)) * (0.4 + 0.6 * drift);
  gl_FragColor = vec4(uColour, clamp(density * 2.0, 0.0, 0.85));   // display choice: the veil's opacity from its density
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`,
      transparent: true, depthWrite: false, side: THREE.DoubleSide,
      blending: THREE.NormalBlending,   // display choice
      clipping: true, clippingPlanes: [plane],
    });
  }

  // Screen-space diagonal stripes over a material: every other band of PITCH pixels takes a darker shade
  // of the colour. Works on the standard materials and on the shader materials above, which all have
  // the tonemapping chunk; the stripes go in just before it, in linear colour. A stripe is drawn opaque: at the
  // skin's own opacity the self-lit space behind a veil or a liquid washed it out to a few levels of grey.
  function hatch(material, colourHex) {
    const shade = new THREE.Color(colourHex).multiplyScalar(SHADE);
    const previous = material.onBeforeCompile;
    const key = material.customProgramCacheKey();
    material.onBeforeCompile = (shader, renderer) => {
      previous.call(material, shader, renderer);
      shader.uniforms.uHatch = { value: shade };
      shader.fragmentShader = shader.fragmentShader
        .replace('void main() {', 'uniform vec3 uHatch;\nvoid main() {')
        .replace('#include <tonemapping_fragment>', `if (fract((gl_FragCoord.x + gl_FragCoord.y) / ${PITCH}) < 0.5) gl_FragColor = vec4(uHatch, 1.0);
#include <tonemapping_fragment>`);
    };
    // the wrapper's source is the same for every material it wraps; keep their programs apart
    material.customProgramCacheKey = () => `${key}|hatch`;
    material.needsUpdate = true;
    return material;
  }

  return { stone, glass, bedrock, space, water, gas, hatch, update: dt => { time.value += dt; } };
}
