"""Original painted texture studies; no game textures are used."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import random, math, numpy as np
OUT=Path(__file__).parent/'textures';OUT.mkdir(exist_ok=True)
random.seed(71);rng=np.random.default_rng(71);N=1024

def surface(name,base,grain=False):
    small=rng.normal(0,8,(16,16)).astype('float32')
    broad=np.asarray(Image.fromarray(small).resize((N,N),Image.Resampling.BICUBIC))
    fine=rng.normal(0,1.5,(N,N));y,x=np.mgrid[:N,:N]
    val=broad+fine
    if grain:val+=4*np.sin(x*.13+np.sin(y*.004)*3)+2*np.sin(x*.47)
    a=np.stack([np.clip(c+val,0,255) for c in base],axis=2).astype('uint8')
    im=Image.fromarray(a);d=ImageDraw.Draw(im,'RGBA')
    for i in range(280):
        x=random.randrange(N);y=random.randrange(N);length=random.randrange(6,150)
        d.line([(x,y),(x+random.randrange(-10,11),y+length)] if grain else [(x,y),(x+length,y+random.randrange(-15,16))],fill=(210,206,185,random.randrange(6,24)),width=random.randrange(1,5))
    if name=='stone':
        for i in range(7):
            x=random.randrange(N);y=random.randrange(N);pts=[(x,y)]
            for j in range(random.randrange(2,7)):
                x+=random.randrange(-35,36);y+=random.randrange(20,60);pts.append((x,y))
            d.line(pts,fill=(39,43,44,80),width=2)
        # Broad irregular edge shading and a light brushed rim.
        d.rectangle((6,6,N-7,N-7),outline=(37,42,42,70),width=8)
        d.line([(16,N-16),(16,16),(N-16,16)],fill=(195,191,172,70),width=4)
    im.save(OUT/(name+'.jpg'),quality=95)

surface('stone',(107,112,110));surface('plaster',(96,101,96));surface('oak',(58,49,43),True)
surface('cloth',(88,34,35),True)
im=Image.open(OUT/'cloth.jpg');d=ImageDraw.Draw(im,'RGBA')
for x in [64,79,944,959]:d.line([(x,0),(x,1024)],fill=(183,148,93,170),width=4)
for x in range(110,920,45):d.polygon([(x,45),(x+13,72),(x,99),(x-13,72)],outline=(170,130,75,100),width=2)
im.save(OUT/'banner.jpg',quality=95)
print('Original texture studies written to',OUT)
