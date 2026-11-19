"""Optimize embedded campus textures after Blender export. Requires Python 3 and Pillow."""
from io import BytesIO
import json
from pathlib import Path
import struct
from PIL import Image

def compact(path):
    data=path.read_bytes()
    size,=struct.unpack_from('<I',data,12)
    doc=json.loads(data[20:20+size])
    source=data[28+size:]
    images={im['bufferView']:im for im in doc['images']}
    buffer=bytearray()
    for i,view in enumerate(doc['bufferViews']):
        start=view.get('byteOffset',0)
        raw=source[start:start+view['byteLength']]
        if i in images and len(raw)>100_000:
            with Image.open(BytesIO(raw)) as img:
                alpha='A' in img.getbands() and img.getchannel('A').getextrema()[0]<255
                limit=640 if alpha else 576
                img.thumbnail((limit,limit),Image.Resampling.LANCZOS)
                out=BytesIO()
                if alpha:img.save(out,'PNG',optimize=True)
                else:img.convert('RGB').save(out,'JPEG',quality=84,optimize=True)
                if len(out.getvalue())<len(raw):
                    raw=out.getvalue()
                    images[i]['mimeType']='image/png' if alpha else 'image/jpeg'
        view['byteOffset']=len(buffer)
        view['byteLength']=len(raw)
        buffer.extend(raw)
        buffer.extend(b'\0'*(-len(buffer)%4))
    doc['buffers'][0]['byteLength']=len(buffer)
    desc=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode()
    desc+=b' '*(-len(desc)%4)
    packed=struct.pack('<4sIIII',b'glTF',2,28+len(desc)+len(buffer),len(desc),0x4e4f534a)+desc+struct.pack('<II',len(buffer),0x004e4942)+buffer
    dest=path.with_suffix('.glb.part');dest.write_bytes(packed);dest.replace(path)
if __name__=='__main__':
    compact(Path(__file__).resolve().parents[1]/'grounds.glb')
