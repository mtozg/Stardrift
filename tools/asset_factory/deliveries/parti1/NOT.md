# Parti 1 (Mehmet onaylı): C (enkaz, lav kayası), H (roket, kaçak yük, kayıp sonda), G düşük risk (buz devi, kristal monolit, patron ini, uydu) — ilk tur adaylar
Hat: `families/prop/build.py` (14 nesne, 10 yerleşim) → `pipeline/model.py` → `pipeline/prepare.py` (prosedürel malzeme → UV → bake → LOD) → GLB. Hepsi tek malzeme, LOD0/LOD1, normal haritalı (1024/512/512). **Sözleşme notu:** props için ölçek = EN BÜYÜK boyut 1,0 (gemilerdeki 'uzunluk = 1,0' değil), merkez orijin, yukarı +Y, uzun eksen +Z (roket/uydu), çapa yok.

| Nesne | Dosya | LOD0 / LOD1 üçgen | Boyut | Texel px/m |
|---|---|---|---|---|
| Güdümlü roket | sd_prop_rocket_guided.glb | 498 / 149 | 146 KB | 371.1 |
| Güdümsüz roket | sd_prop_rocket_free.glb | 458 / 137 | 126 KB | 394.6 |
| Kaçak yük konteyneri | sd_prop_cache.glb | 342 / 86 | 228 KB | 46.3 |
| Kayıp sonda | sd_prop_probe.glb | 631 / 187 | 179 KB | 96.3 |
| Eski uydu (varyant 0) | sd_prop_sat.glb | 170 / 46 | 185 KB | 31.5 |
| Buz devi | sd_prop_ice.glb | 735 / 219 | 319 KB | 3.6 |
| Kristal monolit (mor) | sd_prop_monolith_violet.glb | 655 / 195 | 260 KB | 3.6 |
| Kristal monolit (yeşil) | sd_prop_monolith_green.glb | 655 / 195 | 271 KB | 3.6 |
| Patron ini (varyant 0) | sd_prop_lair.glb | 1524 / 451 | 223 KB | 1.1 |
| Lav kayası (varyant 0) | sd_prop_lava.glb | 1336 / 400 | 265 KB | 13.3 |
| Enkaz: panel | sd_prop_debris0.glb | 40 / 12 | 62 KB | 117.9 |
| Enkaz: boru | sd_prop_debris1.glb | 60 / 16 | 70 KB | 148.5 |
| Enkaz: tank | sd_prop_debris2.glb | 12 / 2 | 55 KB | 394.1 |
| Enkaz: parça | sd_prop_debris3.glb | 44 / 12 | 71 KB | 152.0 |

## Dürüst durum
- **Oyun içi karşılaştırma YAPILAMADI** bu nesneler için: yükleyicide (`js/glb.js`) yalnız `npc_*`, `ast_*`, `st_*`, `ship_*` anahtarları var; roket, konteyner, sonda, buz devi, monolit, ini, uydu, lav kayası, enkaz için yükleyici kancası YOK (Lead'in eklemesi gerek). Karşılaştırma Blender lookdev ile (pano.png); şimdiki karşılıkları ilkel/sprite olanlar (kutu, oktahedron, düz düzlem) için yeni modellerin üstün olması beklenir, ama oyunda doğrulanmadı.
- Çoğu nesne basit (1–1,5k üçgen altı), ayrıntı düşük: roketler/sonda/konteyner makul; enkaz parçaları çok yalın (40–60 üçgen); patron ini ve uydu tek varyant (kalan 5 ini + 2 uydu varyantı parametreyle ucuz); lav kayasında parlak çatlaklar küçük; texel yoğunluğu büyük nesnelerde düşük (buz devi, monolit, ini: 1–4 px/m, uzaktan görülecekleri için kabul edilebilir ama yakında bulanık).
- Bulunup düzeltilen hata: bükülü dörtgen yüzlü kuleler 'gizli yüz silme' (cull) adımında kendi yüzlerine ışın çarpıp siliniyordu → props'ta üçgenlere bölme + cull eps'i koordinat büyüklüğüne bağlandı (`core/cleanup.py`).
- Kalan: asteroit (C2) oyun içi 3B vs 2B sprite karşılaştırması (test düzeneği kuruldu; yeni 3B kaya oyunda sorunsuz yükleniyor ve doğru ışıklanıyor, aynı-açı kıyas kaya alanı rastgele olduğu için eşleştirilemedi), kalan varyantlar, kalite turları.

## Kalite turu (lav / buz / uydu) — Lead notlarına göre tek hedefli
Lav: çatlaklar büyütüldü ve daha sıcak turuncu emissive, kaya içinde ısı çekirdeği; buz: içten ışıma çekirdeği eklendi (dışarıdan görünmüyor: kristaller opak, gerçek şeffaflık yok → etkisi zayıf); uydu: açık gövde + açık mavi güneş panelleri, gunmetal direkler. Oyun içi doğrulanmadı; varyantlar (lava2/3, sat1/2) bu tura dahil EDİLMEDİ (eski sürümde).

## Kalite turu 2 (ini / enkaz)
Patron ini: seed'e göre 4 gerçek yerleşim (iki kule, tek büyük blok, üç konteyner, iki direk); varyant 4–5 hâlâ eski yerleşim. Enkaz: kırık kaburga/kablo kütükleri eklendi (hâlâ yalın). Oyun içi doğrulanmadı.
