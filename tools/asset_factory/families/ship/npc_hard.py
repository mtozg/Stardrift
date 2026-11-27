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

MATS = ['pir_gray', 'pir_gray2', 'pir_orange', 'pir_titan', 'pir_gun', 'pir_heat', 'pir_glass', 'emit_redhot', 'emit_blue', 'emit_red', 'pir_white', 'pir_blue', 'pir_yellow']
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
    return {'akbaba': build_akbaba, 'kurt': build_kurt, 'yagmaci': build_yagmaci, 'corvette': lambda sp, m: build_generic(sp, m, CFG['corvette']), 'cargo': lambda sp, m: build_generic(sp, m, CFG['cargo']), 'tanker': lambda sp, m: build_generic(sp, m, CFG['tanker']), 'courier': lambda sp, m: build_generic(sp, m, CFG['courier']), 'mining': lambda sp, m: build_generic(sp, m, CFG['mining'])}[spec['params'].get('kind', 'akbaba')](spec, mats)


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
    parts.append(_obj('beam', loft([(-0.5, 0.36, 0.30, 0.28, 3.0, 0.12, 0.0), (1.2, 0.34, 0.28, 0.26, 3.0, 0.06, 0.04)]), 'pir_titan', mats))
    # yakıt tankı (sol, kayışlı) ve yama motor
    parts.append(_obj('tank', loft([(-1.6, 0.26, 0.26, 0.26, 2.0, -0.95, -0.50), (-0.9, 0.34, 0.34, 0.34, 2.0, -0.95, -0.50), (0.9, 0.34, 0.34, 0.34, 2.0, -0.95, -0.50), (1.4, 0.20, 0.20, 0.20, 2.0, -0.95, -0.50)], 28), 'pir_orange', mats))
    parts.append(_obj('tankmnt', box_bm((-0.62, -0.30, 0.0), (0.7, 0.14, 0.9)), 'pir_titan', mats))
    parts.append(_obj('eng2', loft([(-2.9, 0.38, 0.38, 0.38, 2.0, -1.55, -0.20), (-1.6, 0.42, 0.42, 0.42, 2.0, -1.55, -0.20), (-0.9, 0.26, 0.26, 0.26, 2.0, -1.55, -0.20)], 28), 'pir_titan', mats))
    parts.append(_obj('eng2mnt', box_bm((-0.95, -0.18, -1.4), (1.0, 0.18, 1.0)), 'pir_titan', mats))
    union_all(cap, parts)
    core = cap
    diff_all(core, [_obj('noz', tube((CX, 0.0, -4.4), (CX, 0.0, -3.85), 0.55, 0.50, 36), 'pir_heat', mats), _obj('noz2', tube((-1.55, -0.20, -3.5), (-1.55, -0.20, -2.95), 0.30, 0.27, 28), 'pir_heat', mats)])
    # bakım kapakları/oyuklar (oyma)
    cuts = []
    for z in (1.2, 2.2, 3.1):
        cuts.append(_obj('hat', box_bm((0.0, 0.52 - (z - 1.2) * 0.04, z), (0.34, 0.05, 0.30)), 'pir_gun', mats))
    for k in range(5):
        cuts.append(_obj('louv', box_bm((CX, 1.17, -3.1 + k * 0.45), (0.9, 0.06, 0.12)), 'pir_gun', mats))
    diff_all(core, cuts)
    # ---------------------------------------------------------------- hi-poly oluk
    hi_core = core.copy(); hi_core.data = core.data.copy(); geo.collection('Asset').objects.link(hi_core); hi_core.name = 'hi_core'; hi_core['sd_role'] = 'hi'
    grv = []
    for z in (-3.2, -2.6, -2.0, -1.4, -0.8):                                           # çekirdek halka dikişleri (daire: ring_bm sekizgen, dişli oluk verir)
        grv.append(_obj('rg', ring_bm(z, 0.012, 2.3, 1.15, 1.15, 0.5, D), 'pir_gun', mats))
        for v in grv[-1].data.vertices:
            v.co.x += CX
    for z in (1.4, 2.0, 2.6, 3.2):
        w = cap_w(z)
        grv.append(_obj('rc', ring_bm(z, 0.012, w * 2, 0.40, 0.34, 0.14, D), 'pir_gun', mats))
    for sx in (-1, 1):
        grv.append(_obj('cl', box_bm((sx * 0.46, 0.46, 2.0), (0.012, 0.08, 1.9)), 'pir_gun', mats))
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
                f.material_index = SLOT['pir_heat']                                    # çekirdek arkası ısı bölgesi
            elif gy < -0.1 and gz > 0.5:
                f.material_index = SLOT['pir_gray2']
            else:
                h = (int((gx + 4.0) / 0.55) * 73856093 ^ int((gz + 6.0) / 0.5) * 19349663 ^ int((gy + 2.0) / 0.4) * 83492791) % 16
                if h in (0, 1, 2):
                    f.material_index = SLOT['pir_gray2']
                elif h == 3:
                    f.material_index = SLOT['pir_orange']                              # turuncu yama paneli (az)
                elif h == 4:
                    f.material_index = SLOT['pir_titan']                               # bakım kapağı
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
    small('cframe', loft([(1.2, 0.20, 0.05, 0.10, 2.6, 0, 0.41), (1.9, 0.46, 0.085, 0.12, 2.8, 0, 0.465), (2.6, 0.42, 0.075, 0.12, 2.8, 0, 0.42), (3.3, 0.20, 0.04, 0.08, 2.4, 0, 0.37)]), 'pir_titan')
    small('glass', loft([(1.4, 0.24, 0.07, 0.0, 2.6, 0, 0.42), (1.9, 0.40, 0.10, 0.0, 2.8, 0, 0.465), (2.6, 0.36, 0.09, 0.0, 2.8, 0, 0.42), (3.2, 0.16, 0.05, 0.0, 2.6, 0, 0.38)]), 'pir_glass')
    # ---------------------------------------------------------------- çekirdek nozulu + kafes kule (referans: kafes/lattice motor kuleleri)
    small('bell', tube((CX, 0.0, -4.4), (CX, 0.0, -3.9), 0.62, 0.52, 40, cap=False), 'pir_heat')
    small('inner', tube((CX, 0.0, -4.32), (CX, 0.0, -4.28), 0.44, None, 36), 'pir_gun')
    small('ncore', tube((CX, 0.0, -4.30), (CX, 0.0, -4.27), 0.26, None, 28), 'emit_redhot')
    small('nblue', tube((CX, 0.0, -4.305), (CX, 0.0, -4.295), 0.10, None, 20), 'emit_blue')
    small('nlip', tube((CX, 0.0, -4.50), (CX, 0.0, -4.42), 0.66, 0.64, 40, cap=False), 'pir_titan')
    for k in range(6):                                                                   # kafes kule çubukları: çekirdek arkasından nozul halkasına
        a = k * math.pi / 3
        small('lat', tube((CX + math.cos(a) * 1.0, math.sin(a) * 1.0, -3.4), (CX + math.cos(a) * 0.80, math.sin(a) * 0.80, -4.45), 0.075, None, 8), 'pir_gun')
    for z in (-3.75, -4.1):
        small('latr', tube((CX, 0.0, z), (CX, 0.0, z + 0.03), 0.92 - (z + 3.75) * -0.2, None, 36, cap=False), 'pir_gun')
    # çekirdek kuşakları (halka bantları) + soğutma levhaları
    for k in range(8):
        small('band', tube((CX, 0.0, -3.35 + k * 0.28), (CX, 0.0, -3.35 + k * 0.28 + 0.06), 1.20, None, 48, cap=False), 'pir_gun')
    for sy in (-1, 1):                                                                   # radyatör: çekirdek üstü/altı dikey kanatçıklar (masa değil)
        small('radbase', box_bm((CX, sy * 1.17, -2.2), (1.5, 0.05, 2.2)), 'pir_gun')
        for q in range(3):
            small('radfin', box_bm((CX - 0.42 + q * 0.42, sy * 1.42, -2.2), (0.07, 0.5, 2.0)), 'pir_gray2')
            small('radfint', box_bm((CX - 0.42 + q * 0.42, sy * 1.69, -2.2), (0.09, 0.05, 2.0)), 'pir_orange')
        small('radpipe', tube((CX - 0.7, sy * 1.2, -3.15), (CX + 0.7, sy * 1.2, -3.15), 0.05, None, 10), 'pir_gun')
    # yama motor nozulu ve kafes
    small('bell2', tube((-1.55, -0.20, -3.5), (-1.55, -0.20, -3.0), 0.36, 0.30, 32, cap=False), 'pir_heat')
    small('ncore2', tube((-1.55, -0.20, -3.42), (-1.55, -0.20, -3.40), 0.18, None, 24), 'emit_redhot')
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        small('lat2', tube((-1.55 + math.cos(a) * 0.42, -0.20 + math.sin(a) * 0.42, -2.8), (-1.55 + math.cos(a) * 0.38, -0.20 + math.sin(a) * 0.38, -3.5), 0.025, None, 6), 'pir_gun')
    # ---------------------------------------------------------------- kafes omurga + tank kayışları + bağlantı donanımı
    cs = [(-0.28, -0.22), (0.28, -0.22), (0.28, 0.22), (-0.28, 0.22)]
    for cx_, cy_ in cs:
        small('lon', tube((cx_ + 0.1, cy_, -0.1), (cx_, cy_, 1.3), 0.05, None, 10), 'pir_titan')
    for z in (0.0, 0.5, 1.0):
        for a, b in zip(cs, cs[1:] + cs[:1]):
            small('rng', tube((a[0] + 0.08, a[1], z), (b[0] + 0.08, b[1], z), 0.03, None, 8), 'pir_gun')
    for k in range(4):
        small('strap', tube((-0.95, -0.50, -0.7 + k * 0.5), (-0.95, -0.50, -0.7 + k * 0.5 + 0.08), 0.355, None, 28, cap=False), 'pir_titan')
    for q in range(2):
        small('tankcap', tube((-0.95, -0.50, -1.62 + q * 3.0), (-0.95, -0.50, -1.58 + q * 3.0), 0.27, None, 20), 'pir_gun')
    # ---------------------------------------------------------------- insan ölçeği ipuçları: pencere, kapak+tutamak, korkuluk, merdiven, kanca/tambur
    for sx in (-1, 1):
        for k in range(4):
            zz = 1.35 + k * 0.28
            small('win', box_bm((sx * (cap_w(zz) - 0.004), 0.10, zz), (0.03, 0.08, 0.14)), 'emit_blue')
        small('hatchp', box_bm((sx * (cap_w(2.0) - 0.004), -0.10, 2.0), (0.035, 0.30, 0.34)), 'pir_titan')
        small('hatchh', box_bm((sx * (cap_w(2.0) + 0.012), -0.10, 2.0), (0.02, 0.10, 0.02)), 'pir_gun')
        small('hook', tube((sx * 0.30, -0.30, 2.6), (sx * 0.40, -0.35, 4.3), 0.07, 0.05, 12), 'pir_gun')
        small('hookt', box_bm((sx * 0.40, -0.35, 4.35), (0.2, 0.05, 0.12)), 'pir_titan')
        small('drum', tube((sx * 0.20, -0.28, 2.40), (sx * 0.20, -0.28, 2.62), 0.15, None, 16), 'pir_titan')
    small('door', box_bm((cap_w(1.8) - 0.012, 0.05, 1.8), (0.03, 0.55, 0.45)), 'pir_gun')
    small('doorh', box_bm((cap_w(1.8) + 0.012, 0.05, 1.95), (0.02, 0.12, 0.03)), 'pir_titan')
    for q in range(3):
        small('step', box_bm((cap_w(1.8) + 0.004, -0.28 - q * 0.15, 1.8), (0.05, 0.03, 0.26)), 'pir_titan')
    for q in range(4):                                                                   # çekirdek üzerinde korkuluk
        small('post', tube((CX - 0.5 + q * 0.34, 1.16, -1.4), (CX - 0.5 + q * 0.34, 1.34, -1.4), 0.014, None, 6), 'pir_gun')
    small('rail', tube((CX - 0.5, 1.34, -1.4), (CX + 0.52, 1.34, -1.4), 0.012, None, 6), 'pir_gun')
    # turuncu hatch panelleri (X çaprazlı, referanstaki gibi): çekirdek yanı ve tank
    for (x, y, z, ang) in ((CX + 1.17, 0.0, -1.2, 0.0), (CX - 1.17, 0.0, -2.4, 0.0)):
        small('ohatch', box_bm((x, y, z), (0.035, 0.7, 0.9)), 'pir_orange')
        small('oxa', _rot_z(box_bm((x + (0.02 if x > 0 else -0.02), y, z), (0.02, 0.06, 1.1)), 0.7, (x, y, z)), 'pir_gun')
    small('ohatch2', box_bm((-0.95, -0.17, 0.2), (0.7, 0.025, 0.7)), 'pir_orange')
    small('ant', tube((0.0, 0.56, 2.2), (0.0, 0.95, 2.0), 0.014, 0.007, 6), 'pir_gun')
    small('ant2', tube((CX, 1.18, -1.0), (CX + 0.1, 1.7, -1.1), 0.016, 0.008, 6), 'pir_gun')
    for z in (1.5, 2.5):
        small('mark', box_bm((0.0, 0.40 + (z - 1.5) * -0.04, z), (0.50, 0.012, 0.12)), 'pir_orange')
    small('nav1', box_bm((0.0, 0.18, 4.2), (0.14, 0.14, 0.14)), 'emit_red')
    small('nav2', box_bm((-1.55, 0.17, -2.9), (0.14, 0.14, 0.14)), 'emit_red')
    # alt gövde: ısı kalkanı plakaları, iniş ayağı yuvaları, kablo kanalı
    for z in (0.6, 1.6, 2.6):
        small('bplate', box_bm((0.0, 0.10 - 0.36 - 0.0, z), (0.52, 0.03, 0.8)), 'pir_heat')
    for sx in (-1, 1):
        small('gleg', tube((sx * 0.35, -0.30, 1.5), (sx * 0.42, -0.62, 1.5), 0.05, 0.06, 10), 'pir_titan')
        small('gfoot', box_bm((sx * 0.42, -0.64, 1.5), (0.22, 0.03, 0.30)), 'pir_gun')
    small('gleg3', tube((CX, -1.10, -2.4), (CX, -1.34, -2.4), 0.07, 0.08, 10), 'pir_titan')
    small('gfoot3', box_bm((CX, -1.36, -2.4), (0.30, 0.03, 0.34)), 'pir_gun')
    small('tray', tube((0.3, -0.34, 0.2), (0.3, -0.34, 3.4), 0.025, None, 8), 'pir_gun')
    # ---------------------------------------------------------------- soketler
    for sx in (-1, 1):                                                                   # ince emissive ışık şeritleri (uzaktan okunur)
        small('lstrip', box_bm((sx * (cap_w(2.4) - 0.003), 0.0, 2.4), (0.035, 0.03, 1.8)), 'emit_blue')
        small('lstrip2', box_bm((CX + sx * 1.152, 0.0, -2.2), (0.035, 0.03, 2.2)), 'emit_blue')
    socks = [{'name': 'ANCH_ENG_1', 'loc': tuple(geo.g2b(Vector((CX, 0.0, -4.30)))), 'dir': (0.0, 1.0, 0.0), 'extras': {'kind': 'engine'}},
             {'name': 'ANCH_ENG_2', 'loc': tuple(geo.g2b(Vector((-1.55, -0.20, -3.42)))), 'dir': (0.0, 1.0, 0.0), 'extras': {'kind': 'engine'}}]
    for i, p in enumerate(((0.0, 0.18, 4.2), (-1.55, 0.17, -2.9), (CX, 1.34, -1.4)), 1):
        socks.append({'name': 'ANCH_NAV_%d' % i, 'loc': tuple(geo.g2b(Vector(p))), 'dir': (0.0, 0.0, 1.0), 'extras': {'kind': 'nav'}})
    for i, p in enumerate(((-0.4, -0.35, 4.35), (0.4, -0.35, 4.35)), 1):
        socks.append({'name': 'ANCH_MUZ_%d' % i, 'loc': tuple(geo.g2b(Vector(p))), 'dir': (0.0, -1.0, 0.0), 'extras': {'kind': 'muzzle'}})
    return {'objects': out_body + out_hi, 'sockets': socks}


