"""Aşama D (bpy): oyuna hazırlık. Kapı 1 (görsel onay) sonrasında çalışır.
rol birleştirme → kaynak/temizlik → gizli yüz silme → UV → kanal bake → glTF malzemesi → LOD → hiyerarşi + soketler → GLB (WebP)
Kullanım: python pipeline/prepare.py <asset_id> <rev> [--fast]"""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy
import numpy as np
from mathutils import Vector
from core import geo, cleanup, uv, bake, lod, export
from core.paths import load_spec, work_dir, save_json, load_json, json_hash

t_start = time.time()
args = sys.argv[1:]
asset_id, rev = args[0], int(args[1])
fast = '--fast' in args
spec = load_spec(asset_id)
T, info = {}, {}


def tick(k, t0):
    T[k] = round(time.time() - t0, 2)
    print('ADIM', k, T[k], 's', flush=True)
    return time.time()


src = work_dir(asset_id, rev, 'model')
out = work_dir(asset_id, rev, 'prepare')
texdir = os.path.join(out, 'tex')
os.makedirs(texdir, exist_ok=True)
model_meta = load_json(os.path.join(src, 'meta.json'))
t0 = time.time()
bpy.ops.wm.open_mainfile(filepath=os.path.join(src, 'model.blend'))
for o in [o for o in bpy.data.objects if o.type in ('CAMERA', 'LIGHT')]:
    bpy.data.objects.remove(o)
objs = [o for o in bpy.data.objects if o.type == 'MESH']
roles = {}
for o in objs:
    roles.setdefault(o.get('sd_role', 'body'), []).append(o)
body = cleanup.join_role(roles.get('body', []), 'LOD0_body')
live = cleanup.join_role(roles.get('emit_live', []), 'LOD0_emit')
info['welded_verts'] = cleanup.weld(body) + (cleanup.weld(live) if live else 0)
t0 = tick('join_weld', t0)

occ = [o for o in (body, live) if o]
info['tris_before_cull'] = geo.tri_count(occ)
info['culled_faces'] = {'body': cleanup.cull_hidden_exterior(body, occ)}
if live:
    info['culled_faces']['emit'] = cleanup.cull_hidden_exterior(live, occ)
info['tris_after_cull'] = geo.tri_count(occ)
t0 = tick('cull_hidden', t0)

size = 512 if fast else spec['texture_size']
uv.unwrap_unique(body, size)
info['uv'] = uv.stats(body, size)
t0 = tick('uv', t0)

imgs = bake.bake(body, size, samples=8 if fast else 24, ao_samples=24 if fast else 128)
t0 = tick('bake', t0)

orm = bake.compose_orm(imgs, size)
# normal: float → 8 bit doğrusal görüntü (glTF/WebP)
nrm = bpy.data.images.new('sd_normal', size, size, alpha=False)
nrm.colorspace_settings.name = 'Non-Color'
nrm.pixels = imgs['normal'].pixels[:]
emit_px = bake.pixels(imgs['emit'])
has_emit = float(emit_px[..., :3].max()) > 0.01
files = {}
for k, im in (('base', imgs['base']), ('orm', orm), ('normal', nrm), ('emit', imgs['emit']), ('ao', imgs['ao']), ('rough', imgs['rough']), ('metal', imgs['metal'])):
    files[k] = bake.save_png(im, os.path.join(texdir, 'sd_%s_%s.png' % (asset_id, k)))
