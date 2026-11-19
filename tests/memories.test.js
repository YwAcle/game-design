import test from 'node:test';
import assert from 'node:assert/strict';
import {validMemory, mergeBackup, memoryDestination, outdoorFromQuery, readStoredState, sceneURL, sceneFromQuery, writeStoredState} from '../src/shared/memory-data.js';
const memory = (patch={}) => ({id:'memory-original',title:'长桌旁',body:'那一晚的烛光',author:'巫师',house:'',cover:'letter',created:'2026-11-17T00:00:00.000Z',...patch});
const state = (memories=[]) => ({memories,favorites:[],house:''});
const backup = (memories=[],patch={}) => ({version:1,memories,favorites:[],house:'',...patch});
test('old stories remain valid; new scenes and covers survive validation',()=>{
  assert.ok(validMemory(memory()));
  assert.ok(validMemory(memory({scene:'hall',cover:'hall'})));
  assert.ok(validMemory(memory({scene:'arena',cover:'arena'})));
  assert.equal(validMemory(memory({scene:'javascript:alert(1)'})),false);
  assert.equal(validMemory(memory({body:'   '})),false);
});
test('import preserves existing stories and house, merges favorites, and is idempotent',()=>{
  const original=memory(); const incoming=memory({id:'memory-new',scene:'arena'});
  const current={...state([original]),house:'ravenclaw',favorites:['inspiration-letter']};
  const data=backup([original,incoming],{house:'slytherin',favorites:['memory-new','unknown']});
  const first=mergeBackup(current,data);
  assert.equal(first.added,1); assert.equal(first.house,'ravenclaw');
  assert.equal(first.memories.length,2); assert.ok(first.favorites.includes('memory-new'));
  assert.ok(!first.favorites.includes('unknown'));assert.equal(mergeBackup(first,data).added,0);
  assert.deepEqual(current.memories,[original]);
});
test('ID collision retains both different stories and maps imported favorites',()=>{
  const old=memory();const changed=memory({body:'另一个故事'});
  const data=backup([changed],{favorites:[changed.id]});
  const result=mergeBackup(state([old]),data);
  assert.equal(result.memories.length,2);assert.equal(result.conflicts,1);
  const imported=result.memories.find(x=>x.body===changed.body);
  assert.notEqual(imported.id,old.id);assert.ok(result.favorites.includes(imported.id));
  assert.equal(mergeBackup(result,data).added,0);
});
test('reject invalid backups atomically and ignore untrusted extra fields',()=>{
  for(const data of [null,backup([memory({title:''})]),backup([memory(),memory()]),{...backup(),version:2}])
    assert.throws(()=>mergeBackup(state(),data));
  const result=mergeBackup(state(),backup([memory({url:'https://evil.example',__extra:'bad'})]));
  assert.equal(result.memories[0].url,undefined);
});
test('scene navigation preserves old routes and rejects untrusted destinations',()=>{
  assert.equal(sceneURL('hall'),'hall/');assert.equal(sceneURL('arena'),'arena/');
  assert.equal(sceneURL('../outside'),null);assert.equal(sceneURL('__proto__'),null);
  assert.equal(sceneFromQuery('?write=hall'),'hall');
  assert.equal(sceneFromQuery('?write=https://evil.example'),null);
});
test('an outdoor story keeps its position and viewing direction through a backup', ()=>{
  const outdoor = {place:'boats', name:'黑湖泊位', position:[36.2, 68.9, -.48, .06]};
  const query = new URLSearchParams({outdoor: JSON.stringify({...outdoor, url:'https://example.com'})});
  assert.deepEqual(outdoorFromQuery(query), outdoor);
  const story = memory({outdoor});
  const restored = mergeBackup(state(), backup([story]));
  assert.deepEqual(readStoredState(JSON.stringify(backup(restored.memories))).memories, [story]);
  assert.deepEqual(memoryDestination(story), {name:'黑湖泊位', url:'world/?memory=memory-original'});
  assert.equal(mergeBackup(restored, backup([story])).added, 0);
  assert.equal(mergeBackup(restored, backup([memory({outdoor:{...outdoor, position:[36.2, 68, -.48, .06]}})])).conflicts, 1);
  assert.equal(memoryDestination(memory({scene:'hall'})).url, 'hall/');
});
test('invalid outdoor locations and ambiguous indoor/outdoor stories are rejected', ()=>{
  const outdoor = {place:'path', name:'高地小径', position:[2, 7, .12, .08]};
  assert.equal(validMemory(memory({scene:'hall', outdoor})), false);
  for (const invalid of [
    {...outdoor, place:'../../../'},
    {...outdoor, name:''},
    {...outdoor, position:[null, 7, .12, .08]},
    {...outdoor, position:[201, 7, .12, .08]},
    {...outdoor, position:[2, 7, 4, .08]}
  ]) {
    assert.equal(validMemory(memory({outdoor:invalid})), false);
    assert.equal(outdoorFromQuery(new URLSearchParams({outdoor: JSON.stringify(invalid)})), null);
  }
  assert.equal(outdoorFromQuery('?outdoor=broken'), null);
});
test('writing from a restored page reads fresh stories before applying changes',()=>{
  let raw=JSON.stringify({...backup([memory()]),reducedMotion:null});
  const storage={getItem:()=>raw,setItem:(_,value)=>{raw=value;}};
  // Another page adds a story while this page still holds the older snapshot.
  const newer=memory({id:'memory-another',title:'另一页'});
  raw=JSON.stringify(backup([newer,memory()]));
  writeStoredState(storage,{house:'ravenclaw'});
  assert.equal(JSON.parse(raw).memories.length,2);
  writeStoredState(storage,latest=>({memories:[memory({id:'memory-third'}),...latest.memories]}));
  assert.equal(JSON.parse(raw).memories.length,3);
  writeStoredState(storage,latest=>({memories:latest.memories.filter(m=>m.id!=='memory-original')}));
  assert.equal(JSON.parse(raw).memories.length,2);
  raw='{broken';assert.throws(()=>writeStoredState(storage,{house:''}));assert.equal(raw,'{broken');
});
test('the app can reimport its own large backups without an arbitrary story count limit',()=>{
  const stories=Array.from({length:2001},(_,i)=>memory({id:`memory-large-${i}`,body:'魔'.repeat(400)}));
  const result=mergeBackup(state(),JSON.parse(JSON.stringify(backup(stories))));
  assert.equal(result.memories.length,2001);
});
