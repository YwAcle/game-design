// Court limits include a 0.25m player clearance from the modeled rails.
export function insideCourt(x,z){return Math.abs(x)<=9.1&&Math.abs(z)<=12&&Math.abs(x)+Math.abs(z)<=20.1;}
export function movePlayer(p,d){
  let {x,z}=p;if(![x,z,d.x,d.z].every(Number.isFinite))return {x,z};
  const n=Math.max(1,Math.ceil(Math.hypot(d.x,d.z)/.1)),dx=d.x/n,dz=d.z/n;
  for(let i=0;i<n;i++){if(insideCourt(x+dx,z))x+=dx;if(insideCourt(x,z+dz))z+=dz;}
  return {x,z};
}
export function inputVector(keys,yaw){
  let f=Number(keys.has('KeyW')||keys.has('ArrowUp'))-Number(keys.has('KeyS')||keys.has('ArrowDown'));
  let r=Number(keys.has('KeyD')||keys.has('ArrowRight'))-Number(keys.has('KeyA')||keys.has('ArrowLeft'));
  const len=Math.hypot(f,r)||1;f/=len;r/=len;
  return {x:-Math.sin(yaw)*f+Math.cos(yaw)*r,z:-Math.cos(yaw)*f-Math.sin(yaw)*r};
}
export function acceptNavigationKey(target,dialogOpen=false){return !dialogOpen&&!target?.isContentEditable&&!/^(INPUT|SELECT|TEXTAREA)$/.test(target?.tagName||'');}
