import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {DRACOLoader} from 'three/addons/loaders/DRACOLoader.js';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {movePlayer,inputVector,acceptNavigationKey} from './navigation.js';
import './style.css';
import '../shared/scene-shell.css';
import {bindSceneShell,groundsEntrance} from '../shared/scene-shell.js';

const $=s=>document.querySelector(s),keys=new Set();
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const state=window.__hall={ready:false,error:null,frames:0,fps:0,drawCalls:0,triangles:0,mode:'view',camera:null};
let renderer,scene,camera,composer,bloom,flameMesh,dust,walk=false,drag=false,lastX=0,lastY=0,yaw=-Math.PI/2,pitch=.135,hidden=false;
let target=null,elapsed=0,previous=performance.now(),frameTimes=[];
const bookmarks={aisle:{x:-5.9,y:1.8,z:0,yaw:-Math.PI/2,pitch:.095},feast:{x:-5.85,y:1.72,z:3.9,yaw:-1.88,pitch:.06},window:{x:19.9,y:1.85,z:0,yaw:-Math.PI/2,pitch:.53}};
function progress(value,label){$('#load-bar').style.width=`${value}%`;$('#load-percent').textContent=`${Math.round(value)}%`;$('#load-label').textContent=label;}
function fail(error){renderer?.setAnimationLoop(null);walk=false;keys.clear();state.error=String(error);$('#loading').removeAttribute('aria-hidden');$('#loading').classList.remove('done');$('#loading h1').textContent='礼堂暂未打开';$('#load-label').textContent='场景加载失败，请检查本地服务后重试。';$('#load-percent').textContent='';$('#retry').hidden=false;console.error(error);}
$('#retry').onclick=()=>location.reload();
try{await init();}catch(error){fail(error);}

