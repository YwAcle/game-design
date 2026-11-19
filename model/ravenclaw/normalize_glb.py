"""Convert baked emissive atlas materials to portable KHR_materials_unlit."""
import json,struct,sys
from pathlib import Path
def normalize(path):
    p=Path(path);blob=p.read_bytes();magic,version,length=struct.unpack_from('<4sII',blob)
    assert magic==b'glTF' and length==len(blob)
    offset=12;chunks=[]
    while offset<len(blob):
        n,kind=struct.unpack_from('<II',blob,offset);offset+=8;chunks.append((kind,blob[offset:offset+n]));offset+=n
    data=json.loads(chunks[0][1]);used=set(data.get('extensionsUsed',[]));count=0
    for mat in data.get('materials',[]):
        if not mat.get('name','').startswith('Baked |'):continue
        tex=mat.pop('emissiveTexture',None);mat.pop('emissiveFactor',None)
        pbr=mat.setdefault('pbrMetallicRoughness',{});pbr['baseColorFactor']=[1,1,1,1];pbr['metallicFactor']=0;pbr['roughnessFactor']=1
        if tex:pbr['baseColorTexture']=tex
        ex=mat.setdefault('extensions',{});ex.pop('KHR_materials_emissive_strength',None);ex['KHR_materials_unlit']={};used.add('KHR_materials_unlit');count+=1
        # Open decorative leaves and curtain surfaces are intentionally visible both sides.
        mat['doubleSided'] = mat['name'] == 'Baked | details'
        if mat['name'] == 'Baked | statue':
            # Match the statue's original color map to the room's subdued lighting.
            pbr['baseColorFactor'] = [.68, .71, .78, 1]
            mat['doubleSided'] = True
    data['extensionsUsed']=sorted(used)
    raw=json.dumps(data,separators=(',',':')).encode();raw+=b' '*((-len(raw))%4);chunks[0]=(chunks[0][0],raw)
    out=b''.join(struct.pack('<II',len(x),k)+x for k,x in chunks);p.write_bytes(struct.pack('<4sII',b'glTF',2,len(out)+12)+out)
    print('UNLIT_NORMALIZED',p.name,count)
if __name__=='__main__':normalize(sys.argv[1])
