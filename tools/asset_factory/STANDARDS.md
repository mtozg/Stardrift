# Asset Factory Standartları (v0.2, onay bekliyor)

"GEÇİCİ" işaretli maddeler oyun kodunun gözleminden çıkarıldı. Ana sohbetten gelecek `contracts/game_contract.md` ile kesinleşecek.

---

## 1. Görsel dil

Mevcut oyun görselleri (`assets/img/`) incelendi. Fabrikanın koruyacağı dil şu:

| Öğe | Stardrift'teki karşılığı | Fabrika kuralı |
|---|---|---|
| Genel ton | Gerçekçi, kullanılmış gelecek. Sert yüzeyler, yıpranmış metal. Çizgi film ya da düz low-poly değil | Biçim düşük poligonla verilir, yüzey ayrıntısını normal haritası ve trim taşır. Düz renkli yüzey bırakılmaz |
| Ana malzeme | Gunmetal ve gri çelik, açık gri gövde plakaları; panel hatları, perçin, havalandırma ızgarası | `library/materials`: gunmetal, steel, titanium, aluminum, composite |
| Yıpranma | Kenar aşınması, girintide kir, çizik, sızıntı lekesi | Malzemede yıpranma (`wear`), kir (`dirt`) ve çizik (`scratch`) parametreleri zorunlu. Sıfır yıpranma yalnızca Filo'nun "yeni" stilinde serbest |
| Işık vurguları | Küçük, sıcak pencere ışıkları (amber), kırmızı ve yeşil seyir ışıkları, camgöbeği ekranlar, motor parlaması | Emisyon yüzeyin %3'ünü geçmez (boss ve Kadim hariç). Renkler stil paketinden gelir |
| Taraf: Filo | Temiz, açık gri ve beyaz, mavi vurgu | düşük yıpranma, düzenli greeble |
| Taraf: Lonca | Altın ve amber vurgu, düzenli ticari yapılar | amber emisyon, pirinç ve titanyum detay |
| Taraf: Korsan | Paslı, yamalı, asimetrik eklentiler, kırmızı işaret ve yazı | pas malzemesi, yüksek kir, asimetri parametresi, kırmızı decal |
| Kadim | Mor, runik devre desenleri, ışıyan halkalar | `kadim` stili: koyu metal ve mor emisyonlu oyuk desen (trim) |
| Boss / biyo | Organik, dikenli, yeşil biyolüminesans | `biyo` stili: organik kafes ve Subsurf şekiller, yeşil emisyon damarları |
| Evrenler | Ankora (nötr, mavi gökyüzü), Kızıl (lav, pas, turuncu), Buzul (buz, soğuk mavi), Zümrüt (yeşil sis, kristal) | evren stili ton kaydırma, kir rengi ve emisyon tonunu belirler |
| Silüet | Oyundaki üst ve yan çizimler oyuncunun tanıdığı şekil | Çizimi olan varlıkta silüet sadakati ölçülür (QC.md §3). 0,80 yalnızca **prototip** eşiğidir; nihai eşikler sınıfa göre daha yüksektir (`qc/rules.json`) |

Her varlığın `ref/<asset_id>/` klasöründe referans görsel ve kısa stil notu (`style.md`) bulunur. Kapı 1'de render bu referansla yan yana gösterilir.

## 2. Koordinat, ölçek, pivot (GEÇİCİ)

- Oyun uzayı: **X sağ, Y yukarı, −Z ileri** (kokpit hattındaki `g2b` dönüşümüyle tutarlı). Blender'da X sağ, +Y ileri, Z yukarı. glTF dışa aktarımı Y-up yapar, sonuçta burun **−Z**'ye bakar.
- Birim **metre**, gerçek boy. Oyundaki gemi tablosunda boylar var (cargo 70, mining 52, corvette 38, courier 16…).
  - Açık soru (ana sohbet): oyun bugün NPC modelini 1 birim kurup `S.len` ile ölçekliyor. GLB gerçek boyda mı gelsin, normalize mi? Varsayılan: gerçek boy, `extras.length_m` ile birlikte.
- Pivot:

| Aile | Pivot |
|---|---|
| gemi | sınır kutusunun merkezi (X, Y), Z'de kütle merkezine yakın |
| kokpit | pilot gözü (0, 0, 0) |
| istasyon | dönme ekseni merkezi |
| kapı / geçit | halka merkezi, geçiş ekseni −Z |
| hangar ve iç mekân | zemin merkezi, giriş −Z yönünde |
| asteroit ve enkaz | hacim merkezi |
| item | taban merkezi |

- Dönüşümler uygulanmış olur (ölçek 1, dönüş 0). Negatif ölçek yasak.

## 3. Adlandırma

