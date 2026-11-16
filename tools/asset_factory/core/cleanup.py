"""Temizlik (bpy): rol bazında birleştirme, çakışık köşe kaynağı, dışarıdan hiç görünmeyen yüzlerin silinmesi.

Kaşif kokpitindeki gizli yüz silme gözü orijinde varsayıyordu (iç mekân). Burada aileye göre iki mod var:
  exterior — 26 yönden (+ yüz başına birkaç örnek noktadan) dışarı ışın; hiçbiri kaçamıyorsa yüz gizlidir.
  interior — verilen göz noktalarından görünürlük (iç mekân / kokpit; ileride)."""
import bpy, bmesh, itertools
from mathutils import Vector
from mathutils.bvhtree import BVHTree

DIRS = [Vector(d).normalized() for d in itertools.product((-1, 0, 1), repeat=3) if any(d)]


def join_role(objs, name):
    objs = [o for o in objs if o.type == 'MESH']
    if not objs:
        return None
    with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs, selected_objects=objs):
        bpy.ops.object.join()
    ob = objs[0]
    ob.name = name
    ob.data.name = name
    return ob


def weld(ob, dist=1e-5):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    n0 = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context='VERTS')
    degen = [f for f in bm.faces if f.calc_area() < 1e-10]
    bmesh.ops.delete(bm, geom=degen, context='FACES')
    bm.to_mesh(ob.data)
    removed = n0 - len(bm.verts)
    bm.free()
    ob.data.update()
    return removed


def _bvh(objs):
    verts, polys, off = [], [], 0
    for o in objs:
        M = o.matrix_world
        verts += [M @ v.co for v in o.data.vertices]
        polys += [[i + off for i in p.vertices] for p in o.data.polygons]
        off += len(o.data.vertices)
    return BVHTree.FromPolygons(verts, polys, epsilon=0.0)


def cull_hidden_exterior(target, occluders, far=1e3, eps=2e-4):
    """target içindeki dışarıdan görünmeyen yüzleri sil. occluders: tıkayan tüm nesneler (target dahil)."""
    tree = _bvh(occluders)
    M = target.matrix_world
    bm = bmesh.new()
    bm.from_mesh(target.data)
    bm.normal_update()
    kill = []
    for f in bm.faces:
        c = M @ f.calc_center_median()
        n = (M.to_3x3() @ f.normal).normalized()
        pts = [c] + [M @ (v.co * 0.8 + f.calc_center_median() * 0.2) for v in f.verts]
        visible = False
        for p in pts:
            o = p + n * eps
            for d in DIRS:
                if d.dot(n) <= 0.05:
                    continue
                hit = tree.ray_cast(o, d, far)
                if hit[0] is None:
                    visible = True
                    break
            if visible:
                break
        if not visible:
            kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bm.to_mesh(target.data)
    bm.free()
    target.data.update()
    return len(kill)


def cull_hidden_interior(target, occluders, eyes, eps=2e-4):
    """İç mekân (kokpit): yüz, verilen göz noktalarından (pilotun baş hareket aralığı) hiçbirinden görünmüyorsa silinir.
    Görünür = yüz göze dönük VE yüz noktasından göze giden ışın engelsiz (merkez + 4 iç nokta)."""
    tree = _bvh(occluders)
    M = target.matrix_world
    bm = bmesh.new()
    bm.from_mesh(target.data)
    bm.normal_update()
    E = [Vector(e) for e in eyes]
    kill = []
    for f in bm.faces:
        cl = f.calc_center_median()
        n = (M.to_3x3() @ f.normal).normalized()
        pts = [M @ cl] + [M @ (v.co * 0.8 + cl * 0.2) for v in f.verts]
        vis = False
        for p in pts:
            o = p + n * eps
            for e in E:
                d = e - o
                L = d.length
                if L < 1e-6 or d.dot(n) <= 0:
                    continue
                hit = tree.ray_cast(o, d / L, L - 1e-3)
                if hit[0] is None:
                    vis = True
                    break
            if vis:
                break
        if not vis:
            kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bm.to_mesh(target.data)
    bm.free()
    target.data.update()
    return len(kill)
