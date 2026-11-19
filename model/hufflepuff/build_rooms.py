"""Original stylized study interiors; no extracted game geometry or textures.
Run Blender --background --python build_rooms.py -- ravenclaw|hufflepuff [draft].
"""
import bpy, sys, os, math, random, json, shutil, bmesh
from math import sin,cos,pi
from pathlib import Path
from mathutils import Vector, Matrix
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import geometry as g
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['ravenclaw']
ID=args[0];DRAFT='draft' in args
ROOT=HERE.parents[1]
MODEL=ROOT/'model'/ID;ASSETS=ROOT/'scene-assets'/ID
MODEL.mkdir(parents=True,exist_ok=True);ASSETS.mkdir(parents=True,exist_ok=True)
random.seed(71 if ID=='ravenclaw' else 93)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.samples=20;S.cycles.use_denoising=True
try:
    p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
    for d in p.devices:d.use=d.type=='CUDA'
    S.cycles.device='GPU' if any(d.type=='CUDA' for d in p.devices) else 'CPU'
except Exception:S.cycles.device='CPU'
S.cycles.max_bounces=6;S.cycles.diffuse_bounces=4
S.render.resolution_x=1440;S.render.resolution_y=900;S.render.resolution_percentage=70 if DRAFT else 100
S.world.color=(.18,.20,.25) if ID=='ravenclaw' else (.22,.18,.10)
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=-.35 if ID=='ravenclaw' else -.5
def paint(name,tex,col,rough=.8,metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1)
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    tc=n.new('ShaderNodeTexCoord');im=n.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(MODEL/'textures'/tex),check_existing=True);im.projection='BOX';im.projection_blend=.16;l.new(tc.outputs['Generated'],im.inputs['Vector']);l.new(im.outputs['Color'],p.inputs['Base Color'])
    if tex=='ivory.jpg' and ID=='ravenclaw':
        tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(.65,.63,.60,1);l.new(im.outputs['Color'],tint.inputs[1]);l.new(tint.outputs[0],p.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.17;bump.inputs['Distance'].default_value=.035;l.new(im.outputs['Color'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal']);return m
def image_mat(name,filename,portrait=False):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links
    im=n.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(MODEL/'textures'/filename),check_existing=True)
    tc=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');com=n.new('ShaderNodeCombineXYZ');l.new(tc.outputs['Generated'],sep.inputs[0]);l.new(sep.outputs['X'],com.inputs['X']);l.new(sep.outputs['Z' if portrait else 'Y'],com.inputs['Y']);l.new(com.outputs[0],im.inputs['Vector']);l.new(im.outputs[0],n.get('Principled BSDF').inputs['Base Color']);return m
ivory=paint('Hand-brushed limestone','ivory.jpg',(.63,.59,.48));stone=paint('Warm ochre cut stone','stone.jpg',(.43,.36,.24));wood=paint('Oiled oak streaks','wood.jpg',(.28,.15,.07));blue=paint('Indigo woven velvet','blue.jpg',(.09,.16,.28));yellow=paint('Ochre linen upholstery','yellow.jpg',(.51,.34,.08));green=paint('Deep botanical leaves','green.jpg',(.09,.16,.035))
dark=g.material('Ink-dark bevel outlines',(.025,.029,.035),rough=.85);gold=g.material('Dulled antique brass',(.31,.19,.065) if ID=='ravenclaw' else (.48,.30,.10),(.48,.34,.12) if ID=='ravenclaw' else (.72,.53,.22),rough=.65 if ID=='ravenclaw' else .46,metal=0 if ID=='ravenclaw' else .52)
cream=g.material('Linen stitch and marble highlight',(.72,.67,.51),rough=.92);navy=g.material('Deep midnight blue',(.018,.037,.082),rough=.9);pale=g.material('Pale blue cushion',(.24,.48,.57),(.38,.58,.63));copper=g.material('Copper planters',(.32,.14,.045),(.55,.28,.09),rough=.5,metal=.5)
leaflight=g.material('New leaf edges',(.18,.26,.055),(.32,.37,.095));paper=g.material('Antique book paper',(.73,.65,.45),rough=1);red=g.material('Old red leather',(.24,.06,.035));black=g.material('Fireplace soot',(.021,.018,.014));glow=g.material('Windows | soft daylight',(.64,.78,1) if ID=='ravenclaw' else (1,.76,.31),emission=1.5);fire=g.material('Lamps | warm flame',(1,.5,.065),emission=4)
def group(name):g.collection(name)
def ring(name,c,r,mat,thick=.025,axis='Z',n=64):
    pts=[]
    for i in range(n):
        a=i*2*pi/n;v=(r*cos(a),r*sin(a),0) if axis=='Z' else (r*cos(a),0,r*sin(a));pts.append(tuple(c[j]+v[j] for j in range(3)))
    return g.path(name,pts,thick,mat,True)
def local(c,x,y,z,a=0):return g.tf(c,x,y,z,a)
def rounded(name,c,dim,mat,b=.10,a=0):return g.box(name,c,dim,mat,b,a)
def book(c,w=.28,h=.42,d=.1,a=0,mat=None,standing=False):
    mat=mat or random.choice([red,blue,green,wood])
    if standing:
        rounded('Book pages',c,(w,d,h),paper,.007,a)
        for x in [-w/2,w/2]:rounded('Leather cover',local(c,x,0,0,a),(.025,d+.045,h+.035),mat,.009,a)
        rounded('Leather spine',local(c,0,-d/2,0,a),(w+.03,.025,h+.02),mat,.01,a)
        for z in [-h*.36,h*.36]:g.box('Gold spine bands',local(c,0,-d/2-.016,z,a),(w*.85,.006,.015),gold,0,a)
    else:
        rounded('Book page block',c,(w,h,d),paper,.006,a)
        for z in [-d/2,d/2]:rounded('Leather cover',local(c,0,0,z,a),(w+.035,h+.035,.02),mat,.008,a)
        g.box('Book clasp',local(c,w*.3,0,d/2+.016,a),(.06,.10,.012),gold,.002,a)
def teacup(c):
    g.lathe('Porcelain teacup',c,[(0,0),(.11,0),(.13,.04),(.15,.17),(.14,.19),(.125,.18),(.11,.05),(.02,.035)],cream,n=24)
    o=ring('Cup handle',(c[0]+.15,c[1],c[2]+.11),.073,gold,.014,axis='Y',n=20)
    g.cyl('Saucer',(c[0],c[1],c[2]-.015),.21,.02,cream,32)
def vase(c,h=.5,mat=wood):return g.lathe('Shaped vessel',c,[(0,0),(.19,0),(.22,.07),(.26,h*.45),(.15,h*.8),(.14,h),(.12,h),(.12,h*.8),(.02,.06)],mat,24)
def portrait(c,w,h,index=0):
    tex=image_mat('Original allegorical portrait '+str(index),f'portrait{index%4}.png',True)
    g.box('Canvas',c,(w,.055,h),tex)
    for dx in [-w/2,w/2]:rounded('Dark carved portrait frame',(c[0]+dx,c[1]-.05,c[2]),(.10,.13,h+.15),wood,.018)
    for dz in [-h/2,h/2]:rounded('Dark carved portrait frame',(c[0],c[1]-.05,c[2]+dz),(w+.12,.13,.10),wood,.018)
    for dx in [-w/2+.055,w/2-.055]:g.box('Gold inner frame',(c[0]+dx,c[1]-.125,c[2]),(.018,.018,h-.05),gold)
    for dz in [-h/2+.055,h/2-.055]:g.box('Gold inner frame',(c[0],c[1]-.125,c[2]+dz),(w-.05,.018,.018),gold)
def shelf(c,w=1.8,h=2.5):
    rounded('Book cabinet back',(c[0],c[1]+.15,c[2]+h/2),(w,.18,h),wood,.025)
    for x in [-w/2,w/2]:rounded('Carved cabinet pillar',(c[0]+x,c[1],c[2]+h/2),(.13,.65,h+.15),wood,.03)
    for z in [0,.65,1.3,1.95,h]:
        rounded('Cabinet shelf',(c[0],c[1]-.04,c[2]+z),(w+.18,.70,.10),wood,.025)
        if z<h-.1:
            xx=-w/2+.15
            while xx<w/2-.1:
                ww=random.uniform(.1,.2);hh=random.uniform(.31,.54);book((c[0]+xx,c[1]-.22,c[2]+z+.10+hh/2),ww,hh,.23,standing=True);xx+=ww+.055
    rounded('Cabinet cornice',(c[0],c[1],c[2]+h+.13),(w+.35,.78,.13),gold,.025)
def leaf(name,a,b,width,mat=green):
    a=Vector(a);b=Vector(b);v=b-a;side=v.cross(Vector((0,0,1)))
    if side.length<.01:side=Vector((1,0,0))
    side.normalize();mid=a+v*.52+Vector((0,0,.07));vs=[a,mid+side*width,mid+Vector((0,0,.045)),mid-side*width,b];return g.mesh(name,[tuple(v) for v in vs],[(0,1,2),(1,4,2),(4,3,2),(3,0,2)],mat)
def plant(c,scale=1,hanging=False):
    vase(c,.38*scale,copper if hanging else wood)
    for i in range(15):
        a=i*2.399;length=random.uniform(.4,.8)*scale
        base=Vector(c)+Vector((0,0,.32*scale));tip=base+Vector((cos(a)*length*.75,sin(a)*length*.75,length*.75))
        stem=base+(tip-base)*.55;g.path('Plant stem',[base,stem,tip],.012*scale,green)
        leaf('Broad lance-shaped leaf',stem,tip+Vector((cos(a)*.25,sin(a)*.25,-.07)),.15*scale,leaflight if i%4==0 else green)
def vine(c,length=2.0,phase=0):
    pts=[(c[0]+sin(i*.6+phase)*.12,c[1]-.03*cos(i*.8),c[2]-length*i/20) for i in range(21)];g.path('Drooping vine',pts,.018,green)
    for i in range(1,20):
        p=Vector(pts[i]);s=1 if i%2 else -1;t=p+Vector((s*random.uniform(.19,.36),-.08,-.08));leaf('Heart-shaped ivy leaf',p,t,.11,leaflight if i%3==0 else green)
def stonearch(c,r,thick=.25,start=0,end=pi,n=15):
    for i in range(n):
        a=start+(end-start)*(i+.5)/n
        o=g.box('Separate arch voussoir',(c[0]+r*cos(a),c[1],c[2]+r*sin(a)),(2*r*sin((end-start)/n/2)*.95,.38,thick),ivory if ID=='ravenclaw' else stone,.018);o.rotation_euler.y=-a+pi/2
def circle_window(x,y,z,r=.66):
    # Actual bored opening in the wall panel, with a recessed luminous exterior.
    wall=g.box('Circular window masonry',(x,y,z),(2.8,.45,2.4),stone,.012);wall.data=wall.data.copy()
    cutter=g.cyl('Window opening cutter',(x,y,z),r,1.2,dark,48);cutter.rotation_euler.x=pi/2
    bpy.context.view_layer.objects.active=wall;mod=wall.modifiers.new('Circular opening','BOOLEAN');mod.object=cutter;mod.operation='DIFFERENCE';bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
    disk=g.cyl('Windows | circular sky',(x,y+.3,z),r,.02,glow,48);disk.rotation_euler.x=pi/2
    stonearch((x,y-.16,z),r+.10,.23,0,2*pi,17)
    rounded('Window plant sill',(x,y-.18,z-r),(.95,.60,.10),wood,.03);plant((x,y-.30,z-r+.05),.60)
def pointed_panel(c,w,h,mat):
    pts=[(-w/2,0),(w/2,0),(w/2,h*.65),(w*.32,h*.83),(0,h),(-w*.32,h*.83),(-w/2,h*.65)]
    return g.mesh('Recessed pointed panel',[g.tf(c,x,0,z) for x,z in pts],[tuple(range(len(pts)))],mat)
def window_bay(x,y,w=2.6,h=6.7):
    g.portal('Lancet masonry bay',(x,y,0),w*.70,h,w,8.1,.45,ivory,cream)
    pointed_panel((x,y+.3,.55),w*.65,h-.7,glow)
    g.beam('Slender window mullion',(x,y-.03,.55),(x,y-.03,h-.4),.045,gold)
    for z in [1.0,1.9,2.8,3.7,4.6,5.5]:
        g.beam('Lead transom',(x-w*.3,y-.04,z),(x+w*.3,y-.04,z),.025,gold)
        for s in [-1,1]:g.beam('Diamond lead tracery',(x,y-.05,z-.38),(x+s*w*.29,y-.05,z+.40),.025,gold)
    curtain((x-w*.35,y-.25,.8),.65,h-.8,1);curtain((x+w*.35,y-.25,.8),.65,h-.8,-1)
def curtain(c,w,h,sign):
    vs=[];fs=[];nx=9;nz=18
    for j in range(nz+1):
        t=j/nz;gather=sin(t*pi)*.36
        for i in range(nx+1):
            u=i/nx;xx=(u-.5)*w*(.55+.45*abs(t-.5)*2)+sign*gather
            vs.append((c[0]+xx,c[1]+.065*cos(u*8*pi),c[2]+t*h))
    for j in range(nz):
        for i in range(nx):a=j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
    g.mesh('Blue pleated star curtain',vs,fs,blue,True)
    g.path('Curtain gold tie',[(c[0]-w*.33+sign*.3,c[1]-.08,c[2]+h*.48),(c[0]+w*.3+sign*.3,c[1]-.08,c[2]+h*.48)],.028,gold)
    for i in range(13):
        u=random.random();t=random.random();xx=(u-.5)*w*(.55+.45*abs(t-.5)*2)+sign*sin(t*pi)*.36
        star_mesh((c[0]+xx,c[1]-.085,c[2]+t*h),.045,cream,axis='Y')
def star_mesh(c,r,mat,axis='Z',points=5):
    pts=[]
    for i in range(points*2):
        a=i*pi/points;rr=r if i%2==0 else r*.4;v=(rr*cos(a),rr*sin(a),0) if axis=='Z' else (rr*cos(a),0,rr*sin(a));pts.append(tuple(c[j]+v[j] for j in range(3)))
    g.mesh('Inlaid star',pts,[tuple(range(len(pts)))],mat)
def column(x,y,h=8.2):
    g.lathe('Carved limestone pillar',(x,y,0),[(.46,0),(.46,.16),(.38,.22),(.33,.48),(.31,.7),(.29,1.0),(.29,h-.65),(.39,h-.57),(.43,h-.39),(.48,h-.26),(.48,h)],ivory,24)
    for z in [.2,.60,2.2,h-.52,h-.29]:ring('Brass pillar moulding',(x,y,z),.35 if z<3 else .43,gold,.035, n=32)
    for k in range(8):
        a=k*2*pi/8;g.path('Fine pillar fluting',[(x+.298*cos(a),y+.298*sin(a),2.35),(x+.298*cos(a),y+.298*sin(a),h-.7)],.007,cream)
def eagle(c,scale=1):
    g.sphere('Eagle breast',c,(.15*scale,.09*scale,.25*scale),gold)
    g.sphere('Eagle head',(c[0],c[1]-.03,c[2]+.27*scale),(.12*scale,.10*scale,.12*scale),gold)
    g.mesh('Eagle beak',[(c[0]-.04*scale,c[1]-.1,c[2]+.26*scale),(c[0]+.04*scale,c[1]-.1,c[2]+.26*scale),(c[0],c[1]-.21*scale,c[2]+.19*scale)],[(0,1,2)],cream)
    for sign in [-1,1]:
        for j in range(7):
            base=Vector((c[0]+sign*.1*scale,c[1],c[2]+.08*scale));tip=Vector((c[0]+sign*(.34+j*.057)*scale,c[1]+.015,c[2]+(.12+j*.095)*scale));leaf('Sculpted eagle wing feather',base,tip,.07*scale,gold)
def sconce(c):
    eagle(c,.70);g.lathe('Wall candle cup',(c[0],c[1]-.1,c[2]+.28),[(.04,0),(.13,.04),(.16,.10)],gold)
    g.cyl('Ivory candle',(c[0],c[1]-.1,c[2]+.46),.05,.28,cream,12);g.sphere('Lamps | flame',(c[0],c[1]-.1,c[2]+.65),(.04,.04,.12),fire,12,6);g.point('Candle light',(c[0],c[1]-.45,c[2]+.7),32,(1,.66,.25),.2)
def armillary(c):
    existing=set(bpy.context.scene.objects)
    g.lathe('Armillary turned foot',c,[(0,0),(.33,0),(.34,.07),(.22,.13),(.12,.23),(.08,.48),(.18,.55)],gold,32)
    center=(c[0],c[1],c[2]+1.15)
    for i in range(4):
        o=ring('Nested celestial armillary ring',center,.56+.045*i,gold,.025,axis='Y');o.matrix_world=Matrix.Translation(Vector(center))@Matrix.Rotation(i*pi/4,4,'Z')@Matrix.Translation(-Vector(center))
    ring('Armillary equator',center,.66,gold,.023)
    g.beam('Tilted polar axis',(c[0]-.3,c[1],c[2]+.45),(c[0]+.3,c[1],c[2]+1.88),.035,gold)
    g.sphere('Celestial blue earth',center,(.14,.14,.14),pale,20,12)
    for k in range(24):
        a=k*2*pi/24;g.box('Zodiac etched mark',(c[0]+.665*cos(a),c[1]+.665*sin(a),c[2]+1.15),(.045,.012,.015),cream,0,a)
    bpy.context.view_layer.update()
    origin=Vector(c);transform=Matrix.Translation(origin)@Matrix.Scale(.63,4)@Matrix.Translation(-origin)
    for obj in set(bpy.context.scene.objects)-existing:obj.matrix_world=transform@obj.matrix_world
def chaise(c,a=0,huffle=False,length_override=None):
    prior=set(S.objects)
    upholstery=yellow if huffle else blue;trim=wood if huffle else gold;length=length_override or (3.7 if huffle else 3.3);depth=1.25
    rounded('Scroll sofa lower frame',local(c,0,0,.47,a),(length,depth,.28),wood,.09,a)
    rounded('Sofa gold lower rail',local(c,0,-depth/2-.025,.55,a),(length,.07,.09),trim,.025,a)
    for x in [-length*.40,length*.40]:
        for y in [-.42,.42]:
            g.beam('Swept couch leg',local(c,x,y,.08,a),local(c,x*.95,y,.5,a),.15,wood)
    for j in (range(3) if length>2 else [1]):
        x=(j-1)*length*.27;rounded('Separate upholstered seat',local(c,x,-.02,.80,a),(length*(.29 if length>2 else .8),1.1,.30),upholstery,.12,a)
        g.path('Seat piping',[local(c,x-length*.14,-.57,.87,a),local(c,x+length*.14,-.57,.87,a)],.012,cream if huffle else gold)
        if huffle:
            rounded('Tufted high sofa back',local(c,x,.48,1.38,a),(length*(.30 if length>2 else .9),.28,1.12),upholstery,.11,a)
            for zz in [1.2,1.65]:
                for xx in [x-.23,x+.23]:g.sphere('Recessed tuft button',local(c,xx,.322,zz,a),(.035,.02,.035),gold,10,6)
            for xx in [x-.39,x+.39]:g.path('Back stitched welt',[local(c,xx,.316,.95,a),local(c,xx,.316,1.83,a)],.011,cream)
    for sign in [-1,1]:
        x=sign*(length/2-.07);rounded('Raised scroll arm bolster',local(c,x,0,1.14,a),(.43,1.3,.63),upholstery,.18,a)
        pts=[]
        for k in range(48):
            t=k/47*2.2*pi;rr=.29*(1-k/56);pts.append(local(c,x+sign*rr*cos(t),-.69,1.18+rr*sin(t),a))
        g.path('Carved spiral sofa arm',pts,.055,trim)
        g.path('Armrest gold piping',[local(c,x-.18,-.64,1.40,a),local(c,x-.18,.60,1.40,a)],.023,trim)
    for x in ([-length*.28,length*.27] if length>2 else [0]):
        o=rounded('Plump loose patterned cushion',local(c,x,.29,1.13 if not huffle else 1.26,a),(.68,.28,.66),pale if not huffle else cream,.13,a);o.rotation_euler.x=-.16
        for j in [-.22,0,.22]:g.path('Cushion hand-stitched stripe',[local(c,x+j,.125,.99 if huffle else .88,a),local(c,x+j,.125,1.5 if huffle else 1.39,a)],.013,blue if not huffle else yellow)
    factor=.84 if huffle else .88
    bpy.context.view_layer.update()
    origin=Vector(c);transform=Matrix.Translation(origin)@Matrix.Diagonal((factor,factor,.92 if huffle else .94,1))@Matrix.Translation(-origin)
    for obj in set(S.objects)-prior:obj.matrix_world=transform@obj.matrix_world
def table(c,r=1.55,h=.85,mat=wood):
    g.cyl('Octagonal carved tabletop',(c[0],c[1],c[2]+h),r,.16,mat,8);g.cyl('Table rim inset',(c[0],c[1],c[2]+h+.09),r-.09,.025,gold if ID=='ravenclaw' else wood,8);g.cyl('Inset table wood',(c[0],c[1],c[2]+h+.11),r-.13,.025,wood,8)
    for x in [-r*.60,r*.60]:
        for y in [-r*.60,r*.60]:g.beam('Tapered table leg',(c[0]+x*1.08,c[1]+y*1.08,c[2]+.05),(c[0]+x,c[1]+y,c[2]+h-.05),.13,wood)
def statue(c):
    g.cyl('Statue stepped plinth',(c[0],c[1],.25),.72,.5,ivory,8);g.cyl('Statue base moulding',(c[0],c[1],.55),.65,.15,cream,8)
    # A continuous fluted robe, asymmetrical bell sleeves, sculpted head and crown.
    vs=[];fs=[];n=48
    for z,r in [(.64,.58),(1.0,.54),(1.8,.40),(2.4,.30),(2.9,.32),(3.3,.49),(3.55,.33)]:
        for i in range(n):
            a=i*2*pi/n;rr=r*(1+.07*cos(a*12));vs.append((c[0]+rr*cos(a),c[1]+rr*.67*sin(a),z))
    for j in range(6):
        for i in range(n):a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
    fs+=[tuple(reversed(range(n))),tuple(range(6*n,7*n))];g.mesh('Sculpted fluted scholar robe',vs,fs,ivory,True)
    g.sphere('Sculpted neck',(c[0],c[1],3.62),(.12,.12,.20),ivory)
    g.sphere('Sculpted face',(c[0],c[1]-.01,3.94),(.23,.19,.33),cream,24,14)
    g.sphere('Sculpted nose',(c[0],c[1]-.20,3.94),(.04,.055,.07),ivory)
    for x in [-.085,.085]:g.path('Quiet carved eye',[(c[0]+x-.025,c[1]-.181,4.015),(c[0]+x+.025,c[1]-.181,4.02)],.009,dark)
    g.path('Carved mouth',[(c[0]-.05,c[1]-.18,3.83),(c[0]+.05,c[1]-.18,3.83)],.008,stone)
    for k in range(14):
        a=k*2*pi/14
        if sin(a)<-.35:continue
        pts=[(c[0]+.25*cos(a),c[1]+.21*sin(a),4.12-j*.09) for j in range(random.randint(4,9))];g.path('Long carved hair lock',pts,.035,stone)
    for sign in [-1,1]:
        a=(c[0]+sign*.32,c[1],3.35);b=(c[0]+sign*.66,c[1]-.10,2.94);g.beam('Sculpted upper sleeve',a,b,.30,ivory)
        hand=(c[0]+sign*.53,c[1]-.35,3.0);g.beam('Sculpted lower sleeve',b,hand,.23,ivory);g.sphere('Carved hand',hand,(.10,.10,.13),cream)
        g.path('Trailing robe sleeve',[(c[0]+sign*.52,c[1],3.16),(c[0]+sign*.8,c[1]+.02,2.05),(c[0]+sign*.53,c[1]-.13,2.18),(c[0]+sign*.44,c[1]-.18,2.9)],.08,ivory)
    ring('Scholar diadem',(c[0],c[1],4.18),.25,gold,.025)
    for k in range(5):
        x=(k-2)*.09;g.mesh('Diadem pointed leaf',[(c[0]+x-.04,c[1]-.19,4.18),(c[0]+x+.04,c[1]-.19,4.18),(c[0]+x,c[1]-.19,4.36-abs(k-2)*.035)],[(0,1,2)],gold)
    g.beam('Scholar wand',(c[0]+.52,c[1]-.37,2.99),(c[0]+.88,c[1]-.37,3.66),.026,gold)
def ceiling(raven):
    z=8.15 if raven else 5.7
    g.box('Continuous enclosed ceiling',(0,-1,z),(14.4,15,.25),navy if raven else wood)
    for y in [-6,-3,0,3,5.5]:g.box('Heavy ceiling beam',(0,y,z-.24),(14.0,.24,.30),wood,.04)
    if raven:
        for i in range(90):star_mesh((random.uniform(-6.7,6.7),random.uniform(-7.6,5.7),z-.14),random.uniform(.025,.065),gold)
    else:
        for x in [-6,-3,0,3,6]:g.box('Crossed ceiling beam',(x,-1,z-.23),(.20,14.5,.28),wood,.035)

from art_refinement import install
install(globals())

group('01 floor')
g.box('Floor foundation',(0,-1,-.15),(14.4,15.0,.3),stone)
if ID=='ravenclaw':
    for x in range(-7,7):
        for y in range(-8,6):g.box('Large pale stone floor slab',(x+.5,y+.5,.015),(.986,.986,.045),ivory,.012)
else:
    for j in range(32):
        y=-8+j*.44
        for k in range(7):
            x=-7+k*2.2+(1.1 if j%2 else 0);g.box('Individual honey oak floorboard',(x,y,.015),(2.18,.426,.045),wood,.008)
rug=image_mat('Original engraved textile medallion','rug.png');g.cyl('Large circular woven rug',(0,-.8,.058),5.3 if ID=='ravenclaw' else 4.8,.024,rug,96)
ring('Rug stitched outer binding',(0,-.8,.079),5.25 if ID=='ravenclaw' else 4.75,gold if ID=='ravenclaw' else cream,.018)

if ID=='ravenclaw':
    group('02 architecture')
    for x in [-5.6,-2.8]:window_bay(x,5.8)
    g.portal('Statue library alcove',(0,5.8,0),2.6,6.9,2.8,8.1,.55,ivory,gold)
    g.box('Alcove rear blue shadow',(0,6.55,3.7),(2.7,.22,7.4),navy)
    g.portal('Right library doorway',(2.8,5.8,0),1.75,4.9,2.8,8.1,.55,ivory,cream)
    g.box('Library rear wall',(2.8,7.0,3.8),(2.6,.2,7.6),navy)
    g.box('Right solid wall',(5.6,5.8,4.05),(2.8,.45,8.1),ivory)
    for x in [-7,-4.2,-1.4,1.4,4.2,7]:column(x,5.43)
    for sign in [-1,1]:
        g.box('Side chamber wall',(sign*7.1,-1,4.1),(.35,13.9,8.2),ivory)
        for y in [-6,-2,2]:column(sign*6.85,y)
        g.box('Blue lower wall dado',(sign*6.85,-1,.7),(.20,13.7,1.4),blue)
        g.box('Dado brass rail',(sign*6.72,-1,1.43),(.08,13.7,.065),gold)
    g.box('Inferred entrance rear wall',(0,-8.25,4.1),(14.3,.3,8.2),ivory)
    g.box('Dado base',(0,5.49,.63),(14,.11,1.25),blue)
    for x in [-5.6,-2.8]:g.box('Window stone sill',(x,5.2,.65),(2.0,.72,.18),cream,.03)
    ceiling(True)
    group('03 furniture')
    chaise((-2.85,1.35,0),.15);chaise((3.1,.65,0),-.22)
    coffee_prior=set(S.objects)
    table((0,-1.35,0),1.10,.80);armillary((0,-1.15,.935))
    opened_book((-.45,-1.60,.97));book((.60,-1.83,1.02),.36,.48,.12,-.13,red);teacup((.72,-.97,.96))
    bpy.context.view_layer.update()
    for obj in set(S.objects)-coffee_prior:obj.matrix_world=Matrix.Translation(Vector((0,.70,0)))@obj.matrix_world
    table((-4.6,-2.4,0),.65,.75);teacup((-4.6,-2.4,.90))
    carved_cabinet((5.25,5.20,.05),2.3,2.5);shelf((0,6.02,.04),2.2,4.4);shelf((2.8,6.64,0),1.65,3.7)
    for x in [-5.6,-2.8]:table((x,4.4,0),.7,.70);book((x,4.38,.85),.4,.55,.12)
    group('04 details')
    statue((0,4.90,0));eagle((0,5.35,6.6),1.10)
    for x in [-6.7,-4.1,-1.45,1.45,4.18,6.8]:sconce((x,5.08,4.3))
    portrait((5.5,5.48,4.32),1.0,1.4,0);portrait((4.75,5.46,3.45),.55,.75,1)
    # Telescope and tabletop terrestrial globe.
    g.lathe('Telescope pivot',(5.8,4.98,2.71),[(.22,0),(.13,.08),(.08,.5)],gold)
    g.beam('Brass telescope body',(5.35,4.98,3.10),(6.35,5.0,3.55),.16,gold)
    for t in [0,.25,.75,1.0]:
        o=g.cyl('Telescope raised brass collar',(5.35+t,4.98,3.10+t*.45),.12,.07,gold,20);o.rotation_euler=(Vector((1,0,.45))).to_track_quat('Z','Y').to_euler()
    g.sphere('Desk celestial globe',(4.62,5.02,3.11),(.30,.30,.30),blue,32,16);ring('Globe brass meridian',(4.62,5.02,3.11),.34,gold,.02,axis='Y');g.lathe('Globe foot',(4.62,5.02,2.71),[(.20,0),(.15,.05),(.06,.18)],gold)
    for i in range(4):book((5.0,4.99,2.83+i*.1),.36,.48,.08,random.uniform(-.2,.2))
    # Inferred reading area behind primary camera remains furnished for walking.
    for x in [-4.8,4.8]:
        shelf((x,-7.8,.02),2.7,3.0);table((x,-5.6,0),.80,.8);book((x,-5.6,.94),.46,.62,.10)
    group('05 lighting')
    g.area('Cool window wash',(-4.5,4.8,5.2),(0,-1,1),1050,(.60,.76,1),4)
    g.area('Soft skylight',(0,-1,7.8),(0,0,0),1000,(.72,.80,1),7)
    g.area('Warm foreground fill',(0,-6,5.2),(0,3,2),650,(1,.82,.61),5)
    cam=g.camera('Main reference camera',(-.7,-7.6,4.3),(0,1.6,2.05),19)
    cams=[('星穹会客室',[-.7,4.3,7.6],[0,2.05,-1.6]),('天球仪与长榻',[4.7,2.8,4.6],[-.6,1.8,-.6]),('雕像与藏书',[-3.7,2.2,-2.6],[0,2.8,-4.9])]
    obs=[(-4.85,-1.10,-2.0,-.1),(1.1,4.85,-2.0,-.1),(-1.7,1.7,-.30,2.9),(-5.4,-3.8,1.5,3.2),(-.8,.8,-5.7,-4.2),(-6.3,-4.6,-5.6,-3.5),(-3.5,-2.0,-5.5,-3.5),(4.0,6.6,-5.7,-4.6),(-6.2,-3.5,4.7,7.9),(3.5,6.2,4.7,7.9)]
else:
    group('02 architecture')
    g.box('Low rounded chamber back base',(0,5.8,1.62),(14.0,.45,3.25),stone)
    for x in [-5.6,-2.8,0,2.8,5.6]:
        if x in [-5.6,0,5.6]:circle_window(x,5.8,4.40,.68)
        else:g.box('Upper chamber wall',(x,5.8,4.4),(2.8,.45,2.4),stone)
    for sign in [-1,1]:
        g.box('Chamber side stone',(sign*7.05,-1,2.8),(.45,14.0,5.6),stone)
        for y in [-5,-1,3]:
            g.box('Low side pilaster',(sign*6.8,y,1.5),(.45,.6,3.0),stone,.04)
            g.box('Pilaster capital',(sign*6.8,y,3.05),(.60,.82,.22),wood,.04)
    g.box('Inferred entrance back wall',(0,-8.2,2.8),(14.1,.4,5.6),stone)
    # Deliberately irregular masonry outlines, shallow relief, rather than noisy flat planes.
    for j in range(15):
        z=.25+j*.35
        for i in range(15):
            x=-6.8+i*.93+(j%2)*.42
            if z>3.3 and any(abs(x-w)<.9 for w in [-5.6,0,5.6]):continue
            if random.random()<.57:g.box('Raised irregular brick',(x,5.55,z),(random.uniform(.6,.9),.055,.30),stone,.018)
    for x in [-3.65,3.65]:
        stonearch((x,5.14,1.3),1.63,.38,0,pi,15)
        for xx in [x-1.62,x+1.62]:g.box('Door arch side stone',(xx,5.18,.68),(.38,.52,1.36),stone,.035)
        disk=g.cyl('Round oak barrel door',(x,5.30,1.49),1.30,.18,wood,48);disk.rotation_euler.x=pi/2
        ring('Door outer carved rim',(x,5.17,1.49),1.25,gold,.065,axis='Y');ring('Door inner oak rim',(x,5.13,1.49),1.12,wood,.055,axis='Y')
        for dx in [-.9,-.6,-.3,0,.3,.6,.9]:
            hh=math.sqrt(max(0,1.16**2-dx**2));g.path('Door plank groove',[(x+dx,5.09,1.49-hh),(x+dx,5.09,1.49+hh)],.011,dark)
        ring('Barrel door brass pull',(x+.12,5.04,1.44),.11,gold,.022,axis='Y')
    ceiling(False)
    # Arches on the reverse and side walls echo the rounded underground silhouette.
    for x in [-4,0,4]:stonearch((x,-7.96,1.0),1.65,.30,0,pi,14)
    group('03 furniture')
    chaise((-3.13,.48,0),.38,True);chaise((3.13,.70,0),-.32,True)
    chaise((-1.8,3.05,0),-.06,True,1.45)
    # Large pumpkin-shaped round upholstered tea pouffe.
    tea_prior=set(S.objects)
    g.lathe('Round yellow center pouffe',(0,-1.3,.10),[(0,0),(.75,0),(1.08,.15),(1.25,.52),(1.22,.88),(1.05,1.05),(.85,1.12),(0,1.12)],yellow,48)
    for k in range(18):
        a=k*2*pi/18;g.path('Pouffe stitched vertical seam',[(r*cos(a),-1.3+r*sin(a),.1+z) for r,z in [(1.0,.1),(1.24,.45),(1.23,.8),(1.05,1.05)]],.009,cream)
    ring('Pouffe upper piping',(0,-1.3,1.14),1.04,cream,.02)
    teacup((.10,-1.35,1.26));teacup((-.4,-1.17,1.26));book((.38,-.95,1.32),.32,.45,.1,.2)
    bpy.context.view_layer.update()
    tea_xform=Matrix.Translation(Vector((0,-.45,0)))@Matrix.Diagonal((.70,.70,.90,1))@Matrix.Translation(Vector((0,1.3,0)))
    for obj in set(S.objects)-tea_prior:obj.matrix_world=tea_xform@obj.matrix_world
    g.lathe('Small round footstool',(2,-2.5,0),[(0,0),(.43,.05),(.45,.35),(.49,.4),(.49,.50),(.43,.55),(0,.55)],yellow,32);ring('Footstool oak band',(2,-2.5,.24),.46,wood,.055)
    table((-4.8,-2.3,0),.70,.72);table((4.8,-2.0,0),.65,.83)
    teacup((-4.8,-2.3,.87));book((4.8,-2.05,.96),.4,.5,.1)
    carved_cabinet((5.9,4.80,.04),1.6,2.7);carved_cabinet((-5.9,4.80,.04),1.6,2.7)
    # Stone hearth, timber mantel and compact flame.
    g.box('Fireplace dark opening',(0,5.25,.85),(2.65,.5,1.7),black,.07)
    stonearch((0,4.97,.38),1.25,.25,0,pi,13)
    g.box('Hearth slab',(0,4.90,.13),(3.1,1.0,.23),ivory,.04)
    for x in [-1.5,1.5]:g.box('Carved oak mantel side',(x,5.0,1.18),(.24,.5,2.1),wood,.04)
    rounded('Wide oak fireplace mantel',(0,5.0,2.25),(3.5,.75,.19),wood,.05)
    for k in range(4):g.beam('Fireplace logs',(-.7+k*.35,4.93,.28),(-.45+k*.35,5.28,.32),.12,wood)
    for x in [-.45,-.15,.18,.47]:g.sphere('Lamps | small hearth flame',(x,4.99,.55),(.10,.08,.25),fire,12,8)
    group('04 details')
    portrait((0,5.5,3.17),.9,1.15,3)
    for x in [-1.45,1.45]:plant((x,4.93,2.36),.85)
    for x,y,sc in [(-5.4,2.8,1.5),(5.2,2.75,1.35),(-5,-3.5,1.4),(5.6,-3.7,1.4),(-6.1,-.2,1.2),(6.1,-.2,1.5),(-4.8,-6.6,1.5),(4.8,-6.6,1.5)]:plant((x,y,.04),sc)
    # Hanging copper bowls with chains, soil, leafy crowns, and trailing ivy.
    for x,y,z in [(-3.2,2.5,4.2),(3.1,2.7,4.3),(0,-.8,4.90)]:
        g.lathe('Hanging copper bowl',(x,y,z),[(0,0),(.15,.02),(.6,.26),(.80,.42),(.82,.48),(.75,.48),(.50,.24),(.03,.08)],copper,32)
        ring('Hanging planter rolled rim',(x,y,z+.46),.8,gold,.04)
        for k in range(3):
            a=k*2*pi/3;g.path('Planter suspension chain',[(x+.73*cos(a),y+.73*sin(a),z+.45),(x+.14*cos(a),y+.14*sin(a),5.65)],.017,gold)
        for k in range(6):
            a=k*2*pi/6;leaf('Planter broad crown leaf',(x,y,z+.4),(x+.65*cos(a),y+.65*sin(a),z+.7+random.random()*.2),.17,leaflight)
        for k in range(4):
            a=k*2*pi/4;vine((x+.65*cos(a),y+.65*sin(a),z+.45),(.28 if abs(x)<.01 else .6)+random.random()*.25,k)
    for x in [-6.5,-5.9,-4.9,-4.2,-2.2,-1.5,.8,1.4,2.0,4.2,4.8,6.3]:vine((x,5.33,5.48),random.uniform(.55,1.65),x)
    for k in range(100):
        x=random.uniform(-6.7,6.7);z=random.uniform(5.05,5.48);leaf('Dense ivy canopy',(x,5.34,z),(x+random.uniform(-.32,.32),5.16,z-random.uniform(.1,.32)),.16,leaflight if k%4==0 else green)
    for x in [-5.4,-3.8,-2.0,2.0,3.8,5.4]:vine((x,5.12,3.15),random.uniform(.4,.85),x)
    for x in [-6.72,6.72]:
        for y in [-6,-4,-2,0,2,4]:
            for k in range(5):leaf('Ceiling trailing side foliage',(x,y,5.39),(x+(-.35 if x>0 else .35),y+random.uniform(-.4,.4),4.9+random.random()*.4),.20,green)
    for x in [-5.8,5.8]:
        table((x,-5.9,0),.65,.75);book((x,-5.9,.90),.4,.55,.12)
    group('05 lighting')
    for x in [-5.6,0,5.6]:g.area('Golden circular window wash',(x,5.10,4.35),(x*.45,-1,.6),260,(1,.79,.39),1.5)
    g.area('Warm hanging ceiling light',(0,-1,5.4),(0,-1,0),480,(1,.80,.45),5)
    g.area('Gentle front fill',(0,-6,3.9),(0,2,1.4),360,(1,.88,.65),6)
    g.point('Hearth amber light',(0,4.6,.65),140,(1,.39,.09),.6)
    cam=g.camera('Main reference camera',(-.5,-7.65,3.9),(0,1.4,1.8),19)
    cams=[('暖阳植物客厅',[-.5,3.9,7.65],[0,1.8,-1.4]),('茶点与黄绒沙发',[5.6,2.45,3.9],[0,1.4,.2]),('圆窗与壁炉',[-4.2,2.8,-1.8],[0,2.6,-4.8])]
    obs=[(-5.2,-.9,-1.0,1.6),(.9,5.2,-1.0,1.6),(-2.7,-.9,-3.8,-2.3),(-1.3,1.3,.0,2.6),(1.45,2.55,1.9,3.1),(-5.6,-4.0,1.5,3.1),(4.0,5.6,1.2,2.8),(-1.8,1.8,-5.5,-4.4),(-6.7,-5,-5.5,-4.2),(5,6.7,-5.5,-4.2),(-6.3,-5.0,5,6.7),(5,6.3,5,6.7)]
    for x,y in [(-5.4,2.8),(5.2,2.75),(-5,-3.5),(5.6,-3.7),(-6.1,-.2),(6.1,-.2),(-4.8,-6.6),(4.8,-6.6)]:obs.append((x-.37,x+.37,-y-.37,-y+.37))
post_refine(globals())
S.camera=cam
# All curve outlines are editable in the source; export converts in a separate copy.
for im in bpy.data.images:
    if im.source=='FILE':im.pack()
S.render.image_settings.file_format='PNG';S.render.filepath=str(ROOT/'previews'/('blender-'+ID+('-draft' if DRAFT else '')+'.png'))
bpy.ops.wm.save_as_mainfile(filepath=str(MODEL/(ID+'.blend')))
meta=dict(id=ID,name='拉文克劳休息室' if ID=='ravenclaw' else '赫奇帕奇休息室',lighting='baked',background='#111827' if ID=='ravenclaw' else '#21180d',exposure=1.0,cameras=[dict(name=n,position=p,target=t) for n,p,t in cams],spawn=dict(position=[0,1.65,5.8],target=[0,1.65,-2]),bounds=dict(minX=-6.45,maxX=6.45,minZ=-4.95,maxZ=7.5),obstacles=[dict(minX=a,maxX=b,minZ=c,maxZ=d) for a,b,c,d in obs],artisticLimitations=['Original stylized reconstruction from the selected official promotional image; inferred reverse walls and dimensions.','Statue, portraits, textiles and foliage are original simplified geometry or illustrations, not game assets.','Fine hand-painted linework and sculptural complexity remain less detailed than the game reference.'])
meta['cameras'][0]['fov']=refined_fov
meta['bounds']=refined_bounds
if ID=='ravenclaw':
    meta['obstacles']=[dict(minX=a,maxX=b,minZ=c,maxZ=d) for a,b,c,d in [
        (-4.52,-1.18,-2.26,-.44),(1.41,4.79,-1.65,.35),(-1.20,1.20,-.55,1.85),
        (-4.4,-3.0,1.5,2.9),(-5.4,-3.8,1.5,3.2),(4.0,6.35,-4.25,-3.0),
        (-6.1,-4.5,-4.2,-2.8),(-3.55,-2.0,-4.8,-3.1),(-6.2,-3.5,4.7,7.9),(3.5,6.2,4.7,7.9)]]
else:
    meta['obstacles']=[dict(minX=a,maxX=b,minZ=c,maxZ=d) for a,b,c,d in [
        (-4.95,-1.32,-1.72,.75),(1.32,4.95,-1.86,.46),(-2.7,-.9,-3.8,-2.3),
        (-1.02,1.02,-.58,1.48),(1.45,2.55,1.9,3.1),(-5.6,-4.0,1.5,3.1),(4.0,5.6,1.2,2.8),
        (-6.35,-4.8,-3.9,-2.65),(4.8,6.35,-3.9,-2.65),(-6.3,-5,5,6.7),(5,6.3,5,6.7)]]
    for x,y in [(-5.4,2.8),(5.2,2.75),(-5,-3.5),(5.6,-3.7),(-6.1,-.2),(6.1,-.2),(-4.8,-6.6),(4.8,-6.6)]:
        meta['obstacles'].append(dict(minX=x-.29,maxX=x+.29,minZ=-y-.29,maxZ=-y+.29))
meta['referenceAspect']=16/9
meta['revision']='sculpture-curved-enclosure-v2'
meta['cameras'][1]['fov']=52
meta['cameras'][2]['fov']=48
json.dump(meta,open(ASSETS/'metadata.json','w',encoding='utf8'),ensure_ascii=False,indent=2)
bpy.ops.render.render(write_still=True)
print('ROOM_BUILD_COMPLETE',ID,len(S.objects),flush=True)
