// T1/T2: ?tani=1 ölçüm paneli. Kapalıyken hiçbir iz olmamalı; açıkken sayılar anlamlı, açılış işaretleri sıralı, 5 yüklemede medyan hesaplanabilir olmalı.
const { chromium } = require('playwright');
(async () => {
  const BASE = process.env.BASE || 'http://localhost:8771/';
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const R = {}; const errs = [];
  const yeni = async () => { const c = await b.newContext({ viewport: { width: 1280, height: 720 }, serviceWorkers: 'block' }); const p = await c.newPage(); p.on('pageerror', e => errs.push(e.message.slice(0, 160))); return { c, p }; };
  const hazir = async p => { await p.waitForFunction(() => document.documentElement.classList.contains('sd-ready'), null, { timeout: 60000 }).catch(() => {}); };

  // A) kapalı: iz yok
  { const { c, p } = await yeni(); const reqs = []; p.on('request', r => reqs.push(r.url()));
    await p.goto(BASE); await hazir(p); await p.waitForTimeout(1500);
    R.kapaliTaniDosyasiYok = !reqs.some(u => /js\/tani\.js/.test(u));
    R.kapaliPanelYok = await p.evaluate(() => !document.getElementById('taniPanel') && typeof window.__tani === 'undefined' && typeof window.__sdm === 'undefined');
    R.kapaliGetContextYerli = await p.evaluate(() => /\[native code\]/.test(HTMLCanvasElement.prototype.getContext.toString()));
    await c.close(); }

  // B) açık: tek yükleme ayrıntısı + 5 yükleme medyanı
  { const { c, p } = await yeni(); await p.goto(BASE + '?tani=1&yukSifirla=1');
    for (let i = 0; i < 5; i++){
      if (i){ await p.waitForTimeout(21000); await p.goto(BASE + '?tani=1'); }   // açılış koruması: 20 sn içinde 3. yükleme önbelleği temizler ve ?tani=1'i siler; bu yüzden yüklemeler arası >20 sn
      await hazir(p); await p.waitForFunction(() => window.__tani && window.__tani.marks.menu, null, { timeout: 60000 }).catch(() => {}); await p.waitForTimeout(i === 0 ? 4000 : 1500);
    }
    const s = await p.evaluate(() => window.__tani.snapshot()), m = await p.evaluate(() => window.__tani.marks), h = await p.evaluate(() => window.__tani.history());
    R.panelVar = await p.evaluate(() => { const e = document.getElementById('taniPanel'); return !!e && /fps/.test(e.textContent) && /WebGL/.test(e.textContent) && /yükleme/.test(e.textContent); });
    R.fpsPozitif = s.fps > 0 && s.fpsMedyan > 0 && s.fpsDusuk5 > 0 && s.fpsDusuk5 <= s.fpsMedyan + 0.1;
    R.cizimUcgen = s.cizim > 0 && s.ucgen > 0;
    R.dokuGeometri = s.doku > 0 && s.geometri > 0;
    R.webgl = s.webgl.olusturulan >= 1 && s.webgl.renderer >= 1 && s.webgl.kayip === 0;
    R.isaretSirali = ['tani-basla', 'game-basla', 'game-hazir', 'sd-ready', 'menu'].every(k => k in m) && m['tani-basla'] <= m['game-basla'] && m['game-basla'] <= m['game-hazir'] && m['game-hazir'] <= m['sd-ready'] && m['sd-ready'] <= m['menu'];
    R.gecmis5 = h.length === 5;
    R.medyan5 = s.medyanSoguk.n + s.medyanSicak.n === 5 && (s.medyanSoguk.menu > 0 || s.medyanSicak.menu > 0);
    R.ornek = { fps: s.fps, cizim: s.cizim, ucgen: s.ucgen, doku: s.doku, geo: s.geometri, ctx: s.webgl.olusturulan, marks: m, medyanSoguk: s.medyanSoguk, medyanSicak: s.medyanSicak };
    await c.close(); }
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
