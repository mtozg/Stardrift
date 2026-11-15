// Oyun içi ?ck=b testi (Playwright). Kullanım: repo kökünde `python3 -m http.server 8765` çalışırken `node tools/cockpit/verify/ckb_test.js`
// Kontroller: GLB yüklendi mi, ekran mesh'leri canlı SCR dokularına bağlı mı, kamera hizası (ekran köşeleri ↔ CKP), çizim çağrısı/üçgen/süre, fallback (GLB engellenince paralaks).
const { chromium, devices } = require('playwright'); const fs = require('fs');
const A = JSON.parse(fs.readFileSync(__dirname + '/../anchors/kasif.json', 'utf8')); const OUT = process.argv[2] || '/tmp';
async function boot(b, dev, block){
  const ctx = await b.newContext({ ...devices[dev], serviceWorkers: 'block' });
  await ctx.addInitScript(() => { try { localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', 'kayip-yildizlar:test'); localStorage.setItem('sd_ck3', 'b'); window.__noFbk = 1; } catch (e) {} });
  const p = await ctx.newPage(); p.on('pageerror', e => console.log('PE', e.message.slice(0, 200))); p.on('console', m => { if (/kokpit|hata|Error/i.test(m.text())) console.log('  C:', m.text().slice(0, 160)); });
  if (block) await p.route('**/models/cockpit_kasif*.glb*', r => r.abort());
  await p.goto('http://localhost:8765/'); await p.waitForTimeout(2500);
  await p.evaluate(() => document.getElementById('titleGo').click()); await p.waitForTimeout(1500);
  await p.evaluate(() => { const i = document.getElementById('ssName'); if (i) i.value = 'Test'; const k = document.querySelector('#sideSel .c[data-k="filo"] .pk'); k && k.click(); }); await p.waitForTimeout(1200);
  for (let k = 0; k < 8; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return window.__menuOn; }); if (!m && k > 2) break; await p.waitForTimeout(600); }
  await p.waitForTimeout(7000); return { ctx, p };
}
(async () => { const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const res = {};
  for (const dev of ['iPad Pro 11 landscape', 'iPhone 13 landscape', 'Pixel 7 landscape']){
    const { ctx, p } = await boot(b, dev, false);
    const r = await p.evaluate(A => { const B = window.__ckb; if (!B) return { err: 'yok' }; const k = B.k, v = B.view, out = { ready: B.ready, failed: B.failed, scrBound: null, err: null };
      if (!k) return out; out.scrBound = k.scr.map(e => ({ kind: e.kind, hasCanvas: !!(e.tx.image && e.tx.image.width), ver: e.ver })); out.calls = B.stat.calls; out.tris = B.stat.tris; out.ms = +B.stat.ms.toFixed(2);
      // kamera hizası: ekran mesh köşeleri → ekran pikseli; beklenen: OX + (u-800)*s, OY + (v-239.5)*s  (s = (H-OY)/416.5)
      const s = (v.H - v.OY) / 416.5, errs = {};
      for (const sc of A.screens){ const e = k.scr.find(q => q.o.name === sc.name); if (!e){ errs[sc.name] = null; continue; } e.o.updateMatrixWorld(true); const pos = e.o.geometry.attributes.position, got = [];
        for (let i = 0; i < pos.count; i++){ const w = new k.cam.position.constructor().fromBufferAttribute(pos, i).applyMatrix4(e.o.matrixWorld).project(k.cam); got.push([(w.x * 0.5 + 0.5) * v.W, (1 - (w.y * 0.5 + 0.5)) * v.H]); }
        let mx = 0; sc.ckp.forEach(q => { const ex = v.OX + (q[0] - 800) * s, ey = v.OY + (q[1] - 239.5) * s; let best = 1e9; got.forEach(g => { best = Math.min(best, Math.hypot(g[0] - ex, g[1] - ey)); }); mx = Math.max(mx, best); }); errs[sc.name] = +mx.toFixed(2); }
      out.alignErrPx = errs; out.view = v; return out; }, A);
    res[dev] = r; console.log(dev, JSON.stringify(r)); await p.screenshot({ path: OUT + '/ckb_' + dev.replace(/\s+/g, '_') + '.png' }); await ctx.close(); }
  // fallback: GLB engellenir → paralaks kokpit çalışmalı
  { const { ctx, p } = await boot(b, 'iPad Pro 11 landscape', true); const r = await p.evaluate(() => ({ failed: window.__ckb.failed, ready: window.__ckb.ready, ck3on: !!window.__ck3on })); res.fallback = r; console.log('fallback', JSON.stringify(r)); await p.screenshot({ path: OUT + '/ckb_fallback.png' }); await ctx.close(); }
  fs.writeFileSync(OUT + '/ckb_result.json', JSON.stringify(res, null, 1)); await b.close(); })();
