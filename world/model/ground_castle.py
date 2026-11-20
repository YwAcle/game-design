"""Extend the castle's original ground-level masonry down into the grounds."""
from collections import Counter
import json
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

scene = bpy.context.scene
castle = next(obj for obj in scene.objects if obj.get('artist') == 'Sebastian Holthausen')
ashlar = bpy.data.materials['Weathered Hogwarts ashlar']
name = 'Castle masonry foundations'
if old := bpy.data.objects.get(name):
    bpy.data.objects.remove(old, do_unlink=True)

vertices, faces, sections = [], [], []
corners = {}
edges = Counter()
for face in castle.data.polygons:
    if castle.data.materials[face.material_index] != ashlar or face.normal.z > -.98:
        continue
    points = [castle.matrix_world @ castle.data.vertices[i].co for i in face.vertices]
    # The main masonry is seated at 13.65 m. Higher undersides include
    # door heads, covered passages and projecting ornament.
    if max(p.z for p in points) > 13.68 or max(p.z for p in points) - min(p.z for p in points) > .008:
        continue
    section = []
    for point in points:
        key = tuple(round(v, 4) for v in point)
        if key not in corners:
            corners[key] = len(vertices)
            # The surveyed plateau under the castle is approximately 12 m high.
            vertices.extend([(point.x, point.y, 11.2), (point.x, point.y, point.z + .045)])
        section.append(corners[key])
    sections.append(section)
    for a, b in zip(section, section[1:] + section[:1]):
        edges[a, b] += 1

for section in sections:
    faces.append(section)
    faces.append([a + 1 for a in reversed(section)])
for a, b in edges:
    if edges[a, b] > edges[b, a]:
        faces.append([a + 1, b + 1, b, a])

foundation = bpy.data.meshes.new(name)
foundation.from_pydata(vertices, [], faces)
foundation.materials.append(ashlar)
uv = foundation.uv_layers.new(name='Ashlar')
for face in foundation.polygons:
    direction = face.normal.cross((0, 0, 1))
    for index in face.loop_indices:
        point = foundation.vertices[foundation.loops[index].vertex_index].co
        if abs(face.normal.z) < .5:
            uv.data[index].uv = (point.dot(direction) * .40, point.z * .40)
        else:
            uv.data[index].uv = (point.x * .40, point.y * .40)

assert len(sections) > 1000 and len(faces) > 2 * len(sections)
obj = bpy.data.objects.new(name, foundation)
scene.collection.objects.link(obj)
print(f'Grounded {len(sections)} underside faces with {len(faces) - 2 * len(sections)} side faces')

# The kit-built kitchen porch was behind the original southern parapet.
# Bring its opening forward of the masonry and leave space behind the casks.
porch = [
    'Wall_UnevenBrick_Door_Round.004', 'DoorFrame_Round_Brick.004', 'Door_4_Round.004',
    'Wall_UnevenBrick_Straight.008', 'Wall_UnevenBrick_Straight.009',
    'Prop_Vine2.008', 'Prop_Vine2.009', 'Roof_RoundTiles_4x4.004',
    'kitchen wall torch', 'kitchen wall torch.001',
]
cask_names = ('Kitchen · cask', 'Iron cask hoop', 'Solidity of end grain',
              'Cask board seam', 'Cask center pin')
casks = [item for item in scene.objects if item.name.startswith(cask_names)]
depth_scale = Matrix.Diagonal((1, 1.5, 1, 1))
cask_depth = Matrix.Translation((0, -12.14, 0)) @ depth_scale @ Matrix.Translation((0, 10.48, 0))
for item in [*(bpy.data.objects[name] for name in porch), *casks]:
    if 'kitchen original transform' not in item:
        item['kitchen original transform'] = [value for row in item.matrix_world for value in row]
    values = item['kitchen original transform']
    original = Matrix([values[i:i+4] for i in range(0, 16, 4)])
    if item.name in porch:
        item.matrix_world = Matrix.Translation((0, -1.22, 0)) @ original
    else:
        lift = .10 if abs(original.translation.x) < .7 else .22
        item.matrix_world = Matrix.Translation((0, 0, lift)) @ cask_depth @ original

for index, (x, width) in enumerate([(-1.12, .39), (0, 1.16), (1.14, .45)]):
    support_name = f'Kitchen cask cradle {index + 1}'
    if old_support := bpy.data.objects.get(support_name):
        bpy.data.objects.remove(old_support, do_unlink=True)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x,-12.67,12.18))
    support = bpy.context.object
    support.name = support_name
    support.scale = (width, .65, .22)
    support.data.materials.append(bpy.data.materials['Dark timber'])

# Check the finished mesh bounds against the actual masonry on both sides of the gap.
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
masonry = BVHTree.FromObject(castle, depsgraph)
base = BVHTree.FromObject(obj, depsgraph)
for item in casks:
    points = [item.matrix_world @ Vector(corner) for corner in item.bound_box]
    for x, z in {(p.x, p.z) for p in points} | {(item.location.x, item.location.z)}:
        origin = (x, min(p.y for p in points)-.05, z)
        depth = max(p.y for p in points) - origin[1] + .12
        assert masonry.ray_cast(origin, (0,1,0), depth)[0] is None, item.name
        assert base.ray_cast(origin, (0,1,0), depth)[0] is None, item.name

nav_path = Path(bpy.data.filepath).parents[1] / 'navigation.json'
nav = json.loads(nav_path.read_text())
for bounds in [[-1.87, 8.8, 1.87, 11.78], [-1.55, 12.14, 1.55, 13.17]]:
    if bounds not in nav['blocks']:
        nav['blocks'].append(bounds)
nav_path.write_text(json.dumps(nav, separators=(',', ':')) + '\n')

bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath, compress=True)
