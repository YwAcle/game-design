"""Add the painted shopfront, forest silhouettes and house door props to the editable campus."""
import json
from math import atan2, cos, pi, sin
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


# Clear the northern pavilion doorway by relocating the two cards of one fir.
for name in ("Fir crowns 0", "Fir crowns 1"):
    tree_cards = bpy.data.objects[name]
    for face in tree_cards.data.polygons:
        center = tree_cards.matrix_world @ face.center
        if abs(center.x-50.89)<.15 and abs(center.y-51.28)<.15:
            for index in face.vertices:
                tree_cards.data.vertices[index].co += Vector((5.2,2.9,0))

# Set the large path lamp to the side of the observatory rather than in its sightline.
wayfinding = bpy.data.objects["Wayfinding lanterns"]
for vertex in wayfinding.data.vertices:
    point = wayfinding.matrix_world @ vertex.co
    if abs(point.x-27.48)<.58 and abs(point.y-25.42)<.58:
        vertex.co.x -= 2.6

# East gardens: an original walk-through pavilion beside the existing glasshouses.
glass = pigment("Pavilion glass", "98C5BA", .12)
glass.surface_render_method = 'BLENDED'
glass.node_tree.nodes.get("Principled BSDF").inputs["Alpha"].default_value = .23
copper = pigment("Greenhouse aged bronze", "6E7152", .16)
planter = pigment("Herb bench umber", "684738", .18)
soil = pigment("Dark garden soil", "474032", .07)
leaves = [pigment("Garden foliage " + name, tone, .08) for name, tone in
          [("sage","789066"),("jade","477460"),("yellow","9FA068"),("fern","586D43")]]
petals = [pigment("Glasshouse flowers " + name, tone, .28) for name, tone in
          [("rose","C7808C"),("amber","E7BA63"),("lilac","9A86BE")]]
ground = pigment("Warm clay paving", "827260", .15)
lamp = pigment("Soft amber lantern glass", "CD8B46", 1.2)
girth_left, girth_right = 48.55, 53.05
sill, eave, ridge = 3.58, 6.28, 7.82
south, north = 43, 52
center = (girth_left+girth_right)/2
details = []
for x in (girth_left,girth_right):
    # Glass and narrow framing leave the full central aisle open at both ends.
    for y in (43,45.25,47.5,49.75,52):
        box("Copper post",(x,y,(sill+eave)/2),(.115,.13,eave-sill),copper)
    for ym in (44.125,46.375,48.625,50.875):
        box("Side glazing",(x,ym,5.24),(.038,2.16,2.0),glass)
        box("Low terracotta curb",(x,ym,3.83),(.21,2.22,.46),planter)
    for z in (4.07,5.42,eave):
        box("Long greenhouse rail",(x,(south+north)/2,z),(.13,north-south+.13,.09),copper)
    details.append([x-.12,-north,x+.12,-south])

for y in (south,45.25,47.5,49.75,north):
    for x in (girth_left,girth_right):
        beam("Gabled rafter",(x,y,eave),(center,y,ridge),.067,.048,copper,6)
for edge in (girth_left,girth_right):
    dx = center-edge
    slope = ridge-eave
    length = (dx*dx+slope*slope)**.5
    pane = box("Roof glazing",((center+edge)/2,(south+north)/2,(eave+ridge)/2),
               (length,north-south,.038),glass)
    pane.rotation_euler.y = -atan2(slope,dx)
box("Greenhouse ridge",(center,(south+north)/2,ridge),(.15,north-south+.2,.13),copper)

for row in range(11):
    y = 43.15+row*.78
    for x in (50.10,51.02):
        box("Worn clay aisle paver",(x,y,3.61+(y-43)*.018),(.87,.75,.15),ground,
            random.uniform(-.025,.025))
