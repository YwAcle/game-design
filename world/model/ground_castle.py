"""Extend the castle's original ground-level masonry down into the grounds."""
from collections import Counter

import bpy

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
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath, compress=True)
