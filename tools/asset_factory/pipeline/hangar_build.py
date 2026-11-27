"""Hangar giriş koridoru modülü + dış kapı (Ankora prototipi). Mevcut sanat dili: kaynak = oyundaki xdoor_ankora (kapı), ximg_in (koridor duvar/zemin/tavan) çizimleri.
Ölçüler oyun koduyla aynı: OW=9, OH=5,2, segment uzunluğu XSEG=7,6 (koridor 6 segment). Parametrik geometri + kaynak çizimlerin düzlemsel izdüşümü (palet birebir).
Çıktı: hangar_koridor_ankora.glb (1 modül, LOD0 ≤ 6k), hangar_kapi_dis_ankora.glb (≤ 4k). Eksen: oyun uzayı, koridor boyu +Z (oyun −Z ileri → burada +Z), yukarı +Y; birim = oyun birimi.
Kullanım: python pipeline/hangar_build.py <çıktı_klasörü>"""
import os, sys, json, math, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix
from PIL import Image
from core import geo, export, bake as B, glbpack, render as R

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
out = sys.argv[1]
ST = sys.argv[2] if len(sys.argv) > 2 else 'ankora'      # istasyon: ankora, demirhan, ice, kara, kristal, lonca
os.makedirs(out, exist_ok=True)
IC = len(sys.argv) > 3 and sys.argv[3] == 'ic'      # iç hangar kabuğu + iç kapı (Parti 2 / I3)
OW, OH, XSEG = 9.0, 5.2, (15.0 if IC else 7.6)
TEX = 1024
T = TEX // 2      # 4 karo 512²: 0 kapı, 1 duvar, 2 zemin, 3 tavan
t_start = time.time()


def crop(path, box, size):
    im = Image.open(os.path.join(REPO, path)).convert('RGB')
    w, h = im.size
    return im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h))).resize(size, Image.LANCZOS)


def lab_stats(im):
    a = np.array(im.convert('RGB').resize((128, 128))).astype(np.float32) / 255.0
    c = np.where(a > 0.04045, ((a + 0.055) / 1.055) ** 2.4, a / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    x = c.reshape(-1, 3) @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(x > 0.008856, np.cbrt(x), 7.787 * x + 16 / 116)
    L = np.stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])], -1)
    return L.mean(0), L.std(0) + 1e-3


def to_lab(a):
    c = np.where(a > 0.04045, ((a + 0.055) / 1.055) ** 2.4, a / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    sh = c.shape
    x = c.reshape(-1, 3) @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(x > 0.008856, np.cbrt(x), 7.787 * x + 16 / 116)
    return np.stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])], -1).reshape(sh)


def from_lab(L):
    sh = L.shape
    L = L.reshape(-1, 3)
    fy = (L[:, 0] + 16) / 116
    fx = fy + L[:, 1] / 500
    fz = fy - L[:, 2] / 200
    inv = lambda f: np.where(f ** 3 > 0.008856, f ** 3, (f - 16 / 116) / 7.787)
    xyz = np.stack([inv(fx) * 0.95047, inv(fy), inv(fz) * 1.08883], -1)
    M = np.linalg.inv(np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]))
    c = xyz @ M.T
    c = np.clip(c, 0, 1)
    a = np.where(c > 0.0031308, 1.055 * c ** (1 / 2.4) - 0.055, 12.92 * c)
    return a.reshape(sh)


WARM = {'ankora': (34, 9, 24)}      # (min L, a, b): sıcak amber/bronz (oyun içi Ankora hangarı)


