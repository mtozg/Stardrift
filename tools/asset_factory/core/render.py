"""Render (bpy): iki ışık düzeni.
  lookdev  — görsel inceleme (Kapı 1): uzay gradyanı + yıldızlar, softbox anahtar/kenar ışıkları, AgX.
  neutral  — motor sadakati referansı (L3): düz renkli dünya + tek güneş, 'Standard' görüntü dönüşümü.
             Three r128 tarafında birebir karşılığı kurulabilir: ortam = float düz equirect (radyans C),
             DirectionalLight yoğunluğu = güneş gücü / π (r128, physicallyCorrectLights=false). Deneyle doğrulandı.
Nötr düzende güneş gölge düşürmez (Three tarafında gölge haritası yok); yakın temas gölgesini her iki tarafta AO verir.
Kameralar oyun uzayında JSON'a yazılır; Three sayfası aynı kamerayı kurar."""
import bpy, math
from mathutils import Vector
from .geo import b2g

NEUTRAL = {'ambient': [0.10, 0.105, 0.115], 'sun_strength': 3.2, 'sun_dir_game': [-0.45, -0.70, -0.55], 'sun_color': [1.0, 0.97, 0.92]}


def _world():
    w = bpy.data.worlds.get('SD_World') or bpy.data.worlds.new('SD_World')
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    return w, nt


def world_space(strength=1.0):
    """Lookdev dünyası: yukarı açılan soğuk gradyan + seyrek yıldızlar (oyunun uzay tonu)."""
    w, nt = _world()
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Generated'], sep.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.30, (0.004, 0.005, 0.010, 1)
    e[1].position, e[1].color = 1.0, (0.16, 0.22, 0.38, 1)
    mid = e.new(0.55)
    mid.color = (0.02, 0.03, 0.06, 1)
    vo = nt.nodes.new('ShaderNodeTexVoronoi')
    vo.inputs['Scale'].default_value = 260.0
    nt.links.new(tc.outputs['Generated'], vo.inputs['Vector'])
    st = nt.nodes.new('ShaderNodeMapRange')
    st.inputs['From Min'].default_value = 0.03
    st.inputs['From Max'].default_value = 0.01
    nt.links.new(vo.outputs['Distance'], st.inputs['Value'])
    add = nt.nodes.new('ShaderNodeMix')
    add.data_type = 'RGBA'
    add.blend_type = 'ADD'
    add.inputs['Factor'].default_value = 1.0
    nt.links.new(ramp.outputs['Color'], add.inputs['A'])
    nt.links.new(st.outputs['Result'], add.inputs['B'])
    nt.links.new(add.outputs['Result'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = strength
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])


def world_uniform(color):
    w, nt = _world()
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.inputs['Color'].default_value = (*color, 1)
    bg.inputs['Strength'].default_value = 1.0
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])


def clear_lights():
    for o in list(bpy.data.objects):
        if o.type == 'LIGHT':
            bpy.data.objects.remove(o)


def light(kind, loc, energy, color=(1, 1, 1), size=1.0, look=(0, 0, 0), name='L'):
    d = bpy.data.lights.new(name, kind)
    d.energy = energy
    d.color = color
    if kind == 'AREA':
        d.size = size
    if kind == 'SUN':
        d.angle = math.radians(size)
    ob = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(look) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


def rig_lookdev(radius):
    """Softbox düzeni: sıcak anahtar (sol üst ön), soğuk kenar (sağ arka), zayıf alt dolgu. radius: varlık yarıçapı."""
    clear_lights()
    world_space(0.8)
    r = max(radius, 0.1)
    k = r * r
    light('AREA', (-2.2 * r, -2.4 * r, 2.4 * r), 160 * k, (1.0, 0.94, 0.86), 2.0 * r, name='Key')
    light('AREA', (2.6 * r, 2.2 * r, 1.6 * r), 120 * k, (0.60, 0.76, 1.0), 1.6 * r, name='Rim')
    light('AREA', (0.5 * r, -2.0 * r, -1.8 * r), 18 * k, (0.75, 0.82, 1.0), 2.5 * r, name='Fill')


def rig_neutral(cfg=NEUTRAL):
    clear_lights()
    world_uniform(cfg['ambient'])
    from .geo import g2b
    d = g2b(cfg['sun_dir_game']).normalized()      # ışığın gittiği yön
    sun = light('SUN', tuple(-d * 10), cfg['sun_strength'], tuple(cfg['sun_color']), 0.5, look=(0, 0, 0), name='Sun')
    sun.data.use_shadow = False      # oyun mobilde gerçek zamanlı gölge kullanmıyor (GEÇİCİ); temas gölgesi pişmiş AO'dan gelir


def camera(name, loc, look, fovy_deg=35.0, ortho_scale=None):
    cd = bpy.data.cameras.new(name)
    cd.sensor_fit = 'VERTICAL'
    cd.sensor_height = 24.0
    if ortho_scale:
        cd.type = 'ORTHO'
        cd.ortho_scale = ortho_scale
    else:
        cd.lens = 12.0 / math.tan(math.radians(fovy_deg / 2))
    cd.clip_start = 0.01
    cd.clip_end = 500
    ob = bpy.data.objects.new(name, cd)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    up = 'Y'
    dvec = Vector(look) - Vector(loc)
    if abs(dvec.normalized().z) > 0.999:      # tam üstten/alttan bakış: yukarı ekseni +Y (Blender ileri)
        ob.rotation_euler = dvec.to_track_quat('-Z', 'Y').to_euler()
    else:
        ob.rotation_euler = dvec.to_track_quat('-Z', up).to_euler()
    ob['sd_look'] = list(look)
    ob['sd_fovy'] = fovy_deg
    return ob


def camera_json(ob, res):
    """Kamerayı oyun/glTF uzayında tarif et (Three tarafı için)."""
    M = ob.matrix_world
    pos = M.translation
    fwd = (M.to_3x3() @ Vector((0, 0, -1))).normalized()
    up = (M.to_3x3() @ Vector((0, 1, 0))).normalized()
    cd = ob.data
    j = {'name': ob.name, 'position': b2g(pos), 'target': b2g(pos + fwd), 'up': b2g(up), 'width': res[0], 'height': res[1]}
    if abs(cd.shift_y) > 1e-6:
        j['shift_y'] = cd.shift_y      # Three: setViewOffset(w, h, 0, −shift_y·h, w, h) (dikey sensör uyumu)
    if cd.type == 'ORTHO':
        j['ortho_height'] = cd.ortho_scale if res[1] >= res[0] else cd.ortho_scale * res[1] / res[0]
    else:
        j['fovy'] = math.degrees(2 * math.atan(12.0 / cd.lens))
    return j


def render(path, cam, res, samples=64, view='AgX', transparent=False, denoise=True, bounces=4):
    sc = bpy.context.scene
    sc.camera = cam
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = denoise
    sc.cycles.max_bounces = bounces      # altın referans: 0 (yalnız doğrudan ışık; r128'de dolaylı ışık yok — Şahin kokpiti r011 bulgusu)
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = transparent
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA' if transparent else 'RGB'
    sc.render.filepath = path
    sc.view_settings.view_transform = view
    sc.view_settings.look = 'None'
    sc.view_settings.exposure = 0.0
    sc.view_settings.gamma = 1.0
    bpy.ops.render.render(write_still=True)
    return path
