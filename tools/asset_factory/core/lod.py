"""LOD (bpy): kopyala + collapse decimate. UV ve sert kenarlar korunmaya çalışılır."""
import bpy
from .geo import apply_modifier, tri_count


def make_lod(src, ratio, name):
    me = src.data.copy()
    me.name = name
    ob = bpy.data.objects.new(name, me)
    for c in src.users_collection:
        c.objects.link(ob)
    if ratio < 0.999:
        m = ob.modifiers.new('dec', 'DECIMATE')
        m.decimate_type = 'COLLAPSE'
        m.ratio = ratio
        m.use_collapse_triangulate = False
        apply_modifier(ob, m)
    return ob, tri_count([ob])
