"""Normalize authored static baked textures to explicit KHR_materials_unlit.

Only materials explicitly named 'Baked | ...' are changed. Fire, glass and
other authored materials retain their own glTF semantics.
"""
import json, struct
from pathlib import Path

def normalize(path):
    path=Path(path);blob=path.read_bytes()
    assert blob[:4]==b'glTF'
    offset=12;chunks=[]
    while offset<len(blob):
        length,kind=struct.unpack_from('<II',blob,offset);offset+=8
        chunks.append((kind,blob[offset:offset+length]));offset+=length
    doc=json.loads(next(data for kind,data in chunks if kind==0x4E4F534A))
    count=0
    for material in doc.get('materials',[]):
        if not material.get('name','').startswith('Baked |'):continue
        texture=material.pop('emissiveTexture',None)
        if texture is None:raise ValueError('Baked material has no emissive texture')
        material.pop('emissiveFactor',None)
        material['pbrMetallicRoughness']={'baseColorFactor':[1,1,1,1],'baseColorTexture':texture,'metallicFactor':0,'roughnessFactor':1}
        material.setdefault('extensions',{}).pop('KHR_materials_emissive_strength',None)
        material['extensions']['KHR_materials_unlit']={}
        count+=1
    used=doc.setdefault('extensionsUsed',[])
    if 'KHR_materials_unlit' not in used:used.append('KHR_materials_unlit')
    data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4)
    result=bytearray()
    for kind,chunk in chunks:
        if kind==0x4E4F534A:chunk=data
        result+=struct.pack('<II',len(chunk),kind)+chunk
    path.write_bytes(struct.pack('<4sII',b'glTF',2,len(result)+12)+result)
    print('NORMALIZED_BAKED_MATERIALS',count,flush=True)
    return count

if __name__=='__main__':
    import sys
    normalize(sys.argv[1])
