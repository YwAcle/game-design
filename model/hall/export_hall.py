"""Cycles baked, merged GLB export. Run after refine_hall.py with Blender 5.3."""
import bpy,os,json,math,time
from mathutils import Vector
HERE=os.path.dirname(os.path.abspath(__file__));ROOT=os.path.abspath(os.path.join(HERE,'..','..'));ASSETS=os.path.join(ROOT,'scene-assets','hall')
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE,'Great_Hall_ArtRefined.blend'))
S=bpy.context.scene;S.cycles.samples=24;S.cycles.use_denoising=True
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
for d in p.devices:d.use=d.type=='CUDA'
S.cycles.device='GPU';S.render.bake.margin=8;S.render.bake.use_clear=True
S.render.bake.use_pass_direct=True;S.render.bake.use_pass_indirect=True
os.makedirs(ASSETS,exist_ok=True)
import sys
sys.path.insert(0,os.path.dirname(HERE))
from bake_coordinates import freeze
freeze()

groups={k:[] for k in ['floor','stone','timber','furniture','details','glow','sky']}
flames=[]
for o in list(S.objects):
    if o.type!='MESH':continue
    name=o.name
    mat=o.data.materials[0].name if o.data.materials else ''
    if name.startswith(('I | tapered flame','R | table flame')):
        vs=[o.matrix_world@v.co for v in o.data.vertices];c=sum(vs,Vector())/len(vs)
        flames.append([round(c.x,4),round(c.z,4),round(-c.y,4)])
    if 'flame' in mat or 'celestial stars' in mat:key='glow'
    elif 'ceiling' in name:key='sky'
    elif 'flagstone' in name or 'support' in name:key='floor'
    elif any(c.name.startswith('11') for c in o.users_collection):key='timber'
    elif mat in ['I | warm sandstone','I | dressed pale limestone']:key='stone'
    elif mat in ['I | oak aged dark','I | polished honey oak','R | exposed wood']:key='furniture'
    else:key='details'
    groups[key].append(o)

joined={}
for key,objects in groups.items():
    if not objects:continue
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
    o=bpy.context.object;o.name='Hall_'+key;joined[key]=o
    print('JOINED',key,len(o.data.polygons),flush=True)
    if key=='glow':continue
    # Shared material slots are consolidated by join; UV only affects baked output.
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(70),island_margin=.002,area_weight=.3,correct_aspect=True,scale_to_bounds=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    if o.data.uv_layers:o.data.uv_layers.active.name='BakeUV'

images={}
for key,o in joined.items():
    if key=='glow':continue
    size={'floor':2048,'stone':4096,'timber':2048,'furniture':4096,'details':2048,'sky':1024}[key]
    image=bpy.data.images.new('Baked_'+key,width=size,height=size,alpha=False,float_buffer=False)
    image.colorspace_settings.name='sRGB'
    for mat in o.data.materials:
        if not mat:continue
        nodes=mat.node_tree.nodes
        for node in nodes:node.select=False
        n=nodes.get('BAKE_TARGET') or nodes.new('ShaderNodeTexImage');n.name='BAKE_TARGET';n.image=image;n.select=True;nodes.active=n
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    start=time.time();print('BAKING',key,size,flush=True)
    bpy.ops.object.bake(type='COMBINED')
    image.filepath_raw=os.path.join(ASSETS,'baked-'+key+'.jpg');image.file_format='JPEG';image.save()
    # Reload JPEG so export uses the actual compressed artifact, not a PNG conversion.
    images[key]=bpy.data.images.load(image.filepath_raw,check_existing=False)
    print('BAKED',key,round(time.time()-start),flush=True)

for key,img in images.items():
    mat=bpy.data.materials.new('Baked | '+key);mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear()
    tex=n.new('ShaderNodeTexImage');tex.image=img;em=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial')
    l.new(tex.outputs['Color'],em.inputs['Color']);l.new(em.outputs[0],out.inputs['Surface'])
    o=joined[key];o.data.materials.clear();o.data.materials.append(mat)
    for f in o.data.polygons:f.material_index=0

# Export only model meshes; all baked lighting is already included.
bpy.ops.object.select_all(action='DESELECT')
for o in joined.values():o.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(ASSETS,'great-hall.glb'),export_format='GLB',use_selection=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
triangles=0
for o in joined.values():o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
metadata={'flames':flames,'triangles':triangles,'meshGroups':list(joined),'source':'Great_Hall_ArtRefined.blend','bakeSamples':24,'atlases':{k:[i.size[0],i.size[1]] for k,i in images.items()}}
with open(os.path.join(ASSETS,'metadata.json'),'w') as f:json.dump(metadata,f,indent=2)
print('EXPORT_COMPLETE',triangles,os.path.getsize(os.path.join(ASSETS,'great-hall.glb')),flush=True)

import sys
sys.path.insert(0,os.path.dirname(HERE))
from normalize_baked_glb import normalize
normalize(os.path.join(ASSETS,'great-hall.glb'))
