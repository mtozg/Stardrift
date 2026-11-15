# Stardrift Asset Envanteri ve Üretim Planı (v1, onay bekliyor)

Tarih: 2026-11-15 · Hazırlayan: Asset Factory oturumu · **Bu belge hiçbir varlık üretmez, oyun koduna dokunmaz.**

## 0. Kaynaklar, yöntem, sınırlar

İncelenen kaynaklar (yalnızca okundu):

| Kaynak | Ne için |
|---|---|
| `js/game.js` (main, 10 267 satır, 1,42 MB) | Varlık tabloları, 3B kurucular, NPC/istasyon/olay tanımları |
| `assets/img/` (275 dosya), `assets/sfx/`, `assets/fonts/` | Mevcut dosyalar; her dosyanın kodda nerede yüklendiği (dinamik yollar dahil) |
| `README.md` | Oyunun özellik listesi (tek tasarım belgesi niteliğinde kaynak) |
| `index.html`, `sw.js`, `manifest.webmanifest`, `offline.json` | Uygulama simgeleri, çevrimdışı paket |
| Dal `claude/bold-bardeen-oqf73o` (main'e **birleşmemiş** 40 commit, sürüm 1.44.2 → 1.48.0) | Yeni kokpit çizimleri, paralaks ve Blender GLB kokpit, `tools/cockpit/`, `models/cockpit_kasif.glb` |
| Dal `claude/cizim-deneme` → `drafts/cizim/NOTLAR.md` | Üs eklenti modülü çizim denemesi |

Satır referansları `js/game.js:<satır>` biçimindedir ve **main** dalına aittir; dal referansları ayrıca belirtilmiştir.

**Doğrulanamayanlar (açıkça):**
1. **Oyun içi görsel kalite ekran görüntüsüyle doğrulanmadı.** Kalite seviyeleri (§1) kodun kullandığı çizim tekniğinden çıkarılmıştır. Üretimden önce salt-okunur bir "mevcut durum" ekran görüntüsü seti önerilir (§7, adım 0).
2. **Ayrı bir oyun tasarım belgesi (GDD) bulunamadı.** "Tasarımda tanımlı" sınıfı yalnızca README, dal notları ve kodda tanımlı ama dosyası olmayan yuvalardan çıkarıldı.
3. Gemilerin **gerçek boyu (metre)** oyuncu gemileri için kodda tanımlı değil (hangarda göreli ölçek: `len` 3.9–4.9, `js/game.js:3861`). NPC'lerde `L` (16–205) var (`js/game.js:722`).

---

## 1. Mevcut çizim teknikleri ve kalite ölçeği

Oyunda bir varlığın nasıl çizildiği, yeniden modelleme ihtiyacını belirliyor. Koddan çıkan sınıflar:

| Kod | Teknik | Nerede tanımlı | Kalite (çıkarım) |
|---|---|---|---|
| **K5** | Onaylı referans | Kaşif (kullanıcı onayı) | Referans |
| **K4** | Blender GLB, pişmiş PBR | Yalnızca `models/cockpit_kasif.glb` (dal) | Yüksek |
| **K3+** | Varlığa özel kodla kurulmuş ayrıntılı model | `buildKasif3D` (`js/game.js:3553`) | Orta-yüksek |
| **K3** | Üst + yan çizimden izdüşümle 3B gövde (`buildShip3D` + spec tablosu) | `js/game.js:3760`; spec'ler: `SPECS3D` 3861, `NPCSPEC3D` 2744, `STSPEC3D` 2611, `OLAYSPEC` 7388, `SPEC` 8463 | Orta: siluet çizime sadık, yakından düşük geometri. **Doğrulanmadı** |
| **K2** | 2B-in-3B: sprite, çapraz iki düzlem ya da düz düzlem | `rockMesh` sprite 395, `mkShipArt` 3544, uydu tarlası 7149, roket 4991 | Düşük-orta; açıya göre bozulur |
| **K1** | İlkel geometri (kutu/oktahedron/torus) ya da başka varlığın kopyası | aşağıda tek tek | Yer tutucu düzeyi |
| VFX | Shader / prosedürel efekt | kapı girdabı 4802, patlama/kalkan, lazer, motor alevi, hiper tünel | Model değil; bu fabrikanın kapsamı dışında, yalnızca bağımlılık |
| 2B | Ekran katmanı (kokpit çizimi, hangar arka planı, UI) | `CK` 3421, `A3`/`A6`/`A7`/`A8` | 3B model değil |

## 2. Durum sınıfları

| Sınıf | Anlamı |
|---|---|
| **OYUNDA** | Main'de var ve kullanılıyor (K3–K5) |
| **MODEL VAR / ENTEGRE DEĞİL** | Modeli var ama main'de kullanılmıyor |
| **PLACEHOLDER** | Oyunda ama geçici: kod başka varlığın modelini kullanıyor, ilkel geometri ya da yalnızca sprite/parıltı gösteriyor (K1, bazı K2) |
| **TASARIMDA / ÜRETİLMEMİŞ** | Kodda yuvası, README'de ya da notlarda tanımı var; dosyası yok |
| **GELECEK / KARARSIZ** | Oyunda karşılığı olan ama ayrı bir 3B varlık gerekip gerekmediğine karar verilmemiş ihtiyaç |

Öncelik: **P1** (ilk üretim grubu) … **P5** (en son / karar sonrası).

---

## 3. Oyuncu gemileri ve kokpitler (özel inceleme)

Kaynak: `PSHIPS` (`js/game.js:1077`).

| id | Ad | Fiyat | Rol (oyun metni) | Çarpanlar (itiş/dönüş/hız/gövde/kalkan/kargo) |
|---|---|---|---|---|
| `kasif` | Kaşif | 0 | "Dengeli, her işe uygun. Ücretsiz." | 1 / 1 / 1 / 1 / 1 / 1 |
| `sahin` | Şahin | 4500 | "Avcı gemisi: çevik, hızlı, güçlü kalkan. Kargosu küçük." | 1.3 / 1.3 / 1.15 / 0.9 / 1.5 / 0.7 |
| `yuk` | Yük Devi | 5000 | "Ağır madenci: iki kat kargo, sağlam gövde. Yavaş." | 0.8 / 0.75 / 0.85 / 1.7 / 1 / 2 |
| `hayalet` | Hayalet | 7500 | "Hızlı ve hafif: en yüksek hız. Gövdesi ince." | 1.4 / 1.15 / 1.3 / 0.8 / 1.2 / 1.2 |

### 3.1 Dış model (hangar, sinematik, hiper atlama)

Oyuncu oyunu kokpitten oynar; dış model `mkShip(id)` ile **dört yerde** kullanılır (`js/game.js:3905`):
hangar gemi görüntüleyicisi `hgSet` (3942), hangar giriş/çıkış sineması (4266), 3B hiper atlama (6558) ve kapı geçişi (6770).
Hangarda ölçek düzeltmesi var: Kaşif ×0.86, Yük Devi ×1.16 (`js/game.js:6114`).

| Gemi | Mevcut dosyalar (main) | Çizim tekniği | Tasarım (çizimlerden, isimden değil) |
|---|---|---|---|
| Kaşif | `shipart_kasif_top/side.webp`, `shipx_kasif_f/r/b.webp` | **K3+**: `buildKasif3D` (özel ayrıntılı model, `mkShip3D` ×4.4) | **Onaylı referans; dokunulmayacak.** |
| Şahin | `shipart_sahin_top/side.webp`, `shipx_sahin_f/r/b.webp` | **K3**: `SPECS3D.sahin` (gövde profili, 2 kanat, eğik dikey kuyruk, 1 tüp motor, kanopi elipsoidi) | Beyaz-gri gövde, **kırmızı şeritler**; ok gibi geriye süpürülmüş ana kanatlar, öne eğik ikiz dikey kuyruk; damla kanopi; **tek büyük arka motor** (pembe-mor alev) |
| Yük Devi | `shipart_yuk_top/side.webp`, `shipx_yuk_f/r/b.webp` | **K3**: `SPECS3D.yuk` + **mekanik kıskaç** parçası (`claw`, `js/game.js:3879`) | Haki/amber kutu gövde; yanlarda **konteyner dizileri**; uyarı şeritleri; **8 dairesel motor** (3-2-3, kare çerçeve); burunda **mekanik kıskaç kol**; mor camlı köprü |
| Hayalet | `shipart_hayalet_top/side.webp`, `shipx_hayalet_f/r/b.webp` | **K3**: `SPECS3D.hayalet` (kanat, ince tüp motorlar, `gain 1.15`) | Antrasit/siyah **köşeli (stealth) gövde**; **mor ışık şeritleri**; ince, geriye süpürülmüş kanatlar; **4 motor** (2×2, mor) |

Yedek: 3B kurulamazsa `mkShipArt` iki düz çizim düzlemi gösterir (`js/game.js:3544`).
Not (dal geçmişi): 1.47.0'da Hayalet ve Yük Devi için **Sketchfab hazır modelleri** denenmiş, aynı gün **geri alınmış** (`5dab798`). Lisans/kalite gerekçesi kayıtta yok.

### 3.2 Kokpitler

Kokpit, uçuşun %100'ünde ekranda olan katmandır. **İki nesil var ve main ile dal farklı:**

| | main (1.44.1, yayındaki) | dal `claude/bold-bardeen-oqf73o` (birleşmemiş) |
|---|---|---|
| Kaşif | `ck_kasif.webp` (2400×984 çizim; 3 ekran yuvası `CKP`, `js/game.js:3421`) | **Yeni çizim (1.46.0)** + **paralaks kokpit varsayılan** (`?ck=q`, 1.47.1) + **Blender GLB** `models/cockpit_kasif.glb` (3,78 MB, yalnızca `?ck=b`, 1.48.0) + `tools/cockpit/` hattı |
| Şahin | `ck_sahin.webp`: kemerli fanus cam, kırmızı panelli konsol, ortada kumanda kolu | Yeni çizim: geniş kemer cam, **kırmızı** ışık şeritleri, koltuk önde |
| Yük Devi | `ck_yuk.webp`: dört bölmeli düz cam, haki konsol, uyarı şeritleri | Yeni çizim: **ızgara camlar** (3 sıra), amber ışık, "CARGO HAULER H-07" yazıları |
| Hayalet | `ck_hayalet.webp`: tek orta dikme, çok koyu, ince ekranlar | Yeni çizim: **mor** ışık şeritli geniş cam, koyu metal |

Yapı (her iki nesil): 1600×656 referans uzayında **3 canlı ekran dörtgeni** (Sistem / Radar / Gövde: `bars`, `map`, `hull`), lambalar ve itiş göstergesi konumu (`CKP`).
Dalda tanımlı ama **dosyası olmayan yuvalar**: `assets/img/ck3p_<gemi>.webp` (kokpit kabuğu boyama, 4 gemi) ve `assets/img/ck3_kokpit.glb` (Sketchfab kokpiti; dosya 1.46.0'da kaldırılmış, kod hâlâ `sd_ck3=g` ile arıyor).

### 3.3 Oyuncu gemisi envanteri

| Varlık | Durum | Kalite | Yeniden modelleme | Öncelik |
|---|---|---|---|---|
| Kaşif dış | OYUNDA | K3+ / **K5 (onaylı)** | **Hayır — dondurulmuş** | — |
| Kaşif kokpit | main: 2B çizim · dal: paralaks + GLB | **K5 (onaylı)** | **Hayır — dondurulmuş** | — |
| Şahin dış | OYUNDA | K3 | Evet (GLB, hangar yakın planına uygun) | **P1** |
| Şahin kokpit | OYUNDA (2B çizim) | 2B | Evet (Kaşif GLB hattıyla) | **P1** |
| Yük Devi dış | OYUNDA | K3 (+kıskaç) | Evet | **P1** |
| Yük Devi kokpit | OYUNDA (2B çizim) | 2B | Evet | **P1** |
| Hayalet dış | OYUNDA | K3 | Evet | **P1** |
| Hayalet kokpit | OYUNDA (2B çizim) | 2B | Evet | **P1** |

Teknik bağımlılıklar (dördü için ortak): GLTFLoader yalnızca dalda (`vendor/GLTFLoader.js`); main'de yok. Kokpit GLB yolu (`?ck=b`) yalnızca Kaşif'e bağlı ve dalda. Canlı ekran sözleşmesi (`SCR_SYS/RADAR/HULL`, `CKP` izdüşümü). Çevrimdışı paket politikası (GLB `offline.json`'a eklenmiyor).

---

## 4. Diğer varlıklar (kategori bazında)

### 4.1 NPC ve düşman gemileri

Kaynak: `NPC_DEF` (`js/game.js:722`), çizimler `SHIPS` (2721), 3B gövde `NPCSPEC3D` (2744), giydirme `dressNpcs`.

| Varlık (tür → skin) | Oyundaki görevi | Dosyalar | Boy `L` | Durum / kalite | Yeniden modelleme | Öncelik |
|---|---|---|---|---|---|---|
| raider → `korsanA` "Akbaba" | En sık korsan (5 farklı çağrı yeri), vur-kaç | `ships_korsana_top/side` | 26 | OYUNDA · K3 | Evet | **P2** |
| brute → `korsanB` "Kurt" | Korsan, dibine girer | `ships_korsanb_*` | 44 | OYUNDA · K3 | Evet | **P2** |
| reaver → `korsanC` "Yağmacı" | Ağır korsan; "Aranan korsan" sinyali | `ships_korsanc_*` | 58 | OYUNDA · K3 | Evet | **P2** |
| corvette "Devriye" | Devriye; **mürettebat eskortu**, **ödül avcısı** (korsan tarafta), Filo komutanı | `ships_corvette_*` | 38 | OYUNDA · K3 | Evet | **P2** |
| cargo "Kargo" | Tüccar; yardım/eskort/konvoy; **ziyaretçi uygarlık** gövdesi | `ships_cargo_*` | 70 | OYUNDA · K3 | Evet | P2 |
| tanker | Tüccar; konvoy; ziyaretçi gövdesi | `ships_tanker_*` | 90 | OYUNDA · K3 | Evet | P2 |
| courier "Kurye" | Tüccar; **gezgin tüccar** sinyali | `ships_courier_*` | 16 | OYUNDA · K3 | Evet | P2 |
| mining "Madenci" | Madenci; "arıza" sinyali | `ships_mining_*` | 52 | OYUNDA · K3 | Evet | P2 |
| leader → `korsanL` | Korsan lideri (adlı: Kavrim, Nivea, Silva, Vask…), 4 motor alevi | `ships_korsanl_*` | 120 | OYUNDA · K3 | Evet | P3 |
| boss0 Kara Kaptan Dorak (Ankora) | Patron | `boss_dorak_*` | 190 | OYUNDA · K3 | Evet | P3 |
| boss1 Kızıl Kaptan Zerha (Kızıl) | Patron | `boss_zerha_*` | 200 | OYUNDA · K3 | Evet | P3 |
| boss2 Kırağı Hanı Hiem (Buzul) | Patron | `boss_hiem_*` | 205 | OYUNDA · K3 | Evet | P3 |
| boss3 Sis Efendisi Verdan (Zümrüt) | Patron (organik, yeşil) | `boss_verdan_*` | 195 | OYUNDA · K3 | Evet | P3 |
| boss4 **Kiralık Kaptan Varak** (Lonca Pazarı) | Patron | **çizim yok** | 190 | **PLACEHOLDER**: Dorak'ın modeli (`js/game.js:734`) | **Önce tasarım** | P4 (tasarım bloklu) |
| boss5 **Liman Ağası Morr** (Kara Liman) | Patron | **çizim yok** | 200 | **PLACEHOLDER**: Zerha'nın modeli (`js/game.js:734`) | **Önce tasarım** | P4 (tasarım bloklu) |
| Ziyaretçi uygarlık gemileri | Telsizle konuşan yabancı ziyaretçiler | portreler `devi_0..3` var; gemi yok | — | **PLACEHOLDER**: renklendirilmiş cargo/tanker (`js/game.js:4380`) | Karar gerekli | GELECEK / KARARSIZ |
| Ödül avcısı gemisi | Aranma ★ ile gelir | — | — | raider/brute/corvette yeniden kullanımı (`js/game.js:8569`) | Karar gerekli | GELECEK / KARARSIZ |

### 4.2 Uzay istasyonları

| Varlık | Görevi | Dosyalar | Teknik | Durum | Yeniden modelleme | Öncelik |
|---|---|---|---|---|---|---|
| Ankora İstasyonu | Ana üs, başlangıç | `a3_ankora_top/side` | K3 (`STSPEC3D.ankora`) | OYUNDA | Evet | **P3** (ilk istasyon) |
| Demirhan Üssü | Kızıl Geçit uzmanlık istasyonu | `a3_demirhan_*` | K3 | OYUNDA | Evet | P3 |
| Buzul Durağı | Buzul Halka istasyonu | `a3_ice_top/side/fr` | K3 | OYUNDA | Evet | P3 |
| Kristal Kapısı | Zümrüt Sis istasyonu | `a3_kristal_*` | K3 | OYUNDA | Evet | P3 |
| Lonca Pazarı | Tüccar Loncası ev sistemi | `olay_lonca_top/side` | K3 (`SPEC.lonca`, `js/game.js:8463`) | OYUNDA | Evet | P3 |
| Kara Liman | Korsan Birliği sığınağı (asteroit içi) | `olay_kara_top/side` | K3 (`SPEC.kara`) | OYUNDA | Evet | P3 |
| Oyuncu üssü ("<Pilot> Üssü") | Kendi Üssün | `olay_us_top/side` | K3 (`OLAYSPEC.us`); yüklenemezse `buildOutpost` ilkel (`js/game.js:175,184`) | OYUNDA | Evet | P3 |
| İlkel istasyon (`buildOutpost`) | Yedek / ilk yükleme anı | — | K1 (silindir+torus+kutu) | Yedek | Hayır (yedek kalabilir) | — |

### 4.3 Kapılar, hangarlar ve geçitler

| Varlık | Görevi | Dosyalar | Teknik | Durum | Yeniden modelleme | Öncelik |
|---|---|---|---|---|---|---|
| Geçit kapıları (Ankora↔Kızıl/Buzul/Zümrüt) | Sistemler arası geçiş | `gate_<evren>_yuzey/enerji` (`GK`, `js/game.js:4833`) | Prosedürel çerçeve (torus/silindir/kutu) + shader girdabı | OYUNDA | Çerçeve: Evet · girdap: shader kalır | P4 |
| Kadim Kapı | 16 kalıntı sonrası uyanan son kapı | `gate_kadim_yuzey/enerji`, `a8_i_kadim` | Prosedürel (torus×2, kutu, disk) | OYUNDA | Evet | P4 |
| Ücra düşman kapıları (Lonca/Korsan) | Ev sistemleri arası gizli kapı | `gate_lonca_enerji`, `gate_korsan_enerji` | Prosedürel (torus, kutu, disk) | OYUNDA | Evet | P4 |
| Hangar 3B sahnesi | İstasyon içi; gemi görüntüleyici | `ximg_in/out`, `xhull_*_d`, `xdoor_*`, `xtv_*` (6 istasyon) | Prosedürel geometri + çizim dokuları (`js/game.js:4157–4163`) | OYUNDA | Karar (iç mekân, §4.6) | P5 |
| Hangar arka planları | Menü sahnesi | `a3_hangar`, `a6_h1..3`, `a6_h_lonca/kara` | 2B | OYUNDA | Kapsam dışı (2B) | — |
| İstasyon tünelleri | Yanaşma/kalkış animasyonu | — (kodla üretilen metal/buz/kristal/pas dokuları) | Prosedürel (`js/game.js:6151`) | OYUNDA | Karar | P5 |
| Hiper atlama / sıçrama tüneli | Efekt | — | VFX | OYUNDA | Hayır (VFX) | — |

### 4.4 Asteroitler, maden ve kaynak nesneleri

| Varlık | Görevi | Dosyalar | Teknik | Durum | Yeniden modelleme | Öncelik |
|---|---|---|---|---|---|---|
| Cevher kayaları ×5 tür (demir, kristal, buz, titan, hurda) × 3 varyant | Madencilik (çekirdek döngü), lazerle kırılır | `ore3_<tür>_1..3` (15) | **K2: sprite** (resim yüklenince `rockMesh` 3B yerine `THREE.Sprite` döner, `js/game.js:395`); prosedürel 3B kaya yalnız yedek | OYUNDA (2B) | **Evet** (aile içi ortak atlas, instancing) | **P2** |
| Kaya dokuları | Prosedürel kaya yedeği | `a3_tdemir/tbuz/tkristal` | Doku | OYUNDA | — | — |
| Dökülen cevher parçası (pickup) | Toplanan cevher | `orep_<tür>` (5) + prizma Lathe | K2/K3 karışık | OYUNDA | Evet (küçük, ucuz) | P2 |
| Cevher simgeleri | UI | `orei_*`, `picon_*` | 2B | OYUNDA | Kapsam dışı | — |
| Kırık parça / enkaz (`addDebris`) | Patlama ve kaya kırılması | — | Prosedürel küçük parçalar | OYUNDA | Evet (prop seti) | P4 |
| Lav kayaları akıntısı (Kızıl) | Tehlike bölgesi | — | Kaya mesh'i + emisyon (`js/game.js:7149` civarı) | OYUNDA | Evet (kaya ailesinden varyant) | P4 |

### 4.5 Çevre nesneleri ve olay modelleri

| Varlık | Görevi | Dosyalar | Teknik | Durum | Yeniden modelleme | Öncelik |
|---|---|---|---|---|---|---|
| Kalıntılar (16 adet, tek model) | Kadim yankılar hikâyesi | `olay_kalinti_top/side`, `a3_harabe` | K3 (`OLAYSPEC.kalinti`) | OYUNDA | Evet (16 yerde aynı model: varyasyon adayı) | P4 |
| Korsan kampı | Sinyal olayı | `olay_kamp_top/side` (yedek: 5 kutu) | K3 | OYUNDA | Evet | P4 |
| **Patron inleri** | 6 patronun ini | kamp modelinin ×520 ölçekli kopyası (`js/game.js:7327`) | K3 kopya | **PLACEHOLDER** | Evet (ayrı tasarım) | P4 |
| Terk edilmiş istasyon | Sinyal olayı | `olay_istasyon_top/side` (yedek: torus+silindir) | K3 | OYUNDA | Evet | P4 |
| Eski uydu tarlası (Ankora) | Lazerle sökülebilir hurda | `olay_sat_top/side` | **K2: çapraz düzlem** | OYUNDA (2B) | Evet | P4 |
| **Buz devleri (Buzul)** | Bölge özelliği | — | **K1: `OctahedronGeometry`** (`js/game.js:7149`) | **PLACEHOLDER** | Evet | P4 |
| **Kristal monolitler (Zümrüt)** | Bölge özelliği | — | **K1: `BoxGeometry` 26×200×26** emisyonlu | **PLACEHOLDER** | Evet | P4 |
| Sis bulutları (Zümrüt) | Korsandan saklanma | `a3_fog0..2` | Sprite | OYUNDA | Hayır (VFX) | — |
| Kuyruklu yıldız | Gökyüzü | `a3_comet` | Sprite | OYUNDA | Hayır | — |
| Gezegenler (Veyra, Lira, Orrin, Marzan, Buzay + sistem başına ana gezegen) | Arka plan | `pmap_*`, `a4_p0..5`, `env_*`, `a3_mars`, `a3_buzay` | Doku kaplı küre + atmosfer | OYUNDA | Hayır (küre yeterli) | — |

### 4.6 İç mekânlar

| Varlık | Durum | Not |
|---|---|---|
| Hangar içi (6 istasyon) | OYUNDA: prosedürel + çizim dokuları | Tam 3B iç mekân üretimi büyük iş; önce tasarım ve sözleşme gerekir |
| İstasyon tünelleri (6, istasyona özel süsler `js/game.js:5516`, 6151) | OYUNDA: prosedürel | Aynı |
| Kokpitler | §3.2 | Oyuncu gemisi grubunda |

### 4.7 Silahlar ve savunma

| Varlık | Teknik | Durum | Yeniden modelleme | Öncelik |
|---|---|---|---|---|
| Güdümlü / güdümsüz roket (uçuşta) | İlkel silindir+koni, çizim yüklenince **düz düzlem** (`a6_rk_d`, `a6_rk_g`, `js/game.js:626, 4991`) | OYUNDA (K2) | Evet (2 küçük model) | P4 |
| Roket başlık türleri (standart, ağır, küme, delici, Sarsıntı) | Görsel olarak iki çizimi paylaşır | OYUNDA | Karar (türe göre ayrı model?) | GELECEK / KARARSIZ |
| Lazer başlıkları (darbe, çift, plazma, madenci), mermiler | Huzme dokusu + `A7` çizimleri (2B) | OYUNDA | Hayır (VFX) | — |
| Kalkan, patlama | Shader | OYUNDA | Hayır | — |
| Gemi üstü silah donanımı (namlu, rampa) | — | Yok | Karar | GELECEK / KARARSIZ |

### 4.8 Ticaret ve etkileşim nesneleri

| Varlık | Teknik | Durum | Yeniden modelleme | Öncelik |
|---|---|---|---|---|
| **Kaçak yük (cache)** | **K1: kahverengi `BoxGeometry` 9×7×9** + parıltı (`js/game.js:3297`) | **PLACEHOLDER** | Evet (konteyner) | P4 |
| **Kayıp sonda** (sinyal) | **Yalnızca parıltı sprite'ı**, sonda modeli yok (`js/game.js:5666`) | **PLACEHOLDER** | Evet | P4 |
| **Bilinmeyen enerji** (sinyal) | Yalnızca parıltı sprite'ı (`js/game.js:5648`) | OYUNDA (efekt olabilir) | Karar | GELECEK / KARARSIZ |
| Düşmüş kargo (sinyal) | Cevher pickup'ları + parıltı | OYUNDA | Pickup ile birlikte | P2 |
| Toplama çekim ışını | VFX | OYUNDA | Hayır | — |

### 4.9 UI için 3B varlıklar

| Varlık | Durum | Not |
|---|---|---|
| Hangar gemi görüntüleyicisi | OYUNDA: oyuncu gemisi modellerini kullanır (`hgSet`) | Oyuncu gemileri üretilince kendiliğinden kapsanır |
| Donanım simgeleri ("sade 3B görünüm") | **2B SVG** (`js/game.js:9217`) | 3B'ye çevirmek KARARSIZ |
| Rozetler, HUD, radar, harita | 2B | Kapsam dışı |

### 4.10 Projede gördüğüm ek kategori: tasarımda tanımlı ama üretilmemiş

| Varlık | Kaynak | Durum |
|---|---|---|
| **Üs eklenti modülleri** (tamirhane, depo, roket, savunma; her biri 3 seviye) | Kodda yalnızca veri (`js/game.js:6877`); `drafts/cizim/NOTLAR.md` (cizim-deneme): 3×2 modül sayfası ve güneş paneli kanadı çizim denemesi **başarısız** | TASARIMDA / ÜRETİLMEMİŞ: görsel karşılık yok |
| Kokpit kabuk boyamaları `ck3p_<gemi>.webp` | dal: kodda yuva var, dosya yok | TASARIMDA / ÜRETİLMEMİŞ (yeni GLB hattı varsa gereksiz olabilir) |
| `ck3_kokpit.glb` (Sketchfab) | dal: kod yuvası var, dosya 1.46.0'da kaldırıldı | Ölü yuva; üretim gerektirmez, temizlik kararı ana sohbette |
| Varak ve Morr'un kendi gemileri | README'de adlı patronlar; çizim yok | TASARIMDA / ÜRETİLMEMİŞ |

### 4.11 Main'de olmayan ama dalda var olan (MODEL VAR / ENTEGRE DEĞİL)

| Varlık | Dosya | Durum |
|---|---|---|
| Kaşif Blender kokpit | `models/cockpit_kasif.glb` (dal) | Yalnızca `?ck=b` ile, dalda. Main'e birleşmedi |
| Dört yeni kokpit çizimi | `assets/img/ck_*.webp` (dal sürümü) | Dalda; main'deki eski sürümlerin yerine geçer |
| Paralaks kokpit (Kaşif varsayılanı) | dal `js/game.js` (`qOn`) | Dalda |

Main dalında kod tarafından **yüklenmeyen görsel dosya yok**: 275 görselin tamamı doğrudan ya da dinamik yolla (`gate_`, `ore3_`, `orep_`, `pmap_`, `olay_*`, `xdoor_*`) kullanılıyor.

---

## 5. Eksik varlık listesi (özet)

**Yer tutucu (oyunda, gerçek varlığı yok):**
1. Varak'ın gemisi (Dorak modelini kullanıyor)
2. Morr'un gemisi (Zerha modelini kullanıyor)
3. Patron inleri (korsan kampı ×520)
4. Buz devleri (oktahedron)
5. Kristal monolitler (kutu)
6. Kaçak yük konteyneri (kutu)
7. Kayıp sonda (yalnızca parıltı)
8. Ziyaretçi uygarlık gemileri (renklendirilmiş kargo/tanker)

**2B'de kalmış, 3B'ye taşınması gereken (oyunda):**
9. Cevher kayaları (15 sprite)
10. Uydu tarlası (çapraz düzlem)
11. Roketler (düz düzlem)

**Tasarımda, hiç üretilmemiş:**
12. Üs eklenti modülleri (4 modül × 3 seviye)
13. Kokpit boyama dokuları `ck3p_*` (yeni hat varsa gereksiz olabilir)

**Kararsız (önce karar):**
14. Ödül avcısına özel gemi
15. Roket türüne göre ayrı modeller
16. Bilinmeyen enerji kaynağı nesnesi
17. 3B donanım simgeleri
18. Gemi üstü silah donanımı
19. Hangar ve tünel iç mekânlarının tam 3B üretimi

---

## 6. Bağımlılıklar

```
Oyun sözleşmesi (ana sohbet: koordinat, ölçek, ışık, LOD, kalite seviyeleri)
 ├─ GLTFLoader main'de yok → dalın birleşmesi ya da yükleyicinin eklenmesi (ana sohbet kararı)
 │    └─ HER GLB entegrasyonu buna bağlı
 ├─ Kokpit GLB yolu (?ck=b) yalnız Kaşif'e bağlı ve dalda → Şahin/Yük Devi/Hayalet kokpitleri için genelleştirilmeli
 └─ Çevrimdışı paket politikası (GLB'ler offline.json'a girecek mi?)

Oyuncu gemisi dış modeli ──► hangar görüntüleyici, hiper atlama, kapı geçişi, hangar sineması (mkShip ile otomatik)
Oyuncu kokpiti ──► canlı ekran sözleşmesi (SCR_*, CKP), kokpit çiziminin hangi nesli kanonik? (main / dal)
NPC ortak atlası (aile içi) ──► 9 NPC gemisi; patronlar unique bake
Asteroit ortak atlası ──► 15 kaya + lav kayaları + pickup'lar; instancing (oyun tarafı kararı)
korsanA/B/C ──► ödül avcısı, aranan korsan, korsan kampı korumaları (yeniden kullanım)
cargo/tanker ──► ziyaretçi uygarlıkları (ayrı tasarım kararı gelene kadar)
Korsan kampı modeli ──► patron inleri (ayrılması önerilir)
Kalıntı modeli ──► 16 kalıntı noktası (varyasyon)
Kapı çerçevesi ──► kapı girdap shader'ı (oyunda kalır; çerçeve-girdap sözleşmesi gerekir)
Varak, Morr, üs modülleri, ziyaretçi gemileri ──► ÖNCE KONSEPT/TASARIM (çizim yok)
```

---

## 7. Önerilen üretim sırası

**Adım 0 (salt okunur, üretim değil):** Main'in yerel kopyasında Playwright ile mevcut durum ekran görüntüleri alınır: hangarda 4 gemi, 4 kokpit, Ankora istasyonu, korsan savaşı, kaya kuşağı. "Önce/sonra" karşılaştırması ve gerçek kalite tespiti için gerekli. Oyun dosyalarına yazılmaz.

### Grup 1: Oyuncu gemileri (ilk üretim grubu)

Kaşif **tamamlanmış ve onaylı**; dosyalarına dokunulmaz, kalite ve teknik referanstır.

Önerilen sıra:

| Sıra | Gemi | Gerekçe |
|---|---|---|
| 1 | **Şahin** | Oyuncunun satın alabildiği ilk gemi (4500). Topolojisi Kaşif'e en yakın (avcı, tek kanopi, süpürülmüş kanat) → Kaşif hattının yeniden kullanılabilirliğini en düşük riskle sınar |
| 2 | **Yük Devi** | Satın alma sırasında ikinci (5000). Siluet ve kokpit en farklı olanı (kutu gövde, 8 motor, ızgara cam). **Kıskaç kolu** ayrı bir karar gerektirir: statik mi, oyunda hareketli mi? |
| 3 | **Hayalet** | En pahalı, oyunun sonlarında alınan gemi (7500). Geometrisi en sade (köşeli) ama koyu malzeme ve mor emisyon şeritleri, emisyon kuralı (≤1, bloom) için kalibrasyon ister |

Her gemi için iki varlık var: **kokpit** (uçuşun %100'ü) ve **dış model** (hangar ve sinematik). Öneri: her gemide önce kokpit, sonra dış model. Kokpit, Kaşif hattının doğrudan devamıdır.

### Grup 2: Çekirdek oyun döngüsü (en sık görünenler)

1. **Cevher kayaları** (5 tür × 3 varyant, asteroit aile atlası): madencilik sürekli ekranda; şu an 2B sprite.
2. **Cevher pickup'ları** (5): küçük, kayalarla aynı atlas.
3. **Korsanlar:** raider (`korsanA`) → brute (`korsanB`) → reaver (`korsanC`). Savaşın tamamı.
4. **Devriye korveti:** eskort, ödül avcısı, Filo komutanı olarak da kullanılır.
5. **Tüccarlar:** cargo → tanker → courier → mining (NPC aile atlası).

### Grup 3: İstasyonlar

Ankora (ana üs) → oyuncu üssü → Demirhan → Buzul Durağı → Kristal Kapısı → Lonca Pazarı → Kara Liman.

### Grup 4: Kapılar ve hikâye yapıları

Geçit kapı çerçeveleri → ücra kapılar → **Kadim Kapı** (ana görevin finali) → kalıntı (16 nokta için varyasyon).

### Grup 5: Patronlar ve lider

`korsanL` → Dorak, Zerha, Hiem, Verdan. **Varak ve Morr önce konsept tasarımı ister** (bloklu).

### Grup 6: Yer tutucu çevre ve olay nesneleri

Buz devleri, kristal monolitler (ikisi de K1) → korsan kampı → terk edilmiş istasyon → patron inleri → uydu tarlası → lav kayaları.

### Grup 7: Küçük nesneler (prop)

Roket (2 model) → kaçak yük konteyneri → kayıp sonda → enkaz/hurda parça seti.

### Grup 8: İç mekânlar ve kararsızlar

Hangar ve tünel iç mekânları, üs eklenti modülleri, ziyaretçi gemileri, ödül avcısı, roket türü modelleri, 3B donanım simgeleri: önce tasarım/karar, sonra üretim.

---

## 8. Üretim profilleri ve onay akışı

| Profil | İçerik | Çıktı | Sonraki adım |
|---|---|---|---|
| **PREVIEW** | Hızlı blokaj modelleme, kütüphane malzemeleri, düşük örnekli Cycles (`factory.py model --fast`), referans çizimle yan yana, 128 px okunabilirlik, siluet karşılaştırması | `review.html`: hero, 6 dik görünüş, yakın plan, referans | **Kapı 1: senin görsel onayın.** Onaysız PRODUCTION başlamaz |
| **PRODUCTION** | Onaylı tasarımın ayrıntılı modellemesi, UV, doku, bake, LOD, optimizasyon, GLB, QC (L2–L4), teslim paketi | GLB, dokular, spec sheet, QC raporu, entegrasyon notu | **Kapı 2: teknik onay**, sonra **Kapı 3: oyuna entegrasyon onayı** (ana sohbette, ayrı) |

Fabrikada bu iki profil şu an `--fast` bayrağı ve aşama kapılarıyla karşılanıyor. Adlandırılmış profil dosyası (`profiles/preview.json`, `profiles/production.json`) üretim başlamadan küçük bir ek olarak yapılabilir.

---

## 9. Senden karar gereken noktalar

1. **"Onaylı Kaşif" tam olarak hangi çıktı?** Dalda Blender GLB kokpit (`?ck=b`), dalda paralaks kokpit (`?ck=q`, varsayılan), main'de eski 2B çizim ve dış model `buildKasif3D`. Dördünü de dondurulmuş sayıyorum; kalite referansı olarak hangisini esas alayım?
2. **Kokpit çiziminin kanonik nesli:** Şahin, Yük Devi ve Hayalet kokpitleri main'deki eski çizimlere mi, daldaki yeni (1.46.0) çizimlere mi göre modellenecek?
3. **Dalın durumu:** `claude/bold-bardeen-oqf73o` main'e birleşecek mi? GLB entegrasyonu (GLTFLoader) buna bağlı. Bu, ana sohbetin kararı.
4. **Gemi içi sıra:** Her gemide önce kokpit mi, önce dış model mi? (Önerim: kokpit.)
5. **Yük Devi kıskacı:** Statik model mi, hareketli parça mı?
6. **Sketchfab denemesinin geri alınması (1.47.0):** Hazır model / üçüncü taraf varlık kullanmama bir ilke mi? (Fabrika şu an tamamen prosedürel üretiyor.)
7. Tasarımı olmayan varlıklar için (Varak, Morr, üs modülleri, ziyaretçi gemileri) **konsept önce kimden gelecek?** Senden çizim mi, yoksa fabrikada PREVIEW blokajı ile konsept önerisi mi?
