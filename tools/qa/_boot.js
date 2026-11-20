// Ortak açılış: test kaydıyla oyunu başlatıp ilk menülerin geçmesini bekler. Kullanım: const { p, b, errs } = await boot({ kredi, side });
const { chromium } = require('playwright');
module.exports = async function boot(ek){
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const errs = [];
  const pre = JSON.stringify(Object.assign({ kredi: 100, lv: { lazer: 0, kargo: 0, motor: 0 }, xp: 500, pilot: 'Test', side: 'filo', open: [0], grace: 600, fac: { filo: 40, lonca: 10, korsan: -30 } }, ek || {}));
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, serviceWorkers: 'block' });
  await ctx.addInitScript(pre => { try { if (!sessionStorage.getItem('i')){ sessionStorage.setItem('i', '1'); localStorage.setItem('sd_nointro', '1'); localStorage.setItem('sd-key', 'kayip-yildizlar:test'); localStorage.setItem('kayip-yildizlar:test', pre); } window.__noFbk = 1; } catch (e) {} }, pre);
  const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 160)));
  await p.goto(process.env.BASE || 'http://localhost:8771/'); await p.waitForTimeout(3000);
  await p.evaluate(() => { const g = document.getElementById('titleGo'); g && g.click(); }); await p.waitForTimeout(1500);
  let calm = 0; for (let k = 0; k < 40 && calm < 5; k++){ const m = await p.evaluate(() => { const g = document.querySelector('#ctrlSel [data-go]'); g && g.click(); return !!(window.__menuOn || document.getElementById('ctrlSel') || document.getElementById('sideSel')); }); calm = m ? 0 : calm + 1; await p.waitForTimeout(600); }
  await p.waitForTimeout(1500);
  return { p, b, errs };
};
