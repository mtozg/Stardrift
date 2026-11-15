"""Sınırlı kamera-projeksiyon: onaylı çizim, pilot kamerasından yalnızca görünür ve yüze dönük köşelere (ağırlıkla) detay olarak karışır.
Her köşeye 'ProjUV' (çizim koordinatı) ve 'projw' (karışım ağırlığı) yazılır; malzeme bunları taban renge karıştırır. Kaplama yüzeye bake edilir,
dolayısıyla kamera oynayınca yüzeyden kopmaz. Pencere/ekran (alfa=0) bölgeleri ve gizli/yan bakan yüzler çizimden etkilenmez."""
import bpy, os
import numpy as np
from mathutils import Vector
from PIL import Image
from .common import *
from . import materials

def load_drawing(path):
    im = Image.open(path).convert('RGBA'); arr = np.asarray(im).astype(np.float32) / 255.0
    bi = bpy.data.images.load(path); bi.colorspace_settings.name = 'sRGB'; bi.alpha_mode = 'STRAIGHT'
    materials.PROJ['img'] = bi; return arr

def apply(a, arr, only=None):
    cam = Cam(a); H, W = arr.shape[:2]; dg = bpy.context.evaluated_depsgraph_get(); sc = bpy.context.scene
    objs = [o for o in coll('Cockpit').objects if o.type == 'MESH' and not o.name.startswith(('SCR_', 'Detail_strip'))]
    tot = 0; vis_n = 0
    for ob in objs:
        me = ob.data
        if 'ProjUV' not in me.uv_layers: me.uv_layers.new(name='ProjUV')
        uvl = me.uv_layers['ProjUV']; nv = len(me.vertices); vuv = np.zeros((nv, 2), np.float32); wts = np.zeros(nv, np.float32)
        M = ob.matrix_world; M3 = M.to_3x3()
        for i, v in enumerate(me.vertices):
            pb = M @ v.co; pg = Vector((pb.x, pb.z, -pb.y))       # Blender → oyun uzayı
            if pg.z > -0.02: vuv[i] = (0, 0); continue
            u, vv = cam.proj(pg); vuv[i] = (u / 1600.0, 1.0 - vv / 656.0)
            nb = (M3 @ v.normal); nb.normalize(); view = (-pb).normalized(); facing = max(0.0, nb.dot(view))
            if facing <= 0.05: continue
            px = int(min(W - 1, max(0, u * W / 1600.0))); py = int(min(H - 1, max(0, vv * H / 656.0)))
            if arr[py, px, 3] < 0.5: continue
            d = pb.length; hit, loc, nor, idx, ho, mat = sc.ray_cast(dg, Vector((0, 0, 0)), pb / d, distance=d + 0.05)
            if hit and loc.length < d - 0.014: continue            # önünde başka geometri var: bu köşe pilot için görünmüyor
            wts[i] = smoothstep(0.12, 0.5, facing); vis_n += 1
        tot += nv
        for li, lp in enumerate(me.loops): uvl.data[li].uv = vuv[lp.vertex_index]
        if 'projw' not in me.attributes: me.attributes.new('projw', 'FLOAT', 'POINT')
        me.attributes['projw'].data.foreach_set('value', wts.tolist())
    return tot, vis_n
