const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const errs = []; const R = {};
  const pre = JSON.stringify({ kredi: 5000, lv: { lazer: 0, kargo: 0, motor: 0 }, xp: 3000, side: 'filo', pilot: 'Test', kacak: 4, fac: { filo: 0, lonca: 0, korsan: 50 }, open: [0, 1, 2, 3, 4, 5],
    base: { sys: 0, bi: 0, lv: 1, bank: 0, t: Date.now() }, bases: { 5: { sys: 5, bi: 0, lv: 1, bank: 0, t: Date.now() } } });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, serviceWorkers: 'block' });
  await ctx.addInitScript(pre => { try { if (!sessionStorage.getItem('i')){ sessionStorage.setItem('i', '1'); localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', 'kayip-yildizlar:test'); localStorage.setItem('kayip-yildizlar:test', pre); } window.__noFbk = 1; } catch (e) {} }, pre);
  const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 200)));
  await p.goto('' + (process.env.BASE || 'http://localhost:8771/') + ''); await p.waitForTimeout(3000);
  await p.evaluate(() => { const g = document.getElementById('titleGo'); g && g.click(); }); await p.waitForTimeout(1500);
  let calm = 0; for (let k = 0; k < 40 && calm < 5; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return !!(window.__menuOn || document.getElementById('ctrlSel') || document.getElementById('sideSel')); }); calm = m ? 0 : calm + 1; await p.waitForTimeout(600); }
  const box = () => p.evaluate(() => { const k = document.getElementById('kacakBox'); return { html: k ? k.innerText.replace(/\s+/g, ' ').slice(0, 260) : null, btns: k ? [...k.querySelectorAll('button[data-kc]')].map(b => b.dataset.kc + (b.disabled ? '(d)' : '')) : [] }; });
  const dock = sel => p.evaluate(sel => { const t = window.__sdt; const st = t.stations().find(new Function('s', 'return ' + sel)); if (!st) return 'yok'; t.dockAt(st); t.save.kacak = 4; t.persist(); try { document.querySelector('#dtabs [data-t="trade"]') && document.querySelector('#dtabs [data-t="trade"]').click(); } catch (e) {} return { hedef: st.ad, sys: t.curSys }; }, sel).then(async r => { for (let i = 0; i < 30; i++){ r.curSt = await p.evaluate(() => window.__sdt.docked && window.__sdt.curSt.ad); if (r.curSt === r.hedef) break; await p.waitForTimeout(400); } await p.evaluate(() => { const t = window.__sdt; t.save.kacak = 4; t.persist(); }); await p.waitForTimeout(300); await p.evaluate(() => { try { document.querySelector('#dtabs [data-t="trade"]').click(); } catch (e) {} }); return r; });
  // sistem 0: ana istasyon → satış olmalı
  R.s0main = await dock('s === window.__sdt.stations()[0]'); await p.waitForTimeout(800); R.s0mainBox = await box();
  // sistem 0: üs → satış olmamalı
  R.s0base = await dock('!!s.isBase'); await p.waitForTimeout(800); R.s0baseBox = await box();
  console.log(JSON.stringify(R)); R.dbg = await p.evaluate(() => ({ docked: window.__sdt.docked, st: window.__sdt.curSt.ad, nst: window.__sdt.stations().map(s => s.ad + (s.isBase ? "*" : "")), dcont: !!document.getElementById("dcont"), dock: document.getElementById("dock").className })); console.log(JSON.stringify(R.dbg));
  // üste satış düğmesi zorla tetiklenirse (eski DOM) etkisiz olmalı
  R.forceSell = await p.evaluate(() => { const t = window.__sdt; const k = t.save.kredi, n = t.save.kacak; const btn = document.createElement('button'); btn.dataset.kc = 's'; btn.className = 'act'; document.getElementById('kacakBox').appendChild(btn); btn.click(); return { krediDegisti: t.save.kredi !== k, kacakOnce: n, kacakSonra: t.save.kacak }; });
  // sistem 5'e geç
  await p.evaluate(() => { const t = window.__sdt; t.undock(); t.enter(5); }); await p.waitForTimeout(3000);
  R.s5main = await dock('s === window.__sdt.stations()[0]'); await p.waitForTimeout(800); R.s5mainBox = await box();
  R.s5base = await dock('!!s.isBase'); await p.waitForTimeout(800); R.s5baseBox = await box();
  R.forceBuy = await p.evaluate(() => { const t = window.__sdt; const k = t.save.kredi, n = t.save.kacak; const btn = document.createElement('button'); btn.dataset.kc = 'b1'; btn.className = 'act'; document.getElementById('kacakBox').appendChild(btn); btn.click(); return { krediDegisti: t.save.kredi !== k, kacakOnce: n, kacakSonra: t.save.kacak }; });
  R.errs = errs; console.log("@@" + JSON.stringify(R)); await b.close();
})();
