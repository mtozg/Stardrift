"""Pilot koltuğu (b aşaması): kapitone deri yastıklar, dikiş hatları (gerçek geometri), kenar biyesi, yan destekler,
ray ve braket bağlantıları. Çizimde alt ortada görünen koltuk bölümü; eski düz bloklar kalktı."""
import bpy, bmesh, math
from mathutils import Vector, Matrix
from .common import *
from .detail import box, cyl
from .side import tube

def rbox(name, size, loc, mat, bev=0.05, seg=4, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    ob = obj_from_bm(name, bm, mat, collection='Cockpit'); ob.location = g2b(loc); ob.rotation_euler = rot
    m = ob.modifiers.new('b', 'BEVEL'); m.width = bev; m.segments = seg; m.limit_method = 'NONE'; apply_modifier(ob, m)
    for p in ob.data.polygons: p.use_smooth = True
    return ob

def b2g(p):                      # Blender dünya → oyun uzayı
    return Vector((p.x, p.z, -p.y))

def top_outline(ob, size, inset, step):
    """Kutunun üst yüzünde dikdörtgen çevre noktaları (dünya, Blender)."""
    sx, sy, sz = size; hx, hy = sx / 2 - inset, sy / 2 - inset; z = sz / 2 + 0.002
    corners = [Vector((-hx, -hy, z)), Vector((hx, -hy, z)), Vector((hx, hy, z)), Vector((-hx, hy, z))]
    pts = []
    for i in range(4):
        A, B = corners[i], corners[(i + 1) % 4]; L = (B - A).length; n = max(1, int(L / step))
        for k in range(n): pts.append(A + (B - A) * (k / n))
    pts.append(pts[0]); return [ob.matrix_world @ p for p in pts]

def stitches(name, pts, mat, length=0.017, w=0.0035):
    out = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]; mid = (a + b) / 2; d = (b - a).normalized()
        up = Vector((0, 0, 1)); right = d; nrm = right.cross(up) if abs(right.dot(up)) < 0.9 else Vector((0, 1, 0))
        z = nrm.cross(right).normalized(); y = z.cross(right).normalized()
        R = Matrix(((right.x, y.x, z.x), (right.y, y.y, z.y), (right.z, y.z, z.z)))
        bm = bmesh.new(); hl, hw = length / 2, w / 2
        vs = [bm.verts.new(c) for c in ((-hl, -hw, 0), (hl, -hw, 0), (hl, hw, 0), (-hl, hw, 0))]; bm.faces.new(vs)
        ob = obj_from_bm('Seat_stitch', bm, mat, collection='Cockpit'); ob.location = mid + z * 0.0015; ob.rotation_euler = R.to_euler(); out.append(ob)
    return out

def build(a, P, mats):
    S = P['seat']; out = []; L = mats['leather']; T = mats['thread']; C = mats['composite']
    pieces = []
    for sx in (-1, 1):
        ob = rbox('Seat_Bolster%d' % (sx > 0), (S['bw'], S['bd'], S['bh']), (sx * S['bx'], S['y'], S['z']), L, bev=0.05, seg=5, rot=(math.radians(S['tilt']), 0, sx * math.radians(S['splay'])))
        out.append(ob); pieces.append((ob, (S['bw'], S['bd'], S['bh'])))
        # yan destek kanadı (dışa açılı, daha ince)
        w = rbox('Seat_Wing%d' % (sx > 0), (0.13, S['bd'] * 0.9, S['bh'] * 0.85), (sx * (S['bx'] + S['bw'] * 0.5 + 0.05), S['y'] - 0.015, S['z'] + 0.02), L, bev=0.04, seg=4, rot=(math.radians(S['tilt']), 0, sx * math.radians(S['splay'] + 16)))
        out.append(w); pieces.append((w, (0.13, S['bd'] * 0.9, S['bh'] * 0.85)))
    cu = rbox('Seat_Cushion', (S['cw'], S['cd'], S['ch']), (0, S['y'] - 0.05, S['z'] + 0.08), L, bev=0.045, seg=5, rot=(math.radians(S['tilt'] * 0.6), 0, 0))
    out.append(cu); pieces.append((cu, (S['cw'], S['cd'], S['ch'])))
    # kapitone panel (teknik kumaş) + dikiş hattı + biye
    for (ob, size) in pieces:
        sx, sy, sz = size
        panel = box('Seat_panel', (sx * 0.62, sy * 0.62, 0.008), Vector((0, 0, 0)), C, bev=0.003)
        panel.parent = ob; panel.location = (0, 0, sz / 2 + 0.003); panel.matrix_parent_inverse = Matrix.Identity(4); out.append(panel)
        out += stitches('st', top_outline(ob, size, 0.035, 0.026), T)                  # dış dikiş
        out += stitches('st2', top_outline(ob, (sx * 0.62, sy * 0.62, sz), 0.012, 0.022), T, 0.012, 0.003)   # panel çevresi
        pip = top_outline(ob, size, 0.012, 0.03)
        out.append(tube('Seat_piping', [b2g(p) for p in pip], 0.0055, mats['steel'], 6))
    # ray ve braketler (koltuğun altında)
    for sx in (-1, 1):
        x = sx * S['bx']
        out.append(box('Seat_rail', (0.07, 0.42, 0.03), g2b(Vector((x, S['y'] - 0.13, S['z'] - 0.0))), mats['steel'], bev=0.005))
        for dz in (-0.17, 0.17):
            out.append(box('Seat_bracket', (0.10, 0.045, 0.05), g2b(Vector((x, S['y'] - 0.12, S['z'] + dz))), mats['titanium'], bev=0.006))
            for ddx in (-0.03, 0.03): out.append(cyl('Seat_bolt', 0.007, 0.012, g2b(Vector((x + ddx, S['y'] - 0.095, S['z'] + dz))), (math.radians(90), 0, 0), mats['aluminum'], 6))
    out.append(box('Seat_frame', (S['bx'] * 2 + S['bw'] + 0.30, 0.05, 0.05), g2b(Vector((0, S['y'] - 0.13, S['z'] - 0.05))), mats['steel'], bev=0.012))
    return out
