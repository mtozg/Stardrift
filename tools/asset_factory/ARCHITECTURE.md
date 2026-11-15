# Stardrift Asset Factory — Mimari ve Üretim Hattı (taslak v0.1)

Durum: **tasarım, onay bekliyor.** Bu belgeden başka dosya yok; kod yazılmadı. Oyunun hiçbir dosyasına dokunulmadı.

---

## 1. Amaç ve sınırlar

Blender Python (`bpy`) ile **parametrik, tekrar üretilebilir** 3B varlık üretimi: NPC gemileri, istasyonlar, kapılar, hangarlar, çevre nesneleri.
Çıktı: Three.js r128 (oyunun sürümü) ile açılan **GLB + PBR dokular**, her model için **kalite ve performans raporu**.

Kurallar (bağlayıcı):

| # | Kural | Mimarideki karşılığı |
|---|---|---|
| 1 | Ana oyun koduna izinsiz müdahale yok | Fabrika yalnızca `tools/asset_factory/` içine yazar. `js/`, `index.html`, `assets/`, `models/`, `offline.json`, `sw.js` **salt okunur**. Oyuna geçiş tek kapıdan: `handoff` (bkz. §9), o da yalnızca onaydan sonra ve ana sohbette. |
| 2 | Bağımsız çalışma | Kendi CLI'ı, kendi `requirements.txt`'i, kendi çıktı klasörü. Oyunun yalnızca `vendor/three.min.js` dosyasını **okur** (testin oyunla aynı motor sürümüyle yapılması için). |
| 3 | Kaşif kokpit altyapısı yeniden kullanılır | §3'te parça parça envanter. |
| 4 | Her modele kalite + performans doğrulaması | §7: geçmeyen model `approved` olamaz. |
| 5 | Önce mimari, onay sonra kod | Bu belge. |

---

## 2. Mevcut durumun incelenmesi (bulgular)

