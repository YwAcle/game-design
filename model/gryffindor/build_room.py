"""Original stylised interiors. Run in Blender 5.3; copied beside each room's assets."""
import bpy,bmesh,sys,os,math,random,json
from math import sin,cos,pi,sqrt
from mathutils import Vector
HERE=os.path.dirname(os.path.abspath(__file__));ROOT=os.path.dirname(os.path.dirname(HERE));ROOM=os.path.basename(HERE);SLY=ROOM=='slytherin'
sys.path.insert(0,HERE);import geometry as g
random.seed(404 if SLY else 316);bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);g.BOXES.clear();S=bpy.context.scene

def painted(name,color,tex=None,axis='XZ',rough=.9,metal=0):
    m=g.material(name,color,rough=rough,metal=metal)
    if tex:
        nt=m.node_tree;n=nt.nodes;l=nt.links;p=n.get('Principled BSDF');im=n.new('ShaderNodeTexImage');im.image=bpy.data.images.load(os.path.join(HERE,'textures',tex+'.jpg'),check_existing=True)
        co=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');comb=n.new('ShaderNodeCombineXYZ');l.new(co.outputs['Generated'],sep.inputs[0]);l.new(sep.outputs[axis[0]],comb.inputs['X']);l.new(sep.outputs[axis[1]],comb.inputs['Y']);l.new(comb.outputs[0],im.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.28;mix.inputs[2].default_value=(*color,1);l.new(im.outputs['Color'],mix.inputs[1]);l.new(mix.outputs[0],p.inputs['Base Color'])
    return m
STONE=painted('Stone painted broad strokes',(.35,.46,.41) if SLY else (.56,.46,.31),'stone')
FLOORSTONE=painted('Flagstone face brushwork',(.35,.46,.41) if SLY else (.56,.46,.31),'stone','XY')
TRIM=painted('Carved stone highlights',(.40,.48,.42) if SLY else (.70,.59,.39),'stone')
DARK=painted('Deep recess',(.025,.041,.035) if SLY else (.045,.027,.017))
WOOD=painted('Oak broad grain',(.20,.28,.22) if SLY else (.42,.25,.13),'wood')
RIM=painted('Oak rubbed edges',(.36,.43,.31) if SLY else (.61,.39,.17),'wood')
GOLD=painted('Aged brass',(.44,.47,.27) if SLY else (.42,.26,.085),metal=.22)
IRON=painted('Black iron',(.024,.033,.030),metal=.4)
CLOTH=painted('Tufted teal leather' if SLY else 'Oxblood upholstery',(.26,.44,.39) if SLY else (.42,.24,.22),'cloth')
CLOTHLIGHT=painted('Raised fabric folds',(.36,.57,.49) if SLY else (.56,.35,.29),'cloth')
SEAM=painted('Upholstery seams',(.09,.18,.15) if SLY else (.26,.08,.045))
PAPER=painted('Old parchment',(.65,.62,.43));BOOKS=[painted('Book cloth '+str(i),c) for i,c in enumerate([(.20,.08,.04),(.14,.23,.17),(.40,.30,.10),(.11,.16,.18),(.34,.16,.13)])]
GLASS=g.material('Glow | green leaded panes' if SLY else 'Glow | cloudy leaded panes',(.19,.47,.36) if SLY else (.23,.37,.30),rough=.8,emission=.34 if SLY else .28)
LAMP=g.material('Glow | opal lamp',(.39,.67,.47) if SLY else (1,.65,.20),rough=.8,emission=1.65 if SLY else 2.2)
FLAME=g.material('Glow | hearth fire',(1,.32,.035),rough=.7,emission=5)
FIRECORE=g.material('Glow | fire gold',(1,.68,.07),rough=.7,emission=6)
RUG=painted('Original woven carpet',(.7,.7,.7),'rug','XY')

def extrude(name,pts,depth,loc,mat,angle=0,bevel=0):
    vs=[g.tf(loc,u,d,z,angle) for d in [-depth/2,depth/2] for u,z in pts];n=len(pts);fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    o=g.mesh(name,vs,fs,mat)
    if bevel:
        mod=o.modifiers.new('Hand softened silhouette','BEVEL');mod.width=bevel;mod.segments=2;bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False)
    return o
def ring(name,loc,r,z,mat,thick=.05,n=32):return g.path(name,[(loc[0]+r*cos(i*2*pi/n),loc[1]+r*sin(i*2*pi/n),z) for i in range(n)],thick,mat,True)
def rod(name,a,b,r,mat):
    a,b=Vector(a),Vector(b);o=g.cyl(name,(a+b)/2,r,(b-a).length,mat,12);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def localbox(name,c,u,d,z,dim,mat,ang=0,bevel=.025):return g.box(name,g.tf(c,u,d,z,ang),dim,mat,bevel,ang)
def localsphere(name,c,u,d,z,scale,mat,ang=0):
    o=g.sphere(name,g.tf(c,u,d,z,ang),scale,mat,12,6);o.rotation_euler.z=ang;return o
def scroll(name,c,r,mat,angle=0):
    pts=[]
    for i in range(44):
        a=i/43*pi*3.4;rr=r*(1-i/50);pts.append(g.tf(c,rr*cos(a),-.03,rr*sin(a),angle))
    g.path(name,pts,.035,mat)
def book(name,c,w=.30,d=.22,h=.08,angle=0,standing=False):
    if standing:
        localbox(name+' pages',c,0,0,h/2,(w*.78,d*.86,h*.92),PAPER,angle,.004)
        for s in [-1,1]:localbox(name+' cover',c,s*w*.48,0,h/2,(.025,d,h),random.choice(BOOKS),angle,.005)
        localbox(name+' spine',c,0,-d*.46,h/2,(w,.035,h),random.choice(BOOKS),angle,.004)
        for z in [h*.15,h*.25,h*.78,h*.86]:localbox(name+' gilded band',c,0,-d*.49,z,(w,.014,.012),GOLD,angle,.003)
    else:
        localbox(name+' pages',c,0,0,h/2,(w*.94,d*.91,h*.72),PAPER,angle,.005)
        mat=random.choice(BOOKS)
        for z in [.006,h]:localbox(name+' cover',c,0,0,z,(w,d,.018),mat,angle,.005)
        localbox(name+' spine',c,-w/2+.01,0,h/2,(.025,d,h),mat,angle,.004)
