"""Hayalet kokpiti — karbon-siyah, tek mor neon, ince X/V A-direkleri (ortada dikme yok), açılı kama konsol, kapitone deri koltuk.
Kamera/ekran sözleşmesi build.py ile aynıdır (P, face_eye, ekran dörtgeni UV sırası). Referans: assets/img/ck_hayalet.webp (konsept: docs/hayalet_konsept.html).
Statik (ART/SOCK yok). Şahin ve Yük tariflerine dokunmaz."""
import bpy, bmesh, math
from mathutils import Vector
from core import geo
from families.cockpit.build import P, face_eye, grid, tube, lin, F, CX, CY, W, H, Soft, soft_box
from families.cockpit.yuk_b import Acc


def build(spec, mats):
    A = spec['params']
    obs = []
    prod = spec.get('profile') == 'PRODUCTION'
    dark_d, mid_d, lamps_d, thread_d, rivets = Acc(), Acc(), Acc(), Acc(), Acc()

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
            if sft.level > 0:
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

    cn = A['console']
    fd = lambda v: cn['d0'] - cn['slope'] * (v - cn['v0'])      # konsol yüzü derinliği (aşağı indikçe pilota yaklaşır)
    ct = cn['top']      # konsol üst kenarı: (u, v) kırık çizgi, soldan sağa

    def vtop(u):
        for (ua, va), (ub, vb) in zip(ct[:-1], ct[1:]):
            if ua <= u <= ub:
                return va + (vb - va) * (u - ua) / (ub - ua)
        return ct[0][1] if u < ct[0][0] else ct[-1][1]

    # ---- konsol: kama yüz (üst kenardan aşağı), güverte yanlar
    U = lin(0, W, 41)
    add('fascia', grid([[P(u, vtop(u) + k * (700 - vtop(u)) / 7, fd(vtop(u) + k * (700 - vtop(u)) / 7)) for u in U] for k in range(8)]), 'hay_carbon', eye=True, solid=0.03)
    # üst kenar şeridi (ince profil) + neon çizgisi
    add('top_trim', tube([P(u, vtop(u) - 2, fd(vtop(u)) - 0.004) for u in lin(300, W - 300, 33)], 0.006, 8), 'hay_mid', smooth=60)
    for sd in (-1, 1):      # yan güverte: ekranların dışında geniş, hafif eğimli, dokulu yüzey
        uu = (lambda u: u) if sd < 0 else (lambda u: W - u)
        add('deck_%s' % ('L' if sd < 0 else 'R'), grid([[P(uu(u), v, fd(v) + 0.02 + 0.00025 * (330 - u)) for u in lin(0, 330, 12)] for v in lin(520, 700, 6)]), 'hay_dark', eye=True, solid=0.03)

    # ---- ekranlar (sözleşme: tek dörtgen, UV sol-üst (0,0); köşeler referanstan türetilmiş)
    sc = A['screens']

    def screen(name, q, bezel_px, lbl):
        depths = [fd(v) - 0.015 for u, v in q]
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
            outer.append(((u + du / l * bezel_px * 1.25, v + dv / l * bezel_px * 1.25), d))
        rin = [P(u, v, d + 0.002) for (u, v), d in zip(q, depths)]
        rout = [P(u, v, d + 0.002) for (u, v), d in outer]
        bm2 = bmesh.new()
        vi = [bm2.verts.new(p) for p in rin]
        vo = [bm2.verts.new(p) for p in rout]
        for k in range(4):
            bm2.faces.new((vo[k], vo[(k + 1) % 4], vi[(k + 1) % 4], vi[k]))
        add('bezel_' + lbl, bm2, 'hay_dark', eye=True, solid=0.012, toward_eye=True)
        # neon köşe parantezleri (L biçimli) iç çerçeve köşelerinde: sol-alt ve sağ-alt, sol-üst
        for ci in (0, 3, 2):
            pa, pb, pc = rin[ci], rin[(ci + 1) % 4], rin[(ci - 1) % 4]
            for pn in (pb, pc):
                dpt = (pn - pa).normalized() * 0.05
                lamps_d.box(tuple((pa + dpt / 2 - pa.normalized() * 0.004)), (0.004, 0.004, 0.004)) if False else None
            for pn in (pb, pc):
                seg = [pa + (pn - pa).normalized() * t - pa.normalized() * 0.004 for t in (0.0, 0.04)]
                lamps_d.cyl(seg[0], seg[1], 0.0030, 5)
        # kasa: çerçevenin arkasında kutu
        bm3 = bmesh.new()
        fr = [bm3.verts.new(p) for p in rout]
        bk = [bm3.verts.new(p + p.normalized() * 0.05) for p in rout]
        bm3.faces.new(bk)
        for k in range(4):
            bm3.faces.new((fr[k], fr[(k + 1) % 4], bk[(k + 1) % 4], bk[k]))
        add('housing_' + lbl, bm3, 'hay_dark', eye=True)

    screen('SCR_RADAR', sc['radar'], 9, 'radar')
    screen('SCR_SYS', sc['sys'], 11, 'sys')
    screen('SCR_HULL', sc['hull'], 11, 'hull')
    # ekranlar arası dikey bölme panelleri + orta kama sırt (radar üstü)
    for k, (ua, ub) in enumerate(((606, 622), (978, 994))):
        add('divider_%d' % k, grid([[P(u, v, fd(v) - 0.012) for u in lin(ua, ub, 3)] for v in lin(vtop(ua) + 6, 520, 5)]), 'hay_mid', eye=True, solid=0.014, toward_eye=True)
    add('radar_cap', grid([[P(u, v, fd(v) - 0.02) for u in lin(620, 980, 10)] for v in lin(vtop(800) - 6, vtop(800) + 3, 3)]), 'hay_carbon', eye=True, solid=0.02, toward_eye=True)

    # ---- konsol ortası: V amblemi + iki havalandırma (radar altı bandı)
    vb = cn['emblem_v']
    for sg in (-1, 1):
        lamps_d.box(tuple(P(800 + sg * 12, vb, fd(vb) - 0.010)), (0.006, 0.004, 0.034), rot_z=0.0, skew=sg * 0.45)
    for sg in (-1, 1):
        cxu = 800 + sg * 96
        add('vent_frame_%d' % sg, grid([[P(u, v, fd(v) - 0.012) for u in lin(cxu - 34, cxu + 34, 4)] for v in lin(vb - 14, vb + 14, 3)]), 'hay_mid', eye=True, solid=0.008, toward_eye=True)
        for i_ in range(5):
            dark_d.box(tuple(P(cxu, vb - 10 + i_ * 5, fd(vb) - 0.016)), (0.075, 0.003, 0.003))

    # ---- kanopi çerçevesi: başlık kirişi, iki çapraz A-direği (aşağıya yakınsayan V), dış kemerler, tavan neon çentiği
    dC = A['canopy']['depth']
    rP = A['canopy']['pillar_r']
    hdr = [P(u, 20 + 8 * math.sin((u - 330) / 940 * math.pi) * -1 + 0, dC) for u in lin(330, 1270, 21)]
    add('header_beam', tube(hdr, 0.028, 8), 'hay_carbon', smooth=60)
    for sd in (-1, 1):
        uu = (lambda u: u) if sd < 0 else (lambda u: W - u)
        nm = 'L' if sd < 0 else 'R'
        # A-direği: tavan ortasına doğru geniş, konsol omzuna iner
        pil = [P(uu(385 + (565 - 385) * t), 40 + (335 - 40) * t, dC - 0.25 * t) for t in lin(0, 1, 12)]
        add('pillar_' + nm, tube(pil, rP, 8), 'hay_carbon', smooth=60)
        # iç kenar neonu: direğin iç yüzüne ince çizgi
        neon = [P(uu(395 + (553 - 395) * t), 70 + (300 - 70) * t, dC - 0.25 * t - rP * 0.9) for t in lin(0.0, 1, 8)]
        lamps_d.cyl(neon[1], neon[-2], 0.0035, 5)
        # dış kemer (yan pencere çerçevesi)
        arc = [P(uu(u), v, dC + 0.05) for u, v in ((330, 18), (225, 60), (120, 150), (45, 255), (2, 350))]
        add('arc_' + nm, tube(arc, 0.034, 8), 'hay_carbon', smooth=60)
        lamps_d.cyl(P(uu(300), 26, dC - 0.02), P(uu(250), 44, dC - 0.02), 0.0045, 5)
        lamps_d.cyl(P(uu(60), 230, dC + 0.01), P(uu(18), 320, dC + 0.01), 0.0045, 5)
        # yan güverte kenarı: konsol omzundan yan kenara inen profil + neon çizgi
        rim = [P(uu(u), v, fd(v) - 0.01) for u, v in ((330, 408), (200, 468), (90, 520), (0, 570))]
        add('deck_rim_' + nm, tube(rim, 0.012, 8), 'hay_mid', smooth=60)
        lamps_d.cyl(P(uu(250), 600, fd(600) - 0.012), P(uu(110), 640, fd(640) - 0.012), 0.0042, 5)
    lamps_d.box(tuple(P(800, 36, dC - 0.03)), (0.07, 0.01, 0.012))      # tavan ortası neon çentik
    lamps_d.box(tuple(P(800, 52, dC - 0.03)), (0.034, 0.01, 0.008))

    # ---- koltuk: kapitone siyah deri (Kaşif ayak izi); radar alt kenarı yüksek → geniş görünür alan
    sy = 0.555
    ztop = A['seat']['top_z']
    hr = soft_box((0, sy, ztop - 0.135), (0.34, 0.10, 0.27), 0.028, 1)
    add('seat_headrest_v', hr, 'hay_leather', smooth=60)
    for s_ in (-1, 1):
        nm = 'L' if s_ < 0 else 'R'
        add('seat_wing_v_' + nm, soft_box((s_ * 0.235, sy - 0.012, ztop - 0.215), (0.10, 0.11, 0.26), 0.024, 1), 'hay_leather', smooth=60)
        thread_d.box((s_ * 0.235, sy - 0.0645, ztop - 0.22), (0.003, 0.003, 0.17))
    fyy = sy - 0.0535
    thread_d.box((0, fyy, ztop - 0.11), (0.30, 0.003, 0.003))
    for dx_ in (-0.085, 0.085):
        thread_d.box((dx_, fyy, ztop - 0.19), (0.003, 0.003, 0.15))

    # ---- toplu ayrıntı grupları
    for nm, acc, mt, role in (('detail_dark', dark_d, 'hay_dark', 'body'), ('detail_mid', mid_d, 'hay_mid', 'body'), ('detail_neon', lamps_d, 'emit_violet', 'emit_live'),
                              ('detail_thread', thread_d, 'hay_thread', 'body'), ('detail_rivets', rivets, 'hay_mid', 'body')):
        if not acc.empty():
            add(nm, acc.bm, mt, role=role, smooth=60)

    socks = [{'name': 'SOCK_cam_0', 'loc': (0, 0, 0), 'dir': (0, 1, 0), 'extras': {'purpose': 'pilot gözü (kamera sözleşmesi)', 'fovy': 74}}]
    return {'objects': obs, 'sockets': socks}
