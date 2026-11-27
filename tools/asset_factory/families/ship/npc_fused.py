"""NPC gemileri (Lead/Mehmet yeniden tasarım): sıfırdan, güçlü ayırt edilir silüet, açık/renkli palet, bütünleşik (UNION) gövde + hi-poly panel bake, nozul oyma + emissive çekirdek, ANCH_ENG/NAV.
Tür parametreleri TYPES içinde. Oyun uzayı: x yanal, y yukarı, z burun +, L=1."""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix
from core import geo
from families.ship.yuk_ext import orient_outward
from families.ship.yuk_fused import loft_bm, box_bm, cyl_bm, tbox_bm, boolean, union_all, diff_all
from families.ship.sahin_fused import wing_bm as _wb

NAMES = ['hull', 'acc', 'dark', 'glow', 'glass']
PALS = {
    'raider': ('npc_rust', 'npc_orange', 'npc_dark', 'npc_glow'),
    'brute': ('npc_rust2', 'npc_rust', 'npc_dark', 'npc_glow'),
    'reaver': ('npc_rust', 'npc_gray', 'npc_dark', 'npc_glow'),
    'corvette': ('npc_blue', 'npc_white', 'npc_dark', 'npc_glowb'),
    'cargo': ('npc_gray', 'npc_orange', 'npc_dark', 'npc_glow'),
    'tanker': ('npc_yellow', 'npc_gray', 'npc_dark', 'npc_glow'),
    'courier': ('npc_white', 'npc_blue', 'npc_dark', 'npc_glowb'),
    'mining': ('npc_orange', 'npc_yellow', 'npc_dark', 'npc_glow'),
}
S = 30.0


