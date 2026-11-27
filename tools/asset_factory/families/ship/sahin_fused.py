"""Şahin — BÜTÜNLEŞİK dış model (Mehmet 2026-11-22: dış kötü → yüzey ayrıntısı, panel/kabartma, metal/boya kontrastı, kalın kanat, alt yüz). Yük/Kaşif zinciri:
gövde + kalın konik kanat + nacelle + kuyruk + stabilizer Boolean UNION → tek yüzey; nozul oyma; ızgara bölme; yüz bazlı renk bölgeleri; hi-poly oluk/kabartma bake.
Kanopi: kokpit r012/r014 damla fanus (3 enine kemer + boyuna kemer + kırmızı kenar şeridi). Oyun uzayı (x yanal, y yukarı, z burun +), L=1."""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix
from core import geo
from families.ship.yuk_ext import orient_outward
from families.ship.yuk_fused import loft_bm, box_bm, cyl_bm, tbox_bm, ring_bm, boolean, union_all, diff_all

MATS = ['sahin_hull', 'sahin_white', 'sahin_mid', 'sahin_dark', 'sahin_red', 'sahin_glass', 'yuk_rubber', 'steel_dark', 'gunmetal', 'yuk_soot', 'emit_redhot', 'emit_blue', 'emit_red', 'emit_cyan']
SLOT = {m: i for i, m in enumerate(MATS)}
S = 9.0
SECS = [(-0.30, 0.20, 0.070, 0.060, 0.016, 0.0), (-0.15, 0.28, 0.085, 0.065, 0.020, 0.0), (0.05, 0.30, 0.085, 0.062, 0.020, 0.0), (0.20, 0.24, 0.065, 0.050, 0.018, 0.0),
        (0.34, 0.144, 0.042, 0.034, 0.018, 0.0), (0.46, 0.048, 0.020, 0.018, 0.008, 0.0), (0.50, 0.016, 0.010, 0.010, 0.004, 0.0)]


def _obj(name, bm, mat, mats, role='body'):
    orient_outward(bm)
    for v in bm.verts:
        v.co = geo.g2b(Vector(v.co) * S)
    for f in bm.faces:
        f.material_index = SLOT[mat]
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for m in MATS:
        me.materials.append(mats[m])
    ob = bpy.data.objects.new(name, me)
    geo.collection('Asset').objects.link(ob)
    ob['sd_role'] = role
    return ob


def secat(z):
    for a, b in zip(SECS, SECS[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, 5))
    return SECS[0][1:5]


def wing_bm(sx):
    """kalın konik kanat: kök (x 0.05 gövde içi → 0.085 dış) kalınlık 0,05; uç (x 0.50) kalınlık 0,013, geri süpürmeli, uç aşağı sarkık"""
    bm = bmesh.new()
    def V(x, y, z):
        return bm.verts.new((sx * x, y, z))
    r = [(0.05, 0.10, -0.085), (0.05, -0.080, -0.085)]
    # kök (x=0.05): LE z=0.11, TE z=-0.08, y üst +0.012 alt -0.040
    rt = [V(0.05, 0.008, 0.11), V(0.05, 0.008, -0.08)]
    rb = [V(0.05, -0.030, 0.11), V(0.05, -0.030, -0.08)]
    tt = [V(0.40, -0.076, -0.22), V(0.40, -0.076, -0.38)]
    tb = [V(0.40, -0.086, -0.22), V(0.40, -0.086, -0.38)]
    quads = [(rt[0], rt[1], tt[1], tt[0]), (rb[1], rb[0], tb[0], tb[1]), (rt[0], tt[0], tb[0], rb[0]), (rt[1], rb[1], tb[1], tt[1]),
             (rt[0], rb[0], rb[1], rt[1]), (tt[0], tt[1], tb[1], tb[0])]
    for q in quads:
        bm.faces.new(q if sx > 0 else q[::-1])
    return bm


def stab_bm(sx):
    bm = bmesh.new()
    def V(x, y, z):
        return bm.verts.new((sx * x, y, z))
    rt = [V(0.05, 0.004, -0.30), V(0.05, 0.004, -0.42)]
    rb = [V(0.05, -0.012, -0.30), V(0.05, -0.012, -0.42)]
    tt = [V(0.22, -0.026, -0.375), V(0.22, -0.026, -0.43)]
    tb = [V(0.22, -0.034, -0.375), V(0.22, -0.034, -0.43)]
    quads = [(rt[0], rt[1], tt[1], tt[0]), (rb[1], rb[0], tb[0], tb[1]), (rt[0], tt[0], tb[0], rb[0]), (rt[1], rb[1], tb[1], tt[1]),
             (rt[0], rb[0], rb[1], rt[1]), (tt[0], tt[1], tb[1], tb[0])]
    for q in quads:
        bm.faces.new(q if sx > 0 else q[::-1])
    return bm