def candle(c,h=.38,green=False):
    g.lathe('Turned candlestick',c,[(.12,0),(.12,.025),(.04,.08),(.035,.24),(.085,.28),(.09,.31)],GOLD,12)
    g.cyl('Wax taper',(c[0],c[1],c[2]+.31+h/2),.038,h,PAPER,10)
    g.sphere('Candle flame',(c[0],c[1],c[2]+.35+h),(.045,.045,.12),LAMP,10,5)
def trophy(c,scale=1):
    o=g.lathe('Chased trophy cup',c,[(.19,0),(.19,.07),(.065,.10),(.055,.28),(.12,.35),(.23,.43),(.25,.67),(.27,.71)],GOLD,16);o.scale=(scale,scale,scale)
    for side in [-1,1]:g.path('Trophy handle',[(c[0]+side*(.22+.12*sin(i*pi/12))*scale,c[1],c[2]+(.64-i*.025)*scale) for i in range(13)],.025*scale,GOLD)
def portrait(c,w,h,p,angle=0):
    mat=painted('Painted portrait '+str(p),(.9,.9,.9),'portrait'+str(p),'XZ')
    localbox('Original wizard portrait',c,0,0,h/2,(w,.06,h),mat,angle,.005)
    for inset,thick,dep in [(0,.06,.11),(.08,.03,.14),(-.08,.045,.09)]:
        for u in [-w/2-inset,w/2+inset]:localbox('Gilded portrait frame',c,u,-dep/2,h/2,(thick,dep,h+.18+2*inset),GOLD,angle,.012)
        for z in [-inset,h+inset]:localbox('Gilded portrait frame',c,0,-dep/2,z,(w+.15+2*inset,dep,thick),GOLD,angle,.012)
    for u in [-w/2,w/2]:
        for z in [0,h]:scroll('Frame curled leaf',g.tf(c,u,-.13,z,angle),.12,GOLD,angle)
def window(x,y,z,w,h):
    c=(x,y,z);pts=g.arch_points(w,h)
    extrude('Leaded glass arch',pts,.05,(x,y+.12,z),GLASS)
    for off in [0,.17,.31]:g.arch_frame('Splayed pointed stone reveal',c,w+off*2,h+off,.075 if off<.3 else .095,TRIM)
    for u in [-w*.18,w*.18]:rod('Window mullion',g.tf(c,u,-.06,.02),g.tf(c,u,-.06,g.arch_height(u,w,h)-.06),.032,IRON)
    step=.37 if SLY else .29
    for b in [i*step for i in range(-24,30)]:
        for sign in [-1,1]:
            pts=[]
            for i in range(121):
                u=-w/2+i*w/120;zz=sign*u+b
                if .03<zz<g.arch_height(u,w,h)-.04:pts.append(g.tf(c,u,-.09,zz))
            if len(pts)>1:rod('Diamond leaded lattice',pts[0],pts[-1],.014 if SLY else .012,IRON)
    for z0,ww,dd in [(-.08,w+.5,.65),(-.23,w+.36,.48)]:g.box('Stepped window sill',(x,y-.10,z+z0),(ww,dd,.14),TRIM,.018)
    g.area('Window luminous fill',(x,y-.2,z+h*.50),(x*.5,0,1.8),150 if SLY else 100,(.43,.74,.58) if SLY else (.57,.69,.51),w)
def chair(c,w=1.45,ang=0,wing=False,variant=0):
    # Shaped upholstery, scroll arms, cabriole legs, raised piping and real button tufts.
    backh=(1.75 if wing else 1.38)+[0,.13,-.12,.06][variant%4]
    for u in [-w*.39,w*.39]:
        for d in [-.42,.40]:
            pts=[g.tf(c,u,d,.06,ang),g.tf(c,u*1.04,d,.20,ang),g.tf(c,u*.93,d,.40,ang),g.tf(c,u,d,.59,ang)];g.path('Curved carved furniture leg',pts,.055,WOOD)
    localbox('Upholstered seat base',c,0,0,.56,(w,1.06,.25),CLOTH,ang,.10)
    localbox('Stuffed seat cushion',c,0,-.08,.78,(w-.26,.82,.23),CLOTHLIGHT,ang,.10)
    outline=[(-w*.48,.59),(-w*.52,backh*.78),(-w*.38,backh+.17),(-w*.20,backh+.24),(0,backh+.28),(w*.20,backh+.24),(w*.38,backh+.17),(w*.52,backh*.78),(w*.48,.59)]
    extrude('Shaped tufted back',outline,.25,g.tf(c,0,.43,0,ang),CLOTH,ang,.045)
    g.path('Back hand stitched piping',[g.tf(c,u,.285,z,ang) for u,z in outline],.021,RIM if not SLY else CLOTHLIGHT,True)
    for side in [-1,1]:
        u=side*(w*.48)
        localbox('Stuffed side bolster',c,u,0,.98,(.25,1.04,.40),CLOTH,ang,.11)
        cyl=g.cyl('Rolled leather arm',g.tf(c,u,-.07,1.17,ang),.19,1.07,CLOTHLIGHT,16);cyl.rotation_euler=(pi/2,0,ang)
        scroll('Carved arm scroll',g.tf(c,u,-.64,1.17,ang),.14,RIM if not SLY else SEAM,ang)
        if wing:extrude('High flared wing',[(-.12,1.06),(-.15,1.67),(.02,2.01),(.16,1.78),(.12,1.00)],.38,g.tf(c,u,.25,0,ang),CLOTH,ang,.04)
    # Diamond seam layout follows the front plane of the back.
    for row in range(3):
        zz=.95+row*.28
        for j in range(max(2,round(w/.35))):
            uu=-w*.32+j*(w*.64/max(1,round(w/.35)-1))
            if zz<backh+.05:
                localsphere('Tufted covered button',c,uu,.275,zz,(.033,.022,.033),GOLD if not SLY else SEAM,ang)
                if SLY:
                    for s in [-1,1]:g.path('Diamond upholstery seam',[g.tf(c,uu-.16,.282,zz-s*.14,ang),g.tf(c,uu,.263,zz,ang),g.tf(c,uu+.16,.282,zz+s*.14,ang)],.009,SEAM)
    # Cushions are shaped soft objects, with a contrasting stitched edge.
    p=localbox('Loose embroidered cushion',c,-w*.18,.10,1.04,(.55,.23,.50),CLOTHLIGHT,ang,.11);p.rotation_euler.y=.18+variant*.1
    if variant%2:
        p=localbox('Second slouched cushion',c,w*.25,.03,.97,(.42,.26,.40),CLOTH,ang,.1);p.rotation_euler.y=-.24
    for i in range(5):g.path('Cushion running embroidery',[g.tf(c,-w*.18-.19+i*.09,-.025,.85,ang),g.tf(c,-w*.18-.15+i*.09,-.025,1.03,ang),g.tf(c,-w*.18-.19+i*.09,-.025,1.22,ang)],.006,GOLD if not SLY else SEAM)
    pts=[g.tf(c,-w*.18+u,.005,1.0+z,ang) for u,z in [(-.22,-.22),(.22,-.22),(.22,.22),(-.22,.22)]];g.path('Cushion embroidered border',pts,.012,GOLD if not SLY else SEAM,True)
