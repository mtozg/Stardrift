"""Akbaba (raider, korsan vur-kaç gemisi) — 3 KONSEPT (PREVIEW kütle modeli, üretim varlığı DEĞİL).
Sanat yönü: doğaçlama ama mekanik olarak bütünleşik; jenerik uçak kanadı YOK; Şahin Çatal'dan ayrı mimari.
A "Çalıntı Çekirdek": önde dar kokpit, arkada dışarı açık dev sürücü çekirdeği (asimetrik), kafes omurga, kanca fırlatıcılar.
B "Akbaba": kambur sırt, aşağı kıvrık yırtıcı gaga (ram/abordaj kancası), geniş omuzlarda dışa eğik iki motor kapsülü.
C "Kesici": uzun dar iskelet gövde, önde iki mafsallı kesici kol (disk testereli), yanlarda kablo tamburu, arkada üçlü motor kümesi.
Kullanım: python concepts/akbaba_concepts.py <A|B|C> <çıkış_klasörü>"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Matrix
import sahin_concepts as S
from sahin_concepts import loft, tube, box, box_z, plate_bm, nozzle, canopy, add, mat, MATS, lights, cam, render, bmesh


def setup():
    S.setup_mats()
    MATS['paint'] = mat('paint', (0.42, 0.19, 0.09), 0.0, 0.5)              # pas-kahve boya (kontrollü)
    MATS['ochre'] = mat('ochre', (0.55, 0.40, 0.12), 0.0, 0.5)             # sarı-turuncu işaret
    MATS['steel'] = mat('steel', (0.30, 0.31, 0.33), 0.8, 0.45)
    MATS['plate'] = mat('plate', (0.20, 0.18, 0.16), 0.5, 0.55)            # yamalı zırh levhası


def rz(bm, ang, c=(0, 0, 0)):
    """z (burun) ekseni etrafında döndür"""
    M = Matrix.Translation(Vector(c)) @ Matrix.Rotation(ang, 4, 'Z') @ Matrix.Translation(-Vector(c))
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return bm


def ry(bm, ang, c=(0, 0, 0)):
    """yukarı (y) ekseni etrafında döndür (toe)"""
    M = Matrix.Translation(Vector(c)) @ Matrix.Rotation(ang, 4, 'Y') @ Matrix.Translation(-Vector(c))
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return bm


def rx(bm, ang, c=(0, 0, 0)):
    M = Matrix.Translation(Vector(c)) @ Matrix.Rotation(ang, 4, 'X') @ Matrix.Translation(-Vector(c))
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return bm


def build_A():
    # kokpit kapsülü (dar, ön)
    cap = [(1.0, 0.30, 0.26, 0.24, 2.6, 0, 0.1), (2.0, 0.50, 0.40, 0.34, 2.8, 0, 0.1), (3.1, 0.44, 0.34, 0.30, 2.8, 0, 0.08), (4.0, 0.20, 0.16, 0.15, 2.4, 0, 0.05), (4.6, 0.06, 0.05, 0.05, 2.0, 0, 0.04)]
    add(loft(cap), 'cockpit', 'ochre', True)
    canopy((1.8, 3.4), 0.36, 0.30, 0.22, 1.5)
    # arkada dışarı açık sürücü çekirdeği (sağa ofsetli) + halka bantları + soğutma kanatları
    core = [(-3.6, 0.8, 0.8, 0.8, 2.0, 0.35, 0.0), (-3.0, 1.15, 1.15, 1.15, 2.0, 0.35, 0.0), (-1.7, 1.15, 1.15, 1.15, 2.0, 0.35, 0.0), (-0.7, 0.78, 0.78, 0.78, 2.0, 0.35, 0.0), (-0.2, 0.30, 0.30, 0.30, 2.0, 0.35, 0.0)]
    add(loft(core, 44), 'core', 'steel', True)
    for k in range(8):
        add(tube((0.35, 0, -3.3 + k * 0.28), (0.35, 0, -3.3 + k * 0.28 + 0.06), 1.2, None, 44), 'band', 'gun', True)
    add(box((0.35, 1.18, -2.2), (1.4, 0.06, 2.2)), 'radp', 'plate', True, 0.01)
    add(box((0.35, -1.18, -2.2), (1.4, 0.06, 2.2)), 'radp', 'plate', True, 0.01)
    nozzle(0.35, 0.0, -3.6, 0.7, 1.0)
    # ikinci (yama) motor solda, küçük
    add(loft([(-2.8, 0.34, 0.34, 0.34, 2.0, -1.5, -0.2), (-1.6, 0.4, 0.4, 0.4, 2.0, -1.5, -0.2), (-1.0, 0.25, 0.25, 0.25, 2.0, -1.5, -0.2)], 28), 'eng2', 'gun', True)
    nozzle(-1.5, -0.2, -2.8, 0.34, 0.6)
    # kafes omurga (kokpit ↔ çekirdek)
    cs = [(-0.28, -0.22), (0.28, -0.22), (0.28, 0.22), (-0.28, 0.22)]
    for cx, cy in cs:
        add(tube((cx, cy, -0.3), (cx, cy, 1.2), 0.05, None, 10), 'lon', 'steel', True)
    for z in (-0.1, 0.4, 0.9):
        for a, b in zip(cs, cs[1:] + cs[:1]):
            add(tube((a[0], a[1], z), (b[0], b[1], z), 0.03, None, 8), 'ring', 'gun', True)
    # yamalı zırh levhaları (asimetrik, işlevli: çekirdek koruması)
    for (x, y, z, sx_, sy_, sz_, a) in ((-0.9, 0.35, -1.2, 0.08, 0.8, 1.4, 0.2), (1.35, 0.5, -0.9, 0.08, 0.9, 1.1, -0.25), (0.9, -0.6, -1.2, 0.08, 0.7, 1.2, 0.3)):
        add(rz(box((x, y, z), (sx_, sy_, sz_)), a, (x, y, z)), 'armor', 'plate', True, 0.01)
    add(rz(box((-0.8, -0.2, 0.2), (0.1, 0.5, 0.9)), 0.25, (-0.8, -0.2, 0.2)), 'armor', 'plate', True, 0.01)
    # yan yakıt tankı (sola bağlı)
    add(loft([(-1.6, 0.26, 0.26, 0.26, 2.0, -0.95, -0.55), (-0.9, 0.34, 0.34, 0.34, 2.0, -0.95, -0.55), (0.9, 0.34, 0.34, 0.34, 2.0, -0.95, -0.55), (1.4, 0.2, 0.2, 0.2, 2.0, -0.95, -0.55)], 24), 'tank', 'ochre', True)
    # kanca fırlatıcılar (burun altı)
    for sx in (-1, 1):
        add(tube((sx * 0.3, -0.3, 2.6), (sx * 0.4, -0.35, 4.3), 0.07, 0.05, 12), 'hook', 'gun', True)
        add(box((sx * 0.4, -0.35, 4.35), (0.2, 0.05, 0.12)), 'hookt', 'steel', True)
        add(tube((sx * 0.2, -0.28, 2.4), (sx * 0.2, -0.28, 2.6), 0.15, None, 16), 'drum', 'steel', True)
    add(tube((0.0, 0.5, 2.2), (0.0, 0.85, 2.0), 0.015, 0.008, 6), 'ant', 'gun', True)
    for z in (1.5, 2.4):
        add(box((0, 0.395, z), (0.5, 0.012, 0.18)), 'mark', 'ochre', True)


def build_B():
    # gövde: kambur omuz + aşağı kıvrık gaga (ram)
    hull = [(-2.3, 0.70, 0.55, 0.50, 2.8, 0, 0.35), (-1.3, 1.00, 0.72, 0.60, 3.0, 0, 0.45), (-0.2, 0.95, 0.70, 0.55, 3.0, 0, 0.45), (0.9, 0.68, 0.52, 0.42, 2.8, 0, 0.38),
            (2.0, 0.42, 0.34, 0.28, 2.6, 0, 0.18), (3.1, 0.24, 0.2, 0.17, 2.4, 0, -0.08), (4.0, 0.13, 0.12, 0.1, 2.2, 0, -0.36), (4.7, 0.05, 0.05, 0.04, 2.0, 0, -0.62)]
    h = add(loft(hull, 40), 'hull', 'paint', True)
    canopy((0.2, 2.0), 0.88, 0.40, 0.26, 1.6)
    # gaga altında çene (ram/abordaj kancası)
    add(box((0, -0.45, 3.2), (0.16, 0.14, 1.6)), 'jaw', 'steel', True, 0.015)
    add(tube((0, -0.52, 4.0), (0, -0.78, 4.55), 0.05, 0.015, 8), 'tooth', 'steel', True)
    # omuzlarda dışa eğik (toe-out 14°) iki motor kapsülü
    for sx in (-1, 1):
        pod = loft([(-3.1, 0.52, 0.52, 0.52, 2.0, sx * 1.55, 0.5), (-2.6, 0.7, 0.7, 0.7, 2.0, sx * 1.55, 0.5), (-0.6, 0.7, 0.7, 0.7, 2.0, sx * 1.55, 0.5), (0.3, 0.42, 0.42, 0.42, 2.0, sx * 1.55, 0.5), (0.7, 0.14, 0.14, 0.14, 2.0, sx * 1.55, 0.5)], 30)
        ry(pod, sx * math.radians(12), (sx * 1.55, 0.5, -1.2))
        add(pod, 'pod', 'steel', True)
        nz = bmesh_new_tube = tube((sx * 1.55, 0.5, -3.1), (sx * 1.55, 0.5, -3.95), 0.5, 0.42, 28, cap=False)
        ry(nz, sx * math.radians(12), (sx * 1.55, 0.5, -1.2))
        add(nz, 'bell', 'heat', True)
        gl = tube((sx * 1.55, 0.5, -3.93), (sx * 1.55, 0.5, -3.9), 0.28, None, 24)
        ry(gl, sx * math.radians(12), (sx * 1.55, 0.5, -1.2))
        add(gl, 'core', 'hot', True)
        add(ry(box((sx * 1.05, 0.5, -1.4), (0.8, 0.28, 1.2)), sx * math.radians(12), (sx * 1.05, 0.5, -1.4)), 'mount', 'gun', True, 0.02)
        add(ry(box((sx * 1.55, 1.25, -1.6), (0.08, 0.5, 1.4)), sx * math.radians(12), (sx * 1.55, 1.25, -1.6)), 'fin', 'ochre', True)
    # alt: zıpkın fırlatıcı + vinç kutusu, sırt sensör yelpazesi
    add(tube((0, -0.55, 0.2), (0, -0.55, 2.4), 0.09, 0.07, 14), 'harp', 'gun', True)
    add(box((0, -0.55, -0.6), (0.5, 0.3, 0.8)), 'winch', 'gun', True, 0.02)
    add(tube((0, 0.95, -1.2), (0, 1.0, -1.2), 0.55, None, 32), 'fan', 'steel', True)
    add(tube((0, 0.95, -1.2), (0, 1.35, -1.25), 0.02, 0.01, 6), 'ant', 'gun', True)
    for sx in (-1, 1):
        add(box((sx * 0.62, 0.5, 0.2), (0.4, 0.5, 1.2)), 'sho', 'plate', True, 0.02)


def build_C():
    spine = [(-3.0, 0.36, 0.32, 0.3, 2.6), (-1.8, 0.5, 0.42, 0.36, 2.8), (0.2, 0.42, 0.34, 0.3, 2.8), (2.0, 0.3, 0.26, 0.22, 2.6), (3.2, 0.12, 0.1, 0.09, 2.2), (3.8, 0.04, 0.04, 0.04, 2.0)]
    add(loft(spine, 36), 'spine', 'paint', True)
    canopy((0.8, 2.4), 0.3, 0.28, 0.2, 1.5)
    # arkada üçlü motor kümesi
    eng = [(0.0, 0.42), (-0.62, -0.28), (0.62, -0.28)]
    add(box((0, 0.0, -2.5), (1.9, 1.2, 0.8)), 'eblk', 'steel', True, 0.04)
    for x, y in eng:
        add(tube((x, y, -2.9), (x, y, -2.4), 0.34, 0.3, 24), 'nac', 'gun', True)
        nozzle(x, y, -2.9, 0.3, 0.7)
    # açık iskelet: kargo ağı çerçevesi (gövde altı)
    for sx in (-1, 1):
        add(tube((sx * 0.7, -0.55, -1.5), (sx * 0.7, -0.55, 1.8), 0.05, None, 8), 'netl', 'steel', True)
    for z in (-1.5, -0.4, 0.7, 1.8):
        add(tube((-0.7, -0.55, z), (0.7, -0.55, z), 0.04, None, 8), 'netc', 'gun', True)
        for sx in (-1, 1):
            add(tube((sx * 0.7, -0.55, z), (sx * 0.4, -0.3, z), 0.035, None, 8), 'netd', 'gun', True)
    # önde iki mafsallı kesici kol (disk testere) — dışa açılır
    for sx in (-1, 1):
        add(tube((sx * 0.3, 0.0, 1.8), (sx * 1.1, 0.0, 3.2), 0.1, 0.09, 12), 'arm1', 'steel', True)
        add(tube((sx * 1.1, 0.0, 3.2), (sx * 1.0, 0.0, 4.6), 0.08, 0.07, 12), 'arm2', 'gun', True)
        add(box((sx * 1.1, 0.0, 3.2), (0.26, 0.26, 0.26)), 'joint', 'plate', True, 0.02)
        disc = tube((sx * 1.0 - 0.05, 0.0, 4.6), (sx * 1.0 + 0.05, 0.0, 4.6), 0.62, 0.62, 40)
        rz(disc, math.pi / 2, (sx * 1.0, 0.0, 4.6)) if False else None
        add(rz(tube((sx * 1.0, -0.05, 4.6), (sx * 1.0, 0.05, 4.6), 0.62, 0.62, 40), 0.0), 'disc_dummy', 'ochre', True) if False else None
        # disk: y ekseninde ince silindir (yatay testere); tube z-ekseni → xz düzlemine yatır
        d = tube((0, 0, -0.04), (0, 0, 0.04), 0.62, 0.62, 44)
        rx(d, math.pi / 2)
        bmesh_translate = Matrix.Translation(Vector((sx * 1.0, 0.0, 4.6)))
        bmesh.ops.transform(d, matrix=bmesh_translate, verts=d.verts)
        add(d, 'disc', 'steel', True)
        add(tube((sx * 1.0, -0.02, 4.6), (sx * 1.0, 0.06, 4.6), 0.12, None, 14), 'hub', 'ochre', True)
    # yan kablo tamburları + kanca
    for sx in (-1, 1):
        add(tube((sx * 0.62, 0.05, -0.8), (sx * 0.62, 0.05, -0.3), 0.3, None, 24), 'dr', 'steel', True)
        add(box((sx * 0.62, -0.28, -0.55), (0.12, 0.12, 0.5)), 'hk', 'gun', True)
    add(tube((0, 0.4, -0.8), (0.1, 0.9, -1.0), 0.015, 0.008, 6), 'ant', 'gun', True)
    for z in (0.5, 1.2):
        add(box((0, 0.34, z), (0.4, 0.012, 0.16)), 'mark', 'ochre', True)


if __name__ == '__main__':
    which, out = sys.argv[-2], sys.argv[-1]
    os.makedirs(out, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    setup()
    {'A': build_A, 'B': build_B, 'C': build_C}[which]()
    for k, sc_ in (('top', 18.0), ('side', 18.0), ('front', 9.0)):
        render(os.path.join(out, 'sil_%s.png' % k), cam(k, sc_), (1800, 1080), 'wb')
    render(os.path.join(out, 'sil_persp.png'), cam('persp', 0), (1800, 1080), 'wb')
    bpy.context.view_layer.material_override = None
    lights()
    for k, sc_ in (('top', 18.0), ('side', 18.0), ('front', 9.0)):
        render(os.path.join(out, 'c_%s.png' % k), cam(k, sc_), (1800, 1080), 'cycles', 48)
    render(os.path.join(out, 'c_persp.png'), cam('persp', 0), (1800, 1080), 'cycles', 64)
    print('DONE', which)
