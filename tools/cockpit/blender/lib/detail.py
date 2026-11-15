"""Küçük mekanik ayrıntılar: cıvatalar, kelepçeler/braketler, havalandırma ızgarası, restrained cyan şeritler. Kalabalık yapmaz; bakılan yerlerde."""
import bpy, bmesh, math
from mathutils import Vector, Matrix
from .common import *
from .dash import Face
from . import materials

def box(name, size, loc_b, mat, rot=None, bev=0.002):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    ob = obj_from_bm(name, bm, mat, collection='Cockpit'); ob.location = loc_b
    if rot: ob.rotation_euler = rot
    if bev:
        m = ob.modifiers.new('b', 'BEVEL'); m.width = bev; m.segments = 1; m.limit_method = 'NONE'; apply_modifier(ob, m)
    return ob

def cyl(name, r, h, loc_b, rot, mat, verts=8):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=h)
    ob = obj_from_bm(name, bm, mat, collection='Cockpit'); ob.location = loc_b; ob.rotation_euler = rot; return ob

def face_hit(face, cam, u, v):
    r = Vector(cam.ray(u, v)); t = 1.0
    for _ in range(8): p = r * t; t = face.z(p.x, p.y) / r.z
    return r * t

def basis(face, p):
    n = face.normal(p.x, p.y)                    # oyun uzayında pilota bakan normal
    right = Vector((1, 0, 0)); right = (right - n * right.dot(n)).normalized(); up = n.cross(right)
    return right, up, n

def orient(right, up, n):
    # Blender uzayına çevrilmiş dönüş matrisi (yerel X=sağ, Y=yukarı, Z=normal  → oyun uzayı → Blender)
    cols = [g2b(right), g2b(up), g2b(n)]
    M = Matrix(((cols[0].x, cols[1].x, cols[2].x), (cols[0].y, cols[1].y, cols[2].y), (cols[0].z, cols[1].z, cols[2].z))); return M

def build(a, P, mats):
    cam = Cam(a); face = Face(a, P); out = []; D = P['detail']
    cy = materials.emission('M_cyan', (0.15, 0.85, 1.0), D['cyan_strength'])
    # --- cıvatalar: ekran muhafazalarının dış çerçevesi boyunca
    for s in a['screens']:
        Pn = [Vector(p) for p in s['corners3d']]; n = Vector(s['normal'])
        front = [p * (1 - P['bezel_depth'] / p.length) for p in Pn]; cf = sum(front, Vector()) / 4
        outer = []
        for q in front:
            d = q - cf; d -= n * d.dot(n); d.normalize(); outer.append(q + d * P['bezel_w'])
        mid = [(outer[i] + front[i]) * 0.5 for i in range(4)]    # bezel yüzünün ortası (cıvata hattı)
        for i in range(4):
            A, B = mid[i], mid[(i + 1) % 4]; L = (B - A).length; k = max(2, int(L / D['bolt_gap']))
            for j in range(k + 1):
                p = A + (B - A) * (j / k)
                if (i in (0, 2)) and j in (0, k): continue
                out.append(cyl('Detail_bolt', D['bolt_r'], D['bolt_h'], g2b(p + n * 0.002), orient(*(lambda nn: (Vector((1, 0, 0)), nn.cross(Vector((1, 0, 0))), nn))(n)).to_euler(), mats['aluminum'], 6))
    # --- cyan şeritler (kısık): panel lambaları
    for (u0, u1, v) in D['strips']:
        p0 = face_hit(face, cam, u0, v); p1 = face_hit(face, cam, u1, v); c = (p0 + p1) * 0.5; right, up, n = basis(face, c)
        L = (p1 - p0).length
        out.append(box('Detail_strip', (L, D['strip_h'], 0.004), g2b(c + n * 0.004), cy, rot=orient(right, up, n).to_euler(), bev=0.001))
    # --- orta alt havalandırma ızgarası
    vx = D['vent']; c = face_hit(face, cam, vx['u'], vx['v']); right, up, n = basis(face, c); R = orient(right, up, n)
    out.append(box('Detail_vent_frame', (vx['w'], vx['h'], 0.018), g2b(c + n * 0.006), mats['steel'], rot=R.to_euler(), bev=0.004))
    out.append(box('Detail_vent_back', (vx['w'] - 0.03, vx['h'] - 0.03, 0.004), g2b(c + n * 0.016), mats['composite'], rot=R.to_euler(), bev=0.0))
    for k in range(vx['slats']):
        t = (k + 0.5) / vx['slats'] - 0.5
        pos = c + up * (t * (vx['h'] - 0.05)) + n * 0.022
        out.append(box('Detail_slat', (vx['w'] - 0.05, 0.006, 0.01), g2b(pos), mats['steel'], rot=R.to_euler(), bev=0.0015))
    # --- dikme kelepçeleri: pencerelerin arasında kalan dikme şeridinin ortasında; genişlik şeride göre (camı kapatmaz)
    from .canopy import hit_ellipsoid
    def xs_at(poly, v):
        r = []
        for k in range(len(poly)):
            (x1, y1), (x2, y2) = poly[k], poly[(k + 1) % len(poly)]
            if (y1 - v) * (y2 - v) < 0: r.append(x1 + (x2 - x1) * (v - y1) / (y2 - y1))
        return r
    W = a['windows']
    for (wa, wb, vs) in D['clamps']:
        for v in vs:
            xa = xs_at(W[wa]['poly'], v); xb = xs_at(W[wb]['poly'], v)
            if not xa or not xb: continue
            left, right = (max(xa), min(xb)) if W[wa]['cx'] < W[wb]['cx'] else (max(xb), min(xa))
            gap = right - left
            if gap < 14: continue
            u = (left + right) / 2; r = Vector(cam.ray(u, v))
            p = hit_ellipsoid(r, tuple(P['ell_c']), P['ell_axes']); dist = p.length; p = p * (1 - 0.052 / dist)
            gap_m = gap / cam.f * dist; w = min(0.07, gap_m * 0.55)
            nrm = -r; right_v = Vector((0, 1, 0)).cross(nrm).normalized(); upv = nrm.cross(right_v); R2 = orient(right_v, upv, nrm)
            out.append(box('Detail_clamp', (w, 0.02, 0.016), g2b(p), mats['titanium'], rot=R2.to_euler(), bev=0.003))
            for sx in (-1, 1): out.append(cyl('Detail_pin', 0.0045, 0.008, g2b(p + right_v * sx * w * 0.32), R2.to_euler(), mats['aluminum'], 6))
    return out
