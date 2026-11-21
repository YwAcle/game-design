"""Add the outer landmarks and trails to the packed Hogwarts grounds."""
import json
import os
import sys
from math import cos, exp, pi, sin
from pathlib import Path
from random import Random

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atlas_paths import draw_paths

WORLD = Path(bpy.data.filepath).parents[1]
layout = json.loads((WORLD / 'layout.json').read_text())
nav_path = WORLD / 'navigation.json'
nav = json.loads(nav_path.read_text())
places = {place['id']: place for place in layout['places']}
rng = Random(347)
scene = bpy.context.scene
for previous in [c for c in scene.collection.children if c.name.startswith('Atlas · ')]:
    for obj in list(previous.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(previous)


def collection(name):
    group = bpy.data.collections.new('Atlas · ' + name)
    scene.collection.children.link(group)
    return group


def ground(x, y):
    """Interpolate the same two terrain triangles used by navigation.mjs."""
    u, v = (x - nav['x0']) / nav['step'], (-y - nav['z0']) / nav['step']
    i, j = int(u), int(v)
    a, b = u - i, v - j
    p, q = nav['heights'][j][i:i+2]
    r, s = nav['heights'][j+1][i:i+2]
    return p + (q-p)*a + (s-q)*b if a >= b else p + (s-r)*a + (r-p)*b


def pigment(name, color, emission=0):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    rgb = [int(color[i:i+2], 16)/255 for i in (0, 2, 4)]
    rgba = (*(c/12.92 if c < .04045 else ((c+.055)/1.055)**2.4 for c in rgb), 1)
    material.diffuse_color = rgba
    material.use_nodes = True
    shader = material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = rgba
    shader.inputs['Roughness'].default_value = .88
    shader.inputs['Emission Color'].default_value = rgba
    shader.inputs['Emission Strength'].default_value = emission
    return material


stone, slate, moss, oak, wood, iron, brass, amber, canvas, heather = [
    pigment(name, color, emission) for name, color, emission in [
        ('Atlas limestone', '91836d', .06), ('Atlas slate', '4f6067', .04),
        ('Atlas lichen', '657351', .06), ('Atlas silvery oak', '665346', .05),
        ('Atlas storm-damaged boards', '3e3935', .06), ('Atlas iron', '2a3133', .05),
        ('Atlas brass', 'a59060', .15), ('Atlas amber glass', 'efab57', .65),
        ('Atlas oiled canvas', 'a0784b', .1), ('Atlas heather', '8a5a72', .09)
    ]
]
brick = bpy.data.materials['MI_UnevenBrick.007']
shore_rock = bpy.data.materials['coastal_cliff_02']

primitives = {}
for kind, add, options in [
    ('box', bpy.ops.mesh.primitive_cube_add, {'size': 1}),
    ('rock', bpy.ops.mesh.primitive_ico_sphere_add, {'subdivisions': 2, 'radius': 1}),
    ('pole', bpy.ops.mesh.primitive_cone_add, {'vertices': 9, 'radius1': 1, 'radius2': .62, 'depth': 1}),
    ('spike', bpy.ops.mesh.primitive_cone_add, {'vertices': 7, 'radius1': 1, 'radius2': 0, 'depth': 1}),
]:
    add(**options)
    dummy = bpy.context.object
    primitives[kind] = dummy.data
    bpy.data.objects.remove(dummy, do_unlink=True)
colored_meshes = {}


def shape(group, name, kind, at, size, material, angle=0):
    key = (kind, material.name)
    if key not in colored_meshes:
        colored_meshes[key] = primitives[kind].copy()
        colored_meshes[key].materials.append(material)
    obj = bpy.data.objects.new(name, colored_meshes[key])
    group.objects.link(obj)
    obj.location, obj.scale, obj.rotation_euler.z = at, size, angle
    return obj


def beam(group, name, a, b, radius, material, kind='pole'):
    a, b = Vector(a), Vector(b)
    axis = b - a
    obj = shape(group, name, kind, (a+b)/2, (radius, radius, axis.length), material)
    obj.rotation_euler = axis.to_track_quat('Z', 'Y').to_euler()
    return obj


def mesh(group, name, vertices, faces, material):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.materials.append(material)
    obj = bpy.data.objects.new(name, data)
    group.objects.link(obj)
    return obj


def module(group, source, at, size, angle=0):
    """Reuse the downloaded Quaternius mesh and the campus's packed materials."""
    key = 'Atlas source ' + source
    data = bpy.data.meshes.get(key)
    if data is None:
        path = Path(os.environ['HOGWARTS_MODULES']) / (source + '.gltf')
        bpy.ops.import_scene.gltf(filepath=str(path))
        original = next(obj for obj in bpy.context.selected_objects if obj.type == 'MESH')
        data = original.data
        for i, material in enumerate(data.materials):
            data.materials[i] = bpy.data.materials[material.name.rsplit('.', 1)[0]]
            if material.users == 0:
                bpy.data.materials.remove(material)
        data.name = key
        data.use_fake_user = True
        bpy.data.objects.remove(original, do_unlink=True)
    axes = list(zip(*(v.co for v in data.vertices)))
    minimum = Vector(tuple(min(axis) for axis in axes))
    maximum = Vector(tuple(max(axis) for axis in axes))
    obj = bpy.data.objects.new(source, data)
    group.objects.link(obj)
    obj.rotation_euler.z = angle
    obj.scale = tuple(span / extent for span, extent in zip(size, maximum - minimum))
    pivot = (maximum + minimum) / 2
    pivot.z = minimum.z
    obj.location = Vector(at) - obj.rotation_euler.to_matrix() @ Vector(
        tuple(coord * scale for coord, scale in zip(pivot, obj.scale))
    )
    return obj


blocks = []


def block(x, y, half_x, half_y):
    blocks.append([x-half_x, -y-half_y, x+half_x, -y+half_y])


def site(id):
    x, z = places[id]['look']
    return x, -z, ground(x, -z)


group = collection('Lakeside cavern')
x, y, h = site('cave')
front = Vector((.83,.55))
across = Vector((-.55,.83))
for dx, dy, elevation, sx, sy, sz in [
    (-2.7, -.15, 1.0, 2, 2.8, 2.85), (2.65, -.28, .95, 1.96, 2.4, 3.1),
    (.16, -.53, 3.04, 3.6, 2.4, 1.15), (-.1, -2.55, 1.35, 3, .9, 2.41),
    (-4.22, -1.5, .6, 2.16, 1.8, 2.1), (4.15, -1.2, .42, 1.76, 1.7, 1.75),
]:
    rx, ry = Vector((x,y)) + across*dx + front*dy
    shape(group, 'Fractured shore rock', 'rock', (rx, ry, h+elevation),
          (sx, sy, sz), shore_rock, 2.15)
    shape(group, 'Moss on the rock', 'rock', (rx-.3, ry, h+elevation+sz*.62),
          (sx*.72, sy*.85, sz*.42), moss, 2.15)
shape(group,'Recess at the end of the cave','box',(x-1.52,y-.98,h+1.34),(.18,2.5,2.68),iron,-.98)
for dx in (-.8,-.46,.4,.64):
    shape(group,'Exposed lake minerals','spike',(x+dx,y-.63,h+.20),(.15,.16,.72),
          pigment('Atlas lake minerals','76aea1',.55),dx)
block(x-1, y-.55, 5, 2.95)
for dx, dy in [(-3, 3), (3.8, -1.95), (-4, -5), (-6, -6), (6, -7)]:
    shape(group, 'Rockfall by the water', 'rock', (x+dx, y+dy, max(.2, ground(x+dx,y+dy))),
          (1.35, .96, .76), slate, rng.random())

group = collection('Highland ruins')
x, y, h = site('ruins')
block(x-.1, y, 2.7, 1.55)
module(group,'Wall_UnevenBrick_Door_Round',(x,y,h-.13),(5.3,1.12,5.35),pi*.32)
for dx,dy,count in [(-2.1,2.4,6),(-3.2,3.4,5),(-4.32,4.4,3),(1.8,-2.7,4),(3,-3.9,2)]:
    z = ground(x+dx,y+dy)-.13
    block(x+dx,y+dy,.65,.64)
    for i in range(count):
        shape(group,'Broken masonry course','box',(x+dx+rng.uniform(-.11,.11),y+dy,z+i*.61),
              (1.22,1.11,.65),rng.choice([brick,stone,brick]),pi*.32+rng.uniform(-.12,.12))
    shape(group,'Grass crown along the broken wall','rock',(x+dx,y+dy,z+(count-.8)*.61),(.61,.58,.29),moss)
for dx,dy in [(-3,-1),(-4,2),(3,1),(5,-1),(2,-5)]:
    shape(group,'Rubble','rock',(x+dx,y+dy,ground(x+dx,y+dy)+.17),(.65,.47,.34),stone,rng.random())

group = collection('Forest camp and gamekeeper trail')
x,y,h=site('camp')
for dx,dy,high in [(2.1,2.05,2.25),(4.9,-.3,1.75)]:
    cx,cy=x+dx,y+dy
    z=ground(cx,cy)-.1
    block(cx,cy,1.6,1.35)
    vertices=[(cx+a,cy+b,z+c) for a,b,c in [(-1.6,-1.4,0),(-1.6,1.4,0),(0,1.4,high),
              (1.6,1.4,0),(1.6,-1.4,0),(0,-1.4,high)]]
    mesh(group,'Waxed canvas tent',vertices,[(0,5,2,1),(5,4,3,2),(1,2,3)],canvas)
    beam(group,'Tent ridge',vertices[2],vertices[5],.08,oak)
    beam(group,'Door post',(cx,cy-1.4,z),vertices[5],.055,oak)
for i in range(10):
    angle = i*pi/5
    shape(group,'Firepit stones','rock',(x+.62*cos(angle),y+.62*sin(angle),h+.08),(.28,.27,.20),slate)
    beam(group,'Firewood',(x-.37*cos(angle),y-.37*sin(angle),h+.13),
         (x+.38*cos(angle),y+.38*sin(angle),h+.17),.061,wood)
for i in range(6):
    color = amber if i%2 else pigment('Atlas firelight','e87a3b',1.55)
    obj = shape(group,'Firelight','spike',(x+rng.uniform(-.25,.25),y+rng.uniform(-.22,.22),h+.29),
                (.13,.11,rng.uniform(.28,.55)),color)
    obj.rotation_euler.x = rng.uniform(-.34,.34)
block(x,y,.65,.65)
x,y,h=site('gamekeeper-trail')
for dx,dy in [(-1,-1.25),(1.3,-1.0),(4.4,1.4),(6.65,2.8)]:
    cx,cy=x+dx,y+dy
    z=ground(cx,cy)
    shape(group,'Hunting ground waymarker','rock',(cx,cy,z+.3),(.65,.46,.72),slate,rng.random())
    shape(group,'Moss and heather','rock',(cx+.43,cy+.21,z+.17),(.58,.36,.35),moss)
    for i in range(3):
        shape(group,'Heather tips','rock',(cx+.48+rng.random()*.25,cy+.22+rng.random()*.32,z+.32),
              (.13,.11,.25),heather,rng.random())

group = collection('Hogsmeade shopfronts')
prototype = bpy.data.objects['霍格莫德 · 石墙瓦顶铺面']
for label, token, x, y, color in [
    ('The Three Broomsticks','III',-18.2,69.5,pigment('Atlas mulberry paint','782f31',.12)),
    ('The Hog’s Head','◆',-62,66,pigment('Atlas crooked tavern green','34433a',.08)),
]:
    h = ground(x,y)
    front = y+2.38 if token=='III' else y-2.38
    side = 1 if token=='III' else -1
    if token!='III':
        building=prototype.copy()
        group.objects.link(building)
        building.name=label
        building.location=(x,y,h-.2)
        building.rotation_euler.z=0
        block(x,y,2.42,2.42)
    for dx in (-1.37,1.37):
        shape(group,'Tavern bay frame','box',(x+dx,front,h+2.18),(1.16,.26,1.42),color)
        shape(group,'Tavern leaded amber window','box',(x+dx,front+side*.16,h+2.2),(.91,.05,1.10),amber)
        for bar in (-.31,0,.31):
            shape(group,'Leaded window bar','box',(x+dx+bar,front+side*.20,h+2.2),(.043,.07,1.12),brass)
        shape(group,'Tavern sill','box',(x+dx,front+side*.11,h+1.61),(1.30,.38,.14),wood)
    shape(group,'Carved tavern sign','box',(x,front+side*.27,h+3.10),(2.88,.21,.50),color)
    sign_y = front + side*.40
    if token == 'III':
        for dx, rise in [(-.53,.25),(0,0),(.53,-.21)]:
            beam(group,'Broom handle',(x+dx-.29,sign_y,h+3.0),(x+dx+.35,sign_y,h+3.21+rise),.041,brass)
            shape(group,'Broom straw','rock',(x+dx+.39,sign_y,h+3.23+rise),(.26,.06,.084),brass,.2)
    else:
        shape(group,'Carved boar’s head','rock',(x,sign_y,h+3.10),(.36,.107,.15),brass)
        shape(group,'Carved boar’s snout','rock',(x+.3,sign_y-.06,h+3.07),(.14,.11,.082),brass)
        shape(group,'Carved boar’s ear','spike',(x-.17,sign_y,h+3.22),(.10,.09,.21),brass)

group = collection('Black Lake islands and shore')
rock_colors = [pigment('Atlas granite '+str(i),color,.06) for i,color in enumerate(
    ('53666b','65716b','73806d','82877c','a3a9a5'))]
for x,y,rx,ry,height in [(-51,-98,15,7,5),(54,-129,24,13,8),(-116,-114,32,16,12),
                         (113,-96,28,20,17),(11,-155,35,13,13),(-69,-159,39,15,21)]:
    vertices=[(x+rx*.16,y-ry*.05,height)]
    phases = [rng.uniform(.78,1.14) for _ in range(27)]
    for tier in (.19,.39,.61,.82,1):
        for i, phase in enumerate(phases):
            theta=i*2*pi/len(phases)
            z=height*(1-tier**1.36)*(.87+.13*cos(4*theta)+.12*sin(7*theta))-.65+rng.uniform(-.74,.74)
            vertices.append((x+rx*cos(theta)*tier*phase,y+ry*sin(theta)*tier*phase,z))
    n=len(phases)
    faces=[(0,1+i,1+(i+1)%n) for i in range(n)]
    for tier in range(4):
        for i in range(n):
            a,b = 1+tier*n+i,1+tier*n+(i+1)%n
            faces.extend([(a,a+n,b),(b,a+n,b+n)])
    obj=mesh(group,'Glacial outcrop',vertices,faces,rock_colors[0])
    for material in [*rock_colors[1:],moss]:
        obj.data.materials.append(material)
    for face in obj.data.polygons:
        face.material_index=rng.choice([1,2,2,3,5,5] if face.center.z>height*.33 or face.index<n else [0,1,2,3])
    for i in range(21):
        index = 1 + rng.randrange(n*3)
        px,py,z = vertices[index]
        size = rng.uniform(.59,1.91)
        canopy = rock_colors[1] if i%5==0 else moss
        shape(group,'Wind-bent island fir','spike',(px,py,z+size*.58),(size*.39,size*.40,size*1.44),canopy).rotation_euler.y=.09
        shape(group,'Upper branches','spike',(px+.09,py,z+size*.99),(size*.29,size*.27,size*1.19),canopy)

# The terrain grid ends at the walkable highland. Join its edges to the distant ridges.
group = collection('Highland escarpments')
terrain_mat = pigment('Atlas painted highland slopes','ffffff')
nodes = terrain_mat.node_tree.nodes
paint = nodes.get('Atlas slope pigments') or nodes.new('ShaderNodeVertexColor')
paint.name = 'Atlas slope pigments'
paint.layer_name = 'Slope pigments'
terrain_mat.node_tree.links.new(paint.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
for start, delta, normal in [
    ((-125,111),(0,-1),(-1,0)), ((135,111),(0,-1),(1,0)), ((-125,111),(1,0),(0,1))
]:
    along_length = 192 if delta[0]==0 else 260
    depth, step = 84, 3
    rows, columns = depth//step+1, along_length//step+1
    vertices, faces, colors = [], [], []
    for row in range(rows):
        distance = row*step
        for col in range(columns):
            along = along_length*col/(columns-1)
            x, y = (start[i]+delta[i]*along+normal[i]*distance for i in range(2))
            edge = ground(x-normal[0]*distance,y-normal[1]*distance)
            profile = .56+.26*sin(along*.093)+.15*cos(along*.174)+.08*sin(along*.28)
            crest = (distance/39)**2*exp(2-distance/19.5)
            ridges = crest*(19+27*profile)
            cuts = min(1,distance/19)*(2.6*cos(x*.39+y*.2)+2.25*sin(y*.45-x*.19)+rng.uniform(-1,1))
            z = edge + ridges + cuts - .65
            # Extend the rocky shore below lake level where the side ridges end.
            shore = min(1, max(0,(y+77)/23))
            z = z*shore-(1-shore)*(2.8+.06*distance)
            vertices.append((x,y,z))
            exposure=min(1,max(0,(ridges-3)/29))
            moss = Vector((.125,.178,.084))
            granite = Vector((.153,.190,.167))
            tint = moss.lerp(granite,exposure)*(.76+.37*profile+.15*rng.random())
            colors.append((*tint,1))
    for row in range(rows-1):
        for col in range(columns-1):
            a=row*columns+col
            faces.extend([(a,a+1,a+columns),(a+1,a+columns+1,a+columns)])
    if delta[0]*normal[1]-delta[1]*normal[0]<0:
        faces=[f[::-1] for f in faces]
    obj=mesh(group,'Ridges running into the glen',vertices,faces,terrain_mat)
    data=obj.data.color_attributes.new(name='Slope pigments',type='FLOAT_COLOR',domain='POINT')
    for color, item in zip(colors,data.data):
        item.color=color

group = collection('Highland paths')
draw_paths(group, layout, places, ground, bpy.data.materials['Dirt'])

nav['atlasBlocks'] = [[round(v,3) for v in bounds] for bounds in blocks]
nav_path.write_text(json.dumps(nav, separators=(',', ':'))+'\n')
bpy.ops.file.pack_all()
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath, compress=True)
