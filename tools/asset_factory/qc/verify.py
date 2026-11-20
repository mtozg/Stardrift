"""BUDGET MODE hızlı doğrulama: bir GLB'yi (ve varsa teslim manifestini) yerel Python ile birkaç saniyede denetler. Blender ve tarayıcı gerekmez.
Kapsam: dosya bütünlüğü (GLB başlığı, parça uzunlukları, buffer/accessor sınırları, görsellerin çözülmesi), SHA256 ↔ manifest, bütçe (boyut, üçgen,
draw call, GPU tahmini, malzeme sayısı, uzantılar), kokpit ekran sözleşmesi, isteğe bağlı Khronos doğrulayıcısı.
Bu, tam QC'nin yerine geçmez: render karşılaştırması, UV/doku ölçümleri ve yeniden üretilebilirlik yalnız `qc` komutundadır. Teslim öncesi tam QC zorunludur.
Kullanım (doğrudan): python qc/verify.py <glb> <sınıf> [manifest.json] [--validator]"""
import json, os, struct, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.paths import file_hash, load_json
from qc import glb_checks

QC_DIR = os.path.dirname(os.path.abspath(__file__))
CT_SIZE = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}


def _read_chunks(path):
    b = open(path, 'rb').read()
    out = []
    if len(b) < 20:
        return b, ['dosya çok kısa'], None, None
    magic, ver, length = struct.unpack('<4sII', b[:12])
    if magic != b'glTF' or ver != 2:
        out.append('GLB başlığı geçersiz')
    if length != len(b):
        out.append('başlıktaki uzunluk %d ≠ dosya %d' % (length, len(b)))
    off, js, bn = 12, None, None
    while off + 8 <= len(b):
        cl, ct = struct.unpack('<II', b[off:off + 8])
        data = b[off + 8:off + 8 + cl]
        if off + 8 + cl > len(b):
            out.append('parça dosya sınırını aşıyor')
            break
        if ct == 0x4E4F534A and js is None:
            js = data
        elif ct == 0x004E4942 and bn is None:
            bn = data
        off += 8 + cl
        if cl % 4:
            out.append('parça 4 bayta hizalı değil')
    return b, out, js, bn


def integrity(path):
    """(sorunlar, json, bin)"""
    b, bad, js, bn = _read_chunks(path)
    if js is None:
        return bad + ['JSON parçası yok'], None, None
    try:
        j = json.loads(js)
    except Exception as e:
        return bad + ['JSON çözülemedi: %s' % e], None, None
    if bn is None and j.get('buffers'):
        bad.append('BIN parçası yok')
        bn = b''
    for i, bv in enumerate(j.get('bufferViews', [])):
        if bv.get('byteOffset', 0) + bv['byteLength'] > len(bn):
            bad.append('bufferView %d buffer dışına taşıyor' % i)
    if j.get('buffers') and j['buffers'][0]['byteLength'] > len(bn):
        bad.append('buffers[0].byteLength BIN parçasından büyük')
    for i, a in enumerate(j.get('accessors', [])):
        if 'bufferView' not in a:
            continue
        bv = j['bufferViews'][a['bufferView']]
        n = glb_checks.NC[a['type']] * CT_SIZE[a['componentType']]
        need = a.get('byteOffset', 0) + (a['count'] - 1) * (bv.get('byteStride') or n) + n if a['count'] else 0
        if need > bv['byteLength']:
            bad.append('accessor %d bufferView sınırını aşıyor' % i)
    return bad, j, bn


def metrics(j, bn):
    tris = prims = tris_ns = 0
    for n in j.get('nodes', []):
        if 'mesh' in n:
            for pr in j['meshes'][n['mesh']]['primitives']:
                prims += 1
                t = (j['accessors'][pr['indices']]['count'] if 'indices' in pr else j['accessors'][pr['attributes']['POSITION']]['count']) // 3
                tris += t
                if not str(n.get('name', '')).startswith('SCR_'):
                    tris_ns += t
    gpu, imgs, bad = 0, [], []
    for t in j.get('textures', []):
        src = t.get('source', t.get('extensions', {}).get('EXT_texture_webp', {}).get('source'))
        try:
            im, _ = glb_checks.image(j, bn, src)
            im.load()
            gpu += im.size[0] * im.size[1] * 4 * 4 // 3      # RGBA8 + mip; r128'de her doku girişi ayrı yüklenir
            imgs.append(im.size)
        except Exception as e:
            bad.append('görsel %s çözülemedi: %s' % (src, e))
    return {'tris': tris, 'tris_noscr': tris_ns, 'primitives': prims, 'gpu_mb': round(gpu / 1048576, 1), 'tex_entries': len(j.get('textures', [])), 'images': len(j.get('images', [])),
            'materials': len(j.get('materials', [])), 'sizes': imgs}, bad


