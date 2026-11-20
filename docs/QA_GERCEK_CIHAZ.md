# Gerçek cihaz test listesi (iPhone / iPad)

Durum: **henüz yapılmadı.** Bütün performans ve bellek bilgisi swiftshader emülasyonundan geliyor. Süre: 15-30 dakika. Test eden: Mehmet (ya da gerçek cihazı olan biri).

## Hazırlık
- Safari'de siteyi aç, ana ekrana ekle (PWA). Bir deneme temiz kayıtla, bir deneme eski kayıtla.
- Pil %60 üstü, şarjda değil. Not al: cihaz modeli, iOS sürümü, Safari ya da PWA.

## A. WebGL ve bellek (6 dk)
| Adım | Geçme ölçütü | Sonuç |
|---|---|---|
| Oyun → Hangar → Oyun, 10 kez | Sayfa yenilenmiyor, beyaz ekran yok | |
| Hangarda Kaşif ↔ Şahin, 8 kez | Model yükleniyor, takılma yok | |
| Arka plana at, 30 sn bekle, dön | Oyun kaldığı yerden devam, ses ve görüntü geri geliyor | |
| Safari "bir sorun oluştu, sayfa yeniden yüklendi" uyarısı | Hiç çıkmamalı | |

## B. Kokpit (4 dk)
| Adım | Geçme ölçütü | Sonuç |
|---|---|---|
| Kaşif ve Şahin 3B kokpit | Ekranlar okunuyor, düğmeler görünüyor | |
| Güneşe bak (cam perdesi) | Göz yormuyor, ekran okunuyor | |
| Yaklaşma yazısı | Üst ortada, konsolu örtmüyor | |
| Yatay ve dikey çevirme | Düzen bozulmuyor | |

## C. Dokunmatik kontroller (4 dk)
| Adım | Geçme ölçütü | Sonuç |
|---|---|---|
| Uçuş, ateş, hızlanma düğmeleri | Kaçan dokunuş ya da takılan düğme yok | |
| Devriye çağrısı (Uy / Kaç / Rüşvet) | Düğmeler parmakla rahat basılıyor | |
| Menüler, pano, Başarımlar | Kaydırma ve dokunma sorunsuz | |
| Uçarken + ateş + menü aynı anda | Kontrol kaybı yok | |

## D. 15-30 dk oyun oturumu (10 dk gözlem)
Madencilik, satış, görev kabulü, bir devriye karşılaşması, bir ölüm ve canlanma, bir istasyona yanaşma (bülten satırı).
| Ölçüt | Not |
|---|---|
| Isınma | |
| Kare hızı düşüyor mu | |
| Pil kaç yüzde düştü | |
| Sayfa kendiliğinden yenilendi mi | |

## E. Yalnız iPad
- 120 Hz ekranda hangar animasyonu iki kat hızlı dönmüyor (1.59.0 düzeltmesi).
- Büyük ekranda kokpit oranı ve yazı boyutları.

## Çıktı
Cihaz bilgisi, süre, pil, görülen hatalar ve ekran görüntüleri bu dosyaya ya da bir mesaja yazılsın. Hata çıkarsa hangi adımda ve ne zaman olduğu yeterli.
