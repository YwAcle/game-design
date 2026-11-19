"""Original interiors inspired by the selected official promotional references.
Blender 5.x; run --background --python build_scene.py. Units: metres; Z up.
"""
import bpy,math,random,sys,os,json,bmesh
from pathlib import Path
from math import sin,cos,pi,sqrt
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));import geometry as g
ID=HERE.name;ROOT=HERE.parent.parent;ASSETS=ROOT/'scene-assets'/ID
random.seed(163 if ID=='potions' else 171)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for x in list(bpy.data.materials):bpy.data.materials.remove(x)
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.samples=int(os.environ.get('SCENE_SAMPLES','16'));S.cycles.use_denoising=True
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
 for d in p.devices:d.use=d.type=='CUDA'
 S.cycles.device='GPU' if any(d.type=='CUDA' for d in p.devices) else 'CPU'
except Exception:S.cycles.device='CPU'
S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=int(os.environ.get('SCENE_PERCENT','100'))
S.world.color=(.05,.045,.04);S.view_settings.view_transform='AgX';S.view_settings.exposure=-.20 if ID=='potions' else -.25
def painted(name,color,texture=None):
 m=g.material(name,color,rough=.85)
 if texture:
  nt=m.node_tree;n=nt.nodes;l=nt.links;t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(HERE/'textures'/texture),check_existing=True);t.projection='BOX';t.projection_blend=.15
  tc=n.new('ShaderNodeTexCoord')
  if 'pattern' in texture:
   mult=n.new('ShaderNodeVectorMath');mult.operation='SCALE';mult.inputs[3].default_value=3.2;l.new(tc.outputs['Generated'],mult.inputs[0]);l.new(mult.outputs[0],t.inputs[0])
  else:l.new(tc.outputs['Generated'],t.inputs[0])
  mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.62;mix.inputs[2].default_value=(*color,1);l.new(t.outputs[0],mix.inputs[1]);l.new(mix.outputs[0],n.get('Principled BSDF').inputs['Base Color'])
 return m
stone=[painted('Ashlar stone %02d'%i,(.32+i*.016,.29+i*.014,.245+i*.013),'stone.jpg') for i in range(7)]
warmstone=[painted('Ochre limestone %02d'%i,(.58+i*.025,.42+i*.018,.29+i*.014),'stone.jpg') for i in range(6)]
wood=painted('Hand brushed dark walnut',(.36,.20,.12),'wood.jpg');woodlight=painted('Hand brushed honey oak',(.60,.34,.19),'wood.jpg')
seam=g.material('Deep seams',(.045,.028,.023));iron=g.material('Blackened iron',(.07,.062,.061),rough=.54,metal=.62)
bronze=g.material('Aged warm brass',(.38,.25,.10),rough=.5,metal=.6);gold=g.material('Faded textile gold',(.51,.32,.10),rough=.8)
burgundy=painted('Claret velvet',(.41,.065,.09),'cloth.jpg');pattern=painted('Gold vine claret brocade',(.62,.20,.22),'cloth-pattern.jpg');teal=painted('Ink blue brocade',(.12,.32,.33),'teal-pattern.jpg')
canopy=painted('Deep wine canopy velvet',(.70,.16,.22),'cloth.jpg');canopypattern=painted('Deep wine canopy brocade',(.70,.20,.24),'cloth-pattern.jpg')
for m in [canopy,canopypattern]:
 for n in m.node_tree.nodes:
  if n.type=='MIX_RGB':n.inputs[0].default_value=1
 m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=1
 m.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.12
amber=g.material('Burnt sienna upholstery',(.38,.14,.065),(.53,.23,.11),rough=.95)
parchment=painted('Stained parchment',(.71,.58,.35),'paper.jpg');ink=g.material('Faded ink',(.14,.087,.048));cream=g.material('Glazed ivory crockery',(.59,.52,.39),rough=.4)
crystal=g.material('Crystal translucent shell',(.46,.44,.57),rough=.16,emission=.12)
mist=g.material('Crystal soft mist core',(.38,.35,.48),rough=.65,emission=.18)
crystalglint=g.material('Crystal soft glint',(.77,.72,.82),rough=.3,emission=.20)
for mat,alpha in [(crystal,.28),(mist,.42),(crystalglint,.36)]:
 mat.diffuse_color=(*mat.diffuse_color[:3],alpha);mat.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value=alpha
 if hasattr(mat,'surface_render_method'):mat.surface_render_method='DITHERED'

window=g.material('Warm overcast window',(.68,.55,.34),rough=1,emission=1.25)
glow=g.material('Candle flame',(.95,.46,.09),emission=4)
pottery=[g.material('Apothecary vessel %02d'%i,tuple(v*.39 for v in c),tuple(v*.54 for v in c),rough=.7) for i,c in enumerate([(.21,.23,.12),(.27,.17,.105),(.31,.27,.15),(.12,.22,.17),(.36,.32,.24),(.16,.22,.24)])]
def box(*a,**k):return g.box(*a,**k)
def path(*a,**k):return g.path(*a,**k)
def ring(name,loc,r,mat,t=.025,n=32):return path(name,[(loc[0]+r*cos(i*2*pi/n),loc[1]+r*sin(i*2*pi/n),loc[2]) for i in range(n)],t,mat,True)
def uv_mesh(name,vs,fs,mat,uv):
 o=g.mesh(name,vs,fs,mat,True);layer=o.data.uv_layers.new(name='SurfaceUV')
 for p in o.data.polygons:
  for li in p.loop_indices:layer.data[li].uv=uv[o.data.loops[li].vertex_index]
 # Cloth is a real shell: both its visible underside and top receive their own
 # correctly directed bake rays. Standalone face normal recalculation is unsafe.
 mod=o.modifiers.new('Woven fabric thickness','SOLIDIFY');mod.thickness=.012;mod.offset=0
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False)
 return o
