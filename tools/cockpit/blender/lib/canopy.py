"""Ön cam kabuğu: elipsoid kanopi yüzeyi, onaylı çizimdeki cam açıklıkları kadar delinir (açıklıklar boş kalır).
Pencere kenarlarında kalınlıklı takviye halkaları (flanş) oluşur; dikmeler pencereler arasında kalan kabuk şeritleridir."""
import bpy, bmesh, math
from mathutils import Vector
from .common import *

def hit_ellipsoid(r, c, ax):
    """Gözden (orijin) çıkan r ışınının elipsoidi ilk (içeriden) kesişimi."""
    a = sum((r[i] / ax[i]) ** 2 for i in range(3)); b = -2 * sum(r[i] * c[i] / ax[i] ** 2 for i in range(3)); cc = sum((c[i] / ax[i]) ** 2 for i in range(3)) - 1
    d = b * b - 4 * a * cc; t = (-b + math.sqrt(max(d, 0))) / (2 * a)
    return r * t

def point_in_poly(pt, poly):
    x, y = pt; ins = False; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1: ins = not ins
    return ins

def offset_poly(poly, d):
    """Çokgeni dışa (pencerenin dışına) d piksel genişletir (miter). Görüntü dışına uzatılmış köşeler sabit kalır."""
    n = len(poly); out = []; dirs = []
    for i in range(n):
        p0, p1, p2 = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % n])
        e1 = (p1 - p0); e2 = (p2 - p1)
        if e1.length < 1e-6 or e2.length < 1e-6: dirs.append(Vector((0, 0))); continue
        e1.normalize(); e2.normalize()
        n1 = Vector((e1.y, -e1.x)); n2 = Vector((e2.y, -e2.x)); m = n1 + n2
        if m.length < 1e-6: dirs.append(n1); continue
        m.normalize(); k = 1.0 / max(0.5, m.dot(n1)); dirs.append(m * min(k, 2.0))
    cent = sum((Vector(p) for p in poly), Vector((0, 0))) / n
    # içe bakan yönü bul: ilk anlamlı köşe için test
    flip = 1
    for i in range(n):
        if dirs[i].length > 0 and abs(poly[i][0]) < 300 and poly[i][1] > -300:
            test = (poly[i][0] + dirs[i].x * 3, poly[i][1] + dirs[i].y * 3)
            flip = -1 if point_in_poly(test, poly) else 1; break
    for i in range(n):
        p = Vector(poly[i]); fixed = abs(p.x) > 300 and (p.x < 0 or p.x > 1900) or p.y < -300
        if fixed:   # görüntü dışına uzatılmış köşe: kesici ile halka aynı düzlemi paylaşmasın diye d ile orantılı dışa kaydır
            sx = -1 if p.x < -300 else (1 if p.x > 1900 else 0); sy = -1 if p.y < -300 else 0
            out.append((p.x + sx * d * 1.5, p.y + sy * d * 1.5))
        else: out.append((p.x + dirs[i].x * d * flip, p.y + dirs[i].y * d * flip))
    return out

def prism(name, poly, cam, near=0.30, far=4.0):
    """Gözden çıkan ışınlarla çokgenden bir 'görüş huni' katısı (boolean kesici)."""
    bm = bmesh.new(); vn = []; vf = []
    for (u, v) in poly:
        r = g2b(cam.ray(u, v)); vn.append(bm.verts.new(r * near)); vf.append(bm.verts.new(r * far))
    n = len(poly)
    for i in range(n): bm.faces.new((vn[i], vn[(i + 1) % n], vf[(i + 1) % n], vf[i]))
    fn = bm.faces.new(vn); ff = bm.faces.new(vf[::-1])
    bmesh.ops.triangulate(bm, faces=[fn, ff], quad_method='BEAUTY', ngon_method='EAR_CLIP')
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    ob = obj_from_bm(name, bm, collection='_work'); return ob

def shell_bm(cam, P, offset=0.0, step=32, thk=0.045):
    """Elipsoid yüzeyinin 1600x656 görüntü uzayındaki ızgarasından kapalı katı (radyal kalınlık)."""
    c = (P['ell_c'][0], P['ell_c'][1], P['ell_c'][2]); ax = P['ell_axes']
    us = list(range(-360, 1961, step)); vs = list(range(-360, 761, step))
    bm = bmesh.new(); grid = []
    for v in vs:
        row = []
        for u in us:
            p = hit_ellipsoid(Vector(cam.ray(u, v)), c, ax); d = p.length
            p = p * (1 + offset / d); row.append(bm.verts.new(g2b(p)))
        grid.append(row)
    for j in range(len(vs) - 1):
        for i in range(len(us) - 1): bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    solidify_radial(bm, thk); return bm

