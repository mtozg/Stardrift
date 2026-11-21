# Ekonomi ölçümü (1. tur)

**Durum:** ölçüm. Hiçbir oyun değeri değiştirilmedi. Yazılım çizimiyle, test kaydında, Filo tarafında, Ankora'da ölçüldü; süre değil **miktar** ölçüldü.
**Araç:** `tools/qa/ekonomi_olcum.js` (kredi ve XP değişimleri `window.__ledger` defterinden, değişimi yapan işlev zinciriyle okunur; defter yalnız test kaydında vardır). Çalıştırma: `N=12 node tools/qa/ekonomi_olcum.js` (taraf için `TARAF=korsan`).

## Ölçülen
**Öldürme** (her tür 12 örnek; kredi = ödül + düşen kayıt/ek; XP sabit):
| Tür | Kredi ort. (min–maks) | XP |
|---|---|---|
| raider | 166 (139–196) | 30 |
| brute | 190 (155–225) | 39 |
| reaver | 199 (169–233) | 48 |
| leader | 207 (168–234) | 120 |

**Satış** (Ankora, 16 birim tek tür; kredi / XP):
demir 97 / 20 · buz 162 / 32 · hurda 324 / 30 · titan 421 / 40 · kristal 601 / 90

## Gözlemler (henüz karar değil)
1. Öldürme kredisi türler arasında yalnız ~%25 artıyor (166 → 207); lider avı XP'de 4 kat ama kredide neredeyse aynı. Zor hedefin kredi teşviki zayıf olabilir (H2/H5 ile birlikte bakılacak).
2. Cevher satışı XP'si küçük (16 titan = 40 XP), öldürme XP'si bir hedefte 30–120. Seviye 30 için 32.420 XP gerektiği düşünülürse ilerleme kavgaya bağlı görünüyor; ticaret/madencilik yolunun XP katkısı düşük olabilir.
3. 16 demir 97 kredi (≈6/birim), koddaki taban fiyat 10. Fark istasyon fiyatı/çarpanından olabilir; **doğrulanmadı**, bir sonraki turda istasyon bazında bakılacak.

## Sonraki ölçümler
Kaçak mal satışı, görevler, kalıntı/enkaz, Kadim yankı, ölüm ücreti; Korsan ve Lonca tarafları; istasyon bazlı fiyatlar; **süre başına** kazanç için bot senaryosu. Değer değişikliği ancak bu veriler birleştirilince, önce/sonra tablosuyla önerilecek.
