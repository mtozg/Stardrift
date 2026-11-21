# Yük — bütünleşik gövde RAFİNE (fused_r007) — Lead talimatı: panel 2×, sıcak pas, LOD0 6–8k, UV ≥%70, _m, kıskaç kalın, konteynerler gömülü, kokpit cam uyumu
## Yapılanlar
- Panel/kabartma yoğunluğu ≈2× (panel 0,9→0,5 m, kabartma payı %95, 72k üçgenlik hi-poly), perçin sıklığı artırıldı.
- Renk: oyun içi şimdiki Yük'e yaklaşım — turuncu-kahve pas tonu (boya tabanı kahve-turuncuya çekildi, aşınma/çip rengi sıcak pas, is-yağ akıntısı artırıldı), uyarı kuşakları sarı-turuncu; kamuflaj beneklenmesi azaltıldı (ton aralığı daraltıldı, bulut ölçeği büyütüldü).
- UV doluluğu %72,7 (hedef ≥%70 ✓), texel ≈90 px/m (≥64 ✓): paketleme boşluğu 0 px (komşu ada taşması olmaz; ancak mip'lerde çok ince kenar karışması olabilir, kabul edilebilir).
- Mobil varyant: `sd_ship_yuk_m.glb` (dokular 1024'e indi, geometri aynı).
- Konteynerler rafın içine gömüldü ve gövdeyle tek yüzey olacak şekilde birleştirildi (Boolean union; üstleri raf çizgisinin 16 cm altında). Kıskaç ×1,5 kalınlaştı (kol, piston, çene, bilek).
- **Kokpit cam konumu uyumu (Mehmet'in yeni kuralı):** Yük kokpiti r015 pilot görüşünde ön cam 4:1 genişliğinde, 4 dikmeli (iki dış + iki iç, orta bölme geniş) ve üstte uyarı şeritli başlık, yanlarda açılı duvar camı var. Dış modelde: burun ön cephesinde 0,20 L × 0,056 L (≈3,6:1) tek geniş cam, 4 dikme (x = ±0,100 ve ±0,049: iç/dış oranı 0,49 ≈ kokpitteki 0,51), üstte koyu başlık çubuğu; yan camlar 3 küçük yerine 2 geniş pano (kokpitteki yan duvar camı gibi); üst ön cam korundu. DEĞERLENDİRME: konum ve bölme düzeni UYUMLU; oran biraz sıkı (ön cam 4:1 yerine 3,6:1, burun genişliği sınırı); cam yüksekliği kokpitteki yüksekliğe göre ≈%15 kısa. Kokpit–dış model ölçeği tanımsız olduğundan birebir ölçü karşılaştırması yapılmadı, orantı karşılaştırması yapıldı.
## Hedeflerden kaçan
- **LOD0 3659 üçgen (hedef 6–8k ✗):** pah (angle 20°, 2 segment) yalnız birkaç kenara uygulandı, hat üçgeni artırmadı; gerçek 6–8k için gövdeye ek geometri (daha çok kademe/panel plakası) gerekir.
- Bu dosya 2048/1024/2048 doku: GPU ≈34 MB (mobil _m ≈ 8 MB).
## Oyun içi karşılaştırma (karsilastirma/hangar_yuk_fused_r007.webp; sol şimdiki, sağ yeni; açılar birebir aynı değil)
Yeni: turuncu-altın gövde, tek kütle, gömülü nozul + alev, sarı kuşaklar, kalın kıskaç. Şimdiki: daha çok küçük ayrıntı, kirli, koyu kontrast ve 8 motor kümesi parlak. Yeni gemide koyu dikdörtgen zırh blokları (armor2/omuz) hâlâ 'bloklu' görünüyor; gövde hâlâ büyük düz yüzeyler. KARAR: ADAY (bütünlük ✓, renk yaklaştı, ayrıntı hâlâ geri) — 'şimdikinden iyi' DEĞİL.