def build(a, P, mats):
    cam = Cam(a); objs = []
    shell = obj_from_bm('Canopy_Shell', shell_bm(cam, P, 0.0, thk=P['shell_thk']), mats['gunmetal'], smooth=True)
    flange_src = shell_bm(cam, P, -(P['flange_thk'] + 0.012), thk=P['flange_thk'])
    flange_all = obj_from_bm('_flange_src', flange_src, mats['steel'], collection='_work')
    rings = []
    polys = [tuple(map(tuple, w['poly'])) for w in a['windows']]

    def samples(poly, step=8.0):
        out = []; n = len(poly)
        for i in range(n):
            A, B = Vector(poly[i]), Vector(poly[(i + 1) % n]); L = (B - A).length; c = max(1, int(L / step))
            out += [tuple(A + (B - A) * (t / c)) for t in range(c)]
        return out

    def safe_offset(k):
        """Flanş genişliği: komşu pencerenin açıklığına (3 px payla) girmeyecek en büyük değer."""
        for d in [P['flange_w_px'] - 2 * i for i in range(0, 8)]:
            if d < 5: break
            po = offset_poly(list(polys[k]), d); smp = samples(po)
            bad = any(point_in_poly(q, [(x, y) for x, y in polys[j]]) for q in smp for j in range(len(polys)) if j != k)
            for j in range(len(polys)):
                if j == k or bad: continue
                bad = any(point_in_poly(q, po) for q in samples(polys[j]) if -300 < q[0] < 1900 and q[1] > -300)
            if not bad: return max(4.0, d - 3.0)
        return 4.0

    cuts = [prism('_cut%d' % k, offset_poly(list(pl), 1.2), cam, near=0.30 + 0.0031 * k, far=4.0 + 0.0137 * k) for k, pl in enumerate(polys)]
    for k, pl in enumerate(polys):
        d = safe_offset(k); print('  flanş', k, 'genişlik px', d)
        big = prism('_big%d' % k, offset_poly(list(pl), d), cam, near=0.30 + 0.0017 * k, far=4.0 + 0.0071 * k)
        boolean(shell, cuts[k])
        hollow = big; boolean(hollow, cuts[k])
        ring = flange_all.copy(); ring.data = flange_all.data.copy(); ring.name = 'Canopy_Flange%d' % k; coll('Cockpit').objects.link(ring)
        boolean(ring, hollow, 'INTERSECT'); rings.append(ring)
        bpy.data.objects.remove(hollow, do_unlink=True)
    for c in cuts: bpy.data.objects.remove(c, do_unlink=True)
    bpy.data.objects.remove(flange_all, do_unlink=True)
    bevel(shell, P['bevel'], 2, 35)
    for r in rings: bevel(r, P['bevel'] * 0.8, 2, 35)
    return [shell] + rings


def build_panels(a, P, mats):
    """Yan ve alt paneller: kanopi yüzeyine oturan, aralarında panel derzi bırakan kalınlıklı plakalar (görüntü uzayında çokgenlerle tanımlı)."""
    cam = Cam(a); out = []
    srcs = {}
    for k, pl in enumerate(P.get('panels', [])):
        off = pl.get('offset', 0.03); thk = pl.get('thk', 0.03); key = (off, thk)
        if key not in srcs:
            srcs[key] = obj_from_bm('_psrc%d' % len(srcs), shell_bm(cam, P, -(off + thk), thk=thk), None, collection='_work')
        ob = srcs[key].copy(); ob.data = srcs[key].data.copy(); ob.name = 'Canopy_Panel_%s' % pl.get('name', k); coll('Cockpit').objects.link(ob)
        ob.data.materials.clear(); ob.data.materials.append(mats[pl.get('mat', 'steel')])
        cut = prism('_pc%d' % k, [tuple(p) for p in pl['poly']], cam)
        boolean(ob, cut, 'INTERSECT'); bpy.data.objects.remove(cut, do_unlink=True)
        bevel(ob, pl.get('bevel', 0.005), 2, 35); out.append(ob)
    for o in srcs.values(): bpy.data.objects.remove(o, do_unlink=True)
    return out
