# Sabah kontrol listesi (aşama aşama)

Her aşama ayrı bir commit (ya da ayrı PR). Beğenmediğin aşamayı söylemen yeter; yalnız o aşamanın commit'ini geri alırım (`git revert <sha>`), diğerleri kalır. Ekran görüntüleri `docs/sabah/` altında.
Ekonomi (rütbe, XP, kredi, fiyat) bu aşamaların hiçbirinde değişmez. Ekonomi etkisi olan bir şey çıkarsa buraya "ONAY GEREKİR" diye yazarım ve yapmam.

| Aşama | İş | Durum | Commit / PR | Geri alma |
|---|---|---|---|---|
| 1 | Şahin r014 ve Yük Devi r015 3B kokpitleri oyunda | Hazır, PR #42 senin onayını bekliyor | 9d92f6f / PR #42 | `git revert 9d92f6f` |
| 2 | Hayalet 3B kokpit r001 (Asset Factory production → oyuna `CK3.hayalet`) | Hazır, oyunda; Kapı 1 görsel kararın bekliyor | b58af28 | `git revert b58af28` |
| 3 | Başarım rozet çizimleri (10 rozet × 3 kademe) oyunda; çevrimdışı paket düzeltmesi | Hazır | 1a43723 | `git revert 1a43723` (not: çevrimdışı düzeltmesi de bu commit'te; geri alınırsa Hayalet GLB'leri çevrimdışı pakette olmaz) |

| 4 | Hayalet r003 (derinlik + büyük ekranlar; Mehmet'in geri bildirimi) | Hazır; r001'in yerine | 2c0c30e | `git revert 2c0c30e` (r001'e döner) |

| 5 | Kaşif ekranları %7 büyütüldü (çerçeveye göre küçük kalmıştı) | Hazır | d9055d8 | `git revert d9055d8` |
| 6 | Hayalet r004: sırt hafif, katmanlı derinlik, ekranlar %7 küçük, neon hizası | Hazır; neon kısmen düzeldi | 60fc45d | `git revert 60fc45d` (r003'e döner) |

| 7 | **EKONOMİ (K50):** ölüm bedeli sayfa yenilenerek atlatılamaz (`dp` bayrağı) | Hazır; Mehmet "onay bekleyen işlere başla" dedi | d9a92da | `git revert d9a92da` |

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

## Aşama 4: Hayalet r003 (Mehmet'in geri bildirimine göre)
Görsel: `docs/sabah/asama4_hayalet_r003_kiyas.webp` (üstte Kaşif, altta Hayalet r003).
- **İstenen:** sorunları çöz, derinlik hissi, ekran yerleşimini değiştir.
- **Olan:** Ekranlar belirgin büyüdü ve çerçeveli yuvalara oturdu, yan ekranlar içe açılı; konsol 3 kademeli; direkler/kemerler oluklu; altıgen güverte koyu; HUD payı %7,5 (r001'de %9,0); koltuk ~140 px. 4 kokpit döngüsünde bellek sabit (71/110, 50/100, 50/106, 50/100).
- **Dürüst eksikler (Asset Factory'nin de söylediği):** altıgen hâlâ orta gri; yastıklar hafif ayrık blok; alt kademeler büyük koyu yüz. Ekranlar çok geniş, neredeyse kenardan kenara (televizyon gibi) görünebilir. Derinlik r001'e göre belirgin ama Kaşif kadar katmanlı değil.
- **Tur hakkı:** Hayalet için r001, r002 (küçük), r003 üretildi; Mehmet kararıyla hak genişletilmişti, r003 son tur. Yeni istek olursa Mehmet onayı gerekir.
- **Not:** Bu commit PR #42'de DEĞİL, yeni PR'da (#42 yalnız aşama 1 ile birleşmişti).

## Aşama 5: Kaşif ekranları
Görsel: `docs/sabah/asama5_kasif_ekranlar.webp` (üstte önce, altta sonra).
Sol/orta/sağ canlı ekran dörtgenleri merkezlerinden %7 büyütüldü (`CK3.kasif.qS = 1.07`, yalnız oyun tarafı; Kaşif modeline dokunulmadı). İçerik çerçeve içinde daha dolgun; kenarlara taşma görmedim. Beğenmezsen `qS` değeri tek sayı (1,05 ya da 1,00 = eski).

## Aşama 6: Hayalet r004 (Mehmet'in 2. geri bildirimi)
İstenen: koltuk arkasındaki yüzey yastık gibi duruyor, hafiflet; derinlik Kaşif kadar katmanlı; ekranlar bir tık küçülsün. Asset Factory'ye iletildi (son tur). Teslim olursa oyuna eklenir; olmazsa r003 kalır.

## Aşama 6: Hayalet r004 (ne gördüm)
Görsel: `docs/sabah/asama6_hayalet_r004_kiyas.webp` (üstte Kaşif, altta Hayalet r004).
- **Düzelenler:** koltuk sırtı artık yastık değil, sade tek yüz + ince koyu mor dikiş; konsolda 3 katlı paneller, braketler, kablo oluğu, kalın ekran çerçevesi (r003'e göre belirgin daha katmanlı); ekran + çerçeve %7 küçüldü; ekranların altındaki neon şeritler ekran kenarına artık oturuyor; HUD payı %7,3; bellek sabit (77/135, 56/125, 56/131, 56/125).
- **Hâlâ sorunlu:** çapraz direklerin neon şeridi hâlâ direk kenarından kopuk/kaymış; üst kemerlerde (sol-üst, sağ-üst) kısa mor çizgiler hâlâ kemeri izlemiyor, havada duruyor; alt güvertede mor ızgara çizgileri fazla parlak, ızgara gibi okunuyor; altıgen orta gri; geniş koyu yüzeyler var.
- **Tur hakkı:** r001..r004 üretildi; Asset Factory 4 tam derleme kullandı (hak 1+1 idi, kendi iki hatasını düzeltmek için). Neon direk/kemer düzeltmesi için yeni tur Mehmet onayı gerektirir.
