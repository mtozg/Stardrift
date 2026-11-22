"""Küçük nesneler ve çevre (Parti 1): roket, kaçak yük konteyneri, kayıp sonda, buz devi, kristal monolit, patron ini, uydu, lav kayası, enkaz. spec.params.layout → fonksiyon.
Kurulum uzayı: oyun (x yanal, y yukarı, z burun/uzun eksen +); ×S metre; Blender g2b. Tek gövde objesi + malzeme bölgeleri (prepare tek atlasa pişirir)."""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix, noise
from core import geo
from families.ship.yuk_ext import orient_outward


class Bld:
    def __init__(self, mats, names):
        self.mats = mats
        self.names = names
        self.bm = {n: bmesh.new() for n in names}

    def box(self, c, s, m, rot=(0, 0, 0)):
        bm = self.bm[m]
        r = bmesh.ops.create_cube(bm, size=1.0)
        M = Matrix.Translation(Vector(c)) @ Matrix.Rotation(rot[2], 4, 'Z') @ Matrix.Rotation(rot[1], 4, 'Y') @ Matrix.Rotation(rot[0], 4, 'X') @ Matrix.Diagonal((*s, 1.0))
        bmesh.ops.transform(bm, matrix=M, verts=r['verts'])

    def cyl(self, p0, p1, r0, m, r1=None, seg=16, cap=True):
        bm = self.bm[m]
        d = Vector(p1) - Vector(p0)
        M = Matrix.Translation((Vector(p0) + Vector(p1)) / 2) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=seg, radius1=r0, radius2=r0 if r1 is None else r1, depth=d.length, matrix=M)

    def cone(self, p0, p1, r, m, seg=16):
        self.cyl(p0, p1, r, m, 0.0001, seg, True)

    def blob(self, c, r, m, subdiv=3, disp=0.3, seed=1, squash=(1, 1, 1), scale_noise=1.5, flat=False):
        bm = self.bm[m]
        res = bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
        for v in res['verts']:
            n = Vector(v.co).normalized()
            k = 1.0 + disp * noise.fractal(Vector((n.x * scale_noise + seed * 7.3, n.y * scale_noise + seed * 3.1, n.z * scale_noise + seed * 1.7)), 1.0, 2.0, 4)
            v.co = Vector((c[0] + n.x * r * k * squash[0], c[1] + n.y * r * k * squash[1], c[2] + n.z * r * k * squash[2]))

    def spire(self, base, h, r, m, seg=6, seed=1, lean=(0, 0), tip=0.05):
        rng = random.Random(seed)
        bm = self.bm[m]
        rings = []
        for k, (t, rr) in enumerate(((0.0, 1.0), (0.55, 0.85), (0.9, 0.35), (1.0, tip))):
            ring = []
            for i in range(seg):
                a = 2 * math.pi * i / seg + 0.3 * t
                j = 1.0 + 0.18 * (rng.random() - 0.5)
                ring.append(bm.verts.new((base[0] + lean[0] * t * h + math.cos(a) * r * rr * j, base[1] + lean[1] * t * h + math.sin(a) * r * rr * j, base[2] + h * t)))
            rings.append(ring)
        def mean(rg):
            return sum((v.co for v in rg), Vector()) / len(rg)
        for r0, r1 in zip(rings, rings[1:]):
            ax = (mean(r0) + mean(r1)) / 2
            for i in range(seg):
                j = (i + 1) % seg
                f = bm.faces.new([r0[i], r0[j], r1[j], r1[i]])
                f.normal_update()
                if f.normal.dot(f.calc_center_median() - ax) < 0:
                    f.normal_flip()
        fb = bm.faces.new(rings[0][::-1]); ft = bm.faces.new(rings[-1])
        for f_, sgn in ((fb, -1), (ft, 1)):
            f_.normal_update()
            if f_.normal.z * sgn < 0:
                f_.normal_flip()
        self.keep_normals = True

    def finish(self, S, role='body', up_z=False):
        objs = []
        for n, bm in self.bm.items():
            if not bm.verts:
                continue
            for v in bm.verts:
                c = Vector(v.co)
                if up_z:
                    c = Vector((c.x, c.z, -c.y))      # z-yukarı kurulum → oyun yukarısı +Y
                v.co = geo.g2b(c * S)
            if not getattr(self, 'keep_normals', False):
                bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bmesh.ops.triangulate(bm, faces=bm.faces)      # bükülü dörtgenler (kule sarmalı) kendine ışın çarpıp cull'da silinirdi
            objs.append(geo.mesh_object('P_' + n, bm, self.mats[n], role=role, smooth_angle=35))
        return objs


