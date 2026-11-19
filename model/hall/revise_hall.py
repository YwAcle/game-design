"""V2 architectural/art correction of the preserved, editable V1 hall."""
from pathlib import Path
import bpy, bmesh, json, math, random, sys
from mathutils import Vector
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import interior_geometry as g
bpy.ops.wm.open_mainfile(filepath=str(HERE/'Great_Hall_Refined.blend'))
S=bpy.context.scene
random.seed(1762)
old_centers=[-4.3,-1.95,1.95,4.3]
new_centers=[-4.65,-2.9,2.9,4.65]
table_scale=.74

def center(o):
    return sum((o.matrix_world@Vector(v) for v in o.bound_box),Vector())/8

def remove(o):
    bpy.data.objects.remove(o,do_unlink=True)

# The original centre avenue was only two metres wide. Compress each furniture
# group about its own axis and move both inner tables out, retaining four rows.
for o in list(S.objects):
    if o.type!='MESH':continue
    c=center(o)
    furniture=any(col.name.startswith('12 ') for col in o.users_collection)
    detail=o.name.startswith(('R | tabletop','R | turned bench','R | ceramic feast','R | jug handle','R | fluted pie','R | pie pastry','R | table candle','R | table flame'))
    if not (furniture or detail) or c.x>20.25 or c.z>2.3:continue
    i=min(range(4),key=lambda j:abs(c.y-old_centers[j]))
    if abs(c.y-old_centers[i])>1.02:continue
    o.data=o.data.copy()
    for v in o.data.vertices:
        p=o.matrix_world@v.co
        p.y=new_centers[i]+(p.y-old_centers[i])*table_scale
        v.co=p
    o.matrix_world.identity()
    # Disturb repeated crockery while keeping the table/bench collision envelope.
    if any(k in o.name for k in ['brass goblet','dinner plate','feast apple','bread loaf']):
        c=center(o);angle=random.uniform(-.25,.25)
        sx=random.uniform(.80,1.15);sy=random.uniform(.85,1.12)
        for v in o.data.vertices:
            d=v.co-c
            v.co=c+Vector(((d.x*math.cos(angle)-d.y*math.sin(angle))*sx,(d.x*math.sin(angle)+d.y*math.cos(angle))*sy,d.z*random.uniform(.98,1.02)))

stone=bpy.data.materials['I | warm sandstone']
pale=bpy.data.materials['I | dressed pale limestone']
oak=bpy.data.materials['I | oak aged dark']
brass=bpy.data.materials['I | antique brass']
iron=bpy.data.materials['I | black iron']
wax=bpy.data.materials['I | ivory beeswax']
flame=bpy.data.materials['I | flame gold']

# Replace most side window openings with recessed blind stone lancets. The
# reference relies on broad stone planes and a dominant far window, not a glass
# cathedral wall. Preserve the actual remaining openings and their leadwork.
side_windows=[o for o in S.objects if o.type=='MESH' and o.name.startswith('I | diamond leaded glass') and abs(center(o).y)>6]
xs=sorted({round(center(o).x,2) for o in side_windows})
open_x={xs[i] for i in [1,4,7] if i<len(xs)}
closed_x=set(xs)-open_x
for o in side_windows:
    c=center(o)
    if round(c.x,2) in open_x:continue
    o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(stone)
    o.name='V2 | recessed blind lancet'
    mod=o.modifiers.new('Stone infill thickness','SOLIDIFY');mod.thickness=.22
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.modifier_apply(modifier=mod.name)
for o in list(S.objects):
    if o.type!='MESH' or not o.name.startswith(('I | diamond lattice','I | window mullion','I | window transom')):continue
    c=center(o)
    if abs(c.y)>6 and any(abs(c.x-x)<1 for x in closed_x):remove(o)

# Shift palette towards grey-brown painted stone and subdued edge accents.
for name,colors in {
    'I | warm sandstone':[(.095,.092,.077),(.135,.132,.109),(.205,.196,.160)],
    'I | dressed pale limestone':[(.135,.131,.109),(.20,.192,.153),(.29,.276,.216)],
    'I | polished honey oak':[(.055,.031,.017),(.09,.053,.028),(.15,.094,.049)],
}.items():
    m=bpy.data.materials[name]
    for node in m.node_tree.nodes:
        if node.type=='VALTORGB':
            for i,e in enumerate(node.color_ramp.elements):e.color=(*colors[min(i,2)],1)
        if node.type=='BUMP':node.inputs['Strength'].default_value=.16
glass=bpy.data.materials['I | moonlit diamond glass']
for node in glass.node_tree.nodes:
    if node.type=='BSDF_PRINCIPLED':node.inputs['Emission Strength'].default_value=.42

