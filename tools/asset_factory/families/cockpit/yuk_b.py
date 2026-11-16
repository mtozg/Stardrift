"""Yük Devi kokpiti — konsept B "Kıskaç Gözü" + kullanıcı değişikliği (2026-11-16): ekranlar C'deki gibi panelden yükseltilmiş.
Kamera ve ekran sözleşmesi build.py ile aynıdır (P, face_eye, ekran dörtgeni UV sırası). Şahin'in dondurulmuş tarifine dokunmaz.

Kütleler (Blender: +Y ileri, +Z yukarı, göz orijinde):
  köprü kabini: ön duvar y=front_y, yanlarda geriye açılan eğik duvarlar; tavan kirişi (header), orta dikme, köşe ve yan dikmeler
  konsol: düz güverte (deck) + pilota eğilen ön yüz (fascia); ortada aşağı/öne bakan çene camı ve tüneli
  ekranlar: braketli kasalarda, üst kenarları konsol çizgisinin ~60–80 px üstünde
  kıskaç: ART_claw_root → shoulder → elbow → wrist → jaw_L / jaw_R (statik; pivotlar eklemde), çene camından görünür"""
import bpy, bmesh, math
from mathutils import Vector, Matrix
from core import geo
from families.cockpit.build import P, face_eye, grid, tube, lin, F, CX, CY, W, H


