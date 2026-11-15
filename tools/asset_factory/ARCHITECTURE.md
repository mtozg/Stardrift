# Stardrift Asset Factory — Mimari ve Üretim Hattı (v0.2, onay bekliyor)

Bu klasör yalnızca tasarım içerir; kod yok, varlık üretilmedi, oyunun hiçbir dosyası değişmedi.

| Belge | İçerik |
|---|---|
| `ARCHITECTURE.md` (bu) | Amaç, kapsam, klasör yapısı, üretim hattı, Claude ile yönetim, fazlar |
| `STANDARDS.md` | Görsel dil, koordinat/ölçek, adlandırma, geometri, malzeme, doku, bütçe, teslim paketi |
| `QC.md` | Kalite kontrol sistemi: kapılar, otomatik testler, görsel kontrol, performans, rapor |

---

## 1. Amaç ve ilkeler

Oyunda kullanılacak 3B varlıkları **Blender Python (bpy) ile prosedürel**, tekrar üretilebilir ve mobilde verimli biçimde üretmek; her varlığı GLB, dokular, teknik özellik ve entegrasyon notlarıyla teslim etmek.

İlkeler:
1. **Oyuna dokunmaz.** Fabrika yalnızca `tools/asset_factory/` içine yazar. Oyun dosyaları (`js/`, `index.html`, `assets/`, `models/`, `vendor/`, `offline.json`, `sw.js`) **salt okunur referanstır**. Oyuna aktarım ancak açık onayla ve ana sohbette yapılır.
2. **Önce görüntü, sonra teknik.** Her varlık önce modellenip render edilir ve görsel olarak onaylanır; optimizasyon ve teknik doğrulama ondan sonra gelir (§4).
3. **Entegrasyon kodu yok** — oyunun Three.js mimarisi ve koordinat sözleşmesi ana sohbetten gelip `contracts/game_contract.md`'ye işlenmeden yükleyici/oyun kodu yazılmaz. O zamana dek entegrasyon notları "GEÇİCİ" damgalıdır.
4. **Her varlık bağımsız**: tek komutla, tek tariften (spec), başka varlığa bağlı olmadan üretilir; parçaları ve malzemeleri kütüphaneden paylaşır.
5. **Görsel dil korunur**: mevcut oyun görselleri her varlığın referansıdır (bkz. `STANDARDS.md §1`); sadakat ölçülür (`QC.md`).
6. **Kalite referansı onaylanmış Blender 3B Kaşif kokpitidir** (`models/cockpit_kasif.glb`; bağlayıcı kurallar `STANDARDS.md §0`). Eski 2B ve paralaks kokpit sistemi yeni üretimde kullanılmaz.

## 2. Kapsam — varlık aileleri

| # | Aile (`family`) | Örnekler | Doku modu | Özel not |
|---|---|---|---|---|
| 1 | `player_ship` + `cockpit` | Kaşif, Şahin, Yük, Hayalet gemileri; her birinin kokpiti | unique | Kokpit pilot kamerasına bağlı; Kaşif hibrit hattı şablon |
| 2 | `npc_ship` | cargo, mining, courier, corvette, tanker, korsan A/B/C/L, boss'lar | trim (boss: unique) | Çok örnek aynı anda → paylaşımlı doku |
| 3 | `station` | Ankora, Demirhan, Kristal, Lonca Pazarı, Kara Liman, karakollar | unique | Yanaşma soketleri zorunlu |
| 4 | `structure` | kapılar (Kızıl, Buzul, Zümrüt, Kadim, ücra), hangarlar, tüneller/geçitler | unique | Geçiş ekseni ve enerji yüzeyi ayrı |
| 5 | `env` | asteroit/cevher kayaları (demir, kristal, buz, titan), enkaz/hurda, kalıntılar, uydu tarlası, kristal monolit | trim / vertex | Instancing dostu, çok varyant, düşük poligon |
| 6 | `interior` + `item` | hangar içi, istasyon iç mekânı; konteyner, sonda, şamandıra, roket, kargo kutusu, pickup | unique (interior) / trim (item) | İç mekânda pişmiş ışık |

Her aile kendi parça kütüphanesine ve kurucusuna (`build`) sahiptir; ortak işler `core/`'dadır.

## 3. Kaşif hibrit sürecinin genellemesi

Kaşif kokpiti (`claude/bold-bardeen-oqf73o` dalı, `tools/cockpit/`) şu hibrit akışla üretildi:
**onaylı 2B çizim → çizimden çıpa/ölçü (anchors) → parametrik geometri → çizimden sınırlı detay projeksiyonu → prosedürel PBR → bake → GLB → Three.js doğrulaması.**

Fabrikada bu akış her aile için standart olur:

