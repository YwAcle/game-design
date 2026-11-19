const clamp = (n, low, high) => Math.min(Math.max(n, low), high);

export function terrain(nav, x, z) {
  const { heights, step, x0, z0 } = nav;
  const u = clamp((x - x0) / step, 0, heights[0].length - 1);
  const v = clamp((z - z0) / step, 0, heights.length - 1);
  const i = Math.min(Math.floor(u), heights[0].length - 2);
  const j = Math.min(Math.floor(v), heights.length - 2);
  const [p, q] = [heights[j][i], heights[j][i + 1]];
  const [r, s] = [heights[j + 1][i], heights[j + 1][i + 1]];
  const a = u - i, b = v - j;
  return a >= b ? p + (q - p) * a + (s - q) * b : p + (s - r) * a + (r - p) * b;
}

function onPier(pier, x, z) {
  return Math.abs(x - pier.x) <= pier.width / 2 && z >= pier.z0 && z <= pier.z1;
}

export function floorHeight(nav, bridge, x, z) {
  if (onPier(nav.pier, x, z)) return Math.max(.85, terrain(nav, nav.pier.x, nav.pier.z0));
  if (x >= bridge.x0 && x <= bridge.x1 && Math.abs(z - bridge.z) <= bridge.width / 2) {
    const t = (x - bridge.x0) / (bridge.x1 - bridge.x0);
    const sample = t * (nav.bridgeProfile.length - 1);
    const i = Math.min(Math.floor(sample), nav.bridgeProfile.length - 2);
    const f = sample - i;
    return (1 - f) * nav.bridgeProfile[i] + f * nav.bridgeProfile[i + 1];
  }
  const base = terrain(nav, x, z);
  for (const stair of nav.flights ?? []) {
    const dx=x-stair.cx, dz=z-stair.cz;
    if (Math.abs(dx)>4 || Math.abs(dz)>4) continue;
    const c=Math.cos(stair.angle), s=Math.sin(stair.angle);
    const across=dx*c-dz*s, along=-dx*s-dz*c;
    if (Math.abs(across)>stair.width/2 || Math.abs(along)>stair.length/2) continue;
    const t=clamp(along/stair.length+.5,0,1)*(stair.profile.length-1);
    const i=Math.min(Math.floor(t),stair.profile.length-2);
    return Math.max(base,stair.profile[i]+(stair.profile[i+1]-stair.profile[i])*(t-i));
  }
  return base;
}

export function walkable(nav, bridge, x, z) {
  if (x < -117 || x > 122 || z < -101 || (z > 57 && !onPier(nav.pier, x, z)) || floorHeight(nav, bridge, x, z) < .13) return false;
  if (x > bridge.x0 && x < bridge.x1 && Math.abs(Math.abs(z - bridge.z) - bridge.width / 2) < .43) return false;
  const atTerrace = nav.standRails?.some(([cx, cz, tx, tz, half, depth]) => {
    const dx = x - cx, dz = z - cz;
    return Math.abs(dx * tx + dz * tz) < half + .31 &&
      Math.abs(dx * tz - dz * tx) < depth;
  });
  return !atTerrace && !nav.blocks.some(([left, top, right, bottom]) =>
    x > left - .31 && x < right + .31 && z > top - .31 && z < bottom + .31);
}

export function atDoor(place,x,z) {
  return !!place?.door && Math.hypot(x-place.door[0],z-place.door[1]) <= 3.9;
}
