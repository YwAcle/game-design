import test from 'node:test';
import assert from 'node:assert/strict';
import {movePlayer,inputVector,OBSTACLES,acceptNavigationKey} from '../src/hall/navigation.js';
test('the central aisle remains walkable for its full length',()=>{
  let p={x:-5.5,z:0};for(let i=0;i<250;i++)p=movePlayer(p,{x:.1,z:0});
  assert.ok(p.x>19);assert.equal(p.z,0);
});
test('benches stop the player and permit sliding along their length',()=>{
  let p={x:1,z:0};for(let i=0;i<60;i++)p=movePlayer(p,{x:.04,z:.1});
  assert.ok(p.z>1.8&&p.z<2.1);assert.ok(p.x>3);
});
test('large movements cannot tunnel through furniture',()=>{
  const p=movePlayer({x:0,z:0},{x:0,z:10});assert.ok(p.z>1.8&&p.z<2.1);
});
test('walls and dais bound the accessible floor',()=>{
  const p=movePlayer({x:-6,z:0},{x:-50,z:0});assert.ok(p.x>=-6.95);
  const q=movePlayer({x:19,z:0},{x:50,z:0});assert.ok(q.x<20.6);
});
test('diagonal input has the same speed as straight input',()=>{
  const a=inputVector(new Set(['KeyW']),0),b=inputVector(new Set(['KeyW','KeyD']),0);
  assert.ok(Math.abs(Math.hypot(a.x,a.z)-Math.hypot(b.x,b.z))<1e-9);
  assert.ok(a.z<0);
});
test('the four table groups all contribute physical obstacles',()=>{
  assert.equal(OBSTACLES.length,4);
  for(const o of OBSTACLES){const p=movePlayer({x:-5.5,z:(o.z0+o.z1)/2},{x:12,z:0});assert.ok(p.x<o.x0);}
});
test('clicking UI buttons does not disable navigation or H to restore the UI',()=>{
  for(const tagName of ['BUTTON','CANVAS','BODY'])assert.equal(acceptNavigationKey({tagName}),true);
  for(const tagName of ['SELECT','INPUT','TEXTAREA'])assert.equal(acceptNavigationKey({tagName}),false);
  assert.equal(acceptNavigationKey({tagName:'DIV',isContentEditable:true}),false);
  assert.equal(acceptNavigationKey({tagName:'CANVAS'},true),false);
});

test('the widened central avenue permits two-way walking away from the centre line',()=>{
  for(const z of [-1.75,1.75]){
    const p=movePlayer({x:-5.5,z},{x:24,z:0});
    assert.ok(p.x>18);assert.equal(p.z,z);
  }
});
