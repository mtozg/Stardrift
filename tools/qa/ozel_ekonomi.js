// K30 başlangıç kargosu 16, K31 kaçak satışından birim başına 5 XP, K32 unvanla açılan özel görevler (2. kademe).
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const R = {}; const errs = [];
  async function boot(side, lq, extra){
    const pre = JSON.stringify(Object.assign({ kredi: 1000, lv: { lazer: 0, kargo: 0, motor: 0 }, xp: 500, pilot: 'Test', side, open: [0], grace: 600, lq,
      fac: { filo: 40, lonca: 10, korsan: side === 'korsan' ? 60 : -30 }, ct: { offers: [], active: [], t: 0 } }, extra || {}));
    const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, serviceWorkers: 'block' });
    await ctx.addInitScript(pre => { try { if (!sessionStorage.getItem('i')){ sessionStorage.setItem('i', '1'); localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', 'kayip-yildizlar:test'); localStorage.setItem('kayip-yildizlar:test', pre); } window.__noFbk = 1; } catch (e) {} }, pre);
    const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 160)));
    await p.goto(process.env.BASE || 'http://localhost:8771/'); await p.waitForTimeout(3000);
    await p.evaluate(() => { const g = document.getElementById('titleGo'); g && g.click(); }); await p.waitForTimeout(1500);
    let calm = 0; for (let k = 0; k < 40 && calm < 5; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return !!(window.__menuOn || document.getElementById('ctrlSel') || document.getElementById('sideSel')); }); calm = m ? 0 : calm + 1; await p.waitForTimeout(600); }
    await p.waitForTimeout(1500); return { ctx, p };
  }
  { const { ctx, p } = await boot('filo', { filo: 2 });
    R.kargoKasif = await p.evaluate(() => window.__sdt.cargoCap());
    R.filoT1 = await p.evaluate(() => { window.__ozelT.gen(); const o = window.__sdt.save.ct.offers; return { n: o.length, t1: o[1].type, ks: o[1].ks, ozel: !!o[1].ozel, txt: o[1].txt }; });
    // yakında öldürme sayılmaz, 3 km ötede sayılır
    R.ilerleme = await p.evaluate(() => { const t = window.__sdt, s = t.save; const c = s.ct.offers[1]; s.ct.active.push(s.ct.offers.splice(1, 1)[0]);
      const st = t.stations()[0].pos; const a = t.spawn('raider', st.clone().add(st.clone().set(0, 0, 500))), b2 = t.spawn('raider', st.clone().add(st.clone().set(0, 0, 9000))); const out = {};
      t.kill(a); out.yakin = s.ct.active[0].prog;
      t.kill(b2); out.uzak = s.ct.active[0].prog; return out; });
    await ctx.close(); }
  { const { ctx, p } = await boot('filo', { filo: 1 }); R.filoT0 = await p.evaluate(() => { window.__ozelT.gen(); const o = window.__sdt.save.ct.offers; return !!o[1].ozel; }); await ctx.close(); }
  { const { ctx, p } = await boot('lonca', { lonca: 3 }); R.lonca = await p.evaluate(() => { window.__ozelT.gen(); const o = window.__sdt.save.ct.offers; return { t: o[1].type, toplu: /Toplu sipariş/.test(o[1].txt), n: o[1].n }; }); await ctx.close(); }
  { const { ctx, p } = await boot('korsan', { korsan: 4 }, { kacak: 4, fac: { filo: -50, lonca: -20, korsan: 60 } });
    R.korsan = await p.evaluate(() => { window.__ozelT.gen(); const o = window.__sdt.save.ct.offers; return { t: o[1].type, ks: o[1].ks }; });
    // kaçak satışı XP (Kara Liman dışı istasyon)
    await p.evaluate(() => { window.__sdt.enter(0); }); for (let i = 0; i < 60; i++){ if (await p.evaluate(() => window.__sdt.curSys === 0 && !window.__menuOn)) break; await p.waitForTimeout(300); } await p.waitForTimeout(2000);
    await p.evaluate(() => { const t = window.__sdt; t.undock(); t.dockAt(t.stations()[0]); });
    for (let i = 0; i < 40; i++){ if (await p.evaluate(() => window.__sdt.docked)) break; await p.waitForTimeout(400); }
    await p.evaluate(() => { const t = window.__sdt; t.save.kacak = 4; t.persist(); document.querySelector('#dtabs [data-t="trade"]') && document.querySelector('#dtabs [data-t="trade"]').click(); }); await p.waitForTimeout(800);
    R.kacakXp = await p.evaluate(() => { const t = window.__sdt, x0 = t.save.xp; const b = document.querySelector('#kacakBox button[data-kc="s"]'); if (!b) return 'dugme yok'; b.click(); return { fark: t.save.xp - x0, kacak: t.save.kacak }; });
    await ctx.close(); }
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
