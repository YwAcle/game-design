"""Export the packed campus .blend into its adjacent web project (Blender 5.3)."""
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from bake_landmarks import bake_landmark

scene_path = Path(bpy.data.filepath)
castle = next(o for o in bpy.context.scene.objects if o.get("artist") == "Sebastian Holthausen")
bpy.context.view_layer.objects.active = castle
modifier = castle.modifiers.new("Web silhouette", "DECIMATE")
modifier.ratio = .32
bpy.ops.object.modifier_apply(modifier=modifier.name)
castle.data.validate(clean_customdata=False)

# Preserve editable linked modules in the .blend. Batch nearby modules in the web copy.
for collection in bpy.data.collections:
    if collection.get('study_transform'):
        bake_landmark(collection)
        continue
    objects = [obj for obj in collection.objects if obj.type == "MESH"]
    if " · " not in collection.name or len(objects) < 3:
        continue
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    active = objects[0]
    if active.data.users > 1:
        active.data = active.data.copy()
    bpy.context.view_layer.objects.active = active
    bpy.ops.object.join()
    active.name = collection.name

with TemporaryDirectory() as temp:
    for image in bpy.data.images:
        # Limit textures used on small modular props, retaining the castle and foliage atlases.
        if not image.name.startswith(("T_", "coastal_cliff_02")) or max(image.size) <= 512:
            continue
        image.scale(512,512)
        alpha = "Vine" in image.name
        image.filepath_raw = str(Path(temp) / (str(image.as_pointer()) + (".png" if alpha else ".jpg")))
        image.file_format = "PNG" if alpha else "JPEG"
        image.save()
        image.pack()
    bpy.ops.export_scene.gltf(filepath=str(scene_path.parents[1] / "grounds.glb"),
        export_format="GLB", export_animations=False, export_cameras=False, export_lights=False,
        export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
        export_draco_position_quantization=15, export_draco_texcoord_quantization=14)
