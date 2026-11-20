import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { blackLake } from "./lake.js";
import { evening } from "./sky.js";
import { floorHeight, walkable, atDoor } from './navigation.mjs';
import { readStoredState, STORAGE_KEY } from '../../src/shared/memory-data.js';
import { drawTrailMap } from './trail-map.js';
import { addWoodlands } from './woodlands.js';

const $ = id => document.getElementById(id);
const canvas = $('view'), atlas = $('atlas'), directory = $('places');
const trailMap = $('trail-map'), houseDoor = $('house-door');
const placeCard = document.querySelector('.place');
const viewport = window.visualViewport;
const clamp = THREE.MathUtils.clamp;
const keys = new Set();
const mobile = matchMedia('(pointer: coarse)');
const mapCamera = new THREE.PerspectiveCamera(41, 1, .3, 900);
const eye = new THREE.PerspectiveCamera(67, 1, .08, 750);
eye.rotation.order = 'YXZ';
let layout, nav, renderer, orbit, scene, selected, nearby, walking = false, yaw = 0, pitch = 0;
let destinations = {}, markers = [], drag, previous = 0, dirty = true;
const pins = new Map();
const places = new Map();
const houseDoors = {
  gryffindor: ['画像门', '画像转过脸来，等你报上今晚的口令。', '说出「炉火常明」', '画像点点头，露出门后的暖光。'],
  ravenclaw: ['鹰形门环', '门环问，什么东西分给别人，自己也不会少？', '回答「知识」', '门环微微一响，门后的星图亮了起来。'],
  hufflepuff: ['厨房旁的木桶', '桶箍上刻着一行小字，赫尔加·赫奇帕奇。', '按名字的节奏敲击', '木桶轻轻回响，桶盖向内打开。'],
  slytherin: ['地窖暗门', '石缝里露出一点绿光，蛇纹下方等着一句低语。', '低声说「湖底微光」', '石门滑开，黑湖的绿光照到脚边。'],
};
let shownPlace, outdoorMemories = [];
let route = null, stop = 0, portal = null, water, lastWater = 0;
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
const regionPins = ['hall','tower','boats','pitch','bridge','hut','forest','village','station','glass',
  'willow','shack','ruins','cave','camp','owlery','gamekeeper-trail'];
const explored = new Set();
const explorationKey = 'hogwarts-world-explored';
const temp = new THREE.Vector3();
const moonColor = new THREE.Color(0xb5d7e3), eveningColor = new THREE.Color(0xffba89);
const nightFog = new THREE.Color(0x3d585f), valleyFog = new THREE.Color(0x786477);
let keyLight, ambient, surveyLight;

async function json(url) {
  const res = await fetch(url);
  if (!res.ok) throw Error(url + ' ' + res.status);
  return res.json();
}
function floor(x, z) { return floorHeight(nav, layout.bridge, x, z); }
function display(place) {
  shownPlace = place;
  $('title').textContent = place?.name ?? '高地小径';
  $('english').textContent = place?.en ?? 'Highland Path';
  $('region').textContent = place?.region ?? '霍格沃茨周边';
  $('note').textContent = place?.note ?? '';
  if (walking && place && !explored.has(place.id)) {
    explored.add(place.id);
    pins.get(place.id)?.classList.add('visited');
    renderExploration();
    try { localStorage.setItem(explorationKey, JSON.stringify([...explored])); } catch {}
  }
  updateMemoryActions();
}

function renderExploration() {
  $('explored').max = layout.places.length;
  $('explored').value = explored.size;
  $('explored-count').textContent = explored.size + ' / ' + layout.places.length;
}

function updateMemoryActions() {
  const place = shownPlace?.id ?? 'path';
  const count = outdoorMemories.filter(memory => memory.outdoor.place === place).length;
  $('write-memory').hidden = !walking;
  const read = $('read-memories');
  read.hidden = !count;
  if (count) {
    read.href = '../?' + new URLSearchParams({landmark: place}) + '#memories';
    read.textContent = `此地回忆 ${count}`;
  }
}

