// İstasyon menüsü: yetenek ağacı sekmelerin altında açılır (tam ekran değil); başka sekme ağacı kapatır; uçuştan kalan uyarı menüye taşınmaz.
const boot = require('./_boot.js');
(async () => {
  const { p, b, errs } = await boot({ sp: 3, xp: 3000 });
  const R = {};
  await p.evaluate(() => { const t = window.__sdt; t.undock && t.undock(); document.getElementById('toast').textContent = 'uçuş uyarısı'; document.getElementById('toast').classList.add('on'); });
  await p.evaluate(() => { const t = window.__sdt; t.dockAt(t.stations()[0]); });
  await p.waitForTimeout(2500);
  R.uyariTemiz = await p.evaluate(() => !document.getElementById('toast').classList.contains('on'));
  await p.click('#dock button[data-t="up"]'); await p.waitForTimeout(1500);
  const g = await p.evaluate(() => { const r = e => { const x = document.querySelector(e); if (!x) return null; const q = x.getBoundingClientRect(); return { x: q.x, y: q.y, w: q.width, h: q.height }; }; return { sk: r('#skModal'), tab: r('#dock button[data-t="up"]'), on: document.getElementById('skModal').classList.contains('on'), ind: document.getElementById('skModal').classList.contains('indock'), upOn: document.querySelector('#dock button[data-t="up"]').classList.contains('on') }; });
  R.menudeAcildi = !!(g.on && g.ind);
  R.sekmelerGorunur = !!(g.sk && g.tab && g.sk.y >= g.tab.y + g.tab.h);
  R.tamEkranDegil = !!(g.sk && g.sk.h < 720 - 80);
  R.sekmeVurgusu = !!g.upOn;
  await p.click('#dock button[data-t="trade"]'); await p.waitForTimeout(900);
  R.baskaSekmeKapatir = await p.evaluate(() => !document.getElementById('skModal').classList.contains('on'));
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
