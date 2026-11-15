"""Pilot koltuğu v2 — anatomik, hacimli, yuvarlak. Oturma minderi (çukurlu, yan destekli, ön kıvrımlı), sırt minderi (bel desteği + pilotu kavrayan
kanatlar), baş desteği. Düşük kafeslerden şekillendirilip Subsurf ile yumuşatılır; keskin blok yok. Dikiş/kapitone/deri biye ve alt ray+braketler korunur.
Yerleşim eskisiyle aynı (params['seat'].y/z); yükseklik, dashboard ekranlarının görüşünü kapatmayacak şekilde sınırlı (verify: ekran ışın testi)."""
import bpy, bmesh, math
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from .common import *
from .detail import box, cyl
from .side import tube

def ss(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)

def sculpt(name, dims, cuts, fn, mat, level=2):
    """Kutu kafesini böl, fn ile şekillendir, Subsurf uygula. Yerel eksenler: X yanal, Y ileri (dashboard yönü), Z yukarı."""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=Vector(dims), verts=bm.verts)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True)
    for v in bm.verts: v.co = fn(v.co.copy())
    ob = obj_from_bm(name, bm, mat, collection='Cockpit')
    m = ob.modifiers.new('ss', 'SUBSURF'); m.levels = level; m.render_levels = level; m.subdivision_type = 'CATMULL_CLARK'; apply_modifier(ob, m)
    for p in ob.data.polygons: p.use_smooth = True
    return ob

# ---- şekil fonksiyonları (yerel koordinat; pan merkezi orijin)
PW, PD, PH = 0.62, 0.42, 0.11          # oturma: genişlik, derinlik, kalınlık
def pan_fn(p):
    x, y, z = p.x, p.y, p.z; hw, hd = PW / 2, PD / 2; top = z > 0
    ax, ay = abs(x) / hw, abs(y) / hd
    if top:
        z -= 0.032 * (1 - ax * ax) * (1 - ay * ay)                     # oturma çukuru
        z += 0.058 * ss(0.45, 0.95, ax) * (1 - 0.35 * ay)               # yan destekler (kavrayıcı)
        yy = -y                                                         # ön (pilota bakan) = -Y
        if yy > 0.12: z -= 0.075 * ((yy - 0.12) / 0.09) ** 2            # ön kıvrım (şelale kenar)
        x *= 1 - 0.05 * ss(0.4, 1.0, ax)                                # yan destekler hafif içe
    else:
        x *= 0.84 - 0.08 * ay; y *= 0.94                                # alt: daralır
    # köşe yuvarlama (süper elips): köşeler içeri
    k = 1 - 0.16 * (ax ** 3) * (ay ** 3) * 2.2
    return Vector((x * k, y * k, z))

BW, BT, BH = 0.66, 0.15, 0.21           # sırt: genişlik, kalınlık, yükseklik (ekran görüşü için sınırlı)
def back_fn(p):
    x, y, z = p.x, p.y, p.z; hw = BW / 2; ax = abs(x) / hw; h = (z + BH / 2) / BH     # 0 alt .. 1 üst
    front = y < 0
    if front:
        y -= 0.115 * ss(0.30, 1.0, ax) ** 1.25 * (0.55 + 0.45 * h)       # kanatlar pilota doğru kavrar
        y += 0.020 * (1 - ax * ax) * (1 - 0.5 * h)                      # orta: hafif içbükey, bel desteği
    x *= 1 - 0.14 * ss(0.55, 1.0, h)                                    # omuz hattı daralır
    z += 0.012 * (ax ** 2)                                              # kenarlar hafif yukarı kıvrılır
    k = 1 - 0.14 * (ax ** 4) * (h ** 3) * 1.6
    return Vector((x * k, y, z * k))

HW_, HT, HH = 0.24, 0.09, 0.060
def head_fn(p):
    x, y, z = p.x, p.y, p.z; ax = abs(x) / (HW_ / 2)
    if y < 0: y -= 0.04 * ss(0.4, 1.0, ax)
    return Vector((x * (1 - 0.10 * (ax ** 3)), y, z))

def bvh_of(ob):
    dg = bpy.context.evaluated_depsgraph_get(); return BVHTree.FromObject(ob, dg)

def project(bvh, origin, direction):
    hit = bvh.ray_cast(origin, direction)
    return hit if hit[0] is not None else None

