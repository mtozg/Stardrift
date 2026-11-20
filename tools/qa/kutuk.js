// Pilot Kütüğü testi: istasyonda Görevler sekmesinde rozet listesi, kademeler ve toplam doğru mu.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const errs = [];
  const pre = JSON.stringify({ kredi: 5000, lv: { lazer: 0, kargo: 0, motor: 0 }, xp: 3000, pilot: 'Test', side: 'filo', open: [0, 1, 2, 3, 4, 5], grace: 600, fac: { filo: 40, lonca: 10, korsan: -30 },
    st: { sell: 320, kill: 12, avci: 0, kacak: 0, sip: 0 }, boss: [0, 1, 2], seen: [0, 1, 2], bekci: 1 });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, serviceWorkers: 'block' });
  await ctx.addInitScript(pre => { try { if (!sessionStorage.getItem('i')){ sessionStorage.setItem('i', '1'); localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', 'kayip-yildizlar:test'); localStorage.setItem('kayip-yildizlar:test', pre); } window.__noFbk = 1; } catch (e) {} }, pre);
  const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 200)));
  await p.goto(process.env.BASE || 'http://localhost:8771/'); await p.waitForTimeout(3000);
  await p.evaluate(() => { const g = document.getElementById('titleGo'); g && g.click(); }); await p.waitForTimeout(1500);
  let calm = 0; for (let k = 0; k < 40 && calm < 5; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return !!(window.__menuOn || document.getElementById('ctrlSel') || document.getElementById('sideSel')); }); calm = m ? 0 : calm + 1; await p.waitForTimeout(600); }
  await p.waitForTimeout(1500);
  await p.evaluate(() => { const t = window.__sdt; t.dockAt(t.stations()[0]); });
  for (let i = 0; i < 40; i++){ if (await p.evaluate(() => window.__sdt.docked)) break; await p.waitForTimeout(400); }
  await p.evaluate(() => { const t = document.querySelector('#dtabs [data-t="ct"]'); t && t.click(); }); await p.waitForTimeout(1000);
  await p.evaluate(() => { const b = document.getElementById('ctBox'); const s = [...b.querySelectorAll('.sect')].find(x => /Pilot Kütüğü/.test(x.textContent)); s && s.scrollIntoView(); }); await p.waitForTimeout(600); await p.evaluate(() => { const h = [...document.querySelectorAll('#ctBox .acch, #ctBox .sect')].find(x => /Pilot Kütüğü/.test(x.textContent)); h && h.click(); }); await p.waitForTimeout(700); await p.evaluate(() => { const l = [...document.querySelectorAll('#ctBox .line')].filter(x => /Madenci|Kapı Bekçisi/.test(x.textContent)).pop(); l && l.scrollIntoView({ block: 'center' }); }); await p.waitForTimeout(500); await p.screenshot({ path: (process.argv[2] || '.') + '/kutuk.png' }).catch(() => {});
  const R = { kutuk: await p.evaluate(() => window.__kutuk().map(x => x.ad + ':' + x.n)), metin: await p.evaluate(() => { const b = document.getElementById('ctBox'); const t = b ? b.innerText.replace(/\s+/g, ' ') : ''; const i = t.indexOf('Pilot Kütüğü'); return i < 0 ? null : t.slice(i, i + 260); }), errs };
  console.log('@@' + JSON.stringify(R)); await b.close();
})();
