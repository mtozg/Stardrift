"""Kokpit ailesi — PREVIEW blokajı (kaba kütleler). İlk tarif: Şahin, konsept A "Damla Fanus".

Kamera sözleşmesi (oyunun ortak pilot kamerası; Kaşif GLB ile aynı, kod yeniden yazıldı, kopyalanmadı):
  göz orijinde, ileri = oyun −Z (Blender +Y), dikey FOV 74°, asal nokta (800, 239,5) / 1600×656, odak 435,27 px.
Konsept şemasındaki piksel (u, v) ve bir derinlik d, P(u, v, d) ile 3B noktaya çevrilir; böylece blokaj onaylı şemayla hizalı kurulur.
Ekran sözleşmesi: SCR_SYS / SCR_RADAR / SCR_HULL dörtgenleri, köşe sırası TL, TR, BR, BL; UV TL=(0,1) … (oyun ekranları ada göre bağlar).
Bu dosya YALNIZCA PREVIEW blokajı içindir: ayrıntı, UV, bake ve GLB PRODUCTION aşamasındadır."""
import bpy, bmesh, math, os, json
from mathutils import Vector, Matrix
from core import geo, render as R

F, CX, CY, W, H = 435.2707, 800.0, 239.5, 1600, 656


def P(u, v, d):
    return Vector(((u - CX) / F * d, d, -(v - CY) / F * d))


def to_px(p):
    """Blender noktası → pilot görüntüsü pikseli (1600×656)."""
    return (CX + F * p.x / p.y, CY - F * p.z / p.y)


def face_eye(bm):
    """Göze dönük yüzler: normali gözden uzaklaşan yüzü çevir (pilotun gördüğü taraf ön yüz olsun)."""
    bm.normal_update()
    for f in bm.faces:
        if f.normal.dot(f.calc_center_median()) > 0:
            f.normal_flip()
    return bm


def grid(rows, close=False):
    bm = bmesh.new()
    V = [[bm.verts.new(p) for p in row] for row in rows]
    for r in range(len(V) - 1):
        for c in range(len(V[r]) - 1):
            bm.faces.new((V[r][c], V[r][c + 1], V[r + 1][c + 1], V[r + 1][c]))
    return bm


