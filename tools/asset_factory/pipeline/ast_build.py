"""Asteroit ailesi: tek GLB (AST_<tür>_1..3 + PICK_<tür>), tek ortak atlas (4×4 karo, karo 256²). Kaynak: mevcut cevher sprite'ları (ore3_*, orep_*).
Yöntem: tek bakış maskesinden şişirilmiş görsel gövde (uzaklık dönüşümü → kalınlık) → Remesh → Decimate → ön/arka düzlemsel UV (karo) → GLB.
Kullanım: python pipeline/ast_build.py <spec.json> <çıktı_klasörü>"""
import os, sys, json, math, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import bpy, bmesh
from mathutils import Vector
from PIL import Image
from core import geo, export, bake as B, glbpack, render as R

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
t_start = time.time()
spec = json.load(open(sys.argv[1], encoding='utf-8'))
out = sys.argv[2]
os.makedirs(out, exist_ok=True)
ATLAS = 1024
TILE = 256
KIND = spec['kind']
items = [(f'AST_{KIND}_{i + 1}', p, spec['tris'], spec['voxels']) for i, p in enumerate(spec['sprites'])] + [(f'PICK_{KIND}', spec['pickup'], spec['pickup_tris'], 28)]


def dist_inside(m):
    """Maskenin içindeki piksellerin dış kenara uzaklığı (4-komşu, iteratif aşındırma; scipy yok)."""
    d = np.zeros(m.shape, np.float32)
    cur = m.copy()
    k = 0
    while cur.any():
        k += 1
        d[cur] = k
        er = cur.copy()
        er[1:, :] &= cur[:-1, :]
        er[:-1, :] &= cur[1:, :]
        er[:, 1:] &= cur[:, :-1]
        er[:, :-1] &= cur[:, 1:]
        er[0, :] = er[-1, :] = False
        er[:, 0] = er[:, -1] = False
        cur = er
    return d


def hull_mesh(sprite_path, nv, tris, noise_seed):
    im = Image.open(os.path.join(REPO, sprite_path)).convert('RGBA')
    m = np.array(im.resize((nv, nv), Image.LANCZOS))[:, :, 3] > 110
    d = dist_inside(m)
    d = d / max(d.max(), 1)
    rng = np.random.default_rng(noise_seed)
    # derinlik: kenarda ince, merkezde kalın (yuvarlak kaya); hafif düzensizlik
    depth = (d ** 0.55) * 0.5 * (0.9 + 0.2 * rng.random((nv, nv)))
    occ = np.zeros((nv, nv, nv), bool)      # [x, y(derinlik), z]
    zs = np.arange(nv)
    for i in range(nv):
        for k in range(nv):
            if m[nv - 1 - k, i]:
                h = int(round(depth[nv - 1 - k, i] * nv))
                lo, hi = nv // 2 - h, nv // 2 + h + 1
                occ[i, max(lo, 0):min(hi, nv), k] = True
    bm = bmesh.new()
    vm = {}
    sx = 1.0 / nv

    def V(p):
        if p not in vm:
            vm[p] = bm.verts.new(((p[0] - nv / 2) * sx, (p[1] - nv / 2) * sx, (p[2] - nv / 2) * sx))
        return vm[p]

    occp = np.pad(occ, 1)
    for ax in range(3):
        for sg in (-1, 1):
            face = occp & ~np.roll(occp, -sg, axis=ax)
            for (i, j, k) in np.argwhere(face[1:-1, 1:-1, 1:-1]):
                c = [i, j, k]
                if sg > 0:
                    c[ax] += 1
                a1, a2 = [a for a in range(3) if a != ax]
                q = []
                for d1, d2 in ((0, 0), (1, 0), (1, 1), (0, 1)):
                    p = list(c)
                    p[a1] += d1
                    p[a2] += d2
                    q.append(V(tuple(p)))
                try:
                    bm.faces.new(q if sg > 0 else q[::-1])
                except ValueError:
                    pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new('m')
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new('m', me)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    rm = ob.modifiers.new('rm', 'REMESH')
    rm.mode = 'VOXEL'
    rm.voxel_size = 1.5 * sx
    geo.apply_modifier(ob, rm)
    sm = ob.modifiers.new('sm', 'SMOOTH')
    sm.factor = 0.5
    sm.iterations = 6
    geo.apply_modifier(ob, sm)
    bm = bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.triangulate(bm, faces=bm.faces); bm.to_mesh(ob.data); bm.free()
    n = len(ob.data.polygons)
    if n > tris:
        dc = ob.modifiers.new('dec', 'DECIMATE')
        dc.decimate_type = 'COLLAPSE'
        dc.ratio = tris / n
        geo.apply_modifier(ob, dc)
    bm = bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(ob.data); bm.free()
    geo.set_smooth_by_angle(ob, 60)
    cs = [v.co[:] for v in ob.data.vertices]
    cen = np.mean(cs, 0)
    for v in ob.data.vertices:
        v.co -= Vector(cen)
    ext = max(max(v.co.x for v in ob.data.vertices) - min(v.co.x for v in ob.data.vertices), max(v.co.z for v in ob.data.vertices) - min(v.co.z for v in ob.data.vertices))
    for v in ob.data.vertices:
        v.co *= 1.0 / ext
    return ob, im, m


