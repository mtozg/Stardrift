"""Test kutusu — Faz 0 hattı doğrulama nesnesi (gerçek oyun varlığı değil).
Hattın her yolunu sınar: çok malzemeli gövde (dielektrik + metal), pah, birbirine oturan plakalar (gizli yüz silme),
seed'e bağlı greeble, gövdeye pişirilen sabit emisyon (ön şerit), canlı emisyon (motor ağzı → MAT_emit), soketler.
Blender uzayı: +Y ileri (burun), Z yukarı."""
import bmesh
from mathutils import Vector
from core import geo
from core.seed import rng


def build(spec, mats):
    P = spec['params']
    W, L, H = P['size']
    hx, hy, hz = W / 2, L / 2, H / 2
    obs = []

    def add(name, bm, mat, role='body', bev=None, smooth=35):
        ob = geo.mesh_object(name, bm, mats[mat], role=role)
        if bev:
            geo.bevel(ob, *bev)
        geo.set_smooth_by_angle(ob, smooth)
        obs.append(ob)
        return ob

    # gövde
    add('hull', geo.bm_box((0, 0, 0), (W, L, H)), 'hull_grey', bev=(P['bevel'], 2, 35))
    # üst plakalar (vent için ortası boş)
    for s in (-1, 1):
        add('plate_top_%d' % (s > 0), geo.bm_box((0, s * 0.38, hz + 0.01), (0.46, 0.50, 0.02)), 'gunmetal', bev=(0.006, 1, 35))
    # yan plakalar
    for s in (-1, 1):
        add('plate_side_%d' % (s > 0), geo.bm_box((s * (hx + 0.01), 0.0, -0.02), (0.02, 1.10, 0.40)), 'gunmetal', bev=(0.006, 1, 35))
    # havalandırma ızgarası
    for i in range(6):
        y = -0.10 + i * 0.04
        add('vent_%d' % i, geo.bm_box((0, y, hz + 0.0125), (0.34, 0.018, 0.025)), 'steel_dark', bev=(0.003, 1, 35))
    # ön: çerçeve + sabit emisyon şeridi (gövdeye pişer)
    add('front_frame', geo.bm_box((0, hy + 0.005, 0.10), (0.70, 0.012, 0.14)), 'gunmetal', bev=(0.004, 1, 35))
    add('front_strip', geo.bm_box((0, hy + 0.013, 0.10), (0.60, 0.006, 0.05)), 'emit_cyan', role='body')
    # arka: motor çanı (kapalı profil) + canlı emisyon diski
    bell = geo.bm_lathe([(0.17, 0.0), (0.22, 0.16), (0.20, 0.165), (0.15, 0.035)], (0, -hy, 0), (0, -1, 0), segments=24)
    add('engine_bell', bell, 'steel_dark', smooth=50)
    add('engine_glow', geo.bm_disc((0, -hy - 0.035, 0), (0, -1, 0), 0.15, 24), 'emit_amber', role='emit_live')
    # seed'e bağlı yan greeble kutuları
    r = rng(spec['seed'], 'greeble')
    for s in (-1, 1):
        for i in range(P['greebles_per_side']):
            y = r.uniform(-0.42, 0.42)
            z = r.uniform(-0.12, 0.08)
            sx, sy, sz = r.uniform(0.02, 0.04), r.uniform(0.08, 0.18), r.uniform(0.05, 0.10)
            add('greeble_%d_%d' % (s > 0, i), geo.bm_box((s * (hx + 0.02 + sx / 2), y, z), (sx, sy, sz)), 'steel_dark', bev=(0.004, 1, 35))
    # borular (yan alt kenar boyunca)
    rp = rng(spec['seed'], 'pipes')
    for s in (-1, 1):
        for i in range(P['pipes']):
            z = -hz + 0.07 + i * 0.05
            x = s * (hx + 0.02)
            y0, y1 = -0.70 + rp.uniform(0, 0.08), 0.70 - rp.uniform(0, 0.08)
            add('pipe_%d_%d' % (s > 0, i), geo.bm_cylinder((x, y0, z), (x, y1, z), 0.016, 12), 'steel_dark', smooth=60)
    # anten
    ax, ay = 0.30, -0.55
    add('antenna', geo.bm_cylinder((ax, ay, hz - 0.01), (ax, ay, hz + P['antenna_h']), 0.012, 10), 'steel_dark', smooth=60)
    add('antenna_base', geo.bm_cylinder((ax, ay, hz - 0.01), (ax, ay, hz + 0.03), 0.04, 16), 'gunmetal', smooth=60)

    sockets = [
        {'name': 'SOCK_engine_0', 'loc': (0, -hy - 0.035, 0), 'dir': (0, -1, 0), 'extras': {'purpose': 'motor alevi/izi; yön = egzoz'}},
        {'name': 'SOCK_light_0', 'loc': (ax, ay, hz + P['antenna_h'] + 0.01), 'dir': (0, 0, 1), 'extras': {'purpose': 'seyir ışığı', 'color': [1.0, 0.15, 0.1], 'blink_hz': 1.0}},
    ]
    return {'objects': obs, 'sockets': sockets}