function refreshOutdoorMemories() {
  // Storage may be disabled. The map can still load and be explored.
  try {
    outdoorMemories = readStoredState(localStorage.getItem(STORAGE_KEY)).memories.filter(memory => memory.outdoor);
  } catch {
    outdoorMemories = [];
  }
  updateMemoryActions();
}

function writeAtCurrentPosition() {
  const outdoor = {
    place: shownPlace?.id ?? 'path',
    name: $('title').textContent,
    position: [eye.position.x, eye.position.z, Math.atan2(Math.sin(yaw), Math.cos(yaw)), pitch]
  };
  location.href = '../?' + new URLSearchParams({outdoor: JSON.stringify(outdoor)}) + '#memories';
}

function openHouseDoor(id, href) {
  const [name, prompt, action, reply] = houseDoors[id];
  const dialog = $('house-door');
  const button = $('door-action'), response = $('door-reply'), enter = $('door-enter');
  dialog.dataset.house = id;
  $('door-title').textContent = name;
  $('door-prompt').textContent = prompt;
  button.textContent = action;
  button.hidden = false;
  response.textContent = reply;
  response.hidden = true;
  enter.href = href;
  enter.textContent = '进入' + layout.rooms[id] + ' →';
  enter.hidden = true;
  button.onclick = () => {
    button.hidden = true;
    response.hidden = false;
    enter.hidden = false;
    enter.focus();
  };
  enter.onclick = () => history.replaceState(null, '', '?from=' + portal.id);
  keys.clear();
  dialog.showModal();
}

function updateDoors() {
  const destination = walking ? layout.places.find(place=>atDoor(place,eye.position.x,eye.position.z)) ?? null : null;
  if (destination !== portal) {
    portal=destination;
    $('rooms').replaceChildren();
    for (const id of portal?.rooms ?? []) {
      const a=document.createElement('a');
      a.href=destinations[id] + (route?.id === 'arrival' && id === 'hall' ? '&route=arrival' : '');
      a.textContent=houseDoors[id]?.[0] ?? ('进入'+layout.rooms[id]+' ↗');
      a.addEventListener('click', event => {
        if (houseDoors[id]) {
          event.preventDefault();
          openHouseDoor(id, a.href);
        } else {
          history.replaceState(null, '', '?from=' + portal.id);
        }
      });
      $('rooms').append(a);
    }
    if (portal?.passage) {
      const tunnel = document.createElement('a');
      const exit = places.get(portal.passage);
      tunnel.href = '?place=' + exit.id;
      tunnel.textContent = '穿过地道 · ' + exit.name + ' →';
      tunnel.onclick = event => {
        event.preventDefault();
        route = null;
        walk(exit, {returning:true});
        updateGuide();
        history.replaceState(null,'',tunnel.href);
      };
      $('rooms').append(tunnel);
    }
  }
  $('rooms').hidden=!portal;
  if (!portal) return;
  temp.set(portal.door[0],floor(...portal.door)+2.5,portal.door[1]).project(eye);
  const inFront=temp.z>0 && temp.z<1 && Math.abs(temp.x)<.81 && Math.abs(temp.y)<.66;
  $('rooms').classList.toggle('at-door',inFront);
  $('rooms').style.left=inFront?((temp.x+1)*50)+'%':'';
  $('rooms').style.top=inFront?((1-temp.y)*50)+'%':'';
  $('rooms').style.bottom = inFront ? '' : `${atlas.getBoundingClientRect().bottom - placeCard.getBoundingClientRect().top + 8}px`;
}

