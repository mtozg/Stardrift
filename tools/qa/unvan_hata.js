// Taraf unvanı (Aşama 1-D) ve hata mesajı (ham metin yalnız test/tanı modunda) testi.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const R = {}; const errs = [];
  async function boot(key, save){
    const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, serviceWorkers: 'block' });
    await ctx.addInitScript(([k, s]) => { try { if (!sessionStorage.getItem('i')){ sessionStorage.setItem('i', '1'); localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', k); localStorage.setItem(k, s); } window.__noFbk = 1; } catch (e) {} }, [key, JSON.stringify(save)]);
    const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 160)));
    await p.goto(process.env.BASE || 'http://localhost:8771/'); await p.waitForTimeout(3000);
    await p.evaluate(() => { const g = document.getElementById('titleGo'); g && g.click(); }); await p.waitForTimeout(1500);
    let calm = 0; for (let k = 0; k < 40 && calm < 5; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return !!(window.__menuOn || document.getElementById('ctrlSel') || document.getElementById('sideSel')); }); calm = m ? 0 : calm + 1; await p.waitForTimeout(600); }
    await p.waitForTimeout(1500); return { ctx, p };
  }
  const base = { kredi: 100, lv: { lazer: 0, kargo: 0, motor: 0 }, xp: 500, pilot: 'Test', open: [0, 1, 2, 3, 4, 5], grace: 600, fac: { filo: 40, lonca: 10, korsan: 60 } };
  { const { ctx, p } = await boot('kayip-yildizlar:test', Object.assign({}, base, { side: 'filo', lq: { filo: 0 } }));
    R.unvan = await p.evaluate(() => [0, 1, 2, 3, 4, 5, 6].map(n => { window.__sdt.save.lq = { filo: n, lonca: n, korsan: n }; return window.__unvan('filo') + '|' + window.__unvan('lonca') + '|' + window.__unvan('korsan'); }));
    R.testHata = await p.evaluate(async () => { window.dispatchEvent(new ErrorEvent('error', { message: 'deneme hatası' })); await new Promise(r => setTimeout(r, 400)); return (document.getElementById('toast') || {}).textContent; });
    await ctx.close(); }
  { const { ctx, p } = await boot('kayip-yildizlar', Object.assign({}, base, { side: 'korsan', lq: { korsan: 4 } }));
    R.gercekHata = await p.evaluate(async () => { window.dispatchEvent(new ErrorEvent('error', { message: 'deneme hatası' })); await new Promise(r => setTimeout(r, 400)); return (document.getElementById('toast') || {}).textContent; });
    R.gercekUnvan = await p.evaluate(() => window.__unvan());
    await ctx.close(); }
  R.errs = errs.filter(e => !/deneme hatası/.test(e)); console.log('@@' + JSON.stringify(R)); await b.close();
})();