def table(c,w,d,h,ornate=False):
    g.box('Handplaned tabletop',(*c[:2],c[2]+h),(w,d,.16),RIM,.035)
    for i in range(round(w/.35)):
        x=c[0]-w/2+(i+.5)*w/round(w/.35);g.path('Table plank seam',[(x,c[1]-d*.47,c[2]+h+.082),(x+.015,c[1]+d*.47,c[2]+h+.082)],.006,DARK)
    for dx in [-w*.42,w*.42]:
        for dy in [-d*.37,d*.37]:
            if ornate:g.path('Cabriole coffee table leg',[(c[0]+dx*1.1,c[1]+dy*1.1,c[2]+.05),(c[0]+dx*.98,c[1]+dy,c[2]+.2),(c[0]+dx*.90,c[1]+dy,c[2]+h*.6),(c[0]+dx,c[1]+dy,c[2]+h-.08)],.075,WOOD)
            else:g.box('Tapered square table foot',(c[0]+dx,c[1]+dy,c[2]+h/2),(.14,.14,h),WOOD,.02)
    for dy in [-d*.42,d*.42]:g.box('Panelled apron',(c[0],c[1]+dy,c[2]+h-.23),(w-.22,.10,.29),WOOD,.018)
    if ornate:
        for dx in [-w*.31,0,w*.31]:scroll('Table apron acanthus',(c[0]+dx,c[1]-d*.48,c[2]+h-.22),.11,GOLD)
def fireplace():
    g.collection('02 Architecture')
    y=5.70
    g.box('Fireplace soot recess',(0,y-.05,1.14),(2.75,.19,2.24),DARK)
    for side in [-1,1]:
        # Tapered masonry cheeks create the reference's flared hearth silhouette.
        p=[(side*1.35,0),(side*2.00,0),(side*2.20,.6),(side*1.92,1.90),(side*2.40,2.45),(side*1.62,2.40)]
        extrude('Hearth flared stone jamb',p,.85,(0,y-.33,0),TRIM,bevel=.025)
        for z in [.24,.64,1.16,1.70,2.15]:g.path('Hearth masonry seam',[(side*1.5,y-.78,z),(side*2.02,y-.78,z+.015)],.014,DARK)
    for z,w,d,h in [(0.12,4.6,1.55,.23),(2.40,5.0,1.15,.20),(2.63,5.35,1.3,.15),(2.78,4.95,1.04,.13)]:g.box('Moulded mantel',(0,y-.35,z),(w,d,h),TRIM,.035)
    if not SLY:
        pts=[(-2.48,2.60),(-2.20,2.95),(-1.50,2.93),(-.70,3.17),(-.38,3.42),(0,3.53),(.38,3.42),(.70,3.17),(1.50,2.93),(2.20,2.95),(2.48,2.60)]
        extrude('Swept carved mantel crown',pts,.22,(0,y-.73,0),TRIM,bevel=.02)
        for side in [-1,1]:scroll('Mantel scrolling stone',(side*1.35,y-.87,2.92),.21,GOLD)
    # Chimney stone cladding with deliberate irregular block widths.
    for row in range(7 if SLY else 5):
        zz=3.08+row*.60
        widths=([1.62,1.19,1.55] if row%2 else [1.08,1.69,1.59])
        cursor=-sum(widths)/2
        for j,ww in enumerate(widths):
            g.box('Chimney hand cut staggered masonry',(cursor+ww/2,y+.04+random.uniform(-.018,.018),zz),(ww-.022,.50,.575),STONE,.014);cursor+=ww
    shield=[(-.52,.34),(-.48,.95),(0,1.12),(.48,.95),(.52,.34),(0,-.12)]
    extrude('Carved house escutcheon',shield,.13,(0,y-.81,1.15 if SLY else 2.6),TRIM,bevel=.02)
    # Original carved leaf scrolls and a shield, developed without official textures.
    crestz=1.15 if SLY else 2.6
    for u,z0 in shield:g.sphere('Escutcheon small raised boss',(u,y-.91,crestz+z0),(.045,.035,.045),TRIM,8,4)
    for side in [-1,1]:
        for j in range(5):
            cx=side*(.55+j*.24);cz=(2.65 if SLY else 2.96)+sin(j*.75)*.16
            g.path('Carved mantel acanthus stem',[(cx-side*.13,y-.92,cz-.10),(cx,y-.94,cz+.12),(cx+side*.15,y-.92,cz+.16)],.023,TRIM)
            for ss in [-1,1]:extrude('Mantel acanthus leaf',[(-.10,0),(0,.19),(.10,.07),(0,-.05)],.055,(cx+ss*.09,y-.94,cz+.1),TRIM,bevel=.008)
    if SLY:
        for z,w in [(3.35,5.32),(3.52,5.55),(3.66,5.26)]:g.box('High dungeon mantel hood cornice',(0,y-.30,z),(w,.85,.15),TRIM,.022)
        g.box('Cavetto mantel hood',(0,y-.25,3.05),(4.86,.66,.63),STONE,.025)
        for side in [-1,1]:
            for j in range(3):g.box('Splayed hearth stepped corbel',(side*(1.74+j*.11),y-.80,1.8+j*.22),(.58,.28,.21),TRIM,.017)
        extrude('Small upper chimney memorial tablet',[(-.39,0),(-.44,.95),(.44,.95),(.39,0)],.15,(0,y-.34,5.5),TRIM,.0,.015)
        g.sphere('Upper memorial relief head',(0,y-.46,6.08),(.20,.06,.24),STONE,12,8)
        for xx in [-.07,.07]:g.sphere('Relief inset eye',(xx,y-.52,6.1),(.038,.025,.05),DARK,8,4)
    # An original coiling serpent or lion-like heraldic relief, not a copied crest.
    if SLY:
        pts=[(.28*cos(i*2*pi/44),y-.91,1.73+i*.008+.19*sin(i*2*pi/44)) for i in range(72)];g.path('Coiled serpent stone relief',pts,.045,TRIM);g.sphere('Serpent head',(.13,y-.91,2.29),(.11,.07,.07),TRIM)
    else:
        for j in range(13):
            a=j*2*pi/13;extrude('Lion carved mane lock',[(-.075,0),(-.08,.14),(0,.23),(.075,.08)],.09,(.19*cos(a),y-.92,3.29+.19*sin(a)),TRIM,bevel=.008)
        g.sphere('Lion medallion mane',(0,y-.91,3.29),(.25,.06,.25),TRIM);g.sphere('Lion medallion face',(0,y-.98,3.27),(.14,.06,.17),GOLD)
        for side in [-1,1]:
            g.sphere('Lion ear',(side*.15,y-.96,3.44),(.06,.04,.07),GOLD)
            g.sphere('Lion sculpted muzzle',(side*.065,y-1.055,3.22),(.07,.055,.05),TRIM,10,5)
            g.sphere('Lion incised eye',(side*.065,y-1.039,3.32),(.025,.012,.018),DARK,8,4)
    g.collection('04 Details')
    for x in [-.75,0,.73]:
        o=g.cyl('Split charred hearth log',(x,y-.55,.30),.13,1.15,WOOD,10);o.rotation_euler=(pi/2,.2,1.0 if x==0 else .25)
    for i in range(11):
        x=random.uniform(-.95,.95);h=random.uniform(.32,.92)
        pts=[(-.15,0),(-.19,h*.35),(-.07,h*.7),(.03,h),(.09,h*.54),(.18,h*.20),(.12,0)]
        extrude('Faceted sculpted hearth flame',pts,.06,(x,y-.76,.26),FLAME if i%2 else FIRECORE,angle=random.uniform(-.25,.25))
    for x in [-1.1,-.7,-.35,0,.35,.7,1.1]:g.beam('Fireguard vertical',(x,y-1.00,.18),(x,y-1.00,.71),.035,IRON)
    g.path('Fireguard arched rail',[(-1.2,y-1.0,.72),(-.65,y-1.0,.84),(0,y-1.0,.92),(.65,y-1.0,.84),(1.2,y-1.0,.72)],.045,IRON)
    g.point('Warm hearth illumination',(0,y-1.2,.85),470 if SLY else 360,(1,.48,.19),.6)
