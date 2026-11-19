"""Original dueling-club interpretation of official promotional images.
Blender 5.3: blender -b --python model/build_arena.py [-- --draft]
"""
import bpy,bmesh,sys,os,math,random,json
from math import sin,cos,pi
from mathutils import Vector
HERE=os.path.dirname(os.path.abspath(__file__));ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
sys.path.insert(0,HERE);import geometry as g
random.seed(812);bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;g.BOXES.clear()

def painted(name,a,b,texture=None,axis='XY',metal=0):
    m=g.material(name,a,b,.88,metal,3)
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
    for bump in n:
        if bump.type=='BUMP':bump.inputs['Strength'].default_value=.018
    if texture:
        tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(os.path.join(HERE,'textures',texture+'.jpg'),check_existing=True)
        co=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');comb=n.new('ShaderNodeCombineXYZ');l.new(co.outputs['Generated'],sep.inputs[0]);l.new(sep.outputs[axis[0]],comb.inputs['X']);l.new(sep.outputs[axis[1]],comb.inputs['Y']);l.new(comb.outputs[0],tex.inputs[0])
        if texture=='plaster':
            geo=n.new('ShaderNodeNewGeometry');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=.18;l.new(geo.outputs['Position'],scale.inputs[0]);l.new(scale.outputs[0],tex.inputs[0]);tex.projection='BOX';tex.projection_blend=.25
        mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.7;l.new(tex.outputs[0],mix.inputs[1]);mix.inputs[2].default_value=(*b,1);l.new(mix.outputs[0],p.inputs['Base Color'])
    return m
STONE=painted('Painted | weathered cool limestone',(.09,.10,.10),(.42,.44,.42),'plaster','XZ')
PALE=painted('Painted | carved edge highlights',(.14,.16,.16),(.51,.51,.45),'plaster','XZ')
DARK=painted('Painted | recesses',(.023,.028,.029),(.08,.095,.095))
WOOD=painted('Painted | dark oak',(.028,.021,.018),(.34,.29,.23),'oak','XZ')
RIM=painted('Painted | worn oak edges',(.065,.047,.028),(.48,.37,.24),'oak','XZ')
GOLD=painted('Painted | aged brass',(.10,.073,.032),(.35,.26,.12),metal=.5)
IRON=g.material('Blackened iron',(.025,.028,.028),rough=.65,metal=.45)
CLOTH=painted('Painted | oxblood cloth',(.09,.02,.02),(.63,.27,.23),'cloth','XZ')
BANNER=painted('Painted | bordered oxblood weave',(.09,.02,.02),(.66,.31,.25),'banner','XZ')
GLASS=g.material('Windows | frosted pale blue',(.27,.37,.42),rough=.65,emission=1.25)
FLAME=g.material('Lamps | warm flame',(.95,.54,.19),rough=.5,emission=5)
ETCH=g.material('Inlaid old silver',(.23,.25,.23),rough=.93)
FLOOR=[painted('Painted | flagstone '+str(i),(.10,.11,.11),(.62+i*.025,.65+i*.023,.64+i*.023),'stone'+str(i)) for i in range(5)]

g.collection('01 Court | carved flagstones')
g.box('Foundation',(0,0,-.33),(27,33,.5),DARK)
for ix in range(14):
    for iy in range(18):
        x=(ix-6.5)*1.90;y=(iy-8.5)*1.90
        o=g.box('Hand edged flagstone',(x,y,-.075+random.uniform(-.006,.006)),(1.872,1.872,.15),FLOOR[(ix*3+iy*7)%5],.028)
        o.rotation_euler.z=random.choice([0,math.pi/2,math.pi,3*math.pi/2])
        if random.random()<.07 and abs(x)<9.2 and abs(y)<12:
            pts=[(x-.48,y+.29,.009),(x-.19,y+.17,.010),(x-.10,y-.08,.011),(x+.22,y-.18,.011)]
            g.path('Fine fissure',pts,.007,DARK)
# Shallow geometric inlay: authored reconstruction of partially occluded markings.
for r in [2.45,2.52,3.10]:
    g.path('Worn center circle',[(r*cos(i*2*pi/128),r*sin(i*2*pi/128),.015) for i in range(128)],.012,ETCH,True)
