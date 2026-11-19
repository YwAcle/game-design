"""Align the source/render to the existing viewer's preset-camera clamp; no rebake."""
import bpy, sys, json, runpy
from pathlib import Path
from mathutils import Vector
here=Path(__file__).resolve().parent
room=sys.argv[sys.argv.index('--')+1];model=here.parent/room;root=here.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(model/(room+'.blend')))
scene=bpy.context.scene;cam=scene.camera
meta_path=root/'scene-assets'/room/'metadata.json';meta=json.loads(meta_path.read_text(encoding='utf8'))
view=meta['cameras'][0]
view['position'][2]=meta['bounds']['maxZ']-.15
cam.location=Vector((view['position'][0],-view['position'][2],view['position'][1]))
t=view['target'];target=Vector((t[0],-t[2],t[1]));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
if room=='hufflepuff':
    for ob in meta['obstacles'][-8:]:
        x=(ob['minX']+ob['maxX'])/2;z=(ob['minZ']+ob['maxZ'])/2
        ob.update(minX=x-.29,maxX=x+.29,minZ=z-.29,maxZ=z+.29)
meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
scene.render.filepath=str(root/'previews'/('blender-'+room+'.png'))
bpy.ops.wm.save_as_mainfile(filepath=str(model/(room+'.blend')))
bpy.ops.render.render(write_still=True)
runpy.run_path(str(model/'verify_source.py'),run_name='__main__')
print('VIEWER_CAMERA_ALIGNED',room,view['position'],flush=True)
