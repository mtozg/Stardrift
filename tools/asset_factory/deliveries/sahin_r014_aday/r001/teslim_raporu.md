# sahin_r014_aday r001 — teknik teslim raporu

**Durum:** Görsel: dondurma kaydı yok; Kapı 1: sahin_r014_aday: Mehmet görsel onayı (Kapı 1) Lead aktarımıyla; Kapı 2 kaydı izni 2026-11-21 Teknik onaylı teslim paketi. **Oyuna entegre edilmedi** — Kapı 3 ayrı onay bekliyor.

## Ana ölçüler
| Ölçü | Şahin r001 | Kaşif (referans) | Bütçe (kokpit) |
|---|---|---|---|
| GLB dosya boyutu | 766,3 KB (784.688 bayt) | 0 KB | ≤ 4 MB |
| Üçgen (three, görünen) | 10.346 | 0 | ≤ 60 bin |
| Draw call (three, sahnede) | 5 | ? primitive | — |
| ↳ statik gövde (ekranlar hariç) | 2 | — | — |
| Doku girişi / görsel | None / None | None / None | giriş ≤ görsel |
| GPU doku belleği (RGBA8 + mip tahmini) | 32,0 MB | ≈ 0 MB | ≤ 40 MB |
| Malzeme | None | None | — |

Draw call: 2 statik çağrı (gövde, emisyon ve varsa eklem mesh'leri) + 3 canlı ekran (`SCR_*`, oyunun canvas'ı için ayrı kalmak zorunda) = 5.
GPU tahmini three r128 davranışına göredir: her doku girişi ayrı yüklenir (Source paylaşımı r138'de geldi). Kaşif'in 24 girişi 4 görseli paylaşıyor; r128'de bu ≈ 0 MB'a çıkar.

## QC
- Karar: **WARN** — PASS 60 · WARN 2 · FAIL 0 · SKIP 2.
- WARN: `gltf.validator_warnings` (tangent yok; Kaşif'te de var) — Kapı 2'de kullanıcı tarafından kabul edildi; runtime tangent entegrasyonda kontrol edilecek.
- Kokpit: cam oranı %54,5 · HUD bölgesi kapanma %0,6 · ekran görünürlüğü SYS 5/5, RADAR 5/5, HULL 5/5 · kamera sapması 0 px.
- Doku yoğunluğu (texel) hedef 240 px/m (Kaşif 239 px/m'den kalibre) üzerinde.

## Blender (Cycles, nötr ışık) ⟷ Three.js r128
| Kamera | Parlaklık farkı | ΔE ort. / p95 | Siluet farkı |
|---|---|---|---|
| N1_pilot | 0,4 % | 3,1 / 11,1 | 0,003 % (1 px toleranslı) · eski XOR 0,21 % |
| N2_goz_sol | 0,1 % | 3,0 / 10,8 | 0,003 % (1 px toleranslı) · eski XOR 0,23 % |
| N3_goz_sag_alt | 1,2 % | 3,1 / 11,2 | 0,002 % (1 px toleranslı) · eski XOR 0,15 % |

## Performans (Playwright swiftshader, n=1 — bilgi amaçlı, kapı değil)
| Profil | Kare süresi |
|---|---|
| masaüstü 1200×750 | 24,8 ms |
| iPad Pro 11 landscape | 27,0 ms |
| iPhone 13 landscape | 26,2 ms |
| Pixel 7 landscape | 28,0 ms |

Gerçek cihaz ölçümü yapılmadı; emülatör değerleri yalnız referanstır, gerçek cihaz testi entegrasyon sonrası yapılmalıdır.

## Kapı 2 kayıtları
- Onaylayan: Mehmet (Lead aktarımı) — 2026-11-21T12:12:46+00:00
- Not: Şahin r014 Kapı 2 teknik onay: QC WARN (metal aralığı, tangent uyarısı) kabul; izin 2026-11-21
- Kabul edilen uyarılar: pbr.base_metal, gltf.validator_warnings
- Kapsam: yalnız Asset Factory teslim paketi. Ana oyun koduna entegrasyon, main dalına aktarım ve Kaşif dosyalarında değişiklik **ayrı onay** gerektirir.


## Dokular
| Doku | Boyut | WebP |
|---|---|---|
| sd_sahin_r014_aday_normal | 1024×1024 | 29,4 KB |
| sd_sahin_r014_aday_orm | 1024×1024 | 179,7 KB |
| sd_sahin_r014_aday_base | 2048×2048 | 187,5 KB |

## Kaşif uyumluluğu
? PASS · ? FAIL · ? INFO — ayrıntı `kasif_uyumluluk.md`.

## Paket içeriği
- `sd_sahin_r014_aday_r001.glb`, `textures/` (GLB'deki WebP'lerin kopyası)
- `preview/` — Blender: `hero` (pilot), `hero_rear` (çapraz), `closeup` (konsol), `koltuk`, `dis`, `ortho_6` (plan); nötr altın `blender_notr_*`;
  Three r128: `three_r128_*`; yan yana `three_vs_blender_*`
- `qc_report.json/html`, `kasif_uyumluluk.json/md`, `manifest.json`, `source.json`, `spec_sheet.md`, `integration.md`
- Süreler: model 1422.1 s · hazırlık 363.4 s · QC 19.0 s