**Kokpit hattı** `claude/bold-bardeen-oqf73o` dalında, `tools/cockpit/` altında (main'de yok):

```
build_cockpit.py          CLI: --ship --stage --views --verify --export --tex --samples
lib/common.py             koordinat dönüşümü (oyun ↔ Blender), mesh/bmesh yardımcıları, boolean, bevel, üçgen sayımı
lib/materials.py          prosedürel PBR: _metal() (fırça, çizik, kenar aşınması, AO kiri), kompozit, deri, kumaş, emisyon, ekran
lib/bake.py               birleştirme, gizli yüz silme, Smart UV, Cycles bake (AO/base/rough/normal), ORM birleştirme, PBR'ye dönüştürme, GLB
lib/render.py             uzay dünyası (gradyan + yıldız), softbox ışıklar, kamera, Cycles render
lib/project.py            onaylı 2B çizimden ince detayı (yüksek geçiren) yüzeye karıştırma
lib/verify.py             kokpite özel ışın testleri (cam açıklığı, ekran hizası)
lib/canopy|dash|seat|side|detail|dash_detail.py   kokpite özel geometri
verify/glb_check.html+.js Three r128 + GLTFLoader + Playwright (swiftshader): isim, malzeme, normal yönü, çağrı/üçgen, ms/kare
INTEGRATION_PLAN.md       ?ck=b deneme bayrağı, fallback, bütçe
```

**Oyun tarafı (salt okunur gözlem):**
- NPC gemileri bugün `SHIPART` (üst + yan çizim, `ships_*_top/side.webp`) ve `SPECS3D` ile `buildShip3D`/`mkShipGen` içinde çizimden kurulan özel shader'lı modeller. Gemilerin gerçek boyu tabloda var (`cargo L:70`, `mining L:52`, `courier L:16`, `corvette L:38`...). Model 1 birim uzunlukta kurulup `S.len` ile ölçekleniyor.
- Three.js **r128**. Oyun main dalında `GLTFLoader` yok; kokpit dalında `vendor/GLTFLoader.js` (r128) eklenmiş. Bu sürüm `EXT_texture_webp`, `KHR_mesh_quantization`, `EXT_meshopt_compression`, `KHR_texture_basisu`, `KHR_draco_mesh_compression` uzantılarını tanıyor.
- Kalite seviyesi `__qLevel` (`localStorage.sd_q`), hasar shader'ı `DMG_GLSL`, çevrimdışı paket `offline.json` (~30 MB).
- Ortamda `bpy 5.3.0` pip ile kurulabilir (Python 3.13); kokpit hattı da 5.3 ile denenmiş.

**Mevcut altyapıda gördüğüm, genelleştirirken düzeltilmesi gereken noktalar:**
1. `bake.METALLIC` sözlüğü malzeme **adına** bağlı → malzeme meta verisine taşınmalı.
2. `cull_hidden` gözün orijinde olduğunu varsayar (kokpit içi) → dış modellerde çok yönlü görünürlük testine dönüşmeli (yoksa yanlış yüz siler).
3. `join_body`/`export_glb` koleksiyon adı `'Cockpit'` sabit; çıktı yalnızca JPEG → WebP + niceleme seçeneği.
4. ORM'nin B (metalik) kanalı hep 1; metalik malzeme sabitinden geliyor → tek atlasta karışık malzemede hatalı olabilir; gerçek metalik bake edilmeli.
5. Smart UV + her varlığa 2048² özgün bake, 40 NPC gemisi için GPU belleğini patlatır → §6'daki "paylaşımlı trim atlas" modu.
6. Rastgelelik `random.Random(sabit)` ile kısmen kontrollü; fabrika her şeyi `seed`'e bağlamalı (tekrar üretilebilirlik + içerik özeti).

---

## 3. Yeniden kullanım envanteri

| Kokpit parçası | Karar | Fabrikadaki yeri / değişiklik |
|---|---|---|
| `common.py` (g2b, obj_from_bm/pydata, boolean, bevel, apply_modifier, tri_count, smooth_by_angle, clear_scene) | **Aynen al** | `core/geo.py` — koleksiyon adı parametre olur |
| `common.Cam` | Kokpite özel | alınmaz (yalnızca kokpit) |
| `materials._metal` ve ailesi | **Al, parametrik yap** | `core/materials.py` — `MaterialSpec` (base, rough aralığı, metalik, aşınma, kir, çizik, fırça) JSON'dan; taraf/evren paletleri buradan türetilir |
| `materials.emission`, `screen_mat` | **Aynen al** | motor çıkışı, pencere ışıkları, kapı enerji halkaları |
| `bake.py` (bake_all, compose_orm, rebuild_materials, occlusion_group, export_glb) | **Al, düzelt** | `core/bake.py` — madde 1, 3, 4; çözünürlük ve mod (trim/unique) parametresi |
| `bake.cull_hidden` | **Yeniden yaz** | `core/cleanup.py` — 26 yönlü ışın görünürlüğü (dışarıdan hiç görünmeyen yüzleri sil) |
| `bake.unwrap` (Smart UV) | Al | `unique` modda; `trim` modda UV kuralla atanır |
| `render.py` (setup_world, add_light, camera, render) | **Aynen al** | `core/render.py` + yeni: turntable, 6 dik görünüş, kontak tabaka |
| `project.py` (çizimden detay) | **Uyarlayarak al** | `core/reference.py` — mevcut `ships_*_top/side.webp` çizimleri hem detay kaynağı hem **siluet doğrulama referansı** (§7.3) |
| `verify.py` ışın testleri | Kalıp alınır | `core/checks/` — ışın altyapısı soket görünürlüğü, iç-dış testleri için |
| `verify/glb_check.html/.js` | **Al, genelleştir** | `viewer/` — her GLB için çağrı/üçgen/doku belleği/ms, cihaz emülasyonu, çoklu örnek (instancing) testi |
| `INTEGRATION_PLAN.md` deseni (bayrak, fallback, bütçe, geri alma) | **Şablon** | her varlık ailesi için `handoff` paketinde aynı başlıklar |
| canopy/dash/seat/side/detail | Kokpite özel | alınmaz; ama kafes → Subsurf "sculpt" kalıbı (`seat.sculpt`) `core/shapes.py`'ye genelleşir |

Kokpit hattı **taşınmaz ve değiştirilmez**; fabrika kendi kopyasını (`core/`) tutar. Fabrika olgunlaşınca kokpitin `core/`'u kullanması ayrı bir karar olur.

---

## 4. Klasör yapısı

```
tools/asset_factory/
  ARCHITECTURE.md
  README.md
  requirements.txt              bpy==5.3.0, numpy, pillow, scipy, pygltflib (+ npm: gltf-validator, gltf-transform, playwright mevcut)
  factory.py                    tek giriş noktası (CLI, §8)
  core/                         Blender'a bağlı, varlıktan bağımsız
    geo.py  shapes.py  materials.py  palettes.py  bake.py  cleanup.py  lod.py
    uv.py  sockets.py  collision.py  export.py  render.py  reference.py  seed.py
  families/                     varlık ailesi = parça kütüphanesi + kurucu (grammar)
    ship/        hull.py engines.py wings.py greebles.py cockpit_glass.py build.py
    station/     core.py ring.py truss.py solar.py docking.py build.py
    gate/        ring.py pylons.py energy.py build.py
    hangar/      shell.py bays.py lights.py props.py build.py
    prop/        container.py debris.py beacon.py satellite.py asteroid_base.py build.py
  specs/                        Claude'un düzenlediği JSON tarifler (kaynak gerçeği)
    _schema/                    JSON Schema (aile başına)
    styles/                     taraf × evren stil paketleri (palet, aşınma, ışık rengi)
    ships/npc_cargo.json  ships/npc_courier.json ...
    stations/ gates/ hangars/ props/
  budgets.json                  sınıf başına performans bütçeleri (§6)
  checks/                       Blender'sız doğrulayıcılar (Python + Node)
    static_glb.py  budgets.py  silhouette.py  pbr_ranges.py  naming.py
  viewer/                       Three r128 doğrulama + karşılaştırma sayfaları
    check.html  bench.html  gallery.html  run_check.js  run_bench.js
  registry.json                 her varlığın durumu, sürümü, içerik özeti (git'te)
  out/        (git dışı)        ara çıktılar: .blend, bake PNG, render
  dist/       (git'te, küçük)   onaylı GLB + rapor + önizleme; handoff'un tek kaynağı
```

---

## 5. Üretim hattı

```
 spec.json ──► [1 resolve] ──► [2 generate] ──► [3 cleanup] ──► [4 LOD] ──► [5 UV+bake] ──► [6 export]
   ▲  seed, stil, varyant       bpy, deterministik   manifold, normal,   0/1/2        trim | unique     GLB, WebP,
   │                                                 gizli yüz, origin                AO→vertex/ORM     quantize, meshopt
   │
   │       ┌──────────────────────── [7 validate] ◄────────────────────────────────────────────┘
   │       │  7a statik (Python): sözleşme, bütçe, PBR aralıkları, glTF validator
   │       │  7b görsel: Cycles önizleme + Three r128 render, siluet ⟷ çizim
   │       │  7c performans: Playwright + cihaz emülasyonu, N örnek sahnesi
   │       ▼
   │   [8 report] report.json + report.html + kontak tabaka PNG
   │       │
   └── Claude okur, spec'i düzeltir ◄── FAIL
           │ PASS
           ▼
       [9 review] kullanıcı onayı (galeri) ──► registry: approved ──► [10 handoff] (ana sohbette, ayrı onay)
```

Her aşama bağımsız çağrılabilir ve çıktısını `out/<asset>/<version>/NN_<stage>/` altına yazar; bir aşama yalnızca girdisinin özeti (hash) değişince yeniden çalışır (bake dakikalar sürdüğü için önemli).

### 5.1 Spec (tarif) biçimi — örnek

```json
{
  "id": "npc_cargo",
  "family": "ship",
  "archetype": "hauler",
  "class": "ship_large",
  "length_m": 70,
  "style": "lonca/ankora",
  "seed": 4127,
  "params": {
    "hull":    { "sections": 5, "taper_nose": 0.35, "taper_tail": 0.6, "width_ratio": 0.29, "height_ratio": 0.20 },
    "cargo":   { "pods": 6, "pod_layout": "spine_pairs", "pod_size": [0.12, 0.08, 0.08] },
    "engines": { "count": 2, "type": "bell", "glow": "lonca_amber" },
    "greeble": { "density": 0.45, "kinds": ["vent", "pipe", "panel", "antenna"] }
  },
  "reference": { "top": "assets/img/ships_cargo_top.webp", "side": "assets/img/ships_cargo_side.webp", "silhouette_iou_min": 0.80 },
  "variants": { "axes": { "style": ["lonca/ankora", "filo/ankora", "korsan/kara"], "params.cargo.pods": [4, 6, 8] }, "max": 6 },
  "texture_mode": "trim",
  "lods": [1.0, 0.45, 0.15]
}
```

`reference` mevcut oyun çizimine bağlanırsa üretilen model, bugünkü 2B tasarımla **aynı kimlikte** kalır (oyuncunun tanıdığı gemi).

### 5.2 Aile kurucuları (grammar)

Her aile `build(spec, rng, mats) -> AssetScene` sağlar; parçalar küçük, tek işi yapan fonksiyonlar:

- **ship**: gövde = kesit profilleri boyunca loft (yaşa/kapsül/köşeli seçenek) → kanat/sponson → motor çanları (lathe) → kargo modülleri → kokpit camı (emisyonlu koyu cam) → greeble dağıtımı (yüzeye dik, çakışma kontrollü, simetri ekseni).
- **station**: merkez gövde (lathe) + halka(lar) + kafes (truss, instanced) + güneş panelleri + yanaşma kolları; yanaşma soketleri zorunlu.
- **gate**: halka (torus kesiti profilden) + direkler + enerji yüzeyi (ayrı emisyon mesh, oyunda shader ile canlandırılır; mevcut `gate_*_enerji/yuzey.webp` dokularıyla uyumlu UV).
- **hangar**: iç mekân kabuğu (içe dönük normaller), bölmeler, tavan ışıkları (emisyon şerit), dekor; kamera yolu soketleri (oyunun yanaşma animasyonu için).
- **prop**: konteyner, enkaz (boolean kırık), işaret şamandırası, uydu, kalıntı parçaları.

Taraf/evren stili (`specs/styles/`) şekle değil **malzeme, renk, aşınma, ışık rengi ve greeble türüne** dokunur: Filo (temiz, beyaz-mavi), Lonca (altın-amber, düzenli), Korsan (paslı, yamalı, asimetrik eklentiler); Ankora / Kızıl / Buzul / Zümrüt / Kara Liman / Lonca Pazarı tonları.

### 5.3 Varyasyon

- Varyant = `spec` + (stil, parametre değerleri, seed) çarpımından seçilen alt küme (`variants.max`).
- Varyant kimliği: `npc_cargo@lonca-ankora.p6.s4127` — deterministik; aynı girdi = aynı GLB (bayt eşitliği hedef, en azından geometri hash eşitliği).
- **Paylaşım**: varyantlar aynı trim atlası ve malzemeleri kullanır → oyunda 6 varyant tek doku setiyle çizilir.

---

## 6. Oyun sözleşmesi ve performans bütçesi

### 6.1 GLB sözleşmesi (tüm aileler)

- Birim **metre**, gerçek boy (`length_m`). Oyun uzayı: Y yukarı, **−Z ileri** (burun −Z). Blender'da `g2b` dönüşümüyle kurulur, glTF dışa aktarımı Y-up.
- Kök düğüm `SD_<id>`; altında `LOD0`, `LOD1`, `LOD2` (her biri ≤ 2 mesh: opak gövde + emisyon).
- Malzeme adları: `MAT_body`, `MAT_emit`, `MAT_glass` (en fazla 3).
- Soketler (boş düğümler, `SOCK_` öneki): `SOCK_engine_N` (alev/iz efekti, yön −Z'nin tersi), `SOCK_gun_N`, `SOCK_dock_N`, `SOCK_light_N` (seyir ışığı rengi `extras`te), `SOCK_cam_N` (hangar/yanaşma kamera yolu).
- Çarpışma: `extras.collision` = küre listesi (oyunun mevcut mesafe tabanlı çarpışmasına uygun) + isteğe bağlı `COL_hull` düşük poligonlu dışbükey mesh.
- `extras`: `{ id, variant, version, faction, universe, radius, bounds, tris:[l0,l1,l2], factory_hash }`.
- Hasar: oyunun `DMG_GLSL` yaklaşımı için `COLOR_0` kanalında hasar maskesi ayrılır (R = kenar/zırh, G = iç bölge). Kullanılıp kullanılmayacağı entegrasyonda karar.

### 6.2 Doku modları

| Mod | Ne zaman | Nasıl | Bellek |
|---|---|---|---|
| **trim** (varsayılan, NPC/prop) | çok sayıda, küçük ekranda görünen | taraf başına paylaşımlı 1024² trim atlası (panel, çizgi, ızgara, şerit) + model başına AO ve hasar maskesi **vertex color**'da | taraf başına ~4 MB GPU, model başına ≈ 0 |
| **unique** (boss, istasyon, kapı, hangar) | yakından görülen tekil varlıklar | kokpit hattındaki bake (base, ORM, normal) | 1024² veya 2048² |

Dokular **WebP** (`EXT_texture_webp`, iOS 14+ destekli) — JPEG'e göre ~%30 küçük; PNG yedeği yalnızca alfa gerekirse. KTX2/Basis (GPU belleği en düşük) r128'de destekli ama transcoder ister → faz 3'te değerlendirme.

### 6.3 Geometri sıkıştırma

`KHR_mesh_quantization` + `EXT_meshopt_compression` (gltf-transform ile). Meshopt çözücüsü tek küçük JS dosyası (wasm gömülü), Draco'dan hafif → oyuna eklenmesi gerekecek; bu entegrasyon kararı, fabrika her iki sürümü de (sıkıştırmalı/sıkıştırmasız) üretebilir.

### 6.4 Bütçeler (`budgets.json`, mobil hedef: iPhone 13 / orta Android, 30+ fps)

| Sınıf | LOD0 üçgen | LOD1 | LOD2 | Çizim çağrısı | Doku | GLB |
|---|---|---|---|---|---|---|
| prop | 800 | 300 | 80 | ≤ 2 | trim | ≤ 60 KB |
| ship_small (≤ 25 m) | 2 500 | 1 100 | 350 | ≤ 2 | trim | ≤ 150 KB |
| ship_large (≤ 80 m) | 6 000 | 2 700 | 900 | ≤ 3 | trim | ≤ 300 KB |
| boss | 12 000 | 5 000 | 1 500 | ≤ 3 | unique 1024² | ≤ 1 MB |
| gate | 10 000 | 4 000 | 1 200 | ≤ 3 | unique 1024² | ≤ 1 MB |
| station | 25 000 | 10 000 | 3 000 | ≤ 4 | unique 2048² | ≤ 2 MB |
| hangar (iç) | 40 000 | — | — | ≤ 6 | unique 2048² | ≤ 3,5 MB |

Sahne düzeyi: aynı anda 12 NPC gemisi + 1 istasyon + 1 kapı ile ek kokpit dışı yük ≤ 4 ms/kare (cihazda). Sayılar ilk tahmin; faz 1'de gerçek cihaz ölçümüyle ayarlanır.

---

## 7. Doğrulama (her model, her varyant)

Sonuç üç düzeyli: **PASS / WARN / FAIL**. Tek FAIL bile `approved` durumunu engeller.

### 7.1 Statik (Blender içinde + GLB üzerinde)
- glTF Khronos validator: 0 hata.
- Sözleşme: düğüm/malzeme/soket adları, kök, LOD sayısı, `extras` alanları, birim/boy (±%2).
- Geometri: uygulanmış dönüşümler, sıfır alanlı yüz yok, gevşek köşe yok, tutarlı normal (dışa bakış ışın testi), açık kenar sayısı (gövde için 0 hedef), kendi içine geçen greeble oranı.
- UV: 0..1 dışı yok (trim hariç), ada çakışması yok (unique), texel yoğunluğu sınıf hedefinin ±%30'unda.
- PBR aralıkları: base color sRGB 30–240 (metaller 180–250 hariç), metalik ~0 ya da ~1 (ara değer oranı uyarı), roughness 0,05–1, normal haritası birim uzunlukta.
- Bütçe: §6.4 tablosu.

### 7.2 Görsel
- Cycles önizleme: 6 dik görünüş + 3/4 + turntable (8 kare) → kontak tabaka PNG. Claude bu görüntüleri okuyup yorumlar.
- **Three r128 render** aynı açılardan (`viewer/check.html`, oyunun ışık düzeniyle); Cycles ile parlaklık/renk farkı ölçülür (glTF malzeme kaybını yakalar: örn. kokpitteki iplik metalik=1 hatası türünden).
- LOD geçiş farkı: LOD0 ↔ LOD1 ekranda belirlenen mesafede siluet farkı < %3 piksel.

### 7.3 Referansa sadakat
- Mevcut `ships_*_top/side.webp` varsa: üretilen modelin üst ve yan siluetinin çizimin alfa maskesiyle **IoU**'su ≥ `silhouette_iou_min` (varsayılan 0,80). Böylece yeni 3B gemi bugünkü tasarımdan kopmaz.

### 7.4 Performans (Playwright, oyunun `vendor/three.min.js`'i)
- Tek model: `renderer.info` çağrı/üçgen, doku/geometri belleği, ilk yükleme (parse) süresi.
- Kalabalık sahne: N = 1/12/40 örnek, ms/kare; cihaz emülasyonu iPad Pro 11, iPhone 13, Pixel 7 (yatay).
- Not: swiftshader süreleri gerçek cihazı yansıtmaz — **göreli karşılaştırma** içindir. Gerçek ölçüm için `viewer/bench.html` sayfası telefonda açılır (GitHub Pages veya yerel sunucu), sonucu kopyalanabilir JSON olarak verir.

### 7.5 Rapor
`dist/<id>/<variant>/report.json` (makine) + `report.html` (insan: önizleme, metrikler, bütçe çubukları, PASS/WARN/FAIL listesi). `viewer/gallery.html` tüm kayıtları yan yana gösterir; onay buradan verilir.

---

## 8. Claude ile yönetim (orkestrasyon)

Kaynak gerçeği **spec JSON**; Claude kod değil, tarif düzenleyerek üretir. Tek CLI:

```
python factory.py new     ship npc_cargo --from-ref ships_cargo        # şablon spec, çizimden boy/oran tahmini
python factory.py build   npc_cargo [--variant all] [--stage generate..export] [--fast]
python factory.py validate npc_cargo [--perf]
python factory.py report  npc_cargo                                    # report.html + kontak tabaka
python factory.py variants npc_cargo --list | --build
python factory.py status                                               # registry özeti
python factory.py approve npc_cargo@lonca-ankora.p6.s4127              # yalnızca kullanıcı isteğiyle
python factory.py handoff  npc_cargo --target models/ships/           # yalnızca ana sohbette, ayrı onayla (§9)
```

- `--fast`: düşük örnek, 512² bake, yalnızca 3 görünüş → döngü süresi dakikalar değil saniyeler (tasarım iterasyonu).
- Her komut sonunda tek satır makine özeti basar (`RESULT {...}`); Claude bunu ve PNG'leri okuyup bir sonraki adımı seçer.
- `registry.json` durumları: `draft → built → validated (PASS/FAIL) → approved → handed_off`. Her geçiş zaman, içerik hash'i ve neden ile kaydedilir.
- Uzun bake işleri arka planda; aynı anda tek Blender süreci (bellek).
- Döngü: Claude spec'i değiştirir → `build --fast` → raporu okur → düzeltir → tam `build` + `validate --perf` → kullanıcıya galeri.

---

## 9. Ana projeye entegrasyon (handoff)

Fabrika oyunu **değiştirmez**; `handoff` yalnızca bir **paket** hazırlar:

```
dist/handoff/<tarih>_<aile>/
  models/...glb                 kopyalanacak dosyalar (hedef yollarıyla)
  manifest.json                 id, varyant, boy, soketler, çarpışma, bütçe, hash
  INTEGRATION.md                kokpitteki INTEGRATION_PLAN deseni: bayrak (?m3=1 gibi), yükleme,
                                fallback (GLB yoksa bugünkü çizim tabanlı model), bütçe, test, geri alma
  loader_snippet.js             önerilen yükleyici (oyuna yapıştırılmaz; ana sohbette incelenir)
```

Ana sohbette: paket incelenir → onaylanırsa dosyalar `models/` altına konur, `tools/offline_list.py` çalıştırılır, oyun kodu değişikliği orada yapılır. Varsayılan davranış hiçbir zaman fabrika tarafından değiştirilmez.

---

## 10. Fazlar

| Faz | Kapsam | Çıkış ölçütü |
|---|---|---|
| **0 — Temel** | `core/`'un kokpitten çıkarılması (§3), CLI iskeleti, registry, viewer/check, bpy kurulum doğrulaması, budgets.json | Basit bir test kutusu tüm hattan geçip rapor üretir |
| **1 — İlk NPC gemisi** | `families/ship` + `npc_courier` (en küçük, 16 m) ve `npc_cargo`; trim atlas (Lonca); siluet testi | 2 gemi PASS, gerçek cihaz bench ölçümü, bütçelerin ayarı |
| **2 — Varyasyon** | stil paketleri (3 taraf × 2 evren), varyant matrisi, galeri | 1 gemiden 6 tutarlı varyant, tek doku seti |
| **3 — Büyük varlıklar** | gate, station (unique bake), LOD otomasyonu, meshopt/KTX2 kararı | 1 kapı + 1 istasyon PASS |
| **4 — Hangar ve prop** | hangar iç mekân, kamera soketleri, prop seti | hangar PASS, prop kütüphanesi |
| **5 — Handoff** | ilk paket ana sohbete | ana sohbette onay |

---

## 11. Onay gereken kararlar

1. **Konum**: `tools/asset_factory/` (aynı depo, oyundan yalıtılmış) — öneri. Alternatif: ayrı depo.
2. **Kokpit kodu**: kopyalanıp `core/` olarak genelleşsin, kokpit dalı olduğu gibi kalsın — öneri.
3. **NPC doku modu**: paylaşımlı trim atlas + vertex AO (bellek dostu) — öneri; görsel kalite unique bake'ten biraz düşük.
4. **Referans sadakati**: yeni 3B gemiler mevcut üst/yan çizimlerin silüetine bağlı kalsın mı (IoU ≥ 0,80), yoksa serbest yeniden tasarım mı?
5. **Sıkıştırma**: WebP + quantization her zaman; meshopt (oyuna ~20 KB çözücü gerekir) entegrasyonda karar.
6. **İlk hedef**: Faz 1 için `courier` (küçük, hızlı iterasyon) + `cargo` (büyük, greeble ağırlıklı).
7. Bütçe tablosu (§6.4) başlangıç olarak kabul mü?
