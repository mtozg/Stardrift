#!/usr/bin/env python3
"""Stardrift Asset Factory — tek giriş noktası.

  python factory.py model    <id> [--fast]        A–C: kurulum + lookdev + altın referans render
  python factory.py review   <id>                 Kapı 1 sayfası
  python factory.py approve  <id> --gate visual|tech --by "<kim>" --note "<neden>" [--accept-warn id,id]
  python factory.py prepare  <id> [--fast]        D: oyuna hazırlık (Kapı 1 onayı gerekir)
  python factory.py qc       <id>                 E: teknik doğrulama (L2–L4)
  python factory.py deliver  <id>                 F: teslim paketi (Kapı 2 onayı gerekir)
  python factory.py status

Kurallar: oyun dosyalarına yazılmaz (yalnızca okunur); onaylar registry.json'a kaydedilir; gerçek varlıklar yalnızca
kullanıcı onayıyla kapıdan geçer (Claude yalnızca spec'inde test_asset=true olan Faz 0 test nesnelerini onaylayabilir)."""
import argparse, datetime, glob, json, os, shutil, socket, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import registry
from core.paths import FACTORY, GAME_ROOT, DELIVERIES, QC, load_json, save_json, load_spec, work_dir, file_hash, json_hash

PY = sys.executable


def sh(cmd, log=None, cwd=FACTORY):
    t0 = time.time()
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if log:
        with open(log, 'a', encoding='utf-8') as f:
            f.write('$ %s\n%s\n%s\n' % (' '.join(cmd), p.stdout, p.stderr))
    res = None
    for line in p.stdout.splitlines():
        if line.startswith('RESULT '):
            res = json.loads(line[7:])
    if p.returncode != 0:
        tail = '\n'.join((p.stdout + p.stderr).splitlines()[-25:])
        raise SystemExit('HATA (%s):\n%s' % (' '.join(cmd[:3]), tail))
    return res, time.time() - t0


def commit():
    try:
        return subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=FACTORY, capture_output=True, text=True).stdout.strip()
    except Exception:
        return '?'


def check_forbidden_refs(spec):
    """STANDARDS.md §0.1: kokpit/oyuncu gemisi tariflerinde eski 2B ve paralaks kokpit kaynakları yasak."""
    fr = load_json(os.path.join(QC, 'rules.json')).get('forbidden_references', {})
    if spec.get('family') not in fr.get('families', []):
        return
    txt = json.dumps(spec.get('reference') or {}, ensure_ascii=False) + json.dumps(spec.get('params', {}), ensure_ascii=False)
    import re
    bad = [p for p in fr.get('patterns', []) if re.search(p, txt)]
    if bad:
        raise SystemExit('RED: tarif eski kokpit kaynaklarına referans veriyor %s (STANDARDS.md §0.1)' % bad)


def cmd_model(a):
    spec = load_spec(a.id)
    check_forbidden_refs(spec)
    reg = registry.get(a.id, create=True)
    production = spec.get('profile') == 'PRODUCTION' and reg['state'] in ('visual_approved', 'prepared', 'qc_fail', 'qc_pass')
    if production:
        # PRODUCTION ayrıntı modeli: Kapı 1 onayına dayanır; onaylı PREVIEW revizyonu korunur, yeni revizyon açılır, onay durumu kalır
        base_rev = reg['rev']
        registry.update(a.id, rev=base_rev + 1, timings={})
        registry.transition(a.id, 'visual_approved', 'PRODUCTION modeli r%03d (Kapı 1 onaylı r%03d tasarımına dayanır)' % (base_rev + 1, base_rev))
        reg = registry.get(a.id)
    elif reg['state'] not in ('draft', 'modeled'):
        raise SystemExit('model yalnızca draft/modeled durumunda yeniden çalışır (şu an %s); yeni revizyon gerekir' % reg['state'])
    rev = reg['rev']
    log = os.path.join(work_dir(a.id, rev), 'factory.log')
    res, dt = sh([PY, 'pipeline/model.py', a.id, str(rev)] + (['--fast'] if a.fast else []), log)
    registry.record_timing(a.id, 'model', dt)
    registry.update(a.id, geometry_hash=res['geometry_hash'], spec_hash=json_hash(spec), fast=bool(a.fast))
    if reg['state'] == 'draft':
        registry.transition(a.id, 'modeled', 'model + lookdev render')
    print('MODEL tamam: %.1f s, %d üçgen (kaynak), hash %s…' % (dt, res['tris_source'], res['geometry_hash'][:12]))
    print('RESULT', json.dumps({'stage': 'model', 'seconds': round(dt, 1), **res}))


