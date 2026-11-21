"""UV (bpy). unique mod: Smart UV + ada paketleme. trim mod (aile içi paylaşımlı atlas) Faz 1+'da eklenecek."""
import bpy, math
import numpy as np


def unwrap_unique(ob, tex_size, margin_px_at_1024=4, name='UVMap', shape='CONCAVE', angle=66):
    me = ob.data
    while len(me.uv_layers) > 0:
        me.uv_layers.remove(me.uv_layers[0])
    me.uv_layers.new(name=name)
    margin = margin_px_at_1024 / 1024.0      # STANDARDS §5: 1024²'de ≥ 4 px (oran sabit; hızlı modda 512² → 2 px)
    vl = bpy.context.view_layer
    for o in vl.objects:
        o.select_set(False)
    ob.select_set(True)
    vl.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(angle), island_margin=margin, area_weight=0.0, scale_to_bounds=False)
    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.average_islands_scale()
    bpy.ops.uv.pack_islands(rotate=True, rotate_method='ANY', shape_method=shape, margin_method='FRACTION', margin=margin)
    bpy.ops.object.mode_set(mode='OBJECT')


def stats(ob, tex_size):
    """Texel yoğunluğu (px/m, alan ağırlıklı medyan ve 5-95 yüzdelik), UV doluluk oranı, 0..1 dışı."""
    me = ob.data
    uv = me.uv_layers.active.data
    M = ob.matrix_world
    dens, areas, uv_area, oob = [], [], 0.0, 0
    for p in me.polygons:
        a3 = p.area * (M.to_3x3().determinant() ** (2 / 3))
        pts = [uv[i].uv for i in p.loop_indices]
        a2 = 0.0
        for k in range(1, len(pts) - 1):
            a2 += abs((pts[k].x - pts[0].x) * (pts[k + 1].y - pts[0].y) - (pts[k + 1].x - pts[0].x) * (pts[k].y - pts[0].y)) / 2
        uv_area += a2
        if any(q.x < -1e-4 or q.x > 1 + 1e-4 or q.y < -1e-4 or q.y > 1 + 1e-4 for q in pts):
            oob += 1
        if a3 > 1e-9:
            dens.append(math.sqrt(a2 / a3) * tex_size)
            areas.append(a3)
    d, w = np.array(dens), np.array(areas)
    o = np.argsort(d)
    cw = np.cumsum(w[o]) / w.sum()
    pct = lambda q: float(d[o][np.searchsorted(cw, q)])
    return {'texel_px_per_m_median': round(pct(0.5), 1), 'texel_p05': round(pct(0.05), 1), 'texel_p95': round(pct(0.95), 1),
            'uv_fill': round(uv_area, 3), 'faces_out_of_bounds': oob}
