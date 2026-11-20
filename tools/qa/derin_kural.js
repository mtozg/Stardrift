// K37: "Kadim yankı" sinyali yalnız derin kuşakta (üsten > 12,6 km) ve Korsan dışı taraflarda seçilebilir (ağırlık işlevi evW).
const boot = require('./_boot');
(async () => {
  const { p, b, errs } = await boot(); const R = {};
  const w = async (uz, side) => p.evaluate(([u, s]) => { const t = window.__sdt; t.undock(); const v = t.rigPos(); v.set(u, 0, 0); t.tp(v, 0); t.stop(); t.save.side = s; return window.__evW('derin'); }, [uz, side]);
  R.uzak14k = await w(14000, 'filo');          // derin: ağırlık 2
  R.orta7k = await w(7000, 'filo');            // 1,5 kat kuşağı: 0
  R.yakin3k = await w(3000, 'filo');           // 0
  R.sinirAlti = await w(12500, 'filo');        // eşiğin hemen altı: 0
  R.sinirUstu = await w(12700, 'filo');        // eşiğin hemen üstü: 2
  R.lonca14k = await w(14000, 'lonca');        // Lonca da alır: 2
  R.korsan14k = await w(14000, 'korsan');      // Korsan'a çıkmaz: 0
  R.baskasiEtkilenmedi = await p.evaluate(() => window.__evW('kamp') + ':' + window.__evW('yardim'));   // korsan tarafında kamp (noK) 0, yardım (noK) 0
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