def cmd_review(a):
    reg = registry.require(a.id, 'modeled', 'visual_approved')
    d = work_dir(a.id, reg['rev'], 'model')
    spec = load_spec(a.id)
    imgs = [i for i in ['hero.png', 'hero_rear.png', 'closeup.png', 'ortho_6.png', 'thumb_128.png'] if os.path.exists(os.path.join(d, i))] or \
        sorted(f for f in os.listdir(d) if f.endswith('.png'))
    ref = spec.get('reference') or {}
    body = ''.join('<figure><img src="%s"><figcaption>%s</figcaption></figure>' % (i, i) for i in imgs)
    refs = ''.join('<figure><img src="%s"><figcaption>referans: %s</figcaption></figure>' % (os.path.relpath(os.path.join(GAME_ROOT, v), d), v) for v in ref.values() if isinstance(v, str))
    open(os.path.join(d, 'review.html'), 'w', encoding='utf-8').write(
        '<!doctype html><meta charset="utf-8"><title>Kapı 1 — %s</title><style>body{background:#0d1118;color:#dbe2ee;font:14px system-ui;margin:0;padding:16px}'
        'figure{margin:0 0 16px}img{max-width:100%%;border-radius:8px}</style><h1>Kapı 1 — görsel inceleme: %s</h1>%s%s' % (a.id, a.id, refs or '<p>Referans görsel yok (test nesnesi).</p>', body))
    print('RESULT', json.dumps({'review': os.path.join(d, 'review.html')}))


def cmd_approve(a):
    spec = load_spec(a.id)
    if a.by.lower().startswith('claude') and not spec.get('test_asset'):
        raise SystemExit('ONAY REDDİ: gerçek varlıklar yalnızca kullanıcı onayıyla kapıdan geçer')
    registry.approve(a.id, a.gate, a.by, a.note, (a.accept_warn or '').split(',') if a.accept_warn else [])
    print('RESULT', json.dumps({'approved': a.gate, 'state': registry.get(a.id)['state']}))


def cmd_prepare(a):
    reg = registry.require(a.id, 'visual_approved', 'prepared', 'qc_fail', 'qc_pass')
    rev = reg['rev']
    log = os.path.join(work_dir(a.id, rev), 'factory.log')
    res, dt = sh([PY, 'pipeline/prepare.py', a.id, str(rev)] + (['--fast'] if a.fast else []), log)
    registry.record_timing(a.id, 'prepare', dt)
    registry.transition(a.id, 'prepared', 'GLB üretildi')
    print('HAZIRLIK tamam: %.1f s, LOD üçgen %s, GLB %.1f KB' % (dt, res['tris_lod'], res['glb_bytes'] / 1024))
    print('RESULT', json.dumps({'stage': 'prepare', 'seconds': round(dt, 1), **res}, ensure_ascii=False))


