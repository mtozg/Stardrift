"""Prosedürel PBR malzemeler (bpy). Tanımlar library/materials/*.json içindedir; kod yalnızca düğüm grafiğini kurar.

Kaşif kokpitindeki yaklaşımın genelleştirilmiş, yeniden yazılmış hâli: geniş bulut ton değişimi, fırça izi,
çizik, kenar aşınması (Bevel normali ile geometrik normal farkı), girinti kiri (AO), kabartma.
Farklar: (1) tüm katsayılar veriden gelir, (2) metaliklik malzeme tanımında ve bake'te gerçek kanal olarak taşınır,
(3) emisyon gücü ≤ 1 (three r128 KHR_materials_emissive_strength desteklemez; parlaklık oyunda bloom ile verilir)."""
import os, bpy
from .paths import LIBRARY, load_json

DEFAULTS = {
    'kind': 'metal', 'base': [0.3, 0.3, 0.32], 'metallic': 1.0, 'rough': [0.3, 0.45],
    'tone_var': [0.82, 1.15], 'cloud_scale': 2.6, 'brush': 0.0, 'brush_scale': 140.0,
    'scratch': 0.0, 'scratch_color': [0.22, 0.23, 0.25], 'wear': 0.0, 'wear_color': [0.5, 0.52, 0.56], 'wear_radius': 0.01,
    'dirt': 0.0, 'dirt_distance': 0.06, 'bump': 0.04, 'micro_scale': 420.0,
    'emission': None,
    'panels': 0.0, 'panel_scale': 2.6,      # panel derzleri: nesne uzayında üç eksenli tuğla örüntüsü (düz büyük yüzeyleri böler); 0 = kapalı
    'chips': 0.0, 'chip_scale': 14.0, 'chip_color': [0.42, 0.43, 0.45], 'grime': 0.0, 'streaks': 0.0,
}


def load_def(name):
    d = dict(DEFAULTS)
    d.update(load_json(os.path.join(LIBRARY, 'materials', name + '.json')))
    d['name'] = name
    return d


