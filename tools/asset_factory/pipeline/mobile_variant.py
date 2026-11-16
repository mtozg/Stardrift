"""Teslim GLB'sinden telefon varyantı: yalnız dokular küçültülür (geometri, düğümler, malzemeler bayt düzeyinde aynı kalır).
Kaşif'in oyundaki iki dosyalı düzeninin (cockpit_kasif.glb / cockpit_kasif_m.glb) karşılığı. Onaylı teslim dosyasına dokunmaz; yeni dosya yazar.
Kullanım: python pipeline/mobile_variant.py <girdi.glb> <çıktı.glb> [en_büyük_kenar=1024]"""
import io, json, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image
from qc import glb_checks


def main(src, dst, maxe=1024):
    j, b, _ = glb_checks.read_glb(src)
    views = []      # her bufferView için yeni bayt dizisi
    imgv = {im['bufferView']: im for im in j.get('images', [])}
    report = []
    for i, bv in enumerate(j['bufferViews']):
        o = bv.get('byteOffset', 0)
        data = b[o:o + bv['byteLength']]
        if i in imgv:
            im = Image.open(io.BytesIO(data))
            if max(im.size) > maxe:
                k = maxe / max(im.size)
                small = im.resize((round(im.size[0] * k), round(im.size[1] * k)), Image.LANCZOS)
                buf = io.BytesIO()
                q = 88 if 'base' in (imgv[i].get('name') or '') else 92      # teslim kodlaması: base q88, ORM/normal q92 (ICC yok)
                small.save(buf, 'WEBP', quality=q, method=6)
                report.append({'image': imgv[i].get('name'), 'from': list(im.size), 'to': list(small.size), 'kb': round(len(buf.getvalue()) / 1024, 1)})
                data = buf.getvalue()
        views.append(data)
    out = bytearray()
    for bv, data in zip(j['bufferViews'], views):
        while len(out) % 4:
            out.append(0)
        bv['byteOffset'] = len(out)
        bv['byteLength'] = len(data)
        out += data
    while len(out) % 4:
        out.append(0)
    j['buffers'][0]['byteLength'] = len(out)
    js = json.dumps(j, separators=(',', ':')).encode()
    js += b' ' * ((4 - len(js) % 4) % 4)
    glb = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(out)) + struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(out), 0x004E4942) + bytes(out)
    open(dst, 'wb').write(glb)
    print('RESULT', json.dumps({'out': dst, 'bytes': len(glb), 'images': report}, ensure_ascii=False))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1024)
