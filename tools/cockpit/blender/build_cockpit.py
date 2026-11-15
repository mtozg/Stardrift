"""Parametrik kokpit kurucu. Kullanım:  python build_cockpit.py --ship kasif --stage all --out ../out
Aşamalar: canopy (kabuk+cam açıklıkları), all (tam model), render (önizleme görüntüleri), export (GLB)."""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib.common import *
from lib import materials, canopy, render as R

ap = argparse.ArgumentParser(); ap.add_argument('--ship', default='kasif'); ap.add_argument('--stage', default='all'); ap.add_argument('--out', default=os.path.join(COCKPIT, 'out'))
ap.add_argument('--verify', action='store_true'); ap.add_argument('--proj', type=float, default=1.0); ap.add_argument('--export', action='store_true'); ap.add_argument('--tex', type=int, default=2048); ap.add_argument('--bake_samples', type=int, default=24); ap.add_argument('--samples', type=int, default=32); ap.add_argument('--views', default='pilot'); ap.add_argument('--scale', type=float, default=1.0)
args = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])
os.makedirs(args.out, exist_ok=True)
a = load_json('anchors/%s.json' % args.ship); P = load_json('params/%s.json' % args.ship)
clear_scene()
from lib import project
arr = None
if args.proj > 0:
    arr = project.load_drawing(os.path.join(COCKPIT, '..', '..', 'assets', 'img', 'ck_%s.webp' % args.ship), args.out); materials.PROJ['strength'] = args.proj
mats = {'gunmetal': materials.gunmetal(), 'steel': materials.steel(), 'titanium': materials.titanium(), 'aluminum': materials.aluminum(), 'composite': materials.composite(), 'leather': materials.leather(), 'thread': materials.thread(), 'fabric': materials.fabric()}
t0 = time.time(); objs = []
objs += canopy.build(a, P, mats); print('kanopi', round(time.time() - t0, 1), 's')
if args.stage != 'canopy': objs += canopy.build_panels(a, P, mats); print('paneller', round(time.time() - t0, 1), 's')
for stage_mod in ('dash', 'dash_detail', 'side', 'seat', 'detail'):
    try:
        m = __import__('lib.' + stage_mod, fromlist=['build'])
        if args.stage in ('all',): objs += m.build(a, P, mats)
    except ModuleNotFoundError: pass
if arr is not None: print('projeksiyon (köşe, görünür):', project.apply(a, arr, P['proj']))
smooth_by_angle([o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(('Canopy', 'Dash', 'Seat', 'Bezel'))], 40)
if args.verify:
    from lib import verify
    tot, bad, blocked = verify.window_clear(a); print('CAM_TESTI', tot, 'ışın,', bad, 'engelli', blocked)
    print('EKRAN_UYUMU', verify.screen_fit(a))
R.setup_world(); R.lights_default()
print('üçgen', tri_count([o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(('Canopy', 'Dash', 'Seat', 'Detail', 'SCR', 'Bezel'))]))
W = int(1200 * args.scale); Hh = int(492 * args.scale)
if 'pilot' in args.views:
    cam = R.camera(a, 'Pilot'); R.render(os.path.join(args.out, 'kasif_pilot.png'), cam, (W, Hh), args.samples)
for o in bpy.data.objects:
    if o.name in ('Dash_Body','Canopy_Shell'):
        import mathutils; bb=[o.matrix_world @ mathutils.Vector(c) for c in o.bound_box]; print(o.name, 'bbox', [round(min(v[i] for v in bb),2) for i in range(3)], [round(max(v[i] for v in bb),2) for i in range(3)], 'verts', len(o.data.vertices))
if 'oblique' in args.views:
    cam = R.camera(a, 'Obl', loc=g2b((0.55, 0.05, 0.10)), look=g2b((-0.15, -0.30, -1.05)), fovy=70); R.render(os.path.join(args.out, 'kasif_oblique.png'), cam, (int(1200 * args.scale), int(640 * args.scale)), args.samples)
if 'oblique_l' in args.views:
    cam = R.camera(a, 'OblL', loc=g2b((-0.55, 0.05, 0.10)), look=g2b((0.15, -0.30, -1.05)), fovy=70); R.render(os.path.join(args.out, 'kasif_oblique_l.png'), cam, (int(1200 * args.scale), int(640 * args.scale)), args.samples)
if 'low' in args.views:
    cam = R.camera(a, 'Low', loc=g2b((0.0, -0.30, 0.25)), look=g2b((0.0, -0.58, -1.0)), fovy=62); R.render(os.path.join(args.out, 'kasif_low.png'), cam, (int(1200 * args.scale), int(640 * args.scale)), args.samples)
if 'seat' in args.views:
    cam = R.camera(a, 'SeatCam', loc=g2b((0.34, -0.30, -0.02)), look=g2b((-0.02, -0.74, -0.62)), fovy=50); R.render(os.path.join(args.out, 'kasif_seat.png'), cam, (int(1200 * args.scale), int(640 * args.scale)), args.samples)
if 'close' in args.views:
    cam = R.camera(a, 'Close', loc=g2b((0.38, -0.04, -0.28)), look=g2b((-0.05, -0.50, -1.0)), fovy=44); R.render(os.path.join(args.out, 'kasif_close.png'), cam, (int(1200 * args.scale), int(640 * args.scale)), args.samples)
if 'persp' in args.views:
    cam = R.camera(a, 'Persp', loc=(-2.4, -2.2, 1.3), look=(0, 0.7, -0.35), fovy=48); R.render(os.path.join(args.out, 'kasif_persp.png'), cam, (int(900 * args.scale), int(560 * args.scale)), args.samples)
if 'side' in args.views:
    cam = R.camera(a, 'Side', loc=(3.2, 0.2, 0.0), look=(0, 0.2, -0.3), fovy=45); R.render(os.path.join(args.out, 'kasif_side.png'), cam, (int(900 * args.scale), int(560 * args.scale)), args.samples)
if args.stage in ('export', 'all') and args.export:
    from lib import bake
    body = bake.join_body(); print('gizli yüz silindi:', bake.cull_hidden(body)); bake.unwrap(body); print('gövde üçgen', tri_count([body]))
    imgs = bake.bake_all(body, size=args.tex, samples=args.bake_samples)
    orm = bake.compose_orm(imgs, args.tex); bake.rebuild_materials(body, imgs, orm); bake.strip_proj(body)
    sz = bake.export_glb(os.path.join(args.out, 'cockpit_%s.glb' % args.ship)); print('GLB bayt', sz, round(sz / 1048576, 2), 'MB')
    for k, im in list(imgs.items()) + [('orm', orm)]:
        im.filepath_raw = os.path.join(args.out, 'tex_%s_%s.png' % (args.ship, k)); im.file_format = 'PNG'; im.save()
print('bitti', round(time.time() - t0, 1), 's')
