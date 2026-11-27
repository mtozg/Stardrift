"""NPC sert-yüzey ailesi (Mehmet referansı: endüstriyel modüler gemi; gerçekçilik kontrol listesi a–g). kind: akbaba | (kurt, yagmaci … sonraki turlar).
AKBABA (konsept A "Çalıntı Çekirdek", Lead/Mehmet seçimi 2026-11-27): önde dar kokpit kapsülü, arkada sağa ofsetli dev sürücü çekirdeği + kafes kule + nozul, kafes omurga,
silindirik yakıt tankı (kayışlı), yama motor (sol), yamalı zırh levhaları, kanca fırlatıcılar. Palet: kirli açık gri + 1 vurgu (turuncu), çelik/gunmetal/ısı malzemesi.
Zincir: loft kütleler → Boolean UNION → nozul oyma → ızgara bölme → bölge malzeme → hi-poly kabartma → bake. Birim metre (oyun uzayı, burun +z)."""
import math
import bpy, bmesh
from mathutils import Vector
from core import geo
from families.ship.yuk_ext import orient_outward
from families.ship.yuk_fused import box_bm, boolean, union_all, diff_all, ring_bm
from families.ship.sahin_catal import loft, loft_x, plate, tube

MATS = ['pir_gray', 'pir_gray2', 'pir_orange', 'cat_titan', 'cat_gun', 'cat_heat', 'sahin_glass', 'emit_redhot', 'emit_blue', 'emit_red']
SLOT = {m: i for i, m in enumerate(MATS)}


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


def _rot_z(bm, ang, c):
    from mathutils import Matrix
    M = Matrix.Translation(Vector(c)) @ Matrix.Rotation(ang, 4, 'Z') @ Matrix.Translation(-Vector(c))
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return bm


def build(spec, mats):
    return build_akbaba(spec, mats)


