// K38: ölüm bedeli = min(kredi, max(50, min(2000, yuvarla(kredi × %10)))). Alt sınır 50, %10 aralığı, üst sınır 2000.
const boot = require('./_boot');
(async () => {
  const { p, b, errs } = await boot(); const R = {};
  for (const k of [0, 30, 50, 200, 500, 600, 1000, 8000, 19999, 25000, 999999])
    R['k' + k] = await p.evaluate(k => { window.__sdt.save.kredi = k; return window.__feeT(); }, k);   // aynı çağrıda: test modunun kredi doldurması araya giremez
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
