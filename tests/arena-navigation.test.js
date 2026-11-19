import test from 'node:test';
import assert from 'node:assert/strict';
import {movePlayer,inputVector,insideCourt,acceptNavigationKey} from '../src/arena/navigation.js';
test('walking stays inside all four railings even with a long frame',()=>{
  for(const d of [{x:100,z:0},{x:-100,z:0},{x:0,z:100},{x:0,z:-100}]){const p=movePlayer({x:0,z:0},d);assert(Math.abs(p.x)<=9.1&&Math.abs(p.z)<=12.0);}
});
test('diagonal corners respect the chamfered barrier',()=>{
  const p=movePlayer({x:8,z:10},{x:5,z:5});assert(insideCourt(p.x,p.z));assert(Math.abs(p.x)+Math.abs(p.z)<=20.1);
});
test('center and both duel positions remain freely reachable',()=>{
  for(const z of [-7.4,0,7.4]){const p=movePlayer({x:0,z:0},{x:0,z});assert(Math.abs(p.z-z)<1e-8);}
});
test('diagonal key movement is normalized',()=>{
  const p=inputVector(new Set(['KeyW','KeyD']),.7);assert(Math.abs(Math.hypot(p.x,p.z)-1)<1e-10);
});
test('non-finite movement preserves the last valid position',()=>{
  assert.deepEqual(movePlayer({x:1,z:2},{x:NaN,z:0}),{x:1,z:2});
});
test('button focus allows movement but dialogs and selects suppress it',()=>{
  assert(acceptNavigationKey({tagName:'BUTTON'}));assert(!acceptNavigationKey({tagName:'SELECT'}));assert(!acceptNavigationKey(null,true));
});