def build_kurt(spec, mats):
    """KURT (brute, ağır zırhlı korsan): geniş kama gövde, katmanlı zırh, yan sponson+taret, arkada 3 kafes motor kulesi, sırtta kayışlı yakıt tankları."""
    P = spec['params']; D = 0.012
    hs = [(-3.6, 1.5, 0.75, 0.65, 4.0), (-2.6, 2.0, 0.90, 0.70, 4.0), (-0.5, 2.1, 0.95, 0.70, 4.0), (1.5, 1.6, 0.80, 0.60, 3.8), (3.0, 0.9, 0.55, 0.45, 3.4), (4.0, 0.35, 0.30, 0.25, 3.0), (4.5, 0.10, 0.09, 0.09, 2.4)]
    hull = _obj('hull', loft(hs), 'pir_gray2', mats)

    def hw(z):
        for a, b in zip(hs, hs[1:]):
            if a[0] <= z <= b[0]:
                t = (z - a[0]) / (b[0] - a[0]); return a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t
        return hs[0][1], hs[0][2]
    parts = []
    # katmanlı üst zırh plakaları (üst üste, hafif eğimli)
    for (z0, z1, w, y) in ((-1.9, 0.2, 1.7, 0.96), (0.1, 1.7, 1.3, 0.84), (-3.1, -1.8, 1.4, 0.76)):
        parts.append(_obj('plateT', box_bm((0.0, y, (z0 + z1) / 2), (w, 0.14, z1 - z0)), 'pir_gray', mats))
    # yan sponsonlar (yuvarlatılmış kare loft) + omuz kalkanı
    for sx in (-1, 1):
        sp = [(-1.8, 0.40, 0.45, 0.40, 3.6, sx * 2.05, -0.10), (-0.6, 0.55, 0.55, 0.45, 3.6, sx * 2.1, -0.08), (1.4, 0.50, 0.50, 0.42, 3.6, sx * 2.0, -0.06), (2.4, 0.26, 0.28, 0.24, 3.0, sx * 1.8, -0.02)]
        parts.append(_obj('spon', loft(sp), 'pir_gray', mats))
        parts.append(_obj('tur', tube((sx * 2.0, 0.40, 0.6), (sx * 2.0, 0.66, 0.6), 0.34, 0.28, 24), 'pir_titan', mats))
    # motor bloğu + 3 kule tabanı
    parts.append(_obj('eblk', box_bm((0.0, 0.0, -3.55), (3.2, 1.3, 0.8)), 'pir_titan', mats))
    # sırt yakıt tankları (kayışlı, turuncu-kahve) iki yanda
    for sx in (-1, 1):
        parts.append(_obj('tank', loft([(-2.3, 0.28, 0.28, 0.28, 2.0, sx * 1.0, 1.25), (-1.7, 0.36, 0.36, 0.36, 2.0, sx * 1.0, 1.25), (0.0, 0.36, 0.36, 0.36, 2.0, sx * 1.0, 1.25), (0.5, 0.22, 0.22, 0.22, 2.0, sx * 1.0, 1.25)], 28), 'pir_orange', mats))
        parts.append(_obj('tmnt', box_bm((sx * 1.0, 1.0, -1.1), (0.6, 0.2, 1.4)), 'pir_titan', mats))
    union_all(hull, parts)
    core = hull
    ENG = [(0.0, 0.0, 0.62), (-1.05, 0.05, 0.42), (1.05, 0.05, 0.42)]
    diff_all(core, [_obj('noz', tube((x, y, -4.5), (x, y, -3.95), r * 0.9, r * 0.8, 32), 'pir_heat', mats) for x, y, r in ENG])
    cuts = []
    for z in (-1.2, 0.2, 1.4):
        cuts.append(_obj('hat', box_bm((0.0, 1.02, z), (0.5, 0.05, 0.42)), 'pir_gun', mats))
    for sx in (-1, 1):
        for k in range(4):
            cuts.append(_obj('louv', box_bm((sx * 2.1, 0.1, -1.3 + k * 0.4), (0.06, 0.4, 0.14)), 'pir_gun', mats))
    diff_all(core, cuts)
    hi_core = core.copy(); hi_core.data = core.data.copy(); geo.collection('Asset').objects.link(hi_core); hi_core.name = 'hi_core'; hi_core['sd_role'] = 'hi'
    grv = []
    for z in (-3.0, -2.2, -1.4, -0.6, 0.2, 1.0, 1.8, 2.6):
        w, h = hw(z)
        grv.append(_obj('rg', ring_bm(z, 0.012, w * 2, h, h * 0.8, 0.25, D), 'pir_gun', mats))
    diff_all(hi_core, grv)
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
        if cur in ('pir_gray', 'pir_gray2'):
            if gz > 3.3:
                f.material_index = SLOT['pir_orange']
            elif gz < -3.9:
                f.material_index = SLOT['pir_heat']
            elif gy < -0.1:
                f.material_index = SLOT['pir_titan'] if int((gz + 6) / 0.8) % 2 else SLOT['pir_gray2']      # alt gövde: koyu kalkan şeritleri
            else:
                h = (int((gx + 4.0) / 0.55) * 73856093 ^ int((gz + 6.0) / 0.5) * 19349663 ^ int((gy + 2.0) / 0.4) * 83492791) % 16
                if h in (0, 1, 2):
                    f.material_index = SLOT['pir_gray'] if cur == 'pir_gray2' else SLOT['pir_gray2']
                elif h == 3:
                    f.material_index = SLOT['pir_orange']
                elif h == 4:
                    f.material_index = SLOT['pir_titan']
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
    # köprü: dar, alçak, gömülü kanopi
    small('cframe', loft([(2.4, 0.46, 0.05, 0.10, 3.0, 0, 0.60), (2.9, 0.70, 0.09, 0.14, 3.2, 0, 0.60), (3.5, 0.50, 0.07, 0.12, 3.0, 0, 0.52)]), 'pir_titan')
    small('glass', loft([(2.55, 0.34, 0.06, 0.0, 3.0, 0, 0.62), (2.95, 0.56, 0.085, 0.0, 3.2, 0, 0.615), (3.4, 0.36, 0.06, 0.0, 3.0, 0, 0.54)]), 'pir_glass')
    # 3 kafes motor kulesi + nozul
    for (x, y, r) in ENG:
        small('bell', tube((x, y, -4.5), (x, y, -4.0), r, r * 0.85, 36, cap=False), 'pir_heat')
        small('ncore', tube((x, y, -4.43), (x, y, -4.40), r * 0.55, None, 28), 'emit_redhot')
        small('nblue', tube((x, y, -4.435), (x, y, -4.425), r * 0.2, None, 18), 'emit_blue')
        small('nlip', tube((x, y, -4.56), (x, y, -4.49), r * 1.12, r * 1.10, 36, cap=False), 'pir_titan')
        for k in range(6):
            a = k * math.pi / 3
            small('lat', tube((x + math.cos(a) * r * 1.35, y + math.sin(a) * r * 1.35, -3.3), (x + math.cos(a) * r * 1.1, y + math.sin(a) * r * 1.1, -4.4), 0.035, None, 8), 'pir_gun')
        for z in (-3.7, -4.05):
            small('latr', tube((x, y, z), (x, y, z + 0.03), r * 1.3, None, 32, cap=False), 'pir_gun')
    # sponson taret namluları
    for sx in (-1, 1):
        small('barrel', tube((sx * 2.0, 0.55, 0.9), (sx * 2.0, 0.55, 2.6), 0.08, 0.065, 12), 'pir_gun')
        small('shroud', tube((sx * 2.0, 0.55, 0.6), (sx * 2.0, 0.55, 1.3), 0.16, 0.14, 16), 'pir_titan')
        small('muz', tube((sx * 2.0, 0.55, 2.55), (sx * 2.0, 0.55, 2.72), 0.11, 0.08, 12), 'pir_gun')
    # tank kayışları
    for sx in (-1, 1):
        for k in range(4):
            small('strap', tube((sx * 1.0, 1.25, -2.1 + k * 0.55), (sx * 1.0, 1.25, -2.1 + k * 0.55 + 0.08), 0.375, None, 28, cap=False), 'pir_titan')
    # prow ram sırtı ve kancalar
    small('ram', box_bm((0.0, 0.05, 3.9), (0.20, 0.5, 0.9)), 'pir_titan')
    for sx in (-1, 1):
        small('hook', tube((sx * 0.4, -0.4, 2.6), (sx * 0.5, -0.45, 4.2), 0.08, 0.055, 12), 'pir_gun')
        small('hookt', box_bm((sx * 0.5, -0.45, 4.25), (0.22, 0.05, 0.12)), 'pir_titan')
    # ölçek ipuçları: pencere sıraları, hatch+tutamak, korkuluk, merdiven, iniş ayakları, turuncu X hatch
    for sx in (-1, 1):
        for k in range(6):
            zz = -1.0 + k * 0.30
            small('win', box_bm((sx * (hw(zz)[0] + 0.004 - 0.1), 0.62, zz), (0.04, 0.11, 0.22)), 'emit_blue')
        small('hatchp', box_bm((sx * (hw(0.8)[0] - 0.01), 0.15, 0.8), (0.035, 0.5, 0.5)), 'pir_titan')
        small('hatchh', box_bm((sx * (hw(0.8)[0] + 0.012), 0.15, 0.95), (0.02, 0.12, 0.03)), 'pir_gun')
        small('ohatch', box_bm((sx * 2.55, 0.0, -0.5), (0.035, 0.8, 1.0)), 'pir_orange')
        small('oxa', _rot_z(box_bm((sx * 2.57, 0.0, -0.5), (0.02, 0.06, 1.2)), 0.7, (sx * 2.57, 0.0, -0.5)), 'pir_gun')
        small('gleg', tube((sx * 1.3, -0.62, 0.8), (sx * 1.4, -0.95, 0.8), 0.07, 0.08, 10), 'pir_titan')
        small('gfoot', box_bm((sx * 1.4, -0.97, 0.8), (0.32, 0.04, 0.40)), 'pir_gun')
        small('gleg2', tube((sx * 1.3, -0.62, -2.2), (sx * 1.4, -0.95, -2.2), 0.07, 0.08, 10), 'pir_titan')
        small('gfoot2', box_bm((sx * 1.4, -0.97, -2.2), (0.32, 0.04, 0.40)), 'pir_gun')
    for q in range(5):
        small('post', tube((-0.6 + q * 0.3, 0.98, 1.9), (-0.6 + q * 0.3, 1.16, 1.9), 0.014, None, 6), 'pir_gun')
    small('rail', tube((-0.6, 1.16, 1.9), (0.6, 1.16, 1.9), 0.012, None, 6), 'pir_gun')
    for q in range(4):
        small('step', box_bm((0.5 + q * 0.0, 0.2 - q * 0.17, 3.05 - 0.9), (0.05, 0.03, 0.28)), 'pir_titan')
    for z in (-2.2, -0.2, 1.8):
        small('bplate', box_bm((0.0, -0.70, z), (1.5, 0.03, 1.2)), 'pir_heat')
    small('tray', tube((0.5, -0.72, -3.0), (0.5, -0.72, 3.0), 0.025, None, 8), 'pir_gun')
    small('ant1', tube((0.3, 1.0, -2.4), (0.4, 1.7, -2.5), 0.02, 0.01, 6), 'pir_gun')
    small('ant2', tube((-0.5, 1.0, -0.6), (-0.6, 1.5, -0.7), 0.016, 0.008, 6), 'pir_gun')
    for z in (-0.2, 0.5):
        small('mark', box_bm((0.0, 1.03, z), (1.0, 0.012, 0.14)), 'pir_orange')
    small('nav1', box_bm((-2.5, 0.3, 1.8), (0.14, 0.14, 0.14)), 'emit_red')
    small('nav2', box_bm((2.5, 0.3, 1.8), (0.14, 0.14, 0.14)), 'emit_blue')
    small('nav3', box_bm((0.0, 0.85, -3.0), (0.14, 0.14, 0.14)), 'emit_red')
    for sx in (-1, 1):
        small('lstrip', box_bm((sx * (hw(0.8)[0] - 0.01), 0.35, 0.3), (0.035, 0.03, 3.4)), 'emit_blue')
        small('lstrip2', box_bm((sx * 2.6, -0.1, -1.0), (0.035, 0.03, 3.0)), 'emit_blue')
    socks = []
    for i, (x, y, r) in enumerate(ENG, 1):
        socks.append({'name': 'ANCH_ENG_%d' % i, 'loc': tuple(geo.g2b(Vector((x, y, -4.43)))), 'dir': (0.0, 1.0, 0.0), 'extras': {'kind': 'engine'}})
    for i, p in enumerate(((-2.5, 0.3, 1.8), (2.5, 0.3, 1.8), (0.0, 0.85, -3.0)), 1):
        socks.append({'name': 'ANCH_NAV_%d' % i, 'loc': tuple(geo.g2b(Vector(p))), 'dir': (0.0, 0.0, 1.0), 'extras': {'kind': 'nav'}})
    for i, p in enumerate(((-2.0, 0.55, 2.7), (2.0, 0.55, 2.7)), 1):
        socks.append({'name': 'ANCH_MUZ_%d' % i, 'loc': tuple(geo.g2b(Vector(p))), 'dir': (0.0, -1.0, 0.0), 'extras': {'kind': 'muzzle'}})
    return {'objects': out_body + out_hi, 'sockets': socks}


