from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, random, math
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent if HERE.name in ['gryffindor','slytherin'] else HERE.parents[1]/'outputs/hogwarts-complete/model'
N=1024
for room in ([HERE.name] if HERE.name in ['gryffindor','slytherin'] else ['gryffindor','slytherin']):
    out=ROOT/room/'textures'; out.mkdir(exist_ok=True,parents=True)
    random.seed(233);rng=np.random.default_rng(233)
    def paint(name,base,wood=False):
        broad=np.asarray(Image.fromarray(rng.normal(0,8,(24,24)).astype('float32')).resize((N,N),Image.Resampling.BICUBIC))
        y,x=np.mgrid[:N,:N];v=broad+rng.normal(0,1.4,(N,N))
        if wood:v+=3*np.sin(x*.16+2*np.sin(y*.008))+2*np.sin(x*.53)
        im=Image.fromarray(np.stack([np.clip(c+v,0,255) for c in base],axis=2).astype('uint8'));d=ImageDraw.Draw(im,'RGBA')
        for _ in range(260):
            x=random.randrange(N);y=random.randrange(N);l=random.randrange(10,190)
            d.line([(x,y),(x+random.randrange(-8,9),y+l)] if wood else [(x,y),(x+l,y+random.randrange(-10,11))],fill=(205,200,160,random.randrange(10,30)),width=random.randrange(1,4))
        if name=='stone':
            for _ in range(10):
                x=random.randrange(N);y=random.randrange(N);pts=[(x,y)]
                for _ in range(4):x+=random.randrange(-25,26);y+=random.randrange(10,45);pts.append((x,y))
                d.line(pts,fill=(35,40,35,65),width=2)
            d.rectangle((4,4,1019,1019),outline=(20,25,23,48),width=8)
        im.save(out/(name+'.jpg'),quality=93)
    paint('stone',(128,123,104) if room=='gryffindor' else (93,116,109))
    paint('wood',(101,71,44) if room=='gryffindor' else (55,68,59),True)
    paint('cloth',(121,77,69) if room=='gryffindor' else (68,112,103),True)
    base=(108,43,35) if room=='gryffindor' else (38,74,65)
    gold=(192,151,82) if room=='gryffindor' else (125,160,139)
    rug=Image.new('RGB',(1536,1024),base);d=ImageDraw.Draw(rug)
    for inset,w in [(12,3),(28,8),(56,3),(78,2),(115,5),(135,2)]:d.rounded_rectangle((inset,inset,1535-inset,1023-inset),radius=50,outline=gold,width=w)
    for x in range(170,1400,80):
        for y in [84,940]:d.polygon([(x-22,y),(x,y-20),(x+22,y),(x,y+20)],outline=gold,width=3)
    for y in range(180,900,75):
        for x in [85,1450]:d.polygon([(x-20,y),(x,y-23),(x+20,y),(x,y+23)],outline=gold,width=3)
    for x in [260,1276]:
        for y in [230,794]:
            pts=[]
            for j in range(180):
                a=j/179*math.pi*4;r=3+j*.32;pts.append((x+math.cos(a)*r,y+math.sin(a)*r))
            d.line(pts,fill=gold,width=5)
    for scale in [1,.8,.6]:
        d.polygon([(768,200+290*(1-scale)),(768+400*scale,512),(768,824-290*(1-scale)),(768-400*scale,512)],outline=gold,width=4)
    for i in range(75):
        x=random.randrange(1536);y=random.randrange(1024);d.line((x,y,x+random.randrange(20,70),y+1),fill=base,width=1)
    rug.save(out/'rug.jpg',quality=95)
    # Original stylised painted portraits, deliberately no official image sampling.
    for p in range(5):
        im=Image.new('RGB',(512,768),(42+p*3,40+p*2,33));d=ImageDraw.Draw(im)
        d.ellipse((80,30,450,690),fill=(64+p*3,55,40))
        d.polygon([(40,768),(110,490),(200,430),(330,430),(460,600),(510,768)],fill=(45,47,42))
        d.polygon([(200,440),(265,600),(330,440),(300,720),(200,768)],fill=(133,93,50))
        d.ellipse((170,170,355,450),fill=(156+p*7,131+p*4,99+p*3))
        d.polygon([(167,200),(190,115),(305,108),(360,190),(344,290),(316,198),(220,175),(183,290)],fill=(67+p*8,65+p*6,53+p*6))
        d.polygon([(270,270),(294,339),(263,342)],fill=(111,87,65))
        d.line([(205,270),(238,274)],fill=(56,48,37),width=7);d.line([(300,272),(331,269)],fill=(56,48,37),width=7)
        d.line([(245,375),(294,373)],fill=(79,53,39),width=5)
        if p%2:d.polygon([(190,340),(215,428),(279,480),(333,400),(344,331),(300,376),(248,400)],fill=(163,153,129))
        im.save(out/f'portrait{p}.jpg',quality=92)
    # Repeating original tapestry of branching trees and tiny heraldic animals.
    im=Image.new('RGB',(768,1024),(76,31,28));d=ImageDraw.Draw(im)
    for x in [120,380,650]:
        d.line([(x,970),(x+18,370)],fill=(97,79,42),width=15)
        for y in range(380,900,100):
            d.line([(x+10,y),(x-64,y-60)],fill=(97,79,42),width=8);d.line([(x+10,y-20),(x+75,y-90)],fill=(97,79,42),width=8)
            for xx in [-65,70]:d.ellipse((x+xx-40,y-140,x+xx+40,y-65),fill=(44,56,36))
        for y in [280,720]:
            d.ellipse((x-35,y,x+20,y+28),fill=(175,139,71));d.line([(x-25,y+20),(x-40,y+58)],fill=(175,139,71),width=7);d.line([(x+10,y+20),(x+35,y+50)],fill=(175,139,71),width=7);d.polygon([(x+15,y+12),(x+25,y-25),(x+45,y-15),(x+40,y+14)],fill=(175,139,71))
    im.save(out/'tapestry.jpg',quality=95)
