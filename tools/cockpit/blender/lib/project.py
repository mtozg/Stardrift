"""Sınırlı kamera-projeksiyon: onaylı çizim, pilot kamerasından yalnızca görünür ve yüze dönük köşelere (ağırlıkla) detay olarak karışır.
Her köşeye 'ProjUV' (çizim koordinatı) ve 'projw' (karışım ağırlığı) yazılır; malzeme bunları taban renge karıştırır. Kaplama yüzeye bake edilir,
dolayısıyla kamera oynayınca yüzeyden kopmaz. Pencere/ekran (alfa=0) bölgeleri ve gizli/yan bakan yüzler çizimden etkilenmez."""
import bpy, os
import numpy as np
from mathutils import Vector
from PIL import Image
from .common import *
from . import materials

PREFIX_W = None   # params['proj'] ile gelir: nesne adı öneki → ağırlık

def load_drawing(path, outdir):
    """Çizimden DETAY haritası: R = yüksek geçiren (çizik, panel hattı, perçin kenarı), G = orta frekans lekelenme; 0.5 = nötr.
    Pencere/ekran (alfa=0) ve kenarlarında nötr. Büyük şekiller, ışık ve gölge taşınmaz."""
    import scipy.ndimage as ndi
    im = Image.open(path).convert('RGBA'); arr = np.asarray(im).astype(np.float32) / 255.0
    L = arr[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32); A = arr[..., 3]
    ok = ndi.binary_erosion(A > 0.5, iterations=6)
    b5 = ndi.gaussian_filter(L, 3.0); b25 = ndi.gaussian_filter(L, 22.0)
    hp = np.clip((L - b5) / 0.10, -1, 1); mid = np.clip((b5 - b25) / 0.12, -1, 1)
    hp = np.where(ok, hp, 0.0); mid = np.where(ok, mid, 0.0)
    det = np.dstack([0.5 + 0.5 * hp, 0.5 + 0.5 * mid, np.full_like(hp, 0.5)])
    dp = os.path.join(outdir, 'drawing_detail.png'); Image.fromarray((det * 255 + 0.5).astype(np.uint8)).save(dp)
    bi = bpy.data.images.load(dp); bi.colorspace_settings.name = 'Non-Color'
    materials.PROJ['img'] = bi; return np.dstack([arr[..., :3], ok.astype(np.float32)])

def _obj_strength(name, table):
    best = None
    for k, v in table.items():
        if name.startswith(k) and (best is None or len(k) > len(best[0])): best = (k, v)
    return best[1] if best else 0.0

def apply(a, arr, table):
    import bmesh
    cam = Cam(a); H, W = arr.shape[:2]; dg = bpy.context.evaluated_depsgraph_get(); sc = bpy.context.scene
    objs = [o for o in coll('Cockpit').objects if o.type == 'MESH' and not o.name.startswith(('SCR_', 'Detail_strip'))]
    tot = 0; vis_n = 0
    for ob in objs:
        me = ob.data; strength = _obj_strength(ob.name, table)
        if 'ProjUV' not in me.uv_layers: me.uv_layers.new(name='ProjUV')
        uvl = me.uv_layers['ProjUV']; nv = len(me.vertices); vuv = np.zeros((nv, 2), np.float32)
        M = ob.matrix_world; M3 = M.to_3x3()
        for i, v in enumerate(me.vertices):
            pb = M @ v.co; pg = Vector((pb.x, pb.z, -pb.y))
            if pg.z > -0.02: continue
            u, vv = cam.proj(pg); vuv[i] = (u / 1600.0, 1.0 - vv / 656.0)
        wts = np.zeros(nv, np.float32) + 1.0
        if strength <= 0: wts[:] = 0.0
        else:
            bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.normal_update()
            fw = {}
            for f in bm.faces:
                c = M @ f.calc_center_median(); d = c.length
                if d < 0.05: fw[f.index] = 0.0; continue
                nrm = (M3 @ f.normal); nrm.normalize(); facing = nrm.dot(-c / d)
                w = smoothstep(0.5, 0.82, facing)          # yalnızca göze neredeyse dik bakan yüzler (esneme yok)
                if w <= 0: fw[f.index] = 0.0; continue
                # yüzdeki en uç köşelerin kamera koordinatları arasındaki çarpılma: UV alanı / gerçek alan oranı
                px = int(min(W - 1, max(0, vuv[f.verts[0].index][0] * W))); py = int(min(H - 1, max(0, (1 - vuv[f.verts[0].index][1]) * H)))
                if arr[py, px, 3] < 0.5: fw[f.index] = 0.0; continue
                hit, loc, nor, idx, ho, mat = sc.ray_cast(dg, Vector((0, 0, 0)), c / d, distance=d + 0.05)
                if hit and loc.length < d - 0.012: fw[f.index] = 0.0; continue
                fw[f.index] = w
            for v in bm.verts:
                wl = [fw[f.index] for f in v.link_faces]; wts[v.index] = (min(wl) if wl else 0.0) * strength
            bm.free(); vis_n += int((wts > 0.01).sum())
        tot += nv
        for li, lp in enumerate(me.loops): uvl.data[li].uv = vuv[lp.vertex_index]
        if 'projw' not in me.attributes: me.attributes.new('projw', 'FLOAT', 'POINT')
        me.attributes['projw'].data.foreach_set('value', wts.tolist())
    return tot, vis_n