def verify(glb, cls, manifest=None, validator=False):
    items = []
    add = lambda tid, ok, value=None, limit=None, note='': items.append({'id': tid, 'status': 'PASS' if ok else 'FAIL', 'value': value, 'limit': limit, 'note': note})
    info = lambda tid, value, note='': items.append({'id': tid, 'status': 'INFO', 'value': value, 'limit': None, 'note': note})
    if not os.path.isfile(glb):
        add('dosya.var', False, glb)
        return items, {}
    size = os.path.getsize(glb)
    bad, j, bn = integrity(glb)
    add('glb.butunluk', not bad, bad or 'tamam', None, 'başlık, parça uzunlukları, buffer ve accessor sınırları')
    if j is None:
        return items, {}
    m, ibad = metrics(j, bn)
    add('glb.gorseller_cozulur', not ibad, ibad or '%d görsel' % m['images'], None, 'her doku WebP olarak çözülüyor')
    sha = file_hash(glb)
    info('glb.sha256', sha[:16] + '…')
    if manifest:
        add('manifest.sha256', manifest.get('glb_sha256') == sha, sha[:12], (manifest.get('glb_sha256') or '')[:12], 'GLB baytları manifestle aynı')
        add('manifest.boyut', manifest.get('glb_bytes') == size, size, manifest.get('glb_bytes'), '')
        mt = manifest.get('tris'); mt = mt[0] if isinstance(mt, list) else mt
        add('manifest.ucgen', mt in (None, m['tris_noscr']), m['tris_noscr'], mt, 'LOD0 üçgen (canlı ekran dörtgenleri hariç)')
    B = load_json(os.path.join(QC_DIR, 'budgets.json'))['classes'].get(cls, {})
    R = load_json(os.path.join(QC_DIR, 'rules.json'))
    if B.get('glb_kb'):
        add('butce.glb_kb', size / 1024 <= B['glb_kb'], round(size / 1024, 1), B['glb_kb'])
    if B.get('tris'):
        add('butce.ucgen', m['tris'] <= B['tris'][0], m['tris'], B['tris'][0], 'LOD0')
    if B.get('calls'):
        add('butce.draw_call', m['primitives'] <= B['calls'] + (3 if cls == 'cockpit' else 0), m['primitives'], B['calls'] + (3 if cls == 'cockpit' else 0), 'primitive sayısı (kokpitte +3 canlı ekran)')
    gb = R.get('gpu_budget_mb', {}).get(cls)
    if gb:
        add('butce.gpu_mb', m['gpu_mb'] <= gb, m['gpu_mb'], gb, 'r128: her doku girişi ayrı yüklenir')
    add('doku.giris_le_gorsel', m['tex_entries'] <= m['images'], '%d/%d' % (m['tex_entries'], m['images']), None, 'aynı görsel için çoklu giriş yok')
    add('malzeme.sayi', m['materials'] <= R['max_materials'] + (1 if cls == 'cockpit' else 0), m['materials'], R['max_materials'] + (1 if cls == 'cockpit' else 0))
    ext = set(j.get('extensionsUsed', []))
    add('uzanti.izinli', ext <= set(R['allowed_extensions']) and not (ext & set(R['forbidden_extensions'])), sorted(ext), None, 'r128 GLTFLoader uyumu')
    if cls == 'cockpit':
        sys.path.insert(0, QC_DIR)
        import cockpit_compat as cc
        _, _, scr, lo, hi, _ = cc.screens(glb)
        for nm in cc.SCR:
            a = scr.get(nm)
            ok = bool(a) and a['prims'] == 1 and a['verts'] == 4 and a['uv_tl'] == [0.0, 0.0] and a['uv_br'] == [1.0, 1.0] and a['in_front'] and all(0 <= x <= cc.W and 0 <= y <= cc.H for x, y in a['px'])
            add('ekran.%s' % nm, ok, ('%dx%d px' % (a['w_px'], a['h_px'])) if a else 'yok', None, 'tek dörtgen, UV sol-üst (0,0), gözün önünde, 1600x656 çerçevede')
            if a:
                info('ekran.%s.oran' % nm, round(a['w_px'] / a['h_px'], 2), 'canlı tuval bu orana göre hazırlanır')
    if validator:
        out = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'verify_validator.json')
        try:
            p = subprocess.run(['node', os.path.join(QC_DIR, 'validate.js'), glb, out], capture_output=True, text=True, cwd=os.path.dirname(QC_DIR), timeout=120)
            r = json.loads([l for l in p.stdout.splitlines() if l.startswith('RESULT ')][-1][7:])
            add('gltf.validator_hata', r['errors'] == 0, r['errors'], 0, 'uyarı: %d' % r['warnings'])
        except Exception as e:
            info('gltf.validator', 'çalışmadı: %s' % str(e)[:60])
    return items, {**m, 'bytes': size, 'sha256': sha}


def main(glb, cls, manifest=None, validator=False):
    mf = load_json(manifest) if manifest else None
    items, m = verify(glb, cls, mf, validator)
    for i in items:
        if i['status'] != 'INFO' or True:
            print('%-4s %-28s %s' % (i['status'], i['id'], i['value'] if i['limit'] is None else '%s (sınır %s)' % (i['value'], i['limit'])))
    f = sum(1 for i in items if i['status'] == 'FAIL')
    print('RESULT', json.dumps({'fail': f, 'pass': sum(1 for i in items if i['status'] == 'PASS'), 'metrics': m}, ensure_ascii=False))
    return items, f


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    _, f = main(a[0], a[1], a[2] if len(a) > 2 else None, '--validator' in sys.argv)
    sys.exit(1 if f else 0)
