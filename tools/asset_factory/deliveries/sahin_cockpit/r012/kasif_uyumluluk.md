# sahin_cockpit r012 ⟷ Kaşif — sözleşme uyumluluğu

Kaşif GLB'si (`models/cockpit_kasif.glb`, dal `claude/bold-bardeen-oqf73o`) yalnızca okundu; değiştirilmedi.
Karşılaştırma oyunun `?ck=b` yolunun beklentilerine göredir (ekran adları, UV yönü, kamera, ölçek, uzantılar, malzeme).
Tasarım kopyalanmadı: ekran boyutu/konumu farkları INFO olarak kayıtlıdır.

**Özet:** PASS 18 · FAIL 0 · INFO 3

| Kontrol | Durum | Şahin | Kaşif | Not |
|---|---|---|---|---|
| `ekran.SCR_SYS.var` | PASS | True | True | oyun ekranı ada göre bağlar (traverse) |
| `ekran.SCR_SYS.tek_primitive` | PASS | [1, 4] | [1, 4] | tek dörtgen |
| `ekran.SCR_SYS.uv_yonu` | PASS | {'sol_ust': [0.0, 0.0], 'sag_alt': [1.0, 1.0]} | {'sol_ust': [0.0, 0.0], 'sag_alt': [1.0, 1.0]} | CanvasTexture flipY=false: görüntünün sol-üstü UV (0,0) |
| `ekran.SCR_SYS.gozun_onunde` | PASS | True | True | göz orijinde, ileri −Z |
| `ekran.SCR_SYS.cerceve_ici` | PASS | [[390, 432], [620, 420], [626, 560], [400, 582]] | [[393, 411], [588, 392], [582, 501], [342, 525]] | pilot çerçevesinde (1600×656) |
| `ekran.SCR_SYS.boyut_px` | INFO | [236, 162] | [246, 133] | tasarım farkı (r008 kararı: daha büyük, yakın, yüksek) |
| `ekran.SCR_RADAR.var` | PASS | True | True | oyun ekranı ada göre bağlar (traverse) |
| `ekran.SCR_RADAR.tek_primitive` | PASS | [1, 4] | [1, 4] | tek dörtgen |
| `ekran.SCR_RADAR.uv_yonu` | PASS | {'sol_ust': [0.0, 0.0], 'sag_alt': [1.0, 1.0]} | {'sol_ust': [0.0, 0.0], 'sag_alt': [1.0, 1.0]} | CanvasTexture flipY=false: görüntünün sol-üstü UV (0,0) |
| `ekran.SCR_RADAR.gozun_onunde` | PASS | True | True | göz orijinde, ileri −Z |
| `ekran.SCR_RADAR.cerceve_ici` | PASS | [[660, 404], [940, 404], [940, 584], [660, 584]] | [[627, 382], [975, 383], [974, 498], [625, 498]] | pilot çerçevesinde (1600×656) |
| `ekran.SCR_RADAR.boyut_px` | INFO | [280, 180] | [350, 116] | tasarım farkı (r008 kararı: daha büyük, yakın, yüksek) |
| `ekran.SCR_HULL.var` | PASS | True | True | oyun ekranı ada göre bağlar (traverse) |
| `ekran.SCR_HULL.tek_primitive` | PASS | [1, 4] | [1, 4] | tek dörtgen |
| `ekran.SCR_HULL.uv_yonu` | PASS | {'sol_ust': [0.0, 0.0], 'sag_alt': [1.0, 1.0]} | {'sol_ust': [0.0, 0.0], 'sag_alt': [1.0, 1.0]} | CanvasTexture flipY=false: görüntünün sol-üstü UV (0,0) |
| `ekran.SCR_HULL.gozun_onunde` | PASS | True | True | göz orijinde, ileri −Z |
| `ekran.SCR_HULL.cerceve_ici` | PASS | [[980, 420], [1210, 432], [1200, 582], [974, 560]] | [[1009, 392], [1206, 411], [1257, 525], [1018, 501]] | pilot çerçevesinde (1600×656) |
| `ekran.SCR_HULL.boyut_px` | INFO | [236, 162] | [248, 133] | tasarım farkı (r008 kararı: daha büyük, yakın, yüksek) |
| `birim.olcek` | PASS | {'min': [-1.305, -1.32, -1.197], 'max': [1.305, 0.583, 0.635]} | {'min': [-1.388, -1.483, -1.572], 'max': [1.387, 1.007, -0.366]} | metre; aynı ölçek düzeyi (genişlik farkı < 1,5 m) |
| `uzanti.r128` | PASS | ['EXT_texture_webp'] | ['KHR_materials_emissive_strength'] | r128 GLTFLoader tanır; Kaşif'teki emissive_strength r128'de yok sayılıyor |
| `malzeme.standart` | PASS | ['MAT_body', 'MAT_emit', 'MAT_screen'] | ['M_gunmetal_baked', 'M_dark_steel_baked', 'M_composite_baked', 'M_tit | MeshStandardMaterial'a dönüşür; oyun envMapIntensity 0,9 atar |
