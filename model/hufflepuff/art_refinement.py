"""Second art pass: original sculpture, carved joinery and enclosing masonry.

Installed by build_rooms.py before scene assembly. All geometry remains editable.
"""
import math, random
from mathutils import Vector, Matrix

def sculpt_statue(c):
    marble=g.material('Carved cool ivory marble',(.43,.44,.39),(.62,.63,.56),rough=.88,noise_scale=6)
    edge=g.material('Sculpture recessed line',(.23,.25,.24),rough=.98)
    def P(x,y,z):return (c[0]+x,c[1]+y,c[2]+z)
    # An articulated, seven-head-high silhouette with a weighted, flared hem.
    for z,w,d,h in [(.13,1.50,1.08,.26),(.34,1.25,.92,.17),(.52,1.14,.84,.20)]:
        rounded('Sculpture layered plinth',P(0,0,z),(w,d,h),marble,.025)
    levels=[(.64,.64,.40),(.82,.59,.38),(1.1,.52,.35),(1.55,.45,.32),(2.05,.37,.29),(2.48,.31,.245),(2.76,.29,.235),(2.98,.36,.255),(3.18,.39,.25),(3.32,.47,.22),(3.43,.33,.19)]
    n=64;vs=[];fs=[]
    for j,(z,rx,ry) in enumerate(levels):
        for k in range(n):
            a=2*pi*k/n;fold=(.055+.055*(1-j/(len(levels)-1)))*cos(12*a+z*.8)+.018*cos(23*a-z)
            # Long folds settle at an asymmetrical hem and pull diagonally to the hip.
            x=.08*sin(z*1.1)+(rx+fold)*cos(a)
            y=(ry+fold*.65)*sin(a)-.015*z
            zz=z+(.038*sin(a*5)+.018*cos(a*9))*(1-j/(len(levels)-1))
            vs.append(P(x,y,zz))
    for j in range(len(levels)-1):
        for k in range(n):a=j*n+k;b=j*n+(k+1)%n;fs.append((a,b,b+n,a+n))
    fs.extend([tuple(reversed(range(n))),tuple(range((len(levels)-1)*n,len(levels)*n))])
    g.mesh('Sculpted asymmetrical full robe',vs,fs,marble,True)
    # A second diagonal mantle has its own edge, fold ridges and hanging ends.
    def drape(name,points,widths):
        verts=[];faces=[];steps=12
        for j,p in enumerate(points):
            for i in range(steps+1):
                u=i/steps-.5
                verts.append(P(p[0]+u*widths[j],p[1]-.045*cos(u*8*pi)-.045*sin(j*.8),p[2]+.035*cos(u*6*pi)))
        for j in range(len(points)-1):
            for i in range(steps):a=j*(steps+1)+i;faces.append((a,a+1,a+steps+2,a+steps+1))
        ob=g.mesh(name,verts,faces,marble,True)
        mod=ob.modifiers.new('Sculpted cloth thickness','SOLIDIFY');mod.thickness=.04
        for s in [-1,1]:g.path(name+' rolled edge',[P(p[0]+s*w/2,p[1]-.045,p[2]) for p,w in zip(points,widths)],.025,marble)
    drape('Shoulder sash carved folds',[(-.30,-.22,3.40),(-.22,-.31,3.22),(-.10,-.34,3.04),(.12,-.34,2.84),(.31,-.29,2.68)],[.38,.42,.43,.37,.28])
    drape('Long left mantle',[(-.36,-.04,3.34),(-.53,-.08,3.15),(-.67,-.17,2.89),(-.62,-.24,2.48),(-.51,-.26,2.05),(-.38,-.25,1.85)],[.26,.33,.42,.44,.37,.23])
    drape('Right hanging scholar sleeve',[(.36,-.05,3.34),(.58,-.11,3.15),(.67,-.15,2.94),(.64,-.23,2.60),(.57,-.27,2.34),(.45,-.26,2.16)],[.27,.34,.39,.38,.31,.19])
    # Anatomical arms: broad shoulder, narrowing elbow, bent wrist, fingers.
    def limb(name,a,b,ra,rb):
        o=g.cyl(name,tuple((Vector(P(*a))+Vector(P(*b)))/2),ra,(Vector(a)-Vector(b)).length,marble,16,r2=rb)
        o.rotation_euler=(Vector(b)-Vector(a)).to_track_quat('Z','Y').to_euler()
    limb('Left sculpted upper arm',(-.37,-.01,3.32),(-.62,-.17,3.02),.14,.105)
    limb('Left bent forearm',(-.62,-.17,3.02),(-.40,-.39,3.13),.10,.07)
    limb('Right sculpted upper arm',(.37,-.01,3.31),(.65,-.13,3.02),.14,.10)
    limb('Right bent forearm',(.65,-.13,3.02),(.37,-.43,2.98),.10,.07)
    for hand in [(-.36,-.40,3.13),(.32,-.44,3.0)]:
        g.sphere('Sculpted palm',P(*hand),(.105,.065,.09),marble,16,10)
        for k in range(4):
            x=hand[0]+(k-1.5)*.025
            g.path('Separated carved finger',[P(x,hand[1]-.045,hand[2]+.015),P(x-.01,hand[1]-.065,hand[2]-.065)],.012,marble)
    # Neck and face are modeled in cross sections: chin, jaw, cheek, brow, cranium.
    g.cyl('Sculpted neck',P(.015,-.03,3.51),.11,.32,marble,24)
    head=[(3.58,.06,.085),(3.62,.12,.14),(3.69,.17,.17),(3.80,.19,.18),(3.93,.185,.19),(4.06,.17,.17),(4.16,.12,.12),(4.20,.025,.035)]
    v=[];f=[];nn=40
    for z,rx,ry in head:
        for k in range(nn):
            a=2*pi*k/nn;v.append(P(.015+rx*cos(a),-.03+ry*sin(a),z))
    for j in range(len(head)-1):
        for k in range(nn):a=j*nn+k;b=j*nn+(k+1)%nn;f.append((a,b,b+nn,a+nn))
    f += [tuple(reversed(range(nn))),tuple(range((len(head)-1)*nn,len(head)*nn))]
    g.mesh('Sculpted brow cheek jaw and chin',v,f,marble,True)
    # Slightly angular bridge and lips avoid a featureless ball or black cartoon eyes.
    g.mesh('Faceted classical nose',[P(-.035,-.203,3.96),P(.055,-.203,3.96),P(.045,-.277,3.79),P(-.024,-.277,3.79),P(.015,-.30,3.81),P(.015,-.21,3.75)],[(0,1,4),(1,2,4),(0,4,3),(3,4,2,5),(0,3,5),(1,5,2)],marble)
    for s in [-1,1]:
        x=.015+s*.082
        g.path('Sculpture raised brow',[P(x-s*.05,-.202,3.97),P(x,-.216,3.988),P(x+s*.044,-.188,3.96)],.015,marble)
        g.path('Sculpture eye recess',[P(x-.034,-.207,3.93),P(x,-.215,3.918),P(x+.033,-.207,3.93)],.008,edge)
        g.path('Sculpture lower eyelid',[P(x-.034,-.209,3.915),P(x,-.218,3.904),P(x+.033,-.209,3.915)],.010,marble)
    g.path('Sculpture upper lip',[P(-.045,-.199,3.742),P(.005,-.214,3.75),P(.06,-.199,3.742)],.014,marble)
    g.path('Sculpture mouth recess',[P(-.035,-.208,3.728),P(.015,-.219,3.726),P(.055,-.208,3.73)],.006,edge)
    # Thick carved hair flows outward from the diadem and returns to the shoulders.
    for s in [-1,1]:
        for k in range(7):
            x=.14+k*.019
            pts=[P(s*.055,-.005,4.19),P(s*x,.03-k*.012,4.10),P(s*(x+.055),.025-k*.006,3.91),P(s*(x+.13),.025,3.71),P(s*(x+.08),-.005,3.53),P(s*(x+.21),-.02,3.38)]
            g.path('Wavy carved marble hair lock',pts,.032+(k%2)*.008,marble)
    ring('Raven diadem circlet',P(.015,-.01,4.12),.194,marble,.027)
    for s in [-1,1]:
        g.path('Raven diadem wing',[P(.015,-.20,4.14),P(s*.14,-.19,4.24),P(s*.20,-.16,4.35),P(s*.15,-.18,4.17)],.025,marble)
    g.sphere('Diadem central stone',P(.015,-.22,4.19),(.045,.025,.065),gold,16,8)
    g.beam('Scholar slender wand',P(.35,-.47,2.97),P(.82,-.40,3.72),.018,gold)
    for zz in [.69,.86]:
        g.path('Sculpted robe hem piping',[P(.60*cos(a),.38*sin(a)-.03,zz+.03*sin(a*5)) for a in [k*2*pi/64 for k in range(64)]],.018,marble,True)

