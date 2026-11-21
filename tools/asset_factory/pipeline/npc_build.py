"""NPC gemisi / istasyon üretimi: MEVCUT KAYNAK SANATTAN gerçek 3B model + PBR (sanat dili korunur).
Yöntem: kaynak ÜST ve YAN çizim maskelerinden görsel gövde (voxel kesişimi, kalınlık biçimlendirmeli) → Remesh → yumuşatma → Decimate
→ UV → kaynak çizimlerin kutu izdüşümüyle albedo pişirme (palet birebir) → AO + türetilmiş ORM/normal/emissive → GLB (LOD0/LOD1, ANCH_*).
Eksen sözleşmesi (Lead): glTF'de burun +Z, yukarı +Y, uzunluk 1,0, orijin kütle merkezi. Blender'da burun −Y.
Kullanım: python pipeline/npc_build.py <spec.json> <çıktı_klasörü> [--probe]   (probe: düşük çözünürlük, doku yok, yalnız gövde + metrik)"""
import os, sys, json, math, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import bpy, bmesh
from mathutils import Vector
from PIL import Image
from core import geo, export, bake as B, glbpack, render as R

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
t_start = time.time()
spec_path, out = sys.argv[1], sys.argv[2]
PROBE = '--probe' in sys.argv
spec = json.load(open(spec_path, encoding='utf-8'))
SUF = ''
for _a in sys.argv:
    if _a.startswith('--set='):      # --set=anahtar=değer (JSON değer): spec üzerine yaz, ör. --set=budget.tex=1024
        _k, _v = _a[6:].split('=', 1)
        _d = spec
        _ks = _k.split('.')
        for _x in _ks[:-1]:
            _d = _d[_x]
        _d[_ks[-1]] = json.loads(_v)
    if _a.startswith('--suffix='):
        SUF = _a[9:]
os.makedirs(out, exist_ok=True)
T = {}


def tick(k, t0):
    T[k] = round(time.time() - t0, 2)
    return time.time()


t0 = time.time()
top_im = Image.open(os.path.join(REPO, spec['top'])).convert('RGBA')
side_im = Image.open(os.path.join(REPO, spec['side'])).convert('RGBA')
WT, HT = top_im.size
WS, HS = side_im.size
ht, hs = HT / WT, HS / WS                      # üst/yan görüntünün uzunluğa oranı (uzunluk = 1)
NX = spec.get('voxels', 96 if PROBE else 168)
NY, NZ = int(round(NX * ht)), int(round(NX * hs))
mt = (np.array(top_im.resize((NX, NY), Image.LANCZOS))[:, :, 3] > 100)       # [satır(y, yukarıdan), sütun(x)]
ms = (np.array(side_im.resize((NX, NZ), Image.LANCZOS))[:, :, 3] > 100)
if spec.get('side_crop'):                       # yansıma/gölge kopyası olan yan çizimlerde alt bölümü dışla (oran)
    ms[int(NZ * spec['side_crop']):, :] = False

# ---- görsel gövde: occ[x, y, z]
xs = (np.arange(NX) + 0.5) / NX - 0.5
ys = -(((np.arange(NY) + 0.5) / NY) * ht - ht / 2)       # üst görüntü satırı 0 = +y
zs = -(((np.arange(NZ) + 0.5) / NZ) * hs - hs / 2)     # yan görüntü satırı 0 = +z
top_xy = mt.T                                           # [x, y]
side_xz = ms.T                                          # [x, z]
occ = np.zeros((NX, NY, NZ), bool)
fw, fl = spec['shape'].get('fuse_hw', 0.1), spec['shape'].get('floor', 0.10)
for i in range(NX):
    zi = np.where(side_xz[i])[0]
    yi = np.where(top_xy[i])[0]
    if len(zi) == 0 or len(yi) == 0:
        continue
    zc = (zs[zi].min() + zs[zi].max()) / 2
    hh = max((zs[zi].max() - zs[zi].min()) / 2, 1e-3)
    for j in yi:
        k = fl + (1 - fl) * max(0.0, 1.0 - abs(ys[j]) / fw)     # gövde ekseninde tam kalınlık, kanatlarda incelen
        lo, hi = zc - hh * k, zc + hh * k
        zok = side_xz[i] & (zs >= lo) & (zs <= hi)
        occ[i, j] = zok
