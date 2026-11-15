"""Kamera, ışık ve Cycles render yardımcıları."""
import bpy, math
from mathutils import Vector
from .common import *

def setup_world(strength=1.0):
    """Uzay ortamı: yukarı doğru açılan soğuk gradyan, ufukta ince ışıltı, yıldızlar. Metal yüzeyler bunu yansıtır."""
    w = bpy.data.worlds.new('W'); bpy.context.scene.world = w; w.use_nodes = True; nt = w.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputWorld'); bg = nt.nodes.new('ShaderNodeBackground')
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); mr = nt.nodes.new('ShaderNodeMapRange'); cr = nt.nodes.new('ShaderNodeValToRGB')
    nt.links.new(tc.outputs['Object'], sep.inputs['Vector']); nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
    mr.inputs['From Min'].default_value = -0.35; mr.inputs['From Max'].default_value = 0.95; nt.links.new(mr.outputs['Result'], cr.inputs['Fac'])
    cr.color_ramp.elements[0].position = 0.0; cr.color_ramp.elements[0].color = (0.004, 0.005, 0.010, 1)
    e = cr.color_ramp.elements.new(0.45); e.color = (0.020, 0.030, 0.060, 1)
    cr.color_ramp.elements[2].position = 1.0; cr.color_ramp.elements[2].color = (0.30, 0.42, 0.70, 1)
    # yıldızlar
    vo = nt.nodes.new('ShaderNodeTexVoronoi'); vo.feature = 'DISTANCE_TO_EDGE' if False else 'F1'; vo.inputs['Scale'].default_value = 420.0
    nt.links.new(tc.outputs['Object'], vo.inputs['Vector'])
    st = nt.nodes.new('ShaderNodeMapRange'); st.inputs['From Min'].default_value = 0.075; st.inputs['From Max'].default_value = 0.02; nt.links.new(vo.outputs['Distance'], st.inputs['Value'])
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 6.0; nt.links.new(st.outputs['Result'], mul.inputs[0])
    add = nt.nodes.new('ShaderNodeMix'); add.data_type = 'RGBA'; add.blend_type = 'ADD'; add.inputs['Factor'].default_value = 1.0
    nt.links.new(cr.outputs['Color'], add.inputs['A']); nt.links.new(mul.outputs['Value'], add.inputs['B'])
    nt.links.new(add.outputs['Result'], bg.inputs['Color']); bg.inputs['Strength'].default_value = strength; nt.links.new(bg.outputs['Background'], out.inputs['Surface'])

def add_light(kind, loc, energy, color=(1, 1, 1), size=1.0, rot=None, name='L'):
    d = bpy.data.lights.new(name, kind); d.energy = energy; d.color = color
    if kind == 'AREA': d.size = size
    if kind == 'SUN': d.angle = math.radians(size)
    ob = bpy.data.objects.new(name, d); bpy.context.scene.collection.objects.link(ob); ob.location = loc
    if rot: ob.rotation_euler = rot
    return ob

def lights_default():
    # dış ışık kutuları (softbox): camlardan içeri düşen güneş/yansıma; bevellerde uzun parlamalar verir
    add_light('AREA', (-1.4, 1.9, 1.6), 300, (1.0, 0.95, 0.88), 1.5, (math.radians(62), 0, math.radians(-38)), 'KeyBox')
    add_light('AREA', (1.8, 1.5, 1.3), 150, (0.62, 0.78, 1.0), 1.4, (math.radians(65), 0, math.radians(40)), 'RimBox')
    add_light('AREA', (0.0, 0.15, 1.1), 7, (0.7, 0.8, 1.0), 1.8, (0, 0, 0), 'TopFill')
    # ekran ışığı: her ekrandan konsola ve pilota yumuşak camgöbeği (oyundaki ekran ışığı)
    for x, e in ((-0.75, 0.9), (0.0, 1.6), (0.75, 0.9)):
        add_light('AREA', (x, 0.92, -0.42), e, (0.3, 0.8, 1.0), 0.5, (math.radians(95), 0, 0), 'ScreenGlow')

def camera(a, name='Pilot', res=(1200, 492), fovy=None, loc=None, look=None, shift_y=None):
    c = a['camera']
    cd = bpy.data.cameras.new(name); cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 24.0
    fy = c['fovy_deg'] if fovy is None else fovy
    cd.lens = 12.0 / math.tan(math.radians(fy / 2))
    ob = bpy.data.objects.new(name, cd); bpy.context.scene.collection.objects.link(ob)
    if loc is None:   # pilot: göz orijinde, +Y (Blender) ileri
        ob.location = (0, 0, 0); ob.rotation_euler = (math.radians(90), 0, 0)
        cd.shift_y = -(0.5 - c['principal'][1] / 656.0)      # asal nokta yukarıda (oyun rehber kamerası)
    else:
        ob.location = loc; d = Vector(look) - Vector(loc); ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        if shift_y is not None: cd.shift_y = shift_y
    cd.clip_start = 0.02; cd.clip_end = 30
    return ob

def render(path, cam, res, samples=48, denoise=True):
    sc = bpy.context.scene; sc.camera = cam; sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'; sc.cycles.samples = samples; sc.cycles.use_denoising = denoise
    try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception: pass
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'; sc.render.filepath = path
    sc.view_settings.view_transform = 'Filmic' if 'Filmic' in [t.identifier for t in sc.view_settings.bl_rna.properties['view_transform'].enum_items] else 'AgX'
    try: sc.view_settings.look = 'None'
    except Exception: pass
    sc.view_settings.exposure = 0.0
    sc.cycles.max_bounces = 6
    bpy.ops.render.render(write_still=True)
