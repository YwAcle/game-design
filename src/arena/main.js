import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {DRACOLoader} from 'three/addons/loaders/DRACOLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {ShaderPass} from 'three/addons/postprocessing/ShaderPass.js';
import {FXAAShader} from 'three/addons/shaders/FXAAShader.js';
import {movePlayer,inputVector,acceptNavigationKey} from './navigation.js';
import {createMagic} from './magic.js';
import './style.css';
import '../shared/scene-shell.css';
import {sceneViewFromQuery} from '../shared/memory-data.js';
import {bindSceneShell,groundsEntrance,nearestView} from '../shared/scene-shell.js';
const $=s=>document.querySelector(s),keys=new Set(),reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const state=window.__arena={ready:false,error:null,frames:0,fps:0,drawCalls:0,triangles:0,mode:'orbit',magic:true};
let renderer,scene,camera,composer,bloom,fxaa,orbit,magic,walk=false,drag=false,lastX=0,lastY=0,yaw=0,pitch=0,hidden=false,elapsed=0,previous=performance.now(),frameTimes=[];
const bookmarks={overview:{pos:[7.8,4.6,11.5],target:[-1,2.2,-4]},court:{pos:[0,1.75,10.7],target:[0,3.2,-8]},gallery:{pos:[-10.5,6.6,-13.6],target:[0,2,0]}};
function progress(v,label){$('#load-bar').style.width=`${v}%`;$('#load-percent').textContent=`${Math.round(v)}%`;$('#load-label').textContent=label;}
function fail(error){renderer?.setAnimationLoop(null);walk=false;keys.clear();state.error=String(error);$('#loading').removeAttribute('aria-hidden');$('#loading').classList.remove('done');$('#loading h1').textContent='决斗场暂未打开';$('#load-label').textContent='场景加载失败，请检查本地服务后重试。';$('#load-percent').textContent='';$('#retry').hidden=false;console.error(error);}
$('#retry').onclick=()=>location.reload();
try{await init();}catch(error){fail(error);}
async function init(){
  renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.92;renderer.info.autoReset=false;
  renderer.domElement.tabIndex=0;$('#scene').appendChild(renderer.domElement);renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();fail('WebGL context lost');});
  scene=new THREE.Scene();scene.background=new THREE.Color('#171e23');scene.fog=new THREE.FogExp2('#263039',.005);
  camera=new THREE.PerspectiveCamera(51.5,1,.07,100);camera.rotation.order='YXZ';
  orbit=new OrbitControls(camera,renderer.domElement);orbit.enablePan=false;orbit.enableDamping=!reduced;orbit.dampingFactor=.08;orbit.minDistance=7;orbit.maxDistance=22;orbit.minPolarAngle=.40;orbit.maxPolarAngle=1.48;
  // A postprocess AA pass avoids a black HDR multisample resolve on this driver.
  composer=new EffectComposer(renderer);composer.addPass(new RenderPass(scene,camera));bloom=new UnrealBloomPass(new THREE.Vector2(1,1),.30,.55,1.2);composer.addPass(bloom);composer.addPass(new OutputPass());fxaa=new ShaderPass(FXAAShader);composer.addPass(fxaa);
  setView('overview');resize();
  const draco=new DRACOLoader();draco.setDecoderPath('../assets/draco/');draco.setWorkerLimit(2);const loader=new GLTFLoader();loader.setDRACOLoader(draco);
  const start=performance.now();let timeout;
  const task=loader.loadAsync('./assets/dueling-arena.glb',e=>progress(e.total?e.loaded/e.total*85:20,'正在展开看台、石柱与高窗…'));
  let gltf;try{gltf=await Promise.race([task,new Promise((_,reject)=>{timeout=setTimeout(()=>reject(new Error('Model load timed out')),90000);})]);}finally{clearTimeout(timeout);}
  const response=await fetch('./assets/metadata.json');if(!response.ok)throw new Error(`Metadata HTTP ${response.status}`);const meta=await response.json();
  gltf.scene.traverse(o=>{if(o.isMesh)for(const m of Array.isArray(o.material)?o.material:[o.material]){if(m.map)m.map.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());}});
  scene.add(gltf.scene);magic=createMagic();scene.add(magic.group);progress(94,'正在唤醒魔咒余光…');
  bindControls();
  bindSceneShell(stopWalk, 'arena', () => state.mode === 'orbit'
    ? document.querySelector('[data-view].active').dataset.view
    : nearestView(camera.position, Object.entries(bookmarks).map(([id, view]) => [id, view.pos])));
  const savedView = sceneViewFromQuery(location.search, 'arena');
  if (savedView) setView(savedView);
  else if (groundsEntrance('arena')) await startWalk(false);
  await renderer.compileAsync(scene,camera);progress(100,'欢迎来到决斗俱乐部');
  state.loadMs=Math.round(performance.now()-start);state.assetTriangles=meta.triangles;state.ready=true;$('#explore').disabled=false;$('#loading').classList.add('done');$('#loading').setAttribute('aria-hidden','true');draco.dispose();renderer.setAnimationLoop(animate);
}
function syncAngles(){yaw=camera.rotation.y;pitch=camera.rotation.x;}
function setView(name){
  stopWalk();const b=bookmarks[name];keys.clear();orbit.enabled=false;orbit.reset();camera.position.set(...b.pos);camera.lookAt(...b.target);syncAngles();orbit.target.set(...b.target);
  orbit.enabled=name!=='court';state.mode=orbit.enabled?'orbit':'view';if(orbit.enabled){orbit.update();orbit.saveState();}
  $('#control-hint').textContent=orbit.enabled?'拖动旋转 · 滚轮缩放 · 入场后 WASD 行走':'拖动环顾 · 点击入场后 WASD 行走';
  document.querySelectorAll('[data-view]').forEach(e=>e.classList.toggle('active',e.dataset.view===name));
}
function stopWalk(){
  walk=false;keys.clear();document.body.classList.remove('walking');$('#crosshair').hidden=true;$('#explore-label').textContent='进入决斗场';if(document.pointerLockElement)document.exitPointerLock();
  if(state.mode==='walk')state.mode='view';
}
async function startWalk(lockPointer=true){
  if(walk){stopWalk();return;}setView('court');walk=true;state.mode='walk';document.body.classList.add('walking');$('#crosshair').hidden=false;$('#explore-label').textContent='退出漫游';renderer.domElement.focus();
  if(lockPointer&&matchMedia('(pointer:fine)').matches)try{await renderer.domElement.requestPointerLock();}catch{$('#control-hint').textContent='按住画面拖动环顾 · WASD 行走 · Esc 退出';}
}
function look(dx,dy){yaw-=dx*.0023;pitch=THREE.MathUtils.clamp(pitch-dy*.0023,-1.1,1.25);camera.rotation.set(pitch,yaw,0,'YXZ');}
function toggleUI(){hidden=!hidden;document.body.classList.toggle('ui-hidden',hidden);$('#interface').inert=hidden;$('#restore-ui').hidden=!hidden;(hidden?$('#restore-ui'):$('#hide-ui')).focus();}
function bindControls(){
  const canvas=renderer.domElement;
  $('#explore').onclick=startWalk;$('#hide-ui').onclick=toggleUI;$('#restore-ui').onclick=toggleUI;
  $('#magic').onclick=()=>{state.magic=!state.magic;magic.group.visible=state.magic;$('#magic').setAttribute('aria-pressed',String(state.magic));$('#magic').textContent=`魔咒光效 · ${state.magic?'开':'关'}`;};
  $('#help').onclick=()=>{stopWalk();keys.clear();$('#help-dialog').showModal();};$('#close-help').onclick=()=>$('#help-dialog').close();
  document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>setView(b.dataset.view));$('#quality').onchange=resize;
  canvas.addEventListener('pointerdown',e=>{if(!orbit.enabled&&!document.pointerLockElement){drag=true;lastX=e.clientX;lastY=e.clientY;canvas.setPointerCapture(e.pointerId);}});
  canvas.addEventListener('pointermove',e=>{if(orbit.enabled)return;if(document.pointerLockElement===canvas)look(e.movementX,e.movementY);else if(drag){look(e.clientX-lastX,e.clientY-lastY);lastX=e.clientX;lastY=e.clientY;}});
  for(const name of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(name,()=>drag=false);
  document.addEventListener('pointerlockchange',()=>{if(!document.pointerLockElement&&walk)stopWalk();});
  document.addEventListener('keydown',e=>{
    if(!acceptNavigationKey(e.target,$('#help-dialog').open))return;
    if(walk&&['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','ShiftLeft','ShiftRight'].includes(e.code)){keys.add(e.code);e.preventDefault();}
    if(!e.repeat){if(e.code==='KeyR')setView('overview');if(e.code==='KeyH')toggleUI();if(e.code==='Escape')stopWalk();}
  });
  document.addEventListener('keyup',e=>keys.delete(e.code));window.addEventListener('blur',()=>{keys.clear();drag=false;});document.addEventListener('visibilitychange',()=>{keys.clear();previous=performance.now();});
  document.querySelectorAll('[data-key]').forEach(button=>{button.addEventListener('pointerdown',e=>{e.preventDefault();if(!walk)startWalk();keys.add(button.dataset.key);button.setPointerCapture(e.pointerId);});for(const name of ['pointerup','pointercancel','lostpointercapture'])button.addEventListener(name,()=>keys.delete(button.dataset.key));});
  window.addEventListener('resize',resize);
}
function resize(){
  const high=$('#quality').value==='high',ratio=Math.min(devicePixelRatio,high?1.5:1,(high?2560:1920)/innerWidth);
  renderer.setPixelRatio(ratio);renderer.setSize(innerWidth,innerHeight);composer.setPixelRatio(ratio);composer.setSize(innerWidth,innerHeight);fxaa.material.uniforms.resolution.value.set(1/(innerWidth*ratio),1/(innerHeight*ratio));camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();state.renderSize=[Math.round(innerWidth*ratio),Math.round(innerHeight*ratio)];
}
function animate(now){
  const frameDt=(now-previous)/1000,dt=Math.min(.05,Math.max(0,frameDt));previous=now;elapsed+=dt;
  if(orbit.enabled){orbit.update();camera.position.x=THREE.MathUtils.clamp(camera.position.x,-12.1,12.1);camera.position.z=THREE.MathUtils.clamp(camera.position.z,-15,15);camera.position.y=Math.min(camera.position.y,13.4);camera.lookAt(orbit.target);syncAngles();}
  if(!$('#help-dialog').open&&walk&&keys.size){const dir=inputVector(keys,yaw),speed=(keys.has('ShiftLeft')||keys.has('ShiftRight'))?4.2:2.5;const p=movePlayer(camera.position,{x:dir.x*speed*dt,z:dir.z*speed*dt});camera.position.x=p.x;camera.position.z=p.z;camera.position.y=1.75;}
  if(!reduced)magic.update(elapsed);renderer.info.reset();composer.render();state.frames++;
  if(frameDt>0&&frameDt<.5){frameTimes.push(frameDt);if(frameTimes.length>90)frameTimes.shift();state.fps=Math.round(frameTimes.length/frameTimes.reduce((a,b)=>a+b,0));}
  state.drawCalls=renderer.info.render.calls;state.triangles=renderer.info.render.triangles;state.camera={x:camera.position.x,y:camera.position.y,z:camera.position.z,yaw,pitch};
}


document.addEventListener('visibilitychange',()=>{if(state.ready&&!state.error)renderer.setAnimationLoop(document.hidden?null:animate);});
window.addEventListener('pagehide',()=>{keys.clear();renderer?.setAnimationLoop(null);});
window.addEventListener('pageshow',()=>{previous=performance.now();if(state.ready&&!state.error&&!document.hidden)renderer.setAnimationLoop(animate);});
