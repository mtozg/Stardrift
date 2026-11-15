"""Dashboard'u kase görünümünden çıkaran fiziksel ayrıntılar: yükseltilmiş panel plakaları (derzli), orta konsol kütlesi, havalandırma,
braketler ve bezel bağlantı blokları. Hepsi gerçek kalınlık/pahlı geometri; camların önüne geçmez (sırtın altında)."""
import bpy, bmesh, math
from mathutils import Vector, Matrix
from .common import *
from .dash import Face
from .detail import box, cyl, orient, basis, face_hit

def plate(name, face, P, x0, x1, s0, s1, raise_, mat, nx=8, ns=4, gap=0.005, bev=0.004):
    x0 += gap * 0.5; x1 -= gap * 0.5
    bm = bmesh.new(); grid = []
    for i in range(nx + 1):
        x = x0 + (x1 - x0) * i / nx; yr = face.ridge_y(x); col = []
        for j in range(ns + 1):
            s = s0 + (s1 - s0) * j / ns; y = yr - s; z = face.z(x, y) + P['fascia_curl'] * max(0.0, s - 0.55) ** 2
            p = Vector((x, y, z)); p = p * (1 + (P['dash_back'] - raise_) / p.length); col.append(bm.verts.new(g2b(p)))
        grid.append(col)
    for i in range(nx):
        for j in range(ns): bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    solidify_radial(bm, raise_ + 0.03)
    ob = obj_from_bm(name, bm, mat, collection='Cockpit'); bevel(ob, bev, 2, 30); return ob

def louver(name, c, right, up, n, w, h, slats, mats, tilt=0.45):
    """Çerçeveli, eğik panjurlu havalandırma. c: oyun uzayında merkez; right/up/n: yerel taban (n pilota bakar)."""
    R = orient(right, up, n); out = []
    out.append(box(name + '_frame', (w, h, 0.016), g2b(c + n * 0.004), mats['steel'], rot=R.to_euler(), bev=0.004))
    out.append(box(name + '_back', (w - 0.026, h - 0.026, 0.004), g2b(c + n * 0.013), mats['composite'], rot=R.to_euler(), bev=0.0))
    for k in range(slats):
        t = (k + 0.5) / slats - 0.5; pos = c + up * (t * (h - 0.04)) + n * 0.018
        Rm = R @ Matrix.Rotation(tilt, 3, 'X')
        out.append(box(name + '_slat', (w - 0.04, 0.0065, 0.014), g2b(pos), mats['titanium'], rot=Rm.to_euler(), bev=0.0015))
    return out

def gusset(name, corner, da, db, n, size, thk, mat):
    """Köşe braketi: üçgen plaka (da, db: düzlem içi iki doğrultu)."""
    bm = bmesh.new(); pts = [corner, corner + da * size, corner + db * size]
    lo = [bm.verts.new(g2b(p)) for p in pts]; hi = [bm.verts.new(g2b(p + n * thk)) for p in pts]
    bm.faces.new(lo[::-1]); bm.faces.new(hi)
    for i in range(3): j = (i + 1) % 3; bm.faces.new((lo[j], lo[i], hi[i], hi[j]))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    ob = obj_from_bm(name, bm, mat, collection='Cockpit'); bevel(ob, 0.002, 1, 40); return ob

def build(a, P, mats):
    face = Face(a, P); cam = Cam(a); out = []; D = P['dash_detail']
    cm = [mats[k] for k in ('gunmetal', 'steel', 'titanium', 'aluminum')]
    # --- panel plakaları (derzli, farklı malzeme ve yükseklik)
    for k, pl in enumerate(D['plates']):
        out.append(plate('Dash_Plate_%d' % k, face, P, pl['x'][0], pl['x'][1], pl['s'][0], pl['s'][1], pl['raise'], mats[pl['mat']], pl.get('nx', 8), pl.get('ns', 4), bev=pl.get('bev', 0.004)))
    # --- orta konsol kütlesi + havalandırma
    pd = D['pedestal']; out.append(plate('Dash_Pedestal', face, P, pd['x'][0], pd['x'][1], pd['s'][0], pd['s'][1], pd['raise'], mats['steel'], 12, 6, bev=0.014))
    yc = face.ridge_y(0) - (pd['s'][0] + pd['s'][1]) * 0.5; c = Vector((0, yc, face.z(0, yc))); c = c * (1 - (pd['raise'] - P['dash_back']) / c.length)
    right, up, n = basis(face, c)
    out += louver('Dash_vent', c + up * D['vent_dy'], right, up, n, D['vent_w'], D['vent_h'], D['vent_slats'], mats)
    # --- bezel köşe braketleri + bezel arası bağlantı blokları
    for s in a['screens']:
        Pn = [Vector(p) for p in s['corners3d']]; n_ = Vector(s['normal']); front = [p * (1 - P['bezel_depth'] / p.length) for p in Pn]
        cf = sum(front, Vector()) / 4; outer = []
        for q in front:
            d = q - cf; d -= n_ * d.dot(n_); d.normalize(); outer.append(q + d * P['bezel_w'])
        rt = (front[1] - front[0]).normalized(); upv = (front[0] - front[3]).normalized()
        for idx, (sx, sy) in ((2, (-1, 1)), (3, (1, 1))):        # alt köşeler: braket aşağı ve dışa
            out.append(gusset('Dash_gusset', outer[idx] + n_ * 0.002, rt * (sx * 0.9) , upv * (sy * 0.9), n_, 0.075, 0.013, mats['titanium']))
    sc = a['screens']
    for (i0, i1) in ((0, 1), (1, 2)):          # sol/orta ve orta/sağ bezel arası bağlantı
        pa = Vector(sc[i0]['corners3d'][1] if i0 == 0 else sc[i0]['corners3d'][1]); pb = Vector(sc[i1]['corners3d'][0] if i1 == 1 else sc[i1]['corners3d'][0])
    for (ia, ib) in ((0, 1), (1, 2)):
        A = Vector(sc[ia]['corners3d'][1]) if ia < 1 else Vector(sc[ia]['corners3d'][1])
        B = Vector(sc[ib]['corners3d'][0])
        mid = (A + B) * 0.5; nn = Vector(sc[1]['normal']); rt = Vector((1, 0, 0)); up_ = nn.cross(rt).normalized()
        for t in (0.2, 0.8):
            pos = mid + (Vector(sc[ia]['corners3d'][2]) - Vector(sc[ia]['corners3d'][1])) * (t - 0.5) * 0.0 + up_ * (0.0)
        for dy in (-0.02, -0.09, -0.16):
            out.append(box('Dash_joint', (0.075, 0.034, 0.022), g2b(mid * (1 - 0.040 / mid.length) + up_ * dy), mats['titanium'], rot=orient(rt, up_, nn).to_euler(), bev=0.004))
    return out
