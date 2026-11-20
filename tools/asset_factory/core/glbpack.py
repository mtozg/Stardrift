"""GLB son işlem (bpy gerektirmez): gömülü dokuları kanal bazlı kaliteyle yeniden kodla, renk profilini/meta veriyi at,
ikili tamponu yeniden paketle. STANDARDS.md §5: base q88, orm/normal q92; WebP, ICC profilsiz."""
import io, json, struct
from PIL import Image

QUALITY = {'base': 88, 'emit': 88, 'orm': 92, 'normal': 92}


def read(path):
    b = open(path, 'rb').read()
    jl = struct.unpack('<I', b[12:16])[0]
    j = json.loads(b[20:20 + jl])
    off = 20 + jl
    bl = struct.unpack('<I', b[off:off + 4])[0]
    return j, b[off + 8: off + 8 + bl]


def write(path, j, views):
    """views: her bufferView için bayt dizisi (sırayla). Ofsetler 4 bayta hizalanır."""
    buf = bytearray()
    for i, data in enumerate(views):
        while len(buf) % 4:
            buf.append(0)
        j['bufferViews'][i]['byteOffset'] = len(buf)
        j['bufferViews'][i]['byteLength'] = len(data)
        buf += data
    while len(buf) % 4:
        buf.append(0)
    j['buffers'] = [{'byteLength': len(buf)}]
    js = json.dumps(j, separators=(',', ':'), ensure_ascii=False).encode()
    js += b' ' * ((4 - len(js) % 4) % 4)
    total = 12 + 8 + len(js) + 8 + len(buf)
    with open(path, 'wb') as f:
        f.write(struct.pack('<4sII', b'glTF', 2, total))
        f.write(struct.pack('<I4s', len(js), b'JSON') + js)
        f.write(struct.pack('<I4s', len(buf), b'BIN\x00') + bytes(buf))
    return total


def recompress_textures(path, out_path=None, quality=QUALITY):
    j, bin_ = read(path)
    views = []
    for bv in j['bufferViews']:
        o = bv.get('byteOffset', 0)
        views.append(bin_[o:o + bv['byteLength']])
    report = {}
    for im in j.get('images', []):
        name = im.get('name', '')
        ch = next((k for k in quality if name.endswith('_' + k)), 'base')
        src = Image.open(io.BytesIO(views[im['bufferView']]))
        mode = 'RGB' if src.mode != 'RGBA' else 'RGBA'
        bio = io.BytesIO()
        src.convert(mode).save(bio, 'WEBP', quality=quality[ch], method=6, exact=False)   # icc_profile/exif yazılmaz
        new = bio.getvalue()
        report[name] = {'channel': ch, 'q': quality[ch], 'kb_before': round(len(views[im['bufferView']]) / 1024, 1), 'kb_after': round(len(new) / 1024, 1)}
        views[im['bufferView']] = new
        im['mimeType'] = 'image/webp'
    size = write(out_path or path, j, views)
    return size, report
