// Korsan oyuncu: sivil gemiler Kara Liman'da (Korsan bölgesi) kaçmaz, başka bölgede kaçar.
const boot = require('./_boot.js');
(async () => {
  const { p, b, errs } = await boot({ side: 'korsan', open: [0, 5], fac: { filo: -20, lonca: 0, korsan: 40 } });
  const R = {};
  const dene = async sys => {
    await p.evaluate(s => { const t = window.__sdt; if (t.docked) t.undock(); t.enter(s); }, sys);
    await p.waitForTimeout(2500);
    return p.evaluate(() => { const t = window.__sdt; if (t.docked) t.undock(); const v = t.rigPos(); v.z -= 250; const n = t.spawn('cargo', v); n.state = 'idle'; n.alertT = 0; window.__kn = n; return t.curSys; });
  };
  R.s0 = await dene(0); R.kacmaDiger = false; for (let i = 0; i < 24 && !R.kacmaDiger; i++){ await p.waitForTimeout(500); R.kacmaDiger = await p.evaluate(() => window.__kn.alertT > 0); } R.dbg = await p.evaluate(() => ({ d: window.__kn.pos.distanceTo(window.__sdt.rigPos()), side: window.__sdt.save.side, dk: window.__sdt.docked, a: window.__kn.alertT, h: window.__kn.hostile, r: window.__kn.role, sg: !!window.__kn.sg, es: !!window.__kn.escort }));
  R.s5 = await dene(5); await p.waitForTimeout(12000); R.kacmaKara = await p.evaluate(() => window.__kn.alertT > 0);
  R.kosul = R.s5 === 5 && R.s0 === 0; R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
