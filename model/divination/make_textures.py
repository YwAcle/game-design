"""Original brush and textile studies. No official artwork is used as texture."""
from pathlib import Path
from PIL import Image,ImageDraw
import random,math,numpy as np
ROOT=Path(__file__).parent
if ROOT.name=='classrooms': ROOT=ROOT.parent.parent/'outputs/hogwarts-complete/model'
else: ROOT=ROOT.parent
for scene in ['potions','divination']:
 out=ROOT/scene/'textures';out.mkdir(parents=True,exist_ok=True)
 random.seed(351);rng=np.random.default_rng(351);N=512
 for name,base in [('stone',(119,111,99)),('wood',(81,48,34)),('cloth',(102,27,39)),('paper',(174,148,103)),('teal',(24,64,68))]:
  broad=np.asarray(Image.fromarray(rng.normal(0,7,(18,18)).astype('float32')).resize((N,N),Image.Resampling.BICUBIC))
  fine=rng.normal(0,1,(N,N));yy,xx=np.mgrid[:N,:N];v=broad+fine
  if name=='wood':v+=4*np.sin(xx*.21+np.sin(yy*.022)*2)+2*np.sin(xx*.57)
  a=np.stack([np.clip(c+v,0,255) for c in base],axis=2).astype('uint8');im=Image.fromarray(a);d=ImageDraw.Draw(im,'RGBA')
  for i in range(120):
   x=random.randrange(N);y=random.randrange(N);l=random.randrange(6,80)
   d.line([(x,y),(x+random.randrange(-4,5),y+l)] if name=='wood' else [(x,y),(x+l,y+random.randrange(-6,7))],fill=(219,199,155,random.randrange(8,26)),width=random.randrange(1,4))
  if name=='stone':
   d.rectangle((4,4,N-5,N-5),outline=(40,34,32,100),width=5)
   d.line([(7,N-8),(7,7),(N-8,7)],fill=(201,185,157,70),width=3)
   for i in range(3):
    x=random.randrange(N);y=random.randrange(N);d.line([(x,y),(x+8,y+25),(x-4,y+37),(x+14,y+55)],fill=(39,30,29,95),width=1)
  im.save(out/(name+'.jpg'),quality=94)
  if name in ['cloth','teal']:
   d=ImageDraw.Draw(im,'RGBA')
   for y in range(-64,N+64,80):
    for x in range(-64,N+64,80):
     x+=40 if (y//80)%2 else 0
     pts=[(x+15*math.cos(t*math.pi/4),y+24*math.sin(t*math.pi/4)) for t in range(9)]
     d.line(pts,fill=(197,149,66,105),width=2)
     d.ellipse((x-4,y-4,x+4,y+4),fill=(191,151,75,140))
     for s in [-1,1]:
      d.arc((x+s*12-14,y-16,x+s*12+14,y+16),20,320,fill=(191,151,75,90),width=1)
     d.line([(x-25,y-25),(x-13,y-20),(x-9,y-10)],fill=(191,151,75,90),width=2)
   im.save(out/(name+'-pattern.jpg'),quality=94)
 print('TEXTURES_READY',scene)
