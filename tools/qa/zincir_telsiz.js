// 1.63.1: taraf zincirinin tek numaralı adımlarında telsiz sahnesi; çift adım (unvan adımı) sahne vermez.
const boot = require('./_boot');
(async () => {
  const R = {}; const { p, b, errs } = await boot({ side: 'korsan' });
  const radyo = () => p.evaluate(() => Array.from(document.querySelectorAll('#radio .rl')).map(e => e.textContent).join('|'));
  await p.evaluate(() => window.__chainSay('korsan', 1)); await p.waitForTimeout(3800);
  R.korsan1 = (await radyo()).indexOf('Kara Liman: İşin sessiz') >= 0;
  await p.evaluate(() => window.__chainSay('filo', 3)); await p.waitForTimeout(3800);
  R.filo3 = (await radyo()).indexOf('Ana karargah: Raporların') >= 0;
  await p.evaluate(() => window.__chainSay('lonca', 2)); await p.waitForTimeout(3800);
  R.cift = (await radyo()).indexOf('Lonca masası') < 0;
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
