"""Yan panel karakteri: kademeli yükseltilmiş plakalar, panjurlu havalandırmalar, kablo/hortum hatları ve pencere flanşı cıvataları."""
import bpy, bmesh, math
from mathutils import Vector, Matrix
from .common import *
from .canopy import hit_ellipsoid, offset_poly, point_in_poly, prism
from .detail import cyl, orient
from .dash_detail import louver

def ell_normal(p, P):
    c = P['ell_c']; ax = P['ell_axes']; g = Vector(((p.x - c[0]) / ax[0] ** 2, (p.y - c[1]) / ax[1] ** 2, (p.z - c[2]) / ax[2] ** 2)); g.normalize(); return -g   # içe (göze) bakan

def surf(cam, P, u, v, off):
    r = Vector(cam.ray(u, v)); p = hit_ellipsoid(r, tuple(P['ell_c']), P['ell_axes']); return p * (1 - off / p.length)

def tube(name, pts, r, mat, sides=6):
    """Noktalar boyunca düzgün hortum/boru (bmesh süpürme)."""
    bm = bmesh.new(); rings = []; n = len(pts)
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized(); ref = Vector((0, 1, 0)) if abs(t.y) < 0.9 else Vector((1, 0, 0))
        a = t.cross(ref).normalized(); b = t.cross(a).normalized(); ring = []
        for k in range(sides): ang = 2 * math.pi * k / sides; ring.append(bm.verts.new(g2b(p + (a * math.cos(ang) + b * math.sin(ang)) * r)))
        rings.append(ring)
    for i in range(n - 1):
        for k in range(sides): bm.faces.new((rings[i][k], rings[i][(k + 1) % sides], rings[i + 1][(k + 1) % sides], rings[i + 1][k]))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    ob = obj_from_bm(name, bm, mat, collection='Cockpit', smooth=True); return ob

def build(a, P, mats):
    cam = Cam(a); out = []; S = P['side']
    # --- panjurlu havalandırmalar (yan panellerin üstünde)
    for k, (u, v, w, h, sl) in enumerate(S['vents']):
        for mir in (False, True):
            uu = 1600 - u if mir else u; c = surf(cam, P, uu, v, S['vent_off']); n = ell_normal(c, P)
            right = Vector((1, 0, 0)); right = (right - n * right.dot(n)).normalized(); up = n.cross(right)
            out += louver('Side_vent%d%s' % (k, 'R' if mir else 'L'), c, right, up, n, w, h, sl, mats)
    # --- kablo/hortum hatları
    for k, line in enumerate(S['conduits']):
        for mir in (False, True):
            pts = [surf(cam, P, (1600 - u) if mir else u, v, S['conduit_off']) for (u, v) in line]
            out.append(tube('Side_conduit%d%s' % (k, 'R' if mir else 'L'), pts, S['conduit_r'], mats['composite']))
            # hat boyunca kelepçeler
            for t in range(1, len(pts) - 1):
                p = pts[t]; n = ell_normal(p, P); right = Vector((1, 0, 0)); right = (right - n * right.dot(n)).normalized(); up = n.cross(right)
                out.append(cyl('Side_clip', S['conduit_r'] * 1.9, 0.014, g2b(p), orient(right, up, n).to_euler(), mats['aluminum'], 8))
    # --- pencere flanşı cıvataları: flanş halkasının ortasında, cam açıklığına taşmadan
    polys = [[tuple(p) for p in w['poly']] for w in a['windows']]
    for k, poly in enumerate(polys):
        ring = offset_poly(poly, P['flange_w_px'] * 0.55); n_ = len(ring)
        for i in range(n_):
            A, B = Vector(ring[i]), Vector(ring[(i + 1) % n_]); L = (B - A).length
            if L < 20: continue
            cnt = max(1, int(L / S['rivet_px']))
            for j in range(cnt):
                q = A + (B - A) * ((j + 0.5) / cnt); u, v = q.x, q.y
                if v < -200 or u < -20 or u > 1620: continue
                if any(point_in_poly((u, v), pp) for pp in polys): continue     # başka bir pencerenin açıklığına düşmesin
                c = surf(cam, P, u, v, P['flange_thk'] + 0.016); n = ell_normal(c, P)
                right = Vector((1, 0, 0)); right = (right - n * right.dot(n)).normalized(); up = n.cross(right)
                out.append(cyl('Side_rivet', 0.0042, 0.006, g2b(c), orient(right, up, n).to_euler(), mats['aluminum'], 6))
    return out
