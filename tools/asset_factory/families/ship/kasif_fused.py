"""Kaşif — BÜTÜNLEŞİK gövde (Yük pilotu yöntemi): 16 kenarlı yuvarlak kesit loft, burun sivrilmesi, balon kanopi (kokpit GLB'sindeki 3 bölmeli ön cam: orta + iki açılı yan pano, iki eğik A-direği, üst başlık),
kanat kesiti (ince mercek, hafif yukarı eğimli), 4 motor kovanı (2×2) gövdeye kaideyle bağlı ve gömülü nozul; renk bölgeleri yüz bazında; hi-poly'de çevresel + boyuna panel olukları.
Oyun uzayı (x yanal, y yukarı, z burun +), L=1; ×S; g2b."""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix
from core import geo
from families.ship.yuk_ext import orient_outward
from families.ship.yuk_fused import box_bm, cyl_bm, tbox_bm, boolean, union_all, diff_all

MATS = ['kasif_hull', 'kasif_light', 'sahin_dark', 'sahin_glass', 'steel_dark', 'gunmetal', 'yuk_rubber', 'yuk_soot', 'emit_cyan', 'emit_pinkhot', 'emit_red', 'emit_amber']
SLOT = {m: i for i, m in enumerate(MATS)}
S = 14.0


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


def super_pts(a, hu, hd, n=3.2, N=16, x0=0.0, y0=0.0):
    pts = []
    for i in range(N):
        t = 2 * math.pi * i / N + math.pi / N
        c, s_ = math.cos(t), math.sin(t)
        x = a * math.copysign(abs(c) ** (2 / n), c)
        h = hu if s_ >= 0 else hd
        y = h * math.copysign(abs(s_) ** (2 / n), s_)
        pts.append((x0 + x, y0 + y))
    return pts


def sloft_bm(secs, N=16, cap=True):
    """secs: (z, a, hu, hd, n, x0, y0)"""
    bm = bmesh.new()
    rings = []
    for z, a, hu, hd, n, x0, y0 in secs:
        rings.append([bm.verts.new((x, y, z)) for x, y in super_pts(a, hu, hd, n, N, x0, y0)])
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(N):
            j = (i + 1) % N
            bm.faces.new([r0[i], r0[j], r1[j], r1[i]])
    if cap:
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    return bm


def sring_bm(z, t, a, hu, hd, n, d, grow=0.05, N=16):
    bm = bmesh.new()
    o0 = [bm.verts.new((x, y, z - t / 2)) for x, y in super_pts(a + grow, hu + grow, hd + grow, n, N)]
    o1 = [bm.verts.new((x, y, z + t / 2)) for x, y in super_pts(a + grow, hu + grow, hd + grow, n, N)]
    i0 = [bm.verts.new((x, y, z - t / 2)) for x, y in super_pts(a - d, hu - d, hd - d, n, N)]
    i1 = [bm.verts.new((x, y, z + t / 2)) for x, y in super_pts(a - d, hu - d, hd - d, n, N)]
    for k in range(N):
        j = (k + 1) % N
        bm.faces.new([o0[k], o0[j], i0[j], i0[k]]); bm.faces.new([o1[j], o1[k], i1[k], i1[j]])
        bm.faces.new([o0[j], o0[k], o1[k], o1[j]]); bm.faces.new([i0[k], i0[j], i1[j], i1[k]])
    return bm


def wing_bm(sx, root_x=0.13, tip_x=0.50):
    """kanat kesiti: kök kalın (0,034), uç ince (0,010); geri süpürmeli; uç yukarı eğimli (dihedral)"""
    bm = bmesh.new()
    def pt(x, y, z):
        return bm.verts.new((sx * x, y, z))
    r = [(root_x, -0.045, 0.10, 0.034), (root_x, -0.045, -0.13, 0.034)]
    t = [(tip_x, 0.030, -0.12, 0.011), (tip_x, 0.030, -0.27, 0.011)]
    # üst: kök LE, kök TE, uç TE, uç LE ; alt: aynı noktaların -kalınlık
    top = [pt(r[0][0], r[0][1] + r[0][3] / 2, r[0][2]), pt(r[1][0], r[1][1] + r[1][3] / 2, r[1][2]), pt(t[1][0], t[1][1] + t[1][3] / 2, t[1][2]), pt(t[0][0], t[0][1] + t[0][3] / 2, t[0][2])]
    bot = [pt(r[0][0], r[0][1] - r[0][3] / 2, r[0][2]), pt(r[1][0], r[1][1] - r[1][3] / 2, r[1][2]), pt(t[1][0], t[1][1] - t[1][3] / 2, t[1][2]), pt(t[0][0], t[0][1] - t[0][3] / 2, t[0][2])]
    bm.faces.new(top[::-1]); bm.faces.new(bot)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new([top[j], top[i], bot[i], bot[j]])
    return bm


def build(spec, mats):
    P = spec['params']
    HW = 0.155
    D = 0.0060
    # ---------------- çekirdek: yuvarlak gövde + burun
    hull = _obj('hull', sloft_bm([(-0.42, 0.095, 0.115, 0.115, 3.0, 0, 0), (-0.34, 0.128, 0.130, 0.132, 3.0, 0, 0), (-0.20, 0.152, 0.138, 0.142, 3.0, 0, 0), (0.0, 0.158, 0.141, 0.146, 3.1, 0, 0),
                                  (0.16, 0.148, 0.132, 0.136, 3.2, 0, 0), (0.28, 0.122, 0.112, 0.114, 3.2, 0, 0.002), (0.38, 0.092, 0.090, 0.088, 3.0, 0, 0.004), (0.46, 0.056, 0.060, 0.058, 2.8, 0, 0.006), (0.505, 0.020, 0.026, 0.026, 2.5, 0, 0.008)]), 'kasif_hull', mats)
    parts = []
    # balon kanopi: gövde üstünden hafifçe taşan cam kabarcık (kokpit GLB: geniş ön cam)
    parts.append(_obj('canopy', sloft_bm([(0.215, 0.082, 0.116, 0.050, 2.6, 0, 0.012), (0.30, 0.104, 0.140, 0.052, 2.7, 0, 0.012), (0.38, 0.086, 0.122, 0.052, 2.6, 0, 0.014), (0.45, 0.054, 0.082, 0.046, 2.4, 0, 0.012), (0.49, 0.022, 0.040, 0.030, 2.2, 0, 0.010)]), 'sahin_glass', mats))
    # kaide kanatları (kök blokları) + dikmeler: motorları gövdeye bağlayan pylonlar
    ENG = [(sx * 0.125, y) for sx in (-1, 1) for y in (0.10, -0.09)]
    for x, y in ENG:
        parts.append(_obj('nac', sloft_bm([(-0.50, 0.060, 0.060, 0.060, 2.4, x, y), (-0.40, 0.066, 0.066, 0.066, 2.4, x, y), (-0.26, 0.064, 0.064, 0.064, 2.4, x, y), (-0.20, 0.056, 0.056, 0.056, 2.4, x, y), (-0.155, 0.034, 0.034, 0.034, 2.4, x, y), (-0.135, 0.008, 0.008, 0.008, 2.4, x, y)], 20), 'kasif_hull', mats))
        parts.append(_obj('spin', sloft_bm([(-0.205, 0.052, 0.052, 0.052, 2.2, x, y), (-0.165, 0.040, 0.040, 0.040, 2.2, x, y), (-0.135, 0.010, 0.010, 0.010, 2.2, x, y)], 20), 'kasif_light', mats))
    for sx in (-1, 1):
        parts.append(_obj('pyl', tbox_bm((sx * 0.11, 0.005), 0.090, 0.07, 0.24, 0.20, -0.42, -0.24), 'sahin_dark', mats))     # motor kaidesi: gövdeden nacellelere bağlanan blok
        parts.append(_obj('pylf', tbox_bm((sx * 0.10, 0.005), 0.050, 0.04, 0.22, 0.20, -0.24, -0.14), 'kasif_hull', mats))     # öne doğru incelen kaporta
    # kanatlar (üçgen prizmaya benzer ince mercek) kök bloğu ile
    for sx in (-1, 1):
        parts.append(_obj('wing%d' % sx, wing_bm(sx), 'kasif_hull', mats))
        parts.append(_obj('wroot', tbox_bm((sx * 0.17, -0.040), 0.14, 0.10, 0.060, 0.034, -0.14, 0.11), 'kasif_hull', mats))
    # sırt: radar kaidesi + anten tabanı
    parts.append(_obj('rbase', cyl_bm((0, 0.13, -0.08), (0, 0.168, -0.08), 0.030, 0.022, 16), 'sahin_dark', mats))
    # kokpit çerçevesi: iki eğik A-direği + üst başlık (kokpit GLB'sindeki gibi) — çekirdeğe birleşir
    for sx in (-1, 1):
        parts.append(_obj('apil', cyl_bm((sx * 0.080, 0.092, 0.250), (sx * 0.030, 0.142, 0.385), 0.0085, 0.0075, 8), 'steel_dark', mats))
    parts.append(_obj('hdr', box_bm((0, 0.143, 0.39), (0.075, 0.008, 0.012)), 'steel_dark', mats))
    union_all(hull, parts)
    core = hull
    # nozul boşlukları (arkadan oyulur)
    cuts = [_obj('noz', cyl_bm((x, y, -0.56), (x, y, -0.45), 0.047, 0.040, 20), 'sahin_dark', mats) for x, y in ENG]
    diff_all(core, cuts)
    adds = [_obj('lip', cyl_bm((x, y, -0.505), (x, y, -0.478), 0.056, 0.054, 20), 'gunmetal', mats) for x, y in ENG]
    union_all(core, adds)
    # ---------------- hi-poly: oluklar
    hi_core = core.copy(); hi_core.data = core.data.copy(); geo.collection('Asset').objects.link(hi_core); hi_core.name = 'hi_core'; hi_core['sd_role'] = 'hi'
    grv = []
    for z in (-0.32, -0.25, -0.18, -0.11, -0.04, 0.03, 0.10, 0.17):
        grv.append(_obj('ring', sring_bm(z, 0.0055, 0.158, 0.141, 0.146, 3.1, D), 'sahin_dark', mats))
    for x in (-0.08, -0.04, 0.04, 0.08):
        grv.append(_obj('lg', box_bm((x, 0.141 - D + 0.02, -0.12), (0.0055, 0.04, 0.48)), 'sahin_dark', mats))
    for sx in (-1, 1):
        for y in (-0.06, 0.0, 0.06):
            grv.append(_obj('ls', box_bm((sx * (0.158 - D + 0.02), y, -0.10), (0.04, 0.0055, 0.50)), 'sahin_dark', mats))
    diff_all(hi_core, grv)
    # ---------------- düşük poligon: ızgara bölme + renk bölgeleri
    bm = bmesh.new(); bm.from_mesh(core.data)
    cut_len = P.get('split_len', 0.10)
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
    for f in bm.faces:
        cb = f.calc_center_median()
        gx, gy, gz = cb.x / S, cb.z / S, -cb.y / S
        if MATS[f.material_index] != 'kasif_hull':
            continue
        if gy < -0.085 and abs(gx) < 0.14:                 # karın: koyu
            f.material_index = SLOT['sahin_dark']
        elif gy > 0.095 and abs(gx) < 0.075 and -0.38 < gz < 0.22:       # sırt orta şeridi: açık gri panel
            f.material_index = SLOT['kasif_light']
        elif -0.012 < gy < 0.012 and abs(gx) > 0.14 and -0.30 < gz < 0.30 and f.normal.x * gx > 0:   # yan ince açık bant
            f.material_index = SLOT['kasif_light']
    bm.to_mesh(core.data); bm.free()
    if P.get('bevel_m', 0) > 0:
        mb = core.modifiers.new('bev', 'BEVEL'); mb.width = P['bevel_m']; mb.segments = 2; mb.limit_method = 'ANGLE'; mb.angle_limit = math.radians(25)
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
    # nozul çekirdekleri + is, cam çerçeveleri, ışık şeritleri, radar, anten, lambalar
    for x, y in ENG:
        small('core', cyl_bm((x, y, -0.462), (x, y, -0.468), 0.030, None, 16), 'emit_pinkhot')
        small('soot', cyl_bm((x, y, -0.500), (x, y, -0.482), 0.045, 0.047, 16, cap=False), 'yuk_soot')
    small('dish', cyl_bm((0.03, 0.178, -0.08), (0.034, 0.188, -0.08), 0.045, 0.004, 18), 'kasif_light')
    small('mast', cyl_bm((0, 0.165, -0.08), (0.03, 0.182, -0.08), 0.008, None, 8), 'sahin_dark')
    small('ant', cyl_bm((-0.05, 0.14, -0.14), (-0.05, 0.23, -0.14), 0.003, None, 6), 'sahin_dark')
    small('antl', box_bm((-0.05, 0.232, -0.14), (0.010, 0.010, 0.010)), 'emit_red')
    small('turret', cyl_bm((0, 0.141, 0.06), (0, 0.158, 0.06), 0.034, None, 20), 'sahin_dark')
    small('turret2', cyl_bm((0, 0.158, 0.06), (0, 0.168, 0.06), 0.022, None, 20), 'kasif_light')
    for sx in (-1, 1):
        small('strip', box_bm((sx * 0.1565, 0.02, -0.10), (0.004, 0.005, 0.40)), 'emit_cyan')
        small('strip2', box_bm((sx * 0.1460, -0.045, 0.14), (0.004, 0.005, 0.20)), 'emit_cyan')
        small('wlamp', box_bm((sx * 0.495, 0.036, -0.12), (0.010, 0.010, 0.012)), 'emit_red' if sx > 0 else 'emit_cyan')
    for z in (-0.20, -0.02, 0.14):
        for sx in (-1, 1):
            small('hatch', box_bm((sx * 0.1565, 0.07, z), (0.004, 0.06, 0.09)), 'kasif_light')
    socks = []
    for i, (x, y) in enumerate(ENG, 1):
        socks.append({'name': 'ANCH_ENG_%d' % i, 'loc': tuple(geo.g2b(Vector((x, y, -0.465)) * S)), 'dir': (0.0, 1.0, 0.0), 'extras': {'kind': 'engine'}})
    for i, p in enumerate(((0.495, 0.036, -0.12), (-0.495, 0.036, -0.12), (-0.05, 0.232, -0.14)), 1):
        socks.append({'name': 'ANCH_NAV_%d' % i, 'loc': tuple(geo.g2b(Vector(p) * S)), 'dir': (0.0, 0.0, 1.0), 'extras': {'kind': 'nav'}})
    socks.append({'name': 'ANCH_MUZ_1', 'loc': tuple(geo.g2b(Vector((0.0, 0.168, 0.06)) * S)), 'dir': (0.0, -1.0, 0.0), 'extras': {'kind': 'muzzle'}})
    return {'objects': out_body + out_hi, 'sockets': socks}
