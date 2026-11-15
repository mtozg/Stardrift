// Kullanım: repo kökünde `python3 -m http.server 8767` çalışırken `node tools/cockpit/verify/glb_check.js [çıktı.png]`
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1200, height: 492 } }); p.on('console', m => { if (!/GL Driver/.test(m.text())) console.log('C:', m.text().slice(0, 200)); });
  await p.goto('http://localhost:8767/tools/cockpit/verify/glb_check.html'); await p.waitForFunction(() => window.__R && window.__R.done, null, { timeout: 180000 }); await p.waitForTimeout(500);
  const R = await p.evaluate(() => window.__R); console.log(JSON.stringify(R, null, 1)); await p.screenshot({ path: process.argv[2] || 'glb_check.png' }); await b.close(); })();
