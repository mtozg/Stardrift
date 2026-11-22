// GLB yükleyici prototipi (varsayılan kapalı). Sahte GLB'lerle: kapalıyken iz yok; model yoksa yedek zinciri; model varsa LOD, asteroit örnekleme, sızıntı yok.
const { execSync } = require('child_process'); const fs = require('fs'); const path = require('path');
const boot = require('./_boot');
const FIX = '/tmp/sd_glb_fix'; execSync('python3 ' + path.join(__dirname, 'glb_fixture.py') + ' ' + FIX, { stdio: 'ignore' });
const rota = async (p, fixture) => { await p.route(/models\/glb\//, r => { const f = r.request().url().split('models/glb/')[1].split('?')[0];
  if (!fixture) return r.fulfill({ status: 404, body: '' }); const fp = path.join(FIX, f); if (!fs.existsSync(fp)) return r.fulfill({ status: 404, body: '' });
  r.fulfill({ status: 200, contentType: f.endsWith('.json') ? 'application/json' : 'model/gltf-binary', body: fs.readFileSync(fp) }); }); };
const sizinti = async p => { const geo = () => p.evaluate(() => window.__sdt.memInfo().geo);
  const don = n => p.evaluate(n => { const t = window.__sdt; for (let i = 0; i < n; i++){ const v = t.rigPos(); v.z -= 150; const x = t.spawn('raider', v); t.kill(x); } }, n);
  await don(6); await p.waitForTimeout(2500); const g0 = await geo(); await don(60); await p.waitForTimeout(9000); const g1 = await geo(); return [g0, g1]; };
