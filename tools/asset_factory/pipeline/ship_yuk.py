"""Yük Devi — sıfırdan modelleme (konsept turu c001): oyun içi görünüm yalnız TASARIM referansı (siluet/renk/kimlik).
Oyun uzayı: burun +Z, yukarı +Y, uzunluk 1,0. Malzeme bölgeleri adlı (konsept: düz malzemeler; nihai: tek atlas).
Kullanım: python pipeline/ship_yuk.py <çıktı_klasörü>"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy, bmesh
from mathutils import Vector, Matrix
from core import geo, render as R

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
PAL = {      # (renk, pürüz, metal, emissive)
    'boya': ((0.30, 0.29, 0.14), 0.65, 0.25, None), 'turuncu': ((0.62, 0.27, 0.06), 0.6, 0.3, None),
    'metal': ((0.09, 0.09, 0.10), 0.45, 0.85, None), 'koyu': ((0.03, 0.03, 0.035), 0.7, 0.4, None),
    'kirmizi': ((0.40, 0.09, 0.06), 0.6, 0.2, None), 'mavi': ((0.07, 0.11, 0.20), 0.6, 0.2, None),
    'cam': ((0.02, 0.10, 0.22), 0.15, 0.0, (0.2, 0.55, 1.0, 1.6)), 'isik': ((1, .6, .2), 0.5, 0, (1.0, 0.55, 0.15, 6.0)),
    'alev': ((1, .5, .1), 0.5, 0, (1.0, 0.50, 0.12, 4.0)), 'sari': ((0.75, 0.55, 0.04), 0.6, 0.1, None), 'bell': ((0.025, 0.025, 0.03), 0.5, 0.7, None),
}
BM = {k: bmesh.new() for k in PAL}


def box(c, s, mat, bev=0.004, rx=0.0):
    bm = BM[mat]
    r = bmesh.ops.create_cube(bm, size=1.0)
    M = Matrix.Translation(Vector(c)) @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Diagonal((*s, 1.0))
    bmesh.ops.transform(bm, matrix=M, verts=r['verts'])
    if bev > 0:
        bmesh.ops.bevel(bm, geom=list({e for v in r['verts'] for e in v.link_edges}), offset=bev, segments=1, affect='EDGES')


def tbox(c, w0, w1, h0, h1, z0, z1, mat, bev=0.004):
    """kesik piramit gövde: z0→z1 arası genişlik w0→w1, yükseklik h0→h1 (c: x,y merkezi)"""
    bm = BM[mat]
    vs = []
    for z, w, h in ((z0, w0, h0), (z1, w1, h1)):
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            vs.append(bm.verts.new((c[0] + sx * w / 2, c[1] + sy * h / 2, z)))
    for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def loft(secs, mat):
    """sekizgen kesit halkaları: secs = [(z, genişlik, üst, alt, pah, y0)] ; kapaklı"""
    bm = BM[mat]
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


def cyl(p0, p1, r0, mat, r1=None, seg=16, cap=True):
    bm = BM[mat]
    d = Vector(p1) - Vector(p0)
    M = Matrix.Translation((Vector(p0) + Vector(p1)) / 2) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=seg, radius1=r0, radius2=r0 if r1 is None else r1, depth=d.length, matrix=M)


# ---------------- gövde (ölçüler L=1; x yanal ±, y yukarı, z burun +)
HW, HY0, HY1 = 0.185, -0.10, 0.13           # ana gövde yarı genişlik, alt/üst
loft([(-0.36, 0.37, 0.13, 0.10, 0.05, 0.0), (0.30, 0.37, 0.13, 0.10, 0.05, 0.0)], 'boya')                   # ana kargo gövdesi (sekizgen kesit)
loft([(-0.405, 0.40, 0.145, 0.125, 0.05, 0.0), (-0.355, 0.40, 0.145, 0.125, 0.05, 0.0)], 'metal')          # arka çerçeve halkası
loft([(-0.50, 0.39, 0.13, 0.11, 0.05, 0.0), (-0.40, 0.395, 0.135, 0.115, 0.05, 0.0)], 'boya')              # motor bloğu
loft([(0.30, 0.37, 0.125, 0.10, 0.05, 0.0), (0.42, 0.33, 0.115, 0.09, 0.05, 0.0), (0.50, 0.24, 0.085, 0.07, 0.04, 0.0)], 'boya')   # burun kabini
loft([(0.50, 0.24, 0.07, 0.06, 0.03, 0.0), (0.52, 0.19, 0.05, 0.04, 0.02, 0.0)], 'metal')
# kokpit camı: yan pencere şeridi (5 pano) + ön cam
for k in range(5):
    z = 0.325 + k * 0.034
    w = 0.185 - (z - 0.3) * 0.18
    for sx in (-1, 1):
        box((sx * (0.185 - (z - 0.3) * 0.31 + 0.002), 0.045, z), (0.008, 0.055, 0.027), 'cam', 0.002)
box((0, 0.119, 0.41), (0.21, 0.008, 0.09), 'cam', 0.002)
box((0, 0.118, 0.405), (0.19, 0.012, 0.012), 'metal', 0.002)
box((0, 0.118, 0.47), (0.16, 0.012, 0.012), 'metal', 0.002)
# alt zırh paneli (turuncu) + uyarı şeridi
tbox((0, -0.105), 0.30, 0.30, 0.02, 0.02, -0.30, 0.22, 'turuncu', 0.004)
for k in range(11):
    box((0, -0.136, -0.28 + k * 0.045), (0.34, 0.006, 0.02), 'koyu', 0.001)
# yan kargo koyları (üst kenar boyunca, 3 konteyner/yan)
for sx in (-1, 1):
    box((sx * 0.155, 0.125, -0.02), (0.075, 0.018, 0.46), 'koyu', 0.003)                                  # raf çerçevesi
    for k, col in enumerate(('kirmizi', 'mavi', 'turuncu')):
        z = -0.20 + k * 0.145
        box((sx * 0.155, 0.158, z), (0.07, 0.058, 0.13), col, 0.004)
        for r in range(3):
            box((sx * 0.155, 0.158, z - 0.04 + r * 0.04), (0.072, 0.06, 0.006), 'koyu', 0.001)             # konteyner kaburgası
    for z in (-0.27, 0.03, 0.2):
        box((sx * 0.155, 0.17, z), (0.008, 0.07, 0.008), 'metal', 0.001)
        box((sx * 0.188, 0.14, z), (0.02, 0.05, 0.012), 'metal', 0.002)                                   # raf direği
# üst orta güverte: tabaka, turret yuvası, havalandırma, kapaklar
box((0, 0.135, -0.07), (0.20, 0.012, 0.40), 'boya', 0.003)
cyl((0.0, 0.14, 0.10), (0.0, 0.17, 0.10), 0.055, 'metal', seg=24)                                         # turret halkası
cyl((0.0, 0.17, 0.10), (0.0, 0.185, 0.10), 0.04, 'koyu', seg=24)
cyl((0.0, 0.185, 0.10), (0.0, 0.2, 0.10), 0.014, 'turuncu', seg=12)
for k in range(5):
    box((-0.04, 0.147, -0.25 + k * 0.012), (0.06, 0.006, 0.006), 'koyu', 0.001)                         # havalandırma ızgarası
for z in (-0.18, -0.06, 0.04):
    box((0.0, 0.142, z), (0.07, 0.01, 0.045), 'metal', 0.002)
    box((0.045, 0.145, z), (0.02, 0.01, 0.02), 'sari', 0.002)
for sx in (-1, 1):
    box((sx * 0.075, 0.14, -0.07), (0.022, 0.018, 0.42), 'metal', 0.002)                                 # boyuna boru/korkuluk
# yan panel çizgileri / levhalar
for sx in (-1, 1):
    for k in range(4):
        z = -0.28 + k * 0.17
        box((sx * (HW + 0.002), 0.01, z), (0.006, 0.20, 0.15), 'boya', 0.004)
        box((sx * (HW + 0.006), 0.005, z), (0.006, 0.06, 0.07), 'turuncu', 0.003)
    box((sx * (HW + 0.004), -0.06, 0.12), (0.01, 0.07, 0.22), 'turuncu', 0.004)
    # sensör/top kapsülü (gövde altı yanında) + kanat kısa levhası
    cyl((sx * 0.17, -0.12, 0.00), (sx * 0.17, -0.12, 0.26), 0.022, 'metal', 0.028)
    cyl((sx * 0.17, -0.12, 0.26), (sx * 0.17, -0.12, 0.30), 0.012, 'cam', seg=10)
# kanatlar: gövde dışına çıkan kısa delta (üstte turuncu uç, altta destek)
for sx in (-1, 1):
    bm = BM['boya']
    P = [(0.18, 0.12), (0.30, 0.00), (0.33, -0.07), (0.18, -0.12)]      # (x, z) kök-uç çokgeni
    for yy, th in ((0.012, 0.012),):
        top = [bm.verts.new((sx * x, yy + th, z)) for x, z in P]
        bot = [bm.verts.new((sx * x, yy - th, z)) for x, z in P]
        if sx < 0:
            top, bot = top[::-1], bot[::-1]
        bm.faces.new(top[::-1]); bm.faces.new(bot)
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new([top[j], top[i], bot[i], bot[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    box((sx * 0.32, 0.012, -0.035), (0.03, 0.03, 0.07), 'turuncu', 0.003)
    box((sx * 0.245, 0.0, 0.02), (0.14, 0.012, 0.012), 'koyu', 0.001)
# uyarı şeritleri (arka yan)
for sx in (-1, 1):
    for k in range(7):
        box((sx * (HW + 0.004), 0.0, -0.40 + k * 0.014), (0.005, 0.20, 0.008), 'sari', 0.001) if k % 2 == 0 else None
# ---------------- motor grubu: 3 yan × 2 yükseklik büyük kovan + 2 küçük yedek
ENG = []
for iy, y in enumerate((0.07, -0.05)):
    for ix, x in enumerate((-0.125, 0.0, 0.125)):
        ENG.append((x, y, 0.046))
for x, y, r in ENG:
    cyl((x, y, -0.50), (x, y, -0.53), r * 1.22, 'metal', seg=20)                                         # bağlantı halkası
    cyl((x, y, -0.53), (x, y, -0.60), r * 1.10, 'bell', r * 1.30, seg=20, cap=False)                      # çan (dışa açılan)
    cyl((x, y, -0.60), (x, y, -0.612), r * 1.34, 'metal', seg=20)                                         # dudak
    cyl((x, y, -0.545), (x, y, -0.55), r * 0.82, 'alev', seg=20)                                         # çekirdek (içeride)
    for a_ in range(6):
        ang = a_ * math.pi / 3
        box((x + math.cos(ang) * r * 1.18, y + math.sin(ang) * r * 1.18, -0.52), (0.012, 0.012, 0.04), 'turuncu', 0.001)
for sx in (-1, 1):                                                                                          # küçük yardımcı iticiler
    cyl((sx * 0.185, 0.0, -0.50), (sx * 0.185, 0.0, -0.53), 0.022, 'metal', seg=12)
    cyl((sx * 0.185, 0.0, -0.53), (sx * 0.185, 0.0, -0.545), 0.018, 'alev', seg=12)
# ---------------- kıskaç kolu (burun altı; büyük)
def arm(p0, p1, r):
    cyl(p0, p1, r, 'metal', seg=12)
    for p in (p0, p1):
        cyl((p[0] - 0.004, p[1], p[2]), (p[0] + 0.004, p[1], p[2]), r * 1.5, 'koyu', seg=12)
root, elb, wr = (0.0, -0.08, 0.44), (0.0, -0.17, 0.50), (0.0, -0.20, 0.585)
cyl((0.0, -0.05, 0.40), (0.0, -0.09, 0.45), 0.05, 'koyu', 0.04, seg=12)
arm(root, elb, 0.03); arm(elb, wr, 0.026)
cyl((0.0, wr[1], wr[2]), (0.0, wr[1] - 0.02, wr[2] + 0.02), 0.035, 'metal', seg=12)
for sx in (-1, 1):
    j0 = (sx * 0.015, wr[1] - 0.01, wr[2] + 0.015)
    j1 = (sx * 0.065, wr[1] - 0.045, wr[2] + 0.06)
    j2 = (sx * 0.035, wr[1] - 0.095, wr[2] + 0.095)
    cyl(j0, j1, 0.016, 'metal', 0.012, seg=8)
    cyl(j1, j2, 0.012, 'turuncu', 0.006, seg=8)
# ---------------- Blender'a taşı (oyun → Blender), malzemeler
geo.reset_scene()
mats = {}
for k, (col, rough, metal, em) in PAL.items():
    m = bpy.data.materials.new('M_' + k)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if em:
        b.inputs['Emission Color'].default_value = (*em[:3], 1)
        b.inputs['Emission Strength'].default_value = em[3]
    mats[k] = m
objs = []
for k, bm in BM.items():
    if not bm.verts:
        continue
    for v in bm.verts:
        v.co = geo.g2b(v.co)
    if k != 'bell':
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(k)
    bm.to_mesh(me)
    ob = bpy.data.objects.new('P_' + k, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(mats[k])
    geo.set_smooth_by_angle(ob, 35)
    objs.append(ob)
tri = sum(len(o.data.polygons) for o in objs)
print('KONSEPT quad/poly:', tri)
sc = bpy.context.scene
R.rig_lookdev(0.7)
views = {'on34': ((1.15, -1.35, 0.7), 'on_uc_ceyrek'), 'arka34': ((-1.2, 1.35, 0.65), 'arka_uc_ceyrek'), 'yan': ((1.7, 0.0, 0.12), 'yan'), 'ust': ((0.0, 0.0, 1.9), 'ust')}
for key, (loc, nm) in views.items():
    cam = R.camera('c_' + key, loc, (0, 0.0, 0.0), 32.0)
    R.render(os.path.join(out, 'konsept_%s.png' % nm), cam, (1000, 620), 40, transparent=False)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'model.blend'), compress=True)