mat_body = bake.gltf_body_material('MAT_body', imgs['base'], orm, nrm, imgs['emit'] if has_emit else None)
mat_body.use_backface_culling = True     # glTF doubleSided=false (tek yüz: hem doğru hem ucuz)
bake.assign_single(body, mat_body)
if live:   # canlı emisyon: tek düz renk (oyunda animasyonla sürülebilir), ≤ 1
    src_m = live.material_slots[0].material
    b = [n for n in src_m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'][0]
    c = list(b.inputs['Emission Color'].default_value)[:3]
    me = bpy.data.materials.new('MAT_emit')
    me.use_nodes = True
    pb = [n for n in me.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'][0]
    pb.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1)
    pb.inputs['Roughness'].default_value = 0.5
    pb.inputs['Emission Color'].default_value = (*[min(1.0, x) for x in c], 1)
    pb.inputs['Emission Strength'].default_value = 1.0
    me.use_backface_culling = True
    bake.assign_single(live, me)
    for p in live.data.polygons:
        p.use_smooth = False
info['has_static_emit'] = has_emit
t0 = tick('materials', t0)

# LOD
ratios = spec['lods']
lods = {0: [body] + ([live] if live else [])}
tris = [geo.tri_count(lods[0])]
for i, r in enumerate(ratios[1:], start=1):
    b, nb = lod.make_lod(body, r, 'LOD%d_body' % i)
    group = [b]
    n = nb
    if live:
        e, ne = lod.make_lod(live, 1.0, 'LOD%d_emit' % i)
        group.append(e)
        n += ne
    lods[i] = group
    tris.append(n)
info['tris_lod'] = tris
t0 = tick('lod', t0)

# hiyerarşi + soketler + extras
lo, hi = geo.bounds(lods[0])
gl, gh = geo.b2g(lo), geo.b2g(hi)
bmin = [round(min(a, b), 4) for a, b in zip(gl, gh)]
bmax = [round(max(a, b), 4) for a, b in zip(gl, gh)]
root = export.empty('SD_' + asset_id, props={
    'sd_asset': json.dumps({'id': asset_id, 'rev': rev, 'family': spec['family'], 'class': spec['class'],
                            'length_m': spec.get('length_m'), 'units': 'm', 'forward': '-Z', 'up': '+Y',
                            'bounds_min': bmin, 'bounds_max': bmax, 'radius': round((hi - lo).length / 2, 4),
                            'tris': tris, 'lod_ratios': ratios, 'texture_mode': spec['texture_mode'],
                            'spec_hash': json_hash(spec), 'geometry_hash': model_meta['geometry_hash'],
                            'test_asset': bool(spec.get('test_asset')), 'contract': 'GEÇİCİ (game_contract bekleniyor)'}, ensure_ascii=False)})
for i, group in lods.items():
    le = export.empty('LOD%d' % i, root)
    for o in group:
        o.parent = le
sock_objs = []
for e in [o for o in bpy.data.objects if o.type == 'EMPTY' and o.name.startswith('SOCK_')]:
    sd = json.loads(e['sd_socket'])
    s = export.socket(root, e.name + '_x', tuple(e.location), tuple(sd['dir']), {'sd_socket_extras': json.dumps(sd['extras'], ensure_ascii=False)})
    name = e.name
    bpy.data.objects.remove(e)
    s.name = name
    sock_objs.append(s)
# extras: fabrika iç özellikleri kaldır, yalnız sözleşme alanlarını glTF extras'a yaz
allobjs = [root] + [o for o in bpy.data.objects if o.parent is not None]
for o in allobjs:
    keep = {}
    if 'sd_asset' in o:
        keep = json.loads(o['sd_asset'])
    if 'sd_socket_extras' in o:
        keep = json.loads(o['sd_socket_extras'])
    for k in list(o.keys()):
        del o[k]
    for k, v in keep.items():
        o[k] = v
glb = os.path.join(out, 'sd_%s_r%03d.glb' % (asset_id, rev))
size_raw = export.export_glb(glb, allobjs, quality=95)
from core import glbpack
size_b, info['texture_recompress'] = glbpack.recompress_textures(glb)
info['glb_bytes_blender'] = size_raw
info['glb_bytes'] = size_b
t0 = tick('export', t0)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'prepared.blend'), compress=True)
meta = {'asset_id': asset_id, 'rev': rev, 'fast': fast, 'texture_size': size, 'glb': glb, 'textures_png': files,
        **info, 'timings': T, 'seconds': round(time.time() - t_start, 1)}
save_json(os.path.join(out, 'meta.json'), meta)
print('RESULT', json.dumps(meta, ensure_ascii=False))
