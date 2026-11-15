// Playwright sürücüsü: check.html'i çalıştırır, render PNG'lerini ve sonuç JSON'unu yazar.
// Kullanım: node run_check.js <taban_url> <cfg_url> <çıktı_klasörü> [cihazlar(virgüllü)] [perf_cfg_url]
// swiftshader (yazılım GPU): mutlak hız değil, göreli karşılaştırma içindir (QC.md §5).
const { chromium, devices } = require('playwright'); const fs = require('fs'); const path = require('path');
const [base, cfgUrl, out, devs, perfCfgUrl] = process.argv.slice(2);
const ARGS = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'];
async function run(b, ctxOpts, cfg) {
  const ctx = await b.newContext(ctxOpts); const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto(base + '/tools/asset_factory/qc/viewer/check.html?cfg=' + encodeURIComponent(cfg));
  await p.waitForFunction(() => window.__R && window.__R.done, null, { timeout: 300000 });
  const R = await p.evaluate(() => window.__R); R.page_errors = errs; await ctx.close(); return R;
}
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ARGS });
  const R = await run(b, { viewport: { width: 1200, height: 800 }, deviceScaleFactor: 1 }, cfgUrl);
  for (const [k, v] of Object.entries(R.renders || {})) { fs.writeFileSync(path.join(out, 'three_' + k + '.png'), Buffer.from(v.split(',')[1], 'base64')); }
  delete R.renders;
  R.devices = {};
  if (devs && perfCfgUrl) for (const d of devs.split(',')) {
    const r = await run(b, { ...devices[d] }, perfCfgUrl); R.devices[d] = { perf: r.perf, load_ms: r.load_ms, page_errors: r.page_errors, viewport: devices[d].viewport, dpr: devices[d].deviceScaleFactor };
  }
  fs.writeFileSync(path.join(out, 'three_result.json'), JSON.stringify(R, null, 1)); await b.close();
  console.log('RESULT', JSON.stringify({ ok: !R.error, error: R.error || null }));
})();
