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
from families.cockpit.build import P, face_eye, grid, tube, lin, F, CX, CY, W, H, Soft, soft_box


class Acc:
    """Aynı malzemeli küçük parçaları tek bmesh'te toplar (PRODUCTION ayrıntısı: nesne sayısı düşük kalır)."""
    def __init__(self):
        self.bm = bmesh.new()

    def box(self, c, s, rot_z=0.0, skew=0.0):
        """skew: x'= x + skew·z (kesme): yükseklik boyunca yana kayan paralelkenar; çapraz uyarı bantları için."""
        r = bmesh.ops.create_cube(self.bm, size=1.0)
        sh = Matrix(((1, 0, skew, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
        bmesh.ops.transform(self.bm, matrix=Matrix.Translation(Vector(c)) @ Matrix.Rotation(rot_z, 4, 'Z') @ Matrix.Diagonal((*s, 1.0)) @ sh, verts=r['verts'])

    def cyl(self, p0, p1, r, seg=6):
        p0, p1 = Vector(p0), Vector(p1)
        d = p1 - p0
        up = 'X' if abs(d.normalized().y) > 0.99 else 'Y'
        M = Matrix.Translation((p0 + p1) / 2) @ d.to_track_quat('Z', up).to_matrix().to_4x4()
        bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r, depth=d.length, matrix=M)

    def empty(self):
        return len(self.bm.verts) == 0


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
    prod = spec.get('profile') == 'PRODUCTION'
    rivets, dark_d, black_d, rust_d, hazard_d, lamps_d, pale_d, steel_d = Acc(), Acc(), Acc(), Acc(), Acc(), Acc(), Acc(), Acc()      # PRODUCTION ayrıntı grupları (malzeme başına tek nesne)

    def add(name, bm, mat, role='body', smooth=35, eye=False, solid=None, toward_eye=False):
        sft = bm if isinstance(bm, Soft) else None
        if sft:
            bm = sft.bm
        if eye:
            face_eye(bm)
        ob = geo.mesh_object(name, bm, mats[mat], coll='Asset', role=role)
        if sft:
            mb = ob.modifiers.new('bev', 'BEVEL')
            mb.width = sft.bev
            mb.segments = 2
            mb.limit_method = 'NONE'
            geo.apply_modifier(ob, mb)
            ms = ob.modifiers.new('ss', 'SUBSURF')
            ms.levels = sft.level
            ms.render_levels = sft.level
            geo.apply_modifier(ob, ms)
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
        Ls = math.hypot(sb[0] - fh, sb[1] - fy)      # eğik yan duvarın uzunluğu (t parametresi → metre)
        cw, sw_, pt_ = cb.get('post_corner_w', 0.0676), cb.get('post_side_w', 0.0772), cb.get('post_t', 0.07)      # dikme genişliği (duvar boyunca) ve kalınlığı (dışa) — r009: Mehmet 'dikmeler çok kalın'
        tc = 0.005
        add('post_corner_' + sd, wall_box(side_pt(s, tc - cw / 2 / Ls), side_pt(s, tc + cw / 2 / Ls), zs, zh, pt_), 'yuk_dark')
        t = cb['side_post_t']
        add('post_side_' + sd, wall_box(side_pt(s, t - sw_ / 2 / Ls), side_pt(s, t + sw_ / 2 / Ls), zs, zh, pt_), 'yuk_dark')
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
    for u in ([] if prod else lin(cq[0][0] + 10, cq[1][0] - 10, 11)):
        v0, v1 = cv0 - 34, cv0 - 18
        q = [bm.verts.new(P(uu, vv, fd(vv) - 0.006)) for uu, vv in ((u - 8, v0), (u + 6, v0), (u - 2, v1), (u - 16, v1))]
        bm.faces.new(q)
    if not prod:
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
        if prod:      # çerçeve köşelerinde bulon başları; ekran altında etiket plakası ve üç durum lambası
            for pp in rout:
                rivets.cyl(pp - pp.normalized() * 0.005, pp - pp.normalized() * 0.011, 0.0062, 6)
            pm = (rout[2] + rout[3]) / 2
            pale_d.box((pm.x, pm.y - 0.010, pm.z - 0.016), (0.11, 0.006, 0.022))
            for dx_ in (-0.065, 0.065):
                lamps_d.cyl((pm.x + dx_, pm.y - 0.010, pm.z - 0.016), (pm.x + dx_, pm.y - 0.017, pm.z - 0.016), 0.0058, 6)
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
    for u in ([] if prod else lv['u']):
        x = (u - CX) / F * lv['depth']
        add('lever_shaft_%d' % u, geo.bm_cylinder((x, 0.62, -0.75), (x, 0.58, -0.52), 0.014, 12), 'gunmetal', smooth=60)
        add('lever_grip_%d' % u, geo.bm_cylinder((x, 0.58, -0.52), (x, 0.575, -0.46), 0.03, 14), 'yuk_hazard', smooth=60)
        add('lever_cap_%d' % u, geo.bm_cylinder((x, 0.575, -0.46), (x, 0.574, -0.445), 0.026, 14), 'yuk_black', smooth=60)

    # ---- PRODUCTION ayrıntısı (kokpit gövdesi): perçin sıraları, flanşlar, plakalar, havalandırma, anahtar panelleri, ikaz lambaları
    if prod:
        # (1) başlık kirişi: ön yüzde iki perçin sırası + alt flanş şeridi; yan başlıklarda aynı sıralar eğik hat boyunca
        for z in (zh + 0.026, zc - 0.026):
            for x in lin(-fh + 0.06, fh - 0.06, 17):
                if abs(x) > 0.05:
                    rivets.cyl((x, fy - 0.0085, z), (x, fy, z), 0.0075, 6)
        dark_d.box((0, fy - 0.015, zh + 0.012), (2 * fh, 0.03, 0.024))
        for sd in (-1, 1):
            a2, b2 = Vector((*side_pt(sd, 0), 0)), Vector((*side_pt(sd, 1), 0))
            dd = (b2 - a2).normalized()
            nn = Vector((dd.y, -dd.x, 0))
            if nn.dot((a2 + b2) / 2) < 0:
                nn = -nn
            inw = -nn
            for z in (zh + 0.026, zc - 0.026):
                for t in lin(0.05, 0.95, 9):
                    pp = a2 + (b2 - a2) * t
                    rivets.cyl((pp.x, pp.y, z), (pp.x + inw.x * 0.0085, pp.y + inw.y * 0.0085, z), 0.0075, 6)
            # dikme tabanı ve tepesinde bağlantı plakaları + 4 bulon
            for t, pw_ in ((0.0, cb.get('post_corner_w', 0.0676)), (cb['side_post_t'], cb.get('post_side_w', 0.0772))):
                pp = a2 + (b2 - a2) * t
                for z in (zs + 0.05, zh - 0.05):
                    dark_d.box((pp.x + inw.x * 0.004, pp.y + inw.y * 0.004, z), (pw_ + 0.016, pw_ + 0.016, 0.08), rot_z=math.atan2(dd.y, dd.x))
        for z in (zs + 0.055, zh - 0.055):      # orta dikme plakaları
            pw2 = cb.get('post_plate_w', 0.1)      # orta dikme plakası genişliği (HUD bölgesindeki engel)
            dark_d.box((0, fy - 0.006, z), (pw2, 0.012, 0.07))
            for dx in (-0.32 * pw2, 0.32 * pw2):
                for dz in (-0.022, 0.022):
                    rivets.cyl((dx, fy - 0.0125, z + dz), (dx, fy - 0.006, z + dz), 0.007, 6)

        # (2) güverte dudağı: perçin sırası; güverte plakaları, havalandırma ızgaraları, anahtar kapakları
        for x in lin(-0.86, 0.86, 29):
            rivets.cyl((x, ey - 0.014, ez - 0.045), (x, ey - 0.006, ez - 0.045), 0.0055, 6)
        for sd in (-1, 1):
            gx, gy = sd * 0.43, 0.94
            dark_d.box((gx, gy, ez + 0.006), (0.22, 0.15, 0.012))
            for k in range(8):
                black_d.box((gx, gy - 0.062 + k * 0.0177, ez + 0.0145), (0.19, 0.007, 0.01))
            for k in range(3):      # anahtar kapakları (kaldırma kolları)
                cx_ = sd * (0.19 + k * 0.045)
                rust_d.box((cx_, 0.86, ez + 0.014), (0.032, 0.034, 0.028))
                hazard_d.cyl((cx_, 0.86, ez + 0.026), (cx_, 0.86, ez + 0.044), 0.006, 6)
            dark_d.box((sd * 0.62, 0.95, ez + 0.008), (0.12, 0.10, 0.016))      # kenar servis kapağı
            for dx_ in (-0.05, 0.05):
                for dy_ in (-0.035, 0.035):
                    rivets.cyl((sd * 0.62 + dx_, 0.95 + dy_, ez + 0.016), (sd * 0.62 + dx_, 0.95 + dy_, ez + 0.0235), 0.0065, 6)

        # (3) konsol ön yüzü (fascia): panel dikişleri, anahtar panelleri, ikaz lambaları, kadran
        def onF(u, v, off=0.0):
            return P(u, v, fd(v) - off)

        def seam(u, v0, v1):
            pc = onF(u, (v0 + v1) / 2, 0.003)
            black_d.box((pc.x, pc.y, pc.z), (0.006, 0.004, abs(v1 - v0) / F * fd((v0 + v1) / 2)))
        for u in (300, 1300):
            seam(u, 566, 656)
        for u in (590, 1010):
            seam(u, 580, 656)
        for u in lin(cq[0][0] + 16, cq[1][0] - 16, 12):      # çene camı çerçevesi perçinleri
            pp = onF(u, cv0 - 13, 0.0)
            rivets.cyl((pp.x, pp.y - 0.003, pp.z), (pp.x, pp.y - 0.0115, pp.z), 0.0062, 6)

        # ---- r011: gerçekçi kumanda kitaplığı + orta konsol (Mehmet: oyuncak düğmeler, boş orta bölge) ----
        # Kural: ana tonlar boyalı haki / koyu çelik / mat metal / kauçuk; sarı-turuncu yalnız küçük vurgu (uç, nokta, tek tek parça).
        def plate(u0, v0, u1, v1, acc, off=0.0075, depth=0.010):
            pa, pb = onF(u0, v0, 0.0), onF(u1, v1, 0.0)
            acc.box(((pa.x + pb.x) / 2, pa.y - off, (pa.z + pb.z) / 2), (abs(pb.x - pa.x), depth, abs(pa.z - pb.z)))

        def frame(u0, v0, u1, v1, acc, th=3, off=0.0085, depth=0.010):
            plate(u0, v0, u1, v0 + th, acc, off, depth); plate(u0, v1 - th, u1, v1, acc, off, depth)
            plate(u0, v0, u0 + th, v1, acc, off, depth); plate(u1 - th, v0, u1, v1, acc, off, depth)

        def label(pc, w, h, n=5, seed=0):      # etiket plakası + baskı çizgileri
            pale_d.box((pc.x, pc.y - 0.0035, pc.z), (w, 0.0035, h))
            x0 = pc.x - w / 2 + 0.004
            for k in range(n):
                bw = 0.004 + 0.009 * (((k + seed) * 7) % 5) / 4
                if x0 + bw > pc.x + w / 2 - 0.003:
                    break
                black_d.box((x0 + bw / 2, pc.y - 0.0058, pc.z), (bw, 0.0016, h * 0.42))
                x0 += bw + 0.004

        def toggle(pc, guarded=False, accent=False):      # mandal anahtar: taban plakası, kovan halkası, ince çelik mandal, kauçuk uç, isteğe bağlı menteşeli koruma kapağı
            dark_d.box((pc.x, pc.y - 0.004, pc.z), (0.024, 0.008, 0.026))
            steel_d.cyl((pc.x, pc.y - 0.007, pc.z), (pc.x, pc.y - 0.0135, pc.z), 0.0085, 8)
            tip = (pc.x, pc.y - 0.034, pc.z + 0.007)
            steel_d.cyl((pc.x, pc.y - 0.0135, pc.z), tip, 0.0032, 5)
            (rust_d if accent else black_d).cyl(tip, (tip[0], tip[1] - 0.007, tip[2] + 0.002), 0.0052, 6)
            if guarded:
                dark_d.box((pc.x, pc.y - 0.027, pc.z + 0.002), (0.022, 0.003, 0.024))
                steel_d.cyl((pc.x - 0.011, pc.y - 0.027, pc.z + 0.0155), (pc.x + 0.011, pc.y - 0.027, pc.z + 0.0155), 0.0028, 5)

        def knob(pc, r=0.0105, ticks=True):      # ribli döner düğme: çelik etek, kauçuk gövde, 8 rib, işaret çizgisi, kadran tikleri
            steel_d.cyl((pc.x, pc.y - 0.002, pc.z), (pc.x, pc.y - 0.007, pc.z), r * 1.55, 10)
            black_d.cyl((pc.x, pc.y - 0.007, pc.z), (pc.x, pc.y - 0.022, pc.z), r, 8)
            for k in range(8):
                a_ = k * math.pi / 4
                black_d.box((pc.x + (r + 0.0011) * math.cos(a_), pc.y - 0.0145, pc.z + (r + 0.0011) * math.sin(a_)), (0.0032, 0.013, 0.0032))
            pale_d.box((pc.x, pc.y - 0.0228, pc.z + r * 0.45), (0.0022, 0.0016, r * 0.8))
            if ticks:
                for k in range(9):
                    a_ = math.radians(-125 + k * 31)
                    pale_d.box((pc.x + 1.9 * r * math.sin(a_), pc.y - 0.0045, pc.z + 1.9 * r * math.cos(a_)), (0.0024, 0.0016, 0.0055))

        def pbutton(pc, accent=False):      # çerçeveli basma düğmesi + koruma kafesi
            steel_d.box((pc.x, pc.y - 0.004, pc.z), (0.034, 0.008, 0.034))
            black_d.cyl((pc.x, pc.y - 0.008, pc.z), (pc.x, pc.y - 0.019, pc.z), 0.0105, 8)
            (rust_d if accent else pale_d).cyl((pc.x, pc.y - 0.019, pc.z), (pc.x, pc.y - 0.0205, pc.z), 0.0072, 8)
            for dx_, dz_ in ((-0.0145, -0.0145), (0.0145, -0.0145), (-0.0145, 0.0145), (0.0145, 0.0145)):
                steel_d.cyl((pc.x + dx_, pc.y - 0.008, pc.z + dz_), (pc.x + dx_, pc.y - 0.027, pc.z + dz_), 0.0019, 4)
            for dz_ in (-0.0145, 0.0145):
                steel_d.box((pc.x, pc.y - 0.027, pc.z + dz_), (0.031, 0.0035, 0.0035))
            for dx_ in (-0.0145, 0.0145):
                steel_d.box((pc.x + dx_, pc.y - 0.027, pc.z), (0.0035, 0.0035, 0.031))

        def gauge(pc, r=0.03):      # gösterge: çelik halka, kadran, 11 tik, ibre, cam kenarı
            steel_d.cyl((pc.x, pc.y - 0.004, pc.z), (pc.x, pc.y - 0.0175, pc.z), r + 0.005, 12)
            black_d.cyl((pc.x, pc.y - 0.0175, pc.z), (pc.x, pc.y - 0.0205, pc.z), r, 12)
            for k in range(11):
                a_ = math.radians(-120 + k * 24)
                pale_d.box((pc.x + 0.82 * r * math.sin(a_), pc.y - 0.0215, pc.z + 0.82 * r * math.cos(a_)), (0.0022, 0.0014, 0.0065))
            pale_d.box((pc.x + 0.004, pc.y - 0.0225, pc.z + 0.008), (0.0024, 0.0014, 0.02), rot_z=0.0, skew=0.35)
            steel_d.cyl((pc.x, pc.y - 0.0225, pc.z), (pc.x, pc.y - 0.026, pc.z), 0.0042, 6)

        def relay(pc, seed=0):      # röle/sigorta modülü: gövde, etiket şeridi, iki LED
            dark_d.box((pc.x, pc.y - 0.007, pc.z), (0.019, 0.014, 0.024))
            pale_d.box((pc.x, pc.y - 0.0145, pc.z + 0.004), (0.014, 0.0016, 0.007))
            lamps_d.cyl((pc.x - 0.005, pc.y - 0.0145, pc.z - 0.007), (pc.x - 0.005, pc.y - 0.0185, pc.z - 0.007), 0.0021, 5)
            steel_d.cyl((pc.x + 0.004, pc.y - 0.014, pc.z - 0.007), (pc.x + 0.004, pc.y - 0.0185, pc.z - 0.007), 0.0036, 6)

        def vent(u0, v0, u1, v1, n=6):
            plate(u0, v0, u1, v1, dark_d, 0.008, 0.012)
            pa, pb = onF(u0, v0, 0.0), onF(u1, v1, 0.0)
            for k in range(n):
                zc_ = pa.z + (pb.z - pa.z) * (k + 0.5) / n
                black_d.box(((pa.x + pb.x) / 2, pa.y - 0.0105, zc_), (abs(pb.x - pa.x) * 0.82, 0.006, abs(pa.z - pb.z) / n * 0.5))
            frame(u0, v0, u1, v1, steel_d, 2, 0.0095, 0.006)

        def bundle(pts, r=0.0065, n=3):      # kablo demeti: paralel kauçuk borular + çelik kelepçeler
            for i_ in range(n):
                off = (i_ - (n - 1) / 2) * r * 1.9
                for (x1, y1, z1), (x2, y2, z2) in zip(pts[:-1], pts[1:]):
                    black_d.cyl((x1 + off, y1, z1), (x2 + off, y2, z2), r, 6)
            for (x1, y1, z1) in pts[1:-1]:
                steel_d.box((x1, y1, z1), (n * r * 2.1 + 0.006, 0.014, 0.012))

        # --- A: radarın altındaki şerit (çene camının üstü): röle/sigorta paneli, kablo demeti, etiketler
        pA = [onF(u, 560, 0.0) for u in (650, 950)]
        plate(646, 543, 954, 580, dark_d, 0.0065, 0.009)
        frame(646, 543, 954, 580, steel_d, 2, 0.0075, 0.006)
        for k_, u_ in enumerate(lin(668, 932, 12)):
            pc = onF(u_, 556, 0.0)
            relay(pc, k_)
        for k_, u_ in enumerate(lin(668, 932, 6)):      # ikinci sıra: küçük gösterge lambaları + etiketler
            pc = onF(u_, 572, 0.0)
            label(pc, 0.034, 0.011, 4, k_)
            lamps_d.cyl((pc.x + 0.024, pc.y - 0.006, pc.z), (pc.x + 0.024, pc.y - 0.012, pc.z), 0.0026, 5)
        # --- B/C: çene camının iki yanındaki orta paneller
        for sd, (u0, u1) in ((-1, (578, 676)), (1, (924, 1022))):
            plate(u0, 586, u1, 654, dark_d, 0.0065, 0.009)
            frame(u0, 586, u1, 654, steel_d, 2, 0.0075, 0.006)
            if sd < 0:
                vent(u0 + 8, 594, u1 - 8, 616, 7)
                for u_ in (u0 + 26, u1 - 26):
                    knob(onF(u_, 634, 0.0))
                label(onF((u0 + u1) / 2, 648, 0.0), 0.075, 0.012, 6, 1)
            else:
                for r_, v_ in enumerate((602, 626)):
                    for k_, u_ in enumerate(lin(u0 + 18, u1 - 18, 3)):
                        toggle(onF(u_, v_, 0.0), guarded=(k_ + r_) % 2 == 0, accent=(k_ == 1 and r_ == 0))
                label(onF((u0 + u1) / 2, 646, 0.0), 0.075, 0.012, 6, 3)
                for u_ in lin(u0 + 12, u1 - 12, 4):
                    lamps_d.cyl((onF(u_, 591, 0.0).x, onF(u_, 591, 0.0).y - 0.004, onF(u_, 591, 0.0).z), (onF(u_, 591, 0.0).x, onF(u_, 591, 0.0).y - 0.009, onF(u_, 591, 0.0).z), 0.0028, 5)
        # kablo demetleri: şeridin altından çene camı kenarlarına
        for sd, u_ in ((-1, 676), (1, 924)):
            p1, p2, p3 = onF(u_, 580, 0.012), onF(u_ + sd * -10, 600, 0.012), onF(u_ + sd * -22, 640, 0.012)
            bundle([(p1.x, p1.y, p1.z), (p2.x, p2.y, p2.z), (p3.x, p3.y, p3.z)])
        # --- D: sol/sağ kanat (kıskaç kumanda grubu ve göstergeler)
        for sd, (u0, u1) in ((-1, (330, 522)), (1, (1078, 1270))):
            plate(u0, 572, u1, 650, dark_d, 0.006, 0.009)
            frame(u0, 572, u1, 650, steel_d, 2, 0.0075, 0.006)
            plate(u0 + 4, 572, u1 - 4, 575, rust_d, 0.0085, 0.004)      # tek ince turuncu vurgu çizgisi
            for u_ in lin(u0 + 20, u1 - 20, 7):
                pc = onF(u_, 582, 0.0)
                lamps_d.cyl((pc.x, pc.y - 0.004, pc.z), (pc.x, pc.y - 0.009, pc.z), 0.0028, 5)
            if sd < 0:      # kıskaç kumanda grubu
                for k_, u_ in enumerate(lin(u0 + 30, u1 - 30, 4)):
                    pbutton(onF(u_, 604, 0.0), accent=(k_ == 0))
                for r_, v_ in enumerate((630,)):
                    for k_, u_ in enumerate(lin(u0 + 22, u1 - 22, 6)):
                        toggle(onF(u_, v_, 0.0), guarded=(k_ % 3 == 0), accent=(k_ == 5))
                label(onF((u0 + u1) / 2, 645, 0.0), 0.11, 0.011, 7, 5)
            else:
                for k_, u_ in enumerate(lin(u0 + 38, u1 - 38, 3)):
                    gauge(onF(u_, 606, 0.0), 0.029)
                for k_, u_ in enumerate(lin(u0 + 22, u1 - 22, 6)):
                    toggle(onF(u_, 634, 0.0), guarded=(k_ % 2 == 1), accent=(k_ == 0))
                label(onF((u0 + u1) / 2, 646, 0.0), 0.11, 0.011, 7, 2)
        # --- E: kumanda kolları: kauçuk körük, çelik bilezik, kauçuk kaplı ribli tutamak, etiketli başlık, tek küçük vurgu düğmesi
        for u in lv['u']:
            lx = (u - CX) / F * lv['depth']
            ly = lv['depth'] + 0.02
            steel_d.cyl((lx, ly + 0.02, -0.62), (lx, ly, -0.50), 0.0075, 8)
            for k_, (z0, z1, r_) in enumerate(((-0.575, -0.545, 0.030), (-0.545, -0.52, 0.024), (-0.52, -0.498, 0.019))):
                black_d.cyl((lx, ly, z0), (lx, ly, z1), r_, 10)      # körük halkaları
            steel_d.cyl((lx, ly, -0.498), (lx, ly, -0.490), 0.024, 10)      # bilezik
            black_d.cyl((lx, ly, -0.490), (lx, ly, -0.425), 0.0165, 9)      # kauçuk tutamak
            for z_ in lin(-0.480, -0.440, 5):
                steel_d.cyl((lx, ly, z_ - 0.0015), (lx, ly, z_ + 0.0015), 0.0172, 9)      # ribler
            black_d.cyl((lx, ly, -0.425), (lx, ly, -0.414), 0.0145, 9)
            pale_d.box((lx, ly - 0.0136, -0.4195), (0.012, 0.0014, 0.006))      # başlık etiketi
            rust_d.cyl((lx + 0.0105, ly - 0.0165, -0.455), (lx + 0.0105, ly - 0.0215, -0.455), 0.0055, 6)      # başparmak düğmesi (tek küçük vurgu)
        # güverte: derz şeritleri, turuncu plakalar, uyarı bandı
        for y_ in (0.80, 0.90, 0.99):
            black_d.box((0, y_, ez + 0.003), (2 * xw(y_) * 0.92, 0.007, 0.004))
        for sd in (-1, 1):
            for yy_ in (0.84, 0.97):
                rust_d.box((sd * 0.66, yy_, ez + 0.007), (0.26, 0.10, 0.012))
                for dx_, dy_ in ((-0.11, -0.04), (0.11, -0.04), (-0.11, 0.04), (0.11, 0.04)):
                    rivets.cyl((sd * 0.66 + dx_, yy_ + dy_, ez + 0.013), (sd * 0.66 + dx_, yy_ + dy_, ez + 0.0195), 0.0062, 6)
        for x_ in lin(-0.74, 0.74, 25):
            hazard_d.box((x_, 1.035, ez + 0.004), (0.022, 0.026, 0.008), skew=1.0)

        # ---- yan duvarlar (pilotun iki yanındaki eğik iç yüzler): renk blokları, uyarı bandı, derz, panel, ızgara, kablo kanalı
        def wl(sd):
            a2, b2 = Vector((*side_pt(sd, 0), 0)), Vector((*side_pt(sd, 1), 0))
            dd = (b2 - a2).normalized()
            nn = Vector((dd.y, -dd.x, 0))
            if nn.dot((a2 + b2) / 2) < 0:
                nn = -nn
            return a2, b2, dd, -nn, (b2 - a2).length

        def wbox(acc, sd, t, z, along, h, thick, off=0.0):
            a2, b2, dd, inw, L_ = wl(sd)
            pp = a2 + (b2 - a2) * t + inw * (off + thick / 2)
            acc.box((pp.x, pp.y, z), (along, thick, h), rot_z=math.atan2(dd.y, dd.x))
        for sd in (-1, 1):
            a2, b2, dd, inw, Lw = wl(sd)
            wbox(dark_d, sd, 0.5, -0.70, 0.94 * Lw, 0.34, 0.010)      # alt yarı koyu çelik
            wbox(black_d, sd, 0.5, zs - 0.075, 0.94 * Lw, 0.065, 0.008)      # uyarı bandı tabanı
            for k_ in range(int(0.94 * Lw / 0.07)):
                a_, b_, d_, in_, L_ = wl(sd)
                pp = a2 + (b2 - a2) * (0.03 + k_ * 0.07 / Lw) + inw * 0.0105
                hazard_d.box((pp.x, pp.y, zs - 0.075), (0.026, 0.013, 0.065), rot_z=math.atan2(dd.y, dd.x), skew=0.75)
            for z_ in (zs - 0.17, zs - 0.31, zs - 0.47):      # yatay derzler
                wbox(black_d, sd, 0.5, z_, 0.94 * Lw, 0.009, 0.006)
            for t_ in (0.2, 0.44, 0.68, 0.9):      # dikey derzler
                wbox(black_d, sd, t_, zs - 0.50, 0.009, 0.84, 0.006)
            for t_, z_ in ((0.32, zs - 0.24), (0.62, zs - 0.24)):      # yükseltilmiş turuncu paneller + perçin
                wbox(rust_d, sd, t_, z_, 0.20, 0.12, 0.014)
                for da_, dz_ in ((-0.08, -0.045), (0.08, -0.045), (-0.08, 0.045), (0.08, 0.045)):
                    a_, b_, d_, in_, L_ = wl(sd)
                    pp = a2 + (b2 - a2) * (t_ + da_ / Lw) + inw * 0.014
                    rivets.cyl((pp.x, pp.y, z_ + dz_), (pp.x + inw.x * 0.007, pp.y + inw.y * 0.007, z_ + dz_), 0.0062, 6)
            wbox(dark_d, sd, 0.80, zs - 0.26, 0.17, 0.15, 0.012)      # havalandırma ızgarası: çerçeve + ince dilimler
            for k_ in range(7):
                wbox(black_d, sd, 0.80, zs - 0.20 - k_ * 0.019, 0.14, 0.008, 0.017)
            for r_ in (-0.012, 0.012):      # kablo kanalı: iki kauçuk boru + çelik kelepçeler
                a_, b_, d_, in_, L_ = wl(sd)
                p0 = a2 + (b2 - a2) * 0.04 + inw * 0.03
                p1 = a2 + (b2 - a2) * 0.96 + inw * 0.03
                black_d.cyl((p0.x, p0.y, zs - 0.40 + r_), (p1.x, p1.y, zs - 0.40 + r_), 0.0105, 7)
            for t_ in (0.12, 0.35, 0.58, 0.81):
                wbox(steel_d, sd, t_, zs - 0.40, 0.022, 0.044, 0.030)
            for t_, pw_ in ((0.0, cb.get('post_corner_w', 0.0676)), (cb['side_post_t'], cb.get('post_side_w', 0.0772))):      # dikme tabanlarında sarı-siyah kelepçe bantları
                for z_, mt_ in ((zs + 0.012, hazard_d), (zs + 0.040, black_d), (zs + 0.068, hazard_d)):
                    wbox(mt_, sd, t_, z_, pw_ + 0.014, 0.020, 0.010)
        # orta dikme: kelepçe halkaları ve sarı bantlar
        for z_ in lin(zs + 0.06, zh - 0.06, 6):
            steel_d.box((0, fy - 0.0035, z_), (cb.get('post_w', 0.036) + 0.012, 0.007, 0.012))
        for z_ in (zs + 0.11, (zs + zh) / 2, zh - 0.11):
            hazard_d.box((0, fy - 0.0045, z_), (cb.get('post_w', 0.036) + 0.004, 0.009, 0.034))
        # başlık kirişi: boru hattı, kelepçeler, sarı-siyah alt flanş, etiket plakaları
        for z_ in (zh + 0.075, zh + 0.112):
            black_d.cyl((-0.70, fy - 0.026, z_), (0.70, fy - 0.026, z_), 0.0125, 8)
        for x_ in lin(-0.62, 0.62, 8):
            steel_d.box((x_, fy - 0.026, zh + 0.094), (0.026, 0.026, 0.066))
        for x_ in lin(-0.72, 0.72, 25):
            hazard_d.box((x_, fy - 0.0165, zh + 0.012), (0.017, 0.033, 0.026), skew=0.9)
        for x_ in (-0.50, 0.0, 0.50):
            pale_d.box((x_, fy - 0.008, zc - 0.05), (0.11, 0.006, 0.032))
            for dx_ in (-0.045, 0.045):
                rivets.cyl((x_ + dx_, fy - 0.014, zc - 0.05), (x_ + dx_, fy - 0.008, zc - 0.05), 0.0055, 6)

    # ---- koltuk (pilot görüşünde görünmez; çapraz ve plan görünüşleri için)
    st = A['seat']
    pz = st['pan_z']
    mk = (lambda c, sz: soft_box(c, sz, 0.035, 1)) if prod else (lambda c, sz: geo.bm_box(c, sz))      # PRODUCTION: dolgulu yumuşak minderler (Bevel + Subsurf)
    add('seat_pan', mk((0, -0.02, pz), (0.58, 0.52, 0.13)), 'seat_textile')
    back = mk((0, -0.31, pz + 0.42), (0.56, 0.12, 0.80))
    bmesh.ops.rotate(back.bm if isinstance(back, Soft) else back, cent=Vector((0, -0.31, pz + 0.02)), matrix=Matrix.Rotation(math.radians(-st['recline_deg']), 3, 'X'), verts=(back.bm if isinstance(back, Soft) else back).verts)
    add('seat_back', back, 'seat_textile')
    for s in (-1, 1):
        add('seat_arm_%s' % ('L' if s < 0 else 'R'), mk((s * 0.34, -0.05, pz + 0.17), (0.09, 0.46, 0.08)), 'yuk_dark')
    if prod:      # kemer şeritleri ve tokalar
        for s in (-1, 1):
            strap = geo.bm_box((s * 0.15, -0.35, pz + 0.55), (0.05, 0.012, 0.62))
            bmesh.ops.rotate(strap, cent=Vector((0, -0.31, pz + 0.02)), matrix=Matrix.Rotation(math.radians(-st['recline_deg']), 3, 'X'), verts=strap.verts)
            add('seat_strap_%s' % ('L' if s < 0 else 'R'), strap, 'yuk_black')
        add('seat_buckle', geo.bm_box((0, -0.27, pz + 0.22), (0.07, 0.02, 0.05)), 'gunmetal')
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
        ob = add(name, bm, mat, smooth=smooth, role='art')      # eklemli: prepare birleştirmez, eklem başına ayırır (STANDARDS §0.3)
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


    if prod:      # kıskaç ayrıntısı: hidrolik silindirler, kelepçeler, civata başları, çene dişleri (hepsi ilgili eklemin çocuğu)
        for sx in (-1, 1):
            off = xa * sx * (gap * 0.5 + 0.075)
            a0, a1 = shoulder + d * 0.03 + off, elbow - d * 0.06 + off
            part('claw_piston_barrel_%d' % sx, geo.bm_cylinder(a0, a0 + (a1 - a0) * 0.62, 0.024, 12), 'yuk_dark', 'ART_claw_shoulder')
            part('claw_piston_rod_%d' % sx, geo.bm_cylinder(a0 + (a1 - a0) * 0.62, a1, 0.011, 8), 'gunmetal', 'ART_claw_elbow')
            part('claw_clamp_%d' % sx, geo.bm_cylinder(a0 + (a1 - a0) * 0.30 - d * 0.012, a0 + (a1 - a0) * 0.30 + d * 0.012, 0.031, 12), 'gunmetal', 'ART_claw_shoulder')
            part('claw_pin_head_%d' % sx, geo.bm_cylinder(elbow + xa * sx * 0.09, elbow + xa * sx * 0.108, 0.03, 8), 'gunmetal', 'ART_claw_elbow')
        part('claw_shoulder_collar', geo.bm_cylinder(shoulder - xa * 0.11, shoulder + xa * 0.11, 0.05, 14), 'gunmetal', 'ART_claw_shoulder')
        for k in range(6):
            ang = k * math.pi / 3
            bp = wrist + d * 0.09 + (xa * math.cos(ang) + nrm * math.sin(ang)) * 0.056
            part('claw_hub_bolt_%d' % k, geo.bm_cylinder(bp, bp + d * 0.012, 0.0085, 6), 'gunmetal', 'ART_claw_wrist')
        for dx_ in (-0.07, 0.07):
            for dd_ in (-0.045, 0.045):
                bp = root + Vector((dx_, dd_, 0.085))
                part('claw_mount_bolt_%d_%d' % (dx_ * 100, dd_ * 100), geo.bm_cylinder(bp, bp + Vector((0, 0, 0.012)), 0.011, 6), 'gunmetal', 'ART_claw_root')
        for jn, sx in (('L', -1), ('R', 1)):      # çene dişleri: ucun son bölümünde üç diş
            pts_ = [c + R * (-math.cos(math.radians(a)) * d + math.sin(math.radians(a)) * sx * xa) for a in lin(12, 158, 16)]
            for k, i_ in enumerate((11, 12, 13)):
                part('claw_tooth_%s_%d' % (jn, k), geo.bm_box(tuple(pts_[i_] - xa * sx * 0.026), (0.022, 0.03, 0.022)), 'gunmetal', 'ART_claw_jaw_' + jn, smooth=35)

    if prod:      # toplu ayrıntı grupları: malzeme başına tek nesne
        for nm, acc, mt, role in (('detail_rivets', rivets, 'yuk_steel', 'body'), ('detail_plates', dark_d, 'yuk_dark', 'body'), ('detail_black', black_d, 'yuk_black', 'body'),
                                  ('detail_rust', rust_d, 'yuk_rust', 'body'), ('detail_hazard', hazard_d, 'yuk_hazard', 'body'), ('detail_pale', pale_d, 'yuk_pale', 'body'),
                                  ('detail_steel', steel_d, 'yuk_steel', 'body'), ('detail_lamps', lamps_d, 'emit_amber', 'emit_live')):
            if not acc.empty():
                add(nm, acc.bm, mt, role=role, smooth=60)

    socks = [{'name': 'SOCK_cam_0', 'loc': (0, 0, 0), 'dir': (0, 1, 0), 'extras': {'purpose': 'pilot gözü (kamera sözleşmesi)', 'fovy': 74}},
             {'name': 'SOCK_claw_grip', 'loc': tuple(c + Vector((0, R, 0))), 'dir': (0, 1, 0), 'extras': {'purpose': 'kıskaç kavrama noktası', 'parent': 'ART_claw_wrist'}}]
    return {'objects': obs, 'sockets': socks}
