"""Ortak yardımcılar. Oyun uzayı (x sağ, y yukarı, -z ileri) ↔ Blender (X sağ, Y ileri, Z yukarı)."""
import bpy, bmesh, json, math, os
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
COCKPIT = os.path.abspath(os.path.join(HERE, '..', '..'))

def load_json(rel):
    return json.load(open(os.path.join(COCKPIT, rel), encoding='utf-8'))

def g2b(p):
    x, y, z = p
    return Vector((x, -z, y))

class Cam:
    """Pilot kamerası (oyun rehber kamerasıyla aynı): dikey FOV 74°, asal nokta (800, 239.5) / 1600x656."""
    def __init__(self, a):
        c = a['camera']; self.f = c['focal_px']; self.cx, self.cy = c['principal']
    def ray(self, u, v):
        d = Vector(((u - self.cx) / self.f, -(v - self.cy) / self.f, -1.0)); d.normalize(); return d
    def proj(self, p):   # oyun uzayı 3B → 1600x656 piksel
        x, y, z = p; return (self.cx + self.f * x / -z, self.cy - self.f * y / -z)

def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def coll(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c

def obj_from_bm(name, bm, mat=None, collection='Cockpit', smooth=False):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); coll(collection).objects.link(ob)
    if mat: ob.data.materials.append(mat)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    return ob

def obj_from_pydata(name, verts, faces, mat=None, collection='Cockpit'):
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], faces); me.update()
    ob = bpy.data.objects.new(name, me); coll(collection).objects.link(ob)
    if mat: ob.data.materials.append(mat)
    return ob

def solidify_radial(bm, thk, eye=Vector((0, 0, 0))):
    """Açık yüzeyi, göz noktasından uzaklaşan yönde kalınlaştırıp kapalı bir katı yapar (kalınlık ışın boyunca)."""
    faces = list(bm.faces)
    ret = bmesh.ops.extrude_face_region(bm, geom=faces)
    nv = [g for g in ret['geom'] if isinstance(g, bmesh.types.BMVert)]
    for v in nv:
        d = v.co - eye; l = d.length
        v.co = eye + d * (1 + thk / max(l, 1e-6))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return bm

def apply_modifier(ob, mod):
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.selected_objects: o.select_set(False)
    ob.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)

def boolean(ob, other, op='DIFFERENCE', solver='EXACT'):
    m = ob.modifiers.new('bool', 'BOOLEAN'); m.operation = op; m.solver = solver; m.object = other
    apply_modifier(ob, m)

def bevel(ob, width=0.006, seg=2, angle=40, apply=True):
    m = ob.modifiers.new('bevel', 'BEVEL'); m.width = width; m.segments = seg; m.limit_method = 'ANGLE'; m.angle_limit = math.radians(angle); m.harden_normals = False
    if apply: apply_modifier(ob, m)
    return m

def tri_count(obs):
    dg = bpy.context.evaluated_depsgraph_get(); n = 0
    for o in obs:
        if o.type != 'MESH': continue
        ev = o.evaluated_get(dg); me = ev.to_mesh(); me.calc_loop_triangles(); n += len(me.loop_triangles); ev.to_mesh_clear()
    return n


def smooth_by_angle(obs, deg=35):
    for o in bpy.context.selected_objects: o.select_set(False)
    for o in obs:
        if o.type != 'MESH': continue
        bpy.context.view_layer.objects.active = o; o.select_set(True)
        try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(deg))
        except Exception:
            for p in o.data.polygons: p.use_smooth = True
        o.select_set(False)