def fin_bm(pts_yz, th=0.018):
    bm = bmesh.new()
    a = [bm.verts.new((-th / 2, y, z)) for y, z in pts_yz]
    b = [bm.verts.new((th / 2, y, z)) for y, z in pts_yz]
    bm.faces.new(a[::-1]); bm.faces.new(b)
    n = len(pts_yz)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([a[i], a[j], b[j], b[i]])
    return bm


def build(spec, mats):
    P = spec['params']
    D = 0.0045
    hull = _obj('hull', loft_bm(SECS), 'sahin_hull', mats)
    parts = []
    for sx in (-1, 1):
        parts.append(_obj('wing', wing_bm(sx), 'sahin_hull', mats))
        parts.append(_obj('stab', stab_bm(sx), 'sahin_mid', mats))
        parts.append(_obj('wtip', box_bm((sx * 0.385, -0.087, -0.30), (0.060, 0.022, 0.185)), 'sahin_red', mats))               # kırmızı uç kapağı
        parts.append(_obj('wroot', tbox_bm((sx * 0.13, -0.010), 0.14, 0.10, 0.060, 0.034, -0.08, 0.10), 'sahin_hull', mats))      # kanat kökü kaplaması (gövdeye akıtır)
        parts.append(_obj('inl', tbox_bm((sx * 0.094, 0.012), 0.020, 0.012, 0.050, 0.040, -0.12, 0.00), 'sahin_dark', mats))     # yan hava girişi
    parts.append(_obj('glass', loft_bm([(-0.02, 0.070, 0.030, 0.004, 0.015, 0.075), (0.04, 0.108, 0.044, 0.004, 0.022, 0.075), (0.12, 0.104, 0.042, 0.004, 0.022, 0.075), (0.20, 0.060, 0.028, 0.004, 0.014, 0.075)]), 'sahin_glass', mats))
    parts.append(_obj('tail', fin_bm([(0.07, -0.26), (0.07, -0.46), (0.19, -0.49), (0.19, -0.43)]), 'sahin_hull', mats))
    parts.append(_obj('tailr', fin_bm([(0.14, -0.445), (0.19, -0.47), (0.19, -0.43)], 0.022), 'sahin_red', mats))
    ENG = [(-0.058, -0.002), (0.058, -0.002)]
    for x, y in ENG:
        parts.append(_obj('nac', cyl_bm((x, y, -0.45), (x, y, -0.25), 0.050, 0.047, 20), 'sahin_dark', mats))
        parts.append(_obj('ring', cyl_bm((x, y, -0.445), (x, y, -0.462), 0.057, None, 20), 'sahin_red', mats))
    parts.append(_obj('nbr', box_bm((0, 0.0, -0.275), (0.12, 0.09, 0.05)), 'sahin_hull', mats))
    for sx in (-1, 1):
        parts.append(_obj('gun', cyl_bm((sx * 0.016, -0.030, 0.34), (sx * 0.016, -0.030, 0.52), 0.007, 0.006, 8), 'steel_dark', mats))
        parts.append(_obj('gunb', box_bm((sx * 0.016, -0.028, 0.35), (0.026, 0.026, 0.08)), 'sahin_dark', mats))
    union_all(hull, parts)
    core = hull
    diff_all(core, [_obj('noz', cyl_bm((x, y, -0.56), (x, y, -0.455), 0.039, 0.035, 20), 'sahin_dark', mats) for x, y in ENG])
    union_all(core, [_obj('lip', cyl_bm((x, y, -0.508), (x, y, -0.482), 0.047, 0.045, 20), 'gunmetal', mats) for x, y in ENG])
    # ---------------- hi-poly oluk + kabartma
    hi_core = core.copy(); hi_core.data = core.data.copy(); geo.collection('Asset').objects.link(hi_core); hi_core.name = 'hi_core'; hi_core['sd_role'] = 'hi'
    grv = []
    for z in (-0.28, -0.24, -0.20, -0.16, -0.12, -0.08, -0.04, 0.0, 0.04, 0.08, 0.12, 0.16, 0.20, 0.24, 0.28):
        w, hu, hd, ch = secat(z)
        grv.append(_obj('ring', ring_bm(z, 0.0045, w, hu, hd, ch, D), 'sahin_dark', mats))
    for x in (-0.07, -0.035, 0.035, 0.07):
        grv.append(_obj('lg', box_bm((x, 0.085 - D + 0.02, -0.05), (0.0045, 0.04, 0.58)), 'sahin_dark', mats))
    for sx in (-1, 1):
        for y in (-0.03, 0.01, 0.045):
            grv.append(_obj('ls', box_bm((sx * (0.175 - D + 0.02), y, -0.05), (0.04, 0.0045, 0.50)), 'sahin_dark', mats))
        for t in (0.3, 0.55, 0.8):                                                             # kanat üstü/alt panel olukları (kanat boyunca)
            grv.append(_obj('wg', box_bm((sx * (0.05 + 0.35 * t), 0.0 - 0.09 * t + 0.016 * (1 - t), -0.05 - 0.17 * t), (0.0045, 0.05, 0.18)), 'sahin_dark', mats))
    diff_all(hi_core, grv)
    # ---------------- ızgara bölme + renk bölgeleri
    bm = bmesh.new(); bm.from_mesh(core.data)
    cl = P.get('split_len', 0.065)
    for _ in range(2):
        groups = {}
        for e in bm.edges:
            Lg = (e.verts[0].co - e.verts[1].co).length / S
            c = int(Lg / cl)
            if c >= 1 and any(f.calc_area() / (S * S) > (cl * 0.6) ** 2 for f in e.link_faces):
                groups.setdefault(min(c, 8), []).append(e)
        for c, es in groups.items():
            es = [e for e in es if e.is_valid]
            if es:
                bmesh.ops.subdivide_edges(bm, edges=es, cuts=c, use_grid_fill=True)
    for f in bm.faces:
        cb = f.calc_center_median()
        gx, gy, gz = cb.x / S, cb.z / S, -cb.y / S
        cur = MATS[f.material_index]
        if cur != 'sahin_hull':
            continue
        if gy < -0.048 and abs(gx) < 0.16 and gz > -0.30:      # karın: koyu
            f.material_index = SLOT['sahin_dark']
        elif gy > 0.078 and abs(gx) < 0.06 and -0.28 < gz < 0.30:   # sırt şeridi: beyaz
            f.material_index = SLOT['sahin_white']
        elif abs(gx) > 0.10 and abs(gx) < 0.185 and 0.0 < gy < 0.05 and -0.28 < gz < 0.18:   # yan şerit: orta gri
            f.material_index = SLOT['sahin_mid']
        elif gz > 0.36:                                         # burun: orta gri
            f.material_index = SLOT['sahin_mid']
        elif abs(gx) > 0.0 and gy < -0.03 and gz < -0.05 and abs(gx) > 0.12:     # kanat altı: koyu
            f.material_index = SLOT['sahin_dark']
        else:                                                   # panel bazlı renk çeşitliliği (değiştirilmiş/boyanmış paneller)
            h = (int((gx + 1) / 0.085) * 73856093 ^ int((gy + 1) / 0.045) * 19349663 ^ int((gz + 1) / 0.085) * 83492791) % 23
            if h in (0, 1, 2):
                f.material_index = SLOT['sahin_white']
            elif h in (3, 4):
                f.material_index = SLOT['sahin_mid']
            elif h == 5:
                f.material_index = SLOT['sahin_dark']
            elif h == 6:
                f.material_index = SLOT['sahin_red']
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
    # kanopi: damla cam + 3 enine kemer + boyuna kemer + kırmızı kenar şeridi + taban contası

    for z, w, hu in ((0.012, 0.086, 0.054), (0.08, 0.108, 0.064), (0.155, 0.086, 0.054)):
        pts = [(math.cos(t) * (w / 2), 0.075 + math.sin(t) * hu * 0.7) for t in [math.pi * i / 8 for i in range(9)]]
        for p, q in zip(pts, pts[1:]):
            small('arch', cyl_bm((p[0], p[1], z), (q[0], q[1], z), 0.0022, None, 6), 'steel_dark')
    for p, q in (((0, 0.139, -0.01), (0, 0.143, 0.09)), ((0, 0.143, 0.09), (0, 0.124, 0.2))):
        small('arch2', cyl_bm(p, q, 0.0032, None, 6), 'steel_dark')
    for sx in (-1, 1):
        small('rstrip', box_bm((sx * 0.047, 0.076, 0.095), (0.003, 0.003, 0.235)), 'sahin_red')
    for x, y in ENG:
        small('core', cyl_bm((x, y, -0.462), (x, y, -0.468), 0.032, None, 16), 'emit_redhot')
        small('blue', cyl_bm((x, y, -0.4625), (x, y, -0.4655), 0.014, None, 12), 'emit_blue')
        small('soot', cyl_bm((x, y, -0.505), (x, y, -0.485), 0.043, 0.045, 16, cap=False), 'yuk_soot')
    small('navtail', box_bm((0, 0.185, -0.485), (0.016, 0.010, 0.010)), 'emit_red')
    socks = []
    for i, (x, y) in enumerate(ENG, 1):
        socks.append({'name': 'ANCH_ENG_%d' % i, 'loc': tuple(geo.g2b(Vector((x, y, -0.466)) * S)), 'dir': (0.0, 1.0, 0.0), 'extras': {'kind': 'engine'}})
    for i, p in enumerate(((0.40, -0.087, -0.30), (-0.40, -0.087, -0.30), (0.0, 0.185, -0.485)), 1):
        socks.append({'name': 'ANCH_NAV_%d' % i, 'loc': tuple(geo.g2b(Vector(p) * S)), 'dir': (0.0, 0.0, 1.0), 'extras': {'kind': 'nav'}})
    for i, sx in enumerate((-1, 1), 1):
        socks.append({'name': 'ANCH_MUZ_%d' % i, 'loc': tuple(geo.g2b(Vector((sx * 0.016, -0.030, 0.52)) * S)), 'dir': (0.0, -1.0, 0.0), 'extras': {'kind': 'muzzle'}})
    return {'objects': out_body + out_hi, 'sockets': socks}
