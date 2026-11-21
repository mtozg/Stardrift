"""NPC/istasyon GLB teknik + sanat dili kontrolü (Blender'sız).
Kullanım: python qc/npc_check.py <spec.json> <çıktı_klasörü>   (npc_build.py çıktısı: sd_<id>.glb, meta.json, m_top.png, m_side.png, m_persp.png)
Kontroller: LOD0/LOD1 üçgen, malzeme/draw call, doku boyutları ve GPU tahmini, dosya boyutu, uzantılar, ANCH_* düğümleri, eksen/ölçek (burun +Z, L=1, merkez),
siluet IoU (meta.json), baskın palet ΔE (kaynak ↔ model render), yan yana görsel (kaynak | model)."""
import os, sys, json, io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from PIL import Image
from qc import glb_checks

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
spec = json.load(open(sys.argv[1], encoding='utf-8'))
out = sys.argv[2]
SUF = next((a[9:] for a in sys.argv if a.startswith('--suffix=')), '')
for a_ in sys.argv:
    if a_.startswith('--max_gpu='):
        spec['max_gpu_mb'] = float(a_[10:])
    if a_.startswith('--max_bytes='):
        spec['max_bytes'] = int(a_[12:])
glb = os.path.join(out, 'sd_%s%s.glb' % (spec['id'], SUF))
meta = json.load(open(os.path.join(out, 'meta.json'), encoding='utf-8'))
j, b, _ = glb_checks.read_glb(glb)
B = spec['budget']
res = {'id': spec['id'], 'bytes': os.path.getsize(glb)}


def acc_count(i):
    return j['accessors'][i]['count']


def node_by(n):
    return next((k for k, x in enumerate(j['nodes']) if x.get('name') == n), None)


def mesh_of(node_idx):
    st, tris, calls = [node_idx], 0, 0
    bbmin, bbmax = None, None
    while st:
        x = j['nodes'][st.pop()]
        st += x.get('children', [])
        if 'mesh' in x:
            for p in j['meshes'][x['mesh']]['primitives']:
                tris += acc_count(p['indices']) // 3
                calls += 1
                a = j['accessors'][p['attributes']['POSITION']]
                lo, hi = np.array(a['min']), np.array(a['max'])
                bbmin = lo if bbmin is None else np.minimum(bbmin, lo)
                bbmax = hi if bbmax is None else np.maximum(bbmax, hi)
    return tris, calls, bbmin, bbmax


n0, n1 = node_by('LOD0'), node_by('LOD1')
t0, c0, lo, hi = mesh_of(n0)
t1, c1, _, _ = mesh_of(n1)
res.update({'tris_lod0': t0, 'tris_lod1': t1, 'draw_calls_lod0': c0, 'materials': len(j.get('materials', [])), 'extensions': j.get('extensionsUsed', [])})
# doku boyutları / GPU
gpu = 0.0
tex = []
for im in j.get('images', []):
    bv = j['bufferViews'][im['bufferView']]
    data = b[bv.get('byteOffset', 0):bv.get('byteOffset', 0) + bv['byteLength']]
    w, h = Image.open(io.BytesIO(data)).size
    tex.append([im.get('name'), w, h])
    gpu += w * h * 4 * 1.333 / 1e6
res['textures'] = tex
res['gpu_mb'] = round(gpu, 2)
ext = (hi - lo)
cen = (hi + lo) / 2
res['bbox'] = [round(float(x), 3) for x in ext]
res['uzunluk_z'] = round(float(ext[2]), 3)
res['merkez'] = [round(float(x), 3) for x in cen]
anch = [x['name'] for x in j['nodes'] if x.get('name', '').startswith('ANCH_')]
res['anchors'] = anch
res['iou'] = meta['iou']
# ---- palet ΔE (Lab, 5 küme): kaynak üst çizim ↔ modelin nötr ışık üst render'ı
def lab(rgb):
    c = rgb / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])], -1)


def clusters(path, k=5, seed=1):
    im = Image.open(path).convert('RGBA')
    im.thumbnail((200, 200))
    a = np.array(im)
    px = a[a[..., 3] > 200][:, :3].astype(np.float32)
    L = lab(px)
    rng = np.random.default_rng(seed)
    cen = L[rng.choice(len(L), k, replace=False)]
    for _ in range(25):
        d = ((L[:, None, :] - cen[None]) ** 2).sum(-1)
        lbl = d.argmin(1)
        for i in range(k):
            if (lbl == i).any():
                cen[i] = L[lbl == i].mean(0)
    w = np.array([(lbl == i).mean() for i in range(k)])
    return cen, w


def de(c1, w1, c2, w2):
    tot = 0.0
    for c, w in zip(c1, w1):
        tot += w * np.sqrt(((c2 - c) ** 2).sum(-1)).min()
    return tot