def bookshelf(c,w=1.8,h=3.8,angle=0,trophies=False):
    for u in [-w/2,w/2]:localbox('Cabinet carved upright',c,u,0,h/2,(.14,.58,h),WOOD,angle)
    localbox('Cabinet back',c,0,.23,h/2,(w,.10,h),WOOD,angle,.008)
    for z in [.12,1.15,2.18,3.10,h]:localbox('Cabinet shelf cornice',c,0,-.02,z,(w+.25,.75,.13),RIM,angle,.018)
    for row in range(3):
        z=.20+row*1.02
        if trophies and row==1:
            for u in [-w*.29,0,w*.29]:trophy(g.tf(c,u,-.10,z,angle),.73)
        else:
            for j in range(max(4,round(w/.22))):book('Library folio',g.tf(c,-w*.40+j*.21,-.06,z,angle),.14+random.random()*.045,.32,.57+random.random()*.20,angle,True)
    if trophies:
        for u in [-w*.30,0,w*.30]:trophy(g.tf(c,u,0,h+.08,angle),1.05)
        for u in [-w*.3,0,w*.3]:
            pts=[(-.20,.32),(-.24,.70),(0,.84),(.24,.70),(.20,.32),(0,.15)];extrude('Engraved trophy shield',pts,.07,g.tf(c,u,-.44,2.1,angle),GOLD,angle,.008)
    else:
        for u in [-w*.25,w*.25]:
            localbox('Lower cabinet panel',c,u,-.34,.65,(w*.45,.08,.90),WOOD,angle,.012)
            for du in [-w*.19,w*.19]:localbox('Cabinet gothic panel stile',c,u+du,-.40,.66,(.025,.03,.77),RIM,angle,.005)

def gothic_wardrobe(c,w,h):
    localbox('Wardrobe deep oak body',c,0,0,h/2,(w,.85,h),WOOD,bevel=.025)
    for z in [.15,h-.15,h]:localbox('Wardrobe moulded cornice',c,0,-.07,z,(w+.30,1.04,.13),RIM,bevel=.025)
    for u in [-w*.245,w*.245]:
        localbox('Wardrobe carved recessed door',c,u,-.47,h*.48,(w*.46,.08,h*.86),DARK,bevel=.008)
        localbox('Wardrobe raised oak door field',c,u,-.52,h*.48,(w*.37,.05,h*.81),WOOD,bevel=.012)
        for du in [-w*.18,0,w*.18]:localbox('Wardrobe pointed gothic stile',c,u+du,-.57,h*.48,(.032,.05,h*.80),RIM,bevel=.005)
        for zz in [.42,h-.40]:
            g.path('Wardrobe pierced pointed tracery',[g.tf(c,u-w*.18,-.59,zz-.15),g.tf(c,u,-.59,zz+.22),g.tf(c,u+w*.18,-.59,zz-.15)],.028,RIM)
        localsphere('Wardrobe old brass handle',c,u*.12,-.62,h*.50,(.04,.04,.06),GOLD)
    for u in [-w*.46,0,w*.46]:
        extrude('Wardrobe carved crown finial',[(-.08,0),(0,.23),(.08,0)],.08,g.tf(c,u,-.34,h+.08),RIM)

