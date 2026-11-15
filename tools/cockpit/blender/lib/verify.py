"""Doğrulama: (1) cam açıklıklarının önü/arkası boş mu (göz→cam ışın testi), (2) ekran köşeleri CKP'ye izdüşüm hatası."""
import bpy, random
from mathutils import Vector
from .common import *

def window_clear(a, samples=900, inset_px=3.0):
    cam = Cam(a); dg = bpy.context.evaluated_depsgraph_get(); sc = bpy.context.scene; rnd = random.Random(5)
    blocked = {}; tot = 0; bad = 0
    from .canopy import point_in_poly
    for w in a['windows']:
        poly = [tuple(p) for p in w['poly']]; xs = [p[0] for p in poly if -300 < p[0] < 1900]; ys = [p[1] for p in poly if p[1] > -300]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys); n = 0
        while n < samples:
            u, v = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            if not point_in_poly((u, v), poly): continue
            # kenara yakın örnekleri ele (piksel payı): 4 komşuyu da içeride iste
            if not all(point_in_poly((u + du, v + dv), poly) for du, dv in ((inset_px, 0), (-inset_px, 0), (0, inset_px), (0, -inset_px))): continue
            n += 1; tot += 1
            d = g2b(cam.ray(u, v)); hit, loc, nor, idx, ob, mat = sc.ray_cast(dg, Vector((0, 0, 0)), d)
            if hit:
                bad += 1; blocked[ob.name] = blocked.get(ob.name, 0) + 1; print('  engel', ob.name, round(u), round(v), round(loc.length, 3))
    return tot, bad, blocked

def screen_fit(a):
    cam = Cam(a); worst = 0.0; res = {}
    for s in a['screens']:
        ob = bpy.data.objects.get(s['name'])
        if not ob: res[s['name']] = None; continue
        errs = []
        for co, q in zip(ob.data.vertices, s['ckp']):
            p = ob.matrix_world @ co.co; g = Vector((p.x, p.z, -p.y)); u, v = cam.proj(g); errs.append(((u - q[0]) ** 2 + (v - q[1]) ** 2) ** 0.5)
        res[s['name']] = round(max(errs), 3); worst = max(worst, max(errs))
    return worst, res


def screen_clear(a, samples=200):
    """Ekran önünde engel var mı: göz→ekran noktası ışınında, ekran yüzeyinden DAHA YAKIN bir geometri (koltuk, bezel dışı parça) bulunmamalı."""
    import random
    from mathutils import geometry
    cam = Cam(a); dg = bpy.context.evaluated_depsgraph_get(); sc = bpy.context.scene; rnd = random.Random(9); bad = {}; tot = 0
    for s in a['screens']:
        q = s['ckp']; so = bpy.data.objects[s['name']]; vs = [so.matrix_world @ v.co for v in so.data.vertices]
        for _ in range(samples):
            u1, v1 = rnd.uniform(0.04, 0.96), rnd.uniform(0.04, 0.96)
            top = (q[0][0] + (q[1][0] - q[0][0]) * u1, q[0][1] + (q[1][1] - q[0][1]) * u1); bot = (q[3][0] + (q[2][0] - q[3][0]) * u1, q[3][1] + (q[2][1] - q[3][1]) * u1)
            u, v = top[0] + (bot[0] - top[0]) * v1, top[1] + (bot[1] - top[1]) * v1; tot += 1
            d = g2b(cam.ray(u, v)); dscr = None
            for tri in ((0, 1, 2), (0, 2, 3)):
                x = geometry.intersect_ray_tri(vs[tri[0]], vs[tri[1]], vs[tri[2]], d, Vector((0, 0, 0)))
                if x is not None: dscr = x.length
            if dscr is None: continue
            hit, loc, nor, idx, ob, mat = sc.ray_cast(dg, Vector((0, 0, 0)), d)
            if hit and not ob.name.startswith('SCR_') and loc.length < dscr - 0.004 and ob.name.startswith(('Seat', 'Detail', 'Dash_Plate', 'Dash_Ped', 'Bezel_')): bad[ob.name] = bad.get(ob.name, 0) + 1
    return tot, sum(bad.values()), bad
