# sahin_cockpit r012 — kokpit entegrasyon notu

> **GEÇİCİ · KOD YOK.** Bu belge oyuna hiçbir şey eklemez. Entegrasyon (Kapı 3) ayrı onayla, ana sohbette yapılır.
> Ana oyun kodu ve `main` dalı değiştirilmedi.

## Dosya
- `sd_sahin_cockpit_r012.glb` — tek dosya, dokular gömülü (`EXT_texture_webp`). three r128 GLTFLoader okur.
- GLTFLoader şu an yalnızca `claude/bold-bardeen-oqf73o` dalında (Kaşif ?ck=b yolu); `main`de yok.

## Kamera sözleşmesi (Kaşif ile aynı — doğrulandı)
- Göz orijinde, ileri −Z, +Y yukarı, birim metre. Model ölçeklenmez/eğilmez/kaydırılmaz.
- Dikey FOV 74°, odak 435,27 px, asal nokta (800, 239,5) — 1600×656 referans çerçevesinde; three'de `setViewOffset(w, h, 0, −shift_y·h, w, h)`, shift_y = −(0,5 − 239,5/656).
- Göz salınımı (sway) Kaşif'teki gibi uygulanabilir; QC iki ek göz noktasında (sol −7 cm; sağ +7 cm / alt −4 cm) ölçüldü.

## Canlı ekranlar
- `SCR_SYS` → bars, `SCR_RADAR` → map, `SCR_HULL` → hull (dalın renderB/buildB'sindeki ada göre bağlama; traverse).
- Her biri tek dörtgen, 4 köşe; UV sol-üst (0,0), sağ-alt (1,1) → CanvasTexture `flipY=false`.
- Dosyadaki `MAT_screen` yer tutucudur (koyu camgöbeği emisyon); oyun MeshBasicMaterial + canvas ile değiştirir.
- **Dikkat — RADAR oranı:** Şahin RADAR 280×180 px (≈ 1,56:1), Kaşif 350×116 px (≈ 3,02:1). Kaşif'e göre çizilmiş canvas
  içeriği gerilebilir; entegrasyonda canvas boyutu ekran oranına göre seçilmeli (r008 tasarım kararı: daha büyük, yakın, yüksek ekranlar).

## Gemiye göre seçim
- Daldaki kod Kaşif'e bağlı (`save.ship === 'kasif'`, `models/cockpit_kasif.glb`). Şahin için gemi → GLB eşlemesi gerekir (ör. `models/cockpit_sahin.glb`).
  Bu genelleştirme Kapı 3'te, onayla yapılır.

## Malzeme ve ışık
- `MAT_body` (base 2048 + ORM 1024 + normal 1024), `MAT_emit` (düz emisyon ≤ 1; parlaklık bloom'dan — r128'de emissive_strength yok), `MAT_screen`.
- Oyun Kaşif'te envMapIntensity 0,9 atıyor; Şahin aynı ayarla QC'deki nötr ışıkta Blender'a ΔE ≈ 3 içinde.
- Tangent dosyada yok; three çalışma anında üretir (validator uyarısı; Kaşif'te de var).
- Model gözün arkasına uzanır (koltuk, z en çok +0,64 m): kamera önünde görünmez, zararsız.

## Fallback ve çevrimdışı
- GLB yüklenemezse mevcut kokpit davranışı korunmalı (eski 2D/parallax **yeni üretimde kullanılmaz**; yalnız mevcut oyunun kendi fallback'i).
- Dosya yerel paketle gelir; ağ gerektirmez.

## Test
- `qc/viewer/check.html` (otomatik, Three r128) ve `qc/viewer/bench.html?glb=…` (gerçek cihaz ölçümü — henüz yapılmadı).