def recolor(im, ref, strength=0.9):
    """istasyon paleti: koridor dokularının Lab ortalama/sapması, istasyonun kapı çizimine kaydırılır (ankora: kaynak ximg_in birebir)"""
    m0, s0 = lab_stats(im)
    m1, s1 = lab_stats(ref)
    if ST in WARM:      # istasyon kimlik tonu: kapı çiziminin L'sini koru, a/b ortalamasını hedef tona çek
        m1 = m1.copy(); m1[0] = max(m1[0], WARM[ST][0]); m1[1], m1[2] = WARM[ST][1], WARM[ST][2]
        s1 = s1.copy(); s1[1:] = np.maximum(s1[1:], 3.0)
    a = np.array(im.convert('RGB')).astype(np.float32) / 255.0
    L = to_lab(a)
    L2 = (L - m0) / s0 * (s1 * 0.8 + s0 * 0.2) + m1
    L2[..., 0] = np.clip(L2[..., 0], 2, 98)
    L3 = strength * L2 + (1 - strength) * L
    if ST in WARM:      # r5: albedo luminansı ×0.5, kroma ×0.6 (oyun içi referans koyu düşük doygun bronz-gri)
        Y = ((L3[..., 0] + 16) / 116) ** 3 * 0.50
        L3[..., 0] = 116 * np.cbrt(Y) - 16
        L3[..., 1:] *= 0.6
    out = from_lab(L3)
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


