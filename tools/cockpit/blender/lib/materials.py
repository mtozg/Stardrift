"""PBR malzemeler (prosedürel düğümler). Fırçalı gunmetal, koyu havacılık çeliği, titanyum, kompozit, deri, ekran camı.
Doğrusal çalışır; dokular bake ile GLB'ye taşınır (bake.py)."""
import bpy

def _mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    return m, nt

def _n(nt, t, **kw):
    n = nt.nodes.new(t)
    for k, v in kw.items():
        if k == 'loc': n.location = v
        else:
            try: setattr(n, k, v)
            except Exception: pass
    return n

def _metal(name, base, rough_lo, rough_hi, metallic=1.0, brush=1.0, scratch=0.6, tint_var=0.06, aniso=0.0, bump=0.06):
    m, nt = _mat(name)
    out = _n(nt, 'ShaderNodeOutputMaterial'); bsdf = _n(nt, 'ShaderNodeBsdfPrincipled')
    tc = _n(nt, 'ShaderNodeTexCoord')
    # 1) fırça: çok uzun, dar gürültü (yatay çizgiler)
    mp = _n(nt, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.0, 55.0, 1.0)
    nz = _n(nt, 'ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 90.0; nz.inputs['Detail'].default_value = 6.0; nz.inputs['Roughness'].default_value = 0.6
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
    # 2) geniş bulutlu değişim (pürüzlülük / ton)
    cl = _n(nt, 'ShaderNodeTexNoise'); cl.inputs['Scale'].default_value = 3.5; cl.inputs['Detail'].default_value = 4.0
    nt.links.new(tc.outputs['Object'], cl.inputs['Vector'])
    # 3) çizikler: uzun ince Voronoi benzeri; ince şerit gürültüsü eşiklenir
    mp2 = _n(nt, 'ShaderNodeMapping'); mp2.inputs['Scale'].default_value = (1.0, 600.0, 1.0); mp2.inputs['Rotation'].default_value = (0.0, 0.0, 0.35)
    nz2 = _n(nt, 'ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 120.0; nz2.inputs['Detail'].default_value = 1.0
    nt.links.new(tc.outputs['Object'], mp2.inputs['Vector']); nt.links.new(mp2.outputs['Vector'], nz2.inputs['Vector'])
    sr = _n(nt, 'ShaderNodeMapRange'); sr.inputs['From Min'].default_value = 0.70; sr.inputs['From Max'].default_value = 0.73
    nt.links.new(nz2.outputs['Fac'], sr.inputs['Value'])
    # roughness
    rr = _n(nt, 'ShaderNodeMapRange'); rr.inputs['To Min'].default_value = rough_lo; rr.inputs['To Max'].default_value = rough_hi
    mixr = _n(nt, 'ShaderNodeMath', operation='ADD'); mixr.use_clamp = True
    nt.links.new(cl.outputs['Fac'], rr.inputs['Value'])
    mulb = _n(nt, 'ShaderNodeMath', operation='MULTIPLY'); mulb.inputs[1].default_value = 0.12 * brush
    nt.links.new(nz.outputs['Fac'], mulb.inputs[0])
    nt.links.new(rr.outputs['Result'], mixr.inputs[0]); nt.links.new(mulb.outputs['Value'], mixr.inputs[1])
    # çizik: pürüzlülüğü düşür (parlak çizgi)
    sc = _n(nt, 'ShaderNodeMath', operation='MULTIPLY'); sc.inputs[1].default_value = 0.35 * scratch
    nt.links.new(sr.outputs['Result'], sc.inputs[0])
    sub = _n(nt, 'ShaderNodeMath', operation='SUBTRACT'); sub.use_clamp = True
    nt.links.new(mixr.outputs['Value'], sub.inputs[0]); nt.links.new(sc.outputs['Value'], sub.inputs[1])
    nt.links.new(sub.outputs['Value'], bsdf.inputs['Roughness'])
    # renk: baz renk x hafif bulut değişimi (+ çizikte hafif açılma)
    mixc = _n(nt, 'ShaderNodeMix', data_type='RGBA'); mixc.blend_type = 'MULTIPLY'; mixc.inputs['Factor'].default_value = tint_var * 4
    mixc.inputs['A'].default_value = (*base, 1.0); mixc.inputs['B'].default_value = (1.0, 1.0, 1.0, 1.0)
    cr = _n(nt, 'ShaderNodeMapRange'); cr.inputs['To Min'].default_value = 0.85; cr.inputs['To Max'].default_value = 1.12
    nt.links.new(cl.outputs['Fac'], cr.inputs['Value'])
    mulc = _n(nt, 'ShaderNodeVectorMath', operation='SCALE')
    mulc.inputs['Scale'].default_value = 1.0
    mixc.inputs['A'].default_value = (*base, 1.0)
    scr_add = _n(nt, 'ShaderNodeMix', data_type='RGBA'); scr_add.blend_type = 'ADD'
    scr_add.inputs['A'].default_value = (*base, 1.0); scr_add.inputs['B'].default_value = (0.20, 0.21, 0.23, 1.0)
    nt.links.new(sr.outputs['Result'], scr_add.inputs['Factor'])
    scr_mul = _n(nt, 'ShaderNodeMix', data_type='RGBA'); scr_mul.blend_type = 'MULTIPLY'; scr_mul.inputs['Factor'].default_value = 1.0
    nt.links.new(scr_add.outputs['Result'], scr_mul.inputs['A'])
    nt.links.new(cr.outputs['Result'], scr_mul.inputs['B'])   # float → renk; çarpan
    nt.links.new(scr_mul.outputs['Result'], bsdf.inputs['Base Color'])
    bsdf.inputs['Metallic'].default_value = metallic
    if aniso > 0:
        try: bsdf.inputs['Anisotropic'].default_value = aniso
        except Exception: pass
    # kabartma: fırça + çizik
    bmp = _n(nt, 'ShaderNodeBump'); bmp.inputs['Strength'].default_value = bump; bmp.inputs['Distance'].default_value = 0.01
    addh = _n(nt, 'ShaderNodeMath', operation='ADD'); nt.links.new(nz.outputs['Fac'], addh.inputs[0]); nt.links.new(sr.outputs['Result'], addh.inputs[1])
    nt.links.new(addh.outputs['Value'], bmp.inputs['Height']); nt.links.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

def gunmetal():  return _metal('M_gunmetal', (0.075, 0.082, 0.098), 0.30, 0.48, scratch=0.9, bump=0.05)
def steel():     return _metal('M_dark_steel', (0.040, 0.045, 0.056), 0.40, 0.62, brush=0.7, scratch=0.6, bump=0.04)
def titanium():  return _metal('M_titanium', (0.34, 0.30, 0.26), 0.30, 0.46, scratch=0.8, bump=0.05)
def aluminum():  return _metal('M_aluminum', (0.40, 0.42, 0.45), 0.26, 0.40, brush=1.2, scratch=1.0, bump=0.06)

def composite():
    m, nt = _mat('M_composite'); out = _n(nt, 'ShaderNodeOutputMaterial'); bsdf = _n(nt, 'ShaderNodeBsdfPrincipled')
    tc = _n(nt, 'ShaderNodeTexCoord'); nz = _n(nt, 'ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 420.0; nz.inputs['Detail'].default_value = 3.0
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    bsdf.inputs['Base Color'].default_value = (0.016, 0.018, 0.022, 1); bsdf.inputs['Metallic'].default_value = 0.35; bsdf.inputs['Roughness'].default_value = 0.36
    bmp = _n(nt, 'ShaderNodeBump'); bmp.inputs['Strength'].default_value = 0.10; bmp.inputs['Distance'].default_value = 0.0006
    nt.links.new(nz.outputs['Fac'], bmp.inputs['Height']); nt.links.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface']); return m

def leather():
    m, nt = _mat('M_leather'); out = _n(nt, 'ShaderNodeOutputMaterial'); bsdf = _n(nt, 'ShaderNodeBsdfPrincipled')
    tc = _n(nt, 'ShaderNodeTexCoord'); vo = _n(nt, 'ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 900.0
    nt.links.new(tc.outputs['Object'], vo.inputs['Vector'])
    bsdf.inputs['Base Color'].default_value = (0.020, 0.023, 0.030, 1); bsdf.inputs['Roughness'].default_value = 0.52; bsdf.inputs['Metallic'].default_value = 0.0
    try: bsdf.inputs['Specular IOR Level'].default_value = 0.45
    except Exception: pass
    bmp = _n(nt, 'ShaderNodeBump'); bmp.inputs['Strength'].default_value = 0.35; bmp.inputs['Distance'].default_value = 0.0015
    nt.links.new(vo.outputs['Distance'], bmp.inputs['Height']); nt.links.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface']); return m

def emission(name, color, strength):
    m, nt = _mat(name); out = _n(nt, 'ShaderNodeOutputMaterial'); em = _n(nt, 'ShaderNodeEmission')
    em.inputs['Color'].default_value = (*color, 1); em.inputs['Strength'].default_value = strength
    nt.links.new(em.outputs['Emission'], out.inputs['Surface']); return m

def screen_mat(image_path=None, strength=1.0):
    m, nt = _mat('M_screen'); out = _n(nt, 'ShaderNodeOutputMaterial'); em = _n(nt, 'ShaderNodeEmission')
    if image_path:
        tx = _n(nt, 'ShaderNodeTexImage'); tx.image = bpy.data.images.load(image_path); nt.links.new(tx.outputs['Color'], em.inputs['Color'])
    else:
        em.inputs['Color'].default_value = (0.012, 0.07, 0.11, 1)
    em.inputs['Strength'].default_value = strength; nt.links.new(em.outputs['Emission'], out.inputs['Surface']); return m
