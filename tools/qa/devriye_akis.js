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
  const base = { kredi: 5000, lv: { lazer: 0, kargo: 0, motor: 0 }, xp: 3000, pilot: 'Test', open: [0, 1, 2, 3, 4, 5], grace: 0 };
  const nearPatrol = p => p.evaluate(() => { const t = window.__sdt; const q = t.npcs().find(n => n.role === 'patrol' && !n.hunter && !n.escort); if (!q) return null; const v = q.pos.clone(); v.y += 420; t.tp(v, 0); t.stop(); return q.name; });
  // karar tablosu
  { const { ctx, p } = await boot(Object.assign({}, base, { side: 'filo', fac: { filo: 40, lonca: 10, korsan: -30 } }));
    R.tablo = await p.evaluate(async () => { const t = window.__sdt, out = {}; const q = {}; const cases = [['temiz', 0, 0, 40], ['kacak', 0, 4, 40], ['w2', 2, 0, 40], ['w3', 3, 0, 40], ['dusuk', 0, 0, -70]];
      for (const k of [0, 1, 3, 4]){ t.enter(k); for (let i = 0; i < 40 && t.curSys !== k; i++) await new Promise(r => setTimeout(r, 300)); await new Promise(r => setTimeout(r, 300)); out['sys' + k] = t.curSys; for (const [ad, w, kc, f] of cases){ t.save.wanted = w; t.save.kacak = kc; t.save.fac.filo = f; const qq = {}; out[k + ':' + ad] = window.__pDec(qq); } }
      t.save.wanted = 0; t.save.kacak = 0; t.save.fac.filo = 40; t.enter(0); return out; });
    await ctx.close(); }
  // 1) Filo, kaçak 4, Ankora → çağrı → uy → tarama → sonuç
  { const { ctx, p } = await boot(Object.assign({}, base, { side: 'filo', kacak: 4, fac: { filo: 40, lonca: 10, korsan: -30 } }));
    R.uyDevriye = await nearPatrol(p); let st = null; for (let i = 0; i < 100 && !st; i++){ await p.waitForTimeout(100); st = await p.evaluate(() => { window.__sdt.stop(); return window.__hailT.st; }); } R.uyCagri = st;
    R.uyKutu = await p.evaluate(() => document.getElementById('hailBox').innerText.replace(/\s+/g, ' '));
    await p.evaluate(() => document.querySelector('#hailBox button[data-h="uy"]').dispatchEvent(new PointerEvent('pointerdown', { bubbles: true })));
    const t0 = await p.evaluate(() => window.__sdt.time); R.uyIz = [];
    for (let i = 0; i < 120; i++){ const r = await p.evaluate(() => { window.__sdt.stop(); return { t: window.__sdt.time, hl: window.__hailT.st }; }); if (i % 10 === 0) R.uyIz.push([+(r.t - t0).toFixed(1), r.hl && r.hl.ph]); if (!r.hl) break; await p.waitForTimeout(400); } R.uySonra = await p.evaluate(() => ({ hl: window.__hailT.st, kacak: window.__sdt.save.kacak, wanted: window.__sdt.save.wanted }));
    await ctx.close(); }
  // 2) Korsan, kaçak 10, Ankora → rüşvet
  { const { ctx, p } = await boot(Object.assign({}, base, { side: 'korsan', kacak: 10, fac: { filo: -50, lonca: -20, korsan: 50 } }));
    await p.evaluate(() => window.__sdt.enter(0)); for (let i = 0; i < 40; i++){ if (await p.evaluate(() => window.__sdt.curSys === 0 && !window.__menuOn)) break; await p.waitForTimeout(300); } await p.waitForTimeout(2500);
    await nearPatrol(p); let st = null; for (let i = 0; i < 30 && !st; i++){ await p.waitForTimeout(500); st = await p.evaluate(() => window.__hailT.st); } R.rsCagri = st;
    R.rsKutu = await p.evaluate(() => document.getElementById('hailBox').innerText.replace(/\s+/g, ' '));
    R.rsFiyat = await p.evaluate(() => window.__hailT.bribeP()); const k0 = await p.evaluate(() => window.__sdt.save.kredi);
    await p.evaluate(() => { const b = document.querySelector('#hailBox button[data-h="rs"]'); b && b.click(); }); await p.waitForTimeout(500);
    R.rsSonra = await p.evaluate(k0 => ({ hl: window.__hailT.st, kacak: window.__sdt.save.kacak, krediFark: window.__sdt.save.kredi - k0 }), k0);
    // tüccar kaçışı
    R.tuccar = await p.evaluate(async () => { const t = window.__sdt; const n = t.npcs().find(x => x.role === 'trader' && !x.sg); if (!n) return null; t.tp(n.pos, 300); await new Promise(r => setTimeout(r, 1500)); return { state: n.state, alert: n.alertT > 0 }; });
    await ctx.close(); }
  // 3) Filo, aranma 1, Ankora → kaç → aranma +1, takip, 20 sn sonra saldırı
  { const { ctx, p } = await boot(Object.assign({}, base, { side: 'filo', wanted: 1, fac: { filo: 40, lonca: 10, korsan: -30 } }));
    const ad = await nearPatrol(p); let st = null; for (let i = 0; i < 20 && !st; i++){ await p.waitForTimeout(500); st = await p.evaluate(() => window.__hailT.st); } R.kacCagri = st;
    await p.evaluate(() => document.querySelector('#hailBox button[data-h="kac"]').dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }))); await p.waitForTimeout(300);
    R.kacHemen = await p.evaluate(ad => { const q = window.__sdt.npcs().find(n => n.name === ad); return { wanted: window.__sdt.save.wanted, chase: q && q.chaseT > 0 }; }, ad);
    { const t0 = await p.evaluate(() => window.__sdt.time); for (let i = 0; i < 200; i++){ const t = await p.evaluate(() => { window.__sdt.stop(); return window.__sdt.time; }); if (t - t0 > 22) break; await p.waitForTimeout(400); } R.kacOyunSn = +(await p.evaluate(() => window.__sdt.time) - t0).toFixed(1); }
    R.kacSonra = await p.evaluate(ad => { const q = window.__sdt.npcs().find(n => n.name === ad); return q ? { saldiri: q.rev > 0, rel: window.__sdt.rel(q) } : 'yok'; }, ad);
    await ctx.close(); }
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