def build_akbaba(spec, mats):
    P = spec['params']
    CX = 0.35                                    # çekirdek ofseti (sağ)
    D = 0.012
    # ---------------------------------------------------------------- ana kütleler
    cap_s = [(0.9, 0.34, 0.30, 0.28, 2.8, 0, 0.10), (1.8, 0.56, 0.45, 0.38, 3.0, 0, 0.10), (3.0, 0.50, 0.40, 0.34, 3.0, 0, 0.08), (4.0, 0.26, 0.20, 0.19, 2.6, 0, 0.05), (4.7, 0.10, 0.09, 0.09, 2.3, 0, 0.04)]
    cap = _obj('cap', loft(cap_s), 'pir_gray', mats)

    def cap_w(z):
        for a, b in zip(cap_s, cap_s[1:]):
            if a[0] <= z <= b[0]:
                return a[1] + (b[1] - a[1]) * (z - a[0]) / (b[0] - a[0])
        return cap_s[0][1]
    parts = []
    # çekirdek (silindirik, sağa ofsetli) + halka kuşakları gövdeye dahil
    core_s = [(-3.5, 0.80, 0.80, 0.80, 2.0, CX, 0.0), (-2.9, 1.15, 1.15, 1.15, 2.0, CX, 0.0), (-1.6, 1.15, 1.15, 1.15, 2.0, CX, 0.0), (-0.6, 0.80, 0.80, 0.80, 2.0, CX, 0.0), (-0.1, 0.30, 0.30, 0.30, 2.0, CX, 0.0)]
    parts.append(_obj('core', loft(core_s, 48), 'pir_gray', mats))
    # omurga kirişi (kapsül ↔ çekirdek)
    parts.append(_obj('beam', loft([(-0.5, 0.36, 0.30, 0.28, 3.0, 0.12, 0.0), (1.2, 0.34, 0.28, 0.26, 3.0, 0.06, 0.04)]), 'cat_titan', mats))
    # yakıt tankı (sol, kayışlı) ve yama motor
    parts.append(_obj('tank', loft([(-1.6, 0.26, 0.26, 0.26, 2.0, -0.95, -0.50), (-0.9, 0.34, 0.34, 0.34, 2.0, -0.95, -0.50), (0.9, 0.34, 0.34, 0.34, 2.0, -0.95, -0.50), (1.4, 0.20, 0.20, 0.20, 2.0, -0.95, -0.50)], 28), 'pir_orange', mats))
    parts.append(_obj('tankmnt', box_bm((-0.62, -0.30, 0.0), (0.7, 0.14, 0.9)), 'cat_titan', mats))
    parts.append(_obj('eng2', loft([(-2.9, 0.38, 0.38, 0.38, 2.0, -1.55, -0.20), (-1.6, 0.42, 0.42, 0.42, 2.0, -1.55, -0.20), (-0.9, 0.26, 0.26, 0.26, 2.0, -1.55, -0.20)], 28), 'cat_titan', mats))
    parts.append(_obj('eng2mnt', box_bm((-0.95, -0.18, -1.4), (1.0, 0.18, 1.0)), 'cat_titan', mats))
    # yamalı zırh levhaları (çekirdek çevresi, asimetrik; kalın)
    for (x, y, z, sx_, sy_, sz_, a, key) in ((-0.95, 0.60, -1.2, 0.12, 0.9, 1.5, 0.20, 'pir_gray2'), (1.55, 0.45, -1.0, 0.12, 0.95, 1.3, -0.25, 'pir_gray'), (1.1, -0.70, -1.3, 0.12, 0.8, 1.4, 0.30, 'pir_gray2')):
        parts.append(_obj('armor', _rot_z(box_bm((x, y, z), (sx_, sy_, sz_)), a, (x, y, z)), key, mats))
    union_all(cap, parts)
    core = cap
    diff_all(core, [_obj('noz', tube((CX, 0.0, -4.4), (CX, 0.0, -3.85), 0.55, 0.50, 36), 'cat_heat', mats), _obj('noz2', tube((-1.55, -0.20, -3.5), (-1.55, -0.20, -2.95), 0.30, 0.27, 28), 'cat_heat', mats)])
    # bakım kapakları/oyuklar (oyma)
    cuts = []
    for z in (1.2, 2.2, 3.1):
        cuts.append(_obj('hat', box_bm((0.0, 0.52 - (z - 1.2) * 0.04, z), (0.34, 0.05, 0.30)), 'cat_gun', mats))
    for k in range(5):
        cuts.append(_obj('louv', box_bm((CX, 1.17, -3.1 + k * 0.45), (0.9, 0.06, 0.12)), 'cat_gun', mats))
    diff_all(core, cuts)
    # ---------------------------------------------------------------- hi-poly oluk
    hi_core = core.copy(); hi_core.data = core.data.copy(); geo.collection('Asset').objects.link(hi_core); hi_core.name = 'hi_core'; hi_core['sd_role'] = 'hi'
    grv = []
    for z in (-3.2, -2.6, -2.0, -1.4, -0.8):                                           # çekirdek halka dikişleri (daire: ring_bm sekizgen, dişli oluk verir)
        grv.append(_obj('rg', ring_bm(z, 0.012, 2.3, 1.15, 1.15, 0.5, D), 'cat_gun', mats))
        for v in grv[-1].data.vertices:
            v.co.x += CX
    for z in (1.4, 2.0, 2.6, 3.2):
        w = cap_w(z)
        grv.append(_obj('rc', ring_bm(z, 0.012, w * 2, 0.40, 0.34, 0.14, D), 'cat_gun', mats))
    for sx in (-1, 1):
        grv.append(_obj('cl', box_bm((sx * 0.46, 0.46, 2.0), (0.012, 0.08, 1.9)), 'cat_gun', mats))
    diff_all(hi_core, grv)
    # ---------------------------------------------------------------- ızgara bölme + bölge malzeme
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
        cb = f.calc_center_median(); gx, gy, gz = cb.x, cb.z, -cb.y
        cur = MATS[f.material_index]
        if cur == 'pir_gray':
            if gz > 3.5:
                f.material_index = SLOT['pir_orange']                                  # kapsül burnu: turuncu (uzaktan tanıma)
            elif gz < -3.4 and abs(gx - CX) < 1.3:
                f.material_index = SLOT['cat_heat']                                    # çekirdek arkası ısı bölgesi
            elif gy < -0.1 and gz > 0.5:
                f.material_index = SLOT['pir_gray2']
            else:
                h = (int((gx + 4.0) / 0.55) * 73856093 ^ int((gz + 6.0) / 0.5) * 19349663 ^ int((gy + 2.0) / 0.4) * 83492791) % 16
                if h in (0, 1, 2):
                    f.material_index = SLOT['pir_gray2']
                elif h == 3:
                    f.material_index = SLOT['pir_orange']                              # turuncu yama paneli (az)
                elif h == 4:
                    f.material_index = SLOT['cat_titan']                               # bakım kapağı
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
    # ---------------------------------------------------------------- kokpit kanopisi: alçak, gömülü, kasalı
    small('cframe', loft([(1.2, 0.20, 0.05, 0.10, 2.6, 0, 0.41), (1.9, 0.46, 0.085, 0.12, 2.8, 0, 0.465), (2.6, 0.42, 0.075, 0.12, 2.8, 0, 0.42), (3.3, 0.20, 0.04, 0.08, 2.4, 0, 0.37)]), 'cat_titan')
    small('glass', loft([(1.4, 0.24, 0.07, 0.0, 2.6, 0, 0.42), (1.9, 0.40, 0.10, 0.0, 2.8, 0, 0.465), (2.6, 0.36, 0.09, 0.0, 2.8, 0, 0.42), (3.2, 0.16, 0.05, 0.0, 2.6, 0, 0.38)]), 'sahin_glass')
    # ---------------------------------------------------------------- çekirdek nozulu + kafes kule (referans: kafes/lattice motor kuleleri)
    small('bell', tube((CX, 0.0, -4.4), (CX, 0.0, -3.9), 0.62, 0.52, 40, cap=False), 'cat_heat')
    small('inner', tube((CX, 0.0, -4.32), (CX, 0.0, -4.28), 0.44, None, 36), 'cat_gun')
    small('ncore', tube((CX, 0.0, -4.30), (CX, 0.0, -4.27), 0.26, None, 28), 'emit_redhot')
    small('nblue', tube((CX, 0.0, -4.305), (CX, 0.0, -4.295), 0.10, None, 20), 'emit_blue')
    small('nlip', tube((CX, 0.0, -4.50), (CX, 0.0, -4.42), 0.66, 0.64, 40, cap=False), 'cat_titan')
    for k in range(6):                                                                   # kafes kule çubukları: çekirdek arkasından nozul halkasına
        a = k * math.pi / 3
        small('lat', tube((CX + math.cos(a) * 1.0, math.sin(a) * 1.0, -3.4), (CX + math.cos(a) * 0.80, math.sin(a) * 0.80, -4.45), 0.04, None, 8), 'cat_gun')
    for z in (-3.75, -4.1):
        small('latr', tube((CX, 0.0, z), (CX, 0.0, z + 0.03), 0.92 - (z + 3.75) * -0.2, None, 36, cap=False), 'cat_gun')
    for k in range(8):                                                                   # çaprazlar
        a = k * math.pi / 4
        a2 = a + math.pi / 6
        small('latx', tube((CX + math.cos(a) * 0.95, math.sin(a) * 0.95, -3.55), (CX + math.cos(a2) * 0.85, math.sin(a2) * 0.85, -4.2), 0.025, None, 6), 'cat_gun')
    # çekirdek kuşakları (halka bantları) + soğutma levhaları
    for k in range(8):
        small('band', tube((CX, 0.0, -3.35 + k * 0.28), (CX, 0.0, -3.35 + k * 0.28 + 0.06), 1.20, None, 48, cap=False), 'cat_gun')
    for sy in (-1, 1):
        small('radp', box_bm((CX, sy * 1.18, -2.2), (1.4, 0.07, 2.2)), 'pir_gray2')
        for q in range(4):
            small('radr', box_bm((CX - 0.5 + q * 0.33, sy * 1.225, -2.2), (0.04, 0.04, 2.0)), 'cat_titan')
    # yama motor nozulu ve kafes
    small('bell2', tube((-1.55, -0.20, -3.5), (-1.55, -0.20, -3.0), 0.36, 0.30, 32, cap=False), 'cat_heat')
    small('ncore2', tube((-1.55, -0.20, -3.42), (-1.55, -0.20, -3.40), 0.18, None, 24), 'emit_redhot')
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        small('lat2', tube((-1.55 + math.cos(a) * 0.42, -0.20 + math.sin(a) * 0.42, -2.8), (-1.55 + math.cos(a) * 0.38, -0.20 + math.sin(a) * 0.38, -3.5), 0.025, None, 6), 'cat_gun')
    # ---------------------------------------------------------------- kafes omurga + tank kayışları + bağlantı donanımı
    cs = [(-0.28, -0.22), (0.28, -0.22), (0.28, 0.22), (-0.28, 0.22)]
    for cx_, cy_ in cs:
        small('lon', tube((cx_ + 0.1, cy_, -0.1), (cx_, cy_, 1.3), 0.05, None, 10), 'cat_titan')
    for z in (0.0, 0.5, 1.0):
        for a, b in zip(cs, cs[1:] + cs[:1]):
            small('rng', tube((a[0] + 0.08, a[1], z), (b[0] + 0.08, b[1], z), 0.03, None, 8), 'cat_gun')
    for k in range(4):
        small('strap', tube((-0.95, -0.50, -0.7 + k * 0.5), (-0.95, -0.50, -0.7 + k * 0.5 + 0.08), 0.355, None, 28, cap=False), 'cat_titan')
    for q in range(2):
        small('tankcap', tube((-0.95, -0.50, -1.62 + q * 3.0), (-0.95, -0.50, -1.58 + q * 3.0), 0.27, None, 20), 'cat_gun')
    # ---------------------------------------------------------------- insan ölçeği ipuçları: pencere, kapak+tutamak, korkuluk, merdiven, kanca/tambur
    for sx in (-1, 1):
        for k in range(4):
            zz = 1.35 + k * 0.28
            small('win', box_bm((sx * (cap_w(zz) - 0.004), 0.10, zz), (0.03, 0.08, 0.14)), 'emit_blue')
        small('hatchp', box_bm((sx * (cap_w(2.0) - 0.004), -0.10, 2.0), (0.035, 0.30, 0.34)), 'cat_titan')
        small('hatchh', box_bm((sx * (cap_w(2.0) + 0.012), -0.10, 2.0), (0.02, 0.10, 0.02)), 'cat_gun')
        small('hook', tube((sx * 0.30, -0.30, 2.6), (sx * 0.40, -0.35, 4.3), 0.07, 0.05, 12), 'cat_gun')
        small('hookt', box_bm((sx * 0.40, -0.35, 4.35), (0.2, 0.05, 0.12)), 'cat_titan')
        small('drum', tube((sx * 0.20, -0.28, 2.40), (sx * 0.20, -0.28, 2.62), 0.15, None, 16), 'cat_titan')
    small('door', box_bm((cap_w(1.8) - 0.012, 0.05, 1.8), (0.03, 0.55, 0.45)), 'cat_gun')
    small('doorh', box_bm((cap_w(1.8) + 0.012, 0.05, 1.95), (0.02, 0.12, 0.03)), 'cat_titan')
    for q in range(3):
        small('step', box_bm((cap_w(1.8) + 0.004, -0.28 - q * 0.15, 1.8), (0.05, 0.03, 0.26)), 'cat_titan')
    for q in range(4):                                                                   # çekirdek üzerinde korkuluk
        small('post', tube((CX - 0.5 + q * 0.34, 1.16, -1.4), (CX - 0.5 + q * 0.34, 1.34, -1.4), 0.014, None, 6), 'cat_gun')
    small('rail', tube((CX - 0.5, 1.34, -1.4), (CX + 0.52, 1.34, -1.4), 0.012, None, 6), 'cat_gun')
    # turuncu hatch panelleri (X çaprazlı, referanstaki gibi): çekirdek yanı ve tank
    for (x, y, z, ang) in ((CX + 1.17, 0.0, -1.2, 0.0), (CX - 1.17, 0.0, -2.4, 0.0)):
        small('ohatch', box_bm((x, y, z), (0.035, 0.7, 0.9)), 'pir_orange')
        small('oxa', _rot_z(box_bm((x + (0.02 if x > 0 else -0.02), y, z), (0.02, 0.06, 1.1)), 0.7, (x, y, z)), 'cat_gun')
    small('ohatch2', box_bm((-0.95, -0.17, 0.2), (0.7, 0.025, 0.7)), 'pir_orange')
    small('ant', tube((0.0, 0.56, 2.2), (0.0, 0.95, 2.0), 0.014, 0.007, 6), 'cat_gun')
    small('ant2', tube((CX, 1.18, -1.0), (CX + 0.1, 1.7, -1.1), 0.016, 0.008, 6), 'cat_gun')
    for z in (1.5, 2.5):
        small('mark', box_bm((0.0, 0.40 + (z - 1.5) * -0.04, z), (0.50, 0.012, 0.12)), 'pir_orange')
    small('nav1', box_bm((0.0, 0.58, 4.2), (0.05, 0.05, 0.05)), 'emit_red')
    small('nav2', box_bm((-1.55, 0.35, -2.9), (0.05, 0.05, 0.05)), 'emit_red')
    # alt gövde: ısı kalkanı plakaları, iniş ayağı yuvaları, kablo kanalı
    for z in (0.6, 1.6, 2.6):
        small('bplate', box_bm((0.0, 0.10 - 0.36 - 0.0, z), (0.52, 0.03, 0.8)), 'cat_heat')
    for sx in (-1, 1):
        small('gleg', tube((sx * 0.35, -0.30, 1.5), (sx * 0.42, -0.62, 1.5), 0.05, 0.06, 10), 'cat_titan')
        small('gfoot', box_bm((sx * 0.42, -0.64, 1.5), (0.22, 0.03, 0.30)), 'cat_gun')
    small('gleg3', tube((CX, -1.10, -2.4), (CX, -1.34, -2.4), 0.07, 0.08, 10), 'cat_titan')
    small('gfoot3', box_bm((CX, -1.36, -2.4), (0.30, 0.03, 0.34)), 'cat_gun')
    small('tray', tube((0.3, -0.34, 0.2), (0.3, -0.34, 3.4), 0.025, None, 8), 'cat_gun')
    # ---------------------------------------------------------------- soketler
    socks = [{'name': 'ANCH_ENG_1', 'loc': tuple(geo.g2b(Vector((CX, 0.0, -4.30)))), 'dir': (0.0, 1.0, 0.0), 'extras': {'kind': 'engine'}},
             {'name': 'ANCH_ENG_2', 'loc': tuple(geo.g2b(Vector((-1.55, -0.20, -3.42)))), 'dir': (0.0, 1.0, 0.0), 'extras': {'kind': 'engine'}}]
    for i, p in enumerate(((0.0, 0.58, 4.2), (-1.55, 0.35, -2.9), (CX, 1.34, -1.4)), 1):
        socks.append({'name': 'ANCH_NAV_%d' % i, 'loc': tuple(geo.g2b(Vector(p))), 'dir': (0.0, 0.0, 1.0), 'extras': {'kind': 'nav'}})
    for i, p in enumerate(((-0.4, -0.35, 4.35), (0.4, -0.35, 4.35)), 1):
        socks.append({'name': 'ANCH_MUZ_%d' % i, 'loc': tuple(geo.g2b(Vector(p))), 'dir': (0.0, -1.0, 0.0), 'extras': {'kind': 'muzzle'}})
    return {'objects': out_body + out_hi, 'sockets': socks}