def dashes(parent, pts_nrm, mat, length=0.017, w=0.0035, lift=0.0016):
    out = []
    for i in range(len(pts_nrm) - 1):
        (a, na), (b, nb) = pts_nrm[i], pts_nrm[i + 1]; mid = (a + b) / 2; n = (na + nb).normalized(); d = (b - a)
        if d.length < 1e-5: continue
        d = (d - n * d.dot(n)).normalized(); y = n.cross(d).normalized()
        R = Matrix(((d.x, y.x, n.x), (d.y, y.y, n.y), (d.z, y.z, n.z)))
        bm = bmesh.new(); hl, hw = length / 2, w / 2
        vs = [bm.verts.new(c) for c in ((-hl, -hw, 0), (hl, -hw, 0), (hl, hw, 0), (-hl, hw, 0))]; bm.faces.new(vs)
        ob = obj_from_bm('Seat_stitch', bm, mat, collection='Cockpit'); ob.location = mid + n * lift; ob.rotation_euler = R.to_euler(); ob.parent = parent; out.append(ob)
    return out

def line_pts(bvh, a_uv, b_uv, axis, n, frame_z):
    """(u,v) düzleminde a→b doğrusu boyunca yüzeye iz düşür. axis: 'z' (üstten), 'y' (önden)."""
    pts = []
    for k in range(n + 1):
        t = k / n; u = a_uv[0] + (b_uv[0] - a_uv[0]) * t; v = a_uv[1] + (b_uv[1] - a_uv[1]) * t
        if axis == 'z': o = Vector((u, v, frame_z)); d = Vector((0, 0, -1))
        else: o = Vector((u, frame_z, v)); d = Vector((0, 1, 0))
        h = project(bvh, o, d)
        if h: pts.append((h[0], h[1]))
    return pts

def rect_loop(u0, u1, v0, v1, step_est=0.026):
    """Dikdörtgen çevre (a,b noktaları çifti listesi)."""
    c = [(u0, v0), (u1, v0), (u1, v1), (u0, v1), (u0, v0)]; return list(zip(c[:-1], c[1:]))

def stitched_panel(parent, bvh, axis, frame_z, rect, mats, label, step=0.026):
    """Yüzeye oturan kapitone panel çevresi: dikiş hattı (dışta), biye (kenarda), orta çapraz dikişler (elmas hissi)."""
    out = []; u0, u1, v0, v1 = rect
    outline = []
    for (a, b) in rect_loop(u0, u1, v0, v1):
        n = max(2, int(math.dist(a, b) / step))
        outline += line_pts(bvh, a, b, axis, n, frame_z)[:-1]
    if outline: outline.append(outline[0])
    ex = 0.024; outer = []                                               # dış dikiş hattı: biyenin dışında, deri üzerinde
    for (a, b) in rect_loop(u0 - ex, u1 + ex, v0 - ex, v1 + ex):
        n = max(2, int(math.dist(a, b) / step))
        outer += line_pts(bvh, a, b, axis, n, frame_z)[:-1]
    if outer: outer.append(outer[0])
    out += dashes(parent, outer, mats['thread'], 0.019, 0.0045)
    pip = tube('Seat_piping', [Vector((p.x, -p.y, p.z)) for p, nrm in [(q[0] + q[1] * 0.0075, q[1]) for q in []]], 0.0075, mats['leather'], 8) if False else None
    # biye: dış kenar boyunca deri boru (oyun uzayına çevrilmeden doğrudan yerel)
    ring = [q[0] + q[1] * 0.0085 for q in outline]
    if len(ring) > 3:
        tb = bmesh.new(); sides = 8; rings = []; n = len(ring)
        for i, p in enumerate(ring):
            t = (ring[min(i + 1, n - 1)] - ring[max(i - 1, 0)]); t.normalize(); ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
            a = t.cross(ref).normalized(); b = t.cross(a).normalized()
            rings.append([tb.verts.new(p + (a * math.cos(2 * math.pi * k / sides) + b * math.sin(2 * math.pi * k / sides)) * 0.0072) for k in range(sides)])
        for i in range(n - 1):
            for k in range(sides): tb.faces.new((rings[i][k], rings[i][(k + 1) % sides], rings[i + 1][(k + 1) % sides], rings[i + 1][k]))
        bmesh.ops.recalc_face_normals(tb, faces=list(tb.faces))
        po = obj_from_bm('Seat_piping', tb, mats['leather'], collection='Cockpit', smooth=True); po.parent = parent; out.append(po)
    # orta çapraz dikişler
    cu, cv = (u0 + u1) / 2, (v0 + v1) / 2
    for (a, b) in (((u0 + (u1 - u0) * 0.1, cv), (u1 - (u1 - u0) * 0.1, cv)), ((cu, v0 + (v1 - v0) * 0.1), (cu, v1 - (v1 - v0) * 0.1)),
                   ((u0 + (u1 - u0) * 0.1, v0 + (v1 - v0) * 0.1), (u1 - (u1 - u0) * 0.1, v1 - (v1 - v0) * 0.1)), ((u0 + (u1 - u0) * 0.1, v1 - (v1 - v0) * 0.1), (u1 - (u1 - u0) * 0.1, v0 + (v1 - v0) * 0.1))):
        out += dashes(parent, line_pts(bvh, a, b, axis, 14, frame_z), mats['thread'], 0.013, 0.0035, lift=0.0092)
    return out

