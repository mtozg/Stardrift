"""QC raporu: qc_report.json (makine) + qc_report.html (insan). bpy gerektirmez."""
import html, json, os


def summarize(items):
    c = {'PASS': 0, 'WARN': 0, 'FAIL': 0, 'SKIP': 0}
    for it in items:
        c[it['status']] = c.get(it['status'], 0) + 1
    return c


def _fmt(v):
    if isinstance(v, float):
        return '%.4g' % v
    if isinstance(v, (list, dict)):
        s = json.dumps(v, ensure_ascii=False)
        return s if len(s) < 120 else s[:117] + '…'
    return '' if v is None else str(v)


CSS = """
:root{--bg:#f6f7f9;--card:#fff;--fg:#1b2230;--mut:#5e6b80;--line:#dfe3ea;--pass:#1f8a4c;--warn:#b7791f;--fail:#c53030;--skip:#718096;--acc:#1f6fb2}
@media (prefers-color-scheme:dark){:root{--bg:#0d1118;--card:#151b25;--fg:#dbe2ee;--mut:#8f9bb0;--line:#263042;--pass:#48bb78;--warn:#ecc94b;--fail:#fc8181;--skip:#a0aec0;--acc:#63b3ed}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1180px;margin:0 auto;padding:24px 16px 64px}h1{font-size:22px;margin:0 0 4px}h2{font-size:16px;margin:28px 0 10px}
.mut{color:var(--mut)}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.row{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px}.kpi b{display:block;font-size:20px;font-variant-numeric:tabular-nums}
.kpi span{color:var(--mut);font-size:12px}.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-weight:600;font-size:12px;color:#fff}
.PASS{background:var(--pass)}.WARN{background:var(--warn)}.FAIL{background:var(--fail)}.SKIP{background:var(--skip)}
table{width:100%;border-collapse:collapse;font-size:13px}td,th{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{color:var(--mut);font-weight:600}td.num{font-variant-numeric:tabular-nums;text-align:right}.wrap{overflow-x:auto}
.imgs{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px}.imgs figure{margin:0}.imgs img{width:100%;border-radius:8px;border:1px solid var(--line);background:#141821}
figcaption{font-size:12px;color:var(--mut);margin-top:4px}code{font-size:12px}
"""