def L_rocket(spec, mats, guided):
    P = ['white', 'red', 'steel', 'dark', 'hazard', 'emit']
    M = {'white': 'white_paint', 'red': 'red_paint', 'steel': 'steel_dark', 'dark': 'yuk_dark', 'hazard': 'yuk_hazard', 'emit': 'emit_amber'}
    b = Bld({k: mats[v] for k, v in M.items()}, P)
    body = 'white' if guided else 'steel'
    b.cyl((0, 0, -0.30), (0, 0, 0.30), 0.075, body, 0.075, 20)
    b.cyl((0, 0, 0.30), (0, 0, 0.50), 0.075, 'red', 0.032, 20)                 # ogive baş (kademeli)
    b.cone((0, 0, 0.50), (0, 0, 0.56), 0.032, 'dark', 16)
    b.cyl((0, 0, -0.30), (0, 0, -0.38), 0.062, 'dark', 0.085, 20, False)       # motor kovanı
    b.cyl((0, 0, -0.37), (0, 0, -0.372), 0.052, 'emit', None, 16)
    for z in (-0.18, 0.05, 0.22):
        b.cyl((0, 0, z), (0, 0, z + 0.025), 0.0775, 'hazard' if z == 0.05 else 'steel', None, 20, False)
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        b.box((math.cos(a) * 0.12, math.sin(a) * 0.12, -0.27), (0.07 if i % 2 == 0 else 0.07, 0.012, 0.15), body, (0, 0, a))
        if guided:
            b.box((math.cos(a) * 0.10, math.sin(a) * 0.10, 0.27), (0.04, 0.008, 0.07), 'steel', (0, 0, a))
    for k in range(6):
        a = k * math.pi / 3
        b.box((math.cos(a) * 0.078, math.sin(a) * 0.078, 0.12), (0.012, 0.012, 0.06), 'dark')
    return b


def L_cache(spec, mats):
    P = ['paint', 'steel', 'hazard', 'dark', 'rubber', 'lamp']
    M = {'paint': 'yuk_cont_rust', 'steel': 'steel_dark', 'hazard': 'yuk_hazard', 'dark': 'yuk_dark', 'rubber': 'yuk_rubber', 'lamp': 'emit_amber'}
    b = Bld({k: mats[v] for k, v in M.items()}, P)
    b.box((0, 0, 0), (0.80, 0.80, 0.60), 'paint')
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.box((sx * 0.40, sy * 0.40, 0), (0.06, 0.06, 0.62), 'steel')      # köşe direkleri
            for sz in (-1, 1):
                b.box((sx * 0.40, sy * 0.40, sz * 0.30), (0.08, 0.08, 0.04), 'dark')
    for i in range(7):
        b.box((-0.30 + i * 0.10, 0.402, 0), (0.025, 0.012, 0.60), 'dark')        # oluklu yan yüz
        b.box((-0.30 + i * 0.10, -0.402, 0), (0.025, 0.012, 0.60), 'dark')
    b.box((0, 0, 0.305), (0.80, 0.80, 0.02), 'steel')
    b.box((0, 0.403, 0.0), (0.30, 0.012, 0.10), 'hazard')
    b.box((0.0, 0.41, 0.05), (0.08, 0.012, 0.05), 'dark')
    b.cyl((0.34, 0.0, 0.31), (0.34, 0.0, 0.36), 0.03, 'lamp', None, 10)
    b.box((0, -0.404, -0.10), (0.5, 0.01, 0.08), 'rubber')
    return b


