const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const errs = [];
  const pre = JSON.stringify({ kredi: 50000, lv: { lazer: 0, kargo: 0, motor: 0 }, xp: 3000, side: 'filo', pilot: 'Test', fac: { filo: 40, lonca: 10, korsan: -30 }, ships: ['kasif', 'sahin', 'yuk', 'hayalet'] });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, serviceWorkers: 'block' });
  await ctx.addInitScript(pre => { try { if (!sessionStorage.getItem('i')){ sessionStorage.setItem('i', '1'); localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', 'kayip-yildizlar:test'); localStorage.setItem('kayip-yildizlar:test', pre); } window.__noFbk = 1; } catch (e) {} }, pre);
  const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 200)));
  await p.goto('' + (process.env.BASE || 'http://localhost:8771/') + '?glb=0'); await p.waitForTimeout(3000);
  await p.evaluate(() => { const g = document.getElementById('titleGo'); g && g.click(); }); await p.waitForTimeout(1500);
  let calm = 0; for (let k = 0; k < 40 && calm < 5; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return !!(window.__menuOn || document.getElementById('ctrlSel') || document.getElementById('sideSel')); }); calm = m ? 0 : calm + 1; await p.waitForTimeout(600); }
  await p.evaluate(() => { const t = window.__sdt; t.dockAt(t.stations()[0]); });
  for (let i = 0; i < 30; i++){ if (await p.evaluate(() => window.__sdt.docked)) break; await p.waitForTimeout(400); }
  await p.evaluate(() => { const t = document.querySelector('#dtabs [data-t="hg"]'); t && t.click(); }); await p.waitForTimeout(2500);
  const R = { open: await p.evaluate(() => window.__sdt.hg()) };
  const seq = ['sahin', 'yuk', 'hayalet', 'kasif']; R.cycles = [];
  for (let c = 0; c < 3; c++){ for (const id of seq){ await p.evaluate(id => window.__sdt.hgSet(id), id); await p.waitForTimeout(1500); } R.cycles.push(await p.evaluate(() => window.__sdt.hg())); }
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