for i in range(8):
    a=i*pi/4;pts=[]
    for rr,da in [(3.9,0),(1.2,.14),(1.8,pi/8),(1.2,pi/4-.14)]:pts.append((rr*cos(a+da),rr*sin(a+da),.017))
    g.path('Compass incised filigree',pts,.012,ETCH)
for y in [-7.4,7.4]:
    g.path('Duelist position',[(.85*cos(i*2*pi/64),y+.85*sin(i*2*pi/64),.018) for i in range(64)],.018,ETCH,True)
for x in [-9.25,9.25]:g.box('Court stone border',(x,0,.015),(.17,24,.035),PALE,.015)
for y in [-12,12]:g.box('Court stone border',(0,y,.015),(18.5,.17,.035),PALE,.015)

g.collection('02 Galleries | tiered seating')
def panel(a,b):
    a,b=Vector(a),Vector(b);d=b-a;mid=(a+b)/2;angle=math.atan2(d.y,d.x);w=d.length
    g.box('Raised panel barrier',(mid.x,mid.y,.57),(w,.19,1.14),WOOD,.022,angle)
    g.box('Brushed handrail',(mid.x,mid.y,1.16),(w+.12,.30,.11),RIM,.025,angle)
    for u in [i*w/max(1,round(w/1.4)) for i in range(round(w/1.4)+1)]:
        p=a+d*u/w;g.box('Panel stile',(p.x,p.y,.6),(.075,.26,1.1),RIM,.012,angle)
    n=max(1,round(w/1.4))
    for j in range(n):
        u=(j+.5)*w/n;c=a+d*u/w;ww=w/n-.24
        for s in [-1,1]:
            offset=Vector((-sin(angle)*s*.109,cos(angle)*s*.109,0))
            for z in [.19,.94]:g.box('Inset panel beading',(c.x+offset.x,c.y+offset.y,z),(ww,.035,.035),RIM,.008,angle)
            for dx in [-ww/2,ww/2]:g.box('Inset panel beading',(c.x+dx*cos(angle)+offset.x,c.y+dx*sin(angle)+offset.y,.565),(.035,.035,.75),RIM,.008,angle)

for side in [-1,1]:
    panel((side*9.5,-11.6,0),(side*9.5,11.6,0))
    for row in range(3):
        x=side*(10.1+row*.85);z=.26+row*.57
        g.box('Gallery riser',(x,0,z/2),(.84,24.5,z),WOOD,.025)
        for k in [-1,1]:
            y=k*6.5
            g.box('Long bench seat',(x,y,z+.48),(.63,10.5,.14),RIM,.025)
            g.box('Long bench back',(x+side*.28,y,z+.85),(.10,10.5,.75),WOOD,.025)
            for yy in [y-4.8,y-2.4,y,y+2.4,y+4.8]:
                for xx in [-.23,.23]:g.box('Bench foot',(x+xx,yy,z+.22),(.10,.13,.45),WOOD,.01)
                g.box('Bench back upright',(x+side*.31,yy,z+.8),(.16,.12,.95),RIM,.015)
        # aisle stair treads in the central gap
        g.box('Gallery aisle step',(x,0,z),(.87,1.5,.13),STONE,.015)
    for end in [-1,1]:
        panel((side*9.5,end*11.6,0),(side*8.4,end*12.5,0))
for end in [-1,1]:
    for side in [-1,1]:
        panel((side*1.7,end*12.5,0),(side*8.4,end*12.5,0))
        for row in range(3):
            y=end*(13.1+row*.82);z=.27+row*.57
            g.box('End gallery riser',(side*5.1,y,z/2),(6.8,.8,z),WOOD,.02)
            g.box('End bench',(side*5.1,y,z+.46),(6.5,.58,.14),RIM,.02)
            g.box('End bench back',(side*5.1,y+end*.23,z+.88),(6.5,.13,.8),WOOD,.025)
            for x in [side*2.1,side*4.1,side*6.1,side*8.1]:g.box('End bench support',(x,y,z+.24),(.13,.47,.48),WOOD,.015)