def L_probe(spec, mats):
    P = ['body', 'steel', 'dark', 'panel', 'lamp', 'gold']
    M = {'body': 'white_paint', 'steel': 'steel_dark', 'dark': 'yuk_dark', 'panel': 'hay_dark', 'lamp': 'emit_red', 'gold': 'yuk_hazard'}
    b = Bld({k: mats[v] for k, v in M.items()}, P)
    b.blob((0, 0, 0), 0.22, 'body', 3, 0.04, 1)
    b.cyl((0, 0, 0.05), (0, 0, 0.30), 0.02, 'steel', 0.012, 10)
    b.cyl((0, 0.0, 0.30), (0, 0.0, 0.36), 0.14, 'steel', 0.01, 20)                 # çanak anten
    b.cyl((-0.24, 0, 0), (-0.55, 0, 0), 0.012, 'steel', None, 8)
    b.box((-0.75, 0, 0.0), (0.40, 0.02, 0.26), 'panel', (0, 0.15, 0))               # güneş paneli (eğik)
    b.cyl((0.24, 0, 0), (0.46, 0, 0), 0.012, 'steel', None, 8)
    b.box((0.58, 0.05, 0.1), (0.20, 0.02, 0.12), 'panel', (0.5, 0, 0.7))             # kırık panel
    b.cyl((0, -0.20, -0.05), (0, -0.30, -0.05), 0.06, 'dark', 0.08, 12)             # iticiler
    for a in range(3):
        t = a * 2 * math.pi / 3
        b.cyl((math.cos(t) * 0.12, math.sin(t) * 0.12, -0.22), (math.cos(t) * 0.15, math.sin(t) * 0.15, -0.30), 0.025, 'dark', 0.04, 8)
    b.cyl((0.18, 0.12, 0.10), (0.20, 0.14, 0.13), 0.02, 'lamp', None, 8)
    b.box((0, 0.22, 0.0), (0.18, 0.04, 0.10), 'gold')
    return b


def L_ice(spec, mats):
    P = ['ice', 'white', 'rock', 'glow']
    M = {'ice': 'ice_blue', 'white': 'ice_white', 'rock': 'rock_dark', 'glow': 'emit_cyan'}
    b = Bld({k: mats[v] for k, v in M.items()}, P)
    rng = random.Random(spec['params'].get('seed', 5))
    b.blob((0, 0, -0.10), 0.55, 'rock', 3, 0.35, 2, (1.2, 1.2, 0.55))
    for i in range(9):
        a = i * 2 * math.pi / 9 + rng.random() * 0.4
        r0 = 0.0 if i == 0 else 0.20 + rng.random() * 0.24
        h = 0.55 + rng.random() * 0.6 if i else 1.25
        rr = 0.26 + rng.random() * 0.12
        b.spire((math.cos(a) * r0, math.sin(a) * r0, -0.05), h, rr, 'ice' if i % 2 == 0 else 'white', 5 + i % 3, i + 1, lean=(math.cos(a) * 0.25, math.sin(a) * 0.25), tip=0.12)
    b.blob((0, 0, 0.35), 0.16, 'glow', 2, 0.1, 3)
    for i in range(9):                                                   # her kristalin tabanında parlayan halka + yüzeyde ince emissive damar (içten ışıma dışarıdan okunur)
        a = i * 2 * math.pi / 9
        r0 = 0.0 if i == 0 else 0.30
        bx, by = math.cos(a) * r0, math.sin(a) * r0
        b.box((bx * 0.8, by * 0.8, 0.08), (0.20, 0.035, 0.035), 'glow', (0, 0, a))
        b.box((bx * 0.9 + 0.02, by * 0.9, 0.32 + 0.04 * (i % 3)), (0.03, 0.03, 0.34), 'glow', (0.0, 0.1, a))
    for i in range(4):
        a = i * 1.7 + 0.4
        b.blob((math.cos(a) * 0.62, math.sin(a) * 0.62, 0.0), 0.14, 'white', 2, 0.3, 10 + i)
    return b