# boşlukları doldurmadan: yalnız en büyük bağlı parça (basit: tüm occ)
T0 = tick('voxel', t0)

# ---- voxel yüzeyi → bmesh
cell = 1.0 / NX
bm = bmesh.new()
vmap = {}


def V(p):
    k = p
    if k not in vmap:
        vmap[k] = bm.verts.new(((p[0] - NX / 2) * cell, (p[1] - NY / 2) * (ht / NY), (p[2] - NZ / 2) * (hs / NZ)))
    return vmap[k]


dy, dz = ht / NY, hs / NZ
occp = np.pad(occ, 1)
for ax in range(3):
    for sgn in (-1, 1):
        sh = np.roll(occp, -sgn, axis=ax)
        face = occp & ~sh
        idx = np.argwhere(face[1:-1, 1:-1, 1:-1])
        for (i, j, k) in idx:
            c = [i, j, k]
            if sgn > 0:
                c[ax] += 1
            a1, a2 = [a for a in range(3) if a != ax]
            q = []
            for d1, d2 in ((0, 0), (1, 0), (1, 1), (0, 1)):
                p = list(c)
                p[a1] += d1
                p[a2] += d2
                q.append(V(tuple(p)))
            try:
                bm.faces.new(q if sgn > 0 else q[::-1])
            except ValueError:
                pass
# eksen düzeni: x=uzunluk(burun +x), y=yanal, z=yukarı; üst görüntüde satır arttıkça y azalır → y indeksi tersine
for v in bm.verts:
    v.co.y = -v.co.y
    v.co.z = -v.co.z
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
geo.reset_scene()
me = bpy.data.meshes.new('hull')
bm.to_mesh(me)
bm.free()
ob = bpy.data.objects.new('hull', me)
bpy.context.scene.collection.objects.link(ob)
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
T0 = tick('mesh', T0)

# ---- PARAMETRİK yol (spec.param='ankora'): halka + göbek + kollar + güneş panelleri; ölçüler kaynak maskelerden ölçüldü
def build_ankora():
    from mathutils import Matrix
    P = spec['dims']
    bmp = bmesh.new()

    def sweep_ring(R, rw, h, nseg, prof):
        rings = []
        for i in range(nseg):
            a = 2 * math.pi * i / nseg
            ca, sa = math.cos(a), math.sin(a)
            rings.append([bmp.verts.new(((R + po * rw) * ca, (R + po * rw) * sa, pz * h)) for po, pz in prof])
        n = len(prof)
        for i in range(nseg):
            for k in range(n):
                try:
                    bmp.faces.new((rings[i][k], rings[(i + 1) % nseg][k], rings[(i + 1) % nseg][(k + 1) % n], rings[i][(k + 1) % n]))
                except ValueError:
                    pass

    def lathe(profile, nseg):
        rows = []
        for i in range(nseg):
            a = 2 * math.pi * i / nseg
            rows.append([bmp.verts.new((r * math.cos(a), r * math.sin(a), z)) for r, z in profile])
        for i in range(nseg):
            for k in range(len(profile) - 1):
                try:
                    bmp.faces.new((rows[i][k], rows[(i + 1) % nseg][k], rows[(i + 1) % nseg][k + 1], rows[i][k + 1]))
                except ValueError:
                    pass

    def box(c, sz, rot=0.0):
        r_ = bmesh.ops.create_cube(bmp, size=1.0)
        bmesh.ops.transform(bmp, matrix=Matrix.Translation(c) @ Matrix.Rotation(rot, 4, 'Z') @ Matrix.Diagonal((*sz, 1.0)), verts=r_['verts'])

    R, rw, rh = P['ring_r'], P['ring_w'], P['ring_h']
    prof = [(-0.5, -0.30), (-0.42, -0.5), (0.42, -0.5), (0.5, -0.30), (0.5, 0.30), (0.42, 0.5), (-0.42, 0.5), (-0.5, 0.30)]
    sweep_ring(R, rw, rh, P.get('ring_seg', 160), prof)
    sweep_ring(R - rw * 0.62, rw * 0.22, rh * 0.62, 120, prof)
    hr, hh = P['hub_r'], P['hub_h']
    lathe([(0.0, -hh), (hr * 0.5, -hh), (hr * 0.8, -hh * 0.6), (hr, -hh * 0.25), (hr, hh * 0.25), (hr * 0.8, hh * 0.6), (hr * 0.5, hh), (0.0, hh)], 64)
    lathe([(0.0, hh), (hr * 0.42, hh), (hr * 0.34, hh * 1.5), (hr * 0.2, hh * 1.9), (0.0, hh * 2.0)], 40)
    lathe([(0.0, -hh), (hr * 0.42, -hh), (hr * 0.34, -hh * 1.5), (hr * 0.2, -hh * 1.9), (0.0, -hh * 2.0)], 40)
    box((0, 0, hh * 2.0 + P['ant_h'] / 2), (0.006, 0.006, P['ant_h']))
    box((0, 0, -hh * 2.0 - P['ant_h'] * 0.4), (0.006, 0.006, P['ant_h'] * 0.8))
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        L = (R - rw * 0.4) - hr * 0.8
        c = (math.cos(a) * (hr * 0.8 + L / 2), math.sin(a) * (hr * 0.8 + L / 2), 0)
        box(c, (L, P['spoke_w'], P['spoke_h']), a)
        box(c, (L * 0.96, P['spoke_w'] * 1.5, P['spoke_h'] * 0.35), a)
    for k in range(12):
        a = k * math.pi / 6
        box((math.cos(a) * hr * 1.7, math.sin(a) * hr * 1.7, 0), (hr * 1.4, 0.006, 0.006), a)
    for sx, sy in ((1, 1), (-1, -1)):
        a = math.atan2(sy, sx)
        box((P['panel_c'] * sx, P['panel_c'] * sy, 0), (P['panel_l'], P['panel_w'], 0.006), a + math.pi / 2)
        box((math.cos(a) * (R + rw * 0.5 + 0.05), math.sin(a) * (R + rw * 0.5 + 0.05), 0), (0.10, 0.012, 0.012), a)
    return bmp


