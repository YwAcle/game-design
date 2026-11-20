import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { floorHeight, terrain, walkable, atDoor } from '../src/navigation.mjs';

const read = file => JSON.parse(fs.readFileSync(new URL('../' + file, import.meta.url)));
const layout = read('layout.json'), nav = read('navigation.json');
const places = Object.fromEntries(layout.places.map(p => [p.id, p.at]));
const at = point => typeof point === 'string' ? places[point] : point;
const key = point => at(point).join(',');

test('every landmark joins the same trail network', () => {
  const graph = new Map();
  for (const path of layout.trails) {
    for (let i = 1; i < path.length; i++) {
      const a = key(path[i-1]), b = key(path[i]);
      if (!graph.has(a)) graph.set(a, []);
      if (!graph.has(b)) graph.set(b, []);
      graph.get(a).push(b);graph.get(b).push(a);
    }
  }
  const reached = new Set([key('court')]);
  for (const node of reached) for (const next of graph.get(node)) reached.add(next);
  for (const p of layout.places) assert.ok(reached.has(key(p.id)), p.name);
});
for (const [index,path] of layout.trails.entries()) {
  test('walk trail ' + (index+1) + ' including its entrances', () => {
    for (let i = 1; i < path.length; i++) {
      const a=at(path[i-1]), b=at(path[i]);
      const steps=Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/.25);
      for (let k=0;k<=steps;k++) {
        const x=a[0]+(b[0]-a[0])*k/steps, z=a[1]+(b[1]-a[1])*k/steps;
        assert.ok(walkable(nav,layout.bridge,x,z),'blocked near '+[x,z].map(v=>v.toFixed(1)));
      }
    }
  });
}
test('bridge crosses above the gorge, lake and walls stop movement', () => {
  assert.ok(floorHeight(nav,layout.bridge,-54,0)>terrain(nav,-54,0)+5);
  for (const point of [[-54,2.5],[0,60],[-30,-13]]) assert.equal(walkable(nav,layout.bridge,...point),false);
});

test('all guided walks follow connected, existing paths', () => {
  const edges = new Set();
  for(const trail of layout.trails) for(let i=1;i<trail.length;i++){
    const a=key(trail[i-1]), b=key(trail[i]);
    edges.add(a+'|'+b);edges.add(b+'|'+a);
  }
  for(const route of layout.routes){
    assert.equal(route.stops.length,route.labels.length);
    assert.equal(route.stops.at(-1),route.end);
    let from=route.start;
    for(const to of route.stops){assert.ok(edges.has(key(from)+'|'+key(to)),route.id);from=to;}
  }
});

test('entry, outward return steps and surveyed stone treads are reachable',()=>{
  for(const p of layout.places.filter(p=>p.rooms)){
    assert.ok(atDoor(p,...p.at),p.id);
    const dx=p.at[0]-p.door[0], dz=p.at[1]-p.door[1], d=Math.hypot(dx,dz);
    assert.ok(walkable(nav,layout.bridge,p.at[0]+dx/d*.7,p.at[1]+dz/d*.7),p.id);
    assert.equal(atDoor(p,p.door[0]+8,p.door[1]),false);
  }
  assert.ok(nav.flights.length>0);
  for(const flight of nav.flights){
    const h=floorHeight(nav,layout.bridge,flight.cx,flight.cz);
    assert.ok(Math.abs(h-flight.profile[10])<.25);
  }
});

test('the kitchen barrel approach is walkable and the casks stop movement', () => {
  const kitchen = layout.places.find(place => place.id === 'kitchen');
  const view = layout.views.find(view => view.id === 'kitchen-door');
  assert.ok(atDoor(kitchen, ...view.at));
  assert.ok(walkable(nav, layout.bridge, ...view.at));
  assert.equal(walkable(nav, layout.bridge, ...kitchen.door), false);
});

test('the secret passage connects two accessible approaches', () => {
  const entrances = layout.places.filter(place => place.passage);
  assert.equal(entrances.length, 2);
  for (const place of entrances) {
    const exit = layout.places.find(candidate => candidate.id === place.passage);
    assert.equal(exit.passage, place.id);
    assert.ok(walkable(nav, layout.bridge, ...exit.at));
    const direction = place.door.map((v, i) => v - place.at[i]);
    const t = 1 - 2.5 / Math.hypot(...direction);
    const approach = place.at.map((v, i) => v + direction[i] * t);
    assert.ok(atDoor(place, ...approach));
    assert.ok(walkable(nav, layout.bridge, ...approach));
  }
});
