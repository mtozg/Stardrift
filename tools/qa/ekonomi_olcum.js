// Ekonomi ölçümü (DEĞER DEĞİŞTİRMEZ): etkinlik başına kredi ve XP kazancını test defterinden (window.__ledger) okur.
// Çıktı: @@ ile JSON; docs/EKONOMI_OLCUM.md tablosunun ham verisi. Yazılım çizimiyle çalışır, süre ölçmez, yalnız miktar.
const boot = require('./_boot.js');
(async () => {
  const { p, b, errs } = await boot({ kredi: 0, xp: 0, lv: { lazer: 0, kargo: 0, motor: 0 }, side: process.env.TARAF || 'filo' });
  const R = { satis: {}, oldur: {}, taraf: process.env.TARAF || 'filo' };
  const mark = () => p.evaluate(() => window.__ledger.length);
  const since = n => p.evaluate(n => window.__ledger.slice(n), n);
  const topla = L => { const o = { kredi: 0, xp: 0 }; for (const e of L) o[e.k] += e.d; return o; };
  // 1) İstasyonda cevher satışı (16 birim, her tür)
  for (const ore of ['demir', 'buz', 'titan', 'hurda', 'kristal']){
    await p.evaluate(() => { const t = window.__sdt; if (t.docked) t.undock(); });
    await p.waitForFunction(() => !window.__sdt.docked, null, { timeout: 30000 }).catch(() => {}); await p.waitForTimeout(800);
    await p.evaluate(ore => { const t = window.__sdt; for (const k in t.cargo) t.cargo[k] = 0; t.cargo[ore] = 16; t.dockAt(t.stations()[0]); }, ore);
    await p.waitForFunction(() => window.__sdt.docked, null, { timeout: 30000 }).catch(() => {}); await p.waitForTimeout(800);
    const m = await mark(); await p.evaluate(() => { const b = document.getElementById('sellAll'); b && b.click(); }); await p.waitForTimeout(600);
    R.satis[ore] = topla(await since(m)); R.satis[ore].defter = (await since(m)).map(e => e.k + ' ' + e.d + ' ' + e.s);
  }
  // 2) Öldürme: her korsan türü
  await p.evaluate(() => { const t = window.__sdt; if (t.docked) t.undock(); });
  await p.waitForFunction(() => !window.__sdt.docked, null, { timeout: 30000 }).catch(() => {}); await p.waitForTimeout(1000);
  const N = +(process.env.N || 1);
  for (const ty of ['raider', 'brute', 'reaver', 'leader']){
    const ks = [], xs = []; for (let i = 0; i < N; i++){
    const m = await mark();
    const ok = await p.evaluate(ty => { const t = window.__sdt, v = t.rigPos(); v.z -= 300; try { const n = t.spawn(ty, v); t.kill(n); return true; } catch (e) { return String(e); } }, ty);
    await p.waitForTimeout(500); const L = await since(m); const T = topla(L); ks.push(T.kredi); xs.push(T.xp); if (i === 0) R.oldur[ty] = { ok, defter: L.map(e => e.k + ' ' + e.d + ' ' + e.s) };
    }
    const ort = a => Math.round(a.reduce((x, y) => x + y, 0) / a.length * 10) / 10;
    Object.assign(R.oldur[ty], { n: N, krediOrt: ort(ks), krediMin: Math.min(...ks), krediMax: Math.max(...ks), xpOrt: ort(xs), xpMin: Math.min(...xs), xpMax: Math.max(...xs) });
  }
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
