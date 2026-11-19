"""Preserve object-space procedural coordinates before joining static meshes."""
import bpy

def freeze():
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH' or not obj.data.vertices:continue
        obj.data=obj.data.copy()
        generated=obj.data.attributes.new('BakeGenerated','FLOAT_VECTOR','POINT')
        local=obj.data.attributes.new('BakeLocal','FLOAT_VECTOR','POINT')
        lo=[min(v.co[a] for v in obj.data.vertices) for a in range(3)]
        size=[max(v.co[a] for v in obj.data.vertices)-lo[a] for a in range(3)]
        for index,v in enumerate(obj.data.vertices):
            generated.data[index].vector=tuple((v.co[a]-lo[a])/size[a] if size[a]>1e-8 else 0 for a in range(3))
            local.data[index].vector=v.co
    for mat in bpy.data.materials:
        if not mat.use_nodes:continue
        nt=mat.node_tree
        for node in list(nt.nodes):
            if node.type!='TEX_COORD':continue
            for output,attribute in [('Generated','BakeGenerated'),('Object','BakeLocal')]:
                if output=='Object' and node.object is not None:continue
                links=list(node.outputs[output].links)
                if not links:continue
                attr=nt.nodes.new('ShaderNodeAttribute');attr.attribute_name=attribute
                for link in links:nt.links.new(attr.outputs['Vector'],link.to_socket)
