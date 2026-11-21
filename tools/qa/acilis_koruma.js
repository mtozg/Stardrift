// Açılış çökme koruması (1.66.6): hızlı manuel yenileme çökme sayılmaz ve çevrimdışı paketi kapatmaz; gerçek açılış çökmesi (oyun hiç açılmıyor) hâlâ kurtarmayı tetikler;
// kurtarmanın kapattığı paket indirmesi 24 saatte kendiliğinden açılır; eski sürümün kalıcı '1' bayrağı silinir.
const { chromium } = require('playwright');
(async () => {
  const BASE = process.env.BASE || 'http://localhost:8771/';
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const R = {}; const errs = [];
  const yeni = async () => { const c = await b.newContext({ viewport: { width: 900, height: 500 }, serviceWorkers: 'block' }); const p = await c.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 160))); return { c, p }; };
  const hazir = p => p.waitForFunction(() => document.documentElement.classList.contains('sd-ready') && localStorage.getItem('sd_boot') === '0', null, { timeout: 60000 }).catch(() => {});

  // A) hızlı manuel yenileme: oyun açıldıktan sonra 5 kez art arda (hepsi 20 sn içinde)
  { const { c, p } = await yeni(); await p.goto(BASE + '?x=1'); let sorunsuz = true;
    for (let i = 0; i < 5; i++){ if (i) await p.goto(BASE + '?x=1'); await hazir(p); await p.waitForTimeout(500);
      const s = await p.evaluate(() => ({ q: location.search, n: localStorage.getItem('sd_nosync') })); if (s.q !== '?x=1' || s.n) sorunsuz = false; }
    R.hizliYenilemeKurtarmaYok = sorunsuz; await c.close(); }

  // B) gerçek açılış çökmesi: game.js hiç yüklenmiyor, 3 yükleme üst üste
  { const { c, p } = await yeni(); await p.route(/js\/game\.js/, r => r.abort());
    for (let i = 0; i < 3; i++){ await p.goto(BASE + '?x=1').catch(() => {}); await p.waitForTimeout(1200); }
    await p.waitForTimeout(3000);
    const s = await p.evaluate(() => ({ q: location.search, n: localStorage.getItem('sd_nosync') }));
    R.cokmeKurtarmaTetiklendi = s.q === '' && +s.n > 1e12 && Date.now() - +s.n < 120000; await c.close(); }

  // C) bayrak süresi ve eski bayrak
  const bayrak = async (deger) => { const { c, p } = await yeni(); await p.goto(BASE); await p.evaluate(d => { if (d === null) localStorage.removeItem('sd_nosync'); else localStorage.setItem('sd_nosync', d); }, deger);
    await p.goto(BASE); await hazir(p); await p.waitForTimeout(800);
    const o = await p.evaluate(() => ({ f: window.__noSync, k: localStorage.getItem('sd_nosync') })); await c.close(); return o; };
  const eski = await bayrak('1'); R.eskiBayrakSilinir = eski.f === false && eski.k === null;
  const taze = await bayrak(String(Date.now())); R.tazeBayrakAktif = taze.f === true;
  const sureDoldu = await bayrak(String(Date.now() - 90000000)); R.sureDolunca = sureDoldu.f === false && sureDoldu.k === null;
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