def html_report(R, path, img):
    """img: {anahtar: göreli yol}"""
    s = R['summary']
    st = R['stats']
    e = html.escape
    fig = lambda k, cap: ('<figure><img src="%s" alt="%s" loading="lazy"><figcaption>%s</figcaption></figure>' % (e(img[k]), e(cap), e(cap))) if k in img else ''
    rows = ''.join('<tr><td><span class="badge %s">%s</span></td><td><code>%s</code></td><td>%s</td><td>%s</td><td>%s</td><td class="mut">%s</td></tr>' % (
        it['status'], it['status'], e(it['id']), it['layer'], e(_fmt(it.get('value'))), e(_fmt(it.get('limit'))), e(it.get('note', ''))) for it in R['items'])
    cmp_rows = ''.join('<tr><td>%s</td><td class="num">%.2f%%</td><td class="num">%.2f</td><td class="num">%.2f</td><td class="num">%.3f%%</td></tr>' % (
        e(k), v['lum_diff'] * 100, v['deltaE_mean'], v['deltaE_p95'], v['silhouette_diff'] * 100) for k, v in R['three_vs_golden'].items())
    perf_rows = ''
    for dev, d in R.get('perf', {}).items():
        for p in d.get('perf') or []:
            perf_rows += '<tr><td>%s</td><td class="num">%d</td><td class="num">%.2f</td><td class="num">%.2f</td><td class="num">%.2f</td><td class="num">%d</td><td class="num">%d</td></tr>' % (
                e(dev), p['n'], p['ms_avg'], p['ms_p50'], p['ms_p95'], p['calls'], p['triangles'])
    tim = ''.join('<tr><td>%s</td><td class="num">%.1f s</td></tr>' % (e(k), v) for k, v in R['timings'].items())
    tex = ''.join('<tr><td>%s</td><td>%s</td><td class="num">%s KB</td></tr>' % (e(k), '×'.join(map(str, v['size'])), v['kb']) for k, v in st['textures'].items())
    doc = """<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>QC Raporu</title><style>%(css)s</style></head><body><main>
<h1>QC raporu — <code>%(id)s</code> r%(rev)03d</h1>
<div class="mut">%(when)s · fabrika %(commit)s · Blender %(blender)s · Three r128 (oyunun vendor/three.min.js) · %(mode)s</div>
<h2>Sonuç</h2><div class="row">
<div class="card kpi"><b><span class="badge %(verdict)s">%(verdict)s</span></b><span>genel karar</span></div>
<div class="card kpi"><b>%(p)d / %(w)d / %(f)d / %(sk)d</b><span>PASS / WARN / FAIL / SKIP</span></div>
<div class="card kpi"><b>%(tris)s</b><span>üçgen LOD0 / LOD1 / LOD2</span></div>
<div class="card kpi"><b>%(calls)d</b><span>draw call (LOD0, Three ölçümü)</span></div>
<div class="card kpi"><b>%(kb).1f KB</b><span>GLB boyutu</span></div>
<div class="card kpi"><b>%(gpu).2f MB</b><span>GPU doku belleği (tahmin)</span></div>
<div class="card kpi"><b>%(total).0f s</b><span>toplam üretim süresi</span></div></div>
<h2>Blender ⟷ Three.js (nötr ışık, aynı kamera)</h2>
<div class="imgs">%(cmp_imgs)s</div>
<div class="card wrap" style="margin-top:10px"><table><tr><th>kamera</th><th>parlaklık farkı</th><th>ΔE ort.</th><th>ΔE p95</th><th>siluet farkı</th></tr>%(cmp_rows)s</table></div>
<h2>Lookdev (Kapı 1 görüntüleri)</h2><div class="imgs">%(look)s</div>
<h2>Performans (Playwright, swiftshader — yalnızca göreli)</h2>
<div class="card wrap"><table><tr><th>profil</th><th>örnek</th><th>ms ort.</th><th>p50</th><th>p95</th><th>çağrı</th><th>üçgen</th></tr>%(perf_rows)s</table>
<p class="mut">Yazılım GPU'su mutlak hız vermez; gerçek cihaz ölçümü <code>qc/viewer/bench.html</code> ile yapılır.</p></div>
<h2>Dokular</h2><div class="card wrap"><table><tr><th>doku</th><th>boyut</th><th>dosya</th></tr>%(tex)s</table></div>
<h2>Testler</h2><div class="card wrap"><table><tr><th></th><th>test</th><th>katman</th><th>değer</th><th>sınır</th><th>not</th></tr>%(rows)s</table></div>
<h2>Süreler</h2><div class="card wrap"><table>%(tim)s</table></div>
<h2>Teşhis görüntüleri</h2><div class="imgs">%(diag)s</div>
</main></body></html>""" % dict(
        css=CSS, id=e(R['asset_id']), rev=R['rev'], when=e(R['time']), commit=e(R.get('factory_commit', '?')), blender=e(R.get('blender', '?')),
        mode='hızlı mod (--fast)' if R.get('fast') else 'tam kalite', verdict=R['verdict'], p=s['PASS'], w=s['WARN'], f=s['FAIL'], sk=s.get('SKIP', 0),
        tris=' / '.join(str(t) for t in st['tris']), calls=R['three'].get('info', {}).get('calls', -1), kb=st['glb_bytes'] / 1024,
        gpu=st['tex_gpu_bytes_est'] / 1048576, total=sum(R['timings'].values()),
        cmp_imgs=''.join(fig('cmp_' + k, k + ': Blender (sol) · Three r128 (orta) · ΔE haritası (sağ)') for k in R['three_vs_golden']),
        cmp_rows=cmp_rows, look=fig('hero', 'hero (lookdev)') + fig('hero_rear', 'arka 3/4') + fig('closeup', 'yakın plan') + fig('ortho_6', '6 dik görünüş'),
        perf_rows=perf_rows, tex=tex, rows=rows, tim=tim,
        diag=fig('normal_side_diff', 'FrontSide ⟷ DoubleSide fark haritası (kırmızı = fark)') + fig('thumb', '128 px okunabilirlik'))
    open(path, 'w', encoding='utf-8').write(doc)
