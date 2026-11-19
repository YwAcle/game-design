import test from 'node:test';
import assert from 'node:assert/strict';
import {validMemory,mergeBackup,readStoredState,sceneFromQuery,sceneURL} from '../src/shared/memory-data.js';
const ids=['potions','divination','gryffindor','slytherin','ravenclaw','hufflepuff'];
test('stories from every new room survive saving, backup import and return navigation',()=>{
  const memories=ids.map(id=>({id:'memory-'+id,title:'回到这里',body:'灯还亮着。',author:'归来的巫师',house:'',cover:id,scene:id,created:'2026-11-17T00:00:00Z'}));
  for(const m of memories)assert.ok(validMemory(m),'story rejected: '+m.scene);
  const backup={version:1,memories,favorites:[],house:''};
  const result=mergeBackup({memories:[],favorites:[],house:''},backup);
  assert.equal(result.added,6);
  assert.deepEqual(readStoredState(JSON.stringify(backup)).memories,memories);
  for(const id of ids){assert.equal(sceneURL(id),'interior/?scene='+id);assert.equal(sceneFromQuery('?write='+id),id);}
  assert.equal(mergeBackup(result,backup).added,0);
});
