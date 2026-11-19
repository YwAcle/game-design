"""Refine the existing authored Hall, then render and save the editable scene.
Blender -b --python refine_hall.py -- [source.blend]
"""
import bpy, bmesh, os, sys, random, math, json
from mathutils import Vector
from math import sin, cos, pi
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
sys.path.insert(0,HERE)
import interior_geometry as g
random.seed(417)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
source=args[0] if args else os.path.join(HERE,'Foundation.blend')
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(source))
S=bpy.context.scene

def drop(o):bpy.data.objects.remove(o,do_unlink=True)
for o in list(S.objects):
    groups=[c.name[:2] for c in o.users_collection]
    keep=any(c in ['10','11','12','13'] for c in groups)
    if '16' in groups:
        p=o.matrix_world.translation
        keep=-7.6<p.x<26 and 23<p.y<37
    if o.type=='CAMERA':keep=o.name=='04 Interior | Great Hall'
    if not keep:drop(o)

# Remove the old flat-looking emblems and overly repetitive feast pieces.
for o in list(S.objects):
    if o.name.startswith(('I | house initial','I | banner embroidered shield','I | banner crossbar')) or 'hanging banner' in o.name:drop(o);continue
    if o.name.startswith(('I | feast apple','I | bread loaf')) and random.random()<.6:drop(o);continue
    if o.name.startswith(('I | brass goblet','I | pewter dinner plate')):
        o.location.x+=random.uniform(-.11,.11);o.location.y+=random.uniform(-.045,.045)
        o.rotation_euler.z=random.uniform(-.15,.15)

