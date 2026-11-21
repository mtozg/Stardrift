# Oyun içi varlıkların yenilenmesi (program taslağı)

Durum: **denetim aşaması.** Üretim başlamadı; Mehmet öncelik onayı bekleniyor.
İstek (Mehmet): "Kokpitler bu kadar iyiyken diğer NPC'ler, evrenler, gökyüzü, kapılar gerçekçi durmuyor; eski kalan her şeyi yeniden yapmamız lazım."

## Neden listede yoktu (dürüst not)
Asset Factory'nin ilk kapsamı yalnız 3B kokpitlerdi. Diğer varlıklar ROADMAP'e hiç girmedi; bunu ben (Lead Developer) kapsamayı unutarak yaptım. Bu dosya ve ROADMAP B-12 bu boşluğu kapatır.

## Envanter (kod ve dosya adlarından çıkarım; Asset Factory denetimiyle doğrulanacak)
| Kategori | Dosyalar / tablo | Mevcut yöntem (tahmin) |
|---|---|---|
| NPC gemileri (cargo, tanker, courier, mining, corvette, raider, brute, reaver, leader, boss0-3) | `NPCSPEC3D` (`js/data_gemi.js`), `shipart`/`skin` dokuları | Çizim silüetinden üretilen gövde + doku |
| Oyuncu gemileri (dış görünüm, hangar) | `shipx_*`, `shipart_*`, `STSPEC3D` | 2B çizim + yarı prosedürel model |
| İstasyonlar | `STSPEC3D` (ice, ankora, demirhan, kristal ...), `a3_*_side/top` | Çizimden loft + doku |
| Kapılar | `xdoor_*` | 2B görsel / sprite |
| Gezegen ve aylar | `pmap_*`, `a3_mars`, `a3_mon*` | Doku haritası |
| Gökyüzü, nebula, sis | `env_*`, `a3_fog*` | Doku / sprite |
| Asteroit ve cevher | `ore3_*`, `orei_*`, `orep_*` | Sprite / basit model |
| Efektler | `fx2_*`, `fxart_*` | Sprite |
| Hangar ve arka planlar | `a3_hangar`, `a5`, `a6` ... | 2B arka plan |

## Önerilen yol
1. **Denetim (Asset Factory, üretim yok):** her kategori için güncel oyun içi görüntü, yöntem, dürüst kalite notu (kokpit = 5), mobil sınırlar, önerilen hat, derleme sayısı tahmini.
2. **Öncelik onayı (Mehmet):** en görünür etkiyi veren 3 kategori önce.
3. **Kademeli üretim:** her kategori ayrı aday, konsolide rapor, 2 tur sınırı, Kapı 1 görsel kararı; ben oyuna entegre ederim (ayrı commit/PR).

## Riskler
- Haftalık kota uyarısı var; büyük kapsam gerçekçi sıralanmalı.
- NPC gemi sayısı çok (14+ tip); mobilde üçgen ve draw call bütçesi şart.
- Gökyüzü ve gezegenler tüm sahneyi etkiler; bellek ve yükleme süresi telefonda ölçülmeli (gerçek cihaz testi yok).
