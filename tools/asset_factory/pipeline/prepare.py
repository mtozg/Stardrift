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
PC = spec.get('prepare', {})      # aileye özel hazırlık ayarları (kokpit: iç mekân temizliği, ekranlar, kanal boyutları)
screens = roles.get('screen', [])      # SCR_* düğümleri ayrı kalır (oyun canlı ekranları ada göre bağlar)
arts = roles.get('art', [])      # eklemli parçalar (ör. Yük Devi kıskacı): aynı atlasa pişer, sonra eklem başına ayrılır; temizlikten (cull) muaf
joints = {o.name: o for o in bpy.data.objects if o.type == 'EMPTY' and o.name.startswith('ART_')}
bpy.context.view_layer.update()
body = cleanup.join_role(roles.get('body', []), 'LOD0_body')
live = cleanup.join_role(roles.get('emit_live', []), 'LOD0_emit')
info['welded_verts'] = cleanup.weld(body) + (cleanup.weld(live) if live else 0)
t0 = tick('join_weld', t0)

occ = [o for o in (body, live) if o] + screens + arts
info['tris_before_cull'] = geo.tri_count(occ)
if PC.get('cull') == 'interior':
    eyes = [tuple(e) for e in PC['eyes']]
    info['culled_faces'] = {'body': cleanup.cull_hidden_interior(body, occ, eyes)}
    if live:
        info['culled_faces']['emit'] = cleanup.cull_hidden_interior(live, occ, eyes)
else:
    info['culled_faces'] = {'body': cleanup.cull_hidden_exterior(body, occ)}
    if live:
        info['culled_faces']['emit'] = cleanup.cull_hidden_exterior(live, occ)
info['tris_after_cull'] = geo.tri_count(occ)
t0 = tick('cull_hidden', t0)

hi = None
if roles.get('hi'):      # aile kendi hi-poly'sini üretti (bütünleşik gövde: oluklu çekirdek + aynı küçük parçalar)
    hi = cleanup.join_role(roles['hi'], 'HI')
    hi.hide_render = True
    info['hipoly_tris'] = geo.tri_count([hi])
    if PC.get('hipoly', {}).get('extra'):
        from core import hipoly as _hp
        HPx = PC['hipoly']
        _ob, _n = _hp.make_high(hi, panel=HPx.get('panel', 1.2), seed=HPx.get('seed', 3), relief=tuple(HPx.get('relief', (0.008, 0.02))), inset=HPx.get('inset', 0.05), bevel=HPx.get('bevel', 0.005), rivet_r=HPx.get('rivet_r', 0.024), rivet_h=HPx.get('rivet_h', 0.014), rivet_p=HPx.get('rivet_p', 0.4), frac=HPx.get('frac', 0.3))
        bpy.data.objects.remove(hi)
        hi = _ob
        hi.hide_render = True
        info['hipoly_tris'] = _n
elif PC.get('hipoly'):
    from core import hipoly
    HP = PC['hipoly']
    hi, hi_tris = hipoly.make_high(body, panel=HP.get('panel', 0.9), seed=HP.get('seed', 1), relief=tuple(HP.get('relief', (0.012, 0.03))), inset=HP.get('inset', 0.045),
                                   bevel=HP.get('bevel', 0.006), rivet_r=HP.get('rivet_r', 0.024), rivet_h=HP.get('rivet_h', 0.014), rivet_p=HP.get('rivet_p', 0.55), frac=HP.get('frac', 0.6))
    info['hipoly_tris'] = hi_tris
    hi.hide_render = True      # AO/diğer bake'ler hi-poly'yi görmemeli (kabartma AO'ya 'dama' gölgesi basıyordu)
    t0 = tick('hipoly_build', t0)

part_joint = {}      # yüz özniteliği sd_part → eklem adı (0 = gövde)
if arts:
    import bmesh
    groups = {}
    for o in arts:
        groups.setdefault(o.parent.name, []).append(o)
    for pid, (jn, objs_) in enumerate(sorted(groups.items()), start=1):
        part_joint[pid] = jn
        for o in objs_:
            o.data.attributes.new('sd_part', 'INT', 'FACE')
            for i in range(len(o.data.polygons)):
                o.data.attributes['sd_part'].data[i].value = pid
    body.data.attributes.new('sd_part', 'INT', 'FACE')
    body = cleanup.join_role([body] + arts, 'LOD0_body')      # gövde aktif nesne kalır
    info['articulated'] = {jn: pid for pid, jn in part_joint.items()}
    t0 = tick('join_articulated', t0)