if spec.get('param') == 'ankora':
    bm_p = build_ankora()
    bmesh.ops.recalc_face_normals(bm_p, faces=bm_p.faces)
    bmesh.ops.triangulate(bm_p, faces=bm_p.faces)
    me2 = bpy.data.meshes.new('hull2')
    bm_p.to_mesh(me2)
    bm_p.free()
    bpy.data.objects.remove(ob, do_unlink=True)
    ob = bpy.data.objects.new('hull', me2)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    geo.set_smooth_by_angle(ob, 45)
else:
    # ---- Remesh (voxel) → yumuşat → decimate
    rm = ob.modifiers.new('rm', 'REMESH')
    rm.mode = 'VOXEL'
    rm.voxel_size = spec.get('remesh', 1.6) * cell
    rm.use_smooth_shade = True
    geo.apply_modifier(ob, rm)
    sm = ob.modifiers.new('sm', 'SMOOTH')
    sm.factor = 0.55
    sm.iterations = spec.get('smooth_iter', 10)
    geo.apply_modifier(ob, sm)
    tgt = spec['budget']['tris0']
    cur = len(ob.data.polygons) * 1  # üçgen sayısı ≈ çokgen (remesh üçgen/dörtgen karışık)
    bm = bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.triangulate(bm, faces=bm.faces); bm.to_mesh(ob.data); bm.free()
    ntri = len(ob.data.polygons)
    if ntri > tgt:
        dc = ob.modifiers.new('dec', 'DECIMATE')
        dc.decimate_type = 'COLLAPSE'
        dc.ratio = tgt / ntri
        geo.apply_modifier(ob, dc)
    bm = bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(ob.data); bm.free()      # dışa bakan normaller
    geo.set_smooth_by_angle(ob, 50)
# merkez: kütle merkezi ≈ sınırlayıcı kutu merkezi (basit)
cs = [ob.matrix_world @ v.co for v in ob.data.vertices]
cen = sum(cs, Vector()) / len(cs)
if spec.get('param'):      # parametrik: sınırlayıcı kutu merkezi (köşe ortalaması ince bölgelere kayıyor)
    cen = Vector(((min(c.x for c in cs) + max(c.x for c in cs)) / 2, (min(c.y for c in cs) + max(c.y for c in cs)) / 2, (min(c.z for c in cs) + max(c.z for c in cs)) / 2))