class Server:
    """Oyun kökünü (salt okunur) yerel olarak sunar: Three sayfası oyunun /vendor/three.min.js dosyasını kullanır."""
    def __enter__(self):
        s = socket.socket()
        s.bind(('127.0.0.1', 0))
        self.port = s.getsockname()[1]
        s.close()
        self.p = subprocess.Popen([PY, '-m', 'http.server', str(self.port), '--bind', '127.0.0.1'], cwd=GAME_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(50):
            try:
                socket.create_connection(('127.0.0.1', self.port), 0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        self.url = 'http://127.0.0.1:%d' % self.port
        return self

    def __exit__(self, *e):
        self.p.terminate()
        self.p.wait(5)


def cmd_qc(a):
    reg = registry.require(a.id, 'prepared', 'qc_fail', 'qc_pass')
    rev = reg['rev']
    spec = load_spec(a.id)
    budgets, rules = load_json(os.path.join(QC, 'budgets.json')), load_json(os.path.join(QC, 'rules.json'))
    mdir, pdir, qdir = (work_dir(a.id, rev, s) for s in ('model', 'prepare', 'qc'))
    log = os.path.join(work_dir(a.id, rev), 'factory.log')
    pmeta, mmeta = load_json(os.path.join(pdir, 'meta.json')), load_json(os.path.join(mdir, 'meta.json'))
    glb = pmeta['glb']
    fast = pmeta.get('fast')
    T, items = {}, []
    add = lambda tid, layer, st, value=None, limit=None, note='': items.append({'id': tid, 'layer': layer, 'status': st, 'value': value, 'limit': limit, 'note': note})

    # L2-a: Khronos validator
    vres, T['qc_validator'] = sh(['node', 'qc/validate.js', glb, os.path.join(qdir, 'validator.json')], log)
    add('gltf.validator_errors', 'L2', 'PASS' if vres['errors'] == 0 else 'FAIL', vres['errors'], 0, 'Khronos glTF Validator %s' % vres['validator'])
    vj = load_json(os.path.join(qdir, 'validator.json'))
    codes = sorted({m['code'] for m in vj['issues']['messages'] if m['severity'] == 1})
    add('gltf.validator_warnings', 'L2', 'WARN' if vres['warnings'] else 'PASS', vres['warnings'], 0, ', '.join(codes))

    # L2-b: Blender geometri testleri (GLB yeniden içe aktarılarak)
    interior = spec.get('prepare', {}).get('cull') == 'interior'
    bres, T['qc_blender'] = sh([PY, 'qc/blender_checks.py', glb, str(pmeta['texture_size']), os.path.join(qdir, 'blender_checks.json'), 'interior' if interior else 'exterior'], log)
    if interior:
        for nm, k in bres.get('screens_visible', {}).items():
            add('cockpit.screen_visible.%s' % nm, 'L2', 'PASS' if k == 5 else 'FAIL', '%d/5' % k, '5/5', 'pilot gözünden merkez + 4 köşe ışını, ekrandan önce engel yok')
        add('cockpit.glass_ratio', 'L2', 'PASS', bres['glass_ratio'], None, 'pilot çerçevesinde dışarının görünen oranı (%%); Kaşif 50,7')
        add('cockpit.hud_zone_block', 'L2', 'PASS' if bres['hud_zone_block'] <= rules.get('hud_zone_block_warn', 10) else 'WARN', bres['hud_zone_block'], rules.get('hud_zone_block_warn', 10), 'orta HUD bölgesi engeli (%%); Kaşif 9,3')
    add('geom.zero_area_faces', 'L2', 'PASS' if bres['zero_area_faces'] == 0 else 'FAIL', bres['zero_area_faces'], 0)
    add('geom.loose_verts', 'L2', 'PASS' if bres['loose_verts'] == 0 else 'FAIL', bres['loose_verts'], 0)
    add('geom.backface_visible', 'L2', 'PASS' if bres['backface_visible'] <= rules['backface_visible_fail'] else 'FAIL', bres['backface_visible'], rules['backface_visible_fail'],
        '%d %s ışın; delik + ters normal' % (bres['backface_samples'], 'pilot gözünden' if interior else 'dış'))
    add('uv.overlap', 'L2', 'PASS' if bres['uv_overlap'] <= rules['uv_overlap_fail'] else 'FAIL', bres['uv_overlap'], rules['uv_overlap_fail'], 'unique modda ada çakışması')
    add('uv.out_of_bounds', 'L2', 'PASS' if bres['faces_out_of_bounds'] == 0 else 'FAIL', bres['faces_out_of_bounds'], 0)
    full = budgets['classes'][spec['class']].get('tex_size', pmeta['texture_size'])
    tgt = rules['texel_target'].get(spec['class'], 256) * pmeta['texture_size'] / full
    dev = abs(bres['texel_px_per_m_median'] - tgt) / tgt
    add('uv.texel_density', 'L2', 'FAIL' if dev > rules['texel_tol_fail'] else ('WARN' if dev > rules['texel_tol_warn'] else 'PASS'),
        bres['texel_px_per_m_median'], round(tgt, 1), 'px/m medyan; hedef ±%d%% (WARN ±%d%%)%s; UV doluluk %.0f%%' % (
            rules['texel_tol_fail'] * 100, rules['texel_tol_warn'] * 100, ' — hızlı mod, hedef doku boyutuna göre ölçeklendi' if fast else '', bres['uv_coverage'] * 100))

    # L2-c: tekrar üretilebilirlik (aynı spec + seed → aynı geometri)
    hres, T['qc_repro'] = sh([PY, 'pipeline/model.py', a.id, str(rev), '--hash-only', os.path.join(qdir, 'repro.json')], log)
    add('repro.geometry_hash', 'L2', 'PASS' if hres['geometry_hash'] == mmeta['geometry_hash'] else 'FAIL', hres['geometry_hash'][:16], mmeta['geometry_hash'][:16], 'ayrı süreçte yeniden kurulum')

    # L2-d: referans siluet
    if spec.get('reference'):
        add('ref.silhouette_iou', 'L2', 'SKIP', None, rules['silhouette_iou']['prototype'], 'Faz 1+ (referans çizim karşılaştırması)')
    else:
        add('ref.silhouette_iou', 'L2', 'SKIP', None, rules['silhouette_iou']['prototype'], 'referans çizim yok (test nesnesi)')
    add('mat.emit_area', 'L2', 'PASS' if mmeta['emit_area_ratio'] <= rules['emit_area_max'] else 'WARN', mmeta['emit_area_ratio'], rules['emit_area_max'], 'emisyonlu yüzey oranı')

    # L3 + L4: Three r128
    cams = load_json(os.path.join(mdir, 'cameras.json'))
    rel = '/' + os.path.relpath(glb, GAME_ROOT).replace(os.sep, '/')
    counts = [1] if spec['family'] == 'cockpit' else [1, 12, 40]      # kokpit tek örnek (oyuncunun kendi kokpiti)
    cfg = {'name': a.id, 'glb': rel, 'cameras': cams['cameras'], 'neutral': cams['neutral'], 'perf': {'width': 1200, 'height': 750, 'counts': counts, 'frames': 60}}
    save_json(os.path.join(qdir, 'cfg.json'), cfg)
    save_json(os.path.join(qdir, 'cfg_perf.json'), dict(cfg, only_perf=True, perf=dict(cfg['perf'], frames=40)))
    devices = 'iPad Pro 11 landscape,iPhone 13 landscape,Pixel 7 landscape'
    with Server() as srv:
        cu = '/' + os.path.relpath(os.path.join(qdir, 'cfg.json'), GAME_ROOT).replace(os.sep, '/')
        pu = '/' + os.path.relpath(os.path.join(qdir, 'cfg_perf.json'), GAME_ROOT).replace(os.sep, '/')
        tres, T['qc_three'] = sh(['node', 'qc/viewer/run_check.js', srv.url, cu, qdir, devices, pu], log)
    TR = load_json(os.path.join(qdir, 'three_result.json'))
    add('three.load', 'L3', 'PASS' if not TR.get('error') and not TR.get('page_errors') else 'FAIL', TR.get('load_ms'), None, TR.get('error') or '; '.join(TR.get('page_errors', [])) or 'yükleme ms (swiftshader)')
    insp = TR.get('inspect', {})
    add('three.materials', 'L3', 'PASS' if all(m['type'] == 'MeshStandardMaterial' and m['side'] == 0 for m in insp.get('materials', {}).values()) else 'FAIL',
        {k: m['type'] for k, m in insp.get('materials', {}).items()}, 'MeshStandardMaterial, FrontSide')
    import math as _m
    for sk in insp.get('sockets', []):
        want = (sk.get('extras') or {}).get('dir')
        if not want:
            add('contract.socket_dir.%s' % sk['name'], 'L3', 'FAIL', sk['dir'], None, 'extras.dir yok: beklenen yön doğrulanamıyor')
            continue
        dot = sum(a * b for a, b in zip(sk['dir'], want)) / (max(1e-9, _m.sqrt(sum(a * a for a in want))))
        ang = _m.degrees(_m.acos(max(-1.0, min(1.0, dot))))
        add('contract.socket_dir.%s' % sk['name'], 'L3', 'PASS' if ang <= 1.0 else 'FAIL', sk['dir'], want, 'Three r128\'de okunan yön (düğüm −Z) ile tarifteki yön arası %.1f°' % ang)
    add('three.calls_lod0', 'L3', 'PASS' if TR['info']['calls'] <= budgets['classes'][spec['class']]['calls'] else 'FAIL', TR['info']['calls'], budgets['classes'][spec['class']]['calls'], 'renderer.info')
    add('three.normal_side', 'L3', 'PASS' if TR['normal_side_diff'] <= rules['normal_side_diff_fail'] else 'FAIL', TR['normal_side_diff'], rules['normal_side_diff_fail'],
        'FrontSide⟷DoubleSide, erozyon sonrası (ham %.3f%%)' % (TR['normal_side_diff_raw'] * 100))
    for l in TR['lod']:
        add('three.lod%d_silhouette' % l['lod'], 'L3', 'PASS' if l['silhouette_diff'] <= rules['lod_silhouette_fail'] else 'FAIL', l['silhouette_diff'], rules['lod_silhouette_fail'],
            'nesne ~%d px yükseklikte LOD0 ile maske farkı' % l['object_px'])
    sys.path.insert(0, QC)
    from qc import visual
    from PIL import Image
    tvg, th = {}, rules['three_vs_golden']
    for c in cams['cameras']:
        k = c['name']
        g, t = os.path.join(mdir, 'golden_%s.png' % k), os.path.join(qdir, 'three_%s.png' % k)
        dpath = os.path.join(qdir, 'diff_%s.png' % k)
        m = visual.compare(g, t, dpath)
        tvg[k] = m
        ok = m['lum_diff'] <= th['lum_diff_fail'] and m['deltaE_mean'] <= th['deltaE_fail'] and m['silhouette_diff'] <= th['silhouette_fail']
        add('three.fidelity.%s' % k, 'L3', 'PASS' if ok else 'FAIL', {'lum': m['lum_diff'], 'dE': m['deltaE_mean'], 'sil': m['silhouette_diff']},
            {'lum': th['lum_diff_fail'], 'dE': th['deltaE_fail'], 'sil': th['silhouette_fail']}, 'Cycles nötr ⟷ Three r128')
        sheet = Image.new('RGB', (c['width'] * 3, c['height']), (20, 22, 30))
        for i, pth in enumerate((g, t)):
            im = Image.open(pth).convert('RGBA')
            bg = Image.new('RGBA', im.size, (20, 22, 30, 255))
            bg.alpha_composite(im)
            sheet.paste(bg.convert('RGB'), (i * c['width'], 0))
        sheet.paste(Image.open(dpath).convert('RGB'), (2 * c['width'], 0))
        sheet.save(os.path.join(qdir, 'cmp_%s.png' % k))
    # L4: performans (göreli; ilk ölçüm temel değerdir)
    prev = reg.get('perf_baseline')
    perf = {'masaüstü 1200×750': {'perf': TR.get('perf')}, **TR.get('devices', {})}
    for dev, d in perf.items():
        for p in d.get('perf') or []:
            key = '%s|%d' % (dev, p['n'])
            v = p[rules['perf_metric']]
            if prev and key in prev:
                r = (v - prev[key]) / prev[key]
                big = (v - prev[key]) > rules['perf_abs_floor_ms']      # küçük sürelerde yazılım GPU gürültüsünü ele
                st = 'FAIL' if (r > rules['perf_regress_fail'] and big) else ('WARN' if (r > rules['perf_regress_warn'] and big) else 'PASS')
                if p['n'] < rules.get('perf_gate_min_n', 1):
                    st = 'PASS'      # bilgi amaçlı: n küçükken ölçüm varlık maliyetini değil sabit gideri yansıtır
                add('perf.%s.n%d' % (dev, p['n']), 'L4', st, v, prev[key], '%s, temel ölçüme göre %+.0f%% (eşik: göreli ve > %.1f ms)' % (rules['perf_metric'], r * 100, rules['perf_abs_floor_ms']))
            else:
                add('perf.%s.n%d' % (dev, p['n']), 'L4', 'PASS', v, None, '%s; temel ölçüm (karşılaştırılacak önceki revizyon yok)' % rules['perf_metric'])
    if not prev:
        registry.update(a.id, perf_baseline={'%s|%d' % (dev, p['n']): p[rules['perf_metric']] for dev, d in perf.items() for p in (d.get('perf') or [])})
    add('perf.device_real', 'L4', 'SKIP', None, None, 'gerçek cihaz ölçümü bench.html ile elle yapılır')

    # L2 GLB statik testleri
    from qc import glb_checks
    gitems, stats = glb_checks.run(glb, dict(spec, _fast=fast), budgets, rules)
    items = gitems + items
    registry.record_timing(a.id, 'qc', sum(T.values()))
    reg = registry.get(a.id)
    summ = __import__('qc.report', fromlist=['x']).summarize(items)
    verdict = 'FAIL' if summ['FAIL'] else ('WARN' if summ['WARN'] else 'PASS')
    R = {'asset_id': a.id, 'rev': rev, 'time': datetime.datetime.now().isoformat(timespec='seconds'), 'factory_commit': commit(),
         'blender': mmeta.get('blender'), 'fast': fast, 'verdict': verdict, 'summary': summ, 'stats': stats,
         'three': {'info': TR['info'], 'load_ms': TR['load_ms'], 'tex_gpu_bytes': TR['tex_gpu_bytes'], 'inspect': insp},
         'three_vs_golden': tvg, 'perf': perf, 'prepare': {k: pmeta[k] for k in ('tris_lod', 'culled_faces', 'tris_before_cull', 'tris_after_cull', 'uv', 'texture_recompress', 'glb_bytes_blender', 'glb_bytes')},
         'timings': {**reg.get('timings', {}), **{k: round(v, 1) for k, v in T.items()}}, 'items': items}
    # göreli görsel yolları (rapor work/…/qc/ içinde)
    imgs = {'hero': '../model/hero.png', 'hero_rear': '../model/hero_rear.png', 'closeup': '../model/closeup.png', 'ortho_6': '../model/ortho_6.png',
            'thumb': '../model/thumb_128.png', 'normal_side_diff': 'three_normal_side_diff.png', **{'cmp_' + k: 'cmp_%s.png' % k for k in tvg}}
    save_json(os.path.join(qdir, 'qc_report.json'), R)
    from qc.report import html_report
    html_report(R, os.path.join(qdir, 'qc_report.html'), imgs)
    registry.transition(a.id, 'qc_pass' if verdict != 'FAIL' else 'qc_fail', 'QC %s (%d PASS, %d WARN, %d FAIL)' % (verdict, summ['PASS'], summ['WARN'], summ['FAIL']))
    print('QC %s — PASS %d, WARN %d, FAIL %d, SKIP %d' % (verdict, summ['PASS'], summ['WARN'], summ['FAIL'], summ.get('SKIP', 0)))
    for it in items:
        if it['status'] in ('FAIL', 'WARN'):
            print('  %s %s = %s (sınır %s) %s' % (it['status'], it['id'], it['value'], it['limit'], it['note']))
    print('RESULT', json.dumps({'stage': 'qc', 'verdict': verdict, **summ, 'report': os.path.join(qdir, 'qc_report.html')}))


def cmd_deliver(a):
    reg = registry.require(a.id, 'tech_approved', 'delivered')
    rev = reg['rev']
    spec = load_spec(a.id)
    mdir, pdir, qdir = (work_dir(a.id, rev, s) for s in ('model', 'prepare', 'qc'))
    R = load_json(os.path.join(qdir, 'qc_report.json'))
    pmeta = load_json(os.path.join(pdir, 'meta.json'))
    out = os.path.join(DELIVERIES, a.id, 'r%03d' % rev)
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, 'textures'))
    os.makedirs(os.path.join(out, 'preview'))
    glb_name = 'sd_%s_r%03d.glb' % (a.id, rev)
    shutil.copy(pmeta['glb'], os.path.join(out, glb_name))
    # GLB'deki son dokuları (oyunun göreceği hâliyle) ayrıca çıkar
    from qc import glb_checks
    j, bin_, _ = glb_checks.read_glb(pmeta['glb'])
    texfiles = []
    for i, im in enumerate(j.get('images', [])):
        bv = j['bufferViews'][im['bufferView']]
        fn = im.get('name', 'img%d' % i) + '.webp'
        open(os.path.join(out, 'textures', fn), 'wb').write(bin_[bv.get('byteOffset', 0): bv.get('byteOffset', 0) + bv['byteLength']])
        texfiles.append('textures/' + fn)
    prev = {}
    for k, src in (('hero.png', 'model/hero.png'), ('hero_rear.png', 'model/hero_rear.png'), ('closeup.png', 'model/closeup.png'), ('ortho_6.png', 'model/ortho_6.png'),
                   ('thumb_128.png', 'model/thumb_128.png'), ('normal_side_diff.png', 'qc/three_normal_side_diff.png')):
        shutil.copy(os.path.join(work_dir(a.id, rev), src), os.path.join(out, 'preview', k))
        prev[k.split('.')[0]] = 'preview/' + k
    for c in R['three_vs_golden']:
        shutil.copy(os.path.join(qdir, 'cmp_%s.png' % c), os.path.join(out, 'preview', 'three_vs_blender_%s.png' % c))
        prev['cmp_' + c] = 'preview/three_vs_blender_%s.png' % c
    shutil.copy(os.path.join(qdir, 'qc_report.json'), out)
    from qc.report import html_report
    html_report(R, os.path.join(out, 'qc_report.html'), {'hero': prev['hero'], 'hero_rear': prev['hero_rear'], 'closeup': prev['closeup'], 'ortho_6': prev['ortho_6'],
                                                          'thumb': prev['thumb_128'], 'normal_side_diff': prev['normal_side_diff'], **{k: v for k, v in prev.items() if k.startswith('cmp_')}})
    st = R['stats']
    socks = R['three']['inspect'].get('sockets', [])
    manifest = {'id': a.id, 'rev': rev, 'glb': glb_name, 'glb_sha256': file_hash(os.path.join(out, glb_name)), 'glb_bytes': st['glb_bytes'],
                'class': spec['class'], 'family': spec['family'], 'test_asset': bool(spec.get('test_asset')), 'units': 'm', 'forward': '-Z', 'up': '+Y',
                'length_m': st['length_m'], 'bounds_min': st['bounds_min'], 'bounds_max': st['bounds_max'], 'tris': st['tris'], 'calls_lod0': st['calls_lod0'],
                'materials': list(R['three']['inspect'].get('materials', {}).keys()), 'textures': texfiles, 'tex_gpu_bytes_est': st['tex_gpu_bytes_est'],
                'sockets': socks, 'qc': {'verdict': R['verdict'], **R['summary']}, 'contract': 'GEÇİCİ — contracts/game_contract.md bekleniyor'}
    save_json(os.path.join(out, 'manifest.json'), manifest)
    save_json(os.path.join(out, 'source.json'), {'spec': spec, 'seed': spec.get('seed'), 'spec_hash': json_hash(spec), 'geometry_hash': reg.get('geometry_hash'),
                                                  'factory_commit': commit(), 'blender': R.get('blender'), 'library_materials': spec.get('materials'),
                                                  'rebuild': 'python factory.py model %s && python factory.py prepare %s' % (a.id, a.id)})
    tex_rows = '\n'.join('| %s | %s | %s KB |' % (k, '×'.join(map(str, v['size'])), v['kb']) for k, v in st['textures'].items())
    sock_rows = '\n'.join('| `%s` | %s | %s | %s |' % (s['name'], s['position'], s['dir'], s['extras'].get('purpose', '')) for s in socks)
    t = R['timings']
    open(os.path.join(out, 'spec_sheet.md'), 'w', encoding='utf-8').write("""# %(id)s r%(rev)03d — teknik özellikler

%(test)s

| Özellik | Değer |
|---|---|
| Aile / sınıf | %(fam)s / %(cls)s |
| Boy (Z) | %(len).3f m |
| Sınır kutusu (oyun uzayı) | %(bmin)s → %(bmax)s |
| Üçgen LOD0 / LOD1 / LOD2 | %(tris)s |
| Draw call (LOD0) | %(calls)d |
| Malzeme | %(mats)s |
| GLB | %(kb).1f KB |
| GPU doku belleği (tahmin) | %(gpu).2f MB |
| QC | %(verdict)s (PASS %(p)d · WARN %(w)d · FAIL %(f)d · SKIP %(s)d) |
| Üretim süresi | model %(tm)s s · hazırlık %(tp)s s · QC %(tq)s s |

## Dokular (WebP, GLB'ye gömülü; `textures/` içinde ayrı kopya)
| Doku | Boyut | Dosya |
|---|---|---|
%(tex)s

## Soketler
| Ad | Konum (m) | Yön | Amaç |
|---|---|---|---|
%(socks)s
""" % dict(id=a.id, rev=rev, test='> **Test nesnesi** — Faz 0 hattı doğrulaması içindir, oyuna girmez.' if spec.get('test_asset') else '',
           fam=spec['family'], cls=spec['class'], len=st['length_m'], bmin=st['bounds_min'], bmax=st['bounds_max'], tris=' / '.join(map(str, st['tris'])),
           calls=st['calls_lod0'], mats=', '.join(manifest['materials']), kb=st['glb_bytes'] / 1024, gpu=st['tex_gpu_bytes_est'] / 1048576,
           verdict=R['verdict'], p=R['summary']['PASS'], w=R['summary']['WARN'], f=R['summary']['FAIL'], s=R['summary'].get('SKIP', 0),
           tm=t.get('model'), tp=t.get('prepare'), tq=t.get('qc'), tex=tex_rows, socks=sock_rows))
    open(os.path.join(out, 'integration.md'), 'w', encoding='utf-8').write("""# %s r%03d — entegrasyon notu

> **GEÇİCİ.** Oyunun koordinat, ölçek, ışık ve yükleyici sözleşmesi (`contracts/game_contract.md`) henüz gelmedi.
> Bu belge kod içermez; oyuna hiçbir şey eklenmedi.%s

- **Dosya:** `%s` (tek dosya; dokular gömülü, `EXT_texture_webp` gerekli — three r128 GLTFLoader destekler; oyunda GLTFLoader şu an main dalında yok).
- **Yön/ölçek (geçici):** metre, +Y yukarı, burun −Z. Kök düğüm `SD_%s`; `userData` = kök extras.
- **LOD:** `LOD0/LOD1/LOD2` kardeş düğümler; hepsi dosyada. Oyun LOD kullanmıyorsa yalnızca `LOD0` görünür bırakılmalı.
- **Malzemeler:** `MAT_body` (base + ORM + normal + emissive harita), `MAT_emit` (canlı emisyon, düz renk ≤ 1 — parlaklık bloom ile).
- **Soketler:** `SOCK_*` boş düğümler; yön düğümün −Z ekseni. extras: amaç, renk vb.
- **Normal haritası:** tangent dosyada yok; three çalışma anında üretir (validator uyarısı). Görsel fark QC'de ölçüldü (ΔE).
- **Gölge:** gerçek zamanlı gölge varsayılmadı; temas gölgesi AO haritasında.
- **Fallback (öneri):** GLB yüklenemezse mevcut model kalır.
- **Test:** `qc/viewer/check.html` (otomatik) ve `qc/viewer/bench.html?glb=…` (gerçek cihaz).
""" % (a.id, rev, '\n> **Test nesnesi: oyuna entegre edilmeyecek.**' if spec.get('test_asset') else '', glb_name, a.id))
    if reg['state'] != 'delivered':
        registry.transition(a.id, 'delivered', 'teslim paketi: ' + os.path.relpath(out, FACTORY))
    print('RESULT', json.dumps({'stage': 'deliver', 'out': out, 'files': sorted(os.path.relpath(p, out) for p in glob.glob(out + '/**/*', recursive=True) if os.path.isfile(p))}, ensure_ascii=False))


