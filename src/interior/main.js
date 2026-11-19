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
import {SCENES,INTERIORS} from '../shared/scenes.js';
import {bindSceneShell,groundsEntrance} from '../shared/scene-shell.js';
import {canStand,movePlayer,inputVector,acceptNavigationKey} from './navigation.js';
import './style.css';

const $=s=>document.querySelector(s),keys=new Set();
const requested=new URLSearchParams(location.search).get('scene');
const id=requested||'potions',entry=SCENES[id];
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const state=window.__interior={id,ready:false,error:null,frames:0,mode:'view',effects:!reduced,drawCalls:0,triangles:0};
let renderer,scene,camera,composer,bloom,fxaa,orbit,meta,dust;
let walking=false,dragging=false,lastX=0,lastY=0,yaw=0,pitch=0,hidden=false,previous=performance.now(),elapsed=0;
const frameTimes=[];

function progress(value,label){$('#load-bar').style.width=value+'%';$('#load-percent').textContent=Math.round(value)+'%';$('#load-label').textContent=label;}
function fail(error){
  state.error=String(error);state.ready=false;stopWalk();renderer?.setAnimationLoop(null);
  $('#loading').classList.remove('done');$('#loading').removeAttribute('aria-hidden');
  $('#loading h1').textContent='这扇门暂时没有打开';$('#load-label').textContent='场景加载失败，请检查本地服务后重试。';
  $('#load-percent').textContent='';$('#retry').hidden=false;$('#explore').disabled=true;console.error(error);
}
$('#retry').onclick=()=>location.reload();
if(!INTERIORS.includes(id)){
  $('#loading h1').textContent='没有找到这间房间';$('#load-label').textContent='请返回回忆录，选择想去的地方。';$('#load-percent').textContent='';
}else{
  document.title=entry.name+' · 魔法留声';$('#room-name').textContent=entry.name;$('#room-english').textContent=entry.english;
  $('#room-description').textContent=entry.description;$('#room-caption').textContent='魔法留声 / '+entry.english;
  $('#scene').setAttribute('aria-label',entry.name+'三维场景');bindSceneShell(stopWalk,id);
  try{await init();}catch(error){fail(error);}
}

