# sahin_cockpit r012 — teknik teslim raporu

**Durum:** Görsel: r012 görsel olarak onaylandı ve donduruldu (kullanıcı, sohbet 2026-11-16). Daha fazla aşınma/koyulaştırma yok; açık gri, temiz ama kullanılmış avcı karakteri korunur; Kaşif'in yıpranmış koyu metali kopyalanmaz. Teknik onaylı teslim paketi. **Oyuna entegre edilmedi** — Kapı 3 ayrı onay bekliyor.

## Ana ölçüler
| Ölçü | Şahin r012 | Kaşif (referans) | Bütçe (kokpit) |
|---|---|---|---|
| GLB dosya boyutu | 717,4 KB (734.596 bayt) | 3875 KB | ≤ 4 MB |
| Üçgen (three, görünen) | 9.384 | 56.556 | ≤ 60 bin |
| Draw call (three, sahnede) | 5 | 15 primitive | — |
| ↳ statik gövde (ekranlar hariç) | 2 | — | — |
| Doku girişi / görsel | 3 / 3 | 24 / 4 | giriş ≤ görsel |
| GPU doku belleği (RGBA8 + mip tahmini) | 32,0 MB | ≈ 512 MB | ≤ 40 MB |
| Malzeme | 3 | 10 | — |

Draw call: 2 statik gövde çağrısı (`MAT_body`, `MAT_emit`) + 3 canlı ekran (`SCR_*`, oyunun canvas'ı için ayrı kalmak zorunda) = 5.
GPU tahmini three r128 davranışına göredir: her doku girişi ayrı yüklenir (Source paylaşımı r138'de geldi). Kaşif'in 24 girişi 4 görseli paylaşıyor; r128'de bu ≈ 512 MB'a çıkar.

## QC
- Karar: **WARN** — PASS 61 · WARN 1 · FAIL 0 · SKIP 2.
- WARN: `gltf.validator_warnings` (tangent yok; Kaşif'te de var) — Kapı 2'de kullanıcı tarafından kabul edildi; runtime tangent entegrasyonda kontrol edilecek.
- Kokpit: cam oranı %54,5 · HUD bölgesi kapanma %0,6 · ekran görünürlüğü SYS 5/5, RADAR 5/5, HULL 5/5 · kamera sapması 0 px.
- Doku yoğunluğu (texel) hedef 240 px/m (Kaşif 239 px/m'den kalibre) üzerinde.

## Blender (Cycles, nötr ışık) ⟷ Three.js r128
| Kamera | Parlaklık farkı | ΔE ort. / p95 | Siluet farkı |
|---|---|---|---|
| N1_pilot | 1,8 % | 3,1 / 11,7 | 0,21 % |
| N2_goz_sol | 1,5 % | 3,0 / 11,4 | 0,23 % |
| N3_goz_sag_alt | 2,4 % | 2,9 / 11,5 | 0,15 % |

## Performans (Playwright swiftshader, n=1 — bilgi amaçlı, kapı değil)
| Profil | Kare süresi |
|---|---|
| masaüstü 1200×750 | 20,7 ms |
| iPad Pro 11 landscape | 20,8 ms |
| iPhone 13 landscape | 20,1 ms |
| Pixel 7 landscape | 18,7 ms |

Gerçek cihaz ölçümü yapılmadı. Kapı 2 kararı: emülatör değerleri yalnız referans; gerçek cihaz testi sonra.

## Kapı 2 kayıtları
- Onaylayan: kullanıcı (sohbet, 2026-11-16: 'Şahin r012 için Kapı 2 teknik onayını veriyorum') — 2026-11-16T10:17:52+00:00
- Not: Yalnız Asset Factory teslim paketi için teknik onay; entegrasyon/main/Kaşif değişikliği değil. Tangent uyarısı kabul (runtime tangent + normal map entegrasyonda kontrol). RADAR 1,56:1 korunur. Emülatör 19-21 ms yalnız referans; gerçek cihaz testi sonra.
- Kabul edilen uyarılar: gltf.validator_warnings
- Kapsam: yalnız Asset Factory teslim paketi. Ana oyun koduna entegrasyon, main dalına aktarım ve Kaşif dosyalarında değişiklik **ayrı onay** gerektirir.


## Dokular
| Doku | Boyut | WebP |
|---|---|---|
| sd_sahin_cockpit_normal | 1024×1024 | 23,7 KB |
| sd_sahin_cockpit_orm | 1024×1024 | 173,5 KB |
| sd_sahin_cockpit_base | 2048×2048 | 182,4 KB |

## Kaşif uyumluluğu
18 PASS · 0 FAIL · 3 INFO — ayrıntı `kasif_uyumluluk.md`.

## Paket içeriği
- `sd_sahin_cockpit_r012.glb`, `textures/` (GLB'deki WebP'lerin kopyası)
- `preview/` — Blender: `hero` (pilot), `hero_rear` (çapraz), `closeup` (konsol), `koltuk`, `dis`, `ortho_6` (plan); nötr altın `blender_notr_*`;
  Three r128: `three_r128_*`; yan yana `three_vs_blender_*`
- `qc_report.json/html`, `kasif_uyumluluk.json/md`, `manifest.json`, `source.json`, `spec_sheet.md`, `integration.md`
- Süreler: model 1061.0 s · hazırlık 265.3 s · QC 15.8 s
