"""Small Blender geometry library. All coordinates use metres."""
import bpy, math, random
from mathutils import Vector
from math import sin,cos,pi,sqrt
CURRENT=None
BOXES={}
def collection(name):
    global CURRENT
    c=bpy.data.collections.get(name)
    if not c:c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c)
    CURRENT=c
    return c
def mesh(name,vs,fs,mat,smooth=False):
    m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update()
    o=bpy.data.objects.new(name,m);CURRENT.objects.link(o)
    if mat:m.materials.append(mat)
    if smooth:
        for p in m.polygons:p.use_smooth=True
    return o
def box(name,loc,dim,mat,bevel=0,angle=0):
    key=(mat.name,round(bevel,5),tuple(round(v,4) for v in dim))
    if key not in BOXES:
        vs=[(x*dim[0]/2,y*dim[1]/2,z*dim[2]/2) for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
        o=mesh(name,vs,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],mat)
        if bevel:
            mod=o.modifiers.new('Worn edge','BEVEL');mod.width=bevel;mod.segments=2
            bpy.context.view_layer.objects.active=o;o.select_set(True)
            bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False)
        BOXES[key]=o.data
    else:o=bpy.data.objects.new(name,BOXES[key]);CURRENT.objects.link(o)
    o.location=loc;o.rotation_euler.z=angle;return o
def cyl(name,loc,r,h,mat,n=24,r2=None):
    if r2 is None:r2=r
    vs=[(rr*cos(i*2*pi/n),rr*sin(i*2*pi/n),z) for rr,z in [(r,-h/2),(r2,h/2)] for i in range(n)]
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    o=mesh(name,vs,fs,mat);o.location=loc;return o
def lathe(name,loc,profile,mat,n=24):
    vs=[];rings=[];fs=[]
    for r,z in profile:
        if abs(r)<1e-8:rings.append([len(vs)]);vs.append((0,0,z))
        else:
            rings.append(list(range(len(vs),len(vs)+n)))
            vs.extend([(r*cos(i*2*pi/n),r*sin(i*2*pi/n),z) for i in range(n)])
    for lower,upper in zip(rings,rings[1:]):
        if len(lower)==1 and len(upper)>1:
            fs.extend([(lower[0],upper[(i+1)%n],upper[i]) for i in range(n)])
        elif len(upper)==1 and len(lower)>1:
            fs.extend([(lower[i],lower[(i+1)%n],upper[0]) for i in range(n)])
        elif len(lower)>1 and len(upper)>1:
            fs.extend([(lower[i],lower[(i+1)%n],upper[(i+1)%n],upper[i]) for i in range(n)])
    o=mesh(name,vs,fs,mat,True);o.location=loc;return o

def path(name,pts,r,mat,closed=False):
    d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=1;d.bevel_depth=r;d.bevel_resolution=2
    s=d.splines.new('POLY');s.points.add(len(pts)-1)
    for p,v in zip(s.points,pts):p.co=(*v,1)
    s.use_cyclic_u=closed;o=bpy.data.objects.new(name,d);CURRENT.objects.link(o);d.materials.append(mat);return o
def beam(name,a,b,w,mat,w2=None):
    a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(w,w if w2 is None else w2,(b-a).length),mat,.015);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def sphere(name,loc,scale,mat,n=16,rings=8):
    profile=[(sin(pi*j/rings),cos(pi*j/rings)) for j in range(rings+1)]
    o=lathe(name,loc,profile,mat,n)
    for v in o.data.vertices:
        v.co.x*=scale[0];v.co.y*=scale[1];v.co.z*=scale[2]
    return o

def material(name,a,b=None,rough=.7,metal=0,noise_scale=3,grain=False,emission=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*a,1)
    nt=m.node_tree;n=nt.nodes;l=nt.links;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*a,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if emission:p.inputs['Emission Color'].default_value=(*a,1);p.inputs['Emission Strength'].default_value=emission
    if b:
        tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=noise_scale;noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.75
        if grain:
            mul=n.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=(7,.45,15);l.new(tc.outputs['Object'],mul.inputs[0]);l.new(mul.outputs[0],noise.inputs['Vector'])
        else:l.new(tc.outputs['Object'],noise.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.15;ramp.color_ramp.elements[0].color=(*a,1);ramp.color_ramp.elements[1].position=.85;ramp.color_ramp.elements[1].color=(*b,1)
        l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
        bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.24;bump.inputs['Distance'].default_value=.023 if grain else .045;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    return m
def tf(c,u,d,z,angle=0):return (c[0]+u*cos(angle)-d*sin(angle),c[1]+u*sin(angle)+d*cos(angle),c[2]+z)
def arch_height(u,w,h,spring=None):
    if spring is None:spring=h*.65
    t=min(1,(abs(u)+w/2)/w)
    return spring+(h-spring)*sqrt(max(0,1-t*t))/.8660254
def arch_points(w,h):
    return [(-w/2,0),(w/2,0)]+[(w/2-i*w/32,arch_height(w/2-i*w/32,w,h)) for i in range(33)]
def arch_frame(name,c,w,h,r,mat,angle=0):
    return path(name,[tf(c,u,-.025,z,angle) for u,z in arch_points(w,h)],r,mat,True)
def portal(name,c,w,h,span,top,depth,mat,trim,angle=0):
    # Solid wall assembled around the void. No hidden flat panel across the opening.
    def b(u,z,du,dz,label):return box(name+' '+label,tf(c,u,0,z,angle),(du,depth,dz),mat,.012,angle)
    side=(span-w)/2
    for sign in [-1,1]:b(sign*(w/2+side/2),top/2,side,top,'pier')
    vs=[];fs=[]
    # Curved lower edge and level top make the spandrel watertight.
    for i in range(33):
        u=-w/2+i*w/32;lo=arch_height(u,w,h)
        for d,z in [(-depth/2,lo),(depth/2,lo),(-depth/2,top),(depth/2,top)]:vs.append(tf(c,u,d,z,angle))
    for i in range(32):
        a=i*4;b0=(i+1)*4;fs.extend([(a,b0,b0+2,a+2),(a+1,a+3,b0+3,b0+1),(a,a+1,b0+1,b0),(a+2,b0+2,b0+3,a+3)])
    fs.extend([(0,2,3,1),(128,129,131,130)])
    mesh(name+' arched spandrel',vs,fs,mat)
    for d in [-depth/2-.035,depth/2+.035]:arch_frame(name+' carved archivolt',tf(c,0,d,0,angle),w+.12,h+.06,.10,trim,angle)
    return {'center':list(c),'width':w,'height':h,'angle':angle}
def text(name,body,loc,size,mat,rot=(pi/2,0,0),align='CENTER'):
    d=bpy.data.curves.new(name,'FONT');d.body=body;d.size=size;d.align_x=align;d.extrude=.003;d.bevel_depth=.001
    o=bpy.data.objects.new(name,d);CURRENT.objects.link(o);o.location=loc;o.rotation_euler=rot;d.materials.append(mat);return o
def area(name,loc,target,power,color,size=3,shape='DISK',size_y=None):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape=shape;d.size=size
    if size_y is not None:d.size_y=size_y
    o=bpy.data.objects.new(name,d);CURRENT.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def point(name,loc,power,color,r=.3):
    d=bpy.data.lights.new(name,'POINT');d.energy=power;d.color=color;d.shadow_soft_size=r;o=bpy.data.objects.new(name,d);CURRENT.objects.link(o);o.location=loc;return o
def camera(name,loc,target,lens=24):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);CURRENT.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.07;d.clip_end=1400;return o
