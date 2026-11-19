// Circle against furniture rectangles in the Hall's X/Z ground plane.
export const OBSTACLES=[-4.65,-2.9,2.9,4.65].map(z=>({x0:-4.7,x1:20.1,z0:z-.94*.74,z1:z+.94*.74}));
const R=.23;
export function acceptNavigationKey(target,dialogOpen=false){
  return !dialogOpen&&!target?.isContentEditable&&!/^(INPUT|SELECT|TEXTAREA)$/.test(target?.tagName||'');
}
export function blocked(x,z,obstacles=OBSTACLES){
  if(x<-6.95||x>20.55||z<-5.88||z>5.88)return true;
  return obstacles.some(o=>{
    const dx=x-Math.max(o.x0,Math.min(o.x1,x));const dz=z-Math.max(o.z0,Math.min(o.z1,z));
    return dx*dx+dz*dz<R*R;
  });
}
export function movePlayer(position,delta,obstacles=OBSTACLES){
  let {x,z}=position;
  if(![x,z,delta.x,delta.z].every(Number.isFinite))return {...position};
  const steps=Math.max(1,Math.ceil(Math.hypot(delta.x,delta.z)/.08));
  const dx=delta.x/steps,dz=delta.z/steps;
  for(let i=0;i<steps;i++){
    if(!blocked(x+dx,z,obstacles))x+=dx;
    if(!blocked(x,z+dz,obstacles))z+=dz;
  }
  return {x,z};
}
export function inputVector(keys,yaw){
  let forward=Number(keys.has('KeyW')||keys.has('ArrowUp'))-Number(keys.has('KeyS')||keys.has('ArrowDown'));
  let right=Number(keys.has('KeyD')||keys.has('ArrowRight'))-Number(keys.has('KeyA')||keys.has('ArrowLeft'));
  const len=Math.hypot(forward,right)||1;forward/=len;right/=len;
  return {x:-Math.sin(yaw)*forward+Math.cos(yaw)*right,z:-Math.cos(yaw)*forward-Math.sin(yaw)*right};
}