def build_yagmaci(spec, mats):
    """YAĞMACI (reaver, korsan kurtarma mavnası): iki farklı gövde bölümü kafes çerçeveyle bağlı (asimetrik), çerçevede yüklü konteyner, yan vinç kolu+kıskaç,
    arkada eşit olmayan 2 kafes motor kulesi, tank kümesi, kesici kol. Doğaçlama ama mekanik olarak bütünleşik."""
    P = spec['params']; D = 0.012
    fs = [(1.0, 0.70, 0.55, 0.45, 3.4, 0.0, 0.0), (2.2, 1.05, 0.70, 0.55, 3.4, 0.0, 0.05), (3.8, 0.85, 0.55, 0.45, 3.2, 0.0, 0.05), (5.0, 0.35, 0.28, 0.22, 2.8, 0.0, 0.0), (5.6, 0.10, 0.09, 0.08, 2.3, 0.0, 0.0)]
    fore = _obj('fore', loft(fs), 'pir_gray', mats)
    aft_s = [(-4.2, 1.5, 0.95, 0.8, 4.0, -0.15, 0.1), (-3.2, 1.95, 1.1, 0.9, 4.0, -0.15, 0.1), (-1.6, 1.95, 1.1, 0.9, 4.0, -0.15, 0.1), (-0.9, 1.4, 0.85, 0.7, 3.6, -0.1, 0.05)]
    aft = _obj('aft', loft(aft_s), 'pir_gray2', mats)

    def fw(z):
        for a, b in zip(fs, fs[1:]):
            if a[0] <= z <= b[0]:
                t = (z - a[0]) / (b[0] - a[0]); return a[1] + (b[1] - a[1]) * t
        return fs[0][1]
    parts = [aft]
    # eksiz bağlantı kirişi: tek ana kiriş fore↔aft (kafes çerçeve dekor olarak small'da)
    parts.append(_obj('keel', loft([(-1.0, 0.45, 0.35, 0.30, 3.0, 0.0, 0.0), (1.2, 0.45, 0.35, 0.30, 3.0, 0.0, 0.0)]), 'pir_titan', mats))
    # vinç tabanı + tank kümesi (union)
    parts.append(_obj('crbase', tube((1.2, 1.0, -2.3), (1.2, 1.35, -2.3), 0.42, 0.36, 28), 'pir_titan', mats))
    for k, (x, z) in enumerate(((-1.0, -2.6), (-1.0, -1.6))):
        parts.append(_obj('tank', loft([(z - 0.45, 0.30, 0.30, 0.30, 2.0, x, 1.25), (z - 0.2, 0.36, 0.36, 0.36, 2.0, x, 1.25), (z + 0.2, 0.36, 0.36, 0.36, 2.0, x, 1.25), (z + 0.45, 0.26, 0.26, 0.26, 2.0, x, 1.25)], 28), 'pir_orange', mats))
    parts.append(_obj('tmnt', box_bm((-1.0, 1.0, -2.1), (0.9, 0.2, 1.9)), 'pir_titan', mats))
    union_all(fore, parts)
    core = fore
    ENG = [(-0.75, 0.15, 0.56), (1.0, 0.3, 0.36)]
    diff_all(core, [_obj('noz', tube((x, y, -4.9), (x, y, -4.3), r * 0.9, r * 0.8, 32), 'pir_heat', mats) for x, y, r in ENG])
    cuts = []
    for z in (-3.0, -1.8):
        cuts.append(_obj('hat', box_bm((0.1, 1.17, z), (0.5, 0.05, 0.42)), 'pir_gun', mats))
    for k in range(4):
        cuts.append(_obj('louv', box_bm((-0.3, 1.2, -3.8 + k * 0.4), (0.8, 0.06, 0.12)), 'pir_gun', mats))
    diff_all(core, cuts)
    hi_core = core.copy(); hi_core.data = core.data.copy(); geo.collection('Asset').objects.link(hi_core); hi_core.name = 'hi_core'; hi_core['sd_role'] = 'hi'
    grv = []
    for z in (-3.8, -3.0, -2.2, -1.4):
        grv.append(_obj('rg', ring_bm(z, 0.012, 3.9, 1.1, 0.9, 0.3, D), 'pir_gun', mats))
        for v in grv[-1].data.vertices:
            v.co.x += -0.15
    for z in (1.5, 2.2, 3.0, 3.8):
        grv.append(_obj('rc', ring_bm(z, 0.012, fw(z) * 2, 0.6, 0.5, 0.16, D), 'pir_gun', mats))
    diff_all(hi_core, grv)
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
        if cur in ('pir_gray', 'pir_gray2'):
            if gz > 4.2:
                f.material_index = SLOT['pir_gray']
            elif gz < -4.1:
                f.material_index = SLOT['pir_heat']
            elif gy < -0.15:
                f.material_index = SLOT['pir_titan'] if int((gz + 6) / 0.8) % 2 else SLOT['pir_gray2']
            else:
                h = (int((gx + 4.0) / 0.55) * 73856093 ^ int((gz + 6.0) / 0.5) * 19349663 ^ int((gy + 2.0) / 0.4) * 83492791) % 14
                if h in (0, 1, 2):
                    f.material_index = SLOT['pir_gray'] if cur == 'pir_gray2' else SLOT['pir_gray2']
                elif h == 3:
                    f.material_index = SLOT['pir_orange']
                elif h == 4:
                    f.material_index = SLOT['pir_titan']
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
    # köprü: gömülü alçak kanopi (fore üstü)
    small('cframe', loft([(1.8, 0.30, 0.05, 0.10, 2.8, 0, 0.70), (2.5, 0.62, 0.09, 0.14, 3.0, 0, 0.74), (3.3, 0.55, 0.08, 0.14, 3.0, 0, 0.66), (3.9, 0.22, 0.04, 0.08, 2.6, 0, 0.58)]), 'pir_titan')
    small('glass', loft([(2.0, 0.24, 0.06, 0.0, 2.8, 0, 0.73), (2.5, 0.50, 0.085, 0.0, 3.0, 0, 0.745), (3.2, 0.44, 0.075, 0.0, 3.0, 0, 0.67), (3.7, 0.16, 0.045, 0.0, 2.8, 0, 0.60)]), 'pir_glass')
    # kafes çerçeve (fore ↔ aft) + yüklü kurtarma konteyneri
    cs = [(-0.8, -0.55), (0.8, -0.55), (0.8, 0.65), (-0.8, 0.65)]
    for cx_, cy_ in cs:
        small('flon', tube((cx_, cy_, -1.2), (cx_, cy_, 1.1), 0.06, None, 10), 'pir_titan')
    for z in (-0.9, -0.2, 0.5, 1.1):
        for a, b in zip(cs, cs[1:] + cs[:1]):
            small('frng', tube((a[0], a[1], z), (b[0], b[1], z), 0.035, None, 8), 'pir_gun')
    for z0, z1 in ((-0.9, -0.2), (-0.2, 0.5), (0.5, 1.1)):
        small('fdiag', tube((cs[0][0], cs[0][1], z0), (cs[3][0], cs[3][1], z1), 0.03, None, 8), 'pir_gun')
        small('fdiag', tube((cs[1][0], cs[1][1], z0), (cs[2][0], cs[2][1], z1), 0.03, None, 8), 'pir_gun')
    small('cont', box_bm((0.15, 0.05, -0.05), (1.1, 0.9, 1.7)), 'pir_orange')
    small('contr', box_bm((0.15, 0.52, -0.05), (1.14, 0.04, 0.12)), 'pir_titan')
    for k in range(4):
        small('contrib', box_bm((0.15 - 0.45 + k * 0.30, 0.05, 0.82), (0.05, 0.92, 0.04)), 'pir_titan')
    # 2 kafes motor kulesi
    for (x, y, r) in ENG:
        small('bell', tube((x, y, -4.9), (x, y, -4.35), r, r * 0.85, 36, cap=False), 'pir_heat')
        small('ncore', tube((x, y, -4.83), (x, y, -4.80), r * 0.55, None, 28), 'emit_redhot')
        small('nblue', tube((x, y, -4.835), (x, y, -4.825), r * 0.2, None, 18), 'emit_blue')
        small('nlip', tube((x, y, -4.96), (x, y, -4.89), r * 1.12, r * 1.10, 36, cap=False), 'pir_titan')
        for k in range(6):
            a = k * math.pi / 3
            small('lat', tube((x + math.cos(a) * r * 1.35, y + math.sin(a) * r * 1.35, -3.7), (x + math.cos(a) * r * 1.1, y + math.sin(a) * r * 1.1, -4.8), 0.035, None, 8), 'pir_gun')
        for z in (-4.1, -4.45):
            small('latr', tube((x, y, z), (x, y, z + 0.03), r * 1.3, None, 32, cap=False), 'pir_gun')
    # vinç kolu + kıskaç (sancakta, dışarı uzanır)
    small('arm1', tube((1.2, 1.35, -2.3), (1.65, 2.1, -1.1), 0.14, 0.12, 14), 'pir_titan')
    small('arm2', tube((1.65, 2.1, -1.1), (2.15, 1.55, 1.9), 0.11, 0.09, 14), 'pir_gun')
    small('elbow', box_bm((1.65, 2.1, -1.1), (0.3, 0.3, 0.3)), 'pir_gray2')
    small('piston', tube((1.3, 1.4, -2.0), (1.6, 2.0, -1.2), 0.05, None, 10), 'pir_gun')
    for k in range(3):
        a_ = k * 2 * math.pi / 3
        small('claw', tube((2.15, 1.55, 1.9), (2.15 + math.cos(a_) * 0.35, 1.55 + math.sin(a_) * 0.35, 2.5), 0.045, 0.03, 8), 'pir_titan')
    small('wrist', tube((2.15, 1.55, 1.8), (2.15, 1.55, 2.0), 0.13, None, 14), 'pir_gun')
    small('cable', tube((1.2, 1.4, -2.2), (2.1, 1.6, 1.7), 0.012, None, 6), 'pir_gun')
    # tank kayışları
    for z in (-2.6, -1.6):
        for k in range(3):
            small('strap', tube((-1.0, 1.25, z - 0.3 + k * 0.3), (-1.0, 1.25, z - 0.3 + k * 0.3 + 0.07), 0.375, None, 28, cap=False), 'pir_titan')
    # ölçek ipuçları: pencere, hatch, korkuluk, merdiven, iniş ayağı, turuncu X hatch
    for sx in (-1, 1):
        for k in range(5):
            zz = 1.6 + k * 0.30
            small('win', box_bm((sx * (fw(zz) - 0.004), 0.18, zz), (0.04, 0.11, 0.22)), 'emit_blue')
        small('hatchp', box_bm((sx * (fw(2.3) - 0.008), -0.08, 2.3), (0.035, 0.3, 0.4)), 'pir_titan')
        small('hatchh', box_bm((sx * (fw(2.3) + 0.012), -0.08, 2.46), (0.02, 0.10, 0.03)), 'pir_gun')
    small('ohatch', box_bm((1.80, 0.1, -3.0), (0.035, 0.8, 1.0)), 'pir_orange')
    small('oxa', _rot_z(box_bm((1.82, 0.1, -3.0), (0.02, 0.06, 1.2)), 0.7, (1.82, 0.1, -3.0)), 'pir_gun')
    small('ohatch2', box_bm((-2.12, 0.1, -2.2), (0.035, 0.8, 1.0)), 'pir_orange')
    for q in range(4):
        small('post', tube((-0.3 + q * 0.3, 1.14, -3.3), (-0.3 + q * 0.3, 1.32, -3.3), 0.014, None, 6), 'pir_gun')
    small('rail', tube((-0.3, 1.32, -3.3), (0.6, 1.32, -3.3), 0.012, None, 6), 'pir_gun')
    for q in range(4):
        small('step', box_bm((1.0 + 0.0, 0.3 - q * 0.17, -2.0 - 0.0), (0.05, 0.03, 0.28)), 'pir_titan') if False else None
    for (x, z) in ((-1.1, -3.4), (0.9, -3.4), (0.0, 1.6)):
        small('gleg', tube((x, -0.80 if z < 0 else -0.55, z), (x, -1.15 if z < 0 else -0.85, z), 0.07, 0.08, 10), 'pir_titan')
        small('gfoot', box_bm((x, -1.17 if z < 0 else -0.87, z), (0.32, 0.04, 0.38)), 'pir_gun')
    for z in (-3.4, -2.0):
        small('bplate', box_bm((-0.15, -0.86, z), (1.6, 0.03, 1.0)), 'pir_heat')
    small('tray', tube((0.4, -0.88, -4.0), (0.4, -0.55, 4.2), 0.025, None, 8), 'pir_gun')
    small('ant1', tube((-0.5, 1.2, -2.9), (-0.6, 1.9, -3.0), 0.02, 0.01, 6), 'pir_gun')
    small('ant2', tube((0.2, 0.78, 2.0), (0.3, 1.2, 1.9), 0.016, 0.008, 6), 'pir_gun')
    for z in (2.6, 3.4):
        small('mark', box_bm((0.0, 0.71, z), (0.6, 0.012, 0.12)), 'pir_orange')
    small('nav1', box_bm((2.15, 1.55, 2.0), (0.14, 0.14, 0.14)), 'emit_blue')
    small('nav2', box_bm((-2.1, 0.5, -3.5), (0.14, 0.14, 0.14)), 'emit_red')
    small('nav3', box_bm((0.0, 0.18, 4.4), (0.14, 0.14, 0.14)), 'emit_red')
    for sx in (-1, 1):
        small('lstrip', box_bm((sx * (fw(2.6) - 0.003), 0.15, 2.6), (0.035, 0.03, 2.2)), 'emit_blue')
        small('lstrip2', box_bm((sx * 2.1 - 0.15, 0.3, -2.4), (0.035, 0.03, 3.4)), 'emit_blue')
    socks = []
    for i, (x, y, r) in enumerate(ENG, 1):
        socks.append({'name': 'ANCH_ENG_%d' % i, 'loc': tuple(geo.g2b(Vector((x, y, -4.83)))), 'dir': (0.0, 1.0, 0.0), 'extras': {'kind': 'engine'}})
    for i, p in enumerate(((2.15, 1.55, 2.0), (-2.1, 0.5, -3.5), (0.0, 0.18, 4.4)), 1):
        socks.append({'name': 'ANCH_NAV_%d' % i, 'loc': tuple(geo.g2b(Vector(p))), 'dir': (0.0, 0.0, 1.0), 'extras': {'kind': 'nav'}})
    socks.append({'name': 'ANCH_MUZ_1', 'loc': tuple(geo.g2b(Vector((0.0, 0.4, 5.55)))), 'dir': (0.0, -1.0, 0.0), 'extras': {'kind': 'muzzle'}})
    return {'objects': out_body + out_hi, 'sockets': socks}