g.collection('03 Architecture | lancet windows')
def window(c,ang,w=2.05,h=7):
    # Portal contains a true void. Thin glass is at the exterior face.
    g.portal('Gothic window bay',c,w,h,4.6,9.9,.6,STONE,PALE,ang)
    pts=g.arch_points(w-.12,h-.13)
    g.mesh('Pale window glass',[g.tf(c,u,.29,z+.035,ang) for u,z in pts],[tuple(range(len(pts)))],GLASS)
    for u in [-w/6,w/6]:g.beam('Vertical stone mullion',g.tf(c,u,0,.06,ang),g.tf(c,u,0,h-.48,ang),.06,PALE)
    for z in [1.65,3.3,4.95]:g.beam('Horizontal window saddlebar',g.tf(c,-w/2,0,z,ang),g.tf(c,w/2,0,z,ang),.045,DARK)
    # Visible leaded diamonds, clipped below the lancet crown.
    for z in [i*.65 for i in range(9)]:
        for u in [-.68,0,.68]:
            for s in [-1,1]:g.beam('Diamond leadwork',g.tf(c,u-.32,-.03,z+.2,ang),g.tf(c,u+.32,-.03,z+.2+s*.65,ang),.018,DARK)
    # Stepped sill and pointed hood.
    for zz,ww,dd in [(-.13,w+.5,.85),(-.30,w+.32,.72)]:g.box('Window sill',g.tf(c,0,0,zz,ang),(ww,dd,.16),PALE,.025,ang)

def pilaster(c,ang=0):
    for z,ww,dd,hh in [(1.5,.90,.78,3),(7,.58,.56,8),(11.2,.88,.78,.45),(11.57,1.03,.86,.25),(12.85,.65,.55,2.3)]:
        g.box('Tiered Gothic pier',g.tf(c,0,0,z,ang),(ww,dd,hh),PALE,.035,ang)
    for u in [-.22,.22]:g.beam('Pier edge flute',g.tf(c,u,-.33,3.2,ang),g.tf(c,u,-.33,10.9,ang),.07,STONE)
    for i in range(4):
        g.box('Carved capital tooth',g.tf(c,(i-1.5)*.21,-.45,11.32,ang),(.10,.2,.30),STONE,.015,ang)
    # Angular corbel silhouette, with a cut diamond on its face.
    vs=[g.tf(c,u,d,z,ang) for u,d,z in [(-.38,-.35,3.3),(.38,-.35,3.3),(.28,-.68,3.75),(-.28,-.68,3.75),(-.45,-.35,4),(.45,-.35,4)]]
    g.mesh('Cut stone corbel',vs,[(0,1,2,3),(3,2,5,4),(0,3,4),(1,5,2),(0,4,5,1)],STONE)

for side in [-1,1]:
    x=side*13.25;ang=-side*pi/2
    g.box('Lower side masonry',(x,0,1.55),(.7,32.6,3.1),STONE,.03)
    for y in [-12,-7.2,-2.4,2.4,7.2,12]:window((x,y,3.1),ang)
    for y in [-14.4,-9.6,-4.8,0,4.8,9.6,14.4]:pilaster((x-side*.28,y,0),ang)
    for z in [2.8,3.08,12.8,13.15]:g.box('Side stone stringcourse',(x-side*.18,0,z),(.9,32.5,.18),PALE,.02)
    # Block joints low on the supporting wall.
    for y in range(-15,16,2):g.box('Stone footing block',(x-side*.38,y,1.8),(.1,1.96,.8),STONE,.035)
