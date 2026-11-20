"""Kanal bake (bpy) — prosedürel malzemeleri tek atlasa taşır.

Kaşif hattından farkı: taban renk, pürüzlülük ve METALİKLİK, Principled girişleri geçici olarak bir Emission düğümüne
yönlendirilerek EMIT bake ile alınır. Böylece (1) metaliği sıfırlama hilesi gerekmez, (2) metaliklik gerçek bir kanal
olur (ORM.B), (3) yöntem her malzeme grafiğinde aynı çalışır. AO ve tangent normal Cycles'ın kendi bake türleriyle alınır."""
import bpy, os
import numpy as np

CHANNELS = {  # anahtar: (Principled girişi | özel tür, renk uzayı)
    'base': ('Base Color', 'sRGB'),
    'rough': ('Roughness', 'Non-Color'),
    'metal': ('Metallic', 'Non-Color'),
    'emit': ('Emission Color', 'sRGB'),       # renk × güç (Principled'da varsayılan renk beyaz, güç 0)
    'ao': ('AO', 'Non-Color'),
    'normal': ('NORMAL', 'Non-Color'),
}


def _principled(m):
    for n in m.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            return n
    raise RuntimeError('Principled yok: ' + m.name)


def _output(m):
    for n in m.node_tree.nodes:
        if n.type == 'OUTPUT_MATERIAL':
            return n


def _target(mats, img):
    for m in mats:
        nt = m.node_tree
        node = nt.nodes.get('SD_BAKE') or nt.nodes.new('ShaderNodeTexImage')
        node.name = 'SD_BAKE'
        node.image = img
        for n in nt.nodes:
            n.select = False
        node.select = True
        nt.nodes.active = node


def _route(mats, socket_name):
    """Principled girişini Emission'a yönlendir; geri alma listesi döndür."""
    undo = []
    for m in mats:
        nt = m.node_tree
        b, out = _principled(m), _output(m)
        em = nt.nodes.new('ShaderNodeEmission')
        em.inputs['Strength'].default_value = 1.0
        src = b.inputs[socket_name]
        k = b.inputs['Emission Strength'].default_value if socket_name == 'Emission Color' else 1.0
        if socket_name == 'Emission Color' and b.inputs['Emission Strength'].is_linked:
            raise RuntimeError('bağlı emisyon gücü desteklenmiyor: ' + m.name)
        if src.is_linked and k > 0:
            em.inputs['Strength'].default_value = k
            nt.links.new(src.links[0].from_socket, em.inputs['Color'])
        else:
            v = src.default_value
            em.inputs['Color'].default_value = (v[0] * k, v[1] * k, v[2] * k, 1) if hasattr(v, '__len__') else (v, v, v, 1)
        prev = out.inputs['Surface'].links[0].from_socket
        nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
        undo.append((nt, em, prev, out))
    return undo


def _unroute(undo):
    for nt, em, prev, out in undo:
        nt.links.new(prev, out.inputs['Surface'])
        nt.nodes.remove(em)


SIZE_GROUP = {'base': 'base', 'emit': 'base', 'normal': 'normal', 'ao': 'orm', 'rough': 'orm', 'metal': 'orm'}


def bake(ob, size, samples=32, ao_samples=96, margin=12, log=print, ao_distance=None):
    """size: tek sayı ya da {'base','orm','normal'} sözlüğü (ORM kanalları aynı boyutta pişer)."""
    sizes = size if isinstance(size, dict) else {'base': size, 'orm': size, 'normal': size}
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.use_denoising = False
    bk = sc.render.bake
    bk.margin = margin
    bk.margin_type = 'EXTEND'
    bk.use_clear = True
    bk.use_selected_to_active = False
    mats = [s.material for s in ob.material_slots if s.material]
    imgs = {}
    for key, (sock, cs) in CHANNELS.items():
        sz = sizes[SIZE_GROUP[key]]
        img = bpy.data.images.new('bake_' + key, sz, sz, alpha=False, float_buffer=(key == 'normal'))
        img.colorspace_settings.name = cs
        imgs[key] = img
        _target(mats, img)
        with bpy.context.temp_override(active_object=ob, object=ob, selected_objects=[ob], selected_editable_objects=[ob]):
            if key == 'ao':
                if ao_distance:      # ayrıntı ölçekli AO (köşe/birleşim gölgesi); varsayılan dünya mesafesi (10 m) yalnız genel kapalılığı verir
                    sc.world.light_settings.distance = ao_distance
                sc.cycles.samples = ao_samples
                bpy.ops.object.bake(type='AO')
            elif key == 'normal':
                sc.cycles.samples = 8
                bk.normal_space = 'TANGENT'
                bpy.ops.object.bake(type='NORMAL')
            else:
                sc.cycles.samples = samples
                undo = _route(mats, sock)
                try:
                    bpy.ops.object.bake(type='EMIT')
                finally:
                    _unroute(undo)
        log('bake', key)
    return imgs


def pixels(img):
    a = np.array(img.pixels[:], dtype=np.float32)
    return a.reshape(img.size[1], img.size[0], 4)


def compose_orm(imgs, size):
    ao, ro, me = pixels(imgs['ao']), pixels(imgs['rough']), pixels(imgs['metal'])
    orm = np.ones((size, size, 4), np.float32)
    orm[..., 0] = np.clip(ao[..., 0], 0, 1)
    orm[..., 1] = np.clip(ro[..., 0], 0.04, 1)
    orm[..., 2] = np.clip(me[..., 0], 0, 1)
    img = bpy.data.images.new('sd_orm', size, size, alpha=False)
    img.colorspace_settings.name = 'Non-Color'
    img.pixels = orm.ravel().tolist()
    return img


def save_png(img, path):
    img.filepath_raw = path
    img.file_format = 'PNG'
    img.save()
    return path


def _occlusion_group():
    g = bpy.data.node_groups.get('glTF Material Output')
    if g is None:
        g = bpy.data.node_groups.new('glTF Material Output', 'ShaderNodeTree')
        g.interface.new_socket('Occlusion', in_out='INPUT', socket_type='NodeSocketFloat')
    return g


def gltf_body_material(name, base, orm, normal, emit=None):
    """glTF'e birebir çevrilen yalın malzeme: base + ORM(R=AO via glTF Material Output, G=rough, B=metal) + normal."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    tb, to, tn = (nt.nodes.new('ShaderNodeTexImage') for _ in range(3))
    tb.image, to.image, tn.image = base, orm, normal
    sep = nt.nodes.new('ShaderNodeSeparateColor')
    nm = nt.nodes.new('ShaderNodeNormalMap')
    grp = nt.nodes.new('ShaderNodeGroup')
    grp.node_tree = _occlusion_group()
    L = nt.links.new
    L(tb.outputs['Color'], b.inputs['Base Color'])
    L(to.outputs['Color'], sep.inputs['Color'])
    L(sep.outputs['Red'], grp.inputs['Occlusion'])
    L(sep.outputs['Green'], b.inputs['Roughness'])
    L(sep.outputs['Blue'], b.inputs['Metallic'])
    L(tn.outputs['Color'], nm.inputs['Color'])
    L(nm.outputs['Normal'], b.inputs['Normal'])
    L(b.outputs['BSDF'], out.inputs['Surface'])
    if emit is not None:
        te = nt.nodes.new('ShaderNodeTexImage')
        te.image = emit
        L(te.outputs['Color'], b.inputs['Emission Color'])
        b.inputs['Emission Strength'].default_value = 1.0
    return m


def assign_single(ob, mat):
    ob.data.materials.clear()
    ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.material_index = 0
