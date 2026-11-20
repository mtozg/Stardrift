"""Kalibrasyon referansı (bpy): BİR GLB'yi (ör. onaylı Kaşif, SALT OKUNUR) Blender'a alıp 3 göz kamerasından nötr ışıkta altın referans render'ı üretir.
Kullanım: python qc/silhouette_ref.py <glb> <cameras.json> <çıktı_klasörü> [örnek=64]
Çıktı: <çıktı>/golden_<kamera>.png (RGBA). Üretim hattı dosyalarına ve GLB'ye yazmaz."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy
from core import geo, render as R
from core.paths import load_json
from families.cockpit import build as B

glb, camf, out = sys.argv[1:4]
samples = int(sys.argv[4]) if len(sys.argv) > 4 else 64
geo.reset_scene()
bpy.ops.import_scene.gltf(filepath=glb)
R.rig_neutral()
os.makedirs(out, exist_ok=True)
for c in load_json(camf)['cameras']:
    cam = B._pilot_cam()
    nm = c['name']
    cam.location = {'N1_pilot': (0, 0, 0), 'N2_goz_sol': (-0.07, 0, 0), 'N3_goz_sag_alt': (0.07, 0, -0.04)}[nm]
    R.render(os.path.join(out, 'golden_%s.png' % nm), cam, (c['width'], c['height']), samples, view='Standard', transparent=True, bounces=0)
print('RESULT ok')
