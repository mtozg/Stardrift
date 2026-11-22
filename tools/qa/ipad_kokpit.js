// iPad (dokunmatik, büyük ekran): kokpit modeli hafif (_m, 1024 dokulu) yüklenir; masaüstünde tam model.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const R = {}; const errs = [];
  const run = async (opt, nm) => {
    const ctx = await b.newContext(Object.assign({ serviceWorkers: 'block' }, opt));
    await ctx.addInitScript(() => { try { localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', 'kayip-yildizlar:test'); localStorage.setItem('kayip-yildizlar:test', JSON.stringify({ kredi: 100, lv: { lazer: 0, kargo: 0, motor: 0 }, xp: 500, pilot: 'Test', side: 'filo', open: [0], grace: 600 })); } catch (e) {} });
    const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 120))); const urls = []; p.on('request', r => { if (/cockpit_kasif/.test(r.url())) urls.push(r.url().split('/').pop().split('?')[0]); });
    await p.goto((process.env.BASE || 'http://localhost:8771/')); await p.waitForTimeout(3000);
    await p.evaluate(() => { const g = document.getElementById('titleGo'); g && g.click(); }); await p.waitForTimeout(1500);
    for (let k = 0; k < 25 && !urls.length; k++){ await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]') || document.querySelector('#sideSel [data-go]'); g && g.click(); }); await p.waitForTimeout(800); }
    await p.waitForTimeout(2500); R[nm] = urls; R[nm + 'Glb'] = await p.evaluate(() => typeof window.__glb !== 'undefined'); await ctx.close();
  };
  await run({ viewport: { width: 1180, height: 820 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true, userAgent: 'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' }, 'ipad');
  await run({ viewport: { width: 1280, height: 720 } }, 'masaustu');
  R.ipadHafif = R.ipad.length > 0 && R.ipad.every(u => /_m\.glb/.test(u));
  R.masaustuTam = R.masaustu.length > 0 && R.masaustu.every(u => !/_m\.glb/.test(u));
  R.ipadGlbKapali = R.ipadGlb === false; R.masaustuGlbAcik = R.masaustuGlb === true;   // 1.68.0: iPad'de GLB otomatik kapalı, masaüstünde açık
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