def trophy_cabinet(c,w,h):
    # Tall solid panelled cabinet with a central open display and shield frieze.
    for u in [-w/2,w/2]:
        localbox('Trophy cabinet broad stile',c,u,0,h/2,(.21,.78,h),WOOD,bevel=.025)
        localbox('Cabinet stile recessed flute',c,u,-.42,h/2,(.065,.05,h-.38),RIM,bevel=.008)
    localbox('Trophy cabinet shadow back',c,0,.36,h/2,(w,.14,h),DARK,bevel=.01)
    for z in [.16,1.50,2.78,h-.25,h]:localbox('Trophy cabinet layered cornice',c,0,-.02,z,(w+.37,.99,.16),RIM,bevel=.02)
    for z,hh in [(.84,1.15),(3.91,2.05)]:
        for u in [-w*.245,w*.245]:
            localbox('Cabinet aged oak door',c,u,-.37,z,(w*.475,.13,hh),WOOD,bevel=.015)
            for uu in [-w*.19,w*.19]:localbox('Door carved raised stile',c,u+uu,-.46,z,(.055,.06,hh-.15),RIM,bevel=.008)
            localsphere('Cabinet brass stud',c,u*.25,-.48,z,(.04,.03,.04),GOLD)
    for u,sc in [(-.72,.98),(.15,.70),(.79,.52)]:trophy(g.tf(c,u,-.1,1.61),sc)
    for u,sc in [(-.93,.88),(0,1.20),(.91,1.05)]:trophy(g.tf(c,u,.1,h+.09),sc)
    for i,u in enumerate([-w*.32,0,w*.32]):
        zz=3.45+(.18 if i==1 else 0)
        pts=[(-.31,.78),(-.25,1.03),(0,1.15),(.25,1.03),(.31,.78),(.26,.31),(0,0),(-.26,.31)]
        extrude('Cabinet embossed heraldic shield',pts,.10,g.tf(c,u,-.50,zz),TRIM,bevel=.012)
        g.path('Shield incised border',[g.tf(c,u+uu*.80,-.57,zz+.10+vv*.82) for uu,vv in pts],.018,RIM,True)
        for side in [-1,1]:scroll('Shield flanking leaf scroll',g.tf(c,u+side*.25,-.60,zz+.70),.10,TRIM)
        # Different central figures distinguish the three trophies.
        if i==1:trophy(g.tf(c,u,-.65,zz+.30),.43)
        else:
            g.path('Cabinet serpent heraldic relief',[g.tf(c,u+.13*cos(t*.17),-.64,zz+.32+t*.012) for t in range(45)],.026,RIM)

# -------------------------- Architecture --------------------------
g.collection('01 Floor')
g.box('Room foundation',(0,-1.34,-.25),(16.6,19.08,.4),DARK)
for ix in range(12):
    for iy in range(14):
        x=(ix-5.5)*1.34;y=(iy-7.5)*1.34;g.box('Irregular edged flagstone',(x,y,-.045),(1.315,1.315,.09),FLOORSTONE,.018)
        if random.random()<.055:g.path('Floor worn fissure',[(x-.45,y-.3,.005),(x-.12,y-.13,.006),(x+.08,y+.22,.006),(x+.4,y+.30,.006)],.005,DARK)
g.collection('02 Architecture')
# Main wall has true translucent inset panes in recessed openings and a solid reverse side.
if SLY:
    g.box('Upper continuous dungeon masonry',(0,6.35,8.1),(16.5,.92,2.2),STONE,.025)
    g.box('Massive central chimney wall',(0,6.35,4.25),(4.8,1.1,8.5),STONE,.025)
    for sign in [-1,1]:
        g.box('Dungeon end wall',(sign*7.35,6.35,4.25),(1.8,1.1,8.5),STONE,.02)
        for xx in [3.25,5.10]:
            g.portal('Recessed gothic window bay',(sign*xx,6.30,.55),1.48,6.8,1.85,8.0,1.14,STONE,TRIM)
            for z in [.35,4.83,5.04]:g.box('Broad layered pier capital',(sign*(xx+.91),5.69,z),(.73,.74,.20),TRIM,.025)
            g.box('Clustered massive stone pier',(sign*(xx+.91),5.76,2.50),(.57,.76,4.9),STONE,.04)
            g.box('Pier recessed face flute',(sign*(xx+.91),5.33,2.55),(.21,.07,4.15),DARK,.01)
else:g.box('Back masonry wall',(0,6.35,4.25),(16.5,.55,8.5),STONE,.02)
for x in [-8.15,8.15]:g.box('Side enclosure',(x,-2.05,4.25),(.5,16.8,8.5),STONE,.02)
g.box('Front enclosure',(0,-10.5,4.25),(16.5,.4,8.5),STONE,.02)
for x in [-7.5,-5.8,5.8,7.5]:
    for z in [.25,3.7,6.9]:g.box('Pier projecting capital',(x,6.0,z),(.64,.72,.16),TRIM,.025)
    g.box('Carved tall wall pier',(x,6.08,3.5),(.32,.49,6.9),TRIM,.025)
for side in [-1,1]:
    for y in [-6,-2,2,5]:
        g.box('Side stone buttress',(side*7.90,y,3.8),(.42,.55,7.6),STONE,.02)
        for z in [.25,3.35,6.6]:g.box('Side corbel band',(side*7.72,y,z),(.68,.75,.18),TRIM,.02)
    for z in [.18,3.55,6.65]:g.box('Side wall stringcourse',(side*7.82,-2.25,z),(.25,16.5,.15),RIM if not SLY else TRIM,.02)
for z in [.18,6.66]:g.box('Back wall stringcourse',(0,5.97,z),(16,.28,.16),RIM if not SLY else TRIM,.02)
if SLY:
    for x in [-5.10,-3.25,3.25,5.10]:window(x,6.40,.69,1.40,6.61)
    for y in [-8.5,-4.5,0,5.75]:
        # Repeated pointed transverse ribs form the dungeon ceiling silhouette.
        pts=[(-7.95,y,4.0),(-7.7,y,6.4),(-6.4,y,7.7),(0,y,9.1),(6.4,y,7.7),(7.7,y,6.4),(7.95,y,4.0)]
        # A deep curved structural arch, not a thin roof bar.
        pts=[(-7.86,y,0),(-7.86,y,4.75),(-7.42,y,6.0),(-6.35,y,7.2),(-4.6,y,8.25),(0,y,9.45),(4.6,y,8.25),(6.35,y,7.2),(7.42,y,6.0),(7.86,y,4.75),(7.86,y,0)]
        for a,b in zip(pts,pts[1:]):g.beam('Massive cut stone transverse arch',a,b,.58,STONE,.78)
        g.path('Carved arch lip',[(x,yy-.42,z) for x,yy,z in pts],.085,TRIM)
        g.path('Inner incised rib',[(x,yy-.45,z-.12) for x,yy,z in pts],.025,DARK)
    for row in range(13):
        for side in [-1,1]:
            for j in range(6):g.box('Dungeon side broad block',(side*7.87,-6.4+j*2.25+(row%2)*.28,.38+row*.57),(.14,2.20,.54),STONE,.012)
    g.box('Dark vaulted ceiling',(0,-2,9.35),(16.4,16.8,.25),DARK)