async function init(){
  renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
  renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.82;
  renderer.info.autoReset=false;renderer.domElement.tabIndex=0;$('#scene').appendChild(renderer.domElement);
  renderer.domElement.addEventListener('webglcontextlost',event=>{event.preventDefault();fail('WebGL context lost');});
  scene=new THREE.Scene();scene.background=new THREE.Color('#182025');scene.fog=new THREE.FogExp2('#283334',.008);
  camera=new THREE.PerspectiveCamera(54.9,1,.06,100);camera.rotation.order='YXZ';setView('aisle',false);
  composer=new EffectComposer(renderer);composer.addPass(new RenderPass(scene,camera));
  bloom=new UnrealBloomPass(new THREE.Vector2(1,1),.30,.65,.87);composer.addPass(bloom);composer.addPass(new OutputPass());resize();
  const draco=new DRACOLoader();draco.setDecoderPath('../assets/draco/');draco.setWorkerLimit(2);
  const loader=new GLTFLoader();loader.setDRACOLoader(draco);
  const start=performance.now();
  let timeout;
  const modelPromise=loader.loadAsync('./assets/great-hall.glb',event=>progress(event.total?event.loaded/event.total*82:20,'正在展开石拱、长桌与烛光…'));
  const deadline=new Promise((_,reject)=>{timeout=setTimeout(()=>reject(new Error('Model load timed out')),90000);});
  let gltf;
  try{gltf=await Promise.race([modelPromise,deadline]);}finally{clearTimeout(timeout);}
  const response=await fetch('./assets/metadata.json');if(!response.ok)throw new Error(`Metadata HTTP ${response.status}`);const meta=await response.json();
  gltf.scene.traverse(o=>{
    if(!o.isMesh)return;
    const materials=Array.isArray(o.material)?o.material:[o.material];
    for(const m of materials){
      if(m.map){m.map.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());}
      // Baked surfaces carry their authored illumination; preserve GLB strength.
    }
  });
  scene.add(gltf.scene);progress(88,'正在点亮悬浮蜡烛…');
  addFlames(meta.flames);addDust();addRays();
  bindControls();bindSceneShell(stopWalk);if(groundsEntrance("hall"))await startWalk(false);await renderer.compileAsync(scene,camera);progress(100,'欢迎回到霍格沃茨');
  state.loadMs=Math.round(performance.now()-start);state.assetTriangles=meta.triangles;state.ready=true;$('#explore').disabled=false;
  $('#loading').classList.add('done');$('#loading').setAttribute('aria-hidden','true');renderer.setAnimationLoop(animate);draco.dispose();
}
function addFlames(positions){
  const geometry=new THREE.PlaneGeometry(.40,.64);
  const material=new THREE.ShaderMaterial({transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,uniforms:{time:{value:0}},vertexShader:`attribute float phase; varying vec2 vUv; varying float vPhase; void main(){vUv=uv;vPhase=phase;vec4 p=modelViewMatrix*instanceMatrix*vec4(0.,0.,0.,1.);p.xy+=position.xy;gl_Position=projectionMatrix*p;}`,fragmentShader:`varying vec2 vUv; varying float vPhase; uniform float time; void main(){vec2 p=(vUv-.5)*2.;p.x+=sin(time*4.+vPhase)*.08*p.y;float core=exp(-dot(p*vec2(2.8,1.6),p*vec2(2.8,1.6))*2.);float glow=exp(-dot(p,p)*4.);float pulse=.9+.1*sin(time*5.+vPhase);gl_FragColor=vec4(vec3(1.,.42,.08)*(core*2.+glow*.55)*pulse,glow*.65);}`});
  flameMesh=new THREE.InstancedMesh(geometry,material,positions.length);const m=new THREE.Matrix4();const phase=[];
  positions.forEach((p,i)=>{m.makeTranslation(...p);flameMesh.setMatrixAt(i,m);phase.push(i*1.618);});
  geometry.setAttribute('phase',new THREE.InstancedBufferAttribute(new Float32Array(phase),1));flameMesh.frustumCulled=false;scene.add(flameMesh);
}
function addDust(){
  const count=240,positions=new Float32Array(count*3);let seed=29;const rand=()=>{seed=(seed*16807)%2147483647;return(seed-1)/2147483646;};
  for(let i=0;i<count;i++){positions[i*3]=rand()*30-5;positions[i*3+1]=rand()*11+.4;positions[i*3+2]=rand()*11-5.5;}
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));
  dust=new THREE.Points(geometry,new THREE.ShaderMaterial({transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,uniforms:{time:{value:0}},vertexShader:`uniform float time;varying float a;void main(){vec3 p=position;p.y+=sin(time*.2+p.x)*.12;p.x+=sin(time*.13+p.z)*.14;vec4 mv=modelViewMatrix*vec4(p,1.);gl_Position=projectionMatrix*mv;gl_PointSize=clamp(18./-mv.z,1.,3.);a=.12+.12*sin(p.x*3.+p.z);}`,fragmentShader:`varying float a;void main(){float d=length(gl_PointCoord-.5);gl_FragColor=vec4(.78,.65,.40,(1.-smoothstep(.08,.5,d))*a);}`}));scene.add(dust);
}
function addRays(){
  const material=new THREE.ShaderMaterial({transparent:true,depthWrite:false,side:THREE.DoubleSide,blending:THREE.AdditiveBlending,vertexShader:`varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,fragmentShader:`varying vec2 vUv;void main(){float edge=pow(sin(vUv.x*3.14159),2.);float fade=sin(vUv.y*3.14159);gl_FragColor=vec4(.22,.35,.48,edge*fade*.032);}`});
  for(const z of [-2,0,2]){
    const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute([24.7,10,z-.20,24.7,10,z+.20,5,.1,z-1.3,5,.1,z+1.3],3));geo.setAttribute('uv',new THREE.Float32BufferAttribute([0,1,1,1,0,0,1,0],2));geo.setIndex([0,2,1,1,2,3]);scene.add(new THREE.Mesh(geo,material));
  }
}
function setView(name,animated=true){
  if(walk)stopWalk();const b=bookmarks[name];keys.clear();
  // Bookmarks jump to known clear locations; easing through furniture would be misleading.
  camera.position.set(b.x,b.y,b.z);yaw=b.yaw;pitch=b.pitch;target=null;applyLook();
  document.querySelectorAll('[data-view]').forEach(e=>e.classList.toggle('active',e.dataset.view===name));
}
function applyLook(){camera.rotation.set(pitch,yaw,0,'YXZ');}
function look(dx,dy){yaw-=dx*.0023;pitch=THREE.MathUtils.clamp(pitch-dy*.0023,-1.15,1.3);applyLook();}
function stopWalk(){walk=false;state.mode='view';keys.clear();document.body.classList.remove('walking');$('#crosshair').hidden=true;$('#explore-label').textContent='进入礼堂';if(document.pointerLockElement)document.exitPointerLock();}
async function startWalk(lockPointer=true){
  if(walk){stopWalk();return;}walk=true;state.mode='walk';document.body.classList.add('walking');$('#crosshair').hidden=false;$('#explore-label').textContent='退出漫游';renderer.domElement.focus();
  if(lockPointer&&matchMedia('(pointer:fine)').matches){try{await renderer.domElement.requestPointerLock();}catch{ $('#control-hint').textContent='按住画面拖动环顾 · WASD 行走 · Esc 退出';}}
}
function toggleUI(){hidden=!hidden;document.body.classList.toggle('ui-hidden',hidden);$('#interface').inert=hidden;$('#restore-ui').hidden=!hidden;(hidden?$('#restore-ui'):$('#hide-ui')).focus();}
function bindControls(){
  const canvas=renderer.domElement;
  $('#explore').onclick=startWalk;$('#hide-ui').onclick=toggleUI;$('#restore-ui').onclick=toggleUI;
  $('#help').onclick=()=>{stopWalk();$('#help-dialog').showModal();};$('#close-help').onclick=()=>$('#help-dialog').close();
  document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>setView(b.dataset.view));
  $('#quality').onchange=resize;
  canvas.addEventListener('pointerdown',e=>{if(!document.pointerLockElement){drag=true;lastX=e.clientX;lastY=e.clientY;canvas.setPointerCapture(e.pointerId);}});
  canvas.addEventListener('pointermove',e=>{if(document.pointerLockElement===canvas)look(e.movementX,e.movementY);else if(drag){look(e.clientX-lastX,e.clientY-lastY);lastX=e.clientX;lastY=e.clientY;}});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>drag=false);
  document.addEventListener('pointerlockchange',()=>{if(!document.pointerLockElement&&walk)stopWalk();});
  document.addEventListener('keydown',e=>{
    if(!acceptNavigationKey(e.target,$('#help-dialog').open))return;
    if(walk&&['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','ShiftLeft','ShiftRight'].includes(e.code)){keys.add(e.code);e.preventDefault();}
    if(!e.repeat){if(e.code==='KeyR')setView('aisle');if(e.code==='KeyH')toggleUI();if(e.code==='Escape')stopWalk();}
  });
  document.addEventListener('keyup',e=>keys.delete(e.code));window.addEventListener('blur',()=>{keys.clear();drag=false;});
  document.addEventListener('visibilitychange',()=>{keys.clear();previous=performance.now();});
  document.querySelectorAll('[data-key]').forEach(button=>{
    button.addEventListener('pointerdown',e=>{e.preventDefault();if(!walk)startWalk();keys.add(button.dataset.key);button.setPointerCapture(e.pointerId);});
    for(const name of ['pointerup','pointercancel','lostpointercapture'])button.addEventListener(name,()=>keys.delete(button.dataset.key));
  });
  window.addEventListener('resize',resize);
}
function resize(){
  const high=$('#quality').value==='high';const ratio=Math.min(devicePixelRatio,high?1.5:1,(high?2560:1920)/innerWidth);
  renderer.setPixelRatio(ratio);renderer.setSize(innerWidth,innerHeight);composer.setPixelRatio(ratio);composer.setSize(innerWidth,innerHeight);
  camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();bloom.enabled=true;
  state.renderSize=[Math.round(innerWidth*ratio),Math.round(innerHeight*ratio)];
}
function animate(now){
  const frameDt=(now-previous)/1000,dt=Math.min(.05,Math.max(0,frameDt));previous=now;elapsed+=dt;
  if(!$('#help-dialog').open&&walk&&keys.size){
    const direction=inputVector(keys,yaw),speed=(keys.has('ShiftLeft')||keys.has('ShiftRight'))?3.8:2.1;
    const p=movePlayer(camera.position,{x:direction.x*speed*dt,z:direction.z*speed*dt});camera.position.x=p.x;camera.position.z=p.z;
  }
  if(!reduced){flameMesh.material.uniforms.time.value=elapsed;dust.material.uniforms.time.value=elapsed;}
  renderer.info.reset();composer.render();state.frames++;
  if(frameDt>0&&frameDt<.5){frameTimes.push(frameDt);if(frameTimes.length>90)frameTimes.shift();state.fps=Math.round(frameTimes.length/frameTimes.reduce((a,b)=>a+b,0));}
  state.drawCalls=renderer.info.render.calls;state.triangles=renderer.info.render.triangles;state.camera={x:camera.position.x,y:camera.position.y,z:camera.position.z,yaw,pitch};
}

document.addEventListener('visibilitychange',()=>{if(state.ready&&!state.error)renderer.setAnimationLoop(document.hidden?null:animate);});
window.addEventListener('pagehide',()=>{keys.clear();renderer?.setAnimationLoop(null);});
window.addEventListener('pageshow',()=>{previous=performance.now();if(state.ready&&!state.error&&!document.hidden)renderer.setAnimationLoop(animate);});
