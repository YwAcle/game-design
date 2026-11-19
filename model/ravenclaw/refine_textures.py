"""Generate the V2 authored cloth and stone surfaces (no reference-image pixels)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import random, math
root=Path(__file__).resolve().parent.parent
for room in ['ravenclaw','hufflepuff']:
    random.seed(171)
    out=root/room/'textures'
    for name,base in [('yellow',(150,139,88)),('stone',(145,139,119)),('ivory',(181,183,175)),('blue',(39,56,77))]:
        im=Image.new('RGB',(768,768),base);d=ImageDraw.Draw(im,'RGBA')
        # Hand-placed broad tonal patches followed by short directional brush hatching.
        for k in range(240):
            x=random.randrange(768);y=random.randrange(768);w=random.randint(10,120);h=random.randint(5,45)
            d.polygon([(x,y),(x+w,y+random.randint(-6,6)),(x+w*.7,y+h),(x+5,y+h*.8)],fill=(255,244,219,random.randint(2,10)) if k%2 else (28,30,23,random.randint(2,12)))
        for k in range(9500):
            x=random.randrange(768);y=random.randrange(768);l=random.randint(3,22)
            d.line((x,y,x+l,y+random.randint(-2,2)),fill=(230,225,195,random.randrange(3,19)) if k%3 else (23,28,23,random.randrange(6,25)),width=1)
        if name in ['yellow','blue']:
            # A subdued, worn woven vine pattern rather than high-contrast new stripes.
            ink=(65,68,43,36) if name=='yellow' else (143,149,137,24)
            for yy in range(30,768,108):
                for xx in range(30,768,108):
                    x=xx+(54 if (yy//108)%2 else 0)
                    pts=[(x+7*math.sin(t*.26),yy+t) for t in range(-35,36)]
                    d.line(pts,fill=ink,width=2)
                    for t in [-23,0,23]:
                        for s in [-1,1]:
                            d.polygon([(x,yy+t),(x+s*15,yy+t-17),(x+s*23,yy+t-10),(x+s*16,yy+t+1)],fill=ink)
            for y in range(0,768,3):d.line((0,y,768,y),fill=(225,223,200,9),width=1)
            for x in range(0,768,4):d.line((x,0,x,768),fill=(15,25,25,7),width=1)
            for k in range(45):
                x=random.randrange(768);y=random.randrange(768)
                d.line((x,y,x+random.randrange(4,22),y+random.randrange(2,8)),fill=(36,35,26,47),width=1)
        im.save(out/(name+'.jpg'),quality=95)
print('V2_TEXTURES_COMPLETE')
