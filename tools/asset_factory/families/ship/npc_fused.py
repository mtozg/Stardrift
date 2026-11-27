"""NPC gemileri (Lead/Mehmet yeniden tasarım): sıfırdan, güçlü ayırt edilir silüet, açık/renkli palet, bütünleşik (UNION) gövde + hi-poly panel bake, nozul oyma + emissive çekirdek, ANCH_ENG/NAV.
Tür parametreleri TYPES içinde. Oyun uzayı: x yanal, y yukarı, z burun +, L=1."""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix
from core import geo
from families.ship.yuk_ext import orient_outward
from families.ship.yuk_fused import loft_bm, box_bm, cyl_bm, tbox_bm, boolean, union_all, diff_all
from families.ship.sahin_fused import wing_bm as _wb

NAMES = ['hull', 'acc', 'dark', 'glow', 'glass', 'acc2']
ACC2 = {'raider': 'npc_yellow', 'brute': 'npc_red2', 'reaver': 'npc_steel', 'corvette': 'npc_orange', 'cargo': 'npc_blue', 'tanker': 'npc_orange', 'courier': 'npc_orange', 'mining': 'npc_steel'}
PALS = {
    'raider': ('npc_rust', 'npc_orange', 'npc_dark', 'npc_glow'),
    'brute': ('npc_steel', 'npc_hazard', 'npc_dark', 'npc_glow'),
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
    pal = PALS[kind] + ('sahin_glass', ACC2[kind])
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

    WINGS = []

    def wing(sx, root, tip, thick=0.03):
        WINGS.append((sx, root, tip, thick))
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
    secs = None
    def rbox(c, sz, rot=(0, 0, 0)):
        bm = bmesh.new(); r = bmesh.ops.create_cube(bm, size=1.0)
        M = Matrix.Translation(Vector(c)) @ Matrix.Rotation(rot[2], 4, 'Z') @ Matrix.Rotation(rot[1], 4, 'Y') @ Matrix.Rotation(rot[0], 4, 'X') @ Matrix.Diagonal((*sz, 1.0))
        bmesh.ops.transform(bm, matrix=M, verts=r['verts'])
        return bm

    def env(z):
        for a, b in zip(secs, secs[1:]):
            if a[0] <= z <= b[0]:
                t = (z - a[0]) / (b[0] - a[0])
                return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, 5))
        return secs[0][1:5] if z < secs[0][0] else secs[-1][1:5]

    def greebles():
        W = P.get('detail', 1.0)
        lo, hi_ = secs[0][0] + 0.06, secs[-1][0] - 0.12
        for _ in range(int(3 * W)):                                                  # antenler
            z = rng.uniform(lo, hi_); w_, hu_, _, _ = env(z)
            x = rng.choice((-1, 1)) * w_ * rng.uniform(0.15, 0.35)
            parts.append(obj('ant', cyl_bm((x, hu_, z), (x + rng.uniform(-0.01, 0.01), hu_ + rng.uniform(0.05, 0.12), z), 0.004, 0.002, 6), 'dark'))
        for sx in (-1, 1):                                                           # üst borular + kelepçe
            z0 = rng.uniform(lo, lo + 0.15); z1 = z0 + rng.uniform(0.2, 0.4); zc = (z0 + z1) / 2
            w_, hu_, _, _ = env(zc); x = sx * w_ * 0.28
            parts.append(obj('pipe', cyl_bm((x, hu_ + 0.008, z0), (x, hu_ + 0.008, z1), 0.008, None, 8), 'acc'))
            for k in range(3):
                zz = z0 + (z1 - z0) * (k + 0.5) / 3
                parts.append(obj('clamp', box_bm((x, hu_ + 0.008, zz), (0.026, 0.026, 0.012)), 'dark'))
        for _ in range(int(5 * W)):                                                  # kapaklar / menhol
            z = rng.uniform(lo, hi_); w_, hu_, _, _ = env(z)
            x = rng.uniform(-0.55, 0.55) * w_
            sz = rng.uniform(0.04, 0.08)
            parts.append(obj('hatch', box_bm((x, hu_ + 0.002, z), (sz, 0.006, sz * 0.9)), 'acc' if rng.random() < 0.5 else 'dark'))
            parts.append(obj('hatchk', cyl_bm((x, hu_ + 0.006, z), (x, hu_ + 0.012, z), sz * 0.14, None, 8), 'dark'))
        for _ in range(int(2 * W)):                                                  # havalandırma ızgarası
            z = rng.uniform(lo, hi_ - 0.1); w_, hu_, _, _ = env(z)
            x = rng.uniform(-0.5, 0.5) * w_
            for k in range(5):
                parts.append(obj('vent', box_bm((x, hu_ + 0.002, z + k * 0.011), (0.06, 0.005, 0.005)), 'dark'))
        zz = lo
        while zz < hi_:                                                              # kaynak/derz çizgileri (gövdeyi enine kesen)
            w_, hu_, _, _ = env(zz)
            parts.append(obj('seam', box_bm((0, hu_ + 0.0015, zz), (w_ * 0.85, 0.004, 0.005)), 'dark'))
            zz += rng.uniform(0.09, 0.14)
        for sx in (-1, 1):                                                           # yan kablo/boru
            z0 = rng.uniform(lo + 0.05, lo + 0.2); z1 = z0 + rng.uniform(0.2, 0.35); zc = (z0 + z1) / 2
            w_, hu_, hd_, _ = env(zc)
            parts.append(obj('side', cyl_bm((sx * w_ / 2 * 1.005, 0.0, z0), (sx * w_ / 2 * 1.005, 0.0, z1), 0.006, None, 6), 'acc'))

    if kind == 'raider':      # agresif dart: keskin sivri burun, ileri keskin kanat, çift motor
        secs = [(-0.40, 0.14, 0.05, 0.04, 0.018, 0), (-0.2, 0.22, 0.06, 0.05, 0.022, 0), (0.0, 0.20, 0.06, 0.05, 0.02, 0), (0.25, 0.10, 0.04, 0.035, 0.014, 0), (0.50, 0.012, 0.008, 0.008, 0.003, 0)]
        hull = obj('hull', loft_bm(secs), 'hull')
        for sx in (-1, 1):
            parts.append(obj('w', wing(sx, (0.05, 0.12, -0.28), (0.42, -0.02, -0.12, -0.34), 0.09), 'acc'))
            parts.append(obj('fin', box_bm((sx * 0.07, 0.06, -0.33), (0.012, 0.11, 0.14)), 'dark'))
        ENG = [(-0.06, 0.0), (0.06, 0.0)]
        for x, y in ENG: parts.append(obj('nac', cyl_bm((x, y, -0.5), (x, y, -0.25), 0.055, 0.05, 14), 'dark'))
    elif kind == 'brute':     # kalın zırhlı blok, geniş omuz zırhı, tek büyük motor bloğu
        secs = [(-0.42, 0.50, 0.16, 0.14, 0.06, 0), (-0.2, 0.62, 0.20, 0.17, 0.07, 0), (0.1, 0.64, 0.20, 0.17, 0.07, 0), (0.32, 0.46, 0.15, 0.13, 0.06, 0), (0.5, 0.18, 0.07, 0.06, 0.03, 0)]
        hull = obj('hull', loft_bm(secs), 'hull')
        for sx in (-1, 1):
            parts.append(obj('pl', box_bm((sx * 0.34, 0.07, 0.02), (0.20, 0.08, 0.36)), 'acc'))
            parts.append(obj('pl2', box_bm((sx * 0.30, -0.08, -0.14), (0.16, 0.06, 0.30)), 'acc'))
            parts.append(obj('gun', cyl_bm((sx * 0.20, 0.0, 0.30), (sx * 0.20, 0.0, 0.58), 0.025, 0.02, 8), 'dark'))
        ENG = [(-0.18, 0.0), (0.0, 0.0), (0.18, 0.0)]
        for x, y in ENG: parts.append(obj('nac', cyl_bm((x, y, -0.5), (x, y, -0.3), 0.075, 0.07, 14), 'dark'))
    elif kind == 'reaver':    # hurda parçalı asimetrik
        secs = [(-0.42, 0.26, 0.09, 0.08, 0.035, 0), (-0.15, 0.36, 0.11, 0.09, 0.04, 0), (0.15, 0.30, 0.10, 0.08, 0.035, 0), (0.50, 0.04, 0.03, 0.025, 0.01, 0)]
        hull = obj('hull', loft_bm(secs), 'hull')
        for i in range(9):
            a = rng.uniform(0, 6.28); r_ = rng.uniform(0.14, 0.34); z = rng.uniform(-0.38, 0.28)
            parts.append(obj('scrap', box_bm((math.cos(a) * r_ * 0.9, math.sin(a) * r_ * 0.35 + 0.02, z), (rng.uniform(0.07, 0.18), rng.uniform(0.04, 0.09), rng.uniform(0.10, 0.22))), 'acc' if i % 2 else 'dark'))
        parts.append(obj('w', wing(1, (0.10, 0.05, -0.30), (0.46, 0.04, -0.15, -0.32), 0.05), 'acc'))
        parts.append(obj('w', wing(-1, (0.10, 0.0, -0.28), (0.30, -0.05, -0.20, -0.30), 0.05), 'dark'))
        ENG = [(-0.09, 0.02), (0.11, -0.02), (0.0, 0.07)]
        for x, y in ENG: parts.append(obj('nac', cyl_bm((x, y, -0.5), (x, y, -0.28), 0.05, 0.045, 12), 'dark'))
    elif kind == 'corvette':  # dengeli savaş gemisi
        secs = [(-0.45, 0.22, 0.08, 0.07, 0.03, 0), (-0.2, 0.32, 0.10, 0.09, 0.04, 0), (0.1, 0.30, 0.10, 0.09, 0.04, 0), (0.35, 0.18, 0.07, 0.06, 0.03, 0), (0.5, 0.05, 0.03, 0.025, 0.01, 0)]
        hull = obj('hull', loft_bm(secs), 'hull')
        for sx in (-1, 1):
            parts.append(obj('w', wing(sx, (0.10, 0.10, -0.30), (0.36, -0.01, -0.10, -0.34), 0.09), 'acc'))
        parts.append(obj('bridge', box_bm((0, 0.115, -0.10), (0.14, 0.07, 0.24)), 'acc'))
        for z in (0.1, 0.28):
            parts.append(obj('tur', cyl_bm((0, 0.10, z), (0, 0.15, z), 0.04, None, 12), 'dark'))
        ENG = [(-0.09, 0.0), (0.09, 0.0)]
        for x, y in ENG: parts.append(obj('nac', cyl_bm((x, y, -0.53), (x, y, -0.35), 0.06, 0.055, 14), 'dark'))
    elif kind == 'cargo':     # kutu konteynerli
        secs = [(-0.45, 0.18, 0.07, 0.06, 0.025, 0), (-0.25, 0.22, 0.08, 0.07, 0.03, 0), (0.30, 0.20, 0.07, 0.06, 0.03, 0), (0.5, 0.08, 0.04, 0.035, 0.015, 0)]
        hull = obj('hull', loft_bm(secs), 'hull')
        for i, z in enumerate((-0.28, -0.10, 0.08, 0.26)):
            for sx in (-1, 1):
                parts.append(obj('cont', box_bm((sx * 0.17, 0.0, z), (0.14, 0.15, 0.15)), 'acc' if (i + (sx > 0)) % 2 else 'dark'))
        parts.append(obj('cab', box_bm((0, 0.085, 0.38), (0.10, 0.08, 0.14)), 'acc'))
        ENG = [(-0.06, 0.0), (0.06, 0.0)]
        for x, y in ENG: parts.append(obj('nac', cyl_bm((x, y, -0.52), (x, y, -0.4), 0.05, 0.045, 12), 'dark'))
    elif kind == 'tanker':    # büyük tanklar
        secs = [(-0.42, 0.10, 0.04, 0.04, 0.015, 0), (0.30, 0.10, 0.04, 0.04, 0.015, 0), (0.5, 0.05, 0.03, 0.03, 0.01, 0)]
        hull = obj('hull', loft_bm(secs), 'hull')
        for sx, sy in ((-1, 1), (1, 1), (-1, -1), (1, -1)):
            parts.append(obj('tank', cyl_bm((sx * 0.11, sy * 0.11, -0.36), (sx * 0.11, sy * 0.11, 0.20), 0.095, 0.095, 16), 'acc' if sy > 0 else 'hull'))
        parts.append(obj('bridge', box_bm((0, 0.0, 0.34), (0.12, 0.12, 0.2)), 'acc'))
        ENG = [(-0.07, 0.0), (0.07, 0.0)]
        for x, y in ENG: parts.append(obj('nac', cyl_bm((x, y, -0.52), (x, y, -0.4), 0.055, 0.05, 12), 'dark'))
    elif kind == 'courier':   # ince/hızlı
        secs = [(-0.40, 0.10, 0.04, 0.035, 0.014, 0), (-0.1, 0.14, 0.05, 0.04, 0.018, 0), (0.2, 0.10, 0.04, 0.03, 0.014, 0), (0.50, 0.01, 0.01, 0.01, 0.003, 0)]
        hull = obj('hull', loft_bm(secs), 'hull')
        for sx in (-1, 1):
            parts.append(obj('w', wing(sx, (0.06, 0.0, -0.30), (0.30, -0.01, -0.22, -0.38), 0.02), 'acc'))
        ENG = [(0.0, 0.0)]
        parts.append(obj('nac', cyl_bm((0, 0, -0.5), (0, 0, -0.3), 0.06, 0.055, 14), 'dark'))
    elif kind == 'mining':    # madenci: iki kol + kazı başlığı
        secs = [(-0.45, 0.22, 0.09, 0.08, 0.035, 0), (-0.1, 0.30, 0.10, 0.09, 0.04, 0), (0.25, 0.24, 0.09, 0.08, 0.035, 0), (0.5, 0.10, 0.05, 0.04, 0.02, 0)]
        hull = obj('hull', loft_bm(secs), 'hull')
        for sx in (-1, 1):
            parts.append(obj('arm', cyl_bm((sx * 0.12, -0.04, 0.2), (sx * 0.20, -0.07, 0.5), 0.035, 0.028, 8), 'dark'))
            parts.append(obj('drill', cyl_bm((sx * 0.20, -0.07, 0.5), (sx * 0.22, -0.08, 0.60), 0.05, 0.005, 10), 'acc'))
            parts.append(obj('pod', box_bm((sx * 0.20, 0.0, -0.10), (0.10, 0.10, 0.30)), 'acc'))
        ENG = [(-0.08, 0.0), (0.08, 0.0)]
        for x, y in ENG: parts.append(obj('nac', cyl_bm((x, y, -0.53), (x, y, -0.35), 0.06, 0.055, 12), 'dark'))
    greebles()
    for (sx, root, tip, th) in WINGS:                                                  # kanat nervürleri + hücum/firar kenarı şeridi
        chord_r = abs(root[1] - root[2]); chord_t = abs(tip[2] - tip[3])
        for t in (0.2, 0.4, 0.6, 0.8):
            x = root[0] + (tip[0] - root[0]) * t
            zl = root[1] + (tip[2] - root[1]) * t; zt = root[2] + (tip[3] - root[2]) * t
            ytop = (th / 2) * (1 - t) + tip[1] + th * .15 * t
            parts.append(obj('rib', box_bm((sx * x, ytop + 0.004, (zl + zt) / 2), (0.014, 0.012, abs(zl - zt) * 0.9)), 'dark'))
        for t in (0.5,):
            x = root[0] + (tip[0] - root[0]) * t; zl = root[1] + (tip[2] - root[1]) * t
            parts.append(obj('le', box_bm((sx * x, tip[1] * t, zl), (abs(tip[0] - root[0]) * 1.0, th * 0.7, 0.014)), 'acc2'))
    if kind == 'brute':
        zs = [-0.30, -0.18, -0.06, 0.06, 0.18]
        for z in zs:                                                                  # ağır zırh kaburga + kaynak izi
            w_, hu_, hd_, _ = env(z)
            parts.append(obj('rib', box_bm((0, hu_ + 0.01, z), (w_ * 0.95, 0.026, 0.035)), 'acc'))
            for sx in (-1, 1):
                parts.append(obj('sidepl', box_bm((sx * (w_ / 2 + 0.008), 0.0, z + 0.06), (0.016, (hu_ + hd_) * 0.8, 0.10)), 'acc'))
                for k in range(3):
                    parts.append(obj('weld', box_bm((sx * (w_ / 2 + 0.018), -0.03 + k * 0.03, z + 0.01), (0.006, 0.012, 0.02)), 'dark'))
    elif kind == 'reaver':
        for k in range(14):                                                           # kaynaklı hurda plaka/kiriş parçaları
            z = rng.uniform(-0.38, 0.30); w_, hu_, hd_, _ = env(z)
            x = rng.uniform(-1, 1) * w_ * 0.6; y = rng.uniform(-hd_, hu_)
            if k % 3 == 0:
                parts.append(obj('beam', rbox((x, y, z), (0.02, 0.02, rng.uniform(0.14, 0.26)), (rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), 0)), 'dark'))
            else:
                parts.append(obj('plate', rbox((x, y + 0.03, z), (rng.uniform(0.07, 0.15), 0.012, rng.uniform(0.07, 0.15)), (rng.uniform(-0.7, 0.7), rng.uniform(-0.7, 0.7), rng.uniform(0, 3))), 'acc' if k % 2 else 'hull'))
    elif kind == 'tanker':
        for sx, sy in ((-1, 1), (1, 1), (-1, -1), (1, -1)):
            for z in (-0.28, -0.12, 0.04):                                            # tank bantları + vana
                parts.append(obj('band', cyl_bm((sx * 0.11, sy * 0.11, z - 0.012), (sx * 0.11, sy * 0.11, z + 0.012), 0.102, None, 16), 'dark'))
            parts.append(obj('valve', cyl_bm((sx * 0.11, sy * 0.11 + sy * 0.09, -0.1), (sx * 0.11, sy * 0.11 + sy * 0.13, -0.1), 0.014, None, 8), 'acc'))
        for k in range(8):                                                            # merdiven
            parts.append(obj('ladder', box_bm((0.0, 0.17, -0.2 + k * 0.05), (0.05, 0.004, 0.006)), 'dark'))
    elif kind == 'corvette':
        for sx in (-1, 1):
            parts.append(obj('pod', box_bm((sx * 0.20, 0.13, 0.05), (0.10, 0.08, 0.30)), 'acc'))
            parts.append(obj('cann', cyl_bm((sx * 0.20, 0.13, 0.20), (sx * 0.20, 0.13, 0.44), 0.022, 0.016, 8), 'dark'))
            parts.append(obj('radar', cyl_bm((sx * 0.07, 0.20, -0.22), (sx * 0.07, 0.21, -0.22), 0.05, 0.01, 12), 'acc2'))
            parts.append(obj('mast', cyl_bm((sx * 0.07, 0.15, -0.22), (sx * 0.07, 0.20, -0.22), 0.008, None, 6), 'dark'))
        parts.append(obj('hangar', box_bm((0, 0.05, -0.38), (0.16, 0.06, 0.12)), 'dark'))
    elif kind == 'cargo':
        parts.append(obj('crane', cyl_bm((0, 0.09, 0.08), (0, 0.24, 0.08), 0.014, 0.01, 8), 'dark'))
        parts.append(obj('craneb', box_bm((0, 0.24, -0.02), (0.012, 0.012, 0.2)), 'dark'))
        for i, z in enumerate((-0.28, -0.10, 0.08, 0.26)):
            for sx in (-1, 1):
                parts.append(obj('door', box_bm((sx * 0.17, 0.0, z + 0.077), (0.14, 0.12, 0.004)), 'dark'))
                parts.append(obj('lock', box_bm((sx * 0.17 + 0.03, 0.0, z + 0.081), (0.012, 0.05, 0.008)), 'acc'))
                for q in range(3):
                    parts.append(obj('rib', box_bm((sx * 0.17 - 0.04 + q * 0.04, 0.083, z), (0.006, 0.006, 0.15)), 'dark'))
    union_all(hull, parts)
    core = hull
    diff_all(core, [obj('noz', cyl_bm((x, y, -0.62), (x, y, -0.47), 0.042, 0.036, 14), 'dark') for x, y in ENG])
    # r4: BÜYÜK ölçekli kontrast bantları (uzaktan okunur): gövde enine renk bantları + orta şerit
    bmz = bmesh.new(); bmz.from_mesh(core.data)
    for f in bmz.faces:
        if f.material_index != slot['hull']:
            continue
        cb = f.calc_center_median(); gx, gy, gz = cb.x / S, cb.z / S, -cb.y / S
        if int((gz + 0.6) / 0.16) % 5 == 0:          # ince koyu panel kuşağı (düz renk bant DEĞİL: gerçekçi derz/koyu zırh kuşağı)
            f.material_index = slot['dark']
    bmz.to_mesh(core.data); bmz.free()
    # hi-poly: oluklar
    hi = core.copy(); hi.data = core.data.copy(); geo.collection('Asset').objects.link(hi); hi.name = 'hi_core'; hi['sd_role'] = 'hi'
    geo.set_smooth_by_angle(core, 38); geo.set_smooth_by_angle(hi, 38)
    core.name = 'core'; core['sd_role'] = 'body'
    out_body, out_hi = [core], [hi]

    def small(name, bm_, key):
        o = obj(name, bm_, key); geo.set_smooth_by_angle(o, 35); out_body.append(o)
        h = o.copy(); h.data = o.data.copy(); geo.collection('Asset').objects.link(h); h['sd_role'] = 'hi'; out_hi.append(h)
    for x, y in ENG:
        small('core', cyl_bm((x, y, -0.470), (x, y, -0.484), 0.045, None, 14), 'glow')
    _w, _hu, _hd, _ = env(0.2)
    navs = [(_w / 2, 0.0, 0.2), (-_w / 2, 0.0, 0.2), (0.0, _hu, -0.4)]
    for p in navs:
        small('nav', box_bm(p, (0.04, 0.04, 0.04)), 'glow')
    for sx in (-1, 1):                                                              # emissive seyir/gövde ışık şeritleri
        zc = secs[len(secs) // 2][0]; w_, hu_, hd_, _ = env(zc)
        small('strip', box_bm((sx * w_ / 2 * 1.01, 0.0, zc), (0.012, 0.022, 0.30)), 'glow')
        small('strip2', box_bm((sx * w_ * 0.30, hu_ * 1.01, -0.10), (0.02, 0.008, 0.22)), 'glow')
    small('canopy', loft_bm([(0.12, 0.07, 0.03, 0.002, 0.012, 0.06), (0.22, 0.09, 0.04, 0.002, 0.016, 0.06), (0.32, 0.05, 0.025, 0.002, 0.01, 0.06)]), 'glass') if kind not in ('tanker', 'cargo') else None
    socks = []
    for i, (x, y) in enumerate(ENG, 1):
        socks.append({'name': 'ANCH_ENG_%d' % i, 'loc': tuple(geo.g2b(Vector((x, y, -0.48)) * S)), 'dir': (0.0, 1.0, 0.0), 'extras': {'kind': 'engine'}})
    for i, p in enumerate(navs, 1):
        socks.append({'name': 'ANCH_NAV_%d' % i, 'loc': tuple(geo.g2b(Vector(p) * S)), 'dir': (0.0, 0.0, 1.0), 'extras': {'kind': 'nav'}})
    socks.append({'name': 'ANCH_MUZ_1', 'loc': tuple(geo.g2b(Vector((0, 0.0, 0.5)) * S)), 'dir': (0.0, -1.0, 0.0), 'extras': {'kind': 'muzzle'}})
    return {'objects': out_body + out_hi, 'sockets': socks}