# ====================================================================== ortak iskelet (corvette, cargo, tanker, courier, mining)
def tower(small, x, y, r, zend, n=6, zback=1.1):
    """kafes motor kulesi + nozul"""
    small('bell', tube((x, y, zend), (x, y, zend + 0.55), r, r * 0.85, 36, cap=False), 'pir_heat')
    small('ncore', tube((x, y, zend + 0.07), (x, y, zend + 0.10), r * 0.55, None, 28), 'emit_redhot')
    small('nblue', tube((x, y, zend + 0.065), (x, y, zend + 0.075), r * 0.2, None, 18), 'emit_blue')
    small('nlip', tube((x, y, zend - 0.06), (x, y, zend + 0.01), r * 1.12, r * 1.10, 36, cap=False), 'pir_titan')
    for k in range(n):
        a = k * 2 * math.pi / n
        small('lat', tube((x + math.cos(a) * r * 1.35, y + math.sin(a) * r * 1.35, zend + zback), (x + math.cos(a) * r * 1.1, y + math.sin(a) * r * 1.1, zend + 0.1), 0.035, None, 8), 'pir_gun')
    for dz in (0.35, 0.7):
        small('latr', tube((x, y, zend + dz), (x, y, zend + dz + 0.03), r * 1.3, None, 32, cap=False), 'pir_gun')


