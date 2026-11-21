// 3B kokpit döngüsü: Kaşif → Şahin → Yük → Hayalet ×3. Doku/geometri sayıları ikinci ve üçüncü turda aynı kalmalı (sızıntı yok), hata yok.
const boot = require('./_boot');
(async () => {
  const { p, b, errs } = await boot(); const R = { s: [] };
  await p.evaluate(() => { window.__sdt.undock(); });
  for (let r = 0; r < 3; r++) for (const id of ['kasif', 'sahin', 'yuk', 'hayalet']){
    await p.evaluate(id => window.__ckb.swap(id), id); await p.waitForTimeout(7000);
    R.s.push(await p.evaluate(() => { const m = window.__ckb.mem; return window.__ckb.id + ':' + m.textures + '/' + m.geometries; }));
  }
  R.hepsi = ['kasif', 'sahin', 'yuk', 'hayalet'].every(id => R.s.some(x => x.indexOf(id + ':') === 0));
  R.sabit = R.s.slice(4, 8).join() === R.s.slice(8, 12).join();
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
