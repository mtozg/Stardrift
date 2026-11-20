# BUDGET MODE

Amaç: kalite standartlarını düşürmeden gereksiz tekrarı, render sayısını ve belge okumayı azaltmak. Hiçbir eşik, kapı veya QC ölçütü gevşetilmedi.
Onay: kullanıcı, 2026-11-20 (sohbet).

## Kurallar
1. **Görev başında** `python factory.py brief` ve BRIEF.md. ARCHITECTURE/STANDARDS/QC/INVENTORY baştan okunmaz; yalnız ilgili bölüm açılır.
2. **Geri bildirim biriktirilir:** `factory.py note <id> "..."`. Küçük görsel istek için ayrı PREVIEW üretilmez; notlar bir sonraki revizyonda birlikte uygulanır (kuyruk o revizyonda boşalır ve kayıt defterine yazılır).
3. **Konsept alternatifleri** metin ve şemayla değerlendirilir. Yalnız onaylanan yön blokaja geçer.
4. **Kademe:** `probe` (ara düzeltmeler) → `--fast` PREVIEW (yalnız Kapı 1 sunumu) → PRODUCTION (yalnız onaydan sonra).
5. **QC otomasyonu:** `verify` yerel Python ile saniyeler içinde bütünlük, SHA256, boyut, üçgen, draw call, GPU, ekran sözleşmesi denetler.
6. **Etkilenen kontroller:** değişiklikten sonra `probe` ve `verify`; tam `qc` yalnız teslimden önce (`deliver` bunu zorlar).
7. **Raporlar** yalnız değişiklik, sorun ve karar bekleyenleri anlatır. Yayın sayfası yalnız Kapı 1, 2 ve 3'te.
8. **Dondurulmuş/entegre varlık** yeniden üretilmez: `model`, `prepare`, `revise` reddeder. İstisna yalnız kullanıcının açık sözüyle (`revise --user-approved "..."`).
9. **PRODUCTION ve entegrasyon** kullanıcı onayı olmadan başlamaz (Kapı 1, 2, 3 değişmedi).
10. **Maliyet özeti:** her görev sonunda `factory.py cost` (ölçülen yerel komut süresi) + Claude tarafı için tahmin. Token/kullanım verisine erişim yoktur; Claude tarafı daima "tahmin" diye etiketlenir.

## Komutlar
| Komut | Ne yapar | Süre (ölçülen) |
|---|---|---|
| `brief` | Tüm varlıkların durumu, bekleyen notlar, sıradaki adım | < 1 s |
| `model <id> --probe` | Geometri + ölçümler (cam oranı, HUD, ekran görünürlüğü, kamera) + tek 800×328 render. Revizyon/durum değişmez; çıktı `work/<id>/rNNN/probe/` | bkz. aşağıdaki ölçüm |
| `model <id> --fast` | Altı görünümlü hızlı PREVIEW (Kapı 1 sunumu) | r001: 366 s |
| `model <id>` | Tam kalite PREVIEW (kokpitte artık nötr altın render yok; yalnız PRODUCTION'da) | r007: 1564 s (altın dahil) |
| `note <id> "..."`, `notes <id>` | Geri bildirim kuyruğu | < 1 s |
| `verify <id> [--delivery] [--validator]` | Hızlı doğrulama, Blender yok | ~2 s |
| `diff <id> <revA> <revB>` | İki revizyon arasında yalnız değişen ölçümler | < 1 s |
| `cost [--since]` | Komut sayısı ve toplam süre (`work/_cost.jsonl`) | < 1 s |
| `qc`, `deliver` | Tam QC ve teslim. `deliver` QC güncel değilse reddeder | qc ≈ 16 s |

## Bilinçli olarak yapılmayanlar
- **`qc --changed` (kısmi tam QC) eklenmedi.** Ölçüm: Şahin r012'de tam QC toplam 15,8 s sürüyor; maliyet Blender modelleme (1061 s) ve hazırlık (265 s) aşamalarında. Kısmi QC bu yüzden kazanç sağlamaz ve eski sonuçları taşıma riski ekler. Ara kontrol `verify` ile yapılır.
- `verify`, tam QC'nin yerini almaz: render karşılaştırması, UV/texel ölçümleri ve yeniden üretilebilirlik yalnız `qc`'dedir.

## Tipik akış (yeni kokpit)
1. `brief` → konsept (metin/şema) → kullanıcı seçer.
2. `model --probe` (birkaç kez, yalnız ölçüm) → notlar `note` ile birikir.
3. `model --fast` → Kapı 1 sunumu → kullanıcı onayı.
4. Onaydan sonra PRODUCTION: `model` → `prepare` → `verify` → `qc` → Kapı 2 → `deliver` → Kapı 3.
5. Oyun içi test: ara adımda tek cihaz (`ingame_cockpit.js <çıktı> "iPhone 13 landscape"`), teslim öncesi 4 cihaz.
