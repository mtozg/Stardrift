"""NPC — BÜTÜNLEŞİK bölümlü-loft gövde (Yük/Hayalet/Şahin hattı). Lead 2026-11-27: NPC'ler blok/LEGO okunuyor → aerodinamik/organik silüet, farklı kesitli gövde bölümleri,
Boolean UNION (gövde+kanat+nacelle+kuyruk) → nozul oyma → ızgara bölme → yüz bazlı renk bölgeleri → hi-poly oluk/kabartma bake. Palet: pas-kahve / gri-çelik / sarı-turuncu (mevcut NPC'lere yakın).
Oyun uzayı (x yanal, y yukarı, z burun +), L=1. kind: raider | brute | reaver."""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix
from core import geo
from families.ship.yuk_ext import orient_outward
from families.ship.yuk_fused import loft_bm as _loft_bm, box_bm, cyl_bm, tbox_bm, ring_bm, boolean, union_all, diff_all

def loft_bm(secs):
    """pah kesit yüksekliği/genişliğine sığmazsa kesit kendini keser (Boolean bozulur) → pahı sınırla"""
    out = []
    for z, w, hu, hd, ch, y0 in secs:
        out.append((z, w, hu, hd, min(ch, (hu + hd) / 2 * 0.92, w / 2 * 0.92), y0))
    return _loft_bm(out)


NAMES = ['hull', 'acc', 'dark', 'glow', 'glass', 'acc2']
PAL = {
    'raider': ('npc_rust', 'npc_steel', 'npc_dark', 'npc_glow', 'sahin_glass', 'npc_orange'),
    'brute': ('npc_steel', 'npc_hazard', 'npc_dark', 'npc_glow', 'sahin_glass', 'npc_rust2'),
    'reaver': ('npc_rust2', 'npc_steel', 'npc_dark', 'npc_glow', 'sahin_glass', 'npc_orange'),
    'courier': ('npc_gray', 'npc_orange', 'npc_dark', 'npc_glow', 'sahin_glass', 'npc_steel'),
    'corvette': ('npc_steel', 'npc_orange', 'npc_dark', 'npc_glow', 'sahin_glass', 'npc_rust2'),
    'cargo': ('npc_steel', 'npc_hazard', 'npc_dark', 'npc_glow', 'sahin_glass', 'npc_rust'),
    'tanker': ('npc_steel', 'npc_hazard', 'npc_dark', 'npc_glow', 'sahin_glass', 'npc_rust'),
    'mining': ('npc_rust', 'npc_hazard', 'npc_dark', 'npc_glow', 'sahin_glass', 'npc_steel'),
}
ENGR = {'raider': 0.058, 'brute': 0.075, 'reaver': 0.06, 'courier': 0.05, 'corvette': 0.06, 'cargo': 0.06, 'tanker': 0.07, 'mining': 0.062}
SC = {'raider': 26.0, 'brute': 44.0, 'reaver': 58.0, 'courier': 16.0, 'corvette': 38.0, 'cargo': 70.0, 'tanker': 90.0, 'mining': 52.0}

