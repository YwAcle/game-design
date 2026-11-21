"""Pack the landmark study pigments into portable glTF materials."""
from pathlib import Path
from tempfile import TemporaryDirectory

import bpy
from mathutils import Matrix


def bake_landmark(collection):
    objects = list(collection.objects)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)

    # Apply the shop trim bevels before joining. Work in the original study frame
    # so Blender's Object-coordinate timber and bark still run along the grain.
    placement = Matrix([collection['study_transform'][i:i+4] for i in range(0,16,4)])
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.convert(target='MESH')
    mesh = bpy.data.meshes.new(collection.name)
    joined = bpy.data.objects.new(collection.name, mesh)
    collection.objects.link(joined)
    joined.matrix_world = placement
    joined.select_set(True)
    bpy.context.view_layer.objects.active = joined
    bpy.ops.object.join()
    mesh = joined.data
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.18, island_margin=.003, margin_method='FRACTION')
    bpy.ops.object.mode_set(mode='OBJECT')

    atlas = bpy.data.images.new(collection.name+' · pigment', width=2048, height=2048, alpha=False)
    original = list(mesh.materials)
    for material in set(original) - {None}:
        nodes = material.node_tree.nodes
        target = nodes.new('ShaderNodeTexImage')
        target.image = atlas
        nodes.active = target
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 1
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 12
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, margin=5)

    # Store the compact local atlas before export. Amber glass keeps its own glow.
    with TemporaryDirectory() as directory:
        atlas.filepath_raw = str(Path(directory) / 'pigment.jpg')
        atlas.file_format = 'JPEG'
        atlas.save()
        atlas.pack()

    baked = bpy.data.materials.new(collection.name+' · baked finish')
    baked.use_nodes = True
    shader = baked.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Roughness'].default_value = .90
    source = baked.node_tree.nodes.new('ShaderNodeTexImage')
    source.image = atlas
    baked.node_tree.links.new(source.outputs['Color'],shader.inputs['Base Color'])
    final = [baked]
    assignments = []
    for material in original:
        if material is None:
            assignments.append(0)
            continue
        shader = material.node_tree.nodes.get('Principled BSDF')
        if shader.inputs['Emission Strength'].default_value > .1 and material not in final:
            final.append(material)
        assignments.append(final.index(material) if material in final else 0)
    indices = [assignments[face.material_index] for face in mesh.polygons]
    mesh.materials.clear()
    for material in final:
        mesh.materials.append(material)
    mesh.polygons.foreach_set('material_index',indices)