def _graph(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    return m, nt


def _n(nt, t, **kw):
    n = nt.nodes.new(t)
    for k, v in kw.items():
        setattr(n, k, v)
    return n


def _math(nt, op, a, b=None, clamp=False):
    n = _n(nt, 'ShaderNodeMath', operation=op)
    n.use_clamp = clamp
    for i, x in enumerate((a, b)):
        if x is None:
            continue
        if isinstance(x, (int, float)):
            n.inputs[i].default_value = x
        else:
            nt.links.new(x, n.inputs[i])
    return n.outputs[0]


def _range(nt, src, fmin, fmax, tmin=0.0, tmax=1.0):
    n = _n(nt, 'ShaderNodeMapRange')
    n.inputs['From Min'].default_value = fmin
    n.inputs['From Max'].default_value = fmax
    n.inputs['To Min'].default_value = tmin
    n.inputs['To Max'].default_value = tmax
    nt.links.new(src, n.inputs['Value'])
    return n.outputs['Result']


def _mix(nt, mode, a, b, fac=1.0):
    n = _n(nt, 'ShaderNodeMix', data_type='RGBA')
    n.blend_type = mode
    for sock, x in ((n.inputs['A'], a), (n.inputs['B'], b), (n.inputs['Factor'], fac)):
        if isinstance(x, (int, float)):
            sock.default_value = x
        elif isinstance(x, (list, tuple)):
            sock.default_value = (*x[:3], 1.0)
        else:
            nt.links.new(x, sock)
    return n.outputs['Result']


def build(defn):
    """Tanımdan malzeme kur. Döndürülen malzemede m['sd_metallic'] ve m['sd_def'] saklanır."""
    d = defn
    m, nt = _graph('M_' + d['name'])
    m['sd_def'] = d['name']
    out = _n(nt, 'ShaderNodeOutputMaterial')
    bsdf = _n(nt, 'ShaderNodeBsdfPrincipled')
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    if d['kind'] == 'emit':
        c = [min(1.0, x) for x in d['emission']]
        bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1)
        bsdf.inputs['Roughness'].default_value = 0.4
        bsdf.inputs['Metallic'].default_value = 0.0
        bsdf.inputs['Emission Color'].default_value = (*c, 1)
        bsdf.inputs['Emission Strength'].default_value = 1.0
        m['sd_metallic'] = 0.0
        return m

    tc = _n(nt, 'ShaderNodeTexCoord')
    obj = tc.outputs['Object']
    cloud = _n(nt, 'ShaderNodeTexNoise')
    cloud.inputs['Scale'].default_value = d['cloud_scale']
    cloud.inputs['Detail'].default_value = 5.0
    nt.links.new(obj, cloud.inputs['Vector'])

    # fırça izi (bir eksende uzatılmış gürültü)
    mp = _n(nt, 'ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1.0, 38.0, 1.0)
    nt.links.new(obj, mp.inputs['Vector'])
    brush = _n(nt, 'ShaderNodeTexNoise')
    brush.inputs['Scale'].default_value = d['brush_scale']
    brush.inputs['Detail'].default_value = 7.0
    nt.links.new(mp.outputs['Vector'], brush.inputs['Vector'])

    # çizikler: ince eşiklenmiş şeritler
    mp2 = _n(nt, 'ShaderNodeMapping')
    mp2.inputs['Scale'].default_value = (1.0, 420.0, 1.0)
    mp2.inputs['Rotation'].default_value = (0.0, 0.0, 0.35)
    nt.links.new(obj, mp2.inputs['Vector'])
    scr_n = _n(nt, 'ShaderNodeTexNoise')
    scr_n.inputs['Scale'].default_value = 70.0
    scr_n.inputs['Detail'].default_value = 1.0
    nt.links.new(mp2.outputs['Vector'], scr_n.inputs['Vector'])
    scratch = _range(nt, scr_n.outputs['Fac'], 0.69, 0.73)
    scratch = _math(nt, 'MULTIPLY', scratch, d['scratch'])

    # kenar aşınması: dışbükey kenarlarda bevel normali sapar
    bv = _n(nt, 'ShaderNodeBevel')
    bv.inputs['Radius'].default_value = d['wear_radius']
    bv.samples = 6
    geo = _n(nt, 'ShaderNodeNewGeometry')
    dot = _n(nt, 'ShaderNodeVectorMath', operation='DOT_PRODUCT')
    nt.links.new(bv.outputs['Normal'], dot.inputs[0])
    nt.links.new(geo.outputs['Normal'], dot.inputs[1])
    edge = _math(nt, 'SUBTRACT', 1.0, dot.outputs['Value'])
    wear = _math(nt, 'MULTIPLY', _range(nt, edge, 0.01, 0.10), d['wear'], clamp=True)

    # girinti kiri
    ao = _n(nt, 'ShaderNodeAmbientOcclusion')
    ao.inputs['Distance'].default_value = d['dirt_distance']
    ao.samples = 8
    dirt = _range(nt, ao.outputs['AO'], 0.0, 1.0, 1.0 - d['dirt'], 1.0)

    # pürüzlülük
    r_lo, r_hi = d['rough']
    rough = _range(nt, cloud.outputs['Fac'], 0.3, 0.7, r_lo, r_hi)
    rough = _math(nt, 'ADD', rough, _math(nt, 'MULTIPLY', brush.outputs['Fac'], 0.2 * d['brush']), clamp=True)
    rough = _math(nt, 'SUBTRACT', rough, _math(nt, 'MULTIPLY', scratch, 0.35), clamp=True)
    rough = _math(nt, 'SUBTRACT', rough, _math(nt, 'MULTIPLY', wear, 0.35), clamp=True)
    # kir maskesi (0 = temiz, 1 = tam kir): metalde kir dielektrik bir katmandır → metalikliği düşürür, pürüzlülüğü artırır
    dmask = _math(nt, 'SUBTRACT', 1.0, _range(nt, ao.outputs['AO'], 0.0, 1.0, 0.0, 1.0), clamp=True)
    dmask = _math(nt, 'MULTIPLY', dmask, d['dirt'], clamp=True)
    if d['kind'] == 'metal':
        rough = _math(nt, 'ADD', rough, _math(nt, 'MULTIPLY', dmask, 0.35), clamp=True)
    # boya kırıkları (yalnız dielektrik boya): altından metal görünür → metaliklik kanalında gerçekten metal
    chips = None
    if d['kind'] == 'dielectric' and d['chips'] > 0:
        cn = _n(nt, 'ShaderNodeTexNoise')
        cn.inputs['Scale'].default_value = d['chip_scale']
        cn.inputs['Detail'].default_value = 8.0
        cn.inputs['Roughness'].default_value = 0.7
        nt.links.new(obj, cn.inputs['Vector'])
        chips = _math(nt, 'MULTIPLY', _range(nt, cn.outputs['Fac'], 0.66, 0.69), d['chips'], clamp=True)
        chips = _math(nt, 'MAXIMUM', chips, _math(nt, 'MULTIPLY', wear, 0.8), clamp=True)      # kenar aşınması da metali açar
        rough = _math(nt, 'ADD', _math(nt, 'MULTIPLY', rough, _math(nt, 'SUBTRACT', 1.0, chips)), _math(nt, 'MULTIPLY', chips, 0.32))
    # geniş ölçekli kir lekelenmesi ve dikey akıntı izleri
    grime = streak = None
    if d['grime'] > 0:
        gn = _n(nt, 'ShaderNodeTexNoise')
        gn.inputs['Scale'].default_value = 1.4
        gn.inputs['Detail'].default_value = 5.0
        nt.links.new(obj, gn.inputs['Vector'])
        grime = _math(nt, 'MULTIPLY', _range(nt, gn.outputs['Fac'], 0.42, 0.72), d['grime'], clamp=True)
        rough = _math(nt, 'ADD', rough, _math(nt, 'MULTIPLY', grime, 0.15), clamp=True)
    if d['streaks'] > 0:
        sm = _n(nt, 'ShaderNodeMapping')
        sm.inputs['Scale'].default_value = (7.0, 7.0, 0.35)
        nt.links.new(obj, sm.inputs['Vector'])
        sn = _n(nt, 'ShaderNodeTexNoise')
        sn.inputs['Scale'].default_value = 9.0
        sn.inputs['Detail'].default_value = 3.0
        nt.links.new(sm.outputs['Vector'], sn.inputs['Vector'])
        streak = _math(nt, 'MULTIPLY', _range(nt, sn.outputs['Fac'], 0.52, 0.74), d['streaks'], clamp=True)
    nt.links.new(rough, bsdf.inputs['Roughness'])

    # panel derzleri: üç eksen izdüşümünün birleşimi (her yüzey yönünde ızgara)
    seam = None
    if d['panels'] > 0:
        sep = _n(nt, 'ShaderNodeSeparateXYZ')
        nt.links.new(obj, sep.inputs['Vector'])
        fac = []
        for ax in ((0, 1), (0, 2), (1, 2)):
            cmb = _n(nt, 'ShaderNodeCombineXYZ')
            nt.links.new(sep.outputs['XYZ'[ax[0]]], cmb.inputs['X'])
            nt.links.new(sep.outputs['XYZ'[ax[1]]], cmb.inputs['Y'])
            bk = _n(nt, 'ShaderNodeTexBrick')
            bk.offset = 0.0
            bk.inputs['Scale'].default_value = d['panel_scale']
            bk.inputs['Mortar Size'].default_value = 0.05
            bk.inputs['Mortar Smooth'].default_value = 0.15
            bk.inputs['Bias'].default_value = 0.0
            bk.inputs['Brick Width'].default_value = 1.0
            bk.inputs['Row Height'].default_value = 0.62
            nt.links.new(cmb.outputs['Vector'], bk.inputs['Vector'])
            fac.append(bk.outputs['Fac'])
        mn = _math(nt, 'MINIMUM', _math(nt, 'MINIMUM', fac[0], fac[1]), fac[2])
        seam = _math(nt, 'SUBTRACT', 1.0, mn, clamp=True)      # 1 = derz
        rough = _math(nt, 'ADD', rough, _math(nt, 'MULTIPLY', seam, 0.12), clamp=True)
        nt.links.new(rough, bsdf.inputs['Roughness'])
    # renk
    tone = _range(nt, cloud.outputs['Fac'], 0.3, 0.7, d['tone_var'][0], d['tone_var'][1])
    col = _mix(nt, 'MULTIPLY', d['base'], tone)
    col = _mix(nt, 'MIX', col, d['scratch_color'], scratch)
    col = _mix(nt, 'MIX', col, d['wear_color'], wear)
    if d['kind'] == 'metal':
        col = _mix(nt, 'MIX', col, d.get('dirt_color', [0.07, 0.065, 0.06]), dmask)      # kir rengi karışır, metal tabanı koyulaşmaz
    else:
        col = _mix(nt, 'MULTIPLY', col, dirt)
    if grime is not None:
        col = _mix(nt, 'MULTIPLY', col, _range(nt, grime, 0.0, 1.0, 1.0, 0.70))
    if streak is not None:
        col = _mix(nt, 'MULTIPLY', col, _range(nt, streak, 0.0, 1.0, 1.0, 0.78))
    if chips is not None:
        col = _mix(nt, 'MIX', col, d['chip_color'], chips)
    if seam is not None:
        col = _mix(nt, 'MULTIPLY', col, _range(nt, seam, 0.0, 1.0, 1.0, 1.0 - 0.78 * d['panels']))
    nt.links.new(col, bsdf.inputs['Base Color'])

    if d['kind'] == 'metal' and d['dirt'] > 0:
        nt.links.new(_math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, dmask), d['metallic'], clamp=True), bsdf.inputs['Metallic'])
    elif chips is not None:
        nt.links.new(chips, bsdf.inputs['Metallic'])
    else:
        bsdf.inputs['Metallic'].default_value = d['metallic']
    m['sd_metallic'] = d['metallic']
    if d['kind'] == 'dielectric':
        try:
            bsdf.inputs['Specular IOR Level'].default_value = 0.5
        except KeyError:
            pass

    # kabartma: fırça + çizik + mikro gürültü
    micro = _n(nt, 'ShaderNodeTexNoise')
    micro.inputs['Scale'].default_value = d['micro_scale']
    micro.inputs['Detail'].default_value = 2.0
    nt.links.new(obj, micro.inputs['Vector'])
    h = _math(nt, 'ADD', _math(nt, 'MULTIPLY', brush.outputs['Fac'], d['brush']), scratch)
    h = _math(nt, 'ADD', h, _math(nt, 'MULTIPLY', micro.outputs['Fac'], 0.5))
    if seam is not None:
        h = _math(nt, 'SUBTRACT', h, _math(nt, 'MULTIPLY', seam, 3.0 * d['panels']))      # derz çukuru
    bump = _n(nt, 'ShaderNodeBump')
    bump.inputs['Strength'].default_value = d['bump']
    bump.inputs['Distance'].default_value = 0.01
    nt.links.new(h, bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def library(names, overrides=None):
    """overrides: {malzeme_adı: {alan: değer}} — spec düzeyinde (kütüphane JSON'una dokunmadan) ince ayar; r012 gibi dondurulmuş varlıkların yeniden üretimini bozmaz"""
    ov = overrides or {}
    out = {}
    for n in names:
        d = load_def(n)
        d.update(ov.get(n, {}))
        out[n] = build(d)
    return out