size = 512 if fast else spec['texture_size']
tex = {k: (max(256, v // 4) if fast else v) for k, v in PC.get('tex', {'base': size, 'orm': size, 'normal': size}).items()}
size = tex['base']
uv.unwrap_unique(body, size, shape=PC.get('uv_pack', 'CONCAVE'), margin_px_at_1024=PC.get('uv_margin', 4), angle=PC.get('uv_angle', 66))
info['uv'] = uv.stats(body, size)
info['tex_sizes'] = tex
t0 = tick('uv', t0)

imgs = bake.bake(body, tex, samples=8 if fast else PC.get('bake_samples', 24), ao_samples=24 if fast else PC.get('ao_samples', 128), ao_distance=PC.get('ao_distance'))
if PC.get('ao_into_base'):      # pişirilmiş AO'yu albedoya da çarp: Three'de aoMap yalnız dolaylı ışığı etkiler; derinlik her ışıkta görünsün (Kaşif yaklaşımı)
    _s = float(PC['ao_into_base'])
    _b, _a = bake.pixels(imgs['base']), bake.pixels(imgs['ao'])
    if _b.shape[:2] != _a.shape[:2]:
        from PIL import Image as _I
        _a = np.asarray(_I.fromarray((np.clip(_a[..., 0], 0, 1) * 255).astype(np.uint8)).resize((_b.shape[1], _b.shape[0]), _I.BILINEAR), np.float32)[..., None] / 255.0
        _a = np.repeat(_a, 4, axis=2)
    _b[..., :3] *= ((1.0 - _s) + _s * np.clip(_a[..., :1], 0, 1))
    imgs['base'].pixels = _b.ravel().tolist()
    info['ao_into_base'] = _s
t0 = tick('bake', t0)
if hi is not None:      # normal: hi-poly'den pişir; eğrilik maskeleriyle albedo/ORM'e kenar parlaması + girinti kiri işle
    HP = PC['hipoly']
    hi.hide_render = False
    nimg = bake.bake_normal_from_high(body, hi, tex['normal'], cage=HP.get('cage', 0.08), ray=HP.get('ray', 0.25))
    npx = bake.pixels(nimg)
    edge, cav = bake.curvature_from_normal(npx, HP.get('k_edge', 7.0), HP.get('k_cav', 7.0))
    imgs['normal'] = nimg
    from PIL import Image as _I
    def _fit(m, sz):
        return m if m.shape[0] == sz else np.asarray(_I.fromarray((m * 255).astype(np.uint8)).resize((sz, sz), _I.BILINEAR), np.float32) / 255.0
    eb, cb = _fit(edge, imgs['base'].size[0]), _fit(cav, imgs['base'].size[0])
    b = bake.pixels(imgs['base'])
    b[..., :3] = b[..., :3] * (1 - HP.get('cav_dark', 0.38) * cb[..., None]) + (b[..., :3] * 1.5 + 0.05 - b[..., :3]) * (HP.get('edge_light', 0.7) * eb[..., None])
    b[..., :3] = np.clip(b[..., :3], 0, 1)
    imgs['base'].pixels = b.ravel().tolist()
    eo, co = _fit(edge, imgs['rough'].size[0]), _fit(cav, imgs['rough'].size[0])
    for key, fn in (('rough', lambda a: a * (1 - 0.45 * eo[..., None]) * (1 + 0.15 * co[..., None])), ('metal', lambda a: a + (1 - a) * 0.55 * eo[..., None] * HP.get('edge_metal', 1.0)), ('ao', lambda a: a * (1 - 0.35 * co[..., None]))):
        a = bake.pixels(imgs[key])
        a[..., :3] = np.clip(fn(a[..., :3]), 0, 1)
        imgs[key].pixels = a.ravel().tolist()
    bpy.data.objects.remove(hi)
    info['hipoly_baked'] = True
    t0 = tick('hipoly_bake', t0)

orm = bake.compose_orm(imgs, tex['orm'])
# normal: float → 8 bit doğrusal görüntü (glTF/WebP)
nrm = bpy.data.images.new('sd_normal', tex['normal'], tex['normal'], alpha=False)
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
if screens:   # ekran yer tutucusu: tek düz emisyon (≤ 1); oyunda canlı ekran dokusuyla değiştirilir
    ms = bpy.data.materials.new('MAT_screen')
    ms.use_nodes = True
    ps = [n for n in ms.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'][0]
    ps.inputs['Base Color'].default_value = (0.0, 0.0, 0.0, 1)
    ps.inputs['Emission Color'].default_value = (0.03, 0.22, 0.30, 1)
    ps.inputs['Emission Strength'].default_value = 1.0
    ms.use_backface_culling = True
    for o in screens:
        o.data.materials.clear()
        o.data.materials.append(ms)
t0 = tick('materials', t0)

NORM = None      # normalize_length: modeli metre ölçeğinden L=1,0 (burun ekseni) ve merkez orijine ölçekle (bake'ten sonra: doku değişmez); soketler/eklemler aynı dönüşümle
if PC.get('normalize_length'):
    _objs = [o for o in [body, live] + screens + arts if o]
    _lo, _hi = geo.bounds(_objs)
    _ext = (_hi - _lo)
    _s = 1.0 / (max(_ext.x, _ext.y, _ext.z) if PC.get('normalize_axis') == 'max' else _ext.y)
    _c = (_lo + _hi) / 2
    for o in _objs:
        for v in o.data.vertices:
            v.co = (v.co - _c) * _s
        o.data.update()
    for j in joints.values():
        j.location = (Vector(j.location) - _c) * _s
    NORM = (_s, _c)
    info['normalize'] = {'scale': round(_s, 6), 'length_m_before': round(1.0 / _s, 3)}

# eklemli parçaları ayır: her eklem için tek mesh, köşeler eklemin yerel uzayında (pivot eklem merkezinde), düğüm dönüşümü birim
art_meshes = []
if part_joint:
    import bmesh
    from mathutils import Matrix
    me0 = body.data
    coll = body.users_collection[0]

    def keep_faces(me, pid, to_local=None):
        bm = bmesh.new()
        bm.from_mesh(me)
        lay = bm.faces.layers.int['sd_part']
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[lay] != pid], context='FACES')
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
        if to_local is not None:
            bmesh.ops.transform(bm, matrix=to_local, verts=bm.verts)
        bm.to_mesh(me)
        bm.free()
        me.update()
    for pid, jn in part_joint.items():
        me = me0.copy()
        me.name = jn + '_geo'
        keep_faces(me, pid, joints[jn].matrix_world.inverted())
        ob = bpy.data.objects.new(jn + '_geo', me)
        coll.objects.link(ob)
        ob.parent = joints[jn]      # matrix_parent_inverse birim: yerel köşeler eklem uzayında
        art_meshes.append(ob)
        me.attributes.remove(me.attributes['sd_part'])
    keep_faces(me0, 0)
    me0.attributes.remove(me0.attributes['sd_part'])
    info['articulated_tris'] = {o.name: len(o.data.polygons) for o in art_meshes}
    t0 = tick('split_articulated', t0)

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
lo, hi = geo.bounds(lods[0] + art_meshes)
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
for o in screens:
    o.parent = root
for jn, j in joints.items():
    if j.parent is None:
        j.parent = bpy.data.objects['LOD0']      # kinematik zincirin kökü LOD0 altında; alt eklemler zaten ebeveynine bağlı
sock_objs = []
for e in [o for o in bpy.data.objects if o.type == 'EMPTY' and o.name.startswith(('SOCK_', 'ANCH_'))]:
    sd = json.loads(e['sd_socket'])
    _loc = tuple((Vector(e.location) - NORM[1]) * NORM[0]) if NORM else tuple(e.location)
    s = export.socket(root, e.name + '_x', _loc, tuple(sd['dir']), {'sd_socket_extras': json.dumps(dict(sd['extras'], dir=[round(x, 4) for x in geo.b2g(sd['dir'])]), ensure_ascii=False)})
    name = e.name
    bpy.data.objects.remove(e)
    s.name = name
    pj = sd['extras'].get('parent')
    if pj in joints:      # soket eklemle birlikte hareket eder (ör. kıskaç kavrama noktası bilekte)
        s.parent = joints[pj]
        s.matrix_parent_inverse = joints[pj].matrix_world.inverted()
    sock_objs.append(s)
# extras: fabrika iç özellikleri kaldır, yalnız sözleşme alanlarını glTF extras'a yaz
allobjs = [root] + [o for o in bpy.data.objects if o.parent is not None]
for o in allobjs:
    keep = {}
    if 'sd_asset' in o:
        keep = json.loads(o['sd_asset'])
    if 'sd_socket_extras' in o:
        keep = json.loads(o['sd_socket_extras'])
    if 'sd_joint' in o:
        keep = {'joint_axis': str(o['sd_joint'])}
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
