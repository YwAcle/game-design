"""Build the atlas paths from the web navigation polylines."""
from math import sin

import bpy
from mathutils import Vector


def draw_paths(group, layout, places, ground, material):
    approaches = [view['at'] for view in layout['views'] if view['id'] == 'owlery-stairs']
    landmarks = {'cave','owlery','willow','shack','ruins','camp','gamekeeper-trail','broomsticks','hogs-head'}
    for trail in layout['trails']:
        if not any(isinstance(point,str) and point in landmarks for point in trail) and trail[-1] not in approaches:
            continue
        vertices, faces = [], []
        for p,q in zip(trail,trail[1:]):
            a,b=(Vector(places[v]['at'] if isinstance(v,str) else v) for v in (p,q))
            vector=b-a
            along=vector.normalized()
            across=Vector((-along.y,along.x))
            steps=max(2,int(vector.length*2))
            offset=len(vertices)
            for i in range(steps+1):
                center=a.lerp(b,i/steps)
                for j in (-1,0,1):
                    x,z=center+across*j*(.52+.12*sin(i*.62))
                    vertices.append((x,-z,ground(x,-z)+.038))
            for i in range(steps):
                edge=offset+i*3
                faces.extend([(edge+j,edge+j+1,edge+j+4,edge+j+3) for j in (0,1)])
        data=bpy.data.meshes.new('Contoured trail')
        data.from_pydata(vertices,[],faces)
        uv = data.uv_layers.new(name='Ground projection')
        for loop in data.loops:
            x,y,_ = data.vertices[loop.vertex_index].co
            uv.data[loop.index].uv = (x*.52,y*.52)
        data.materials.append(material)
        group.objects.link(bpy.data.objects.new(data.name,data))
