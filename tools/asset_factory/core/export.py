"""GLB dışa aktarım (bpy) — STANDARDS.md §3, §5, §6 sözleşmesi:
  SD_<id> (extras: meta)
    ├─ LOD0 ─ LOD0_body, LOD0_emit
    ├─ LOD1 ─ ...
    ├─ LOD2 ─ ...
    └─ SOCK_<tür>_<n> (extras: yön, renk ...)
Dokular WebP (EXT_texture_webp). Fabrikanın iç özellikleri (sd_*) dışa aktarımdan önce silinir."""
import bpy, os
from mathutils import Vector


def empty(name, parent=None, loc=(0, 0, 0), props=None, coll=None):
    ob = bpy.data.objects.new(name, None)
    (coll or bpy.context.scene.collection).objects.link(ob)
    ob.location = loc
    if parent:
        ob.parent = parent
    for k, v in (props or {}).items():
        ob[k] = v
    return ob


def socket(root, name, loc_b, dir_b=(0, 1, 0), extras=None):
    """Soket: konum ve yön Blender uzayında verilir; glTF düğümünün yerel −Z ekseni bu yönü gösterir.
    Dikkat: glTF dışa aktarıcısı (Y-up) düğümün yerel eksenlerini de dönüştürür: glTF yerel −Z = Blender yerel +Y.
    Bu yüzden Blender'da yerel +Y yöne hizalanır. (Faz 0 raporunda bulunan hata: önceden −Z hizalanıyordu.)"""
    ob = empty(name, root, loc_b)
    ob.empty_display_type = 'SINGLE_ARROW'
    d = Vector(dir_b).normalized()
    ob.rotation_euler = d.to_track_quat('Y', 'Z' if abs(d.z) < 0.99 else 'X').to_euler()
    for k, v in (extras or {}).items():
        ob[k] = v
    return ob


def strip_internal_props(objs):
    for o in objs:
        for k in [k for k in o.keys() if k.startswith('sd_')]:
            del o[k]
    for m in bpy.data.materials:
        for k in [k for k in m.keys() if k.startswith('sd_')]:
            del m[k]


def export_glb(path, objs, quality=90):
    bpy.context.view_layer.update()
    for o in bpy.context.view_layer.objects:
        if o is not None:
            o.select_set(False)
    for o in objs:
        if o is not None:
            o.select_set(True)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_apply=True,
                              export_image_format='WEBP', export_image_quality=quality, export_extras=True,
                              export_yup=True, export_tangents=False, export_cameras=False, export_lights=False,
                              export_materials='EXPORT', export_vertex_color='NONE', export_attributes=False)
    return os.path.getsize(path)
