import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { terrain, walkable } from './navigation.mjs';

export function addWoodlands(scene, layout, nav) {
  const canopy = [
    [.13, 1.16, .08, 0x426249],
    [.90, 1.46, .71, 0x3d6049],
    [.76, 1.34, 1.18, 0x4d6d51],
    [.58, 1.24, 1.65, 0x537655],
    [.43, 1.01, 2.13, 0x63845c],
    [.29, 1.01, 2.60, 0x799564],
  ].map(([radius,height,base,tint],tier) => {
    const geo = new THREE.CylinderGeometry(tier ? radius*.15 : radius*.68,radius,height,11,2);
    geo.rotateY(tier*.81);
    const positions = geo.attributes.position;
    const colors = [];
    const shade = new THREE.Color();
    for (let i=0;i<positions.count;i++) {
      const a = Math.atan2(positions.getZ(i),positions.getX(i));
      const r = 1 + .24*Math.sin(5*a+.8*tier) + .095*Math.cos(3*a+tier);
      const skirt = tier ? .15*Math.cos(5*a+tier) + .14*Math.sin(9*a+.54*tier) : 0;
      positions.setXYZ(i, positions.getX(i)*r, positions.getY(i)+base+height/2+skirt, positions.getZ(i)*r);
      shade.set(tint).multiplyScalar(.80+.19*Math.sin(a+1.2)+.09*Math.cos(5*a));
      colors.push(shade.r,shade.g,shade.b);
    }
    geo.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
    return geo;
  });
  const geometry = mergeGeometries(canopy);
  const material = new THREE.MeshStandardMaterial({vertexColors:true,flatShading:true,roughness:.98});
  const points = new Map(layout.places.map(p=>[p.id, new THREE.Vector2(...p.at)]));
  const segments = layout.trails.flatMap(trail => {
    const nodes=trail.map(p=>typeof p==='string'?points.get(p):new THREE.Vector2(...p));
    return nodes.slice(1).map((p,i)=>new THREE.Line3(
      new THREE.Vector3(nodes[i].x,0,nodes[i].y),new THREE.Vector3(p.x,0,p.y)
    ));
  });
  const close = new THREE.Vector3(), point = new THREE.Vector3(), transform = new THREE.Object3D();
  const shade = new THREE.Color();
  let seed = 742;
  const random = () => ((seed = (Math.imul(1664525, seed) + 1013904223) >>> 0) / 4294967296);
  // Keep trails and silhouettes readable by grouping trees along the edge of each valley.
  for (const [cx,cz,rx,rz,count] of [
    [106,-57,25,43,275], [96,3,29,37,210], [57,21,16,28,75],
    [-105,-68,15,26,125], [-103,12,16,34,145], [-31,33,30,9,100],
    [52,-78,17,20,90], [-66,-88,17,12,55],
  ]) {
    const trees = new THREE.InstancedMesh(geometry,material,count);
    let used = 0;
    for (let i=0;i<count;i++) {
      const theta = random()*Math.PI*2, r = Math.sqrt(random());
      const x = cx+Math.cos(theta)*rx*r, z = cz+Math.sin(theta)*rz*r;
      if (z > 57 || !walkable(nav,layout.bridge,x,z)) continue;
      point.set(x,0,z);
      if (segments.some(line=>line.closestPointToPoint(point,true,close).distanceToSquared(point)<10)) continue;
      if (layout.places.some(p=>Math.hypot(p.look[0]-x,p.look[1]-z)<6.2)) continue;
      const y = terrain(nav,x,z);
      const scale = .58+random()*.86;
      transform.position.set(x,y-.12,z);
      transform.rotation.y=random()*Math.PI*2;
      transform.scale.set(scale,scale*(1.05+random()*.36),scale);
      transform.updateMatrix();
      const index=used++;
      trees.setMatrixAt(index,transform.matrix);
      trees.setColorAt(index,shade.setHSL(.17+random()*.13,.28+random()*.22,.45+random()*.21));
    }
    trees.count=used;
    if (trees.count) {
      trees.name = 'Highland fir stands';
      trees.receiveShadow = true;
      scene.add(trees);
    }
  }
}
