import http from 'node:http';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {readFile,stat} from 'node:fs/promises';
import {spawn} from 'node:child_process';
const root=path.join(path.dirname(fileURLToPath(import.meta.url)),'dist');
const port=Number(process.env.MEMORIES_PORT||4175);
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json','.glb':'model/gltf-binary','.wasm':'application/wasm','.jpg':'image/jpeg','.png':'image/png','.webp':'image/webp','.svg':'image/svg+xml','.md':'text/plain; charset=utf-8','.txt':'text/plain; charset=utf-8'};
const server=http.createServer(async(req,res)=>{
  try{
    const url=new URL(req.url,'http://localhost');let pathname=decodeURIComponent(url.pathname);
    if(pathname.endsWith('/'))pathname+='index.html';
    const file=path.resolve(root,'.'+pathname),relative=path.relative(root,file);
    if(relative.startsWith('..')||path.isAbsolute(relative)){res.writeHead(403).end();return;}
    const info=await stat(file);
    if(info.isDirectory()){res.writeHead(302,{Location:url.pathname+'/'}).end();return;}
    if(!info.isFile())throw new Error('Not a file');
    const data=await readFile(file);
    res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream','Content-Length':data.length,'Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'});
    res.end(req.method==='HEAD'?undefined:data);
  }catch{res.writeHead(404,{'Content-Type':'text/plain; charset=utf-8'}).end('Not found');}
});
server.on('error',error=>{console.error(error.code==='EADDRINUSE'?`Port ${port} is in use. If this site is already running, open http://127.0.0.1:${port}/. Otherwise close the other server or set MEMORIES_PORT.`:error);process.exitCode=1;});
server.listen(port,'127.0.0.1',()=>{
  const url=`http://127.0.0.1:${port}/`;console.log(`Hogwarts, Always: ${url}`);
  if(process.argv.includes('--open')){
    const command=process.platform==='win32'?'rundll32.exe':process.platform==='darwin'?'open':'xdg-open';
    const args=process.platform==='win32'?['url.dll,FileProtocolHandler',url]:[url];
    spawn(command,args,{windowsHide:true,stdio:'ignore'}).on('error',()=>console.log(`Open ${url} in your browser.`));
  }
});