def brickwall(name,axis,at,span,h,matlist,opening=None):
 # Individual offset ashlar creates worn hand drawn joints at every scale.
 rows=int(h/.55)
 for j in range(rows):
  z=(j+.5)*h/rows;step=1.25;start=-span/2-(.62 if j%2 else 0)
  for k in range(int(span/step)+2):
   a=max(-span/2,start+k*step);b=min(span/2,start+(k+1)*step)
   if b-a<.05:continue
   mid=(a+b)/2
   if opening and opening(mid,z):continue
   loc=(mid,at,z) if axis=='y' else (at,mid,z);dim=(b-a-.018,.30,h/rows-.016) if axis=='y' else (.30,b-a-.018,h/rows-.016)
   box(name,loc,dim,random.choice(matlist),.012)
def front_window(name,c,w,h,mat=window,angle=0):
 pts=g.arch_points(w,h);verts=[g.tf(c,u,0,z,angle) for u,z in pts];g.mesh(name+' luminous glazing',verts,[tuple(range(len(verts)))],mat)
 g.arch_frame(name+' carved pointed surround',c,w+.16,h+.07,.13,woodlight if ID=='divination' else stone[4],angle)
 g.arch_frame(name+' inset lead frame',g.tf(c,0,-.035,0,angle),w-.05,h-.06,.035,iron,angle)
 # Diamond lead lattice clipped to the pointed silhouette.
 for slope in [-1,1]:
  for q in range(-8,12):
   pts2=[]
   for j in range(101):
    u=-w/2+j*w/100;z=slope*u*1.45+q*.52
    if .03<z<g.arch_height(u,w,h)-.05:pts2.append(g.tf(c,u,-.055,z,angle))
   if len(pts2)>1:path(name+' diamond lead',pts2,.018,woodlight if ID=='divination' else iron)
 path(name+' central mullion',[g.tf(c,0,-.10,.02,angle),g.tf(c,0,-.10,h-.04,angle)],.055,woodlight if ID=='divination' else stone[4])
def bottle(x,y,z,h=.45,r=.12,kind=0,label=True):
 mat=random.choice(pottery);neck=r*(.38 if kind%2 else .52)
 prof=[(0,0),(r*.72,0),(r,.04*h),(r*1.04,.52*h),(r*.88,.69*h),(neck,.78*h),(neck,.94*h),(neck*1.12,.96*h),(neck*1.12,h),(0,h)] if kind%3 else [(0,0),(r*.8,0),(r,.08*h),(r,.85*h),(r*.82,.92*h),(r*.84,h),(0,h)]
 o=g.lathe('Irregular ingredient jar', (x,y,z),prof,mat,12);o.rotation_euler.z=random.uniform(-.15,.15);o.scale.x=random.uniform(.90,1.10)
 g.cyl('Cork and sealed stopper',(x,y,z+h+.025),neck*1.02,.055,woodlight,n=12)
 if label and h>.27:
  # Curved label rather than a floating flat rectangle.
  vs=[];fs=[]
  for j in range(9):
   a=-pi/2-.72+j*.18
   for zz in [.26*h,.53*h]:vs.append((x+r*1.055*cos(a),y+r*1.055*sin(a),z+zz))
  for j in range(8):fs.append((j*2,j*2+1,j*2+3,j*2+2))
  labelmesh=g.mesh('Ochre paper specimen label',vs,fs,parchment)
  for vertex in labelmesh.data.vertices:
   vertex.co.x=x+(vertex.co.x-x)*o.scale.x
   vertex.co.y=y+(vertex.co.y-y)*1.025
  mod=labelmesh.modifiers.new('Paper thickness','SOLIDIFY');mod.thickness=.002;mod.offset=0
  bpy.context.view_layer.objects.active=labelmesh;labelmesh.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);labelmesh.select_set(False)
  for zz in [.34,.39,.44]:box('Handwritten label mark',(x,y-r*1.06-.002,z+h*zz),(r*.69,.003,.007),ink)
def cauldron(x,y,z,r=.46):
 g.lathe('Hammered bulbous cauldron',(x,y,z),[(0,.02),(r*.55,.02),(r*.92,.20),(r,.39),(r*.84,.61),(r*.70,.70),(r*.70,.78),(r*.82,.80),(r*.82,.85),(r*.67,.85),(r*.65,.77),(r*.74,.69),(r*.79,.58)],iron,28)
 ring('Rolled cauldron rim',(x,y,z+.83),r*.78,bronze,.024)
 g.cyl('Dark herbal liquid',(x,y,z+.62),r*.75,.018,pottery[0],n=28)
 for s in [-1,1]:
  pts=[(x+s*(r+.08*cos(a)),y+.18*sin(a),z+.52+.18*cos(a)) for a in [i*2*pi/24 for i in range(25)]];path('Forged oval handle',pts,.028,iron)
 for a in [0,2*pi/3,4*pi/3]:g.beam('Splayed cauldron foot',(x+r*.66*cos(a),y+r*.66*sin(a),z+.13),(x+r*.86*cos(a),y+r*.86*sin(a),z-.13),.065,iron)
 path('Stirring rod',[(x+.15,y,z+.55),(x+.42,y+.18,z+1.18)],.027,woodlight)
