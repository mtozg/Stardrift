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

## Tur 2: Korsan ve Lonca tarafı (her tür 8 örnek; **sistem farkı karıştırıcı**)
Uyarı: taraf değişince oyuncu başka sistemde başlar (Korsan = Kara Liman, Lonca = Lonca Pazarı), bu yüzden fark yalnız "taraf" değil **sistem çarpanlarıdır** (Kara Liman: düşman ödülü +%60; Lonca Pazarı: cevher fiyatı +%25, düşman daha zayıf). Aynı sistemde taraf karşılaştırması ayrı ölçülecek.

**Öldürme (kredi ort. / XP):**
| Tür | Filo (Ankora) | Korsan (Kara Liman) | Lonca (Lonca Pazarı) |
|---|---|---|---|
| raider | 166 / 30 | 235 / 45 | 163 / 21 |
| brute | 190 / 39 | 252 / 59 | 160 / 27 |
| reaver | 199 / 48 | 256 / 72 | 149 / 34 |
| leader | 207 / 120 | 267 / 180 | 176 / 84 |

**Satış (16 birim; kredi / XP):**
| Cevher | Filo | Korsan | Lonca |
|---|---|---|---|
| demir | 97 / 20 | 145 / 20 | 196 / 20 |
| buz | 162 / 32 | 227 / 32 | 250 / 32 |
| hurda | 324 / 30 | 389 / 30 | 429 / 30 |
| titan | 421 / 40 | 518 / 40 | 553 / 40 |
| kristal | 601 / 90 | 715 / 90 | 1038 / 90 |

## Gözlemler (karar değil)
1. XP tür ve sistem çarpanlarıyla tutarlı büyüyor (raider 30 → lider 120; Kara Liman ×1,5; Lonca ×0,7).
2. **Öldürme kredisi türe göre neredeyse düz, Lonca'da tersine:** brute ve reaver, raider'dan *az* kredi veriyor (163, 160, 149). Zor hedef daha az kazandırıyor: bu tasarım amacı olamaz; **kaynağı koddan doğrulandı:** `killNpc` içinde korsan ödülü `rand(90, 160) × sistem çarpanı` ve düşman türüne bağlı DEĞİL (XP ise tür çarpanıyla büyüyor). Türler arasındaki küçük fark düşen ek parçalardan ve rastgelelikten geliyor. **Öneri (henüz uygulanmadı):** ödülü XP ile aynı tür çarpanına bağlamak (raider ×1, brute ×1,3, reaver ×1,6, lider ×4). Bu geliri artırır; geç oyun kredi fazlası varsayımı (H1) ölçülmeden uygulanmayacak, önce/sonra tablosuyla raporlanacak.
3. XP, satıştan gelen kısımda sistemden bağımsız sabit (cevher XP = birim miktarı × birim değeri / 8; fiyat çarpanları XP'yi etkilemiyor). Lonca'da fiyat çarpanı yalnızca krediyi büyütüyor.
4. Kristal satışı Lonca'da Filo'ya göre +%73: +%25 çarpanından fazla; istasyon fiyat eğrisi/ stok etkisi olabilir (**doğrulanmadı**).

## Sonraki
Aynı sistemde taraf karşılaştırması, kaçak mal, görevler, kalıntı, ölüm ücreti, süre başına kazanç; ardından Öldürme kredisi tablosunun kaynağı (gözlem 2) incelenir. Değer değişikliği önce/sonra tablosuyla ayrıca raporlanacak.