for v in ob.data.vertices:
    v.co -= cen
CEN = cen.copy()
if spec.get('param'):      # uzunluk 1,0'a normalize (IoU doğru ölçülsün)
    _xs = [v.co.x for v in ob.data.vertices]
    _k = 1.0 / (max(_xs) - min(_xs))
    for v in ob.data.vertices:
        v.co *= _k
    CEN = CEN * _k
T0 = tick('remesh', T0)
tris0 = len(ob.data.polygons)

# ---- metrik: siluet IoU (üst/yan), ağ izdüşümü rasterlaştırma
def raster(ob, ax_u, ax_v, flip_v, W, H, rng_u, rng_v):
    im = Image.new('L', (W, H), 0)
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    co = [v.co + CEN for v in ob.data.vertices]
    for p in ob.data.polygons:
        pts = []
        for i in p.vertices:
            c = co[i]
            u = (c[ax_u] - rng_u[0]) / (rng_u[1] - rng_u[0]) * W
            v = (c[ax_v] - rng_v[0]) / (rng_v[1] - rng_v[0]) * H
            pts.append((u, (H - v) if flip_v else v))
        d.polygon(pts, fill=255)
    return np.array(im) > 128


def iou(a, b):
    return float((a & b).sum() / max((a | b).sum(), 1))


# kaynak maskeleri ortak ızgarada (merkez, uzunluk 1; yan/üst yatay merkez = kütle merkezi kayması dikkate alınmaz → bbox hizalı karşılaştırma)
def aligned_iou():
    co = np.array([v.co[:] for v in ob.data.vertices])
    xr = (co[:, 0].min(), co[:, 0].max())
    outd = {}
    res = 512
    # üst: (x, y)
    W = res; H = int(res * ht)
    src = np.array(top_im.resize((W, H), Image.LANCZOS))[:, :, 3] > 100
    yr = (-ht / 2 + 0, ht / 2)
    # model üst izdüşümü: yanal y → görüntü satırı (y=+ üstte)
    m = raster(ob, 0, 1, True, W, H, (-0.5, 0.5), (-ht / 2, ht / 2))
    # ağ merkezi kayması: sınırlayıcı kutu ile hizala
    def bbox_align(a, b):
        ya, xa = np.where(a); yb, xb = np.where(b)
        dx = int(round((xa.min() + xa.max()) / 2 - (xb.min() + xb.max()) / 2))
        dy = int(round((ya.min() + ya.max()) / 2 - (yb.min() + yb.max()) / 2))
        return b      # hizalama yok: model kaynakla aynı normalize uzayda (merkezleme kaymasını CEN telafi eder)
    if os.environ.get('NPC_DEBUG'):
        Image.fromarray(np.stack([src * 255, bbox_align(src, m) * 255, np.zeros_like(src)], -1).astype(np.uint8)).save(os.path.join(out, 'dbg_top.png'))
    outd['top'] = iou(src, bbox_align(src, m))
    H2 = int(res * hs)
    srcs = np.array(side_im.resize((W, H2), Image.LANCZOS))[:, :, 3] > 100
    if spec.get('side_crop'):
        srcs[int(H2 * spec['side_crop']):, :] = False
    m2 = raster(ob, 0, 2, True, W, H2, (-0.5, 0.5), (-hs / 2, hs / 2))
    if os.environ.get('NPC_DEBUG'):
        Image.fromarray(np.stack([srcs * 255, bbox_align(srcs, m2) * 255, np.zeros_like(srcs)], -1).astype(np.uint8)).save(os.path.join(out, 'dbg_side.png'))
    outd['side'] = iou(srcs, bbox_align(srcs, m2))
    return outd


iou_r = aligned_iou()
T0 = tick('iou', T0)
info = {'id': spec['id'], 'tris0': tris0, 'iou': {k: round(v, 3) for k, v in iou_r.items()}, 'probe': PROBE}
if PROBE:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'probe.blend'))
    info['seconds'] = round(time.time() - t_start, 1)
    info['timings'] = T
    print('RESULT', json.dumps(info, ensure_ascii=False))
    sys.exit(0)