def tube(points, r, seg=10):
    bm = bmesh.new()
    rings = []
    a_prev = None
    for i, p in enumerate(points):
        t = (points[min(i + 1, len(points) - 1)] - points[max(i - 1, 0)]).normalized()
        # paralel taşıma: önceki kesit eksenini yeni teğete dik düzleme izdüşür (r005'teki burulmanın düzeltmesi)
        a = t.orthogonal().normalized() if a_prev is None else (a_prev - t * a_prev.dot(t)).normalized()
        a_prev = a
        b = t.cross(a).normalized()
        rings.append([bm.verts.new(p + (a * math.cos(2 * math.pi * k / seg) + b * math.sin(2 * math.pi * k / seg)) * r) for k in range(seg)])
    for i in range(len(rings) - 1):
        for k in range(seg):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % seg], rings[i + 1][(k + 1) % seg], rings[i + 1][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def lin(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


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
            m.offset = 1.0 if toward_eye else -1.0      # kalınlık gözden uzağa (PREVIEW r001'de göze doğruydu ve ekranları örttü)
            geo.apply_modifier(ob, m)
        geo.set_smooth_by_angle(ob, smooth)
        obs.append(ob)
        return ob

    # ---- konsol "küvet": şemadaki üst kenar eğrisi (0,520)–(250,436)–Q(800,396)–(1350,436)–(1600,520)
    def vtop(u):
        if u < 250:
            return 436 + (250 - u) / 250 * 84
        if u > 1350:
            return 436 + (u - 1350) / 250 * 84
        return 436 - 40 * (1 - ((u - 800) / 550) ** 2)

    def dep(u):
        return max(0.36, A['console_depth'] - A['console_wrap'] * ((u - 800) / 800) ** 2)

    U = lin(-700, 2300, 61)
    top = [P(u, vtop(u), dep(u)) for u in U]
    mid = [P(u, vtop(u) + 40, dep(u) - 0.004) for u in U]
    bot = [P(u, 900, dep(u) - A['fascia_lean']) for u in U]

    def surf(u, v):
        """Konsol ön yüzünün (u, v) pikselindeki derinliği (üst bant + pilota eğilen alt yüz)."""
        vt = vtop(u)
        if v <= vt + 40:
            return dep(u) - 0.004 * (v - vt) / 40
        return dep(u) - 0.004 - (A['fascia_lean'] - 0.004) * (v - vt - 40) / (900 - vt - 40)
    add('console_panel', grid([top, mid]), 'sahin_paint', eye=True, solid=0.02)
    add('console_fascia', grid([mid, bot]), 'sahin_mid', eye=True, solid=0.02)
    deck = [p + Vector((0, A['deck_depth'], -A['deck_drop'])) for p in top]      # üst yüzey ileriye doğru alçalır: gözden ufka yükselmez (HUD bölgesi açık)
    add('console_deck', grid([deck, top]), 'sahin_paint', eye=True, solid=0.015)
    U2 = lin(262, 1338, 33)
    add('console_stripe', grid([[P(u, vtop(u) + 6, dep(u) - 0.006) for u in U2], [P(u, vtop(u) + 13, dep(u) - 0.006) for u in U2]]), 'emit_red', role='emit_live', eye=True)

    # ---- göz kalkanı (anti-glare): üst eğri 436→376→436, alt kenar 452→398→452
    UG = lin(560, 1040, 25)
    gt = [P(u, 436 - 60 * (1 - ((u - 800) / 240) ** 2), A['glare_depth']) for u in UG]
    gb = [P(u, max(452 - 54 * (1 - ((u - 800) / 222) ** 2), 398), A['glare_depth']) for u in UG]
    add('glare_front', grid([gt, gb]), 'antiglare', eye=True, solid=0.012)
    add('glare_top', grid([[p + Vector((0, 0.16, -0.035)) for p in gt], gt]), 'antiglare', eye=True, solid=0.012)

    # ---- ekranlar + çerçeveler (şemadaki piksel dörtgenlerinden)
    def screen(name, q, depth_fn, bezel_px=12):
        pts = [P(u, v, depth_fn(u, v) - 0.012) for u, v in q]      # ekran, konsol yüzeyinin her noktada 12 mm önünde
        bm = bmesh.new()
        vs = [bm.verts.new(p) for p in pts]
        f = bm.faces.new(vs)
        uvl = bm.loops.layers.uv.new('UVMap')
        for loop, uv in zip(f.loops, [(0, 1), (1, 1), (1, 0), (0, 0)]):
            loop[uvl].uv = uv
        face_eye(bm)
        ob = geo.mesh_object(name, bm, mats['screen_placeholder'], coll='Asset', role='screen')
        obs.append(ob)
        cu = sum(u for u, v in q) / 4
        cv = sum(v for u, v in q) / 4
        outer = []
        for u, v in q:
            du, dv = u - cu, v - cv
            l = math.hypot(du, dv)
            outer.append((u + du / l * bezel_px * 1.4, v + dv / l * bezel_px * 1.4))
        ring_in = [P(u, v, depth_fn(u, v) - 0.010) for u, v in q]
        ring_out = [P(u, v, depth_fn(u, v) - 0.010) for u, v in outer]
        bm2 = bmesh.new()
        vi = [bm2.verts.new(p) for p in ring_in]
        vo = [bm2.verts.new(p) for p in ring_out]
        for k in range(4):
            bm2.faces.new((vo[k], vo[(k + 1) % 4], vi[(k + 1) % 4], vi[k]))
        add(name.replace('SCR_', 'bezel_').lower(), bm2, 'sahin_dark', eye=True, solid=A['bezel_protrude'], toward_eye=True)      # çıkıntı ≤ 8 mm: eğik bakışta ekran kenarını örtmesin
        return ob

    sc = A['screens']
    screen('SCR_RADAR', sc['radar'], lambda u, v: min(A['radar_depth'], surf(u, v)))
    screen('SCR_SYS', sc['sys'], surf)
    screen('SCR_HULL', sc['hull'], surf)

    # ---- kabarcık kanopi: tek ince ön kemer (elips yay) + tepeden geçen omurga + iç kırmızı şerit
    hc = A['hoop']
    th = lin(0.0, math.pi, 49)
    # geriye yatık ön kemer: tepe önde (depth), ayaklar pilotun yanında (side_depth) → şemadaki gibi uçlar görüş alanının dışında
    hoop = [Vector((hc['a'] * math.cos(t), hc['side_depth'] + (hc['depth'] - hc['side_depth']) * math.sin(t), hc['y0'] + hc['b'] * math.sin(t))) for t in th]
    add('canopy_hoop', tube(hoop, hc['r'], 12), 'sahin_dark', smooth=60)
    inner = [Vector((p.x * 0.985, p.y - 0.022, p.z - 0.018 * math.sin(t))) for p, t in zip(hoop, th)]
    add('canopy_hoop_light', tube(inner[3:-3], 0.005, 6), 'emit_red', role='emit_live', smooth=60)
    ztop = hc['y0'] + hc['b']
    spine = [Vector((0, hc['depth'], ztop)), Vector((0, 0.45, ztop + 0.07)), Vector((0, 0.05, ztop + 0.11)), Vector((0, -0.35, ztop + 0.06)), Vector((0, -0.6, ztop - 0.08))]
    add('canopy_spine', tube(spine, 0.016, 10), 'sahin_dark', smooth=60)

    # ---- yan eşikler: kanopi rayı pilota doğru yükselir (şema: (250,436) → (0,318)); altında koyu yan panel; zemin
    sl = A['sill']
    rail = [Vector((0, y, sl['z_front'] + (sl['z_mid'] - sl['z_front']) * min(1.0, (sl['y_front'] - y) / (sl['y_front'] - sl['y_mid'])))) for y in lin(sl['y_front'], sl['y_back'], 17)]
    for s in (-1, 1):
        sx = s * sl['x']
        top_r = [Vector((sx, p.y, p.z)) for p in rail]
        add('sill_panel_%s' % ('L' if s < 0 else 'R'), grid([top_r, [Vector((sx, p.y, -0.85)) for p in rail]]), 'sahin_dark', eye=True, solid=0.03)
        add('sill_rail_%s' % ('L' if s < 0 else 'R'), tube([Vector((sx - s * 0.02, p.y, p.z + 0.015)) for p in rail], 0.03, 10), 'sahin_paint', smooth=60)
    add('floor', geo.bm_box((0, 0.2, -0.87), (2.0 * sl['x'], 1.6, 0.04)), 'sahin_dark')

    # ---- uçuş kolu (orta) + gaz kolu (sol)
    add('stick_shaft', geo.bm_cylinder((0, 0.40, -0.85), (0, 0.44, -0.44), 0.016, 12), 'sahin_dark', smooth=60)
    add('stick_grip', geo.bm_cylinder((0, 0.44, -0.46), (0, 0.455, -0.37), 0.028, 14), 'sahin_dark', smooth=60)
    add('stick_button', geo.bm_cylinder((0, 0.452, -0.375), (0, 0.456, -0.36), 0.009, 10), 'sahin_red', smooth=60)
    add('throttle_base', geo.bm_box((-0.30, 0.52, -0.50), (0.09, 0.12, 0.04)), 'sahin_dark')
    add('throttle_handle', geo.bm_box((-0.30, 0.52, -0.455), (0.035, 0.035, 0.05)), 'sahin_red')

    # ---- yatık fırlatma koltuğu (pilot görüşünde görünmez; plan ve çapraz görünüşler için)
    st = A['seat']
    add('seat_pan', geo.bm_box((0, 0.02, st['pan_z']), (0.46, 0.46, 0.10)), 'seat_textile')
    back = geo.bm_box((0, -0.27, st['pan_z'] + 0.40), (0.44, 0.10, 0.78))
    bmesh.ops.rotate(back, cent=Vector((0, -0.27, st['pan_z'] + 0.02)), matrix=Matrix.Rotation(math.radians(-st['recline_deg']), 3, 'X'), verts=back.verts)
    add('seat_back', back, 'seat_textile')
    for s in (-1, 1):
        wing = geo.bm_box((s * 0.25, -0.24, st['pan_z'] + 0.32), (0.06, 0.16, 0.55))
        bmesh.ops.rotate(wing, cent=Vector((0, -0.27, st['pan_z'] + 0.02)), matrix=Matrix.Rotation(math.radians(-st['recline_deg']), 3, 'X'), verts=wing.verts)
        add('seat_wing_%s' % ('L' if s < 0 else 'R'), wing, 'sahin_dark')
    hr = geo.bm_box((0, -0.32, st['pan_z'] + 0.86), (0.26, 0.09, 0.18))      # sırtın üstüne oturur (r006'da ayrıktı)
    bmesh.ops.rotate(hr, cent=Vector((0, -0.27, st['pan_z'] + 0.02)), matrix=Matrix.Rotation(math.radians(-st['recline_deg']), 3, 'X'), verts=hr.verts)
    add('seat_headrest', hr, 'seat_textile')
    hd = geo.bm_box((0, -0.28, st['pan_z'] + 0.97), (0.16, 0.03, 0.05))
    bmesh.ops.rotate(hd, cent=Vector((0, -0.27, st['pan_z'] + 0.02)), matrix=Matrix.Rotation(math.radians(-st['recline_deg']), 3, 'X'), verts=hd.verts)
    add('seat_eject_handle', hd, 'sahin_red')
    add('seat_rail', geo.bm_box((0, -0.05, st['pan_z'] - 0.12), (0.30, 0.6, 0.12)), 'sahin_dark')

    return {'objects': obs, 'sockets': [{'name': 'SOCK_cam_0', 'loc': (0, 0, 0), 'dir': (0, 1, 0), 'extras': {'purpose': 'pilot gözü (kamera sözleşmesi)', 'fovy': 74}}]}


# ------------------------------------------------------------------ PREVIEW render ve ölçümleri

def _pilot_cam():
    cd = bpy.data.cameras.new('Pilot')
    cd.sensor_fit = 'VERTICAL'
    cd.sensor_height = 24.0
    cd.lens = 12.0 / math.tan(math.radians(37.0))
    cd.shift_y = -(0.5 - CY / H)      # asal nokta 239,5/656; dikey sensör uyumunda shift birimi görüntü YÜKSEKLİĞİ (r001 ölçümü: 52 px hata = 0,0796 × 656)
    cd.clip_start = 0.01
    cd.clip_end = 100
    ob = bpy.data.objects.new('Pilot', cd)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = (0, 0, 0)
    ob.rotation_euler = (math.radians(90), 0, 0)
    return ob


def _lights():
    R.clear_lights()
    R.world_space(0.35)
    R.light('SUN', (-3, 4, 6), 3.0, (1.0, 0.95, 0.88), 2.0, look=(0, 0, 0), name='Sun')
    R.light('AREA', (0, 0.35, 0.9), 25, (0.75, 0.82, 1.0), 1.6, look=(0, 0.6, -0.5), name='Sky')
    R.light('AREA', (0, 0.6, -0.25), 3.0, (0.30, 0.80, 1.0), 0.6, look=(0, 0.9, -0.5), name='ScreenGlow')
    R.light('AREA', (0, 0.15, -0.30), 6.0, (0.9, 0.95, 1.0), 1.2, look=(0, 0.9, -0.45), name='Fill')


def preview(spec, out, fast, obs):
    import numpy as np
    sc = bpy.context.scene
    _lights()
    samples = 32 if fast else 128
    res = {}
    pilot = _pilot_cam()
    R.render(os.path.join(out, '01_pilot.png'), pilot, (1600, 656) if not fast else (1200, 492), samples)
    views = [('02_capraz', (0.62, -0.30, 0.28), (-0.15, 0.85, -0.45), 70, (1200, 750)),
             ('03_konsol', (0.30, 0.30, -0.18), (-0.05, 0.92, -0.42), 52, (1200, 750)),
             ('04_koltuk', (0.45, 0.62, -0.05), (0.0, -0.22, -0.40), 62, (1200, 750)),
             ('05_dis', (-2.2, 2.6, 1.5), (0, 0.25, -0.35), 38, (1200, 750))]
    for name, loc, look, fov, rs in views:
        c = R.camera(name, loc, look, fov)
        R.render(os.path.join(out, name + '.png'), c, rs, samples)
    plan = R.camera('Plan', (0, 0.2, 4.0), (0, 0.2, -0.5), ortho_scale=2.6)
    R.render(os.path.join(out, '06_plan.png'), plan, (900, 900), samples)

    # ölçüm 1: cam oranı ve orta (HUD) bölge engeli — pilot kamerasından alfa maskesi
    R.render(os.path.join(out, '_mask.png'), pilot, (1600, 656), 1, transparent=True, denoise=False)
    from PIL import Image
    a = np.asarray(Image.open(os.path.join(out, '_mask.png')).convert('RGBA'))[..., 3] > 127
    res['glass_ratio'] = round(float(1 - a.mean()) * 100, 1)
    res['hud_zone_block'] = round(float(a[60:380, 560:1040].mean()) * 100, 1)
    os.remove(os.path.join(out, '_mask.png'))

    # ölçüm 2: ekran sözleşmesi — ad, çerçeve içinde mi, gözden görünür mü (merkez + %6 içeri köşeler)
    dg = bpy.context.evaluated_depsgraph_get()
    scr = {}
    for nm in ('SCR_SYS', 'SCR_RADAR', 'SCR_HULL'):
        o = bpy.data.objects.get(nm)
        if not o:
            scr[nm] = {'var': False}
            continue
        vs = [o.matrix_world @ v.co for v in o.data.vertices]
        c = sum(vs, Vector()) / 4
        pts = [c] + [c + (v - c) * 0.94 for v in vs]
        vis = 0
        for p in pts:
            hit, loc, nor, idx, hob, mat = sc.ray_cast(dg, Vector((0, 0, 0)), p.normalized())
            vis += int(hit and hob.name == nm)
        px = [tuple(round(x) for x in to_px(v)) for v in vs]
        inside = all(0 <= x <= W and 0 <= y <= H for x, y in px)
        uv = [tuple(round(x, 2) for x in l.uv) for l in o.data.uv_layers[0].data]
        scr[nm] = {'var': True, 'gorunur': '%d/5' % vis, 'cerceve_ici': inside, 'kose_px': px, 'uv': uv}
    res['screens'] = scr
    # ölçüm 3: kamera sözleşmesi — bilinen 3B noktaların render pikseline düştüğü yer (Blender'ın kendi izdüşümüyle)
    from bpy_extras.object_utils import world_to_camera_view
    sc.render.resolution_x, sc.render.resolution_y = W, H
    errs = []
    for u, v in ((800, 239.5), (200, 500), (1400, 120), (690, 452)):
        q = world_to_camera_view(sc, pilot, P(u, v, 0.9))
        errs.append(math.hypot(q.x * W - u, (1 - q.y) * H - v))
    res['camera_contract_err_px'] = round(max(errs), 3)
    res['tris_by_object'] = {o.name: geo.tri_count([o]) for o in obs}
    return res
