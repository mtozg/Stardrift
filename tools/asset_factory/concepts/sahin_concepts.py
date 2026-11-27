"""Şahin — 3 KONSEPT (PREVIEW profili, üretim varlığı DEĞİL). Her konsept farklı ana gövde mimarisi ve itki düzeni:
A "Mızrak"  : tek omurga gövde + omurga topu, kuyrukta çaprazlı (X) radyatör, tek ana motor.
B "Çatal"   : kısa merkez kapsül + iki uzun gövde-kirişi (H çerçeve), iki ana motor, radyatör = dikey dış plaka.
C "Binici"  : arkada büyük itki tamburu, öne uzanan açık kafes omurga, üstte kapsül kokpit, yanlarda tank/silah askısı.
Çıktı: renkli 4 görünüm (üst, yan, ön, 3/4) + siyah silüet testi. Kullanım: python concepts/sahin_concepts.py <A|B|C> <çıkış_klasörü>
Koordinat: oyun uzayı (x yanal, y yukarı, z burun +), metre; g2b ile Blender'a çevrilir."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy, bmesh
from mathutils import Vector, Matrix
from core import geo

OBJS = []
MATS = {}


def mat(name, base, metal=0.0, rough=0.5, emit=None, bump=0.0, tiles=False):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); bs = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Base Color'].default_value = (*base, 1); bs.inputs['Metallic'].default_value = metal; bs.inputs['Roughness'].default_value = rough
    if emit:
        bs.inputs['Emission Color'].default_value = (*emit, 1); bs.inputs['Emission Strength'].default_value = 6.0
    if tiles:      # seramik karo / panel dikişi (bump)
        tc = nt.nodes.new('ShaderNodeTexCoord'); br = nt.nodes.new('ShaderNodeTexBrick'); bp = nt.nodes.new('ShaderNodeBump')
        br.inputs['Scale'].default_value = 1.6; br.inputs['Mortar Size'].default_value = 0.012; br.inputs['Brick Width'].default_value = 0.9; br.inputs['Row Height'].default_value = 0.5
        br.inputs['Color1'].default_value = (0.9, 0.9, 0.9, 1); br.inputs['Color2'].default_value = (0.8, 0.8, 0.8, 1); br.inputs['Mortar'].default_value = (0.0, 0, 0, 1)
        nt.links.new(tc.outputs['Object'], br.inputs['Vector']); bp.inputs['Strength'].default_value = 0.6; bp.inputs['Distance'].default_value = 0.01
        nt.links.new(br.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], bs.inputs['Normal'])
        nt.links.new(br.outputs['Color'], bs.inputs['Base Color']) if False else None
    nt.links.new(bs.outputs['BSDF'], out.inputs['Surface'])
    return m


def setup_mats():
    MATS['ceramic'] = mat('ceramic', (0.60, 0.61, 0.63), 0.0, 0.42, tiles=True)
    MATS['titan'] = mat('titan', (0.34, 0.35, 0.37), 0.85, 0.38)
    MATS['gun'] = mat('gun', (0.045, 0.047, 0.055), 0.8, 0.42)
    MATS['heat'] = mat('heat', (0.07, 0.055, 0.045), 0.3, 0.7)
    MATS['red'] = mat('red', (0.42, 0.04, 0.03), 0.1, 0.4)
    MATS['glass'] = mat('glass', (0.01, 0.025, 0.04), 0.0, 0.08)
    MATS['hot'] = mat('hot', (1, 0.5, 0.2), 0, 0.5, emit=(1.0, 0.45, 0.15))
    MATS['blue'] = mat('blue', (0.4, 0.6, 1), 0, 0.5, emit=(0.4, 0.65, 1.0))


def add(bm, name, key, smooth=True, bevel=0.0):
    for v in bm.verts:
        v.co = geo.g2b(Vector(v.co))
    bm.normal_update()
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(MATS[key])
    for p in ob.data.polygons:
        p.use_smooth = smooth
    if bevel:
        m = ob.modifiers.new('b', 'BEVEL'); m.width = bevel; m.segments = 2; m.limit_method = 'ANGLE'
    OBJS.append(ob)
    return ob


def zone(ob, keys, fn):
    """yüz bazlı malzeme: fn(x, y_yukarı, z_ileri) → keys indeksi"""
    for k in keys:
        ob.data.materials.append(MATS[k])
    for p in ob.data.polygons:
        c = sum((ob.data.vertices[i].co for i in p.vertices), Vector()) / len(p.vertices)
        p.material_index = fn(c.x, c.z, -c.y)


def sup(a, p):
    return math.copysign(abs(a) ** (2.0 / p), a)


def loft(secs, n=36, axis_cap=True):
    """secs: (z, yarı_genişlik, yarı_üst, yarı_alt, p [2=elips, 4≈yuvarlak kare], cx, cy)"""
    bm = bmesh.new(); rings = []
    for s in secs:
        z, wx, hu, hd, p = s[:5]; cx = s[5] if len(s) > 5 else 0.0; cy = s[6] if len(s) > 6 else 0.0
        ring = []
        for i in range(n):
            t = 2 * math.pi * i / n; c, sn = math.cos(t), math.sin(t)
            ring.append(bm.verts.new((cx + wx * sup(c, p), cy + (hu if sn > 0 else hd) * sup(sn, p), z)))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([r0[i], r0[j], r1[j], r1[i]])
    if axis_cap:
        for ring in (rings[0], rings[-1]):
            bm.faces.new(ring if ring is rings[-1] else ring[::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def tube(p0, p1, r0, r1=None, seg=20, cap=True):
    bm = bmesh.new(); d = Vector(p1) - Vector(p0)
    M = Matrix.Translation((Vector(p0) + Vector(p1)) / 2) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=seg, radius1=r0, radius2=r0 if r1 is None else r1, depth=d.length, matrix=M)
    return bm


def box(c, s, rot=0.0):
    bm = bmesh.new(); r = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(c)) @ Matrix.Rotation(rot, 4, 'Z') @ Matrix.Diagonal((*s, 1.0)), verts=r['verts'])
    return bm


def fin_prism(a, r0, r1, zr0, zr1, zt0, zt1, th):
    """radyatör kanatçığı: kök (r0, z zr0..zr1) → uç (r1, z zt0..zt1); a = nose ekseni etrafında açı; kalınlık th (teğet yönde)"""
    bm = bmesh.new(); ca, sa = math.cos(a), math.sin(a)
    def V(r, z, t):
        return bm.verts.new((ca * r - sa * t, sa * r + ca * t, z))
    rt = [V(r0, zr0, th / 2), V(r0, zr1, th / 2), V(r0, zr1, -th / 2), V(r0, zr0, -th / 2)]
    tp = [V(r1, zt0, th / 3), V(r1, zt1, th / 3), V(r1, zt1, -th / 3), V(r1, zt0, -th / 3)]
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new([rt[i], rt[j], tp[j], tp[i]])
    bm.faces.new(rt[::-1]); bm.faces.new(tp)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def plate_bm(pts_zy, x, th):
    """yan plaka: (z, y) çokgeni x konumunda th kalınlıkla ekstrüde"""
    bm = bmesh.new()
    a = [bm.verts.new((x - th / 2, y, z)) for z, y in pts_zy]; b = [bm.verts.new((x + th / 2, y, z)) for z, y in pts_zy]
    bm.faces.new(a[::-1]); bm.faces.new(b)
    n = len(pts_zy)
    for i in range(n):
        j = (i + 1) % n; bm.faces.new([a[i], a[j], b[j], b[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def box_z(c, s, rot):
    """z ekseni (burun) etrafında döndürülmüş kutu"""
    bm = bmesh.new(); r = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(c)) @ Matrix.Rotation(rot, 4, 'Z') @ Matrix.Diagonal((*s, 1.0)), verts=r['verts'])
    return bm


def nozzle(x, y, z, r, length=0.9, glow='hot'):
    """motor: dış çan + ısı kalkanı halkası + içte parlayan çekirdek"""
    add(tube((x, y, z + 0.1), (x, y, z - length), r * 0.72, r, 32, cap=False), 'bell', 'heat', True)
    add(tube((x, y, z + 0.14), (x, y, z + 0.02), r * 0.80, None, 32), 'shield', 'titan', True)
    add(tube((x, y, z - length + 0.06), (x, y, z - length + 0.10), r * 0.82, None, 32), 'inner', 'gun', True)
    add(tube((x, y, z - length + 0.09), (x, y, z - length + 0.11), r * 0.55, None, 28), 'core', glow, True)
    add(tube((x, y, z - length), (x, y, z - length - 0.05), r * 1.03, r * 1.03, 32, cap=False), 'lip', 'titan', True)


def canopy(zs, cy, w, h, ln, extra_frame=0.07):
    """kasalı cam: önce titanyum kasa (hafif büyük/alçak), üstüne cam; ikisi de gövde üstüne oturur"""
    z0, z1 = zs
    zm = (z0 + z1) / 2
    fr = [(z0 - 0.15, w * 0.35 + extra_frame, 0.02, 0.0, 2.4, 0, cy), (zm - ln * 0.2, w + extra_frame, h * 0.8, 0.0, 2.6, 0, cy), (zm + ln * 0.2, w * 0.95 + extra_frame, h * 0.8, 0.0, 2.6, 0, cy), (z1 + 0.1, w * 0.3 + extra_frame, 0.02, 0.0, 2.4, 0, cy)]
    gl = [(z0, w * 0.32, h * 0.45, 0.0, 2.4, 0, cy), (zm - ln * 0.2, w, h, 0.0, 2.6, 0, cy), (zm + ln * 0.2, w * 0.95, h * 0.95, 0.0, 2.6, 0, cy), (z1, w * 0.28, h * 0.4, 0.0, 2.4, 0, cy)]
    add(loft(fr), 'cframe', 'titan', True)
    add(loft(gl), 'glass', 'glass', True)
    for dx in (-1, 1):       # cam kenar çıtası
        add(box((dx * w * 0.5, cy + h * 0.55, zm), (0.025, 0.025, ln * 0.7)), 'mull', 'titan', True)
    add(box((0, cy + h * 0.95, zm), (0.03, 0.03, ln * 0.9)), 'spine', 'titan', True)


def build_A():
    hull = [(-4.1, 0.42, 0.40, 0.36, 2.6), (-3.6, 0.80, 0.52, 0.42, 3.0), (-2.4, 1.05, 0.55, 0.44, 3.4), (-0.6, 1.00, 0.54, 0.42, 3.6), (0.9, 0.84, 0.48, 0.38, 3.2), (2.3, 0.55, 0.34, 0.28, 2.8), (3.4, 0.28, 0.20, 0.16, 2.4), (4.0, 0.10, 0.08, 0.08, 2.0)]
    h = add(loft(hull), 'hull', 'ceramic', True)
    h.data.materials.clear()
    zone(h, ['ceramic', 'titan', 'heat'], lambda x, y, z: 2 if z < -3.2 else (1 if (y < -0.05 or z > 3.0) else 0))
    canopy((0.7, 2.9), 0.46, 0.30, 0.20, 2.2)
    # omurga topu: namlu + bobin halkaları + ray çubukları
    add(tube((0, 0.0, 3.3), (0, 0.0, 5.1), 0.085, 0.07, 20), 'barrel', 'gun', True)
    for i in range(7):
        z = 3.55 + i * 0.24
        add(tube((0, 0, z), (0, 0, z + 0.11), 0.14, None, 24), 'coil', 'titan', True)
    for sx in (-1, 1):
        add(box((sx * 0.10, 0.0, 4.4), (0.025, 0.025, 1.4)), 'rail', 'gun', True)
    add(tube((0, 0, 5.0), (0, 0, 5.3), 0.05, 0.03, 12), 'muzzle', 'gun', True)
    nozzle(0, 0, -4.0, 0.52, 0.95)
    for k in range(4):      # geriye süpürmeli radyatör kanatçıkları (X düzeni): ısı atımı işlevi, uç kırmızı
        a = math.radians(45 + 90 * k)
        add(fin_prism(a, 0.55, 1.75, -2.2, -3.55, -3.4, -4.0, 0.05), 'rad', 'ceramic', True, 0.004)
        add(fin_prism(a, 0.56, 1.70, -2.35, -3.4, -3.45, -3.95, 0.075), 'radc', 'gun', True)
        add(fin_prism(a, 1.72, 1.78, -3.38, -3.98, -3.42, -4.02, 0.09), 'radt', 'red', True)
    for dx in (-1, 1):
        add(box((dx * 0.96, 0.02, 0.6), (0.06, 0.30, 1.6)), 'intake', 'gun', True)
        add(box((dx * 0.50, 0.46, 2.0), (0.14, 0.05, 0.5)), 'sens', 'titan', True)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        add(box_z((math.cos(a) * 0.39, math.sin(a) * 0.37, 3.0), (0.09, 0.09, 0.16), a), 'rcs', 'gun', True)
    add(tube((0, -0.42, 1.8), (0, -0.52, 1.8), 0.14, 0.10, 16), 'dome', 'gun', True)
    add(tube((0.1, 0.55, -1.8), (0.2, 0.95, -2.0), 0.012, 0.007, 6), 'ant', 'gun', True)
    for z in (-1.7, -0.5, 0.2):
        add(box((0, 0.575, z), (0.55, 0.012, 0.16)), 'mark', 'red', True)


def build_B():
    pod = [(-1.3, 0.55, 0.42, 0.40, 2.8), (-0.4, 0.80, 0.60, 0.52, 3.0), (1.3, 0.76, 0.58, 0.48, 3.0), (2.6, 0.52, 0.42, 0.36, 2.6), (3.5, 0.22, 0.18, 0.17, 2.2), (4.0, 0.07, 0.07, 0.07, 2.0)]
    pd = add(loft(pod), 'pod', 'ceramic', True)
    pd.data.materials.clear()
    zone(pd, ['ceramic', 'titan'], lambda x, y, z: 1 if (z < -0.2 or y < -0.1 or z > 3.2) else 0)
    canopy((0.9, 3.0), 0.55, 0.40, 0.22, 2.0)
    add(tube((0, -0.05, 3.6), (0, -0.05, 5.4), 0.13, 0.10, 20), 'gun', 'gun', True)
    add(tube((0, -0.05, 3.7), (0, -0.05, 3.95), 0.22, None, 24), 'mount', 'titan', True)
    for sx in (-1, 1):
        cx = sx * 2.1
        boom = [(-4.2, 0.40, 0.38, 0.38, 2.6, cx), (-3.5, 0.56, 0.50, 0.50, 2.8, cx), (-1.0, 0.52, 0.46, 0.46, 2.8, cx), (1.4, 0.44, 0.40, 0.40, 2.6, cx), (2.7, 0.28, 0.26, 0.26, 2.4, cx), (3.4, 0.09, 0.09, 0.09, 2.0, cx)]
        b = add(loft(boom), 'boom', 'titan', True)
        b.data.materials.clear()
        zone(b, ['titan', 'ceramic'], lambda x, y, z: 1 if y > 0.05 else 0)
        nozzle(cx, 0, -4.2, 0.38, 0.9)
        add(tube((cx, 0.0, 3.1), (cx, 0.0, 4.4), 0.055, 0.04, 12), 'pgun', 'gun', True)
        add(box((cx, 0.0, 2.9), (0.2, 0.2, 0.5)), 'pcase', 'gun', True)
        # dış radyatör plakası (dikey) + soğutma hattı + kırmızı kenar
        ox = sx * (2.1 + 0.62)
        add(plate_bm([(-3.9, -0.55), (-3.9, 0.55), (-1.9, 1.55), (0.1, 1.05), (0.4, 0.2), (0.0, -0.8), (-2.4, -1.15)], ox, 0.06), 'rad', 'ceramic', True, 0.008)
        add(plate_bm([(-3.6, -0.2), (-3.6, 0.35), (-1.9, 1.1), (-0.3, 0.8), (-0.1, 0.1), (-2.4, -0.7)], ox + sx * 0.04, 0.03), 'radc', 'gun', True)
        add(plate_bm([(-3.9, -0.55), (-3.9, 0.55), (-3.8, 0.55), (-3.8, -0.55)], ox, 0.09), 'radt', 'red', True)
        # pod-bom bağlantı kirişi (öne eğimli)
        add(box((sx * 1.15, 0.0, -0.1), (1.4, 0.34, 1.5)), 'strut', 'titan', True, 0.03)
        add(box((sx * 1.15, 0.2, -0.1), (1.0, 0.02, 1.2)), 'strutp', 'gun', True)
    add(box((0, 0.0, -2.8), (4.2, 0.36, 0.9)), 'xbeam', 'titan', True, 0.04)
    add(box((0, 0.2, -2.8), (3.6, 0.02, 0.6)), 'xbeamp', 'gun', True)
    add(tube((-2.1, 0.0, 2.3), (2.1, 0.0, 2.3), 0.07, None, 12), 'spar', 'titan', True)
    for sx in (-1, 1):
        add(box((sx * 1.1, 0.0, 2.3), (0.18, 0.18, 0.18)), 'sparnode', 'gun', True)
    for z in (-0.6, 0.4):
        add(box((0, 0.605, z), (0.7, 0.012, 0.18)), 'mark', 'red', True)
    add(tube((0.1, 0.65, -0.9), (0.18, 1.05, -1.0), 0.012, 0.007, 6), 'ant', 'gun', True)


def build_C():
    drum = [(-4.3, 0.62, 0.62, 0.62, 2.0), (-3.8, 0.92, 0.92, 0.92, 2.0), (-1.6, 0.92, 0.92, 0.92, 2.1), (-0.8, 0.66, 0.66, 0.66, 2.0), (-0.1, 0.30, 0.30, 0.30, 2.0)]
    d = add(loft(drum, 40), 'drum', 'titan', True)
    for k in range(9):      # soğutma halkaları
        z = -3.6 + k * 0.28
        add(tube((0, 0, z), (0, 0, z + 0.07), 0.955, None, 40), 'fin', 'gun', True)
    add(box((0, 0.93, -2.5), (1.1, 0.04, 2.6)), 'rad1', 'ceramic', True, 0.008)      # üst katlanmış radyatör panelleri
    for sx in (-1, 1):
        add(box((sx * 0.80, 0.50, -2.7), (0.04, 0.9, 2.2)), 'rad2', 'ceramic', True, 0.008)
        add(box((sx * 0.82, 0.50, -3.82), (0.06, 0.92, 0.06)), 'rad2t', 'red', True)
    nozzle(0, 0, -4.3, 0.62, 1.0)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        nozzle(math.cos(a) * 0.80, math.sin(a) * 0.80, -4.0, 0.10, 0.35, 'blue')
    # açık kafes omurga: 4 boyuna tüp + enine halkalar + çaprazlar
    cs = [(-0.46, -0.36), (0.46, -0.36), (0.46, 0.34), (-0.46, 0.34)]
    for cx, cy in cs:
        add(tube((cx, cy, -0.1), (cx, cy, 4.2), 0.06, None, 10), 'lon', 'titan', True)
    zs = [0.1 + i * 0.7 for i in range(6)]
    for z in zs:
        for a, b in zip(cs, cs[1:] + cs[:1]):
            add(tube((a[0], a[1], z), (b[0], b[1], z), 0.035, None, 8), 'ring', 'gun', True)
    for z0, z1 in zip(zs, zs[1:]):
        for a, b, flip in ((cs[0], cs[1], 1), (cs[2], cs[3], 1), (cs[1], cs[2], 0), (cs[3], cs[0], 0)):
            add(tube((a[0], a[1], z0), (b[0], b[1], z1), 0.025, None, 8), 'diag', 'gun', True)
    # yanlarda tank ve silah askıları
    for sx in (-1, 1):
        tk = [(-0.2, 0.18, 0.18, 0.18, 2.0, sx * 0.88, -0.25), (0.3, 0.32, 0.32, 0.32, 2.0, sx * 0.88, -0.25), (2.0, 0.32, 0.32, 0.32, 2.0, sx * 0.88, -0.25), (2.7, 0.14, 0.14, 0.14, 2.0, sx * 0.88, -0.25)]
        add(loft(tk, 24), 'tank', 'ceramic', True)
        add(tube((sx * 0.88, -0.25, 0.5), (sx * 0.88, -0.25, 0.56), 0.335, None, 24), 'band', 'red', True)
        add(tube((sx * 0.88, -0.25, 1.5), (sx * 0.88, -0.25, 1.56), 0.335, None, 24), 'band2', 'gun', True)
        add(box((sx * 0.62, -0.05, 1.0), (0.3, 0.1, 0.1)), 'brace', 'titan', True)
        add(box((sx * 0.95, 0.30, 3.3), (0.26, 0.24, 1.3)), 'gpod', 'gun', True, 0.02)
        add(tube((sx * 0.95, 0.30, 3.9), (sx * 0.95, 0.30, 5.0), 0.05, 0.04, 10), 'gbar', 'gun', True)
        add(box((sx * 0.72, 0.3, 3.0), (0.4, 0.1, 0.12)), 'gmount', 'titan', True)
    # kapsül kokpit + pilon
    cap = [(1.4, 0.26, 0.20, 0.24, 2.4, 0, 0.95), (2.1, 0.46, 0.36, 0.32, 2.7, 0, 0.95), (3.1, 0.42, 0.32, 0.28, 2.7, 0, 0.95), (4.0, 0.18, 0.16, 0.14, 2.3, 0, 0.95), (4.5, 0.06, 0.05, 0.05, 2.0, 0, 0.95)]
    cp = add(loft(cap), 'capsule', 'ceramic', True)
    add(box((0, 0.55, 2.0), (0.34, 0.5, 1.0)), 'pylon', 'titan', True, 0.04)
    add(box((0, 0.58, 3.4), (0.26, 0.3, 0.7)), 'pylon2', 'titan', True, 0.03)
    canopy((2.3, 3.9), 0.95, 0.30, 0.26, 1.4)
    add(tube((0, 1.36, 2.6), (0, 1.38, 2.62), 0.0001, None, 3), 'dummy', 'gun', True)
    add(tube((0.12, 1.4, 2.0), (0.2, 1.8, 1.9), 0.012, 0.007, 6), 'ant', 'gun', True)
    for z in (1.6, 2.2):
        add(box((0, 1.5, z), (0.5, 0.012, 0.16)), 'mark', 'red', True)


def lights():
    w = bpy.context.scene.world or bpy.data.worlds.new('W'); bpy.context.scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes.get('Background'); bg.inputs[0].default_value = (0.05, 0.058, 0.075, 1); bg.inputs[1].default_value = 1.0
    def area(loc, e, col, size):
        ld = bpy.data.lights.new('l', 'AREA'); ld.energy = e; ld.color = col; ld.size = size
        o = bpy.data.objects.new('l', ld); bpy.context.scene.collection.objects.link(o); o.location = loc
        o.rotation_euler = (-Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        return o
    area((7, -6, 9), 2200, (1.0, 0.95, 0.88), 6)
    area((-9, 7, 5), 900, (0.6, 0.76, 1.0), 6)
    area((0, -3, -8), 250, (0.8, 0.85, 1.0), 6)


def cam(kind, scale):
    cd = bpy.data.cameras.new('c'); o = bpy.data.objects.new('c', cd); bpy.context.scene.collection.objects.link(o)
    if kind == 'persp':
        cd.type = 'PERSP'; cd.lens = 36
        o.location = (-11.5, -15.0, 6.5)
        o.rotation_euler = (Vector((0.0, 0.8, 0.0)) - o.location).to_track_quat('-Z', 'Z').to_euler()
        return o
    cd.type = 'ORTHO'; cd.ortho_scale = scale
    if kind == 'top':
        o.location = (0, 0, 30); o.rotation_euler = (0, 0, 0)       # Blender: nose −Y, görüntüde alt; 180° döndür → burun üstte
        o.rotation_euler = (0, 0, math.pi)
    elif kind == 'side':
        o.location = (-30, 0, 0); o.rotation_euler = (math.pi / 2, 0, -math.pi / 2)          # burun sağa bakar
    elif kind == 'front':
        o.location = (0, -30, 0); o.rotation_euler = (math.pi / 2, 0, 0)
    return o


def render(path, camob, res, engine, samples=40):
    sc = bpy.context.scene; sc.camera = camob
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'; sc.render.filepath = path
    if engine == 'cycles':
        sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = samples; sc.cycles.use_denoising = True; sc.cycles.max_bounces = 3
        sc.view_settings.view_transform = 'AgX'
    else:      # silüet: tüm malzemeler siyah, zemin beyaz (Cycles; ortamda GPU/EGL yok → Workbench kullanılamıyor)
        sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 6; sc.cycles.use_denoising = False; sc.cycles.max_bounces = 0
        sc.view_settings.view_transform = 'Standard'
        if 'sil_black' not in bpy.data.materials:
            m = bpy.data.materials.new('sil_black'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
            o_ = nt.nodes.new('ShaderNodeOutputMaterial'); e_ = nt.nodes.new('ShaderNodeEmission'); e_.inputs['Color'].default_value = (0, 0, 0, 1)
            nt.links.new(e_.outputs['Emission'], o_.inputs['Surface'])
        w = sc.world or bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
        bg = w.node_tree.nodes.get('Background'); bg.inputs[0].default_value = (1, 1, 1, 1); bg.inputs[1].default_value = 1.0
        bpy.context.view_layer.material_override = bpy.data.materials['sil_black']
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    which, out = sys.argv[-2], sys.argv[-1]
    os.makedirs(out, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    setup_mats()
    {'A': build_A, 'B': build_B, 'C': build_C}[which]()
    # silüet testi (Workbench düz siyah / beyaz zemin)
    for k, sc_ in (('top', 18.0), ('side', 18.0), ('front', 9.0)):
        render(os.path.join(out, 'sil_%s.png' % k), cam(k, sc_), (1800, 1080), 'wb')
    render(os.path.join(out, 'sil_persp.png'), cam('persp', 0), (1800, 1080), 'wb')
    # renkli
    bpy.context.view_layer.material_override = None
    lights()
    for k, sc_ in (('top', 18.0), ('side', 18.0), ('front', 9.0)):
        render(os.path.join(out, 'c_%s.png' % k), cam(k, sc_), (1800, 1080), 'cycles', 48)
    render(os.path.join(out, 'c_persp.png'), cam('persp', 0), (1800, 1080), 'cycles', 64)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'massing.blend'), compress=True)
    print('DONE', which)