def cmd_revise(a):
    """Yeni revizyon: rev+1, durum draft. Eski revizyonun work/ ve deliveries/ kayıtları korunur."""
    reg = registry.get(a.id)
    if reg is None:
        raise SystemExit('kayıt yok: ' + a.id)
    registry.update(a.id, rev=reg['rev'] + 1, timings={}, perf_baseline=reg.get('perf_baseline'))
    registry.transition(a.id, 'draft', 'yeni revizyon r%03d: %s' % (reg['rev'] + 1, a.reason))
    print('RESULT', json.dumps({'id': a.id, 'rev': reg['rev'] + 1}))


def cmd_status(a):
    reg = registry.load()
    for k, v in reg['assets'].items():
        print('%-20s r%03d  %-16s %s' % (k, v['rev'], v['state'], v.get('timings', {})))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    for n in ('model', 'review', 'prepare', 'qc', 'deliver'):
        p = sp.add_parser(n)
        p.add_argument('id')
        if n in ('model', 'prepare'):
            p.add_argument('--fast', action='store_true')
    p = sp.add_parser('approve')
    p.add_argument('id')
    p.add_argument('--gate', choices=['visual', 'tech'], required=True)
    p.add_argument('--by', required=True)
    p.add_argument('--note', required=True)
    p.add_argument('--accept-warn')
    p = sp.add_parser('revise')
    p.add_argument('id')
    p.add_argument('--reason', required=True)
    sp.add_parser('status')
    a = ap.parse_args()
    globals()['cmd_' + a.cmd](a)


if __name__ == '__main__':
    main()
