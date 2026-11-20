// Stardrift kokpit regresyon testi (QA, PR #28 @ bc5ba4a için yazıldı).
// Kullanım: oyunu `python3 -m http.server 8766` ile sun, sonra: node tools/qa/qa_pr28.js <çıktı_klasörü> 8766
// Notlar: service worker kapalı; test anahtarı 'kayip-yildizlar:test' (__ckb.swap yalnız test modunda);
// swiftshader sayıları gerçek GPU'dan farklı olabilir. Referans (bc5ba4a): masaüstü doku 69/48/69/48/69, iPhone 60/39/60/39/60.
const { chromium, devices } = require('playwright'); const fs = require('fs');
const OUT = process.argv[2]; const PORT = process.argv[3] || '8766';
const DEV = { 'masaustu': { viewport: { width: 1600, height: 800 } }, 'iphone13': devices['iPhone 13 landscape'] };
async function boot(b, dev, opt = {}){
  const ctx = await b.newContext({ ...DEV[dev], serviceWorkers: 'block' });
  const key = opt.real ? 'kayip-yildizlar' : 'kayip-yildizlar:test';
  await ctx.addInitScript(k => { try { localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', k); window.__noFbk = 1; } catch (e) {} }, key);
  const p = await ctx.newPage(); const log = [];
  p.on('pageerror', e => log.push('PAGEERR ' + e.message.slice(0, 200)));
  p.on('console', m => { if (m.type() === 'error' || /kokpit|Hata/i.test(m.text())) log.push(m.type() + ' ' + m.text().slice(0, 180)); });
  const glb = []; p.on('request', r => { if (/\.glb/.test(r.url())) glb.push(r.url().replace(/^.*\/models\//, '').replace(/\?.*$/, '')); });
  if (opt.block) await p.route(opt.block, r => r.abort());
  const t0 = Date.now(); await p.goto('http://localhost:' + PORT + '/'); const loadMs = Date.now() - t0; await p.waitForTimeout(2500);
  await p.evaluate(() => document.getElementById('titleGo').click()); await p.waitForTimeout(1500);
  await p.evaluate(() => { const i = document.getElementById('ssName'); if (i) i.value = 'Test'; const k = document.querySelector('#sideSel .c[data-k="filo"] .pk'); k && k.click(); }); await p.waitForTimeout(1200);
  let calm = 0; for (let k = 0; k < 40 && calm < 5; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return !!(window.__menuOn || document.getElementById('ctrlSel') || document.getElementById('sideSel')); }); calm = m ? 0 : calm + 1; await p.waitForTimeout(600); }
  return { ctx, p, log, glb, loadMs };
}
const mem = p => p.evaluate(() => { const m = window.__ckb && window.__ckb.mem; return m ? { tex: m.textures, geo: m.geometries, id: window.__ckb.id, ready: window.__ckb.ready, on: !!window.__ck3on } : null; });
async function waitReady(p, id, ms){ const t0 = Date.now(); while (Date.now() - t0 < ms){ const r = await p.evaluate(id => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return window.__ckb && window.__ckb.id === id && window.__ckb.ready && !!window.__ck3on; }, id); if (r) return Date.now() - t0; await p.waitForTimeout(400); } return -1; }
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const R = {};
  for (const dev of Object.keys(DEV)){
    // A: döngü K→Ş→K→Ş→K
    { const { ctx, p, log, glb, loadMs } = await boot(b, dev); const r = { loadMs, steps: [] };
      r.kasifMs = await waitReady(p, 'kasif', 60000); await p.waitForTimeout(1500); r.steps.push(['kasif', (Date.now()), await mem(p)]);
      for (const id of ['sahin', 'kasif', 'sahin', 'kasif']){ await p.evaluate(id => window.__ckb.swap(id), id); const ms = await waitReady(p, id, 60000); await p.waitForTimeout(1500); r.steps.push([id, ms, await mem(p)]); }
      await p.screenshot({ path: OUT + '/' + dev + '_kasif_son.png' });
      r.glb = glb; r.log = log.slice(0, 12); R[dev + '_dongu'] = r; await ctx.close(); }
    // B: kontrol, yalnız Kaşif, aynı süre boyunca örnekle
    { const { ctx, p, log } = await boot(b, dev); const r = { samples: [] }; await waitReady(p, 'kasif', 60000); await p.waitForTimeout(1500);
      for (let i = 0; i < 6; i++){ r.samples.push(await mem(p)); await p.waitForTimeout(4000); }
      r.log = log.slice(0, 8); R[dev + '_kontrol'] = r; await ctx.close(); }
  }
  // C: Şahin GLB tamamen engelli
  { const { ctx, p, log, glb } = await boot(b, 'masaustu', { block: '**/models/cockpit_sahin*.glb*' }); const r = {};
    await waitReady(p, 'kasif', 60000); await p.evaluate(() => window.__ckb.swap('sahin')); const sn = [];
    for (let i = 0; i < 9; i++){ await p.waitForTimeout(5000); sn.push(await p.evaluate(() => ({ t: Math.round(performance.now() / 1000), tries: window.__ckb.tries, ready: window.__ckb.ready, failed: window.__ckb.failed, on: !!window.__ck3on, wait: !!window.__ck3wait, menuOn: !!window.__menuOn, prep: !!document.getElementById('ckPrep'), img2d: window.__ckb.img2d, toast: (document.getElementById('toast') || {}).textContent || '' }))); }
    r.samples = sn; r.glbReq = glb.length; r.log = log.slice(0, 10); await p.screenshot({ path: OUT + '/sahin_engelli.png' });
    // engel kalkınca toparlanıyor mu
    await p.unroute('**/models/cockpit_sahin*.glb*'); r.recoverMs = await waitReady(p, 'sahin', 40000); R.engelli = r; await ctx.close(); }
  // D: gerçek kayıt: swap tanımsız olmalı
  { const { ctx, p, log } = await boot(b, 'masaustu', { real: true }); R.gercek = { swap: await p.evaluate(() => typeof (window.__ckb && window.__ckb.swap)), ckb: await p.evaluate(() => !!window.__ckb), ships: await p.evaluate(() => { try { return JSON.parse(localStorage.getItem('kayip-yildizlar') || '{}').ships; } catch (e) { return 'x'; } }), log: log.slice(0, 8) }; await ctx.close(); }
  fs.writeFileSync(OUT + '/sonuc.json', JSON.stringify(R, null, 1)); console.log(JSON.stringify(R, null, 1)); await b.close();
})();
