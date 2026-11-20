import {build} from 'esbuild';
import {mkdir,cp,copyFile,readFile,writeFile,access,rm} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {INTERIORS} from './src/shared/scenes.js';
process.chdir(fileURLToPath(new URL('.',import.meta.url)));
for(const id of INTERIORS){
  await access(`scene-assets/${id}/scene.glb`);await access(`scene-assets/${id}/metadata.json`);await access(`assets/${id}.webp`);
}
const output=path.resolve('dist');
if(path.dirname(output)!==process.cwd()||path.basename(output)!=='dist')throw new Error('Unexpected build output path');
await rm(output,{recursive:true,force:true});
await mkdir('dist',{recursive:true});
await build({absWorkingDir:process.cwd(),entryPoints:{app:'src/memoir/app.js','hall/app':'src/hall/main.js','arena/app':'src/arena/main.js','interior/app':'src/interior/main.js'},bundle:true,splitting:true,minify:true,format:'esm',outdir:'dist',chunkNames:'shared/[name]-[hash]',legalComments:'linked',target:'es2022'});
await copyFile('src/memoir/index.html','dist/index.html');
await writeFile('dist/styles.css',(await readFile('src/memoir/styles.css','utf8'))+'\n'+(await readFile('src/memoir/integration.css','utf8')));
await cp('assets','dist/assets',{recursive:true});
await cp('node_modules/three/examples/jsm/libs/draco/gltf','dist/assets/draco',{recursive:true});
await copyFile('node_modules/three/LICENSE','dist/THREE-LICENSE.txt');
await cp('licenses','dist/licenses',{recursive:true});
for(const scene of ['hall','arena']){
  await copyFile(`src/${scene}/index.html`,`dist/${scene}/index.html`);
  await copyFile(`src/${scene}/REFERENCES.md`,`dist/${scene}/REFERENCES.md`);
  await mkdir(`dist/${scene}/assets`,{recursive:true});
  const model=scene==='hall'?'great-hall.glb':'dueling-arena.glb';
  for(const file of [model,'metadata.json'])await copyFile(`scene-assets/${scene}/${file}`,`dist/${scene}/assets/${file}`);
  await cp(`src/${scene}/references`,`dist/${scene}/references`,{recursive:true}).catch(e=>{if(e.code!=='ENOENT')throw e;});
}
await copyFile('src/interior/index.html','dist/interior/index.html');
for(const id of INTERIORS){
  await mkdir(`dist/rooms/${id}`,{recursive:true});
  for(const file of ['scene.glb','metadata.json'])await copyFile(`scene-assets/${id}/${file}`,`dist/rooms/${id}/${file}`);
}
await copyFile('REFERENCES.md','dist/REFERENCES.md');
console.log('Built memoir, hall, arena, six interior routes and shared local resources.');

await mkdir("dist/world", {recursive:true});
for (const file of ["index.html","world.css","evening-sky.jpg","moon.webp","wind-waves.webp","lakebed.webp","grounds.glb","layout.json","navigation.json","ground-plan.png","rooms.json","Three-LICENSE.txt","CREDITS.md","reference-comparison.jpg","lake-comparison.jpg","style-comparison.jpg","pitch-comparison.jpg","campus-comparison.jpg","campus-preview.jpg","arrival-comparison.jpg","map-review.jpg","highlands-preview.jpg"]) await copyFile("world/"+file,"dist/world/"+file);

await build({entryPoints:['world/src/main.js'],outfile:'dist/world/world.js',bundle:true,minify:true,legalComments:'linked'});
