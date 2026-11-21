"""Hangar giriş koridoru modülü + dış kapı (Ankora prototipi). Mevcut sanat dili: kaynak = oyundaki xdoor_ankora (kapı), ximg_in (koridor duvar/zemin/tavan) çizimleri.
Ölçüler oyun koduyla aynı: OW=9, OH=5,2, segment uzunluğu XSEG=7,6 (koridor 6 segment). Parametrik geometri + kaynak çizimlerin düzlemsel izdüşümü (palet birebir).
Çıktı: hangar_koridor_ankora.glb (1 modül, LOD0 ≤ 6k), hangar_kapi_dis_ankora.glb (≤ 4k). Eksen: oyun uzayı, koridor boyu +Z (oyun −Z ileri → burada +Z), yukarı +Y; birim = oyun birimi.
Kullanım: python pipeline/hangar_build.py <çıktı_klasörü>"""
import os, sys, json, math, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix
from PIL import Image
from core import geo, export, bake as B, glbpack, render as R

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
OW, OH, XSEG = 9.0, 5.2, 7.6
TEX = 1024
T = TEX // 2      # 4 karo 512²: 0 kapı, 1 duvar, 2 zemin, 3 tavan
t_start = time.time()


def crop(path, box, size):
    im = Image.open(os.path.join(REPO, path)).convert('RGB')
    w, h = im.size
    return im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h))).resize(size, Image.LANCZOS)


atlas = Image.new('RGB', (TEX, TEX))
atlas.paste(crop('assets/img/xdoor_ankora.webp', (0, 0, 1, 1), (T, T)), (0, 0))                       # 0: kapı
atlas.paste(crop('assets/img/ximg_in.webp', (0.0, 0.10, 0.30, 0.90), (T, T)), (T, 0))                    # 1: sol duvar boruları
atlas.paste(crop('assets/img/ximg_in.webp', (0.25, 0.70, 0.75, 1.0), (T, T)), (0, T))                    # 2: zemin ızgara
atlas.paste(crop('assets/img/ximg_in.webp', (0.25, 0.0, 0.75, 0.25), (T, T)), (T, T))                   # 3: tavan
base = np.array(atlas).astype(np.float32) / 255.0