# ---- UV + albedo: kaynak çizimler DOĞRUDAN atlasa yerleştirilir (üst çizim + yan çizim), UV düzlemsel izdüşüm → pişirme yok, palet birebir
TEX = spec['budget'].get('tex', 512)
WTX = int((TEX - 6 - 2) / (ht + hs))      # üst+yan çizim dikeyde yan yana sığacak en büyük genişlik
HTX = int(round(WTX * ht))
HSX = int(round(WTX * hs))
GAP = 6
assert HTX + GAP + HSX <= TEX, 'atlas sığmıyor'
atlas = np.zeros((TEX, TEX, 4), np.uint8)
tt_ = np.array(top_im.resize((WTX, HTX), Image.LANCZOS))
ss_ = np.array(side_im.resize((WTX, HSX), Image.LANCZOS))
atlas[0:HTX, 0:WTX] = tt_
atlas[HTX + GAP:HTX + GAP + HSX, 0:WTX] = ss_
# kenar dolgusu: saydam pikselleri en yakın dolu renkle doldur (bilinear sızıntısı koyu saçak yapmasın)
filled = atlas[..., 3] > 40
rgb = atlas[..., :3].astype(np.float32)
for _ in range(24):
    k = ~filled
    if not k.any():
        break
    acc = np.zeros_like(rgb); cnt = np.zeros(filled.shape, np.float32)
    for dy_, dx_ in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        f2 = np.roll(filled, (dy_, dx_), (0, 1)); r2 = np.roll(rgb, (dy_, dx_), (0, 1))
        acc += r2 * f2[..., None]; cnt += f2
    nz = k & (cnt > 0)
    rgb[nz] = acc[nz] / cnt[nz][..., None]
    filled = filled | nz
tgt_img = bpy.data.images.new('sd_base', TEX, TEX, alpha=False)
tgt_img.colorspace_settings.name = 'sRGB'
bl = np.concatenate([rgb / 255.0, np.ones((TEX, TEX, 1), np.float32)], -1)[::-1]      # Blender: satır 0 = alt
tgt_img.pixels = bl.astype(np.float32).ravel().tolist()
ao_img = None
# UV (düzlemsel): yukarı bakan yüzler üst çizim bölgesine, diğerleri yan çizim bölgesine
bmu = bmesh.new(); bmu.from_mesh(ob.data); bmu.normal_update()
uvl = bmu.loops.layers.uv.verify()
for f in bmu.faces:
    top_mode = abs(f.normal.z) >= spec.get('top_thr', 0.5)
    for lp in f.loops:
        c = lp.vert.co
        u = (c.x + CEN.x + 0.5) * WTX / TEX
        if top_mode:
            r = (0.5 - (c.y + CEN.y) / ht) * HTX
        else:
            r = HTX + GAP + (0.5 - (c.z + CEN.z) / hs) * HSX
        lp[uvl].uv = (u, 1.0 - r / TEX)
bmu.to_mesh(ob.data); bmu.free()
T0 = tick('uv_atlas', T0)
sc = bpy.context.scene

# ---- türetilmiş haritalar (numpy)
base = B.pixels(tgt_img)
aoa = np.ones_like(base)
if os.environ.get('NPC_DEBUG'):
    Image.fromarray((np.clip(base[..., :3], 0, 1) * 255).astype(np.uint8)).save(os.path.join(out, 'dbg_base.png'))
