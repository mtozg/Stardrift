"""Yük Devi — BÜTÜNLEŞİK gövde (Mehmet 2026-11-21: 'her şey parça parça duruyor'). Yöntem: büyük kütleler (gövde, motor bloğu, burun, kanat kökleri, kıskaç kaidesi, karın zırhı) Boolean UNION ile tek yüzeye
birleştirilir; kargo rafı/pencere/nozul boşlukları gövdeden OYULUR (Boolean DIFFERENCE) ve parçalar içine oturtulur; 3 büyük renk alanı (boya / koyu gunmetal / turuncu zırh); hi-poly'de gövdeyi boydan ve çevreden
kesen panel olukları. Çıktı: düşük poligon çekirdek (dissolve+decimate) + küçük ayrı parçalar (role body) ve hi-poly (role 'hi': oluklu çekirdek + aynı küçük parçalar).
Kurulum uzayı: oyun (x yanal, y yukarı, z burun +), L=1; ×S metre, g2b ile Blender."""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix
from core import geo
from families.ship.yuk_ext import orient_outward

MATS = ['yuk_paint', 'yuk_dark', 'yuk_orange', 'yuk_steel', 'yuk_black', 'yuk_glass_ext', 'yuk_rubber', 'yuk_cont_red', 'yuk_cont_blue', 'yuk_cont_orange', 'yuk_cont_rust', 'yuk_soot', 'emit_amber', 'yuk_hazard', 'yuk_pale', 'yuk_bare']
SLOT = {m: i for i, m in enumerate(MATS)}
S = 12.0


def _obj(name, bm, mat, mats, role='body'):
    orient_outward(bm)
    for v in bm.verts:
        v.co = geo.g2b(Vector(v.co) * S)
    for f in bm.faces:
        f.material_index = SLOT[mat]
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in MATS:
        me.materials.append(mats[m])
    ob = bpy.data.objects.new(name, me)
    geo.collection('Asset').objects.link(ob)
    ob['sd_role'] = role
    return ob


def loft_bm(secs):
    bm = bmesh.new()
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
    return bm


def box_bm(c, s):
    bm = bmesh.new()
    r = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(c)) @ Matrix.Diagonal((*s, 1.0)), verts=r['verts'])
    return bm


def cyl_bm(p0, p1, r0, r1=None, seg=16, cap=True):
    bm = bmesh.new()
    d = Vector(p1) - Vector(p0)
    M = Matrix.Translation((Vector(p0) + Vector(p1)) / 2) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=seg, radius1=r0, radius2=r0 if r1 is None else r1, depth=d.length, matrix=M)
    return bm


def tbox_bm(c, w0, w1, h0, h1, z0, z1):
    bm = bmesh.new()
    vs = []
    for z, w, h in ((z0, w0, h0), (z1, w1, h1)):
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            vs.append(bm.verts.new((c[0] + sx * w / 2, c[1] + sy * h / 2, z)))
    for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm.faces.new([vs[i] for i in f])
    return bm


def ring_bm(z, t, w, hu, hd, ch, d, grow=0.05):
    """octagon çerçeve halkası: dışı gövdeden büyük, içi gövde kesitinden d kadar küçük → gövdede d derinlikte çevresel olukları keser"""
    bm = bmesh.new()

    def octo(W, HU, HD, CH, z):
        a = W / 2
        pts = [(a - CH, HU), (a, HU - CH), (a, -HD + CH), (a - CH, -HD), (-a + CH, -HD), (-a, -HD + CH), (-a, HU - CH), (-a + CH, HU)]
        return [bm.verts.new((x, y, z)) for x, y in pts]
    z0, z1 = z - t / 2, z + t / 2
    o0, o1 = octo(w + grow, hu + grow, hd + grow, ch, z0), octo(w + grow, hu + grow, hd + grow, ch, z1)
    i0, i1 = octo(w - 2 * d, hu - d, hd - d, ch, z0), octo(w - 2 * d, hu - d, hd - d, ch, z1)
    for k in range(8):
        j = (k + 1) % 8
        bm.faces.new([o0[k], o0[j], i0[j], i0[k]])         # ön halka yüzü
        bm.faces.new([o1[j], o1[k], i1[k], i1[j]])         # arka
        bm.faces.new([o0[j], o0[k], o1[k], o1[j]])         # dış
        bm.faces.new([i0[k], i0[j], i1[j], i1[k]])         # iç
    return bm


