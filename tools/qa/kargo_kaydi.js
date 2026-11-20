const { chromium } = require('playwright');
const URL = '' + (process.env.BASE || 'http://localhost:8771/') + '';
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const R = {}; const errs = [];
  async function page(key, pre){
    const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, serviceWorkers: 'block' });
    await ctx.addInitScript(([k, pre]) => { try { if (!sessionStorage.getItem('init')){ sessionStorage.setItem('init', '1'); localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', k); if (pre) localStorage.setItem(k, pre); } window.__noFbk = 1; } catch (e) {} }, [key, pre || null]);
    const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 160)));
    await p.goto(URL); await p.waitForTimeout(4000); return { ctx, p };
  }
  const C = p => p.evaluate(() => { const t = window.__sdt; return { cargo: { ...t.cargo }, same: t.save.cargo === t.cargo, ship: t.save.ship, stored: JSON.parse(localStorage.getItem('kayip-yildizlar:test')).cargo }; });
  // 1) eski kayıt (cargo alanı yok)
  { const old = JSON.stringify({ kredi: 500, lv: { lazer: 0, kargo: 0, motor: 0 }, xp: 100 });
    const { ctx, p } = await page('kayip-yildizlar:test', old); R.eski = await C(p);
    // 2) kalıcılık: kargo + kredi birlikte, persist ile
    await p.evaluate(() => { const t = window.__sdt; t.cargo.titan = 5; t.cargo.demir = 2; t.persist(); });
    await p.reload(); await p.waitForTimeout(4000); R.yenile = await C(p);
    // 3) persist çağrılmadan pagehide ile
    await p.evaluate(() => { window.__sdt.cargo.hurda = 3; });
    await p.reload(); await p.waitForTimeout(4000); R.pagehide = await C(p);
    // 4) satış benzetimi: kargo sıfır + kredi artışı tek persist
    await p.evaluate(() => { const t = window.__sdt; for (const k in t.cargo) t.cargo[k] = 0; t.persist(); });
    await p.reload(); await p.waitForTimeout(4000); R.satYenile = await C(p);
    // 5) gemi değişimi: kapasite aşımı engeli
    await p.evaluate(() => { const t = window.__sdt; t.save.ships = ['kasif', 'sahin']; t.cargo.titan = 12; t.persist(); });
    R.gemi = await p.evaluate(() => { const t = window.__sdt; const r = t.hgAct('use:s:sahin'); return { r, ship: t.save.ship, sum: t.cargoSum(), capNow: t.cargoCap() }; });
    await p.evaluate(() => { window.__sdt.cargo.titan = 3; });
    R.gemi2 = await p.evaluate(() => { const t = window.__sdt; t.hgAct('use:s:sahin'); return { ship: t.save.ship, sum: t.cargoSum(), cap: t.cargoCap() }; });
    await ctx.close(); }
  // 6) bozuk değerler
  { const bad = JSON.stringify({ kredi: 10, lv: { lazer: 0, kargo: 0, motor: 0 }, cargo: { titan: -5, demir: 'abc', kristal: 1e9, buz: 2.7, foo: 3 } });
    const { ctx, p } = await page('kayip-yildizlar:test', bad); R.bozuk = await C(p); R.bozukFoo = await p.evaluate(() => 'foo' in window.__sdt.cargo); await ctx.close(); }
  { const { ctx, p } = await page('kayip-yildizlar', null); R.gercekHook = await p.evaluate(() => typeof window.__sdt); await ctx.close(); }
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
