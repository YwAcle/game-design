"""Build three editable exterior studies and render their review cameras in Blender."""
from math import cos, exp, pi, sin, sqrt, tau
from pathlib import Path
from random import Random
import sys

import bpy
from mathutils import Vector
from mathutils.geometry import interpolate_bezier

OUT = Path(__file__).resolve().parent
rng = Random()
group = None


def color(hex_value):
    channels = [int(hex_value[i:i+2], 16)/255 for i in (0, 2, 4)]
    return tuple(v/12.92 if v < .04045 else ((v+.055)/1.055)**2.4 for v in channels)


def paint(name, dark, light=None, grain=(3, 3, 3), glow=0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color(light or dark), 1)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    link = material.node_tree.links.new
    shader = nodes.get('Principled BSDF')
    shader.inputs['Roughness'].default_value = .92
    shader.inputs['Base Color'].default_value = material.diffuse_color
    shader.inputs['Emission Color'].default_value = material.diffuse_color
    shader.inputs['Emission Strength'].default_value = glow
    if light:
        coords = nodes.new('ShaderNodeTexCoord')
        stretch = nodes.new('ShaderNodeVectorMath')
        stretch.operation = 'MULTIPLY'
        stretch.inputs[1].default_value = grain
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 1
        noise.inputs['Detail'].default_value = 1.4
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .26
        ramp.color_ramp.elements[0].color = (*color(dark), 1)
        ramp.color_ramp.elements[1].position = .75
        ramp.color_ramp.elements[1].color = (*color(light), 1)
        link(coords.outputs['Object'], stretch.inputs[0])
        link(stretch.outputs[0], noise.inputs[0])
        link(noise.outputs['Fac'], ramp.inputs[0])
        link(ramp.outputs[0], shader.inputs['Base Color'])
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .13
        bump.inputs['Distance'].default_value = .047
        link(noise.outputs['Fac'], bump.inputs['Height'])
        link(bump.outputs[0], shader.inputs['Normal'])
    return material


def collection(name):
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll


def mesh(name, verts, faces, mats, indices=None):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    group.objects.link(obj)
    for mat in mats:
        data.materials.append(mat)
    if indices:
        for face, index in zip(data.polygons, indices):
            face.material_index = index
    return obj


def box(name, at, size, mat, angle=0, bevel=0):
    x, y, z = at
    u, v, w = (a/2 for a in size)
    c, s = cos(angle), sin(angle)
    verts = [(x+a*c-b*s, y+a*s+b*c, z+d) for a,b,d in
             [(-u,-v,-w),(u,-v,-w),(u,v,-w),(-u,v,-w),(-u,-v,w),(u,-v,w),(u,v,w),(-u,v,w)]]
    obj = mesh(name, verts, [(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)], [mat])
    if bevel:
        mod = obj.modifiers.new('Worn edges', 'BEVEL')
        mod.width, mod.segments = bevel, 1
    return obj


def rock(name, at, size, mats, seed=0):
    noise = Random(seed)
    x,y,z = at
    a,b,c = size
    ridges = [.78+.22*noise.random() for _ in range(7)]
    verts = []
    for r,h in [(.75,-.42),(1,.12),(.60,.73)]:
        for i in range(7):
            angle = tau*i/7 + seed*.71
            verts.append((x+a*r*ridges[i]*cos(angle)+h*a*.19,
                          y+b*r*ridges[i]*sin(angle)-h*b*.12,
                          z+c*(h+noise.uniform(-.20,.20))))
    faces = [tuple(reversed(range(7)))]
    for k in [0,7]:
        for i in range(7):
            j=(i+1)%7
            faces.extend([(k+i,k+j,k+7+i),(k+j,k+7+j,k+7+i)])
    faces.extend([(14,15+i,16+i) for i in range(5)])
    palette = [0]+[noise.randrange(len(mats)) for _ in faces[1:29]]+[len(mats)-1]*5
    return mesh(name,verts,faces,mats,palette)