# gövde bölümleri (z, genişlik, üst yükseklik, alt yükseklik, pah, y-ofset)
SECS = {
    'raider': [(-0.50, 0.12, 0.050, 0.045, 0.015, 0), (-0.42, 0.18, 0.075, 0.060, 0.025, 0), (-0.28, 0.21, 0.088, 0.066, 0.032, 0), (-0.10, 0.19, 0.084, 0.060, 0.030, 0.002),
               (0.08, 0.145, 0.070, 0.050, 0.026, 0.006), (0.24, 0.095, 0.052, 0.036, 0.020, 0.010), (0.38, 0.055, 0.034, 0.024, 0.014, 0.012), (0.46, 0.028, 0.020, 0.014, 0.008, 0.012), (0.50, 0.010, 0.008, 0.007, 0.004, 0.012)],
    'brute': [(-0.50, 0.30, 0.13, 0.10, 0.06, 0), (-0.43, 0.46, 0.18, 0.14, 0.09, 0), (-0.26, 0.56, 0.21, 0.16, 0.11, 0), (-0.02, 0.54, 0.20, 0.15, 0.11, 0.004), (0.18, 0.44, 0.17, 0.12, 0.09, 0.010),
              (0.32, 0.30, 0.12, 0.09, 0.065, 0.016), (0.43, 0.17, 0.07, 0.055, 0.04, 0.018), (0.50, 0.07, 0.04, 0.035, 0.02, 0.018)],
    'courier': [(-0.50, 0.10, 0.05, 0.04, 0.02, 0), (-0.38, 0.16, 0.07, 0.055, 0.035, 0), (-0.15, 0.17, 0.07, 0.055, 0.035, 0), (0.10, 0.12, 0.058, 0.045, 0.03, 0.004), (0.30, 0.07, 0.04, 0.03, 0.02, 0.008), (0.44, 0.03, 0.022, 0.018, 0.01, 0.01), (0.50, 0.01, 0.008, 0.008, 0.004, 0.01)],
    'corvette': [(-0.50, 0.20, 0.09, 0.07, 0.04, 0), (-0.40, 0.30, 0.12, 0.09, 0.06, 0), (-0.15, 0.34, 0.14, 0.10, 0.07, 0), (0.10, 0.28, 0.12, 0.09, 0.06, 0.004), (0.30, 0.16, 0.08, 0.06, 0.04, 0.008), (0.44, 0.07, 0.045, 0.035, 0.02, 0.01), (0.50, 0.025, 0.02, 0.02, 0.01, 0.01)],
    'cargo': [(-0.50, 0.16, 0.08, 0.07, 0.04, 0), (-0.42, 0.22, 0.10, 0.09, 0.05, 0), (0.0, 0.20, 0.09, 0.08, 0.045, 0), (0.30, 0.16, 0.08, 0.07, 0.04, 0), (0.44, 0.12, 0.07, 0.06, 0.035, 0.004), (0.50, 0.05, 0.035, 0.03, 0.015, 0.004)],
    'tanker': [(-0.50, 0.14, 0.07, 0.06, 0.035, 0), (-0.40, 0.20, 0.09, 0.08, 0.05, 0), (0.10, 0.18, 0.08, 0.07, 0.045, 0), (0.35, 0.12, 0.07, 0.06, 0.035, 0), (0.50, 0.05, 0.03, 0.03, 0.015, 0)],
    'mining': [(-0.50, 0.26, 0.11, 0.09, 0.06, 0), (-0.38, 0.34, 0.14, 0.11, 0.08, 0), (-0.10, 0.32, 0.13, 0.10, 0.075, 0), (0.14, 0.26, 0.11, 0.09, 0.06, 0.004), (0.30, 0.18, 0.08, 0.07, 0.045, 0.008), (0.40, 0.10, 0.05, 0.045, 0.03, 0.01), (0.44, 0.06, 0.03, 0.03, 0.018, 0.01)],
    'reaver': [(-0.50, 0.16, 0.08, 0.07, 0.025, 0), (-0.40, 0.26, 0.11, 0.09, 0.04, 0), (-0.22, 0.30, 0.12, 0.09, 0.045, 0.004), (0.00, 0.25, 0.10, 0.08, 0.04, 0.006),
               (0.20, 0.17, 0.075, 0.06, 0.03, 0.010), (0.36, 0.10, 0.05, 0.04, 0.02, 0.012), (0.46, 0.05, 0.03, 0.025, 0.012, 0.012), (0.50, 0.012, 0.010, 0.010, 0.004, 0.012)],
}