def painted(name,a,b,wood=False,rough=.85,metal=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
    out=n.new('ShaderNodeOutputMaterial');p=n.new('ShaderNodeBsdfPrincipled')
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    l.new(p.outputs[0],out.inputs[0]);tc=n.new('ShaderNodeNewGeometry')
    mul=n.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=(.5,24,26) if wood else (1.3,1.3,2.1)
    l.new(tc.outputs['Position'],mul.inputs[0])
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2.5;noise.inputs['Detail'].default_value=3.3;noise.inputs['Roughness'].default_value=.8
    l.new(mul.outputs[0],noise.inputs[0]);r=n.new('ShaderNodeValToRGB')
    r.color_ramp.elements[0].position=.2;r.color_ramp.elements[0].color=(*a,1)
    r.color_ramp.elements[1].position=.8;r.color_ramp.elements[1].color=(*b,1)
    r.color_ramp.elements.new(.48).color=(*(v*.55+w*.45 for v,w in zip(a,b)),1)
    l.new(noise.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.32;bump.inputs['Distance'].default_value=.022 if wood else .065
    l.new(noise.outputs[0],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    return m

STONE=painted('I | warm sandstone',(.105,.103,.079),(.235,.221,.165))
PALE=painted('I | dressed pale limestone',(.20,.19,.14),(.38,.35,.25))
DARK=painted('I | oak aged dark',(.018,.012,.009),(.07,.043,.020),True)
OAK=painted('I | polished honey oak',(.065,.037,.019),(.19,.126,.066),True,.74)
GOLD=painted('I | antique brass',(.16,.10,.035),(.36,.24,.10),False,.5,.62)
IRON=bpy.data.materials['I | black iron'];WAX=bpy.data.materials['I | ivory beeswax']
for i in range(5):painted('I | limestone flag '+str(i),(.12+i*.009,.119+i*.008,.095+i*.007),(.255+i*.013,.24+i*.012,.18+i*.009),rough=.88)
painted('I | apples',(.12,.017,.009),(.32,.068,.025),rough=.63)
painted('I | bread crust',(.16,.063,.017),(.39,.21,.071),rough=.91)
painted('I | pewter plate',(.105,.115,.10),(.27,.28,.22),rough=.52,metal=.5)
glass=bpy.data.materials['I | moonlit diamond glass'];p=glass.node_tree.nodes.get('Principled BSDF')
p.inputs['Base Color'].default_value=(.045,.09,.12,1);p.inputs['Emission Color'].default_value=(.13,.23,.32,1);p.inputs['Emission Strength'].default_value=.8
# Give the large east window a cooler, uneven leaded-glass colour.
n=glass.node_tree.nodes;l=glass.node_tree.links
geo=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1.4;noise.inputs['Detail'].default_value=1
l.new(geo.outputs['Position'],noise.inputs[0]);r=n.new('ShaderNodeValToRGB')
r.color_ramp.elements[0].color=(.025,.055,.075,1);r.color_ramp.elements[1].color=(.21,.31,.40,1)
l.new(noise.outputs[0],r.inputs[0]);l.new(r.outputs[0],p.inputs['Emission Color'])

g.collection('20 Refined Hall | carved details')
# Gothic tracery subdivides the east aperture, including four quatrefoil rosettes.
for yy in [27.9,30,32.1]:
    g.arch_frame('R | eastern lancet tracery',(25.0,yy,20.1),1.93,10.8,.065,PALE,pi/2)
for zz in [24,27,29.2]:g.beam('R | east transom',(24.97,26.8,zz),(24.97,33.2,zz),.07,PALE)
for yy,zz in [(28.9,30),(31.1,30),(30,31.4)]:
    for i in range(4):
        cy=yy+.23*cos(i*pi/2);cz=zz+.23*sin(i*pi/2)
        g.path('R | quatrefoil tracery',[(24.88,cy+.29*cos(t*2*pi/32),cz+.29*sin(t*2*pi/32)) for t in range(32)],.043,PALE,True)

# Carved winged corbels and suspended braziers, based on the game's silhouette.
for xx in [-4,3.6,11.2,18.8]:
    for sign in [-1,1]:
        yy=30+sign*5.65;z=23.7
        g.lathe('R | carved wall corbel',(xx,yy,z-.3),[(.16,-.65),(.31,-.5),(.25,-.38),(.43,-.25),(.40,0)],PALE,12)
        g.sphere('R | stone beast breast',(xx,yy,z+.34),(.24,.31,.48),PALE,12,8)
        g.sphere('R | stone beast head',(xx,yy-sign*.20,z+.82),(.22,.24,.25),PALE,10,6)
        g.cyl('R | carved crest',(xx,yy,z+1.04),.15,.45,PALE,5,r2=.015)
        for side in [-1,1]:
            for feather in range(5):
                a=(xx+side*.13,yy,z+.3+feather*.07)
                b=(xx+side*(.72-feather*.08),yy+sign*.08,z+1.25-feather*.11)
                g.beam('R | carved wing feather',a,b,.095,PALE)
        bowl=(xx,yy-sign*.67,z-.05)
        g.lathe('R | suspended fire bowl',bowl,[(.10,-.25),(.40,-.10),(.48,.07),(.47,.12),(.40,.12)],IRON,20)
        for side in [-1,1]:g.path('R | suspension chain',[(xx+side*.37,yy-sign*.65,z),(xx+side*.20,yy-sign*.25,z+.82)],.018,GOLD)

# Handworked timber details, worn table edges and uneven scratches.
SCRATCH=painted('R | exposed wood',(.14,.09,.041),(.28,.19,.089),True)
for yy in [25.7,28.05,31.95,34.3]:
    for i in range(58):
        xx=random.uniform(-4.4,19.8);dy=random.uniform(-.39,.39);length=random.uniform(.08,.60)
        g.path('R | tabletop worn grain',[(xx,yy+dy,18.031),(xx+length,yy+dy+.004,18.032)],random.uniform(.0015,.004),SCRATCH)
    for xx in [-3.8,0,3.8,7.6,11.4,15.2,19]:
        for sign in [-1,1]:
            g.lathe('R | turned bench foot',(xx,yy+sign*.76,17.05),[(.08,0),(.11,.07),(.065,.15),(.06,.32),(.085,.40)],DARK,10)
    for xx in [-2.8,1.6,6.5,11.7,16.7]:
        xx+=random.uniform(-.3,.3)
        g.lathe('R | ceramic feast jug',(xx,yy,18.04),[(.09,0),(.17,.06),(.20,.22),(.15,.36),(.08,.40),(.085,.54),(.11,.57),(.08,.59)],OAK,16)
        g.path('R | jug handle',[(xx+.10+.15*sin(i*pi/14),yy,18.51-.30*i/14) for i in range(15)],.025,GOLD)
        px=xx+1.0
        g.lathe('R | fluted pie',(px,yy,18.07),[(.24,0),(.29,.05),(.25,.17),(.08,.21),(0,.21)],bpy.data.materials['I | bread crust'],16)
        for i in range(3):g.path('R | pie pastry score',[(px-.15+i*.13,yy-.18,18.26),(px-.15+i*.13,yy+.18,18.26)],.01,WAX)
    for xx in [-4.1,3.4,10.5,18.6]:
        g.lathe('R | table candlestick',(xx,yy,18.05),[(.13,0),(.14,.04),(.04,.10),(.035,.42),(.12,.45)],GOLD,16)
        g.cyl('R | table candle',(xx,yy,18.67),.044,.32,WAX,12)
        g.sphere('R | table flame',(xx,yy,18.91),(.033,.033,.10),bpy.data.materials['I | flame gold'],10,6)
        g.point('R | table pool',(xx,yy,19.05),15,(1,.57,.22),.25)

# Paneled front to the dais, a closed west door, and a more elaborate head chair.
for yy in [25.2+i*.60 for i in range(17)]:
    g.box('R | dais carved front',(21.6,yy,17.98),(.16,.55,.73),DARK,.018)
    g.arch_frame('R | dais panel moulding',(21.50,yy,17.66),.42,.59,.018,GOLD,pi/2)
g.box('R | closed entrance door',(-7.62,30,20.15),(.18,3.65,6.3),DARK,.03)
for yy in [28.7,29.56,30.44,31.3]:
    g.arch_frame('R | entrance door carving',(-7.49,yy,17.3),.70,5.6,.045,SCRATCH,pi/2)
for sign in [-1,1]:
    g.path('R | throne soaring finial',[(24.32,30+sign*.65,18),(24.32,30+sign*.65,20.5),(24.32,30,21.35)],.055,GOLD)
for yy in [29.56,30,30.44]:g.cyl('R | throne pinnacle',(24.35,yy,21.15),.075,.7,GOLD,8,r2=.008)

# Four restrained hanging textiles on the side walls, with original embroidered motifs.
for i,(xx,sign,matname) in enumerate([(1.3,-1,'GRYFFINDOR'),(8.9,-1,'HUFFLEPUFF'),(1.3,1,'SLYTHERIN'),(8.9,1,'RAVENCLAW')]):
    yy=30+sign*5.58;m=bpy.data.materials['I | '+matname+' velvet'];vs=[]
    for j in range(14):
        for k in range(9):
            u=k/8;t=j/13;vs.append((xx+(u-.5)*1.2,yy+.055*sin(u*5*pi+t),29.2-t*3.2+(abs(u-.5)*.4 if j==13 else 0)))
    g.mesh('R | woven house hanging',vs,[(j*9+k,j*9+k+1,(j+1)*9+k+1,(j+1)*9+k) for j in range(13) for k in range(8)],m,True)
    for dx in [-.53,.53]:g.path('R | textile embroidered border',[(xx+dx,yy-sign*.07,29),(xx+dx,yy-sign*.07,26.15)],.016,GOLD)
    g.path('R | embroidered shield',[(xx-.35,yy-sign*.08,28.5),(xx+.35,yy-sign*.08,28.5),(xx+.3,yy-sign*.08,27.8),(xx,yy-sign*.08,27.5),(xx-.3,yy-sign*.08,27.8)],.027,GOLD,True)
    for side in [-1,1]:g.path('R | embroidered wing',[(xx,yy-sign*.1,27.8),(xx+side*.24,yy-sign*.1,28.25),(xx+side*.07,yy-sign*.1,28.12)],.028,GOLD)

# Convert all mesh-like objects once, then compress the high architecture consistently.
bpy.ops.object.select_all(action='DESELECT')
for o in S.objects:
    if o.type in {'MESH','CURVE','FONT'}:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in S.objects if o.select_get())
bpy.ops.object.convert(target='MESH')
def position(v):
    z=v.z if v.z<=19 else 19+(v.z-19)*.72
    return Vector((v.x,v.y-30,z-17))
for o in list(S.objects):
    if o.type=='MESH':
        o.data=o.data.copy();matrix=o.matrix_world.copy()
        for v in o.data.vertices:v.co=position(matrix@v.co)
        o.matrix_world.identity()
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    else:o.location=position(o.location)

# Replace old lighting; keep a cinematic but readable warm/cool separation.
for o in list(S.objects):
    if o.type=='LIGHT':drop(o)
g.collection('21 Refined Hall | lighting')
for xx in [-4,3.6,11.2,18.8]:
    for sign in [-1,1]:
        z=2+(23.7-19)*.72
        g.point('Bake | fire bowl',(xx,sign*4.7,z+.35),155,(1,.52,.20),.55)
    g.area('Bake | candle bounce',(xx,0,8.2),(xx,0,0),190,(1,.68,.35),4)
    g.area('Bake | cool window',(xx,5.95,8.5),(xx,-1,1.5),200,(.34,.52,1),3,'RECTANGLE',4)
    for yy in [-4.3,-1.95,1.95,4.3]:g.point('Bake | feast candles',(xx,yy,2.2),11,(1,.59,.24),.3)
g.area('Bake | east moon',(24.6,0,9.2),(5,0,2),650,(.35,.55,1),4)
g.area('Bake | entry bounce',(-6.7,0,4.8),(8,0,3),165,(1,.74,.47),4)
S.world=bpy.data.worlds.new('Night outside the hall');S.world.use_nodes=True
S.world.node_tree.nodes['Background'].inputs[0].default_value=(.04,.055,.075,1)
S.world.node_tree.nodes['Background'].inputs[1].default_value=.25
S.render.engine='CYCLES';S.cycles.samples=48;S.cycles.use_denoising=True
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
for d in p.devices:d.use=d.type=='CUDA'
S.cycles.device='GPU';S.cycles.max_bounces=6
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=.7
cam=bpy.data.objects['04 Interior | Great Hall'];cam.location=(-5.9,0,1.85)
cam.rotation_euler=(Vector((23,0,5.7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=19
S.camera=cam;S.render.resolution_x=1600;S.render.resolution_y=1000;S.render.resolution_percentage=100
S['Source']='Original authored scene; refined from Magic Awakened visual references.'
S['Coordinate note']='Z up; floor at zero; long axis X; browser glTF uses Y up.'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE,'Great_Hall_Refined.blend'))
S.render.filepath=os.path.join(ROOT,'Great_Hall_Refined.png')
bpy.ops.render.render(write_still=True)
print('REFINED_COMPLETE',len(S.objects),flush=True)
