# yuk_cockpit r009 ⟷ Kaşif — sözleşme uyumluluğu

Kaşif GLB'si (`models/cockpit_kasif.glb`, dal `claude/bold-bardeen-oqf73o`) yalnızca okundu; değiştirilmedi.
Karşılaştırma oyunun `?ck=b` yolunun beklentilerine göredir (ekran adları, UV yönü, kamera, ölçek, uzantılar, malzeme).
Tasarım kopyalanmadı: ekran boyutu/konumu farkları INFO olarak kayıtlıdır.

**Özet:** PASS 18 · FAIL 0 · INFO 3

| Kontrol | Durum | Yeni model | Kaşif | Not |
|---|---|---|---|---|
| `ekran.SCR_SYS.var` | PASS | True | True | oyun ekranı ada göre bağlar (traverse) |
| `ekran.SCR_SYS.tek_primitive` | PASS | [1, 4] | [1, 4] | tek dörtgen |
| `ekran.SCR_SYS.uv_yonu` | PASS | {'sol_ust': [0.0, 0.0], 'sag_alt': [1.0, 1.0]} | {'sol_ust': [0.0, 0.0], 'sag_alt': [1.0, 1.0]} | CanvasTexture flipY=false: görüntünün sol-üstü UV (0,0) |
| `ekran.SCR_SYS.gozun_onunde` | PASS | True | True | göz orijinde, ileri −Z |
| `ekran.SCR_SYS.cerceve_ici` | PASS | [[316, 404], [586, 388], [594, 540], [332, 566]] | [[393, 411], [565, 393], [558, 504], [342, 525]] | pilot çerçevesinde (1600×656) |
| `ekran.SCR_SYS.boyut_px` | INFO | [278, 178] | [223, 132] | tasarım farkı (r008 kararı: daha büyük, yakın, yüksek) |
| `ekran.SCR_RADAR.var` | PASS | True | True | oyun ekranı ada göre bağlar (traverse) |
| `ekran.SCR_RADAR.tek_primitive` | PASS | [1, 4] | [1, 4] | tek dörtgen |
| `ekran.SCR_RADAR.uv_yonu` | PASS | {'sol_ust': [0.0, 0.0], 'sag_alt': [1.0, 1.0]} | {'sol_ust': [0.0, 0.0], 'sag_alt': [1.0, 1.0]} | CanvasTexture flipY=false: görüntünün sol-üstü UV (0,0) |
| `ekran.SCR_RADAR.gozun_onunde` | PASS | True | True | göz orijinde, ileri −Z |
| `ekran.SCR_RADAR.cerceve_ici` | PASS | [[662, 378], [938, 378], [938, 538], [662, 538]] | [[628, 369], [974, 370], [975, 508], [624, 508]] | pilot çerçevesinde (1600×656) |
| `ekran.SCR_RADAR.boyut_px` | INFO | [276, 160] | [350, 139] | tasarım farkı (r008 kararı: daha büyük, yakın, yüksek) |
| `ekran.SCR_HULL.var` | PASS | True | True | oyun ekranı ada göre bağlar (traverse) |
| `ekran.SCR_HULL.tek_primitive` | PASS | [1, 4] | [1, 4] | tek dörtgen |
| `ekran.SCR_HULL.uv_yonu` | PASS | {'sol_ust': [0.0, 0.0], 'sag_alt': [1.0, 1.0]} | {'sol_ust': [0.0, 0.0], 'sag_alt': [1.0, 1.0]} | CanvasTexture flipY=false: görüntünün sol-üstü UV (0,0) |
| `ekran.SCR_HULL.gozun_onunde` | PASS | True | True | göz orijinde, ileri −Z |
| `ekran.SCR_HULL.cerceve_ici` | PASS | [[1014, 388], [1284, 404], [1268, 566], [1006, 540]] | [[1032, 393], [1206, 411], [1257, 525], [1042, 504]] | pilot çerçevesinde (1600×656) |
| `ekran.SCR_HULL.boyut_px` | INFO | [278, 178] | [225, 132] | tasarım farkı (r008 kararı: daha büyük, yakın, yüksek) |
| `birim.olcek` | PASS | {'min': [-1.175, -1.38, -1.719], 'max': [1.175, 0.62, 0.9]} | {'min': [-1.388, -1.483, -1.572], 'max': [1.387, 1.007, -0.366]} | metre; aynı ölçek düzeyi (genişlik farkı < 1,5 m) |
| `uzanti.r128` | PASS | ['EXT_texture_webp'] | ['KHR_materials_emissive_strength'] | r128 GLTFLoader tanır; Kaşif'teki emissive_strength r128'de yok sayılıyor |
| `malzeme.standart` | PASS | ['MAT_body', 'MAT_emit', 'MAT_screen'] | ['M_gunmetal_baked', 'M_dark_steel_baked', 'M_composite_baked', 'M_tit | MeshStandardMaterial'a dönüşür; oyun envMapIntensity 0,9 atar |
