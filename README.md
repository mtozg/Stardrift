# Stardrift

**Kayıp Yıldızlar** — kokpit görünümlü, tarayıcıda oynanan bir uzay oyunu. Tek bir HTML dosyası, kurulum yok.

Gemini istasyondan kaldır, asteroit kır, kargonu sat, gemini geliştir ve dört farklı evrende yolunu çiz. Zorunlu görev yok; ne yapacağına sen karar verirsin.

## Neler var

**Evrenler**
- Dört evren: Ankora, Kızıl, Buzul ve Zümrüt. Her birinin kendi atmosferi, istasyonları ve müziği var.
- Evrenler arası hiperatlama.
- Ana istasyonlar tünel ve hangar görünümüyle yanaşma ve kalkış animasyonuna sahip.

**Oynanış**
- Madencilik, kargo taşıma ve ticaret.
- Gemi geliştirme: silahlar, kalkan, motor ve kargo kapasitesi.
- Dört lazer türü (darbe, çift, plazma, madenci) ve dört roket başlığı (standart, ağır, küme, delici).
- Korsanlar ve 3 boyutlu korsan lideri ile uzay savaşı.
- Pilot adı ve otomatik kayıt.

**Ses ve müzik**
- Lazer, roket, patlama, motor, kalkan, yanaşma ve hiperatlama için ayrı ses efektleri.
- Her evrene, hangara ve savaşa göre değişen müzik.
- Ayarlardan seçilebilen dört ana müzik: *Before the Horizon Fades*, *Against the Nebula*, *Oxygen*, *The Longest Orbit*.
- Müzik sesi ve oyun sesi ayrı ayrı ayarlanır.

## Oynamak için

1. Bu depoyu indir ya da klonla.
2. `index.html` dosyasını tarayıcıda aç.

`muzik_*.mp3` dosyaları `index.html` ile aynı klasörde durmalı. Tarayıcı dosyaları doğrudan açmaya izin vermezse klasörde basit bir sunucu başlat:

```bash
python3 -m http.server 8000
```

Sonra `http://localhost:8000` adresine git.

iPad'de yatay tutarak oynamak en rahatı. Tarayıcılar sesi ilk dokunuşa kadar başlatmaz, başlangıç ekranındaki **BAŞLA** düğmesine bastığında müzik açılır.

## Kayıt

İlerleme tarayıcıda (`localStorage`) saklanır. Tarayıcı verisi silinirse kayıt da gider.

## Teknik

- Tek dosyalık HTML, CSS ve JavaScript.
- 3B için [three.js](https://threejs.org) (r128).
- Ses efektleri sayfanın içine gömülü, müzikler ayrı mp3 dosyalarıdır.

## Dosyalar

| Dosya | Ne işe yarar |
|---|---|
| `index.html` | Oyunun kendisi |
| `muzik_ana*.mp3` | Ana müzikler (4 tema) |
| `muzik_ankora/kizil/buzul/zumrut.mp3` | Evren müzikleri |
| `muzik_hangar.mp3`, `muzik_savas.mp3` | Hangar ve savaş müzikleri |

## Üretim

Oyun, Claude ile birlikte adım adım geliştirildi. Ses efektleri ve müzikler yapay zekâ araçlarıyla üretildi.