def botanical_leaf(name,a,b,width,mat=None):
    mat=mat or green;a=Vector(a);b=Vector(b);d=b-a
    # Wall ivy and relief feathers need a face in the wall plane. Crossing only
    # with world Z made their widths point into the wall and look like needles.
    if any(word in name.lower() for word in ['ivy','canopy','eagle','feather','carved','cupboard','niche']):
        facing=Vector((0,-1,.13))
    else:
        facing=Vector((random.uniform(-.5,.5),-.8,random.uniform(.15,.65)))
    side=d.cross(facing)
    if side.length<.01:side=Vector((1,0,0))
    side.normalize();normal=side.cross(d).normalized()
    # Broad curled leaf, closed thin volume; an irregular pointed outline plus central ridge.
    verts=[a, a+d*.24+side*width*.65,a+d*.52+side*width,a+d*.77+side*width*.63,b,a+d*.77-side*width*.58,a+d*.50-side*width*.94,a+d*.22-side*width*.53,a+d*.5+normal*width*.26]
    fs=[(i,(i+1)%8,8) for i in range(8)]
    o=g.mesh(name,[tuple(v) for v in verts],fs,mat,False)
    if 'ivy' in name.lower() or 'canopy' in name.lower():
        g.path('Leaf central pale vein',[a,a+d*.50+normal*width*.27,b],.004,leaflight)
    return o