def L_monolith(spec, mats):
    P = ['crystal', 'core', 'rock', 'steel']
    col = spec['params'].get('crystal', 'crystal_violet')
    M = {'crystal': col, 'core': 'emit_violet' if col == 'crystal_violet' else 'emit_green', 'rock': 'rock_dark', 'steel': 'steel_dark'}
    b = Bld({k: mats[v] for k, v in M.items()}, P)
    b.blob((0, 0, -0.06), 0.42, 'rock', 3, 0.3, 4, (1.3, 1.3, 0.4))
    b.spire((0, 0, -0.02), 2.3, 0.26, 'crystal', 6, 3, tip=0.40)
    for k in range(6):                                                         # iç ışıldayan damarlar (kenar boyunca)
        a = k * math.pi / 3 + 0.0
        b.box((math.cos(a) * 0.235, math.sin(a) * 0.235, 1.0), (0.026, 0.026, 1.9), 'core', (0, 0, a))
    for i in range(6):
        a = i * 2 * math.pi / 6 + 0.3
        b.spire((math.cos(a) * 0.36, math.sin(a) * 0.36, -0.03), 0.55 + 0.25 * (i % 3), 0.11, 'crystal', 5, 10 + i, lean=(math.cos(a) * 0.45, math.sin(a) * 0.45), tip=0.15)
    for z in (0.3, 0.9, 1.5, 2.05):
        b.cyl((0, 0, z), (0, 0, z + 0.035), 0.268 - z * 0.05, 'steel', None, 6, False)
    return b


def L_lair(spec, mats):
    P = ['rock', 'metal', 'hazard', 'dark', 'lamp', 'paint']
    acc = spec['params'].get('accent', 'yuk_cont_rust')
    M = {'rock': 'rock_dark', 'metal': 'steel_dark', 'hazard': 'yuk_hazard', 'dark': 'yuk_dark', 'lamp': 'emit_amber', 'paint': acc}
    b = Bld({k: mats[v] for k, v in M.items()}, P)
    sd = spec['params'].get('seed', 3)
    b.blob((0, 0, 0), 0.5, 'rock', 4, 0.32, sd, (1.5, 1.2, 0.8), 1.4)
    b.box((0.0, 0.0, 0.42), (0.7, 0.5, 0.06), 'metal')                                       # iniş platformu
    for i in range(6):
        b.box((-0.30 + i * 0.12, 0.26, 0.42), (0.04, 0.02, 0.07), 'hazard')
    vr = spec['params'].get('seed', 3) % 4
    if vr == 1:
        b.box((0.0, 0.0, 0.62), (0.30, 0.30, 0.34), 'paint'); b.cyl((0.0, 0.0, 0.79), (0.0, 0.0, 1.10), 0.02, 'metal', 0.01, 8)
    elif vr == 2:
        for sx in (-1, 1):
            b.cyl((sx * 0.3, 0.0, 0.45), (sx * 0.3, 0.0, 0.85), 0.05, 'metal', 0.035, 10); b.box((sx * 0.3, 0.0, 0.88), (0.16, 0.12, 0.07), 'paint')
    elif vr == 3:
        for k in range(3):
            b.box((-0.25 + k * 0.25, 0.12, 0.55 + 0.08 * k), (0.18, 0.14, 0.14), 'paint'); b.cyl((-0.25 + k * 0.25, 0.12, 0.62 + 0.08 * k), (-0.25 + k * 0.25, 0.12, 0.9 + 0.08 * k), 0.015, 'metal', None, 6)
    b.cyl((-0.36, -0.1, 0.45), (-0.36, -0.1, 0.95), 0.045, 'metal', 0.03, 10)               # kule
    b.box((-0.36, -0.1, 0.97), (0.20, 0.14, 0.08), 'paint')
    b.cyl((0.30, 0.05, 0.45), (0.30, 0.05, 0.75), 0.035, 'dark', 0.05, 10)
    b.cyl((0.30, 0.05, 0.75), (0.45, 0.05, 0.85), 0.012, 'metal', None, 8)
    b.box((0.0, -0.34, 0.30), (0.34, 0.12, 0.24), 'paint')                                  # hangar kapısı bloğu
    b.box((0.0, -0.405, 0.30), (0.22, 0.012, 0.16), 'dark')
    for sx in (-1, 1):
        b.cyl((sx * 0.5, 0.1, 0.1), (sx * 0.62, 0.1, 0.38), 0.03, 'metal', 0.02, 8)         # destek payandaları
        b.box((sx * 0.60, 0.1, 0.40), (0.05, 0.05, 0.05), 'lamp')
    for i in range(5):
        a = i * 2 * math.pi / 5 + 0.5
        b.cone((math.cos(a) * 0.42, math.sin(a) * 0.30, -0.05), (math.cos(a) * 0.46, math.sin(a) * 0.33, 0.28), 0.06, 'rock', 6)
    return b


