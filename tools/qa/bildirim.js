// Başarım ve unvan bildirimleri: açılışta sessiz, sonradan yükselişte toast (ve unvanda telsiz) gelir.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const errs = [];
  const pre = JSON.stringify({ kredi: 100, lv: { lazer: 0, kargo: 0, motor: 0 }, xp: 500, pilot: 'Test', side: 'filo', open: [0], grace: 600, fac: { filo: 40, lonca: 10, korsan: -30 }, lq: { filo: 1 }, st: { sell: 40, kill: 0, avci: 0, kacak: 0, sip: 0 } });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, serviceWorkers: 'block' });
  await ctx.addInitScript(pre => { try { if (!sessionStorage.getItem('i')){ sessionStorage.setItem('i', '1'); localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', 'kayip-yildizlar:test'); localStorage.setItem('kayip-yildizlar:test', pre); } window.__noFbk = 1; } catch (e) {} }, pre);
  const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 160)));
  const toasts = []; await p.exposeFunction('__tl', t => toasts.push(t));
  await p.goto(process.env.BASE || 'http://localhost:8771/'); await p.waitForTimeout(2500);
  await p.evaluate(() => { const t = document.getElementById('toast'); if (t) new MutationObserver(() => window.__tl(t.textContent)).observe(t, { childList: true, characterData: true, subtree: true }); const g = document.getElementById('titleGo'); g && g.click(); }); await p.waitForTimeout(1500);
  let calm = 0; for (let k = 0; k < 40 && calm < 5; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return !!(window.__menuOn || document.getElementById('ctrlSel') || document.getElementById('sideSel')); }); calm = m ? 0 : calm + 1; await p.waitForTimeout(600); }
  const R = {}; await p.waitForTimeout(11000);
  R.baseline = await p.evaluate(() => !!window.__sdt.save.bz); R.acilistaToast = toasts.filter(t => /Başarım|Yeni unvan/.test(t)).length;
  await p.evaluate(() => { const s = window.__sdt.save; s.st.sell = 60; s.lq.filo = 2; });
  await p.waitForTimeout(9000);
  R.toasts = toasts.filter(t => /Başarım|Yeni unvan/.test(t)); R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