rgb = np.clip(base[..., :3], 0, 1)
lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
mx, mn = rgb.max(-1), rgb.min(-1)
sat = np.where(mx > 1e-4, (mx - mn) / np.maximum(mx, 1e-4), 0)
# AO'yu albedoya kısmen çarp (Kaşif yaklaşımı)
ao_strength = spec.get('ao_into_base', 0.35)
base_o = base.copy()
base_o[..., :3] = rgb * ((1 - ao_strength) + ao_strength * np.clip(aoa[..., :1], 0, 1))
# yalın PBR türetimi: metalik = düşük doygunluk + parlak/orta (boyasız metal), pürüz = 0.78 - 0.30*lum + 0.15*sat
metal = np.clip((0.55 - sat) * 1.4, 0, 1) * np.clip((lum - 0.12) * 4, 0, 1) * spec.get('metal_gain', 0.55)
rough = np.clip(0.80 - 0.34 * lum + 0.12 * sat + 0.06 * (1 - metal), 0.30, 0.95)
orm = np.ones_like(base)
orm[..., 0] = np.clip(aoa[..., 0], 0, 1)
orm[..., 1] = rough
orm[..., 2] = metal
# normal: albedo parlaklığından yükseklik → Sobel (UV'de), güç spec
hgt = lum - np.mean(lum)
gx = np.gradient(hgt, axis=1)
gy = np.gradient(hgt, axis=0)
st = spec.get('normal_strength', 3.0)
nx_, ny_ = -gx * st, gy * st
nz_ = np.ones_like(nx_)
ln = np.sqrt(nx_ ** 2 + ny_ ** 2 + nz_ ** 2)
nrm = np.stack([nx_ / ln * 0.5 + 0.5, ny_ / ln * 0.5 + 0.5, nz_ / ln * 0.5 + 0.5, np.ones_like(nx_)], -1)
# emissive: doygun + parlak pikseller (kırmızı/turuncu ışıklar), küçük doku
emis = np.zeros_like(base)
em = ((mx > spec.get('emit_v', 0.80)) & (sat > spec.get('emit_s', 0.55))).astype(np.float32)
em = np.array(Image.fromarray((em * 255).astype(np.uint8)).filter(__import__('PIL.ImageFilter', fromlist=['x']).MaxFilter(3))) / 255.0
emis[..., :3] = rgb * em[..., None]
emis[..., 3] = 1
has_emit = em.sum() > 6


def mkimg(name, arr, non_color):
    im = bpy.data.images.new(name, arr.shape[1], arr.shape[0], alpha=False)
    if non_color:
        im.colorspace_settings.name = 'Non-Color'
    im.pixels = arr.astype(np.float32).ravel().tolist()
    return im


img_base = mkimg('sd_npc_base', np.concatenate([np.clip(base_o[..., :3], 0, 1), np.ones_like(base[..., :1])], -1), False)
OS = spec['budget'].get('orm_tex', 256)
orm_s = np.array(Image.fromarray((np.clip(orm[..., :3], 0, 1) * 255).astype(np.uint8)).resize((OS, OS), Image.LANCZOS)).astype(np.float32) / 255.0      # ORM düşük frekanslı
img_orm = mkimg('sd_npc_orm', np.concatenate([orm_s, np.ones((OS, OS, 1), np.float32)], -1), True)
img_nrm = mkimg('sd_npc_normal', nrm, True)
img_emit = None
if has_emit:
    ES = spec['budget'].get('emit_tex', 256)
    e256 = Image.fromarray((emis[..., :3] * 255).astype(np.uint8)).resize((ES, ES), Image.LANCZOS)
    img_emit = mkimg('sd_npc_emit', np.concatenate([np.array(e256).astype(np.float32) / 255.0, np.ones((ES, ES, 1), np.float32)], -1), False)
mat = B.gltf_body_material('MAT_' + spec['id'], img_base, img_orm, img_nrm if spec.get('normal_map') else None, img_emit)
B.assign_single(ob, mat)
ob.name = 'LOD0_body'
T0 = tick('maps', T0)

# ---- LOD1
from core import lod as LOD
ob1, tris1 = LOD.make_lod(ob, spec['budget'].get('lod1_ratio', 0.3), 'LOD1_body')
T0 = tick('lod', T0)

# ---- çapalar (maskelerden türetilir): motor = arka %6'daki yanal kümeler, nav = kanat uçları, namlu = burun
co = np.array([v.co[:] for v in ob.data.vertices])
xmin, xmax = co[:, 0].min(), co[:, 0].max()
rear = co[co[:, 0] < xmin + 0.06 * (xmax - xmin)]
anch = []
if len(rear):
    ysr = np.sort(rear[:, 1])
    groups, g0 = [], ysr[0]
    for a, b in zip(ysr[:-1], ysr[1:]):
        if b - a > 0.035:
            groups.append((g0, a)); g0 = b
    groups.append((g0, ysr[-1]))
    for (a, b) in groups[:3]:
        zc = float(np.median(rear[(rear[:, 1] >= a) & (rear[:, 1] <= b)][:, 2]))
        anch.append(('ANCH_ENG', (xmin, (a + b) / 2, zc), 'aft'))
