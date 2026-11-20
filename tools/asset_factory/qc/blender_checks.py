"""L2 geometri testleri (bpy) — dışa aktarılmış GLB yeniden İÇE aktarılarak (yani gerçekten teslim edilen dosya üzerinde):
sıfır alanlı yüz, gevşek köşe, dışarıdan görünen arka yüz (delik + ters normal), UV çakışması, UV 0..1 dışı, texel yoğunluğu.
Kullanım: python qc/blender_checks.py <glb> <tex_size> <çıktı.json>"""
import os, sys, json, math, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy, bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from PIL import Image, ImageDraw
from core import uv as uvmod

glb, tex_size, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
mode = sys.argv[4] if len(sys.argv) > 4 else 'exterior'      # 'interior': kokpit — testler pilot gözünden
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
lod0 = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('LOD0_')]
body = [o for o in lod0 if o.name.startswith('LOD0_body')][0]
R = {}

# 1) temel hijyen
zero = loose = 0
for o in lod0:
    bm = bmesh.new()
    bm.from_mesh(o.data)
    zero += sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    loose += sum(1 for v in bm.verts if not v.link_faces)
    bm.free()
R['zero_area_faces'] = zero
R['loose_verts'] = loose

if mode == 'interior':
    # 2i) kokpit: pilot gözünden, oyunun kamera çerçevesindeki her ışın (FOV 74°, asal nokta 800/239,5, 1600×656)
    Fp, CXp, CYp = 435.2707, 800.0, 239.5
    allm = [o for o in bpy.data.objects if o.type == 'MESH']
    verts, polys, off = [], [], 0
    for o in allm:
        M = o.matrix_world
        verts += [M @ v.co for v in o.data.vertices]
        polys += [[i + off for i in p.vertices] for p in o.data.polygons]
        off += len(o.data.vertices)
    tree = BVHTree.FromPolygons(verts, polys, epsilon=0.0)
    # glTF içe aktarımı oyun uzayını Blender'a g2b ile çevirir: oyun −Z (ileri) = Blender +Y, göz orijinde
    hits = back = glass = hud = hud_n = 0
    for vv in range(4, 656, 8):
        for uu in range(4, 1600, 8):
            d = Vector(((uu - CXp) / Fp, 1.0, -(vv - CYp) / Fp)).normalized()
            loc, nrm, idx, dist = tree.ray_cast(Vector((0, 0, 0)), d, 50.0)
            inhud = 60 <= vv < 380 and 560 <= uu < 1040
            hud_n += inhud
            if loc is None:
                glass += 1
                continue
            hud += inhud
            hits += 1
            if nrm.dot(d) > 0:
                back += 1
    tot = (656 // 8) * (1600 // 8)
    R['backface_visible'] = round(back / max(hits, 1), 5)
    R['backface_samples'] = hits
    R['backface_points_blender'] = []
    R['glass_ratio'] = round(glass / tot * 100, 1)
    R['hud_zone_block'] = round(hud / max(hud_n, 1) * 100, 1)
    scr = {}
    for nm in ('SCR_SYS', 'SCR_RADAR', 'SCR_HULL'):
        o = bpy.data.objects.get(nm)
        if not o:
            scr[nm] = 0
            continue
        vs = [o.matrix_world @ v.co for v in o.data.vertices]
        c = sum(vs, Vector()) / len(vs)
        ok = 0
        for p in [c] + [c + (v - c) * 0.94 for v in vs]:
            loc, nrm, idx, dist = tree.ray_cast(Vector((0, 0, 0)), p.normalized(), 50.0)
            ok += int(loc is not None and abs(dist - p.length) < 2e-3)
        scr[nm] = ok
    R['screens_visible'] = scr
else:
    # 2) dışarıdan görünen arka yüz: sınır küresinin üstündeki noktalardan merkeze doğru ışın
    verts, polys, off = [], [], 0
    for o in lod0:
        M = o.matrix_world
        verts += [M @ v.co for v in o.data.vertices]
        polys += [[i + off for i in p.vertices] for p in o.data.polygons]
        off += len(o.data.vertices)
    tree = BVHTree.FromPolygons(verts, polys, epsilon=0.0)
    c = sum(verts, Vector()) / len(verts)
    rad = max((v - c).length for v in verts) * 1.5
    rnd = random.Random(3)
    hits = back = 0
    back_pts = []
    for _ in range(20000):
        z = rnd.uniform(-1, 1)
        t = rnd.uniform(0, 2 * math.pi)
        d = Vector((math.sqrt(1 - z * z) * math.cos(t), math.sqrt(1 - z * z) * math.sin(t), z))
        o_ = c + d * rad
        tgt = c + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * rad * 0.5
        dirv = (tgt - o_).normalized()
        loc, nrm, idx, dist = tree.ray_cast(o_, dirv, rad * 3)
        if loc is None:
            continue
        hits += 1
        if nrm.dot(dirv) > 0:
            back += 1
            if len(back_pts) < 12:
                back_pts.append([round(x, 3) for x in loc])
    R['backface_visible'] = round(back / max(hits, 1), 5)
    R['backface_samples'] = hits
    R['backface_points_blender'] = back_pts

# 3) UV: çakışma (raster), sınır dışı, yoğunluk
me = body.data
uvl = me.uv_layers.active.data
me.calc_loop_triangles()
uvarr = np.array([(l.uv.x, 1.0 - l.uv.y) for l in uvl], dtype=np.float64)
tris = np.array([lt.loops[:] for lt in me.loop_triangles], dtype=np.int64)
from qc.uvraster import raster
acc = raster(uvarr, tris, 2048)
cov = (acc > 0).sum()
R['uv_overlap'] = round(float((acc > 1).sum() / max(cov, 1)), 5)
R['uv_coverage'] = round(float(cov / acc.size), 4)
R.update(uvmod.stats(body, tex_size))
json.dump(R, open(out, 'w'), indent=1)
print('RESULT', json.dumps(R))
