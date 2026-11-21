"""Yük Devi — dış model (sıfırdan; oyun içi görünüm yalnız tasarım referansı). Kapı 1 onaylı konsept c001 + gerçekçilik turu.
Kurulum uzayı: oyun (x yanal, y yukarı, z burun +), birim L=1; çıktıda ×S (metre) ve Blender uzayına (g2b). Burun kutumsu kalır (kokpit tasarımı)."""
import math
import bpy, bmesh
from mathutils import Vector, Matrix
from core import geo

MAT = {'boya': 'yuk_paint', 'turuncu': 'yuk_orange', 'metal': 'yuk_steel', 'koyu': 'yuk_dark', 'siyah': 'yuk_black', 'lastik': 'yuk_rubber',
       'cam': 'yuk_glass_ext', 'kirmizi': 'yuk_cont_red', 'mavi': 'yuk_cont_blue', 'konturuncu': 'yuk_cont_orange', 'pas': 'yuk_cont_rust',
       'sari': 'yuk_hazard', 'is': 'yuk_soot', 'soluk': 'yuk_pale', 'isik': 'emit_amber', 'cekirdek': 'emit_amber', 'celik': 'yuk_bare'}


class B:
    def __init__(self):
        self.bm = {k: bmesh.new() for k in MAT}

    def box(self, c, s, mat, bev=0.0, rx=0.0, ry=0.0):
        bm = self.bm[mat]
        r = bmesh.ops.create_cube(bm, size=1.0)
        M = Matrix.Translation(Vector(c)) @ Matrix.Rotation(ry, 4, 'Y') @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Diagonal((*s, 1.0))
        bmesh.ops.transform(bm, matrix=M, verts=r['verts'])
        if bev > 0:
            bmesh.ops.bevel(bm, geom=list({e for v in r['verts'] for e in v.link_edges}), offset=bev, segments=1, affect='EDGES')

    def loft(self, secs, mat):
        bm = self.bm[mat]
        rings = []
        for z, w, hu, hd, ch, y0 in secs:
            a = w / 2
            pts = [(a - ch, hu), (a, hu - ch), (a, -hd + ch), (a - ch, -hd), (-a + ch, -hd), (-a, -hd + ch), (-a, hu - ch), (-a + ch, hu)]
            rings.append([bm.verts.new((x, y0 + y, z)) for x, y in pts])
        for r0, r1 in zip(rings, rings[1:]):
            for i in range(8):
                j = (i + 1) % 8
                bm.faces.new([r0[i], r0[j], r1[j], r1[i]])
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def tbox(self, c, w0, w1, h0, h1, z0, z1, mat):
        bm = self.bm[mat]
        vs = []
        for z, w, h in ((z0, w0, h0), (z1, w1, h1)):
            for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                vs.append(bm.verts.new((c[0] + sx * w / 2, c[1] + sy * h / 2, z)))
        for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
            bm.faces.new([vs[i] for i in f])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def cyl(self, p0, p1, r0, mat, r1=None, seg=12, cap=True):
        bm = self.bm[mat]
        d = Vector(p1) - Vector(p0)
        M = Matrix.Translation((Vector(p0) + Vector(p1)) / 2) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=seg, radius1=r0, radius2=r0 if r1 is None else r1, depth=d.length, matrix=M)


