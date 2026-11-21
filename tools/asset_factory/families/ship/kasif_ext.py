"""Kaşif — dış model (sıfırdan; oyun içi görünüm yalnız tasarım referansı). Kapı 1 onaylı konsept c001: 4 motor (2 üst + 2 alt), kalın yuvarlak gövde, camlı çok panolu burun, radar/anten.
Kurulum uzayı: oyun (x yanal, y yukarı, z burun +), L=1 → ×S (metre) → Blender (g2b)."""
import math
import bpy, bmesh
from mathutils import Vector, Matrix
from core import geo
from families.ship.sahin_ext import B as _B
from families.ship.yuk_ext import orient_outward

MAT = {'gri': 'kasif_hull', 'beyaz': 'kasif_light', 'koyu': 'sahin_dark', 'cam': 'sahin_glass', 'lastik': 'yuk_rubber', 'celik': 'steel_dark', 'metal': 'gunmetal',
       'is': 'yuk_soot', 'cyan': 'emit_cyan', 'cekirdek': 'emit_pinkhot', 'isik': 'emit_amber', 'kirmizi_isik': 'emit_red', 'pas': 'yuk_cont_rust'}


class B(_B):
    def __init__(self):
        self.bm = {k: bmesh.new() for k in MAT}


def build(spec, mats):
    S = spec['params'].get('scale_m', 14.0)
    k = B()
    # ---------------- gövde: kalın, yuvarlak (sekizgen) kesit
    k.loft([(-0.40, 0.200, 0.125, 0.125, 0.06, 0.0), (-0.25, 0.280, 0.135, 0.140, 0.08, 0.0), (0.0, 0.310, 0.140, 0.145, 0.09, 0.0),
            (0.20, 0.280, 0.125, 0.130, 0.08, 0.0), (0.34, 0.210, 0.100, 0.105, 0.06, 0.0), (0.45, 0.120, 0.068, 0.075, 0.04, 0.0), (0.505, 0.040, 0.030, 0.035, 0.02, 0.0)], 'gri')
    k.loft([(-0.30, 0.200, 0.1385, 0.1345, 0.03, 0.0), (0.0, 0.220, 0.1435, 0.1395, 0.03, 0.0), (0.22, 0.180, 0.1285, 0.1245, 0.03, 0.0)], 'beyaz')      # üst plaka
    k.loft([(-0.30, 0.200, -0.1275, -0.1235, 0.03, 0.0), (0.2, 0.19, -0.1325, -0.1285, 0.03, 0.0)], 'beyaz')                                         # alt plaka
    # ---------------- camlı burun: 3 pano üstte + yan pencereler, çerçeve/dikme
    k.loft([(0.30, 0.134, 0.133, 0.058, 0.03, 0.0), (0.37, 0.128, 0.118, 0.050, 0.03, 0.0), (0.44, 0.092, 0.092, 0.046, 0.025, 0.0), (0.49, 0.040, 0.048, 0.024, 0.012, 0.0)], 'cam')
    for z in (0.305, 0.345, 0.385, 0.425, 0.465):
        w = 0.134 - (z - 0.30) * 0.48
        hu = 0.133 - (z - 0.30) * 0.22
        k.poly([(-w / 2 - 0.002, 0.062, z), (-w / 2 - 0.002, hu - 0.02, z), (-w / 2 + 0.02, hu + 0.003, z), (w / 2 - 0.02, hu + 0.003, z), (w / 2 + 0.002, hu - 0.02, z), (w / 2 + 0.002, 0.062, z)], 0.004, 'celik', 6)
    k.box((0, 0.121, 0.40), (0.006, 0.004, 0.19), 'celik')
    k.poly([(-0.05, 0.058, 0.30), (-0.052, 0.058, 0.47)], 0.004, 'celik', 6); k.poly([(0.05, 0.058, 0.30), (0.052, 0.058, 0.47)], 0.004, 'celik', 6)
    # ---------------- üst güverte: radar tabağı + anten, taret kubbesi, kapaklar, panjurlar
    k.cyl((0, 0.14, -0.06), (0, 0.17, -0.06), 0.018, 'koyu', seg=12)
    k.cyl((0, 0.17, -0.06), (0.03, 0.215, -0.06), 0.008, 'koyu', seg=8)
    k.cyl((0.03, 0.215, -0.06), (0.034, 0.222, -0.06), 0.040, 'beyaz', 0.002, seg=16)
    k.cyl((-0.05, 0.14, -0.12), (-0.05, 0.23, -0.12), 0.003, 'koyu', seg=6)
    k.box((-0.05, 0.232, -0.12), (0.010, 0.010, 0.010), 'kirmizi_isik')
    k.cyl((0, 0.14, 0.06), (0, 0.155, 0.06), 0.040, 'koyu', seg=20)
    k.cyl((0, 0.155, 0.06), (0, 0.168, 0.06), 0.028, 'beyaz', 0.02, seg=20)
    for z in (-0.20, -0.10, 0.12):
        k.box((0.0 if z != 0.12 else 0.07, 0.1415, z), (0.07, 0.008, 0.06), 'koyu')
    for i in range(6):
        k.box((-0.07, 0.1445, -0.30 + i * 0.012), (0.07, 0.005, 0.006), 'koyu')
    for sx in (-1, 1):
        k.box((sx * 0.10, 0.141, -0.17), (0.05, 0.006, 0.12), 'metal')
    # ---------------- yan paneller: turkuaz ışık şeritleri, kapaklar, menteşe, hava girişleri
    for sx in (-1, 1):
        k.box((sx * 0.1585, 0.02, -0.10), (0.004, 0.005, 0.40), 'cyan')
        k.box((sx * 0.1585, -0.04, 0.15), (0.004, 0.005, 0.20), 'cyan')
        for z in (0.04, 0.24, -0.32):
            k.box((sx * 0.157, 0.0, z), (0.006, 0.20, 0.006), 'koyu')
        for z in (-0.18, -0.02, 0.14):
            k.box((sx * 0.1575, 0.02, z), (0.006, 0.07, 0.10), 'beyaz')
            for q in (-0.04, 0.04):
                k.box((sx * 0.1605, 0.045, z + q), (0.004, 0.008, 0.008), 'celik')
        k.box((sx * 0.157, -0.03, 0.0), (0.006, 0.05, 0.14), 'koyu')
        for i in range(5):
            k.box((sx * 0.1585, -0.045 + i * 0.01, 0.0), (0.004, 0.004, 0.12), 'lastik')
        k.box((sx * 0.140, 0.02, 0.31), (0.005, 0.03, 0.05), 'metal')
    # ---------------- kanatlar: kısa, geri süpürmeli, hafif yukarı eğimli (kaynak ön görünümde uçlar yukarı); beyaz hücum şeridi
    for sx in (-1, 1):
        def P_(*v): return [(sx * p[0], p[1], p[2]) for p in v]
        def rev(l): return l if sx > 0 else l[::-1]
        k.prism(rev(P_((0.15, -0.02, 0.09), (0.50, 0.03, -0.12), (0.50, 0.03, -0.27), (0.15, -0.02, -0.12))), 0.024, 'gri')
        k.prism(rev(P_((0.15, -0.0185, 0.09), (0.50, 0.0315, -0.12), (0.50, 0.0315, -0.15), (0.17, -0.0185, 0.03))), 0.020, 'beyaz')
        k.prism(rev(P_((0.17, -0.020, -0.07), (0.48, 0.028, -0.20), (0.48, 0.028, -0.26), (0.17, -0.020, -0.115))), 0.016, 'metal')       # flap izi
        for t in (0.4, 0.7):
            k.box((sx * (0.15 + 0.35 * t), -0.02 + 0.05 * t, 0.09 - 0.21 * t - 0.08), (0.003, 0.003, 0.14), 'koyu')
        k.box((sx * 0.50, 0.03, -0.20), (0.012, 0.030, 0.14), 'koyu')
        k.box((sx * 0.49, 0.027, -0.12), (0.010, 0.010, 0.012), 'kirmizi_isik' if sx > 0 else 'cyan')
        k.box((sx * 0.20, -0.055, 0.03), (0.10, 0.04, 0.18), 'koyu')            # kanat kökü havalandırma/boru
        k.cyl((sx * 0.17, -0.07, 0.02), (sx * 0.17, -0.07, 0.15), 0.014, 'celik', seg=8)
    # ---------------- 4 motor kovanı (2×2): kaynak çizim gibi yuvarlak, beyaz spinnerlı
    ENG = [(sx * 0.125, y) for sx in (-1, 1) for y in (0.10, -0.09)]
    r = 0.060
    for x, y in ENG:
        k.cyl((x, y, -0.26), (x, y, -0.46), r * 1.03, 'gri', r, seg=20)
        k.cyl((x, y, -0.20), (x, y, -0.26), r * 0.93, 'beyaz', r * 1.03, seg=20)
        k.cyl((x, y, -0.15), (x, y, -0.20), r * 0.50, 'beyaz', r * 0.93, seg=20)
        k.cyl((x, y, -0.40), (x, y, -0.43), r * 1.10, 'koyu', seg=20)
        k.cyl((x, y, -0.46), (x, y, -0.50), r * 0.95, 'metal', r * 1.05, seg=20, cap=False)
        k.cyl((x, y, -0.50), (x, y, -0.535), r * 1.05, 'is', r * 1.12, seg=20, cap=False)
        k.cyl((x, y, -0.535), (x, y, -0.545), r * 1.14, 'celik', seg=20, cap=False)
        k.cyl((x, y, -0.482), (x, y, -0.488), r * 0.82, 'cekirdek', seg=20)
        for a in range(8):
            ang = a * math.pi / 4
            k.box((x + math.cos(ang) * r * 1.0, y + math.sin(ang) * r * 1.0, -0.505), (0.008, 0.008, 0.080), 'celik')
            k.box((x + math.cos(ang) * r * 1.05, y + math.sin(ang) * r * 1.05, -0.33), (0.010, 0.010, 0.13), 'koyu')
        for dz in (-0.30, -0.36):
            k.cyl((x, y, dz), (x, y, dz - 0.008), r * 1.05, 'celik', seg=20, cap=False)
    for sx in (-1, 1):
        k.box((sx * 0.10, 0.0, -0.33), (0.045, 0.19, 0.12), 'gri')
    k.box((0, 0.0, -0.45), (0.10, 0.12, 0.10), 'koyu')                                         # arka orta kapak (kaynak arka görünümdeki merkez panel)
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
    for i, p in enumerate(((0.49, 0.027, -0.12), (-0.49, 0.027, -0.12), (-0.05, 0.232, -0.12)), 1):
        socks.append({'name': 'ANCH_NAV_%d' % i, 'loc': tuple(geo.g2b(Vector(p) * S)), 'dir': (0.0, 0.0, 1.0), 'extras': {'kind': 'nav'}})
    socks.append({'name': 'ANCH_MUZ_1', 'loc': tuple(geo.g2b(Vector((0.0, 0.168, 0.06)) * S)), 'dir': (0.0, -1.0, 0.0), 'extras': {'kind': 'muzzle'}})
    return {'objects': objs, 'sockets': socks}
