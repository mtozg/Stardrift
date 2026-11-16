# `?ck=b` — Blender kokpitinin Three.js entegrasyon test planı (Kaşif)

Durum: **plan**. Oyunda hiçbir şey değişmedi; mevcut kokpit ve paralaks kokpit (`?ck=q`, Kaşif varsayılanı) olduğu gibi duruyor.
Hedef: `?ck=b` ile, yalnızca Kaşif'te, `cockpit_kasif.glb` denenir. Varsayılan değişmez. Eski sistem silinmez.

## 0. Ön koşullar (entegrasyondan önce)
1. GLB boyutu ≤ 4 MB, gövde ≤ 60 bin üçgen (`build_cockpit.py` çıktısı), dokular JPEG 2048².
2. `build_cockpit.py --verify`: cam açıklıklarında 0 engelli ışın; ekran köşe sapması ≤ 0,05 px.
3. GLB düğüm sözleşmesi: `SCR_SYS`, `SCR_RADAR`, `SCR_HULL` (UV 0..1, boş), gövde `Cockpit_Body`, şeritler `Detail_strip*`.

## 1. Yükleme ve anahtar
- `?ck=b` → `localStorage.sd_ck3 = 'b'` (mevcut `?ck=` mekanizması). `?ck=0` kapatır. Varsayılan: `q` (Kaşif), diğer gemiler eski kokpit.
- Mevcut 3B kokpit yolunun (`__ck3on` + `render()` kancası) yanına `bOn()` eklenir; `qOn()`/`want()` dallarına dokunulmaz.
- `vendor/GLTFLoader.js` (r128) zaten var; GLB `assets/models/` altına **yalnızca entegrasyon aşamasında** konur ve `offline.json` yeniden üretilir.
- Yükleme asenkron; yüklenene kadar mevcut kokpit (q) görünür kalır, geçiş tek karede yapılır (karartma/pop yok).

## 2. Kamera hizası
- Pilot kamerası: dikey FOV 74°, asal nokta (800, 239.5)/1600×656. Mevcut 3B yoldaki `setViewOffset(W,H, W/2−OX, H/2−OY, W,H)` aynen kullanılır (OX,OY = `mp(800,215)`).
- Test: GLB'yi yüklü sahnede ekran köşelerini `CKP` dörtgenleriyle üst üste çiz (`window.__cktest`); sapma ≤ 1 piksel (iPad, iPhone, Pixel, iPad Mini oranlarında).
- Cam açıklıkları: üst üste çizilen eski kokpit (alfa) ile yeni kokpit siluet farkı < %1 alan.
- Sallanma: `sway.x/y` kamera ötelemesine bağlanır (paralaks `×0.9` ile başlar); kenarda boşluk (`CKM` payı) görünmemeli.

## 3. Ekranların canlı SCR texture bağlantısı
- Mevcut `SCR` tuvalleri (`sc.cv`) `CanvasTexture`'a bağlanır (3B yoldaki `e.tex.image = sc.cv` kalıbı).
- `SCR_SYS ↔ kind 'bars'`, `SCR_RADAR ↔ 'map'`, `SCR_HULL ↔ 'hull'`. UV: GLB'de `TL=(0,1)…`, tuvalin ters çevrilmediği doğrulanır (rakam yönü, radar kuzeyi).
- Güncelleme sıklığı mevcut `scrPaint` döngüsü (kare başına tek ekran); texture `needsUpdate` yalnızca `sc.ver` değişince.
- Malzeme: `MeshBasicMaterial`, `toneMapped:false`; ekran ışığı `PointLight`/ışık dokusu ile konsola verilir (paralaks kokpitteki `scrGlow` karşılığı).
- Test: `ck3test` betiği her ekran içeriğinin piksel konumunu `drawQuad` ile çizilmiş eski sonuçla karşılaştırır.

## 4. Işıklandırma
- Sahne ışıkları: gökyüzü (hemisfer), güneş (gerçek `sunDir` → kamera uzayı, mevcut `k.sun` mantığı), patlama (`flashLight`), lazer, ekran ışığı.
- Ortam: küçük bir PMREM (CanvasTexture gradyanı) — metal yüzeyler yansıtsın; `sRGBEncoding` + `ACESFilmic` yalnızca kokpit geçişinde.
- Gölge: bake edilmiş AO (ORM.R) yeterli; gerçek zamanlı gölge **yok** (mobil).
- Test: gece/gündüz/patlama/lazer durumlarında ekran görüntüsü; kokpit iç parlaması çizimden çok sapmamalı.

## 5. Performans bütçesi
- Hedef: iPhone 13'te ≥ 30 fps savaşta; kokpit render ≤ 2 ms/kare (Chrome DevTools/`performance.now` ile ölç).
- Ölçümler: üçgen sayısı, çizim çağrısı sayısı (≤ 25), doku belleği (≤ 40 MB GPU), GLB indirme (≤ 4 MB), ilk yükleme süresi.
- Kontrol: `renderer.info.render.{calls,triangles}` önce/sonra; düşük kalite seviyesinde (`__qLevel`) doku 1024'e iner.
- Yük azaltma: GLB'yi kokpit görünmezken (menü/hangar) `visible=false`; ekran güncelleme 20 Hz.

## 6. Fallback sistemi
- GLB yüklenemezse (ağ/ayrıştırma), `console.warn` + otomatik `q` moduna dön; kullanıcıya bildirim yok.
- Bellek/FPS koruması: 3 saniye ortalaması < 24 fps ise otomatik `q`'ya düş, ayarı o oturum için kilitle.
- Hata: `render()` içinde try/catch (mevcut kalıp) → `__ck3bad` bayrağı.
- `?ck=0` her zaman eski/varsayılan sisteme döner. Eski kokpit kodu ve resimleri silinmez.

## 7. Kabul testleri (Playwright, 4 cihaz × 3 durum)
1. Pilot görüntüsü, çapraz sallanma (±60 px), savaş/patlama ışığı.
2. Ekran konumu: `CKP` farkı ≤ 1 px; ekran metinleri okunur.
3. HUD, düğmeler, dokunmatik kontroller değişmedi (mevcut `play3.js` 20 adım, "TOPLAM HATA: 0").
4. Fallback: GLB yolunu engelleyip `q`'ya dönüş; düşük FPS simülasyonu.
5. Offline: `offline.json` GLB'yi içerir; uçak modunda yükleme.

## 8. Geri alma
- Yalnızca `?ck=0` / `?ck=q` ile; kod tarafında `bOn()` tek noktadan kapatılır. Varsayılan hiçbir zaman `b` yapılmaz; karar sende.
