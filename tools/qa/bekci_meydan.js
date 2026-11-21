// Oyun sonu E1: Bekçi meydan okuması. Bekçi yenildikten sonra isteğe bağlı; Gümüş ve Altın rozet kademesi; ödül yalnız rozet (gWin kredi/XP yazmaz).
const boot = require('./_boot.js');
(async () => {
  const { p, b, errs } = await boot({ bekci: 1, side: 'filo' });
  const R = {};
  await p.evaluate(() => { const t = window.__sdt; if (t.docked) t.undock(); });
  await p.waitForFunction(() => !window.__sdt.docked, null, { timeout: 30000 }).catch(() => {}); await p.waitForTimeout(1500);
  R.kapaliBekciYok = await p.evaluate(() => { const d = window.__bekciDbg(); return !d.active && !d.G; });
  await p.evaluate(() => { const t = window.__sdt; t.save.bekciOn = 1; const d = window.__bekciDbg(); const v = d.GP.clone(); v.z += 900; t.tp(v, 0); t.stop(); });
  await p.waitForFunction(() => window.__bekciDbg().G, null, { timeout: 40000 }).catch(() => {});
  R.acikBekciVar = await p.evaluate(() => !!window.__bekciDbg().G);
  R.hull1 = await p.evaluate(() => { const g = window.__bekciDbg().G; return g ? g.hullMax : 0; });
  for (let z = 0; z < 2; z++){
    const m = await p.evaluate(() => window.__ledger.length);
    await p.evaluate(() => { const g = window.__bekciDbg().G; if (g){ g.hull = 0; window.__sdt.kill(g); } });
    await p.waitForTimeout(2500);
    R['z' + (z + 1)] = await p.evaluate(() => [window.__sdt.save.bekciZ || 0, window.__sdt.save.bekciOn || 0]);
    R['gwinOdul' + (z + 1)] = await p.evaluate(m => window.__ledger.slice(m).some(e => /gWin/.test(e.s)), m);
    if (z === 0) { await p.evaluate(() => { const t = window.__sdt; t.save.bekciOn = 1; const d = window.__bekciDbg(); const v = d.GP.clone(); v.z += 900; t.tp(v, 0); t.stop(); });
      await p.waitForFunction(() => window.__bekciDbg().G, null, { timeout: 40000 }).catch(() => {}); R.hull2 = await p.evaluate(() => { const g = window.__bekciDbg().G; return g ? g.hullMax : 0; }); }
  }
  R.rozet = await p.evaluate(() => window.__kutuk().find(x => x.ad === 'Kapı Bekçisi').n);
  R.hullOran = R.hull1 && R.hull2 ? Math.round(R.hull2 / R.hull1 * 100) / 100 : 0;
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