def carved_cabinet(c,w=2.4,h=2.7):
    # Paneled walnut frame with arch-headed doors, individual carved moldings and relief.
    g.box('Carved cupboard deep shadow',(c[0],c[1]+.10,c[2]+h/2),(w,.55,h),navy if ID=='ravenclaw' else black,.025)
    for dx in [-w/2,w/2]:
        g.box('Cupboard fluted stile',(c[0]+dx,c[1]-.12,c[2]+h/2),(.16,.57,h+.18),wood,.025)
        for k in [-.04,.04]:g.path('Stile engraved flute',[(c[0]+dx+k,c[1]-.422,c[2]+.24),(c[0]+dx+k,c[1]-.422,c[2]+h-.20)],.009,gold)
    for zz,ww,dep in [(0,w+.18,.67),(.16,w+.12,.65),(h-.10,w+.08,.63),(h+.05,w+.32,.75),(h+.18,w+.43,.82)]:
        g.box('Cupboard layered cornice',(c[0],c[1]-.08,c[2]+zz),(ww,dep,.10),wood,.024)
    for s in [-1,1]:
        xx=c[0]+s*w*.247;ww=w*.43
        g.box('Recessed cupboard door',(xx,c[1]-.21,c[2]+h*.45),(ww,.09,h*.77),wood,.02)
        g.box('Blue-black cabinet inset',(xx,c[1]-.27,c[2]+h*.43),(ww-.13,.04,h*.64),navy if ID=='ravenclaw' else black,.01)
        pts=[(xx-ww*.42,c[1]-.30,c[2]+.23),(xx-ww*.42,c[1]-.30,c[2]+h*.67)]
        pts += [(xx+ww*.42*cos(a),c[1]-.30,c[2]+h*.67+ww*.42*sin(a)) for a in [pi-i*pi/24 for i in range(25)]]
        pts += [(xx+ww*.42,c[1]-.30,c[2]+.23)]
        g.path('Carved door gothic arch',pts,.048,wood)
        for z in [.55,1.11,1.65]:
            g.box('Display cupboard inner shelf',(xx,c[1]-.32,c[2]+z),(ww-.14,.10,.055),wood,.008)
            if z<1.2:
                for k in range(3):book((xx-.23+k*.19,c[1]-.29,c[2]+z+.16),.11,.26,.13,standing=True,mat=wood if k%2 else blue)
            else:vase((xx,c[1]-.32,c[2]+z+.03),.28,gold)
        g.sphere('Cupboard small brass knob',(xx-s*ww*.30,c[1]-.36,c[2]+h*.42),(.038,.024,.038),gold)
    center=(c[0],c[1]-.49,c[2]+h-.07)
    ring('Cupboard central relief wreath',center,.21,gold,.018,axis='Y',n=40)
    for s in [-1,1]:
        g.path('Cornice leaf scroll',[(c[0]+s*(.15+j*.035),c[1]-.47,c[2]+h-.03+.07*sin(j*.28)) for j in range(24)],.020,gold)
    for k in range(11):
        a=k*2*pi/11;leaf('Cupboard carved medallion leaf',center,(center[0]+.17*cos(a),center[1]-.015,center[2]+.17*sin(a)),.04,gold)

