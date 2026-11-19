"""Read-only source and metadata verification. Run inside Blender with -- <room>."""
import bpy, sys, json, math
from pathlib import Path
from mathutils import Vector
here=Path(__file__).resolve().parent
room=sys.argv[sys.argv.index('--')+1]
model=here.parent/room;root=here.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(model/(room+'.blend')))
scene=bpy.context.scene
meta=json.loads((root/'scene-assets'/room/'metadata.json').read_text(encoding='utf8'))
bad=[];negative=[];mesh_objects=0;polygons=0
for o in scene.objects:
    if o.type!='MESH':continue
    mesh_objects+=1;polygons+=len(o.data.polygons)
    if o.matrix_world.determinant()<=0:negative.append(o.name)
    if any(not math.isfinite(v) for vert in o.data.vertices for v in vert.co):bad.append(o.name)
cam=scene.camera
actual_fov=math.degrees(2*math.atan(cam.data.sensor_width/(2*cam.data.lens*(scene.render.resolution_x/scene.render.resolution_y))))
saved=meta['cameras'][0]
assert max(abs(a-b) for a,b in zip(saved['position'],[cam.location.x,cam.location.z,-cam.location.y]))<1e-4
assert abs(saved['fov']-actual_fov)<1e-4
assert not negative and not bad
spawn=meta['spawn']['position'];bounds=meta['bounds']
assert bounds['minX']<spawn[0]<bounds['maxX'] and bounds['minZ']<spawn[2]<bounds['maxZ']
for ob in meta['obstacles']:
    assert ob['minX']<ob['maxX'] and ob['minZ']<ob['maxZ']
    assert not (ob['minX']<=spawn[0]<=ob['maxX'] and ob['minZ']<=spawn[2]<=ob['maxZ'])
images=[i for i in bpy.data.images if i.source=='FILE']
assert all(i.packed_file or len(i.packed_files) for i in images)
# This verifies a 0.3m-radius avatar has a path from spawn to several room regions.
step=.1;radius=.30
def safe(x,z):
    if x<bounds['minX']+radius or x>bounds['maxX']-radius or z<bounds['minZ']+radius or z>bounds['maxZ']-radius:return False
    return not any(o['minX']-radius<x<o['maxX']+radius and o['minZ']-radius<z<o['maxZ']+radius for o in meta['obstacles'])
start=(round(spawn[0]/step),round(spawn[2]/step));seen={start};stack=[start]
while stack:
    x,z=stack.pop()
    for nxt in [(x-1,z),(x+1,z),(x,z-1),(x,z+1)]:
        if nxt not in seen and safe(nxt[0]*step,nxt[1]*step):seen.add(nxt);stack.append(nxt)
assert min(z for x,z in seen)*step<-3.0, 'Rear lounge route is not reachable'
result=dict(scene=room,objects=len(scene.objects),meshObjects=mesh_objects,sourcePolygons=polygons,negativeTransforms=negative,nonFiniteGeometry=bad,packedImageCount=len(images),cameraFov=actual_fov,sourceAspect=scene.render.resolution_x/scene.render.resolution_y,spawnClear=True,reachableNavigationCells=len(seen),navigationCellMetres=step,navigationRadiusMetres=radius,reachableX=[min(x for x,z in seen)*step,max(x for x,z in seen)*step],reachableZ=[min(z for x,z in seen)*step,max(z for x,z in seen)*step],limitations=['Metadata path sampling verifies conservative rectangles, not a physical collision simulation. Browser walkthrough remains separate.'])
(model/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print('SOURCE_VERIFIED',json.dumps(result),flush=True)
