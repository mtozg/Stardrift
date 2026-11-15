# Kalite Kontrol Sistemi (v0.2, onay bekliyor)

## 1. Yapı

Kalite kontrol üç onay kapısı ve dört test katmanından oluşur. Her test şu sonuçlardan birini döndürür: **PASS**, **WARN** (gerekçeyle kabul edilebilir) ya da **FAIL** (engeller).
Kurallar, eşikler ve aileye özgü istisnalar `qc/rules.json` ile `qc/budgets.json` dosyalarında, kodun dışında tutulur.

| Katman | Ne zaman | Araç | Amaç |
|---|---|---|---|
| L1 Görsel inceleme | Kapı 1'den önce | Cycles render + Claude'un incelemesi + senin onayın | Doğru şey mi üretildi? (biçim, görsel dil, referansa sadakat) |
| L2 Statik teknik | Hazırlıktan sonra | Blender + Python + Khronos glTF Validator | Dosya doğru ve temiz mi? |
| L3 Motor sadakati | L2'den sonra | Three r128 (oyunun `vendor/three.min.js`'i) + Playwright | Oyunda da Kapı 1'deki gibi mi görünüyor? |
| L4 Performans | L3'ten sonra | Playwright cihaz emülasyonu + gerçek cihazda `bench.html` | Mobil bütçeye sığıyor mu? |

Kapı 2'ye (teknik onay) yalnızca L2, L3 ve L4'te FAIL'i olmayan varlık çıkar.

## 2. L1 — Görsel inceleme (Kapı 1)

Üretilen görüntüler:
- Hero render (3/4 açı, oyunun ışığına yakın lookdev).
- 6 dik görünüş.
- 8 karelik turntable.
- Referans karşılaştırması: oyun görselinin yanına aynı açıdan render. Kokpitte pilot kamerası, dış modelde çizim açısı kullanılır.
- Yakın plan detay.
- Ölçek görüntüsü: Kaşif ve insan silueti yanında.

Claude'un yapacağı ön kontrol (sana göstermeden önce):
- [ ] Biçim referansla aynı karakterde mi? Silüet, oranlar, ana kütleler.
- [ ] Görsel dil (STANDARDS §1): yıpranma, malzeme, taraf ve evren renkleri, emisyon miktarı.
- [ ] Ayrıntı ölçeği tutarlı mı? Perçin, panel ve greeble boyutları gerçek ölçüyle uyumlu mu?
- [ ] Hatalı görünüm var mı: kesişen parçalar, yüzen parçalar, delik, ters normal, gölgede kaybolan bölge.
- [ ] Oyun kamerasının tipik uzaklığında okunuyor mu? Küçük görüntü testi: 128 px'e indirilmiş render.

Onay `factory.py approve <id> --gate visual` ile kaydedilir. Onaylanan hero ve dik görünüş render'ları L3 için **altın referans** olur.

## 3. L2 — Statik teknik testler

| Grup | Test | FAIL koşulu |
|---|---|---|
| Biçim | Khronos glTF Validator | herhangi bir hata |
| Sözleşme | kök, LOD, mesh, malzeme ve soket adları (STANDARDS §3) | eksik ya da yanlış ad; ailede zorunlu soket eksik (istasyonda `SOCK_dock`, gemide `SOCK_engine`) |
| Sözleşme | `extras` alanları, birim, boy (`length_m` ±%2), yön (burun −Z), pivot | sapma |
| Uzantılar | izin verilenler dışında glTF uzantısı (STANDARDS §6) | yasak uzantı, özellikle `KHR_materials_emissive_strength` |
| Geometri | sıfır alanlı yüz, gevşek ya da çakışık köşe, uygulanmamış dönüşüm, negatif ölçek | > 0 |
| Geometri | normal yönü (dışa bakış ışın testi) | gövdede ters normal oranı > %0,5 |
| Geometri | açık kenar (manifold) | gövdede > 0 (aile istisnası hariç) |
| Geometri | gizli yüz oranı (26 yönlü görünürlük) | > %5 |
| UV | 0..1 dışı (unique), çakışma, ada payı, texel yoğunluğu | çakışma > %1, texel yoğunluğu hedefin ±%30'u dışında (WARN ±%15) |
| Malzeme | sayı, PBR aralıkları, metaliklik ikiliği, emisyon ≤ 1, emisyon alan oranı | bütçe dışı ya da aralık dışı |
| Doku | 2'nin kuvveti, biçim, renk uzayı, normal haritası birim uzunluk, boş kanal | hata |
| Bütçe | üçgen (LOD bazında), draw call, GLB boyutu, doku belleği (GPU tahmini) | `budgets.json` aşımı (WARN %90) |
| LOD | oranlar, silüet kaybı | LOD1 silüet farkı > %3 piksel |
| Tekrar üretilebilirlik | aynı spec ve seed ile yeniden üret, geometri hash'i | farklı |
| Referans | silüet IoU (çizimin alfa maskesine karşı, üst ve yan) | < `silhouette_iou_min` (varsayılan 0,80; WARN 0,85) |
| Kokpite özel | cam açıklığı ışın testi, ekran köşe hizası (Kaşif `verify.py`) | engelli ışın > 0; köşe sapması > 0,05 px |