def large_eagle(c,scale=1):
    # Continuous broad wing surfaces, separated long feathers, breast and hooked beak.
    g.sphere('Eagle carved breast',c,(.13*scale,.12*scale,.25*scale),gold,20,12)
    g.sphere('Eagle hooked head',(c[0]+.035*scale,c[1]-.04*scale,c[2]+.28*scale),(.12*scale,.13*scale,.13*scale),gold,20,12)
    g.mesh('Eagle beak relief',[(c[0]+x*scale,c[1]+y*scale,c[2]+z*scale) for x,y,z in [(.04,-.12,.31),(.14,-.14,.29),(.10,-.23,.20),(.0,-.14,.23)]],[(0,1,2,3)],gold)
    for s in [-1,1]:
        vs=[(c[0]+s*x*scale,c[1]+y*scale,c[2]+z*scale) for x,y,z in [(.05,.01,.14),(.36,.02,.24),(.67,.025,.65),(.55,.025,.04),(.24,-.015,-.12)]]
        g.mesh('Broad carved eagle wing',vs,[(0,1,2,3,4)],gold)
        for k in range(9):
            a=Vector((c[0]+s*(.14+k*.022)*scale,c[1]-.03*scale,c[2]+(.01+k*.017)*scale))
            b=Vector((c[0]+s*(.39+k*.041)*scale,c[1]-.035*scale,c[2]+(.10+k*.071)*scale))
            leaf('Long relief eagle feather',a,b,.055*scale,gold)
        for k in range(3):leaf('Eagle descending tail',(c[0]+s*.07*scale,c[1],c[2]-.10*scale),(c[0]+s*(.05+k*.045)*scale,c[1],c[2]-(.36-k*.035)*scale),.042*scale,gold)

def add_highback(c,a=0):
    rounded('Reading chair carved seat',local(c,0,0,.53,a),(.88,.89,.16),wood,.06,a)
    rounded('Reading chair velvet pad',local(c,0,-.02,.64,a),(.78,.79,.16),blue,.08,a)
    rounded('Tall curved reading chair back',local(c,0,.35,1.32,a),(.80,.16,1.35),wood,.06,a)
    rounded('Tufted reading chair blue inset',local(c,0,.247,1.34,a),(.64,.06,1.15),blue,.06,a)
    for x in [-.34,.34]:
        for y in [-.34,.34]:g.beam('Turned reading chair leg',local(c,x*1.13,y*1.1,.03,a),local(c,x,y,.56,a),.075,wood)
    for z in [1.05,1.35,1.65]:
        for x in [-.18,.18]:g.sphere('Reading chair stud',local(c,x,.20,z,a),(.02,.015,.02),gold,10,6)

def opened_book(c):
    for s in [-1,1]:
        o=g.box('Open book leather board',(c[0]+s*.20,c[1],c[2]),(.39,.57,.035),wood,.008)
        o.rotation_euler.y=s*.12
        o=g.box('Fanned open parchment pages',(c[0]+s*.20,c[1],c[2]+.035),(.37,.55,.055),paper,.012)
        o.rotation_euler.y=s*.12
        for j in range(8):
            y=c[1]-.19+j*.047
            g.path('Ink lines on open book',[(c[0]+s*.055,y,c[2]+.092),(c[0]+s*(.31+(.02 if j%3 else -.03)),y,c[2]+.062)],.0025,stone)
    g.path('Open book spine valley',[(c[0],c[1]-.27,c[2]+.073),(c[0],c[1]+.27,c[2]+.073)],.008,wood)

