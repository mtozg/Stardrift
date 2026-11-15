"""Aşama A–C (bpy): spec → geometri → prosedürel malzeme → lookdev render (Kapı 1) + nötr altın referans render (L3).
Kullanım: python pipeline/model.py <asset_id> <rev> [--fast] [--hash-only <çıktı.json>]"""
import os, sys, time, json, importlib, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy
from mathutils import Vector
from core import geo, materials, render as R
from core.paths import load_spec, work_dir, save_json, json_hash
from PIL import Image

t_start = time.time()
args = sys.argv[1:]
asset_id, rev = args[0], int(args[1])
fast = '--fast' in args
hash_only = args[args.index('--hash-only') + 1] if '--hash-only' in args else None
spec = load_spec(asset_id)
T = {}


def tick(k, t0):
    T[k] = round(time.time() - t0, 2)
    return time.time()


t0 = time.time()
geo.reset_scene()
mats = materials.library(spec['materials'])
fam = importlib.import_module('families.%s.build' % spec['family'])
built = fam.build(spec, mats)
obs = built['objects']
for s in built['sockets']:
    e = bpy.data.objects.new(s['name'], None)
    geo.collection('Asset').objects.link(e)
    e.location = s['loc']
    e['sd_socket'] = json.dumps({'dir': list(s['dir']), 'extras': s.get('extras', {})})
ghash = geo.geometry_hash(obs)
t0 = tick('build', t0)
if hash_only:
    save_json(hash_only, {'geometry_hash': ghash})
    print('RESULT', json.dumps({'geometry_hash': ghash}))
    sys.exit(0)

out = work_dir(asset_id, rev, 'model')
lo, hi = geo.bounds(obs)
center = (lo + hi) / 2
radius = (hi - lo).length / 2
tris = geo.tri_count(obs)
emit_area = sum(p.area for o in obs for p in o.data.polygons if o.data.materials[0].get('sd_def', '').startswith('emit'))
total_area = sum(p.area for o in obs for p in o.data.polygons)

# ---- lookdev (Kapı 1)
samples = 24 if fast else 96
scale = 0.5 if fast else 1.0
R.rig_lookdev(radius)
d = Vector((-0.50, 0.68, 0.38)).normalized()
hero = R.camera('Hero', tuple(center + d * radius * 3.1), tuple(center), 30)
R.render(os.path.join(out, 'hero.png'), hero, (int(1600 * scale), int(1000 * scale)), samples)
d2 = Vector((0.62, -0.62, 0.30)).normalized()
rear = R.camera('Rear', tuple(center + d2 * radius * 3.1), tuple(center), 30)
R.render(os.path.join(out, 'hero_rear.png'), rear, (int(1200 * scale), int(750 * scale)), samples)
close = R.camera('Close', tuple(center + Vector((-0.35, 0.55, 0.30)) * radius * 1.6 + Vector((0, radius * 0.3, 0))), tuple(center + Vector((0, radius * 0.45, radius * 0.05))), 35)
R.render(os.path.join(out, 'closeup.png'), close, (int(1200 * scale), int(750 * scale)), samples)
t0 = tick('render_lookdev', t0)

views = {'on': (0, 1, 0), 'arka': (0, -1, 0), 'sol': (-1, 0, 0), 'sag': (1, 0, 0), 'ust': (0, 0, 1), 'alt': (0, 0, -1)}
tiles = []
for k, v in views.items():
    c = R.camera('O_' + k, tuple(center + Vector(v) * radius * 5), tuple(center), ortho_scale=radius * 2.15)
    p = R.render(os.path.join(out, 'ortho_%s.png' % k), c, (420, 420), max(16, samples // 3))
    tiles.append((k, p))
sheet = Image.new('RGB', (420 * 3, 420 * 2), (8, 10, 16))
for i, (k, p) in enumerate(tiles):
    sheet.paste(Image.open(p).convert('RGB'), ((i % 3) * 420, (i // 3) * 420))
sheet.save(os.path.join(out, 'ortho_6.png'))
Image.open(os.path.join(out, 'hero.png')).convert('RGB').resize((128, 80), Image.LANCZOS).save(os.path.join(out, 'thumb_128.png'))
t0 = tick('render_ortho', t0)

# ---- nötr altın referans (L3: Three r128 ile birebir kurulabilen ışık)
R.rig_neutral()
cams = []
for name, dv in (('N1_on34', (-0.55, 0.75, 0.40)), ('N2_arka34', (0.60, -0.70, 0.35)), ('N3_yan', (1.0, 0.05, -0.12))):
    dd = Vector(dv).normalized()
    c = R.camera(name, tuple(center + dd * radius * 4.0), tuple(center), 30)
    R.render(os.path.join(out, 'golden_%s.png' % name), c, (800, 500), 32 if fast else 128, view='Standard', transparent=True)
    cams.append(R.camera_json(c, (800, 500)))
save_json(os.path.join(out, 'cameras.json'), {'cameras': cams, 'neutral': R.NEUTRAL})
t0 = tick('render_golden', t0)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'model.blend'), compress=True)
t0 = tick('save', t0)
meta = {'asset_id': asset_id, 'rev': rev, 'fast': fast, 'geometry_hash': ghash, 'spec_hash': json_hash(spec),
        'objects': len(obs), 'tris_source': tris, 'radius': round(radius, 4),
        'bounds_game': {'min': [round(min(a, b), 4) for a, b in zip(geo.b2g(lo), geo.b2g(hi))], 'max': [round(max(a, b), 4) for a, b in zip(geo.b2g(lo), geo.b2g(hi))]},
        'emit_area_ratio': round(emit_area / total_area, 4), 'timings': T, 'seconds': round(time.time() - t_start, 1),
        'blender': bpy.app.version_string}
save_json(os.path.join(out, 'meta.json'), meta)
print('RESULT', json.dumps(meta))