for x in (49.11,52.36):
    for y in (44.1,46.3,48.6,50.8):
        box("Herb trough",(x,y,4.2),(.67,1.96,.34),planter)
        box("Herb soil",(x,y,4.38),(.58,1.85,.04),soil)
        for yy in (y-.64,y+.01,y+.64):
            xx = x+random.uniform(-.10,.10)
            tip = (xx,yy,4.8+random.random()*.35)
            beam("Herb stem",(xx,yy,4.4),tip,.023,.014,leaves[1],6)
            for side in (-1,1):
                shape("Long herb leaf",(xx+.19*side,yy,4.64),
                      (.24,.14,.075),random.choice(leaves),random.random()*pi)
            if random.random()<.62:
                petal = random.choice(petals)
                for index in range(5):
                    angle = index*2*pi/5
                    shape("Herb flower petal",(tip[0]+.083*cos(angle),tip[1]+.083*sin(angle),tip[2]),
                          (.11,.062,.055),petal,angle)
                shape("Herb flower center",(tip[0],tip[1],tip[2]+.03),(.058,.058,.045),trim)
        details.append([x-.34,-y-.98,x+.34,-y+.98])
for y in (43.25,51.73):
    for x in (49.04,52.59):
        box("Entry lantern copper cap",(x,y,5.96),(.26,.26,.10),copper)
        box("Entry lantern amber light",(x,y,5.77),(.17,.17,.28),lamp)

# Replace the original stones and the later faceted fruit with a single planted patch.
legacy_pumpkins = bpy.data.objects.get("Pumpkin patch")
if legacy_pumpkins:
    bpy.data.objects.remove(legacy_pumpkins, do_unlink=True)

rind = pigment("Pumpkin painted rind", "FFFFFF")
rind_shader = rind.node_tree.nodes.get("Principled BSDF")
rind_shader.inputs["Roughness"].default_value = .76
paint_colors = rind.node_tree.nodes.new("ShaderNodeVertexColor")
paint_colors.layer_name = "Pumpkin paint"
rind.node_tree.links.new(paint_colors.outputs["Color"], rind_shader.inputs["Base Color"])
stalk = pigment("Pumpkin stalk", "74704A", .05)
stalk_tip = pigment("Dry pumpkin stalk", "9A804C", .06)
vine = pigment("Pumpkin vine", "586C3E", .08)
patch_green = pigment("Pumpkin leaf muted green", "626F40", .09)
patch_light = pigment("Pumpkin leaf lit green", "82915A", .09)
earth = pigment("Pumpkin bed earth", "574636", .06)
earth_light = pigment("Pumpkin bed dry soil", "66523A", .06)
patch_rng = Random(420)


def patch_mesh(name, vertices, faces, material, smooth=True):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    paint.objects.link(obj)
    mesh.materials.append(material)
    for face in mesh.polygons:
        face.use_smooth = smooth
    return mesh


def pumpkin_fruit(x, y, foot, radius, height, color, ribs, phase):
    around, bands = ribs * 6, 19
    vertices = [(x, y, foot + height * .06)]
    colors = [(*[value * .55 for value in color], 1)]
    for band in range(1, bands):
        t = pi * band / bands
        lat = sin(t)
        for i in range(around):
            angle = 2*pi*i/around
            rib = (.5 + .5*cos(ribs * angle + .48*cos(t)))**.85
            width = lat**.74 * (1 + .15*rib) * (1 + .049*sin(3*angle+phase))
            z = foot + height * ((1 - cos(t)) / 2 + .05*cos(t)**5 + .019*rib*lat)
            vertices.append((x+radius*width*cos(angle+phase), y+radius*.91*width*sin(angle+phase), z))
            stroke = sin(31*angle + 14*t + 2*sin(7*t)) * sin(22*t - 9*angle)
            shade = .62 + .31*rib + .25*band/bands + .065*stroke + .072*sin(3*t + 3*angle)
            red, green, blue = color
            colors.append((red*shade, green*shade*(1+.11*sin(2*t+angle)), blue*shade, 1))
    vertices.append((x, y, foot+height*.943))
    colors.append((*color, 1))
    top = len(vertices)-1
    faces = []
    for i in range(around):
        following = (i+1)%around
        faces.append((0, 1+following, 1+i))
        for offset in range(1, top-around, around):
            faces.append((offset+i, offset+following, offset+around+following, offset+around+i))
        faces.append((top-around+i, top-around+following, top))
    mesh = patch_mesh("Pumpkin · ribbed fruit", vertices, faces, rind)
    attribute = mesh.color_attributes.new(name="Pumpkin paint", type='FLOAT_COLOR', domain='POINT')
    attribute.data.foreach_set('color', [channel for rgba in colors for channel in rgba])
    base = Vector((x,y,foot+height*.941))
    sway = Vector((cos(phase),sin(phase),0))
    elbow = base + sway*radius*.09 + Vector((0,0,radius*.23))
    tip = elbow + sway*radius*.14 + Vector((0,0,radius*.14))
    beam("Pumpkin · stalk base",base,elbow,radius*.10,radius*.067,stalk,7)
    beam("Pumpkin · dry stalk tip",elbow,tip,radius*.071,radius*.054,stalk_tip,7)


