const { chromium } = require('playwright');
const URL = '' + (process.env.BASE || 'http://localhost:8771/') + '';
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const R = {}; const errs = [];
  async function boot(pre, opt = {}){
    const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, serviceWorkers: 'block' });
    await ctx.addInitScript(pre => { try { if (!sessionStorage.getItem('i')){ sessionStorage.setItem('i', '1'); localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', 'kayip-yildizlar:test'); if (pre) localStorage.setItem('kayip-yildizlar:test', pre); } window.__noFbk = 1; } catch (e) {} }, pre ? JSON.stringify(pre) : null);
    const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 200)));
    const toasts = []; await p.exposeFunction('__tl', t => toasts.push(t));
    if (opt.block) await p.route(opt.block, r => r.abort());
    await p.goto(URL); await p.waitForTimeout(3000);
    await p.evaluate(() => { const t = document.getElementById('toast'); if (t) new MutationObserver(() => window.__tl(t.textContent)).observe(t, { childList: true, characterData: true, subtree: true }); const g = document.getElementById('titleGo'); g && g.click(); }); await p.waitForTimeout(1500);
    let calm = 0; for (let k = 0; k < 40 && calm < 5; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return !!(window.__menuOn || document.getElementById('ctrlSel') || document.getElementById('sideSel')); }); calm = m ? 0 : calm + 1; await p.waitForTimeout(600); }
    return { ctx, p, toasts };
  }
  const base = { kredi: 5000, lv: { lazer: 0, kargo: 0, motor: 0 }, xp: 3000, pilot: 'Test' };
  // K6 göç
  { const { ctx, p } = await boot(Object.assign({}, base, { side: 'korsan', fac: { filo: -65, lonca: -20, korsan: 50 }, st: { avci: 0 } })); R.gocTemiz = await p.evaluate(() => window.__sdt.fac().filo); await ctx.close(); }
  { const { ctx, p } = await boot(Object.assign({}, base, { side: 'korsan', fac: { filo: -65, lonca: -20, korsan: 50 }, st: { avci: 2 } })); R.gocAvci = await p.evaluate(() => window.__sdt.fac().filo); await ctx.close(); }
  { const { ctx, p } = await boot(Object.assign({}, base, { side: 'korsan', sideN: 1, fac: { filo: -65, lonca: -20, korsan: 50 } })); R.gocHain = await p.evaluate(() => window.__sdt.fac().filo); await ctx.close(); }
  { const { ctx, p } = await boot(Object.assign({}, base, { side: 'korsan', fac: { filo: -80, lonca: -20, korsan: 50 } })); R.gocKotu = await p.evaluate(() => window.__sdt.fac().filo); await ctx.close(); }
  // 1-B renk: korsan, devriyeler tetikte
  { const { ctx, p } = await boot(Object.assign({}, base, { side: 'korsan', fac: { filo: -50, lonca: -20, korsan: 50 }, grace: 600, open: [0, 1, 2, 3, 4, 5] }));
    await p.evaluate(() => window.__sdt.enter(0)); await p.waitForTimeout(4000);
    R.korsanRel = await p.evaluate(() => { const t = window.__sdt, c = {}; for (const n of t.npcs()){ const k = n.role + ':' + t.rel(n); c[k] = (c[k] || 0) + 1; } return c; });
    // 1-A: sıçrama mesajında bölge
    await p.evaluate(() => window.__sdt.enter(1)); await p.waitForTimeout(2500); await ctx.close(); }
  { const { ctx, p, toasts } = await boot(Object.assign({}, base, { side: 'filo', fac: { filo: 40, lonca: 10, korsan: -30 }, open: [0, 1, 2, 3], boss: [0, 1, 2] }));
    R.filoRel = await p.evaluate(() => { const t = window.__sdt, c = {}; for (const n of t.npcs()){ const k = n.role + ':' + t.rel(n); c[k] = (c[k] || 0) + 1; } return c; });
    // S1-11: ücra kapı işareti (3 patron, Morr yok, Ankora)
    await p.waitForTimeout(1000); R.ucraIsaret = await p.evaluate(() => (window.__featMap ? window.__featMap() : []).filter(f => f && f.gate).map(f => f.label));
    await p.evaluate(() => window.__sdt.enter(1)); await p.waitForTimeout(2500); R.sicramaToast = toasts.filter(t => /Sıçrama/.test(t)).slice(-1)[0] || null; await ctx.close(); }
  { const { ctx, p } = await boot(Object.assign({}, base, { side: 'filo', fac: { filo: 40, lonca: 10, korsan: -30 }, boss: [0, 1, 2, 5] })); await p.waitForTimeout(1000);
    R.ucraIsaretMorrYenik = await p.evaluate(() => (window.__featMap ? window.__featMap() : []).filter(f => f && f.gate).map(f => f.label)); await ctx.close(); }
  // K14: GLB engelli → bildirim, sonra toparlanma
  { const { ctx, p, toasts } = await boot(Object.assign({}, base, { side: 'filo', fac: { filo: 40, lonca: 10, korsan: -30 } }), { block: '**/models/cockpit_kasif*.glb*' });
    await p.waitForTimeout(36000); R.k14Uyari = toasts.filter(t => /Kokpit/.test(t));
    await p.unroute('**/models/cockpit_kasif*.glb*'); await p.waitForTimeout(25000); R.k14Sonra = toasts.filter(t => /Kokpit/.test(t)); R.k14Hazir = await p.evaluate(() => !!(window.__ckb && window.__ckb.ready)); await ctx.close(); }
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