def book(x,y,z,angle=0):
 box('Thick stained page block',(x,y,z+.07),(.43,.32,.10),parchment,.015,angle)
 for dz in [.01,.14]:box('Leather book cover',(x,y,z+dz),(.46,.35,.035),burgundy,.012,angle)
 box('Brass book clasp',(x+.17*cos(angle),y+.17*sin(angle),z+.17),(.055,.18,.018),bronze,.002,angle)
def candle(x,y,z,h=.34):
 g.lathe('Candle stick',(x,y,z),[(.13,0),(.13,.03),(.05,.06),(.035,.19),(.08,.24)],bronze,16)
 g.cyl('Dripped wax candle',(x,y,z+.24+h/2),.047,h,cream,12)
 g.sphere('Small candle flame',(x,y,z+.24+h+.045),(.027,.027,.075),glow,12,8)
def scale(x,y,z):
 box('Balance carved foot',(x,y,z+.04),(.62,.44,.08),woodlight,.035)
 g.lathe('Balance brass stem',(x,y,z+.08),[(.15,0),(.09,.05),(.035,.18),(.03,.78),(.07,.84),(.01,.90)],bronze,16)
 path('Balance crooked beam',[(x-.48,y,z+.86),(x-.40,y,z+.93),(x,y,z+.88),(x+.42,y,z+.98),(x+.48,y,z+.92)],.027,bronze)
 for s in [-1,1]:
  cx=x+s*.42
  for dy in [-.13,.13]:path('Suspended pan chain',[(cx,y,z+.90),(cx+s*.11,y+dy,z+.27)],.006,bronze)
  g.lathe('Balance weighing bowl',(cx+s*.07,y,z+.23),[(0,0),(.18,.015),(.22,.06)],bronze,18)
def table(x,y,z,w,d,name='Student workbench'):
 for k in range(4):box(name+' worn plank',(x,y+(k-1.5)*d/4,z),(w-.025,d/4-.012,.13),wood,.025)
 for sx in [-1,1]:
  for sy in [-1,1]:
   leg=box(name+' trestle foot',(x+sx*(w/2-.20),y+sy*(d/2-.15),z/2),(.12,.14,z),wood,.018);leg.rotation_euler.y=sx*.05
 box(name+' long stretcher',(x,y,z*.32),(w-.3,.10,.13),wood,.012)