def pumpkin_leaf(anchor, angle, reach):
    direction = Vector((cos(angle), sin(angle), 0))
    side = Vector((-sin(angle), cos(angle), 0))
    center = anchor + direction*reach*.54 + Vector((0, 0, reach*.26))
    outline = [(0,0),(.09,-.43),(.35,-.51),(.46,-.39),(.70,-.35),
               (.71,-.22),(1,0),(.75,.18),(.69,.37),(.46,.36),(.30,.51),(.12,.36)]
    points = [center] + [anchor + reach*(direction*length+side*width) +
                         Vector((0, 0, reach*(.10+.14*length-.14*abs(width)))) for length,width in outline]
    faces = [(0, 1+i, 1+(i+1)%len(outline)) for i in range(len(outline))]
    mesh = patch_mesh("Pumpkin · broad leaf", points, faces, patch_green, smooth=False)
    mesh.materials.append(patch_light)
    for index in (1,2,3,6,7,8):
        mesh.polygons[index].material_index = 1
    beam("Pumpkin · leaf midrib", points[1]+Vector((0,0,.01)), center+Vector((0,0,.01)),
         reach*.023, reach*.012, vine, 5)


for x,y,height,fruit in [
    (60.6,21.6,3.42,[(-.05,-.54,.46,.59),(.16,.47,.35,.46)]),
    (65.65,22.1,3.35,[(-.06,-.49,.44,.67),(.18,.47,.48,.59)]),
    (63.9,24.15,3.38,[(.19,-.62,.36,.48),(-.08,.38,.58,.77)]),
    (58.65,24.65,3.51,[(-.10,-.59,.33,.41),(.04,.40,.53,.67)]),
]:
    vertices = [(x, y, height+.12)]
    count = 18
    for scale, rise in ((.52,.105),(1,-.055)):
        for i in range(count):
            angle = 2*pi*i/count
            edge = patch_rng.uniform(.89,1.06)
            vertices.append((x+.77*scale*edge*cos(angle),y+1.01*scale*edge*sin(angle),
                             height+rise+patch_rng.uniform(-.030,.025)))
    mound_faces = [(0,i+1,(i+1)%count+1) for i in range(count)]
    for i in range(count):
        j=(i+1)%count
        mound_faces.append((i+1,i+count+1,j+count+1,j+1))
    mound = patch_mesh("Pumpkin · low soil mound",vertices,mound_faces,earth)
    mound.materials.append(earth_light)
    for face in mound.polygons:
        face.material_index = int(patch_rng.random()<.29)

    for dx,dy,radius,fruit_height in fruit:
        color = patch_rng.choice(((.78,.197,.024),(.67,.135,.018),(.84,.262,.047),(.59,.173,.028)))
        pumpkin_fruit(x+dx,y+dy,height+.043,radius,fruit_height,color,
                      patch_rng.choice((8,9,10,11)),patch_rng.random()*2*pi)
    start = Vector((x-.40,y-.78,height+.11))
    for dy in (-.46,-.08,.31,.69):
        end = Vector((x+patch_rng.uniform(-.53,-.21),y+dy,height+.115))
        beam("Pumpkin · trailing vine",start,end,.019,.015,vine,6)
        pumpkin_leaf(end,patch_rng.uniform(2.25,4.35),patch_rng.uniform(.28,.51))
        start = end
    details.append([x-.78,-y-1,x+.78,-y+1])

