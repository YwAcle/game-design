import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {canStand, movePlayer} from '../src/interior/navigation.js';
const room={bounds:{minX:-6,maxX:6,minZ:-6,maxZ:6},obstacles:[{minX:-1,maxX:1,minZ:-1,maxZ:1}]};
test('player clearance prevents walking into furniture or through room walls',()=>{
  assert.equal(canStand(0,0,room),false);
  assert.equal(canStand(1.1,0,room),false);
  assert.equal(canStand(1.3,0,room),true);
  assert.equal(canStand(5.9,0,room),false);
});
test('large frame movement cannot tunnel through a table',()=>{
  const p=movePlayer({x:0,z:3},{x:0,z:-8},room);
  assert.ok(p.z>=1.25&&p.z<1.4);assert.equal(p.x,0);
});
test('walking along a wall slides instead of freezing',()=>{
  const p=movePlayer({x:5.7,z:3},{x:2,z:-2},room);
  assert.ok(p.x<=5.75);assert.ok(p.z<1.1);
});
test('nonfinite movement is ignored',()=>{
  assert.deepEqual(movePlayer({x:2,z:2},{x:NaN,z:0},room),{x:2,z:2});
});

test('Gryffindor reading stand and floor cushions block fixed-height walking',()=>{
  const gry=JSON.parse(readFileSync(new URL('../scene-assets/gryffindor/metadata.json',import.meta.url),'utf8'));
  for(const [x,z] of [[-2.7,-3.13],[-2.8,-3.13],[-3.8,2.8],[3.8,2.3]]){
    assert.equal(canStand(x,z,gry),false,`Furniture at ${x}, ${z} must block the player`);
  }
  const p=movePlayer({x:-3.3,z:-3.13},{x:.8,z:0},gry);
  assert.ok(p.x<=-3.095,'The side table must stop a long step');
});
