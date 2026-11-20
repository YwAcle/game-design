import * as THREE from 'three';
import { Reflector } from 'three/addons/objects/Reflector.js';

const surface = {
  name: 'Black Lake',
  uniforms: {
    ...Reflector.ReflectorShader.uniforms,
    waveMap: {value: null}, bedMap: {value: null}, depthMap: {value: null},
    grid: {value: new THREE.Vector4()}, time: {value: 0}
  },
  vertexShader: `
    uniform mat4 textureMatrix;
    varying vec4 mirrorCoord;
    varying vec3 point;
    void main() {
      point = (modelMatrix * vec4(position, 1.)).xyz;
      mirrorCoord = textureMatrix * vec4(position, 1.);
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.);
    }`,
  fragmentShader: `
    uniform mat4 textureMatrix;
    uniform sampler2D tDiffuse, waveMap, bedMap, depthMap;
    uniform vec4 grid;
    uniform float time;
    varying vec4 mirrorCoord;
    varying vec3 point;
    void main() {
      vec2 p = point.xz;
      vec3 toEye = normalize(cameraPosition - point);
      float distanceToEye = length(cameraPosition - point);
      vec2 flow = vec2(-.033, .017) * time;
      mat2 crossing = mat2(.8, .6, -.6, .8);
      vec2 swell = texture2D(waveMap, p / vec2(18., 9.) + flow * .32).rg * 2. - 1.;
      vec2 chop = (texture2D(waveMap, crossing * p / 4.7 + flow * .61).rg * 2. - 1.) * crossing;
      vec2 fine = texture2D(waveMap, p / 1.2 - flow).rg * 2. - 1.;
      vec2 slope = swell * .23 + chop * .072 + fine * .021 / (1. + distanceToEye * .027);
      vec3 normal = normalize(vec3(slope.x, 1., slope.y));
      float incidence = clamp(dot(normal, toEye), 0., 1.);
      float depth = texture2D(depthMap, (p - grid.xy) / grid.zw).r * 12.;
      vec2 offset = slope * min(distanceToEye, 30.) * .23;
      vec4 distorted = mirrorCoord + textureMatrix * vec4(offset.x, -offset.y, 0., 0.);
      vec2 uv = distorted.xy / distorted.w;
      uv.y += dot(slope, toEye.xz) * .21 / (1. + distanceToEye * .011);
      vec4 reflected = texture2D(tDiffuse, clamp(uv,.002,.998));
      vec3 reflection = reflected.rgb;
      vec2 bedUV = (p - toEye.xz * min(depth, 2.) * .72 + slope * min(depth, 2.)) * .81;
      vec3 stones = texture2D(bedMap, bedUV).rgb * vec3(.45,.57,.61);
      vec3 transmission = exp(-vec3(1.55,.73,.55) * depth / max(.30, incidence));
      float elevated = smoothstep(32., 96., cameraPosition.y);
      vec3 deepWater = mix(vec3(.0024,.015,.018),vec3(.008,.070,.091),elevated);
      vec3 body = mix(deepWater, stones, transmission);
      float fresnel = .035 + .965 * pow(1. - incidence, 4.);
      // Group the sky reflection into dark troughs and lit facets at lake scale.
      float crest = smoothstep(-.20,.26,swell.x + .35*chop.y);
      vec3 tintedReflection = reflection * mix(vec3(.40,.53,.50),vec3(.86,.99,.91), crest);
      vec3 color = mix(body,tintedReflection,.11 + .89 * fresnel);
      // The reflected sky writes zero alpha; banks and buildings occlude the moon glitter.
      vec3 halfAngle = normalize(normalize(vec3(-.66,.39,-.53)) + toEye);
      float highlight = pow(max(dot(normal, halfAngle), 0.), 230.);
      color += vec3(.42,.47,.36) * smoothstep(.19,.67,highlight) * (1. - reflected.a);
      // A low, broken wash follows the terrain contour only at the waterline.
      float wash = 1. - smoothstep(.015, .12, abs(depth - (.09 + swell.y * .12)));
      color += vec3(.085,.11,.107) * wash * smoothstep(-.12,.53, chop.x + fine.y);
      gl_FragColor = vec4(color, 1.);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`
};

export async function blackLake(scene, nav, renderer, original) {
  const loader = new THREE.TextureLoader();
  const [waves, bed] = await Promise.all(['wind-waves.webp','lakebed.webp'].map(file => loader.loadAsync('./' + file)));
  for (const tex of [waves, bed]) {
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    tex.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
  }
  bed.colorSpace = THREE.SRGBColorSpace;
  const width = nav.heights[0].length, height = nav.heights.length;
  const depths = Uint8Array.from(nav.heights.flat(), y => Math.round(255 * THREE.MathUtils.clamp(-y / 12, 0, 1)));
  const depthMap = new THREE.DataTexture(depths, width, height, THREE.RedFormat);
  depthMap.magFilter = depthMap.minFilter = THREE.LinearFilter;
  depthMap.needsUpdate = true;

  const bounds = new THREE.Box3().setFromObject(original);
  const size = bounds.getSize(new THREE.Vector3());
  const lake = new Reflector(new THREE.PlaneGeometry(size.x, size.z), {
    textureWidth: 768, textureHeight: 512, multisample: 0, clipBias: .00015, shader: surface
  });
  if (!renderer.extensions.has('EXT_color_buffer_float')) lake.getRenderTarget().texture.type = THREE.UnsignedByteType;
  bounds.getCenter(lake.position);
  lake.position.y = bounds.max.y;
  lake.rotation.x = -Math.PI / 2;
  original.visible = false;
  scene.add(lake);

  const {uniforms} = lake.material;
  uniforms.waveMap.value = waves;
  uniforms.bedMap.value = bed;
  uniforms.depthMap.value = depthMap;
  uniforms.grid.value.set(nav.x0-nav.step/2, nav.z0-nav.step/2, nav.step*width, nav.step*height);

  // All reflected geometry is static. Ripples can animate against the cached view.
  const lastView = new THREE.Matrix4(), lastProjection = new THREE.Matrix4();
  const renderMirror = lake.onBeforeRender;
  lake.onBeforeRender = function(renderer, scene, camera) {
    if (lastView.equals(camera.matrixWorld) && lastProjection.equals(camera.projectionMatrix)) return;
    lastView.copy(camera.matrixWorld);
    lastProjection.copy(camera.projectionMatrix);
    renderMirror.call(this, renderer, scene, camera);
  };
  return uniforms.time;
}