| Şey | Biçim | Örnek |
|---|---|---|
| Varlık kimliği | `<family>_<ad>` (küçük harf, ASCII, `_`) | `npc_ship_cargo`, `structure_gate_kizil`, `env_rock_demir` |
| Varyant | `<asset_id>@<stil>.<param>.s<seed>` | `npc_ship_cargo@lonca-ankora.p6.s4127` |
| Revizyon | `r<NNN>` (her onaylı değişiklikte artar) | `r003` |
| GLB dosyası | `sd_<asset_id>[__<varyant>]_r<NNN>.glb` | `sd_npc_ship_cargo__lonca-ankora_r003.glb` |
| Doku dosyası | `sd_<asset_id>_<kanal>.webp`; kanallar: `base`, `orm`, `normal`, `emit` | `sd_station_ankora_orm.webp` |
| Kök düğüm | `SD_<asset_id>` | |
| LOD | `LOD0`, `LOD1`, `LOD2` | |
| Mesh | `<LOD>_body`, `<LOD>_emit`, `<LOD>_glass` | `LOD0_body` |
| Soket (boş düğüm) | `SOCK_<tür>_<n>`; türler: `engine`, `gun`, `dock`, `light`, `cam`, `fx`, `screen`, `door` | `SOCK_engine_0` |
| Çarpışma | `COL_<ad>` (görünmez) | `COL_hull` |
| Ekran / canlı doku | `SCR_<ad>` (kokpit sözleşmesi: `SCR_SYS`, `SCR_RADAR`, `SCR_HULL`) | |
| Malzeme | `MAT_<rol>` (`body`, `emit`, `glass`, `screen`, `energy`) | |

Türkçe karakter yalnızca görünen metinde kullanılır, dosya ve düğüm adlarında kullanılmaz.

## 4. Geometri

- Biçimi silüet verir. Ekranda 2 pikselden küçük kalacak ayrıntı geometriyle değil, normal haritası ya da trim ile yapılır.
- Gizli yüz yok: birleşen parçalardaki iç yüzler ve hiçbir bakış açısından görünmeyen yüzler silinir.
- Kapalı ve manifold gövde (aile istisnası: iç mekân kabuğu, enerji yüzeyleri).
- Sıfır alanlı yüz, gevşek köşe ve çakışık köşe yok. Normaller dışa bakar.
- Pürüzsüz ve sert kenar ayrımı açıyla yapılır (smooth by angle 30–40°). Pahlar (bevel) yalnızca silüeti ve ışığı etkileyen kenarlarda kullanılır.
- Tekrar eden parçalar (kafes, panel, ışık) Blender'da instance olarak kurulur, dışa aktarımda birleştirilir. Draw call artırılmaz.
- LOD: LOD1 ≈ %45, LOD2 ≈ %15 üçgen. LOD2'de greeble yok, silüet korunur. Geçiş mesafeleri `extras.lod_dist` alanında yazılır (GEÇİCİ: oyun LOD kullanıyor mu, ana sohbette sorulacak).

## 5. UV ve doku

