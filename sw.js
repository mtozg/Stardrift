// Stardrift çevrimdışı paketi.
// - Sayfa (index.html): önce internet, yoksa önbellek → internet varken her açılışta yeni sürüm gelir.
// - Kod (*.js?v=…): sürüm adresiyle saklanır; yeni sürüm gelince eskisi silinir.
// - Görsel, ses, müzik, yazı tipi: adresin ?v= kısmı yok sayılarak tek kopya saklanır.
//   offline.json bütün dosyaları ve içerik özetlerini listeler: ilk açılışta hepsi arkada iner (oyun tamamen çevrimdışı olur),
//   sonraki açılışlarda yalnızca eksik ya da içeriği değişen dosyalar yeniden iner.
const CACHE = 'stardrift-v2', META = '__offline_meta';
const CORE = ['./', 'index.html', 'manifest.webmanifest', 'offline.json', 'vendor/three.min.js', 'assets/img/app_180.png', 'assets/img/app_192.png'];
const scopeUrl = p => new URL(p, self.registration.scope).href;
const isCode = u => /\.js$/.test(u.pathname);
const keyOf = u => isCode(u) ? u.href : u.origin + u.pathname;   // görsel/ses: ?v= yok sayılır

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(CORE.map(u => fetch(scopeUrl(u), { cache: 'reload' }).then(r => r.ok && c.put(keyOf(new URL(scopeUrl(u))), r)).catch(() => {})))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('stardrift-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()).then(() => { sync(); }));
});

const sameOrigin = u => u.origin === self.location.origin;
const isPage = (req, u) => req.mode === 'navigate' || u.pathname.endsWith('/') || u.pathname.endsWith('/index.html');
async function put(c, key, res){
  if (!res || !res.ok || res.status !== 200 || res.type === 'opaque') return;
  const u = new URL(key);
  if (isCode(u) && u.search){ for (const k of await c.keys()){ const ku = new URL(k.url); if (ku.pathname === u.pathname && ku.search !== u.search) c.delete(k); } }
  await c.put(key, res);
}
async function page(req){
  const c = await caches.open(CACHE), key = scopeUrl('index.html');
  try {
    const ctl = new AbortController(), t = setTimeout(() => ctl.abort(), 6000);
    const res = await fetch(req.url, { cache: 'no-store', signal: ctl.signal }); clearTimeout(t);
    if (res.ok){ await put(c, key, res.clone()); sync(); return res; }
    throw new Error('HTTP ' + res.status);
  } catch (err){ const hit = await c.match(key) || await c.match(scopeUrl('./')); if (hit) return hit; throw err; }
}
async function asset(req){
  const u = new URL(req.url), key = keyOf(u), c = await caches.open(CACHE), hit = await c.match(key);
  if (hit) return hit;
  try { const res = await fetch(req); put(c, key, res.clone()).catch(() => {}); return res; }
  catch (err){ const any = await c.match(req, { ignoreSearch: true }); if (any) return any; throw err; }
}
self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET') return;
  const u = new URL(req.url); if (!sameOrigin(u) || req.headers.has('range') || u.pathname.endsWith('/sw.js')) return;
  if (isPage(req, u)) { e.respondWith(page(req)); return; }
  e.respondWith(asset(req));
});

// ---- çevrimdışı paketi eşitle: listedeki eksik/değişmiş dosyaları sırayla indir, ilerlemeyi sayfaya bildir
let syncing = null, state = { done: 0, total: 0, ready: false };
const tell = async () => { for (const cl of await self.clients.matchAll()) cl.postMessage(Object.assign({ type: 'offline' }, state)); };
function sync(){
  if (syncing) return syncing;
  syncing = (async () => {
    const c = await caches.open(CACHE); let list;
    try { const r = await fetch(scopeUrl('offline.json'), { cache: 'no-store' }); if (!r.ok) throw 0; list = (await r.json()).files; await c.put(scopeUrl('offline.json'), new Response(JSON.stringify({ files: list }))); }
    catch (err){ const o = await c.match(scopeUrl('offline.json')); list = o ? (await o.json()).files : null; }
    if (!list) return;
    const mr = await c.match(META), meta = mr ? await mr.json() : {}, files = Object.keys(list);
    state = { done: 0, total: files.length, ready: false };
    for (const f of files){ const key = scopeUrl(f);
      if (meta[f] !== list[f] || !(await c.match(key))){ try { const res = await fetch(key, { cache: 'reload' }); if (res.ok){ await c.put(key, res); meta[f] = list[f]; } } catch (err) {} }
      else meta[f] = list[f];
      state.done++; if (state.done % 12 === 0) { await c.put(META, new Response(JSON.stringify(meta))); tell(); }
    }
    await c.put(META, new Response(JSON.stringify(meta)));
    state.ready = files.every(f => meta[f] === list[f]); tell();
  })().finally(() => { syncing = null; });
  return syncing;
}
self.addEventListener('message', e => {
  const d = e.data || {};
  if (d.type === 'status'){ e.waitUntil(tell()); return; }
  if (d.type === 'sync'){ e.waitUntil(sync()); return; }
  // eski sürümden kalan istek: sayfanın yüklediği dosyaları da sakla (kod dahil)
  if (d.type === 'cache' && Array.isArray(d.urls)) e.waitUntil(caches.open(CACHE).then(async c => { for (const s of d.urls){ try { const u = new URL(s, self.registration.scope); if (!sameOrigin(u) || u.pathname.endsWith('/sw.js') || isPage({}, u)) continue; const key = keyOf(u); if (await c.match(key)) continue; const res = await fetch(u.href); await put(c, key, res); } catch (err) {} } }));
});
