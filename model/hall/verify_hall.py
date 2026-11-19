import bpy,bmesh,os,json
from mathutils import Vector
HERE=os.path.dirname(os.path.abspath(__file__));ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE,'Great_Hall_ArtRefined.blend'))
S=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();audit={'closedMeshes':0,'invertedClosedMeshes':0,'floorSamples':[],'aisleClear':True}
for o in S.objects:
    if o.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(o.data)
    if len(bm.faces) and all(e.is_manifold for e in bm.edges):
        audit['closedMeshes']+=1
        if bm.calc_volume(signed=True)<-.000001:audit['invertedClosedMeshes']+=1
    bm.free()
audit['negativeTransforms']=[o.name for o in S.objects if o.type=='MESH' and o.matrix_world.to_3x3().determinant()<0]
for y in [-1.75,0,1.75]:
    for i in range(27):
        x=-5.8+i
        hit,loc,norm,ind,obj,mat=S.ray_cast(deps,Vector((x,y,1.7)),Vector((0,0,-1)),distance=2)
        audit['floorSamples'].append(bool(hit and -.05<loc.z<.06))
    hit,*_=S.ray_cast(deps,Vector((-5.8,y,1.7)),Vector((1,0,0)),distance=26)
    audit['aisleClear'] &= not hit
assert audit['invertedClosedMeshes']==0,audit
assert not audit['negativeTransforms'],audit
assert all(audit['floorSamples']) and audit['aisleClear'],audit
with open(os.path.join(HERE,'source-audit.json'),'w') as f:json.dump(audit,f,indent=2)
print('MODEL_VERIFIED',audit,flush=True)
if '--render' in __import__('sys').argv:
    p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
    for d in p.devices:d.use=d.type=='CUDA'
    S.cycles.device='GPU';S.render.filepath=os.path.join(ROOT,'Great_Hall_Refined.png');bpy.ops.render.render(write_still=True)
