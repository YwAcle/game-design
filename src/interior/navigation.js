export {inputVector,acceptNavigationKey} from '../arena/navigation.js';
export function canStand(x,z,room,radius=.25){
  const b=room.bounds;
  if(!Number.isFinite(x)||!Number.isFinite(z)||x<b.minX+radius||x>b.maxX-radius||z<b.minZ+radius||z>b.maxZ-radius)return false;
  return !(room.obstacles||[]).some(o=>x>o.minX-radius&&x<o.maxX+radius&&z>o.minZ-radius&&z<o.maxZ+radius);
}
export function movePlayer(p,d,room,radius=.25){
  let {x,z}=p;if(![x,z,d.x,d.z].every(Number.isFinite))return {x,z};
  const n=Math.max(1,Math.ceil(Math.hypot(d.x,d.z)/.1)),dx=d.x/n,dz=d.z/n;
  for(let i=0;i<n;i++){
    if(canStand(x+dx,z,room,radius))x+=dx;
    if(canStand(x,z+dz,room,radius))z+=dz;
  }
  return {x,z};
}
