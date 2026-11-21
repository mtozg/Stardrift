// Oyun sonu E1: İstatistikler bölümü (yalnız okuma) ve Efsane+ etiketi. Kayıt alanı eklenmez.
const boot = require('./_boot.js');
(async () => {
  const { p, b, errs } = await boot({ xp: 40000, kredi: 5000 });
  const R = {};
  R.efsane = await p.evaluate(() => [window.__efsaneP(0), window.__efsaneP(32419), window.__efsaneP(32420), window.__efsaneP(47420), window.__efsaneP(999999)]);
  await p.evaluate(() => { const t = window.__sdt; t.undock && 0; });
  await p.waitForFunction(() => window.__sdt.docked, null, { timeout: 30000 }).catch(() => {});
  const before = await p.evaluate(() => JSON.stringify(Object.keys(window.__sdt.save).sort()));
  const I = await p.evaluate(() => window.__istatistik());
  R.satirSayisi = I.satir.length; R.rutbe = I.satir[0][1];
  await p.evaluate(() => { try { window.renderCt && window.renderCt(); } catch (e) {} });
  const html = await p.evaluate(() => { const bx = document.getElementById('ctBox'); return bx ? bx.textContent : ''; });
  const after = await p.evaluate(() => JSON.stringify(Object.keys(window.__sdt.save).sort()));
  R.kayitAlaniDegismedi = before === after;
  R.atlasMetin = await p.evaluate(() => { const t = window.__kadimMetin(); return Array.isArray(t) && t.length <= 16; });
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
