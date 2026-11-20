# sahin_cockpit r014 — aday teslim dosyaları (entegrasyon için)

Durum: Mehmet Kapı 1 görsel onayı verildi (Lead aktarımı). **Resmi Kapı 2 / registry kaydı YOK**: bu klasör yalnızca GLB + CK3 verisidir; tam QC raporu ve manifest ayrıca hazırlanır (kayıt komutları için kullanıcı izni gerekiyor).

| Dosya | Boyut | SHA256 |
|---|---|---|
| sd_sahin_cockpit_r014.glb (masaüstü/tablet, 2048 base) | 784272 B | d1305121f444a3b902ea7bbd028a64d1a1770dd5b5905a49d8e9125df3b0d109 |
| sd_sahin_cockpit_r014_m.glb (telefon, 1024 base) | 677672 B | 4a3626bb9c2eeef89da353285d6f493c38fb56c825ba8ef495250b383a805e88 |

Oyunda dosya adları: models/cockpit_sahin.glb (tam), models/cockpit_sahin_m.glb (telefon); içerik aynen kopyalanır.

## Ekran köşeleri (1600×656 çerçeve): DEĞİŞMEDİ
GLB'den ölçüldü (qc/cockpit_compat.py), önceki sürümle (Şahin r012 / Yük r009) aynı. Sıra: SCR_SYS, SCR_RADAR, SCR_HULL.
q = [[[390, 432], [620, 420], [626, 560], [400, 582]], [[660, 404], [940, 404], [940, 584], [660, 584]], [[980, 420], [1210, 432], [1200, 582], [974, 560]]]
RADAR oranı 1,56:1. Ekran adları ve UV (sol-üst 0,0) aynı.

## HUD sırtı (ridge)
ck3_sahin.json oyundaki CK3 biçiminde: {top, q, ridge} (x −400..2000). Yöntem: pilot görüşü alfa maskesi (Blender, 1600×656); her 50 px sütunda alttan yukarı ilk saydam piksele kadar; dar dikmeler yatay açmayla (70 px) ve ≤40 px boşluklar doldurularak yok sayıldı. Yöntem r012 Şahin'in oyundaki sırtını yeniden üretir (±3 px).
Şahin r014 sırtı r012 ile aynı (siluet değişmedi); r012 değerleri kullanıldı.

## Teknik (verify.py 12/12)
10.346 üçgen, 5 draw call, GPU 32 MB, HUD bölgesi %1,2.
