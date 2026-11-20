# yuk_cockpit r009 — kokpit entegrasyon notu

> **GEÇİCİ · KOD YOK.** Bu belge oyuna hiçbir şey eklemez. Entegrasyon (Kapı 3) ayrı onayla, ana sohbette yapılır.
> Ana oyun kodu ve `main` dalı değiştirilmedi.

## Dosya
- `sd_yuk_cockpit_r009.glb` — tek dosya, dokular gömülü (`EXT_texture_webp`). three r128 GLTFLoader okur.
- GLTFLoader şu an yalnızca `claude/bold-bardeen-oqf73o` dalında (Kaşif ?ck=b yolu); `main`de yok.

## Kamera sözleşmesi (Kaşif ile aynı — doğrulandı)
- Göz orijinde, ileri −Z, +Y yukarı, birim metre. Model ölçeklenmez/eğilmez/kaydırılmaz.
- Dikey FOV 74°, odak 435,27 px, asal nokta (800, 239,5) — 1600×656 referans çerçevesinde; three'de `setViewOffset(w, h, 0, −shift_y·h, w, h)`, shift_y = −(0,5 − 239,5/656).
- Göz salınımı (sway) Kaşif'teki gibi uygulanabilir; QC iki ek göz noktasında (sol −7 cm; sağ +7 cm / alt −4 cm) ölçüldü.

## Canlı ekranlar
- `SCR_SYS` → bars, `SCR_RADAR` → map, `SCR_HULL` → hull (dalın renderB/buildB'sindeki ada göre bağlama; traverse).
- Her biri tek dörtgen, 4 köşe; UV sol-üst (0,0), sağ-alt (1,1) → CanvasTexture `flipY=false`.
- Dosyadaki `MAT_screen` yer tutucudur (koyu camgöbeği emisyon); oyun MeshBasicMaterial + canvas ile değiştirir.
- **Dikkat — RADAR oranı:** Yük Devi RADAR 276×160 px (≈ 1,73:1), Kaşif 350×139 px (≈ 2,52:1). Kaşif'e göre çizilmiş canvas
  içeriği gerilebilir. **Kapı 2 notu:** Yük Devi r009 teknik onayı; orta dikme 30 mm kalır. Tangent ve HUD (%10,1) uyarıları kabul. Kapsam: yalnız Asset Factory teslim paketi; entegrasyon Lead Developer'da.

## Eklemli parçalar (statik, animasyona hazır)
Her eklem ayrı düğüm; pivot eklem merkezinde, eklem mesh'i (`ART_*_geo`) eklem uzayında ve birim dönüşümlü. Oyun bu parçalara ad ve hiyerarşiyle erişir; bu sürümde animasyon yoktur (STANDARDS §0.3).
| Eklem düğümü | Ebeveyn | Dönüş ekseni (extras.joint_axis) |
|---|---|---|
| `ART_claw_jaw_L` | `ART_claw_wrist` | çene düzlemi normali: sol çene açma |
| `ART_claw_jaw_R` | `ART_claw_wrist` | çene düzlemi normali: sağ çene açma |
| `ART_claw_wrist` | `ART_claw_elbow` | kol ekseni (ileri-aşağı): bilek dönüşü |
| `ART_claw_elbow` | `ART_claw_shoulder` | X: dirsek |
| `ART_claw_shoulder` | `ART_claw_root` | X (yan eksen): kaldırma |
| `ART_claw_root` | `LOD0` | sabit: gövde bağlantısı |
Soketler eklemle birlikte hareket eder (ör. `SOCK_claw_grip` → `ART_claw_wrist`). Eksenler Blender yerel uzayında yazılmıştır; glTF'de Y-up dönüşümü uygulanır, dönüş testi animasyon görevinde yapılmalıdır.


## Gemiye göre seçim
- Oyunda gemi başına 3B kokpit tablosu (`CK3`, `js/game.js`) var: yeni gemi = bir satır (model, telefon modeli, ekran köşeleri, HUD sırtı) + iki GLB. Telefon varyantı: `pipeline/mobile_variant.py` (yalnız base doku 1024).
  Entegrasyon Lead Developer'a aittir; bu paket oyun koduna dokunmaz.

## Malzeme ve ışık
- `MAT_body` (base 2048 + ORM 1024 + normal 1024), `MAT_emit` (düz emisyon ≤ 1; parlaklık bloom'dan — r128'de emissive_strength yok), `MAT_screen`.
- Oyun Kaşif'te envMapIntensity 0,9 atıyor; Yük Devi aynı ayarla QC'deki nötr ışıkta Blender'a ΔE ≈ 3 içinde.
- Tangent dosyada yok; three çalışma anında üretir (validator uyarısı; Kaşif'te de var). **Kapı 2:** uyarı kabul edildi (gltf.validator_warnings, cockpit.hud_zone_block); entegrasyon sonrası runtime tangent ve normal map görünümü oyun içinde ayrıca kontrol edilecek.
- Model gözün arkasına uzanır (koltuk, z en çok +0,64 m): kamera önünde görünmez, zararsız.

## Fallback ve çevrimdışı
- GLB yüklenemezse mevcut kokpit davranışı korunmalı (eski 2D/parallax **yeni üretimde kullanılmaz**; yalnız mevcut oyunun kendi fallback'i).
- Dosya yerel paketle gelir; ağ gerektirmez.

## Test
- `qc/viewer/check.html` (otomatik, Three r128) ve `qc/viewer/bench.html?glb=…` (gerçek cihaz ölçümü — henüz yapılmadı).
- Emülatör kare süreleri yalnız referanstır; gerçek cihaz performans testi entegrasyon sonrası yapılmalıdır.

## Entegrasyon sonrası kontrol listesi
- [ ] Runtime tangent + normal map görünümü (pilot ve iki göz noktası)
- [ ] RADAR canvas 1,56:1, gerilme yok; SYS/HULL içerik hizası
- [ ] Gerçek cihaz kare süresi (iPhone/Android, yatay)
- [ ] Bloom altında `MAT_emit` ve ekran parlaklığı

