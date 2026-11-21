"""Şahin — sıfırdan modelleme (konsept c001): açık gri/beyaz av uçağı, kırmızı şeritler, geniş geri süpürmeli sarkık kanatlar, tek büyük motor, balon kanopi.
Oyun uzayı: burun +Z, yukarı +Y, uzunluk 1,0. Kullanım: python pipeline/ship_sahin.py <çıktı_klasörü>"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy, bmesh
from core.shipkit import Kit

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
PAL = {
    'gri': ((0.30, 0.32, 0.35), 0.5, 0.45, None), 'beyaz': ((0.62, 0.63, 0.64), 0.5, 0.35, None),
    'koyu': ((0.07, 0.075, 0.09), 0.55, 0.5, None), 'kirmizi': ((0.36, 0.05, 0.05), 0.55, 0.3, None),
    'cam': ((0.06, 0.16, 0.30), 0.08, 0.0, (0.25, 0.55, 1.0, 0.7)), 'alev': ((1, .35, .2), 0.5, 0, (1.0, 0.32, 0.18, 6.0)),
    'mavi': ((0.4, 0.7, 1.0), 0.5, 0, (0.3, 0.65, 1.0, 5.0)), 'bell': ((0.03, 0.03, 0.035), 0.5, 0.75, None),
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


# gövde: arka motor bloğu → geniş orta → uzun sivri burun
K.loft([(-0.30, 0.060, 0.050, 0.070, -0.060, 0), (-0.15, 0.085, 0.070, 0.085, -0.065, 0), (0.05, 0.090, 0.070, 0.085, -0.062, 0),
        (0.20, 0.070, 0.048, 0.065, -0.050, 0), (0.34, 0.036, 0.024, 0.042, -0.034, 0), (0.46, 0.012, 0.008, 0.020, -0.018, 0), (0.50, 0.004, 0.004, 0.010, -0.010, 0)], 'gri')
K.loft([(-0.28, 0.045, 0.045, 0.0715, 0.068, 0), (0.0, 0.052, 0.052, 0.0865, 0.082, 0), (0.28, 0.020, 0.020, 0.052, 0.049, 0)], 'beyaz')      # üst omurga plakası
# balon kanopi + çerçeve
K.loft([(-0.02, 0.016, 0.040, 0.118, 0.072, 0), (0.04, 0.034, 0.046, 0.138, 0.076, 0), (0.12, 0.032, 0.044, 0.136, 0.074, 0), (0.20, 0.014, 0.030, 0.098, 0.066, 0)], 'cam')
# kanatlar: geniş geri süpürmeli, sarkık uç; beyaz hücum kenarı, kırmızı uç kapağı, panel şeritleri
for sx in (-1, 1):
    LE0, LE1, TE1, TE0 = (0.085, -0.010, 0.10), (0.50, -0.050, -0.14), (0.50, -0.050, -0.27), (0.085, -0.010, -0.075)
    def P(*v): return [(sx * p[0], p[1], p[2]) for p in v]
    wing = P(LE0, LE1, TE1, TE0)
    prism(wing if sx > 0 else wing[::-1], 0.022, 'gri')
    # beyaz hücum kenarı şeridi
    prism(P((0.085, -0.0085, 0.10), (0.50, -0.0485, -0.14), (0.50, -0.0485, -0.17), (0.10, -0.0085, 0.045)) if sx > 0 else P((0.10, -0.0085, 0.045), (0.50, -0.0485, -0.17), (0.50, -0.0485, -0.14), (0.085, -0.0085, 0.10)), 0.018, 'beyaz')
    # kırmızı uç kapağı
    prism(P((0.42, -0.0385, -0.118), (0.50, -0.0485, -0.14), (0.50, -0.0485, -0.27), (0.42, -0.0385, -0.235)) if sx > 0 else P((0.42, -0.0385, -0.235), (0.50, -0.0485, -0.27), (0.50, -0.0485, -0.14), (0.42, -0.0385, -0.118)), 0.018, 'kirmizi')
    # iç panel şeritleri (koyu çizgi) ve flaplar
    for t in (0.35, 0.60):
        x = 0.085 + t * 0.415
        zle = 0.10 - t * 0.24
        K.box((sx * x, -0.0085 - t * 0.0415, zle - 0.075), (0.003, 0.003, 0.10), 'koyu', 0.0005)
    # kuyruk yatay stabilizer
    prism(P((0.075, 0.0, -0.30), (0.22, -0.03, -0.375), (0.22, -0.03, -0.43), (0.075, 0.0, -0.42)) if sx > 0 else P((0.075, 0.0, -0.42), (0.22, -0.03, -0.43), (0.22, -0.03, -0.375), (0.075, 0.0, -0.30)), 0.014, 'gri')
    prism(P((0.19, -0.025, -0.385), (0.22, -0.03, -0.375), (0.22, -0.03, -0.43), (0.19, -0.025, -0.425)) if sx > 0 else P((0.19, -0.025, -0.425), (0.22, -0.03, -0.43), (0.22, -0.03, -0.375), (0.19, -0.025, -0.385)), 0.012, 'kirmizi')
    # yan hava girişi + panel
    K.box((sx * 0.086, 0.01, -0.05), (0.012, 0.045, 0.11), 'koyu', 0.002)
    K.box((sx * 0.0905, 0.01, 0.07), (0.004, 0.05, 0.05), 'kirmizi', 0.001)
# dikey kuyruk: büyük geri süpürmeli
fin([(0.075, -0.28), (0.075, -0.46), (0.19, -0.49), (0.19, -0.43)], 0.0, 0.012, 'gri')
fin([(0.15, -0.44), (0.19, -0.465), (0.19, -0.43)], 0.0, 0.0145, 'kirmizi')
# burun altı çift top namlusu
for sx in (-1, 1):
    K.cyl((sx * 0.016, -0.030, 0.34), (sx * 0.016, -0.030, 0.52), 0.006, 'koyu', seg=8)
    K.box((sx * 0.016, -0.028, 0.34), (0.022, 0.022, 0.07), 'koyu', 0.002)
# kırmızı şeritler (gövde yan)
for z in (0.30, 0.36, -0.06):
    K.box((0, 0.0875 - (0.02 if z > 0.2 else 0), z), (0.07 if z > 0.1 else 0.11, 0.003, 0.012), 'kirmizi', 0.001)
# tek büyük motor: nacelle + kırmızı halka + çan + alev/mavi çekirdek
K.cyl((0, 0.0, -0.30), (0, 0.0, -0.46), 0.068, 'koyu', 0.064, seg=24)
K.cyl((0, 0.0, -0.45), (0, 0.0, -0.475), 0.074, 'kirmizi', seg=24)
K.cyl((0, 0.0, -0.475), (0, 0.0, -0.53), 0.060, 'bell', 0.082, seg=24, cap=False)
K.cyl((0, 0.0, -0.53), (0, 0.0, -0.54), 0.086, 'beyaz', seg=24, cap=False)
K.cyl((0, 0.0, -0.49), (0, 0.0, -0.495), 0.056, 'alev', seg=24)
K.cyl((0, 0.0, -0.4905), (0, 0.0, -0.4915), 0.028, 'mavi', seg=16)
for k in range(8):
    a = k * math.pi / 4
    K.box((math.cos(a) * 0.075, math.sin(a) * 0.075, -0.36), (0.01, 0.01, 0.07), 'gri', 0.001)
objs = K.to_blender()
print('KONSEPT poly:', sum(len(o.data.polygons) for o in objs))
K.render(out, {'on_uc_ceyrek': (1.0, -1.15, 0.6), 'arka_uc_ceyrek': (-1.0, 1.1, 0.5), 'yan': (1.7, 0.0, 0.1), 'ust': (0.0, 0.0, 2.0)}, 0.8, look=(0, 0, 0))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'model.blend'), compress=True)
