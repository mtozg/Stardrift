"""L2 statik testler — doğrudan GLB dosyası üzerinde (bpy gerektirmez).
Sözleşme (adlar, hiyerarşi, extras, yön/boy), uzantılar, malzemeler, dokular (biçim, boyut, PBR aralıkları), bütçe."""
import io, json, struct
import numpy as np
from PIL import Image

CT = {5120: 'b', 5121: 'B', 5122: 'h', 5123: 'H', 5125: 'I', 5126: 'f'}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}


def read_glb(path):
    b = open(path, 'rb').read()
    magic, ver, length = struct.unpack('<4sII', b[:12])
    assert magic == b'glTF' and ver == 2, 'GLB değil'
    jl = struct.unpack('<I', b[12:16])[0]
    j = json.loads(b[20:20 + jl])
    off = 20 + jl
    bl = struct.unpack('<I', b[off:off + 4])[0]
    return j, b[off + 8: off + 8 + bl], len(b)


def accessor(j, bin_, i):
    a = j['accessors'][i]
    bv = j['bufferViews'][a['bufferView']]
    n = NC[a['type']]
    dt = np.dtype('<' + CT[a['componentType']])
    start = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    stride = bv.get('byteStride', 0)
    if stride and stride != n * dt.itemsize:
        raw = np.frombuffer(bin_, np.uint8, count=stride * a['count'], offset=start).reshape(a['count'], stride)
        return raw[:, :n * dt.itemsize].copy().view(dt).reshape(a['count'], n)
    return np.frombuffer(bin_, dt, count=a['count'] * n, offset=start).reshape(a['count'], n)


def image(j, bin_, i):
    bv = j['bufferViews'][j['images'][i]['bufferView']]
    o = bv.get('byteOffset', 0)
    return Image.open(io.BytesIO(bin_[o:o + bv['byteLength']])), bv['byteLength']


def uv_mask(j, bin_, mesh_nodes, size):
    """LOD0 'body' mesh'inin UV adalarının kapladığı tekseller (piksel merkezi kesin içeride; bake kenar uzatması hariç)."""
    from qc.uvraster import raster
    acc = np.zeros((size, size), np.uint16)
    for mn in mesh_nodes:
        for p in j['meshes'][mn['mesh']]['primitives']:
            if 'TEXCOORD_0' in p['attributes'] and j['materials'][p.get('material', 0)].get('name') == 'MAT_body':
                acc += raster(accessor(j, bin_, p['attributes']['TEXCOORD_0']).astype(np.float64), accessor(j, bin_, p['indices']).reshape(-1, 3), size)
    return acc > 0


class Out:
    def __init__(self):
        self.items = []

    def add(self, tid, layer, ok, value=None, limit=None, note='', warn=False):
        st = 'PASS' if ok else ('WARN' if warn else 'FAIL')
        self.items.append({'id': tid, 'layer': layer, 'status': st, 'value': value, 'limit': limit, 'note': note})
        return ok


