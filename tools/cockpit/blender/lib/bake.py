"""AO / normal / taban renk / pürüzlülük bake ve GLB dışa aktarım (PBR dokulu, JPEG, mobil bütçe).
Yan ürün: tüm opak parçalar tek gövdede birleşir, tek UV atlası (Smart UV Project) kullanılır; ekranlar ve emissive şeritler ayrı kalır."""
import bpy, math, os
import numpy as np
from .common import *

METALLIC = {'M_gunmetal': 1.0, 'M_dark_steel': 1.0, 'M_titanium': 1.0, 'M_aluminum': 1.0, 'M_composite': 0.35, 'M_leather': 0.0}

def _set_bake_target(mats, img):
    for m in mats:
        nt = m.node_tree
        node = nt.nodes.get('BAKE_IMG') or nt.nodes.new('ShaderNodeTexImage'); node.name = 'BAKE_IMG'; node.image = img
        for n in nt.nodes: n.select = False
        node.select = True; nt.nodes.active = node

def join_body():
    keep = [o for o in coll('Cockpit').objects if o.type == 'MESH' and not o.name.startswith('SCR_') and not o.name.startswith('Detail_strip')]
    for o in bpy.context.selected_objects: o.select_set(False)
    for o in keep: o.select_set(True)
    bpy.context.view_layer.objects.active = keep[0]; bpy.ops.object.join()
    body = bpy.context.view_layer.objects.active; body.name = 'Cockpit_Body'; body.data.name = 'Cockpit_Body'
    # kullanılmayan malzeme yuvalarını sil
    bpy.ops.object.material_slot_remove_unused()
    return body

def unwrap(body, margin=0.002):
    bpy.context.view_layer.objects.active = body; body.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=margin, area_weight=0.4)
    bpy.ops.object.mode_set(mode='OBJECT')

def bake_all(body, size=2048, samples=24, log=print):
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = samples; sc.cycles.use_denoising = False
    bk = sc.render.bake; bk.margin = 10; bk.margin_type = 'EXTEND'; bk.use_clear = True; bk.use_selected_to_active = False
    mats = [s.material for s in body.material_slots if s.material]
    imgs = {}
    def mk(name, cs='Non-Color'):
        im = bpy.data.images.new(name, size, size, alpha=False); im.colorspace_settings.name = cs; return im
    plan = [('ao', 'AO', 'Non-Color'), ('base', 'DIFFUSE', 'sRGB'), ('rough', 'ROUGHNESS', 'Non-Color'), ('normal', 'NORMAL', 'Non-Color')]
    for key, typ, cs in plan:
        im = mk('bk_' + key, cs); imgs[key] = im; _set_bake_target(mats, im)
        bpy.context.view_layer.objects.active = body
        for o in bpy.context.selected_objects: o.select_set(False)
        body.select_set(True)
        if typ == 'DIFFUSE': bk.use_pass_direct = False; bk.use_pass_indirect = False; bk.use_pass_color = True
        if typ == 'AO': sc.cycles.samples = max(samples, 48)
        else: sc.cycles.samples = samples if typ != 'NORMAL' else 4
        saved = []
        if typ == 'DIFFUSE':   # tam metal yüzeyde difüz renk geçişi siyah çıkar: taban rengi için metaliği geçici sıfırla
            for m in mats:
                for n in m.node_tree.nodes:
                    if n.type == 'BSDF_PRINCIPLED': saved.append((n, n.inputs['Metallic'].default_value)); n.inputs['Metallic'].default_value = 0.0
        log('bake', typ); bpy.ops.object.bake(type=typ)
        for n, v in saved: n.inputs['Metallic'].default_value = v
    return imgs

def _px(im):
    a = np.array(im.pixels[:], dtype=np.float32); return a.reshape(im.size[1], im.size[0], 4)

def compose_orm(imgs, size):
    ao = _px(imgs['ao']); ro = _px(imgs['rough']); orm = np.ones((size, size, 4), np.float32)
    orm[..., 0] = np.clip(ao[..., 0] * 1.05, 0, 1); orm[..., 1] = ro[..., 0]; orm[..., 2] = 1.0
    im = bpy.data.images.new('bk_orm', size, size, alpha=False); im.colorspace_settings.name = 'Non-Color'; im.pixels = orm.ravel().tolist(); return im

def occlusion_group():
    g = bpy.data.node_groups.get('glTF Material Output')
    if g: return g
    g = bpy.data.node_groups.new('glTF Material Output', 'ShaderNodeTree')
    g.interface.new_socket('Occlusion', in_out='INPUT', socket_type='NodeSocketFloat'); return g

def rebuild_materials(body, imgs, orm):
    """Her malzemeyi basit PBR'ye çevir: taban renk, ORM (R=AO, G=pürüzlülük, B=1), normal haritası. Metalik katsayı malzemeye göre."""
    grp = occlusion_group()
    for slot in body.material_slots:
        old = slot.material
        if not old: continue
        nm = old.name; m = bpy.data.materials.new(nm + '_baked'); m.use_nodes = True; nt = m.node_tree
        for n in list(nt.nodes): nt.nodes.remove(n)
        out = nt.nodes.new('ShaderNodeOutputMaterial'); b = nt.nodes.new('ShaderNodeBsdfPrincipled')
        tb = nt.nodes.new('ShaderNodeTexImage'); tb.image = imgs['base']
        to = nt.nodes.new('ShaderNodeTexImage'); to.image = orm
        tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = imgs['normal']
        sep = nt.nodes.new('ShaderNodeSeparateColor'); nm_ = nt.nodes.new('ShaderNodeNormalMap'); gn = nt.nodes.new('ShaderNodeGroup'); gn.node_tree = grp
        nt.links.new(tb.outputs['Color'], b.inputs['Base Color']); nt.links.new(to.outputs['Color'], sep.inputs['Color'])
        nt.links.new(sep.outputs['Green'], b.inputs['Roughness']); nt.links.new(sep.outputs['Red'], gn.inputs['Occlusion'])
        base = nm.replace('_baked', '')
        if METALLIC.get(base, 1.0) >= 0.99: nt.links.new(sep.outputs['Blue'], b.inputs['Metallic'])
        else: b.inputs['Metallic'].default_value = METALLIC.get(base, 0.0)
        nt.links.new(tn.outputs['Color'], nm_.inputs['Color']); nt.links.new(nm_.outputs['Normal'], b.inputs['Normal']); nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
        slot.material = m

def export_glb(path, quality=85):
    for o in bpy.context.selected_objects: o.select_set(False)
    objs = [o for o in coll('Cockpit').objects if o.type == 'MESH']
    for o in objs: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_apply=True, export_image_format='JPEG', export_jpeg_quality=quality,
                              export_yup=True, export_materials='EXPORT', export_cameras=False, export_lights=False)
    return os.path.getsize(path)