def wall_box(a, b, z0, z1, th):
    """İki (x, y) noktası arasında, gözden dışa doğru th kalınlığında duvar parçası."""
    a, b = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
    d = (b - a).normalized()
    n = Vector((d.y, -d.x, 0))
    if n.dot((a + b) / 2) < 0:
        n = -n
    bm = bmesh.new()
    pts = [a, b, b + n * th, a + n * th]
    lo = [bm.verts.new((p.x, p.y, z0)) for p in pts]
    hi = [bm.verts.new((p.x, p.y, z1)) for p in pts]
    bm.faces.new(lo[::-1])
    bm.faces.new(hi)
    for k in range(4):
        bm.faces.new((lo[k], lo[(k + 1) % 4], hi[(k + 1) % 4], hi[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def build(spec, mats):
    A = spec['params']
    obs = []

    def add(name, bm, mat, role='body', smooth=35, eye=False, solid=None, toward_eye=False):
        if eye:
            face_eye(bm)
        ob = geo.mesh_object(name, bm, mats[mat], coll='Asset', role=role)
        if solid:
            m = ob.modifiers.new('sol', 'SOLIDIFY')
            m.thickness = solid
            m.offset = 1.0 if toward_eye else -1.0
            geo.apply_modifier(ob, m)
        geo.set_smooth_by_angle(ob, smooth)
        obs.append(ob)
        return ob

    cb = A['cabin']
    fy, fh, zs, zh, zc = cb['front_y'], cb['front_half'], cb['sill_z'], cb['header_z'], cb['ceil_z']
    sb = cb['side_back']

    def side_pt(s, t):      # eğik yan duvar üzerinde nokta (t: 0 ön köşe → 1 arka)
        return (s * (fh + (sb[0] - fh) * t), fy + (sb[1] - fy) * t)

    # ---- köprü kabini: tavan kirişi, cam kenarı şeridi, alt eşik duvarı, dikmeler
    add('header_front', wall_box((-fh, fy), (fh, fy), zh, zc, 0.08), 'yuk_dark')
    add('glass_edge_front', wall_box((-fh, fy - 0.004), (fh, fy - 0.004), zh - 0.016, zh, 0.01), 'yuk_glass_edge')
    add('sill_front', wall_box((-fh, fy), (fh, fy), -0.62, zs, 0.06), 'yuk_paint')
    add('post_center', geo.bm_box((0, fy + 0.03, (zs + zh) / 2), (cb.get('post_w', 0.058), 0.06, zh - zs)), 'yuk_dark')
    for s in (-1, 1):
        sd = 'L' if s < 0 else 'R'
        c0, c1 = side_pt(s, 0), side_pt(s, 1)
        add('header_side_' + sd, wall_box(c0, c1, zh, zc, 0.08), 'yuk_dark')
        add('glass_edge_side_' + sd, wall_box(c0, c1, zh - 0.016, zh, 0.01), 'yuk_glass_edge')
        add('sill_side_' + sd, wall_box(c0, c1, -0.92, zs, 0.06), 'yuk_paint')
        add('post_corner_' + sd, wall_box(side_pt(s, -0.03), side_pt(s, 0.04), zs, zh, 0.07), 'yuk_dark')
        t = cb['side_post_t']
        add('post_side_' + sd, wall_box(side_pt(s, t - 0.04), side_pt(s, t + 0.04), zs, zh, 0.07), 'yuk_dark')
        add('wall_side_' + sd, wall_box((s * sb[0], sb[1]), (s * sb[0], -0.9), -0.92, zc, 0.06), 'yuk_paint')
        add('lamp_side_' + sd, geo.bm_box((s * 0.80, 0.58, -0.33), (0.03, 0.015, 0.015)), 'emit_amber', role='emit_live')
        add('lamp_header_' + sd, geo.bm_cylinder((s * 0.45, fy - 0.005, 0.53), (s * 0.45, fy - 0.03, 0.53), 0.022, 14), 'emit_amber', role='emit_live', smooth=60)
    add('lamp_header_C', geo.bm_cylinder((0, fy - 0.005, 0.53), (0, fy - 0.035, 0.53), 0.028, 16), 'emit_amber', role='emit_live', smooth=60)
    add('ceiling', geo.bm_box((0, (fy + 0.08 - 0.9) / 2, zc + 0.02), (2 * sb[0] + 0.12, fy + 0.08 + 0.9, 0.04)), 'yuk_dark')
    add('floor', geo.bm_box((0, -0.1, -0.92), (2 * sb[0], 1.4, 0.04)), 'yuk_dark')

    # ---- konsol: güverte + pilota eğilen ön yüz (fascia), ortada çene camı açıklığı
    dk = A['deck']
    ey, ez = dk['edge_y'], dk['z']
    slope = dk['fascia_dir'][1] / dk['fascia_dir'][0]

    def fd(v):      # fascia düzleminin (u'dan bağımsız) v pikselindeki derinliği: ışın ∩ düzlem
        k = -(v - CY) / F
        return (ez - slope * ey) / (k - slope)

    hx = dk['half']
    def xw(y):      # kabin iç genişliği (yarı): ön duvarda fh, eğik yan duvar boyunca genişler
        return fh + (sb[0] - fh) * min(1.0, max(0.0, (fy - y) / (fy - sb[1])))
    add('deck', grid([[Vector((x, ey, ez)) for x in lin(-xw(ey), xw(ey), 9)], [Vector((x, fy, ez)) for x in lin(-fh, fh, 9)]]), 'yuk_paint', eye=True, solid=0.03)
    uw = lambda v, s: CX + s * F * xw(fd(v)) / fd(v)      # konsol satırını yan duvarda kes (r001: kabin dışına taşıyordu)
    v_lip = 239.5 - F * ez / ey
    cq = A['chin']['quad']
    cv0 = cq[0][1]
    uL = lambda v: cq[0][0] + (cq[3][0] - cq[0][0]) * (v - cv0) / (cq[3][1] - cv0)
    uR = lambda v: cq[1][0] + (cq[2][0] - cq[1][0]) * (v - cv0) / (cq[2][1] - cv0)
    VT = lin(v_lip, cv0, 6)
    add('fascia_top', grid([[P(u, v, fd(v)) for u in lin(uw(v, -1), uw(v, 1), 27)] for v in VT]), 'yuk_paint', eye=True, solid=0.03)
    VB = lin(cv0, 760, 8)
    add('fascia_L', grid([[P(u, v, fd(v)) for u in lin(uw(v, -1), uL(v), 14)] for v in VB]), 'yuk_paint', eye=True, solid=0.03)
    add('fascia_R', grid([[P(u, v, fd(v)) for u in lin(uR(v), uw(v, 1), 14)] for v in VB]), 'yuk_paint', eye=True, solid=0.03)
    # güverte dudağı: siyah şerit + eğik sarı parçalar (uyarı şeridi)
    add('lip_black', geo.bm_box((0, ey - 0.006, ez - 0.02), (2 * hx * 0.92, 0.012, 0.04)), 'yuk_black')
    bm = bmesh.new()
    for x in lin(-0.88, 0.88, 23):
        q = [bm.verts.new(p) for p in ((x - 0.02, ey - 0.014, ez - 0.002), (x + 0.012, ey - 0.014, ez - 0.002), (x - 0.008, ey - 0.014, ez - 0.038), (x - 0.04, ey - 0.014, ez - 0.038))]
        bm.faces.new(q)
    add('lip_hazard', bm, 'yuk_hazard', eye=True, solid=0.004, toward_eye=True)

    # ---- çene camı: çerçeve (bezel), görüş ışınları boyunca tünel, üst kenarda uyarı şeridi
    ring_in = [P(u, v, fd(v) - 0.004) for u, v in cq]
    cu, cvm = sum(u for u, _ in cq) / 4, sum(v for _, v in cq) / 4
    outer = [(u + (u - cu) / math.hypot(u - cu, v - cvm) * 26, v + (v - cvm) / math.hypot(u - cu, v - cvm) * 26) for u, v in cq]
    ring_out = [P(u, v, fd(v) - 0.004) for u, v in outer]
    bm = bmesh.new()
    vi = [bm.verts.new(p) for p in ring_in]
    vo = [bm.verts.new(p) for p in ring_out]
    for k in range(4):
        bm.faces.new((vo[k], vo[(k + 1) % 4], vi[(k + 1) % 4], vi[k]))
    add('chin_bezel', bm, 'yuk_dark', eye=True, solid=0.02, toward_eye=True)
    tf = A['chin']['tunnel']
    bm = bmesh.new()
    a = [bm.verts.new(p) for p in ring_in]
    b = [bm.verts.new(p * tf) for p in ring_in]
    for k in range(4):
        bm.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
    add('chin_tunnel', bm, 'yuk_dark', eye=True, solid=0.02)
    add('chin_glass_edge', tube([p * 1.002 for p in ring_in] + [ring_in[0] * 1.002], 0.006, 6), 'yuk_glass_edge', smooth=60)
    bm = bmesh.new()
    for u in lin(cq[0][0] + 10, cq[1][0] - 10, 11):
        v0, v1 = cv0 - 34, cv0 - 18
        q = [bm.verts.new(P(uu, vv, fd(vv) - 0.006)) for uu, vv in ((u - 8, v0), (u + 6, v0), (u - 2, v1), (u - 16, v1))]
        bm.faces.new(q)
    add('chin_hazard', bm, 'yuk_hazard', eye=True, solid=0.004, toward_eye=True)

    # ---- ekranlar: braketli kasalar, panelden yükseltilmiş (C'deki gibi)
    sc = A['screens']

    def screen(name, q, depths, bezel_px=14):
        pts = [P(u, v, d) for (u, v), d in zip(q, depths)]
        bm = bmesh.new()
        f = bm.faces.new([bm.verts.new(p) for p in pts])
        uvl = bm.loops.layers.uv.new('UVMap')
        for loop, uv in zip(f.loops, [(0, 1), (1, 1), (1, 0), (0, 0)]):
            loop[uvl].uv = uv
        face_eye(bm)
        ob = geo.mesh_object(name, bm, mats['screen_placeholder'], coll='Asset', role='screen')
        obs.append(ob)
        cu = sum(u for u, v in q) / 4
        cv = sum(v for u, v in q) / 4
        outer = []
        for (u, v), d in zip(q, depths):
            du, dv = u - cu, v - cv
            l = math.hypot(du, dv)
            outer.append(((u + du / l * bezel_px * 1.4, v + dv / l * bezel_px * 1.4), d))
        rin = [P(u, v, d + 0.002) for (u, v), d in zip(q, depths)]
        rout = [P(u, v, d + 0.002) for (u, v), d in outer]
        bm2 = bmesh.new()
        vi = [bm2.verts.new(p) for p in rin]
        vo = [bm2.verts.new(p) for p in rout]
        for k in range(4):
            bm2.faces.new((vo[k], vo[(k + 1) % 4], vi[(k + 1) % 4], vi[k]))
        key = name.replace('SCR_', '').lower()
        add('bezel_' + key, bm2, 'yuk_dark', eye=True, solid=0.008, toward_eye=True)
        # kasa: dış çerçevenin arkasında 6 cm derin kutu (gözden uzağa)
        bm3 = bmesh.new()
        fr = [bm3.verts.new(p) for p in rout]
        bk = [bm3.verts.new(p + p.normalized() * 0.06) for p in rout]
        bm3.faces.new(bk)
        for k in range(4):
            bm3.faces.new((fr[k], fr[(k + 1) % 4], bk[(k + 1) % 4], bk[k]))
        add('housing_' + key, bm3, 'yuk_dark', eye=True)
        # braket: kasa sırtından konsol yüzüne iki kol
        for side in (0.3, 0.7):
            (u0, v0), d0 = outer[3][0], outer[3][1]
            (u1, v1), d1 = outer[2][0], outer[2][1]
            u = u0 + (u1 - u0) * side
            v = v0 + (v1 - v0) * side - 30
            d = d0 + (d1 - d0) * side
            p0 = P(u, v, d + 0.06)
            p1 = P(u, v + 12, fd(v + 12) + 0.01)
            if (p1 - p0).length > 0.01:
                add('bracket_%s_%d' % (key, int(side * 10)), geo.bm_cylinder(p0, p1, 0.016, 10), 'gunmetal', smooth=60)
        return ob

    sd0, sd1 = sc['side_depth']
    screen('SCR_RADAR', sc['radar'], [sc['radar_depth']] * 4, bezel_px=9)
    screen('SCR_SYS', sc['sys'], [sd0, sd1, sd1, sd0])
    screen('SCR_HULL', sc['hull'], [sd1, sd0, sd0, sd1])

    # ---- kıskaç kumanda kolları (çene camının iki yanında)
    lv = A['levers']
    for u in lv['u']:
        x = (u - CX) / F * lv['depth']
        add('lever_shaft_%d' % u, geo.bm_cylinder((x, 0.62, -0.75), (x, 0.58, -0.52), 0.014, 12), 'gunmetal', smooth=60)
        add('lever_grip_%d' % u, geo.bm_cylinder((x, 0.58, -0.52), (x, 0.575, -0.46), 0.03, 14), 'yuk_hazard', smooth=60)
        add('lever_cap_%d' % u, geo.bm_cylinder((x, 0.575, -0.46), (x, 0.574, -0.445), 0.026, 14), 'yuk_black', smooth=60)

    # ---- koltuk (pilot görüşünde görünmez; çapraz ve plan görünüşleri için)
    st = A['seat']
    pz = st['pan_z']
    add('seat_pan', geo.bm_box((0, -0.02, pz), (0.58, 0.52, 0.13)), 'seat_textile')
    back = geo.bm_box((0, -0.31, pz + 0.42), (0.56, 0.12, 0.80))
    bmesh.ops.rotate(back, cent=Vector((0, -0.31, pz + 0.02)), matrix=Matrix.Rotation(math.radians(-st['recline_deg']), 3, 'X'), verts=back.verts)
    add('seat_back', back, 'seat_textile')
    for s in (-1, 1):
        add('seat_arm_%s' % ('L' if s < 0 else 'R'), geo.bm_box((s * 0.34, -0.05, pz + 0.17), (0.09, 0.46, 0.08)), 'yuk_dark')
    add('seat_base', geo.bm_box((0, -0.05, pz - 0.18), (0.36, 0.5, 0.24)), 'gunmetal')

    # ---- kıskaç: statik, animasyona hazır hiyerarşi (STANDARDS §0.3)
    cl = A['claw']
    root, elbow, wrist = Vector(cl['root']), Vector(cl['elbow']), Vector(cl['wrist'])
    shoulder = root + Vector((0, 0.02, -0.04))
    joints = {}

    def joint(name, loc, parent, axis):
        e = bpy.data.objects.new(name, None)
        geo.collection('Asset').objects.link(e)
        e.location = loc
        e['sd_joint'] = axis
        if parent:
            e.parent = joints[parent]
            e.matrix_parent_inverse = joints[parent].matrix_world.inverted()
        bpy.context.view_layer.update()
        joints[name] = e
        return e

    joint('ART_claw_root', root, None, 'sabit: gövde bağlantısı')
    joint('ART_claw_shoulder', shoulder, 'ART_claw_root', 'X (yan eksen): kaldırma')
    joint('ART_claw_elbow', elbow, 'ART_claw_shoulder', 'X: dirsek')
    joint('ART_claw_wrist', wrist, 'ART_claw_elbow', 'kol ekseni (ileri-aşağı): bilek dönüşü')
    R, gap = cl['jaw_r'], cl['jaw_gap']
    d = (wrist - elbow).normalized()      # kol ekseni (ileri-aşağı)
    xa = Vector((1, 0, 0))
    nrm = d.cross(xa).normalized()        # çene düzleminin normali: çeneler yana (sol/sağ) açılır → kokpitten yukarıdan kerpeten şekli okunur (r004)
    c = wrist + d * R * 0.78              # çene yayı merkezi bileğin önünde
    joint('ART_claw_jaw_L', wrist - xa * 0.06 + d * 0.04, 'ART_claw_wrist', 'çene düzlemi normali: sol çene açma')
    joint('ART_claw_jaw_R', wrist + xa * 0.06 + d * 0.04, 'ART_claw_wrist', 'çene düzlemi normali: sağ çene açma')

    def part(name, bm, mat, parent, smooth=60):
        ob = add(name, bm, mat, smooth=smooth)
        ob.parent = joints[parent]
        ob.matrix_parent_inverse = joints[parent].matrix_world.inverted()
        return ob

    # bağlantı kutusu kökün üstünde: göz ışınlarında k > −0,75 (çene camının üst kenarı) → fascia arkasında gizli. r002: burun plakası çene ışınlarını kesiyordu, kaldırıldı
    part('claw_mount', geo.bm_box(tuple(root + Vector((0, 0, 0.04))), (0.22, 0.16, 0.08)), 'yuk_dark', 'ART_claw_root', smooth=35)
    for s in (-1, 1):
        o = nrm * s * gap * 0.25      # çift plakalı kol: çene düzleminin iki yanında
        part('claw_upper_arm_%d' % s, geo.bm_cylinder(shoulder + o, elbow + o, 0.04, 12), 'yuk_rust', 'ART_claw_shoulder')
        part('claw_fore_arm_%d' % s, geo.bm_cylinder(elbow + o, wrist + o, 0.036, 12), 'yuk_rust', 'ART_claw_elbow')
    part('claw_elbow_pin', geo.bm_cylinder(elbow - xa * 0.09, elbow + xa * 0.09, 0.045, 16), 'gunmetal', 'ART_claw_elbow')
    part('claw_hub', geo.bm_cylinder(wrist - d * 0.05, wrist + d * 0.09, 0.08, 18), 'gunmetal', 'ART_claw_wrist')
    tr = cl.get('tube_r', 0.022)
    for jn, sx in (('L', -1), ('R', 1)):
        pts = [c + R * (-math.cos(math.radians(a)) * d + math.sin(math.radians(a)) * sx * xa) for a in lin(12, 158, 16)]
        part('claw_jaw_%s' % jn, tube(pts, tr, 12), 'yuk_rust', 'ART_claw_jaw_' + jn)
        tip = pts[-1]
        part('claw_tooth_%s' % jn, geo.bm_cylinder(tip - nrm * 0.03, tip + nrm * 0.03, tr * 1.25, 12), 'gunmetal', 'ART_claw_jaw_' + jn)

    socks = [{'name': 'SOCK_cam_0', 'loc': (0, 0, 0), 'dir': (0, 1, 0), 'extras': {'purpose': 'pilot gözü (kamera sözleşmesi)', 'fovy': 74}},
             {'name': 'SOCK_claw_grip', 'loc': tuple(c + Vector((0, R, 0))), 'dir': (0, 1, 0), 'extras': {'purpose': 'kıskaç kavrama noktası', 'parent': 'ART_claw_wrist'}}]
    return {'objects': obs, 'sockets': socks}