def build_potions():
 g.collection('01 Floor')
 box('Room floor foundation',(0,0,-.15),(10.6,11.6,.3),seam)
 for row in range(12):
  for col in range(11):
   x=-5+col*.94; y=-5.15+row*.91
   box('Irregular flagged limestone',(x,y,-.025+random.uniform(-.006,.006)),(.92,.89,.10),random.choice(stone),.018,random.uniform(-.005,.005))
 g.collection('02 Architecture')
 brickwall('Left cellar masonry','x',-5.1,11.2,4.4,stone);brickwall('Right cellar masonry','x',5.1,11.2,4.4,stone)
 brickwall('Rear ashlar masonry','y',5.6,10.3,6.4,stone,lambda x,z:abs(x)<1.20 and 1.8<z<5.5)
 brickwall('Inferred reverse masonry','y',-5.6,10.3,6.4,stone)
 # Barrel vault constructed in twelve long strips plus visible rib and keystone courses.
 for k in range(28):
  a=k*pi/28+.001;b=(k+1)*pi/28-.001
  for j in range(14):
   vs=[(5.05*cos(t),y,4.25+2.15*sin(t)) for y in [-5.6+j*.80+.008,-5.6+(j+1)*.80-.008] for t in [a,b]]
   g.mesh('Curving stone vault block',vs,[(0,1,3,2)],stone[(k+j)%7])
 for y in [-5.25,-1.8,1.8,5.25]:
  for side in [-1,1]:
   box('Square fluted pier',(side*4.72,y,2.12),(.42,.48,4.25),stone[3],.035)
   for z,w,h in [(.18,.72,.28),(.42,.57,.16),(3.83,.66,.17),(4.05,.82,.21)]:box('Stepped pier capital',(side*4.72,y,z),(w,.74,h),stone[4],.018)
  pts=[(4.72*cos(t),y,4.18+2.12*sin(t)) for t in [i*pi/48 for i in range(49)]];path('Bold transverse vault rib',pts,.15,stone[5])
  for k in range(17):
   t=(k+.5)*pi/17;o=box('Rib voussoir',(4.72*cos(t),y,4.18+2.12*sin(t)),(.40,.38,.25),stone[(k+2)%7],.018);o.rotation_euler.y=pi/2-t
 for side in [-1,1]:path('Longitudinal vault rib',[(side*3.4,-5.45,5.82),(side*3.4,5.45,5.82)],.065,stone[3])
 front_window('Twin lancet apothecary window',(0,5.41,1.72),2.12,3.66)
 # Surround opens into the real luminous window; stepped sill and crest carved geometry.
 box('Deep stone window sill',(0,5.12,1.72),(2.65,.60,.18),stone[4],.025)
 for x in [-1.08,1.08]:box('Lancet jamb',(x,5.22,3.10),(.18,.35,2.8),stone[4],.025)
 g.arch_frame('Large ornamental window hood',(0,5.1,1.63),2.64,4.15,.19,stone[5])
 # Original rune-like strokes, decorative rather than copied lettering.
 for i in range(17):
  u=-1.24+i*.155;z=g.arch_height(u,2.65,4.15)+1.65
  path('Incised apothecary rune',[(u-.035,4.88,z-.04),(u,4.88,z+.055),(u+.035,4.88,z-.025)],.009,bronze)
 g.collection('03 Shelving and furniture')
 for side in [-1,1]:
  for z in [.45,1.23,2.01]:
   box('Long apothecary shelf',(side*4.62,.0,z),(.68,9.90,.10),wood,.02)
   for y in [-4.7,-1.6,1.6,4.7]:g.beam('Triangular shelf bracket',(side*4.94,y,z-.40),(side*4.40,y,z-.06),.065,wood)
  box('Dark shelf backing',(side*4.98,0,1.32),(.07,10.2,2.75),wood,.01)
 for side in [-1,1]:
  for z in [.48,1.25,2.03]:box('Rear ingredient shelf',(side*3.1,5.03,z),(3.25,.60,.10),wood,.02)
  box('Rear shelf backing',(side*3.1,5.40,1.4),(3.40,.08,2.80),wood,.01)
 table(0,3.75,1.04,4.3,1.12,'Professor demonstration table')
 for x in [-2.15,2.15]:
  for y in [-2.2,.55]:table(x,y,.95,3.4,1.18)
 # Rear board and original side door are extrapolations for exploration.
 box('Reverse door panels',(0,-5.37,1.63),(2.1,.12,3.25),wood,.025)
 g.arch_frame('Reverse door pointed stone surround',(0,-5.26,0),2.2,3.4,.14,stone[4])
 for x in [-.78,-.39,0,.39,.78]:box('Door plank seam',(x,-5.28,1.55),(.012,.015,3.0),seam)
 for z in [.55,2.5]:box('Iron door strap',(0,-5.22,z),(1.85,.035,.09),iron,.01)
 g.collection('04 Small props')
 for side in [-1,1]:
  for z in [.51,1.29,2.07]:
   for k in range(31):
    y=-4.65+k*.31+random.uniform(-.035,.035);h=random.uniform(.33,.70);r=random.uniform(.10,.15)
    bottle(side*4.49,y,z,h,r,k)
    if k%3==0:bottle(side*4.76,y+.10,z,random.uniform(.30,.52),.10,k+1)
  for z in [.54,1.31,2.09]:
   for k in range(12):bottle(side*(1.64+k*.255),4.93,z,random.uniform(.30,.67),random.uniform(.085,.12),k)
 for x in [-2.15,2.15]:
  for y in [-2.2,.55]:
   cauldron(x-.65,y,.99,.43)
   for k in range(3):bottle(x+.25+k*.25,y+.12,1.03,.30+random.random()*.27,.075,k)
   book(x+.65,y-.26,1.04,random.uniform(-.3,.3))
   g.lathe('Mortar bowl',(x+.12,y-.25,1.03),[(.06,0),(.14,.03),(.18,.20),(.14,.21),(.10,.06)],bronze,16)
   path('Pestle',[(x+.10,y-.25,1.15),(x+.21,y-.18,1.38)],.035,woodlight)
   # Three fine glass vials in a timber rack.
   box('Vial rack',(x+1.15,y+.25,1.08),(.46,.20,.08),woodlight,.01)
   for k in range(3):bottle(x+.99+k*.15,y+.25,1.12,.22,.035,k,False)
 scale(.77,3.72,1.12);cauldron(-1.1,3.72,1.13,.53);candle(1.75,3.75,1.11,.46)
 # Hanging dried botanical clusters occupy corners without blocking walk routes.
 for x in [-3.75,3.75]:
  path('Herb suspension cord',[(x,4.80,3.65),(x,4.80,2.88)],.012,woodlight)
  for i in range(10):
   dx=random.uniform(-.17,.17);dy=random.uniform(-.10,.10);g.beam('Dried botanical stem',(x,4.8,3.05),(x+dx,4.8+dy,2.50+random.random()*.25),.012,woodlight)
   g.sphere('Dried sage foliage',(x+dx,4.8+dy,2.60),(.08,.045,.14),pottery[0],8,5)
 for y in [-3.4,2.4]:
  for side in [-1,1]:
   candle(side*4.15,y,2.35,.32);g.point('Small warm candlelight',(side*4.15,y,3.0),36,(1,.58,.24),.20)
 g.collection('05 Lighting')
 g.area('Soft leaded window light',(0,4.90,4.45),(0,-.8,.8),620,(1,.79,.53),3)
 g.area('Ceiling bounced warm fill',(0,-.4,5.6),(0,1,1),125,(.73,.68,.55),7)
 g.area('Front soft reflected fill',(0,-4.7,3.5),(0,2,1.8),65,(.61,.68,.67),5)
 cams=[('药剂课全景',(0,-4.85,3.15),(0,2.45,2.6),23),('炼制工作台',(3.8,-3.9,2.05),(-1.0,1.55,1.55),26),('瓶罐与石窗',(-3.6,1.35,2.2),(1.0,4.3,2.5),28)]
 obs=[(-4.99,-4.13,-5.15,5.18),(4.13,4.99,-5.15,5.18),(-4.8,-1.45,4.66,5.42),(1.45,4.8,4.66,5.42),(-2.2,2.2,3.12,4.38)]
 for x in [-2.15,2.15]:
  for y in [-2.2,.55]:obs.append((x-1.73,x+1.73,y-.63,y+.63))
 return cams,obs,(-4.05,4.05,-5.05,4.55),(0,-4.45,1.65),(0,3.5,1.65)