# Watch the northern ridge from the same terrain height as the tower path.
blue_stone = pigment("Observatory cool limestone","89847A",.10)
metallic = pigment("Telescope brass","BFA16C",.20)
for x in (26.7,27.77,28.84):
    box("Observatory parapet",(x,25.35,11.85),(1.21,.43,1.03),blue_stone)
    box("Observatory weathered capping",(x,25.35,12.42),(1.26,.59,.15),ground)
details.append([26.1,-25.57,29.45,-25.13])
beam("Telescope foot",(27.95,23.85,11.75),(27.95,23.85,12.61),.36,.14,blue_stone)
beam("Brass telescope",(27.66,23.37,12.55),(28.42,24.69,13.31),.12,.23,metallic,12)
beam("Telescope objective rim",(28.37,24.61,13.27),(28.46,24.77,13.36),.248,.248,copper,12)
details.append([27.65,-24.17,28.25,-23.55])

# Give the inner forest and station platform their own recognizable stopping places.
moss = pigment("Forest moss dabs","657754",.12)
rock = pigment("Forest granite shade","565E59",.05)
for x,y,z,scale in [(95.15,81.2,3.25,(1.4,.88,.99)),(98.65,81.4,3.24,(1.13,.7,.86)),(99.9,79.4,3.23,(.8,1.1,.8))]:
    shape("Glade granite",(x,y,z),scale,rock,y*.31)
    shape("Rockcap moss",(x+.15,y-.08,z+.54),(scale[0]*.8,scale[1]*.72,.37),moss,y)
    details.append([x-scale[0]*.65,-y-scale[1]*.68,x+scale[0]*.65,-y+scale[1]*.68])
beam("Fallen tree in the glade",(95.3,81.4,3.39),(99.3,81.8,3.55),.52,.32,bark[1],9)

box("Lantern base in the glade",(97.0,80.64,3.51),(.43,.41,.35),bark[1])
box("Lantern glass in the glade",(97.0,80.64,3.85),(.19,.19,.28),lamp)
box("Lantern cap in the glade",(97.0,80.64,4.02),(.29,.29,.07),copper)

rail_sign = pigment("Station sign oxblood","672F36",.14)
box("Station sign board",(12.8,90.04,5.59),(3.39,.16,.49),rail_sign)
box("Station sign upper beading",(12.8,89.934,5.81),(3.39,.05,.048),trim)
box("Station sign lower beading",(12.8,89.934,5.37),(3.39,.05,.048),trim)
bpy.ops.object.text_add(location=(12.8,89.92,5.49),rotation=(pi/2,0,0))
station_sign = place("Hogsmeade · station sign",paper)
station_sign.data.body = "HOGSMEADE STATION"
station_sign.data.align_x = 'CENTER'
station_sign.data.size = .205
for x in (11.22,14.38):
    box("Station sign support",(x,90.04,4.63),(.14,.14,2.02),wood)
for x in (9.4,14.7):
    box("Platform bench seat",(x,89.31,4.33),(1.52,.57,.13),planter)
    box("Platform bench back",(x,89.55,4.64),(1.52,.13,.38),wood_high)
    for dx in (-.55,.55):
        box("Platform bench leg",(x+dx,89.32,4.1),(.12,.42,.49),wood)
    details.append([x-.76,-89.62,x+.76,-89.02])

nav_path = Path(bpy.data.filepath).parents[1]/"navigation.json"
navigation = json.loads(nav_path.read_text())
navigation["detailBlocks"] = [[round(v,3) for v in block] for block in details]
nav_path.write_text(json.dumps(navigation, separators=(",",":"))+"\n")

bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(Path(bpy.data.filepath)))
