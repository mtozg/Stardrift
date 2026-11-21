# hayalet_r007_aday r001 — teknik teslim raporu

**Durum:** Görsel: dondurma kaydı yok; Kapı 1: hayalet_r007_aday: Mehmet görsel onayı (Kapı 1) Lead aktarımıyla; Kapı 2 kaydı izni 2026-11-21 Teknik onaylı teslim paketi. **Oyuna entegre edilmedi** — Kapı 3 ayrı onay bekliyor.

## Ana ölçüler
| Ölçü | Hayalet r001 | Kaşif (referans) | Bütçe (kokpit) |
|---|---|---|---|
| GLB dosya boyutu | 1332,3 KB (1.364.320 bayt) | 0 KB | ≤ 4 MB |
| Üçgen (three, görünen) | 15.210 | 0 | ≤ 60 bin |
| Draw call (three, sahnede) | 5 | ? primitive | — |
| ↳ statik gövde (ekranlar hariç) | 2 | — | — |
| Doku girişi / görsel | None / None | None / None | giriş ≤ görsel |
| GPU doku belleği (RGBA8 + mip tahmini) | 32,0 MB | ≈ 0 MB | ≤ 40 MB |
| Malzeme | None | None | — |

Draw call: 2 statik çağrı (gövde, emisyon ve varsa eklem mesh'leri) + 3 canlı ekran (`SCR_*`, oyunun canvas'ı için ayrı kalmak zorunda) = 5.
GPU tahmini three r128 davranışına göredir: her doku girişi ayrı yüklenir (Source paylaşımı r138'de geldi). Kaşif'in 24 girişi 4 görseli paylaşıyor; r128'de bu ≈ 0 MB'a çıkar.

## QC
- Karar: **WARN** — PASS 56 · WARN 6 · FAIL 0 · SKIP 2.
- WARN: `gltf.validator_warnings` (tangent yok; Kaşif'te de var) — Kapı 2'de kullanıcı tarafından kabul edildi; runtime tangent entegrasyonda kontrol edilecek.
- Kokpit: cam oranı %53,6 · HUD bölgesi kapanma %5,4 · ekran görünürlüğü SYS 5/5, RADAR 5/5, HULL 5/5 · kamera sapması 0 px.
- Doku yoğunluğu (texel) hedef 240 px/m (Kaşif 239 px/m'den kalibre) üzerinde.

## Blender (Cycles, nötr ışık) ⟷ Three.js r128
| Kamera | Parlaklık farkı | ΔE ort. / p95 | Siluet farkı |
|---|---|---|---|
| N1_pilot | 7,8 % | 3,1 / 10,2 | 0,274 % (1 px toleranslı) · eski XOR 0,86 % |
| N2_goz_sol | 7,7 % | 3,1 / 10,2 | 0,345 % (1 px toleranslı) · eski XOR 0,96 % |
| N3_goz_sag_alt | 7,6 % | 3,0 / 10,2 | 0,149 % (1 px toleranslı) · eski XOR 0,72 % |

## Performans (Playwright swiftshader, n=1 — bilgi amaçlı, kapı değil)
| Profil | Kare süresi |
|---|---|
| masaüstü 1200×750 | 25,7 ms |
| iPad Pro 11 landscape | 26,2 ms |
| iPhone 13 landscape | 26,6 ms |
| Pixel 7 landscape | 26,9 ms |

Gerçek cihaz ölçümü yapılmadı; emülatör değerleri yalnız referanstır, gerçek cihaz testi entegrasyon sonrası yapılmalıdır.

## Kapı 2 kayıtları
- Onaylayan: Mehmet (Lead aktarımı) — 2026-11-21T12:30:56+00:00
- Not: Hayalet r007 Kapı 2: QC WARN 6 kabul (karbon-siyah palet dar aralık, metal ikili, tangent, Three-Cycles lum 0,078 sınıra yakın) ; izin 2026-11-21
- Kabul edilen uyarılar: pbr.base_dielectric, pbr.base_metal, pbr.metal_binary, gltf.validator_warnings, three.fidelity.N1_pilot, three.fidelity.N2_goz_sol
- Kapsam: yalnız Asset Factory teslim paketi. Ana oyun koduna entegrasyon, main dalına aktarım ve Kaşif dosyalarında değişiklik **ayrı onay** gerektirir.


## Dokular
| Doku | Boyut | WebP |
|---|---|---|
| sd_hayalet_r007_aday_normal | 1024×1024 | 53,8 KB |
| sd_hayalet_r007_aday_orm | 1024×1024 | 221,5 KB |
| sd_hayalet_r007_aday_base | 2048×2048 | 304,9 KB |

## Kaşif uyumluluğu
? PASS · ? FAIL · ? INFO — ayrıntı `kasif_uyumluluk.md`.

## Paket içeriği
- `sd_hayalet_r007_aday_r001.glb`, `textures/` (GLB'deki WebP'lerin kopyası)
- `preview/` — Blender: `hero` (pilot), `hero_rear` (çapraz), `closeup` (konsol), `koltuk`, `dis`, `ortho_6` (plan); nötr altın `blender_notr_*`;
  Three r128: `three_r128_*`; yan yana `three_vs_blender_*`
- `qc_report.json/html`, `kasif_uyumluluk.json/md`, `manifest.json`, `source.json`, `spec_sheet.md`, `integration.md`
- Süreler: model 743.6 s · hazırlık 314.7 s · QC 18.4 s
