"""Original painted-style textiles, wood, limestone and decorative illustrations."""
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
import math, random
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
random.seed(267)
N=1536
def star(d,c,r,fill,points=8,inner=.36,outline=None):
    x,y=c;p=[]
    for i in range(points*2):
        a=math.pi*i/points-math.pi/2; rr=r if i%2==0 else r*inner;p.append((x+rr*math.cos(a),y+rr*math.sin(a)))
    d.polygon(p,fill=fill,outline=outline)
def save(im,name):
    for scene in ['ravenclaw','hufflepuff']:
        p=ROOT/scene/'textures';p.mkdir(parents=True,exist_ok=True);im.save(p/name)
for kind,col in [('stone',(166,151,125)),('ivory',(195,188,168)),('wood',(98,62,31)),('blue',(39,60,92)),('yellow',(178,139,51)),('green',(58,83,32))]:
    im=Image.new('RGB',(768,768),col);d=ImageDraw.Draw(im,'RGBA')
    for i in range(10000):
        x=random.randrange(768);y=random.randrange(768);v=random.choice([-1,1]);a=random.randint(4,20);l=random.randint(8,95) if kind=='wood' else random.randint(3,35)
        d.line((x,y,x+l,y+random.randint(-4,4)), fill=(240,220,180,a) if v>0 else (20,13,8,a),width=random.randint(1,4))
    if kind=='wood':
        for i in range(180):
            y=random.randrange(768);pts=[(x,y+math.sin(x*.018+i)*random.uniform(1,5)) for x in range(0,769,12)];d.line(pts,fill=(30,20,10,60),width=1)
    save(im,kind+'.jpg')
for raven in [True,False]:
    bg=(78,96,136) if raven else (161,155,120);ink=(34,51,88) if raven else (81,78,54);gold=(177,164,119) if raven else (118,99,62)
    im=Image.new('RGB',(N,N),bg);d=ImageDraw.Draw(im,'RGBA');c=N/2
    for i in range(11000):
        x=random.randrange(N);y=random.randrange(N);d.line((x,y,x+random.randrange(3,13),y),fill=(*ink,random.randrange(10,45)),width=1)
    for r,w in [(740,8),(720,3),(700,9),(675,3),(520,7),(500,3),(470,3),(280,5),(260,3)]:d.ellipse((c-r,c-r,c+r,c+r),outline=ink,width=w)
    for k in range(48):
        a=k*math.tau/48;r=688;x=c+r*math.cos(a);y=c+r*math.sin(a)
        star(d,(x,y),13,gold,points=4,inner=.4)
        a=k*math.tau/48;r=490;x=c+r*math.cos(a);y=c+r*math.sin(a)
        d.arc((x-17,y-17,x+17,y+17),0,300,fill=ink,width=3)
    for k in range(16):
        a=k*math.tau/16;aa=a+.03
        d.line((c+285*math.cos(a),c+285*math.sin(a),c+655*math.cos(a),c+655*math.sin(a)),fill=ink,width=2)
        star(d,(c+595*math.cos(aa+.13),c+595*math.sin(aa+.13)),25,gold,points=8 if raven else 4)
    if raven:
        star(d,(c,c),250,ink,points=16,inner=.23)
        star(d,(c,c),228,gold,points=8,inner=.20)
        star(d,(c,c),145,bg,points=8,inner=.30)
        for k in range(12):
            a=k*math.tau/12;star(d,(c+375*math.cos(a),c+375*math.sin(a)),23,ink)
    else:
        for r,w in [(635,8),(606,3),(560,7)]:d.polygon([(c,c-r),(c+r,c),(c,c+r),(c-r,c),(c,c-r)],outline=gold,width=w)
        for k in range(12):
            a=k*math.tau/12;x=c+355*math.cos(a);y=c+355*math.sin(a)
            for j in range(6):
                q=j*math.tau/6;xx=x+28*math.cos(q);yy=y+28*math.sin(q);d.ellipse((xx-19,yy-12,xx+19,yy+12),outline=gold,width=3)
        star(d,(c,c),230,gold,points=8,inner=.48);star(d,(c,c),195,bg,points=8,inner=.45)
    p=ROOT/('ravenclaw' if raven else 'hufflepuff')/'textures/rug.png';im.save(p)
for i in range(4):
    im=Image.new('RGB',(384,512),[(36,54,60),(38,44,72),(65,44,33),(39,60,33)][i]);d=ImageDraw.Draw(im)
    for j in range(25):
        y=j*23;d.polygon([(0,y),(384,y-60),(384,y+4),(0,y+60)],fill=(45+i*4,51+i*2,46))
    d.polygon([(45,512),(70,340),(128,297),(256,296),(315,353),(341,512)],fill=[(63,78,107),(97,52,37),(122,94,48),(42,72,60)][i])
    d.polygon([(144,313),(154,267),(228,267),(242,318),(196,366)],fill=(193,164,118))
    d.ellipse((123,119,267,298),fill=(69,52,38));d.polygon([(143,143),(226,133),(248,188),(234,264),(204,287),(163,263),(139,222)],fill=(204,179,136))
    d.polygon([(125,178),(138,116),(204,91),(254,134),(267,194),(228,153),(178,155)],fill=(70+i*10,57+i*9,43+i*8))
    d.line((157,203,178,198),fill=(55,47,37),width=5);d.line((211,198,231,203),fill=(55,47,37),width=5)
    d.line((197,208,189,235,203,239),fill=(131,104,78),width=3);d.line((182,258,213,257),fill=(105,66,51),width=3)
    d.polygon([(139,309),(195,365),(172,404),(107,330)],fill=(183,165,122));d.polygon([(244,309),(195,365),(216,404),(283,337)],fill=(183,165,122))
    for k in range(17):
        y=390+k*7;d.line((190,y,205,y),fill=(180,146,81),width=2)
    save(im,f'portrait{i}.png')
print('TEXTURES_COMPLETE')
