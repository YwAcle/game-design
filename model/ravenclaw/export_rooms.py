"""Bake inspected source into four atlases; preserve editable source separately."""
import bpy, os, sys, math, json, time, bmesh
from pathlib import Path
HERE=Path(__file__).resolve().parent
ID=sys.argv[sys.argv.index('--')+1]
ROOT=HERE.parents[1]
MODEL=ROOT/'model'/ID;ASSETS=ROOT/'scene-assets'/ID
bpy.ops.wm.open_mainfile(filepath=str(MODEL/(ID+'.blend')))
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.samples=20;S.cycles.use_denoising=True;S.render.bake.margin=7
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
for d in p.devices:d.use=d.type=='CUDA'
S.cycles.device='GPU' if any(d.type=='CUDA' for d in p.devices) else 'CPU'
S.render.bake.use_clear=True;S.render.bake.use_pass_direct=True;S.render.bake.use_pass_indirect=True
bpy.ops.object.select_all(action='DESELECT')
for o in S.objects:
    if o.type in ['CURVE','FONT']:o.select_set(True)
if bpy.context.selected_objects:
    bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.convert(target='MESH')
groups={k:[] for k in ['floor','architecture','furniture','details','glow']}
for o in S.objects:
    if o.type!='MESH' or not len(o.data.vertices):continue
    o.data=o.data.copy()
    bpy.context.view_layer.objects.active=o
    for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
    if o.name.startswith('Blue pleated star curtain'):
        bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Cloth thickness for stable bake normals','SOLIDIFY');mod.thickness=.025;mod.offset=0;bpy.ops.object.modifier_apply(modifier=mod.name)
    attr=o.data.attributes.new('PaintCoord','FLOAT_VECTOR','POINT')
    lo=[min(v.co[a] for v in o.data.vertices) for a in range(3)];span=[max(v.co[a] for v in o.data.vertices)-lo[a] for a in range(3)]
    for i,v in enumerate(o.data.vertices):attr.data[i].vector=tuple((v.co[a]-lo[a])/span[a] if span[a]>1e-8 else 0 for a in range(3))
    # Curves and generated shapes get coherent normals before atlas packing.
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    col=o.users_collection[0].name[:2];key={'01':'floor','02':'architecture','03':'furniture','04':'details'}.get(col,'details')
    if any(m and m.name.startswith(('Windows |','Lamps |')) for m in o.data.materials):key='glow'
    groups[key].append(o)
for m in bpy.data.materials:
    if not m.use_nodes:continue
    for node in list(m.node_tree.nodes):
        if node.type=='TEX_COORD' and node.outputs['Generated'].is_linked:
            a=m.node_tree.nodes.new('ShaderNodeAttribute');a.attribute_name='PaintCoord'
            for link in list(node.outputs['Generated'].links):m.node_tree.links.new(a.outputs['Vector'],link.to_socket)
joined={};images={}
for key,objects in groups.items():
    if not objects:continue
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=ID+'_'+key;joined[key]=o
    print('JOINED',key,len(o.data.polygons),flush=True)
    if key=='glow':continue
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(68),island_margin=.0015,area_weight=.6,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT');o.data.uv_layers.active.name='BakeUV'
for key,o in joined.items():
    if key=='glow':continue
    size=2048
    im=bpy.data.images.new('Baked_'+key,width=size,height=size,alpha=False);im.colorspace_settings.name='sRGB'
    for mat in o.data.materials:
        if not mat:continue
        n=mat.node_tree.nodes
        for q in n:q.select=False
        q=n.get('BAKE_TARGET') or n.new('ShaderNodeTexImage');q.name='BAKE_TARGET';q.image=im;q.select=True;n.active=q
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    start=time.time();print('BAKING',key,flush=True);bpy.ops.object.bake(type='COMBINED')
    im.filepath_raw=str(MODEL/('baked-'+key+'.jpg'));im.file_format='JPEG';im.save();images[key]=bpy.data.images.load(im.filepath_raw,check_existing=False)
    print('BAKED',key,round(time.time()-start),flush=True)
for key,img in images.items():
    mat=bpy.data.materials.new('Baked | '+key);mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear();tex=n.new('ShaderNodeTexImage');tex.image=img;em=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial');l.new(tex.outputs[0],em.inputs[0]);l.new(em.outputs[0],out.inputs[0]);o=joined[key];o.data.materials.clear();o.data.materials.append(mat)
    for f in o.data.polygons:f.material_index=0
bpy.ops.object.select_all(action='DESELECT')
for o in joined.values():o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ASSETS/'scene.glb'),export_format='GLB',use_selection=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
triangles=0
for o in joined.values():o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
meta=json.load(open(ASSETS/'metadata.json',encoding='utf8'));meta.update(triangles=triangles,meshGroups=list(joined),bakeSamples=20,atlases={k:list(i.size) for k,i in images.items()});json.dump(meta,open(ASSETS/'metadata.json','w',encoding='utf8'),ensure_ascii=False,indent=2)
print('EXPORT_COMPLETE',ID,triangles,(ASSETS/'scene.glb').stat().st_size,flush=True)
sys.path.insert(0,str(HERE))
from normalize_glb import normalize
normalize(ASSETS/'scene.glb')
