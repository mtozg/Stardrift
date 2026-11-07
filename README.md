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
- Anlık sinyaller: yardım çağrısı, eskort, düşmüş kargo, arıza, korsan pususu, gezgin tüccar, bilinmeyen enerji, aranan korsan, kayıp sonda, kaçan korsan. Hepsi isteğe bağlı; kabul et ya da yoksay.
- Kilit (T): nişandaki gemiye ya da gök cismine, nişan boşsa 2 km içindeki en yakın düşmana kilitlenir. Asteroitler elle kazılır.
- İlk açılışta kısa bir rehber çıkar; "Rehberi geç" ile her an kapatılır.

**Ses ve müzik**
- Lazer, roket, patlama, motor, kalkan, yanaşma ve hiperatlama için ayrı ses efektleri.
- Her evrene, hangara ve savaşa göre değişen müzik.
- Ayarlardan seçilebilen dört ana müzik: *Before the Horizon Fades*, *Against the Nebula*, *Oxygen*, *The Longest Orbit*.
- Müzik sesi ve oyun sesi ayrı ayrı ayarlanır.

## Oynamak için

En kolayı GitHub Pages üzerinden açmak. Bilgisayarda oynamak için depoyu indir, klasörde basit bir sunucu başlat:

```bash
python3 -m http.server 8000
```

Sonra `http://localhost:8000` adresine git. Görseller artık ayrı dosyalarda durduğu için `index.html` dosyasına çift tıklayarak açmak bazı tarayıcılarda 3B dokuları bozar; sunucuyla aç.

iPad'de yatay tutarak oynamak en rahatı. Tarayıcılar sesi ilk dokunuşa kadar başlatmaz, başlangıç ekranındaki **BAŞLA** düğmesine bastığında müzik açılır.

## Kayıt

İlerleme tarayıcıda (`localStorage`) saklanır. Tarayıcı verisi silinirse kayıt da gider.

## Teknik

- [three.js](https://threejs.org) (r128) ile 3B. Kopyası `vendor/` içinde, internet olmadan da çalışır.
- Ses efektleri ve yazı tipleri sayfanın içine gömülü, müzikler ayrı mp3 dosyalarıdır.

## Dosya yapısı

```
index.html          sayfa, stil, yazı tipleri
js/game.js          oyunun bütün kodu
assets/img/         bütün görseller (webp/png/jpg)
vendor/three.min.js 3B motoru
muzik_*.mp3         müzikler
```

## Yeni görsel eklemek

Görseller `assets/img/` içinde, adları kodda nerede kullanıldıklarını söyler: önek koddaki tabloyu, devamı anahtarı gösterir. Örnekler: `a8_i_coin.webp` → `A8.i_coin` (arayüz ikonu), `ck_kasif.webp` → `CK.kasif` (Kaşif kokpiti), `shipx_sahin_f.webp` → `SHIPX.sahin.f`.

- **Var olan bir görseli değiştirmek:** Aynı adla, aynı en-boy oranında ve saydam arka planla üzerine yaz. Kod değişmez.
- **Yeni görsel:** Dosyayı `assets/img/` içine koy, kodda ilgili tabloya `anahtar: "assets/img/dosya.webp"` satırını ekle.
- İkonlar için saydam arka planlı kare webp (160×160 yeterli), arka planlar için 2048 genişlik iyi bir ölçü.
