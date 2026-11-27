"""Şahin — KONSEPT B "ÇATAL" (Mehmet onayı 2026-11-27): kısa merkez kapsül + iki uzun gövde-kirişi (H çerçeve), iki ana motor, kiriş dışında radyatör plakaları.
Sanat yönü: premium hard sci-fi; malzeme kimliği: beyaz seramik karo (üst), titanyum (alt/yapı), gunmetal (mekanik), ısıya dayanıklı koyu (motor), dar kırmızı işaret.
Her detay işlevli: soğutma hatları, RCS kümeleri, bakım kapakları, bağlantı mafsalları, emme ızgaraları. Rastgele renk/greeble yok.
Üretim zinciri: süperelips loft kütleler → Boolean UNION (kapsül+kirişler+bağlantı kirişleri) → nozul oyma → ızgara bölme → bölge bazlı malzeme → hi-poly oluk/karo kabartma → bake.
Birim: METRE (oyun uzayı: x yanal, y yukarı, z burun +). pipeline normalize_length ile 1.0'a ölçekler."""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix
from core import geo
from families.ship.yuk_ext import orient_outward
from families.ship.yuk_fused import box_bm, cyl_bm, boolean, union_all, diff_all, ring_bm

MATS = ['cat_ceramic', 'cat_ceramic2', 'cat_titan', 'cat_gun', 'cat_heat', 'cat_red', 'sahin_glass', 'emit_redhot', 'emit_blue', 'emit_red']
SLOT = {m: i for i, m in enumerate(MATS)}
BX = 2.1          # kiriş yarı açıklığı
D = 0.012         # hi-poly oluk derinliği (m)


def sup(a, p):
    return math.copysign(abs(a) ** (2.0 / p), a)


