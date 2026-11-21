// Grafik bağlantısı koparsa: kalite Performans'a düşer ve sayaç artar; ?q=0 adresle kalite seçer.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const errs = [];
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, serviceWorkers: 'block' });
  await ctx.addInitScript(() => { try { if (!sessionStorage.getItem('i')){ sessionStorage.setItem('i', '1'); localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd_q', '2'); localStorage.setItem('sd_qm', '1'); } } catch (e) {} });
  const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 160)));
  const R = {}; const base = (process.env.BASE || 'http://localhost:8771/');
  await p.goto(base + '?q=1'); await p.waitForTimeout(3000);
  R.adresKalite = await p.evaluate(() => localStorage.getItem('sd_q') === '1' && window.__qLevel === 1);
  await p.evaluate(() => { const c = document.querySelector('canvas'); const gl = c && (c.getContext('webgl2') || c.getContext('webgl')); const e = gl && gl.getExtension('WEBGL_lose_context'); window.__lost = !!e; if (e) e.loseContext(); });
  await p.waitForTimeout(800);
  R.baglamKopar = await p.evaluate(() => window.__lost === true);
  R.kaliteDustu = await p.evaluate(() => localStorage.getItem('sd_q') === '0' && localStorage.getItem('sd_qm') === '1');
  R.sayac = await p.evaluate(() => +localStorage.getItem('sd_lost') || 0);
  R.uyari = await p.evaluate(() => /düşük görüntü kalitesiyle/.test(document.body.textContent));
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
