"""Hayalet — dış model (sıfırdan; oyun içi görünüm yalnız tasarım referansı). Kapı 1: ikiz motor, cam yönü konsepttekiyle.
Kurulum uzayı: oyun (x yanal, y yukarı, z burun +), L=1 → ×S (metre) → Blender (g2b). İnce, alçak, yüzeyli gizli av uçağı; yarı-delta kanatlar, mor ışık çizgileri."""
import math
import bpy, bmesh
from mathutils import Vector, Matrix
from core import geo
from families.ship.sahin_ext import B as _B
from families.ship.yuk_ext import orient_outward

MAT = {'gri': 'hayalet_hull', 'panel': 'hayalet_panel', 'koyu': 'hay_dark', 'cam': 'hayalet_glass', 'mor': 'emit_violet2', 'celik': 'steel_dark', 'metal': 'gunmetal',
       'lastik': 'yuk_rubber', 'is': 'yuk_soot', 'cekirdek': 'emit_violet', 'isik': 'emit_amber', 'kirmizi_isik': 'emit_red'}


class B(_B):
    def __init__(self):
        self.bm = {k: bmesh.new() for k in MAT}


def build(spec, mats):
    S = spec['params'].get('scale_m', 6.0)
    k = B()
    # ---------------- gövde: uzun, ince, yüzeyli (sekizgen kesit; üst düz, omuz pahlı)
    k.loft([(-0.46, 0.120, 0.040, 0.030, 0.018, 0.0), (-0.30, 0.160, 0.050, 0.038, 0.024, 0.0), (-0.05, 0.176, 0.056, 0.040, 0.028, 0.0),
            (0.15, 0.156, 0.052, 0.036, 0.026, 0.0), (0.30, 0.100, 0.040, 0.028, 0.020, 0.0), (0.43, 0.044, 0.024, 0.016, 0.012, 0.0), (0.50, 0.012, 0.010, 0.006, 0.004, 0.0)], 'gri')
    k.loft([(-0.40, 0.080, 0.0425, 0.0405, 0.012, 0.0), (0.10, 0.090, 0.0575, 0.0555, 0.014, 0.0), (0.28, 0.060, 0.043, 0.041, 0.012, 0.0)], 'panel')          # sırt plakası
    # ---------------- kokpit camı: yüzeyli (faceted) mor tonlu iki pano + çerçeve
    k.loft([(0.17, 0.060, 0.064, 0.050, 0.014, 0.0), (0.24, 0.074, 0.074, 0.050, 0.018, 0.0), (0.33, 0.052, 0.062, 0.046, 0.014, 0.0), (0.38, 0.028, 0.050, 0.040, 0.010, 0.0)], 'cam')
    for z, w in ((0.175, 0.062), (0.245, 0.076), (0.325, 0.054)):
        k.poly([(-w / 2 - 0.002, 0.050, z), (-w / 2 - 0.002, 0.060, z), (-w / 2 + 0.014, 0.0765, z), (w / 2 - 0.014, 0.0765, z), (w / 2 + 0.002, 0.060, z), (w / 2 + 0.002, 0.050, z)], 0.0032, 'celik', 6)
    k.box((0, 0.077, 0.28), (0.004, 0.003, 0.20), 'celik')
    # ---------------- kanatlar: yarı-delta, alçak; mor kenar şeridi, panel bölmeleri, flap, uç fin
    for sx in (-1, 1):
        def P_(*v): return [(sx * p[0], p[1], p[2]) for p in v]
        def rev(l): return l if sx > 0 else l[::-1]
        k.prism(rev(P_((0.07, -0.012, 0.07), (0.31, -0.020, -0.22), (0.31, -0.020, -0.34), (0.10, -0.012, -0.21), (0.07, -0.012, -0.15))), 0.020, 'gri')
        k.prism(rev(P_((0.075, -0.0105, 0.062), (0.305, -0.0185, -0.215), (0.300, -0.0185, -0.205), (0.072, -0.0105, 0.07))), 0.012, 'mor')
        k.prism(rev(P_((0.12, -0.010, -0.02), (0.27, -0.017, -0.23), (0.26, -0.017, -0.25), (0.11, -0.010, -0.07))), 0.012, 'panel')
        k.prism(rev(P_((0.11, -0.012, -0.19), (0.30, -0.019, -0.31), (0.30, -0.019, -0.34), (0.10, -0.012, -0.21))), 0.014, 'koyu')                 # flap
        for t in (0.35, 0.65):
            k.box((sx * (0.07 + 0.24 * t), -0.0145 - 0.008 * t, 0.07 - 0.29 * t - 0.06), (0.003, 0.0025, 0.12), 'koyu')
        k.box((sx * 0.31, -0.012, -0.28), (0.012, 0.032, 0.12), 'gri')                                                                              # uç fin
        k.box((sx * 0.31, -0.012, -0.34), (0.012, 0.014, 0.012), 'mor')
        k.box((sx * 0.083, 0.012, -0.08), (0.004, 0.005, 0.24), 'mor')                                                                              # gövde yanı mor çizgi
        k.box((sx * 0.060, 0.030, 0.22), (0.004, 0.005, 0.18), 'mor')
        k.box((sx * 0.082, 0.016, 0.06), (0.012, 0.020, 0.07), 'koyu')                                                                              # yan hava girişi
        for i in range(3):
            k.box((sx * 0.0835, 0.008 + i * 0.008, 0.06), (0.003, 0.003, 0.055), 'lastik')
        k.box((sx * 0.060, 0.052, -0.17), (0.020, 0.004, 0.05), 'koyu')                                                                             # üst kapak
        k.box((sx * 0.060, 0.052, -0.28), (0.022, 0.004, 0.06), 'panel')
    # ---------------- dikey kuyruk (küçük, geriye süpürmeli) + arka stabilizer + anten
    k.fin([(0.050, -0.20), (0.050, -0.36), (0.092, -0.375), (0.092, -0.335)], 0.0, 0.008, 'gri')
    k.fin([(0.083, -0.335), (0.092, -0.34), (0.092, -0.375), (0.082, -0.37)], 0.0, 0.0105, 'mor')
    k.box((0, 0.094, -0.378), (0.012, 0.008, 0.008), 'kirmizi_isik')
    # ---------------- ikiz motor kovanı (gövde arkası, yanda): nacelle + çan (kaburgalı) + mor-beyaz çekirdek + is
    ENG = [(-0.045, 0.0), (0.045, 0.0)]
    r = 0.030
    for x, y in ENG:
        k.cyl((x, y, -0.40), (x, y, -0.485), r * 1.10, 'koyu', r * 1.04, seg=16)
        k.cyl((x, y, -0.48), (x, y, -0.495), r * 1.16, 'metal', seg=16, cap=False)
        k.cyl((x, y, -0.495), (x, y, -0.520), r * 1.04, 'celik', r * 1.14, seg=16, cap=False)
        k.cyl((x, y, -0.520), (x, y, -0.545), r * 1.14, 'is', r * 1.26, seg=16, cap=False)
        k.cyl((x, y, -0.545), (x, y, -0.552), r * 1.34, 'celik', seg=16, cap=False)
        k.cyl((x, y, -0.510), (x, y, -0.516), r * 0.80, 'cekirdek', seg=16)
        for a_ in range(6):
            ang = a_ * math.pi / 3
            k.box((x + math.cos(ang) * r * 1.12, y + math.sin(ang) * r * 1.12, -0.52), (0.006, 0.006, 0.060), 'metal')
        k.cyl((x, y, -0.44), (x, y, -0.452), r * 1.22, 'panel', seg=16, cap=False)
    k.box((0, 0.0, -0.40), (0.10, 0.045, 0.06), 'gri')                                                                                               # nacelle bağlantı bloğu
    # ---------------- gövde yüzey ayrıntıları: panjur, kapaklar, gravür çizgileri, pitot
    for z in (-0.28, -0.12, 0.02, 0.14):
        k.box((0, 0.0555, z), (0.11, 0.0025, 0.003), 'koyu')
    for i in range(6):
        k.box((0.0, 0.0575, -0.23 + i * 0.008), (0.05, 0.003, 0.004), 'koyu')
    k.box((0.04, 0.0585, -0.07), (0.05, 0.003, 0.07), 'panel')
    k.box((-0.04, 0.0585, -0.07), (0.05, 0.003, 0.07), 'panel')
    k.cyl((0.0, 0.0, 0.50), (0.0, 0.0, 0.545), 0.0035, 'celik', seg=6)                                                                                 # pitot
    for sx in (-1, 1):
        k.box((sx * 0.012, 0.0, 0.40), (0.004, 0.004, 0.08), 'mor')
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
        socks.append({'name': 'ANCH_ENG_%d' % i, 'loc': tuple(geo.g2b(Vector((x, y, -0.512)) * S)), 'dir': (0.0, 1.0, 0.0), 'extras': {'kind': 'engine'}})
    for i, p in enumerate(((0.31, -0.012, -0.34), (-0.31, -0.012, -0.34), (0.0, 0.094, -0.378)), 1):
        socks.append({'name': 'ANCH_NAV_%d' % i, 'loc': tuple(geo.g2b(Vector(p) * S)), 'dir': (0.0, 0.0, 1.0), 'extras': {'kind': 'nav'}})
    socks.append({'name': 'ANCH_MUZ_1', 'loc': tuple(geo.g2b(Vector((0.0, 0.0, 0.545)) * S)), 'dir': (0.0, -1.0, 0.0), 'extras': {'kind': 'muzzle'}})
    return {'objects': objs, 'sockets': socks}
