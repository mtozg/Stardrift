"""Pilot koltuğu: yumuşak pahlı deri yastıklar (iki yan destek + orta oturma). Çizimde alt ortada görünen koltuk kısmı."""
import bpy, bmesh, math
from mathutils import Vector, Matrix
from .common import *

def rbox(name, size, loc, mat, bev=0.05, seg=4, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    ob = obj_from_bm(name, bm, mat, collection='Cockpit'); ob.location = g2b(loc); ob.rotation_euler = rot
    m = ob.modifiers.new('b', 'BEVEL'); m.width = bev; m.segments = seg; m.limit_method = 'NONE'; apply_modifier(ob, m)
    for p in ob.data.polygons: p.use_smooth = True
    return ob

def build(a, P, mats):
    S = P['seat']; out = []; L = mats['leather']
    # Blender ekseni: size = (X genişlik, Y derinlik, Z yükseklik); loc oyun uzayında (x, y, z)
    for sx in (-1, 1):
        out.append(rbox('Seat_Bolster%d' % (sx > 0), (S['bw'], S['bd'], S['bh']), (sx * S['bx'], S['y'], S['z']), L, bev=0.05, seg=5, rot=(math.radians(S['tilt']), 0, sx * math.radians(S['splay']))))
    out.append(rbox('Seat_Cushion', (S['cw'], S['cd'], S['ch']), (0, S['y'] - 0.05, S['z'] + 0.08), L, bev=0.045, seg=5, rot=(math.radians(S['tilt'] * 0.6), 0, 0)))
    # kenar dikişi/koruma şeridi (kompozit)
    out.append(rbox('Seat_Frame', (S['bx'] * 2 + S['bw'] + 0.08, 0.05, 0.05), (0, S['y'] - 0.13, S['z'] - 0.12), mats['composite'], bev=0.012, seg=2))
    return out
