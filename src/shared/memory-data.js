import {SCENES} from './scenes.js';
export {SCENES};
const houses = ['', 'gryffindor','slytherin','ravenclaw','hufflepuff'];
const covers = ['letter','bridge','ballroom','fireworks',...Object.keys(SCENES)];
const exampleIds = ['inspiration-letter','inspiration-ballroom','inspiration-fireworks'];
export const STORAGE_KEY='hogwarts-always-v1';
export function readStoredState(raw) {
  if(!raw)return {version:1,memories:[],favorites:[],house:'',reducedMotion:null};
  const saved=JSON.parse(raw);
  if(!saved || saved.version!==1 || !Array.isArray(saved.memories) || !saved.memories.every(validMemory)
    || new Set(saved.memories.map(m=>m.id)).size!==saved.memories.length)throw new Error('Invalid saved memories');
  const ids=new Set([...exampleIds,...saved.memories.map(m=>m.id)]);
  return {version:1,memories:saved.memories,favorites:Array.isArray(saved.favorites)?[...new Set(saved.favorites.filter(id=>ids.has(id)))]:[],
    house:houses.includes(saved.house)?saved.house:'',reducedMotion:typeof saved.reducedMotion==='boolean'?saved.reducedMotion:null};
}
export function writeStoredState(storage, change) {
  // A previous page may be restored from BFCache after another page saved a story.
  const latest=readStoredState(storage.getItem(STORAGE_KEY));
  const patch=typeof change==='function'?change(latest):change;
  const next={...latest,...patch,version:1};
  storage.setItem(STORAGE_KEY,JSON.stringify(next));
  return next;
}
export function sceneURL(id) { return Object.hasOwn(SCENES,id) ? SCENES[id].url : null; }
export function sceneFromQuery(search) { const id=new URLSearchParams(search).get('write'); return sceneURL(id)?id:null; }

const namedViews = {
  hall: ['aisle', 'feast', 'window', 'arrival'],
  arena: ['overview', 'court', 'gallery'],
};
function validSceneView(scene, view) {
  return Boolean(sceneURL(scene) && (namedViews[scene] ?? ['0', '1', '2']).includes(view));
}
export function sceneViewFromQuery(search, scene) {
  const view = new URLSearchParams(search).get('view');
  return validSceneView(scene, view) ? view : null;
}

function validOutdoor(outdoor) {
  if (!outdoor || typeof outdoor.place !== 'string' || !/^[a-z][a-z0-9-]{0,31}$/.test(outdoor.place)
    || typeof outdoor.name !== 'string' || !outdoor.name.trim() || outdoor.name.length > 48
    || !Array.isArray(outdoor.position) || outdoor.position.length !== 4) return false;
  const [x, z, yaw, pitch] = outdoor.position;
  return [x, z, yaw, pitch].every(Number.isFinite) && Math.abs(x) <= 200 && Math.abs(z) <= 200
    && Math.abs(yaw) <= Math.PI && Math.abs(pitch) <= Math.PI / 2;
}

export function outdoorFromQuery(search) {
  const value = new URLSearchParams(search).get('outdoor');
  if (!value) return null;
  try {
    const outdoor = JSON.parse(value);
    if (validOutdoor(outdoor)) {
      const {place, name, position} = outdoor;
      return {place, name, position};
    }
  } catch { /* A broken link can still open the memoir. */ }
  return null;
}

export function memoryDestination(memory) {
  if (memory.outdoor) {
    return {name: memory.outdoor.name, url: 'world/?' + new URLSearchParams({memory: memory.id})};
  }
  const url = sceneURL(memory.scene);
  if (!url) return null;
  const view = memory.view;
  const destination = validSceneView(memory.scene, view) ? url + (url.includes('?') ? '&' : '?') + 'view=' + view : url;
  return {name: SCENES[memory.scene].name, url: destination};
}

export function validMemory(m) {
  return !!(m && typeof m==='object' && typeof m.id==='string' && /^memory-[\w-]{1,160}$/.test(m.id)
    && typeof m.title==='string' && m.title.trim().length>0 && m.title.length<=32
    && typeof m.body==='string' && m.body.trim().length>0 && m.body.length<=400
    && typeof m.author==='string' && m.author.trim().length>0 && m.author.length<=24
    && houses.includes(m.house) && covers.includes(m.cover)
    && typeof m.created==='string' && Number.isFinite(Date.parse(m.created))
    && (m.scene===undefined || m.scene==='' || !!sceneURL(m.scene))
    && (m.outdoor === undefined || (!m.scene && validOutdoor(m.outdoor)))
    && (m.view === undefined || validSceneView(m.scene, m.view)));
}
function clean(m) {
  const {id,title,body,author,house,cover,created}=m;
  const record = {id,title,body,author,house,cover,created};
  if (m.scene) record.scene = m.scene;
  if (m.view !== undefined) record.view = m.view;
  if (m.outdoor) {
    const {place, name, position} = m.outdoor;
    record.outdoor = {place, name, position};
  }
  return record;
}
function signature(m) { const {id,...content}=clean(m); return JSON.stringify(content); }
export function mergeBackup(current, backup) {
  if (!backup || backup.version!==1 || !Array.isArray(backup.memories)
    || !backup.memories.every(validMemory) || new Set(backup.memories.map(m=>m.id)).size!==backup.memories.length)
    throw new Error('这不是有效的魔法留声回忆备份。请使用原网页导出的 JSON 文件。');
  const memories=[...current.memories], byId=new Map(memories.map(m=>[m.id,m]));
  const signatures=new Map(memories.map(m=>[signature(m),m.id]));
  const remap=new Map();let added=0,conflicts=0;
  for(const raw of backup.memories) {
    const m=clean(raw),sig=signature(m),existing=byId.get(m.id);
    if(existing && signature(existing)===sig) {remap.set(m.id,m.id);continue;}
    if(existing && signatures.has(sig)) {remap.set(m.id,signatures.get(sig));continue;}
    const oldId=m.id;
    if(existing) {
      let n=1;const base=m.id.slice(0,140);
      while(byId.has(`${base}-import-${n}`))n++;
      m.id=`${base}-import-${n}`;conflicts++;
    }
    remap.set(oldId,m.id);byId.set(m.id,m);signatures.set(sig,m.id);memories.unshift(m);added++;
  }
  const allowed=new Set([...byId.keys(),...exampleIds]);
  const incoming=Array.isArray(backup.favorites)?backup.favorites:[];
  const favorites=[...new Set([...current.favorites,...incoming.map(id=>remap.get(id)||id)])].filter(id=>allowed.has(id));
  return {memories,favorites,house:current.house || (houses.includes(backup.house)?backup.house:''),added,conflicts};
}
