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
