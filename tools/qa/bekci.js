// Kadim Bekçi (K25) testi: görev adımı, doğuş, 3 aşama, ölünce save.bekci, ödül yalnız rozet (kredi/XP değişmez), Korsan'da da düşman.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const R = {}; const errs = [];
  for (const side of ['filo', 'korsan']){
    const pre = JSON.stringify({ kredi: 5000, lv: { lazer: 0, kargo: 0, motor: 0 }, xp: 9000, pilot: 'Test', side, open: [0, 1, 2, 3, 4, 5], grace: 600, kadimDone: 1,
      fac: { filo: side === 'korsan' ? -50 : 40, lonca: 10, korsan: side === 'korsan' ? 60 : -30 }, boss: [0, 1, 2, 3, 4, 5], mq: { i: 0 } });
    const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, serviceWorkers: 'block' });
    await ctx.addInitScript(pre => { try { if (!sessionStorage.getItem('i')){ sessionStorage.setItem('i', '1'); localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', 'kayip-yildizlar:test'); localStorage.setItem('kayip-yildizlar:test', pre); } window.__noFbk = 1; } catch (e) {} }, pre);
    const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 200)));
    await p.goto(process.env.BASE || 'http://localhost:8771/'); await p.waitForTimeout(3000);
    await p.evaluate(() => { const g = document.getElementById('titleGo'); g && g.click(); }); await p.waitForTimeout(1500);
    let calm = 0; for (let k = 0; k < 40 && calm < 5; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return !!(window.__menuOn || document.getElementById('ctrlSel') || document.getElementById('sideSel')); }); calm = m ? 0 : calm + 1; await p.waitForTimeout(600); }
    await p.waitForTimeout(1500);
    const r = {};
    if (await p.evaluate(() => window.__sdt.curSys) !== 0){ await p.evaluate(() => { window.__sdt.undock(); window.__sdt.enter(0); }); for (let i = 0; i < 60; i++){ if (await p.evaluate(() => window.__sdt.curSys === 0 && !window.__menuOn)) break; await p.waitForTimeout(300); } await p.waitForTimeout(2000); }
    r.once = await p.evaluate(() => window.__bekciDbg().active);                                            // görev adımı gelmeden aktif değil
    r.adim = await p.evaluate(() => { const t = window.__sdt; t.save.mq.i = window.__mqLen() - 1; const c = window.__mqCur(); return c && c.t; });
    r.aktif = await p.evaluate(() => window.__bekciDbg().active);
    const k0 = await p.evaluate(() => ({ kredi: window.__sdt.save.kredi, xp: window.__sdt.save.xp }));
    await p.evaluate(() => { const t = window.__sdt; t.undock(); t.tp(window.__bekciDbg().GP, 1200); t.stop(); });
    for (let i = 0; i < 60; i++){ await p.waitForTimeout(300); if (await p.evaluate(() => { window.__sdt.stop(); return !!window.__bekciDbg().G; })) break; }
    r.dogdu = await p.evaluate(() => { const d = window.__bekciDbg(); return d.G ? { ad: d.G.name, hull: d.G.hull, foe: window.__sdt.rel(d.G), n: d.n } : null; });
    // aşamalar: gövdeyi %60 ve %30'a indir
    for (const f of [0.6, 0.3]){ await p.evaluate(f => { const d = window.__bekciDbg(); d.G.hull = d.G.hullMax * f; }, f); await p.waitForTimeout(1500); r['faz_' + Math.round(f * 100)] = await p.evaluate(() => { const d = window.__bekciDbg(); return { gph: d.gph, muhafiz: d.n }; }); }
    // öldür
    await p.evaluate(() => { const d = window.__bekciDbg(); d.G.hull = 0; window.__sdt.kill(d.G); }); 
    for (let i = 0; i < 40; i++){ await p.waitForTimeout(300); if (await p.evaluate(() => !!window.__sdt.save.bekci)) break; }
    r.bitis = await p.evaluate(k0 => ({ bekci: window.__sdt.save.bekci, krediFark: window.__sdt.save.kredi - k0.kredi, xpFark: window.__sdt.save.xp - k0.xp, aktifSonra: window.__bekciDbg().active, boss: window.__sdt.save.boss.length, step: (window.__mqCur() || {}).t }), k0);
    R[side] = r; await ctx.close();
  }
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
