// Oyun içi 3B kokpit testi (Playwright, swiftshader). Kullanım: repo kökünde `python3 -m http.server 8765` çalışırken
//   node tools/asset_factory/qc/ingame_cockpit.js <çıktı_klasörü>
// Kontroller (gemi başına): model yüklendi mi (masaüstü/telefon dosyası), ekran mesh'leri canlı tuvallere bağlı mı, kamera hizası
// (GLB ekran köşeleri ↔ CK3 dörtgenleri, px), RADAR tuval oranı, çizim çağrısı/üçgen/süre, gemi değişiminde eski modelin bırakılması,
// Şahin modeli engellenince çizim kokpitine dönüş. Kaşif davranışı aynı kalmalı.
const { chromium, devices } = require('playwright'); const fs = require('fs');
const OUT = process.argv[2] || '/tmp'; fs.mkdirSync(OUT, { recursive: true });
const DEV = { 'masaüstü': { viewport: { width: 1600, height: 800 } }, 'iPad Pro 11 landscape': devices['iPad Pro 11 landscape'], 'iPhone 13 landscape': devices['iPhone 13 landscape'], 'Pixel 7 landscape': devices['Pixel 7 landscape'] };
async function boot(b, dev, block){
  const ctx = await b.newContext({ ...DEV[dev], serviceWorkers: 'block' });
  await ctx.addInitScript(() => { try { localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', 'kayip-yildizlar:test'); window.__noFbk = 1; } catch (e) {} });
  const p = await ctx.newPage(); const log = []; p.on('pageerror', e => log.push('PE ' + e.message.slice(0, 200))); p.on('console', m => { if (/kokpit|hata|Error/i.test(m.text())) log.push('C ' + m.text().slice(0, 160)); });
  const glb = []; p.on('request', r => { if (/\.glb/.test(r.url())) glb.push(r.url().replace(/^.*\/models\//, '').replace(/\?.*$/, '')); });
  if (block) await p.route(block, r => r.abort());
  await p.goto('http://localhost:8765/'); await p.waitForTimeout(2500);
  await p.evaluate(() => document.getElementById('titleGo').click()); await p.waitForTimeout(1500);
  await p.evaluate(() => { const i = document.getElementById('ssName'); if (i) i.value = 'Test'; const k = document.querySelector('#sideSel .c[data-k="filo"] .pk'); k && k.click(); }); await p.waitForTimeout(1200);
  for (let k = 0; k < 8; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return window.__menuOn; }); if (!m && k > 2) break; await p.waitForTimeout(600); }
  return { ctx, p, log, glb };
}
const setShip = (p, id) => p.evaluate(id => window.__ckb.swap(id), id);
async function waitReady(p, id, ms){ const t0 = Date.now(); while (Date.now() - t0 < ms){ const r = await p.evaluate(id => window.__ckb && window.__ckb.id === id && window.__ckb.ready && !!window.__ck3on, id); if (r) return true; await p.waitForTimeout(500); } return false; }
function measure(p, id){
  return p.evaluate(id => { const B = window.__ckb, k = B.k, v = B.view, out = { id: B.id, ready: B.ready, failed: B.failed, ck3on: !!window.__ck3on };
    if (!k) return out; out.scr = k.scr.map(e => ({ kind: e.kind, canvas: e.tx.image ? [e.tx.image.width, e.tx.image.height] : null }));
    const m = B.scr.find(s => s.kind === 'map'); out.radarCanvasAspect = m ? +(m.cv.width / m.cv.height).toFixed(3) : null; out.radarLogical = m ? [m.lw, m.lh] : null;
    out.calls = B.stat.calls; out.tris = B.stat.tris; out.ms = +B.stat.ms.toFixed(2); out.texMem = B.mem.textures; out.geoMem = B.mem.geometries;
    const Q = B.quads, s = (v.H - v.OY) / 416.5, names = { SCR_SYS: 0, SCR_RADAR: 1, SCR_HULL: 2 }, err = {}; const swayNow = [B.sway.x, B.sway.y];
    for (const e of k.scr){ const q = Q[names[e.o.name]]; e.o.updateMatrixWorld(true); const pos = e.o.geometry.attributes.position, got = [];
      for (let i = 0; i < pos.count; i++){ const w = new THREE.Vector3().fromBufferAttribute(pos, i).applyMatrix4(e.o.matrixWorld).project(k.cam); got.push([(w.x * 0.5 + 0.5) * v.W, (1 - (w.y * 0.5 + 0.5)) * v.H]); }
      const fpx = 435.3 * s, ox = -swayNow[0] * 1.08, oy = swayNow[1] * 1.08;   /* sallanma kafa ötelemesi: beklenen konuma derinliğe bağlı kayma eklenir → hizayı sallanmasız ölç */
      let mx = 0; q.forEach(c => { const ex = v.OX + (c[0] - 800) * s, ey = v.OY + (c[1] - 239.5) * s; let best = 1e9; got.forEach(g => { best = Math.min(best, Math.hypot(g[0] - ex, g[1] - ey)); }); mx = Math.max(mx, best); }); err[e.o.name] = +mx.toFixed(2); }
    out.alignErrPx = err; out.sway = swayNow.map(x => +x.toFixed(2)); out.view = v; return out; }, id);
}
const still = p => p.evaluate(() => { try { window.__ckb.sway.x = 0; window.__ckb.sway.y = 0; } catch (e) {} });
(async () => { const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const res = {};
  for (const dev of Object.keys(DEV)){
    const { ctx, p, log, glb } = await boot(b, dev, null); const R = {};
    R.kasif_ok = await waitReady(p, 'kasif', 60000); await still(p); await p.waitForTimeout(300); R.kasif = await measure(p, 'kasif'); await p.screenshot({ path: OUT + '/kasif_' + dev.replace(/\s+/g, '_') + '.png' });
    await setShip(p, 'sahin'); R.sahin_ok = await waitReady(p, 'sahin', 60000); await p.waitForTimeout(1500); await still(p); await p.waitForTimeout(300); R.sahin = await measure(p, 'sahin'); await p.screenshot({ path: OUT + '/sahin_' + dev.replace(/\s+/g, '_') + '.png' });
    await setShip(p, 'kasif'); R.back_ok = await waitReady(p, 'kasif', 60000); await p.waitForTimeout(1000); R.back = await measure(p, 'kasif');
    R.glbRequests = glb; R.log = log.slice(0, 8); res[dev] = R;
    console.log(dev, JSON.stringify({ kasif: R.kasif_ok, sahin: R.sahin_ok, geri: R.back_ok, glb, hizaS: R.sahin.alignErrPx, hizaK: R.kasif.alignErrPx, radar: R.sahin.radarCanvasAspect, calls: R.sahin.calls, tris: R.sahin.tris, tex: [R.kasif.texMem, R.sahin.texMem, R.back.texMem], log: R.log }));
    await ctx.close(); }
  // fallback: Şahin modeli engellenir → çizim kokpiti (ck_sahin.webp)
  { const { ctx, p, log } = await boot(b, 'iPad Pro 11 landscape', '**/models/cockpit_sahin*.glb*'); await waitReady(p, 'kasif', 60000); await setShip(p, 'sahin'); await p.waitForTimeout(6000);
    const r = await p.evaluate(() => ({ failed: window.__ckb.failed, ck3on: !!window.__ck3on, ck3wait: !!window.__ck3wait, off: !!window.__ckb.off.sahin, img2d: /ck_sahin/.test(window.__ckb.img2d), menuOn: !!window.__menuOn })); res.fallback = { ...r, log: log.slice(0, 5) };
    console.log('fallback', JSON.stringify(res.fallback)); await p.screenshot({ path: OUT + '/sahin_fallback.png' }); await ctx.close(); }
  fs.writeFileSync(OUT + '/ingame_result.json', JSON.stringify(res, null, 1)); await b.close(); })();
