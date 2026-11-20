// Derin sinyal (Kadim yankı): derin kuşakta doğar, 5 muhafız, öldürünce ödül ve olay biter.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const errs = [];
  const pre = JSON.stringify({ kredi: 100, lv: { lazer: 0, kargo: 0, motor: 0 }, xp: 500, pilot: 'Test', side: 'filo', open: [0], grace: 600, fac: { filo: 40, lonca: 10, korsan: -30 } });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, serviceWorkers: 'block' });
  await ctx.addInitScript(pre => { try { if (!sessionStorage.getItem('i')){ sessionStorage.setItem('i', '1'); localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', 'kayip-yildizlar:test'); localStorage.setItem('kayip-yildizlar:test', pre); } window.__noFbk = 1; } catch (e) {} }, pre);
  const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 160)));
  await p.goto(process.env.BASE || 'http://localhost:8771/'); await p.waitForTimeout(3000);
  await p.evaluate(() => { const g = document.getElementById('titleGo'); g && g.click(); }); await p.waitForTimeout(1500);
  let calm = 0; for (let k = 0; k < 40 && calm < 5; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return !!(window.__menuOn || document.getElementById('ctrlSel') || document.getElementById('sideSel')); }); calm = m ? 0 : calm + 1; await p.waitForTimeout(600); }
  await p.waitForTimeout(1500);
  const R = {};
  await p.evaluate(() => { const t = window.__sdt; t.undock(); const v = t.rigPos(); v.set(14000, 0, 0); t.tp(v, 0); t.stop(); window.__forceEv = 'derin'; });
  for (let i = 0; i < 40; i++){ await p.waitForTimeout(300); await p.evaluate(() => window.__sdt.stop()); if (await p.evaluate(() => !!document.querySelector('button[data-a="ok"]'))) break; }
  R.teklif = await p.evaluate(() => { const b = document.querySelector('button[data-a="ok"]'); const t = document.querySelector('#sigCard b, .sig b'); return !!b; });
  const k0 = await p.evaluate(() => window.__sdt.save.kredi);
  await p.evaluate(() => { document.querySelector('button[data-a="ok"]').click(); });
  for (let i = 0; i < 40; i++){ await p.waitForTimeout(300); await p.evaluate(() => window.__sdt.stop()); if (await p.evaluate(() => window.__sdt.npcs().filter(n => n.guard).length >= 5)) break; }
  R.muhafiz = await p.evaluate(() => window.__sdt.npcs().filter(n => n.guard).length);
  await p.evaluate(() => { const t = window.__sdt; for (const n of t.npcs().filter(x => x.guard)) t.kill(n); });
  for (let i = 0; i < 30; i++){ await p.waitForTimeout(400); await p.evaluate(() => window.__sdt.stop()); if (await p.evaluate(k0 => window.__sdt.save.kredi - k0 >= 400, k0)) break; }
  R.odul = await p.evaluate(k0 => window.__sdt.save.kredi - k0 >= 450, k0);
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