function follow(itinerary) {
  route=itinerary;stop=0;walk(places.get(route.start));updateGuide();
}
function updateGuide() {
  $('guide').hidden=!route;
  if (!route) return;
  let goal;
  while (stop < route.stops.length) {
    const point=route.stops[stop];
    goal=typeof point==='string'?places.get(point).at:point;
    const threshold=places.get(point);
    const finishDistance=(stop===route.stops.length-1 && threshold?.door)?0.7:2.0;
    if (Math.hypot(goal[0]-eye.position.x,goal[1]-eye.position.z)>finishDistance) break;
    stop++;
  }
  const complete=stop===route.stops.length;
  $('waypoint').textContent=complete
    ? (route.id === 'arrival' ? '进入礼堂，沿长桌之间向前走' : '已抵达'+places.get(route.end).name)
    : route.labels[stop];
  $('remaining').textContent=complete?'':Math.ceil(Math.hypot(goal[0]-eye.position.x,goal[1]-eye.position.z))+' m';
  $('bearing').hidden=complete;
  if(!complete){
    const angle=Math.atan2(goal[0]-eye.position.x,eye.position.z-goal[1])+yaw;
    $('bearing').style.transform='rotate('+angle+'rad)';
  }
}

function openTrailMap() {
  keys.clear();
  const point = walking ? [eye.position.x, eye.position.z] : selected.at;
  drawTrailMap($('trail-chart'), layout, nav, point, route, stop, walking ? yaw : null);
  const locationName = (walking ? shownPlace?.name : selected.name) ?? '高地小径';
  const next = route && route.labels[stop];
  $('trail-map-status').textContent = [walking ? '当前位置 · ' + locationName : '选中地点 · ' + locationName,
    next ? '下一站 · ' + next : route ? '已走完室外路线' : ''].filter(Boolean).join('　');
  trailMap.showModal();
}