def cloth_table(x,y,z,r,mat):
 # Continuous radial cloth; scalloped hem and uneven gravity folds are actual mesh.
 n=72;radial=[0,.25,.60,.92,1.04,1.065,1.08];vs=[];uv=[]
 for j,rr in enumerate(radial):
  for i in range(n):
   a=2*pi*i/n;drop=0 if j<4 else [0,0,0,0,.15,.42,.70][j];wave=sin(12*a+.6)*.028*(j/6)**2
   rz=z+.03 if j<4 else z-drop+.035*cos(a*12)
   vs.append((x+(r*rr+wave)*cos(a),y+(r*rr+wave)*sin(a),rz));uv.append((.5+rr*cos(a)/2,.5+rr*sin(a)/2))
 fs=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(6) for i in range(n)]
 uv_mesh('Scalloped embroidered tablecloth',vs,fs,mat,uv)
 for ringid in [4,6]:
  path('Gold stitched circular cloth border',[vs[ringid*n+i] for i in range(n)],.012,gold,True)
 for a in [0,2*pi/3,4*pi/3]:g.beam('Splayed low table leg',(x+r*.53*cos(a),y+r*.53*sin(a),z-.12),(x+r*.67*cos(a),y+r*.67*sin(a),.08),.10,wood)
 for i in range(12):
  a=2*pi*i/12
  # Gold petal motif on the top border, drawn geometry readable even at distance.
  cx=x+r*.84*cos(a);cy=y+r*.84*sin(a)
  ring('Embroidered gold rosette',(cx,cy,z+.037),.037,gold,.006,12)
def cushion(x,y,mat,r=.38):
 g.cyl('Carved low footstool rim',(x,y,.20),r,.23,wood,n=28)
 g.sphere('Deep tufted round cushion',(x,y,.37),(r*1.03,r*1.03,.16),mat,32,12)
 ring('Piped cushion seam',(x,y,.36),r,bronze,.012)
 g.sphere('Tuft button',(x,y,.49),(.045,.045,.019),gold,12,6)
 for i in range(6):
  a=2*pi*i/6
  pts=[(x+t*r*cos(a),y+t*r*sin(a),.49-.115*t**.7) for t in [j/12 for j in range(1,12)]];path('Gathered cushion tuck',pts,.008,burgundy)
 for a in [0,2*pi/3,4*pi/3]:g.beam('Small stool foot',(x+.24*cos(a),y+.24*sin(a),.13),(x+.30*cos(a),y+.30*sin(a),.035),.07,wood)
def ball(x,y,z,r=.14):
 g.lathe('Small carved crystal foot',(x,y,z),[(0,0),(.075,0),(.095,.025),(.06,.055),(.05,.073)],wood,12)
 center=z+r+.06
 g.sphere('Clouded translucent gazing globe',(x,y,center),(r,r,r),crystal,28,18)
 # Partially transparent, irregular interior clouds remain isolated during baking.
 for dx,dy,dz,sc in [(-.22,.14,-.10,.48),(.22,-.08,.23,.34),(.05,.22,-.35,.25)]:
  g.sphere('Lavender mist within crystal',(x+dx*r,y+dy*r,center+dz*r),(r*sc,r*sc*.72,r*sc*.85),mist,18,10)
 pts=[(x+r*.81*sin(t),y-r*.67,center+r*.81*cos(t)) for t in [(-.95+i*.75/16) for i in range(17)]]
 path('Soft curved crystal highlight',pts,r*.025,crystalglint)


def rug(x,y,w,d,mat,angle=0):
 box('Persian carpet base',(x,y,.016),(w,d,.018),mat,.004,angle)
 def tf(u,v):return(x+u*cos(angle)-v*sin(angle),y+u*sin(angle)+v*cos(angle),.032)
 for gap in [.06,.12,.23]:path('Woven rug border',[tf(u,v) for u,v in [(-w/2+gap,-d/2+gap),(w/2-gap,-d/2+gap),(w/2-gap,d/2-gap),(-w/2+gap,d/2-gap)]],.012,gold,True)
 for k in range(12):
  u=-w/2+.35+k*(w-.7)/11
  for v in [-d/2+.18,d/2-.18]:path('Carpet border diamond',[tf(u-.045,v),tf(u,v+.055),tf(u+.045,v),tf(u,v-.055)],.008,gold,True)
 for u in [-w*.28,0,w*.28]:
  for v in [-d*.25,0,d*.25]:
   pts=[tf(u+(.16 if i%2==0 else .075)*cos(i*pi/4),v+(.20 if i%2==0 else .10)*sin(i*pi/4)) for i in range(8)];path('Woven carpet flower',pts,.009,gold,True)
def drape_strip(name,side,y,mat):
 # Catenary-like cloth: high center attachment, bowed concave belly, raised outer tie.
 nx=38;ny=24;vs=[];uv=[]
 for i in range(nx+1):
  t=i/nx;x=side*(.15+5.20*t)
  z=6.30-2.65*t-1.18*sin(pi*t)
  for j in range(ny+1):
   v=j/ny;fold=.095*sin(v*8*pi+.4)*sin(pi*t)**.6-.20*sin(pi*v)*sin(pi*t)
   vs.append((x,y+(v-.5)*2.8,z+fold));uv.append((t*1.8,v*1.1))
 fs=[(i*(ny+1)+j,(i+1)*(ny+1)+j,(i+1)*(ny+1)+j+1,i*(ny+1)+j+1) for i in range(nx) for j in range(ny)]
 o=uv_mesh(name,vs,fs,mat,uv);mod=o.modifiers.new('Woven canopy thickness','SOLIDIFY');mod.thickness=.012
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False)
 for j in [0,ny]:path('Canopy stitched seam',[vs[i*(ny+1)+j] for i in range(nx+1)],.007,bronze)


