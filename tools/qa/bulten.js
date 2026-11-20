// İstasyon bülteni (1.63.0): yanaşınca tarafa göre bir bülten satırı çıkar; kayıt değerlerine dokunmaz.
const boot = require('./_boot');
(async () => {
  const R = {};
  for (const [ad, side, pfx] of [['filo', 'filo', 'Filo Bülteni'], ['lonca', 'lonca', 'Lonca Haberleri'], ['korsan', 'korsan', 'Kara Liman Dedikodusu']]){
    const { p, b, errs } = await boot({ side });
    await p.evaluate(() => { const t = window.__sdt; t.dockAt(t.stations()[0]); });
    await p.waitForFunction(() => document.getElementById('bulten'), null, { timeout: 15000 }).catch(() => {});
    const o = await p.evaluate(() => { const e = document.getElementById('bulten'); const s = window.__sdt.save; return { t: e ? e.textContent : null, k: s.kredi, x: s.xp }; });
    R[ad] = { onek: !!o.t && o.t.indexOf(pfx) === 0, bos: !o.t || o.t.indexOf('{u}') >= 0 };
    R.kredi = o.k > 0; R['errs' + ad] = errs;
    await b.close();
  }
  R.errs = [].concat(R.errsfilo, R.errslonca, R.errskorsan); console.log('@@' + JSON.stringify(R));
})();
