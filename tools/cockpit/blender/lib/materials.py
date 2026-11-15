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

PROJ = {'img': None, 'strength': 0.0}   # build_cockpit tarafından doldurulur: onaylı çizim (detay referansı)

def _metal(name, base, rough_lo, rough_hi, metallic=1.0, brush=1.0, scratch=0.6, tint_var=0.06, aniso=0.0, bump=0.06, wear=0.8, dirt=0.55, proj=1.0):
    m, nt = _mat(name)
    out = _n(nt, 'ShaderNodeOutputMaterial'); bsdf = _n(nt, 'ShaderNodeBsdfPrincipled')
    tc = _n(nt, 'ShaderNodeTexCoord')
    # fırça: uzun dar gürültü (yatay çizgiler) — daha kontrastlı
    mp = _n(nt, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.0, 38.0, 1.0)
    nz = _n(nt, 'ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 140.0; nz.inputs['Detail'].default_value = 7.0; nz.inputs['Roughness'].default_value = 0.65
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
    # geniş bulutlu değişim (pürüzlülük / ton)
    cl = _n(nt, 'ShaderNodeTexNoise'); cl.inputs['Scale'].default_value = 2.6; cl.inputs['Detail'].default_value = 5.0
    nt.links.new(tc.outputs['Object'], cl.inputs['Vector'])
    # çizikler: ince şeritler, eşiklenmiş
    mp2 = _n(nt, 'ShaderNodeMapping'); mp2.inputs['Scale'].default_value = (1.0, 420.0, 1.0); mp2.inputs['Rotation'].default_value = (0.0, 0.0, 0.35)
    nz2 = _n(nt, 'ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 70.0; nz2.inputs['Detail'].default_value = 1.0
    nt.links.new(tc.outputs['Object'], mp2.inputs['Vector']); nt.links.new(mp2.outputs['Vector'], nz2.inputs['Vector'])
    sr = _n(nt, 'ShaderNodeMapRange'); sr.inputs['From Min'].default_value = 0.69; sr.inputs['From Max'].default_value = 0.73
    nt.links.new(nz2.outputs['Fac'], sr.inputs['Value'])
    # kenar aşınması: bevel normali ile geometrik normal farkı (dışbükey kenarlar)
    bv = _n(nt, 'ShaderNodeBevel'); bv.inputs['Radius'].default_value = 0.010; bv.samples = 6
    geo = _n(nt, 'ShaderNodeNewGeometry'); dot = _n(nt, 'ShaderNodeVectorMath', operation='DOT_PRODUCT')
    nt.links.new(bv.outputs['Normal'], dot.inputs[0]); nt.links.new(geo.outputs['Normal'], dot.inputs[1])
    inv = _n(nt, 'ShaderNodeMath', operation='SUBTRACT'); inv.inputs[0].default_value = 1.0; nt.links.new(dot.outputs['Value'], inv.inputs[1])
    wr = _n(nt, 'ShaderNodeMapRange'); wr.inputs['From Min'].default_value = 0.01; wr.inputs['From Max'].default_value = 0.10
    nt.links.new(inv.outputs['Value'], wr.inputs['Value'])
    wmul = _n(nt, 'ShaderNodeMath', operation='MULTIPLY'); wmul.inputs[1].default_value = wear; nt.links.new(wr.outputs['Result'], wmul.inputs[0])
    # AO kirlenmesi: girintilerde koyulaşma
    ao = _n(nt, 'ShaderNodeAmbientOcclusion'); ao.inputs['Distance'].default_value = 0.07; ao.samples = 8
    aor = _n(nt, 'ShaderNodeMapRange'); aor.inputs['To Min'].default_value = 1.0 - dirt; aor.inputs['To Max'].default_value = 1.0
    nt.links.new(ao.outputs['AO'], aor.inputs['Value'])
    # --- roughness: bulut aralığı + fırça + (aşınmada düşer) - çizik
    rr = _n(nt, 'ShaderNodeMapRange'); rr.inputs['To Min'].default_value = rough_lo * 0.85; rr.inputs['To Max'].default_value = rough_hi * 1.25
    nt.links.new(cl.outputs['Fac'], rr.inputs['Value'])
    mulb = _n(nt, 'ShaderNodeMath', operation='MULTIPLY'); mulb.inputs[1].default_value = 0.26 * brush; nt.links.new(nz.outputs['Fac'], mulb.inputs[0])
    r1 = _n(nt, 'ShaderNodeMath', operation='ADD'); r1.use_clamp = True; nt.links.new(rr.outputs['Result'], r1.inputs[0]); nt.links.new(mulb.outputs['Value'], r1.inputs[1])
    sc = _n(nt, 'ShaderNodeMath', operation='MULTIPLY'); sc.inputs[1].default_value = 0.40 * scratch; nt.links.new(sr.outputs['Result'], sc.inputs[0])
    r2 = _n(nt, 'ShaderNodeMath', operation='SUBTRACT'); r2.use_clamp = True; nt.links.new(r1.outputs['Value'], r2.inputs[0]); nt.links.new(sc.outputs['Value'], r2.inputs[1])
    wl = _n(nt, 'ShaderNodeMath', operation='MULTIPLY'); wl.inputs[1].default_value = 0.45; nt.links.new(wmul.outputs['Value'], wl.inputs[0])
    r3 = _n(nt, 'ShaderNodeMath', operation='SUBTRACT'); r3.use_clamp = True; nt.links.new(r2.outputs['Value'], r3.inputs[0]); nt.links.new(wl.outputs['Value'], r3.inputs[1])
    nt.links.new(r3.outputs['Value'], bsdf.inputs['Roughness'])
    # --- renk: taban × bulut değişimi, çizikte açılma, kenarda çıplak metal, girintide koyulaşma
    cr = _n(nt, 'ShaderNodeMapRange'); cr.inputs['To Min'].default_value = 0.80; cr.inputs['To Max'].default_value = 1.18
    nt.links.new(cl.outputs['Fac'], cr.inputs['Value'])
    c0 = _n(nt, 'ShaderNodeMix', data_type='RGBA'); c0.blend_type = 'MULTIPLY'; c0.inputs['Factor'].default_value = 1.0
    c0.inputs['A'].default_value = (*base, 1.0); nt.links.new(cr.outputs['Result'], c0.inputs['B'])
    c1 = _n(nt, 'ShaderNodeMix', data_type='RGBA'); c1.blend_type = 'ADD'
    nt.links.new(c0.outputs['Result'], c1.inputs['A']); c1.inputs['B'].default_value = (0.22, 0.23, 0.25, 1.0); nt.links.new(sr.outputs['Result'], c1.inputs['Factor'])
    c2 = _n(nt, 'ShaderNodeMix', data_type='RGBA'); c2.blend_type = 'MIX'
    nt.links.new(c1.outputs['Result'], c2.inputs['A']); c2.inputs['B'].default_value = (0.50, 0.52, 0.56, 1.0); nt.links.new(wmul.outputs['Value'], c2.inputs['Factor'])
    c3 = _n(nt, 'ShaderNodeMix', data_type='RGBA'); c3.blend_type = 'MULTIPLY'; c3.inputs['Factor'].default_value = 1.0
    nt.links.new(c2.outputs['Result'], c3.inputs['A']); nt.links.new(aor.outputs['Result'], c3.inputs['B'])
    last = c3
    hp_node = None
    if proj > 0:   # onaylı çizimden yalnızca İNCE detay (yüksek geçiren) ve orta frekans lekelenme: çizik, panel hattı, kir. Büyük şekil/ışık/gölge taşınmaz.
        uvn = _n(nt, 'ShaderNodeUVMap'); uvn.uv_map = 'ProjUV'
        tx = _n(nt, 'ShaderNodeTexImage', name='PROJ_IMG'); tx.interpolation = 'Linear'; tx.extension = 'EXTEND'
        if PROJ['img']: tx.image = PROJ['img']
        nt.links.new(uvn.outputs['UV'], tx.inputs['Vector'])
        sp = _n(nt, 'ShaderNodeSeparateColor'); nt.links.new(tx.outputs['Color'], sp.inputs['Color'])
        def sc2(src, name):   # (x-0.5)*2
            a = _n(nt, 'ShaderNodeMath', operation='SUBTRACT'); a.inputs[1].default_value = 0.5; nt.links.new(src, a.inputs[0])
            b = _n(nt, 'ShaderNodeMath', operation='MULTIPLY', name=name); b.inputs[1].default_value = 2.0; nt.links.new(a.outputs['Value'], b.inputs[0]); return b
        hp = sc2(sp.outputs['Red'], 'PROJ_HP'); mid = sc2(sp.outputs['Green'], 'PROJ_MID'); hp_node = hp
        at = _n(nt, 'ShaderNodeAttribute', name='PROJ_W'); at.attribute_name = 'projw'; at.attribute_type = 'GEOMETRY'
        wm = _n(nt, 'ShaderNodeMath', operation='MULTIPLY', name='PROJ_S'); wm.inputs[1].default_value = PROJ['strength']; nt.links.new(at.outputs['Fac'], wm.inputs[0])
        k1 = _n(nt, 'ShaderNodeMath', operation='MULTIPLY'); k1.inputs[1].default_value = 0.32; nt.links.new(hp.outputs['Value'], k1.inputs[0])
        k2 = _n(nt, 'ShaderNodeMath', operation='MULTIPLY'); k2.inputs[1].default_value = 0.35; nt.links.new(mid.outputs['Value'], k2.inputs[0])
        ad = _n(nt, 'ShaderNodeMath', operation='ADD'); nt.links.new(k1.outputs['Value'], ad.inputs[0]); nt.links.new(k2.outputs['Value'], ad.inputs[1])
        mw = _n(nt, 'ShaderNodeMath', operation='MULTIPLY'); nt.links.new(ad.outputs['Value'], mw.inputs[0]); nt.links.new(wm.outputs['Value'], mw.inputs[1])
        mu = _n(nt, 'ShaderNodeMath', operation='ADD'); mu.use_clamp = False; mu.inputs[1].default_value = 1.0; nt.links.new(mw.outputs['Value'], mu.inputs[0])
        mc = _n(nt, 'ShaderNodeMath', operation='MAXIMUM'); mc.inputs[1].default_value = 0.25; nt.links.new(mu.outputs['Value'], mc.inputs[0])
        cb = _n(nt, 'ShaderNodeCombineColor'); [nt.links.new(mc.outputs['Value'], cb.inputs[i]) for i in range(3)]
        c4 = _n(nt, 'ShaderNodeMix', data_type='RGBA'); c4.blend_type = 'MULTIPLY'; c4.inputs['Factor'].default_value = 1.0
        nt.links.new(c3.outputs['Result'], c4.inputs['A']); nt.links.new(cb.outputs['Color'], c4.inputs['B'])
        last = c4
        # roughness: ince çizik/çukurda parlaklık değişir
        rk = _n(nt, 'ShaderNodeMath', operation='MULTIPLY'); rk.inputs[1].default_value = 0.20
        nt.links.new(hp.outputs['Value'], rk.inputs[0])
        rw = _n(nt, 'ShaderNodeMath', operation='MULTIPLY'); nt.links.new(rk.outputs['Value'], rw.inputs[0]); nt.links.new(wm.outputs['Value'], rw.inputs[1])
        r4 = _n(nt, 'ShaderNodeMath', operation='SUBTRACT'); r4.use_clamp = True; nt.links.new(r3.outputs['Value'], r4.inputs[0]); nt.links.new(rw.outputs['Value'], r4.inputs[1])
        nt.links.new(r4.outputs['Value'], bsdf.inputs['Roughness'])
        PROJ_W_NODE = wm
    nt.links.new(last.outputs['Result'], bsdf.inputs['Base Color'])
    bsdf.inputs['Metallic'].default_value = metallic
    # kabartma: fırça + çizik
    bmp = _n(nt, 'ShaderNodeBump'); bmp.inputs['Strength'].default_value = bump; bmp.inputs['Distance'].default_value = 0.01
    addh = _n(nt, 'ShaderNodeMath', operation='ADD'); nt.links.new(nz.outputs['Fac'], addh.inputs[0]); nt.links.new(sr.outputs['Result'], addh.inputs[1])
    nt.links.new(addh.outputs['Value'], bmp.inputs['Height'])
    if hp_node is not None:
        hh = _n(nt, 'ShaderNodeMath', operation='MULTIPLY'); nt.links.new(hp_node.outputs['Value'], hh.inputs[0]); nt.links.new(wm.outputs['Value'], hh.inputs[1])
        h2 = _n(nt, 'ShaderNodeMath', operation='ADD'); h2.inputs[1].default_value = 0.5; nt.links.new(hh.outputs['Value'], h2.inputs[0])
        b2 = _n(nt, 'ShaderNodeBump'); b2.inputs['Strength'].default_value = 0.22; b2.inputs['Distance'].default_value = 0.004
        nt.links.new(h2.outputs['Value'], b2.inputs['Height']); nt.links.new(bmp.outputs['Normal'], b2.inputs['Normal']); nt.links.new(b2.outputs['Normal'], bsdf.inputs['Normal'])
    else:
        nt.links.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

def gunmetal():  return _metal('M_gunmetal', (0.060, 0.067, 0.082), 0.26, 0.44, scratch=1.0, bump=0.07, wear=1.1, dirt=0.65)
def steel():     return _metal('M_dark_steel', (0.026, 0.030, 0.038), 0.38, 0.60, brush=0.7, scratch=0.6, bump=0.04, wear=1.0, dirt=0.7)
def titanium():  return _metal('M_titanium', (0.34, 0.30, 0.26), 0.30, 0.46, scratch=0.8, bump=0.05, wear=0.9, dirt=0.5)
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
    bsdf.inputs['Base Color'].default_value = (0.030, 0.034, 0.045, 1); bsdf.inputs['Roughness'].default_value = 0.46; bsdf.inputs['Metallic'].default_value = 0.0
    try: bsdf.inputs['Specular IOR Level'].default_value = 0.45
    except Exception: pass
    bmp = _n(nt, 'ShaderNodeBump'); bmp.inputs['Strength'].default_value = 0.35; bmp.inputs['Distance'].default_value = 0.0015
    nt.links.new(vo.outputs['Distance'], bmp.inputs['Height']); nt.links.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface']); return m

def fabric():
    m, nt = _mat('M_fabric'); out = _n(nt, 'ShaderNodeOutputMaterial'); bsdf = _n(nt, 'ShaderNodeBsdfPrincipled')
    tc = _n(nt, 'ShaderNodeTexCoord'); mp = _n(nt, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (260.0, 260.0, 260.0)
    ck = _n(nt, 'ShaderNodeTexChecker'); ck.inputs['Scale'].default_value = 1.0
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], ck.inputs['Vector'])
    bsdf.inputs['Base Color'].default_value = (0.060, 0.068, 0.082, 1); bsdf.inputs['Roughness'].default_value = 0.82; bsdf.inputs['Metallic'].default_value = 0.0
    bmp = _n(nt, 'ShaderNodeBump'); bmp.inputs['Strength'].default_value = 0.35; bmp.inputs['Distance'].default_value = 0.0012
    nt.links.new(ck.outputs['Fac'], bmp.inputs['Height']); nt.links.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface']); return m

def thread():
    m, nt = _mat('M_thread'); out = _n(nt, 'ShaderNodeOutputMaterial'); bsdf = _n(nt, 'ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.36, 0.34, 0.29, 1); bsdf.inputs['Roughness'].default_value = 0.85; bsdf.inputs['Metallic'].default_value = 0.0
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