def vertical_curtain(x,y,w,h,angle=0):
 vs=[];uv=[];nx=22;nz=12
 for j in range(nz+1):
  t=j/nz
  for i in range(nx+1):
   u=i/nx;v=(u-.5)*w*(.45+.55*abs(2*t-1));d=.08*sin(u*8*pi)+.18*sin(pi*t);pt=g.tf((x,y,.18),v,d,t*h,angle);vs.append(pt);uv.append((u,t*1.5))
 fs=[(j*(nx+1)+i,j*(nx+1)+i+1,(j+1)*(nx+1)+i+1,(j+1)*(nx+1)+i) for j in range(nz) for i in range(nx)]
 uv_mesh('Gathered burgundy window drape',vs,fs,pattern,uv)
 path('Golden curtain tie',[g.tf((x,y,.18),-.25*w, -.02,h*.43,angle),g.tf((x,y,.18),.25*w,-.02,h*.43,angle)],.035,gold)
def build_divination():
 g.collection('01 Floor')
 box('Tower floor foundation',(0,0,-.15),(11.6,12,.3),seam)
 for i in range(27):
  for j in range(4):
   x=-5.5+(i+.5)*11/27;y=-5.65+(j+.5)*2.85
   box('Long crooked oak floorboard',(x,y,-.015),(11/27-.016,2.83,.07),woodlight,.012)
 rug(0,2.28,4.3,3.5,pattern,pi/6)
 # Raised side teaching platforms visibly frame the continuous low center aisle.
 for side in [-1,1]:
  for y,d,height in [(-3.85,3.55,.34),(-.45,3.16,.24)]:
   cx=side*3.16
   box('Raised side platform dark riser',(cx,y,height/2),(4.42,d,height),wood,.018)
   for k in range(10):
    box('Platform aged oak plank',(cx-2.16+(k+.5)*.432,y,height+.022),(.422,d-.025,.055),woodlight,.012)
   box('Broad worn platform aisle nosing',(side*.95,y,height+.04),(.15,d+.02,.10),wood,.012)
   for v in [-d/2+.06,d/2-.06]:box('Platform cross edging',(cx,y+v,height+.04),(4.45,.14,.10),wood,.012)

 g.collection('02 Architecture')
 # Tall glazing in fully modeled walls. The room is a compressed tower interior.
 for side in [-1,1]:
  brickwall('Tower side limestone','x',side*5.58,11.6,6.2,warmstone,lambda y,z: any(abs(y-t)<1.15 for t in [-3.7,0,3.7]) and .9<z<5.5)
  for y in [-3.7,0,3.7]:front_window('Tall tower window',(side*5.40,y,.83),2.1,4.85,angle=pi/2 if side<0 else -pi/2)
  for y in [-5.35,-1.85,1.85,5.35]:
   box('Tower dark timber post',(side*5.22,y,2.9),(.20,.24,5.8),wood,.025)
   box('Stone pier',(side*5.37,y,2.7),(.36,.48,5.4),warmstone[2],.025)
 brickwall('Rear tower wall','y',5.85,11.2,6.4,warmstone,lambda x,z: 1.5<abs(x)<3.8 and 1.0<z<5.7)
 for x in [-2.6,2.6]:front_window('Rear high diamond window',(x,5.63,.91),2.1,4.85)
 brickwall('Inferred reverse tower wall','y',-5.85,11.2,6.4,warmstone)
 for x in [-4.5,-.95,.95,4.5]:
  box('Tall timber wall upright',(x,5.42,2.8),(.18,.30,5.6),wood,.02)
 # Stylized stone hood above the central teacher chair.
 pts=[(-1.47,5.35,1.95)]+[(x,5.35,1.95+g.arch_height(x,2.94,3.55)) for x in [-1.47+i*2.94/24 for i in range(25)]]+[(1.47,5.35,1.95)]
 for i,(a,b) in enumerate(zip(pts,pts[1:])):g.beam('Thick stone tower archivolt',a,b,.30,warmstone[(i//4)%6],.40)
 for side in [-1,1]:
  box('Archivolt carved spring block',(side*1.47,5.28,4.22),(.55,.56,.30),warmstone[3],.018)

 box('Carved central corbel',(0,5.10,4.4),(.65,.62,.32),warmstone[3],.08)
 g.sphere('Owl capital body',(0,4.98,3.94),(.23,.17,.30),warmstone[1],12,8)
 for x in [-.12,.12]:
  g.sphere('Owl capital eye',(x,4.81,4.09),(.10,.06,.10),warmstone[4],12,8)
  g.sphere('Owl stone pupil',(x,4.75,4.09),(.035,.026,.045),seam,10,6)
 for side in [-1,1]:g.sphere('Owl folded wing',(side*.22,4.99,3.94),(.12,.12,.27),warmstone[2],12,8)
 box('Reverse tower door',(0,-5.61,1.6),(1.9,.13,3.2),wood,.025)
 g.arch_frame('Door carved arch',(0,-5.48,0),2.05,3.45,.12,woodlight)
 g.collection('03 Drapery')
 box('Dark timber canopy ridge',(0,0,6.20),(.48,11.80,.20),wood,.025)
 for y in [-4.25,-1.42,1.42,4.25]:
  for side in [-1,1]:drape_strip('Folded burgundy canopy',side,y,canopypattern if abs(y)>3 else canopy)
 for side in [-1,1]:
  for y in [-5.20,-1.80,1.80,5.20]:vertical_curtain(side*5.04,y,1.75,4.35,pi/2 if side<0 else -pi/2)
 for x in [-4.10,-1.17,1.17,4.10]:vertical_curtain(x,5.33,1.22,5.55)
 # Front valance has a bowed lower edge and hangs with its lowest belly away from the walls.
 for side in [-1,1]:
  vs=[];uv=[];nx=38;nz=16
  for i in range(nx+1):
   t=i/nx;x=side*(.12+5.12*t);bottom=6.23-2.63*t-1.05*sin(pi*t)
   for j in range(nz+1):
    v=j/nz;z=bottom+(6.42-bottom)*v;y=-2.85+.18*sin(pi*t)+.06*sin(t*11*pi)*(1-v)
    vs.append((x,y,z));uv.append((t*2,v))
  fs=[(i*(nz+1)+j,(i+1)*(nz+1)+j,(i+1)*(nz+1)+j+1,i*(nz+1)+j+1) for i in range(nx) for j in range(nz)]
  uv_mesh('Gravity bowed velvet valance',vs,fs,canopy,uv)
  path('Valance muted embroidered hem',[vs[i*(nz+1)] for i in range(nx+1)],.010,bronze)
  for i in range(3,nx,3):
   x,y,z=vs[i*(nz+1)];path('Small curtain fringe tassel',[(x,y,z),(x,y,z-.11)],.013,gold)
 g.collection('04 Furniture')
 positions=[(-3.48,-3.60,.41,.91),(-2.72,-.48,.31,.82),(-4.10,2.65,0,.67),(3.42,-3.10,.41,.96),(2.58,.10,.31,.78),(4.12,2.88,0,.69)]
 for i,(x,y,lift,radius) in enumerate(positions):
  before=set(bpy.context.scene.objects)
  angle=[-.16,.13,.08,.20,-.10,-.09][i]
  rug(x,y,2.65 if i<4 else 2.0,2.75 if i<4 else 1.9,pattern if i%2==0 else burgundy,angle)
  cloth_table(x,y,.91+(i%3)*.045,radius,pattern if i%3 else teal)
  for k in range(2 if i in [2,5] else 3):
   a=-pi/2+(k-1)*1.19+angle+.11*(i%2)
   cushion(x+(radius+.30)*cos(a),y+(radius+.30)*sin(a),burgundy if (k+i)%2==0 else amber,.31+.035*(k%2))
  for k in range(2 if i%3==2 else 3):
   ball(x+(k-1)*.35+.04*(i%2),y+.10*((k+i)%2),.96+(i%3)*.045,.125+(.018 if k==1 else 0))
  # Move all newly authored table, rug, cushions and crystal objects onto their real platform.
  for o in set(bpy.context.scene.objects)-before:o.location.z+=lift
 chair_start=set(bpy.context.scene.objects)
 # Curved padded wing chair, scaled against the official camera composition.
 for x in [-.45,.45]:
  for y in [2.7,3.36]:g.beam('Wing chair carved leg',(x,y,.40),(x*1.15,y-.06,.07),.11,wood)
 g.sphere('Wing chair seat',(.10,3.01,.64),(.54,.44,.18),burgundy,32,12)
 box('Tall wing chair padded back',(0,3.40,1.47),(.94,.30,1.62),burgundy,.15)
 for s in [-1,1]:
  wing=g.sphere('Curving upholstered wing',(s*.52,3.31,1.63),(.19,.28,.68),burgundy,20,12);wing.rotation_euler.y=s*.13
  g.sphere('Rolled velvet arm',(s*.54,3.0,.94),(.13,.49,.13),burgundy,24,10)
  path('Gold stitched chair silhouette',[(s*.49,3.27,.73),(s*.63,3.30,1.60),(s*.60,3.37,2.18),(s*.45,3.38,2.29)],.014,gold)
 for x in [-.25,0,.25]:
  for z in [1.1,1.4,1.7]:g.sphere('Chair tuft button',(x,3.228,z),(.027,.018,.027),gold,10,6)
 bpy.context.view_layer.update();pivot=Vector((0,3.0,0))
 for o in set(bpy.context.scene.objects)-chair_start:o.matrix_world=Matrix.Translation(pivot)@Matrix.Scale(.88,4)@Matrix.Translation(-pivot)@o.matrix_world
 # Two narrow filled tea cupboards and a stepped collection of orbs.
 for side in [-1,1]:
  cabinet_start=set(bpy.context.scene.objects)
  x=side*4.55;table(x,4.80,.82,1.15,.62,'Tea cabinet base')
  box('Tea cabinet back',(x,5.18,2.05),(1.24,.10,2.7),wood,.02)
  for xx in [x-.62,x+.62]:box('Tea cabinet side',(xx,4.99,2.05),(.10,.52,2.7),wood,.015)
  for z in [.92,1.53,2.14,2.75,3.36]:box('Tea cabinet shelf',(x,4.97,z),(1.2,.52,.06),woodlight,.012)
  for z in [.96,1.57,2.18,2.79]:
   for j in range(4):
    cx=x-.43+j*.28;g.lathe('Stack of chipped teacups',(cx,4.86,z),[(.045,0),(.09,.04),(.11,.13),(.09,.14),(.065,.055)],cream,14)
    path('Tiny cup handle',[(cx+.10,4.86,z+.04),(cx+.15,4.86,z+.05),(cx+.15,4.86,z+.11),(cx+.10,4.86,z+.12)],.012,bronze)
  bottle(x,4.86,.94,.35,.14,1)
  if side<0:
   bpy.context.view_layer.update();pivot=Vector((x,4.9,0));shape=Matrix.Diagonal((1.22,1.0,.76,1.0))
   for o in set(bpy.context.scene.objects)-cabinet_start:o.matrix_world=Matrix.Translation(pivot)@shape@Matrix.Translation(-pivot)@o.matrix_world

 table(-1.65,4.80,.76,.75,.75,'Crystal reading stand');ball(-1.65,4.80,.84,.25)
 for row in range(3):
  box('Stepped orb bench',(2.15,4.72+row*.22,.30+row*.24),(1.60,.31,.10),wood,.015)
  for k in range(4-row):ball(1.55+k*.36+row*.17,4.72+row*.22,.36+row*.24,.11)
 for x in [-.76,.76]:candle(x,4.65,.24,.60)
 g.collection('05 Lighting')
 g.area('Strong local left window spill',(-4.8,2.0,3.7),(.8,1,.4),860,(1,.80,.62),2.1)
 g.area('Soft right window spill',(4.8,.5,3.7),(0,1,1),280,(.88,.75,.66),2.4)
 g.area('Back windows warm wash',(0,5.25,4.7),(0,-1,1),450,(1,.76,.58),3)
 g.area('Soft front bounced light',(0,-4.6,4.2),(0,2,1.5),95,(.78,.60,.52),5)
 g.area('Canopy bounced fill',(0,.0,5.7),(0,0,1),55,(1,.48,.32),4)
 cams=[('占卜课全景',(.12,-5.15,2.83),(0,2.6,2.04),19.8),('水晶球与绣毯',(-.3,-2.55,1.85),(3.0,.2,1.0),26),('高窗与翼椅',(-2.0,1.50,2.2),(.3,4.0,1.8),27)]
 obs=[(-5.40,-.87,-5.65,1.15),(.87,5.40,-5.65,1.15)]+[(x-1.0,x+1.0,y-1.05,y+.86) for x,y,lift,r in positions if lift==0]+[(-.77,.77,2.5,3.7),(-5.1,-3.95,4.35,5.4),(3.95,5.1,4.35,5.4),(-2.06,-1.24,4.37,5.22),(1.25,3.05,4.35,5.4)]
 return cams,obs,(-4.95,4.95,-5.30,5.30),(0,-4.80,1.65),(0,3.1,1.65)
cams,obs,bounds,spawn,target=build_potions() if ID=='potions' else build_divination()
g.collection('06 Cameras')
for name,loc,targ,lens in cams:g.camera(name,loc,targ,lens)
S.camera=bpy.data.objects.get(cams[0][0]);S.render.filepath=str(ROOT/'previews'/('blender-'+ID+'.png'))
# Convert curves, normalize connected mesh face winding and preserve editability in objects.
for o in list(S.objects):
 if o.type in ['CURVE','FONT']:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
seen=set();negative=[]
for o in S.objects:
 if o.type!='MESH' or o.data.name in seen:continue
 seen.add(o.data.name);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
def yup(p):return [round(p[0],3),round(p[2],3),round(-p[1],3)]
meta={'id':ID,'title':'魔药课教室' if ID=='potions' else '占卜课教室','lighting':'baked','background':'#181311' if ID=='potions' else '#231314','exposure':1.0,'cameras':[{'name':n,'position':yup(p),'target':yup(t),'horizontalFov':round(2*math.atan(36/(2*l))*180/pi,2),'fov':round(2*math.atan(36/(2*(16/9)*l))*180/pi,2)} for n,p,t,l in cams],'spawn':{'position':yup(spawn),'target':yup(target)},'bounds':{'minX':bounds[0],'maxX':bounds[1],'minZ':-bounds[3],'maxZ':-bounds[2]},'obstacles':[{'minX':a,'maxX':b,'minZ':-d,'maxZ':-c} for a,b,c,d in obs],'artisticLimitations':['Original interpretation of the selected official promotional image, not ripped game assets.','Unseen reverse wall, depth, floor plan and walk routes are original extrapolations.','Promotional reference has denser painterly edge strokes; this model uses authored texture studies and actual geometric detail.'],'sourceReference':{'page':'https://www.harrypottermagicawakened.com/global/','image':'https://www.harrypottermagicawakened.com/pc/gw/20230516102258/img/v2/'+('map6_a177a0c.jpg' if ID=='potions' else 'map8_f1502e7.jpg'),'type':'official promotional scene image','inspected':'2026-11-17'}}
ASSETS.mkdir(parents=True,exist_ok=True);json.dump(meta,open(ASSETS/'metadata.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
meta['navigationSurface']='Ground-level central aisle and rear floor; raised side platforms are blocked by collision rectangles'
meta['platformHeights']=[.24,.34]
meta['crystalTreatment']='Layered unlit alpha glass with cloudy interior volumes; artistic approximation without dynamic refraction'
json.dump(meta,open(ASSETS/'metadata.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
S.render.image_settings.file_format='PNG';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'scene.blend'))
bpy.ops.render.render(write_still=True)
print('CLASSROOM_BUILD_COMPLETE',ID,len(S.objects),flush=True)
