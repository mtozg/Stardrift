// K50: ölüm ekranı açıkken sayfa yenilenirse kurtarma ücreti açılışta alınır (eskiden yenilemek ücreti atlatıyordu).
const boot = require('./_boot');
(async () => {
  const { p, b, errs } = await boot(); const R = {};
  R.once = await p.evaluate(() => window.__sdt.save.kredi);
  await p.evaluate(() => window.__sdt.wreck());
  await p.waitForFunction(() => { const d = document.querySelector('#death'); return d && /CANLAN/.test(d.innerText); }, null, { timeout: 30000 }).catch(() => {});
  R.dp = await p.evaluate(() => { try { return JSON.parse(localStorage.getItem('kayip-yildizlar:test')).dp; } catch (e) { return null; } });
  await p.reload(); await p.waitForTimeout(6000);
  for (let k = 0; k < 40; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return !!(window.__menuOn || document.getElementById('ctrlSel') || document.getElementById('sideSel')); }); if (!m) break; await p.waitForTimeout(600); }
  await p.waitForFunction(() => window.__sdt && window.__sdt.save, null, { timeout: 30000 }).catch(() => {});
  await p.waitForTimeout(4000);
  R.sonra = await p.evaluate(() => window.__sdt.save.kredi); R.dpSonra = await p.evaluate(() => window.__sdt.save.dp || 0);
  R.fark = R.once - R.sonra;
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