def sweep(name, nodes, mats, sides=12, phase=0):
    """Continuous tapered rings, with long ridges following the bend."""
    points = [Vector(p[:3]) for p in nodes]
    verts, faces, indices = [], [], []
    for i,(p,node) in enumerate(zip(points,nodes)):
        axis = (points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized()
        reference = Vector((0,0,1)) if abs(axis.y)>.98 else Vector((0,1,0))
        horizontal = reference.cross(axis).normalized()
        vertical = axis.cross(horizontal)
        for j in range(sides):
            a = tau*j/sides + phase + .08*i
            radius=node[3]*(1+.16*cos(5*a-.27*i)+.075*sin(3*a+phase))
            verts.append(tuple(p + radius*(horizontal*cos(a)+vertical*sin(a))))
            if i:
                q=(i-1)*sides
                k=(j+1)%sides
                faces.append((q+j,q+k,q+sides+k,q+sides+j))
                indices.append((j*5+j//3)%len(mats))
    faces.extend((tuple(reversed(range(sides))),tuple(range(len(verts)-sides,len(verts)))))
    obj=mesh(name,verts,faces,mats,indices+[0,0])
    for face in obj.data.polygons[:-2]:
        face.use_smooth=len(nodes)>4 and sides>=10
    return obj


def limb(name, bends, mats, sides=14):
    points = [Vector(p[:3]) for p in bends]
    nodes = []
    for i,p in enumerate(points[:-1]):
        q = points[i+1]
        t0 = (q-points[max(i-1,0)])*.19
        t1 = (points[min(i+2,len(points)-1)]-p)*.19
        samples = interpolate_bezier(p,p+t0,q-t1,q,5)
        for j,v in enumerate(samples[:-1]):
            r=bends[i][3]+(bends[i+1][3]-bends[i][3])*j/4
            nodes.append((*v,r))
    nodes.append(bends[-1])
    return sweep(name,nodes,mats,sides,rng.uniform(0,1))


def gather_tiles(name, quads, mats):
    vertices, faces, indices = [], [], []
    for top,index in quads:
        i=len(vertices)
        vertices.extend(top+[(x,y,z-.065) for x,y,z in top])
        faces.extend([tuple(i+j for j in face) for face in
                      [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]])
        indices.extend([index,index,*([0]*4)])
    mesh(name,vertices,faces,mats,indices)


def willow():
    bark = [paint('Bark · furrow','201f22','423c34',(9,9,1.1)),
            paint('Bark · old ridge','322a24','665a48',(8,8,.9)),
            paint('Bark · split heartwood','473832','806a52',(11,11,1.3)),
            paint('Bark · weathered olive','2b2b25','515744',(12,12,1.4))]
    moss = paint('Olive moss','313f2b','67724a',(5,5,5))
    earth = [paint('Root soil','23221e','454334'),moss]
    rock('Root mound',(-.25,.20,-.21),(3.65,2.85,.67),earth)
    trunk=[(-.58,.05,-.42,1.20),(-.49,.13,.75,1.03),(-.24,.12,1.94,.89),
           (.50,.07,3.32,.82),(.92,.17,4.31,.76),(.63,.33,5.16,.58),
           (.65,.20,6.06,.34),(.16,.28,6.98,.11),(.29,.23,7.64,.018)]
    trunk=[(x,y,z,radius*1.30) for x,y,z,radius in trunk]
    limb('Twisted heart of the willow',trunk,bark,32)
    for i in range(14):
        a = tau*i/14+.18*rng.random()
        v=Vector((cos(a),sin(a),0))
        r = rng.uniform(2.85,5.18)
        limb('Exposed lateral root',[(-.40,.04,1.82 if i%3==0 else 1.22,.51),
            (*(v*1.48+Vector((-.36,0,.54))),.48),(*(v*(r*.68)+Vector((-.48,.08,.18))),.25),
            (*(v*r+Vector((-.65,0,-.14))),.026)],bark,16)
        if i%2:
            q=v*(r*.59)
            limb('Fork of exposed root',[(q.x-.48,q.y,.21,.16),
                (q.x+v.x*.75-v.y*.42,q.y+v.y*.75+v.x*.42,.09,.10),
                (q.x+v.x*1.75-v.y*.67,q.y+v.y*1.75+v.x*.67,-.16,.016)],bark,10)
        if i%2==0:
            p=v*(r*.60)
            rock('Moss against root',(p.x-.48,p.y,.13),(.48,.42,.20),earth,i)
    arms=[
        [( .62,.14,3.99,.56),(-.92,-.16,4.55,.51),(-2.38,-.12,4.97,.39),(-3.75,-.20,5.28,.26),(-4.74,-.15,6.19,.16),(-5.46,-.23,6.25,.072),(-5.89,-.25,6.82,.014)],
        [( .68,.19,4.73,.51),(-.35,.20,5.46,.41),(-.93,.27,6.64,.29),(-1.90,.30,7.19,.18),(-2.65,.11,8.37,.075),(-2.57,.00,9.22,.012)],
        [( .71,.28,4.50,.53),(2.20,.13,4.23,.49),(3.22,.17,4.52,.39),(4.06,.42,5.49,.29),(5.10,.49,5.77,.16),(6.02,.35,6.71,.023)],
        [( .70,.26,4.93,.43),(1.56,.53,6.01,.33),(2.95,.45,6.56,.22),(3.54,.48,7.55,.12),(4.34,.50,8.40,.016)],
        [( .54,.42,4.86,.50),(.45,1.55,5.09,.42),(-.15,2.57,5.81,.28),(-.48,3.68,6.53,.16),(-.17,4.64,7.08,.018)],
        [( .48,.16,4.67,.42),(1.04,-1.06,5.34,.34),(1.37,-2.25,5.61,.23),(2.25,-3.06,6.50,.11),(2.46,-4.01,7.23,.014)],
        [( .18,.12,3.28,.45),(-.41,-.43,3.96,.32),(-1.33,-1.48,4.48,.23),(-2.71,-2.01,4.44,.15),(-3.64,-2.65,5.56,.018)],
        [( .57,.22,5.23,.36),(1.03,1.03,6.28,.26),(1.95,1.86,7.10,.12),(2.15,2.29,8.98,.020)],
        [(.23,.09,3.58,.62),(-1.40,.24,3.96,.56),(-3.20,.53,3.99,.38),
         (-4.52,.54,3.82,.25),(-5.67,.83,4.28,.13),(-6.42,.95,5.06,.028)],
        [(.69,.27,4.20,.58),(1.96,-.47,3.89,.52),(3.29,-1.02,3.58,.34),
         (4.51,-1.37,3.82,.22),(5.49,-1.64,4.51,.075),(5.87,-1.87,5.43,.024)],
    ]
    for arm_index,arm in enumerate(arms):
        arm=[(x*1.22,y*1.14,z,r*(1.15 if i<3 else 1.06))
             for i,(x,y,z,r) in enumerate(arm)]
        limb('Primary willow arm',arm,bark,22)
        for n,(x,y,z,r) in enumerate(arm[2:-1]):
            for direction in [-1,1]:
                dx=direction*rng.uniform(.42,1.28)+.13*arm_index-.45
                dy=rng.uniform(-.90,.74)
                dz=rng.uniform(.65,1.34)
                a=(x+dx*.61,y+dy*.64,z+dz*.63,r*.34)
                b=(x+dx,y+dy,z+dz,r*.17)
                c=(x+dx*1.3,y+dy*.85,z+dz+rng.uniform(.40,1.15),.013)
                limb('Knot and long whip',[(x,y,z,r*.52),a,b,c],bark,10)
                for fork in [-1,1]:
                    tip=(b[0]+fork*rng.uniform(.22,.66),b[1]+rng.uniform(-.45,.45),
                         b[2]+rng.uniform(.58,1.31),.009)
                    limb('Bare twig',[a,(b[0]+fork*.24,b[1],b[2]+.13,.029),tip],bark[:2],7)
        x,y,z,_=arm[-2]
        for i in range(4):
            dx=rng.uniform(-1.12, .87)
            dy=rng.uniform(-.63, .84)
            h=rng.uniform(1.3,2.25)
            limb('Untrimmed upright shoot',[(x,y,z,.072),(x+dx*.55,y+dy*.68,z+h*.55,.039),
                 (x+dx,y+dy,z+h,.007)],bark[0:2],8)
    for i in range(8):
        p=trunk[i]
        q=trunk[i+1]
        a=i*.83
        ridge=[(p[0]+p[3]*cos(a),p[1]+p[3]*sin(a),p[2],p[3]*.18),
               ((p[0]+q[0])/2+p[3]*cos(a+.57)*.92,(p[1]+q[1])/2+p[3]*sin(a+.57)*.92,(p[2]+q[2])/2,p[3]*.15),
               (q[0]+q[3]*cos(a+1.20),q[1]+q[3]*sin(a+1.20),q[2],.024)]
        limb('Twisted grain and growth ridge',ridge,bark[1:],11)
    for i in range(3):
        t=i*.58
        limb('Torn ridge at an old branch scar',[(.25+t*.32,-1.01,2.02+t,.10),
            (.55+t*.32,-1.05,2.36+t,.15),(.77+t*.32,-.95,2.57+t,.075),
            (.81+t*.29,-.81,2.62+t,.025)],bark[0:3],10)
    heartwood=paint('Dry end grain','514036','977854',(5,5,4))
    pitch=paint('Deep split in the bark','241f1b')
    for start,end,radius in [((.29,-.38,3.91),(1.48,-1.36,4.22),.20),
                             ((-1.35,.31,4.47),(-2.02,-.57,4.99),.146)]:
        branch=Vector(end)-Vector(start)
        direction=branch.normalized()
        face=Vector(end)+direction*.025
        limb('Broken branch stump',[(*start,radius*1.83),(*end,radius)],bark,18)
        sweep('Exposed branch end',[(*end,radius*.89),(*face,radius*.86)],[heartwood],18)
        e1=Vector((0,0,1)).cross(direction).normalized()
        e2=direction.cross(e1)
        for ring_radius in (.36,.63,.80):
            ring=[(*(face+direction*.004+radius*ring_radius*
                      (e1*cos(tau*i/22)+e2*sin(tau*i/22))),.009) for i in range(23)]
            sweep('Visible tree rings on broken wood',ring,[bark[1]],6)
    split=[(.12,-1.14,1.80,.025),(.37,-1.08,2.16,.051),(.50,-1.00,2.39,.045),
           (.76,-.96,2.63,.041),(.82,-.91,2.92,.013)]
    limb('Split shaded by the grain ridge',split,[pitch],8)
    plank=paint('Passage oak','332920','765c42',(1,14,11))
    iron=paint('Weathered iron','272a2e','625d4c')
    for i in range(5):
        box('Root passage hatch',(-.52+i*.24,-2.01,.036),(.229,1.10,.14),plank,.028*(i-2),.022)
    for y in [-2.41,-1.64]:
        box('Hatch strap',(-.045,y,.116),(1.19,.073,.038),iron,0,.01)
    ring=[(-.05+.16*cos(tau*i/15),-1.94+.12*sin(tau*i/15),.138,.023) for i in range(16)]
    sweep('Hatch ring',ring,[iron],7)


def timber_materials(along_y=False):
    palette=[('pitch','241b19','51352b'),('faded umber','3b2722','825747'),
             ('old red stain','4e3127','91705a'),('grey edge','413a31','897b66')]
    grain=(14,1.5,18) if along_y else (1.5,14,18)
    return [paint('Timber · '+name,dark,light,grain) for name,dark,light in palette]


def roof_materials():
    return [paint('Slate · shadow','20282e','3b4d56',(9,9,14)),
            paint('Slate · smoke','33424d','60737b',(9,9,14)),
            paint('Slate · blue grey','3a4856','71808b',(8,8,13)),
            paint('Slate · cold lichen','414a49','747e73',(8,8,13))]


def shack():
    wood=timber_materials()
    side_wood=timber_materials(along_y=True)
    slate=roof_materials()
    stone=[paint('Foundation · deep grey','363739','666359'),paint('Foundation · warm grey','514a41','877663')]
    brick=[paint('Chimney · old terracotta','5c3a30','935f49'),paint('Chimney · soot','3e2b29','6e4b3f')]
    glass=paint('Amber through the shutters','b16c37',glow=1.2)
    dark=paint('Shutter recess','201f23')
    iron=paint('Rusted iron hardware','312820','73563d',(7,7,8))
    rotten=paint('Grey rot on exposed timber','302921','5d5b48',(1.8,14,18))
    # Closed stepped foundations under the two legs of the L-shaped plan.
    box('Main stone footing',(-.64,0,.17),(5.25,5.90,.76),stone[0],-.015,.09)
    box('East wing footing',(2.81,.65,.16),(2.07,3.44,.73),stone[0],0,.08)
    for i in range(27):
        x=-3.22+i*.255
        box('Irregular footing stone',(x,-2.91,.28+rng.uniform(-.05,.05)),(.24,.26,rng.uniform(.22,.44)),
            rng.choice(stone),rng.uniform(-.08,.08),.027)
    # In each elevation the boards stop at the rectangular openings.
    elevations=[
        ((-.65,-2.88),0,5.18,3.86,[(-.67,.46,1.72,2.53),(.96,.49,2.03,3.12),(-1.74,.41,2.15,3.02)]),
        ((-.65,2.88),pi,5.18,3.75,[(-.93,.49,1.50,2.56),(1.39,.57,2.05,3.02)]),
        ((-3.22,0),-pi/2,5.81,3.74,[(-.67,.55,1.52,2.90),(1.54,.46,2.07,3.03)]),
        ((1.94,-1.98),pi/2,1.82,3.69,[]),((1.94,2.62),pi/2,.54,3.69,[]),
        ((2.91,-1.05),0,1.96,3.44,[(.19,.55,1.36,2.57)]),
        ((2.91,2.38),pi,1.96,3.40,[]),
        ((3.88,.67),pi/2,3.45,3.42,[(.05,.53,.45,2.28),(-1.15,.33,1.59,2.36)]),
    ]
    for (x,y),angle,w,height,holes in elevations:
        def local(s,d,z):
            return x+s*cos(angle)-d*sin(angle),y+s*sin(angle)+d*cos(angle),z
        blocks = wood
        if abs(sin(angle)) > .5:
            blocks = side_wood
        z=.46
        while z<height-.025:
            thickness=min(.19,height-z)
            spans=[(-w/2,w/2)]
            for mid,r,lo,hi in holes:
                if z < hi and z+thickness > lo:
                    spans=[span for a,b in spans for span in [(a,min(b,mid-r)),(max(a,mid+r),b)] if span[1]-span[0]>.055]
            for a,b in spans:
                middle=(a+b)/2
                material=rotten if z<1.30 and rng.random()<.52 else rng.choice(blocks[:3])
                box('Split clapboard',local(middle,rng.uniform(-.057,.034),z+thickness/2),
                    (b-a-.012,.19,thickness+.02),material,angle+rng.uniform(-.013,.013),.022)
            z+=thickness
        for mid,r,lo,hi in holes:
            height=hi-lo
            box('Recessed backing',local(mid,.14,(lo+hi)/2),(r*2,.16,height),dark,angle)
            for side in [-1,1]:
                box('Old jamb',local(mid+side*r,-.036,(lo+hi)/2),(.128,.29,height+.18),wood[3],angle,.021)
            for edge in [lo,hi]:
                box('Window lintel or sill',local(mid,-.08,edge),(r*2+.28,.31,.135),wood[1],angle,.021)
            if lo>.6:
                if x>1.90 or mid<-.6:
                    box('Warm light between boards',local(mid+r*.15,.044,(lo+hi)/2),
                        (r*.71,.087,height*.64),glass,angle,.009)
                for i in range(3):
                    offset=(i-1)*height*.31
                    skew=rng.uniform(-.13,.19)
                    p=local(mid-r-.09,-.19,(hi+lo)/2+offset-skew)
                    q=local(mid+r+.10,-.21,(hi+lo)/2+offset+skew)
                    limb('Cracked boarding',[(*p,.086),(*q,.068)],wood[:2],5)
                if (mid<-.76 and y<0) or (x>3 and mid<0):
                    p=local(mid-r-.09,-.245,hi+.11)
                    q=local(mid+r+.10,-.245,lo-.083)
                    limb('Last diagonal nail-up',[(*p,.109),(*q,.089)],wood[1:3],5)
            else:
                for i in range(5):
                    box('East passage door',local(mid+(i-2)*.20,-.024,(hi+lo)/2),(.193,.15,height-.09),wood[0],angle,.014)
                for z in (lo+.31,hi-.33):
                    box('Rusted door strap',local(mid-.13,-.119,z),(.69,.061,.113),iron,angle,.012)
                    box('Door hinge knuckle',local(mid-r+.025,-.139,z),(.073,.088,.21),iron,angle,.014)
                    for u in (-.38,-.16,.06):
                        box('Rivet on the hinge strap',local(mid+u,-.163,z),(.041,.027,.043),
                            stone[1],angle,.008)
                box('Door latch back plate',local(mid+.31,-.139,1.31),(.20,.056,.17),iron,angle,.015)
                box('Door latch grip',local(mid+.31,-.183,1.31),(.15,.071,.048),iron,angle,.012)
    # Main roof faces south. The transverse wing starts within the main roof;
    # its inside edges follow the intersection line to close the valley.
    def main(u,v,side):
        return (-.57+side*u*(2.86+.16*v)+.23*sin(v*pi),-3.39+6.80*v,
                7.60-.83*v+.32*cos(tau*v)-u*(3.70+.29*sin(v*pi))-.44*sin(u*pi))
    def wing(u,v,side):
        return (1.34+3.20*v,.66+side*(2.04*u)+.16*sin(pi*v),
                5.91+.95*v+.12*cos(tau*v)-u*(2.53+.10*v)-.28*sin(u*pi))
    for label,fn,cols,rows in [('Principal gable',main,16,14),('Cross gable',wing,8,11)]:
        for side in [-1,1]:
            def point(u,v):
                if label=='Cross gable':
                    vmin=max(0,(u-.08)*.24)
                    v=vmin+(1-vmin)*v
                return fn(u,v,side)
            tiles, deck = [], []
            for row in range(rows):
                for col in range(cols):
                    top=[point(u,v) for u,v in [(row/rows,col/cols),((row+1)/rows,col/cols),
                         ((row+1)/rows,(col+1)/cols),(row/rows,(col+1)/cols)]]
                    if (side==1) == (label=='Cross gable'):
                        top.reverse()
                    deck.append(([(x,y,z-.031) for x,y,z in top],0))
            gather_tiles(label+' roof deck',deck,slate)
            ribs=[]
            for row in range(rows):
                u0=row/rows
                u1=min(1,(row+1.22)/rows)
                for col in range(-1,cols):
                    offset=.46*(row%2)
                    v0=max(0,(col+offset)/cols)
                    v1=min(1,(col+offset+.94)/cols)
                    if v1-v0<.008:
                        continue
                    damaged=(label=='Principal gable' and side==1 and
                             (row,col) in {(6,3),(6,4),(7,3),(7,4),(8,4),(5,3)})
                    if damaged:
                        ribs.append((point(u0,v0),point(u1,v0)))
                        continue
                    top=[point(u,v) for u,v in [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]]
                    if (side==1) == (label=='Cross gable'):
                        top.reverse()
                    curl=rng.uniform(.003,.046) if rng.random()<.17 else .001
                    top=[(x,y,z+.071+rng.uniform(-.014,.016)+(curl if j in (1,2) else 0))
                         for j,(x,y,z) in enumerate(top)]
                    tiles.append((top,rng.choices(range(4),(25,40,18,17))[0]))
            gather_tiles(label+' · overlapping slates',tiles,slate)
            for a,b in ribs:
                limb('Splintered roof batten',[(a[0],a[1],a[2]+.012,.041),
                     (b[0],b[1],b[2]+.031,.027)],wood[:2],6)
            for v in [0,1]:
                limb('Twisted bargeboard',[(*point(u,v),.10 if u<.99 else .086) for u in [0,.35,.68,1]],wood[0:2],8)
            limb('Overhanging eave',[(*point(1,v),.075) for v in (0,.23,.55,.82,1)],wood[:2],8)
        limb('Ridge flashing',[(*fn(0,v,1),.083) for v in (0,.18,.42,.64,.85,1)],slate[:2],9)
    # Fill the volume between the clapboards and gables, behind the slate verges.
    for fn,v,dx,dy in [(main,.075,0,.105),(main,.923,0,-.105),(wing,.787,-.06,0)]:
        left, peak, right = fn(1,v,-1),fn(0,v,1),fn(1,v,1)
        sill = min(3.27,left[2]-.08,right[2]-.08)
        front=[(left[0],left[1],sill),left,peak,right,(right[0],right[1],sill)]
        back=[(x+dx,y+dy,z) for x,y,z in front]
        verts=front+back
        faces=[tuple(range(5)),tuple(reversed(range(5,10)))]
        faces.extend((j,j+5,(j+1)%5+5,(j+1)%5) for j in range(5))
        mesh('Timber infill beneath the gable',verts,faces,[wood[0]])
        for i in range(1,18):
            t=i/18
            point_left=Vector(left).lerp(Vector(peak),t)
            point_right=Vector(right).lerp(Vector(peak),t)
            point_left+=Vector((-.20*dx,-.20*dy,0))
            point_right+=Vector((-.20*dx,-.20*dy,0))
            center=(point_left+point_right)/2
            delta=point_right-point_left
            from_angle = 0 if fn==main else pi/2
            box('Uneven siding beneath the verge',center,(delta.length,.095,.164),rng.choice(wood[:3]),from_angle,.012)
        for point in [left,right]:
            beam_start=(point[0],point[1],3.62)
            limb('Gable edge framing',[(*beam_start,.055),(*peak,.108)],wood[:2],7)
    for x, y, z, angle in [(-.65,-2.99,5.24,0),(4.04,.67,4.60,pi/2)]:
        out=Vector((sin(angle),-cos(angle),0))
        mid=Vector((x,y,z))
        box('Inset attic frame',mid-out*.068,(.57,.34,.85),wood[0],angle,.024)
        box('Attic lantern through a crack',mid+out*.11,(.31,.045,.57),glass,angle,.012)
        box('Attic mullion',mid+out*.149,(.078,.060,.64),wood[3],angle,.01)
    for x,y,base in [(-1.44,.98,6.40),(2.46,1.42,5.67)]:
        for row in range(10 if x<0 else 6):
            center=(x+.022*row,y+.011*row,base+row*.192)
            box('Chimney brick course',center,(.83-(row%2)*.046,.76,.181),brick[row%2],row*.014,.028)
            for i in [-1,1]:
                box('Chimney face brick',(center[0]+i*.187,center[1]-.379,center[2]),
                    (.349,.083,.16),brick[int(rng.random()<.42)],row*.014,.016)
        box('Chimney cap',(center[0],center[1],center[2]+.15),(.96,.90,.18),brick[1],.12,.033)
    # Rack the entire frame above its footing so every wall, trim and roof share the lean.
    for obj in group.objects:
        for vertex in obj.data.vertices:
            x,y,z=vertex.co
            bend=max(0,z-.46)
            vertex.co.x += -.095*bend-.012*bend*sin(y*.94)
            vertex.co.y += .034*bend
            vertex.co.z += .033*(x+.64)*min(1,bend*.65)
    for i in range(3):
        box('Step to the passage',(3.87+i*.21,.70,.43-i*.123),(.29,1.12+i*.10,.30),
            stone[i%2],pi/120*i,.03)
    for i in range(12):
        x=-4.24+i*.60
        y=-4.21+.16*cos(i*.75)
        if 6<=i<=7:
            continue
        z=rng.uniform(.54,.90)
        limb('Bent iron garden paling',[(x,y,-.08,.029),(x+.05,y,z,.028),(x+.02,y,z+.15,.006)],
             [dark],7)
    for a,b in [(-4.24,-1.27),(.55,2.38)]:
        for z in [.28,.59]:
            limb('Weathered rail',[(a,-4.20,z,.037),((a+b)/2,-4.24,z-.05,.036),(b,-4.22,z+.03,.038)],[dark],7)
    ivy=[paint('Ivy · ink green','25372e','4d6048'),
         paint('Ivy · sage tip','344938','667152'),paint('Ivy · dry edge','433f27','786c46')]
    verts,faces,indices=[],[],[]
    for x,y,angle,height in [(-2.76,-3.04,0,2.08),(1.66,-3.08,0,2.42),
                              (.84,2.99,pi,2.17),(4.02,2.11,pi/2,1.39)]:
        origin=Vector((x,y,-.08))
        out=Vector((sin(angle),-cos(angle),0))
        across=Vector((cos(angle),sin(angle),0))
        stem=[]
        for i in range(12):
            t=i/11
            z=t*height
            p=origin+Vector((-.096*z,.026*z,z))+across*(.24*sin(i*1.09))+out*.085
            stem.append((*p,.025-.016*t))
            for k in [-1,1]:
                scale=rng.uniform(.10,.235)
                start=len(verts)
                c=p+across*(k*.12)+out*rng.uniform(.056,.16)
                verts.extend([tuple(c+across*(a*scale)+Vector((0,0,b*scale))+out*d) for a,b,d in
                              [(0,.44,.035),(-.52,.29,0),(-.55,-.12,0),(0,-.84,.063),
                               (.55,-.12,0),(.52,.29,0),(0,-.1,.088)]])
                faces.extend((start+j,start+(j+1)%6,start+6) for j in range(6))
                indices.extend([rng.choices(range(3),(62,29,9))[0]]*6)
        sweep('Ivy stem against the clapboards',stem,ivy[:1],6)
    mesh('Ivy leaves with folded veins',verts,faces,ivy,indices)


def arch(profile, half, rise, z0, head, crown):
    return [(half*profile[0],z0),(half*profile[0],head),(half*profile[1],head+rise*.55),
            (half*profile[2],head+rise*.88),(0,crown),(-half*profile[2],head+rise*.88),
            (-half*profile[1],head+rise*.55),(-half*profile[0],head),(-half*profile[0],z0)]


def owlery():
    rock_mats=[paint('Crag · deep blue grey','252e36','51606a'),paint('Crag · layered schist','39424a','687278'),
               paint('Crag · heather and lichen','434d42','7b7c67')]
    ash=[paint('Tower · mortar','363836','605d58'),paint('Tower · low ashlar','4b4944','867d6e'),
         paint('Tower · edge ashlar','60574a','9c8d75'),paint('Tower · grey ochre','464746','77776e')]
    wood=timber_materials()
    slate=roof_materials()
    brass=paint('Roof finials · antiqued brass','514732','a08a56')
    ember=paint('Amber panes','b97637',glow=1.2)
    dim=paint('Dark amber panes','705239','a07b4a',glow=.18)
    noir=paint('Interior shade','1b2026')
    rock('Owlery rock spur',(0,1.35,.27),(3.49,2.85,2.67),rock_mats,4)
    for x,y,z,a,b,c in [(-2.57,-.5,.29,1.62,1.15,1.95),(1.95,-1.38,.27,1.21,1.09,1.18),
                        (-1.23,2.20,.38,1.25,1.43,1.66),(2.24,1.85,.55,1.82,.80,1.19)]:
        rock('Split rock shoulder',(x,y,z),(a,b,c),rock_mats,int(10+x*3+y))
    sides=8
    def panel(side,u,depth,z,r):
        angle=tau*side/sides-pi/2
        return (cos(angle)*(r+depth)-sin(angle)*u,sin(angle)*(r+depth)+cos(angle)*u,z)
    def block(name,side,a,b,lo,hi,r,mat,depth=.32):
        angle=tau*side/sides-pi/2
        return box(name,panel(side,(a+b)/2,0,(lo+hi)/2,r),
                   (b-a,depth,hi-lo),mat,angle+pi/2,.023)
    # The shaft tapers, then a projecting crown takes three setbacks on corbels.
    def radius(z):
        if z<10.2:
            return 1.76-.043*(z-1.9)
        if z<11.45:
            return 1.40+(z-10.2)*.49
        return 2.015-.022*(z-11.45)
    levels=[(1.55,10.36),(10.36,11.49),(11.49,14.73)]
    for side in range(sides):
        windows=[(0,1.57,3.81,.55)] if side==0 else []
        if side%2==0:
            windows.extend([(0,5.02,6.45,.245),(.035,8.1,9.08,.21)])
        elif side in [1,3,5,7]:
            windows.append((-.04,6.71,7.99,.235))
        windows.extend([(-.40,11.62,12.66,.284),(.40,11.62,12.66,.284),
                        (0,12.97,14.49,.61)])
        if side%2:
            windows.append((0,4.10,5.18,.20))
        for bottom,top in levels:
            rows=round((top-bottom)/.255)
            for i in range(rows):
                lo=bottom+(top-bottom)*i/rows
                hi=bottom+(top-bottom)*(i+1)/rows
                r=radius((lo+hi)/2)
                half=r*(sqrt(2)-1)+.019
                spans=[(-half,half)]
                for center,base,tip,width in windows:
                    if lo<tip and hi>base:
                        # Wedge stones finish the points inside the stepped opening.
                        hole=width*min(1,max(.24,(tip-lo)/(width*.64)))
                        spans=[span for a,b in spans for span in [(a,min(b,center-hole)),(max(a,center+hole),b)] if span[1]-span[0]>.025]
                for a,b in spans:
                    if b-a>.57:
                        cut=(a+b)/2+rng.uniform(-.11,.11)
                        cuts=[(a,cut-.013),(cut+.013,b)]
                    else:
                        cuts=[(a,b)]
                    for start,end in cuts:
                        grade=rng.choice(ash[1:]) if bottom>2 or side%2 else ash[1]
                        block('Dressed tower masonry',side,start,end,lo+.006,hi-.006,r,grade,.38)
        for center,base,tip,width in windows:
            r=radius((base+tip)/2)
            roost=base>12.8
            head=tip-width*.84
            shape=arch((1,.77,.40),width,tip-head,base,head,tip)
            outer=arch((1,.79,.43),width+.121,tip-head+.10,base-.075,head+.020,tip+.128)
            inner=[panel(side,center+u,.185,z,r) for u,z in shape]
            on_wall=[panel(side,center+u,.168,z,r) for u,z in outer]
            reveal_depth=-.24 if roost else -.25
            back=[panel(side,center+u,reveal_depth,z,r) for u,z in shape]
            vs=inner+on_wall+back
            count=len(shape)
            fs=[]
            for i in range(count-1):
                fs.extend([(i+1,i,i+count,i+1+count),(i,i+1,i+1+2*count,i+2*count)])
            surround=mesh('Pointed stone arch and deep reveal',vs,fs,[ash[2],ash[0]],[i%2 for i in range(len(fs))])
            for poly in surround.data.polygons:
                if poly.area<=1e-8:
                    raise ValueError('Degenerate window reveal')
            backing=noir if base<2 else (ember if (side+int(base*3)+int(center*9))%4==0 else dim)
            if roost:
                wall_end=(r+reveal_depth)*(sqrt(2)-1)+.025
                side_faces=back+[panel(side,wall_end if i<4 else -wall_end,reveal_depth,z,r)
                                 for i,(_,z) in enumerate(shape) if i!=4]
                jambs=[(i,i+1,i+1+count,i+count) for i in range(3)]
                jambs.extend((i,i+1,i+count,i+count-1) for i in range(5,8))
                mesh('Continuous inner ashlar at the open arch',side_faces,jambs,[ash[0]])
                cap=back[3:6]+[panel(side,u,reveal_depth,14.68,r)
                               for u in (wall_end,0,-wall_end)]
                mesh('Masonry backing above the arch',cap,[(0,3,4,1),(1,4,5,2)],[ash[0]])
            else:
                mesh('Deep recessed door or pane',back,[tuple(range(count))],[backing])
            if base<2:
                for j in range(5):
                    u=center+(j-2)*.193
                    block('Entry door oak board',side,u-.093,u+.093,base,head+.032,r-.227,wood[1],.087)
                for z in (base+.42,head-.26):
                    block('Door hinge rail',side,center-.477,center+.477,z,z+.08,r-.17,wood[0],.09)
            else:
                overhang=.40 if roost else .13
                block('Stone landing shelf' if roost else 'Perch sill',side,
                      center-width-.10,center+width+.10,base-.14,base-.035,r+overhang,ash[2],
                      .89 if roost else .43)
                if roost:
                    for u in [-.47,.47]:
                        a=panel(side,u,.11,12.61,r)
                        b=panel(side,u,.69,12.82,r)
                        limb('Perch bracket',[(*a,.077),(*b,.067)],wood[1:3],7)
                elif backing==ember or base<10:
                    block('Window mullion',side,center-.027,center+.027,base,head,r-.16,wood[0],.056)
                if backing==ember and 4<base<10:
                    for z in (base+.25,base+.57):
                        for sign in (-1,1):
                            p=panel(side,center-width*.72,-.135,z,r)
                            q=panel(side,center+width*.73,-.135,z+sign*.34,r)
                            limb('Lead diagonal in the amber window',[(*p,.017),(*q,.017)],wood[:1],5)
        for level in [1.49,3.99,6.59,9.68,10.34,11.40,12.76,14.62]:
            r=radius(level)+.13
            w=r*(sqrt(2)-1)+.035
            block('Projecting masonry belt',side,-w,w,level-.10,level+.08,r,ash[2],.29)
        for u in [-.54,0,.54]:
            top=panel(side,u,.36,11.37,radius(11.37))
            bottom=panel(side,u*.70,.16,10.20,radius(10.20))
            limb('Corbel under the lantern floor',[(*bottom,.075),(*top,.139)],wood[0:2],6)
        if side%2:
            for i in range(13):
                z=1.56+i*.322
                block('Outer buttress',side,-.23,.23,z,z+.295,radius(z)+.22-.014*i,ash[2],.62-.024*i)
    # Tile rows narrow towards a bent, needle-like summit.
    def roof_point(u,t):
        center_x=.29*u*u
        radius=2.72*(1-u)**1.21+.09
        angle=t*tau+pi/8
        return (center_x+radius*cos(angle),radius*sin(angle),14.51+5.91*u+.10*sin(angle*3)*(1-u))
    quads=[]
    for row in range(18):
        a=row/18
        b=min(1,(row+1.23)/18)
        count=max(8,round(35*(1-a)**.76))
        for j in range(count):
            t=(j+(row%2)*.44)/count
            q=t+.93/count
            top=[roof_point(a,t),roof_point(a,q),roof_point(b,q),roof_point(b,t)]
            quads.append((top,rng.choices(range(4),(20,47,25,8))[0]))
    gather_tiles('Curved octagonal roof · split slate',quads,slate)
    under=[roof_point(i/18,j/48) for i in range(19) for j in range(48)]
    mesh('Continuous roof underlay',[(x*.984,y*.984,z-.035) for x,y,z in under],
         [(i*48+j,i*48+(j+1)%48,(i+1)*48+(j+1)%48,(i+1)*48+j) for i in range(18) for j in range(48)],[slate[0]])
    for j in range(sides):
        t=j/sides
        curve=[(*roof_point(u,t),.073-.045*u) for u in [0,.18,.39,.60,.80,.98]]
        limb('Slate hip flashing',curve,slate[:2],8)
        x,y,z=roof_point(.071,t)
        limb('Iron spike at roof corner',[(x,y,z,.085),(x+.10*cos(t*tau),y+.10*sin(t*tau),z+.89,.018)],[brass],8)
    limb('Gilt needle finial',[(.29,0,20.22,.125),(.30,0,20.59,.075),(.33,0,21.43,.021)],[brass],11)
    box('Entry landing',(0,-1.97,.77),(1.22,.81,1.55),ash[1],0,.033)
    for i in range(8):
        y=-2.36-i*.262
        top=1.49-i*.192
        box('Rock stair tread',(-i*.085,y,(top-.16)/2),(1.05,.36,top+.16),ash[2],
            -.032*i,.024)
    # Floors fit under the window sills and leave the large upper arches open.
    for height in (11.51,12.86):
        for i in range(-8,9):
            offset=i*.20
            span=2*min(1.75,2.46-abs(offset))
            box('Octagonal roost floor board',(0,offset,height),(span,.195,.14),
                wood[i%3],0,.012)
        for x in (-.88,.88):
            box('Joist under boarded floor',(x,0,height-.11),(.14,3.43,.19),wood[0],0,.024)
    for z in (13.92,14.42):
        for side in (0,2):
            a=panel(side,0,-.30,z,2)
            b=panel(side+4,0,-.30,z,2)
            limb('Crossbeam across the owl loft',[(*a,.108),(*b,.108)],wood[:2],8)
    reed=[paint('Old nest reeds','3d3226','776247'),paint('Pale feather','87877a','d1c2a7')]
    for i,(x,y,z) in enumerate([(-.99,.99,12.96),(.96,1.05,12.96),(.92,-.86,12.96)]):
        rock('Woven nest floor',(x,y,z-.01),(.35,.29,.10),reed[:1],i)
        for j in range(19):
            a=tau*j/19
            b=a+rng.uniform(.42,.95)
            size=rng.uniform(.28,.39)
            limb('Nest twig',[(x+size*cos(a),y+size*.80*sin(a),z,.026),
                 (x+size*cos((a+b)/2),y+size*.81*sin((a+b)/2),z+.105,.033),
                 (x+size*cos(b),y+size*.80*sin(b),z+.051,.012)],reed[:1],6)
    for i in range(13):
        x,y=rng.uniform(-1.52,1.52),rng.uniform(-1.42,1.42)
        length=rng.uniform(.14,.265)
        angle=rng.uniform(0,tau)
        axis=Vector((cos(angle),sin(angle),0))
        across=Vector((-sin(angle),cos(angle),0))
        p=Vector((x,y,12.945))
        points=[p-axis*length*.38,p+across*length*.185+axis*length*.22,
                p+axis*length,p-across*length*.15+axis*length*.19,
                p+axis*length*.29+Vector((0,0,.023))]
        mesh('Moulted owl feather',points,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],reed[1:])
    box('Lantern plate in the loft',(.03,.75,13.01),(.28,.26,.13),wood[0],0,.014)
    box('Loft lantern glass',(.03,.75,13.17),(.181,.18,.25),ember,0,.013)
    box('Loft lantern hood',(.03,.75,13.33),(.28,.26,.09),wood[0],0,.01)
    plumage = [paint('Owl · warm ivory','b4a78c','e3d6b9'),paint('Owl · tawny wing','615246','ad8a69'),
               paint('Owl · facial disc','c3b697','ebddbc'),paint('Owl · eye','1a191b')]
    for location,heading,shade in [((-.98,.98,13.07),.66,0),((.72,.77,12.94),-.37,1),
                                   ((2.24,-.05,12.94),pi*.44,0)]:
        root=Vector(location)
        rotation=lambda x,y,z: root+Vector((x*cos(heading)-y*sin(heading),x*sin(heading)+y*cos(heading),z))
        forms=[('body',(0,0,.25),(.157,.136,.238),shade),
               ('head',(0,-.012,.491),(.145,.123,.135),shade),
               ('face',(0,-.105,.479),(.116,.055,.101),2),
               ('left wing',(-.111,.013,.228),(.068,.104,.176),1),
               ('right wing',(.111,.013,.228),(.068,.104,.176),1),
               ('tail',(0,.080,.125),(.078,.152,.064),1),
               ('left eye',(-.048,-.152,.50),(.016,.011,.017),3),
               ('right eye',(.048,-.152,.50),(.016,.011,.017),3),
               ('beak',(0,-.156,.46),(.024,.028,.035),1)]
        for name,at,size,material in forms:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8, radius=1,
                                                 location=rotation(*at))
            obj=bpy.context.object
            obj.name='Perched owl · '+name
            obj.scale=size
            obj.rotation_euler.z=heading
            for coll in list(obj.users_collection):
                coll.objects.unlink(obj)
            group.objects.link(obj)
            obj.data.materials.append(plumage[material])
            for polygon in obj.data.polygons:
                polygon.use_smooth=True


def ridge(radius, profile, materials):
    verts, faces, indices = [], [], []
    count=len(profile)
    # Continuous terrain around all four inspection cameras.
    for row, (depth, height) in enumerate([(-11,0),(-5,.41),(0,1),(7,.57),(15,0)]):
        for i, peak in enumerate(profile):
            angle=tau*i/count
            r=radius+depth+(1.4+row*.22)*sin(9*angle)
            verts.append((r*cos(angle),r*sin(angle),height*peak-1.8))
    for row in range(4):
        for i in range(count):
            a=row*count+i
            b=row*count+(i+1)%count
            faces.extend([(b,a,a+count),(b,a+count,b+count)])
            indices.extend([rng.randrange(len(materials)),rng.randrange(len(materials))])
    mesh('Layered Highland ridge',verts,faces,materials,indices)


def landscape(kind):
    turf=[paint('Glen grass','303b2d','657453',(.79,.91,2.3)),
          paint('Worn path','4e4d40','88806b',(2.8,3.5,3.7)),
          paint('Damp hollow and moss','233329','4f6043',(1.3,1.4,2.1))]
    stone=[paint('Field stones','3b4448','68737a'),paint('Moss on field stone','434837','727a53')]
    grass=[paint('Dry sedge','5e583b'),paint('Heather olive','484b35'),paint('Heather umber','74624b')]
    if kind=='shack':
        turf[0]=paint('Cold grass and frost','334240','727f76',(1.1,1.1,2))
    def ground_z(x,y):
        level=-.12+.075*sin(x*.85)*cos(y*.61)+.027*cos(1.1*y+x*.8)
        if kind=='willow':
            level += .82*exp(-((x+6.8)**2+(y-3.7)**2)/28)
            level += .93*exp(-((x-8.6)**2+(y-8.5)**2)/31)
            level -= .36*exp(-((x-1.4)**2+(y+5.5)**2)/14)
        return level
    width=185
    vertices=[(x*.6,y*.6,ground_z(x*.6,y*.6)) for y in range(-87,88) for x in range(-92,93)]
    faces=[]
    for row in range(174):
        for col in range(width-1):
            a=row*width+col
            faces.extend([(a,a+1,a+width+1),(a,a+width+1,a+width)])
    obj=mesh('Glen and approach',vertices,faces,turf)
    for face in obj.data.polygons:
        x,y,_=face.center
        track=abs(x-.18*y-.65*sin(y*.44))
        if y < -1.2 and track < .68+.15*sin(.76*y):
            face.material_index=1
        elif track>.88 and sin(x*.54+y*.17)*cos(y*.73-x*.12)>.37:
            face.material_index=2
        face.use_smooth=True
    for i in range(62):
        a=rng.uniform(0,tau)
        r=rng.uniform(3.6,13)
        x,y=r*cos(a),r*sin(a)
        if y<0 and abs(x-.18*y)<1.42:
            continue
        z=ground_z(x,y)+.027
        if i%3==0:
            s=rng.uniform(.15,.68)
            rock('Ground scree',(x,y,z),(s,s*.78,s*.66),stone,i)
        else:
            for j in range(6):
                dx=rng.uniform(-.12,.12)
                dy=rng.uniform(-.11,.11)
                high=rng.uniform(.14,.31)
                mesh('Dry grass strokes',[(x+dx-.014,y+dy,z),(x+dx+.018,y+dy,z),
                    (x+dx*1.55,y+dy*1.60,z+high)],[(0,1,2)],[rng.choice(grass)])
    hill_colors=[('445b59','5c7072'),('586981','81909f'),('667693','98a4b6')]
    for i,(dark,light) in enumerate(hill_colors):
        mats=[paint('Distance shadow '+str(i),dark,light,(.08,.11,.095),.22+i*.14),
              paint('Distant haze '+str(i),light,glow=.17+i*.18)]
        profile=[(6.8+i*6.2)+(2.2+i*1.2)*sin(j*tau/112*5+i*.7)+
                 2.8*cos(j*tau/112*11-i*.55)+rng.uniform(-.7,1.6) for j in range(112)]
        ridge(48+i*22,profile,mats)
    distant=[paint('Distant evergreen shadow','243635','465b4f'),
             paint('Distant evergreen edge','304643','59735a'),
             paint('Needle tips · smoke','3b5146','6d7c63')]
    for i in range(128):
        x=rng.uniform(-50,50)
        y=rng.choice([-1,1])*rng.uniform(16,45)
        if abs(x+.30*y)<9 and abs(y)<37:
            continue
        h=rng.uniform(2.4,8.4)
        phase=rng.uniform(0,1)
        base=ground_z(x,y)
        sweep('Fir trunk',[(x,y,base-.12,.036*h),(x+.058*h,y,base+.81*h,.017*h)],distant[:1],7,phase)
        needles,facets,palette=[],[],[]
        for tier in range(7):
            bottom=base+(tier*.107+.10)*h
            root=.219*h*(1-.133*tier)
            start=len(needles)
            tip_count=18
            for ring in (0,1):
                for j in range(tip_count):
                    theta=tau*j/tip_count+phase+.31*tier
                    skirt=1+.18*sin(j*7+tier)+.09*cos(j*3-tier)
                    depth=((1.13 if j%2 else .79) if ring==0 else .54)*root*skirt
                    z=bottom+(.11*sin(j*4+tier)+(.2 if ring==1 else 0))*root
                    needles.append((x+depth*cos(theta)+.018*tier*h/7,y+depth*sin(theta),z))
            top=len(needles)
            needles.append((x+.064*h,y,bottom+.25*h))
            for j in range(tip_count):
                a,b=start+j,start+(j+1)%tip_count
                facets.extend([(a,b,b+tip_count),(a,b+tip_count,a+tip_count),
                               (a+tip_count,b+tip_count,top)])
                palette.extend((0,1,(j+tier)%3))
        mesh('Layered fir sprays',needles,facets,distant,palette)
    # Broad tufts and smaller heather clumps break up the ground strokes.
    heather=[paint('Thyme · umber','31362b','65634c'),paint('Thyme · sage','3c473d','696d57')]
    for i in range(54):
        x,y=rng.uniform(-13,13),rng.uniform(-10,14)
        if abs(x)<3.7 and (y<1.4 or y<4 and kind=='shack'):
            continue
        if kind=='shack' and abs(x)<4.1 and abs(y)<3.2:
            continue
        z=ground_z(x,y)
        size=rng.uniform(.13,.56)
        rock('Low heather strokes',(x,y,z),(size,size*.79,size*.54),heather,i)
    # Irregular blade groups give the model a readable foreground at walking height.
    verts,faces,indices=[],[],[]
    for i in range(285):
        x,y=rng.uniform(-14,14),rng.uniform(-11,13)
        if (abs(x)<3.40 and abs(y)<3.8) or (y<0 and abs(x-.18*y)<.87):
            continue
        if kind=='shack' and abs(x+.05)<4.45 and abs(y+.3)<3.35:
            continue
        if kind=='owlery' and abs(x)<1.65 and -4.7<y<-1.2:
            continue
        z=ground_z(x,y)-.025
        for j in range(rng.randrange(5,11)):
            a=rng.uniform(0,tau)
            dx,dy=cos(a),sin(a)
            length=rng.uniform(.12,.39)
            width=rng.uniform(.016,.045)
            c=(x+dx*.075,y+dy*.075,z)
            start=len(verts)
            verts.extend([(c[0]-dy*width,c[1]+dx*width,z),(c[0]+dy*width,c[1]-dx*width,z),
                (c[0]+dx*length*.29,c[1]+dy*length*.29,z+length*.53),
                (c[0]+dx*length*.67,c[1]+dy*length*.67,z+length)])
            faces.extend([(start,start+1,start+2),(start+1,start+3,start+2)])
            indices.extend([rng.randrange(3)]*2)
    mesh('Banks of hand-shaped sedge',verts,faces,grass,indices)
    if kind=='willow':
        for i,(x,y,s) in enumerate([(-5.51,1.72,1.27),(4.25,4.52,1.86),(6.2,1.47,.80),
                                  (-5.81,-3.63,.62),(2.94,-4.37,.72)]):
            rock('Mossy slate along the roots',(x,y,ground_z(x,y)-.11),
                 (s,s*.78,s*.79),stone,i+19)
        dead=paint('Deadfall · exposed heartwood','3c342b','82745a',(3,13,17))
        for x,y,s in [(-5.55,-2.16,1.0),(3.20,-4.18,.71),(-2.88,5.31,1.2)]:
            z=ground_z(x,y)
            limb('Fallen forked wood',[(x,y,z,.12*s),(x+.47*s,y+.33*s,z+.09,.10*s),
                 (x+.91*s,y+.16*s,z+.12,.066*s),(x+1.4*s,y+.44*s,z+.02,.023*s)],[dead],9)
            limb('Broken twig on deadfall',[(x+.47*s,y+.33*s,z+.09,.061*s),
                 (x+.84*s,y+.73*s,z+.23,.032*s),(x+1.08*s,y+1.04*s,z+.16,.014*s)],[dead],7)


def lighting(kind):
    scene=bpy.context.scene
    world=bpy.data.worlds.new('Indigo dusk')
    scene.world=world
    world.use_nodes=True
    bg=world.node_tree.nodes.get('Background')
    coords=world.node_tree.nodes.new('ShaderNodeTexCoord')
    stretch=world.node_tree.nodes.new('ShaderNodeVectorMath')
    stretch.operation='MULTIPLY'
    stretch.inputs[1].default_value=(2.2,2.2,7.3)
    noise=world.node_tree.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=3.8
    noise.inputs['Detail'].default_value=2
    ramp=world.node_tree.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=(*color('626f88'),1)
    ramp.color_ramp.elements[0].position=.21
    ramp.color_ramp.elements[1].color=(*color('a6a8c1'),1)
    ramp.color_ramp.elements[1].position=.80
    world.node_tree.links.new(coords.outputs['Normal'],stretch.inputs[0])
    world.node_tree.links.new(stretch.outputs[0],noise.inputs[0])
    world.node_tree.links.new(noise.outputs['Fac'],ramp.inputs[0])
    world.node_tree.links.new(ramp.outputs[0],bg.inputs[0])
    bg.inputs[1].default_value=.77
    def area(name,at,target,power,hex_value,size):
        data=bpy.data.lights.new(name,'AREA')
        data.energy=power
        data.shape='DISK'
        data.size=size
        data.color=color(hex_value)
        obj=bpy.data.objects.new(name,data)
        group.objects.link(obj)
        obj.location=at
        obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    target=(0,0,7 if kind=='owlery' else 3.3)
    area('Remaining evening on the west face',(-11,-8,13),target,2050,'f1cda9',9.8)
    area('Blue skylight over the ridge',(6,8,16),target,4600,'b2c3f7',12)
    area('Cloud bounce',(6,-12,10),target,830,'b0c9d9',13)
    if kind == 'owlery':
        at, power=(.03,.71,13.39),26
    elif kind == 'shack':
        at, power=(3.75,-1.36,1.95),32
    else:
        at, power=(-2.1,-3.9,1.39),20
    lamp=bpy.data.lights.new('Amber bounce','POINT')
    lamp.color=(1,.52,.22)
    lamp.energy=power
    lamp.shadow_soft_size=.30
    obj=bpy.data.objects.new('Amber bounce',lamp)
    group.objects.link(obj)
    obj.location=at


CAMERAS={
    'willow': ((-17.8,-19.5,6.05),(-.16,0,4.98),21.2),
    'shack': ((15,-17,6.25),(-.22,0,3.62),15.15),
    'owlery': ((19,-24,12.15),(0,0,10.51),24.4),
}


def render_study(kind, builder, seed):
    global group
    rng.seed(seed)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.name=kind.title()+' · exterior study'
    scene.unit_settings.system='METRIC'
    group=collection(kind.title()+' · editable asset')
    group.asset_mark()
    builder()
    objects=list(group.objects)
    assert all(obj.type=='MESH' and obj.data.materials and len(obj.data.polygons)>0 for obj in objects)
    degenerate = [obj.name for obj in objects if any(poly.area <= 1e-9 for poly in obj.data.polygons)]
    assert not degenerate, degenerate
    print(f'{kind}: {len(objects)} editable objects, {sum(len(obj.data.polygons) for obj in objects)} faces',flush=True)
    group=collection('Review · glen and horizon')
    scenery=group
    landscape(kind)
    group=collection('Review · light')
    lighting(kind)
    group=collection('Review · cameras')
    cameras={}
    position,target,scale=CAMERAS[kind]
    x,y,z=target
    views={
        'hero':(position,target,scale),
        'front':((x,-30,z),(x,y,z),scale),
        'side':((30,y,z),(x,y,z),scale),
        'rear':((x,30,z),(x,y,z),scale),
    }
    if kind=='owlery':
        views['loft']=((-.28,-1.48,13.48),(.19,1.02,13.34),20)
    for label,(position,target,scale) in views.items():
        data=bpy.data.cameras.new(label)
        if label in ('hero','loft'):
            data.type='PERSP'
            data.lens=36*(Vector(position)-Vector(target)).length/scale if label=='hero' else scale
        else:
            data.type='ORTHO'
            data.ortho_scale=scale
        data.clip_end=230
        camera=bpy.data.objects.new(label+' · '+kind,data)
        group.objects.link(camera)
        camera.location=position
        camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        cameras[label]=camera
    scene.camera=cameras['hero']
    scene.render.engine='CYCLES'
    scene.cycles.samples=24
    scene.cycles.use_denoising=True
    scene.render.threads_mode='FIXED'
    scene.render.threads=12
    scene.view_settings.view_transform='AgX'
    scene.view_settings.look='AgX - Medium High Contrast'
    scene.view_settings.exposure=.35
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.render.resolution_x,scene.render.resolution_y=(800,950) if kind=='owlery' else (1000,680)
    scene.render.filepath='//'+kind+'.png'
    bpy.ops.object.select_all(action='DESELECT')
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_perspective='CAMERA'
                area.spaces.active.shading.color_type='MATERIAL'
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(kind+'.blend')),compress=True)
    for label,camera in cameras.items():
        scene.camera=camera
        if label in ('front','side','rear'):
            scene.render.resolution_percentage=65
            scene.cycles.samples=12
            scene.render.film_transparent=True
            scene.render.image_settings.color_mode='RGBA'
            scenery.hide_render=True
        elif label=='loft':
            scene.render.resolution_x,scene.render.resolution_y=1000,680
            scene.render.resolution_percentage=85
            scene.cycles.samples=20
            scene.render.film_transparent=False
            scene.render.image_settings.color_mode='RGB'
            scenery.hide_render=False
        scene.render.filepath=str(OUT/(kind+('' if label=='hero' else '-'+label)+'.png'))
        bpy.ops.render.render(write_still=True)


studies={'willow':(willow,51),'shack':(shack,42),'owlery':(owlery,98)}
for kind in sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else studies:
    builder,seed=studies[kind]
    render_study(kind,builder,seed)
