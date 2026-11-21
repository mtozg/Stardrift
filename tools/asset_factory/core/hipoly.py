"""Yüksek poligon ayrıntı üretici (bpy/bmesh): düşük poligon gövdeden kabartma panelli hi-poly kopya üretir (normal/AO/eğrilik pişirmek için).
Yöntem: (1) uzun kenarları panel boyuna böl (ızgara), (2) rastgele yüzleri inset+çıkıntı/girinti (panel kabartması), (3) panel kenarlarına pah, (4) panel köşelerine perçin (kısa silindir).
Deterministik (seed). Kaynak nesne dünya dönüşümü birimdir varsayılır."""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix


def make_high(src, panel=0.9, seed=1, relief=(0.012, 0.030), inset=0.045, bevel=0.006, rivet_r=0.024, rivet_h=0.014, rivet_p=0.55, frac=0.6, name='HI'):
    rng = random.Random(seed)
    bm = bmesh.new()
    bm.from_mesh(src.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # 1) ızgara bölme: panel boyundan uzun kenarlar (üst sınır: aşırı bölmeyi önlemek için 24 kesim)
    for _ in range(2):
        groups = {}
        for e in bm.edges:
            L = e.calc_length()
            c = int(L / panel)
            if c >= 1 and any(f.calc_area() > (panel * 0.5) ** 2 for f in e.link_faces):
                groups.setdefault(min(c, 24), []).append(e)
        for c, es in groups.items():
            es = [e for e in es if e.is_valid]
            if es:
                bmesh.ops.subdivide_edges(bm, edges=es, cuts=c, use_grid_fill=True)
    # 2) panel kabartması
    cand = [f for f in bm.faces if f.calc_area() > (panel * 0.22) ** 2 and len(f.verts) in (3, 4, 5)]
    sel = [f for f in cand if rng.random() < frac]
    r = bmesh.ops.inset_individual(bm, faces=sel, thickness=inset, depth=0.0)
    for f in sel:
        if f.is_valid:
            d = rng.uniform(*relief) * (1 if rng.random() < 0.6 else -0.6)
            for v in f.verts:
                v.co += f.normal * d
    # 3) pah: seçili yüzlerin kenarları
    edges = list({e for f in sel if f.is_valid for e in f.edges})
    if bevel > 0 and edges:
        bmesh.ops.bevel(bm, geom=edges, offset=bevel, segments=1, affect='EDGES')
    # 4) perçinler: seçili yüz köşelerinde
    pts = []
    for f in sel:
        if not f.is_valid:
            continue
        n = f.normal.copy()
        for v in f.verts:
            if rng.random() < rivet_p:
                pts.append((v.co + (f.calc_center_median() - v.co) * 0.18, n))
    for p, n in pts:
        M = Matrix.Translation(p + n * rivet_h * 0.5) @ n.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=rivet_r, radius2=rivet_r * 0.8, depth=rivet_h, matrix=M)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    n_tri = sum(len(p.vertices) - 2 for p in me.polygons)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.matrix_world = src.matrix_world.copy()
    from core import geo
    geo.set_smooth_by_angle(ob, 120)      # düşük poligon yumuşak gölgeli: hi-poly de aynı yumuşaklıkta olmalı (yoksa yüz eğimleri normal haritaya 'yama' olarak pişer)
    return ob, n_tri
