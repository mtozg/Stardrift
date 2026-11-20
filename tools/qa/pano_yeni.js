// Yeni pano görev türleri: 'kesif' (yeni bölge kareleri) ve 'doldur' (kargoyu doldur).
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const errs = [];
  const pre = JSON.stringify({ kredi: 100, lv: { lazer: 0, kargo: 0, motor: 0 }, xp: 500, pilot: 'Test', side: 'filo', open: [0], grace: 600, fac: { filo: 40, lonca: 10, korsan: -30 }, ct: { offers: [], active: [], t: 0 } });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, serviceWorkers: 'block' });
  await ctx.addInitScript(pre => { try { if (!sessionStorage.getItem('i')){ sessionStorage.setItem('i', '1'); localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', 'kayip-yildizlar:test'); localStorage.setItem('kayip-yildizlar:test', pre); } window.__noFbk = 1; } catch (e) {} }, pre);
  const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 160)));
  await p.goto(process.env.BASE || 'http://localhost:8771/'); await p.waitForTimeout(3000);
  await p.evaluate(() => { const g = document.getElementById('titleGo'); g && g.click(); }); await p.waitForTimeout(1500);
  let calm = 0; for (let k = 0; k < 40 && calm < 5; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return !!(window.__menuOn || document.getElementById('ctrlSel') || document.getElementById('sideSel')); }); calm = m ? 0 : calm + 1; await p.waitForTimeout(600); }
  await p.waitForTimeout(1500);
  const R = {};
  R.sablon = await p.evaluate(() => { const k = window.__yeniT.mkKesif(), d = window.__yeniT.mkDoldur(); return { kesif: [k.type, k.n >= 25 && k.n <= 45, k.reward === 7 * k.n], doldur: [d.type, d.reward, /16 birim/.test(d.txt)] }; });
  await p.evaluate(() => { const t = window.__sdt, s = t.save; t.undock(); const k = window.__yeniT.mkKesif(); k.id = 1; k.prog = 0; const d = window.__yeniT.mkDoldur(); d.id = 2; d.prog = 0; s.ct.active.push(k, d); window.__sdt.stop(); });
  // keşif: uzak bir noktaya git (yeni kareler açılır)
  await p.evaluate(() => { const t = window.__sdt, p0 = t.rigPos(); p0.x += 9000; p0.z += 9000; t.tp(p0, 0); t.stop(); });
  await p.waitForTimeout(6000);
  R.kesifIlerleme = await p.evaluate(() => window.__sdt.save.ct.active.find(c => c.type === 'kesif') ? window.__sdt.save.ct.active.find(c => c.type === 'kesif').prog : 'bitti');
  // doldur: kargoyu doldur
  await p.evaluate(() => { const t = window.__sdt; const cap = t.cargoCap(); t.cargo.titan = cap - 1; t.spawnOre(t.rigPos(), 'titan'); });
  for (let i = 0; i < 40; i++){ await p.waitForTimeout(400); await p.evaluate(() => window.__sdt.stop()); if (await p.evaluate(() => !window.__sdt.save.ct.active.some(c => c.type === 'doldur'))) break; }
  R.doldurBitti = await p.evaluate(() => !window.__sdt.save.ct.active.some(c => c.type === 'doldur'));
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