def build(spec, mats):
    P = spec['params']; kind = P['kind']
    pal = PALS[kind] + ('sahin_glass',)
    M = dict(zip(NAMES, pal)); slot = {n: i for i, n in enumerate(NAMES)}
    rng = random.Random(P.get('seed', 1))

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

    def wing(sx, root, tip, thick=0.03):
        """root=(x,zle,zte), tip=(x,y,zle,zte), kalınlık kökte thick, uçta thick*0.3"""
        bm = bmesh.new()
        def V(x, y, z): return bm.verts.new((sx * x, y, z))
        rt = [V(root[0], thick / 2, root[1]), V(root[0], thick / 2, root[2])]
        rb = [V(root[0], -thick / 2, root[1]), V(root[0], -thick / 2, root[2])]
        tt = [V(tip[0], tip[1] + thick * .15, tip[2]), V(tip[0], tip[1] + thick * .15, tip[3])]
        tb = [V(tip[0], tip[1] - thick * .15, tip[2]), V(tip[0], tip[1] - thick * .15, tip[3])]
        q = [(rt[0], rt[1], tt[1], tt[0]), (rb[1], rb[0], tb[0], tb[1]), (rt[0], tt[0], tb[0], rb[0]), (rt[1], rb[1], tb[1], tt[1]), (rt[0], rb[0], rb[1], rt[1]), (tt[0], tt[1], tb[1], tb[0])]
        for f in q:
            bm.faces.new(f if sx > 0 else f[::-1])
        return bm

    parts = []; ENG = []; small_items = []
    if kind == 'raider':      # agresif dart: keskin sivri burun, ileri keskin kanat, çift motor
        hull = obj('hull', loft_bm([(-0.40, 0.14, 0.05, 0.04, 0.018, 0), (-0.2, 0.22, 0.06, 0.05, 0.022, 0), (0.0, 0.20, 0.06, 0.05, 0.02, 0), (0.25, 0.10, 0.04, 0.035, 0.014, 0), (0.50, 0.012, 0.008, 0.008, 0.003, 0)]), 'hull')
        for sx in (-1, 1):
            parts.append(obj('w', wing(sx, (0.05, 0.12, -0.28), (0.42, -0.02, -0.12, -0.34), 0.05), 'acc'))
            parts.append(obj('fin', box_bm((sx * 0.07, 0.06, -0.33), (0.012, 0.11, 0.14)), 'dark'))
        ENG = [(-0.06, 0.0), (0.06, 0.0)]
        for x, y in ENG: parts.append(obj('nac', cyl_bm((x, y, -0.5), (x, y, -0.25), 0.055, 0.05, 14), 'dark'))
    elif kind == 'brute':     # kalın zırhlı blok, geniş omuz zırhı, tek büyük motor bloğu
        hull = obj('hull', loft_bm([(-0.42, 0.50, 0.16, 0.14, 0.06, 0), (-0.2, 0.62, 0.20, 0.17, 0.07, 0), (0.1, 0.64, 0.20, 0.17, 0.07, 0), (0.32, 0.46, 0.15, 0.13, 0.06, 0), (0.5, 0.18, 0.07, 0.06, 0.03, 0)]), 'hull')
        for sx in (-1, 1):
            parts.append(obj('pl', box_bm((sx * 0.34, 0.07, 0.02), (0.20, 0.08, 0.36)), 'acc'))
            parts.append(obj('pl2', box_bm((sx * 0.30, -0.08, -0.14), (0.16, 0.06, 0.30)), 'acc'))
            parts.append(obj('gun', cyl_bm((sx * 0.20, 0.0, 0.30), (sx * 0.20, 0.0, 0.58), 0.025, 0.02, 8), 'dark'))
        ENG = [(-0.18, 0.0), (0.0, 0.0), (0.18, 0.0)]
        for x, y in ENG: parts.append(obj('nac', cyl_bm((x, y, -0.5), (x, y, -0.3), 0.075, 0.07, 14), 'dark'))
    elif kind == 'reaver':    # hurda parçalı asimetrik
        hull = obj('hull', loft_bm([(-0.42, 0.26, 0.09, 0.08, 0.035, 0), (-0.15, 0.36, 0.11, 0.09, 0.04, 0), (0.15, 0.30, 0.10, 0.08, 0.035, 0), (0.50, 0.04, 0.03, 0.025, 0.01, 0)]), 'hull')
        for i in range(9):
            a = rng.uniform(0, 6.28); r_ = rng.uniform(0.14, 0.34); z = rng.uniform(-0.38, 0.28)
            parts.append(obj('scrap', box_bm((math.cos(a) * r_ * 0.9, math.sin(a) * r_ * 0.35 + 0.02, z), (rng.uniform(0.07, 0.18), rng.uniform(0.04, 0.09), rng.uniform(0.10, 0.22))), 'acc' if i % 2 else 'dark'))
        parts.append(obj('w', wing(1, (0.10, 0.05, -0.30), (0.46, 0.04, -0.15, -0.32), 0.05), 'acc'))
        parts.append(obj('w', wing(-1, (0.10, 0.0, -0.28), (0.30, -0.05, -0.20, -0.30), 0.05), 'dark'))
        ENG = [(-0.09, 0.02), (0.11, -0.02), (0.0, 0.07)]
        for x, y in ENG: parts.append(obj('nac', cyl_bm((x, y, -0.5), (x, y, -0.28), 0.05, 0.045, 12), 'dark'))
    elif kind == 'corvette':  # dengeli savaş gemisi
        hull = obj('hull', loft_bm([(-0.45, 0.22, 0.08, 0.07, 0.03, 0), (-0.2, 0.32, 0.10, 0.09, 0.04, 0), (0.1, 0.30, 0.10, 0.09, 0.04, 0), (0.35, 0.18, 0.07, 0.06, 0.03, 0), (0.5, 0.05, 0.03, 0.025, 0.01, 0)]), 'hull')
        for sx in (-1, 1):
            parts.append(obj('w', wing(sx, (0.10, 0.10, -0.30), (0.36, -0.01, -0.10, -0.34), 0.05), 'acc'))
        parts.append(obj('bridge', box_bm((0, 0.115, -0.10), (0.14, 0.07, 0.24)), 'acc'))
        for z in (0.1, 0.28):
            parts.append(obj('tur', cyl_bm((0, 0.10, z), (0, 0.15, z), 0.04, None, 12), 'dark'))
        ENG = [(-0.09, 0.0), (0.09, 0.0)]
        for x, y in ENG: parts.append(obj('nac', cyl_bm((x, y, -0.53), (x, y, -0.35), 0.06, 0.055, 14), 'dark'))
    elif kind == 'cargo':     # kutu konteynerli
        hull = obj('hull', loft_bm([(-0.45, 0.18, 0.07, 0.06, 0.025, 0), (-0.25, 0.22, 0.08, 0.07, 0.03, 0), (0.30, 0.20, 0.07, 0.06, 0.03, 0), (0.5, 0.08, 0.04, 0.035, 0.015, 0)]), 'hull')
        for i, z in enumerate((-0.28, -0.10, 0.08, 0.26)):
            for sx in (-1, 1):
                parts.append(obj('cont', box_bm((sx * 0.17, 0.0, z), (0.14, 0.15, 0.15)), 'acc' if (i + (sx > 0)) % 2 else 'dark'))
        parts.append(obj('cab', box_bm((0, 0.085, 0.38), (0.10, 0.08, 0.14)), 'acc'))
        ENG = [(-0.06, 0.0), (0.06, 0.0)]
        for x, y in ENG: parts.append(obj('nac', cyl_bm((x, y, -0.52), (x, y, -0.4), 0.05, 0.045, 12), 'dark'))
    elif kind == 'tanker':    # büyük tanklar
        hull = obj('hull', loft_bm([(-0.42, 0.10, 0.04, 0.04, 0.015, 0), (0.30, 0.10, 0.04, 0.04, 0.015, 0), (0.5, 0.05, 0.03, 0.03, 0.01, 0)]), 'hull')
        for sx, sy in ((-1, 1), (1, 1), (-1, -1), (1, -1)):
            parts.append(obj('tank', cyl_bm((sx * 0.11, sy * 0.11, -0.36), (sx * 0.11, sy * 0.11, 0.20), 0.095, 0.095, 16), 'acc' if sy > 0 else 'hull'))
        parts.append(obj('bridge', box_bm((0, 0.0, 0.34), (0.12, 0.12, 0.2)), 'acc'))
        ENG = [(-0.07, 0.0), (0.07, 0.0)]
        for x, y in ENG: parts.append(obj('nac', cyl_bm((x, y, -0.52), (x, y, -0.4), 0.055, 0.05, 12), 'dark'))
    elif kind == 'courier':   # ince/hızlı
        hull = obj('hull', loft_bm([(-0.40, 0.10, 0.04, 0.035, 0.014, 0), (-0.1, 0.14, 0.05, 0.04, 0.018, 0), (0.2, 0.10, 0.04, 0.03, 0.014, 0), (0.50, 0.01, 0.01, 0.01, 0.003, 0)]), 'hull')
        for sx in (-1, 1):
            parts.append(obj('w', wing(sx, (0.06, 0.0, -0.30), (0.30, -0.01, -0.22, -0.38), 0.02), 'acc'))
        ENG = [(0.0, 0.0)]
        parts.append(obj('nac', cyl_bm((0, 0, -0.5), (0, 0, -0.3), 0.06, 0.055, 14), 'dark'))
    elif kind == 'mining':    # madenci: iki kol + kazı başlığı
        hull = obj('hull', loft_bm([(-0.45, 0.22, 0.09, 0.08, 0.035, 0), (-0.1, 0.30, 0.10, 0.09, 0.04, 0), (0.25, 0.24, 0.09, 0.08, 0.035, 0), (0.5, 0.10, 0.05, 0.04, 0.02, 0)]), 'hull')
        for sx in (-1, 1):
            parts.append(obj('arm', cyl_bm((sx * 0.12, -0.04, 0.2), (sx * 0.20, -0.07, 0.5), 0.035, 0.028, 8), 'dark'))
            parts.append(obj('drill', cyl_bm((sx * 0.20, -0.07, 0.5), (sx * 0.22, -0.08, 0.60), 0.05, 0.005, 10), 'acc'))
            parts.append(obj('pod', box_bm((sx * 0.20, 0.0, -0.10), (0.10, 0.10, 0.30)), 'acc'))
        ENG = [(-0.08, 0.0), (0.08, 0.0)]
        for x, y in ENG: parts.append(obj('nac', cyl_bm((x, y, -0.53), (x, y, -0.35), 0.06, 0.055, 12), 'dark'))
    union_all(hull, parts)
    core = hull
    diff_all(core, [obj('noz', cyl_bm((x, y, -0.62), (x, y, -0.47), 0.042, 0.036, 14), 'dark') for x, y in ENG])
    # hi-poly: oluklar
    hi = core.copy(); hi.data = core.data.copy(); geo.collection('Asset').objects.link(hi); hi.name = 'hi_core'; hi['sd_role'] = 'hi'
    geo.set_smooth_by_angle(core, 38); geo.set_smooth_by_angle(hi, 38)
    core.name = 'core'; core['sd_role'] = 'body'
    out_body, out_hi = [core], [hi]

    def small(name, bm_, key):
        o = obj(name, bm_, key); geo.set_smooth_by_angle(o, 35); out_body.append(o)
        h = o.copy(); h.data = o.data.copy(); geo.collection('Asset').objects.link(h); h['sd_role'] = 'hi'; out_hi.append(h)
    for x, y in ENG:
        small('core', cyl_bm((x, y, -0.475), (x, y, -0.482), 0.032, None, 12), 'glow')
    navs = [(0.32 if kind != 'tanker' else 0.24, 0.0, 0.2), (-0.32 if kind != 'tanker' else -0.24, 0.0, 0.2), (0.0, 0.1, -0.4)]
    for p in navs:
        small('nav', box_bm(p, (0.02, 0.02, 0.02)), 'glow')
    small('canopy', loft_bm([(0.12, 0.07, 0.03, 0.002, 0.012, 0.06), (0.22, 0.09, 0.04, 0.002, 0.016, 0.06), (0.32, 0.05, 0.025, 0.002, 0.01, 0.06)]), 'glass') if kind not in ('tanker', 'cargo') else None
    socks = []
    for i, (x, y) in enumerate(ENG, 1):
        socks.append({'name': 'ANCH_ENG_%d' % i, 'loc': tuple(geo.g2b(Vector((x, y, -0.48)) * S)), 'dir': (0.0, 1.0, 0.0), 'extras': {'kind': 'engine'}})
    for i, p in enumerate(navs, 1):
        socks.append({'name': 'ANCH_NAV_%d' % i, 'loc': tuple(geo.g2b(Vector(p) * S)), 'dir': (0.0, 0.0, 1.0), 'extras': {'kind': 'nav'}})
    socks.append({'name': 'ANCH_MUZ_1', 'loc': tuple(geo.g2b(Vector((0, 0.0, 0.5)) * S)), 'dir': (0.0, -1.0, 0.0), 'extras': {'kind': 'muzzle'}})
    return {'objects': out_body + out_hi, 'sockets': socks}
