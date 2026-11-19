import test from 'node:test';
import assert from 'node:assert/strict';
import {validMemory,mergeBackup,readStoredState,memoryDestination,sceneFromQuery,sceneURL,sceneViewFromQuery} from '../src/shared/memory-data.js';
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

test('a room viewpoint survives backup and opens at the selected camera',()=>{
  const memory={id:'memory-eagle',title:'鹰门后的雕像',body:'今天站在雕像旁。',author:'巫师',house:'',cover:'ravenclaw',
    scene:'ravenclaw',view:'2',created:'2026-11-17T00:00:00Z'};
  const result=mergeBackup({memories:[],favorites:[],house:''},{version:1,memories:[memory]});
  assert.deepEqual(result.memories,[memory]);
  const url=memoryDestination(result.memories[0]).url;
  assert.equal(url,'interior/?scene=ravenclaw&view=2');
  assert.equal(sceneViewFromQuery(url.split('?')[1],'ravenclaw'),'2');
  assert.equal(sceneViewFromQuery('?view=arrival','hall'),'arrival');
  assert.equal(sceneViewFromQuery('?view=arrival','arena'),null);
  assert.equal(validMemory({...memory,view:'3'}),false);
});