| Kokpit adımı | Fabrikadaki genel karşılığı |
|---|---|
| `ck_kasif.webp` çizimi (Kaşif'te yalnızca hat geliştirme aşamasındaki kaynaktı) | **Kokpitlerde kullanılmaz** (`STANDARDS.md §0.1`). Dış modeller ve diğer varlıklarda `ref/`: oyundaki görseller (`ships_*`, `shipx_*`, `olay_*`, `gate_*`, `boss_*`, `a3_*` …) |
| `anchors/build_anchors.py` (cam çokgenleri, ekran düzlemleri) | `core/reference.py` — çizimden siluet maskesi, boy/oran, renk paleti, emisyon noktaları çıkarımı |
| `params/kasif.json` | `specs/<family>/<id>.json` |
| `lib/canopy, dash, seat…` | `families/<family>/parts/*.py` |
| `lib/project.py` (çizimden yüksek frekans detay) | `core/reference.py` — **isteğe bağlı**, yalnızca görünür yüzlere, yalnızca ince detay |
| `lib/materials.py` | `core/materials.py` + `library/materials/*.json` |
| `lib/bake.py`, `render.py` | `core/bake.py`, `core/render.py` (düzeltmelerle, bkz. §3.1) |
| `lib/verify.py`, `verify/glb_check.*` | `qc/` (genelleştirilmiş, bkz. `QC.md`) |
| `INTEGRATION_PLAN.md` | teslim paketindeki `integration.md` şablonu |

### 3.1 Kokpit kodundan alınırken düzeltilecekler
1. `bake.METALLIC` malzeme **adına** bağlı → malzeme tanımına taşınır.
2. `cull_hidden` gözü orijinde varsayar (iç mekân mantığı) → aileye göre: iç mekânda göz noktası(ları), dış modelde çok yönlü görünürlük.
3. Koleksiyon adı `'Cockpit'` sabit; çıktı yalnızca JPEG → parametre; WebP.
4. ORM'nin B (metalik) kanalı hep 1 → gerçek metalik bake.
5. Emisyon `Emission Strength > 1` ile veriliyor → r128 `KHR_materials_emissive_strength` desteklemiyor; oyunda sönük görünür. Kural: emisyon rengi ≤ 1, parlaklık oyunda (bloom) — `STANDARDS.md §6`.
6. Tüm rastgelelik tek `seed`'den türetilir.

Karar (2026-11-15): Kaşif kodu **kopyalanmaz**. İşe yarayan fikirler (koordinat dönüşümü, prosedürel aşınma, kanal bake, ORM, Three doğrulama sayfası) bağımsız ve genel bir `core/` olarak yeniden yazılır. Kaşif'in mevcut kodu ve PR'ı değiştirilmez.

## 4. Üretim hattı

```
 ┌─ A. TASARIM ──────────┐   ┌─ B. MODEL ─────────┐   ┌─ C. GÖRÜNÜM ────────────┐
 │ spec.json + ref/      │──►│ bpy kurulum         │──►│ prosedürel PBR, stil    │
 │ (Claude yazar)        │   │ deterministik, seed │   │ Cycles lookdev render   │
 └───────────────────────┘   └─────────────────────┘   │ referansla yan yana     │
                                                       └───────────┬─────────────┘
                                                                   ▼
                                               ◆ KAPI 1 — GÖRSEL ONAY (sen)
                                                 render sayfası: varlık ⟷ oyun görseli
                                                                   │ onay
 ┌─ D. OYUNA HAZIRLIK ──────────────────────────────────────────┐  ▼
 │ temizlik → LOD → UV (trim/unique) → bake → GLB (WebP, niceleme)│◄─┘
 └───────────────────────────────┬──────────────────────────────┘
                                 ▼
 ┌─ E. TEKNİK DOĞRULAMA (QC.md) ────────────────────────────────┐
 │ statik · Three r128 render (Cycles'a sadakat) · performans    │
 └───────────────────────────────┬──────────────────────────────┘
                                 ▼  PASS
                     ◆ KAPI 2 — TEKNİK ONAY (sen)
                                 ▼
 ┌─ F. TESLİM PAKETİ ───────────────────────────────────────────┐
 │ GLB · dokular · spec sheet · QC raporu · önizleme · entegrasyon│
 │ notu (game_contract yoksa GEÇİCİ)                             │
 └───────────────────────────────┬──────────────────────────────┘
                                 ▼
                ◆ KAPI 3 — OYUNA AKTARIM (ana sohbette, ayrı onay)
```

- A–C hızlı yineleme döngüsüdür (`--fast`: düşük örnek, 3 görünüş, saniyeler–birkaç dakika). Claude render'ları kendisi inceler, spec'i düzeltir, sana yalnızca kendi kontrolünü geçen sürümü gösterir.
- D–E ağırdır (bake). Görsel onaydan önce çalıştırılmaz; böylece reddedilecek tasarıma bake süresi harcanmaz.
- Her aşama çıktısını `work/<asset_id>/<rev>/<NN_stage>/`'a yazar ve girdisinin hash'i değişmedikçe yeniden çalışmaz.
- Kapı 1'de onaylanan render, Kapı 2'de **görsel sadakat referansı** olur: oyuna hazırlık sonrası Three.js görüntüsü bununla karşılaştırılır (`QC.md §4`).

## 5. Klasör yapısı

```
tools/asset_factory/
  ARCHITECTURE.md  STANDARDS.md  QC.md  README.md
  requirements.txt              bpy==5.3.0 numpy pillow scipy pygltflib   (Node: playwright mevcut, gltf-validator, @gltf-transform/cli)
  factory.py                    tek CLI giriş noktası (§6)

  contracts/                    oyunla sözleşme (ana sohbetten gelen bilgiyle doldurulur)
    game_contract.md            koordinat, ölçek, ışık, yükleyici, kalite seviyeleri — şu an BOŞ / GEÇİCİ
    game_contract.json          aynı bilginin makine okunur hâli (QC bunu kullanır)

  core/                         Blender'a bağlı, aileden bağımsız
    geo.py shapes.py seed.py materials.py bake.py cleanup.py lod.py uv.py
    sockets.py collision.py export.py render.py reference.py

  families/                     aile = parça kütüphanesi + kurucu
    player_ship/  cockpit/  npc_ship/  station/  structure/  env/  interior/  item/
      parts/*.py   build.py   schema.json

  library/                      paylaşılan, sürümlenen kaynaklar
    materials/*.json            gunmetal, steel, titanium, composite, rust, glass, emit_* …
    styles/<taraf>.json         filo, lonca, korsan, kadim, biyo (boss)
    styles/<evren>.json         ankora, kizil, buzul, zumrut, lonca_pazari, kara_liman
    trims/<set>/                paylaşımlı trim atlasları (kaynak tarif + üretilmiş WebP)
    lighting/                   lookdev ışık düzenleri (oyunun ışığına yakın + stüdyo)

  specs/<family>/<asset_id>.json   Claude'un düzenlediği tarifler (kaynak gerçeği)
  ref/<asset_id>/               oyundan kopyalanmış referans görseller + notlar (oyun dosyasına bağlantı değil, kopya)

  qc/                           doğrulayıcılar
    budgets.json  rules.json
    static/*.py                 sözleşme, geometri, UV, PBR, bütçe
    visual/*.py                 siluet, renk, Cycles⟷Three farkı, LOD farkı
    viewer/                     check.html bench.html gallery.html compare.html + run_*.js (oyunun vendor/three.min.js'ini okur)

  registry.json                 tüm varlıklar: durum, revizyon, hash, onay kayıtları (git'te)

  work/          (git dışı)     ara çıktılar: .blend, bake PNG, render
  deliveries/    (git'te)       onaylanmış teslim paketleri (STANDARDS.md §9)
```

## 6. Claude ile yönetim

Kaynak gerçeği **spec JSON**'dur; varlık üretmek için kod değil tarif düzenlenir. Yeni bir parça türü gerektiğinde `families/*/parts/`'a kod eklenir.

```
python factory.py new      <family> <asset_id> [--ref ships_cargo]   # şablon spec + ref/ kopyası + ölçü tahmini
python factory.py model    <asset_id> [--fast]                       # A→C, lookdev render
python factory.py review   <asset_id>                                # Kapı 1 sayfası (varlık ⟷ referans)
python factory.py approve  <asset_id> --gate visual|tech             # yalnızca senin açık onayınla
python factory.py prepare  <asset_id>                                # D (Kapı 1 onayı yoksa reddeder)
python factory.py qc       <asset_id> [--perf]                       # E
python factory.py deliver  <asset_id>                                # F (Kapı 2 onayı yoksa reddeder)
python factory.py variants <asset_id> --list|--build
python factory.py status
```

- Her komut sonunda tek satır makine özeti (`RESULT {...}`) yazar; Claude bunu ve PNG'leri okuyup sonraki adımı seçer.
- `registry.json` durumları: `draft → modeled → visual_approved → prepared → qc_pass|qc_fail → tech_approved → delivered → integrated`. Her geçiş: zaman, hash, neden, onaylayan.
- Kapılar komutlarla zorlanır: onaysız aşama atlanamaz.
- Aynı anda tek Blender süreci; bake arka planda.

## 7. Fazlar

| Faz | İçerik | Çıkış ölçütü |
|---|---|---|
| 0 — Temel | `core/` çıkarımı ve düzeltmeler (§3.1), CLI, registry, QC iskeleti, viewer, bpy kurulumu | Bir test kutusu A→F'yi geçer, rapor çıkar |
| 0.5 — Sözleşme | Ana sohbetten gelen bilgiyle `contracts/game_contract.*` | Koordinat, ölçek, ışık, yükleyici, kalite seviyeleri yazılı ve onaylı |
| 1 — İlk varlıklar | Senin seçeceğin ilk varlık(lar) | Kapı 1 + Kapı 2 geçer, gerçek cihaz ölçümü |
| 2+ | Aile aile genişleme | — |

Bu fazların hiçbiri onayın olmadan başlamaz.
