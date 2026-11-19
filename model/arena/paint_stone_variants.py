"""Original broad painted stone planes, five variants for the V2 arena."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import random
out=Path(__file__).resolve().parent/'textures'
N=1024
for variant in range(5):
    rng=random.Random(900+variant)
    base=(118+variant*4,122+variant*3,118+variant*3)
    im=Image.new('RGB',(N,N),base)
    # Designed low-frequency planes avoid the previous cloudy noise texture.
    layer=Image.new('RGBA',(N,N));d=ImageDraw.Draw(layer)
    for i in range(35):
        x=rng.randrange(-80,N);y=rng.randrange(-80,N);w=rng.randrange(80,340);h=rng.randrange(25,160)
        col=(183,177,155,rng.randrange(5,20)) if i%3 else (40,44,43,rng.randrange(6,18))
        pts=[(x,y),(x+w*.8,y+rng.randrange(-20,20)),(x+w,y+h*.5),(x+w*.75,y+h),(x+w*.13,y+h*.8)]
        d.polygon(pts,fill=col)
    im=Image.alpha_composite(im.convert('RGBA'),layer.filter(ImageFilter.GaussianBlur(2)))
    d=ImageDraw.Draw(im)
    for side in [0,1]:
        for i in range(4):
            a=18+i*3;shade=(183,180,162,180-i*30) if side==0 else (57,64,61,150-i*25)
            pts=[(a,N-a),(a,a),(N-a,a)] if side==0 else [(a,N-a),(N-a,N-a),(N-a,a)]
            d.line(pts,fill=shade,width=3)
    for i in range(5):
        x=rng.randrange(70,N-70);y=rng.randrange(70,N-70)
        pts=[(x,y),(x+rng.randrange(-40,40),y+36),(x+rng.randrange(-60,60),y+83)]
        d.line(pts,fill=(55,61,57,255),width=2)
        d.line([(a+2,b+2) for a,b in pts],fill=(152,153,135,255),width=1)
    for i in range(18):
        x=rng.randrange(40,980);y=rng.randrange(40,980)
        d.line([(x,y),(x+rng.randrange(12,68),y+rng.randrange(-4,5))],fill=(155,155,138,255),width=1)
    im.convert('RGB').save(out/f'stone{variant}.jpg',quality=94)
print('ARENA_STONE_VARIANTS_COMPLETE')

# Broad old plaster strokes without the V1 cloudy high-frequency mottling.
rng=random.Random(218)
im=Image.new('RGB',(1024,1024),(106,109,103));layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer)
for i in range(85):
    x=rng.randrange(-100,1050);y=rng.randrange(-80,1050);w=rng.randrange(80,320);h=rng.randrange(20,135)
    col=(178,174,152,rng.randrange(6,17)) if i%2 else (42,47,44,rng.randrange(6,15))
    d.polygon([(x,y),(x+w,y+8),(x+w*.82,y+h),(x+12,y+h*.9)],fill=col)
im=Image.alpha_composite(im.convert('RGBA'),layer.filter(ImageFilter.GaussianBlur(3))).convert('RGB')
im.save(out/'plaster.jpg',quality=95)
