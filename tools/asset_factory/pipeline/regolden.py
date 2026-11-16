"""Altın referansı (nötr ışık) mevcut model.blend'den yeniden render eder; geometri ve tasarım değişmez.
Kullanım: python pipeline/regolden.py <asset_id> <rev> [bounces=0]
Ne zaman: altın referansın ışık modeli değiştiğinde (ör. Şahin r011: dolaylı ışık kapatıldı), 15 dk'lık tam modeli yeniden çalıştırmadan."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy
from core import render as R
from core.paths import work_dir, load_json, save_json

asset_id, rev = sys.argv[1], int(sys.argv[2])
bounces = int(sys.argv[3]) if len(sys.argv) > 3 else 0
d = work_dir(asset_id, rev, 'model')
bpy.ops.wm.open_mainfile(filepath=os.path.join(d, 'model.blend'))
cams = load_json(os.path.join(d, 'cameras.json'))
R.rig_neutral()
for c in cams['cameras']:
    ob = bpy.data.objects.get(c['name']) or (bpy.data.objects.get('Pilot') if c['name'] == 'N1_pilot' else None)
    if ob is None:
        raise SystemExit('kamera bulunamadı: ' + c['name'])
    R.render(os.path.join(d, 'golden_%s.png' % c['name']), ob, (c['width'], c['height']), 128, view='Standard', transparent=True, bounces=bounces)
meta = load_json(os.path.join(d, 'meta.json'))
meta.setdefault('regolden', []).append({'bounces': bounces, 'cameras': [c['name'] for c in cams['cameras']]})
save_json(os.path.join(d, 'meta.json'), meta)
print('RESULT', json.dumps({'regolden': rev, 'bounces': bounces}))
