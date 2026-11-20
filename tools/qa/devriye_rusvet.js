const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const R = {}; const errs = [];
  async function boot(pre){
    const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, serviceWorkers: 'block' });
    await ctx.addInitScript(pre => { try { if (!sessionStorage.getItem('i')){ sessionStorage.setItem('i', '1'); localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', 'kayip-yildizlar:test'); localStorage.setItem('kayip-yildizlar:test', pre); } window.__noFbk = 1; } catch (e) {} }, JSON.stringify(pre));
    const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 200)));
    await p.goto('' + (process.env.BASE || 'http://localhost:8771/') + ''); await p.waitForTimeout(3000);
    await p.evaluate(() => { const g = document.getElementById('titleGo'); g && g.click(); }); await p.waitForTimeout(1500);
    let calm = 0; for (let k = 0; k < 40 && calm < 5; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return !!(window.__menuOn || document.getElementById('ctrlSel') || document.getElementById('sideSel')); }); calm = m ? 0 : calm + 1; await p.waitForTimeout(600); }
    await p.waitForTimeout(1500); return { ctx, p };
  }
  const gwait = async (p, sec, fn) => { const t0 = await p.evaluate(() => window.__sdt.time); for (let i = 0; i < 400; i++){ const r = await p.evaluate(fn || (() => window.__sdt.stop())); const t = await p.evaluate(() => window.__sdt.time); if (t - t0 >= sec) return t - t0; await p.waitForTimeout(250); } return -1; };
  const base = { kredi: 5000, lv: { lazer: 0, kargo: 0, motor: 0 }, xp: 3000, pilot: 'Test', open: [0, 1, 2, 3, 4, 5], grace: 0 };
  { const { ctx, p } = await boot(Object.assign({}, base, { side: 'korsan', kacak: 10, fac: { filo: -50, lonca: -20, korsan: 70 } }));
    await p.evaluate(() => window.__sdt.enter(0)); for (let i = 0; i < 60; i++){ if (await p.evaluate(() => window.__sdt.curSys === 0 && !window.__menuOn)) break; await p.waitForTimeout(300); } await p.waitForTimeout(2000);
    // rüşvet: çağrıyı doğrudan başlat
    R.rs = await p.evaluate(() => { const t = window.__sdt; const q = t.npcs().find(n => n.role === 'patrol' && !n.hunter && !n.escort); t.tp(q.pos, 300); t.stop(); window.__hailT.start(q); const k0 = t.save.kredi, fiyat = window.__hailT.bribeP();
      const btn = document.querySelector('#hailBox button[data-h="rs"]'); const varMi = !!btn; btn && btn.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true })); return { varMi, fiyat, krediFark: t.save.kredi - k0, hl: window.__hailT.st, kacak: t.save.kacak, w: t.save.wanted }; });
    // tüccar kaçışı
    R.tuccarAd = await p.evaluate(() => { const t = window.__sdt; t.undock(); const n = t.npcs().find(x => x.role === 'trader' && !x.sg); if (!n) return null; window.__tt = n; t.tp(n.pos, 250); t.stop(); return n.name; });
    await gwait(p, 1.5, () => { window.__sdt.stop(); if (window.__tt) window.__sdt.tp(window.__tt.pos, 250); });
    R.tuccar = await p.evaluate(() => window.__tt ? { state: window.__tt.state, alert: window.__tt.alertT > 0 } : null);
    await ctx.close(); }
  if (0) { const { ctx, p } = await boot(Object.assign({}, base, { side: "filo", wanted: 1, fac: { filo: 40, lonca: 10, korsan: -30 } }));
    // takip sonu: yakında kalırsa saldırı
    R.takip = await p.evaluate(() => { const t = window.__sdt; const q = t.npcs().find(n => n.role === 'patrol' && !n.hunter && !n.escort); window.__qq = q; t.tp(q.pos, 300); t.stop(); window.__hailT.start(q); window.__hailT.flee(); q.chaseT = t.time + 1; return { w: t.save.wanted, ad: q.name }; });
    await gwait(p, 2, () => { window.__sdt.stop(); window.__sdt.tp(window.__qq.pos, 300); });
    R.takipSonra = await p.evaluate(() => ({ saldiri: window.__qq.rev > window.__sdt.time, rel: window.__sdt.rel(window.__qq), chase: window.__qq.chaseT }));
    // 30 sn bekleme: yeni çağrı hemen gelmiyor
    R.yeniCagri = await p.evaluate(() => window.__hailT.st);
    await ctx.close(); }
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