def build(spec, mats):
    P = spec['params']; kind = P['kind']
    S = SC[kind]
    M = dict(zip(NAMES, PAL[kind])); slot = {n: i for i, n in enumerate(NAMES)}
    rng = random.Random(P.get('seed', 1))
    secs = SECS[kind]
    D = 0.005

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

    def env(z):
        for a, b in zip(secs, secs[1:]):
            if a[0] <= z <= b[0]:
                t = (z - a[0]) / (b[0] - a[0])
                return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, 6))
        return secs[0][1:6] if z < secs[0][0] else secs[-1][1:6]

    WINGS = []

    def wing(sx, root, tip, thick):
        WINGS.append((sx, root, tip, thick))
        """root=(x, zle, zte), tip=(x, y, zle, zte); kök kalınlığı thick, uç 0.3×; üst yüz hafif kambur"""
        bm = bmesh.new()
        def V(x, y, z): return bm.verts.new((sx * x, y, z))
        rt = [V(root[0], thick / 2, root[1]), V(root[0], thick / 2, root[2])]
        rb = [V(root[0], -thick / 2, root[1]), V(root[0], -thick / 2, root[2])]
        tt = [V(tip[0], tip[1] + thick * .15, tip[2]), V(tip[0], tip[1] + thick * .15, tip[3])]
        tb = [V(tip[0], tip[1] - thick * .15, tip[2]), V(tip[0], tip[1] - thick * .15, tip[3])]
        for f in [(rt[0], rt[1], tt[1], tt[0]), (rb[1], rb[0], tb[0], tb[1]), (rt[0], tt[0], tb[0], rb[0]), (rt[1], rb[1], tb[1], tt[1]), (rt[0], rb[0], rb[1], rt[1]), (tt[0], tt[1], tb[1], tb[0])]:
            bm.faces.new(f if sx > 0 else f[::-1])
        return bm

    def fin(pts_yz, x=0.0, th=0.016):
        bm = bmesh.new()
        a = [bm.verts.new((x - th / 2, y, z)) for y, z in pts_yz]; b = [bm.verts.new((x + th / 2, y, z)) for y, z in pts_yz]
        bm.faces.new(a[::-1]); bm.faces.new(b)
        for i in range(len(pts_yz)):
            j = (i + 1) % len(pts_yz); bm.faces.new([a[i], a[j], b[j], b[i]])
        return bm

    hull = obj('hull', loft_bm([s[:5] + (s[5],) for s in secs]), 'hull')
    parts = []; ENG = []; GUN = []
    # ---------------- kind'a özgü kütleler
    if kind == 'raider':
        for sx in (-1, 1):
            parts.append(obj('wing', wing(sx, (0.07, 0.16, -0.36), (0.47, -0.030, -0.22, -0.43), 0.060), 'hull'))
            parts.append(obj('cnrd', wing(sx, (0.06, 0.30, 0.19), (0.19, 0.004, 0.22, 0.17), 0.022), 'acc'))
            parts.append(obj('wtip', box_bm((sx * 0.455, -0.030, -0.33), (0.050, 0.020, 0.21)), 'acc2'))
            parts.append(obj('fin', fin([(0.07, -0.30), (0.07, -0.46), (0.20, -0.50), (0.22, -0.43)], x=sx * 0.115), 'hull'))
            ENG.append((sx * 0.105, -0.005))
            parts.append(obj('intk', tbox_bm((sx * 0.080, 0.000), 0.050, 0.040, 0.070, 0.050, 0.00, 0.18), 'dark'))
        for x, y in ENG:
            parts.append(obj('nac', cyl_bm((x, y, -0.50), (x, y, -0.22), 0.058, 0.052, 20), 'dark'))
            parts.append(obj('ring', cyl_bm((x, y, -0.495), (x, y, -0.515), 0.064, None, 20), 'acc2'))
        GUN = [(sx * 0.050, -0.020) for sx in (-1, 1)]
    elif kind == 'brute':
        def lofted(sc, dx, key, nm):
            bm_ = loft_bm(sc)
            for v in bm_.verts:
                v.co.x += dx
            return obj(nm, bm_, key)
        for sx in (-1, 1):
            parts.append(lofted([(-0.40, 0.10, 0.07, 0.06, 0.04, 0.0), (-0.22, 0.19, 0.11, 0.09, 0.07, -0.01), (0.04, 0.17, 0.10, 0.08, 0.065, -0.01), (0.26, 0.08, 0.05, 0.04, 0.03, 0.0)], sx * 0.31, 'hull', 'spon'))   # yuvarlak yan sponson (loft)
            parts.append(lofted([(-0.28, 0.08, 0.05, 0.012, 0.03, 0.17), (-0.04, 0.15, 0.065, 0.012, 0.045, 0.17), (0.14, 0.09, 0.04, 0.012, 0.025, 0.17)], sx * 0.20, 'acc2', 'shld'))     # omuz zırh kabarması
            parts.append(obj('gunb', cyl_bm((sx * 0.135, -0.025, 0.16), (sx * 0.135, -0.025, 0.34), 0.045, 0.040, 14), 'dark'))
            ENG.append((sx * 0.17, 0.0))
        ENG.append((0.0, 0.0))
        parts.append(lofted([(-0.30, 0.20, 0.05, 0.012, 0.03, 0.165), (-0.05, 0.27, 0.065, 0.012, 0.04, 0.165), (0.18, 0.22, 0.06, 0.012, 0.035, 0.165), (0.34, 0.10, 0.035, 0.012, 0.02, 0.165)], 0.0, 'hull', 'hump'))   # sırt kabarması
        for x, y in ENG:
            parts.append(obj('nac', cyl_bm((x, y, -0.505), (x, y, -0.34), 0.075, 0.070, 22), 'dark'))
            parts.append(obj('ring', cyl_bm((x, y, -0.50), (x, y, -0.52), 0.082, None, 22), 'acc'))
        for sx in (-1, 1):
            parts.append(obj('gun', cyl_bm((sx * 0.135, -0.025, 0.30), (sx * 0.135, -0.025, 0.50), 0.020, 0.017, 10), 'dark'))
        GUN = [(sx * 0.135, -0.025) for sx in (-1, 1)]
    elif kind in ('courier', 'corvette', 'cargo', 'tanker', 'mining'):
        def lofted(sc, dx, dy, key, nm):
            bm_ = loft_bm(sc)
            for v in bm_.verts:
                v.co.x += dx; v.co.y += dy
            return obj(nm, bm_, key)
        er = ENGR[kind]
        if kind == 'courier':
            for sx in (-1, 1):
                parts.append(obj('wing', wing(sx, (0.06, 0.10, -0.30), (0.40, -0.012, -0.05, -0.32), 0.045), 'hull'))
                parts.append(obj('wtip', box_bm((sx * 0.385, -0.012, -0.19), (0.040, 0.014, 0.28)), 'acc'))
            parts.append(obj('fin', fin([(0.06, -0.28), (0.06, -0.46), (0.22, -0.50), (0.20, -0.40)], x=0.0), 'hull'))
            ENG = [(0.0, 0.0)]
            GUN = []
        elif kind == 'corvette':
            for sx in (-1, 1):
                parts.append(lofted([(-0.35, 0.10, 0.06, 0.05, 0.035, 0), (-0.10, 0.17, 0.085, 0.06, 0.055, 0), (0.15, 0.13, 0.07, 0.05, 0.045, 0), (0.30, 0.05, 0.03, 0.025, 0.02, 0)], sx * 0.27, -0.01, 'acc2', 'pod'))
                parts.append(obj('wing', wing(sx, (0.15, 0.00, -0.30), (0.45, -0.012, -0.12, -0.34), 0.055), 'hull'))
                parts.append(obj('dome', cyl_bm((sx * 0.08, 0.145, -0.05), (sx * 0.08, 0.175, -0.05), 0.040, 0.030, 16), 'acc'))
                parts.append(obj('tur', cyl_bm((sx * 0.12, 0.14, 0.18), (sx * 0.12, 0.16, 0.18), 0.032, 0.026, 14), 'dark'))
                parts.append(obj('tg', cyl_bm((sx * 0.12, 0.16, 0.18), (sx * 0.12, 0.16, 0.34), 0.010, 0.008, 8), 'dark'))
                ENG.append((sx * 0.10, 0.0))
            GUN = [(sx * 0.12, 0.16) for sx in (-1, 1)]
        elif kind == 'cargo':
            for sx in (-1, 1):
                for j, dy in enumerate((-0.095, 0.095)):
                    for k_, (z0, z1) in enumerate(((-0.34, -0.06), (-0.02, 0.24))):
                        key = 'acc2' if (j + k_) % 2 == 0 else 'hull'
                        parts.append(lofted([(z0, 0.115, 0.055, 0.055, 0.022, 0), ((z0 + z1) / 2, 0.125, 0.060, 0.060, 0.026, 0), (z1, 0.115, 0.055, 0.055, 0.022, 0)], sx * 0.185, dy, key, 'cnt'))
                parts.append(obj('truss', box_bm((sx * 0.105, 0.0, -0.05), (0.014, 0.03, 0.62)), 'dark'))
                ENG.append((sx * 0.07, 0.0))
            GUN = []
        elif kind == 'tanker':
            for sx in (-1, 1):
                for dy in (0.075, -0.075):
                    parts.append(lofted([(-0.34, 0.14, 0.07, 0.07, 0.06, 0), (-0.28, 0.20, 0.10, 0.10, 0.09, 0), (0.20, 0.20, 0.10, 0.10, 0.09, 0), (0.34, 0.14, 0.07, 0.07, 0.06, 0)], sx * 0.11, dy, 'hull', 'tank'))
                    for zb in (-0.15, 0.04, 0.2):
                        parts.append(lofted([(zb - 0.012, 0.214, 0.108, 0.108, 0.094, 0), (zb + 0.012, 0.214, 0.108, 0.108, 0.094, 0)], sx * 0.11, dy, 'acc2', 'band'))
                ENG.append((sx * 0.07, 0.0))
            GUN = []
        else:   # mining
            for sx in (-1, 1):
                parts.append(obj('arm', cyl_bm((sx * 0.12, -0.03, 0.12), (sx * 0.12, -0.03, 0.48), 0.050, 0.014, 16), 'acc'))
                parts.append(obj('arm2', cyl_bm((sx * 0.12, -0.03, 0.12), (sx * 0.12, -0.03, 0.24), 0.066, 0.058, 16), 'dark'))
                parts.append(obj('strut', tbox_bm((sx * 0.20, 0.0), 0.05, 0.05, 0.05, 0.03, -0.20, 0.14), 'acc2'))
                ENG.append((sx * 0.12, 0.0))
            bm_h = loft_bm([(-0.40, 0.24, 0.05, 0.01, 0.03, 0.13), (-0.10, 0.30, 0.07, 0.01, 0.045, 0.13), (0.10, 0.22, 0.055, 0.01, 0.035, 0.13)])
            parts.append(obj('hopper', bm_h, 'hull'))
            GUN = []
        if kind != 'courier':
            for x, y in ENG:
                pass
        for x, y in ENG:
            parts.append(obj('nac', cyl_bm((x, y, -0.505), (x, y, -0.30), er, er * 0.92, 20), 'dark'))
            parts.append(obj('ring', cyl_bm((x, y, -0.50), (x, y, -0.52), er + 0.007, None, 20), 'acc'))
    else:   # reaver: asimetrik hurda yağmacı
        parts.append(obj('wingL', wing(-1, (0.09, 0.14, -0.38), (0.50, -0.020, -0.12, -0.44), 0.070), 'hull'))
        parts.append(obj('wingR', wing(1, (0.09, 0.10, -0.34), (0.30, -0.010, -0.06, -0.30), 0.070), 'hull'))
        parts.append(obj('ram', fin([(-0.020, 0.14), (-0.11, 0.40), (-0.12, 0.50), (-0.02, 0.50), (0.02, 0.30)], x=0.0, th=0.030), 'acc'))      # alt pruva kıçı/ram bıçağı
        parts.append(obj('plateA', tbox_bm((-0.06, 0.115), 0.20, 0.14, 0.030, 0.026, -0.30, -0.02), 'acc2'))
        parts.append(obj('plateB', tbox_bm((0.08, 0.098), 0.14, 0.10, 0.026, 0.022, 0.00, 0.20), 'acc'))
        parts.append(obj('plateC', tbox_bm((-0.15, 0.040), 0.040, 0.040, 0.10, 0.08, -0.10, 0.10), 'acc'))
        parts.append(obj('plateD', tbox_bm((0.16, 0.030), 0.040, 0.040, 0.09, 0.07, -0.20, -0.04), 'acc2'))
        parts.append(obj('mast', cyl_bm((0.05, 0.10, -0.15), (0.055, 0.20, -0.17), 0.006, 0.004, 8), 'dark'))
        ENG = [(-0.12, -0.005), (0.10, -0.010), (0.0, 0.03)]
        for i, (x, y) in enumerate(ENG):
            r = 0.060 if i < 2 else 0.045
            parts.append(obj('nac', cyl_bm((x, y, -0.505), (x, y, -0.28 if i < 2 else -0.34), r, r * 0.9, 20), 'dark'))
            parts.append(obj('ring', cyl_bm((x, y, -0.500), (x, y, -0.520), r + 0.007, None, 20), 'acc2'))
        GUN = [(0.075, -0.040)]
        parts.append(obj('gunb', box_bm((0.075, -0.040, 0.30), (0.05, 0.05, 0.14)), 'dark'))
        parts.append(obj('gun', cyl_bm((0.075, -0.040, 0.36), (0.075, -0.040, 0.50), 0.016, 0.013, 8), 'dark'))
    # kanopi: gövde hattıyla sürekli, alçak; altında gövde renginde kasa
    zc0, zc1 = {'raider': (0.02, 0.26), 'brute': (0.12, 0.34), 'reaver': (-0.02, 0.22), 'courier': (0.0, 0.22), 'corvette': (0.18, 0.38), 'cargo': (0.34, 0.46), 'tanker': (0.30, 0.44), 'mining': (0.18, 0.34)}[kind]
    wc, hc = env((zc0 + zc1) / 2)[0], env((zc0 + zc1) / 2)[1]
    hh = {'raider': 0.026, 'brute': 0.030, 'reaver': 0.030, 'courier': 0.022, 'corvette': 0.030, 'cargo': 0.030, 'tanker': 0.028, 'mining': 0.030}[kind]
    ww = {'raider': 0.075, 'brute': 0.15, 'reaver': 0.11, 'courier': 0.07, 'corvette': 0.12, 'cargo': 0.09, 'tanker': 0.08, 'mining': 0.12}[kind]
    zm = (zc0 + zc1) / 2
    _e = env(zm); yc = _e[4] + _e[1] - hh * 0.5
    if kind == 'brute':
        yc = 0.205; ww = 0.17
    parts.append(obj('cframe', loft_bm([(zc0 - 0.02, ww * 0.55, hh * 0.5, 0.004, hh * 0.3, yc - 0.004), (zm - 0.04, ww * 1.15, hh * 0.9, 0.004, hh * 0.5, yc - 0.004), (zm + 0.04, ww * 1.10, hh * 0.9, 0.004, hh * 0.5, yc - 0.004), (zc1 + 0.02, ww * 0.55, hh * 0.5, 0.004, hh * 0.3, yc - 0.004)]), 'acc'))
    parts.append(obj('glass', loft_bm([(zc0, ww * 0.48, hh * 0.55, 0.004, hh * 0.3, yc), (zm - 0.04, ww * 1.0, hh, 0.004, hh * 0.55, yc), (zm + 0.04, ww * 0.95, hh * 0.95, 0.004, hh * 0.55, yc), (zc1, ww * 0.48, hh * 0.55, 0.004, hh * 0.3, yc)]), 'glass'))
    union_all(hull, parts)
    core = hull
    diff_all(core, [obj('noz', cyl_bm((x, y, -0.56), (x, y, -0.455), ENGR[kind] * 0.68, ENGR[kind] * 0.62, 20), 'dark') for x, y in ENG])
    # ---------------- hi-poly oluk + kabartma
    hi_core = core.copy(); hi_core.data = core.data.copy(); geo.collection('Asset').objects.link(hi_core); hi_core.name = 'hi_core'; hi_core['sd_role'] = 'hi'
    grv = []
    for z in [-0.46 + 0.04 * i for i in range(24)]:
        w, hu, hd, ch, y0 = env(z)
        if w > 0.05:
            grv.append(obj('ring', ring_bm(z, 0.0045, w, hu, hd, ch, D), 'dark'))
    wmax = max(s[1] for s in secs)
    for x in (-0.4, -0.2, 0.2, 0.4):
        grv.append(obj('lg', box_bm((x * wmax, env(-0.05)[1] - D + 0.02, -0.05), (0.0045, 0.04, 0.60)), 'dark'))
    for sx, root, tip, thick in WINGS:                       # kanat panel/nervür olukları (kökten uca)
        n = 9
        for q in range(1, n):
            t = q / n
            x = root[0] + (tip[0] - root[0]) * t
            zle = root[1] + (tip[2] - root[1]) * t; zte = root[2] + (tip[3] - root[2]) * t
            y = tip[1] * t
            grv.append(obj('wg', box_bm((sx * x, y, (zle + zte) / 2), (0.0045, 0.16, abs(zle - zte) * 0.80)), 'dark'))
        for u in (0.25, 0.5, 0.75):                          # enine dikişler
            x = (root[0] + tip[0]) / 2; hw = (tip[0] - root[0]) / 2 * 0.9
            zz = 0.5 * ((root[1] + tip[2]) / 2 * (1 - u) * 2 + (root[2] + tip[3]) / 2 * u * 2) / 1.0
            grv.append(obj('wc', box_bm((sx * x, tip[1] / 2, zz), (hw * 2 * 0.8, 0.16, 0.0045)), 'dark'))
    diff_all(hi_core, grv)
    # ---------------- ızgara bölme + renk bölgeleri
    bm = bmesh.new(); bm.from_mesh(core.data)
    cl = P.get('split_len', 0.06)
    for _ in range(2):
        groups = {}
        for e in bm.edges:
            Lg = (e.verts[0].co - e.verts[1].co).length / S
            c = int(Lg / cl)
            if c >= 1 and any(f.calc_area() / (S * S) > (cl * 0.6) ** 2 for f in e.link_faces):
                groups.setdefault(min(c, 8), []).append(e)
        for c, es in groups.items():
            es = [e for e in es if e.is_valid]
            if es:
                bmesh.ops.subdivide_edges(bm, edges=es, cuts=c, use_grid_fill=True)
    sl = lambda n: slot[n]
    for f in bm.faces:
        cb = f.calc_center_median()
        gx, up, gz = cb.x / S, cb.z / S, -cb.y / S      # x yanal, up yukarı, gz boy (oyun uzayı)
        if f.material_index != slot['hull']:
            continue
        w, hu, hd, ch, y0 = env(gz)
        if up < y0 - hd * 0.45:                          # karın: koyu
            f.material_index = sl('dark'); continue
        h = (int((gx + 1) / 0.07) * 73856093 ^ int((up + 1) / 0.04) * 19349663 ^ int((gz + 1) / 0.07) * 83492791) % 17
        if kind == 'raider':
            if gz > 0.30:
                f.material_index = sl('acc2')                # burun: turuncu
            elif abs(gx) < 0.025 and gz > 0.0:
                f.material_index = sl('acc')                 # sırt çelik şerit
            elif h in (0, 1, 2):
                f.material_index = sl('acc')
            elif h in (3, 4):
                f.material_index = sl('acc2')
            elif h == 5:
                f.material_index = sl('dark')
        elif kind == 'brute':
            if int((gz + 0.6) / 0.22) % 3 == 1 and abs(gx) > 0.05:
                f.material_index = sl('dark')                # koyu zırh kuşağı
            elif h in (0, 1, 2, 3):
                f.material_index = sl('acc2')                # paslı yama plakalar
            elif h == 4:
                f.material_index = sl('acc')                 # sarı uyarı yamaları (az)
            elif h in (5, 6):
                f.material_index = sl('dark')
        else:
            if h in ((0, 1) if kind in ('cargo', 'tanker', 'mining') else (0, 1, 2, 3)):
                f.material_index = sl('acc')
            elif h in (4, 5, 6):
                f.material_index = sl('acc2')
            elif h in (7, 8):
                f.material_index = sl('dark')
    bm.to_mesh(core.data); bm.free()
    if P.get('bevel_m', 0) > 0:
        mb = core.modifiers.new('bev', 'BEVEL'); mb.width = P['bevel_m']; mb.segments = 2; mb.limit_method = 'ANGLE'; mb.angle_limit = math.radians(25)
        with bpy.context.temp_override(object=core, active_object=core, selected_objects=[core], selected_editable_objects=[core]):
            bpy.ops.object.modifier_apply(modifier=mb.name)
    geo.set_smooth_by_angle(core, 40); geo.set_smooth_by_angle(hi_core, 40)
    core.name = 'core'; core['sd_role'] = 'body'
    out_body, out_hi = [core], [hi_core]

    def small(name, bm_, key):
        o = obj(name, bm_, key)
        geo.set_smooth_by_angle(o, 35)
        out_body.append(o)
        h = o.copy(); h.data = o.data.copy(); geo.collection('Asset').objects.link(h); h['sd_role'] = 'hi'; out_hi.append(h)
        return o
    # kanopi kemerleri + motor çekirdeği + detay donanımı
    small('arch', box_bm((0.0, yc + hh * 0.98, zm), (0.006, 0.005, zc1 - zc0 - 0.02)), 'dark')
    for x, y in ENG:
        r = ENGR[kind] * 0.55
        small('core', cyl_bm((x, y, -0.462), (x, y, -0.470), r, None, 16), 'glow')
        for q in range(8):
            a = q * math.pi / 4; rr = ENGR[kind] * 0.84
            small('bolt', box_bm((x + rr * math.cos(a), y + rr * math.sin(a), -0.452), (0.008, 0.008, 0.012)), 'dark')
        for z_ in (-0.40, -0.35):
            small('fin', cyl_bm((x, y, z_), (x, y, z_ + 0.008), ENGR[kind] * 0.96, None, 20), 'dark')
    navs = []
    wtop = max(env(-0.2)[0], 0.1) / 2
    if kind == 'raider':
        navs = [(0.47, -0.030, -0.33), (-0.47, -0.030, -0.33), (0.0, 0.10, -0.48)]
    elif kind == 'brute':
        navs = [(0.38, -0.01, 0.10), (-0.38, -0.01, 0.10), (0.0, 0.23, -0.40)]
    elif kind == 'reaver':
        navs = [(0.50, -0.02, -0.30), (-0.30, -0.02, -0.18), (0.0, 0.15, -0.40)]
    else:
        e_ = env(-0.35); navs = [(e_[0] / 2 + 0.01, e_[4], -0.35), (-e_[0] / 2 - 0.01, e_[4], -0.35), (0.0, e_[4] + e_[1], -0.40)]
    for p in navs:
        small('nav', box_bm(p, (0.022, 0.022, 0.022)), 'glow')
    for sx in (-1, 1):                                   # gövde yanı emissive ışık şeridi
        z_ = 0.0
        w_, hu_, hd_, _, y0_ = env(z_)
        small('strip', box_bm((sx * w_ / 2, y0_ + 0.01, z_ - 0.05), (0.008, 0.014, 0.24)), 'glow')
    # panel nervürleri / antenler
    small('ant1', cyl_bm((0.0, env(-0.2)[1] + 0.01, -0.24), (0.0, env(-0.2)[1] + 0.09, -0.26), 0.003, 0.0015, 6), 'dark')
    small('ant2', cyl_bm((0.04, env(-0.1)[1], -0.12), (0.055, env(-0.1)[1] + 0.06, -0.135), 0.002, 0.001, 6), 'dark')
    for q in range(5):
        zq = -0.34 + q * 0.12
        w_, hu_, hd_, _, y0_ = env(zq)
        small('hatch', box_bm((((q % 2) * 2 - 1) * w_ * 0.22, y0_ + hu_ + 0.001, zq), (w_ * 0.18, 0.004, 0.05)), 'dark')
    socks = []
    for i, (x, y) in enumerate(ENG, 1):
        socks.append({'name': 'ANCH_ENG_%d' % i, 'loc': tuple(geo.g2b(Vector((x, y, -0.466)) * S)), 'dir': (0.0, 1.0, 0.0), 'extras': {'kind': 'engine'}})
    for i, p in enumerate(navs, 1):
        socks.append({'name': 'ANCH_NAV_%d' % i, 'loc': tuple(geo.g2b(Vector(p) * S)), 'dir': (0.0, 0.0, 1.0), 'extras': {'kind': 'nav'}})
    for i, (x, y) in enumerate(GUN, 1):
        socks.append({'name': 'ANCH_MUZ_%d' % i, 'loc': tuple(geo.g2b(Vector((x, y, 0.50)) * S)), 'dir': (0.0, -1.0, 0.0), 'extras': {'kind': 'muzzle'}})
    return {'objects': out_body + out_hi, 'sockets': socks}