def post_refine(ctx):
    globals().update(ctx)
    group('02 architecture')
    if ID=='ravenclaw':
        # Layered archivolts, sculpted low relief and decorated pedestal base.
        for w,h,y,rad,mat in [(2.83,7.04,5.38,.095,wood),(3.02,7.18,5.49,.055,gold),(2.62,6.84,5.28,.045,gold)]:
            g.arch_frame('Layered carved statue archivolt',(0,y,0),w,h,rad,mat)
        for s in [-1,1]:
            for j in range(15):
                z=.8+j*.35;x=s*(1.36+.025*sin(j*.7))
                g.path('Niche vine relief',[(x,5.23,z),(x-s*.09,5.20,z+.08),(x-s*.04,5.22,z+.23)],.022,gold)
                leaf('Niche carved pointed leaf',(x,5.20,z+.1),(x+s*.095,5.18,z+.28),.042,gold)
        for x in [-7,-4.2,-1.4,1.4,4.2,7]:
            for z in [.36,.72,2.09,6.95,7.47]:
                ring('Stone column raised collar',(x,5.43,z),.36 if z<3 else .40,wood if z<.8 else gold,.026,n=40)
            for k in range(8):
                a=2*pi*k/8
                leaf('Pillar carved acanthus',(x+.34*cos(a),5.43+.34*sin(a),.28),(x+.37*cos(a),5.43+.37*sin(a),.61),.055,gold)
        # Starry swags interrupt the rigid top edge with actual hanging cloth surfaces.
        for x in [-5.6,-2.8,0,2.8,5.6]:
            vs=[];fs=[]
            for j in range(8):
                for k in range(25):
                    u=k/24;v=j/7
                    vs.append((x+(u-.5)*2.75,5.05-.04*cos(u*12*pi),7.98-.68*sin(pi*u)*(.45+.55*v)))
            for j in range(7):
                for k in range(24):a=j*25+k;fs.append((a,a+1,a+26,a+25))
            ob=g.mesh('Starry blue ceiling swag',vs,fs,blue,True);mo=ob.modifiers.new('Cloth thickness','SOLIDIFY');mo.thickness=.025
        group('03 furniture');add_highback((-3.8,-2.1,0),-.30)
        # A loosely folded blue throw over the right couch, beyond its arm and onto the seat.
        sofa_drape((3.1,.65,0),-.22,blue,False)
    else:
        # Secondary blind round arches give the thick stone shell overlapping rhythm.
        for x in [-6.2,-3.65,3.65,6.2]:
            stonearch((x,5.38,2.58),1.06,.29,0,pi,11)
        for x in [-3.65,3.65]:
            # An extra dark recess makes the barrel doors sit behind masonry, not on a flat wall.
            for xx in [x-1.58,x+1.58]:g.box('Deep door jamb return',(xx,5.28,.70),(.29,.90,1.45),stone,.035)
            for z in [.20,.52,.86]:
                for xx in [x-1.68,x+1.68]:g.box('Door pier staggered quoin',(xx,5.02,z),(.49,.73,.28),stone,.03)
        group('03 furniture')
        sofa_drape((-3.13,.48,0),.38,red,True)
        cloth_strip((0,-.45,1.1205),cream,.94,1.16,.09,tablecloth=True)
        # Irregular carved wooden leaves are fitted to mantel and cupboards.
        for s in [-1,1]:
            g.path('Mantel carved stem',[(s*(.15+i*.045),4.59,2.17+.055*sin(i*.28)) for i in range(27)],.018,gold)
        group('04 details')
        # Multiple species and uneven growth, with broad ivy replacing narrow zigzag strips.
        for k in range(360):
            x=random.uniform(-6.8,6.8);z=5.43-random.random()**2*.57
            leaf('Dense organic ivy canopy',(x,5.30,z),(x+random.uniform(-.32,.32),5.14-random.random()*.10,z-random.uniform(.10,.28)),random.uniform(.12,.21),leaflight if k%7==0 else green)
        for x in [-5.0,-2.3,2.1,4.8]:
            for j in range(4):vine((x+j*.14,5.08,3.24),random.uniform(.55,1.1),j+x)
        for x,y,sc in [(-5.1,2.7,1.25),(5.2,2.5,1.15),(-5.7,-2.4,1.2),(5.8,-2.5,1.25)]:
            # Wide curling leaves and a leaning stem produce varied silhouettes.
            for k in range(9):
                a=k*2.399;start=(x,y,.5*sc);end=(x+cos(a)*.68*sc,y+sin(a)*.68*sc,(.75+random.random()*.60)*sc)
                leaf('Broad curled understory plant',start,end,.25*sc,leaflight if k%5==0 else green)
    # Subdivided textile surfaces carry small irregular depressions and tension wrinkles.
    for o in list(S.objects):
        if o.type!='MESH' or not o.name.startswith(('Separate upholstered seat','Tufted high sofa back','Plump loose patterned cushion')):continue
        o.data=o.data.copy();bpy.context.view_layer.objects.active=o
        mod=o.modifiers.new('Cloth topology','SUBSURF');mod.subdivision_type='SIMPLE';mod.levels=2;bpy.ops.object.modifier_apply(modifier=mod.name)
        for v in o.data.vertices:
            x,y,z=v.co
            v.co.z += .018*sin(x*25+y*7)+.009*cos(y*32+x*14)
            if 'back' in o.name.lower():v.co.y += .021*sin(x*19+z*8)+.012*cos(z*26)
        for p in o.data.polygons:p.use_smooth=True
    # Bend facade and its attached furnishings into one enclosing curved wall.
    # All local matrices remain positive. Only rear elements are warped; floor stays flat.
    radius=16 if ID=='ravenclaw' else 10.8
    def bend(v):
        return Vector((radius*sin(v.x/radius),v.y-radius*(1-cos(v.x/radius)),v.z))
    bpy.context.view_layer.update()
    for o in list(S.objects):
        if o.type not in ['MESH','CURVE'] or o.users_collection[0].name[:2] in ['01','05']:continue
        if o.name.startswith(('Side chamber wall','Chamber side stone','Inferred entrance')):continue
        corners=[o.matrix_world@Vector(v) for v in o.bound_box]
        if not corners or sum(v.y for v in corners)/8<4.15:continue
        if o.type=='MESH':
            o.data=o.data.copy();inv=o.matrix_world.inverted()
            if max(v.x for v in corners)-min(v.x for v in corners)>3.0:
                bm=bmesh.new();bm.from_mesh(o.data)
                edges=[e for e in bm.edges if abs((o.matrix_world@e.verts[0].co).x-(o.matrix_world@e.verts[1].co).x)>1]
                if edges:bmesh.ops.subdivide_edges(bm,edges=edges,cuts=20,use_grid_fill=True)
                bm.to_mesh(o.data);bm.free()
            for v in o.data.vertices:v.co=inv@bend(o.matrix_world@v.co)
        else:
            o.data=o.data.copy();inv=o.matrix_world.inverted()
            for spl in o.data.splines:
                for p in spl.points:
                    q=inv@bend(o.matrix_world@Vector(p.co[:3]));p.co=(*q,1)
    # Replace tall blank side panels with thick, faceted segments joining the rounded facade.
    group('02 architecture')
    names=('Side chamber wall','Chamber side stone','Blue lower wall dado','Dado brass rail','Low side pilaster','Pilaster capital')
    for o in list(S.objects):
        if o.name.startswith(names):bpy.data.objects.remove(o,do_unlink=True)
    height=8.15 if ID=='ravenclaw' else 5.60
    for s in [-1,1]:
        if ID=='ravenclaw':points=[(s*6.80,4.40)]+[(s*7.12,3.4-j*.95) for j in range(13)]
        else:points=[(s*(6.65+.16*sin(t*pi)),3.5-t*11.5) for t in [k/12 for k in range(13)]]
        for j in range(len(points)-1):
            a=Vector((*points[j],height/2));b=Vector((*points[j+1],height/2));mid=(a+b)/2
            ang=math.atan2(b.y-a.y,b.x-a.x)
            g.box('Enclosing thick curved side masonry',mid,((b-a).length+.06,.48,height),ivory if ID=='ravenclaw' else stone,.025,ang)
            if ID=='ravenclaw':g.box('Curved navy stone dado',(mid.x,mid.y,.60),((b-a).length+.06,.51,1.20),blue,.01,ang)
    # Light hierarchy is spatial: soft source windows, local warm accents and restrained fill.
    group('05 lighting')
    if ID=='hufflepuff':g.area('Soft leafy window bounce',(0,2.3,4.45),(0,5.1,5.35),95,(.78,.85,.54),6)
    for o in S.objects:
        if o.type!='LIGHT':continue
        if ID=='ravenclaw':
            if o.name.startswith('Cool window'):o.data.energy=580
            elif o.name.startswith('Soft skylight'):o.data.energy=370
            elif o.name.startswith('Warm foreground'):o.data.energy=190;o.data.color=(.70,.78,1)
            elif o.name.startswith('Candle light'):o.data.energy=22
        else:
            if o.name.startswith('Golden circular'):o.data.energy=190;o.data.color=(1,.86,.59)
            elif o.name.startswith('Warm hanging'):o.data.energy=190;o.data.color=(1,.88,.66)
            elif o.name.startswith('Gentle front'):o.data.energy=90;o.data.color=(.82,.86,1)
            elif o.name.startswith('Hearth amber'):o.data.energy=65
    S.world.color=(.07,.09,.13) if ID=='ravenclaw' else (.055,.045,.032)
    S.view_settings.exposure=-.40 if ID=='ravenclaw' else -.35
    S.render.resolution_x=1440;S.render.resolution_y=810;S.render.resolution_percentage=60 if DRAFT else 100
    S.cycles.samples=12 if DRAFT else 32
    cam.location=(-.45,-7.30,3.80) if ID=='ravenclaw' else (-.15,-7.30,3.75)
    target=Vector((0,1.7,1.90 if ID=='ravenclaw' else 1.65))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=21.5;cam.data.sensor_fit='HORIZONTAL'
    ctx['cams'][0]=(ctx['cams'][0][0],[cam.location.x,cam.location.z,-cam.location.y],[target.x,target.z,-target.y])
    # Reduced bounds keep navigation clear of the curved facade edges.
    ctx['refined_bounds']=dict(minX=-6.1,maxX=6.1,minZ=-3.55,maxZ=7.45)
    ctx['refined_fov']=math.degrees(2*math.atan(36/(2*21.5*(1440/810))))