for end in [-1,1]:
    y=end*16.0;ang=0 if end==1 else pi
    g.box('End lower masonry',(0,y,1.55),(26.5,.7,3.1),STONE,.025)
    for x in [-10,-5,5,10]:window((x,y,3.1),ang,2.0,6.9)
    for x in [-12.4,-7.5,-2.45,2.45,7.5,12.4]:pilaster((x,y-end*.27,0),ang)
    # Closed carved entrance in a recessed arch, with an ornate crest above.
    g.portal('Entrance arch',(0,y,0),3.5,6.7,4.9,13,.8,STONE,PALE,ang)
    pts=g.arch_points(3.35,6.55)
    g.mesh('Recessed wooden doors',[g.tf((0,y,0),u,.12,z,ang) for u,z in pts],[tuple(range(len(pts)))],WOOD)
    for x in [-1.25,-.83,-.41,0,.41,.83,1.25]:g.beam('Door planking',g.tf((0,y,0),x,-.02,.1,ang),g.tf((0,y,0),x,-.02,5.8,ang),.045,RIM)
    for z in [.5,2.7,5.1]:g.box('Forged door strap',g.tf((0,y,0),0,-.10,z,ang),(3.2,.10,.11),IRON,.01,ang)
    for x in [-.26,.26]:
        g.path('Door knocker',[g.tf((0,y,0),x+.12*cos(t*2*pi/24),-.18,2.2+.18*sin(t*2*pi/24),ang) for t in range(24)],.026,GOLD,True)
    for z in [3.1,12.8,13.15]:g.box('End stringcourse',(0,y-end*.17,z),(26.5,.9,.16),PALE,.02)
    g.text('Dueling Club carved lettering','DUELLING CLUB',g.tf((0,y,0),0,-.53,7.55,ang),.44,GOLD,rot=(pi/2,0,ang))

g.collection('04 Textiles | drapes and standards')
def fabric(name,c,w,h,mat,angle=0,pennant=False):
    vs=[];fs=[];nu=24;nv=12
    for j in range(nv+1):
        v=j/nv
        for i in range(nu+1):
            u=(i/nu-.5)*w;z=-v*h
            if pennant:z-=v**6*(1-abs(u)/(w/2))*.65
            depth=.16*sin(i/nu*pi*8)*(.45+v*.55)+.07*sin(v*pi*2+i*.3)
            vs.append(g.tf(c,u,depth,z,angle))
    for j in range(nv):
        for i in range(nu):
            a=j*(nu+1)+i;fs.append((a,a+1,a+nu+2,a+nu+1))
    o=g.mesh(name,vs,fs,mat,True)
    mod=o.modifiers.new('Fabric thickness','SOLIDIFY');mod.thickness=.025
    bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False)
    g.beam('Banner pole',g.tf(c,-w*.65,0,.13,angle),g.tf(c,w*.65,0,.13,angle),.055,GOLD)
    return o
for side in [-1,1]:
    ang=-side*pi/2
    for y in [-9.6,0,9.6]:
        c=(side*12.7,y,10.8);fabric('Pointed duel standard',c,1.4,4.4,BANNER,ang,True)
        # Shield and crossed wand insignia, modeled to remain readable.
        center=g.tf(c,0,-.21,-1.8,ang)
        pts=[(-.39,.48),(.39,.48),(.35,-.15),(0,-.50),(-.35,-.15)]
        g.path('Embroidered shield',[g.tf(center,u,0,z,ang) for u,z in pts],.025,GOLD,True)
        for s in [-1,1]:g.beam('Crossed wands badge',g.tf(center,-.22,-.02,s*.24,ang),g.tf(center,.22,-.02,-s*.24,ang),.031,GOLD)
    for y in [-12,-2.4,7.2]:
        for flank in [-1,1]:fabric('Window drape',(side*12.71,y+flank*1.22,11.8),.61,6.4,CLOTH,ang)
for end in [-1,1]:
    for x in [-2,2]:fabric('Entrance ceremonial curtain',(x,end*15.25,11.6),1.15,5.4,BANNER,0 if end==1 else pi,True)

g.collection('05 Details | lamps and finials')
flames=[]
for side in [-1,1]:
    for y in [-9.6,0,9.6]:
        x=side*12.65
        g.beam('Lamp bracket',(x,y,4.1),(x-side*.6,y,4.1),.10,IRON)
        c=(x-side*.64,y,4.35)
        g.lathe('Lamp cup',c,[(.07,-.22),(.26,-.12),(.32,0),(.26,.05)],GOLD,12)
        for a in [i*pi/2 for i in range(4)]:g.beam('Lantern rib',(c[0]+.26*cos(a),c[1]+.26*sin(a),4.35),(c[0]+.15*cos(a),c[1]+.15*sin(a),5.05),.035,IRON)
        g.cyl('Lantern pointed cap',(c[0],c[1],5.13),.27,.24,IRON,8,r2=0)
        g.sphere('Amber lamp core',(c[0],c[1],4.65),(.07,.07,.20),FLAME,8,6);flames.append([c[0],4.65,-c[1]])
        g.point('Warm local lantern',(c[0]-side*.13,c[1],4.7),52,(1,.56,.26),.4)