print('TEXTURES_COMPLETE')

# V2: Original painted surfaces, no sampling from official game imagery.
for room in ([HERE.name] if HERE.name in ['gryffindor','slytherin'] else ['gryffindor','slytherin']):
    out=ROOT/room/'textures'; random.seed(991 if room=='gryffindor' else 995)
    def worn(im,amount=3):
        a=np.asarray(im).astype('float32');yy,xx=np.mgrid[:im.height,:im.width]
        low=np.asarray(Image.fromarray(np.random.default_rng(19).normal(0,amount,(30,30)).astype('float32')).resize(im.size,Image.Resampling.BICUBIC))
        a+=low[:,:,None]
        return Image.fromarray(np.uint8(np.clip(a,0,255)))
    # Linen weave and a restrained damask repeat replace the old wood-like fabric.
    base=(116,72,53) if room=='gryffindor' else (55,88,77)
    cloth=Image.new('RGB',(1024,1024),base);d=ImageDraw.Draw(cloth,'RGBA')
    for y in range(0,1024,4):d.line((0,y,1024,y),fill=(200,175,126,12),width=1)
    for x in range(0,1024,3):d.line((x,0,x,1024),fill=(20,20,15,15),width=1)
    for y in range(0,1150,128):
        for x0 in range(-80,1100,128):
            x=x0+(64 if y%256 else 0)
            col=(178,130,82,28) if room=='gryffindor' else (131,166,139,30)
            for sx in [-1,1]:
                for sy in [-1,1]:d.polygon([(x,y),(x+sx*9,y+sy*27),(x+sx*28,y+sy*35),(x+sx*18,y+sy*9)],fill=col)
            d.ellipse((x-5,y-5,x+5,y+5),outline=col,width=2)
    worn(cloth).save(out/'cloth.jpg',quality=94)
    # Warped tartan with frayed ends, mapped to curved hanging geometry.
    tartan=Image.new('RGB',(1024,1024),(109,68,31));d=ImageDraw.Draw(tartan,'RGBA')
    for x in range(-100,1150,160):
        d.rectangle((x,0,x+53,1024),fill=(56,28,22,220));d.rectangle((x+72,0,x+86,1024),fill=(187,145,62,200));d.line((x+112,0,x+112,1024),fill=(218,181,95,200),width=4)
    for y in range(-60,1150,190):
        d.rectangle((0,y,1024,y+57),fill=(54,27,21,155));d.rectangle((0,y+78,1024,y+93),fill=(195,155,78,130));d.line((0,y+120,1024,y+120),fill=(216,183,118,170),width=4)
    for x in range(0,1024,4):d.line((x,0,x,1024),fill=(26,18,13,20))
    worn(tartan,5).save(out/'tartan.jpg',quality=94)
    # Complex woven borders / central foliate medallion in the room's palette.
    im=Image.open(out/'rug.jpg').convert('RGB');d=ImageDraw.Draw(im,'RGBA')
    ink=(184,135,74,170) if room=='gryffindor' else (109,145,125,150)
    for x,y in [(250,230),(1285,230),(250,790),(1285,790),(768,512)]:
        for j in range(12):
            a=j*math.pi/6;rr=74 if x==768 else 45
            leaf=[]
            for k in range(21):
                t=k*math.pi*2/20;r=rr*(.60+.37*math.cos(t));leaf.append((x+math.cos(a)*(24+r*math.cos(t))-math.sin(a)*r*.25*math.sin(t),y+math.sin(a)*(24+r*math.cos(t))+math.cos(a)*r*.25*math.sin(t)))
            d.line(leaf,fill=ink,width=3)
    for y in [154,866]:
        pts=[(x,y+11*math.sin(x*.035)) for x in range(155,1381,4)];d.line(pts,fill=ink,width=2)
        for x in range(180,1380,34):d.ellipse((x,y-5,x+8,y+4),fill=ink)
    worn(im,4).save(out/'rug.jpg',quality=95)
    # Individually drawn painted figures, with distinctive silhouettes and shaded planes.
    for p in range(5):
        im=Image.new('RGB',(768,1024),(31,32,29));d=ImageDraw.Draw(im)
        d.polygon([(0,0),(480,0),(600,1024),(0,1024)],fill=(48+p*2,44+p*2,34))
        d.polygon([(530,0),(768,0),(768,1024),(680,1024)],fill=(66,45,30))
        d.line([(550,0),(665,1024)],fill=(81,61,39),width=8)
        cx=370+(p%3-1)*24;headtop=202 if p!=2 else 240
        robe=[(30,1024),(78,756),(195,636),(cx-83,595),(cx+93,600),(622,727),(752,1024)]
        robes=[(51,50,40),(50,44,42),(44,58,48),(68,47,39),(42,48,57)]
        d.polygon(robe,fill=robes[p]);d.polygon([(cx-90,623),(cx-33,800),(cx-99,1024),(110,1024),(214,744)],fill=tuple(c+14 for c in robes[p]))
        d.polygon([(cx+76,620),(cx+166,762),(640,1024),(cx+37,1024),(cx+28,794)],fill=tuple(max(0,c-13) for c in robes[p]))
        for j in range(5):d.line([(245+j*24,790),(170+j*33,1024)],fill=tuple(c+8 for c in robes[p]),width=5)
        skin=(166+p*4,132+p*3,94+p*2)
        d.polygon([(cx-55,528),(cx+50,523),(cx+64,646),(cx,710),(cx-80,638)],fill=(116,90,62))
        d.polygon([(cx-115,headtop+72),(cx-97,headtop+242),(cx-53,headtop+344),(cx+35,headtop+363),(cx+94,headtop+267),(cx+111,headtop+84),(cx+63,headtop+19),(cx-50,headtop)],fill=skin)
        d.polygon([(cx+26,headtop+33),(cx+103,headtop+95),(cx+90,headtop+266),(cx+31,headtop+355),(cx-1,headtop+278)],fill=(128+p*4,99+p*3,69+p*2))
        d.polygon([(cx-88,headtop+127),(cx-31,headtop+83),(cx-16,headtop+166),(cx-38,headtop+213),(cx-88,headtop+205)],fill=(188+p*3,154+p*2,110+p*2))
        d.polygon([(cx-1,headtop+151),(cx+28,headtop+241),(cx-4,headtop+252),(cx-24,headtop+238)],fill=(103,77,53))
        d.line([(cx-7,headtop+172),(cx-7,headtop+226),(cx-22,headtop+237)],fill=(195,159,111),width=5)
        for side in [-1,1]:
            ex=cx+side*52;ey=headtop+170+(4 if side>0 else 0)
            d.polygon([(ex-28,ey),(ex-8,ey-8),(ex+22,ey+1),(ex+3,ey+10)],fill=(74,63,45))
            d.line((ex-19,ey+2,ex+14,ey+2),fill=(189,174,135),width=3)
            d.ellipse((ex-4,ey-1,ex+3,ey+7),fill=(32,34,28));d.line((ex-26,ey-20,ex+17,ey-16),fill=(65,57,43),width=6)
        d.line([(cx-33,headtop+285),(cx-8,headtop+282),(cx+27,headtop+287)],fill=(79,54,39),width=5)
        d.line([(cx-20,headtop+297),(cx+18,headtop+300)],fill=(179,139,95),width=4)
        hair=[(74,67,48),(145,141,118),(48,42,30),(111,91,59),(161,158,137)][p]
        d.polygon([(cx-112,headtop+163),(cx-132,headtop+48),(cx-71,headtop-30),(cx+47,headtop-36),(cx+122,headtop+42),(cx+108,headtop+186),(cx+74,headtop+87),(cx-18,headtop+35),(cx-89,headtop+92)],fill=hair)
        for j in range(10):d.line([(cx-110+j*20,headtop+18),(cx-89+j*17,headtop+75)],fill=tuple(min(255,c+19) for c in hair),width=4)
        if p in [1,4]:
            d.polygon([(cx-91,headtop+249),(cx-53,headtop+280),(cx,headtop+307),(cx+63,headtop+260),(cx+64,headtop+348),(cx+5,headtop+450),(cx-65,headtop+377)],fill=hair)
            for j in range(9):d.line([(cx-63+j*15,headtop+308),(cx-38+j*8,headtop+402)],fill=tuple(max(0,c-22) for c in hair),width=3)
        if p==2:
            d.polygon([(cx-160,headtop+12),(cx-76,headtop-85),(cx-18,headtop-206),(cx+40,headtop-160),(cx+111,headtop-20),(cx+160,headtop+34)],fill=(54,58,44))
            d.line([(cx-120,headtop-2),(cx+103,headtop+19)],fill=(144,112,58),width=13)
        d.polygon([(cx-78,628),(cx-13,727),(cx-38,774),(cx-116,661)],fill=(179,164,125))
        d.polygon([(cx+68,628),(cx+3,727),(cx+32,772),(cx+106,663)],fill=(147,132,98))
        for yy in range(811,1000,67):d.ellipse((cx-6,yy,cx+8,yy+14),fill=(141,112,63))
        # Thin irregular brush strokes remain a painting surface, not photographic grain.
        d=ImageDraw.Draw(im,'RGBA')
        for j in range(320):
            x=random.randrange(768);y=random.randrange(1024)
            d.line((x,y,x+random.randrange(-6,10),y+random.randrange(6,39)),fill=(167,144,96,random.randrange(4,17)),width=random.randrange(1,4))
        worn(im,2).save(out/f'portrait{p}.jpg',quality=95)
print('REFINED_PAINTING_COMPLETE')

