# yuk_cockpit r008 — teknik teslim raporu

**Durum:** Görsel: dondurma kaydı yok; Kapı 1: PREVIEW r007 görsel onayı (konsept B + yükseltilmiş ekranlar). PRODUCTION: K15 ile Mehmet başlattı. **TESLİM ADAYI** — Kapı 2 teknik onayı kullanıcıdan bekleniyor; bu paket onay yerine geçmez. **Oyuna entegre edilmedi** — Kapı 3 ayrı onay bekliyor.

## Ana ölçüler
| Ölçü | Yük Devi r008 | Kaşif (referans) | Bütçe (kokpit) |
|---|---|---|---|
| GLB dosya boyutu | 713,9 KB (731.076 bayt) | 3820 KB | ≤ 4 MB |
| Üçgen (three, görünen) | 4.752 | 56.362 | ≤ 60 bin |
| Draw call (three, sahnede) | 11 | 15 primitive | — |
| ↳ statik gövde (ekranlar hariç) | 8 | — | — |
| Doku girişi / görsel | 3 / 3 | 24 / 4 | giriş ≤ görsel |
| GPU doku belleği (RGBA8 + mip tahmini) | 32,0 MB | ≈ 512 MB | ≤ 40 MB |
| Malzeme | 3 | 10 | — |

Draw call: 8 statik çağrı (gövde, emisyon ve varsa eklem mesh'leri) + 3 canlı ekran (`SCR_*`, oyunun canvas'ı için ayrı kalmak zorunda) = 11.
GPU tahmini three r128 davranışına göredir: her doku girişi ayrı yüklenir (Source paylaşımı r138'de geldi). Kaşif'in 24 girişi 4 görseli paylaşıyor; r128'de bu ≈ 512 MB'a çıkar.

## QC
- Karar: **WARN** — PASS 66 · WARN 2 · FAIL 0 · SKIP 2.
- WARN: `gltf.validator_warnings` (tangent yok; Kaşif'te de var) — Kapı 2'de kabul kararı kullanıcınındır.
- Kokpit: cam oranı %46,2 · HUD bölgesi kapanma %10,5 · ekran görünürlüğü SYS 5/5, RADAR 5/5, HULL 5/5 · kamera sapması 0 px.
- Doku yoğunluğu (texel) hedef 240 px/m (Kaşif 239 px/m'den kalibre) üzerinde.

## Blender (Cycles, nötr ışık) ⟷ Three.js r128
| Kamera | Parlaklık farkı | ΔE ort. / p95 | Siluet farkı |
|---|---|---|---|
| N1_pilot | 2,5 % | 3,2 / 15,5 | 0,99 % |
| N2_goz_sol | 2,4 % | 3,2 / 15,6 | 0,72 % |
| N3_goz_sag_alt | 2,1 % | 3,2 / 15,1 | 0,69 % |

## Performans (Playwright swiftshader, n=1 — bilgi amaçlı, kapı değil)
| Profil | Kare süresi |
|---|---|
| masaüstü 1200×750 | 13,6 ms |
| iPad Pro 11 landscape | 13,9 ms |
| iPhone 13 landscape | 13,4 ms |
| Pixel 7 landscape | 13,1 ms |

Gerçek cihaz ölçümü yapılmadı; emülatör değerleri yalnız referanstır, gerçek cihaz testi entegrasyon sonrası yapılmalıdır.


## Dokular
| Doku | Boyut | WebP |
|---|---|---|
| sd_yuk_cockpit_normal | 1024×1024 | 13,1 KB |
| sd_yuk_cockpit_orm | 1024×1024 | 208,7 KB |
| sd_yuk_cockpit_base | 2048×2048 | 258,8 KB |

## Kaşif uyumluluğu
18 PASS · 0 FAIL · 3 INFO — ayrıntı `kasif_uyumluluk.md`.

## Paket içeriği
- `sd_yuk_cockpit_r008.glb`, `textures/` (GLB'deki WebP'lerin kopyası)
- `preview/` — Blender: `hero` (pilot), `hero_rear` (çapraz), `closeup` (konsol), `koltuk`, `dis`, `ortho_6` (plan); nötr altın `blender_notr_*`;
  Three r128: `three_r128_*`; yan yana `three_vs_blender_*`
- `qc_report.json/html`, `kasif_uyumluluk.json/md`, `manifest.json`, `source.json`, `spec_sheet.md`, `integration.md`
- Süreler: model 1249.6 s · hazırlık 340.3 s · QC 13.9 s