(async () => {
  const R = {};
  // A) kapalı
  { const { p, b, errs } = await boot({}, '?glb=0'); const reqs = []; p.on('request', r => reqs.push(r.url()));
    await p.evaluate(() => window.__sdt.undock()); await p.waitForTimeout(1500);
    R.kapaliIzYok = await p.evaluate(() => typeof window.__glb === 'undefined') && !reqs.some(u => /glb\.js|models\/glb/.test(u));
    R.geoTaban = await sizinti(p); R.errsA = errs; await b.close(); }
  // B) açık ama model listesi yok (404): yedek zinciri, hata yok
  { const { p, b, errs } = await boot({}, '?glb=1', async pg => rota(pg, false));
    await p.evaluate(() => { const t = window.__sdt; t.undock(); const v = t.rigPos(); v.z -= 150; const n = t.spawn('raider', v); n.state = 'idle'; });
    await p.waitForTimeout(3000);
    const s = await p.evaluate(() => { const g = window.__glb, n = window.__sdt.npcs()[0]; return { var: !!g, dur: g && g.durum(), glbYok: !n._glb, kabuk: n.g.children.filter(c => !c.isSprite).length > 0, bayrak: localStorage.getItem('sd_glb') }; });
    R.modelYokYedek = s.var && s.dur.npcGlb === 0 && s.glbYok && s.kabuk && s.dur.model.length === 0; R.bayrakKalici = s.bayrak === '1'; R.errsB = errs; await b.close(); }
  // C) açık + sahte modeller: LOD, asteroit, istasyon, sızıntı
  { const { p, b, errs } = await boot({}, '?glb=1', async pg => rota(pg, true));
    await p.evaluate(() => { const t = window.__sdt; t.undock(); const v = t.rigPos(); v.z -= 100; const n = t.spawn('raider', v); n.state = 'idle'; n.vel.set(0, 0, 0); window.__n0 = n; });
    await p.waitForFunction(() => window.__n0 && window.__n0._glb, null, { timeout: 40000 }).catch(() => {});
    const d1 = await p.evaluate(() => ({ g: window.__glb.durum(), m: window.__n0._glb ? window.__n0._glb.mode : -9 })); R.npcModelYuklendi = d1.g.yuklenen >= 1 && d1.m === 0;
    const mod = async (off) => p.evaluate(o => { const n = window.__n0, t = window.__sdt, v = t.rigPos(); v.z -= o; n.g.position.copy(v); n.vel.set(0, 0, 0); return null; }, off);
    await mod(26 * 20); await p.waitForFunction(() => window.__n0._glb.mode === 1, null, { timeout: 30000 }).catch(() => {}); const d2 = await p.evaluate(() => ({ m: window.__n0._glb.mode, fb: window.__n0._glb.fb.some(c => c.visible) }));
    await mod(26 * 100); await p.waitForFunction(() => window.__n0._glb.mode === 2, null, { timeout: 30000 }).catch(() => {}); const d3 = await p.evaluate(() => ({ m: window.__n0._glb.mode, fb: window.__n0._glb.fb.every(c => c.visible) }));
    R.lodGecis = d2.m === 1 && !d2.fb && d3.m === 2 && d3.fb; R.diagLod = [d2, d3];
    // asteroit örnekleme
    const ast = await p.evaluate(() => { const t = window.__sdt, a = t.asteroids().find(x => x.type === 'titan') || t.asteroids()[0]; if (!a) return null; const v = a.pos.clone(); v.z += 250; t.tp(v, 0); t.stop(); return { type: a.type, n: t.asteroids().length }; });
    await p.waitForFunction(() => window.__glb.durum().kayaOrnek > 0, null, { timeout: 30000 }).catch(() => {});
    const d4 = await p.evaluate(() => { const g = window.__glb.durum(), A = window.__sdt.asteroids(); return { g, gizli: A.filter(a => a.mesh && a.mesh.isSprite && a.mesh.visible === false).length }; });
    R.asteroitOrnek = !!ast && ast.type === 'titan' ? (d4.g.kayaOrnek > 0 && d4.g.kayaKumeleri >= 1 && d4.g.kayaKumeleri <= 3 && d4.gizli === d4.g.kayaOrnek) : 'titan-yok';
    await p.evaluate(() => { const t = window.__sdt, v = t.rigPos(); v.set(-20000, 0, -20000); t.tp(v, 0); t.stop(); }); await p.waitForFunction(() => { const t = window.__sdt, c = t.rigPos(), y = t.asteroids().filter(a => a.type === 'titan' && a.pos.distanceTo(c) < 1200).length; return window.__glb.durum().kayaOrnek === Math.min(y, 384); }, null, { timeout: 40000 }).catch(() => {});
    const uz = await p.evaluate(() => { const t = window.__sdt, c = t.rigPos(), yakin = t.asteroids().filter(a => a.type === 'titan' && a.pos.distanceTo(c) < 1200).length; return { ornek: window.__glb.durum().kayaOrnek, yakin }; }); R.uzakOrnekYok = uz.ornek === Math.min(uz.yakin, 128 * 3); R.diagUzak = uz;
    // istasyon
    await p.waitForFunction(() => window.__sdt.stations().some(s => s._glb), null, { timeout: 40000 }).catch(() => {});
    R.istasyonModel = await p.evaluate(() => window.__sdt.stations().some(s => s._glb) || 'istasyon-dokusu-gelmedi');
    // sızıntı: 60 doğ/öl; geometri artışı GLB kapalıyken ölçülen tabanı aşmamalı
    const gc = await sizinti(p); R.geoAcik = gc; R.sizintiYok = (gc[1] - gc[0]) <= (R.geoTaban[1] - R.geoTaban[0]) * 1.1 + 8; R.errsC = errs; await b.close(); }
  // D) ?glb=0 bayrağı siler
  { const { p, b, errs } = await boot({}, '?glb=1', async pg => rota(pg, true)); await p.goto((process.env.BASE || 'http://localhost:8771/') + '?glb=0'); await p.waitForTimeout(2500);
    R.glb0Kapatir = await p.evaluate(() => typeof window.__glb === 'undefined' && localStorage.getItem('sd_glb') === '0'); R.errsD = errs; await b.close(); }
  R.errs = [].concat(R.errsA, R.errsB, R.errsC, R.errsD); delete R.errsA; delete R.errsB; delete R.errsC; delete R.errsD;
  console.log('@@' + JSON.stringify(R));
})();
