"""Kaşif — sıfırdan modelleme (konsept c001): kalın yuvarlak mavi-gri keşif gemisi, 4 motor kovanı (2×2), kısa geri süpürmeli kanatlar, camlı burun, radar/anten.
Oyun uzayı: burun +Z, yukarı +Y, uzunluk 1,0. Kullanım: python pipeline/ship_sahin.py <çıktı_klasörü>"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy, bmesh
from core.shipkit import Kit

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
PAL = {
    'gri': ((0.16, 0.21, 0.27), 0.5, 0.45, None), 'beyaz': ((0.48, 0.50, 0.52), 0.5, 0.35, None),
    'koyu': ((0.05, 0.055, 0.07), 0.55, 0.5, None), 'turkuaz': ((0.1, 0.55, 0.55), 0.5, 0.2, (0.15, 0.85, 0.85, 3.0)),
    'cam': ((0.05, 0.14, 0.26), 0.08, 0.0, (0.2, 0.5, 0.95, 0.6)), 'alev': ((1, .5, .5), 0.5, 0, (1.0, 0.5, 0.5, 5.0)),
    'bell': ((0.03, 0.03, 0.035), 0.5, 0.75, None), 'pas': ((0.22, 0.14, 0.09), 0.7, 0.3, None),
}
K = Kit(PAL)
K.noreno.add('bell')


def prism(pts, th, mat):
    """üst yüzey noktaları (x,y,z) saat yönü fark etmez; alt = y - th (kanat/kuyruk)"""
    bm = K.BM[mat]
    top = [bm.verts.new(p) for p in pts]
    bot = [bm.verts.new((p[0], p[1] - th, p[2])) for p in pts]
    bm.faces.new(top); bm.faces.new(bot[::-1])
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new([top[j], top[i], bot[i], bot[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def fin(pts_yz, x, th, mat):
    bm = K.BM[mat]
    a = [bm.verts.new((x - th / 2, y, z)) for y, z in pts_yz]
    b = [bm.verts.new((x + th / 2, y, z)) for y, z in pts_yz]
    bm.faces.new(a); bm.faces.new(b[::-1])
    for i in range(len(pts_yz)):
        j = (i + 1) % len(pts_yz)
        bm.faces.new([a[j], a[i], b[i], b[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)



def prism(pts, th, mat):
    bm = K.BM[mat]
    top = [bm.verts.new(p) for p in pts]
    bot = [bm.verts.new((p[0], p[1] - th, p[2])) for p in pts]
    bm.faces.new(top); bm.faces.new(bot[::-1])
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new([top[j], top[i], bot[i], bot[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


# gövde: kalın, yuvarlak kesitli (6 köşeli), burun daralır
K.loft([(-0.40, 0.100, 0.085, 0.125, -0.125, 0), (-0.25, 0.140, 0.120, 0.135, -0.140, 0), (0.0, 0.155, 0.130, 0.140, -0.145, 0),
        (0.20, 0.140, 0.110, 0.125, -0.130, 0), (0.34, 0.105, 0.075, 0.100, -0.105, 0), (0.45, 0.060, 0.040, 0.068, -0.075, 0), (0.505, 0.020, 0.015, 0.030, -0.035, 0)], 'gri')
K.loft([(-0.30, 0.100, 0.100, 0.1365, 0.132, 0), (0.0, 0.110, 0.110, 0.1415, 0.137, 0), (0.22, 0.090, 0.090, 0.1265, 0.122, 0)], 'beyaz')      # üst plaka
# burun camı: üç pano, eğimli
K.loft([(0.30, 0.060, 0.092, 0.118, 0.062, 0), (0.37, 0.058, 0.086, 0.108, 0.056, 0), (0.44, 0.040, 0.060, 0.082, 0.050, 0), (0.49, 0.015, 0.026, 0.040, 0.026, 0)], 'cam')
for z in (0.335, 0.40, 0.46):
    K.box((0, 0.108 - (z - 0.30) * 0.18, z), (0.20 - (z - 0.30) * 0.6, 0.006, 0.008), 'koyu', 0.001)
# üst güverte: radar tabağı + anten, taret kubbesi, kapaklar
K.cyl((0, 0.14, -0.06), (0, 0.17, -0.06), 0.018, 'koyu', seg=12)
K.cyl((0.0, 0.17, -0.06), (0.03, 0.215, -0.06), 0.008, 'koyu', seg=8)
K.cyl((0.03, 0.215, -0.06), (0.032, 0.22, -0.06), 0.04, 'beyaz', 0.002, seg=16)
K.cyl((-0.05, 0.14, -0.12), (-0.05, 0.31, -0.12), 0.003, 'koyu', seg=6)
K.cyl((0.0, 0.14, 0.06), (0.0, 0.155, 0.06), 0.04, 'koyu', seg=20)
K.cyl((0.0, 0.155, 0.06), (0.0, 0.165, 0.06), 0.028, 'beyaz', 0.02, seg=20)
for z in (-0.20, -0.10, 0.12):
    K.box((0.0 if z != 0.12 else 0.07, 0.141, z), (0.07, 0.006, 0.06), 'koyu', 0.002)
# yan ışık şeritleri + panel bantları
for sx in (-1, 1):
    K.box((sx * 0.158, 0.02, -0.10), (0.004, 0.005, 0.40), 'turkuaz', 0.001)
    K.box((sx * 0.145, -0.08, 0.15), (0.004, 0.005, 0.20), 'turkuaz', 0.001)
    K.box((sx * 0.157, 0.0, 0.04), (0.006, 0.20, 0.004), 'koyu', 0.001)
    K.box((sx * 0.155, 0.0, 0.24), (0.006, 0.17, 0.004), 'koyu', 0.001)
    K.box((sx * 0.152, 0.05, -0.32), (0.006, 0.12, 0.004), 'koyu', 0.001)
# kanatlar: kısa, geri süpürmeli, hafif aşağıda
for sx in (-1, 1):
    LE0, LE1, TE1, TE0 = (0.12, -0.04, 0.09), (0.50, -0.075, -0.12), (0.50, -0.075, -0.27), (0.12, -0.04, -0.12)
    def P(*v): return [(sx * p[0], p[1], p[2]) for p in v]
    w = P(LE0, LE1, TE1, TE0)
    prism(w if sx > 0 else w[::-1], 0.024, 'gri')
    w2 = P((0.12, -0.038, 0.09), (0.50, -0.0735, -0.12), (0.50, -0.0735, -0.15), (0.14, -0.038, 0.03))
    prism(w2 if sx > 0 else w2[::-1], 0.020, 'beyaz')
    for t in (0.4, 0.7):
        K.box((sx * (0.12 + 0.38 * t), -0.04 - 0.035 * t, 0.09 - 0.21 * t - 0.08), (0.003, 0.003, 0.14), 'koyu', 0.0005)
    K.box((sx * 0.50, -0.075, -0.20), (0.012, 0.03, 0.14), 'koyu', 0.002)
    # kanat köküne havalandırma/boru
    K.box((sx * 0.17, -0.07, 0.02), (0.07, 0.04, 0.18), 'koyu', 0.004)
# 4 motor kovanı (2×2) + burun spinneri + halka + çan + parlak çekirdek
ENG = [(sx * 0.125, y) for sx in (-1, 1) for y in (0.10, -0.09)]
for x, y in ENG:
    K.cyl((x, y, -0.26), (x, y, -0.46), 0.062, 'gri', 0.060, seg=20)
    K.cyl((x, y, -0.20), (x, y, -0.26), 0.056, 'beyaz', 0.062, seg=20)
    K.cyl((x, y, -0.15), (x, y, -0.20), 0.030, 'beyaz', 0.056, seg=20)          # önde spinner
    K.cyl((x, y, -0.40), (x, y, -0.43), 0.066, 'koyu', seg=20)
    K.cyl((x, y, -0.46), (x, y, -0.50), 0.056, 'bell', 0.064, seg=20, cap=False)
    K.cyl((x, y, -0.50), (x, y, -0.506), 0.068, 'pas', seg=20, cap=False)
    K.cyl((x, y, -0.475), (x, y, -0.48), 0.048, 'alev', seg=20)
    for a in range(6):
        ang = a * math.pi / 3
        K.box((x + math.cos(ang) * 0.063, y + math.sin(ang) * 0.063, -0.33), (0.008, 0.008, 0.12), 'koyu', 0.001)
    K.box((x, y - (0.0 if y > 0 else 0.0), -0.30), (0.12, 0.012, 0.012), 'turkuaz', 0.001) if False else None
# motorları gövdeye bağlayan dikme levhaları
for sx in (-1, 1):
    K.box((sx * 0.10, 0.0, -0.33), (0.045, 0.19, 0.12), 'gri', 0.003)
objs = K.to_blender()
print('KONSEPT poly:', sum(len(o.data.polygons) for o in objs))
K.render(out, {'on_uc_ceyrek': (1.1, -1.2, 0.65), 'arka_uc_ceyrek': (-1.1, 1.2, 0.55), 'yan': (1.8, 0.0, 0.1), 'ust': (0.0, 0.0, 2.0)}, 0.8, look=(0, 0, 0))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'model.blend'), compress=True)