def cloth_strip(c,mat,w,length,a=0,tablecloth=False):
    vs=[];fs=[];nx=16;ny=30
    for j in range(ny+1):
        t=j/ny
        for i in range(nx+1):
            u=i/nx-.5
            drop=(max(0,abs(t-.5)-.27)*2.4 if tablecloth else max(0,t-.48)*1.5)
            z=-drop+.025*sin(u*8*pi+t*9)+.013*cos(t*34+u*8)
            vs.append(local(c,u*w,(t-.5)*length,z,a))
    for j in range(ny):
        for i in range(nx):k=j*(nx+1)+i;fs.append((k,k+1,k+nx+2,k+nx+1))
    o=g.mesh('Folded worn fabric throw' if not tablecloth else 'Draped linen tea cloth',vs,fs,mat,True)
    mod=o.modifiers.new('Fabric true thickness','SOLIDIFY');mod.thickness=.018
    return o

def sofa_drape(c,a,mat,high):
    profile=[(.51,1.72),(.43,1.80),(.36,1.70),(.29,1.30),(.14,.83),(-.15,.82),(-.46,.76),(-.56,.52)] if high else [(.31,.80),(.12,.79),(-.14,.80),(-.43,.78),(-.57,.54),(-.63,.13)]
    x=-.48 if high else .32;w=.60 if high else .82;vs=[];fs=[];n=16
    for j,(y,z) in enumerate(profile):
        for k in range(n+1):
            u=k/n-.5;vs.append(local(c,x+u*w,y+.012*sin(u*8*pi),z+.018*cos(u*10*pi+j*.7),a))
    for j in range(len(profile)-1):
        for k in range(n):p=j*(n+1)+k;fs.append((p,p+1,p+n+2,p+n+1))
    o=g.mesh('Folded throw over actual sofa surface',vs,fs,mat,True);mod=o.modifiers.new('Woven throw thickness','SOLIDIFY');mod.thickness=.014
    return o

def install(ctx):
    globals().update(ctx)
    ctx['statue']=sculpt_statue;ctx['eagle']=large_eagle;ctx['leaf']=botanical_leaf
    globals()['leaf']=botanical_leaf
    ctx['carved_cabinet']=carved_cabinet;ctx['post_refine']=post_refine
    ctx['opened_book']=opened_book