door_src = Image.open(os.path.join(REPO, 'assets/img/xdoor_%s.webp' % ST)).convert('RGB')
atlas = Image.new('RGB', (TEX, TEX))
atlas.paste(door_src.resize((T, T), Image.LANCZOS), (0, 0))                                                            # 0: kapı (istasyonun kendi kapı çizimi)
atlas.paste(recolor(crop('assets/img/ximg_in.webp', (0.0, 0.10, 0.30, 0.90), (T, T)), door_src), (T, 0))               # 1: duvar
atlas.paste(recolor(crop('assets/img/ximg_in.webp', (0.25, 0.70, 0.75, 1.0), (T, T)), door_src), (0, T))               # 2: zemin
atlas.paste(recolor(crop('assets/img/ximg_in.webp', (0.25, 0.0, 0.75, 0.25), (T, T)), door_src), (T, T))              # 3: tavan
from PIL import ImageDraw
SY0, SY1 = int(T + 0.92 * T), int(T + 0.99 * T)      # şerit satırları (tile 2/3 alt kenarı)
haz = Image.new('RGB', (T, SY1 - SY0), (18, 18, 15)); hd = ImageDraw.Draw(haz); hh = SY1 - SY0
for k in range(-hh, T + hh, 2 * hh // 1):
    hd.polygon([(k, hh), (k + hh // 1, 0), (k + hh * 3 // 2, 0), (k + hh // 2, hh)], fill=(232, 178, 22))
ImageDraw.Draw(haz).rectangle([T - 44, 0, T - 1, hh], fill=(26, 24, 21))
atlas.paste(haz, (0, SY0))
lit = Image.new('RGB', (T, SY1 - SY0), (255, 232, 180)); ld = ImageDraw.Draw(lit)
ld.rectangle([0, 0, T - 1, 3], fill=(120, 100, 70)); ld.rectangle([0, hh - 4, T - 1, hh - 1], fill=(120, 100, 70))
atlas.paste(lit, (T, SY0))
base = np.array(atlas).astype(np.float32) / 255.0


class Mesh:
    def __init__(self):
        self.bm = bmesh.new()
        self.uvl = self.bm.loops.layers.uv.verify()

    def strip(self, c, s, which, proj, ext):
        """şerit kutusu: which='haz' (sarı-siyah) / 'lit' (armatür paneli); düz yerleşim u=ext[0] tekrar"""
        r = bmesh.ops.create_cube(self.bm, size=1.0)
        bmesh.ops.transform(self.bm, matrix=Matrix.Translation(Vector(c)) @ Matrix.Diagonal((*s, 1.0)), verts=r['verts'])
        x0 = 0.0 if which == 'haz' else 0.5
        if which == 'dark':
            for f in self.bm.faces:
                if all(v in r['verts'] for v in f.verts):
                    for lp in f.loops:
                        lp[self.uvl].uv = ((T - 22) / TEX, 1.0 - (SY0 + 0.5 * (SY1 - SY0)) / TEX)
            return
        for f in self.bm.faces:
            if not all(v in r['verts'] for v in f.verts):
                continue
            for lp in f.loops:
                p = lp.vert.co
                u = (p.z if proj == 'x' else p.x) / ext
                lp[self.uvl].uv = (x0 + 0.01 + 0.40 * (u % 1.0), 1.0 - (SY0 + 0.5 * (SY1 - SY0)) / TEX + 0.0 * p.y)

    def box(self, c, s, tile, proj, ext, rot=None):
        ext = (1.2, 1.2) if tile == 0 else (2.4, 2.4)      # r5: tüm kutularda aynı dünya ölçeği (m/karo)
        """kutu; proj='z' (XY düzlemi, Z normali) / 'x' (YZ) / 'y' (XZ): kaynak karo bu düzleme ölçekli düzlemsel yerleşir (ext = karo ölçüsü m)"""
        r = bmesh.ops.create_cube(self.bm, size=1.0)
        M = Matrix.Translation(Vector(c)) @ Matrix.Diagonal((*s, 1.0))
        bmesh.ops.transform(self.bm, matrix=M, verts=r['verts'])
        tx, ty = (tile % 2) * 0.5, (tile // 2) * 0.5
        for f in self.bm.faces:
            if not all(v in r['verts'] for v in f.verts):
                continue
            for lp in f.loops:
                p = lp.vert.co
                if proj == 'z':
                    u, v = p.x / ext[0], p.y / ext[1]
                elif proj == 'x':
                    u, v = p.z / ext[0], p.y / ext[1]
                else:
                    u, v = p.x / ext[0], p.z / ext[1]
                lp[self.uvl].uv = (tx + 0.02 + 0.46 * (u % 1.0), 1.0 - (ty + 0.02 + (0.38 if tile >= 2 else 0.46) * (1 - (v % 1.0))))


def cyl_x(m, p0, p1, r, tile, seg=10):
    d = Vector(p1) - Vector(p0)
    M = Matrix.Translation((Vector(p0) + Vector(p1)) / 2) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    res = bmesh.ops.create_cone(m.bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r, depth=d.length, matrix=M)
    tx, ty = (tile % 2) * 0.5, (tile // 2) * 0.5
    for v in res['verts']:
        for lp in v.link_loops:
            lp[m.uvl].uv = (tx + 0.02 + 0.46 * ((v.co.x + v.co.z) * 0.2 % 1.0), 1.0 - (ty + 0.02 + 0.46 * (v.co.y * 0.3 % 1.0)))


def octa_frame(m, z, w, h, th, depth, tile, ch=1.1):
    """sekizgen çerçeve halkası: iç boşluk w×h, kalınlık th, derinlik (Z) depth; köşe pahı ch"""
    # 4 kenar kutusu + 4 çapraz köşe kutusu
    m.box((0, h / 2 + th / 2, z), (w + 2 * th, th, depth), tile, 'z', (4.5, 2.6))
    m.box((0, -h / 2 - th / 2, z), (w + 2 * th, th, depth), tile, 'z', (4.5, 2.6))
    m.box((w / 2 + th / 2, 0, z), (th, h, depth), tile, 'x', (2.6, 2.6))
    m.box((-w / 2 - th / 2, 0, z), (th, h, depth), tile, 'x', (2.6, 2.6))
    for sx in (-1, 1):      # köşe takviyeleri (pah görünümü): iç köşede kare dolgu
        for sy in (-1, 1):
            m.box((sx * (w / 2 - ch / 2), sy * (h / 2 - ch / 2), z), (ch, ch, depth * 0.92), tile, 'z', (4.5, 2.6))


def corridor():
    m = Mesh()
    L = XSEG
    # zemin: dolu plaka; kenarlarda levha dikişleri; orta bölge (iniş yastığı) sade; kenarlarda sarı-siyah uyarı şeridi
    m.box((0, -OH / 2 - 0.15, L / 2), (OW + 1.2, 0.3, L), 2, 'y', (4.5, 3.8))
    m.strip((0, -OH / 2 + 0.006, L / 2), (4.4, 0.012, L - 0.1), 'dark', 'x', 1.0)      # iniş yastığı bölgesi: koyu sade
    for sx in (-1, 1):
        for k in range(4):
            for cx, w in ((2.95, 0.95), (3.95, 0.95)):
                m.box((sx * cx, -OH / 2 + 0.02, 0.1 + 0.95 + k * 1.85), (w, 0.04, 1.75), 2, 'y', (2.0, 1.8))
        m.strip((sx * (OW / 2 - 0.35), -OH / 2 + 0.005, L / 2), (0.5, 0.012, L - 0.1), 'haz', 'x', 0.8)
        m.strip((sx * 2.25, -OH / 2 + 0.005, L / 2), (0.12, 0.012, L - 0.1), 'haz', 'x', 0.8)
    # tavan: dolu plaka, enine kirişler, armatür gövdesi + emissive panel (oyun ışığı armatür konumlarına eklenir)
    m.box((0, OH / 2 + 0.15, L / 2), (OW + 1.2, 0.3, L), 3, 'y', (4.5, 3.8))
    for k in range(7):
        zz = 0.5 + k * (L - 1.0) / 6
        m.box((0, OH / 2 - 0.1, zz), (OW - 0.4, 0.2, 0.2), 1, 'y', (4.5, 3.8))
    for sx in (-1, 1):
        for k in range(4):
            zz = 0.95 + k * (L - 1.9) / 3
            m.box((sx * 1.9, OH / 2 - 0.1, zz), (0.9, 0.14, 1.5), 1, 'y', (2.0, 2.0))      # gövde
            m.strip((sx * 1.9, OH / 2 - 0.185, zz), (0.7, 0.02, 1.3), 'lit', 'z', 0.7)       # emissive panel
    # duvarlar: dolu panel plakaları + dikey kaburga + zemine yakın sarı-siyah şerit; borular üstte ayrıntı
    for sx in (-1, 1):
        m.box((sx * (OW / 2 + 0.1), 0, L / 2), (0.2, OH + 0.6, L), 1, 'x', (3.8, 5.2))
        for k in range(4):          # alt ve üst panel plakaları (dikişli)
            zc = 0.1 + 0.95 + k * 1.85
            m.box((sx * (OW / 2 - 0.05), -1.35, zc), (0.1, 2.3, 1.75), 1, 'x', (1.75, 2.3))
            m.box((sx * (OW / 2 - 0.05), 1.05, zc), (0.1, 2.9, 1.75), 1, 'x', (1.75, 2.9))
            m.box((sx * (OW / 2 - 0.11), 0.0, zc), (0.06, 0.5, 1.2), 0, 'x', (1.2, 0.5))      # iç panel kapak
        m.strip((sx * (OW / 2 - 0.12), -OH / 2 + 0.3, L / 2), (0.06, 0.26, L - 0.1), 'haz', 'x', 1.0)
        for k in range(5):
            m.box((sx * (OW / 2 - 0.17), 0, 0.45 + k * (L - 0.9) / 4), (0.3, OH, 0.28), 1, 'x', (1.0, 5.2))
        # boru demetleri (panel üstüne, 5 hat) + kelepçeler + vana/kontrol blokları
        for yy, rr in ((-1.5, 0.16), (-0.2, 0.16), (1.1, 0.16), (2.0, 0.16), (-2.1, 0.07), (0.45, 0.10), (1.6, 0.07), (2.35, 0.12)):
            cyl_x(m, (sx * (OW / 2 - 0.40), yy, 0.2), (sx * (OW / 2 - 0.40), yy, L - 0.2), rr, 1, 8)
        for k in range(10):
            zz = 0.55 + k * (L - 1.1) / 9
            for yy in (-1.5, -0.2, 1.1):
                m.box((sx * (OW / 2 - 0.40), yy, zz), (0.34, 0.36, 0.14), 0, 'x', (1.2, 1.2))
            if k % 3 == 1:
                m.box((sx * (OW / 2 - 0.45), 0.65, zz), (0.4, 0.8, 0.5), 1, 'x', (1.0, 1.0))
                m.box((sx * (OW / 2 - 0.50), 0.65, zz), (0.3, 0.25, 0.3), 0, 'x', (0.5, 0.5))
            if k % 3 == 0:
                m.box((sx * (OW / 2 - 0.30), 1.75, zz + 0.3), (0.22, 1.1, 0.7), 1, 'x', (1.0, 1.0))
    # uçlarda sekizgen çerçeve (segment bağlantısı)
    octa_frame(m, 0.14, OW - 0.4, OH - 0.2, 0.42, 0.28, 0)
    octa_frame(m, L - 0.14, OW - 0.4, OH - 0.2, 0.42, 0.28, 0)
    return m


def door_frame():
    """sabit kasa: derin çerçeve, üst lamba kutuları, kilit gövdesi, menteşe kutuları, uyarı bantları, bulon sıraları"""
    m = Mesh()
    octa_frame(m, 0.0, OW, OH, 0.7, 1.0, 0, ch=0.55)
    for sx in (-1, 1):
        m.box((sx * 2.3, OH / 2 - 0.15, 0.55), (0.9, 0.22, 0.18), 0, 'z', (3.0, 3.0))                    # uyarı lambası kutuları
        for yy in (-1.8, 0, 1.8):
            m.box((sx * (OW / 2 - 0.15), yy, 0.52), (0.38, 0.55, 0.24), 0, 'z', (3.0, 3.0))               # menteşe/raylı kutular
    for xx in np.linspace(-OW / 2 + 0.5, OW / 2 - 0.5, 14):                                                # üst ve alt bulon sıraları
        for yy in (OH / 2 + 0.35, -OH / 2 - 0.35):
            m.box((xx, yy, 0.52), (0.1, 0.1, 0.07), 0, 'z', (3.0, 3.0))
    m.box((0, OH / 2 - 0.45, 0.5), (OW - 1.2, 0.18, 0.12), 0, 'z', (3.0, 3.0))                               # üst ray
    m.box((0, -OH / 2 + 0.2, 0.5), (OW - 1.2, 0.3, 0.12), 0, 'z', (3.0, 3.0))                               # alt ray (sarı-siyah doku)
    return m


def door_leaf(sx):
    """kanat: kendi yarı dokusuna hizalı (kaynak çizim yarısı), yükseltilmiş çerçeveli paneller, bulon/kilit ayrıntıları; yerel koordinat = kanat merkezi"""
    m = Mesh()
    LW = OW / 2 - 0.04
    tx0 = 0.0 if sx < 0 else 0.5            # sol kanat = çizimin sol yarısı, sağ kanat = sağ yarısı
    def add(c, size, back=False, pad=0.0):
        r = bmesh.ops.create_cube(m.bm, size=1.0)
        bmesh.ops.transform(m.bm, matrix=Matrix.Translation(c) @ Matrix.Diagonal((*size, 1.0)), verts=r['verts'])
        for f in m.bm.faces:
            if not all(v in r['verts'] for v in f.verts):
                continue
            for lp in f.loops:
                p = lp.vert.co
                # kanat yerel (0 merkez) → kapı çizimi koordinatı: kapı genişliği OW, merkezde birleşme
                gx = p.x + sx * (OW / 4)           # kapı uzayında x
                u = (gx + OW / 2) / OW             # 0..1 çizim yatay
                v = (p.y + OH / 2) / OH
                lp[m.uvl].uv = (0.02 + 0.46 * u, 1.0 - (0.02 + 0.46 * (1 - v)))
    add((0, 0, 0.1), (LW, OH - 0.05, 0.5))
    # yükseltilmiş çerçeveli paneller (çizimdeki 4 panelle aynı konum: kanat başına üst ve alt, iç kenar kanat merkezine göre)
    for py in (0.95, -0.95):
        add((0, py, 0.38), (LW * 0.72, 1.85, 0.10))
        add((0, py, 0.43), (LW * 0.60, 1.55, 0.05))
    # dikey takviye kaburgaları ve bulon sıraları
    for xx in (-LW / 2 + 0.12, LW / 2 - 0.12):
        add((xx, 0, 0.4), (0.16, OH - 0.4, 0.12))
        for yy in np.linspace(-OH / 2 + 0.4, OH / 2 - 0.4, 9):
            add((xx, yy, 0.48), (0.09, 0.09, 0.06))
    # orta kenarda kilit pimi gövdesi (iki kanat birleşme tarafı)
    inner = -sx * (LW / 2 - 0.1)
    for yy in (-1.5, 0, 1.5):
        add((inner, yy, 0.45), (0.28, 0.5, 0.2))
    # uyarı şeridi plakaları (alt/üst)
    add((0, OH / 2 - 0.28, 0.42), (LW - 0.3, 0.26, 0.08))
    add((0, -OH / 2 + 0.28, 0.42), (LW - 0.3, 0.26, 0.08))
    bmesh.ops.translate(m.bm, vec=(sx * OW / 4, 0, 0), verts=m.bm.verts)      # kapalı konum: geometri dünya konumunda, düğüm başlangıcı 0 (kayma = düğüm ±X)
    return m


def finish(mesh, name, extra_scale=1.0):
    bmesh.ops.recalc_face_normals(mesh.bm, faces=mesh.bm.faces)
    me = bpy.data.meshes.new(name)
    mesh.bm.to_mesh(me)
    mesh.bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


geo.reset_scene()
cor = finish(corridor(), 'LOD0_koridor')
dorF = finish(door_frame(), 'FRAME')
dorL = finish(door_leaf(-1), 'DOOR_L')
dorR = finish(door_leaf(1), 'DOOR_R')
dor = dorF
if IC:      # iç kapı koridor/kabuk sonunda (z = XSEG)
    for ob_ in (dorF, dorL, dorR):
        for v_ in ob_.data.vertices:
            v_.co.z += XSEG
        ob_.data.update()
# doku türetme (npc_build ile aynı mantık)
rgb = base
lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
mx, mn = rgb.max(-1), rgb.min(-1)
sat = np.where(mx > 1e-4, (mx - mn) / np.maximum(mx, 1e-4), 0)
metal = np.clip((0.55 - sat) * 1.4, 0, 1) * np.clip((lum - 0.12) * 4, 0, 1) * 0.55
rough = np.clip(0.80 - 0.34 * lum + 0.12 * sat, 0.30, 0.95)
orm = np.ones((TEX, TEX, 3), np.float32)
orm[..., 1] = rough
orm[..., 2] = metal
em = ((mx > 0.70) & (sat > 0.45)).astype(np.float32)
em = np.array(Image.fromarray((em * 255).astype(np.uint8)).filter(__import__('PIL.ImageFilter', fromlist=['x']).MaxFilter(3))) / 255.0
em[SY0:SY1, :T] = 0.0                       # uyarı şeridi sarısı emissive değil
em[SY0:SY1, T:] = 1.0                       # armatür paneli tam emissive
emis = rgb * em[..., None]


def mkimg(name, arr3, non_color):
    h, w = arr3.shape[:2]
    im = bpy.data.images.new(name, w, h, alpha=False)
    if non_color:
        im.colorspace_settings.name = 'Non-Color'
    a4 = np.concatenate([np.clip(arr3, 0, 1), np.ones((h, w, 1), np.float32)], -1)[::-1]
    im.pixels = a4.astype(np.float32).ravel().tolist()
    return im


img_b = mkimg('sd_hangar_base', base, False)
orm_s = np.array(Image.fromarray((np.clip(orm, 0, 1) * 255).astype(np.uint8)).resize((512, 512), Image.LANCZOS)).astype(np.float32) / 255.0
img_o = mkimg('sd_hangar_orm', orm_s, True)
e_s = np.array(Image.fromarray((np.clip(emis, 0, 1) * 255).astype(np.uint8)).resize((512, 512), Image.LANCZOS)).astype(np.float32) / 255.0
img_e = mkimg('sd_hangar_emit', e_s, False)
mat = B.gltf_body_material('MAT_hangar_' + ST, img_b, img_o, None, img_e)
tris = {}
metas = {}
parts = {'koridor': [cor], 'kapi': [dorF, dorL, dorR]}
LWIDTH = OW / 2 - 0.04
for nm, obs in parts.items():
    for ob in obs:
        B.assign_single(ob, mat)
        geo.set_smooth_by_angle(ob, 40)
        bm = bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.triangulate(bm, faces=bm.faces); bm.to_mesh(ob.data); bm.free()
    tris[nm] = sum(len(o.data.polygons) for o in obs)
for nm, obs in parts.items():
    # oyun uzayı: koridorda (x yanal, y yukarı, z boy) kuruldu → Blender (x, −z, y) (glTF dönüşümü ile oyun uzayı)
    for ob in obs:
        for v in ob.data.vertices:
            v.co = Vector((v.co.x, -v.co.z, v.co.y))
        ob.data.update()
    root = export.empty('SD_hangar_' + nm)
    for ob in obs:
        ob.parent = root
        if ob.name in ('DOOR_L', 'DOOR_R'):      # Lead sözleşmesi: dışa kayma ±X, mesafe = kanat genişliğinin %95'i, süre 1,2 sn, ease-in-out; kasa sabit
            ob['slide'] = round(LWIDTH * 0.95, 3)
            ob['axis'] = 'x'
            ob['dir'] = -1 if ob.name == 'DOOR_L' else 1
            ob['dur'] = 1.2
            ob['ease'] = 'inOut'
    objs = [root] + obs
    for o in objs:
        for k in [k for k in o.keys() if k.startswith('sd_')]:
            del o[k]
    glb = os.path.join(out, 'hangar_%s%s_%s.glb' % ('ic_' if IC else '', nm, ST))
    export.export_glb(glb, objs, quality=90)
    sz, rec = glbpack.recompress_textures(glb)
    metas[nm] = {'bytes': sz, 'tris': tris[nm]}
# önizleme (Blender: koridor boyu −Y, yukarı Z)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'model.blend'), compress=True)
sc = bpy.context.scene
R.rig_neutral()
cd = bpy.data.cameras.new('c'); cd.type = 'PERSP'; cd.lens = 28
cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
# koridor: iç görünüm (başlangıçtan boyuna bakış); kapı: önden
# önizleme: koridor modülü 3 kez tekrarlanır + sonda kapı (oyundaki 6 segment yerine kısa); GLB'de tek modül
for i_ in (1, 2):
    c2 = cor.copy(); c2.data = cor.data; bpy.context.scene.collection.objects.link(c2); c2.location = (0, -XSEG * i_, 0); c2.name = 'prev_cor%d' % i_
d2s = []
for o_ in (dorF, dorL, dorR):
    c3 = o_.copy(); c3.data = o_.data; bpy.context.scene.collection.objects.link(c3); c3.location = (0, -XSEG * 3, 0); c3.name = 'prev_door_' + o_.name; d2s.append(c3)
dorF.hide_render = dorL.hide_render = dorR.hide_render = True
cor.hide_render = False
cam.location = (1.8, 0.8, -1.2)
cam.rotation_euler = (Vector((-0.06, -1, 0.03))).to_track_quat('-Z', 'Y').to_euler()
R.render(os.path.join(out, 'm_koridor.png'), cam, (1000, 560), 24, view='Standard', transparent=False, bounces=1)
for o_ in bpy.data.objects:
    if o_.name.startswith('prev_cor'): o_.hide_render = True
cor.hide_render = True; dorF.hide_render = dorL.hide_render = dorR.hide_render = False
for c3 in d2s: c3.hide_render = True
cam.location = (0, 9.5, 0.0)
cam.rotation_euler = Vector((0, -1, 0)).to_track_quat('-Z', 'Y').to_euler()
R.render(os.path.join(out, 'm_kapi.png'), cam, (1000, 560), 24, view='Standard', transparent=False, bounces=1)
cam.location = (7.5, 8, 3.5)
cam.rotation_euler = (Vector((0, 0, 0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
R.render(os.path.join(out, 'm_kapi_aci.png'), cam, (1000, 560), 24, view='Standard', transparent=False, bounces=1)
json.dump({'parcalar': metas, 'seconds': round(time.time() - t_start, 1)}, open(os.path.join(out, 'meta.json'), 'w'), indent=1)
print('RESULT', json.dumps({'parcalar': metas, 'seconds': round(time.time() - t_start, 1)}))
