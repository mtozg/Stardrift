# test_box r002 — teknik özellikler

> **Test nesnesi** — Faz 0 hattı doğrulaması içindir, oyuna girmez.

| Özellik | Değer |
|---|---|
| Aile / sınıf | test / test |
| Boy (Z) | 1.781 m |
| Sınır kutusu (oyun uzayı) | [-0.5551000237464905, -0.3499999940395355, -0.8159999847412109] → [0.5541999936103821, 0.6499999761581421, 0.9649999737739563] |
| Üçgen LOD0 / LOD1 / LOD2 | 1177 / 540 / 195 |
| Draw call (LOD0) | 2 |
| Malzeme | MAT_emit, MAT_body |
| GLB | 272.2 KB |
| GPU doku belleği (tahmin) | 21.33 MB |
| QC | WARN (PASS 65 · WARN 2 · FAIL 0 · SKIP 2) |
| Üretim süresi | model 297.8 s · hazırlık 176.7 s · QC 43.5 s |

## Dokular (WebP, GLB'ye gömülü; `textures/` içinde ayrı kopya)
| Doku | Boyut | Dosya |
|---|---|---|
| sd_test_box_emit | 1024×1024 | 3.7 KB |
| sd_test_box_normal | 1024×1024 | 11.2 KB |
| sd_test_box_orm | 1024×1024 | 99.0 KB |
| sd_test_box_base | 1024×1024 | 37.0 KB |

## Soketler
| Ad | Konum (m) | Yön | Amaç |
|---|---|---|---|
| `SOCK_engine_0` | [0, 0, 0.835] | [0, 0, 1] | motor alevi/izi; yön = egzoz |
| `SOCK_light_0` | [0.3, 0.66, 0.55] | [0, 1, 0] | seyir ışığı |