def build(spec, mats):
    P = spec['params']
    S = P.get('scale_m', 12.0)
    k = B()
    HW = 0.185
    # ---------------- gövde (sekizgen kesit; kutumsu burun kabini korunur)
    k.loft([(-0.36, 0.37, 0.13, 0.10, 0.05, 0.0), (0.30, 0.37, 0.13, 0.10, 0.05, 0.0)], 'boya')
    k.loft([(-0.405, 0.40, 0.145, 0.125, 0.05, 0.0), (-0.355, 0.40, 0.145, 0.125, 0.05, 0.0)], 'metal')
    k.loft([(-0.50, 0.39, 0.13, 0.11, 0.05, 0.0), (-0.40, 0.395, 0.135, 0.115, 0.05, 0.0)], 'boya')
    k.loft([(0.30, 0.37, 0.125, 0.10, 0.05, 0.0), (0.42, 0.33, 0.115, 0.09, 0.05, 0.0), (0.50, 0.24, 0.085, 0.07, 0.04, 0.0)], 'boya')
    k.loft([(0.50, 0.24, 0.07, 0.06, 0.03, 0.0), (0.52, 0.19, 0.05, 0.04, 0.02, 0.0)], 'metal')
    # ---------------- kokpit camı: büyük şerit pencereler (yanlarda 3 geniş pano + üstte ön cam), lastik conta + çelik dikmeler
    for sx in (-1, 1):
        for i, z in enumerate((0.335, 0.395, 0.455)):
            xs = 0.188 - (z - 0.30) * 0.30 if z < 0.5 else 0.12
            k.box((sx * (xs + 0.0015), 0.055, z), (0.006, 0.062, 0.050), 'cam')
            k.box((sx * (xs + 0.0035), 0.055, z), (0.004, 0.072, 0.060), 'lastik')        # conta çerçevesi (cam üstünde ince çıkıntı kenarı)
            k.box((sx * (xs + 0.0030), 0.055, z + 0.0305), (0.006, 0.075, 0.008), 'celik')    # dikme
    k.box((0, 0.012, 0.5225), (0.150, 0.052, 0.004), 'cam')              # ön cephe geniş cam
    k.box((0, 0.012, 0.5215), (0.168, 0.066, 0.004), 'lastik')
    for x in (-0.05, 0.0, 0.05):
        k.box((x, 0.012, 0.5260), (0.006, 0.060, 0.004), 'celik')
    k.box((0, 0.043, 0.5260), (0.168, 0.006, 0.004), 'celik')
    k.box((0, 0.1205, 0.415), (0.200, 0.006, 0.100), 'cam')
    k.box((0, 0.1195, 0.415), (0.215, 0.004, 0.115), 'lastik')
    for z in (0.36, 0.415, 0.47):
        k.box((0, 0.1245, z), (0.215, 0.007, 0.007), 'celik')
    for x in (-0.07, 0.0, 0.07):
        k.box((x, 0.1245, 0.415), (0.007, 0.007, 0.115), 'celik')
    # ---------------- alt zırh paneli + uyarı şeridi (daha okunur: gövde altı ayrıntısı)
    k.tbox((0, -0.115), 0.30, 0.30, 0.02, 0.02, -0.30, 0.22, 'turuncu')
    for i in range(7):
        k.box((0, -0.127, -0.28 + i * 0.075), (0.30, 0.004, 0.012), 'koyu')
    for sx in (-1, 1):
        k.box((sx * 0.10, -0.123, -0.05), (0.05, 0.008, 0.18), 'metal', 0.001)       # alt hava/servis kapakları
        k.box((sx * 0.06, -0.123, 0.15), (0.06, 0.008, 0.06), 'koyu')
        for z in (-0.02, 0.0, 0.02):
            k.box((sx * 0.10, -0.1285, z - 0.05), (0.04, 0.003, 0.004), 'siyah')
    # ---------------- yan kargo koyları: raf, direkler, bağlama kayışları, farklı ve yıpranmış konteynerler
    cols = {1: ('kirmizi', 'mavi', 'konturuncu'), -1: ('pas', 'konturuncu', 'mavi')}
    sizes = ((0.13, 0.058), (0.13, 0.066), (0.13, 0.052))
    for sx in (-1, 1):
        k.box((sx * 0.155, 0.125, -0.02), (0.078, 0.018, 0.48), 'koyu')
        for i, col in enumerate(cols[sx]):
            z = -0.20 + i * 0.145
            lz, hy = sizes[i]
            k.box((sx * 0.155, 0.134 + hy / 2, z), (0.070, hy, lz), col)
            for r in (-1, 0, 1):
                k.box((sx * 0.155, 0.134 + hy / 2, z + r * 0.040), (0.0725, hy + 0.001, 0.005), 'koyu')       # oluk kaburga
            k.box((sx * 0.155, 0.134 + hy + 0.001, z + (0.04 if i % 2 else -0.04)), (0.074, 0.003, 0.014), 'lastik')      # bağlama kayışı
            k.box((sx * 0.155, 0.134 + hy / 2, z + (0.04 if i % 2 else -0.04)), (0.074, hy + 0.004, 0.012), 'lastik')
            k.box((sx * 0.19, 0.134 + hy / 2, z + 0.055), (0.004, 0.025, 0.010), 'soluk')                       # kimlik plakası (kapak köşesi)
        for z in (-0.275, -0.125, 0.025, 0.175):
            k.box((sx * 0.155, 0.19, z), (0.007, 0.075, 0.007), 'metal')
            k.box((sx * 0.195, 0.145, z), (0.020, 0.052, 0.012), 'metal')
        k.cyl((sx * 0.195, 0.205, -0.275), (sx * 0.195, 0.205, 0.175), 0.004, 'metal', seg=6)             # korkuluk üst borusu
    # ---------------- üst orta güverte: turret, havalandırma panjuru, kapaklar, boru, anten, lambalar
    k.box((0, 0.135, -0.07), (0.20, 0.012, 0.40), 'boya')
    k.cyl((0, 0.14, 0.10), (0, 0.17, 0.10), 0.055, 'metal', seg=20)
    k.cyl((0, 0.17, 0.10), (0, 0.185, 0.10), 0.040, 'koyu', seg=20)
    k.cyl((0, 0.185, 0.10), (0, 0.215, 0.10), 0.014, 'turuncu', seg=10)
    k.cyl((0.0, 0.2, 0.10), (0.0, 0.205, 0.17), 0.006, 'siyah', seg=8)                                          # taret namlusu
    for i in range(8):
        k.box((-0.045, 0.1445 + (i % 2) * 0.0005, -0.27 + i * 0.012), (0.065, 0.006, 0.006), 'koyu')            # panjur
    for z in (-0.18, -0.06, 0.04):
        k.box((0.0, 0.142, z), (0.07, 0.010, 0.045), 'metal', 0.001)
        k.box((0.045, 0.146, z), (0.020, 0.010, 0.020), 'sari')
        k.box((-0.03, 0.1475, z), (0.012, 0.004, 0.012), 'siyah')
    for sx in (-1, 1):
        k.cyl((sx * 0.075, 0.147, -0.27), (sx * 0.075, 0.147, 0.13), 0.011, 'metal', seg=8)                     # üst boru
        for z in (-0.25, -0.1, 0.05, 0.12):
            k.box((sx * 0.075, 0.141, z), (0.024, 0.012, 0.016), 'siyah')                                          # boru kelepçesi
    k.cyl((0.05, 0.14, -0.30), (0.05, 0.25, -0.30), 0.003, 'siyah', seg=6)                                       # anten
    k.box((0.05, 0.252, -0.30), (0.012, 0.012, 0.012), 'isik')                                                  # anten ucu lambası
    for sx in (-1, 1):
        k.box((sx * 0.178, 0.126, 0.285), (0.016, 0.016, 0.016), 'isik')                                        # köşe seyir lambaları
        k.box((sx * 0.178, 0.126, -0.345), (0.016, 0.016, 0.016), 'isik')
    # ---------------- yan paneller: kapaklar, menteşeler, havalandırma, uyarı plakaları
    for sx in (-1, 1):
        for i in range(4):
            z = -0.28 + i * 0.17
            k.box((sx * (HW + 0.002), 0.01, z), (0.006, 0.20, 0.15), 'boya', 0.002)
            k.box((sx * (HW + 0.006), 0.005, z), (0.006, 0.06, 0.07), 'turuncu', 0.001)
            for q in (-0.055, 0.055):
                k.box((sx * (HW + 0.007), 0.075, z + q), (0.006, 0.014, 0.006), 'metal')                         # menteşe
        k.box((sx * (HW + 0.004), -0.06, 0.12), (0.01, 0.07, 0.22), 'turuncu', 0.002)
        for i in range(5):
            k.box((sx * (HW + 0.006), -0.065 + i * 0.012, 0.07), (0.004, 0.005, 0.10), 'siyah')                  # yan havalandırma
        k.cyl((sx * 0.17, -0.12, 0.00), (sx * 0.17, -0.12, 0.26), 0.022, 'metal', 0.028)
        k.cyl((sx * 0.17, -0.12, 0.26), (sx * 0.17, -0.12, 0.30), 0.012, 'cam', seg=10)
        for z in (0.06, 0.2):
            k.box((sx * 0.17, -0.105, z), (0.018, 0.026, 0.016), 'koyu')                                         # sensör braketi
    # ---------------- kanatlar
    for sx in (-1, 1):
        k.tbox((sx * 0.25, 0.01), 0.13, 0.11, 0.024, 0.016, -0.04, 0.10, 'boya')
        k.box((sx * 0.29, 0.012, 0.04), (0.04, 0.03, 0.06), 'turuncu', 0.001)
        k.box((sx * 0.31, 0.012, 0.0), (0.014, 0.018, 0.016), 'isik')                                           # kanat ucu lamba
        k.box((sx * 0.25, 0.0255, 0.03), (0.10, 0.003, 0.012), 'siyah')
        for i in range(3):
            k.box((sx * (0.21 + i * 0.03), 0.0245, -0.01), (0.004, 0.004, 0.06), 'metal')
    # ---------------- arka yan uyarı şeritleri
    for sx in (-1, 1):
        for i in range(4):
            k.box((sx * (HW + 0.004), 0.0, -0.40 + i * 0.028), (0.005, 0.20, 0.010), 'sari')
    # ---------------- motorlar: 3×2 çan nozul, çevrede is izi
    ENG = [(x, y) for y in (0.07, -0.05) for x in (-0.125, 0.0, 0.125)]
    r = 0.046
    for x, y in ENG:
        k.cyl((x, y, -0.50), (x, y, -0.53), r * 1.22, 'metal', seg=16)
        k.cyl((x, y, -0.53), (x, y, -0.565), r * 1.10, 'koyu', r * 1.18, seg=16, cap=False)           # çan ön yarısı: koyu çelik
        k.cyl((x, y, -0.565), (x, y, -0.60), r * 1.18, 'is', r * 1.30, seg=16, cap=False)              # çan arka yarısı: is
        k.cyl((x, y, -0.60), (x, y, -0.612), r * 1.36, 'metal', seg=16, cap=False)                     # dudak
        k.cyl((x, y, -0.55), (x, y, -0.556), r * 0.80, 'cekirdek', seg=16)
        for dz in (-0.545, -0.58):
            k.cyl((x, y, dz), (x, y, dz - 0.008), r * (1.20 if dz > -0.56 else 1.28), 'celik', seg=16, cap=False)      # soğutma halkası
        for a_ in range(8):
            ang = a_ * math.pi / 4
            k.box((x + math.cos(ang) * r * 1.2, y + math.sin(ang) * r * 1.2, -0.52), (0.010, 0.010, 0.035), 'metal')
            k.box((x + math.cos(ang) * r * 1.20, y + math.sin(ang) * r * 1.20, -0.565), (0.007, 0.007, 0.075), 'celik', ry=0.0)   # eksenel kaburga
    for sx in (-1, 1):
        k.cyl((sx * 0.185, 0.0, -0.50), (sx * 0.185, 0.0, -0.53), 0.022, 'metal', seg=10)
        k.cyl((sx * 0.185, 0.0, -0.53), (sx * 0.185, 0.0, -0.545), 0.018, 'cekirdek', seg=10)
    # soot streaks on rear hull (is izi): ince koyu plakalar nozul arkasında
    k.box((0, 0.01, -0.502), (0.40, 0.14, 0.003), 'is')
    # ---------------- kıskaç kolu: pistonlar, hidrolik, kablo, diş
    def arm(p0, p1, rr):
        k.cyl(p0, p1, rr, 'metal', seg=10)
        for p in (p0, p1):
            k.cyl((p[0] - 0.006, p[1], p[2]), (p[0] + 0.006, p[1], p[2]), rr * 1.5, 'koyu', seg=10)
    root, elb, wr = (0.0, -0.08, 0.44), (0.0, -0.17, 0.50), (0.0, -0.20, 0.585)
    k.cyl((0.0, -0.05, 0.40), (0.0, -0.09, 0.45), 0.05, 'koyu', 0.04, seg=10)
    arm(root, elb, 0.03); arm(elb, wr, 0.026)
    # hidrolik pistonlar (kol boyunca paralel, parlak çubuk + gövde)
    for dx in (-0.032, 0.032):
        k.cyl((dx, -0.085, 0.445), (dx, -0.165, 0.505), 0.008, 'celik', seg=6)
        k.cyl((dx, -0.085, 0.445), (dx, -0.120, 0.470), 0.012, 'siyah', seg=6)
        k.cyl((dx, -0.172, 0.505), (dx, -0.198, 0.582), 0.007, 'celik', seg=6)
        k.cyl((dx, -0.172, 0.505), (dx, -0.185, 0.530), 0.011, 'siyah', seg=6)
    k.cyl((0.0, -0.092, 0.452), (0.0, -0.176, 0.507), 0.004, 'lastik', seg=5)                                  # kablo
    k.cyl((0.0, wr[1], wr[2]), (0.0, wr[1] - 0.02, wr[2] + 0.02), 0.035, 'metal', seg=10)
    for sx in (-1, 1):
        j0 = (sx * 0.015, wr[1] - 0.01, wr[2] + 0.015)
        j1 = (sx * 0.065, wr[1] - 0.045, wr[2] + 0.06)
        j2 = (sx * 0.035, wr[1] - 0.095, wr[2] + 0.095)
        k.cyl(j0, j1, 0.016, 'metal', 0.012, seg=8)
        k.cyl(j1, j2, 0.012, 'turuncu', 0.006, seg=8)
        for t in (0.35, 0.65):
            p = Vector(j1) + (Vector(j2) - Vector(j1)) * t
            k.box(tuple(p), (0.012, 0.004, 0.004), 'celik')                                                      # diş
    # ---------------- Blender'a taşı: ×S (metre) + g2b, malzemeler
    objs = []
    for key, bm in k.bm.items():
        if not bm.verts:
            continue
        for v in bm.verts:
            v.co = geo.g2b(Vector(v.co) * S)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ob = geo.mesh_object('P_' + key, bm, mats[MAT[key]], role='body', smooth_angle=35)
        objs.append(ob)
    socks = []
    for i, (x, y) in enumerate(ENG, 1):
        socks.append({'name': 'ANCH_ENG_%d' % i, 'loc': tuple(geo.g2b(Vector((x, y, -0.612)) * S)), 'dir': (0.0, 1.0, 0.0), 'extras': {'kind': 'engine'}})
    for i, p in enumerate(((0.31, 0.012, 0.0), (-0.31, 0.012, 0.0), (0.178, 0.126, 0.285), (-0.178, 0.126, 0.285)), 1):
        socks.append({'name': 'ANCH_NAV_%d' % i, 'loc': tuple(geo.g2b(Vector(p) * S)), 'dir': (0.0, 0.0, 1.0), 'extras': {'kind': 'nav'}})
    socks.append({'name': 'ANCH_MUZ_1', 'loc': tuple(geo.g2b(Vector((0.0, 0.205, 0.17)) * S)), 'dir': (0.0, -1.0, 0.0), 'extras': {'kind': 'muzzle'}})
    return {'objects': objs, 'sockets': socks}