src_top = os.path.join(REPO, spec['top'])
mod_top = os.path.join(out, 'm_top.png')
cs, ws = clusters(src_top)
cm, wm = clusters(mod_top)
res['palet_dE'] = round(float(de(cs, ws, cm, wm)), 2)
res['palet_dE_ust3'] = round(float(sum(w * np.sqrt(((cm - c) ** 2).sum(-1)).min() for c, w in sorted(zip(cs, ws), key=lambda t: -t[1])[:3]) / sum(sorted(ws)[-3:])), 2)
# ---- kabul kapıları
g = []
def gate(name, ok, val, lim):
    g.append({'kapi': name, 'durum': 'GEÇTİ' if ok else 'KALDI', 'deger': val, 'sinir': lim})
gate('LOD0 üçgen', t0 <= B['tris0'], t0, '≤ %d' % B['tris0'])
gate('LOD1 üçgen', t1 <= int(B['tris0'] * 0.30) + 1, t1, '≤ %d (%%30)' % int(B['tris0'] * 0.30))
gate('draw call (LOD0)', c0 <= 2, c0, '≤ 2')
gate('malzeme', res['materials'] == 1, res['materials'], '1')
gate('dosya boyutu', res['bytes'] <= spec.get('max_bytes', 500 * 1024), res['bytes'], '≤ %d KB' % (spec.get('max_bytes', 512000) // 1024))
gate('GPU doku', res['gpu_mb'] <= spec.get('max_gpu_mb', 3.0), res['gpu_mb'], '≤ %.1f MB' % spec.get('max_gpu_mb', 3.0))
gate('uzunluk Z = 1,0', abs(res['uzunluk_z'] - 1.0) < 0.03, res['uzunluk_z'], '1,0 ± 0,03')
gate('siluet IoU üst', meta['iou']['top'] >= 0.88, meta['iou']['top'], '≥ 0,88')
gate('siluet IoU yan', meta['iou']['side'] >= 0.85, meta['iou']['side'], '≥ 0,85')
gate('palet ΔE (5 küme)', res['palet_dE'] <= 8.0, res['palet_dE'], '≤ 8')
gate('palet ΔE (üst 3)', res['palet_dE_ust3'] <= 6.0, res['palet_dE_ust3'], '≤ 6')
gate('uzantılar', set(res['extensions']) <= {'KHR_materials_emissive_strength', 'EXT_texture_webp', 'KHR_mesh_quantization', 'KHR_texture_transform'}, res['extensions'], 'izinli')
gate('çapalar', any(a.startswith('ANCH_ENG') for a in anch) and any(a.startswith('ANCH_MUZ') for a in anch) and any(a.startswith('ANCH_NAV') for a in anch), anch, 'ENG+NAV+MUZ')
res['kapilar'] = g
# ---- yan yana görsel: kaynak üst/yan | model üst/yan
def fit(im, w):
    im = im.convert('RGBA')
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)


W = 760
rows = []
for sn, mn in ((spec['top'], 'm_top.png'), (spec['side'], 'm_side.png')):
    a = fit(Image.open(os.path.join(REPO, sn)), W)
    m0 = Image.open(os.path.join(out, mn)).convert('RGBA')
    k = 1.0 / 1.3      # model render ortho ölçeği 1,3 (uzunluk 1,0) → kaynak çizimle aynı ölçeğe kırp
    cw, ch = int(m0.width * k), int(m0.height * k)
    m0 = m0.crop(((m0.width - cw) // 2, (m0.height - ch) // 2, (m0.width + cw) // 2, (m0.height + ch) // 2))
    m = fit(m0, W)
    r = Image.new('RGBA', (2 * W + 10, max(a.height, m.height)), (22, 30, 46, 255))
    r.alpha_composite(a, (0, 0))
    r.alpha_composite(m, (W + 10, 0))
    rows.append(r)
H = sum(r.height for r in rows) + 10
sheet = Image.new('RGBA', (2 * W + 10, H), (22, 30, 46, 255))
y = 0
for r in rows:
    sheet.alpha_composite(r, (0, y)); y += r.height + 10
sheet.convert('RGB').save(os.path.join(out, 'yanyana%s.webp' % SUF), quality=88)
json.dump(res, open(os.path.join(out, 'check%s.json' % SUF), 'w'), indent=1, ensure_ascii=False)
print('RESULT', json.dumps({k: res[k] for k in ('id', 'bytes', 'tris_lod0', 'tris_lod1', 'draw_calls_lod0', 'materials', 'gpu_mb', 'uzunluk_z', 'iou', 'palet_dE', 'palet_dE_ust3')}, ensure_ascii=False))
for x in g:
    print('%-6s %-22s %s (sınır %s)' % (x['durum'], x['kapi'], x['deger'], x['sinir']))
