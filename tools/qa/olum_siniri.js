// Ölüm bedeli üst sınırı (K38): test modunda kredi 999999 iken bedel 2000 olmalı.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const errs = []; const R = {};
  for (const [ad, kredi] of [['cok', 999999]]){
    const pre = JSON.stringify({ kredi, lv: { lazer: 0, kargo: 0, motor: 0 }, xp: 500, pilot: 'Test', side: 'filo', open: [0], grace: 600, fac: { filo: 40, lonca: 10, korsan: -30 } });
    const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, serviceWorkers: 'block' });
    await ctx.addInitScript(pre => { try { if (!sessionStorage.getItem('i')){ sessionStorage.setItem('i', '1'); localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', 'kayip-yildizlar:test'); localStorage.setItem('kayip-yildizlar:test', pre); } window.__noFbk = 1; } catch (e) {} }, pre);
    const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 160)));
    await p.goto(process.env.BASE || 'http://localhost:8771/'); await p.waitForTimeout(3000);
    await p.evaluate(() => { const g = document.getElementById('titleGo'); g && g.click(); }); await p.waitForTimeout(1500);
    let calm = 0; for (let k = 0; k < 40 && calm < 5; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return !!(window.__menuOn || document.getElementById('ctrlSel') || document.getElementById('sideSel')); }); calm = m ? 0 : calm + 1; await p.waitForTimeout(600); }
    await p.waitForTimeout(1500);
    await p.evaluate(() => { const t = window.__sdt; t.undock(); t.save.kredi = t.save.kredi; });   // TESTM her saniye krediyi 999999 yapar; ölçüm için test kaydını bypass edeceğiz
    const k0 = await p.evaluate(() => window.__sdt.save.kredi);
    await p.evaluate(k => { window.__sdt.save.kredi = k; window.__sdt.wreck(); }, kredi); await p.waitForFunction(() => { const d = document.querySelector('#death'); return d && /CANLAN · \d+/.test(d.innerText); }, null, { timeout: 30000 }).catch(() => {});
    const kutu = await p.evaluate(() => { const d = document.querySelector('#death'); const m = d && d.innerText.match(/CANLAN · (\d+)/); return m ? +m[1] : null; });
    R.ucret = kutu;
    await ctx.close();
  }
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
