const { chromium, devices } = require('playwright');
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const R = {}; const errs = [];
  const pre = JSON.stringify({ kredi: 3000, lv: { lazer: 0, kargo: 0, motor: 0 }, xp: 3000, pilot: 'Test', side: 'korsan', open: [0, 1, 2, 3, 4, 5], grace: 0, fac: { filo: -50, lonca: -20, korsan: 70 } });
  const ctx = await b.newContext({ ...devices['iPhone 13 landscape'], deviceScaleFactor: 1, serviceWorkers: 'block' });
  await ctx.addInitScript(pre => { try { if (!sessionStorage.getItem('i')){ sessionStorage.setItem('i', '1'); localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', 'kayip-yildizlar:test'); localStorage.setItem('kayip-yildizlar:test', pre); } window.__noFbk = 1; } catch (e) {} }, pre);
  const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 200))); const cons = []; p.on('console', m => { if (m.type() !== 'log' || /hata|error/i.test(m.text())) cons.push(m.type() + ': ' + m.text().slice(0, 220)); });
  await p.goto('' + (process.env.BASE || 'http://localhost:8771/') + ''); await p.waitForTimeout(3000);
  await p.tap('#titleGo').catch(() => p.evaluate(() => document.getElementById('titleGo').click())); await p.waitForTimeout(1500);
  let calm = 0; for (let k = 0; k < 40 && calm < 5; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return !!(window.__menuOn || document.getElementById('ctrlSel') || document.getElementById('sideSel')); }); calm = m ? 0 : calm + 1; await p.waitForTimeout(600); }
  await p.waitForTimeout(2000);
  R.basla = await p.evaluate(() => ({ sys: window.__sdt.curSys, docked: window.__sdt.docked, st: window.__sdt.curSt && window.__sdt.curSt.ad }));
  // Kara Liman'a yanaş, Ticaret sekmesinden dokunarak 5 + 5 kaçak al
  await p.evaluate(() => { const t = window.__sdt; if (!t.docked) t.dockAt(t.stations()[0]); });
  for (let i = 0; i < 30; i++){ if (await p.evaluate(() => window.__sdt.docked)) break; await p.waitForTimeout(400); }
  await p.evaluate(() => { const t = document.querySelector('#dtabs [data-t="trade"]'); t && t.click(); }); await p.waitForTimeout(800);
  for (let i = 0; i < 2; i++){ const btn = await p.$('#kacakBox button[data-kc="b5"]'); if (btn) await btn.tap(); await p.waitForTimeout(500); }
  R.alim = await p.evaluate(() => ({ kacak: window.__sdt.save.kacak, kredi: window.__sdt.save.kredi }));
  await p.screenshot({ path: (OUT || '.') + '/1_kara_liman_pazar.png' });
  // Ankora'ya geç, kalk
  await p.evaluate(() => { window.__sdt.undock(); window.__sdt.enter(0); });
  for (let i = 0; i < 60; i++){ if (await p.evaluate(() => window.__sdt.curSys === 0 && !window.__menuOn)) break; await p.waitForTimeout(300); } await p.waitForTimeout(1500);
  await p.evaluate(() => window.__sdt.undock()); await p.waitForTimeout(1500);
  // oyun akıyor mu (hazırlık ekranı vb. bitsin)
  { let t0 = await p.evaluate(() => window.__sdt.time); for (let i = 0; i < 120; i++){ await p.waitForTimeout(500); const r = await p.evaluate(() => ({ t: window.__sdt.time, m: !!window.__menuOn, prep: !!document.getElementById('ckPrep') })); if (r.t > t0 + 1 && !r.m && !r.prep) break; R.bekle = r; } }
  // devriyenin 500 m yakınına git, dur
  R.devriye = await p.evaluate(() => { const t = window.__sdt; const q = t.npcs().find(n => n.role === 'patrol' && !n.hunter && !n.escort); window.__qq = q; const v = q.pos.clone(); v.y += 420; t.tp(v, 0); t.stop(); return q.name; });
  R.durum = await p.evaluate(() => { const t = window.__sdt; return { fac: t.fac(), w: t.save.wanted, grace: t.save.grace, sys: t.curSys, docked: t.docked, dec: window.__pDec(window.__qq), pat: t.npcs().filter(n => n.role === 'patrol').map(n => ({ ad: n.name, rel: t.rel(n), rev: +(n.rev - t.time).toFixed(1), st: n.state, tgt: n.tgt === 'player' ? 'P' : !!n.tgt, hunter: !!n.hunter, chase: n.chaseT, hailT: n.hailT })) }; });
  let st = null; R.iz = []; for (let i = 0; i < 300 && !st; i++){ await p.waitForTimeout(100); const r = await p.evaluate(() => { const t = window.__sdt; t.stop(); const h = t.hp; const atk = t.npcs().filter(n => n.tgt === 'player' || n.rev > t.time).map(n => n.name + ':' + n.role + ':' + n.state + ':' + Math.round(n.pos.distanceTo(window.__qq.pos))); return { st: window.__hailT.st, t: +t.time.toFixed(1), hull: Math.round(h.hull), sh: Math.round(h.shield), atk, dead: !!window.__dead }; }); st = r.st; if (i % 5 === 0 || r.dead) R.iz.push([r.t, r.hull, r.sh, r.atk.join(','), r.st && r.st.ph, r.dead]); if (r.dead) break; }
  R.oyunSaati = await p.evaluate(() => window.__sdt.time);
  const k0b = await p.evaluate(() => window.__sdt.save.kredi); const rb0 = await p.$('#hailBox button[data-h="rs"]'); R.tapOnce = rb0 ? await rb0.isVisible() : 'yok'; if (rb0 && R.tapOnce) await rb0.tap(); await p.waitForTimeout(300);
  R.tapSonra = await p.evaluate(k0 => ({ fark: window.__sdt.save.kredi - k0, kacak: window.__sdt.save.kacak, hl: window.__hailT.st, w: window.__sdt.save.wanted }), k0b);
  R.raf = await p.evaluate(() => new Promise(res => { let n = 0; const t0 = performance.now(); const f = () => { n++; if (performance.now() - t0 < 2000) requestAnimationFrame(f); else res({ n, ov: [...document.body.children].filter(e => { const c = getComputedStyle(e); return c.display !== 'none' && c.visibility !== 'hidden' && +c.opacity > 0.05 && (c.position === 'fixed' || c.position === 'absolute') && +c.zIndex >= 20; }).map(e => e.id + '.' + e.className + ' z' + getComputedStyle(e).zIndex).slice(0, 12), time: window.__sdt.time, docked: window.__sdt.docked, menu: !!window.__menuOn, hid: document.hidden, vis: document.visibilityState }); }; requestAnimationFrame(f); }));
  R.cagri = st; await p.waitForTimeout(400);
  await p.screenshot({ path: (OUT || '.') + '/2_devriye_cagrisi.png', timeout: 8000 }).catch(() => {}); R.ssSaat = await p.evaluate(() => window.__sdt.time);
  R.kutu = await p.evaluate(() => { const h = document.getElementById('hailBox'), r = h.getBoundingClientRect(); return { txt: h.innerText.replace(/\s+/g, ' '), x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height), vw: innerWidth, vh: innerHeight, btns: [...h.querySelectorAll('button')].map(b => { const q = b.getBoundingClientRect(); return b.textContent + ' ' + Math.round(q.width) + 'x' + Math.round(q.height); }) }; });
  const k0 = await p.evaluate(() => window.__sdt.save.kredi);
  const rb = await p.$('#hailBox button[data-h="rs"]'); R.rsGorunur = rb ? await rb.isVisible() : 'yok'; R.rsSaat = await p.evaluate(() => window.__sdt.time); if (rb && R.rsGorunur) await rb.tap(); await p.waitForTimeout(800);
  await p.screenshot({ path: (OUT || '.') + '/3_rusvet_sonrasi.png' }).catch(() => {});
  R.rusvet = await p.evaluate(k0 => ({ fark: window.__sdt.save.kredi - k0, kacak: window.__sdt.save.kacak, hl: window.__hailT.st, w: window.__sdt.save.wanted }), k0);
  await p.screenshot({ path: (OUT || '.') + '/3_rusvet_sonrasi.png' });
  R.errs = errs; R.cons = cons.slice(-12); console.log('@@' + JSON.stringify(R)); await b.close();
})();