def loft(secs, n=40, cap=True):
    """secs: (z, yarı_genişlik, yarı_üst, yarı_alt, p, cx, cy). p=2 elips, 3-4 yuvarlak kare."""
    bm = bmesh.new(); rings = []
    for s in secs:
        z, wx, hu, hd, p = s[:5]; cx = s[5] if len(s) > 5 else 0.0; cy = s[6] if len(s) > 6 else 0.0
        ring = []
        for i in range(n):
            t = 2 * math.pi * i / n; c, sn = math.cos(t), math.sin(t)
            ring.append(bm.verts.new((cx + wx * sup(c, p), cy + (hu if sn > 0 else hd) * sup(sn, p), z)))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([r0[i], r0[j], r1[j], r1[i]])
    if cap:
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def loft_x(secs, n=32):
    """x ekseni boyunca loft (bağlantı kirişleri): secs (x, yarı_z, yarı_üst, yarı_alt, p, cz, cy)"""
    bm = loft([(s[0], s[1], s[2], s[3], s[4], s[5] if len(s) > 5 else 0.0, s[6] if len(s) > 6 else 0.0) for s in secs], n)
    for v in bm.verts:
        x, y, z = v.co
        v.co = Vector((z, y, x))          # loft'un z ekseni → x, yanal → z
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def plate(pts_zy, x, th):
    bm = bmesh.new()
    a = [bm.verts.new((x - th / 2, y, z)) for z, y in pts_zy]; b = [bm.verts.new((x + th / 2, y, z)) for z, y in pts_zy]
    bm.faces.new(a[::-1]); bm.faces.new(b)
    for i in range(len(pts_zy)):
        j = (i + 1) % len(pts_zy); bm.faces.new([a[i], a[j], b[j], b[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def tube(p0, p1, r0, r1=None, seg=16, cap=True):
    return cyl_bm(p0, p1, r0, r1, seg, cap=cap)


def _obj(name, bm, mat, mats, role='body'):
    orient_outward(bm)
    for v in bm.verts:
        v.co = geo.g2b(Vector(v.co))
    for f in bm.faces:
        f.material_index = SLOT[mat]
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in MATS:
        me.materials.append(mats[m])
    ob = bpy.data.objects.new(name, me); geo.collection('Asset').objects.link(ob); ob['sd_role'] = role
    return ob


def build(spec, mats):
    P = spec['params']
    # ------------------------------------------------------------ kapsül (kokpit + reaktör)
    pod_s = [(-1.45, 0.50, 0.40, 0.38, 2.8), (-1.0, 0.72, 0.54, 0.46, 3.0), (-0.2, 0.84, 0.62, 0.52, 3.2), (1.0, 0.80, 0.60, 0.50, 3.2), (2.0, 0.64, 0.50, 0.42, 3.0), (2.9, 0.42, 0.34, 0.30, 2.7), (3.5, 0.20, 0.17, 0.16, 2.4), (3.85, 0.09, 0.08, 0.08, 2.1)]
    pod = _obj('pod', loft(pod_s), 'cat_ceramic', mats)
    parts = []
    # kirişler (süperelips, uca doğru incelir) + motor bölümü kalınlaşması
    ENG = []
    for sx in (-1, 1):
        cx = sx * BX
        bs = [(-4.15, 0.44, 0.42, 0.42, 2.6, cx), (-3.85, 0.58, 0.54, 0.54, 3.0, cx), (-3.0, 0.60, 0.54, 0.54, 3.2, cx), (-1.4, 0.54, 0.48, 0.48, 3.2, cx), (0.5, 0.50, 0.45, 0.44, 3.0, cx),
              (1.8, 0.44, 0.40, 0.40, 2.9, cx), (2.7, 0.30, 0.27, 0.27, 2.6, cx), (3.3, 0.16, 0.15, 0.15, 2.3, cx), (3.6, 0.07, 0.07, 0.07, 2.1, cx)]
        parts.append(_obj('boom', loft(bs), 'cat_ceramic', mats))
        ENG.append((cx, 0.0))
        # motor nacelle şişkinliği (yapısal halka) ve emme kutusu
        parts.append(_obj('nacR', loft([(-4.2, 0.50, 0.47, 0.47, 2.4, cx), (-3.9, 0.64, 0.60, 0.60, 2.8, cx), (-3.2, 0.64, 0.60, 0.60, 2.8, cx), (-2.9, 0.56, 0.52, 0.52, 2.6, cx)]), 'cat_titan', mats))
        # ön silah kovanı (kiriş burnunda) ve sensör
        parts.append(_obj('pcase', loft([(2.55, 0.18, 0.17, 0.17, 2.6, cx, -0.02), (3.1, 0.22, 0.20, 0.20, 2.8, cx, -0.02), (3.7, 0.14, 0.13, 0.13, 2.4, cx, -0.02)]), 'cat_gun', mats))
        # bağlantı kirişi (kapsül ↔ kiriş): kanat kesitli, öne eğik
        parts.append(_obj('strutL', loft_x([(sx * 0.55, 1.15, 0.17, 0.15, 3.0, -0.35, 0.0), (sx * 1.3, 0.95, 0.16, 0.14, 3.0, -0.25, 0.0), (sx * 1.8, 0.70, 0.18, 0.16, 3.0, -0.10, 0.0)]), 'cat_titan', mats))
    # arka enine kiriş (yapısal), ön ince sensör/silah rayı
    parts.append(_obj('xbeam', loft_x([(-2.0, 0.45, 0.20, 0.18, 3.0, -2.85, 0.0), (0.0, 0.52, 0.22, 0.20, 3.2, -2.85, 0.0), (2.0, 0.45, 0.20, 0.18, 3.0, -2.85, 0.0)]), 'cat_titan', mats))
    parts.append(_obj('spar', tube((-BX, 0.0, 2.35), (BX, 0.0, 2.35), 0.065, None, 14), 'cat_titan', mats))
    # kapsül altı reaktör kaportası
    parts.append(_obj('reactor', loft([(-1.35, 0.40, 0.0, 0.40, 2.6, 0, -0.34), (-0.6, 0.60, 0.0, 0.62, 3.0, 0, -0.30), (0.5, 0.56, 0.0, 0.52, 3.0, 0, -0.28), (1.2, 0.30, 0.0, 0.30, 2.6, 0, -0.26)]), 'cat_gun', mats))
    # kokpit kasası (titanyum pah) — cam bu kasanın içine oturur
    parts.append(_obj('cframe', loft([(0.7, 0.26, 0.04, 0.0, 2.4, 0, 0.62), (1.2, 0.50, 0.17, 0.0, 2.6, 0, 0.60), (2.2, 0.46, 0.17, 0.0, 2.6, 0, 0.56), (3.0, 0.22, 0.06, 0.0, 2.4, 0, 0.50)]), 'cat_titan', mats))
    parts.append(_obj('glass', loft([(0.85, 0.22, 0.10, 0.0, 2.4, 0, 0.64), (1.25, 0.43, 0.19, 0.0, 2.6, 0, 0.625), (2.15, 0.40, 0.19, 0.0, 2.6, 0, 0.58), (2.85, 0.17, 0.08, 0.0, 2.4, 0, 0.53)]), 'sahin_glass', mats))
    # ağır top: nose'da halkalı yuva + kılıf + namlu (hepsi ortak eksende)
    parts.append(_obj('mount', tube((0, -0.05, 3.5), (0, -0.05, 3.9), 0.24, 0.22, 32), 'cat_titan', mats))
    parts.append(_obj('shroud', tube((0, -0.05, 3.85), (0, -0.05, 4.7), 0.15, 0.13, 24), 'cat_gun', mats))
    parts.append(_obj('barrel', tube((0, -0.05, 4.65), (0, -0.05, 5.55), 0.07, 0.06, 18), 'cat_gun', mats))
    union_all(pod, parts)
    core = pod
    # nozul oyma
    nozs = [_obj('noz', tube((x, 0.0, -4.7), (x, 0.0, -4.12), 0.34, 0.30, 32), 'cat_heat', mats) for x, _ in ENG]
    diff_all(core, nozs)
    # emme ızgarası girintileri (kiriş üstü) ve bakım kapakları (oyma)
    cuts = []
    for sx in (-1, 1):
        cx = sx * BX
        for k in range(6):
            cuts.append(_obj('louv', box_bm((cx, 0.47, -2.5 + k * 0.30), (0.46, 0.05, 0.10)), 'cat_gun', mats))
        for z in (0.2, 1.3):
            cuts.append(_obj('hatch', box_bm((cx - sx * 0.40, 0.18, z), (0.04, 0.34, 0.5)), 'cat_gun', mats))
    for z in (-1.1, 0.3, 1.6):
        cuts.append(_obj('phatch', box_bm((0.0, 0.60, z), (0.5, 0.05, 0.38)), 'cat_gun', mats))
    diff_all(core, cuts)
    # ------------------------------------------------------------ hi-poly: yapısal oluklar + karo dikişleri
    hi_core = core.copy(); hi_core.data = core.data.copy(); geo.collection('Asset').objects.link(hi_core); hi_core.name = 'hi_core'; hi_core['sd_role'] = 'hi'
    grv = []
    def sec_pod(z):
        for a, b in zip(pod_s, pod_s[1:]):
            if a[0] <= z <= b[0]:
                t = (z - a[0]) / (b[0] - a[0]); return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, 5))
        return pod_s[0][1:5]
    for z in (-1.2, -0.7, -0.2, 0.3, 0.8, 1.3, 1.8, 2.3):              # kapsül yapısal halka oluğu (kaynak/segment dikişi)
        w, hu, hd, p = sec_pod(z)
        grv.append(_obj('ring', ring_bm(z, 0.012, w * 2, hu, hd, 0.16, D), 'cat_gun', mats))
    for x in (-0.55, -0.25, 0.25, 0.55):                              # boyuna dikişler (dorsal karo şeritleri)
        grv.append(_obj('lg', box_bm((x, 0.60 - D, 0.4), (0.010, 0.06, 2.8)), 'cat_gun', mats))
    for sx in (-1, 1):
        cx = sx * BX
        for z in (-3.6, -3.1, -2.5, -1.9, -1.3, -0.7, -0.1, 0.5, 1.1, 1.7, 2.3):     # kiriş enine dikişler
            grv.append(_obj('br', ring_bm(z, 0.012, 1.0, 0.45, 0.45, 0.16, D), 'cat_gun', mats))
            grv[-1].location.x += 0       # (ring merkezde; aşağıda taşınır)
            for v in grv[-1].data.vertices:
                v.co.x += cx
        for x in (cx - 0.3, cx + 0.3):
            grv.append(_obj('bl', box_bm((x, 0.46 - D, -1.0), (0.010, 0.06, 4.6)), 'cat_gun', mats))
    diff_all(hi_core, grv)
    # ------------------------------------------------------------ ızgara bölme + malzeme bölgeleri
    bm = bmesh.new(); bm.from_mesh(core.data)
    cl = P.get('split_len', 0.4)
    for _ in range(2):
        groups = {}
        for e in bm.edges:
            Lg = (e.verts[0].co - e.verts[1].co).length
            c = int(Lg / cl)
            if c >= 1 and any(f.calc_area() > (cl * 0.6) ** 2 for f in e.link_faces):
                groups.setdefault(min(c, 8), []).append(e)
        for c, es in groups.items():
            es = [e for e in es if e.is_valid]
            if es:
                bmesh.ops.subdivide_edges(bm, edges=es, cuts=c, use_grid_fill=True)
    for f in bm.faces:
        cb = f.calc_center_median(); gx, gy, gz = cb.x, cb.z, -cb.y           # oyun uzayı
        cur = MATS[f.material_index]
        if cur not in ('cat_ceramic', 'cat_titan'):
            continue
        in_boom = abs(abs(gx) - BX) < 0.75
        if gz < -3.45 and in_boom:                                          # motor bölümü: ısıya dayanıklı koyu
            f.material_index = SLOT['cat_heat']
        elif gz > 2.9 and in_boom:                                          # kiriş burnu: gunmetal kovan
            f.material_index = SLOT['cat_gun']
        elif gz > 3.35 and not in_boom:                                     # kapsül burnu
            f.material_index = SLOT['cat_gun']
        elif cur == 'cat_ceramic' and gy < (-0.06 if in_boom else -0.10):  # alt yarı titanyum
            f.material_index = SLOT['cat_titan']
        elif cur == 'cat_ceramic':
            # ince, düzenli karo kuşağı farkı: 0,6 m bantlarda iki seramik tonu (rastgele değil, yapısal)
            band = int((gz + 5.0) / 0.6) % 2
            if band:
                f.material_index = SLOT['cat_ceramic2']
    bm.to_mesh(core.data); bm.free()
    if P.get('bevel_m', 0) > 0:
        mb = core.modifiers.new('bev', 'BEVEL'); mb.width = P['bevel_m']; mb.segments = 2; mb.limit_method = 'ANGLE'; mb.angle_limit = math.radians(30)
        with bpy.context.temp_override(object=core, active_object=core, selected_objects=[core], selected_editable_objects=[core]):
            bpy.ops.object.modifier_apply(modifier=mb.name)
    geo.set_smooth_by_angle(core, 40); geo.set_smooth_by_angle(hi_core, 40)
    core.name = 'core'; core['sd_role'] = 'body'
    out_body, out_hi = [core], [hi_core]

    def small(name, bm_, mat):
        o = _obj(name, bm_, mat, mats)
        geo.set_smooth_by_angle(o, 35)
        out_body.append(o)
        h = o.copy(); h.data = o.data.copy(); geo.collection('Asset').objects.link(h); h['sd_role'] = 'hi'; out_hi.append(h)
        return o
    # ------------------------------------------------------------ radyatör plakaları (kiriş dış yüzü): çerçeve + soğutma kanalları + mafsal
    for sx in (-1, 1):
        ox = sx * (BX + 0.74)
        outline = [(-3.9, -0.55), (-3.9, 0.55), (-1.9, 1.55), (0.1, 1.05), (0.4, 0.2), (0.0, -0.8), (-2.4, -1.15)]
        small('rad', plate(outline, ox, 0.05), 'cat_ceramic')
        small('radframe', plate(outline, ox + sx * 0.028, 0.012), 'cat_titan')
        for (za, ya), (zb, yb) in zip(outline, outline[1:] + outline[:1]):        # çerçeve profili: kenar boyunca titanyum kuşak
            zc, yc = (za + zb) / 2, (ya + yb) / 2; ln = math.hypot(zb - za, yb - ya); ang = math.atan2(yb - yc, zb - zc)
            bmf = box_bm((0, 0, 0), (0.03, 0.045, ln))
            for v in bmf.verts:
                z_, y_ = v.co.z, v.co.y
                v.co.z = z_ * math.cos(ang) - y_ * math.sin(ang) + zc
                v.co.y = z_ * math.sin(ang) + y_ * math.cos(ang) + yc
                v.co.x += ox + sx * 0.03
            small('radedge', bmf, 'cat_titan')
        # serpantin soğutma kanalı: 4 yatay şerit + bağlantı
        for k, y in enumerate((-0.45, -0.1, 0.25, 0.6)):
            z0, z1 = (-3.6, -0.4 - 0.1 * k)
            small('radch', box_bm((ox + sx * 0.03, y, (z0 + z1) / 2), (0.014, 0.05, abs(z1 - z0))), 'cat_gun')
        small('radrib', box_bm((ox + sx * 0.03, 0.05, -1.2), (0.014, 1.3, 0.05)), 'cat_gun')
        small('radtip', plate([(-3.9, -0.55), (-3.9, 0.55), (-3.8, 0.55), (-3.8, -0.55)], ox, 0.07), 'cat_red')
        for z in (-3.2, -1.8, -0.4):          # mafsal: kirişe bağlanan 3 destek
            small('hing', tube((sx * (BX + 0.46), 0.0, z), (ox - sx * 0.02, 0.0, z), 0.045, None, 12), 'cat_titan')
            small('hingk', box_bm((ox - sx * 0.05, 0.0, z), (0.07, 0.10, 0.12)), 'cat_gun')
    # ------------------------------------------------------------ motor ayrıntıları (iki motor aynı): çan, kalkan, vernier, parlayan çekirdek
    for x, y in ENG:
        small('bell', tube((x, y, -4.7), (x, y, -4.2), 0.43, 0.36, 36, cap=False), 'cat_heat')
        small('inner', tube((x, y, -4.62), (x, y, -4.58), 0.30, None, 32), 'cat_gun')
        small('core', tube((x, y, -4.6), (x, y, -4.57), 0.19, None, 28), 'emit_redhot')
        small('blue', tube((x, y, -4.605), (x, y, -4.595), 0.07, None, 20), 'emit_blue')
        small('lip', tube((x, y, -4.74), (x, y, -4.66), 0.47, 0.45, 36, cap=False), 'cat_titan')
        for k in range(4):
            a = math.radians(45 + 90 * k)
            small('vern', tube((x + math.cos(a) * 0.54, y + math.sin(a) * 0.54, -4.05), (x + math.cos(a) * 0.54, y + math.sin(a) * 0.54, -4.28), 0.05, 0.04, 10), 'cat_gun')
        for q in range(10):
            a = q * math.pi / 5
            small('bolt', box_bm((x + 0.50 * math.cos(a), y + 0.50 * math.sin(a), -4.30), (0.035, 0.035, 0.05)), 'cat_gun')
    # RCS kümeleri (kapsül burnu ve kuyruğu), alt sensör kubbesi, anten
    for sx in (-1, 1):
        for z, yy in ((3.0, 0.06), (-1.2, 0.10)):
            small('rcs', box_bm((sx * 0.46, yy, z), (0.10, 0.14, 0.18)), 'cat_gun')
            small('rcsn', tube((sx * 0.52, yy, z + 0.02), (sx * 0.58, yy, z + 0.02), 0.04, 0.03, 8), 'cat_heat')
    small('dome', tube((0.0, -0.62, 1.4), (0.0, -0.78, 1.4), 0.20, 0.14, 24), 'cat_gun')
    small('ant1', tube((0.12, 0.64, -1.0), (0.20, 1.1, -1.1), 0.014, 0.007, 6), 'cat_gun')
    small('ant2', tube((-0.20, 0.62, 0.0), (-0.28, 0.90, 0.05), 0.010, 0.006, 6), 'cat_gun')
    # kapsül kırmızı işaretleri (az): burun şeridi + gövde yan sancak
    small('mark1', box_bm((0.0, 0.595, -0.55), (0.62, 0.012, 0.20)), 'cat_red')
    small('mark2', box_bm((0.0, 0.595, -0.20), (0.34, 0.012, 0.08)), 'cat_red')
    for sx in (-1, 1):
        small('idl', box_bm((sx * 0.84, 0.18, 0.1), (0.012, 0.10, 0.60)), 'cat_red')
        small('seyir', box_bm((sx * (BX + 0.58), 0.0, 3.2), (0.04, 0.04, 0.05)), 'emit_red' if sx < 0 else 'emit_blue')
    for sx in (-1, 1):
        small('bmark', box_bm((sx * BX, 0.545, -0.8), (0.34, 0.010, 0.22)), 'cat_red')
        small('bmark2', box_bm((sx * BX, 0.545, -0.4), (0.34, 0.010, 0.06)), 'cat_red')
    small('tailnav', box_bm((0.0, 0.62, -1.45), (0.06, 0.04, 0.05)), 'emit_red')
    # ------------------------------------------------------------ soketler
    socks = []
    for i, (x, y) in enumerate(ENG, 1):
        socks.append({'name': 'ANCH_ENG_%d' % i, 'loc': tuple(geo.g2b(Vector((x, y, -4.62)))), 'dir': (0.0, 1.0, 0.0), 'extras': {'kind': 'engine'}})
    for i, p in enumerate(((BX + 0.58, 0.0, 3.2), (-BX - 0.58, 0.0, 3.2), (0.0, 0.64, -1.45)), 1):
        socks.append({'name': 'ANCH_NAV_%d' % i, 'loc': tuple(geo.g2b(Vector(p))), 'dir': (0.0, 0.0, 1.0), 'extras': {'kind': 'nav'}})
    for i, p in enumerate(((0.0, -0.05, 5.55), (BX, 0.0, 3.6), (-BX, 0.0, 3.6)), 1):
        socks.append({'name': 'ANCH_MUZ_%d' % i, 'loc': tuple(geo.g2b(Vector(p))), 'dir': (0.0, -1.0, 0.0), 'extras': {'kind': 'muzzle'}})
    return {'objects': out_body + out_hi, 'sockets': socks}