for side in [-1,1]:
    for y in [-11.6,-6,0,6,11.6]:
        x=side*9.5
        g.box('Balustrade newel',(x,y,.7),(.33,.33,1.4),WOOD,.03)
        g.cyl('Pointed newel',(x,y,1.53),.21,.33,RIM,4,r2=.045)
        g.box('Newel cap',(x,y,1.38),(.42,.42,.09),RIM,.02)

g.collection('06 Roof | open timber trusses')
for y in [-14.4,-9.6,-4.8,0,4.8,9.6,14.4]:
    for side in [-1,1]:
        g.beam('Hammerbeam',(side*12.8,y,12.9),(side*8.6,y,13.4),.35,WOOD)
        g.beam('Angled roof brace',(side*12.8,y,11.9),(side*9.6,y,13.4),.24,RIM)
        g.beam('Rafter',(side*12.8,y,13.4),(0,y,17.1),.31,WOOD)
    g.beam('Collar tie',(-8.7,y,14.7),(8.7,y,14.7),.24,WOOD)
g.box('Dark roof',(0,0,17.5),(27,33,.25),DARK)

g.collection('07 Lighting and views')
S.world.color=(.04,.04,.04);S.world.use_nodes=True
S.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.22,.27,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.22
for y in [-12,-7.2,-2.4,2.4,7.2,12]:
    g.area('Cold window daylight',(-13.0,y,8.3),(4,y-4,0),1250 if y in [-7.2,2.4] else 700,(.79,.85,.91),.85,'RECTANGLE',3)
    g.area('Opposite soft bounce',(12.4,y,8),(0,y,1),180,(.83,.84,.79),1.5,'RECTANGLE',4)
g.area('Top soft fill',(0,1,13.7),(0,1,0),500,(.80,.82,.79),11)
g.area('Doorway bounce',(0,14.8,6),(0,0,1),450,(.77,.84,1),5)
cam=g.camera('01 Overview',(7.8,-11.5,4.6),(-1,4,2.2),21)
ground=g.camera('02 On the court',(0,-10.7,1.75),(0,8,4.7),22)
opposite=g.camera('03 Upper gallery',(-10.9,13.8,7.0),(0,-1,2.4),24)
S.camera=cam;S.render.engine='CYCLES';S.cycles.samples=32;S.cycles.use_denoising=True
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
for d in p.devices:d.use=d.type=='CUDA'
S.cycles.device='GPU';S.cycles.max_bounces=5
S.render.resolution_x=1600;S.render.resolution_y=900;S.render.resolution_percentage=100
S.view_settings.view_transform='AgX';S.view_settings.exposure=.3
S.render.image_settings.file_format='PNG';S.render.film_transparent=False
# Convert curves and correct all closed-mesh winding before rendering or baking.
for o in list(S.objects):
    if o.type in ['CURVE','FONT']:
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
seen=set();closed=0;inverted=0
for o in S.objects:
    if o.type!='MESH' or o.data.as_pointer() in seen:continue
    seen.add(o.data.as_pointer());bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    if all(e.is_manifold for e in bm.edges):
        closed+=1
        if bm.calc_volume(signed=True)<-1e-6:inverted+=1
    bm.to_mesh(o.data);bm.free()
meta={'flames':flames,'closedMeshes':closed,'invertedClosedMeshes':inverted,'source':'Dueling_Club.blend','courtBounds':{'x':9.1,'z':12.0,'cornerSum':20.1}}
with open(os.path.join(ROOT,'scene-assets','arena','metadata.json'),'w') as f:json.dump(meta,f,indent=2)
for im in bpy.data.images:
    if im.source=='FILE':im.pack()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE,'Dueling_Club.blend'))
S.render.filepath=os.path.join(ROOT,'previews','blender-arena-v2.png');S.render.resolution_percentage=65;S.cycles.samples=12;bpy.ops.render.render(write_still=True)
print('ARENA_BUILD_COMPLETE',len(S.objects),closed,inverted,flush=True)
