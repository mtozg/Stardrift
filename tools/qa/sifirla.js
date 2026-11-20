// Oyunu sıfırla (1.63.3): yanlış yazıda silmez, "SIFIRLA" yazınca yerel kaydı siler ve oyunu yeniden açar.
const boot = require('./_boot');
(async () => {
  const { p, b, errs } = await boot({ pilot: 'Eski Pilot', xp: 777 }); const R = {};
  const KEY = 'kayip-yildizlar:test';
  R.oncePilot = await p.evaluate(k => { try { return JSON.parse(localStorage.getItem(k)).pilot; } catch (e) { return null; } }, KEY);
  await p.evaluate(() => window.__openSet());
  await p.waitForSelector('button[data-set="reset"]', { state: 'attached', timeout: 10000 });
  await p.evaluate(() => { const b = document.querySelector('button[data-set="reset"]'); b.scrollIntoView(); b.click(); });
  await p.waitForSelector('#resetBox', { timeout: 5000 });
  await p.fill('#rsI', 'yanlis'); await p.click('#rsGo'); await p.waitForTimeout(500);
  R.yanlisHata = await p.evaluate(() => (document.getElementById('rsE') || {}).textContent.length > 0);
  R.yanlisKutuAcik = await p.evaluate(() => !!document.getElementById('resetBox'));
  R.yanlisKayitDuruyor = await p.evaluate(k => { try { return JSON.parse(localStorage.getItem(k)).pilot; } catch (e) { return null; } }, KEY);
  await p.fill('#rsI', 'sifirla');
  await Promise.all([p.waitForNavigation({ timeout: 30000 }).catch(() => {}), p.click('#rsGo')]);
  await p.waitForTimeout(2500);
  R.sonra = await p.evaluate(k => { try { const o = JSON.parse(localStorage.getItem(k)); return o ? (o.pilot === 'Eski Pilot' ? 'eski' : 'yeni') : 'yok'; } catch (e) { return 'yok'; } }, KEY);
  R.sonraTemiz = R.sonra !== 'eski'; R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
