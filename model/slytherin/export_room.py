"""Bake original static interior lighting; export self-contained unlit GLB."""
import bpy,os,json,math,time,struct
HERE=os.path.dirname(os.path.abspath(__file__));ROOM=os.path.basename(HERE);ROOT=os.path.dirname(os.path.dirname(HERE));ASSETS=os.path.join(ROOT,'scene-assets',ROOM)
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE,ROOM+'.blend'));S=bpy.context.scene;S.cycles.samples=18;S.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type='CUDA';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='CUDA'
    S.cycles.device='GPU' if any(d.type=='CUDA' for d in prefs.devices) else 'CPU'
except Exception:S.cycles.device='CPU'
# Preserve a full 16:9 source preview from the exact source used for the bake.
S.render.resolution_percentage=100;S.render.filepath=os.path.join(ROOT,'previews','blender-'+ROOM+'.png')
bpy.ops.render.render(write_still=True)
mesh_objects=[o for o in S.objects if o.type=='MESH']
source_audit={'room':ROOM,'objects':len(S.objects),'meshObjects':len(mesh_objects),'negativeScaleObjects':[o.name for o in mesh_objects if o.matrix_world.determinant()<0],'packedImages':sum(bool(i.packed_file) for i in bpy.data.images),'sourceFile':ROOM+'.blend','revision':'reference-guided V2','cameraAspect':[16,9]}
if source_audit['negativeScaleObjects']:raise RuntimeError('Negative source transform')
json.dump(source_audit,open(os.path.join(HERE,'source-audit.json'),'w'),indent=2)
S.render.bake.margin=8;S.render.bake.use_clear=True;S.render.bake.use_pass_direct=True;S.render.bake.use_pass_indirect=True
groups={k:[] for k in ['floor','architecture','furniture','details','glow']}
for o in S.objects:
    if o.type!='MESH' or not o.data.vertices:continue
    # Stable local-box source coordinates survive join; baked UV is a separate layer.
    o.data=o.data.copy();attr=o.data.attributes.new('PaintCoord','FLOAT_VECTOR','POINT')
    lo=[min(v.co[a] for v in o.data.vertices) for a in range(3)];span=[max(v.co[a] for v in o.data.vertices)-lo[a] for a in range(3)]
    for i,v in enumerate(o.data.vertices):attr.data[i].vector=tuple((v.co[a]-lo[a])/span[a] if span[a]>1e-8 else 0 for a in range(3))
    col=o.users_collection[0].name[:2];key={'01':'floor','02':'architecture','03':'furniture'}.get(col,'details')
    if any(m and m.name.startswith('Glow |') for m in o.data.materials):key='glow'
    groups[key].append(o)
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    nt=mat.node_tree
    for node in list(nt.nodes):
        if node.type=='TEX_COORD' and node.outputs['Generated'].is_linked:
            a=nt.nodes.new('ShaderNodeAttribute');a.attribute_name='PaintCoord'
            for link in list(node.outputs['Generated'].links):nt.links.new(a.outputs['Vector'],link.to_socket)
joined={};images={}
for key,objects in groups.items():
    if not objects:continue
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=ROOM+'_'+key;joined[key]=o
    print('JOINED',key,len(o.data.polygons),flush=True)
    if key=='glow':continue
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(70),island_margin=.0025,area_weight=.5,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT');o.data.uv_layers.active.name='BakeUV'
for key,o in joined.items():
    if key=='glow':continue
    size=3072 if key in ['architecture','furniture'] else 2048
    im=bpy.data.images.new('Baked_'+key,width=size,height=size,alpha=False);im.colorspace_settings.name='sRGB'
    for mat in o.data.materials:
        if not mat:continue
        n=mat.node_tree.nodes
        for node in n:node.select=False
        node=n.get('BAKE_TARGET') or n.new('ShaderNodeTexImage');node.name='BAKE_TARGET';node.image=im;node.select=True;n.active=node
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;t=time.time();print('BAKING',key,size,flush=True);bpy.ops.object.bake(type='COMBINED')
    path=os.path.join(HERE,'textures','baked-'+key+'.jpg');im.filepath_raw=path;im.file_format='JPEG';im.save();images[key]=bpy.data.images.load(path,check_existing=False);print('BAKED',key,round(time.time()-t,1),flush=True)
for key,img in images.items():
    mat=bpy.data.materials.new('Baked | '+key);mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear();tex=n.new('ShaderNodeTexImage');tex.image=img;em=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial');l.new(tex.outputs[0],em.inputs[0]);l.new(em.outputs[0],out.inputs[0]);o=joined[key];o.data.materials.clear();o.data.materials.append(mat)
    for f in o.data.polygons:f.material_index=0
bpy.ops.object.select_all(action='DESELECT')
for o in joined.values():o.select_set(True)
path=os.path.join(ASSETS,'scene.glb')
bpy.ops.export_scene.gltf(filepath=path,export_format='GLB',use_selection=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=False)
# Ensure the baked colour is a true unlit base-colour texture, not an emissive
# PBR approximation dependent on the viewer's light or emissive-strength support.
data=open(path,'rb').read();n,kind=struct.unpack_from('<II',data,12);doc=json.loads(data[20:20+n]);binary=data[20+n:]
for mat in doc.get('materials',[]):
    if mat.get('name','').startswith('Baked |'):
        tex=mat.pop('emissiveTexture',None)
        if tex is None:raise RuntimeError('Baked texture missing from exporter')
        mat['pbrMetallicRoughness']={'baseColorFactor':[1,1,1,1],'baseColorTexture':tex,'metallicFactor':0,'roughnessFactor':1};mat.pop('emissiveFactor',None);mat['extensions']={'KHR_materials_unlit':{}}
doc.setdefault('extensionsUsed',[])
if 'KHR_materials_unlit' not in doc['extensionsUsed']:doc['extensionsUsed'].append('KHR_materials_unlit')
jb=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode();jb+=b' '*((-len(jb))%4);open(path,'wb').write(struct.pack('<4sII',b'glTF',2,12+8+len(jb)+len(binary))+struct.pack('<II',len(jb),0x4E4F534A)+jb+binary)
triangles=0
for o in joined.values():o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
meta_path=os.path.join(ASSETS,'metadata.json');meta=json.load(open(meta_path,encoding='utf8'));meta.update(triangles=triangles,meshGroups=list(joined),bakeSamples=18,atlases={k:list(i.size) for k,i in images.items()},glbBytes=os.path.getsize(path),lighting='baked');json.dump(meta,open(meta_path,'w',encoding='utf8'),ensure_ascii=False,indent=2)
meta['technicalReference']='itsLucas02/3d-room aca0dc0348716cc6755a3f9e98d8954fc07b65d9: separation of baked base lighting and local illumination; independent implementation, no copied assets/code.'
meta['refinement']='Original reference-guided V2: revised architecture, camera, furnishing silhouettes and authored painted surfaces.'
meta['bounds']['minX']=-7.3;meta['bounds']['maxX']=7.3
if ROOM=='slytherin':meta['bounds']['minZ']=-5.25
json.dump(meta,open(meta_path,'w',encoding='utf8'),ensure_ascii=False,indent=2)
print('EXPORT_COMPLETE',ROOM,triangles,os.path.getsize(path),flush=True)
