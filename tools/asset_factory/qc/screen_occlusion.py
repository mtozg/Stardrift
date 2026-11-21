"""Blender aşaması kontrolü: ekran dörtgenlerinin pilot gözünden örtülüp örtülmediği (ışın testi).
Her SCR_* içinde 9x5 örnek nokta için gözden ışın atılır; ilk çarpan nesne ekranın kendisi değilse 'örten' sayılır.
Kullanım: python qc/screen_occlusion.py <model.blend> [--no-fail]   → çıktı: RESULT {...}; örten varsa çıkış kodu 1"""
import sys, json
import bpy
from mathutils import Vector

path = [a for a in sys.argv[1:] if not a.startswith('--')][0]
bpy.ops.wm.open_mainfile(filepath=path)
dg = bpy.context.evaluated_depsgraph_get(); sc = bpy.context.scene
res = {}; bad = 0
for name in ('SCR_SYS', 'SCR_RADAR', 'SCR_HULL'):
    ob = bpy.data.objects.get(name)
    if not ob:
        res[name] = 'yok'; bad += 1; continue
    v = [ob.matrix_world @ x.co for x in ob.data.vertices][:4]
    occ = {}
    n = 0
    for i in range(9):
        for j in range(5):
            a, b = (i + 0.5) / 9, (j + 0.5) / 5
            p = (v[0] * (1 - a) + v[1] * a) * (1 - b) + (v[3] * (1 - a) + v[2] * a) * b      # köşe sırası TL,TR,BR,BL
            hit, loc, nrm, idx, h, mw = sc.ray_cast(dg, Vector((0, 0, 0)), p.normalized())
            n += 1
            if hit and h.name != name:
                occ[h.name] = occ.get(h.name, 0) + 1
    res[name] = {'ornek': n, 'orten': occ}
    bad += sum(occ.values())
print('RESULT', json.dumps({'orten_toplam': bad, 'ekranlar': res}, ensure_ascii=False))
sys.exit(1 if bad and '--no-fail' not in sys.argv else 0)
