"""Geometri yardımcıları (bpy).

Koordinat sözleşmesi (GEÇİCİ, contracts/game_contract.md ile kesinleşecek):
  oyun / glTF uzayı : X sağ, Y yukarı, −Z ileri (burun)
  Blender uzayı      : X sağ, +Y ileri, Z yukarı
  g2b(x, y, z) = (x, −z, y)      b2g(X, Y, Z) = (X, Z, −Y)   (glTF dışa aktarımı Y-up dönüşümü b2g ile aynıdır)

Kural: bütün parça mesh'leri DÜNYA koordinatında kurulur (nesne dönüşümü birim). Prosedürel malzemeler
nesne koordinatı kullandığından, birleştirme (join) sonrasında desen kaymaz."""
import bpy, bmesh, math, hashlib
from mathutils import Vector, Matrix


def g2b(p):
    x, y, z = p
    return Vector((x, -z, y))


def b2g(p):
    x, y, z = p
    return (x, z, -y)


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def mesh_object(name, bm, mat=None, coll='Asset', role='body', smooth_angle=None):
    """bmesh → nesne. role: 'body' | 'emit' | 'glass' — hazırlık aşaması bunu kullanarak birleştirir."""
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    collection(coll).objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    ob['sd_role'] = role
    if smooth_angle is not None:
        set_smooth_by_angle(ob, smooth_angle)
    return ob


def set_smooth_by_angle(ob, deg):
    me = ob.data
    for p in me.polygons:
        p.use_smooth = True
    bm = bmesh.new()
    bm.from_mesh(me)
    lim = math.radians(deg)
    for e in bm.edges:
        if e.is_boundary or (len(e.link_faces) == 2 and e.calc_face_angle(0.0) > lim):
            e.smooth = False
    bm.to_mesh(me)
    bm.free()


def apply_modifier(ob, mod):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_apply(modifier=mod.name)


def bevel(ob, width, segments=2, angle=35.0):
    m = ob.modifiers.new('bevel', 'BEVEL')
    m.width = width
    m.segments = segments
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle)
    m.harden_normals = False
    apply_modifier(ob, m)


def boolean(ob, cutter, op='DIFFERENCE'):
    m = ob.modifiers.new('bool', 'BOOLEAN')
    m.operation = op
    m.solver = 'EXACT'
    m.object = cutter
    apply_modifier(ob, m)


# --- ilkel şekiller (bmesh; hepsi dünya koordinatında) -----------------------------

def bm_box(center, size, rot_z=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    M = Matrix.Translation(Vector(center)) @ Matrix.Rotation(rot_z, 4, 'Z') @ Matrix.Diagonal((*size, 1.0))
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return bm


def bm_cylinder(p0, p1, radius, segments=16, radius1=None, cap=True):
    """p0→p1 ekseni boyunca silindir/koni (radius1 verilirse koni)."""
    bm = bmesh.new()
    r1 = radius if radius1 is None else radius1
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=segments, radius1=radius, radius2=r1, depth=1.0)
    a, b = Vector(p0), Vector(p1)
    d = b - a
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    M = Matrix.Translation((a + b) / 2) @ rot @ Matrix.Diagonal((1.0, 1.0, d.length, 1.0))
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return bm


def bm_lathe(profile, axis_p0, axis_dir, segments=24):
    """profile: [(r, t)] — eksen boyunca t, yarıçap r. Dönel yüzey (motor çanı, istasyon gövdesi)."""
    bm = bmesh.new()
    ax = Vector(axis_dir).normalized()
    ref = Vector((1, 0, 0)) if abs(ax.x) < 0.9 else Vector((0, 1, 0))
    u = ax.cross(ref).normalized()
    v = ax.cross(u)
    rings = []
    for r, t in profile:
        ring = []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            ring.append(bm.verts.new(Vector(axis_p0) + ax * t + (u * math.cos(a) + v * math.sin(a)) * r))
        rings.append(ring)
    for k in range(len(rings) - 1):
        for i in range(segments):
            j = (i + 1) % segments
            bm.faces.new((rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bm_disc(center, normal, radius, segments=24):
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, cap_tris=False, segments=segments, radius=radius)
    rot = Vector((0, 0, 1)).rotation_difference(Vector(normal).normalized()).to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(center)) @ rot, verts=bm.verts)
    return bm


# --- ölçüm ------------------------------------------------------------------------

def tri_count(obs):
    dg = bpy.context.evaluated_depsgraph_get()
    n = 0
    for o in obs:
        if o.type != 'MESH':
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        n += len(me.loop_triangles)
        ev.to_mesh_clear()
    return n


def geometry_hash(obs, digits=5):
    """Tekrar üretilebilirlik: konumlar (yuvarlanmış) + yüz dizinleri + malzeme adları; nesne adına göre sıralı."""
    h = hashlib.sha256()
    for o in sorted((o for o in obs if o.type == 'MESH'), key=lambda o: o.name):
        me = o.data
        h.update(o.name.encode())
        for v in me.vertices:
            co = o.matrix_world @ v.co
            h.update(('%.*f,%.*f,%.*f;' % (digits, co.x, digits, co.y, digits, co.z)).encode())
        for p in me.polygons:
            h.update((','.join(str(i) for i in p.vertices) + '|%d;' % p.material_index).encode())
        h.update('|'.join(s.material.name if s.material else '-' for s in o.material_slots).encode())
    return h.hexdigest()


def bounds(obs):
    pts = [o.matrix_world @ Vector(c) for o in obs if o.type == 'MESH' for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi
