import {SCENES} from './scenes.js';
const portals={hall:'hall',arena:'arena',divination:'tower',potions:'dungeon',slytherin:'dungeon',ravenclaw:'houses',gryffindor:'houses',hufflepuff:'kitchen'};
export function groundsEntrance(room) {
  const from=new URLSearchParams(location.search).get('grounds');
  return from===portals[room]?from:null;
}
export function nearestView(position, entries) {
  let view, nearest = Infinity;
  for (const [id, [x, y, z]] of entries) {
    const distance = (position.x - x)**2 + (position.y - y)**2 + (position.z - z)**2;
    if (distance < nearest) {
      nearest = distance;
      view = id;
    }
  }
  return view;
}

export function sceneWriteURL(scene, view) {
  const params = new URLSearchParams({write: scene});
  if (view !== undefined) params.set('view', view);
  return '../?' + params + '#memories';
}

export function bindSceneShell(stopWalk,current,getView) {
  const nav=document.querySelector('.journey-nav');
  current ||= location.pathname.includes('/hall/')?'hall':location.pathname.includes('/arena/')?'arena':new URLSearchParams(location.search).get('scene');
  if(nav){
    nav.replaceChildren();
    const back=document.createElement('a');
    const from=groundsEntrance(current);
    const outdoors=Boolean(from);
    back.href=outdoors?'../world/?from='+from:'../#places';
    back.textContent=outdoors?'← 返回室外地图':'← 回忆录';
    nav.append(back);
    const label=document.createElement('label');label.className='room-select-label';label.textContent='前往';
    const select=document.createElement('select');select.setAttribute('aria-label','切换场景');
    for(const [id,scene] of Object.entries(SCENES)){const option=document.createElement('option');option.value=id;option.textContent=scene.name;option.selected=id===current;select.append(option);}
    label.append(select);nav.append(label);
    select.addEventListener('change',()=>{stopWalk();const next=new URL('../'+SCENES[select.value].url,location.href);if(outdoors)next.searchParams.set('grounds',portals[select.value]);location.href=next.href;});
    const write=document.createElement('a');write.className='write-moment';write.href=sceneWriteURL(current);write.textContent='写下此刻 ✎';nav.append(write);
    const updateWriteLink = () => { write.href = sceneWriteURL(current, getView()); };
    write.addEventListener('pointerdown',updateWriteLink);
    write.addEventListener('focus',updateWriteLink);
    write.addEventListener('click',updateWriteLink);
  }
  document.querySelectorAll('.journey-nav a, .wordmark').forEach(link=>link.addEventListener('click',stopWalk));
}
