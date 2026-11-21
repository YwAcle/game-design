"""Fit the three meter-scale landmark studies to the campus ground and paths."""
import json
from math import atan2, hypot, radians
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
sys.path.insert(0, str(Path(__file__).resolve().parent))
from atlas_paths import draw_paths

WORLD = Path(bpy.data.filepath).parents[1]
scene = bpy.context.scene
layout = json.loads((WORLD / 'layout.json').read_text())
places = {p['id']: p for p in layout['places']}
nav_path = WORLD / 'navigation.json'
nav = json.loads(nav_path.read_text())
names = {'willow': 'Whomping Willow', 'shack': 'Shrieking Shack', 'owlery': 'Owlery'}
collisions = []
nav['flights'] = [flight for flight in nav['flights'] if flight.get('site') != 'owlery']

def ground(x, y):
    u, v = (x-nav['x0'])/nav['step'], (-y-nav['z0'])/nav['step']
    i, j = int(u), int(v)
    s, t = u-i, v-j
    a, b = nav['heights'][j][i:i+2]
    c, d = nav['heights'][j+1][i:i+2]
    return a + (b-a)*s + (d-b)*t if s >= t else a + (d-c)*s + (c-a)*t


for id, name in names.items():
    place = places[id]
    x, z = place['look']
    rotation = Matrix.Rotation(radians(place['modelHeading']), 4, 'Z')
    height = ground(x, -z)
    if id == 'shack':
        # Keep the walls upright over a level slab, with the terrain rising into the stonework.
        height = max(ground(x+dx, -z+dy) for dx in (-3,0,4) for dy in (-3,0,3))-.10
    edit = Matrix.Translation((x,-z,height)) @ rotation
    atlas_name = 'Atlas · ' + name
    if old := bpy.data.collections.get(atlas_name):
        for obj in list(old.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(old)
    source = WORLD/'model'/'landmark-studies'/f'{id}.blend'
    with bpy.data.libraries.load(str(source)) as (available, appended):
        appended.collections = [f'{id.title()} · editable asset']
    group, = appended.collections
    group.name = atlas_name
    group['study_transform'] = [value for row in edit for value in row]
    scene.collection.children.link(group)
    for obj in group.objects:
        if id == 'willow' and obj.name.startswith(('Root passage hatch','Hatch strap','Hatch ring')):
            door_x, door_z = place['door']
            hatch = edit @ Vector((-.045,-2.01,0))
            offset = Vector((door_x-hatch.x,-door_z-hatch.y,ground(door_x,-door_z)-height+.03))
            obj.matrix_world = Matrix.Translation(offset) @ edit @ obj.matrix_world
            continue
        if id == 'willow' and obj.name.startswith(('Root mound','Exposed lateral root','Fork of exposed root','Moss against root')):
            # Let the ends of the roots follow the bank without bending the trunk.
            for vertex in obj.data.vertices:
                p = edit @ (obj.matrix_world @ vertex.co)
                falloff = max(0,min(1,(1.1-vertex.co.z)/.85))
                vertex.co.z += (ground(p.x,p.y)-height-.025)*falloff
        obj.matrix_world = edit @ obj.matrix_world
    if id == 'willow':
        collisions.append([x-2,z-1.44,x+2.02,z+1.62])
    if id == 'shack':
        collisions.extend([[x-3.50,z-2.66,x+2.81,z+3.18],[x+1.75,z-2.78,x+4,z+.76]])
    if id == 'owlery':
        collisions.extend([[x-3.80,z-1.0,x+1.15,z+4.25],[x-.65,z-2.16,x+1.94,z+2.56]])
        # The navigation profile uses the same tread rise as the editable staircase.
        low = edit @ Vector((-.595,-4.21,.12))
        high = edit @ Vector((0,-2.16,1.55))
        mid = (low+high)/2
        nav['flights'].append(dict(site='owlery', cx=mid.x, cz=-mid.y,
            angle=atan2(-(high.x-low.x),high.y-low.y), width=.94,
            length=hypot(high.x-low.x,high.y-low.y),
            profile=[round(low.z+(high.z-low.z)*i/20,4) for i in range(21)]))
    print(f'{name}: {len(group.objects)} parts at ({x}, {z}), ground={height:.2f} m', flush=True)

legacy = [
    [-85.9,9.1,-78.1,16.9], [73.55,-.95,76.45,1.95], [-89.5,-64.7,-82.5,-59.3]
]
nav['atlasBlocks'] = [block for block in nav['atlasBlocks'] if block not in legacy]
nav['landmarkBlocks'] = [[round(value,3) for value in block] for block in collisions]
paths = bpy.data.collections['Atlas · Highland paths']
for obj in list(paths.objects):
    bpy.data.objects.remove(obj,do_unlink=True)
draw_paths(paths,layout,places,ground,bpy.data.materials['Dirt'])

# Old billboard trees predate the tower's new position. Clear the stone steps
# and the approach, leaving the west-valley tree line on both sides.
clearings = [(-83.2,15.0,4.55),(-84.0,-86.6,2.7)]
for name in ('Fir crowns 0','Fir crowns 1'):
    tree = bpy.data.objects[name]
    mesh = bmesh.new()
    mesh.from_mesh(tree.data)
    covered = []
    for face in mesh.faces:
        center = face.calc_center_median()
        if any(hypot(center.x-x,center.y+z)<radius for x,z,radius in clearings):
            covered.append(face)
    if covered:
        bmesh.ops.delete(mesh,geom=covered,context='FACES')
        mesh.to_mesh(tree.data)
    mesh.free()
nav['blocks'] = [block for block in nav['blocks'] if not (
    max(block[2]-block[0],block[3]-block[1]) < 1.15 and
    any(hypot((block[0]+block[2])/2-x,(block[1]+block[3])/2-z) < radius
        for x,z,radius in clearings)
)]
nav_path.write_text(json.dumps(nav,separators=(',',':'))+'\n')
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath, compress=True)
