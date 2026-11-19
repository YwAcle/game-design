import * as THREE from 'three';

const viewSky = `
  uniform sampler2D clouds, lunarDisc;
  uniform float dusk, pitchDay;
  vec3 skyColor(vec3 ray) {
    ray = normalize(ray);
    vec2 uv = vec2(atan(ray.z, ray.x) / 6.283185 + .24, asin(clamp(ray.y, -1., 1.)) / 3.141593 + .5);
    vec2 dx = dFdx(uv), dy = dFdy(uv);
    dx.x -= round(dx.x);
    dy.x -= round(dy.x);
    vec3 cloud = textureGrad(clouds, uv, dx, dy).rgb;
    float horizon = 1. - smoothstep(-.05, .35, ray.y);
    vec3 color = mix(cloud * vec3(.29,.64,.64), vec3(.06,.16,.17), horizon*.30);
    vec3 direction = normalize(vec3(-.66,.39,-.53));
    float moon = dot(ray, direction);
    vec3 right = normalize(cross(direction, vec3(0.,1.,0.)));
    vec3 up = cross(right, direction);
    vec2 disc = vec2(dot(ray, right), dot(ray, up)) / .098 + .5;
    float albedo = texture2D(lunarDisc, clamp(disc,0.,1.)).r;
    color += vec3(.22,.26,.23) * pow(max(0.,moon),155.) + vec3(1.43,1.29,.87)*pow(albedo,1.6)*smoothstep(.99862,.99882,moon);
    vec2 sunsetUV = vec2(uv.x+.37,.59 + .42*ray.y);
    float grain = dot(textureLod(clouds,sunsetUV,2.).rgb,vec3(.24,.64,.12));
    float cloudBank = smoothstep(.068,.097,grain);
    float cloudEdge = smoothstep(.105,.14,grain);
    vec3 sunset = mix(vec3(.99,.49,.25), vec3(.34,.19,.24), smoothstep(-.06,.63,ray.y));
    sunset = mix(sunset, vec3(.38,.185,.22), cloudBank*.73);
    sunset += vec3(.22,.085,.036)*cloudEdge;
    vec3 day = mix(vec3(.91,.76,.55), vec3(.31,.52,.70), smoothstep(-.02,.66,ray.y));
    day = mix(day, vec3(.89,.85,.78), cloudBank*.69);
    return mix(mix(color,sunset,dusk),day,pitchDay);
  }`;
const vertex = `
  varying vec3 point;
  void main() {
    vec4 world = modelMatrix * vec4(position,1.);
    point = world.xyz;
    gl_Position = projectionMatrix * viewMatrix * world;
  }`;

export async function evening(scene) {
  const loader = new THREE.TextureLoader();
  const [texture, moon] = await Promise.all(['evening-sky.jpg','moon.webp'].map(file => loader.loadAsync('./'+file)));
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.wrapS = THREE.RepeatWrapping;
  const clouds = {value:texture};
  const dome = new THREE.Mesh(new THREE.SphereGeometry(530,32,18),new THREE.ShaderMaterial({
    side:THREE.BackSide,depthWrite:false,uniforms:{clouds,lunarDisc:{value:moon},skyAlpha:{value:1},dusk:{value:0},pitchDay:{value:0}},vertexShader:vertex,
    fragmentShader:viewSky+`
      uniform float skyAlpha;
      varying vec3 point;
      void main(){
        gl_FragColor = vec4(skyColor(point - cameraPosition),skyAlpha);
        #include <colorspace_fragment>
      }`
  }));
  // A stationary viewer sees a distant sky, including when stepping between camera positions.
  dome.onBeforeRender = (renderer,_scene,camera) => {
    dome.material.uniforms.skyAlpha.value = renderer.getRenderTarget() ? 0 : 1;
    dome.material.uniformsNeedUpdate = true;
    dome.position.copy(camera.position);dome.updateMatrixWorld();
  };
  dome.frustumCulled = false;scene.add(dome);
  return dome.material.uniforms;
}