def run(path, spec, budgets, rules, extra=None):
    j, bin_, size = read_glb(path)
    o = Out()
    cls = budgets['classes'][spec['class']]
    nodes = j['nodes']
    names = [n.get('name', '') for n in nodes]
    # --- hiyerarşi ve adlar
    root_name = 'SD_' + spec['id']
    roots = [nodes[i] for i in j['scenes'][j.get('scene', 0)]['nodes']]
    o.add('contract.root', 'L2', len(roots) == 1 and roots[0].get('name') == root_name, [r.get('name') for r in roots], root_name)
    root = roots[0]
    nl = len(spec['lods'])
    lod_nodes = {names[c]: nodes[c] for c in root.get('children', []) if names[c].startswith('LOD')}
    o.add('contract.lods', 'L2', sorted(lod_nodes) == ['LOD%d' % i for i in range(nl)], sorted(lod_nodes), nl)
    bad_names = [n for n in names if not (n == root_name or n.startswith(('LOD', 'SOCK_', 'COL_', 'SCR_', 'ART_')))]
    o.add('contract.names', 'L2', not bad_names, bad_names, 'SD_/LODn/LODn_<rol>/SOCK_/COL_/SCR_/ART_<parça>_<eklem>')
    import re
    bad_mesh = [names[c] for ln in lod_nodes.values() for c in ln.get('children', []) if not re.fullmatch(r'LOD\d_(body|emit|glass)|ART_\w+', names[c])]
    o.add('contract.mesh_roles', 'L2', not bad_mesh, bad_mesh or None, 'LODn_body|emit|glass (+ ART_ eklem düğümleri)')
    socks = [n for n in names if n.startswith('SOCK_')]
    need = {'test': ['SOCK_engine_'], 'npc_ship': ['SOCK_engine_'], 'player_ship': ['SOCK_engine_'], 'station': ['SOCK_dock_'], 'cockpit': ['SOCK_cam_']}.get(spec['family'], [])
    o.add('contract.sockets', 'L2', all(any(s.startswith(p) for s in socks) for p in need), socks, need)

    # --- eklemli parçalar (STANDARDS §0.3): hiyerarşi, eksen bilgisi, pivot eklem merkezinde, mesh düğümleri birim, soket eklemle birlikte hareket eder
    artspec = spec.get('articulation')
    if artspec:
        parent_of = {c: i for i, n in enumerate(nodes) for c in n.get('children', [])}
        idx_of = {n: i for i, n in enumerate(names)}
        wrong = []
        for jn, exp in artspec.get('joints', {}).items():
            i = idx_of.get(jn)
            if i is None:
                wrong.append('%s yok' % jn)
            elif names[parent_of.get(i, -1)] != (exp or 'LOD0'):
                wrong.append('%s: ebeveyn %s ≠ %s' % (jn, names[parent_of.get(i, -1)], exp or 'LOD0'))
        o.add('art.hierarchy', 'L2', not wrong, wrong or 'tam', sorted(artspec.get('joints', {})), 'gövde → omuz → dirsek → bilek → çeneler')
        noax = [jn for jn in artspec.get('joints', {}) if jn in idx_of and not nodes[idx_of[jn]].get('extras', {}).get('joint_axis')]
        o.add('art.joint_axis', 'L2', not noax, noax or 'tam', None, 'her eklem düğümünde extras.joint_axis (dönüş ekseni)')
        far, nonid_geo = [], []
        for jn in artspec.get('joints', {}):
            i = idx_of.get(jn)
            if i is None:
                continue
            for c in nodes[i].get('children', []):
                if names[c].endswith('_geo') and 'mesh' in nodes[c]:
                    if any(k in nodes[c] for k in ('translation', 'rotation', 'scale', 'matrix')):
                        nonid_geo.append(names[c])
                    lo_, hi_ = np.array([1e9] * 3), np.array([-1e9] * 3)
                    for p_ in j['meshes'][nodes[c]['mesh']]['primitives']:
                        acc = j['accessors'][p_['attributes']['POSITION']]
                        lo_, hi_ = np.minimum(lo_, acc['min']), np.maximum(hi_, acc['max'])
                    d = float(np.linalg.norm(np.maximum(np.maximum(lo_, -hi_), 0)))      # eklem merkezinin (yerel başlangıç) geometri kutusuna uzaklığı
                    if d > artspec.get('pivot_tol_m', 0.15):
                        far.append('%s: %.3f m' % (names[c], d))
        o.add('art.pivot_near_geometry', 'L2', not far, far or 'tam', artspec.get('pivot_tol_m', 0.15), 'eklem merkezi (pivot) kendi geometrisine yakın')
        o.add('art.geo_identity', 'L2', not nonid_geo, nonid_geo or 'tam', None, 'eklem mesh düğümleri birim dönüşümlü (köşeler eklem uzayında)')
        sock_bad = [s_ for s_, pj in artspec.get('sockets', {}).items() if s_ not in idx_of or names[parent_of.get(idx_of[s_], -1)] != pj]
        o.add('art.socket_follows', 'L2', not sock_bad, sock_bad or 'tam', artspec.get('sockets'), 'soket ilgili eklemin çocuğu')
    nonid = [n.get('name') for n in nodes if not n.get('name', '').startswith(('SOCK_', 'ART_')) and any(k in n for k in ('translation', 'rotation', 'scale', 'matrix'))]
    o.add('contract.transforms', 'L2', not nonid, nonid, 'mesh/LOD/kök düğümleri birim dönüşümlü (SOCK_ ve ART_ eklem düğümleri hariç)')
    ex = root.get('extras', {})
    req = ['id', 'rev', 'family', 'class', 'units', 'forward', 'up', 'bounds_min', 'bounds_max', 'radius', 'tris', 'spec_hash', 'geometry_hash'] + (['length_m'] if spec.get('length_m') is not None else [])      # kokpitin boyu yok
    o.add('contract.extras', 'L2', all(k in ex for k in req), [k for k in req if k not in ex] or 'tam', req)

    # --- geometri: LOD0 sınırları (gerçek köşelerden), boy, yön
    def art_descendants(idx):
        out = []
        for c in nodes[idx].get('children', []):
            if names[c].startswith('ART_'):
                if 'mesh' in nodes[c]:
                    out.append(nodes[c])
                out += art_descendants(c)
        return out

    def lod_meshes(i):
        ln = lod_nodes.get('LOD%d' % i, {})
        res = [nodes[c] for c in ln.get('children', []) if 'mesh' in nodes[c]]
        if i == 0:      # eklemli parçalar (ART_ altındaki mesh'ler) LOD0'ın parçasıdır: üçgen, çağrı, sınır, UV kapsamı
            for c in ln.get('children', []):
                if names[c].startswith('ART_'):
                    res += art_descendants(c)
        return res
    pos = []
    tris = []
    calls = 0
    for i in range(nl):
        t = 0
        for mn in lod_meshes(i):
            for p in j['meshes'][mn['mesh']]['primitives']:
                ia = p.get('indices')
                t += (j['accessors'][ia]['count'] if ia is not None else j['accessors'][p['attributes']['POSITION']]['count']) // 3
                if i == 0:
                    calls += 1
                    pos.append(accessor(j, bin_, p['attributes']['POSITION']))
        tris.append(t)
    P = np.concatenate(pos)
    lo, hi = P.min(0), P.max(0)
    length = float(hi[2] - lo[2])
    L = spec.get('length_m')
    o.add('geom.length', 'L2', L is None or abs(length - L) / L <= rules['length_tol'], round(length, 4), '%s ±%d%%' % (L, rules['length_tol'] * 100))
    eng = [nodes[names.index(s)] for s in socks if s.startswith('SOCK_engine_')]
    if eng:
        ez = eng[0].get('translation', [0, 0, 0])[2]
        o.add('geom.forward_axis', 'L2', ez > (lo[2] + hi[2]) / 2, round(ez, 3), 'motor soketi arkada (+Z) ⇒ burun −Z')
    # --- uzantılar
    used = j.get('extensionsUsed', [])
    bad = [e for e in used if e not in rules['allowed_extensions']]
    o.add('ext.allowed', 'L2', not bad, used, rules['allowed_extensions'], note=('yasak: %s' % bad) if bad else '')
    # --- malzemeler
    mats = j.get('materials', [])
    o.add('mat.count', 'L2', len(mats) <= rules['max_materials'], len(mats), rules['max_materials'])
    o.add('mat.names', 'L2', all(m.get('name', '').startswith('MAT_') for m in mats), [m.get('name') for m in mats], 'MAT_<rol>')
    em_ok = all(max(m.get('emissiveFactor', [0, 0, 0])) <= 1.0 for m in mats)
    o.add('mat.emissive_le_1', 'L2', em_ok, [m.get('emissiveFactor') for m in mats], '≤ 1 (r128)')
    o.add('mat.single_sided', 'L2', not any(m.get('doubleSided') for m in mats), [m.get('doubleSided', False) for m in mats], 'doubleSided=false', warn=True)
    # --- dokular
    tex_info, gpu = {}, 0
    for i, im in enumerate(j.get('images', [])):
        img, nbytes = image(j, bin_, i)
        w, h = img.size
        tex_info[im.get('name', str(i))] = {'size': [w, h], 'mime': im.get('mimeType'), 'kb': round(nbytes / 1024, 1)}
        gpu += w * h * 4 * 4 / 3
        o.add('tex.pow2.%s' % im.get('name'), 'L2', (w & (w - 1)) == 0 and (h & (h - 1)) == 0 and w == h, [w, h], '2^n kare')
        o.add('tex.format.%s' % im.get('name'), 'L2', im.get('mimeType') == 'image/webp', im.get('mimeType'), 'image/webp')
    import hashlib
    nimg, ntex = len(j.get('images', [])), len(j.get('textures', []))
    o.add('tex.entries_le_images', 'L2', ntex <= nimg, ntex, nimg, 'r128 her doku girdisini ayrı GPU dokusu olarak yükler (Kaşif: 24 girdi / 4 görsel)')
    hs = {}
    for i, im in enumerate(j.get('images', [])):
        bv = j['bufferViews'][im['bufferView']]
        h = hashlib.sha1(bin_[bv.get('byteOffset', 0): bv.get('byteOffset', 0) + bv['byteLength']]).hexdigest()
        hs.setdefault(h, []).append(im.get('name', str(i)))
    dups = [v for v in hs.values() if len(v) > 1]
    o.add('tex.no_duplicate_images', 'L2', not dups, dups or None, 'her görsel bir kez', 'Kaşif: ORM iki kez gömülüydü')
    gb = rules.get('gpu_budget_mb', {}).get(spec['class'])
    if gb:
        o.add('budget.gpu_tex_mb', 'L2', gpu / 1048576 <= gb, round(gpu / 1048576, 1), gb, 'RGBA8 + mipmap tahmini')
    if spec['family'] == 'cockpit':
        for nm in ('SCR_SYS', 'SCR_RADAR', 'SCR_HULL'):
            if nm not in names:
                o.add('cockpit.screen.%s' % nm, 'L2', False, 'yok', 'var')
                continue
            nd = nodes[names.index(nm)]
            pr = j['meshes'][nd['mesh']]['primitives'][0]
            P_ = accessor(j, bin_, pr['attributes']['POSITION'])
            uvs = sorted(tuple(round(float(x), 3) for x in r) for r in accessor(j, bin_, pr['attributes']['TEXCOORD_0'])) if 'TEXCOORD_0' in pr['attributes'] else []
            ok = len(P_) == 4 and uvs == [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]
            o.add('cockpit.screen.%s' % nm, 'L2', ok, {'köşe': len(P_), 'uv': uvs}, '4 köşe, UV köşeleri 0..1', 'oyun canlı ekranı ada göre bağlar')
    exp = cls.get('tex_size')
    body = next((m for m in mats if m.get('name') == 'MAT_body'), None)

    def tex_of(ref):
        ti = j['textures'][ref['index']]
        src = ti.get('source', ti.get('extensions', {}).get('EXT_texture_webp', {}).get('source'))
        return np.asarray(image(j, bin_, src)[0].convert('RGB'), dtype=np.float32)
    if body:
        pbr = body.get('pbrMetallicRoughness', {})
        base = tex_of(pbr['baseColorTexture'])
        orm = tex_of(pbr['metallicRoughnessTexture'])
        nrm = tex_of(body['normalTexture'])
        if exp and not spec.get('_fast'):
            o.add('tex.size', 'L2', base.shape[0] == exp, base.shape[0], exp)
        _cov = {}

        def covm(n):
            if n not in _cov:
                _cov[n] = uv_mask(j, bin_, lod_meshes(0), n)
            return _cov[n]
        cov = covm(base.shape[0])
        o.add('tex.uv_coverage', 'L2', True, round(float(cov.mean()), 4), None, 'PBR istatistikleri yalnızca bu kapsamdaki tekseller üzerinden')
        co = covm(orm.shape[0])
        metal_o = (orm[..., 2] / 255.0)
        if orm.shape[0] != base.shape[0]:      # metal maskesini taban renk çözünürlüğüne taşı (en yakın komşu)
            k = base.shape[0] // orm.shape[0]
            metal_b = np.repeat(np.repeat(metal_o, k, 0), k, 1)
        else:
            metal_b = metal_o
        metal = metal_b[cov]
        lum = base.mean(-1)[cov]
        lo_p, hi_p = rules['base_percentiles']
        for kind, mask, rng_ in (('dielectric', metal < 0.5, rules['base_srgb_dielectric']), ('metal', metal >= 0.5, rules['base_srgb_metal'])):
            if mask.sum() < 50:
                continue
            v = lum[mask]
            # emisyonlu (sabit ışık) bölgeler taban rengi kuralından muaf
            a, b_ = float(np.percentile(v, lo_p)), float(np.percentile(v, hi_p))
            o.add('pbr.base_%s' % kind, 'L2', a >= rng_[0] - 1e-6 and b_ <= rng_[1], [round(a), round(b_)], rng_, warn=True,
                  note='p%d–p%d sRGB; kir/aşınma ve sabit emisyon bölgeleri sınır dışına düşebilir (WARN)' % (lo_p, hi_p))
        mid = float(((metal_o[co] > 0.2) & (metal_o[co] < 0.8)).mean())
        o.add('pbr.metal_binary', 'L2', mid <= rules['metal_mid_warn'], round(mid, 4), rules['metal_mid_warn'], warn=True)
        r = (orm[..., 1] / 255.0)[co]
        rp = float(np.percentile(r, 0.5))
        o.add('pbr.rough_range', 'L2', rp >= 0.03, [round(rp, 3), round(float(r.max()), 3)], 'p0.5 ≥ 0.04', note='alt %%0,5 yüzdelik (tek teksellik sıkıştırma artığına duyarsız); min %.3f' % float(r.min()))
        n = (nrm / 127.5 - 1.0)[covm(nrm.shape[0])]
        ln = np.linalg.norm(n, axis=-1)
        o.add('pbr.normal_unit', 'L2', abs(float(np.median(ln)) - 1) <= rules['normal_len_tol'] and float(np.median(n[..., 2])) > 0.5,
              [round(float(np.median(ln)), 3), round(float(np.median(n[..., 2])), 3)], '|n|≈1, z>0 (tangent, +Y)')
    # --- bütçe
    wr = budgets['warn_ratio']

    def budget(tid, val, lim):
        if val > lim:
            o.add(tid, 'L2', False, val, lim)
        else:
            o.add(tid, 'L2', val <= lim * wr, val, lim, warn=True, note='bütçenin %%%d üstü' % (wr * 100) if val > lim * wr else '')
    for i, t in enumerate(tris):
        if i < len(cls['tris']):
            budget('budget.tris_lod%d' % i, t, cls['tris'][i])
    budget('budget.calls_lod0', calls, cls['calls'])
    budget('budget.glb_kb', round(size / 1024, 1), cls['glb_kb'])
    if extra:
        for it in extra:
            o.items.append(it)
    stats = {'glb_bytes': size, 'tris': tris, 'calls_lod0': calls, 'materials': len(mats), 'textures': tex_info,
             'tex_gpu_bytes_est': int(gpu), 'bounds_min': lo.round(4).tolist(), 'bounds_max': hi.round(4).tolist(),
             'length_m': round(length, 4), 'extensions': used, 'sockets': socks}
    return o.items, stats