| Kural | Değer |
|---|---|
| Boyut | 2'nin kuvveti. Kalite seviyelerine göre 2048, 1024 ve 512 sürümleri üretilir |
| Biçim | **WebP** (`EXT_texture_webp`), base q=88, orm/normal q=92. JPEG yedeği isteğe bağlı |
| Renk uzayı | `base` ve `emit` sRGB; `orm` ve `normal` doğrusal |
| ORM | R = AO, G = pürüzlülük, B = metaliklik (glTF standardı) |
| Normal | OpenGL / +Y (glTF standardı), tangent uzayı |
| Texel yoğunluğu | gemi ve istasyon 256 px/m (yakın plan: kokpit 1024 px/m), asteroit 128 px/m, iç mekân 512 px/m. QC ±%30 |
| Ada payı | 1024²'de ≥ 4 px, bake kenar uzatması ≥ 8 px |
| Trim modu | Paylaşımlı atlas **aile içinde** (ör. NPC gemileri kendi aralarında, asteroitler kendi aralarında; aile × stil başına 1024²). Bütün evren tek atlasa zorlanmaz. UV kurala göre trim bantlarına yerleşir. AO ve hasar maskesi `COLOR_0` kanalında |
| Unique modu | Varlığa özgü atlas (Smart UV + paketleme). Çakışma yok |
| İkinci UV | Yalnızca iç mekânda pişmiş ışık için (`TEXCOORD_1`, r128'de `uv2`) |

## 6. Malzeme

- **En fazla 3 malzeme**: `MAT_body` (opak PBR), `MAT_emit` (emisyon), `MAT_glass` / `MAT_energy` (gerekirse). Hedef: varlık başına 1–2 draw call (LOD başına).
- Yalnızca **metallic-roughness** kullanılır. r128'in desteklediği uzantılar dışında hiçbiri kullanılmaz. İzin verilenler:
  - `KHR_materials_unlit`: ekran ve enerji yüzeyi
  - `KHR_texture_transform`
  - `KHR_mesh_quantization`
  - `EXT_texture_webp`
  - `EXT_meshopt_compression`: oyuna çözücü eklenirse
- **Yasak:**
  - `KHR_materials_emissive_strength`: r128 desteklemiyor. Kural: emisyon rengi ≤ 1.0, parlaklık oyunda bloom ile verilir.
  - `transmission` ve `clearcoat`: mobilde pahalı.
  - Prosedürel düğümün GLB'ye çıkması: her şey dokuya pişirilir.
- **Cam**: kokpit camı oyunda ayrı katman. Dış modelde cam opak, koyu, düşük pürüzlülükte. Saydamlık yalnızca gerekirse ve `alphaMode: BLEND` ile tek mesh'te.
- Metaliklik ikili gibi davranır (~0 ya da ~1). Arada kalan değerlerin oranı QC'de uyarı verir.
- Base color aralığı: dielektrik sRGB 30–240, metal 120–250.

## 7. Performans bütçeleri (ilk değerler, `qc/budgets.json`)

Kalite referansı Kaşif kokpiti: 3,78 MB GLB, gövde ≤ 60 bin üçgen, ≤ 25 çizim çağrısı, 2048² dokular.

| Sınıf | LOD0 üçgen | LOD1 | LOD2 | Çizim çağrısı | Doku | GLB üst sınırı |
|---|---|---|---|---|---|---|
| item / prop | 800 | 300 | 80 | ≤ 2 | trim | 60 KB |
| env_rock (instanced) | 400 | 150 | 50 | 1 | trim, paylaşımlı | 40 KB |
| npc_ship_small (≤ 25 m) | 2 500 | 1 100 | 350 | ≤ 2 | trim | 150 KB |
| npc_ship_large (≤ 80 m) | 6 000 | 2 700 | 900 | ≤ 3 | trim | 300 KB |
| player_ship (hangar ve dış görünüm) | 12 000 | 5 000 | 1 500 | ≤ 3 | unique 1024² | 1 MB |
| boss | 12 000 | 5 000 | 1 500 | ≤ 3 | unique 1024² | 1 MB |
| cockpit | 60 000 | — | — | ≤ 25 | unique 2048² | 4 MB |
| structure_gate | 10 000 | 4 000 | 1 200 | ≤ 3 | unique 1024² | 1 MB |
| station | 25 000 | 10 000 | 3 000 | ≤ 4 | unique 2048² | 2 MB |
| interior / hangar | 40 000 | — | — | ≤ 6 | unique 2048² + ışık haritası | 3,5 MB |

Karar (2026-11-15): bu tablo **başlangıç değeridir**; gerçek cihaz ve görsel kalite testlerinden sonra revize edilir.

Sahne hedefi (GEÇİCİ): 12 NPC + 1 istasyon + 1 kapı, kokpit dışında ek yük ≤ 4 ms/kare (iPhone 13 sınıfı). GPU doku belleği için tüm evren ≤ 64 MB. Bütçeler ilk gerçek cihaz ölçümünden sonra yeniden ayarlanır.

## 8. Varyasyon ve tekrar üretilebilirlik

- Tüm rastgelelik `seed`'den türetilir. Aynı spec, seed ve kütüphane sürümü, aynı geometri hash'ini verir (QC'de denetlenir).
- Stil paketleri şekli değiştirmez. Değiştirdikleri: malzeme, renk, yıpranma, emisyon rengi, greeble türü ve asimetri.
- Varyantlar aynı trim ve malzeme setini paylaşır. Paylaşım **aile sınırı içindedir**: NPC gemileri kendi atlasını, asteroitler kendi atlasını kullanır. Aileler arası ortak atlas yoktur.
- Kütüphane (`library/`) sürümlenir. Bir varlık hangi kütüphane sürümüyle üretildiğini kaydeder.

## 9. Teslim paketi (her varlık)

```
deliveries/<asset_id>/r<NNN>/
  sd_<asset_id>_r<NNN>.glb             (+ varyant GLB'leri, + _q512/_q1024 kalite sürümleri)
  textures/sd_<asset_id>_{base,orm,normal,emit}.webp   (GLB'ye gömülü olanların ayrı kopyası, inceleme için)
  preview/  hero.png  ortho_6.png  turntable.webp  ref_compare.png  three_vs_cycles.png  lod.png
  spec_sheet.md                        teknik özellikler (aşağıda)
  qc_report.json  qc_report.html
  integration.md                       entegrasyon notu (game_contract yoksa GEÇİCİ damgalı, kod içermez)
  manifest.json                        makine okunur özet: id, rev, hash, boy, soketler, çarpışma, bütçe, dosya listesi
  source.json                          üretimi tekrarlamak için: spec, seed, kütüphane sürümü, fabrika commit'i
```

**`spec_sheet.md` içeriği:** amaç ve oyundaki yeri; boy ve sınır kutusu; LOD bazında üçgen ve köşe sayısı; malzeme ve draw call sayısı; dokular (boyut, biçim, bellek tahmini); soket listesi (konum, yön, amaç); çarpışma tanımı; animasyonlu ve hareketli parçalar; varyant listesi; bütçeye göre doluluk.

**`integration.md` içeriği:** hedef yol; yükleme biçimi (GLB, kalite sürümleri); ölçek ve yön; soketlerin oyundaki karşılığı; malzeme notları (bloom, unlit, canlı doku bağlantısı); fallback (GLB yoksa bugünkü model); performans notu; test adımları; geri alma. Entegrasyon kodu bu belgede yer almaz. Kod, sözleşme kesinleşip sen onaylayınca ana sohbette yazılır.
