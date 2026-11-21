"""Gemi modelleme yardımcıları (oyun uzayı: x yanal, y yukarı, z burun +; çıktı Blender'a g2b ile taşınır).
Kullanım: K = Kit(PAL); K.box(...), K.loft(...), K.cyl(...), K.poly_slab(...); K.to_blender(); K.render(out, views, radius)"""
import os, math
import bpy, bmesh
from mathutils import Vector, Matrix
from . import geo, render as R


class Kit:
    def __init__(self, pal):
        self.pal = pal
        self.BM = {k: bmesh.new() for k in pal}
        self.noreno = set()

    def box(self, c, s, mat, bev=0.004, rx=0.0):
        bm = self.BM[mat]
        r = bmesh.ops.create_cube(bm, size=1.0)
        M = Matrix.Translation(Vector(c)) @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Diagonal((*s, 1.0))
        bmesh.ops.transform(bm, matrix=M, verts=r['verts'])
        if bev > 0:
            bmesh.ops.bevel(bm, geom=list({e for v in r['verts'] for e in v.link_edges}), offset=bev, segments=1, affect='EDGES')

    def loft(self, secs, mat, cap=True):
        """kesitler: (z, yarı_genişlik_üst, yarı_genişlik_alt, üst_y, alt_y, x0) — 6 köşeli kesit (üst düz, yan omuz, alt dar)"""
        bm = self.BM[mat]
        rings = []
        for z, wu, wd, yu, yd, x0 in secs:
            ws = max(wu, wd) * 1.0
            ym = (yu + yd) / 2 + (yu - yd) * 0.05
            pts = [(-wu, yu), (wu, yu), (ws, ym), (wd, yd), (-wd, yd), (-ws, ym)]
            rings.append([bm.verts.new((x0 + x, y, z)) for x, y in pts])
        n = 6
        for r0, r1 in zip(rings, rings[1:]):
            for i in range(n):
                j = (i + 1) % n
                bm.faces.new([r0[j], r0[i], r1[i], r1[j]])
        if cap:
            bm.faces.new(rings[0]); bm.faces.new(rings[-1][::-1])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def slab(self, pts, y0, y1, mat, y1_pts=None):
        """çokgen levha: pts=(x,z) listesi (saat yönü fark etmez), y0 alt, y1 üst (kanat)"""
        bm = self.BM[mat]
        top = [bm.verts.new((x, y1, z)) for x, z in pts]
        bot = [bm.verts.new((x, y0, z)) for x, z in pts]
        bm.faces.new(top); bm.faces.new(bot[::-1])
        for i in range(len(pts)):
            j = (i + 1) % len(pts)
            bm.faces.new([top[j], top[i], bot[i], bot[j]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def cyl(self, p0, p1, r0, mat, r1=None, seg=16, cap=True):
        bm = self.BM[mat]
        d = Vector(p1) - Vector(p0)
        M = Matrix.Translation((Vector(p0) + Vector(p1)) / 2) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=seg, radius1=r0, radius2=r0 if r1 is None else r1, depth=d.length, matrix=M)

    def to_blender(self):
        geo.reset_scene()
        mats = {}
        for k, (col, rough, metal, em) in self.pal.items():
            m = bpy.data.materials.new('M_' + k)
            m.use_nodes = True
            b = m.node_tree.nodes['Principled BSDF']
            b.inputs['Base Color'].default_value = (*col, 1)
            b.inputs['Roughness'].default_value = rough
            b.inputs['Metallic'].default_value = metal
            if em:
                b.inputs['Emission Color'].default_value = (*em[:3], 1)
                b.inputs['Emission Strength'].default_value = em[3]
            mats[k] = m
        objs = []
        for k, bm in self.BM.items():
            if not bm.verts:
                continue
            for v in bm.verts:
                v.co = geo.g2b(v.co)
            if k not in self.noreno:
                bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            me = bpy.data.meshes.new(k)
            bm.to_mesh(me)
            ob = bpy.data.objects.new('P_' + k, me)
            bpy.context.scene.collection.objects.link(ob)
            ob.data.materials.append(mats[k])
            geo.set_smooth_by_angle(ob, 35)
            objs.append(ob)
        return objs

    def render(self, out, views, radius=0.7, res=(1000, 620), samples=40, fov=32.0, look=(0, 0, 0)):
        R.rig_lookdev(radius)
        for key, loc in views.items():
            cam = R.camera('c_' + key, loc, look, fov)
            R.render(os.path.join(out, 'konsept_%s.png' % key), cam, res, samples, transparent=False)