g.collection('22 V2 Hall | masonry and feast')
# Thin, broken masonry joints and a few relief medallions give wall planes a
# deliberate drawing rhythm rather than uniform high-frequency noise.
joint=g.material('V2 | masonry charcoal',(.035,.034,.029),rough=1)
for side in [-1,1]:
    for x in sorted(closed_x):
        for row,z in enumerate([3.2,4.05,4.9,5.75,6.6,7.45]):
            g.path('V2 | weathered mortar',[(x-.64,side*6.385,z),(x+.61,side*6.385,z+.012)],.007,joint)
            dx=(-.28 if row%2 else .24)
            g.path('V2 | short mortar',[(x+dx,side*6.38,z),(x+dx+.025,side*6.38,z+.77)],.007,joint)
    for x in [0,7.6,15.2]:
        y=side*5.95
        points=[(x-.25,y,4.6),(x+.25,y,4.6),(x+.23,y,4.15),(x,y,3.98),(x-.23,y,4.15)]
        g.path('V2 | aged shield relief',points,.042,pale,True)
        for s in [-1,1]:g.path('V2 | relief branch',[(x,y,4.1),(x+s*.13,y-side*.025,4.32),(x+s*.18,y-side*.025,4.47)],.026,pale)

# Original varied dishes: low pies, dark fruit bowls, cut cheese, scattered
# napkins. These break rows of identical jugs without borrowing game textures.
berry=g.material('V2 | dark berries',(.035,.009,.012),(.11,.025,.032),rough=.68)
leaf=g.material('V2 | sage glaze',(.06,.075,.042),(.18,.19,.10),rough=.65)
cheese=g.material('V2 | aged cheese',(.27,.15,.045),(.48,.31,.10),rough=.9)
linen=g.material('V2 | crumpled linen',(.20,.18,.13),(.42,.38,.27),rough=1)
for row,y in enumerate(new_centers):
    for k,x in enumerate([-3.1,.7,4.8,9.0,13.7,17.5]):
        x+=random.uniform(-.45,.45);yy=y+random.uniform(-.12,.12)
        if k%3==0:
            g.lathe('V2 | fruit bowl',(x,yy,1.05),[(.12,0),(.24,.07),(.28,.17),(.24,.17),(.14,.065),(.09,.05)],leaf,14)
            for j in range(12):
                a=j*2.4;r=.14*math.sqrt(j/12)
                g.sphere('V2 | berry',(x+r*math.cos(a),yy+r*math.sin(a),1.23+random.uniform(-.02,.04)),(.043,.043,.045),berry,7,5)
        elif k%3==1:
            o=g.cyl('V2 | cheese wedge',(x,yy,1.17),.25,.22,cheese,5)
            o.rotation_euler.z=random.uniform(-1,1)
            for j in range(3):g.sphere('V2 | cheese dimples',(x-.1+j*.085,yy-.19,1.16),(.027,.008,.022),joint,7,5)
        else:
            vs=[(x-.23,yy-.17,1.048),(x+.20,yy-.15,1.052),(x+.14,yy+.15,1.07),(x-.15,yy+.18,1.06),(x-.02,yy,1.11)]
            g.mesh('V2 | folded napkin',vs,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],linen)

# Existing lights were broad, symmetric washes. Keep smaller warm pools and
# the far-window key, dropping light sources behind newly filled stone bays.
# The legacy 'Bake | feast candles' points are retained as broad indirect warm
# fill pools around the avenue, not physically colocated per-candle emitters.
# The moved candle/flame geometry provides the visible source positions.
for o in list(S.objects):
    if o.type!='LIGHT':continue
    if o.name.startswith('Bake | cool window'):
        if not any(abs(o.location.x-x)<2 for x in open_x):remove(o);continue
        o.data.energy=110
    elif o.name.startswith('Bake | candle bounce'):o.data.energy=80
    elif o.name.startswith('Bake | fire bowl'):o.data.energy=200
    elif o.name.startswith('Bake | entry bounce'):o.data.energy=90
    elif o.name.startswith('Bake | east moon'):o.data.energy=720
S.world.node_tree.nodes['Background'].inputs[1].default_value=.15

for o in list(S.objects):
    if o.type in {'CURVE','FONT'}:
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
seen=set()
for o in S.objects:
    if o.type!='MESH' or o.data.as_pointer() in seen:continue
    seen.add(o.data.as_pointer())
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
camera=S.camera;camera.location=(-5.9,0,1.8)
camera.rotation_euler=(Vector((23,0,4.55))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.lens=19.5
S.render.resolution_x=1600;S.render.resolution_y=900;S.render.resolution_percentage=100
S.view_settings.exposure=.1
S.cycles.samples=24
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
for d in p.devices:d.use=d.type=='CUDA'
S.cycles.device='GPU'
S['V2 table centers']=new_centers
S['V2 navigation']='Four table groups: half depth 0.94*0.74, x -4.7 to 20.1; central avenue widened.'
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'Great_Hall_ArtRefined.blend'))
S.render.resolution_percentage=65;S.cycles.samples=12
S.render.filepath=str(ROOT/'previews/blender-hall-v2.png')
bpy.ops.render.render(write_still=True)
print('HALL_V2_DRAFT_COMPLETE',len(S.objects),flush=True)