## 4. L3 — Motor sadakati (Three r128)

Test sayfası `qc/viewer/check.html`. Kaşif'in `glb_check.html` sayfasından genelleştirildi ve oyunun kendi `vendor/three.min.js` dosyasını okur. GLTFLoader, oyunda yoksa fabrikanın sabitlenmiş r128 kopyasından gelir.

1. **Yükleme**: hata ve uyarı yok, düğüm ağacı sözleşmeye uygun, malzemeler doğru tipte (`MeshStandardMaterial` / `MeshBasicMaterial`).
2. **Görüntü sadakati**: aynı kamera açılarıyla Three render'ı alınır ve altın referansla karşılaştırılır:
   - ortalama parlaklık farkı ≤ %8
   - renk farkı (ΔE ortalaması) ≤ 6
   - silüet farkı ≤ %1
   Bu test, bake sırasında ya da glTF dönüşümünde kaybolan malzemeleri yakalar (örnek: emisyonun sönmesi, metalikliğin yanlış çıkması).
3. **Normal yönü**: FrontSide ile DoubleSide render'ları arasındaki piksel farkı ≤ %0,5 (Kaşif testindeki yöntem).
4. **Işık senaryoları**: oyunun ışık düzeni (GEÇİCİ: game_contract'tan alınacak) ile gündüz, gece ve patlama flaşı. Aşırı parlama ya da tamamen siyah bölge olmamalı.
5. **Uzaklık testi**: oyunun tipik uzaklıklarında küçük boyutlu render. LOD geçişlerinde atlama görülmemeli.

## 5. L4 — Performans

Emülasyon (otomatik, Playwright, swiftshader):
- Tek model: `renderer.info` üzerinden çağrı ve üçgen sayısı, doku ve geometri belleği, ayrıştırma (parse) ve yükleme süresi.
- Kalabalık sahne: N = 1, 12, 40 örnek (NPC ve asteroit için instancing'li ve instancing'siz), ms/kare.
- Cihaz profilleri: iPad Pro 11, iPhone 13, Pixel 7 (yatay).
- Swiftshader mutlak hız vermez. Bu testler **göreli** karşılaştırma içindir: önceki revizyonla ve sınıfın referans varlığıyla kıyaslanır. %15'ten fazla gerileme WARN, %30'dan fazlası FAIL olur.

Gerçek cihaz (elle, her ailenin ilk varlığında ve büyük değişikliklerde):
- `qc/viewer/bench.html` telefonda açılır. Varlığı oyun benzeri sahnede N örnekle 10 saniye çizer.
- fps, ms/kare dağılımı (p50, p95) ve yükleme süresini kopyalanabilir JSON olarak verir. Sonuç `qc_report`'a işlenir.
- Bütçe tablosu (STANDARDS §7) bu ölçümlerle ayarlanır.

## 6. Rapor

`qc_report.json` makine içindir: her test için id, katman, sonuç, değer, eşik ve gerekçe; varlık hash'i, revizyon, fabrika commit'i.
`qc_report.html` insan içindir: özet rozetleri, önizlemeler, bütçe doluluk çubukları, referans ve Three karşılaştırma görselleri, FAIL/WARN listesi, önceki revizyonla fark.

WARN kabulü: `factory.py approve --gate tech --accept-warn <test_id> --reason "..."` ile yalnızca senin onayınla yapılır ve kayda geçer.

## 7. Regresyon ve altın set

- Her ailenin ilk onaylı varlığı **altın referans** olur. Kokpit ailesinin altın referansı Kaşif kokpitidir.
- `core/` ya da `library/` değişince etkilenen tüm onaylı varlıklar yeniden üretilip L2–L4'ten geçirilir. Görsel fark eşiği aşılırsa değişiklik engellenir ya da varlık revizyonu artırılır.
- `registry.json` her varlığın hangi `core` ve `library` sürümüyle onaylandığını tutar.