geo.reset_scene()
atlas = np.zeros((ATLAS, ATLAS, 4), np.uint8)
objs = []
tiles = []
for idx, (name, sp, tris, nv) in enumerate(items):
    ob, im, mask = hull_mesh(sp, nv, tris, 11 + idx)
    ob.name = name
    r, c = divmod(idx, 4)
    t = np.array(im.resize((TILE, TILE), Image.LANCZOS))
    atlas[r * TILE:(r + 1) * TILE, c * TILE:(c + 1) * TILE] = t
    # UV: ön (y<0 yüzler) ve arka yüzler aynı karoyu düzlemsel kullanır; kaynak sprite çerçevesi = gövde 1.0 birim (ölçek sonrası bbox)
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.normal_update()
    uvl = bm.loops.layers.uv.verify()
    for f in bm.faces:
        for lp in f.loops:
            p = lp.vert.co
            u = (c + (p.x + 0.5)) / 4.0
            v = 1.0 - (r + (0.5 - p.z)) / 4.0
            lp[uvl].uv = (u, v)
    bm.to_mesh(ob.data); bm.free()
    objs.append(ob)
    tiles.append({'ad': name, 'karo': [r, c], 'tris': len(ob.data.polygons)})
# kenar dolgusu
filled = atlas[..., 3] > 40
rgb = atlas[..., :3].astype(np.float32)
for _ in range(16):
    k = ~filled
    if not k.any():
        break
    acc = np.zeros_like(rgb); cnt = np.zeros(filled.shape, np.float32)
    for dy_, dx_ in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        f2 = np.roll(filled, (dy_, dx_), (0, 1)); r2 = np.roll(rgb, (dy_, dx_), (0, 1))
        acc += r2 * f2[..., None]; cnt += f2
    nz = k & (cnt > 0)
    rgb[nz] = acc[nz] / cnt[nz][..., None]
    filled = filled | nz
used = np.zeros((ATLAS, ATLAS), bool)
for idx in range(len(items)):
    r, c = divmod(idx, 4)
    used[r * TILE:(r + 1) * TILE, c * TILE:(c + 1) * TILE] = True
rgb[~used & ~filled] = rgb[used].mean(0)
mx, mn = rgb.max(-1), rgb.min(-1)
sat = np.where(mx > 1, (mx - mn) / np.maximum(mx, 1), 0)
lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]) / 255.0
orm = np.ones((ATLAS, ATLAS, 4), np.float32)
orm[..., 0] = 1.0
orm[..., 1] = np.clip(0.88 - 0.25 * lum, 0.4, 0.95)
orm[..., 2] = np.clip((0.5 - sat) * 0.5, 0, 0.25) * np.clip((lum - 0.2) * 3, 0, 1)
em = ((mx / 255.0 > spec.get('emit_v', 0.6)) & (sat > spec.get('emit_s', 0.45))).astype(np.float32)
OS = spec.get('orm_tex', 256)
ES = spec.get('emit_tex', 256)


def mkimg(name, arr, non_color):
    im = bpy.data.images.new(name, arr.shape[1], arr.shape[0], alpha=False)
    if non_color:
        im.colorspace_settings.name = 'Non-Color'
    im.pixels = arr.astype(np.float32).ravel().tolist()
    return im


base_arr = np.concatenate([rgb / 255.0, np.ones((ATLAS, ATLAS, 1), np.float32)], -1)[::-1]
img_base = mkimg('sd_ast_base', base_arr, False)
orm_s = np.array(Image.fromarray((np.clip(orm[..., :3], 0, 1) * 255).astype(np.uint8)).resize((OS, OS), Image.LANCZOS)).astype(np.float32) / 255.0
img_orm = mkimg('sd_ast_orm', np.concatenate([orm_s, np.ones((OS, OS, 1), np.float32)], -1)[::-1], True)
has_emit = em.sum() > 20
img_emit = None
if has_emit:
    e = Image.fromarray(((rgb / 255.0 * em[..., None]) * 255).astype(np.uint8)).resize((ES, ES), Image.LANCZOS)
    img_emit = mkimg('sd_ast_emit', np.concatenate([np.array(e).astype(np.float32) / 255.0, np.ones((ES, ES, 1), np.float32)], -1)[::-1], False)
mat = B.gltf_body_material('MAT_ast_' + KIND, img_base, img_orm, None, img_emit)
root = export.empty('SD_ast_' + KIND)
for ob in objs:
    B.assign_single(ob, mat)
    # eksen: glTF'e dönüştürme (x, y(derinlik), z yukarı) → Blender (x, y, z) zaten Z-yukarı
    ob.parent = root
allo = [root] + objs
for o in allo:
    for k in [k for k in o.keys() if k.startswith('sd_')]:
        del o[k]
glb = os.path.join(out, 'sd_ast_%s.glb' % KIND)
export.export_glb(glb, allo, quality=90)
size_b, rec = glbpack.recompress_textures(glb)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'model.blend'), compress=True)
# önizleme: tüm parçalar yan yana (nötr ışık)
sc = bpy.context.scene
R.rig_neutral()
for i, ob in enumerate(objs):
    ob.location = Vector(((i - (len(objs) - 1) / 2) * 1.25, 0, 0))
cd = bpy.data.cameras.new('c'); cd.type = 'ORTHO'; cd.ortho_scale = 1.25 * len(objs) + 0.2
cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (0, -4, 0); cam.rotation_euler = (math.pi / 2, 0, 0)
R.render(os.path.join(out, 'm_front.png'), cam, (1500, 360), 24, view='Standard', transparent=True, bounces=0)
cam.location = (0, 4, 0); cam.rotation_euler = (math.pi / 2, 0, math.pi)
R.render(os.path.join(out, 'm_back.png'), cam, (1500, 360), 24, view='Standard', transparent=True, bounces=0)
meta = {'id': 'ast_' + KIND, 'bytes': size_b, 'parcalar': tiles, 'has_emit': bool(has_emit), 'texture_recompress': rec, 'seconds': round(time.time() - t_start, 1)}
json.dump(meta, open(os.path.join(out, 'meta.json'), 'w'), indent=1, ensure_ascii=False)
print('RESULT', json.dumps(meta, ensure_ascii=False))