def boolean(target, other, op):
    m = target.modifiers.new('bool', 'BOOLEAN')
    m.operation = op
    m.object = other
    m.solver = 'EXACT'
    with bpy.context.temp_override(object=target, active_object=target, selected_objects=[target], selected_editable_objects=[target]):
        bpy.ops.object.modifier_apply(modifier=m.name)


def union_all(target, others):
    for o in others:
        boolean(target, o, 'UNION')
        bpy.data.objects.remove(o)


def diff_all(target, others):
    for o in others:
        boolean(target, o, 'DIFFERENCE')
        bpy.data.objects.remove(o)


def build(spec, mats):
    P = spec['params']
    rng = random.Random(4242)
    HW = 0.185
    D = 0.0065      # olukların derinliği
    # ---------------- çekirdek kütleler
    hull = _obj('hull', loft_bm([(-0.36, 0.37, 0.13, 0.10, 0.05, 0.0), (0.30, 0.37, 0.13, 0.10, 0.05, 0.0)]), 'yuk_paint', mats)
    steps = [_obj('step', loft_bm([(-0.24, 0.378, 0.136, 0.106, 0.05, 0.0), (0.12, 0.378, 0.136, 0.106, 0.05, 0.0)]), 'yuk_paint', mats),      # orta kademe
             _obj('spine', tbox_bm((0, 0.13), 0.20, 0.17, 0.03, 0.03, -0.34, 0.27), 'yuk_paint', mats)]
    rear = _obj('rear', loft_bm([(-0.53, 0.385, 0.140, 0.118, 0.06, 0.0), (-0.40, 0.395, 0.142, 0.120, 0.06, 0.0), (-0.33, 0.378, 0.134, 0.108, 0.05, 0.0)]), 'yuk_dark', mats)
    nose = _obj('nose', loft_bm([(0.28, 0.37, 0.125, 0.10, 0.05, 0.0), (0.42, 0.33, 0.115, 0.09, 0.05, 0.0), (0.50, 0.24, 0.085, 0.07, 0.04, 0.0)]), 'yuk_paint', mats)
    nose_f = _obj('nose_f', loft_bm([(0.495, 0.24, 0.07, 0.06, 0.03, 0.0), (0.525, 0.19, 0.05, 0.04, 0.02, 0.0)]), 'yuk_dark', mats)
    belly = _obj('belly', tbox_bm((0, -0.105), 0.31, 0.31, 0.04, 0.04, -0.30, 0.24), 'yuk_orange', mats)
    wings = [_obj('wing%d' % i, tbox_bm((sx * 0.245, 0.01), 0.16, 0.12, 0.034, 0.026, -0.05, 0.11), 'yuk_paint', mats) for i, sx in enumerate((-1, 1))]
    pylon = _obj('pylon', tbox_bm((0, -0.085), 0.12, 0.07, 0.10, 0.06, 0.36, 0.47), 'yuk_dark', mats)
    sponsons = [_obj('spons%d' % i, cyl_bm((sx * 0.17, -0.115, -0.02), (sx * 0.17, -0.115, 0.27), 0.030, 0.034, 12), 'yuk_steel', mats) for i, sx in enumerate((-1, 1))]
    extra = []
    extra.append(_obj('hump', tbox_bm((0, 0.150), 0.20, 0.13, 0.050, 0.030, -0.12, 0.16), 'yuk_paint', mats))                         # sırtta yükseltilmiş köprü/üst yapı
    extra.append(_obj('humpf', tbox_bm((0, 0.170), 0.12, 0.10, 0.02, 0.02, -0.06, 0.14), 'yuk_dark', mats))
    for sx in (-1, 1):
        for i, (z0, z1, h) in enumerate(((-0.34, -0.22, 0.17), (-0.21, -0.07, 0.13), (-0.06, 0.08, 0.16), (0.09, 0.22, 0.12))):
            extra.append(_obj('armor', box_bm((sx * (HW + 0.004), -0.005 + 0.012 * (i % 2), (z0 + z1) / 2), (0.016, h, z1 - z0 - 0.012)), 'yuk_paint', mats))     # kademeli yan zırh plakaları (üst üste binen kaplama)
        for k in range(4):
            extra.append(_obj('rrib', box_bm((sx * 0.20, 0.0, -0.50 + 0.0), (0.0, 0.0, 0.0)), 'yuk_dark', mats)) if False else None
        extra.append(_obj('strut', tbox_bm((sx * 0.17, -0.11), 0.06, 0.04, 0.05, 0.03, -0.02, 0.12), 'yuk_dark', mats))                # sponson bağlantı dikmesi
    for sx in (-1, 0, 1):
        extra.append(_obj('cowlrib', box_bm((sx * 0.13, 0.0, -0.455), (0.012, 0.29, 0.14)), 'yuk_dark', mats))                      # nozul bloğu dikey kaburga
    for sx in (-1, 1):
        for i, (z0, z1) in enumerate(((-0.30, -0.15), (-0.12, 0.04), (0.06, 0.20))):
            pass
    extra = [e for e in extra if e is not None]
    union_all(hull, steps + [rear, nose, nose_f, belly, pylon] + wings + sponsons + extra)
    core = hull
    # ---------------- oyuklar: kargo rafları, nozul boşlukları, pencereler (gövdeden OYULUR)
    cuts = []
    for sx in (-1, 1):
        cuts.append(_obj('bay', box_bm((sx * 0.155, 0.1305, -0.02), (0.080, 0.045, 0.49)), 'yuk_dark', mats))
    ENG = [(x, y) for y in (0.07, -0.05) for x in (-0.125, 0.0, 0.125)]
    for x, y in ENG:
        cuts.append(_obj('noz', cyl_bm((x, y, -0.56), (x, y, -0.44), 0.047, 0.041, 20), 'yuk_dark', mats))
    for sx in (-1, 1):                                                         # kabin yan pencere girintileri: 2 geniş pano (kokpit r015: açılı yan duvar camı)
        for z in (0.345, 0.425):
            xs = 0.188 - (z - 0.30) * 0.30
            cuts.append(_obj('win', box_bm((sx * xs, 0.054, z), (0.022, 0.082, 0.066)), 'yuk_dark', mats))
    cuts.append(_obj('wf', box_bm((0, 0.016, 0.52), (0.200, 0.066, 0.030)), 'yuk_dark', mats))     # ön cephe geniş cam girintisi (kokpitteki 4:1 ön cam)
    cuts.append(_obj('wt', box_bm((0, 0.118, 0.415), (0.200, 0.012, 0.095)), 'yuk_dark', mats))   # üst ön cam girintisi
    diff_all(core, cuts)
    # ---------------- çekirdeğe geri birleşen çerçeveler: raf rayları + nozul dudakları
    adds = []
    for sx in (-1, 1):
        for dx in (-0.0425, 0.0425):
            adds.append(_obj('rail', box_bm((sx * 0.155 + dx, 0.1275, -0.02), (0.007, 0.012, 0.49)), 'yuk_steel', mats))
        for z in (-0.265, -0.115, 0.035, 0.185):
            adds.append(_obj('rib', box_bm((sx * 0.155, 0.1215, z), (0.080, 0.006, 0.008)), 'yuk_steel', mats))
    for x, y in ENG:
        adds.append(_obj('lip', ring_bm(0, 0.0, 1, 1, 1, 0, 0), 'yuk_steel', mats)) if False else None
    adds = [a for a in adds if a is not None]
    union_all(core, adds)
    # renk bölgesi: arka blok çevresinde turuncu uyarı kuşakları (gövdenin üstüne gömülü halkalar, birleşik yüzey)
    bands = [_obj('band', ring_bm(z, 0.020, 0.395, 0.142, 0.120, 0.06, 0.006, 0.012), 'yuk_hazard', mats) for z in (-0.43, -0.395)]
    union_all(core, bands)
    # ---------------- hi-poly: oluklu çekirdek kopyası
    hi_core = core.copy()
    hi_core.data = core.data.copy()
    geo.collection('Asset').objects.link(hi_core)
    hi_core.name = 'hi_core'
    hi_core['sd_role'] = 'hi'
    grv = []
    rz = [-0.32, -0.255, -0.19, -0.125, -0.06, 0.005, 0.07, 0.135, 0.20, 0.265]
    for z in rz:
        if rng.random() < 0.9:
            grv.append(_obj('ring', ring_bm(z, 0.0055, 0.37, 0.13, 0.10, 0.05, D), 'yuk_dark', mats))
    for x in (-0.12, -0.065, 0.065, 0.12):                                   # üstte boyuna oluklar (kargo raflarının dışında kalanlar)
        if abs(x) < 0.09 or True:
            grv.append(_obj('lg', box_bm((x, 0.13 - D + 0.02, -0.05), (0.0055, 0.04, 0.62)), 'yuk_dark', mats))
    for sx in (-1, 1):                                                       # yanlarda boyuna oluklar
        for y in (-0.06, 0.0, 0.07):
            grv.append(_obj('ls', box_bm((sx * (HW - D + 0.02), y, -0.03), (0.04, 0.0055, 0.64)), 'yuk_dark', mats))
    for y in (-0.06, 0.0):
        grv.append(_obj('lb', box_bm((0.0, -0.10 + D - 0.02, -0.03), (0.0042 * 0, 0.0, 0.0)), 'yuk_dark', mats)) if False else None
    grv = [g for g in grv if g is not None]
    diff_all(hi_core, grv)
    # ---------------- büyük düz yüzeyleri böl (LOD0 6–8k) + renk bölgeleri gövdeye göre (koyu alt kuşak, turuncu zırh bandı, burun altı)
    bm = bmesh.new()
    bm.from_mesh(core.data)
    cut_len = P.get('split_len', 0.11)
    for _ in range(2):
        groups = {}
        for e in bm.edges:
            Lg = (e.verts[0].co - e.verts[1].co).length / S
            c = int(Lg / cut_len)
            if c >= 1 and any(f.calc_area() / (S * S) > (cut_len * 0.6) ** 2 for f in e.link_faces):
                groups.setdefault(min(c, 8), []).append(e)
        for c, es in groups.items():
            es = [e for e in es if e.is_valid]
            if es:
                bmesh.ops.subdivide_edges(bm, edges=es, cuts=c, use_grid_fill=True)
    zone = P.get('zones', True)
    if zone:
        for f in bm.faces:
            cb = f.calc_center_median()
            gx, gy, gz = cb.x / S, cb.z / S, -cb.y / S          # Blender → oyun (x, y, z)
            cur = MATS[f.material_index]
            if cur not in ('yuk_paint', 'yuk_dark'):
                continue
            if gz < -0.335:                                  # motor bloğu: koyu
                f.material_index = SLOT['yuk_dark']
            elif gy < -0.088:                                # karın: koyu
                f.material_index = SLOT['yuk_dark']
            elif gy < -0.046 and abs(gx) > 0.12 and -0.33 < gz < 0.26:     # alt yan kuşak: koyu gunmetal
                f.material_index = SLOT['yuk_dark']
            elif -0.046 <= gy < -0.022 and abs(gx) > 0.15 and -0.33 < gz < 0.27:   # ince turuncu zırh bandı
                f.material_index = SLOT['yuk_orange']
            elif gz > 0.31 and gy < 0.0:                     # burun altı: turuncu zırh
                f.material_index = SLOT['yuk_orange']
    bm.to_mesh(core.data)
    bm.free()
    # ---------------- düşük poligon çekirdek: dissolve + decimate
    bm = bmesh.new()
    bm.from_mesh(core.data)
    if P.get('dissolve_deg', 4.0) > 0:
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(P.get('dissolve_deg', 4.0)), verts=bm.verts, edges=bm.edges, use_dissolve_boundaries=False)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(core.data)
    bm.free()
    m = core.modifiers.new('dec', 'DECIMATE')
    m.decimate_type = 'COLLAPSE'
    m.ratio = P.get('core_ratio', 0.5)
    with bpy.context.temp_override(object=core, active_object=core, selected_objects=[core], selected_editable_objects=[core]):
        bpy.ops.object.modifier_apply(modifier=m.name)
    if P.get('bevel_m', 0) > 0:                                             # düşük poligonda gerçek pah (siluet + kenar parlaması)
        mb = core.modifiers.new('bev', 'BEVEL')
        mb.width = P['bevel_m']; mb.segments = P.get('bevel_seg', 2); mb.limit_method = 'ANGLE'; mb.angle_limit = math.radians(P.get('bevel_angle', 20))
        with bpy.context.temp_override(object=core, active_object=core, selected_objects=[core], selected_editable_objects=[core]):
            bpy.ops.object.modifier_apply(modifier=mb.name)
    geo.set_smooth_by_angle(core, 38)
    geo.set_smooth_by_angle(hi_core, 38)
    core.name = 'core'
    core['sd_role'] = 'body'
    out_body = [core]
    out_hi = [hi_core]
    # ---------------- küçük ayrı parçalar (hem düşük hem hi-poly'de aynı)
    def small(name, bm, mat):
        o = _obj(name, bm, mat, mats)
        geo.set_smooth_by_angle(o, 35)
        out_body.append(o)
        h = o.copy(); h.data = o.data.copy(); geo.collection('Asset').objects.link(h); h['sd_role'] = 'hi'; out_hi.append(h)
        return o
    sizes = ((0.13, 0.058), (0.13, 0.066), (0.13, 0.052))
    cols = {1: ('yuk_cont_red', 'yuk_cont_blue', 'yuk_cont_orange'), -1: ('yuk_cont_rust', 'yuk_cont_orange', 'yuk_cont_blue')}
    for sx in (-1, 1):
        for i, col in enumerate(cols[sx]):
            z = -0.20 + i * 0.145
            lz, hy = sizes[i]
            for tgt in (core, hi_core):                                         # konteynerler gövdeye GÖMÜLÜ: rafın içine oturan, gövdeyle tek yüzey (union)
                tgt_c = _obj('cont', box_bm((sx * 0.155, 0.1155 + hy / 2 - 0.016, z), (0.072, hy + 0.016, lz)), col, mats)
                boolean(tgt, tgt_c, 'UNION'); bpy.data.objects.remove(tgt_c)
            for r in (-1, 0, 1):
                small('contrib', box_bm((sx * 0.155, 0.1155 + hy / 2 - 0.0165, z + r * 0.04), (0.0745, hy - 0.002, 0.005)), 'yuk_dark')
            small('strap', box_bm((sx * 0.155, 0.1155 + hy / 2 - 0.0165, z + (0.04 if i % 2 else -0.04)), (0.076, hy - 0.001, 0.012)), 'yuk_rubber')
            small('plate', box_bm((sx * 0.1915 - 0.0, 0.1155 + hy * 0.62, z - 0.02), (0.002, 0.012, 0.05)), 'yuk_pale')
    # pencere camları (oyuk içine oturur) + dikmeler
    for sx in (-1, 1):
        for z in (0.345, 0.425):
            xs = 0.188 - (z - 0.30) * 0.30
            small('glass', box_bm((sx * (xs - 0.002), 0.054, z), (0.014, 0.072, 0.056)), 'yuk_glass_ext')
    small('glassf', box_bm((0, 0.016, 0.518), (0.190, 0.057, 0.016)), 'yuk_glass_ext')
    small('glasst', box_bm((0, 0.116, 0.415), (0.190, 0.008, 0.088)), 'yuk_glass_ext')
    for x in (-0.100, -0.049, 0.049, 0.100):                                  # 4 dikme: iki dış + iki iç (kokpit ön camı gibi: orta bölme geniş)
        small('mull', box_bm((x, 0.016, 0.526), (0.008, 0.072, 0.012)), 'yuk_steel')
    small('hdr', box_bm((0, 0.054, 0.526), (0.206, 0.008, 0.012)), 'yuk_dark')
    # nozul çekirdekleri (oyuğun dibinde) + içi is
    for x, y in ENG:
        small('core', cyl_bm((x, y, -0.455), (x, y, -0.460), 0.030, None, 16), 'emit_amber')
        small('soot', cyl_bm((x, y, -0.500), (x, y, -0.480), 0.048, 0.050, 16, cap=False), 'yuk_soot')
    # üst güverte: taret, korkuluk, panjur, anten, lambalar
    small('turret', cyl_bm((0, 0.14, 0.10), (0, 0.175, 0.10), 0.055, None, 20), 'yuk_steel')
    small('turret2', cyl_bm((0, 0.175, 0.10), (0, 0.19, 0.10), 0.040, None, 20), 'yuk_dark')
    small('barrel', cyl_bm((0.0, 0.2, 0.10), (0.0, 0.205, 0.17), 0.006, None, 8), 'yuk_black')
    for sx in (-1, 1):
        small('hand', cyl_bm((sx * 0.195, 0.205, -0.275), (sx * 0.195, 0.205, 0.175), 0.004, None, 6), 'yuk_steel')
        small('lamp', box_bm((sx * 0.178, 0.126, 0.285), (0.016, 0.016, 0.016)), 'emit_amber')
        small('lamp2', box_bm((sx * 0.178, 0.126, -0.345), (0.016, 0.016, 0.016)), 'emit_amber')
    small('ant', cyl_bm((0.05, 0.14, -0.30), (0.05, 0.25, -0.30), 0.003, None, 6), 'yuk_black')
    for i in range(6):
        small('louver', box_bm((-0.045, 0.1475, -0.27 + i * 0.012), (0.065, 0.006, 0.006)), 'yuk_dark')
    # kıskaç (kaideden çıkan kol): pistonlu
    def arm(p0, p1, rr):
        small('arm', cyl_bm(p0, p1, rr, None, 10), 'yuk_steel')
        for p in (p0, p1):
            small('joint', cyl_bm((p[0] - 0.006, p[1], p[2]), (p[0] + 0.006, p[1], p[2]), rr * 1.5, None, 10), 'yuk_dark')
    root, elb, wr = (0.0, -0.08, 0.44), (0.0, -0.17, 0.50), (0.0, -0.20, 0.585)
    arm(root, elb, 0.046); arm(elb, wr, 0.040)
    for dx in (-0.032, 0.032):
        small('pist', cyl_bm((dx * 1.35, -0.085, 0.445), (dx * 1.35, -0.165, 0.505), 0.013, None, 8), 'yuk_bare')
        small('pistb', cyl_bm((dx * 1.35, -0.085, 0.445), (dx * 1.35, -0.120, 0.470), 0.020, None, 8), 'yuk_black')
    small('wrist', cyl_bm((0.0, wr[1], wr[2]), (0.0, wr[1] - 0.02, wr[2] + 0.02), 0.052, None, 10), 'yuk_steel')
    for sx in (-1, 1):
        j0 = (sx * 0.015, wr[1] - 0.01, wr[2] + 0.015)
        j1 = (sx * 0.065, wr[1] - 0.045, wr[2] + 0.06)
        j2 = (sx * 0.035, wr[1] - 0.095, wr[2] + 0.095)
        small('jaw', cyl_bm(j0, j1, 0.026, 0.020, 8), 'yuk_steel')
        small('jaw2', cyl_bm(j1, j2, 0.020, 0.010, 8), 'yuk_orange')
    socks = []
    for i, (x, y) in enumerate(ENG, 1):
        socks.append({'name': 'ANCH_ENG_%d' % i, 'loc': tuple(geo.g2b(Vector((x, y, -0.460)) * S)), 'dir': (0.0, 1.0, 0.0), 'extras': {'kind': 'engine'}})
    for i, p in enumerate(((0.31, 0.012, 0.0), (-0.31, 0.012, 0.0), (0.178, 0.126, 0.285), (-0.178, 0.126, 0.285)), 1):
        socks.append({'name': 'ANCH_NAV_%d' % i, 'loc': tuple(geo.g2b(Vector(p) * S)), 'dir': (0.0, 0.0, 1.0), 'extras': {'kind': 'nav'}})
    socks.append({'name': 'ANCH_MUZ_1', 'loc': tuple(geo.g2b(Vector((0.0, 0.205, 0.17)) * S)), 'dir': (0.0, -1.0, 0.0), 'extras': {'kind': 'muzzle'}})
    return {'objects': out_body + out_hi, 'sockets': socks}
