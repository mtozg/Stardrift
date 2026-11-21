"""Şahin — dış model (sıfırdan; oyun içi görünüm yalnız tasarım referansı). Kapı 1 onaylı konsept c001 + Mehmet: ikiz motor, kanopi oyundaki Şahin kokpitine (damla fanus: ince koyu kemerler, kırmızı kenar çizgisi).
Kurulum uzayı: oyun (x yanal, y yukarı, z burun +), L=1 → ×S (metre) → Blender (g2b)."""
import math
import bpy, bmesh
from mathutils import Vector, Matrix
from core import geo
from families.ship.yuk_ext import B as _B, orient_outward

MAT = {'gri': 'sahin_hull', 'beyaz': 'sahin_white', 'mid': 'sahin_mid', 'koyu': 'sahin_dark', 'kirmizi': 'sahin_red', 'cam': 'sahin_glass',
       'lastik': 'yuk_rubber', 'celik': 'steel_dark', 'metal': 'gunmetal', 'is': 'yuk_soot', 'isik': 'emit_amber', 'cekirdek': 'emit_redhot', 'mavi': 'emit_blue',
       'kirmizi_isik': 'emit_red', 'cyan': 'emit_cyan'}


class B(_B):
    def __init__(self):
        self.bm = {k: bmesh.new() for k in MAT}

    def prism(self, pts, th, mat):
        bm = self.bm[mat]
        top = [bm.verts.new(p) for p in pts]
        bot = [bm.verts.new((p[0], p[1] - th, p[2])) for p in pts]
        bm.faces.new(top); bm.faces.new(bot[::-1])
        for i in range(len(pts)):
            j = (i + 1) % len(pts)
            bm.faces.new([top[j], top[i], bot[i], bot[j]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def fin(self, pts_yz, x, th, mat):
        bm = self.bm[mat]
        a = [bm.verts.new((x - th / 2, y, z)) for y, z in pts_yz]
        b = [bm.verts.new((x + th / 2, y, z)) for y, z in pts_yz]
        bm.faces.new(a); bm.faces.new(b[::-1])
        for i in range(len(pts_yz)):
            j = (i + 1) % len(pts_yz)
            bm.faces.new([a[j], a[i], b[i], b[j]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def poly(self, pts, r, mat, seg=6):
        for p, q in zip(pts, pts[1:]):
            self.cyl(p, q, r, mat, seg=seg)


def build(spec, mats):
    P = spec['params']
    S = P.get('scale_m', 9.0)
    k = B()
    # ---------------- gövde: sekizgen kesit, uzun sivri burun
    k.loft([(-0.30, 0.120, 0.070, 0.060, 0.025, 0.0), (-0.15, 0.170, 0.085, 0.065, 0.035, 0.0), (0.05, 0.180, 0.085, 0.062, 0.035, 0.0),
            (0.20, 0.140, 0.065, 0.050, 0.030, 0.0), (0.34, 0.072, 0.042, 0.034, 0.018, 0.0), (0.46, 0.024, 0.020, 0.018, 0.008, 0.0), (0.50, 0.008, 0.010, 0.010, 0.004, 0.0)], 'gri')
    k.loft([(-0.28, 0.090, 0.0725, 0.0705, 0.015, 0.0), (0.0, 0.104, 0.0875, 0.0845, 0.02, 0.0), (0.28, 0.040, 0.0535, 0.0505, 0.01, 0.0)], 'beyaz')          # sırt plakası
    # ---------------- damla fanus kanopi (oyundaki Şahin kokpiti gibi): geniş cam kabarcık, ince koyu kemerler, kırmızı kenar çizgisi
    sec = [(-0.02, 0.060, 0.115, 0.072, 0.022), (0.04, 0.092, 0.138, 0.074, 0.032), (0.12, 0.088, 0.136, 0.074, 0.030), (0.20, 0.050, 0.098, 0.066, 0.020)]
    k.loft([(z, w, hu, hd, ch, 0.0) for z, w, hu, hd, ch in sec], 'cam')
    for z, w, hu, hd, ch in ((0.012, 0.075, 0.1275, 0.072, 0.027), (0.08, 0.0905, 0.137, 0.074, 0.031), (0.155, 0.074, 0.1245, 0.070, 0.026)):
        a = w / 2 + 0.002
        arch = [(-a, hd + 0.01, z), (-a - 0.001, hu - ch - 0.01, z), (-(a - ch * 0.8), hu + 0.002, z), (0, hu + 0.004, z), (a - ch * 0.8, hu + 0.002, z), (a + 0.001, hu - ch - 0.01, z), (a, hd + 0.01, z)]
        k.poly(arch, 0.0035, 'koyu', 6)
    k.poly([(0.0, 0.1385, -0.01), (0.0, 0.1415, 0.09), (0.0, 0.1225, 0.2)], 0.0030, 'koyu', 6)                           # boyuna orta kemer
    for sx in (-1, 1):
        k.box((sx * 0.0485, 0.0755, 0.09), (0.006, 0.006, 0.23), 'kirmizi')                                            # kenar boyunca kırmızı şerit
        k.box((sx * 0.0515, 0.0725, 0.09), (0.004, 0.004, 0.23), 'metal')
    k.box((0, 0.0755, -0.025), (0.09, 0.008, 0.008), 'kirmizi')                                                          # arka başlık
    k.box((0, 0.068, 0.21), (0.05, 0.010, 0.010), 'koyu')                                                                # ön kemer tabanı
    # ---------------- kanatlar: geniş geri süpürmeli, sarkık uç; beyaz hücum şeridi, kırmızı uç, flap/aileron panelleri, pylon
    for sx in (-1, 1):
        def P_(*v): return [(sx * p[0], p[1], p[2]) for p in v]
        def rev(l): return l if sx > 0 else l[::-1]
        k.prism(rev(P_((0.085, -0.010, 0.10), (0.50, -0.050, -0.14), (0.50, -0.050, -0.27), (0.085, -0.010, -0.075))), 0.022, 'mid')
        k.prism(rev(P_((0.085, -0.0085, 0.10), (0.50, -0.0485, -0.14), (0.50, -0.0485, -0.17), (0.10, -0.0085, 0.045))), 0.018, 'beyaz')           # hücum kenarı
        k.prism(rev(P_((0.42, -0.0385, -0.118), (0.50, -0.0485, -0.14), (0.50, -0.0485, -0.27), (0.42, -0.0385, -0.235))), 0.018, 'kirmizi')       # uç kapağı
        k.prism(rev(P_((0.10, -0.0125, -0.045), (0.42, -0.0425, -0.20), (0.42, -0.0425, -0.235), (0.10, -0.0125, -0.075))), 0.016, 'gri')          # flap/aileron
        for t, th in ((0.33, 0.0), (0.66, 0.0)):
            x = 0.085 + t * 0.415
            k.box((sx * x, -0.0125 - t * 0.032, 0.10 - t * 0.24 - 0.085), (0.003, 0.0035, 0.12), 'koyu')
        k.box((sx * 0.30, -0.060, -0.07), (0.012, 0.022, 0.10), 'mid')                                                   # pylon
        k.cyl((sx * 0.30, -0.071, -0.12), (sx * 0.30, -0.071, -0.01), 0.010, 'celik', seg=8)                            # silah/sensör kapsülü
        k.box((sx * 0.495, -0.0545, -0.205), (0.010, 0.010, 0.012), 'kirmizi_isik' if sx > 0 else 'cyan')                 # kanat ucu lambası
        k.box((sx * 0.20, -0.012, -0.0), (0.12, 0.003, 0.012), 'koyu')                                                   # kanat kökü kapak izi
        k.box((sx * 0.14, -0.002, 0.04), (0.08, 0.012, 0.10), 'gri')                                                     # kök kaplaması
        # yatay stabilizer
        k.prism(rev(P_((0.075, 0.0, -0.30), (0.22, -0.03, -0.375), (0.22, -0.03, -0.43), (0.075, 0.0, -0.42))), 0.014, 'mid')
        k.prism(rev(P_((0.19, -0.025, -0.385), (0.22, -0.03, -0.375), (0.22, -0.03, -0.43), (0.19, -0.025, -0.425))), 0.012, 'kirmizi')
        # yan hava girişi + kapaklar + menteşe
        k.box((sx * 0.092, 0.01, -0.05), (0.014, 0.045, 0.11), 'koyu')
        for i in range(4):
            k.box((sx * 0.0935, -0.006 + i * 0.01, -0.05), (0.004, 0.004, 0.09), 'lastik')
        k.box((sx * 0.0925, 0.01, 0.07), (0.005, 0.05, 0.05), 'kirmizi')
        for q in (-0.018, 0.018):
            k.box((sx * 0.094, 0.032, 0.07 + q), (0.004, 0.006, 0.006), 'celik')
        k.box((sx * 0.0405, -0.040, 0.24), (0.008, 0.020, 0.04), 'kirmizi')
        k.box((sx * 0.060, -0.052, 0.12), (0.040, 0.012, 0.09), 'koyu')                                                  # karın servis kapağı
    # ---------------- ortada dikey kuyruk (iki motor arasında), kırmızı bant, anten bıçağı
    k.fin([(0.082, -0.26), (0.082, -0.46), (0.19, -0.49), (0.19, -0.43)], 0.0, 0.012, 'gri')
    k.fin([(0.14, -0.445), (0.19, -0.47), (0.19, -0.43)], 0.0, 0.0145, 'kirmizi')
    k.fin([(0.085, -0.34), (0.085, -0.40), (0.115, -0.405), (0.115, -0.36)], 0.0, 0.0145, 'beyaz')
    k.box((0, 0.185, -0.485), (0.016, 0.010, 0.010), 'kirmizi_isik')                                                      # kuyruk lambası
    k.cyl((0.0, 0.085, 0.01), (0.0, 0.12, 0.06), 0.0 + 0.002, 'celik', seg=5)                                            # pitot/sensör çubuğu (kanopi arkası)
    # ---------------- burun: çift top + dümen/pitot
    for sx in (-1, 1):
        k.cyl((sx * 0.016, -0.030, 0.34), (sx * 0.016, -0.030, 0.52), 0.006, 'celik', seg=8)
        k.box((sx * 0.016, -0.028, 0.34), (0.022, 0.022, 0.07), 'koyu')
        k.cyl((sx * 0.016, -0.030, 0.50), (sx * 0.016, -0.030, 0.525), 0.009, 'koyu', seg=8)
    for z, ww in ((0.30, 0.07), (0.36, 0.06)):
        k.box((0, 0.0375, z), (ww, 0.003, 0.012), 'kirmizi')
    # ---------------- ikiz motor: nacelle + kırmızı halka + çan (kaburgalı) + çekirdek + mavi göbek + is
    ENG = [(-0.058, -0.002), (0.058, -0.002)]
    r = 0.044
    for x, y in ENG:
        k.cyl((x, y, -0.27), (x, y, -0.46), r * 1.12, 'koyu', r * 1.04, seg=18)
        k.cyl((x, y, -0.44), (x, y, -0.465), r * 1.22, 'kirmizi', seg=18)
        k.cyl((x, y, -0.465), (x, y, -0.50), r * 1.06, 'metal', r * 1.14, seg=18, cap=False)
        k.cyl((x, y, -0.50), (x, y, -0.535), r * 1.14, 'is', r * 1.28, seg=18, cap=False)
        k.cyl((x, y, -0.535), (x, y, -0.545), r * 1.34, 'celik', seg=18, cap=False)
        k.cyl((x, y, -0.485), (x, y, -0.492), r * 0.84, 'cekirdek', seg=18)
        k.cyl((x, y, -0.4915), (x, y, -0.495), r * 0.40, 'mavi', seg=12)
        for a_ in range(8):
            ang = a_ * math.pi / 4
            k.box((x + math.cos(ang) * r * 1.12, y + math.sin(ang) * r * 1.12, -0.505), (0.007, 0.007, 0.075), 'celik')
        for dz in (-0.31, -0.37, -0.42):
            k.cyl((x, y, dz), (x, y, dz - 0.008), r * 1.14, 'celik', seg=18, cap=False)
        k.box((x, y + r * 1.12, -0.35), (0.016, 0.008, 0.12), 'beyaz')
    k.box((0, 0.0, -0.275), (0.10, 0.09, 0.04), 'gri')                                                                  # iki nacelle arası bağlantı bloğu
    # ---------------- gövde yan/üst kırmızı şeritler, kapaklar, panjur
    for z in (0.30, -0.06):
        for sx in (-1, 1):
            k.box((sx * 0.012, 0.0855 - (0.034 if z > 0.2 else 0), z), (0.045, 0.003, 0.012), 'kirmizi')
    for i in range(6):
        k.box((0.0, 0.0867, -0.20 + i * 0.011), (0.06, 0.004, 0.006), 'koyu')                                            # panjur (sırt)
    for z in (-0.12, -0.02):
        k.box((0.06, 0.0875, z), (0.04, 0.004, 0.05), 'mid')
        k.box((-0.06, 0.0875, z), (0.04, 0.004, 0.05), 'mid')
    # ---------------- Blender'a taşı
    objs = []
    for key, bm in k.bm.items():
        if not bm.verts:
            continue
        for v in bm.verts:
            v.co = geo.g2b(Vector(v.co) * S)
        orient_outward(bm)
        objs.append(geo.mesh_object('P_' + key, bm, mats[MAT[key]], role='body', smooth_angle=35))
    socks = []
    for i, (x, y) in enumerate(ENG, 1):
        socks.append({'name': 'ANCH_ENG_%d' % i, 'loc': tuple(geo.g2b(Vector((x, y, -0.488)) * S)), 'dir': (0.0, 1.0, 0.0), 'extras': {'kind': 'engine'}})
    for i, p in enumerate(((0.495, -0.0545, -0.205), (-0.495, -0.0545, -0.205), (0.0, 0.185, -0.485)), 1):
        socks.append({'name': 'ANCH_NAV_%d' % i, 'loc': tuple(geo.g2b(Vector(p) * S)), 'dir': (0.0, 0.0, 1.0), 'extras': {'kind': 'nav'}})
    for i, sx in enumerate((-1, 1), 1):
        socks.append({'name': 'ANCH_MUZ_%d' % i, 'loc': tuple(geo.g2b(Vector((sx * 0.016, -0.030, 0.525)) * S)), 'dir': (0.0, -1.0, 0.0), 'extras': {'kind': 'muzzle'}})
    return {'objects': objs, 'sockets': socks}
