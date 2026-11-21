// iPad: çizim pikseli bütçesi kaliteye göre düşer, parlama kapalı; masaüstü etkilenmez.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const R = {}; const errs = [];
  const run = async (opt, nm) => {
    const ctx = await b.newContext(Object.assign({ serviceWorkers: 'block' }, opt)); await ctx.addInitScript(() => { try { localStorage.setItem('sd_nointro', '1'); } catch (e) {} });
    const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 120)));
    await p.goto((process.env.BASE || 'http://localhost:8771/')); await p.waitForTimeout(4000);
    R[nm] = await p.evaluate(() => { const o = []; for (const lv of [0, 1, 2]){ window.__qLevel = lv; o.push(Math.round(window.__qCap() * 100) / 100); } return { cap: o, px: innerWidth * innerHeight, bloom: typeof window.__bloomOn !== 'undefined' ? window.__bloomOn : null }; });
    await ctx.close();
  };
  await run({ viewport: { width: 1180, height: 820 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true, userAgent: 'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' }, 'ipad');
  await run({ viewport: { width: 874, height: 402 }, deviceScaleFactor: 3, hasTouch: true, isMobile: true, userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' }, 'iphone');
  await run({ viewport: { width: 1920, height: 1080 } }, 'masaustu');
  R.ipadBudce = R.ipad.cap[0] <= 1.05 && R.ipad.cap[1] < 1.3 && R.ipad.cap[2] < 1.6;
  R.iphoneAyni = R.iphone.cap[0] === 1.25 && R.iphone.cap[1] === 1.6 && R.iphone.cap[2] === 2;
  R.masaustuAyni = R.masaustu.cap[0] === 1.25 && R.masaustu.cap[1] === 1.6 && R.masaustu.cap[2] === 2;
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
