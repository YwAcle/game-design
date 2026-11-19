"""Bake the inspected source scene and export a portable unlit GLB."""
import bpy,os,json,math,time
HERE=os.path.dirname(os.path.abspath(__file__));ROOT=os.path.abspath(os.path.join(HERE,'..','..'));ASSETS=os.path.join(ROOT,'scene-assets','arena')
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE,'Dueling_Club.blend'))
S=bpy.context.scene;S.cycles.samples=20;S.cycles.use_denoising=True
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
for d in p.devices:d.use=d.type=='CUDA'
S.cycles.device='GPU';S.render.bake.margin=6;S.render.bake.use_clear=True
S.render.bake.use_pass_direct=True;S.render.bake.use_pass_indirect=True
groups={k:[] for k in ['floor','architecture','seating','cloth','details','glow']}
import sys
sys.path.insert(0,os.path.dirname(HERE))
from bake_coordinates import freeze
freeze()
for o in list(S.objects):
    if o.type!='MESH':continue
    mats=[m.name for m in o.data.materials if m]
    col=o.users_collection[0].name[:2]
    key='floor' if col=='01' else 'seating' if col=='02' else 'architecture' if col in ['03','06'] else 'cloth' if col=='04' else 'details'
    if any(m.startswith(('Windows |','Lamps |')) for m in mats):key='glow'
    groups[key].append(o)
joined={};images={}
for key,objects in groups.items():
    if not objects:continue
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
    o=bpy.context.object;o.name='Arena_'+key;joined[key]=o
    print('JOINED',key,len(o.data.polygons),flush=True)
    if key=='glow':continue
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(70),island_margin=.002,area_weight=.3,correct_aspect=True,scale_to_bounds=True)
    bpy.ops.object.mode_set(mode='OBJECT');o.data.uv_layers.active.name='BakeUV'
for key,o in joined.items():
    if key=='glow':continue
    size=4096 if key in ['floor','architecture','seating'] else 2048
    im=bpy.data.images.new('Baked_'+key,width=size,height=size,alpha=False);im.colorspace_settings.name='sRGB'
    for mat in o.data.materials:
        if not mat:continue
        n=mat.node_tree.nodes
        for node in n:node.select=False
        node=n.get('BAKE_TARGET') or n.new('ShaderNodeTexImage');node.name='BAKE_TARGET';node.image=im;node.select=True;n.active=node
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    start=time.time();print('BAKING',key,size,flush=True);bpy.ops.object.bake(type='COMBINED')
    im.filepath_raw=os.path.join(ASSETS,'baked-'+key+'.jpg');im.file_format='JPEG';im.save()
    images[key]=bpy.data.images.load(im.filepath_raw,check_existing=False)
    print('BAKED',key,round(time.time()-start),flush=True)
for key,img in images.items():
    mat=bpy.data.materials.new('Baked | '+key);mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear()
    tex=n.new('ShaderNodeTexImage');tex.image=img;em=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial');l.new(tex.outputs[0],em.inputs[0]);l.new(em.outputs[0],out.inputs[0])
    o=joined[key];o.data.materials.clear();o.data.materials.append(mat)
    for f in o.data.polygons:f.material_index=0
bpy.ops.object.select_all(action='DESELECT')
for o in joined.values():o.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(ASSETS,'dueling-arena.glb'),export_format='GLB',use_selection=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
triangles=0
for o in joined.values():o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
meta_path=os.path.join(ASSETS,'metadata.json');meta=json.load(open(meta_path));meta.update(triangles=triangles,meshGroups=list(joined),bakeSamples=20,atlases={k:list(i.size) for k,i in images.items()})
json.dump(meta,open(meta_path,'w'),indent=2)
print('EXPORT_COMPLETE',triangles,os.path.getsize(os.path.join(ASSETS,'dueling-arena.glb')),flush=True)

import sys
sys.path.insert(0,os.path.dirname(HERE))
from normalize_baked_glb import normalize
normalize(os.path.join(ASSETS,'dueling-arena.glb'))
