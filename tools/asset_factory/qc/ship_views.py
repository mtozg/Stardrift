"""Hazırlanmış gemi (prepared.blend) için konsept-sonrası inceleme görünümleri: lookdev ışık, yakın plan dahil. Kullanım: python qc/ship_views.py <prepare_klasörü> <çıkış_klasörü>"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy
from mathutils import Vector
from core import geo, render as R
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(src, 'prepared.blend'))
for o in list(bpy.data.objects):
    if o.name.startswith('LOD1') or o.type in ('CAMERA', 'LIGHT'):
        if o.type == 'MESH' or o.type in ('CAMERA', 'LIGHT'):
            o.hide_render = True if o.type == 'MESH' else False
            if o.type != 'MESH':
                bpy.data.objects.remove(o)
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and not o.hide_render]
lo, hi = geo.bounds(meshes)
c = (lo + hi) / 2
r = (hi - lo).length / 2
R.rig_lookdev(r)
views = {'on34': (-0.55, -0.75, 0.40), 'arka34': (0.60, 0.70, 0.35), 'yan': (1.0, 0.0, 0.08), 'ust': (0.0, 0.001, 1.0), 'alt': (0.15, -0.3, -0.9),
         'yakin_nozul': (0.25, 0.55, 0.10), 'yakin_kargo': (0.35, -0.10, 0.45), 'yakin_kiskac': (-0.30, -0.75, -0.25)}
looks = {'yakin_nozul': (c + Vector((0, 0.5, 0)) * r * 0.5, 1.1), 'yakin_kargo': (c + Vector((0, 0.05, 0.08)) * r, 1.4), 'yakin_kiskac': (c + Vector((0, -0.55, -0.1)) * r, 1.3)}
for k, d in views.items():
    look, dist = looks.get(k, (c, 2.9))
    cam = R.camera('c_' + k, tuple(look + Vector(d).normalized() * r * dist), tuple(look), 30)
    R.render(os.path.join(out, 'v_%s.png' % k), cam, (1000, 625), 48, transparent=False)
