"""Add the painted shopfront, forest silhouettes and house door props to the editable campus."""
from math import cos, pi, sin
from pathlib import Path
from random import Random
import bpy
from mathutils import Vector

scene = bpy.context.scene
random = Random(19)
paint = bpy.data.collections.get("Campus · painted landmarks")
if paint is None:
    paint = bpy.data.collections.new("Campus · painted landmarks")
    scene.collection.children.link(paint)
else:
    for obj in list(paint.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def pigment(name, hex_code, emission=0):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    rgb = [int(hex_code[i:i+2], 16) / 255 for i in (0, 2, 4)]
    linear = tuple(v / 12.92 if v < .04045 else ((v+.055)/1.055)**2.4 for v in rgb)
    material.diffuse_color = (*linear, 1)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = material.diffuse_color
    shader.inputs["Roughness"].default_value = .92
    shader.inputs["Emission Color"].default_value = material.diffuse_color
    shader.inputs["Emission Strength"].default_value = emission
    return material


def place(name, material):
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    paint.objects.link(obj)
    return obj


def box(name, loc, size, material, angle=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = place(name, material)
    obj.scale = size
    obj.rotation_euler.z = angle
    return obj


def shape(name, loc, scale, material, rotation=0, facets=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=facets, radius=1, location=loc)
    obj = place(name, material)
    obj.scale = scale
    obj.rotation_euler.z = rotation
    return obj


def beam(name, start, end, base, tip, material, sides=8):
    start, end = Vector(start), Vector(end)
    axis = end - start
    bpy.ops.mesh.primitive_cone_add(vertices=sides, radius1=base, radius2=tip,
                                   depth=axis.length, location=(start+end)/2)
    obj = place(name, material)
    obj.rotation_euler = axis.to_track_quat('Z', 'Y').to_euler()
    return obj


wood = pigment("Glazed timber", "263C35", .12)
wood_high = pigment("Painted timber edges", "51685A", .13)
trim = pigment("Antique gilt", "BC9252", .23)
dark = pigment("Display shadows", "382531")
warm = pigment("Backlit amber panes", "A4573D", .70)
rose = pigment("Mulberry enamel", "783D53", .15)
paper = pigment("Ochre wrapper", "E5AD62", .35)
candies = [pigment("Glass sweets " + label, color, .22) for label, color in (
    ("rose","E6ACA6"),("mint","84B095"),("violet","A289B1"),("red","B25163"),("cream","F1D299"),
)]

# Build the angled bay over the south face of the existing stone shop.
for x, y, angle in [(-35.35, 76.44, -.25), (-34.04, 76.27, .04), (-32.72, 76.48, .33)]:
    box("Honeydukes · bay casing", (x,y,5.02), (1.39,.42,2.16), wood, angle)
    box("Honeydukes · lit display back", (x,y-.226,5.23), (1.19,.055,1.28), warm, angle)
    for height in (4.54,5.09,5.71):
        box("Display shelf", (x,y-.33,height), (1.22,.33,.075), wood_high, angle)
    for index in range(5):
        dx = (index-2)*.214
        for shelf in (4.58,5.14):
            tall = random.uniform(.10,.25)
            color = random.choice(candies)
            shape("Wrapped sweets", (x+dx,y-.36+dx*sin(angle),shelf+tall*.63),
                  (.11,.097,tall), color, random.random())
    for dx in (-.62,.62):
        box("Mullion", (x+dx,y-.35+dx*sin(angle),5.19), (.075,.1,1.47), trim, angle)
    box("Inset enamel panel", (x,y-.25,4.17), (1.10,.08,.35), rose, angle)
    for dx in (-.35,-.14,.12,.38):
        box("Dry-brushed edge", (x+dx,y-.30+dx*sin(angle),4.32), (.17,.013,.025), wood_high, angle)
box("Sign plate", (-34.05,76.20,6.23), (3.45,.28,.52), wood)
box("Sign border", (-34.05,76.041,6.23), (3.28,.06,.42), trim)
box("Sign inset", (-34.05,76.0,6.23), (3.16,.06,.32), dark)
bpy.ops.object.text_add(location=(-34.05,75.951,6.11), rotation=(pi/2,0,0))
sign = place("Honeydukes · hand-lettered fascia", paper)
sign.data.body = "H O N E Y D U K E S"
sign.data.align_x = 'CENTER'
sign.data.size = .23

# Layer faceted old-growth silhouettes on either side of the existing walk.
bark = [pigment("Forest bark " + str(i), code) for i, code in
        enumerate(("403C3E","54504D","3E4A48","544C49"))]
canopy = [pigment("Forest canopy " + str(i), code) for i, code in
          enumerate(("283F3C","354745","425752","263233"))]
for x,y,z,r,height in [(81.4,55.8,5.34,.76,10.5),(91.8,55.5,5.6,.86,11.2),
                       (88.7,60.6,5.26,.80,12.8),(79,62,4.93,.71,10.4),
                       (94,63,5.15,1.07,13.4),(88,67,4.7,.85,11.8),
                       (76,69,4.26,.70,10.2),(96,69,4.5,.76,12),
                       (72,71,3.96,.73,10.5),(86,76,3.65,.88,12.3)]:
    base = Vector((x,y,z-.18))
    fork = base + Vector((random.uniform(-.75,.75),.7,height*.63))
    top = fork + Vector((random.uniform(-.9,.9),.7,height*.37))
    trunk = beam("Old forest · trunk", base, fork, r, r*.43, bark[0], 9)
    for material in bark[1:]:
        trunk.data.materials.append(material)
    for face in trunk.data.polygons:
        face.material_index = random.choices(range(4), (4,2,3,1))[0]
    beam("Crown stem",fork,top,r*.46,r*.13,bark[1])
    for index in range(4):
        angle = index*1.58+random.random()*.57
        offset = Vector((cos(angle),sin(angle),0))
        root = base + offset*r*1.46
        beam("Exposed root",base+Vector((0,0,.74)),root,r*.24,.025,bark[index])
        branch = fork + offset*random.uniform(2.5,4.1) + Vector((0,0,random.uniform(.4,2.8)))
        beam("Crown branch",fork,branch,r*.37,r*.065,bark[index])
        shape("Faceted foliage",branch,(random.uniform(2,3.5),random.uniform(2.2,3.8),random.uniform(1.15,2.1)),
              canopy[index],angle,facets=2)
    shape("Crown silhouette",top,(3.15,2.6,2.05),canopy[1],random.random(),facets=2)

# Retain the entrance pair, with fewer lanterns beyond the gateway.
for suffix in ("022","024","025"):
    for prefix in ("灯柱","琥珀色铁灯","灯芯"):
        obj = bpy.data.objects.get(prefix + "." + suffix)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

red = pigment("Gryffindor alcove umber","763B3B", .17)
blue = pigment("Ravenclaw alcove indigo","2F435E", .17)
portrait = pigment("Portrait face ochre","B98269", .20)
stone = pigment("Secret sill stone","394741", .05)
staves = pigment("Barrel staves amber","795037", .14)

# Two distinct doors beneath the single northern arch.
origin = Vector((-25,33.2,12.0))
angle = -2.8
across = Vector((cos(angle),sin(angle),0))
front = Vector((sin(angle),-cos(angle),0))
for offset, face in [(-.49,red),(.49,blue)]:
    jamb = origin + across*offset + front*.47
    box("House door · jamb", jamb+Vector((0,0,1.03)), (.92,.15,2.04), trim, angle)
    box("House door · painted leaf", jamb+front*.09+Vector((0,0,1.03)), (.80,.13,1.88), face, angle)
    ornament = jamb+front*.20+Vector((0,0,1.53))
    if face == red:
        box("Portrait frame",ornament,(.56,.09,.67),trim,angle)
        box("Painted portrait ground",ornament+front*.056,(.45,.03,.55),dark,angle)
        shape("Portrait face",ornament+front*.083+Vector((0,0,.075)),(.13,.068,.17),portrait,angle)
        shape("Portrait shoulders",ornament+front*.083-Vector((0,0,.17)),(.19,.052,.10),rose,angle)
    else:
        for side in (-1,1):
            edge = ornament + across*(side*.27) + Vector((0,0,.15))
            beam("Eagle wing",ornament,edge,.095,.019,trim,5)
        shape("Eagle head",ornament+Vector((0,0,.14)),(.11,.09,.12),trim)
        bpy.ops.mesh.primitive_torus_add(major_radius=.11, minor_radius=.025, location=ornament-Vector((0,0,.13)))
        ring = place("Eagle door knocker",trim)
        ring.rotation_euler = front.to_track_quat('Z','Y').to_euler()

# Round cask front and iron hoops distinguish the kitchen arch.
for x, height, radius in [(0,1.05,.85),(-1.12,.38,.32),(1.14,.45,.39)]:
    beam("Kitchen · cask", (x,-10.48,12+height),(x,-11.05,12+height),radius*.95,radius,staves,14)
    for depth in (-10.65,-11.02):
        beam("Iron cask hoop", (x,depth+.023,12+height),(x,depth-.023,12+height),radius*1.04,radius*1.04,stone,14)
    beam("Solidity of end grain", (x,-11.05,12+height),(x,-11.083,12+height),radius*.91,radius*.91,staves,14)
    for line in (-.48,-.22,.20,.47):
        box("Cask board seam", (x,-11.09,12+height+radius*line),(radius*1.43,.011,.014),dark)
    shape("Cask center pin",(x,-11.13,12+height),(.07,.04,.07),trim)

# Thin green recess and serpentine brass line over the old dungeon door.
origin = Vector((-43.54,10.52,13.45))
box("Dungeon · hidden entrance panel",origin,(1.24,.09,.73),stone,-1.36)
for i in range(9):
    start = origin + Vector((-.06,0,(i-4)*.058)) + Vector((0,sin(i*.94)*.16,0))
    end = origin + Vector((-.06,0,(i-3)*.058)) + Vector((0,sin((i+1)*.94)*.16,0))
    beam("Dungeon · brass serpent",start,end,.035,.033,trim,6)

bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(Path(bpy.data.filepath)))
