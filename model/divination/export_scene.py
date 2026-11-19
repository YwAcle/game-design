"""Bake the inspected editable scene into genuine glTF unlit texture atlases."""
import bpy,os,json,math,time,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent;ID=HERE.name;ROOT=HERE.parent.parent;ASSETS=ROOT/'scene-assets'/ID
bpy.ops.wm.open_mainfile(filepath=str(HERE/'scene.blend'))
S=bpy.context.scene;S.cycles.samples=12;S.cycles.use_denoising=True
p=bpy.context.preferences.addons['cycles'].preferences
try:
 p.compute_device_type='CUDA';p.get_devices()
 for d in p.devices:d.use=d.type=='CUDA'
 S.cycles.device='GPU' if any(d.type=='CUDA' for d in p.devices) else 'CPU'
except Exception:S.cycles.device='CPU'
S.render.bake.margin=5;S.render.bake.use_clear=True;S.render.bake.use_pass_direct=True;S.render.bake.use_pass_indirect=True
groups={k:[] for k in ['floor','architecture','furniture','textile','details','glow','crystal']}
for o in S.objects:
 if o.type!='MESH' or not o.data.vertices:continue
 o.data=o.data.copy()
 lo=[min(v.co[a] for v in o.data.vertices) for a in range(3)];span=[max(v.co[a] for v in o.data.vertices)-lo[a] for a in range(3)]
 for key,norm in [('PaintCoord',True),('LocalCoord',False)]:
  attr=o.data.attributes.new(key,'FLOAT_VECTOR','POINT')
  for i,v in enumerate(o.data.vertices):attr.data[i].vector=tuple((v.co[a]-lo[a])/span[a] if span[a]>1e-8 else 0 for a in range(3)) if norm else v.co
 col=o.users_collection[0].name
 if col.startswith('01'):key='floor'
 elif col.startswith('02'):key='architecture'
 elif col.startswith('03'):key='furniture' if ID=='potions' else 'textile'
 elif col.startswith('04'):key='details' if ID=='potions' else 'furniture'
 else:key='details'
 if any(m and m.name in ['Warm overcast window','Candle flame'] for m in o.data.materials):key='glow'
 if any(m and m.name.startswith('Crystal ') for m in o.data.materials):key='crystal'
 groups[key].append(o)
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 nt=mat.node_tree
 for node in list(nt.nodes):
  if node.type=='TEX_COORD':
   for source,attribute in [('Generated','PaintCoord'),('Object','LocalCoord')]:
    links=list(node.outputs[source].links)
    if links:
     attr=nt.nodes.new('ShaderNodeAttribute');attr.attribute_name=attribute
     for link in links:nt.links.new(attr.outputs['Vector'],link.to_socket)
joined={};images={}
for key,objects in groups.items():
 if not objects:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=ID+'_'+key;joined[key]=o
 print('JOINED',key,len(o.data.polygons),flush=True)
 if key in ['glow','crystal']:continue
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(68),island_margin=.002,area_weight=.5,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT');o.data.uv_layers.active.name='BakeUV'
for key,o in joined.items():
 if key in ['glow','crystal']:continue
 size=4096 if key in ['details','furniture'] else 2048
 img=bpy.data.images.new('Baked_'+key,width=size,height=size,alpha=False);img.colorspace_settings.name='sRGB'
 for mat in o.data.materials:
  if not mat:continue
  nodes=mat.node_tree.nodes
  for node in nodes:node.select=False
  node=nodes.get('BAKE_TARGET') or nodes.new('ShaderNodeTexImage');node.name='BAKE_TARGET';node.image=img;node.select=True;nodes.active=node
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 t=time.time();print('BAKING',ID,key,size,flush=True);bpy.ops.object.bake(type='COMBINED')
 dest=HERE/'textures'/('baked-'+key+'.jpg');img.filepath_raw=str(dest);img.file_format='JPEG';img.save();images[key]=bpy.data.images.load(str(dest),check_existing=False)
 print('BAKED',ID,key,round(time.time()-t),flush=True)
for key,img in images.items():
 mat=bpy.data.materials.new('Baked | '+ID+' | '+key);mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear();tex=n.new('ShaderNodeTexImage');tex.image=img;em=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial');l.new(tex.outputs[0],em.inputs[0]);l.new(em.outputs[0],out.inputs[0])
 o=joined[key];o.data.materials.clear();o.data.materials.append(mat)
 for face in o.data.polygons:face.material_index=0
bpy.ops.object.select_all(action='DESELECT')
for o in joined.values():o.select_set(True)
dest=ASSETS/'scene.glb'
bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',use_selection=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
# Explicitly normalize baked materials to KHR_materials_unlit. Emission-only node
# graphs otherwise export differently between Blender glTF add-on versions.
data=dest.read_bytes();jlen,jtype=struct.unpack_from('<II',data,12);doc=json.loads(data[20:20+jlen]);binpos=20+jlen;chunks=data[binpos:]
for m in doc.get('materials',[]):
 if m.get('name','').startswith('Baked |'):
  texture=m.pop('emissiveTexture',None);pbr=m.setdefault('pbrMetallicRoughness',{});pbr['baseColorFactor']=[1,1,1,1];pbr['metallicFactor']=0;pbr['roughnessFactor']=1
  if texture:pbr['baseColorTexture']=texture
  m.pop('emissiveFactor',None);ext=m.setdefault('extensions',{});ext.pop('KHR_materials_emissive_strength',None);ext['KHR_materials_unlit']={}
# Transparent art glass keeps its independent layers, alpha and gentle authored tint.
for m in doc.get('materials',[]):
 if m.get('name','').startswith('Crystal '):
  name=m['name'];color=([.46,.44,.57,.28] if 'shell' in name else [.38,.35,.48,.42] if 'core' in name else [.77,.72,.82,.36])
  m['pbrMetallicRoughness']={'baseColorFactor':color,'metallicFactor':0,'roughnessFactor':.3}
  m['alphaMode']='BLEND';m['doubleSided']=False
  m.pop('emissiveFactor',None);m.pop('emissiveTexture',None)
  m['extensions']={'KHR_materials_unlit':{}}
if 'KHR_materials_unlit' not in doc.setdefault('extensionsUsed',[]):doc['extensionsUsed'].append('KHR_materials_unlit')
raw=json.dumps(doc,separators=(',',':')).encode();raw+=b' '*((-len(raw))%4);total=12+8+len(raw)+len(chunks);dest.write_bytes(struct.pack('<III',0x46546c67,2,total)+struct.pack('<II',len(raw),0x4e4f534a)+raw+chunks)
triangles=0
for o in joined.values():o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
meta=json.load(open(ASSETS/'metadata.json',encoding='utf-8'));meta.update(triangles=triangles,meshGroups=list(joined),bakeSamples=12,atlases={k:list(i.size) for k,i in images.items()},sourceCoordinatesPreserved=['Generated->PaintCoord','Object->LocalCoord'],gltfUnlitMaterials=sum('KHR_materials_unlit' in m.get('extensions',{}) for m in doc['materials']))
json.dump(meta,open(ASSETS/'metadata.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('EXPORT_COMPLETE',ID,triangles,dest.stat().st_size,flush=True)
