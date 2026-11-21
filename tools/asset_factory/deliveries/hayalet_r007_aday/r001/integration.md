# hayalet_r007_aday r001 — kokpit entegrasyon notu

> **GEÇİCİ · KOD YOK.** Bu belge oyuna hiçbir şey eklemez. Entegrasyon (Kapı 3) ayrı onayla, ana sohbette yapılır.
> Ana oyun kodu ve `main` dalı değiştirilmedi.

## Dosya
- `sd_hayalet_r007_aday_r001.glb` — tek dosya, dokular gömülü (`EXT_texture_webp`). three r128 GLTFLoader okur.
- GLTFLoader şu an yalnızca `claude/bold-bardeen-oqf73o` dalında (Kaşif ?ck=b yolu); `main`de yok.

## Kamera sözleşmesi (Kaşif ile aynı — doğrulandı)
- Göz orijinde, ileri −Z, +Y yukarı, birim metre. Model ölçeklenmez/eğilmez/kaydırılmaz.
- Dikey FOV 74°, odak 435,27 px, asal nokta (800, 239,5) — 1600×656 referans çerçevesinde; three'de `setViewOffset(w, h, 0, −shift_y·h, w, h)`, shift_y = −(0,5 − 239,5/656).
- Göz salınımı (sway) Kaşif'teki gibi uygulanabilir; QC iki ek göz noktasında (sol −7 cm; sağ +7 cm / alt −4 cm) ölçüldü.

## Canlı ekranlar
- `SCR_SYS` → bars, `SCR_RADAR` → map, `SCR_HULL` → hull (dalın renderB/buildB'sindeki ada göre bağlama; traverse).
- Her biri tek dörtgen, 4 köşe; UV sol-üst (0,0), sağ-alt (1,1) → CanvasTexture `flipY=false`.
- Dosyadaki `MAT_screen` yer tutucudur (koyu camgöbeği emisyon); oyun MeshBasicMaterial + canvas ile değiştirir.
- **Dikkat — RADAR oranı:** Hayalet RADAR ?×? px (≈ ?:1), Kaşif ?×? px (≈ ?:1). Kaşif'e göre çizilmiş canvas
  içeriği gerilebilir. **Kapı 2 notu:** Hayalet r007 Kapı 2: QC WARN 6 kabul (karbon-siyah palet dar aralık, metal ikili, tangent, Three-Cycles lum 0,078 sınıra yakın) ; izin 2026-11-21


## Gemiye göre seçim
- Oyunda gemi başına 3B kokpit tablosu (`CK3`, `js/game.js`) var: yeni gemi = bir satır (model, telefon modeli, ekran köşeleri, HUD sırtı) + iki GLB. Telefon varyantı: `pipeline/mobile_variant.py` (yalnız base doku 1024).
  Entegrasyon Lead Developer'a aittir; bu paket oyun koduna dokunmaz.

## Malzeme ve ışık
- `MAT_body` (base 2048 + ORM 1024 + normal 1024), `MAT_emit` (düz emisyon ≤ 1; parlaklık bloom'dan — r128'de emissive_strength yok), `MAT_screen`.
- Oyun Kaşif'te envMapIntensity 0,9 atıyor; Hayalet aynı ayarla QC'deki nötr ışıkta Blender'a ΔE ≈ 3 içinde.
- Tangent dosyada yok; three çalışma anında üretir (validator uyarısı; Kaşif'te de var). **Kapı 2:** uyarı kabul edildi (pbr.base_dielectric, pbr.base_metal, pbr.metal_binary, gltf.validator_warnings, three.fidelity.N1_pilot, three.fidelity.N2_goz_sol); entegrasyon sonrası runtime tangent ve normal map görünümü oyun içinde ayrıca kontrol edilecek.
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

