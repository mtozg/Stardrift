// Stardrift çevrimdışı önbelleği.
// - Sayfanın kendisi (index.html): önce internet, yoksa önbellek → internet varken her açılışta yeni sürüm gelir.
// - Sürüm numaralı dosyalar (?v=…): önce önbellek; yeni sürüm yeni adres demektir, eskisi silinir.
// - Diğer dosyalar (görseller, sesler, yazı tipleri): önbellekten hemen verilir, arkada internetten tazelenir.
// - Oyun açıkken yüklenen her dosya sayfa tarafından buraya bildirilir ve saklanır: gezilen sistemler sonradan internetsiz açılır.
const CACHE = 'stardrift-v1';
const CORE = ['./', 'index.html', 'manifest.webmanifest', 'vendor/three.min.js', 'assets/img/app_180.png', 'assets/img/app_192.png', 'assets/img/app_512.png'];
// sesler, yazı tipleri ve müzik küçük (~7 MB): kurulduktan sonra arkada hepsi indirilir, böylece çevrimdışı sessiz kalmaz
const EXTRA = ["assets/fonts/barlow-300-latin-ext.woff2", "assets/fonts/barlow-300-latin.woff2", "assets/fonts/barlow-400-latin-ext.woff2", "assets/fonts/barlow-400-latin.woff2", "assets/fonts/barlow-500-latin-ext.woff2", "assets/fonts/barlow-500-latin.woff2", "assets/fonts/barlow-600-latin-ext.woff2", "assets/fonts/barlow-600-latin.woff2", "assets/fonts/barlow-700-latin-ext.woff2", "assets/fonts/barlow-700-latin.woff2", "assets/sfx/agir_atis.mp3", "assets/sfx/anomali.mp3", "assets/sfx/firtina.mp3", "assets/sfx/firtina_uyari.mp3", "assets/sfx/gecit_atlama.mp3", "assets/sfx/gecit_cekim.mp3", "assets/sfx/gecit_giris.mp3", "assets/sfx/gecit_varis.mp3", "assets/sfx/gorev_tamam.mp3", "assets/sfx/hiper_cikis.mp3", "assets/sfx/hiper_tunel.mp3", "assets/sfx/itibar.mp3", "assets/sfx/kalinti_bul.mp3", "assets/sfx/kapi_uyan.mp3", "assets/sfx/patron_faz.mp3", "assets/sfx/patron_giris.mp3", "assets/sfx/patron_olum.mp3", "assets/sfx/rutbe.mp3", "assets/sfx/salvo.mp3", "assets/sfx/sicrama_isinma.mp3", "assets/sfx/sicrama_patlama.mp3", "assets/sfx/tarayici.mp3", "assets/sfx/yanki.mp3", "assets/sfx/yardim.mp3", "muzik_ana.mp3", "muzik_ana_aksiyon.mp3", "muzik_ana_destan.mp3", "muzik_ana_gergin.mp3", "muzik_ankora.mp3", "muzik_buzul.mp3", "muzik_hangar.mp3", "muzik_kizil.mp3", "muzik_savas.mp3", "muzik_zumrut.mp3"];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(CORE.map(u => c.add(new Request(u, { cache: 'reload' })).catch(() => {})))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('stardrift-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
  // arka plan: eksik ses/müzik/yazı tipi dosyalarını sırayla indir (etkinleşmeyi bekletmez)
  caches.open(CACHE).then(async c => { for (const f of EXTRA){ try { const r = new Request(new URL(f, self.registration.scope).href); if (!(await c.match(r))){ const res = await fetch(r); await put(c, r, res); } } catch (err) {} } });
});

const sameOrigin = u => u.origin === self.location.origin;
const isPage = (req, u) => req.mode === 'navigate' || u.pathname.endsWith('/') || u.pathname.endsWith('/index.html');
// aynı dosyanın eski sürümlerini (farklı ?v=) at
async function put(c, req, res){
  if (!res || !res.ok || res.status !== 200 || res.type === 'opaque') return;
  const u = new URL(req.url);
  if (u.searchParams.has('v')){ for (const k of await c.keys()){ const ku = new URL(k.url); if (ku.pathname === u.pathname && ku.search !== u.search) c.delete(k); } }
  await c.put(req, res);
}
async function page(req){
  const c = await caches.open(CACHE), key = new Request(new URL('index.html', self.registration.scope).href);
  try {
    const ctl = new AbortController(), t = setTimeout(() => ctl.abort(), 6000);
    const res = await fetch(req.url, { cache: 'no-store', signal: ctl.signal }); clearTimeout(t);
    if (res.ok){ await put(c, key, res.clone()); return res; }
    throw new Error('HTTP ' + res.status);
  } catch (err){ const hit = await c.match(key) || await c.match('./'); if (hit) return hit; throw err; }
}
async function asset(req, versioned){
  const c = await caches.open(CACHE), hit = await c.match(req);
  if (hit){ if (!versioned) fetch(req).then(r => put(c, req, r)).catch(() => {}); return hit; }
  try { const res = await fetch(req); put(c, req, res.clone()).catch(() => {}); return res; }
  catch (err){ const any = await c.match(req, { ignoreSearch: true }); if (any) return any; throw err; }   // çevrimdışı: aynı dosyanın başka sürümlü kopyası da olur
}
self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET') return;
  const u = new URL(req.url); if (!sameOrigin(u) || req.headers.has('range')) return;
  if (isPage(req, u)) { e.respondWith(page(req)); return; }
  e.respondWith(asset(req, u.searchParams.has('v')));
});
// sayfa, yüklediği dosyaların listesini yollar: henüz önbellekte olmayanları sakla (ilk açılışta SW yokken yüklenenler dahil)
self.addEventListener('message', e => {
  const d = e.data || {}; if (d.type !== 'cache' || !Array.isArray(d.urls)) return;
  e.waitUntil(caches.open(CACHE).then(async c => { for (const s of d.urls){ try { const u = new URL(s, self.registration.scope); if (!sameOrigin(u) || u.pathname.endsWith('/sw.js')) continue; const r = new Request(u.href); if (await c.match(r)) continue; const res = await fetch(r); await put(c, r, res); } catch (err) {} } }));
});
