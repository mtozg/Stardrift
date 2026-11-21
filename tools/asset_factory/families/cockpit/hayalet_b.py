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
    dark_d, mid_d, lamps_d, thread_d, rivets, carb_d, hexes = Acc(), Acc(), Acc(), Acc(), Acc(), Acc(), Acc()

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

    def nquad(rows, front=0.0):
        """neon şeridi: rows = [(sol, sağ), ...] 3B noktalar (komşu yüzeyin kenarından türetilmiş); yüzün önüne `front` m; normal göze bakar."""
        bm_ = lamps_d.bm
        vs = [[bm_.verts.new(a - a.normalized() * front), bm_.verts.new(b - b.normalized() * front)] for a, b in rows]
        for r0, r1 in zip(vs[:-1], vs[1:]):
            f = bm_.faces.new((r0[0], r0[1], r1[1], r1[0]))
            f.normal_update()
            if f.normal.dot(f.calc_center_median()) > 0:
                f.normal_flip()

    def npoly(pts, hwf, df, off=0.0, wpx=3.0, front=0.003, i0=0, i1=None):
        """komşu şeridin (ribbon) kenar eğrisini izleyen neon: aynı nokta dizisi, kenara göre `off` oranında ofset (merkeze bakan yan), genişlik wpx; uçlar şeridin uçlarıyla çakışır."""
        n_ = len(pts)
        rows = []
        for i in range(i0, (n_ if i1 is None else i1)):
            u, v = pts[i]
            u2, v2 = pts[min(i + 1, n_ - 1)]
            u0, v0 = pts[max(i - 1, 0)]
            tx, ty = u2 - u0, v2 - v0
            l = math.hypot(tx, ty) or 1.0
            nx, ny = -ty / l, tx / l
            t = i / (n_ - 1)
            hw = hwf(t) if callable(hwf) else hwf
            if abs(u + nx - 800) > abs(u - nx - 800):
                nx, ny = -nx, -ny
            c = hw * off
            d = df(t) if callable(df) else df
            rows.append((P(u + nx * (c - wpx / 2), v + ny * (c - wpx / 2), d), P(u + nx * (c + wpx / 2), v + ny * (c + wpx / 2), d)))
        nquad(rows, front)
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
        for ci in (() if A.get('neon2') else (0, 3, 2)):
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

    def raised_frame(q, bz, lbl, h=0.04):
        h = 0.055 if A.get('r004') else h
        """r003: kabartma çerçeveli ekran yuvası: dış pah (konsol yüzünden öne), üst yüz, iç duvar (ekran düzlemine) → gerçek oyuk/derinlik."""
        cu = sum(u for u, v in q) / 4
        cv = sum(v for u, v in q) / 4

        def ring(exp, off):
            out = []
            for (u, v) in q:
                du, dv = u - cu, v - cv
                l = math.hypot(du, dv)
                out.append(P(u + du / l * exp, v + dv / l * exp, fd(v) - off))
            return out
        A_ = ring(bz * 2.3, 0.0)         # dış (konsol yüzünde)
        B_ = ring(bz * 1.7, h)           # dış ön kenar (pahın üstü)
        C_ = ring(bz * 0.45, h)          # iç ön kenar
        D_ = ring(0.0, 0.016)            # ekran düzlemi
        bm = bmesh.new()
        rs = [[bm.verts.new(p) for p in r_] for r_ in (A_, B_, C_, D_)]
        for r0, r1 in ((0, 1), (1, 2), (2, 3)):
            for k in range(4):
                bm.faces.new((rs[r0][k], rs[r0][(k + 1) % 4], rs[r1][(k + 1) % 4], rs[r1][k]))
        add('frame3_' + lbl, bm, 'hay_carbon', eye=True)
        if A.get('neon2') and lbl != 'radar':      # alt kenar neonu (radarda koltuk başlığı örter → yok): ön yüz şeridinin (B→C) ortasında, köşeden köşeye (uçlar kenar uçlarıyla çakışır)
            lerp = lambda a, b, t: a + (b - a) * t
            nquad([(lerp(B_[3], C_[3], 0.40), lerp(B_[3], C_[3], 0.62)), (lerp(B_[2], C_[2], 0.40), lerp(B_[2], C_[2], 0.62))], 0.0015)
        elif not A.get('neon2'):
            for k in range(4):      # ön kenarda ince mor çizgi yalnız alt kenar (tek neon, az)
                if k == 2:
                    lamps_d.cyl(C_[2] * 1.0 - C_[2].normalized() * 0.002, C_[3] * 1.0 - C_[3].normalized() * 0.002, 0.0028, 5)
    if A.get('r003'):
        for q_, bz_, l_ in ((sc['radar'], 9, 'radar'), (sc['sys'], 11, 'sys'), (sc['hull'], 11, 'hull')):
            raised_frame(q_, bz_, l_)
    # ekranlar arası dikey bölme panelleri + orta kama sırt (radar üstü)
    for k, (ua, ub) in enumerate(A.get('dividers', ((606, 622), (978, 994)))):
        add('divider_%d' % k, grid([[P(u, v, fd(v) - 0.012) for u in lin(ua, ub, 3)] for v in lin(vtop(ua) + 6, 520, 5)]), 'hay_mid', eye=True, solid=0.014, toward_eye=True)
    add('radar_cap', grid([[P(u, v, fd(v) - 0.02) for u in lin(620, 980, 10)] for v in lin(vtop(800) - 6, vtop(800) + 3, 3)]), 'hay_carbon', eye=True, solid=0.02, toward_eye=True)

    # ---- konsol ortası: V amblemi + iki havalandırma (radar altı bandı)
    vb = cn['emblem_v']
    for sg in ([] if A.get('neon2') else (-1, 1)):      # neon2: bu V koltuğun arkasında kalıyordu (gizli); radar kepindeki V kullanılır
        lamps_d.box(tuple(P(800 + sg * 12, vb, fd(vb) - 0.010)), (0.006, 0.004, 0.034), rot_z=0.0, skew=sg * 0.45)
    for sg in (-1, 1):
        cxu = 800 + sg * 96
        add('vent_frame_%d' % sg, grid([[P(u, v, fd(v) - 0.012) for u in lin(cxu - 34, cxu + 34, 4)] for v in lin(vb - 14, vb + 14, 3)]), 'hay_mid', eye=True, solid=0.008, toward_eye=True)
        for i_ in range(5):
            dark_d.box(tuple(P(cxu, vb - 10 + i_ * 5, fd(vb) - 0.016)), (0.075, 0.003, 0.003))

    # ---- kanopi çerçevesi: ince kanat profilli başlık kirişi, iki çapraz A-direği (aşağıya yakınsayan V), dış kemerler, tavan neon çentiği
    dC = A['canopy']['depth']

    def ribbon(pts, hw, depth, name, solid=0.018, dfun=None):
        """Piksel uzayında bir çizgi boyunca şerit (kanat profili): her noktada teğete dik ±hw px; solidify ile ince kalınlık."""
        rows = []
        for i, (u, v) in enumerate(pts):
            u2, v2 = pts[min(i + 1, len(pts) - 1)]
            u0, v0 = pts[max(i - 1, 0)]
            tx, ty = u2 - u0, v2 - v0
            l = math.hypot(tx, ty) or 1.0
            nx, ny = -ty / l, tx / l
            w = hw(i / (len(pts) - 1)) if callable(hw) else hw
            d = depth(i / (len(pts) - 1)) if callable(depth) else depth
            rows.append([P(u - nx * w, v - ny * w, d), P(u + nx * w, v + ny * w, d)])
        return add(name, grid(rows), 'hay_carbon', eye=True, solid=solid)

    hdr = [(u, 18 + 6 * math.sin((u - 330) / 940 * math.pi) * -1) for u in lin(330, 1270, 24)]
    ribbon(hdr, 13, dC, 'header_beam', 0.024)
    for u_, hw_ in ((800, 18),):
        zz_ = 0.0075 if A.get('neon2') else 0.03      # neon2: kirişin ön yüzüne oturur
        lamps_d.box(tuple(P(u_, 36, dC - zz_)), (0.07, 0.01, 0.012))      # tavan ortası neon çentik
        lamps_d.box(tuple(P(u_, 50, dC - zz_)), (0.034, 0.01, 0.008))
    for sd in (-1, 1):
        uu = (lambda u: u) if sd < 0 else (lambda u: W - u)
        nm = 'L' if sd < 0 else 'R'
        pil = [(uu(385 + (A['canopy'].get('pil_dx', 180)) * t), 40 + 295 * t) for t in lin(0, 1.13, 13)]
        ribbon(pil, lambda t: 11 + 8 * t, lambda t: dC - 0.25 * t * 1.13, 'pillar_' + nm, 0.022)
        # iç kenar neonu (dar ışık çizgisi, kanat yüzünde)
        if A.get('neon2'):      # direk iç kenarında, kanat yüzüne oturan şerit: aynı nokta dizisi, uçtan uca
            npoly(pil, lambda t: 11 + 8 * t, lambda t: dC - 0.25 * t * 1.13, off=0.62, wpx=3.0, front=0.003)
        else:
            seg = [P(uu(395 + 158 * t + (11 + 8 * t) - 4), 70 + 230 * t, dC - 0.25 * t - 0.014) for t in lin(0.0, 1, 8)]
            lamps_d.cyl(seg[1], seg[-2], 0.0035, 5)
        # dış kemer (yan pencere çerçevesi)
        arc = [(uu(u), v) for u, v in ((330, 18), (270, 38), (225, 60), (170, 100), (120, 150), (80, 200), (45, 255), (20, 305), (2, 350))]
        ribbon(arc, 10, dC + 0.05, 'arc_' + nm, 0.045 if A.get('r003') else 0.02)
        if A.get('r003'):      # oluklu kemer/direk: yan yüzde koyu oluk (gölge çizgisi)
            if not A.get('neon2'):
                ribbon(arc, 2.5, dC + 0.05 - 0.03, 'arc_groove_' + nm, 0.006)
            ribbon(pil, 2.5, lambda t: dC - 0.25 * t * 1.13 - 0.02, 'pillar_groove_' + nm, 0.006)
        if A.get('neon2'):      # kemerin eğrisini izleyen şeritler (merkez hat, kemer ön yüzünde)
            npoly(arc, 10, dC + 0.05, off=0.55, wpx=3.4, front=0.003, i0=0, i1=4)
            npoly(arc, 10, dC + 0.05, off=0.55, wpx=3.4, front=0.003, i0=5, i1=9)
        else:
            lamps_d.cyl(P(uu(300), 26, dC - 0.015), P(uu(250), 44, dC - 0.015), 0.0045, 5)
            lamps_d.cyl(P(uu(60), 230, dC + 0.02), P(uu(18), 320, dC + 0.02), 0.0045, 5)
        # yan güverte kenarı: konsol omzundan yan kenara inen profil + neon çizgi
        rim = [(uu(u), v) for u, v in (((270, 436), (190, 476), (90, 524), (0, 570)) if A.get('r003') else ((330, 408), (200, 468), (90, 520), (0, 570)))]
        ribbon(rim, 6, lambda t: fd(480) - 0.012, 'deck_rim_' + nm, 0.014)
        if not A.get('neon2'):
            lamps_d.cyl(P(uu(250), 600, fd(600) - 0.012), P(uu(110), 640, fd(640) - 0.012), 0.0042, 5)

    # ---- konsol ayrıntısı: sakin yüzeyler (derz, kabartma plaka, ızgara, bulon, V amblemi) + altıgen güverte
    def onF(u, v, off=0.0):
        return P(u, v, fd(v) - off)

    def plate(u0, v0, u1, v1, acc, off=0.006, depth=0.008):
        if A.get('r004'):      # r004: ölçü tek derinlikte hesaplanır (yüz eğimli; iki farklı derinlikteki köşelerden boyut çıkarmak uzun plakaları şişiriyordu)
            vm = (v0 + v1) / 2
            pc = onF((u0 + u1) / 2, vm, off)
            dm = fd(vm)
            acc.box((pc.x, pc.y, pc.z), (abs(u1 - u0) / F * dm, depth, abs(v1 - v0) / F * dm))
            return
        pa, pb = onF(u0, v0), onF(u1, v1)
        acc.box(((pa.x + pb.x) / 2, pa.y - off, (pa.z + pb.z) / 2), (abs(pb.x - pa.x), depth, abs(pa.z - pb.z)))

    def frame(u0, v0, u1, v1, acc, th=2, off=0.0075, depth=0.006):
        plate(u0, v0, u1, v0 + th, acc, off, depth); plate(u0, v1 - th, u1, v1, acc, off, depth)
        plate(u0, v0, u0 + th, v1, acc, off, depth); plate(u1 - th, v0, u1, v1, acc, off, depth)

    def bolts(pts, off=0.0095):
        for (u, v) in pts:
            pp = onF(u, v, off)
            rivets.cyl((pp.x, pp.y, pp.z), (pp.x, pp.y - 0.004, pp.z), 0.0042, 6)

    for sd in (-1, 1):
        uu = (lambda u: u) if sd < 0 else (lambda u: W - u)
        # ekran altı kabartma plaka + çerçeve + bulonlar + kablo kanalı
        ua, ub = sorted((uu(345), uu(560)))
        plate(ua, 546, ub, 612, carb_d, 0.0065, 0.009)
        frame(ua, 546, ub, 612, mid_d, 2)
        bolts([(ua + 8, 554), (ub - 8, 554), (ua + 8, 604), (ub - 8, 604)])
        plate(min(uu(372), uu(532)), 576, max(uu(372), uu(532)), 578, dark_d, 0.009, 0.004)      # derz
        duct = [P(uu(u), 628 + 2 * math.sin(u / 40.0), fd(628) - 0.012) for u in lin(330, 560, 10)]
        d_ = tube(duct, 0.0055, 8)
        add('duct_' + ('L' if sd < 0 else 'R'), d_, 'hay_dark', smooth=60)
        # omuzda havalandırma ızgarası (referanstaki yan ızgara): çerçeve + ince dilimler
        if not A.get('r004'):      # r004: ızgara omuz bloğuna (ekran dışı) taşındı; bu konum ekran sol kenarına bindiği için kaldırıldı
            gu0, gu1 = sorted((uu(268), uu(328)))
            plate(gu0, 470, gu1, 536, mid_d, 0.0065, 0.008)
            for k_ in range(9):
                v_ = 478 + k_ * 6.6
                plate(gu0 + 4, v_, gu1 - 4, v_ + 2.4, dark_d, 0.0105, 0.004)
        # ekranlar arası dikey derzler
    for u_ in (300, 600, 1000, 1300):
        plate(u_ - 1, 510, u_ + 1, 656, dark_d, 0.0085, 0.004)
    # V amblemi radar kepi üstünde (küçük, mor)
    vv = vtop(800) - 1.5
    for sg in (-1, 1):
        lamps_d.box(tuple(onF(800 + sg * 7, vv, 0.0385 if A.get('neon2') else 0.014)), (0.004, 0.004, 0.020), skew=sg * 0.5)
    # altıgen güverte: bal peteği (altıgen prizma)
    for sd in (-1, 1):
        uu = (lambda u: u) if sd < 0 else (lambda u: W - u)
        r_ = 0
        for v_ in lin(566, 696, 13):
            for k_, u_ in enumerate(lin(8, 300, 23)):
                uo = u_ + (6.5 if r_ % 2 else 0.0)
                dd_ = fd(v_) - 0.004      # r001-düzeltme: güverte yüzü konsol yüzünün ARKASINDA kalıp altıgenleri gizliyordu
                p0 = P(uu(uo), v_, dd_)
                if A.get('r002'):      # r002: koyu ve alçak altıgen (parlak petek yok)
                    hexes.cyl(p0 + p0.normalized() * 0.001, P(uu(uo), v_, dd_ - (0.0011 if A.get('seam_min') else 0.0018)), 0.0072, 6)
                else:
                    hexes.cyl(p0 + p0.normalized() * 0.001, P(uu(uo), v_, dd_ - 0.0035), 0.0082, 6)
            r_ += 1

    if A.get('r003'):      # r003: kademeli konsol yüzü (ekran bandı → orta basamak → alt şerit), yan panel kasaları, oluklu kemerler
        tier_box = {}

        def tier(u0, v0, u1, v1, off, th, name, acc=None, mat='hay_carbon'):
            if A.get('r004'):      # r004: boyut tek (orta) derinlikte (iki derinlikten hesap bloğu şişirip ekrana bindiriyordu)
                vm = (v0 + v1) / 2
                pc = onF((u0 + u1) / 2, vm, off)
                dm = fd(vm)
                tier_box[name] = ((pc.x, pc.y, pc.z), (abs(u1 - u0) / F * dm, th, abs(v1 - v0) / F * dm))
                add(name, soft_box((pc.x, pc.y, pc.z), (abs(u1 - u0) / F * dm, th, abs(v1 - v0) / F * dm), 0.006, 0), mat, smooth=60)
                return
            pa, pb = onF(u0, v0), onF(u1, v1)
            c = ((pa.x + pb.x) / 2, pa.y - off, (pa.z + pb.z) / 2)
            add(name, soft_box(c, (abs(pb.x - pa.x), th, abs(pa.z - pb.z)), 0.006, 0), mat, smooth=60)
        for sd in (-1, 1):
            uu = (lambda a_, b_: (a_, b_)) if sd < 0 else (lambda a_, b_: (W - b_, W - a_))
            nm = 'L' if sd < 0 else 'R'
            ua, ub = uu(235, 562); tier(ua, 566, ub, 614, 0.026, 0.05, 'tierB_' + nm)
            ua, ub = uu(190, 540); tier(ua, 618, ub, 662, 0.052, 0.07, 'tierC_' + nm)
            # orta basamak: havalandırma ızgarası + kablo kanalı + bulonlar
            ga, gb = uu(300, 470)
            for k_ in range(7):
                v_ = 574 + k_ * 5.6
                plate(ga, v_, gb, v_ + 2.2, dark_d, 0.0555, 0.004)
            duct = [P(uu(250, 540)[0] + (uu(250, 540)[1] - uu(250, 540)[0]) * t, 620 + 3 * math.sin(t * 7), fd(620) - 0.062) for t in lin(0, 1, 14)]
            add('duct3_' + nm, tube(duct, 0.0065, 8), 'hay_dark', smooth=60)
            bolts([(uu(250, 530)[0], 640), (uu(250, 530)[1], 640), (uu(250, 530)[0], 576), (uu(250, 530)[1], 576)], 0.0545)
            ea, eb = uu(560, 566)      # tier kenarında ince mor çizgi
            if A.get('neon2'):      # neon2: kademe neonu yok (katmanlı paneller örtüyordu; kontrol: qc/neon_check.py)
                pass
            else:
                lamps_d.cyl(P(uu(235, 540)[0], 614, fd(614) - 0.0535), P(uu(235, 540)[1], 614, fd(614) - 0.0535), 0.003, 5)
        # üst gövde: ekran bandının üstünde omuz kalınlığı (yan panel kasası): ekran kasalarının dışında basamaklı omuz bloğu
        for sd in (-1, 1):
            uu = (lambda a_, b_: (a_, b_)) if sd < 0 else (lambda a_, b_: (W - b_, W - a_))
            nm = 'L' if sd < 0 else 'R'
            ua, ub = uu(185, 272); tier(ua, 436, ub, 556, 0.022, 0.04, 'shoulder_' + nm)      # ekran sol kenarına (u≈290) binmez: ekran içeriği örtülmesin
            for k_ in range(8):
                v_ = 450 + k_ * 12
                plate(ua + 8, v_, ub - 8, v_ + 3.5, dark_d, 0.052, 0.004)

    if A.get('r004'):      # r004: Kaşif düzeyinde katmanlı yüzey: üst üste paneller, kasa kalınlığı, oluk, bağlantı parçaları
        def layered(u0, v0, u1, v1, off, nm):
            """üç kat: taban plaka (carb) + orta çerçeveli plaka (dark) + küçük üst plaka (mid) + bulonlar"""
            plate(u0, v0, u1, v1, carb_d, off, 0.010)
            plate(u0 + 8, v0 + 5, u1 - 8, v1 - 5, dark_d, off + 0.006, 0.008)
            frame(u0 + 8, v0 + 5, u1 - 8, v1 - 5, mid_d, 2, off + 0.011, 0.005)
            plate((u0 + u1) / 2 - 24, v0 + 12, (u0 + u1) / 2 + 24, v1 - 12, mid_d, off + 0.014, 0.006)
            bolts([(u0 + 12, v0 + 9), (u1 - 12, v0 + 9), (u0 + 12, v1 - 9), (u1 - 12, v1 - 9)], off + 0.0175)

        for sd in (-1, 1):
            uu = (lambda a_, b_: (a_, b_)) if sd < 0 else (lambda a_, b_: (W - b_, W - a_))
            nm = 'L' if sd < 0 else 'R'
            for k_, (a_, b_) in enumerate(((250, 330), (345, 425), (440, 545))):      # orta basamakta üç katmanlı panel
                ua, ub = uu(a_, b_); layered(ua, 570, ub, 610, 0.0535, 'lay_b%d' % k_)
            for k_, (a_, b_) in enumerate(((200, 300), (312, 430), (442, 535))):      # alt şeritte panel + bağlantı kutusu
                ua, ub = uu(a_, b_); layered(ua, 626, ub, 656, 0.0775, 'lay_c%d' % k_)
            # ekran altında menteşe/braket sırası (bağlantı parçaları)
            q_ = sc['sys'] if sd < 0 else sc['hull']
            for t_ in (0.1, 0.3, 0.5, 0.7, 0.9):
                ub_, vb_ = q_[3][0] + (q_[2][0] - q_[3][0]) * t_, q_[3][1] + (q_[2][1] - q_[3][1]) * t_
                pp = onF(ub_, vb_ + 9, 0.040)
                mid_d.box((pp.x, pp.y, pp.z), (0.026, 0.026, 0.024))
                rivets.cyl((pp.x, pp.y - 0.013, pp.z), (pp.x, pp.y - 0.018, pp.z), 0.0045, 6)
            # omuz bloğu: ikinci kat + üst kapak
            ua, ub = uu(196, 262); tier(ua, 446, ub, 520, 0.040, 0.03, 'shoulder2_' + nm, mat='hay_dark')
            for k_ in range(4):
                plate(ua + 5, 456 + k_ * 16, ub - 5, 458.5 + k_ * 16, mid_d, 0.058, 0.004)
            # ekran dış kenarı: dikey kasa omuzu (yan ekran ile omuz bloğu arası)
            ua, ub = uu(274, 288); plate(ua, 400, ub, 540, mid_d, 0.030, 0.012); plate(ua + 3, 410, ub - 3, 530, dark_d, 0.036, 0.006)
        # radar kepi: ikinci kat + mandallar
        plate(660, vtop(800) - 5, 940, vtop(800) + 2, dark_d, 0.03, 0.008)
        for u_ in (650, 950):
            plate(u_ - 9, vtop(u_) - 7, u_ + 9, vtop(u_) + 1, mid_d, 0.034, 0.008)      # ekran köşesini örtmesin (üstünde kalır)
        # ekran bandı boyunca kablo oluğu (orta ekran altında, koltuk üstünde): iki ince kanal + kelepçeler
        for k_, v_ in enumerate((516, 524)):
            plate(662, v_, 938, v_ + 2.2, dark_d, 0.0455, 0.004)
        for u_ in lin(690, 910, 6):
            plate(u_ - 3, 512, u_ + 3, 528, mid_d, 0.048, 0.006)

    # ---- koltuk: kapitone siyah deri (Kaşif ayak izi); radar alt kenarı yüksek → geniş görünür alan
    sy = 0.555
    ztop = A['seat']['top_z']
    add('seat_headrest_v', soft_box((0, sy, ztop - 0.135), (0.34, 0.10, 0.27), 0.028, 1), 'hay_leather', smooth=60)
    fyy = sy - 0.0505
    for s_ in (-1, 1):
        nm = 'L' if s_ < 0 else 'R'
        add('seat_wing_v_' + nm, soft_box((s_ * 0.235, sy - 0.012, ztop - 0.215), (0.10, 0.11, 0.26), 0.024, 1), 'hay_leather', smooth=60)
    if A.get('r004') and A.get('seam_min'):      # r006: yalnız iki ince dikey dikiş (ızgara okunmasın)
        for dx_ in (-0.095, 0.095):
            thread_d.box((dx_, fyy - 0.0005, ztop - 0.125), (0.003, 0.003, 0.19))
    elif A.get('r004'):      # r004: sade tek yüzlü sırt (yastık/tuğla okunmasın): yalnız ince koyu mor dikiş çizgileri
        for dx_ in (-0.095, 0.095):
            thread_d.box((dx_, fyy - 0.0005, ztop - 0.125), (0.003, 0.003, 0.19))
        thread_d.box((0, fyy - 0.0005, ztop - 0.075), (0.30, 0.003, 0.003))
        for s_ in (-1, 1):
            thread_d.box((s_ * 0.235, sy - 0.012 - 0.0555, ztop - 0.13), (0.003, 0.003, 0.17))
        for dx_ in (-0.17, 0.17):
            thread_d.box((dx_, fyy - 0.0005, ztop - 0.04), (0.003, 0.003, 0.05))
    else:
        # kapitone yastıkçıklar (üç sütun x üç sıra başlıkta; kanatlarda iki sıra) ve aralarında koyu mor iplik
        pw_, ph_, pd_, pb_ = (0.1055, 0.0685, 0.012, 0.014) if A.get('r002') else (0.100, 0.062, 0.022, 0.010)      # r002: yastıklar neredeyse bitişik, düşük kabartma (tek kapitone yüz)
        pad = lambda cx, cz, w, h, nm, yy: add(nm, soft_box((cx, yy, cz), (w if not A.get('r002') else pw_, pd_, h if not A.get('r002') else ph_), pb_, 1), 'hay_leather', smooth=60)
        for r_, dz_ in enumerate((0.045, 0.115, 0.185)):
            for c_, dx_ in enumerate((-0.108, 0.0, 0.108)):
                pad(dx_, ztop - dz_, 0.100, 0.062, 'seat_pad_%d%d' % (r_, c_), fyy - 0.004)
        for s_ in (-1, 1):
            for r_, dz_ in enumerate((0.080, 0.170)):
                pad(s_ * 0.235, ztop - dz_, 0.078, 0.074, 'seat_wpad_%d_%d' % (s_ > 0, r_), sy - 0.012 - 0.0555 - 0.004)
            thread_d.box((s_ * 0.235, sy - 0.012 - 0.0545, ztop - 0.125), (0.082, 0.003, 0.004))
        for dz_ in (0.080, 0.150):
            thread_d.box((0, fyy, ztop - dz_), (0.34, 0.003, 0.004))
        for dx_ in (-0.054, 0.054):
            thread_d.box((dx_, fyy, ztop - 0.12), (0.004, 0.003, 0.20))


    # ---- toplu ayrıntı grupları (küçük pah: kenar parlaması)
    for nm, acc, mt, role, bev in (('detail_carbon', carb_d, 'hay_carbon', 'body', True), ('detail_dark', dark_d, 'hay_dark', 'body', True), ('detail_mid', mid_d, 'hay_mid', 'body', True),
                                   ('detail_neon', lamps_d, 'emit_violet', 'emit_live', False), ('detail_thread', thread_d, 'hay_thread2' if A.get('r004') else 'hay_thread', 'body', False),
                                   ('detail_rivets', rivets, 'hay_mid', 'body', False), ('detail_hex', hexes, 'hay_hex' if A.get('r002') else 'hay_dark', 'body', False)):
        if not acc.empty():
            add(nm, Soft(acc.bm, 0.0018, 0) if bev else acc.bm, mt, role=role, smooth=60)

    socks = [{'name': 'SOCK_cam_0', 'loc': (0, 0, 0), 'dir': (0, 1, 0), 'extras': {'purpose': 'pilot gözü (kamera sözleşmesi)', 'fovy': 74}}]
    return {'objects': obs, 'sockets': socks}