else:
    for x in [-3.45,3.45]:window(x,5.98,1.42,1.72,3.84)
    # A timber mansard ceiling with visible radial cross beams.
    for side in [-1,1]:
        vs=[(side*8.0,-10.5,6.75),(side*8.0,6.5,6.75),(side*2.5,6.5,9.20),(side*2.5,-10.5,9.20)];g.mesh('Sloped timber roof',vs,[(0,1,2,3)],WOOD)
        for y in [-9.5,-7,-4.5,-1.5,1.5,4.5,6.0]:g.beam('Heavy roof hammer beam',(side*7.95,y,6.7),(side*2.5,y,9.12),.23,WOOD)
        for t in [i/9 for i in range(10)]:g.beam('Ceiling plank seam',(side*(8-5.5*t),-10.5,6.75+2.45*t),(side*(8-5.5*t),6.5,6.75+2.45*t),.035,RIM)
    g.box('Timber upper ceiling',(0,-2,9.20),(5,17,.18),WOOD)
    for y in [-9,-6,-2,2,6]:g.beam('Upper roof tie',( -8,y,6.75),(8,y,6.75),.22,WOOD)
    TAP=painted('Original tree and heraldic tapestry',(.8,.6,.5),'tapestry')
    for side in [-1,1]:
        for y in [-6,-3,0,3]:
            c=(side*7.82,y,.35);a=-side*pi/2
            localbox('Wall tree tapestry',c,0,0,1.55,(2.72,.07,3.10),TAP,a,.005)
            for u in [-1.40,1.40]:localbox('Tapestry turned stile',c,u,-.07,1.60,(.065,.12,3.35),GOLD,a,.01)
            portrait(g.tf(c,0,-.15,2.35,a),.95,1.45,random.randrange(5),a)
        for x in [side*5.8,side*7.15]:g.box('Back tapestry panel',(x,5.98,1.9),(1.30,.07,3.30),TAP,.012)
    portrait((-6.0,5.82,3.18),1.30,1.92,2)
    portrait((6.35,5.18,4.18),1.12,1.65,1)
fireplace()

# --------------------------- Furniture ---------------------------
g.collection('03 Furniture')
if SLY:
    # Oval rug with original geometry border; image mapped across its top surface.
    o=g.cyl('Large oval woven rug',(0,-.20,.027),1,.034,RUG,64);o.scale=(4.75,4.05,1)
    for r in [1,.94,.90]:g.path('Silver rug embroidery',[(4.6*r*cos(i*2*pi/100),-.2+3.9*r*sin(i*2*pi/100),.052) for i in range(100)],.018,TRIM,True)
    chair((-2.65,.45,0),2.72,pi/2-.11,variant=1);chair((2.61,.20,0),2.96,-pi/2-.075,variant=2);chair((6.20,2.28,0),1.62,.37,variant=3)
    table((0,.2,0),1.85,3.45,.95)
    g.box('Coffee table lower plinth',(0,.2,.13),(1.75,3.25,.18),WOOD,.025)
    for side in [-1,1]:g.box('Coffee table panel apron',(side*.78,.2,.55),(.12,2.80,.70),WOOD,.02)
    table((-5.25,-3.25,0),2.4,1.45,1.10);table((4.65,-2.3,0),1.35,1.35,.95)
    trophy_cabinet((6.63,5.23,0),2.60,5.45)
    bookshelf((-6.6,5.4,0),1.7,3.6)
else:
    g.box('Gold bordered crimson rug',(0,-.20,.028),(8.15,5.8,.045),RUG,.016)
    chair((-2.95,.32,0),2.70,pi/2-.22,variant=1);chair((2.90,.02,0),2.37,-pi/2-.08,variant=2)
    chair((-1.24,3.10,0),1.55,-.16,True,1);chair((1.33,2.67,0),1.38,.19,False,3)
    table((0,-.42,0),3.55,1.75,.85,True)
    gothic_wardrobe((6.3,5.4,0),2.05,4.1)
    table((-5.4,-3.25,0),2.2,1.25,.98,True);chair((-5.4,-4.4,0),1.10,pi)
    # Hearth reading side stand and scattered floor pillows.
    table((-2.42,3.13,0),.85,.85,1.08,True)
    for x,y,z,a in [(-3.9,-2.9,.16,.2),(-3.8,-2.8,.40,-.3),(3.8,-2.3,.20,.3)]:
        o=g.sphere('Loose floor cushion',(x,y,z),(.55,.38,.17),CLOTHLIGHT if z>.3 else GOLD,16,8);o.rotation_euler.z=a

# ------------------------ Decorative props -----------------------
g.collection('04 Details')
# Main table: books, chessboard, parchment, brass candle and an owl (Gryffindor).
top=.95 if SLY else .85
for j in range(3):book('Stacked study book',(.36,-.60,top+.10+j*.09),.52,.37,.07,j*.12)
g.box('Unrolled parchment',(-.45,.20,top+.10),(.70,.43,.013),PAPER,.008,angle=.13)
for j in range(8):g.path('Parchment ink line',[(-.71,.08+j*.035,top+.109),(-.26+random.random()*.08,.08+j*.035,top+.109)],.003,IRON)
candle((-.65,-.55,top+.11),.36)
if SLY:
    for i in range(8):
        for j in range(8):g.box('Inlaid chessboard square',((i-3.5)*.09,.95+(j-3.5)*.09,1.047),(.088,.088,.015),PAPER if (i+j)%2 else DARK,.001)
    for i in range(5):g.lathe('Chess piece',((i-2)*.12,.77,1.06),[(.025,0),(.028,.02),(.012,.04),(.016,.075),(.024,.09),(.015,.12)],PAPER,10)
    g.lathe('Green glass table lamp',(.28,.7,1.05),[(.13,0),(.15,.03),(.035,.10),(.032,.35),(.09,.41),(.18,.49),(.15,.61),(.05,.66)],GOLD,16)
    g.sphere('Green lamp bulb',(.28,.7,1.60),(.16,.16,.15),LAMP,12,6)
