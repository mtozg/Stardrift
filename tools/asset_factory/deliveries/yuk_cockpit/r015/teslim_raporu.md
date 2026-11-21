# yuk_cockpit r015 — teknik teslim raporu

**Durum:** Görsel: dondurma kaydı yok; Kapı 1: Yük r015 Kapı 1 görsel onay: Mehmet 'Onaylıyorum' (2026-11-20/21); Kapı 2 kaydı için izin Mehmet'ten (2026-11-21) Teknik onaylı teslim paketi. **Oyuna entegre edilmedi** — Kapı 3 ayrı onay bekliyor.

## Ana ölçüler
| Ölçü | Yük Devi r015 | Kaşif (referans) | Bütçe (kokpit) |
|---|---|---|---|
| GLB dosya boyutu | 1098,5 KB (1.124.824 bayt) | 0 KB | ≤ 4 MB |
| Üçgen (three, görünen) | 13.120 | 0 | ≤ 60 bin |
| Draw call (three, sahnede) | 11 | ? primitive | — |
| ↳ statik gövde (ekranlar hariç) | 8 | — | — |
| Doku girişi / görsel | None / None | None / None | giriş ≤ görsel |
| GPU doku belleği (RGBA8 + mip tahmini) | 32,0 MB | ≈ 0 MB | ≤ 40 MB |
| Malzeme | None | None | — |

Draw call: 8 statik çağrı (gövde, emisyon ve varsa eklem mesh'leri) + 3 canlı ekran (`SCR_*`, oyunun canvas'ı için ayrı kalmak zorunda) = 11.
GPU tahmini three r128 davranışına göredir: her doku girişi ayrı yüklenir (Source paylaşımı r138'de geldi). Kaşif'in 24 girişi 4 görseli paylaşıyor; r128'de bu ≈ 0 MB'a çıkar.

## QC
- Karar: **WARN** — PASS 65 · WARN 3 · FAIL 0 · SKIP 2.
- WARN: `gltf.validator_warnings` (tangent yok; Kaşif'te de var) — Kapı 2'de kullanıcı tarafından kabul edildi; runtime tangent entegrasyonda kontrol edilecek.
- Kokpit: cam oranı %52,0 · HUD bölgesi kapanma %6,6 · ekran görünürlüğü SYS 5/5, RADAR 5/5, HULL 5/5 · kamera sapması 0 px.
- Doku yoğunluğu (texel) hedef 240 px/m (Kaşif 239 px/m'den kalibre) üzerinde.

## Blender (Cycles, nötr ışık) ⟷ Three.js r128
| Kamera | Parlaklık farkı | ΔE ort. / p95 | Siluet farkı |
|---|---|---|---|
| N1_pilot | 3,5 % | 3,4 / 10,0 | 0,097 % (1 px toleranslı) · eski XOR 0,64 % |
| N2_goz_sol | 3,6 % | 3,4 / 10,2 | 0,070 % (1 px toleranslı) · eski XOR 0,77 % |
| N3_goz_sag_alt | 2,5 % | 3,3 / 9,7 | 0,201 % (1 px toleranslı) · eski XOR 0,78 % |

## Performans (Playwright swiftshader, n=1 — bilgi amaçlı, kapı değil)
| Profil | Kare süresi |
|---|---|
| masaüstü 1200×750 | 27,4 ms |
| iPad Pro 11 landscape | 25,8 ms |
| iPhone 13 landscape | 27,0 ms |
| Pixel 7 landscape | 27,5 ms |

Gerçek cihaz ölçümü yapılmadı; emülatör değerleri yalnız referanstır, gerçek cihaz testi entegrasyon sonrası yapılmalıdır.

## Kapı 2 kayıtları
- Onaylayan: Mehmet (Lead aktarımı) — 2026-11-21T11:04:54+00:00
- Not: Yük r015 Kapı 2 teknik onay: QC WARN (koyu doku aralığı, tangent uyarısı kabul); Mehmet izni 2026-11-21
- Kabul edilen uyarılar: pbr.base_dielectric, pbr.base_metal, gltf.validator_warnings
- Kapsam: yalnız Asset Factory teslim paketi. Ana oyun koduna entegrasyon, main dalına aktarım ve Kaşif dosyalarında değişiklik **ayrı onay** gerektirir.


## Dokular
| Doku | Boyut | WebP |
|---|---|---|
| sd_yuk_cockpit_normal | 1024×1024 | 25,4 KB |
| sd_yuk_cockpit_orm | 1024×1024 | 209,1 KB |
| sd_yuk_cockpit_base | 2048×2048 | 275,8 KB |

## Kaşif uyumluluğu
? PASS · ? FAIL · ? INFO — ayrıntı `kasif_uyumluluk.md`.

## Paket içeriği
- `sd_yuk_cockpit_r015.glb`, `textures/` (GLB'deki WebP'lerin kopyası)
- `preview/` — Blender: `hero` (pilot), `hero_rear` (çapraz), `closeup` (konsol), `koltuk`, `dis`, `ortho_6` (plan); nötr altın `blender_notr_*`;
  Three r128: `three_r128_*`; yan yana `three_vs_blender_*`
- `qc_report.json/html`, `kasif_uyumluluk.json/md`, `manifest.json`, `source.json`, `spec_sheet.md`, `integration.md`
- Süreler: model 1452.6 s · hazırlık 392.2 s · QC 20.0 s