async function init(){
  progress(4,'正在寻找熟悉的房间…');
  const base='../rooms/'+id+'/';
  const response=await fetch(base+'metadata.json',{signal:AbortSignal.timeout(30000)});
  if(!response.ok)throw new Error('Metadata HTTP '+response.status);
  meta=await response.json();
  if(!meta.cameras?.length||!meta.spawn||!meta.bounds)throw new Error('Incomplete scene metadata');
  if(!canStand(meta.spawn.position[0],meta.spawn.position[2],meta))throw new Error('Scene entrance overlaps an obstacle');
  renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
  renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure=meta.exposure??1;renderer.info.autoReset=false;
  renderer.domElement.tabIndex=0;$('#scene').append(renderer.domElement);
  renderer.domElement.addEventListener('webglcontextlost',event=>{event.preventDefault();fail('WebGL context lost');});
  scene=new THREE.Scene();scene.background=new THREE.Color(meta.background||'#18201b');
  camera=new THREE.PerspectiveCamera(meta.fov||58,1,.05,120);camera.rotation.order='YXZ';
  orbit=new OrbitControls(camera,renderer.domElement);orbit.enablePan=false;orbit.enableDamping=!reduced;orbit.dampingFactor=.08;
  orbit.minDistance=1.6;orbit.maxDistance=meta.orbitMaxDistance||18;orbit.minPolarAngle=.35;orbit.maxPolarAngle=1.65;
  composer=new EffectComposer(renderer);composer.addPass(new RenderPass(scene,camera));
  bloom=new UnrealBloomPass(new THREE.Vector2(1,1),.16,.5,1.3);composer.addPass(bloom);composer.addPass(new OutputPass());
  fxaa=new ShaderPass(FXAAShader);composer.addPass(fxaa);resize();
  if(meta.lighting==='pbr'){
    scene.add(new THREE.HemisphereLight(meta.skyColor||0xadb8bf,meta.groundColor||0x34291d,meta.ambientIntensity??1.2));
    for(const light of meta.lights||[]){const l=new THREE.PointLight(light.color||0xffd49a,light.intensity||15,light.distance||25,2);l.position.set(...light.position);scene.add(l);}
  }
  const draco=new DRACOLoader();draco.setDecoderPath('../assets/draco/');draco.setWorkerLimit(2);
  const loader=new GLTFLoader();loader.setDRACOLoader(draco);const start=performance.now();let timeout;
  try{
    const task=loader.loadAsync(base+'scene.glb',event=>progress(event.total?10+event.loaded/event.total*76:25,'正在展开'+entry.short+'的光影…'));
    const gltf=await Promise.race([task,new Promise((_,reject)=>{timeout=setTimeout(()=>reject(new Error('Model load timed out')),90000);})]);
    gltf.scene.traverse(object=>{
      if(!object.isMesh)return;
      for(const material of Array.isArray(object.material)?object.material:[object.material]){
        if(material.map)material.map.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
      }
    });
    scene.add(gltf.scene);
  }finally{clearTimeout(timeout);draco.dispose();}
  dust=createDust();scene.add(dust);dust.visible=state.effects;bloom.enabled=state.effects;updateEffectsButton();
  meta.cameras.forEach((view,index)=>{
    const button=document.createElement('button');button.dataset.view=index;
    const number=document.createElement('b');number.textContent=String(index+1).padStart(2,'0');
    const label=document.createElement('span');label.textContent=view.name;button.append(number,label);button.onclick=()=>setView(index);$('#view-buttons').append(button);
  });
  setView(0);bindControls();if(groundsEntrance(id))await startWalk(false);progress(94,'正在点亮房间…');await renderer.compileAsync(scene,camera);
  state.ready=true;state.loadMs=Math.round(performance.now()-start);state.assetTriangles=meta.triangles;
  $('#explore').disabled=false;progress(100,'欢迎回来');$('#loading').classList.add('done');$('#loading').setAttribute('aria-hidden','true');
  renderer.setAnimationLoop(animate);
}
function createDust(){
  const b=meta.bounds,data=new Float32Array(180*3);
  for(let i=0;i<180;i++){const a=i*2.399963;data[i*3]=(b.minX+b.maxX)/2+Math.sin(a)*Math.sqrt(i/180)*(b.maxX-b.minX)*.4;data[i*3+1]=.5+(i*.618%1)*3.5;data[i*3+2]=(b.minZ+b.maxZ)/2+Math.cos(a)*Math.sqrt(i/180)*(b.maxZ-b.minZ)*.4;}
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(data,3));
  return new THREE.Points(geometry,new THREE.PointsMaterial({color:meta.dustColor||0xe5cd94,size:.013,transparent:true,opacity:.34,depthWrite:false}));
}
function syncAngles(){yaw=camera.rotation.y;pitch=camera.rotation.x;}
function setView(index){
  stopWalk();const view=meta.cameras[index];orbit.enabled=false;orbit.reset();
  camera.fov=view.fov||meta.fov||58;camera.updateProjectionMatrix();
  camera.position.set(...view.position);camera.lookAt(...view.target);orbit.target.set(...view.target);orbit.enabled=true;orbit.update();orbit.saveState();syncAngles();
  state.mode='view';state.view=index;$('#control-hint').textContent='拖动旋转 · 滚轮缩放 · 漫游后 WASD 行走';
  document.querySelectorAll('[data-view]').forEach(button=>button.classList.toggle('active',Number(button.dataset.view)===index));
}
function stopWalk(){
  walking=false;keys.clear();dragging=false;document.body.classList.remove('walking');$('#crosshair').hidden=true;$('#explore-label').textContent='开始漫游';
  if(document.pointerLockElement)document.exitPointerLock();
  if(state.mode==='walk'){state.mode='look';$('#control-hint').textContent='拖动画面环顾 · 选择观景点返回全景';}
}
async function startWalk(lockPointer=true){
  if(walking){stopWalk();return;}
  keys.clear();orbit.enabled=false;camera.position.set(...meta.spawn.position);camera.lookAt(...meta.spawn.target);syncAngles();
  camera.fov=meta.spawn.fov||62;camera.updateProjectionMatrix();
  walking=true;state.mode='walk';document.body.classList.add('walking');$('#crosshair').hidden=false;$('#explore-label').textContent='退出漫游';
  $('#control-hint').textContent='WASD 行走 · Shift 加快 · Esc 退出';renderer.domElement.focus();
  if(lockPointer&&matchMedia('(pointer:fine)').matches)try{await renderer.domElement.requestPointerLock();}catch{$('#control-hint').textContent='按住画面拖动环顾 · WASD 行走 · Esc 退出';}
}
function look(dx,dy){yaw-=dx*.0023;pitch=THREE.MathUtils.clamp(pitch-dy*.0023,-1.15,1.2);camera.rotation.set(pitch,yaw,0,'YXZ');}
function toggleUI(){hidden=!hidden;document.body.classList.toggle('ui-hidden',hidden);$('#interface').inert=hidden;$('#restore-ui').hidden=!hidden;(hidden?$('#restore-ui'):$('#hide-ui')).focus();}
function updateEffectsButton(){$('#effects').setAttribute('aria-pressed',String(state.effects));$('#effects').textContent='微光 · '+(state.effects?'开':'关');}
function bindControls(){
  const canvas=renderer.domElement;
  $('#explore').onclick=startWalk;$('#hide-ui').onclick=toggleUI;$('#restore-ui').onclick=toggleUI;
  $('#effects').onclick=()=>{state.effects=!state.effects;dust.visible=state.effects;bloom.enabled=state.effects;updateEffectsButton();};
  $('#help').onclick=()=>{stopWalk();$('#help-dialog').showModal();};$('#close-help').onclick=()=>$('#help-dialog').close();$('#quality').onchange=resize;
  canvas.addEventListener('pointerdown',event=>{if(orbit.enabled||document.pointerLockElement)return;dragging=true;lastX=event.clientX;lastY=event.clientY;canvas.setPointerCapture(event.pointerId);});
  canvas.addEventListener('pointermove',event=>{if(orbit.enabled)return;if(document.pointerLockElement===canvas)look(event.movementX,event.movementY);else if(dragging){look(event.clientX-lastX,event.clientY-lastY);lastX=event.clientX;lastY=event.clientY;}});
  for(const name of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(name,()=>dragging=false);
  document.addEventListener('pointerlockchange',()=>{if(!document.pointerLockElement&&walking)stopWalk();});
  document.addEventListener('keydown',event=>{
    if(!acceptNavigationKey(event.target,$('#help-dialog').open))return;
    if(walking&&['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','ShiftLeft','ShiftRight'].includes(event.code)){keys.add(event.code);event.preventDefault();}
    if(!event.repeat){if(event.code==='KeyR')setView(0);if(event.code==='KeyH')toggleUI();if(event.code==='Escape')stopWalk();}
  });
  document.addEventListener('keyup',event=>keys.delete(event.code));window.addEventListener('blur',()=>{keys.clear();dragging=false;});
  document.querySelectorAll('[data-key]').forEach(button=>{
    button.addEventListener('pointerdown',event=>{event.preventDefault();if(!walking)return;keys.add(button.dataset.key);button.setPointerCapture(event.pointerId);});
    for(const name of ['pointerup','pointercancel','lostpointercapture'])button.addEventListener(name,()=>keys.delete(button.dataset.key));
  });
  window.addEventListener('resize',resize);
}
function resize(){
  const high=$('#quality').value==='high',ratio=Math.min(devicePixelRatio,high?1.5:1,(high?2560:1920)/innerWidth);
  renderer.setPixelRatio(ratio);renderer.setSize(innerWidth,innerHeight);composer.setPixelRatio(ratio);composer.setSize(innerWidth,innerHeight);
  fxaa.material.uniforms.resolution.value.set(1/(innerWidth*ratio),1/(innerHeight*ratio));camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();
  state.renderSize=[Math.round(innerWidth*ratio),Math.round(innerHeight*ratio)];
}
function animate(now){
  const frameDt=(now-previous)/1000,dt=Math.min(.05,Math.max(0,frameDt));previous=now;elapsed+=dt;
  if(orbit.enabled){
    orbit.update();const b=meta.bounds;camera.position.x=THREE.MathUtils.clamp(camera.position.x,b.minX+.15,b.maxX-.15);camera.position.z=THREE.MathUtils.clamp(camera.position.z,b.minZ+.15,b.maxZ-.15);camera.position.y=THREE.MathUtils.clamp(camera.position.y,.45,meta.maxViewHeight||7.5);camera.lookAt(orbit.target);syncAngles();
  }
  if(walking&&!$('#help-dialog').open&&keys.size){
    const dir=inputVector(keys,yaw),speed=keys.has('ShiftLeft')||keys.has('ShiftRight')?3.3:2;
    const p=movePlayer(camera.position,{x:dir.x*speed*dt,z:dir.z*speed*dt},meta);camera.position.x=p.x;camera.position.z=p.z;camera.position.y=meta.spawn.position[1];
  }
  if(!reduced&&state.effects)dust.rotation.y=Math.sin(elapsed*.03)*.035;
  renderer.info.reset();composer.render();state.frames++;
  if(frameDt>0&&frameDt<.5){frameTimes.push(frameDt);if(frameTimes.length>120)frameTimes.shift();state.fps=Math.round(frameTimes.length/frameTimes.reduce((a,b)=>a+b,0));}
  state.drawCalls=renderer.info.render.calls;state.triangles=renderer.info.render.triangles;state.camera={x:camera.position.x,y:camera.position.y,z:camera.position.z,yaw,pitch};
}
document.addEventListener('visibilitychange',()=>{keys.clear();dragging=false;previous=performance.now();if(state.ready&&!state.error)renderer.setAnimationLoop(document.hidden?null:animate);});
window.addEventListener('pagehide',()=>{keys.clear();renderer?.setAnimationLoop(null);});
window.addEventListener('pageshow',()=>{previous=performance.now();if(state.ready&&!state.error&&!document.hidden)renderer.setAnimationLoop(animate);});
