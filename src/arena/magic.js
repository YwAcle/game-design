import * as THREE from 'three';
// Original ribbon geometry: tapered, overlapping ink-like strokes, not game assets.
export function createMagic(){
  const group=new THREE.Group(),animated=[];
  const colors=[new THREE.Color('#42cfff'),new THREE.Color('#ef6659')];
  for(let side=0;side<2;side++)for(let strand=0;strand<5;strand++){
    const points=[],sign=side?1:-1;
    for(let i=0;i<=64;i++){
      const t=i/64,a=t*Math.PI*1.65+side*Math.PI+strand*.18;
      const r=3.25*(1-t*.75)+strand*.12;
      points.push(new THREE.Vector3(Math.cos(a)*r, .45+t*2.45+Math.sin(t*Math.PI)*.5+strand*.08,Math.sin(a)*r+sign*(1-t)*1.7));
    }
    const curve=new THREE.CatmullRomCurve3(points),verts=[],uv=[],indices=[];
    for(let i=0;i<=96;i++){
      const t=i/96,p=curve.getPoint(t),tangent=curve.getTangent(t),normal=new THREE.Vector3(-tangent.z,.6,tangent.x).normalize();
      const width=(.035+.10*Math.sin(t*Math.PI))*(strand===0?1.6:.6)*(1-t*.72);
      for(const s of [-1,1]){verts.push(p.x+normal.x*width*s,p.y+normal.y*width*s,p.z+normal.z*width*s);uv.push(t,(s+1)/2);}
      if(i<96){const b=i*2;indices.push(b,b+1,b+2,b+1,b+3,b+2);}
    }
    const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));geometry.setIndex(indices);
    const material=new THREE.ShaderMaterial({transparent:true,depthWrite:false,side:THREE.DoubleSide,blending:THREE.AdditiveBlending,uniforms:{time:{value:0},color:{value:colors[side]},phase:{value:strand*.7+side*2}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'varying vec2 vUv;uniform float time;uniform float phase;uniform vec3 color;void main(){float edge=pow(sin(vUv.y*3.14159),.6);float tail=sin(vUv.x*3.14159);float pulse=.66+.34*sin(vUv.x*17.-time*2.+phase);gl_FragColor=vec4(color*2.2,edge*tail*(.45+pulse*.5));}'});
    animated.push(material);group.add(new THREE.Mesh(geometry,material));
  }
  const pos=[],col=[];
  for(let i=0;i<100;i++){
    const a=i*2.39996,r=.8+(i%29)/29*3.7;
    pos.push(Math.cos(a)*r,.15+(i%31)/31*3.1,Math.sin(a)*r);
    const c=colors[i%2];col.push(c.r,c.g,c.b);
  }
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('color',new THREE.Float32BufferAttribute(col,3));
  const pm=new THREE.ShaderMaterial({transparent:true,depthWrite:false,vertexColors:true,blending:THREE.AdditiveBlending,uniforms:{time:{value:0}},vertexShader:'uniform float time;varying vec3 vColor;varying float fade;void main(){vColor=color;vec3 p=position;p.y+=sin(time*.4+p.x)*.12;vec4 mv=modelViewMatrix*vec4(p,1.);gl_Position=projectionMatrix*mv;gl_PointSize=clamp(25./-mv.z,1.,3.);fade=.3+.5*pow(sin(time*.6+p.z*3.),2.);}',fragmentShader:'varying vec3 vColor;varying float fade;void main(){float d=length(gl_PointCoord-.5);gl_FragColor=vec4(vColor*1.6,(1.0-smoothstep(.1,.5,d))*fade);}'});
  animated.push(pm);group.add(new THREE.Points(g,pm));
  const glow=new THREE.Mesh(new THREE.PlaneGeometry(12,10),new THREE.ShaderMaterial({transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'varying vec2 vUv;void main(){vec2 p=(vUv-.5)*2.;float a=exp(-dot(p,p)*5.)*.20;vec3 c=mix(vec3(.1,.5,1.),vec3(1.,.14,.06),smoothstep(-.5,.5,p.y));gl_FragColor=vec4(c,a);}'}));
  glow.rotation.x=-Math.PI/2;glow.position.y=.045;group.add(glow);
  return {group,update(time){for(const m of animated)m.uniforms.time.value=time;}};
}

