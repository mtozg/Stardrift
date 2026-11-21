# Gerçek cihaz test protokolü (Q0-Q10)

Durum: **hazır, uygulanmadı.** Şu anda iPhone/iPad erişimi yok. **Hiçbir test gerçek cihazda yapılmadı; hiçbir sonuç PASS işaretli değil.** Tüm satırlar "BEKLİYOR (cihaz yok)" durumunda.
Referans (taban) sürüm: **main 1.66.4** (yazım sırasında). Ölçüm paneli (T1/T2, PR #47) birleşince `?tani=1` ile kullanılabilir (1.66.5); taban ölçümü için 1.66.2'ye `?tani=1` eklenemez, bu yüzden **taban elle ve ekran kaydıyla** alınır (ya da aynı cihazda 1.66.5 paneli ile güncel sürüm ölçülür ve "taban = 1.66.5, panel kapalı/açık" diye not edilir). Bu fark kayıt tablosunda belirtilir.

## 0. Ortak hazırlık
**Cihaz kaydı (her cihaz için bir kez):** model, iOS sürümü, Safari ya da ana ekran uygulaması (PWA), depolama boşluğu, pil sağlığı, Düşük Güç Modu açık/kapalı, bağlantı (Wi-Fi/hücresel), tarih.
**Önemli uyarı:** Sayfayı **20 sn içinde 3 kez** yenileme. Açılış çökme koruması bunu çökme sayar, önbelleği siler, `?tani=1`'i atar ve cihazda çevrimdışı paket indirmesini **kalıcı kapatır**. Yüklemeler arası ≥21 sn bekle.
**Panel kullanımı (1.66.5):** adrese `?tani=1` ekle; sol alttaki panel `fps`, `medyan`, `düşük%5`, `çizim`, `üçgen`, `doku/geo`, `WebGL`, `yükleme` değerlerini gösterir (`docs/TANI_OLCUM.md`). Her ölçümde **ekran görüntüsü** al; sonuç tablosuna panel değerlerini yaz.
**Elle ölçümler (panel yok):** kronometre (iPhone saat uygulaması), ekran kaydı, Ayarlar > Pil, Ayarlar > Genel > iPhone Depolama (Safari/Uygulama boyutu), dokunarak ısı gözlemi.
**Hesap/kayıt:** testler için ayrı bir test kaydı kullan; gerçek ilerlemeni bozma (Ayarlar'da test modu açılabilir: sürüm numarasına 5 kez dokun).

## 1. Standart senaryolar
| Kod | Senaryo | Süre | Adımlar |
|---|---|---|---|
| **S1** | Kaya alanı | 3 dk | Ankora'da kaya alanına git, madencilik yap, kayalar kırılırken cevher topla |
| **S2** | Savaş | 3 dk | Korsan bölgesinde düşmanlarla savaş (Kızıl Geçit), roket ve lazer, patlamalar |
| **S3** | İstasyon | 3 dk | Ankora'ya yaklaş, yanaş, hangara gir, gemi/kokpit değiştir, kalkış |
| **S4** | Sistem atlama | 4 dk | 3 sistem atla (hiperatlama + kapı), her atlamadan sonra menü aç |
| **S5** | Karışık oturum | 15-30 dk | S1 + S2 + S3 + S4 sırayla; sonra 1 ölüm/canlanma; Ayarlar ve Başarımlar'ı aç |

## 2. Testler
Her test: yöntem, ölçülen değerler, beklenen sonuç, **kabul kriteri**, başarısızlıkta yapılacak.
Kabul kriterlerindeki sayısal eşikler **hedeftir (öneri)**; gerçek cihaz taban ölçümünden sonra Mehmet kesinleştirir.

### Q0: Taban ölçümü (referans sürüm)
- **Yöntem:** Aynı cihazda S1-S5'i bu protokolün başındaki uyarıya uyarak koş; ekran kaydı al. Panelli sürümde panel değerlerini kaydet.
- **Ölçülen:** her senaryo için medyan fps, düşük%5, çizim, üçgen, doku/geo, takılma sayısı; ilk açılış süresi (Q1); depolama.
- **Beklenen:** Sonuçlar kayda geçer. Q0 "geçti/kaldı" değil, **referans değerlerdir**; sonraki testler bununla kıyaslanır.
- **Kabul:** Her senaryo için bir satır dolu ve ekran görüntüsü var.
- **Başarısızlıkta:** Taban beklenmedik kötüyse (örn. medyan <30 fps) önce o sorunu ayrı kayda al; yeni özellikler ondan sonra.

### Q1: İlk açılış süresi (soğuk)
- **Yöntem:** Safari'de site verisini sil; `?tani=1&yukSifirla=1` aç; menü görününceye kadar **panelin** `hazır` ve `menü` değerini oku (kronometre ile de doğrula). Sonra ≥21 sn arayla 4 kez daha (soğuk için her seferinde önbelleği temizle). **5 yükleme medyanı** al. Wi-Fi ve mümkünse hücresel.
- **Ölçülen:** `three`, `gemi`, `ses`, `game`, `başla`, `motor`, `hazır`, `menü` (ms), soğuk ve sıcak medyan.
- **Beklenen:** Hedef (öneri): Wi-Fi'de `menü` ≤4 sn, hücresel ≤8 sn.
- **Kabul:** 5 yüklemenin medyanı hedefin altında; en kötü yükleme ≤2× medyan.
- **Başarısızlıkta:** Hangi aşama büyüyorsa (`ses` ve `game` indirme bitişleri) belirle; 294 KB'lık `data_ses.js` ertelemesi (T3) ve `document.write` zinciri değerlendirilir.

### Q2: Yeni betik dosyalarının etkisi (1.66.1'de `data_gemi.js`, `data_ses.js`)
- **Yöntem:** Aynı cihazda 1.65.x (tek `game.js`) ile güncel sürüm karşılaştırılır; eski sürüm için eski bir adres/kopya gerekir. **Cihaz yoksa ya da eski sürüm sunulamıyorsa** karşılaştırma yerine yalnız güncel sürümde `gemi`/`ses` indirme bitişlerinin `game`'e göre eklediği süre okunur.
- **Ölçülen:** 5'er yükleme, soğuk/sıcak medyan `menü`; `gemi` ve `ses` bitiş farkı.
- **Beklenen:** Fark ≤ +%10 ve ≤ +300 ms.
- **Kabul:** Hedefin altında.
- **Başarısızlıkta:** T3 (ses verisini ertele) değerlendirilir; **yalnız ölçüm doğrularsa**.

### Q3: Çevrimdışı paket
- **Yöntem:** (a) Ayarlar altında "Çevrimdışı paket hazırlanıyor" göstergesi bitene kadar **süreyi kronometreyle** ölç (Wi-Fi, mümkünse hücresel). (b) iOS Ayarlar > Safari/uygulama depolamasından boyut. (c) **Uçak modu**: uygulamayı kapat, aç; 4 kokpit, hangar, istasyon, 2 sistem atlama.
- **Ölçülen:** indirme süresi, disk boyutu, çevrimdışı açılış süresi, eksik model/ses/görsel sayısı.
- **Beklenen:** Paket ≈43-44 MB; indirme ≤90 sn Wi-Fi (öneri); uçak modunda açılış ≤6 sn; hiçbir model/ses eksik değil.
- **Kabul:** Çevrimdışı tüm özellikler çalışır; disk ≈ paket boyutu (±%30).
- **Başarısızlıkta:** Hangi dosyaların eksik olduğunu not et; indirmeyi önceliklendirme/bölme (T9, T-liste); iOS depolama kotasını aşıyorsa boyutu düşür. **Önce `sd_nosync` bayrağının kendiliğinden kapanmadığından emin ol** (hızlı yenileme riski).

### Q4: 15-30 dk kesintisiz oturum
- **Yöntem:** S5; ekran kaydı açık; panel her 5 dakikada ekran görüntüsü.
- **Ölçülen:** medyan fps ve düşük%5 (5 dk'lık dilimlerde), `takılma>100ms`, çizim/üçgen, doku/geo (artış var mı), pil %, ısınma gözlemi (not), sayfa yeniden yüklendi mi.
- **Beklenen:** Hedef (öneri): 60 Hz'de medyan ≥55, düşük%5 ≥40; 120 Hz iPad'de medyan ≥90.
- **Kabul:** Sayfa yeniden yüklenmesi/beyaz-siyah ekran **0**; kare hızı düşüşü (ilk ve son 5 dk arasında) ≤%20; takılma ≤3/dk; doku/geometri sayısı artmaya devam etmiyor (sızıntı yok); kayıt kaybı yok.
- **Başarısızlıkta:** Çöken/yavaşlayan anı ve sahneyi not et, ekran kaydını sakla; Q5 ve Q8 ile bağla; kalite otomatik düşürme eşiğini incele.

### Q5: WebGL bağlamları
- **Yöntem:** (1) Hangar↔oyun ×10, (2) 4 kokpit ×2 değişim, (3) 4 sistem atlama, (4) Ayarlar ve Başarımlar aç/kapa ×10 (rozet/ikon çizicisini tetikler), (5) XR görünümü varsa aç. Her adımdan sonra paneldeki `WebGL oluşturulan/kayıp/geri` değerini kaydet.
- **Ölçülen:** `oluşturulan`, `kayıp`, `geri`, `renderer` sayısı; "Grafik bağlamı kayboldu" bildirimi; Safari'nin "bir sorun oluştu, sayfa yeniden yüklendi" uyarısı.
- **Beklenen:** Kodda en çok 4 bağlam (ana, hangar, XR, rozet/ikon) olabileceği **biliniyor**; panel gerçek sayıyı verir.
- **Kabul:** `kayıp` = 0; uyarı/yeniden yükleme **0**; `oluşturulan` ≤4.
- **Başarısızlıkta:** Hangi adımda kaybolduğunu not et; bağlamları birleştirme (T6) ancak **bu testin sonucuna göre** düşünülür.

### Q6: Dokunmatik kontroller ve ekran uyumu
- **Yöntem:** Her cihazda yatay (oyun yatay) ve dikey (döndür uyarısı), mümkünse en küçük ekran (SE/mini) ve en büyük ekran. Kontrol listesi: uçuş, ateş, hızlanma düğmeleri; uçuş + ateş + menü aynı anda; devriye çağrısı (Uy/Kaç/Rüşvet); istasyon sekmeleri kaydırma; Başarımlar; hesap formu (klavye açılınca görünüm); Ayarlar kaydırma; çentik/güvenli alan; Kaşif ekran okunurluğu.
- **Ölçülen:** her madde için "çalışıyor/sorun" ve ekran görüntüsü.
- **Beklenen:** Düğmeler ≥42 px, hiçbir öğe kesilmiyor veya örtülmüyor; kaçan/takılan dokunuş yok.
- **Kabul:** Hiç engelleyici sorun yok; küçük sorunlar kayda geçti.
- **Başarısızlıkta:** Cihaz/ekran/yön ve ekran görüntüsüyle kayıt; düzen düzeltmesi ayrı iş.

### Q7: Arka plan ve kesinti
- **Yöntem:** Kilit ekranı (30 sn), başka uygulamaya geçiş, arama/bildirim gelmesi, Düşük Güç Modu açıkken oyna.
- **Ölçülen:** geri dönüşte ses/görüntü, kayıt, fps (Düşük Güç'te).
- **Beklenen:** Geri dönüşte oyun sağlam; Düşük Güç Modu'nda fps ≤30 olabilir (kabul edilebilir, not et).
- **Kabul:** Çökme/siyah ekran yok; kayıt korunmuş.
- **Başarısızlıkta:** Duraklama/yeniden başlatma mantığı (`visibilitychange`, `AudioContext` durumu) incelenir.

### Q8: Isınma ve pil
- **Yöntem:** Q4 sırasında başlangıç/bitiş pil %, 15 ve 30. dakikada dokunarak sıcaklık, kare hızı eğrisi.
- **Ölçülen:** pil kaybı %, sıcaklık gözlemi (hafif/ılık/sıcak/çok sıcak), fps düşüşü.
- **Beklenen:** Pil kaybı ≤%15/30 dk (öneri); ısınmadan kaynaklı sürekli fps çöküşü yok.
- **Kabul:** Hedefler içinde; çok sıcak uyarısı yok.
- **Başarısızlıkta:** Bloom ve kalite varsayılanları, kare sınırlayıcı değerlendirilir.

### Q9: 120 Hz iPad
- **Yöntem:** Hangar animasyonu hızı, genel akıcılık (panelde `medyan`).
- **Beklenen:** Animasyon hızı kare hızından bağımsız (1.59'da düzeltildi); medyan ≥90 fps.
- **Kabul:** Animasyon normal hızda, akıcı.
- **Başarısızlıkta:** Kare sınırlayıcı ve animasyon zamanlaması incelenir.

### Q10: Çevrimdışı oyun ve kayıt
- **Yöntem:** Uçak modunda 10 dk oyna, uygulamayı kapat, aç; sonra internete bağlan.
- **Ölçülen:** kayıt kaybı, bulut eşitlemesi (hesap açıkken) davranışı, hata penceresi.
- **Beklenen:** Kayıt kaybı yok, eşitleme sessiz.
- **Kabul:** Hiçbir ilerleme kaybolmadı; çökme yok.
- **Başarısızlıkta:** Firebase kontrol listesindeki F7 ile birlikte kayda al; kayıt mantığı incelenir.

## 3. Sonuç kayıt tablosu (cihaz başına bir kopya)
Cihaz: __________ iOS: ______ Safari / PWA: ______ Sürüm: ______ Panel: açık / kapalı Tarih: ______

| Test | Durum | Medyan fps | Düşük%5 | Çizim | Üçgen | Doku/Geo | WebGL (ol./kay.) | Süre / pil / ısı | Ekran görüntüsü | Not |
|---|---|---|---|---|---|---|---|---|---|---|
| Q0 S1 | BEKLİYOR (cihaz yok) | | | | | | | | | |
| Q0 S2 | BEKLİYOR (cihaz yok) | | | | | | | | | |
| Q0 S3 | BEKLİYOR (cihaz yok) | | | | | | | | | |
| Q0 S4 | BEKLİYOR (cihaz yok) | | | | | | | | | |
| Q0 S5 | BEKLİYOR (cihaz yok) | | | | | | | | | |
| Q1 açılış (5 yükleme medyan) | BEKLİYOR (cihaz yok) | | | | | | | | | |
| Q2 betik etkisi | BEKLİYOR (cihaz yok) | | | | | | | | | |
| Q3 çevrimdışı paket | BEKLİYOR (cihaz yok) | | | | | | | | | |
| Q4 uzun oturum | BEKLİYOR (cihaz yok) | | | | | | | | | |
| Q5 WebGL | BEKLİYOR (cihaz yok) | | | | | | | | | |
| Q6 dokunmatik | BEKLİYOR (cihaz yok) | | | | | | | | | |
| Q7 arka plan | BEKLİYOR (cihaz yok) | | | | | | | | | |
| Q8 ısınma/pil | BEKLİYOR (cihaz yok) | | | | | | | | | |
| Q9 120 Hz | BEKLİYOR (cihaz yok) | | | | | | | | | |
| Q10 çevrimdışı kayıt | BEKLİYOR (cihaz yok) | | | | | | | | | |
Durum değerleri: BEKLİYOR (cihaz yok) · PASS (yalnız gerçek cihazda ölçülüp kriteri sağladıysa) · FAIL (+ ne olduğu) · KISMEN (+ açıklama).

## 4. Otomatik testlerle ilişki
`tools/qa/` altındaki testler (swiftshader, yazılım çizimi) mantığı doğrular; **bu protokolün yerini tutmaz.** Özellikle FPS, bellek, ısınma, pil, WebGL sınırı ve dokunmatik deneyimi için otomatik test sonucu kanıt sayılmaz.
