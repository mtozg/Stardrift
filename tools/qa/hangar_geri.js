// Hangar: gemi sürüklenip bırakılınca ilk konumuna döner (ve geri dönüş döngüsü yalnız o sırada çalışır).
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
  await p.evaluate(() => { const t = window.__sdt; t.dockAt(t.stations()[0]); });
  for (let i = 0; i < 40; i++){ if (await p.evaluate(() => window.__sdt.docked)) break; await p.waitForTimeout(400); }
  await p.evaluate(() => { const t = document.querySelector('#dtabs [data-t="hg"]'); t && t.click(); }); await p.waitForTimeout(2500);
  const bx = await p.evaluate(() => { const r = document.getElementById('hgStage').getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; });
  await p.mouse.move(bx.x, bx.y); await p.mouse.down(); await p.mouse.move(bx.x + 160, bx.y, { steps: 8 });
  const R = { surukleme: +(await p.evaluate(() => window.__sdt.hgYo())).toFixed(3) };
  await p.mouse.up(); await p.waitForTimeout(4000);
  R.sonra = +(await p.evaluate(() => window.__sdt.hgYo())).toFixed(3); R.errs = errs;
  console.log('@@' + JSON.stringify(R)); await b.close();
})();