def L_sat(spec, mats):
    P = ['body', 'steel', 'panel', 'dark', 'gold', 'lamp']
    M = {'body': 'white_paint', 'steel': 'gunmetal', 'panel': 'ice_blue', 'dark': 'yuk_dark', 'gold': 'yuk_hazard', 'lamp': 'emit_red'}
    b = Bld({k: mats[v] for k, v in M.items()}, P)
    v = spec['params'].get('variant', 0)
    b.box((0, 0, 0), (0.42, 0.42, 0.56), 'body')
    b.box((0, 0, 0.31), (0.47, 0.47, 0.06), 'gold')
    b.box((0, 0, -0.31), (0.47, 0.47, 0.06), 'steel')
    for sx in (-1, 1):
        for z in (-0.15, 0.0, 0.15):
            b.box((sx * 0.215, 0.0, z), (0.02, 0.30, 0.07), 'dark')            # gövde panel kapakları
        b.box((sx * 0.215, 0.0, 0.22), (0.02, 0.30, 0.02), 'gold')
    b.cyl((0.18, 0, 0), (0.45, 0, 0), 0.012, 'steel', None, 8)
    b.cyl((-0.18, 0, 0), (-0.45, 0, 0), 0.012, 'steel', None, 8)
    b.box((0.95, 0, 0), (0.95, 0.04, 0.50), 'panel')
    b.box((-0.95, 0.0, 0.0), (0.95, 0.04, 0.50) if v != 1 else (0.6, 0.04, 0.50), 'panel', (0, 0.0, 0.0) if v != 2 else (0.4, 0, 0))
    for sx in (-1, 1):
        for q in range(1, 4):
            b.box((sx * (0.55 + q * 0.22), 0.0, 0.0), (0.02, 0.046, 0.52), 'dark')   # panel ızgara çizgileri
        b.box((sx * 0.95, 0.0, 0.0), (0.95, 0.046, 0.02), 'dark')
    for i in range(1, 4):
        b.box((0.85, 0.012, 0.0), (0.012, 0.004, 0.30), 'dark') if False else None
    b.cyl((0, 0.15, 0.2), (0, 0.4, 0.25), 0.02, 'steel', None, 8)
    b.cyl((0, 0.4, 0.25), (0, 0.55, 0.30), 0.26, 'body', 0.03, 24)                          # çanak (büyük)
    b.cyl((0, 0.55, 0.30), (0, 0.62, 0.32), 0.02, 'steel', None, 8)
    b.cyl((0, 0.15, 0.2), (0, 0.4, 0.25), 0.02, 'gold', None, 8)
    b.box((0.10, -0.16, 0.1), (0.05, 0.02, 0.05), 'lamp')
    return b


