# yuk_cockpit r015 — aday teslim dosyaları (entegrasyon için)

Durum: Mehmet Kapı 1 görsel onayı verildi (Lead aktarımı). **Resmi Kapı 2 / registry kaydı YOK**: bu klasör yalnızca GLB + CK3 verisidir; tam QC raporu ve manifest ayrıca hazırlanır (kayıt komutları için kullanıcı izni gerekiyor).

| Dosya | Boyut | SHA256 |
|---|---|---|
| sd_yuk_cockpit_r015.glb (masaüstü/tablet, 2048 base) | 1125016 B | 590744a1a25e4ae616e16ca1a4ce846745d17c1e085c0011cbed0375cd0a673a |
| sd_yuk_cockpit_r015_m.glb (telefon, 1024 base) | 965624 B | 82517d0fcf7c92f90b13992d3c95b0d583dfb1f5f7e7a34ca32fbbd5231b0a0b |

Oyunda dosya adları: models/cockpit_yuk.glb (tam), models/cockpit_yuk_m.glb (telefon) — içerik aynen kopyalanır.

## Ekran köşeleri (1600×656 çerçeve) — DEĞİŞMEDİ
GLB'den ölçüldü (qc/cockpit_compat.py), önceki sürümle aynı: sıra SCR_SYS, SCR_RADAR, SCR_HULL.

RADAR oranı: 1,73:1. Ekran adları/UV (sol-üst 0,0) aynı.

## HUD sırtı (ridge)
 oyundaki CK3 biçiminde: {top, q, ridge} (x −400..2000). Yöntem: pilot görüşü alfa maskesi (Blender, 1600×656), her 50 px sütunda alttan yukarı ilk saydam piksele kadar; dar dikmeler yatay açmayla (70 px) ve ≤40 px boşluklar doldurularak yok sayıldı. Yöntem r012 Şahin'in oyundaki sırtını yeniden üretir (±3 px).
Yük r015 sırtı r009 sırtından farklı: orta dikme ve plakalar kalktı (merkez 372 px), koltuk eklendi.

## Teknik (verify.py 12/12)
13.120 üçgen, 11 draw call, GPU 32 MB, HUD bölgesi %5,2 (ortada dikme yok); ART_claw_* hiyerarşisi korunur.