ymax_i, ymin_i = np.argmax(co[:, 1]), np.argmin(co[:, 1])
anch.append(('ANCH_NAV', tuple(co[ymax_i]), 'up'))
anch.append(('ANCH_NAV', tuple(co[ymin_i]), 'up'))
nose = co[np.argmax(co[:, 0])]
anch.append(('ANCH_MUZ', tuple(nose), 'fwd'))

# ---- eksen dönüşümü: (x uzunluk, y yanal, z yukarı) → Blender (X=y, Y=−x, Z=z) ; burun glTF +Z
def tb(p):
    return (p[1], -p[0], p[2])


LEN = max(v.co.x for v in ob.data.vertices) - min(v.co.x for v in ob.data.vertices)
SC = 1.0 / LEN      # uzunluk tam 1,0 (yumuşatma kısalttı)
anch = [(n_, tuple(c * SC for c in p_), k_) for n_, p_, k_ in anch]
for o in (ob, ob1):
    for v in o.data.vertices:
        v.co = Vector(tb(v.co * SC))
    o.data.update()
    o.data.calc_loop_triangles()
bmx = bmesh.new()
for o in (ob, ob1):
    bmx.from_mesh(o.data)
    bmesh.ops.reverse_faces(bmx, faces=[])      # dönüşüm yönelimi korur (dönme)
    bmx.clear()
bmx.free()
root = export.empty('SD_' + spec['id'])
l0 = export.empty('LOD0', root)
l1 = export.empty('LOD1', root)
ob.parent = l0
ob1.parent = l1
counts = {}
for nm, p, kind in anch:
    counts[nm] = counts.get(nm, 0) + 1
    d = {'aft': (0, 1, 0), 'up': (0, 0, 1), 'fwd': (0, -1, 0)}[kind]
    export.socket(root, '%s_%d' % (nm, counts[nm] - 1), tb(p), d, {'purpose': nm})
objs = [root] + [o for o in bpy.data.objects if o.parent is not None]
glb = os.path.join(out, 'sd_%s%s.glb' % (spec['id'], SUF))
for o in objs:
    for k in [k for k in o.keys() if k.startswith('sd_')]:
        del o[k]
export.export_glb(glb, objs, quality=90)
size_b, rec = glbpack.recompress_textures(glb)
T0 = tick('export', T0)

# ---- yan yana kıyas: kaynak üst/yan | model üst/yan (nötr ışık, ortografik)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'model.blend'), compress=True)
R.rig_neutral()
cam_d = bpy.data.cameras.new('c')
cam_d.type = 'ORTHO'
cam = bpy.data.objects.new('c', cam_d)
bpy.context.scene.collection.objects.link(cam)
sc.camera = cam
renders = {}
_co = np.array([v.co[:] for v in ob.data.vertices])
_cy, _cz = float((_co[:, 1].min() + _co[:, 1].max()) / 2), float((_co[:, 2].min() + _co[:, 2].max()) / 2)
ob1.hide_render = True
ob.hide_render = False
for nm, loc, rot, sz, (W_, H_) in (
        ('top', (0, _cy, 3), (0, 0, -math.pi / 2), 1.3, (900, int(900 * ht))),      # burun sağda, kaynak çizimle aynı yönelim
        ('side', (-3, _cy, _cz), (math.pi / 2, 0, -math.pi / 2), 1.3, (900, int(900 * hs))),
        ('persp', None, None, None, (900, 560))):
    if nm == 'persp':
        cam_d.type = 'PERSP'
        cam_d.lens = 42
        cam.location = (0.95, 0.85, 0.55)
        d = Vector((0, 0, 0)) - cam.location
        cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    else:
        cam_d.type = 'ORTHO'
        cam_d.ortho_scale = sz
        cam.location = loc
        cam.rotation_euler = rot
    path = os.path.join(out, 'm_%s.png' % nm)
    R.render(path, cam, (W_, H_), 24, view='Standard', transparent=True, bounces=0)
    renders[nm] = path
info.update({'tris1': tris1, 'glb_bytes': size_b, 'texture_recompress': rec, 'has_emit': bool(has_emit), 'anchors': [(a[0], [round(float(x), 3) for x in tb(a[1])]) for a in anch],
             'timings': T, 'seconds': round(time.time() - t_start, 1)})
json.dump(info, open(os.path.join(out, 'meta.json'), 'w'), indent=1, ensure_ascii=False)
print('RESULT', json.dumps(info, ensure_ascii=False))
