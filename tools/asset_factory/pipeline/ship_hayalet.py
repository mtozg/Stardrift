"""Hayalet — sıfırdan modelleme (konsept c001): ince, alçak, yüzeyli gizli av uçağı; delta kanatlar, ikiz motor, mor ışık çizgileri.
Oyun uzayı: burun +Z, yukarı +Y, uzunluk 1,0. Kullanım: python pipeline/ship_hayalet.py <çıktı_klasörü>"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy
from core.shipkit import Kit

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
PAL = {
    'govde': ((0.11, 0.115, 0.13), 0.5, 0.55, None), 'panel': ((0.19, 0.20, 0.22), 0.45, 0.6, None),
    'koyu': ((0.012, 0.012, 0.015), 0.6, 0.5, None), 'mor': ((0.45, 0.2, 0.9), 0.4, 0.0, (0.65, 0.3, 1.0, 5.0)),
    'cam': ((0.05, 0.02, 0.10), 0.1, 0.0, (0.40, 0.16, 0.80, 0.9)), 'alev': ((0.9, 0.75, 1), 0.5, 0, (0.8, 0.6, 1.0, 5.0)),
    'bell': ((0.02, 0.02, 0.025), 0.45, 0.8, None),
}
K = Kit(PAL)
K.noreno.add('bell')
# gövde: uzun, ince, yüzeyli (6 kesit: üst düz, omuz, dar alt)
K.loft([(-0.46, 0.060, 0.050, 0.040, -0.030, 0), (-0.30, 0.080, 0.060, 0.050, -0.038, 0), (-0.05, 0.088, 0.064, 0.056, -0.040, 0),
        (0.15, 0.078, 0.055, 0.052, -0.036, 0), (0.30, 0.050, 0.034, 0.040, -0.028, 0), (0.43, 0.022, 0.016, 0.024, -0.016, 0), (0.50, 0.006, 0.005, 0.010, -0.006, 0)], 'govde')
# üst plaka (omurga) ve burun kaplaması: panel rengi
K.loft([(-0.40, 0.040, 0.040, 0.0425, 0.039, 0), (0.10, 0.045, 0.045, 0.0575, 0.054, 0), (0.28, 0.030, 0.030, 0.043, 0.040, 0)], 'panel')
# kokpit camı: kabin üstü, öne eğimli iki pano
K.box((0, 0.058, 0.25), (0.05, 0.012, 0.12), 'cam', 0.003)
K.box((0, 0.055, 0.34), (0.034, 0.010, 0.06), 'cam', 0.003)
K.box((0.0, 0.052, 0.18), (0.07, 0.010, 0.018), 'panel', 0.002)         # camın arka çerçevesi
# kanatlar: yarı delta, hafif aşağı eğimli levha + mor kenar şeridi + üst panel çizgileri
for sx in (-1, 1):
    pts = [(sx * 0.07, 0.07), (sx * 0.31, -0.22), (sx * 0.31, -0.34), (sx * 0.10, -0.21), (sx * 0.07, -0.15)]
    if sx < 0:
        pts = pts[::-1]
    K.slab(pts, -0.030, -0.012, 'govde')
    K.slab([(sx * 0.075, 0.062), (sx * 0.305, -0.215), (sx * 0.300, -0.205), (sx * 0.072, 0.07)] if sx > 0 else [(sx * 0.072, 0.07), (sx * 0.300, -0.205), (sx * 0.305, -0.215), (sx * 0.075, 0.062)], -0.0145, -0.0105, 'mor')
    # panel bölmeleri
    K.slab([(sx * 0.12, -0.02), (sx * 0.27, -0.23), (sx * 0.26, -0.25), (sx * 0.11, -0.07)] if sx > 0 else [(sx * 0.11, -0.07), (sx * 0.26, -0.25), (sx * 0.27, -0.23), (sx * 0.12, -0.02)], -0.0125, -0.0095, 'panel')
    K.box((sx * 0.31, -0.02, -0.28), (0.012, 0.03, 0.12), 'koyu', 0.002)        # kanat ucu fin
    # gövde yanı mor çizgi
    K.box((sx * 0.083, 0.012, -0.08), (0.003, 0.004, 0.24), 'mor', 0.0008)
    K.box((sx * 0.060, 0.030, 0.22), (0.003, 0.004, 0.18), 'mor', 0.0008)
# dikey kuyruk (küçük) + arka stabilizer
K.slab([(0.004, -0.15), (0.004, -0.34), (0.004, -0.37), (0.004, -0.2)], 0.040, 0.095, 'govde') if False else None
for xx in (0.0,):
    K.box((0, 0.065, -0.27), (0.008, 0.052, 0.17), 'govde', 0.0015)
    K.box((0, 0.088, -0.32), (0.012, 0.012, 0.07), 'panel', 0.001)
# ikiz motor kovanları (gövde arkası, yanda) + çan + mor-beyaz alev çekirdeği
for sx in (-1, 1):
    K.cyl((sx * 0.045, 0.0, -0.40), (sx * 0.045, 0.0, -0.50), 0.034, 'koyu', 0.030, seg=14)
    K.cyl((sx * 0.045, 0.0, -0.50), (sx * 0.045, 0.0, -0.545), 0.032, 'bell', 0.040, seg=14, cap=False)
    K.cyl((sx * 0.045, 0.0, -0.545), (sx * 0.045, 0.0, -0.552), 0.042, 'panel', seg=14)
    K.cyl((sx * 0.045, 0.0, -0.515), (sx * 0.045, 0.0, -0.52), 0.026, 'alev', seg=14)
    K.cyl((sx * 0.045, 0.0, -0.40), (sx * 0.045, 0.0, -0.41), 0.040, 'panel', seg=14)
# panel çizgileri / gövde detay levhaları (üstte)
for z in (-0.28, -0.12, 0.02):
    K.box((0.0, 0.0555, z), (0.10, 0.003, 0.004), 'koyu', 0.0005)
K.box((0.035, 0.0575, -0.09), (0.06, 0.004, 0.09), 'panel', 0.001)
K.box((-0.035, 0.0575, -0.09), (0.06, 0.004, 0.09), 'panel', 0.001)
K.box((0, 0.058, -0.17), (0.05, 0.006, 0.05), 'koyu', 0.001)            # hava girişi
# yan hava girişleri
for sx in (-1, 1):
    K.box((sx * 0.082, 0.015, 0.06), (0.012, 0.02, 0.07), 'koyu', 0.002)
objs = K.to_blender()
print('KONSEPT poly:', sum(len(o.data.polygons) for o in objs))
K.render(out, {'on_uc_ceyrek': (0.75, -0.85, 0.45), 'arka_uc_ceyrek': (-0.85, 0.95, 0.4), 'yan': (1.5, 0.0, 0.08), 'ust': (0.0, 0.0, 1.6)}, 0.6)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'model.blend'), compress=True)