class Mesh:
    def __init__(self):
        self.bm = bmesh.new()
        self.uvl = self.bm.loops.layers.uv.verify()

    def box(self, c, s, tile, proj, ext, rot=None):
        """kutu; proj='z' (XY düzlemi, Z normali) / 'x' (YZ) / 'y' (XZ): kaynak karo bu düzleme ölçekli düzlemsel yerleşir (ext = karo ölçüsü m)"""
        r = bmesh.ops.create_cube(self.bm, size=1.0)
        M = Matrix.Translation(Vector(c)) @ Matrix.Diagonal((*s, 1.0))
        bmesh.ops.transform(self.bm, matrix=M, verts=r['verts'])
        tx, ty = (tile % 2) * 0.5, (tile // 2) * 0.5
        for f in self.bm.faces:
            if not all(v in r['verts'] for v in f.verts):
                continue
            for lp in f.loops:
                p = lp.vert.co
                if proj == 'z':
                    u, v = p.x / ext[0], p.y / ext[1]
                elif proj == 'x':
                    u, v = p.z / ext[0], p.y / ext[1]
                else:
                    u, v = p.x / ext[0], p.z / ext[1]
                lp[self.uvl].uv = (tx + 0.02 + 0.46 * (u % 1.0), 1.0 - (ty + 0.02 + 0.46 * (1 - (v % 1.0))))


def cyl_x(m, p0, p1, r, tile, seg=10):
    d = Vector(p1) - Vector(p0)
    M = Matrix.Translation((Vector(p0) + Vector(p1)) / 2) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    res = bmesh.ops.create_cone(m.bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r, depth=d.length, matrix=M)
    tx, ty = (tile % 2) * 0.5, (tile // 2) * 0.5
    for v in res['verts']:
        for lp in v.link_loops:
            lp[m.uvl].uv = (tx + 0.02 + 0.46 * ((v.co.x + v.co.z) * 0.2 % 1.0), 1.0 - (ty + 0.02 + 0.46 * (v.co.y * 0.3 % 1.0)))


def octa_frame(m, z, w, h, th, depth, tile, ch=1.1):
    """sekizgen çerçeve halkası: iç boşluk w×h, kalınlık th, derinlik (Z) depth; köşe pahı ch"""
    # 4 kenar kutusu + 4 çapraz köşe kutusu
    m.box((0, h / 2 + th / 2, z), (w + 2 * th, th, depth), tile, 'z', (4.5, 2.6))
    m.box((0, -h / 2 - th / 2, z), (w + 2 * th, th, depth), tile, 'z', (4.5, 2.6))
    m.box((w / 2 + th / 2, 0, z), (th, h, depth), tile, 'x', (2.6, 2.6))
    m.box((-w / 2 - th / 2, 0, z), (th, h, depth), tile, 'x', (2.6, 2.6))
    for sx in (-1, 1):      # köşe takviyeleri (pah görünümü): iç köşede kare dolgu
        for sy in (-1, 1):
            m.box((sx * (w / 2 - ch / 2), sy * (h / 2 - ch / 2), z), (ch, ch, depth * 0.92), tile, 'z', (4.5, 2.6))


def corridor():
    m = Mesh()
    L = XSEG
    # zemin ve tavan plakaları
    m.box((0, -OH / 2 - 0.15, L / 2), (OW + 1.2, 0.3, L), 2, 'z', (4.5, 3.8))
    m.box((0, OH / 2 + 0.15, L / 2), (OW + 1.2, 0.3, L), 3, 'z', (4.5, 3.8))
    # zemin ızgara kaburgaları (boyuna)
    for i in range(-4, 5):
        m.box((i * 0.95, -OH / 2 + 0.06, L / 2), (0.16, 0.12, L - 0.4), 2, 'z', (4.5, 3.8))
    # tavan ışık şeritleri (emissive karo: tavan karosu parlak orta) + kablo kanalları
    for sx in (-1, 1):
        m.box((sx * 1.6, OH / 2 - 0.08, L / 2), (0.55, 0.1, L - 0.6), 3, 'z', (4.5, 3.8))
    # duvarlar: taban plaka + dikey kaburga + boru demetleri
    for sx in (-1, 1):
        m.box((sx * (OW / 2 + 0.1), 0, L / 2), (0.2, OH + 0.6, L), 1, 'x', (3.8, 5.2))
        for k in range(5):
            m.box((sx * (OW / 2 - 0.12), 0, 0.45 + k * (L - 0.9) / 4), (0.34, OH, 0.28), 1, 'x', (1.0, 5.2))
        for yy in (-1.5, -0.2, 1.1, 2.0):
            cyl_x(m, (sx * (OW / 2 - 0.35), yy, 0.2), (sx * (OW / 2 - 0.35), yy, L - 0.2), 0.16, 1)
        m.box((sx * (OW / 2 - 0.22), -OH / 2 + 0.5, L / 2), (0.3, 0.4, L - 0.5), 0, 'x', (3.8, 5.2))      # alt panel şeridi (kapı dokusundan sarı-siyah)
    # uçlarda sekizgen çerçeve (segment bağlantısı)
    octa_frame(m, 0.14, OW - 0.4, OH - 0.2, 0.42, 0.28, 0)
    octa_frame(m, L - 0.14, OW - 0.4, OH - 0.2, 0.42, 0.28, 0)
    return m


def door():
    m = Mesh()
    W, H = OW + 1.2, OH + 1.2
    # çerçeve halkası (derin)
    octa_frame(m, 0.0, OW, OH, 0.7, 1.0, 0, ch=1.3)
    # iki kanat: ön yüz kapı dokusu (düzlem x: XY izdüşüm, tek kanat için yarım doku)
    for sx in (-1, 1):
        r = bmesh.ops.create_cube(m.bm, size=1.0)
        bmesh.ops.transform(m.bm, matrix=Matrix.Translation((sx * OW / 4, 0, 0.1)) @ Matrix.Diagonal((OW / 2 - 0.05, OH - 0.05, 0.5, 1.0)), verts=r['verts'])
        for f in m.bm.faces:
            if not all(v in r['verts'] for v in f.verts):
                continue
            for lp in f.loops:
                p = lp.vert.co
                u = (p.x + OW / 2) / OW
                v = (p.y + OH / 2) / OH
                lp[m.uvl].uv = (0.02 + 0.46 * u, 1.0 - (0.02 + 0.46 * (1 - v)))
        # yükseltilmiş iç paneller (çerçeveli): kanat üzerinde iki kat
        for (px, py, pw, ph) in ((0, 0.9, 3.3, 1.7), (0, -0.9, 3.3, 1.7)):
            r = bmesh.ops.create_cube(m.bm, size=1.0)
            bmesh.ops.transform(m.bm, matrix=Matrix.Translation((sx * OW / 4 + px * sx * 0.0, py, 0.42)) @ Matrix.Diagonal((pw, ph, 0.12, 1.0)), verts=r['verts'])
            for f in m.bm.faces:
                if not all(v in r['verts'] for v in f.verts):
                    continue
                for lp in f.loops:
                    p = lp.vert.co
                    u = (p.x + OW / 2) / OW
                    v = (p.y + OH / 2) / OH
                    lp[m.uvl].uv = (0.02 + 0.46 * u, 1.0 - (0.02 + 0.46 * (1 - v)))
    # orta kilit gövdesi + menteşeler + uyarı lambası kutuları
    m.box((0, 0, 0.45), (0.9, 1.6, 0.35), 0, 'z', (3.0, 3.0))
    for sx in (-1, 1):
        for yy in (-1.7, 0, 1.7):
            cyl_x(m, (sx * (OW / 2 - 0.1), yy - 0.3, 0.3), (sx * (OW / 2 - 0.1), yy + 0.3, 0.3), 0.24, 0)
    for sx in (-1, 1):
        m.box((sx * 2.3, OH / 2 - 0.15, 0.5), (0.9, 0.22, 0.18), 0, 'z', (3.0, 3.0))
    return m


def finish(mesh, name, extra_scale=1.0):
    bmesh.ops.recalc_face_normals(mesh.bm, faces=mesh.bm.faces)
    me = bpy.data.meshes.new(name)
    mesh.bm.to_mesh(me)
    mesh.bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


geo.reset_scene()
cor = finish(corridor(), 'LOD0_koridor')
dor = finish(door(), 'LOD0_kapi')
# doku türetme (npc_build ile aynı mantık)
rgb = base
lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
mx, mn = rgb.max(-1), rgb.min(-1)
sat = np.where(mx > 1e-4, (mx - mn) / np.maximum(mx, 1e-4), 0)
metal = np.clip((0.55 - sat) * 1.4, 0, 1) * np.clip((lum - 0.12) * 4, 0, 1) * 0.55
rough = np.clip(0.80 - 0.34 * lum + 0.12 * sat, 0.30, 0.95)
orm = np.ones((TEX, TEX, 3), np.float32)
orm[..., 1] = rough
orm[..., 2] = metal
em = ((mx > 0.70) & (sat > 0.45)).astype(np.float32)
em = np.array(Image.fromarray((em * 255).astype(np.uint8)).filter(__import__('PIL.ImageFilter', fromlist=['x']).MaxFilter(3))) / 255.0
emis = rgb * em[..., None]


def mkimg(name, arr3, non_color):
    h, w = arr3.shape[:2]
    im = bpy.data.images.new(name, w, h, alpha=False)
    if non_color:
        im.colorspace_settings.name = 'Non-Color'
    a4 = np.concatenate([np.clip(arr3, 0, 1), np.ones((h, w, 1), np.float32)], -1)[::-1]
    im.pixels = a4.astype(np.float32).ravel().tolist()
    return im


img_b = mkimg('sd_hangar_base', base, False)
orm_s = np.array(Image.fromarray((np.clip(orm, 0, 1) * 255).astype(np.uint8)).resize((512, 512), Image.LANCZOS)).astype(np.float32) / 255.0
img_o = mkimg('sd_hangar_orm', orm_s, True)
e_s = np.array(Image.fromarray((np.clip(emis, 0, 1) * 255).astype(np.uint8)).resize((512, 512), Image.LANCZOS)).astype(np.float32) / 255.0
img_e = mkimg('sd_hangar_emit', e_s, False)
mat = B.gltf_body_material('MAT_hangar_ankora', img_b, img_o, None, img_e)
tris = {}
metas = {}
for ob, nm in ((cor, 'koridor'), (dor, 'kapi')):
    B.assign_single(ob, mat)
    geo.set_smooth_by_angle(ob, 40)
    bm = bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.triangulate(bm, faces=bm.faces); bm.to_mesh(ob.data); bm.free()
    tris[nm] = len(ob.data.polygons)
for ob, nm in ((cor, 'koridor'), (dor, 'kapi')):
    # oyun uzayı: Blender (x yanal, y boy, z yukarı) → modelde z boy; burada Blender'da (x, y_yukarı, z_boy) kurduk: glTF Y-up'a doğrudan: Blender (x, -z_boy?, y_up)
    # kurulumda koordinat (x yanal, y yukarı, z boy) kullanıldı; Blender → glTF dönüşümü (x, z, -y) olduğundan önce (x, y, z) → Blender (x, -z, y)
    for v in ob.data.vertices:
        v.co = Vector((v.co.x, -v.co.z, v.co.y))
    ob.data.update()
    root = export.empty('SD_hangar_' + nm)
    ob.parent = root
    objs = [root, ob]
    for o in objs:
        for k in [k for k in o.keys() if k.startswith('sd_')]:
            del o[k]
    glb = os.path.join(out, 'hangar_%s_ankora.glb' % nm)
    export.export_glb(glb, objs, quality=90)
    sz, rec = glbpack.recompress_textures(glb)
    metas[nm] = {'bytes': sz, 'tris': tris[nm]}
# önizleme (Blender: koridor boyu −Y, yukarı Z)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'model.blend'), compress=True)
sc = bpy.context.scene
R.rig_neutral()
cd = bpy.data.cameras.new('c'); cd.type = 'PERSP'; cd.lens = 28
cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
# koridor: iç görünüm (başlangıçtan boyuna bakış); kapı: önden
# önizleme: koridor modülü 3 kez tekrarlanır + sonda kapı (oyundaki 6 segment yerine kısa); GLB'de tek modül
for i_ in (1, 2):
    c2 = cor.copy(); c2.data = cor.data; bpy.context.scene.collection.objects.link(c2); c2.location = (0, -XSEG * i_, 0); c2.name = 'prev_cor%d' % i_
d2 = dor.copy(); d2.data = dor.data; bpy.context.scene.collection.objects.link(d2); d2.location = (0, -XSEG * 3, 0); d2.name = 'prev_door'
dor.hide_render = True
cor.hide_render = False
cam.location = (1.8, 0.8, -1.2)
cam.rotation_euler = (Vector((-0.06, -1, 0.03))).to_track_quat('-Z', 'Y').to_euler()
R.render(os.path.join(out, 'm_koridor.png'), cam, (1000, 560), 24, view='Standard', transparent=False, bounces=1)
for o_ in bpy.data.objects:
    if o_.name.startswith('prev_cor'): o_.hide_render = True
cor.hide_render = True; dor.hide_render = False; d2.hide_render = True
cam.location = (0, 9.5, 0.0)
cam.rotation_euler = Vector((0, -1, 0)).to_track_quat('-Z', 'Y').to_euler()
R.render(os.path.join(out, 'm_kapi.png'), cam, (1000, 560), 24, view='Standard', transparent=False, bounces=1)
cam.location = (7.5, 8, 3.5)
cam.rotation_euler = (Vector((0, 0, 0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
R.render(os.path.join(out, 'm_kapi_aci.png'), cam, (1000, 560), 24, view='Standard', transparent=False, bounces=1)
json.dump({'parcalar': metas, 'seconds': round(time.time() - t_start, 1)}, open(os.path.join(out, 'meta.json'), 'w'), indent=1)
print('RESULT', json.dumps({'parcalar': metas, 'seconds': round(time.time() - t_start, 1)}))
