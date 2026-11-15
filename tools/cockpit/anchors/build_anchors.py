#!/usr/bin/env python3
"""Onaylı kokpit çiziminden Blender modeli için bağlayıcı değerleri çıkarır.
Çıktı: anchors/<gemi>.json  (kamera iç parametreleri, cam çokgenleri, ekran düzlemleri, lambalar)
Kullanım: python build_anchors.py kasif
Koordinatlar: oyunun 1600x656 referans uzayı (piksel, y aşağı). Eğri/üst-sol köşe sırası [TL,TR,BR,BL].
Pilot kamerası: dikey görüş 74°, asal nokta (800, 239.5) — oyunun rehber kamerasıyla aynı."""
import json, os, re, sys
import numpy as np
from PIL import Image
import scipy.ndimage as ndi
from scipy.optimize import least_squares
from skimage.measure import find_contours, approximate_polygon

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
ship = sys.argv[1] if len(sys.argv) > 1 else 'kasif'
IW, IH = 1600, 656
FOVY = 74.0
F = (IH / 2) / np.tan(np.radians(FOVY / 2))      # piksel odak uzaklığı (1600x656 uzayında)
CX, CY = 800.0, 239.5                             # asal nokta (rehber kamerası: bakış merkezi kayık)
WIDTH = {'kasif': [0.50, 0.80, 0.50]}[ship]
PRIOR = {'kasif': [(0.42, 0.20), (0.0, 0.20), (-0.42, 0.20)]}[ship]   # (yaw, pitch) öncülleri: yan ekranlar pilota doğru döner, hepsi hafif geriye yatık       # ekranların gerçek genişliği (metre): sol, orta, sağ

def ray(u, v):
    d = np.array([(u - CX) / F, -(v - CY) / F, -1.0]); return d / np.linalg.norm(d)

src = open(os.path.join(ROOT, 'js', 'game.js'), encoding='utf-8').read()
ckp = json.loads(re.search(r'const CKP = (\{.*?\});\n', src).group(1))[ship]
img = Image.open(os.path.join(ROOT, 'assets', 'img', 'ck_%s.webp' % ship)).convert('RGBA')
al = np.asarray(img)[..., 3].astype(np.float32) / 255
S = img.size[0] / IW
hole = al < 0.5
lab, n = ndi.label(hole)
windows = []

# --- cam açıklıkları: büyük delikler (ekran oyukları hariç)
def centroid(m): ys, xs = np.nonzero(m); return xs.mean() / S, ys.mean() / S
for k in range(1, n + 1):
    m = lab == k
    if m.sum() < 15000: continue
    cx, cy = centroid(m)
    if cy > 330 and 380 < cx < 1230: continue                 # ekran oyukları
    cs = find_contours(np.pad(m, 1).astype(np.float32), 0.5)
    c = max(cs, key=len) - 1
    poly = approximate_polygon(c, tolerance=2.2 * S)
    pts = [[float(x / S), float(y / S)] for y, x in poly[:-1]]
    pts = [[(-320 if x < 4 else IW + 320 if x > IW - 4 else x), (-320 if y < 4 else y)] for x, y in pts]
    windows.append({'poly': pts, 'cx': cx, 'cy': cy, 'area': float(m.sum() / S / S)})
windows.sort(key=lambda w: w['cx'])

# --- ekran düzlemleri: dörtgen köşelerinden gerçek dikdörtgen düzlemi çöz
def plane_pts(R, n, d):
    return np.array([r * (d / (n @ r)) for r in R])

def center_screen(q, width, pit):
    """Orta ekran: hafif geriye yatık düzlem; mesafe fiziksel genişliğe göre ölçeklenir."""
    R = [ray(*p) for p in q]
    n = np.array([0.0, np.sin(pit), np.cos(pit)])
    P1 = plane_pts(R, n, -1.0); P = P1 * (width / np.linalg.norm(P1[1] - P1[0]))
    return P, n

def side_screen(q, inner_idx, outer_idx, pin_z, wrap, pit):
    """Yan ekran: iç üst köşe orta ekranın kenarıyla aynı derinliğe (pin_z) sabitlenir. Düzlemin yaw açısı, DIŞ kenarın iç kenardan `wrap`
    metre daha yakın (pilota doğru kıvrılan, çevreleyen dashboard) olmasını sağlar; böylece ekran kanopi kabuğunun önünde kalır.
    Köşeler pilot kamerasının ışınları üzerinde kaldığından CKP izdüşümü birebir korunur."""
    R = [ray(*p) for p in q]
    pin = R[inner_idx] * (pin_z / R[inner_idx][2]); best = None
    for yaw in np.linspace(-1.25, 1.25, 1001):
        n = np.array([np.sin(yaw) * np.cos(pit), np.sin(pit), np.cos(yaw) * np.cos(pit)])
        if n[2] < 0.2 or abs(n @ R[inner_idx]) < 1e-3: continue
        P = plane_pts(R, n, n @ pin)
        if np.any(P[:, 2] > -0.3): continue
        zo = np.mean([P[k][2] for k in outer_idx]); sc = abs(zo - (pin_z + wrap))
        if best is None or sc < best[0]: best = (sc, P, n)
    return best[1], best[2]

PIT = 0.20
WRAP = 0.14   # dış kenar iç kenardan bu kadar pilota yakın (m)
Pc, nc = center_screen(ckp['q'][1], WIDTH[1], PIT)
PL, nL = side_screen(ckp['q'][0], 1, (0, 3), Pc[0][2], WRAP, PIT)
PR, nR = side_screen(ckp['q'][2], 0, (1, 2), Pc[1][2], WRAP, PIT)
screens = []
for nm, q, P, n in (('SCR_SYS', ckp['q'][0], PL, nL), ('SCR_RADAR', ckp['q'][1], Pc, nc), ('SCR_HULL', ckp['q'][2], PR, nR)):
    screens.append({'name': nm, 'ckp': q, 'corners3d': P.round(4).tolist(), 'normal': n.round(4).tolist(), 'center': P.mean(0).round(4).tolist(),
                    'width': float(np.linalg.norm(P[1] - P[0])), 'height': float(np.linalg.norm(P[3] - P[0])), 'fit_cost': 0.0})
lamps = [{'ckp': l, 'dir': ray(*l).round(5).tolist()} for l in ckp.get('lamps', [])]
out = {'ship': ship, 'image_space': [IW, IH], 'camera': {'fovy_deg': FOVY, 'focal_px': float(F), 'principal': [CX, CY], 'eye': [0, 0, 0], 'forward': [0, 0, -1], 'up': [0, 1, 0]},
       'windows': windows, 'screens': screens, 'lamps': lamps}
json.dump(out, open(os.path.join(os.path.dirname(__file__), '%s.json' % ship), 'w'), indent=1)
print('pencere', len(windows), [len(w['poly']) for w in windows], [round(w['area']) for w in windows])
for s in screens: print(s['name'], 'merkez', s['center'], 'genişlik %.2f yükseklik %.2f maliyet %.5f' % (s['width'], s['height'], s['fit_cost']), 'normal', s['normal'])