def build(a, P, mats):
    S = P['seat']; out = []; L = mats['leather']; Fb = mats['fabric']
    grp = bpy.data.objects.new('Seat', None); coll('Cockpit').objects.link(grp)
    grp.location = g2b(Vector((0, S['y'], S['z']))); grp.rotation_euler = (math.radians(-S.get('pitch', 5)), 0, 0)
    pan = sculpt('Seat_Pan', (PW, PD, PH), 6, pan_fn, L); pan.parent = grp; out.append(pan)
    back = sculpt('Seat_Back', (BW, BT, BH), 6, back_fn, L); back.parent = grp; back.location = (0, PD / 2 - 0.01, PH / 2 + BH / 2 - 0.02)
    back.rotation_euler = (math.radians(-S.get('recline', 12)), 0, 0); out.append(back)
    head = sculpt('Seat_Head', (HW_, HT, HH), 4, head_fn, L); head.parent = grp
    head.location = (0, PD / 2 + 0.030, PH / 2 + BH + HH / 2 - 0.085); head.rotation_euler = (math.radians(-S.get('recline', 12)), 0, 0); out.append(head)
    bpy.context.view_layer.update()
    # kapitone paneller (yüzeye iz düşürülmüş dikiş + biye); panel dolgusu yok — kumaş doku/rengi yüzeyle birlikte okunur
    bp = bvh_of(pan); bb = bvh_of(back)
    out += stitched_panel(pan, bp, 'z', 0.5, (-0.17, 0.17, -0.12, 0.10), mats, 'pan')
    out += stitched_panel(back, bb, 'y', -0.5, (-0.19, 0.19, -0.075, 0.065), mats, 'back')
    # kumaş ek paneller: panel bölgesi için ince yükseltilmiş yama (yüzey kopyası)
    for (ob, bv, axis, fz, rect) in ((pan, bp, 'z', 0.5, (-0.165, 0.165, -0.115, 0.095)), (back, bb, 'y', -0.5, (-0.185, 0.185, -0.07, 0.06))):
        out += fabric_patch(ob, bv, axis, fz, rect, Fb)
    # ray ve braketler (alt mekanik; yerleşim korunur)
    for sx in (-1, 1):
        x = sx * 0.24
        out.append(box('Seat_rail', (0.07, 0.42, 0.03), g2b(Vector((x, S['y'] - 0.13, S['z'] - 0.0))), mats['steel'], bev=0.005))
        for dz in (-0.17, 0.17):
            out.append(box('Seat_bracket', (0.10, 0.045, 0.05), g2b(Vector((x, S['y'] - 0.12, S['z'] + dz))), mats['titanium'], bev=0.006))
            for ddx in (-0.03, 0.03): out.append(cyl('Seat_bolt', 0.007, 0.012, g2b(Vector((x + ddx, S['y'] - 0.095, S['z'] + dz))), (math.radians(90), 0, 0), mats['aluminum'], 6))
    out.append(box('Seat_frame', (0.74, 0.05, 0.05), g2b(Vector((0, S['y'] - 0.13, S['z'] - 0.05))), mats['steel'], bev=0.012))
    return out

def fabric_patch(ob, bvh, axis, frame_z, rect, mat, lift=0.006):
    """rect içindeki yüzey ızgarasını normal boyunca hafif kaldırıp ince kumaş yaması üret."""
    u0, u1, v0, v1 = rect; nu, nv = 14, 10; bm = bmesh.new(); grid = []
    for j in range(nv + 1):
        row = []
        for i in range(nu + 1):
            u = u0 + (u1 - u0) * i / nu; v = v0 + (v1 - v0) * j / nv
            if axis == 'z': o = Vector((u, v, frame_z)); d = Vector((0, 0, -1))
            else: o = Vector((u, frame_z, v)); d = Vector((0, 1, 0))
            h = bvh.ray_cast(o, d)
            if h[0] is None: row.append(None); continue
            # kenarlara doğru alçalt (yumuşak yastık kenarı)
            e = min(i, nu - i, j, nv - j) / 3.0; f = min(1.0, e); row.append(bm.verts.new(h[0] + h[1] * (lift * f + 0.0008)))
        grid.append(row)
    for j in range(nv):
        for i in range(nu):
            vs = [grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]]
            if all(vs): bm.faces.new(vs)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    po = obj_from_bm('Seat_fabric', bm, mat, collection='Cockpit', smooth=True); po.parent = ob; return [po]
