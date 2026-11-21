/* Stardrift tanılama ve ölçüm paneli (T1 + T2). YALNIZ adrese ?tani=1 eklenince yüklenir (index.html); kapalıyken bu dosya hiç indirilmez.
   Ölçüm yöntemleri docs/TANI_OLCUM.md içinde. Oyunun çalışma mantığına dokunmaz: yalnız okur, sayar, ekrana yazar.
   Dış bağımlılık: oyun betiklerinden önce yüklenmelidir (THREE.WebGLRenderer ve canvas.getContext'i sarmalar). */
(function(){
  'use strict';
  if (window.__tani) return;
  var M = {}, nowMs = function(){ return performance.now(); };

  // ---------- T2: açılış işaretleri (performance.now, sayfa gezinme başlangıcına göre ms) ----------
  window.__sdm = function(name){ if (!(name in M)){ M[name] = Math.round(nowMs()); try { performance.mark('sd:' + name); } catch (e) {} if (name === 'menu') setTimeout(function(){ try { maybeRecord(); } catch (e) {} }, 0); } };   // menü çizilince yükleme kaydı hemen yazılır
  window.__sdm('tani-basla');   // bu dosya çalıştı (three ve index.html parse'ı bitmiş)

  // ---------- T1: WebGL bağlam sayacı ----------
  var ctx = { created: 0, lost: 0, restored: 0 }, seen = typeof WeakSet === 'function' ? new WeakSet() : null;
  try {
    var gc = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function(type){
      var c = gc.apply(this, arguments);
      try {
        if (c && /webgl/i.test(String(type)) && seen && !seen.has(this)){
          seen.add(this); ctx.created++;
          this.addEventListener('webglcontextlost', function(){ ctx.lost++; });
          this.addEventListener('webglcontextrestored', function(){ ctx.restored++; });
        }
      } catch (e) {}
      return c;
    };
  } catch (e) {}

  // ---------- T1: çizim çağrısı ve üçgen sayacı (render sarmalayıcı) ----------
  // three.js her render() başında info.render.calls/triangles'ı sıfırlar; bir karede birden çok render çağrısı (ana sahne, bloom geçişleri) olabilir.
  // Bu yüzden her çağrıdan sonra değerleri karelik toplama ekleriz, kare sınırında (rAF) okuruz.
  var rends = [], acc = { calls: 0, tris: 0 };
  try {
    if (window.THREE && THREE.WebGLRenderer){
      THREE.WebGLRenderer = new Proxy(THREE.WebGLRenderer, { construct: function(Target, args){
        var r = new Target(args[0]); rends.push(r);
        var o = r.render;
        r.render = function(){ var out = o.apply(this, arguments); try { var i = this.info.render; acc.calls += i.calls; acc.tris += i.triangles; } catch (e) {} return out; };
        return r;
      } });
    }
  } catch (e) {}

  // ---------- T1: kare hızı örneklemesi ----------
  var N = 600, dts = [], cs = [], last = 0, jank = 0, frames = 0, curCalls = 0, curTris = 0;
  function tick(t){
    if (last){ var dt = t - last; dts.push(dt); if (dts.length > N) dts.shift(); if (dt > 100) jank++; }
    last = t; frames++;
    curCalls = acc.calls; curTris = acc.tris; acc.calls = 0; acc.tris = 0; cs.push(curCalls); if (cs.length > N) cs.shift();
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
  function pct(arr, p){ if (!arr.length) return 0; var s = arr.slice().sort(function(a, b){ return a - b; }); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; }
  function med(arr){ return pct(arr, 0.5); }
  var r1 = function(x){ return Math.round(x * 10) / 10; };

  // ---------- T2: yükleme süreleri ----------
  var HK = 'sd_tani_yuk', hist = [];
  try { if (/[?&]yukSifirla=1/.test(location.search)) localStorage.removeItem(HK); hist = JSON.parse(localStorage.getItem(HK) || '[]'); } catch (e) {}
  function resource(name){
    try { var L = performance.getEntriesByType('resource'); for (var i = 0; i < L.length; i++) if (L[i].name.indexOf(name) >= 0) return L[i]; } catch (e) {}
    return null;
  }
  function loadReport(){
    var r = {}, g = resource('js/game.js'), nav = null;
    try { nav = performance.getEntriesByType('navigation')[0]; } catch (e) {}
    r.cold = !!(g && g.encodedBodySize > 0 && g.transferSize >= g.encodedBodySize);   // game.js gövdesi ağdan tam indiyse soğuk; önbellekten ya da 304 doğrulamasıyla geldiyse sıcak
    r.three = Math.round((resource('three.min.js') || {}).responseEnd || 0);
    r.bloom = Math.round((resource('three-bloom.js') || {}).responseEnd || 0);
    r.gemi = Math.round((resource('js/data_gemi.js') || {}).responseEnd || 0);
    r.ses = Math.round((resource('js/data_ses.js') || {}).responseEnd || 0);
    r.game = Math.round((g || {}).responseEnd || 0);
    r.dom = nav ? Math.round(nav.domContentLoadedEventEnd) : 0;
    r.basla = M['game-basla'] || 0;       // game.js çalışmaya başladı
    r.motor = M['game-hazir'] || 0;       // oyun motoru kuruldu (son satır)
    r.hazir = M['sd-ready'] || 0;         // açılış perdesi kalktı
    r.menu = M['menu'] || 0;              // menü ilk kez çizildi
    r.motorMs = r.motor && r.basla ? r.motor - r.basla : 0;   // motor başlatma süresi
    return r;
  }
  var KEYS = ['three', 'bloom', 'gemi', 'ses', 'game', 'basla', 'motor', 'hazir', 'menu', 'motorMs'];
  function medians(cold){
    var rows = hist.filter(function(h){ return h.cold === cold; }), o = { n: rows.length };
    KEYS.forEach(function(k){ o[k] = med(rows.map(function(h){ return h[k] || 0; })); });
    return o;
  }
  var recorded = false;
  function maybeRecord(){
    if (recorded || !M['menu']) return; recorded = true;
    hist.push(loadReport()); if (hist.length > 10) hist.shift();
    try { localStorage.setItem(HK, JSON.stringify(hist)); } catch (e) {}
  }

  // ---------- anlık görüntü (panel ve testler kullanır) ----------
  function snapshot(){
    var med1 = med(dts), p95 = pct(dts, 0.95), mem = null, prog = 0, main = rends[0];
    try { if (main){ mem = { textures: main.info.memory.textures, geometries: main.info.memory.geometries }; prog = (main.info.programs || []).length; } } catch (e) {}
    var recent = dts.slice(-30), avg = recent.length ? recent.reduce(function(a, b){ return a + b; }, 0) / recent.length : 0;
    return {
      fps: avg ? r1(1000 / avg) : 0, fpsMedyan: med1 ? r1(1000 / med1) : 0, fpsDusuk5: p95 ? r1(1000 / p95) : 0,
      kareMsMedyan: r1(med1), kareMsP95: r1(p95), kareSayisi: dts.length, takilma100ms: jank,
      cizim: curCalls, cizimMedyan: med(cs), ucgen: curTris,
      doku: mem ? mem.textures : null, geometri: mem ? mem.geometries : null, program: prog,
      webgl: { olusturulan: ctx.created, kayip: ctx.lost, geriGelen: ctx.restored, renderer: rends.length },
      yuk: loadReport(), medyanSoguk: medians(true), medyanSicak: medians(false),
      jsHeapMB: (performance.memory && performance.memory.usedJSHeapSize) ? Math.round(performance.memory.usedJSHeapSize / 1048576) : null
    };
  }
  window.__tani = { snapshot: snapshot, marks: M, history: function(){ return hist.slice(); } };

  // ---------- panel ----------
  function ms(x){ return x ? String(x) : '-'; }
  function paint(box){
    var s = snapshot(), y = s.yuk, ms1 = s.medyanSoguk, ms2 = s.medyanSicak, c = y.cold ? 'soğuk' : 'sıcak';
    box.textContent = 'T1/T2 v' + (window.SD_VERSION || '?') + '\n'
      + 'fps ' + s.fps + ' | medyan ' + s.fpsMedyan + ' | düşük%5 ' + s.fpsDusuk5 + ' | kare ms med ' + s.kareMsMedyan + ' p95 ' + s.kareMsP95 + ' | takılma>100ms ' + s.takilma100ms + '\n'
      + 'çizim ' + s.cizim + ' (med ' + s.cizimMedyan + ') | üçgen ' + s.ucgen + ' | doku ' + s.doku + ' geo ' + s.geometri + ' prog ' + s.program + (s.jsHeapMB ? ' | heap ' + s.jsHeapMB + 'MB' : '') + '\n'
      + 'WebGL: oluşturulan ' + s.webgl.olusturulan + ' kayıp ' + s.webgl.kayip + ' geri ' + s.webgl.geriGelen + ' (renderer ' + s.webgl.renderer + ')\n'
      + 'yükleme (' + c + ') ms: three ' + ms(y.three) + ' gemi ' + ms(y.gemi) + ' ses ' + ms(y.ses) + ' game ' + ms(y.game) + ' | başla ' + ms(y.basla) + ' motor ' + ms(y.motorMs) + ' hazır ' + ms(y.hazir) + ' menü ' + ms(y.menu) + '\n'
      + 'medyan soğuk(' + ms1.n + ') hazır ' + ms(ms1.hazir) + ' menü ' + ms(ms1.menu) + ' | sıcak(' + ms2.n + ') hazır ' + ms(ms2.hazir) + ' menü ' + ms(ms2.menu);
  }
  function mount(){
    var box = document.createElement('div'); box.id = 'taniPanel';
    box.style.cssText = 'position:fixed;left:4px;bottom:4px;z-index:99998;font:9px/1.3 ui-monospace,Menlo,monospace;color:#bfe;background:rgba(0,10,20,.78);padding:3px 6px;border:1px solid #2a8;border-radius:5px;pointer-events:none;white-space:pre;max-width:96vw;overflow:hidden';
    document.body.appendChild(box);
    setInterval(function(){ maybeRecord(); paint(box); }, 500);
  }
  if (document.body) mount(); else document.addEventListener('DOMContentLoaded', mount);
})();
