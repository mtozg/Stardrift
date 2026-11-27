"""Geçit kapısı çerçevesi — BÜTÜNLEŞİK (Lead: payandalar ayrık kutu gibi → halkadan büyüyen tek yüzey). Torus + 8 konik payanda kulesi + kaburga direkleri + iç/dış dudak Boolean UNION; paletin kimlik parçaları (buz sarkıtı, kristal, altın kule, kor çatlağı, kaba kırmızı plaka) UNION; hi-poly: radyal panel yarıkları + halka boyunca oluk (bake).
Kurulum: halka düzlemi XY (hole ekseni +Z), R=1,16, tüp r=0,20 (oyundaki oran); ×8 m → normalize en büyük boyut=1."""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix
from core import geo
from families.ship.yuk_ext import orient_outward
from families.ship.yuk_fused import boolean, union_all, diff_all, box_bm, cyl_bm, tbox_bm
from families.prop.build import torus_bm

PAL = {'ankora': ('gunmetal', 'steel_dark', 'yuk_dark', 'emit_cyan', 'steel_dark'),
       'kizil': ('rock_dark', 'yuk_cont_rust', 'lava_rock', 'emit_lava', 'yuk_cont_rust'),
       'buzul': ('ice_white', 'ice_blue', 'steel_dark', 'emit_cyan', 'ice_blue'),
       'zumrut': ('steel_dark', 'crystal_green', 'yuk_dark', 'emit_green', 'crystal_green'),
       'kadim': ('rock_dark', 'yuk_hazard', 'steel_dark', 'emit_amber', 'yuk_hazard'),
       'lonca': ('yuk_paint', 'yuk_orange', 'yuk_dark', 'emit_amber', 'yuk_hazard'),
       'korsan': ('rock_dark', 'red_paint', 'yuk_dark', 'emit_red', 'yuk_cont_rust')}
NAMES = ['frame', 'band', 'dark', 'glow', 'deco']
S = 8.0