else:
    g.sphere('Little owl body',(.95,-.38,1.20),(.17,.15,.28),PAPER,12,8)
    g.sphere('Little owl head',(.95,-.40,1.43),(.20,.17,.16),PAPER,12,6)
    for side in [-1,1]:
        g.sphere('Owl amber eye',(.95+side*.095,-.556,1.45),(.055,.025,.063),GOLD,12,6);g.sphere('Owl pupil',(.95+side*.095,-.580,1.45),(.024,.014,.038),DARK,10,5)
    extrude('Owl beak',[(-.04,0),(.04,0),(0,-.09)],.05,(.95,-.59,1.39),GOLD)
    for side in [-1,1]:g.sphere('Owl folded wing',(.95+side*.15,-.35,1.20),(.07,.13,.20),TRIM,10,5)
    candle((-2.42,3.13,1.18),.45)
    # Woven throws follow a curved path down each sofa, with tapered frayed ends.
    TARTAN=painted('Original worn tartan weave',(.62,.49,.30),'tartan','XZ')
    for c,ang in [((-2.95,.32,0),pi/2-.22),((2.90,.02,0),-pi/2-.08)]:
        vs=[];fs=[];profile=[(.64,1.07),(.60,1.48),(.40,1.66),(.23,1.53),(.18,1.23),(.10,.98),(-.12,.87),(-.32,.78)]
        for row,(dd,zz) in enumerate(profile):
            for j in range(13):
                u=-.39+j*.065;vs.append((u+.55,dd+.018*sin(j*1.7),zz+.026*cos(j*1.7)))
        for row in range(len(profile)-1):
            for j in range(12):
                i=row*13+j;fs.append((i,i+1,i+14,i+13))
        o=g.mesh('Soft draped tartan sofa throw',vs,fs,TARTAN);o.location=c;o.rotation_euler.z=ang
        for j in range(13):
            u=.16+j*.065;g.path('Throw frayed wool tassel',[g.tf(c,u,-.32,.78,ang),g.tf(c,u+.018,-.34,.66-random.random()*.06,ang)],.008,TARTAN)
# Side tables contain props that make the entire room useful from reverse views.
for j in range(4):book('Reading table folio',(-5.20,-3.25,1.12+j*.075),.58,.40,.06,-.1+j*.08)
candle((-5.95,-3.18,1.2),.45)
g.lathe('Pewter goblet',(-4.5,-3.15,1.19),[(.08,0),(.09,.02),(.025,.07),(.025,.18),(.08,.22),(.10,.37),(.11,.4)],GOLD,12)
for x,y,ang in [(-7.65,1,pi/2),(7.65,-4,-pi/2)]:bookshelf((x,y,0),2.10,3.1,ang)
# Reverse wall, an original extension: arched entrance, bench and portraits.
g.collection('02 Architecture')
g.arch_frame('Original reverse entry arch',(0,-10.23,0),2.8,4.9,.15,TRIM)
extrude('Closed oak entry door',g.arch_points(2.63,4.75),.10,(0,-10.20,.03),WOOD)
for x in [-.96,-.48,0,.48,.96]:g.box('Door raised stave',(x,-10.10,2.2),(.045,.05,4.0),RIM,.008)
for z in [.55,2.45,3.65]:g.box('Door iron strap',(0,-10.04,z),(2.48,.035,.075),IRON,.008)
g.collection('04 Details')
for x in [-4.0,4.0]:portrait((x,-10.04,2.20),1.2,1.75,1 if x<0 else 3,pi)
for side in [-1,1]:
    # Ferns have distinct tapering cut leaves.
    x=side*6.8;y=1.7
    g.lathe('Terracotta plant vessel',(x,y,0),[(.23,0),(.35,.06),(.40,.52),(.44,.56),(.44,.63),(.35,.65)],WOOD,14)
    for i in range(11):
        a=i*2.4;rr=.45+random.random()*.35;h=.70+random.random()*.80
        pts=[(x,y,.55),(x+cos(a)*rr*.5,y+sin(a)*rr*.5,h),(x+cos(a)*rr,y+sin(a)*rr,h*.70)]
        g.path('Plant arching stem',pts,.012,SEAM)
        for j in range(3):
            t=(j+1)/4;p0=Vector(pts[0]).lerp(Vector(pts[1]),t);end=p0+Vector((cos(a+.7)*.25,sin(a+.7)*.25,.13));v=Vector((-sin(a)*.06,cos(a)*.06,0));g.mesh('Angular painted leaf',[p0-v,p0+v,end],[(0,1,2)],CLOTHLIGHT)

# ------------------------- Ceiling fixtures ----------------------
g.collection('04 Details')
if SLY:
    for i,(x,y,z,r) in enumerate([(-5.8,1.0,6.9,.34),(-3.4,3.6,5.4,.25),(-1.0,4.1,4.35,.21),(2.4,3.4,6.1,.27),(4.2,1.8,5.55,.29),(3.3,4.3,4.4,.24)]):
        rod('Pendant chain',(x,y,z+.2),(x,y,8.5),.014,IRON)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=r,location=(x,y,z));o=bpy.context.object;o.name='Faceted pale green hanging lantern';o.scale=(.84,.84,1.12);o.data.materials.append(LAMP)
        for col in list(o.users_collection):col.objects.unlink(o)
        g.CURRENT.objects.link(o)
        for e in o.data.edges:
            a=o.data.vertices[e.vertices[0]].co;b=o.data.vertices[e.vertices[1]].co
            p1=(x+a.x*.845,y+a.y*.845,z+a.z*1.125);p2=(x+b.x*.845,y+b.y*.845,z+b.z*1.125)
            g.path('Faceted lantern lead line',[p1,p2],.0035,SEAM)
        ring('Lantern brass collar',(x,y,0),r*.25,z+r*1.08,GOLD,.018,12)
        g.point('Opal pendant light '+str(i),(x,y,z),42,(.40,.72,.52),.4)
else:
    z=5.85;r=1.42
    # Broad twelve-sided crown, suspended under a peaked dark timber roof.
    g.cyl('Chandelier wide crown',(0,.25,z),r,.38,GOLD,12,r2=r*.95)
    # Dark core reveals carved ornaments and keeps the underside legible.
    g.cyl('Chandelier inset underside',(0,.25,z-.215),r*.88,.06,WOOD,12)
    for zz,rr in [(z-.25,r*.98),(z+.23,r*1.02),(z-.32,r*.86)]:ring('Chandelier stepped brass rim',(0,.25,0),rr,zz,GOLD,.055,12)
    for i in range(12):
        a=2*pi*i/12;x=cos(a)*r;y=.25+sin(a)*r
        # Each face has a raised diamond plaque and a spiked candle cup.
        o=g.box('Crown engraved diamond',(cos(a)*(r+.025),.25+sin(a)*(r+.025),z),(.22,.035,.22),RIM,.015,angle=a-pi/2);o.rotation_euler.y=pi/4
        arm=(cos(a)*(r+.28),.25+sin(a)*(r+.28),z+.02)
        g.beam('Chandelier radial bracket',(cos(a)*(r-.2),.25+sin(a)*(r-.2),z-.03),arm,.10,GOLD)
        g.lathe('Chandelier ornate candle cup',arm,[(.14,0),(.17,.14),(.24,.20),(.22,.26),(.12,.30)],GOLD,10)
        h=.38+(i%3)*.10;g.cyl('Tall chandelier ivory candle',(arm[0],arm[1],z+.34+h/2),.065,h,PAPER,10)
        g.sphere('Large candle flame',(arm[0],arm[1],z+.36+h),(.075,.075,.23),LAMP,10,5)
        if i%2==0:g.beam('Chandelier gold suspension',(0,.25,7.65),(cos(a)*(r-.1),.25+sin(a)*(r-.1),z+.25),.034,GOLD)
    rod('Chandelier central suspension',(0,.25,7.62),(0,.25,9.05),.05,IRON)
    g.lathe('Chandelier lower finial',(0,.25,z-.90),[(0,0),(.22,.28),(.28,.38),(.12,.48),(.12,.65)],GOLD,12)
    g.point('Chandelier warm pool',(0,.25,5.55),330,(1,.79,.52),1.1)
    for side in [-1,1]:g.point('Wall sconces',(side*6.8,-2,3.8),65,(1,.57,.27),.45)