def L_lava(spec, mats):
    P = ['rock', 'lava']
    M = {'rock': 'lava_rock', 'lava': 'emit_lava'}
    b = Bld({k: mats[v] for k, v in M.items()}, P)
    sd = spec['params'].get('seed', 1)
    b.blob((0, 0, 0), 0.5, 'rock', 4, 0.45, sd, (1.0, 0.85, 0.8), 1.8)
    rng = random.Random(sd)
    b.blob((0, 0, 0), 0.40, 'lava', 3, 0.30, sd + 9, (1.0, 0.85, 0.8), 1.8)                  # içten ısı: kayanın içinde parlayan çekirdek (çatlaklardan görünür)
    for i in range(10):                                                                     # parlayan çatlaklar (daha büyük, kabuğun içine gömülü yarıklar)
        a = rng.random() * 6.28; e = rng.random() * 1.6 - 0.8
        d = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
        p0 = d * 0.40; p1 = d * 0.58
        b.box(tuple((p0 + p1) / 2), (0.14, 0.030, 0.34), 'lava', (rng.random() * 2, rng.random() * 2, a))
    return b


def L_debris(spec, mats):
    P = ['plate', 'steel', 'dark', 'hazard']
    M = {'plate': 'white_paint', 'steel': 'steel_dark', 'dark': 'yuk_dark', 'hazard': 'yuk_hazard'}
    b = Bld({k: mats[v] for k, v in M.items()}, P)
    v = spec['params'].get('variant', 0)
    for q in range(5):
        b.box((0.1 * q - 0.2, 0.05 * q, 0.1 - 0.05 * q), (0.05, 0.12, 0.03), 'dark', (q, 0.3 * q, 0.2))        # kırık kaburgalar/kablo kütükleri
    b.cyl((-0.3, 0.1, -0.1), (0.1, 0.25, -0.2), 0.012, 'steel', None, 6)
    if v == 0:
        b.box((0, 0, 0), (0.60, 0.04, 0.40), 'plate', (0.1, 0.2, 0.3))
        b.box((0.1, 0.03, 0.05), (0.40, 0.02, 0.10), 'hazard', (0.1, 0.2, 0.3))
        b.cyl((-0.2, 0.0, 0.0), (0.2, 0.05, 0.3), 0.02, 'steel', None, 8)
    elif v == 1:
        b.cyl((-0.4, 0, 0), (0.4, 0, 0), 0.06, 'steel', 0.05, 10)
        b.box((0.0, 0.0, 0.07), (0.30, 0.10, 0.02), 'dark')
        b.cyl((0.4, 0, 0), (0.5, 0.02, 0.04), 0.05, 'dark', 0.02, 6, False)
    elif v == 2:
        b.cyl((0, -0.3, 0), (0, 0.3, 0), 0.16, 'plate', 0.16, 14)
        b.cyl((0, -0.3, 0), (0, -0.32, 0), 0.12, 'dark', None, 14)
        b.box((0.1, 0.05, 0.15), (0.16, 0.20, 0.03), 'hazard', (0, 0, 0.4))
    else:
        b.box((0, 0, 0), (0.35, 0.25, 0.20), 'steel', (0.3, 0.1, 0.4))
        b.box((0.15, 0.1, 0.1), (0.20, 0.10, 0.10), 'dark', (0.1, 0.7, 0.2))
        b.cyl((-0.2, 0.1, 0), (-0.45, 0.2, 0.1), 0.02, 'steel', None, 6)
    return b


def build(spec, mats):
    P = spec['params']
    lay = P['layout']
    if lay == 'rocket_guided': b = L_rocket(spec, mats, True)
    elif lay == 'rocket_free': b = L_rocket(spec, mats, False)
    elif lay == 'cache': b = L_cache(spec, mats)
    elif lay == 'probe': b = L_probe(spec, mats)
    elif lay == 'ice': b = L_ice(spec, mats)
    elif lay == 'monolith': b = L_monolith(spec, mats)
    elif lay == 'lair': b = L_lair(spec, mats)
    elif lay == 'sat': b = L_sat(spec, mats)
    elif lay == 'lava': b = L_lava(spec, mats)
    elif lay == 'debris': b = L_debris(spec, mats)
    else: raise ValueError(lay)
    objs = b.finish(P.get('scale_m', 10.0), up_z=lay in ('ice', 'monolith', 'lair', 'lava'))
    return {'objects': objs, 'sockets': []}


def preview(spec, out, fast, obs, probe=False):
    return {'note': 'prop: lookdev yok'}