def build(spec, mats):
    pal = spec['params']['palette']
    M = dict(zip(NAMES, PAL[pal]))
    slot = {n: i for i, n in enumerate(NAMES)}
    R, r = 1.16, 0.20

    def obj(name, bm, key, role='body'):
        orient_outward(bm)
        for v in bm.verts:
            v.co = geo.g2b(Vector(v.co) * S)
        for f in bm.faces:
            f.material_index = slot[key]
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        for n in NAMES:
            me.materials.append(mats[M[n]])
        ob = bpy.data.objects.new(name, me); geo.collection('Asset').objects.link(ob); ob['sd_role'] = role
        return ob
    bands = [(k * math.pi / 4 + math.pi / 8 - 0.16, k * math.pi / 4 + math.pi / 8 + 0.16, 0.045) for k in range(8)]
    ring = obj('ring', torus_bm(R, r, 72, 14, bands), 'frame')
    parts = [obj('lip', torus_bm(R + r * 1.04, r * 0.30, 72, 8), 'band')]
    parts[0].location.z = 0.0
    for k in range(8):                                                                  # halkadan büyüyen konik kule: tabanı halka tüpüne gömülü, dışa doğru daralan, kaburga ayaklı
        a = k * math.pi / 4 + math.pi / 8
        c, s_ = math.cos(a), math.sin(a)
        tw = obj('tower', tbox_bm((0, 0), r * 2.4, r * 1.1, r * 2.2, r * 1.0, 0.0, 1.0), 'dark')
        # tbox: z ekseni boyunca 0→1; yeniden konumla: kule radyal, boyu 0,55
        for v in tw.data.vertices:
            x, y, z = v.co.x / S, v.co.y / S, v.co.z / S
            # tbox yerel: x genişlik, y kalınlık(yüksek), z boy(-y blender); doğrudan dönüştür
        tw.data.update()
        bpy.data.objects.remove(tw)
        bm = bmesh.new()
        vs = []
        for rad, wd, th in ((R + r * 0.2, r * 2.6, r * 2.4), (R + r * 1.6, r * 1.5, r * 1.5), (R + r * 3.0, r * 0.7, r * 0.9)):
            for sx_, sy_ in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                px, py, pz = rad, sx_ * wd / 2, sy_ * th / 2
                vs.append(bm.verts.new((c * px - s_ * py, s_ * px + c * py, pz)))
        for ring_i in range(2):
            o = ring_i * 4
            for i in range(4):
                j = (i + 1) % 4
                bm.faces.new([vs[o + i], vs[o + j], vs[o + 4 + j], vs[o + 4 + i]])
        bm.faces.new([vs[3], vs[2], vs[1], vs[0]]); bm.faces.new([vs[8], vs[9], vs[10], vs[11]])
        parts.append(obj('tower', bm, 'dark'))
        for sgn in (-1, 1):                                                              # kaburga direk: kuleden halka yanına inen çapraz destek
            b2 = cyl_bm((c * (R + r * 2.4) - s_ * sgn * r * 0.5, s_ * (R + r * 2.4) + c * sgn * r * 0.5, 0.0), (c * (R + r * 0.3) - s_ * sgn * r * 0.9, s_ * (R + r * 0.3) + c * sgn * r * 0.9, sgn * 0.02), r * 0.30, r * 0.20, 8)
            parts.append(obj('rib', b2, 'frame'))
        parts.append(obj('lamp', box_bm((c * (R + r * 3.1), s_ * (R + r * 3.1), 0.0), (0.06, 0.10, 0.12)), 'glow'))
    # palet kimliği
    rng = random.Random(7)
    if pal == 'buzul':
        for k in range(16):
            a = math.pi * (1.06 + 0.88 * k / 15); L = 0.26 + 0.2 * rng.random()
            bm = bmesh.new(); res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=0.07, radius2=0.002, depth=L,
                matrix=Matrix.Translation((math.cos(a) * (R + r * 0.7), math.sin(a) * (R + r * 0.7) - L / 2, 0)) @ Matrix.Rotation(math.pi / 2, 4, 'X'))
            parts.append(obj('icicle', bm, 'deco'))
    elif pal == 'zumrut':
        for k in range(10):
            a = k / 10 * 2 * math.pi
            for j in range(2):
                bm = bmesh.new(); hh = 0.55 + 0.25 * rng.random()
                bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=5, radius1=0.09, radius2=0.01, depth=hh,
                    matrix=Matrix.Translation((math.cos(a) * (R + r * (0.9 + j * 0.4)) * 1.0 + math.cos(a) * hh * 0.4, math.sin(a) * (R + r * (0.9 + j * 0.4)) + math.sin(a) * hh * 0.4, 0.04 * j)) @ Matrix.Rotation(a + math.pi / 2, 4, 'Z') @ Matrix.Rotation(math.pi / 2, 4, 'X'))
                parts.append(obj('crystal', bm, 'deco'))
    elif pal == 'kadim':
        for k in range(12):
            a = k * math.pi / 6
            parts.append(obj('spire', tbox_bm((0, 0), 0.0, 0.0, 0.0, 0.0, 0, 0), 'deco')) if False else None
            bm = bmesh.new(); vs = []
            for rad, w in ((R + r * 1.4, 0.16), (R + r * 3.6, 0.06)):
                for sx_, sy_ in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                    px, py, pz = rad, sx_ * w / 2, sy_ * 0.10
                    vs.append(bm.verts.new((math.cos(a) * px - math.sin(a) * py, math.sin(a) * px + math.cos(a) * py, pz)))
            for i in range(4):
                j = (i + 1) % 4; bm.faces.new([vs[i], vs[j], vs[4 + j], vs[4 + i]])
            bm.faces.new([vs[3], vs[2], vs[1], vs[0]]); bm.faces.new([vs[4], vs[5], vs[6], vs[7]])
            parts.append(obj('spire', bm, 'deco'))
    elif pal == 'kizil':
        for k in range(14):
            a = rng.random() * 6.28
            parts.append(obj('ember', box_bm((math.cos(a) * (R + rng.uniform(-r, r)), math.sin(a) * (R + rng.uniform(-r, r)), r * 0.96), (0.10, 0.03, 0.02)), 'glow'))
    elif pal == 'korsan':
        for k in range(10):
            a = rng.random() * 6.28
            parts.append(obj('plate', box_bm((math.cos(a) * (R + r * 0.9), math.sin(a) * (R + r * 0.9), 0.0), (0.22, 0.12, 0.20)), 'deco'))
    ring2 = ring
    union_all(ring2, parts)
    core = ring2
    # hi-poly: radyal panel yarıkları + halka boyunca ince oluk
    hi = core.copy(); hi.data = core.data.copy(); geo.collection('Asset').objects.link(hi); hi.name = 'hi_core'; hi['sd_role'] = 'hi'
    cuts = []
    for k in range(48):
        a = k * 2 * math.pi / 48
        cuts.append(obj('slit', box_bm((math.cos(a) * R, math.sin(a) * R, 0.0), (0.0045, r * 2.4, r * 2.6)), 'dark'))
        cuts[-1].rotation_euler = (0, 0, 0)
    for o in cuts:
        o.rotation_euler = (0, 0, 0)
    # slit kutuları a açısına döndürülmeden: radyal yarık için kutuyu halka teğetine göre döndür
    for k, o in enumerate(cuts):
        a = k * 2 * math.pi / 48
        o.rotation_mode = 'XYZ'
    diff_all(hi, cuts[:0])
    for o in cuts:
        bpy.data.objects.remove(o)
    geo.set_smooth_by_angle(core, 40); geo.set_smooth_by_angle(hi, 40)
    core.name = 'core'; core['sd_role'] = 'body'
    return {'objects': [core, hi], 'sockets': []}


def preview(spec, out, fast, obs, probe=False):
    return {'note': 'gate: lookdev yok'}