# Render and source preservation.
g.collection('05 Light and cameras')
g.area('Soft camera side fill',(0,-5,5),(0,2,1.5),180 if SLY else 160,(.48,.69,.61) if SLY else (.90,.78,.62),6)
g.area('Seating local warm pool',(0,-.25,4.2),(0,1,1),125 if not SLY else 55,(1,.72,.44),3.6)
g.area('Upper bounce',(0,1,7.5),(0,0,0),100 if SLY else 85,(.36,.58,.46) if SLY else (.75,.64,.48),7)
camera_data=[('主视角',(0,-7.65 if SLY else -9.4,3.70 if SLY else 3.04),(0,3.0,3.27 if SLY else 3.18),18),('炉火与书桌',(-5.8,-3.5,2.5),(.8,3.2,1.8),25),('反向全景',(5.5,4.65,2.75),(-.6,-2.4,2.1),23)]
cams=[g.camera(name,loc,target,lens) for name,loc,target,lens in camera_data];S.camera=cams[0]
S.render.engine='CYCLES';S.cycles.samples=16;S.cycles.use_denoising=True;S.cycles.max_bounces=5
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type='CUDA';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='CUDA'
    S.cycles.device='GPU' if any(d.type=='CUDA' for d in prefs.devices) else 'CPU'
except Exception:S.cycles.device='CPU'
S.world.color=(.12,.12,.12);S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.16,.23,.19,1) if SLY else (.24,.19,.12,1);S.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.12
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=-.10 if SLY else -.30
S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.filepath=os.path.join(ROOT,'previews','blender-'+ROOM+'.png');S.render.film_transparent=False
# Curves are converted for portable export. Preserve source object names and materials.
bpy.ops.object.select_all(action='DESELECT')
for o in S.objects:
    if o.type in ['CURVE','FONT']:o.select_set(True)
if bpy.context.selected_objects:bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.convert(target='MESH')
seen=set()
for o in S.objects:
    if o.type!='MESH' or o.data in seen:continue
    seen.add(o.data);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
bpy.ops.file.pack_all()
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath:im.filepath=bpy.path.relpath(im.filepath,start=HERE)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE,ROOM+'.blend'))
def yup(v):return [round(v[0],4),round(v[2],4),round(-v[1],4)]
obs=[{'minX':-2.55,'maxX':2.55,'minZ':-6.15,'maxZ':-4.30}]
def obstacle(x,y,w,d):obs.append({'minX':x-w/2,'maxX':x+w/2,'minZ':-y-d/2,'maxZ':-y+d/2})
if SLY:
    obstacle(-2.65,.45,1.78,3.25);obstacle(2.61,.20,1.65,3.44);obstacle(0,.2,1.90,3.5);obstacle(-5.25,-3.25,2.45,1.5);obstacle(4.65,-2.3,1.4,1.4);obstacle(6.20,2.28,2.1,1.8);obstacle(6.63,5.23,2.98,1.3);obstacle(-6.6,5.4,1.9,.9)
else:
    obstacle(-2.95,.32,2.0,3.25);obstacle(2.90,.02,1.60,2.90);obstacle(0,-.42,3.6,1.8);obstacle(-1.24,3.10,1.92,1.65);obstacle(1.33,2.67,1.8,1.6);obstacle(6.3,5.4,2.5,.9);obstacle(-5.4,-3.5,2.4,2.4)
    obstacle(-2.42,3.13,.85,.85)
    obstacle(-3.85,-2.85,1.30,1.10);obstacle(3.8,-2.3,1.30,1.10)
for side in [-1,1]:obstacle(side*7.65,1 if side==-1 else -4,1.0,2.5);obstacle(side*6.8,1.7,1.2,1.2)
meta={'id':ROOM,'title':'斯莱特林公共休息室' if SLY else '格兰芬多公共休息室','cameras':[{'name':name,'position':yup(loc),'target':yup(target),'fov':round(math.degrees(2*math.atan(36/(2*lens)/(16/9))),4)} for name,loc,target,lens in camera_data],'spawn':{'position':yup((0,-5.8,1.65)),'target':yup((0,3.2,1.65))},'bounds':{'minX':-7.3,'maxX':7.3,'minZ':-5.9,'maxZ':9.8},'obstacles':obs,'lighting':'baked','background':'#0a1511' if SLY else '#181109','exposure':1.0,'triangles':0,'artisticLimitations':['Original interpretation of one official promotional image; reverse wall, dimensions and hidden surfaces are inferred.','No official game meshes, characters, logos or texture assets are included.','Carved heraldry, portraits and tapestry are original simplified decorative designs.','Baked illumination is static; no physically simulated flickering or moving shadows.']}
assets=os.path.join(ROOT,'scene-assets',ROOM);os.makedirs(assets,exist_ok=True);json.dump(meta,open(os.path.join(assets,'metadata.json'),'w',encoding='utf8'),ensure_ascii=False,indent=2)
meta['fov']=round(math.degrees(2*math.atan(36/(2*18)/(16/9))),4)
meta['exposure']=.933 if SLY else .812
json.dump(meta,open(os.path.join(assets,'metadata.json'),'w',encoding='utf8'),ensure_ascii=False,indent=2)
if '--draft' in sys.argv:
    S.cycles.samples=8;S.render.resolution_percentage=65
    S.render.filepath=os.path.join(ROOT,'previews','blender-'+ROOM+'-draft.png')
bpy.ops.render.render(write_still=True);print('BUILD_RENDER_COMPLETE',ROOM,flush=True)