def cues(small, wfun, zs, ytop, orange_z=None):
    """insan ölçeği ipuçları: pencere sıraları, hatch+tutamak, korkuluk, merdiven"""
    for sx in (-1, 1):
        for z in zs:
            small('win', box_bm((sx * (wfun(z) - 0.004), ytop * 0.55, z), (0.04, 0.11, 0.22)), 'emit_blue')
    for sx in (-1, 1):
        small('lstrip', box_bm((sx * (wfun((zs[0] + zs[-1]) / 2) - 0.002), ytop * 0.30, (zs[0] + zs[-1]) / 2), (0.035, 0.03, abs(zs[-1] - zs[0]) + 0.6)), 'emit_blue')
    zh = zs[len(zs) // 2]
    for sx in (-1, 1):
        small('hatchp', box_bm((sx * (wfun(zh) - 0.008), ytop * 0.1, zh + 0.8), (0.035, 0.3, 0.4)), 'pir_titan')
        small('hatchh', box_bm((sx * (wfun(zh) + 0.012), ytop * 0.1, zh + 0.95), (0.02, 0.10, 0.03)), 'pir_gun')
    for q in range(4):
        small('post', tube((-0.45 + q * 0.3, ytop, zh - 0.7), (-0.45 + q * 0.3, ytop + 0.18, zh - 0.7), 0.014, None, 6), 'pir_gun')
    small('rail', tube((-0.45, ytop + 0.18, zh - 0.7), (0.45, ytop + 0.18, zh - 0.7), 0.012, None, 6), 'pir_gun')


def build_generic(spec, mats, C):
    P = spec['params']; D = 0.012
    hs = C['hs']
    hull = _obj('hull', loft(hs), C.get('main', 'pir_gray'), mats)

    def hw(z):
        for a, b in zip(hs, hs[1:]):
            if a[0] <= z <= b[0]:
                t = (z - a[0]) / (b[0] - a[0]); return a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t
        return hs[0][1], hs[0][2]
    parts = C['union'](_obj, mats, loft, box_bm, tube, _rot_z)
    union_all(hull, parts)
    core = hull
    zend = C['zend']
    diff_all(core, [_obj('noz', tube((x, y, zend - 0.05), (x, y, zend + 0.55), r * 0.9, r * 0.8, 32), 'pir_heat', mats) for x, y, r in C['engs']])
    cuts = [_obj('hat', box_bm((0.0, hw(z)[1] * 1.0 - 0.02, z), (0.5, 0.05, 0.42)), 'pir_gun', mats) for z in C['hatch_z']]
    if cuts:
        diff_all(core, cuts)
    hi_core = core.copy(); hi_core.data = core.data.copy(); geo.collection('Asset').objects.link(hi_core); hi_core.name = 'hi_core'; hi_core['sd_role'] = 'hi'
    grv = []
    for z in C['ring_z']:
        w, h = hw(z)
        grv.append(_obj('rg', ring_bm(z, 0.012, w * 2, h, h * 0.85, 0.25, D), 'pir_gun', mats))
    diff_all(hi_core, grv)
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
    alt = C.get('alt', 'pir_gray2'); mainm = C.get('main', 'pir_gray'); acc = C.get('accent', 'pir_orange'); plain_nose = C.get('nose') == 'plain'
    for f in bm.faces:
        cb = f.calc_center_median(); gx, gy, gz = cb.x, cb.z, -cb.y
        cur = MATS[f.material_index]
        if cur == mainm or cur == alt:
            if gz > C['nose_z']:
                f.material_index = SLOT[alt] if plain_nose else SLOT[acc]
            elif gz < C['tail_z']:
                f.material_index = SLOT['pir_heat']
            elif gy < -0.1:
                f.material_index = SLOT['pir_titan'] if int((gz + 8) / 0.8) % 2 else SLOT[alt]
            else:
                h = (int((gx + 4.0) / 0.55) * 73856093 ^ int((gz + 8.0) / 0.5) * 19349663 ^ int((gy + 2.0) / 0.4) * 83492791) % 12
                if h in (0, 1, 2):
                    f.material_index = SLOT[alt] if cur == mainm else SLOT[mainm]
                elif h in (3, 4):
                    f.material_index = SLOT[acc]                                       # büyük renk blokları (100–170 m okunur)
                elif h == 5:
                    f.material_index = SLOT['pir_titan']
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
    # köprü kanopisi (alçak, gömülü)
    cz0, cz1, cy, cw = C['canopy']
    zm = (cz0 + cz1) / 2
    small('cframe', loft([(cz0, cw * 0.4, 0.05, 0.10, 2.8, 0, cy), (zm - 0.25, cw * 1.05, 0.09, 0.14, 3.0, 0, cy + 0.01), (zm + 0.35, cw * 0.95, 0.08, 0.14, 3.0, 0, cy - 0.04), (cz1, cw * 0.4, 0.04, 0.08, 2.6, 0, cy - 0.12)]), 'pir_titan')
    small('glass', loft([(cz0 + 0.15, cw * 0.3, 0.06, 0.0, 2.8, 0, cy + 0.02), (zm - 0.25, cw * 0.85, 0.085, 0.0, 3.0, 0, cy + 0.025), (zm + 0.3, cw * 0.78, 0.075, 0.0, 3.0, 0, cy - 0.025), (cz1 - 0.15, cw * 0.3, 0.045, 0.0, 2.8, 0, cy - 0.10)]), 'pir_glass')
    for (x, y, r) in C['engs']:
        tower(small, x, y, r, zend)
    cues(small, lambda z: hw(z)[0], C['win_z'], C['ytop'])
    small('ant1', tube((0.2, C['ytop'], C['ant_z']), (0.3, C['ytop'] + 0.7, C['ant_z'] - 0.1), 0.02, 0.01, 6), 'pir_gun')
    for z in C['mark_z']:
        small('mark', box_bm((0.0, hw(z)[1] * 1.0 + 0.005, z), (0.6, 0.012, 0.12)), acc)
    for (x, z) in C['gear']:
        small('gleg', tube((x, -hw(z)[1] * 0.8, z), (x, -hw(z)[1] * 0.8 - 0.3, z), 0.07, 0.08, 10), 'pir_titan')
        small('gfoot', box_bm((x, -hw(z)[1] * 0.8 - 0.32, z), (0.32, 0.04, 0.38)), 'pir_gun')
    for z in C['bplate_z']:
        small('bplate', box_bm((0.0, -hw(z)[1] * 0.85, z), (1.4, 0.03, 1.1)), 'pir_heat')
    if 'details' in C:
        C['details'](small, hw)
    nav = []
    for i, p in enumerate(C['nav']):                                                     # nav ışıkları gövde yüzeyine otursun
        w_, h_ = hw(p[2])
        if i < 2:
            nav.append((math.copysign(w_ - 0.03, p[0]), 0.25 * h_, p[2]))
        else:
            nav.append((p[0], h_ - 0.02, p[2]))
    if plain_nose:                                                                       # düz burun: vurgu renginde kuşaklar
        for z in C.get('nose_bands', (C['nose_z'] + 0.3, C['nose_z'] + 0.8)):
            w_, h_ = hw(z)
            small('nband', box_bm((0.0, 0.0, z), (w_ * 2.04, h_ * 2.0 * 0.96, 0.07)), acc.replace('pir_gray2', 'pir_gray')) if False else small('nband', tube((0.0, 0.0, z), (0.0, 0.0, z + 0.07), min(w_, h_) * 1.02, None, 24, cap=False), acc)
    for sx in (-1, 1):
        pass
    small('tstrip', box_bm((0.0, hw(C['win_z'][0])[1] + 0.002, (C['win_z'][0] + C['win_z'][-1]) / 2), (0.05, 0.012, abs(C['win_z'][-1] - C['win_z'][0]) + 0.8)), 'emit_blue')
    for i, p in enumerate(nav):
        small('nav', box_bm(p, (0.14, 0.14, 0.14)), 'emit_red' if i % 2 == 0 else 'emit_blue')
    socks = []
    for i, (x, y, r) in enumerate(C['engs'], 1):
        socks.append({'name': 'ANCH_ENG_%d' % i, 'loc': tuple(geo.g2b(Vector((x, y, zend + 0.08)))), 'dir': (0.0, 1.0, 0.0), 'extras': {'kind': 'engine'}})
    for i, p in enumerate(nav, 1):
        socks.append({'name': 'ANCH_NAV_%d' % i, 'loc': tuple(geo.g2b(Vector(p))), 'dir': (0.0, 0.0, 1.0), 'extras': {'kind': 'nav'}})
    for i, p in enumerate(C['muz'], 1):
        socks.append({'name': 'ANCH_MUZ_%d' % i, 'loc': tuple(geo.g2b(Vector(p))), 'dir': (0.0, -1.0, 0.0), 'extras': {'kind': 'muzzle'}})
    return {'objects': out_body + out_hi, 'sockets': socks}


def _cfg_corvette():
    hs = [(-4.5, 1.0, 0.70, 0.60, 3.6), (-3.5, 1.35, 0.80, 0.65, 3.6), (-1.0, 1.30, 0.80, 0.65, 3.6), (1.5, 1.00, 0.65, 0.50, 3.4), (3.5, 0.55, 0.40, 0.32, 3.0), (5.0, 0.20, 0.16, 0.14, 2.6), (5.6, 0.06, 0.06, 0.06, 2.2)]

    def union(O, mats, loft, box, tube, rz):
        parts = []
        parts.append(O('hangar', box((-1.35, -0.05, -1.4), (0.5, 0.9, 2.6)), 'pir_gray', mats))      # iskele hangar çıkıntısı
        parts.append(O('tur1', tube((0.0, 0.78, 2.2), (0.0, 1.0, 2.2), 0.4, 0.34, 24), 'pir_titan', mats))
        parts.append(O('mastb', tube((0.0, 0.8, -1.0), (0.0, 1.0, -1.0), 0.45, 0.4, 24), 'pir_titan', mats))
        return parts

    def details(small, hw):
        for k in range(4):                                                    # sensör kulesi (kafes)
            a = k * math.pi / 2 + math.pi / 4
            small('mlat', tube((math.cos(a) * 0.28, 1.0 + math.sin(a) * 0.28, -1.0), (math.cos(a) * 0.1, 2.6 + math.sin(a) * 0.1, -1.0), 0.03, None, 6), 'pir_gun')
        for y in (1.5, 2.1):
            small('mring', tube((0.0, y, -1.0), (0.0, y + 0.03, -1.0), 0.2, None, 20, cap=False), 'pir_gun')
        small('dish', tube((0.0, 2.65, -1.0), (0.0, 2.72, -1.0), 0.55, 0.15, 32), 'pir_gray')
        small('array', box_bm((0.0, 1.8, -1.45), (0.9, 0.7, 0.05)), 'pir_titan')
        small('tbar', tube((0.0, 1.0, 2.2), (0.0, 1.0, 3.5), 0.07, 0.06, 12), 'pir_gun')
        small('tbar2', tube((0.0, 1.02, 2.2), (0.0, 1.02, 3.0), 0.16, 0.14, 16), 'pir_titan')
        for z in (-1.5, -2.7):
            small('doorh', box_bm((-1.62, -0.05, z), (0.04, 0.8, 1.1)), 'pir_blue')                  # hangar kapıları
        small('hangarline', box_bm((-1.62, 0.36, -1.4), (0.03, 0.03, 2.4)), 'pir_gun')
        small('sdome', tube((0.0, -0.55, 3.0), (0.0, -0.72, 3.0), 0.22, 0.16, 20), 'pir_gun')
    return {'hs': hs, 'union': union, 'engs': [(-0.62, 0.0, 0.44), (0.62, 0.0, 0.44)], 'zend': -5.0, 'hatch_z': [-3.0, 0.4], 'ring_z': [-3.2, -2.2, -1.2, -0.2, 0.8, 1.8, 2.8],
            'nose_z': 4.4, 'tail_z': -4.35, 'canopy': (2.6, 4.3, 0.78, 0.42), 'win_z': [-2.6, -2.2, -1.8, 0.2, 0.6, 1.0, 1.4], 'ytop': 0.78, 'ant_z': -3.4, 'mark_z': [-3.2, -2.6], 'gear': [(-0.8, -2.8), (0.8, -2.8), (0.0, 2.0)],
            'bplate_z': [-2.8, -1.0, 0.8], 'details': details, 'nav': [(-1.4, 0.2, -1.5), (1.34, 0.2, -1.5), (0.0, 1.0, -4.2)], 'muz': [(0.0, 1.0, 3.5)], 'main': 'pir_white', 'alt': 'pir_gray', 'accent': 'pir_blue', 'nose': 'plain'}


def _cfg_courier():
    hs = [(-3.0, 0.55, 0.40, 0.34, 3.2), (-2.0, 0.80, 0.50, 0.40, 3.4), (0.0, 0.75, 0.48, 0.38, 3.4), (1.8, 0.50, 0.34, 0.28, 3.0), (3.0, 0.22, 0.17, 0.15, 2.6), (3.5, 0.06, 0.06, 0.05, 2.2)]

    def union(O, mats, loft, box, tube, rz):
        return [O('nacL', loft([(-3.0, 0.22, 0.22, 0.22, 2.0, -0.85, -0.1), (-1.6, 0.28, 0.28, 0.28, 2.0, -0.85, -0.1), (-0.6, 0.18, 0.18, 0.18, 2.0, -0.85, -0.1)], 24), 'pir_gray', mats),
                O('nacR', loft([(-3.0, 0.22, 0.22, 0.22, 2.0, 0.85, -0.1), (-1.6, 0.28, 0.28, 0.28, 2.0, 0.85, -0.1), (-0.6, 0.18, 0.18, 0.18, 2.0, 0.85, -0.1)], 24), 'pir_gray', mats),
                O('str', box((0.0, -0.05, -1.5), (1.8, 0.14, 0.5)), 'pir_titan', mats)]

    def details(small, hw):
        small('dish', tube((0.0, 0.52, -0.8), (0.0, 0.58, -0.8), 0.38, 0.1, 28), 'pir_gray')
        small('dstem', tube((0.0, 0.48, -0.8), (0.0, 0.54, -0.8), 0.06, None, 10), 'pir_gun')
        small('dishrib', tube((0.0, 0.52, -0.8), (0.0, 0.90, -0.8), 0.015, None, 6), 'pir_gun')
        for k in range(3):
            small('cargopod', box_bm((0.0, -0.40, -1.0 + k * 0.6), (0.7, 0.14, 0.5)), 'pir_blue')
    return {'hs': hs, 'union': union, 'engs': [(0.0, 0.0, 0.34), (-0.85, -0.1, 0.22), (0.85, -0.1, 0.22)], 'zend': -3.3, 'hatch_z': [-0.2], 'ring_z': [-2.0, -1.4, -0.8, -0.2, 0.4, 1.0],
            'nose_z': 2.6, 'tail_z': -2.9, 'canopy': (1.0, 2.4, 0.46, 0.34), 'win_z': [-1.2, -0.9, 0.5, 0.8], 'ytop': 0.5, 'ant_z': -1.8, 'mark_z': [-1.2, -0.5], 'gear': [(-0.5, -1.4), (0.5, -1.4), (0.0, 1.2)],
            'bplate_z': [-1.2, 0.2], 'details': details, 'nav': [(-1.1, -0.1, -1.0), (1.1, -0.1, -1.0), (0.0, 0.5, -2.8)], 'muz': [(0.0, 0.0, 3.4)], 'main': 'pir_white', 'alt': 'pir_gray', 'accent': 'pir_blue', 'nose': 'plain'}


def _cfg_cargo():
    hs = [(-5.0, 1.0, 0.70, 0.60, 3.6), (-4.0, 1.25, 0.80, 0.70, 3.6), (-2.5, 0.95, 0.60, 0.50, 3.4), (3.5, 0.95, 0.60, 0.50, 3.4), (5.0, 0.70, 0.55, 0.45, 3.2), (6.2, 0.30, 0.25, 0.20, 2.8), (6.8, 0.08, 0.08, 0.07, 2.2)]

    def union(O, mats, loft, box, tube, rz):
        return [O('keel', box((0.0, -0.1, 0.5), (0.9, 0.6, 7.0)), 'pir_titan', mats)]

    def details(small, hw):
        # konteyner yığınları: 3 sıra x 2 sütun, çerçeve içinde
        for iz, z in enumerate((-1.8, -0.2, 1.4, 3.0)):
            for sx in (-1, 1):
                for sy in (0, 1):
                    key = 'pir_orange' if (iz + (1 if sx > 0 else 0) + sy) % 2 == 0 else ('pir_gray' if (iz + sy) % 2 else 'pir_gray2')
                    small('cnt', box_bm((sx * 1.15, 0.25 + sy * 0.95 - 0.35, z), (1.0, 0.85, 1.4)), key)
                    small('cntrib', box_bm((sx * 1.15, 0.25 + sy * 0.95 - 0.35, z + 0.72), (1.04, 0.89, 0.05)), 'pir_titan')
        for sx in (-1, 1):
            for k in range(5):
                zz = -2.6 + k * 1.6
                small('frame', tube((sx * 1.7, -0.8, zz), (sx * 1.7, 1.55, zz), 0.055, None, 6), 'pir_gun')
            for q in range(6):                                                    # uzun tüpleri kısa parçalara böl (UV doluluğu)
                za, zb = -2.6 + q * 1.07, -2.6 + (q + 1) * 1.07
                small('flon', tube((sx * 1.7, 1.55, za), (sx * 1.7, 1.55, zb), 0.055, None, 6), 'pir_gun')
                small('flon2', tube((sx * 1.7, -0.8, za), (sx * 1.7, -0.8, zb), 0.055, None, 6), 'pir_gun')
        small('crane', tube((0.0, 0.5, -3.5), (0.0, 2.2, -3.2), 0.1, 0.08, 12), 'pir_titan')
        small('crane2', tube((0.0, 2.2, -3.2), (0.0, 2.0, -1.2), 0.07, 0.06, 10), 'pir_gun')
    return {'hs': hs, 'union': union, 'engs': [(-0.55, 0.0, 0.40), (0.55, 0.0, 0.40)], 'zend': -5.6, 'hatch_z': [-4.0], 'ring_z': [-4.6, -3.4, -2.2, 3.8, 4.6, 5.4],
            'nose_z': 5.8, 'tail_z': -4.95, 'canopy': (4.6, 6.2, 0.72, 0.4), 'win_z': [-4.2, -3.8, -3.4, 4.4, 4.7, 5.0], 'ytop': 0.72, 'ant_z': -4.2, 'mark_z': [-4.4, -3.6], 'gear': [(-0.8, -4.0), (0.8, -4.0), (0.0, 5.0)],
            'bplate_z': [-4.0, 4.0], 'details': details, 'nav': [(-1.3, 0.3, -4.6), (1.3, 0.3, -4.6), (0.0, 0.7, -3.4)], 'muz': [(0.0, 0.0, 6.7)], 'main': 'pir_gray', 'alt': 'pir_gray2', 'accent': 'pir_orange', 'nose': 'plain'}


def _cfg_tanker():
    hs = [(-6.0, 1.0, 0.70, 0.60, 3.6), (-5.0, 1.25, 0.80, 0.70, 3.6), (-3.6, 0.95, 0.62, 0.52, 3.4), (5.0, 0.95, 0.62, 0.52, 3.4), (6.4, 0.70, 0.55, 0.45, 3.2), (7.6, 0.30, 0.25, 0.20, 2.8), (8.2, 0.08, 0.08, 0.07, 2.2)]

    def union(O, mats, loft, box, tube, rz):
        parts = [O('keel', box((0.0, 0.0, 0.8), (0.8, 0.7, 9.4)), 'pir_titan', mats)]
        for (x, y) in ((-1.15, 0.85), (1.15, 0.85), (-1.15, -0.85), (1.15, -0.85)):
            parts.append(O('tank', loft([(-3.3, 0.55, 0.55, 0.55, 2.0, x, y), (-3.0, 0.78, 0.78, 0.78, 2.0, x, y), (4.0, 0.78, 0.78, 0.78, 2.0, x, y), (4.3, 0.55, 0.55, 0.55, 2.0, x, y)], 32), 'pir_gray' if (x > 0) == (y > 0) else 'pir_yellow', mats))
        return parts

    def details(small, hw):
        for (x, y) in ((-1.15, 0.85), (1.15, 0.85), (-1.15, -0.85), (1.15, -0.85)):
            for z in (-2.2, -0.4, 1.4, 3.2):
                small('band', tube((x, y, z), (x, y, z + 0.10), 0.80, None, 36, cap=False), 'pir_titan')
            small('valve', tube((x, y + (0.85 if y > 0 else -0.85) * 0.99, 0.5), (x, y + (0.85 if y > 0 else -0.85) * 1.12, 0.5), 0.12, 0.10, 10), 'pir_gun')
            small('cap', tube((x, y, -3.28), (x, y, -3.22), 0.34, None, 20), 'pir_gun')
        for sy in (-1, 1):
            small('pipe', tube((0.0, sy * 0.4, -3.0), (0.0, sy * 0.4, 4.5), 0.05, None, 8), 'pir_gun')
        small('ladder', tube((1.95, -0.8, 0.0), (1.95, 1.7, 0.0), 0.02, None, 6), 'pir_gun')
        small('ladder2', tube((1.99, -0.8, 0.3), (1.99, 1.7, 0.3), 0.02, None, 6), 'pir_gun')
        for q in range(8):
            small('rung', tube((1.95, -0.7 + q * 0.3, 0.0), (1.99, -0.7 + q * 0.3, 0.3), 0.012, None, 5), 'pir_gun')
    return {'hs': hs, 'union': union, 'engs': [(-0.55, 0.0, 0.42), (0.55, 0.0, 0.42)], 'zend': -6.6, 'hatch_z': [-5.0], 'ring_z': [-5.6, -4.6, 5.4, 6.2, 7.0],
            'nose_z': 7.0, 'tail_z': -5.95, 'canopy': (6.0, 7.6, 0.74, 0.4), 'win_z': [-5.2, -4.8, -4.4, 5.6, 5.9, 6.2], 'ytop': 0.74, 'ant_z': -5.2, 'mark_z': [-5.4, -4.6], 'gear': [(-0.8, -5.0), (0.8, -5.0), (0.0, 6.2)],
            'bplate_z': [-5.0, 5.0], 'details': details, 'nav': [(-1.3, 0.3, -5.4), (1.3, 0.3, -5.4), (0.0, 0.8, -4.4)], 'muz': [(0.0, 0.0, 8.1)], 'main': 'pir_gray', 'alt': 'pir_gray2', 'accent': 'pir_yellow', 'nose': 'plain'}


def _cfg_mining():
    hs = [(-4.0, 1.3, 0.8, 0.7, 3.8), (-3.0, 1.7, 0.95, 0.8, 3.8), (-0.5, 1.6, 0.9, 0.75, 3.8), (1.8, 1.3, 0.75, 0.65, 3.6), (3.0, 0.9, 0.55, 0.5, 3.4), (3.8, 0.5, 0.35, 0.3, 3.0), (4.1, 0.2, 0.15, 0.12, 2.6)]

    def union(O, mats, loft, box, tube, rz):
        parts = [O('hopper', loft([(-3.4, 0.9, 0.5, 0.0, 3.2, 0, 0.95), (-1.6, 1.25, 0.6, 0.0, 3.4, 0, 0.95), (0.2, 1.05, 0.5, 0.0, 3.2, 0, 0.9)]), 'pir_orange', mats)]
        for sx in (-1, 1):
            parts.append(O('mnt', box((sx * 1.0, -0.2, 3.2), (0.7, 0.5, 0.9)), 'pir_titan', mats))
        return parts

    def details(small, hw):
        for sx in (-1, 1):                                                       # ön matkap kolları (gövdeye yakın katlı)
            small('arm', tube((sx * 1.0, -0.2, 3.0), (sx * 1.1, -0.25, 6.4), 0.30, 0.22, 20), 'pir_titan')
            small('armsh', tube((sx * 1.0, -0.2, 3.0), (sx * 1.0, -0.2, 4.2), 0.40, 0.34, 20), 'pir_gun')
            for k in range(5):
                small('drill', tube((sx * 1.1, -0.25, 4.6 + k * 0.32), (sx * 1.1, -0.25, 4.6 + k * 0.32 + 0.12), 0.34 - k * 0.04, None, 20, cap=False), 'pir_gun')
            small('bit', tube((sx * 1.1, -0.25, 6.4), (sx * 1.1, -0.25, 7.0), 0.22, 0.03, 16), 'pir_yellow')
            small('hyd', tube((sx * 1.4, 0.2, 2.6), (sx * 1.3, -0.1, 4.8), 0.05, None, 8), 'pir_gun')
        for k in range(3):
            small('hrib', box_bm((0.0, 1.0 + 0.0, -3.0 + k * 1.0), (2.2, 0.06, 0.08)), 'pir_titan')
        small('chute', box_bm((0.0, 0.55, -0.5), (1.2, 0.1, 1.0)), 'pir_gun')
        small('strut', tube((-1.3, 0.8, -1.8), (-1.3, 0.3, -0.2), 0.05, None, 8), 'pir_gun')
    return {'hs': hs, 'union': union, 'engs': [(-0.85, 0.0, 0.5), (0.85, 0.0, 0.5)], 'zend': -4.6, 'hatch_z': [-3.0, -1.0], 'ring_z': [-3.2, -2.2, -1.2, -0.2, 0.8, 1.6],
            'nose_z': 3.4, 'tail_z': -3.9, 'canopy': (1.2, 2.7, 0.8, 0.5), 'win_z': [-2.6, -2.2, -1.8, 0.6, 0.9, 1.2], 'ytop': 0.8, 'ant_z': -2.6, 'mark_z': [-3.2, -2.5], 'gear': [(-1.0, -2.6), (1.0, -2.6), (0.0, 1.8)],
            'bplate_z': [-2.8, -0.6], 'details': details, 'nav': [(-1.8, 0.2, -2.0), (1.8, 0.2, -2.0), (0.0, 1.0, -3.8)], 'muz': [(0.0, 0.0, 4.0)], 'main': 'pir_orange', 'alt': 'pir_gray2', 'accent': 'pir_yellow', 'nose': 'plain'}


CFG = {}


CFG.update({'corvette': _cfg_corvette(), 'courier': _cfg_courier(), 'cargo': _cfg_cargo(), 'tanker': _cfg_tanker(), 'mining': _cfg_mining()})
