# Sabah kontrol listesi (aşama aşama)

Her aşama ayrı bir commit (ya da ayrı PR). Beğenmediğin aşamayı söylemen yeter; yalnız o aşamanın commit'ini geri alırım (`git revert <sha>`), diğerleri kalır. Ekran görüntüleri `docs/sabah/` altında.
Ekonomi (rütbe, XP, kredi, fiyat) bu aşamaların hiçbirinde değişmez. Ekonomi etkisi olan bir şey çıkarsa buraya "ONAY GEREKİR" diye yazarım ve yapmam.

| Aşama | İş | Durum | Commit / PR | Geri alma |
|---|---|---|---|---|
| 1 | Şahin r014 ve Yük Devi r015 3B kokpitleri oyunda | Hazır, PR #42 senin onayını bekliyor | 9d92f6f / PR #42 | `git revert 9d92f6f` |
| 2 | Hayalet 3B kokpit r001 (Asset Factory production → oyuna `CK3.hayalet`) | Hazır, oyunda; Kapı 1 görsel kararın bekliyor | b58af28 | `git revert b58af28` |
| 3 | Başarım rozet çizimleri (10 rozet × 3 kademe) oyunda; çevrimdışı paket düzeltmesi | Hazır | 1a43723 | `git revert 1a43723` (not: çevrimdışı düzeltmesi de bu commit'te; geri alınırsa Hayalet GLB'leri çevrimdışı pakette olmaz) |

## Nasıl bakarsın
- Aşama 1: Hangarda Şahin ve Yük Devi'yi seç, kokpite gir.
- Aşama 2 ve 3: Hazır olunca bu tabloya işlenecek.

## Aşama 1 görseli
`docs/sabah/asama1_sahin_yuk_kiyas.webp` (Kaşif, Şahin r014, Yük r015, oyun içi).

## Aşama 2: Hayalet (ne gördüm)
Görsel: `docs/sabah/asama2_hayalet_kiyas.webp` (üstte Kaşif, altta Hayalet).
- **İyi:** Geniş açık görüş, ortada dikme yok, ince çapraz direkler, tek mor neon, büyük kapitone koltuk (~140 px; Kaşif ~148), ekranlar oturuyor, 4 kokpit döngüsünde bellek sabit (54/118).
- **Sorunlu (Asset Factory'nin de söylediği):** alt köşelerdeki açık gri altıgen petek güverte göz alıyor; konsol yüzü geniş ve koyu; HUD payı %9,0 (sınır %10); yastıklar tuğla gibi okunabiliyor.
- **Düzeltme hakkı:** 1 küçük tur (altıgenleri koyu ve alçak yapmak). İstersen söyle.
- **Benim düzeltmem:** Teslimdeki HUD sırtının sağ kenarı son üç noktada alt kenara kaçmıştı (HUD kokpitin üstüne taşardı); sol kenarın aynasıyla düzelttim.

## Aşama 3: Başarım rozetleri
Görseller: `docs/sabah/asama3_basarimlar.webp` (oyundaki liste), `docs/sabah/asama3_rozetler_hepsi.webp` (30 rozet).
- **İyi:** 10 rozet × 3 kademe, tutarlı neon çizgi stili; Bronz/Gümüş/Altın renkli; kilitliyken soluk gri; Kapı Bekçisi tek kademe (Altın).
- **Zayıf:** Gezgin (halkalı gezegen) küçükte göz gibi okunabiliyor. Düzeltilebilir.
- **Kod:** yalnız `js/game.js` içinde Başarımlar listesine ikon (`r` anahtarı ve `<img>`); veri, sayaç ve ekonomi değişmedi.
- **Hata düzeltmesi (bu commit'te):** 1.64.1'de `offline.json` Hayalet GLB'lerini içermiyordu (yeni dosyalar `git add`'den önce listelenmişti). Şimdi Hayalet ve 30 rozet dahil (364 dosya, 43,4 MB). Çevrimdışı oyunda Hayalet kokpiti bunsuz yüklenemezdi.
