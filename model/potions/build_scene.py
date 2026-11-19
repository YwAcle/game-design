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
S.world.color=(.05,.045,.04);S.view_settings.view_transform='AgX';S.view_settings.exposure=-.20 if ID=='potions' else .15
def painted(name,color,texture=None):
 m=g.material(name,color,rough=.85)
 if texture:
  nt=m.node_tree;n=nt.nodes;l=nt.links;t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(HERE/'textures'/texture),check_existing=True);t.projection='BOX';t.projection_blend=.15
  tc=n.new('ShaderNodeTexCoord');l.new(tc.outputs['Generated'],t.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.62;mix.inputs[2].default_value=(*color,1);l.new(t.outputs[0],mix.inputs[1]);l.new(mix.outputs[0],n.get('Principled BSDF').inputs['Base Color'])
 return m
stone=[painted('Ashlar stone %02d'%i,(.32+i*.016,.29+i*.014,.245+i*.013),'stone.jpg') for i in range(7)]
warmstone=[painted('Ochre limestone %02d'%i,(.58+i*.025,.42+i*.018,.29+i*.014),'stone.jpg') for i in range(6)]
wood=painted('Hand brushed dark walnut',(.36,.20,.12),'wood.jpg');woodlight=painted('Hand brushed honey oak',(.60,.34,.19),'wood.jpg')
seam=g.material('Deep seams',(.045,.028,.023));iron=g.material('Blackened iron',(.07,.062,.061),rough=.54,metal=.62)
bronze=g.material('Aged warm brass',(.38,.25,.10),rough=.5,metal=.6);gold=g.material('Faded textile gold',(.51,.32,.10),rough=.8)
burgundy=painted('Claret velvet',(.41,.065,.09),'cloth.jpg');pattern=painted('Gold vine claret brocade',(.62,.20,.22),'cloth-pattern.jpg');teal=painted('Ink blue brocade',(.12,.32,.33),'teal-pattern.jpg')
amber=g.material('Burnt sienna upholstery',(.38,.14,.065),(.53,.23,.11),rough=.95)
parchment=painted('Stained parchment',(.71,.58,.35),'paper.jpg');ink=g.material('Faded ink',(.14,.087,.048));cream=g.material('Glazed ivory crockery',(.59,.52,.39),rough=.4)
crystal=g.material('Pale cloudy crystal',(.64,.62,.73),rough=.22,metal=.12,emission=.15)
window=g.material('Warm overcast window',(.68,.55,.34),rough=1,emission=1.25)
glow=g.material('Candle flame',(.95,.46,.09),emission=4)
pottery=[g.material('Apothecary vessel %02d'%i,tuple(v*.43 for v in c),rough=.85) for i,c in enumerate([(.28,.25,.18),(.34,.24,.17),(.36,.30,.22),(.24,.25,.20),(.40,.35,.28),(.25,.24,.22)])]
def box(*a,**k):return g.box(*a,**k)
def path(*a,**k):return g.path(*a,**k)
def ring(name,loc,r,mat,t=.025,n=32):return path(name,[(loc[0]+r*cos(i*2*pi/n),loc[1]+r*sin(i*2*pi/n),loc[2]) for i in range(n)],t,mat,True)
def uv_mesh(name,vs,fs,mat,uv):
 o=g.mesh(name,vs,fs,mat,True);layer=o.data.uv_layers.new(name='SurfaceUV')
 for p in o.data.polygons:
  for li in p.loop_indices:layer.data[li].uv=uv[o.data.loops[li].vertex_index]
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
  # Thin closed paper shell, so its exterior normal is unambiguous for baking.
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
def polygon_solid(name,outline,y,depth,mat):
 vs=[(x,yy,z) for yy in [y-depth/2,y+depth/2] for x,z in outline];n=len(outline)
 return g.mesh(name,vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat)

def angular_window():
 # Widened shoulder, two pointed leaves, tapered lower opening: the reference's fan silhouette.
 # Solid wall spandrel is cut to the actual glazing outline, eliminating rectangular gaps.
 backing=box('Solid fan window spandrel',(0,5.57,3.6),(4.05,.31,5.0),stone[2],.002)
 left=[(-.78,1.65),(-1.32,3.94),(-.78,4.55),(-.34,4.37),(-.10,3.92),(-.08,1.65)]
 for side in [-1,1]:
  pane=[(x if side<0 else -x,z) for x,z in left]
  cutter=polygon_solid('Temporary fan opening cutter',pane,5.57,1.20,stone[0])
  mod=backing.modifiers.new('Actual angular glazing opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
  bpy.context.view_layer.objects.active=backing;backing.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);backing.select_set(False);bpy.data.objects.remove(cutter,do_unlink=True)
  polygon_solid('Fan window luminous leaf',pane,5.40,.025,window)
  path('Angular lead window boundary',[(x,5.32,z) for x,z in pane],.050,iron,True)
  # Clip diagonal leading to the actual pane polygon, not an enclosing rectangle.
  def inside(x,z):
   hit=False;j=len(pane)-1
   for i in range(len(pane)):
    a,b=pane[i],pane[j]
    if (a[1]>z)!=(b[1]>z) and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:hit=not hit
    j=i
   return hit
  for slope in [-1.7,1.7]:
   for k in range(-7,14):
    pts=[]
    for i in range(190):
     x=-1.4+i*2.8/189;z=slope*x+k*.48
     if inside(x,z):pts.append((x,5.29,z))
    if len(pts)>1:path('Fan window diagonal lead',pts,.014,iron)
 # Angular hood is a thick, closed polygon band, with a deliberately sharp apex.
 outer=[(-1.55,3.90),(-1.85,4.50),(-.96,5.48),(0,5.88),(.96,5.48),(1.85,4.50),(1.55,3.90)]
 inner=[(-1.23,4.02),(-1.48,4.45),(-.78,5.10),(0,5.49),(.78,5.10),(1.48,4.45),(1.23,4.02)]
 for i in range(6):polygon_solid('Faceted carved fan hood',[outer[i],outer[i+1],inner[i+1],inner[i]],5.10,.35,stone[(i+2)%7])
 path('Dark incised hood inner edge',[(x,4.90,z) for x,z in inner],.022,seam)
 path('Chipped hood outer edge',[(x,4.88,z) for x,z in outer],.028,stone[5])
 for side in [-1,1]:
  polygon_solid('Tapered fan window stone stile',[(side*.77,1.52),(side*1.49,4.02),(side*1.30,4.09),(side*.60,1.52)],5.12,.29,stone[4])
 polygon_solid('Central hanging carved mullion',[(-.17,3.96),(.17,3.96),(.12,3.61),(.065,2.60),(0,2.21),(-.065,2.60),(-.12,3.61)],5.14,.24,stone[4])
 for z,w in [(3.92,.44),(3.78,.32),(3.58,.23)]:box('Mullion layered collar',(0,4.96,z),(w,.24,.10),stone[3],.008)
 box('Deep window sill',(0,5.10,1.58),(1.85,.60,.16),stone[4],.015)
 # Original angular glyphs; subdued carved brown marks, not shining gold text.
 for side in [-1,1]:
  for k in range(7):
   t=(k+.5)/7;x=side*(.22+1.38*t);z=5.53-1.28*t
   path('Cut apothecary glyph',[(x-.04,4.90,z-.065),(x+.02,4.90,z+.065),(x+.055,4.90,z+.015)],.009,ink)

def clay_vessel(x,y,z,h,r,kind):
 # Alternate tall storage jars, squat crocks, pear jugs and flasks; all closed profiles.
 profiles=[[(0,0),(.70,0),(.92,.06),(1,.62),(.82,.83),(.67,.88),(.70,.97),(.76,1),(0,1)],
 [(0,0),(.68,0),(1,.18),(1.08,.58),(.82,.80),(.49,.85),(.48,1),(0,1)],
 [(0,0),(.75,0),(1,.08),(1,.90),(.88,.97),(1,1),(0,1)],
 [(0,0),(.60,0),(.95,.25),(1,.55),(.54,.73),(.25,.80),(.25,1),(0,1)],
 [(0,0),(.72,0),(1,.12),(1.08,.44),(.90,.67),(.77,.74),(.82,.82),(0,.82)]]
 mat=pottery[kind%len(pottery)];prof=[(a*r,b*h) for a,b in profiles[kind%5]]
 o=g.lathe('Large uneven clay ingredient vessel',(x,y,z),prof,mat,10+2*(kind%3));o.rotation_euler.z=random.uniform(-.35,.35);o.scale.x=random.uniform(.92,1.07)
 top=prof[-1][1]
 if kind%5 in [0,2,4]:
  g.cyl('Broad ceramic lid',(x,y,z+top+.015),r*(.81 if kind%5!=2 else .99),.045,mat,n=12)
  g.cyl('Clay lid knob',(x,y,z+top+.05),r*.22,.05,mat,n=10)
 else:g.cyl('Dull wax stopper',(x,y,z+top+.015),r*(.25 if kind%5==3 else .48),.04,wood,n=10)
 if kind%5==1:
  path('Jug loop handle',[(x+r*.80,y,z+h*.28),(x+r*1.37,y,z+h*.34),(x+r*1.40,y,z+h*.66),(x+r*.72,y,z+h*.78)],.035,mat)
 if kind%3!=1:
  box('Aged irregular jar label',(x,y-r*.97-.012,z+h*.45),(r*1.05,.015,h*.23),parchment,.005,random.uniform(-.09,.09))
  for j in range(3):box('Faded jar label script',(x,y-r*.99-.024,z+h*(.40+j*.045)),(r*.7,.006,.008),ink)

def scattered_paper(x,y,z,angle):
 o=box('Loose stained recipe sheet',(x,y,z),(.42,.57,.006),parchment,.002,angle)
 for i in range(7):
  v=-.20+i*.056;u=-.035 if i%3 else .025
  box('Faded recipe writing',(x+u*cos(angle)-v*sin(angle),y+u*sin(angle)+v*cos(angle),z+.005),(.28-random.random()*.08,.006,.003),ink,0,angle)

def build_potions():
 g.collection('01 Floor')
 box('Room floor foundation',(0,0,-.15),(10.6,11.6,.3),seam)
 for row in range(12):
  for col in range(11):
   box('Irregular flagged limestone',(-5+col*.94,-5.15+row*.91,-.025+random.uniform(-.006,.006)),(.92,.89,.10),random.choice(stone),.012,random.uniform(-.005,.005))
 g.collection('02 Architecture')
 brickwall('Left cellar masonry','x',-5.1,11.2,4.4,stone);brickwall('Right cellar masonry','x',5.1,11.2,4.4,stone)
 brickwall('Rear ashlar masonry','y',5.6,10.3,6.4,stone,lambda x,z:abs(x)<1.45 and 1.4<z<5.55)
 brickwall('Inferred reverse masonry','y',-5.6,10.3,6.4,stone)
 # Broad faceted ceiling planes replace the regular small checkerboard vault blocks.
 for k in range(16):
  a=k*pi/16+.0005;b=(k+1)*pi/16-.0005
  for j in range(6):
   ya=-5.6+j*11.2/6;yb=ya+11.2/6-.012
   vs=[(5.05*cos(t),y,4.25+2.15*sin(t)) for y in [ya,yb] for t in [a,b]]
   vs += [(5.28*cos(t),y,4.25+2.38*sin(t)) for y in [ya,yb] for t in [a,b]]
   g.mesh('Broad painted stone vault panel',vs,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],stone[(k+j)%7])
 for y in [-5.25,-1.8,1.8,5.25]:
  for side in [-1,1]:
   box('Massive vault pier',(side*4.66,y,2.12),(.63,.67,4.25),stone[3],.018)
   for z,w,h in [(.18,.85,.28),(.42,.72,.16),(3.83,.87,.17),(4.05,1.05,.23)]:box('Angular stepped pier capital',(side*4.66,y,z),(w,.90,h),stone[4],.012)
  pts=[(4.66*cos(t),y,4.18+2.08*sin(t)) for t in [i*pi/32 for i in range(33)]]
  for a,b in zip(pts,pts[1:]):g.beam('Broad transverse rib stone',a,b,.22,stone[3],.30)
 # True crossing diagonal ribs over each bay, climbing from four corners into a central boss.
 for ya,yb in [(-5.25,-1.8),(-1.8,1.8),(1.8,5.25)]:
  for reverse in [False,True]:
   pts=[]
   for i in range(33):
    t=i/32;pts.append((-4.66+9.32*t,ya+(yb-ya)*(1-t if reverse else t),4.17+2.04*sin(pi*t)**.75))
   for a,b in zip(pts,pts[1:]):g.beam('Intersecting diagonal vault rib',a,b,.16,stone[4],.22)
  box('Cross vault carved boss',(0,(ya+yb)/2,6.20),(.52,.54,.25),stone[5],.035)
 angular_window()
 g.collection('03 Shelving and furniture')
 for side in [-1,1]:
  for z in [.35,1.34,2.34]:
   box('Deep worn apothecary shelf',(side*4.59,0,z),(.83,9.9,.115),wood,.017)
   for y in [-4.6,-1.5,1.6,4.7]:g.beam('Angular shelf bracket',(side*4.94,y,z-.35),(side*4.24,y,z-.06),.075,wood)
  box('Dark shelf backing',(side*4.99,0,1.65),(.07,10.2,3.30),wood,.005)
  for z in [.38,1.37,2.37]:box('Rear ingredient shelf',(side*3.07,5.02,z),(3.10,.68,.11),wood,.015)
  box('Rear shelf backing',(side*3.07,5.41,1.65),(3.25,.08,3.30),wood,.005)
 # Reference-like cross table, then staggered stations with a safe serpentine passage.
 stations=[(-.15,-1.87,.98,6.15,1.55),(-2.05,.65,1.02,3.1,1.36),(2.42,1.55,.94,2.35,1.28),(-.35,3.70,1.07,4.25,1.18)]
 for i,(x,y,z,w,d) in enumerate(stations):table(x,y,z,w,d,'Broad cross worktop' if i==0 else 'Staggered laboratory worktop')
 box('Reverse door panels',(0,-5.37,1.63),(2.1,.12,3.25),wood,.015)
 g.arch_frame('Reverse door pointed surround',(0,-5.26,0),2.2,3.4,.14,stone[4])
 g.collection('04 Small props')
 for side in [-1,1]:
  for row,z in enumerate([.41,1.40,2.40]):
   y=-4.63;k=0
   while y<4.7:
    r=random.uniform(.14,.25) if row<2 else random.uniform(.12,.21);h=random.uniform(.40,.84)
    clay_vessel(side*(4.53+random.uniform(-.08,.08)),y,z,h,r,k+row*5+(3 if side>0 else 0));y+=r*2+random.uniform(.05,.16);k+=1
  for row,z in enumerate([.44,1.43,2.43]):
   for k in range(8):clay_vessel(side*(1.63+k*.39),4.97+random.uniform(-.06,.02),z,random.uniform(.42,.82),random.uniform(.13,.19),k+row*3)
 # Carefully placed distinct foreground groups, leaving significant empty stained worktop.
 for fn,args,pivot in [(cauldron,(-1.25,-1.72,1.08,.43),(-1.25,-1.72,1.08)),(scale,(1.87,-1.55,1.07),(1.87,-1.55,1.07))]:
  before=set(bpy.context.scene.objects);fn(*args);bpy.context.view_layer.update();pivot=Vector(pivot)
  for o in set(bpy.context.scene.objects)-before:o.matrix_world=Matrix.Translation(pivot)@Matrix.Scale(.66,4)@Matrix.Translation(-pivot)@o.matrix_world

 cauldron(-2.62,.73,1.12,.48);cauldron(2.77,1.61,1.04,.39)
 cauldron(-1.33,3.67,1.17,.52);scale(.86,3.68,1.17)
 for x,y,z in [(-.10,-1.97,1.08),(1.74,1.29,1.04),(-1.5,.55,1.12)]:
  for k in range(3):bottle(x+k*.23,y+random.uniform(-.12,.13),z,.24+random.random()*.28,.065+random.random()*.025,k)
  g.lathe('Faceted clay mortar',(x+.18,y-.20,z),[(0,0),(.10,0),(.18,.20),(.14,.22),(.08,.06)],pottery[2],10)
  path('Crooked wooden pestle',[(x+.18,y-.20,z+.08),(x+.31,y-.14,z+.40)],.031,woodlight)
 book(-.51,-2.34,1.08,-.19);book(-1.12,.90,1.12,.24)
 for x,y,z,a in [(.20,-2.34,1.06,.15),(.66,-2.22,1.06,-.20),(2.45,-2.27,1.06,.37),(.2,3.55,1.16,.12)]:scattered_paper(x,y,z,a)
 box('Low sample rack',(-2.26,-1.62,1.08),(.67,.30,.08),woodlight,.01)
 for k in range(5):bottle(-2.52+k*.13,-1.62,1.12,.22,.038,k,False)
 for x in [-3.72,3.55]:
  path('Herb suspension cord',[(x,4.78,4.0),(x,4.78,3.30)],.01,wood)
  for i in range(9):
   dx=random.uniform(-.17,.17);dy=random.uniform(-.1,.1)
   g.beam('Dried herb stem',(x,4.78,3.38),(x+dx,4.78+dy,2.93+random.random()*.22),.01,woodlight)
   g.sphere('Dried sage cluster',(x+dx,4.78+dy,3.03),(.07,.04,.14),pottery[0],8,5)
 candle(3.87,1.1,2.50,.29);g.point('Single warm shelf candle',(3.87,1.1,3.09),20,(1,.58,.24),.20)
 g.collection('05 Lighting')
 g.area('Local fan window light',(0,4.89,3.80),(-.70,-1.4,.65),420,(.94,.85,.68),1.5)
 g.area('Subtle vault bounce',(0,1.6,5.7),(0,.0,1),58,(.67,.62,.56),6)
 g.area('Dim cool foreground bounce',(-1,-4.7,3.5),(0,1,1.8),65,(.57,.61,.64),5)
 cams=[('药剂课全景',(.10,-4.90,2.95),(0,2.60,2.24),19.5),('炼制工作台',(3.65,-2.40,2.05),(-1.2,.70,1.45),25),('瓶罐与石窗',(-3.5,1.45,2.12),(.5,4.5,2.50),27)]
 obs=[(-4.99,-4.12,-5.15,5.18),(4.12,4.99,-5.15,5.18),(-4.8,-1.45,4.62,5.42),(1.45,4.8,4.62,5.42)]
 for x,y,z,w,d in stations:obs.append((x-w/2-.04,x+w/2+.04,y-d/2-.04,y+d/2+.04))
 return cams,obs,(-4.03,4.03,-5.05,4.48),(.65,-.64,1.65),(.65,2.8,1.65)


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
 g.lathe('Crystal ball carved pedestal',(x,y,z),[(.11,0),(.13,.03),(.09,.07),(.07,.10)],bronze,16)
 g.sphere('Milky crystal gazing orb',(x,y,z+r+.075),(r,r,r),crystal,24,16)
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
 # Ceiling fabric sweeps from high central ridge to low outer cornice in deep folds.
 nx=30;ny=20;vs=[];uv=[]
 for i in range(nx+1):
  t=i/nx;x=side*(.2+5.15*t);z=6.05-2.50*t*t-.38*sin(pi*t)
  for j in range(ny+1):
   v=j/ny;wave=.17*sin(v*6*pi+.5)*sin(pi*t/2)
   vs.append((x,y+(v-.5)*2.8,z+wave));uv.append((t*1.7,v*1.2))
 fs=[(i*(ny+1)+j,(i+1)*(ny+1)+j,(i+1)*(ny+1)+j+1,i*(ny+1)+j+1) for i in range(nx) for j in range(ny)]
 uv_mesh(name,vs,fs,mat,uv)
 for j in [0,ny]:path('Canopy stitched seam',[vs[i*(ny+1)+j] for i in range(nx+1)],.016,gold)
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
 rug(0,2.25,4.0,3.4,pattern,pi/6)
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
 for s in [-1,1]:g.beam('Pointed stone arch hood',(s*1.25,5.35,2.0),(0,5.35,5.4),.24,warmstone[3])
 box('Carved central corbel',(0,5.10,4.4),(.65,.62,.32),warmstone[3],.08)
 g.sphere('Owl capital body',(0,4.98,3.94),(.23,.17,.30),warmstone[1],12,8)
 for x in [-.12,.12]:
  g.sphere('Owl capital eye',(x,4.81,4.09),(.10,.06,.10),warmstone[4],12,8)
  g.sphere('Owl stone pupil',(x,4.75,4.09),(.035,.026,.045),seam,10,6)
 for side in [-1,1]:g.sphere('Owl folded wing',(side*.22,4.99,3.94),(.12,.12,.27),warmstone[2],12,8)
 box('Reverse tower door',(0,-5.61,1.6),(1.9,.13,3.2),wood,.025)
 g.arch_frame('Door carved arch',(0,-5.48,0),2.05,3.45,.12,woodlight)
 g.collection('03 Drapery')
 for y in [-4.25,-1.42,1.42,4.25]:
  for side in [-1,1]:drape_strip('Folded burgundy canopy',side,y,pattern if abs(y)>3 else burgundy)
 for side in [-1,1]:
  for y in [-5.20,-1.80,1.80,5.20]:vertical_curtain(side*5.04,y,1.75,4.35,pi/2 if side<0 else -pi/2)
 for x in [-4.10,-1.17,1.17,4.10]:vertical_curtain(x,5.33,1.22,5.55)
 # Main entrance drapes curve down at the sides, preserving the central view.
 for side in [-1,1]:
  vs=[];uv=[];nx=26;nz=15
  for i in range(nx+1):
   t=i/nx;x=side*(.12+5.12*t);bottom=6.05-3.1*sin(t*pi/2)**.9
   for j in range(nz+1):
    v=j/nz;z=bottom+(6.35-bottom)*v;y=-3.0+.20*sin(t*pi)+.13*sin(t*9*pi)*(1-v);vs.append((x,y,z));uv.append((t*2,v))
  fs=[(i*(nz+1)+j,(i+1)*(nz+1)+j,(i+1)*(nz+1)+j+1,i*(nz+1)+j+1) for i in range(nx) for j in range(nz)]
  uv_mesh('Sweeping theatre curtain swag',vs,fs,burgundy,uv);path('Swag gold fringe',[vs[i*(nz+1)] for i in range(nx+1)],.027,gold)
 g.collection('04 Furniture')
 positions=[(-3.42,-3.45),(-2.55,-.65),(-2.22,2.4),(3.42,-3.45),(2.55,-.65),(3.8,2.4)]
 for i,(x,y) in enumerate(positions):
  rug(x,y,2.65,2.8,pattern if i%2==0 else burgundy,(-.09 if x<0 else .09))
  cloth_table(x,y,.98,.78,pattern if i%3 else teal)
  for k in range(3):
   a=(-pi/2)+(k-1)*1.05;cushion(x+1.04*cos(a),y+1.04*sin(a),burgundy if k%2==0 else amber,.33)
  for k in range(3):ball(x+(k-1)*.34,y+.10*(k%2),1.02,.12+(.02 if k==1 else 0))
 # Curved padded wing chair, unusually tall as in the selected reference.
 for x in [-.45,.45]:
  for y in [2.7,3.36]:g.beam('Wing chair carved leg',(x,y,.40),(x*1.15,y-.06,.07),.11,wood)
 g.sphere('Wing chair seat',(0,3.01,.64),(.60,.48,.18),burgundy,32,12)
 g.sphere('Tall wing chair back',(0,3.40,1.41),(.57,.16,.90),burgundy,32,16)
 for s in [-1,1]:
  wing=g.sphere('Curving upholstered wing',(s*.52,3.31,1.63),(.19,.28,.68),burgundy,20,12);wing.rotation_euler.y=s*.13
  g.sphere('Rolled velvet arm',(s*.54,3.0,.94),(.13,.49,.13),burgundy,24,10)
  path('Gold stitched chair silhouette',[(s*.49,3.27,.73),(s*.63,3.30,1.60),(s*.60,3.37,2.18),(s*.45,3.38,2.29)],.014,gold)
 for x in [-.25,0,.25]:
  for z in [1.1,1.4,1.7]:g.sphere('Chair tuft button',(x,3.228,z),(.027,.018,.027),gold,10,6)
 # Two narrow filled tea cupboards and a stepped collection of orbs.
 for side in [-1,1]:
  x=side*4.55;table(x,4.80,.82,1.15,.62,'Tea cabinet base')
  box('Tea cabinet back',(x,5.18,2.05),(1.24,.10,2.7),wood,.02)
  for xx in [x-.62,x+.62]:box('Tea cabinet side',(xx,4.99,2.05),(.10,.52,2.7),wood,.015)
  for z in [.92,1.53,2.14,2.75,3.36]:box('Tea cabinet shelf',(x,4.97,z),(1.2,.52,.06),woodlight,.012)
  for z in [.96,1.57,2.18,2.79]:
   for j in range(4):
    cx=x-.43+j*.28;g.lathe('Stack of chipped teacups',(cx,4.86,z),[(.045,0),(.09,.04),(.11,.13),(.09,.14),(.065,.055)],cream,14)
    path('Tiny cup handle',[(cx+.10,4.86,z+.04),(cx+.15,4.86,z+.05),(cx+.15,4.86,z+.11),(cx+.10,4.86,z+.12)],.012,bronze)
  bottle(x,4.86,.94,.35,.14,1)
 table(-1.65,4.80,.76,.75,.75,'Crystal reading stand');ball(-1.65,4.80,.84,.25)
 for row in range(3):
  box('Stepped orb bench',(2.15,4.72+row*.22,.30+row*.24),(1.60,.31,.10),wood,.015)
  for k in range(4-row):ball(1.55+k*.36+row*.17,4.72+row*.22,.36+row*.24,.11)
 for x in [-.76,.76]:candle(x,4.65,.24,.60)
 g.collection('05 Lighting')
 for x in [-4.8,4.8]:g.area('Warm tall window spill',(x,1.5,3.7),(0,1,1),1350,(1,.79,.55),3.2)
 g.area('Back windows warm wash',(0,5.25,4.7),(0,-1,1),1100,(1,.72,.46),4)
 g.area('Soft front bounced light',(0,-4.6,4.2),(0,2,1.5),600,(.78,.60,.52),5)
 g.area('Canopy bounced fill',(0,.0,5.7),(0,0,1),450,(1,.48,.32),4)
 cams=[('占卜课全景',(0,-5.28,2.80),(0,2.65,2.30),22),('水晶球与绣毯',(-.3,-2.55,1.85),(3.0,.2,1.0),26),('高窗与翼椅',(-2.0,1.50,2.2),(.3,4.0,1.8),27)]
 obs=[(x-1.05,x+1.05,y-1.23,y+.90) for x,y in positions]+[(-.77,.77,2.5,3.7),(-5.1,-3.95,4.35,5.4),(3.95,5.1,4.35,5.4),(-2.06,-1.24,4.37,5.22),(1.25,3.05,4.35,5.4)]
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
S.render.image_settings.file_format='PNG';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'scene.blend'))
bpy.ops.render.render(write_still=True)
print('CLASSROOM_BUILD_COMPLETE',ID,len(S.objects),flush=True)