function select(place, focus = false) {
  selected = place;
  for (const [id, pin] of pins) pin.classList.toggle('selected', id === place.id);
  display(place);
  if (focus && !walking) {
    const target = new THREE.Vector3(place.at[0], floor(...place.at) + 2, place.at[1]);
    const offset = mapCamera.position.clone().sub(orbit.target).setLength(86);
    orbit.target.copy(target); mapCamera.position.copy(target).add(offset); orbit.update();
  }
  dirty = true;
}
function reset() {
  const narrow = atlas.clientWidth < 680;
  orbit.target.set(narrow ? -6 : 1, 6, narrow ? -13 : -10);
  mapCamera.position.copy(orbit.target).add(narrow ? new THREE.Vector3(-26, 233, -120) : new THREE.Vector3(-20, 240, -154));
  orbit.update(); dirty = true;
}
function zoom(factor) {
  const offset = mapCamera.position.clone().sub(orbit.target);
  offset.setLength(clamp(offset.length()*factor, orbit.minDistance, orbit.maxDistance));
  mapCamera.position.copy(orbit.target).add(offset); orbit.update(); dirty = true;
}
function walk(place, {at=place.at, look=place.look, tilt=place.pitch ?? (place.id === 'boats' ? .045 : .03), returning=false, heading}={}) {
  walking = true; orbit.enabled = false; keys.clear();
  select(place);
  nearby = place;
  const [x,z] = at;
  eye.position.set(x, floor(x,z) + 1.65, z);
  yaw = heading ?? (Math.atan2(x-look[0],z-look[1])+(returning?Math.PI:0)); pitch=returning?0:tilt;
  eye.rotation.set(pitch,yaw,0,'YXZ'); atlas.classList.add('walking');
  $('map-toggle').hidden = false; $('enter').hidden = true; $('touch').hidden = !mobile.matches;
  $('hint').textContent = mobile.matches ? '方向键移动 · 拖动画面转向' : 'WASD / 方向键移动 · 拖动转向 · M 全图';
  display(place);canvas.focus({preventScroll:true});dirty=true;
}
function revisitMemory(outdoor) {
  const place = places.get(outdoor.place);
  const fallback = place ?? layout.places[0];
  const [x,z,heading,tilt] = outdoor.position;
  if (!walkable(nav, layout.bridge, x, z)) {
    walk(fallback);
    return;
  }
  walk(fallback, {at: [x,z], heading, tilt});
  if (!atDoor(place, x, z)) nearby = null;
  display(place);
  $('title').textContent = outdoor.name;
}
function overview() {
  route=null;updateGuide();walking=false;updateDoors();orbit.enabled=true;keys.clear();atlas.classList.remove('walking');
  $('map-toggle').hidden=true;$('touch').hidden=true;$('enter').hidden=false;
  $('hint').textContent=mobile.matches?'拖动旋转 · 双指缩放 · 点选地标':'拖动旋转 · 滚轮缩放 · 选择地标';
  select(nearby ?? selected);history.replaceState(null,'',location.pathname);dirty=true;
}
function createDirectory() {
  const groups = Map.groupBy ? Map.groupBy(layout.places, p => p.region) : layout.places.reduce((m,p) => m.set(p.region,[...(m.get(p.region)??[]),p]),new Map());
  for (const [region, places] of groups) {
    const h = document.createElement('h3'); h.textContent = region; $('list').append(h);
    for (const p of places) {
      const button=document.createElement('button'), en=document.createElement('small');
      button.textContent=p.name; en.textContent=p.en;button.append(en);
      button.onclick=()=>{directory.close();if(walking) overview();select(p,true);$('enter').focus({preventScroll:true});};
      $('list').append(button);
    }
  }
  for(const trip of layout.routes){
    const button=document.createElement('button');button.textContent=trip.name;
    const dest=document.createElement('small');dest.textContent=places.get(trip.end).name;
    button.append(dest);button.onclick=()=>{directory.close();follow(trip);};$('routes').append(button);
  }
  for (const p of layout.places) {
    const el=document.createElement('button');el.className='pin';el.textContent=p.name;
    if (explored.has(p.id)) el.classList.add('visited');
    el.onclick=()=>select(p,true);el.hidden=true;$('markers').append(el);pins.set(p.id,el);
    markers.push({p, el, pos:new THREE.Vector3(p.at[0],floor(...p.at)+3,p.at[1])});
  }
}
function updateMarkers() {
  const w=canvas.clientWidth,h=canvas.clientHeight;
  const lake = temp.set(0,.2,104).project(mapCamera);
  const lakeLabel = $('lake-label');
  lakeLabel.hidden = lake.z >= 1 || Math.abs(lake.x) > .83 || Math.abs(lake.y) > .79;
  lakeLabel.style.left = (lake.x+1)*w/2+'px';
  lakeLabel.style.top = (1-lake.y)*h/2+'px';
  const card=placeCard.getBoundingClientRect();
  const map=canvas.getBoundingClientRect();
  const occupied=[]; const compact=w<680;
  const sorted=[...markers].sort((a,b)=>Number(b.p===selected)-Number(a.p===selected) ||
    regionPins.indexOf(a.p.id)-regionPins.indexOf(b.p.id));
  for (const {p,el,pos} of sorted) {
    const projected=temp.copy(pos).project(mapCamera);
    const x=(projected.x+1)*w/2,y=(1-projected.y)*h/2;
    const selectedPin=p===selected;
    const small=(compact?10:12)*p.name.length/2+13;
    const inUI=x>card.left-map.left-small && x<card.right-map.left+small &&
      y>card.top-map.top-8 && y<card.bottom-map.top+28;
    const overlaps=occupied.some(([px,py,halfWidth])=>Math.abs(px-x)<small+halfWidth&&Math.abs(py-y)<28);
    const show=projected.z<1 && x>small && x<w-small && y>90 && y<h-60 && !inUI &&
       (selectedPin || (regionPins.includes(p.id) && !overlaps));
    el.hidden=!show;
    if(show){el.style.left=x+'px';el.style.top=y+'px';occupied.push([x,y,small]);}
  }
  const meters=55*2*orbit.getDistance()*Math.tan(mapCamera.fov*Math.PI/360)/h;
  $('scale').textContent=Math.round(meters)+' m';
  document.querySelector('.compass i').style.transform='rotate('+(-orbit.getAzimuthalAngle())+'rad)';
}
function move(dt) {
  const forward=Number(keys.has('KeyW')||keys.has('ArrowUp'))-Number(keys.has('KeyS')||keys.has('ArrowDown'));
  const strafe=Number(keys.has('KeyD')||keys.has('ArrowRight'))-Number(keys.has('KeyA')||keys.has('ArrowLeft'));
  if(!forward && !strafe) return;
  const amount=dt*(keys.has('ShiftLeft')||keys.has('ShiftRight')?9:5.5)/Math.hypot(forward,strafe);
  const dx=(Math.cos(yaw)*strafe-Math.sin(yaw)*forward)*amount;
  const dz=(-Math.sin(yaw)*strafe-Math.cos(yaw)*forward)*amount;
  const pos=eye.position;
  if(walkable(nav,layout.bridge,pos.x+dx,pos.z))pos.x+=dx;
  if(walkable(nav,layout.bridge,pos.x,pos.z+dz))pos.z+=dz;
  pos.y=floor(pos.x,pos.z)+1.65;
  let nearest=null, distance=6.5;
  for(const p of layout.places){
    const d=Math.hypot(p.at[0]-pos.x,p.at[1]-pos.z);
    if(d<distance){nearest=p;distance=d;}
  }
  if(nearest!==nearby || nearest!==shownPlace){nearby=nearest;display(nearby);}
  dirty=true;
}
function frame(now) {
  const dt=Math.min(.05,(now-previous)*.001);previous=now;
  if(walking && !directory.open && !houseDoor.open && !trailMap.open) move(dt);
  if (walking && eye.position.z>40 && !reduced.matches && !directory.open && now-lastWater>=1000/60 - 1) {
    water.value=now*.001;lastWater=now;dirty=true;
  }
  if(dirty){
    // The elevated overview camera looks through much more atmosphere than a walker.
    scene.fog.density = walking ? .0043 : .00128;
    const distanceToBridge = Math.hypot(eye.position.x+58,eye.position.z);
    const distanceToGardens = Math.hypot(eye.position.x-41,eye.position.z+38);
    const distanceToVillage = Math.hypot(eye.position.x+18,eye.position.z+79);
    const dusk = walking ? 1 - THREE.MathUtils.smoothstep(distanceToBridge, 13, 48) : 0;
    const gardens = 1 - THREE.MathUtils.smoothstep(distanceToGardens, 17, 50);
    const village = 1 - THREE.MathUtils.smoothstep(distanceToVillage, 27, 56);
    const light = walking ? Math.max(dusk, .42*gardens, .56*village) : .5;
    keyLight.color.lerpColors(moonColor, eveningColor, walking ? .2 + .42*light : .38);
    keyLight.intensity = walking ? 1.48 + 1.1*light : 3.5;
    ambient.intensity = walking ? .72 + .24*light : 1.35;
    surveyLight.visible = !walking;
    scene.fog.color.lerpColors(nightFog,valleyFog,.18 + .36*light);
    renderer.render(scene,walking?eye:mapCamera);
    if(walking){updateDoors();updateGuide();}else updateMarkers();
    dirty=false;
  }
  requestAnimationFrame(frame);
}
function resize() {
  const w=canvas.clientWidth,h=canvas.clientHeight;
  renderer.setSize(w,h,false);
  mapCamera.fov = THREE.MathUtils.radToDeg(2*Math.atan(
    Math.tan(THREE.MathUtils.degToRad(41)/2) / Math.max(.51, Math.min(1, w/h))
  ));
  for(const c of [mapCamera,eye]){c.aspect=w/h;c.updateProjectionMatrix();}
  dirty=true;
}
function fitVisualViewport() {
  const style = document.documentElement.style;
  style.setProperty('--viewport-left', viewport.offsetLeft + 'px');
  style.setProperty('--viewport-top', viewport.offsetTop + 'px');
  style.setProperty('--viewport-width', viewport.width + 'px');
  style.setProperty('--viewport-height', viewport.height + 'px');
  dirty = true;
}
function controls() {
  $('directory').onclick=()=>{keys.clear();directory.showModal();}; $('close').onclick=()=>directory.close();
  directory.addEventListener('click',e=>{if(e.target===directory && e.clientX<directory.getBoundingClientRect().left)directory.close();});
  $('arrival').onclick=()=>follow(layout.routes.find(r=>r.id==='arrival'));
  $('foot-map').onclick=openTrailMap;
  $('write-memory').onclick=writeAtCurrentPosition;
  $('enter').onclick=()=>walk(selected);$('map-toggle').onclick=overview;
  $('reset').onclick=reset;$('zoom-in').onclick=()=>zoom(.78);$('zoom-out').onclick=()=>zoom(1.28);
  document.addEventListener('keydown',e=>{
    if(directory.open||houseDoor.open||trailMap.open||e.ctrlKey||e.altKey||e.metaKey) return;
    if(e.code==='KeyM' && walking){overview();return;}
    if(!walking || !/^(Key[WASD]|Arrow(Up|Down|Left|Right)|Shift(Left|Right))$/.test(e.code))return;
    e.preventDefault();keys.add(e.code);
  });
  document.addEventListener('keyup',e=>keys.delete(e.code));
  window.addEventListener('blur',()=>{keys.clear();drag=null;});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)keys.clear();});
  for(const button of $('touch').querySelectorAll('button')){
    button.onpointerdown=e=>{e.preventDefault();button.setPointerCapture(e.pointerId);keys.add(button.dataset.key);};
    button.onlostpointercapture=()=>keys.delete(button.dataset.key);
  }
  canvas.addEventListener('pointerdown',e=>{if(!walking||drag)return;canvas.setPointerCapture(e.pointerId);drag={id:e.pointerId,x:e.clientX,y:e.clientY};});
  canvas.addEventListener('pointermove',e=>{
    if(!walking||e.pointerId!==drag?.id)return;
    yaw-=(e.clientX-drag.x)*.005;pitch=clamp(pitch-(e.clientY-drag.y)*.005,-1.28,1.28);
    drag.x=e.clientX;drag.y=e.clientY;eye.rotation.set(pitch,yaw,0,'YXZ');dirty=true;
  });
  canvas.addEventListener('lostpointercapture',()=>{drag=null;});
}
function lightScene() {
  scene = new THREE.Scene(); scene.fog=new THREE.FogExp2(0x576e80,.0043);
  ambient = new THREE.HemisphereLight(0xc4d4dd,0x918783,.69);
  scene.add(ambient);
  const sun=new THREE.DirectionalLight(0xe0e9fc,1.48);sun.position.set(-33,42,-77);
  surveyLight = new THREE.DirectionalLight(0xffecd2, 1.35);
  surveyLight.position.set(87,127,-31);
  scene.add(surveyLight);
  keyLight = sun;
  sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);
  Object.assign(sun.shadow.camera,{left:-115,right:115,top:105,bottom:-105,near:1,far:310});sun.shadow.camera.updateProjectionMatrix();
  sun.shadow.normalBias=.11;sun.shadow.bias=-.00025;scene.add(sun);
}
async function start() {
  if(location.protocol==='file:') throw Error('请通过本地网页服务打开地图。');
  renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.75));renderer.shadowMap.enabled=true;
  renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.shadowMap.autoUpdate=false;
  lightScene();
  [layout,nav,destinations]=await Promise.all([json('./layout.json'),json('./navigation.json'),json('./rooms.json'),evening(scene)]);
  for(const p of layout.places)places.set(p.id,p);
  try {
    for (const id of JSON.parse(localStorage.getItem(explorationKey) ?? '[]')) {
      if (places.has(id)) explored.add(id);
    }
  } catch {}
  renderExploration();
  const decoder = new DRACOLoader().setDecoderPath('../assets/draco/');
  let gltf;
  try {
    gltf = await new GLTFLoader().setDRACOLoader(decoder).loadAsync('./grounds.glb');
  } finally {
    decoder.dispose();
  }
  let surface;
  gltf.scene.traverse(obj=>{
    if(!obj.isMesh)return;
    obj.castShadow=true;obj.receiveShadow=true;
    if(obj.material.name==='Lake') surface=obj;
    if(obj.material.name==='Water glint')obj.visible=false;
    if(obj.material.name==='Pavilion glass') obj.castShadow=false;
    if(obj.material.name==='Highland turf and exposed shore') tintMeadows(obj.geometry);
    if(obj.material.name.startsWith('Silver fir')){
      obj.material.transparent=false;obj.material.alphaTest=.36;obj.material.depthWrite=true;
      obj.material.side=THREE.DoubleSide;obj.castShadow=false;
    }
  });
  for (const [x,y,z] of layout.shoreLights) {
    const lamp = new THREE.PointLight(0xffc189, 12, 8);
    lamp.position.set(x,y+.20,z+.27);
    scene.add(lamp);
  }
  scene.add(gltf.scene);
  addWoodlands(scene, layout, nav);
  water = await blackLake(scene, nav, renderer, surface);
  renderer.shadowMap.needsUpdate=true;
  orbit=new OrbitControls(mapCamera,canvas);orbit.enablePan=false;orbit.minDistance=35;orbit.maxDistance=320;
  orbit.minPolarAngle=.09;orbit.maxPolarAngle=Math.PI*.46;orbit.addEventListener('change',()=>{dirty=true;});
  createDirectory();resize();controls();reset();
  refreshOutdoorMemories();
  window.addEventListener('pageshow', event => { if (event.persisted) refreshOutdoorMemories(); });
  window.addEventListener('storage', event => {
    if (event.key === STORAGE_KEY || event.key === null) refreshOutdoorMemories();
  });
  const query=new URLSearchParams(location.search);
  const memory=outdoorMemories.find(({id}) => id === query.get('memory'));
  const returning=places.get(query.get('from'));
  const landmark=places.get(query.get('place'));
  const view=layout.views.find(v=>v.id===query.get('view'));
  const trip=layout.routes.find(r=>r.id===query.get('route'));
  if (memory) revisitMemory(memory.outdoor);
  else if (view) {
    const near=layout.places.reduce((a,b)=>Math.hypot(b.at[0]-view.at[0],b.at[1]-view.at[1])<Math.hypot(a.at[0]-view.at[0],a.at[1]-view.at[1])?b:a);
    walk(near,{...view,tilt:view.pitch});
    $('title').textContent=view.name;
    if(!atDoor(near,...view.at))nearby=null;
  } else if(returning)walk(returning,{returning:true});
  else if(trip)follow(trip);
  else if(landmark)walk(landmark);
  else select(layout.places[0]);
  $('loading').hidden=true;$('enter').disabled=false;$('foot-map').disabled=false;
  new ResizeObserver(resize).observe(atlas);requestAnimationFrame(frame);
}

function tintMeadows(geometry) {
  const {position, color} = geometry.attributes;
  if (!color) return;
  for (let i = 0; i < position.count; i++) {
    const x = position.getX(i), z = position.getZ(i);
    const slope = Math.max(0, geometry.attributes.normal.getY(i));
    const patch = .5+.24*Math.sin(.093*x+.17*z)+.19*Math.cos(.11*x-.153*z);
    const meadow = THREE.MathUtils.smoothstep(slope,.63,.94);
    color.setXYZ(i,Math.min(1,color.getX(i)*(1+meadow*(.23+.62*patch))),
      Math.min(1,color.getY(i)*(1+meadow*(.28+.70*patch))),color.getZ(i)*(1-meadow*.19));
  }
}
$('retry').onclick=()=>location.reload();
if (viewport) {
  fitVisualViewport();
  viewport.addEventListener('resize', fitVisualViewport);
  viewport.addEventListener('scroll', fitVisualViewport);
}
start().catch(error=>{
  console.error(error);
  $('loading').firstElementChild.textContent=location.protocol==='file:'?'三维地图需要通过 HTTP 打开。请使用工程里的启动脚本。':'地图加载失败，请检查浏览器的 WebGL 与本地资源。';
  $('retry').hidden=false;
});
