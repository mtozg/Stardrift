"""Neon yüzey oturma kontrolü (Blender aşaması): detail_neon'un her bağlı parçası için, gözden parçanın ağırlık merkezine ışın atılır;
 - ilk çarpan neon değilse parça GİZLİ (başka yüzeyin içinde/arkasında),
 - neonun arkasındaki ilk yüzeye mesafe > tol ise parça HAVADA (yüzeyden kopuk).
Kullanım: python qc/neon_check.py <model.blend> [tol_m=0.012]   → RESULT {...}; sorun varsa çıkış kodu 1"""
import sys, json, collections
import bpy
from mathutils import Vector

path = sys.argv[1]; tol = float(sys.argv[2]) if len(sys.argv) > 2 else 0.012
bpy.ops.wm.open_mainfile(filepath=path)
ob = bpy.data.objects.get('detail_neon')
dg = bpy.context.evaluated_depsgraph_get(); sc = bpy.context.scene
me = ob.data
par = list(range(len(me.vertices)))
def f(x):
    while par[x] != x:
        par[x] = par[par[x]]; x = par[x]
    return x
for e in me.edges: par[f(e.vertices[0])] = f(e.vertices[1])
comp = collections.defaultdict(list)
for v in me.vertices: comp[f(v.index)].append(v.index)
F = 435.27
cid = {}
for k, vs in comp.items():
    for i in vs: cid[i] = k
stat = collections.defaultdict(lambda: {'n': 0, 'gizli': 0, 'havada': 0, 'maxgap': 0.0, 'ornek': None, 'ust': None})
for p in me.polygons:
    ws = [ob.matrix_world @ me.vertices[i].co for i in p.vertices]
    c = sum(ws, Vector()) / len(ws)
    d = c.normalized()
    st = stat[cid[p.vertices[0]]]
    st['n'] += 1
    if st['ornek'] is None: st['ornek'] = [round(800 + F * c.x / c.y), round(239.5 - F * c.z / c.y)]
    hit, loc, nrm, idx, h, mw = sc.ray_cast(dg, Vector((0, 0, 0)), d)
    if not hit or h.name != 'detail_neon':
        st['gizli'] += 1; st['ust'] = h.name if hit else 'yok'; continue
    hit2, loc2, _, _, h2, _ = sc.ray_cast(dg, loc + d * 0.0005, d)
    gap = (loc2 - loc).length if hit2 else 9.9
    st['maxgap'] = max(st['maxgap'], gap)
    if gap > tol: st['havada'] += 1
bad = []; n = len(stat)
for k, st in stat.items():
    if st['gizli'] > st['n'] * 0.5 or st['havada'] > st['n'] * 0.34:
        bad.append({'piksel': st['ornek'], 'yuzey': st['n'], 'gizli': st['gizli'], 'ustte': st['ust'], 'havada': st['havada'], 'en_buyuk_bosluk_mm': round(st['maxgap'] * 1000, 1)})
print('RESULT', json.dumps({'parca': n, 'sorunlu': len(bad), 'tol_mm': tol * 1000, 'liste': bad[:40]}, ensure_ascii=False))
sys.exit(1 if bad else 0)
