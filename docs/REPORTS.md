# Stardrift — Denetim ve Analiz Raporları (özet arşivi)

QA Engineer ve Game Designer oturumlarının raporlarının özeti. 2026-11-20 ekip değişikliğiyle (K16) bu işler Lead Developer'a geçti.
Satır numaraları `js/game.js` 1.53.1 içindir; sonraki sürümlerde kayabilir.

## 1. QA ilk denetimi (1.53.1, statik inceleme)

### Kanıtlı hatalar
| Öncelik | Bulgu | Konum | Durum |
|---|---|---|---|
| P1 | Bekçi, güncelleme 3,5 sn durursa ve ekran yataysa `paused=false` yapıyor; `__menuOn`'u DOM sezgisiyle sıfırlıyor. Bilinçli duraklatma bozulabilir. | 10431-10441 | S1-03 |
| P1 | Hangar `hgSet` eski modeli çıkarıyor ama dispose etmiyor | 4014-4016 | S1-03 |
| P1 | Aynı anda en fazla 4 WebGL bağlamı (ana, hgR, XR, R3), forceContextLoss yok; iOS bellek riski | 28, 4112, 4260, 6645, 9609 | S1-03 |
| P1 | Kargo kayda yazılmıyor | 1092 civarı | S1-13 (K9 onaylı) |
| P1 | Eski "Claude hesabı" bulut yüklemesi SAVEKEY yerine sabit `kayip-yildizlar` anahtarına yazıyor | 5976 | S1-04 |
| P1 | İki zaman damgası (`save.ts` / `save._t`) ayrı güncelleniyor; bulut çakışma kararı tutarsız | 5970, 10178 | S1-04 |
| P1 | `saveWorld` yalnız curSys 0'da; stokta yalnız demir/buz/kristal | 2969-2974 | Backlog |
| P2 | Hangar sürükleme tick'i durmayan rAF döngüsü | 6422 | Backlog |
| P2 | Bekçi her saniye body çocuklarında getComputedStyle | 10432 | S1-03 |
| P2 | Kare hızına bağlı animasyonlar (120 Hz'de iki kat hızlı) | 4021, 6422 | Backlog |
| P2 | dt 0,05 sınırı; 20 FPS altında oyun zamanı yavaşlıyor | 7968 | Backlog |
| P2 | Ham "Hata: …" toast'ları oyuncuya gösteriliyor | 7965 | Backlog |
| P3 | README eski bilgiler (Kokpit görünümü ayarı, 4/6 evren) | README | Kısmen düzeldi (PR #30) |
| P3 | Her kare `$('bDock')` / `$('bLock')` DOM sorgusu | 7978 | Backlog |
| P3 | Sürüme 5 dokunuş test modunu açıyor (999.999 kredi, ayrı kayıt) | 7038 | Bilgi |

### Riskler / doğrulanacaklar
- Kayıt şeması sürümsüz; kayıt kodu düz JSON+base64; Firestore `codes` anonim yazma, kurallar repoda yok (T2, T3). B-08.
- Eski yerel hesaplar: SHA-256, tuz yalnız kullanıcı adı (T4).
- `renderExtras`, `renderDock`, `killNpc` 10'ar kez, `dockLayout` 9 kez sarılmış; test/CI yok (T1). B-07, B-09.
- Ziyaretçi tüccar "Yükünü sat" canSell/repMul/stok mantığını atlıyor (G4, bilgi).
- Ödül avcısı `__skA` katlanması: S1-06 ölçümüyle **sorun yok** (tek çarpan, en çok ×1,45).

## 2. QA PR #28 incelemeleri
- S1-01 (statik): koşullu PASS. `__ckb.swap` ekonomi baypası (P1) ve dropB dispose (P2) → S1-02a (bc5ba4a) ile düzeltildi.
- S1-01c (statik): bc5ba4a ve 53dfdf6 PASS. Kaşif hiza farkı ölçüm referansı yuvarlaması, gerileme değil.
- S1-01c (Playwright, masaüstü 1600×800 + iPhone 13): **PASS**. K→Ş→K→Ş→K doku Δ0, gerçek kayıtta `__ckb.swap` tanımsız, hata yok. GLB engellenince ~30 sn hazırlık ekranı, sonra mesajsız HUD modu (K14, S1-17).
- Açık: GLB'ler `offline.json`'da yok (S1-10).
- Kurulum: `git archive` ile geçici klasör, `python3 -m http.server`, Playwright Chromium (swiftshader), service worker kapalı, test anahtarı `kayip-yildizlar:test`.

## 3. QA diğer doğrulamalar
- **S1-01b Morr erişimi:** PASS. Filo oyuncusu Ankora ücra kapısıyla (0→5, 400 kr) gidebilir. Riskler: Kara Liman korsan ≤ −60'ta yanaşmayı reddeder; ücra kapı 3,2 km'ye girmeden haritada görünmez; zincirde ipucu yok → S1-11.
- **S1-14 üste kaçak satışı:** KANITLI. Üste gümrük yok (8668), satış 150 kr ile açık (8669-8685). Devriyesiz sefer birim başı +60 kr. Kara Liman'daki oyuncu üssü kara pazar gibi davranıyor olabilir → K13, S1-15.
- **PR #30:** PASS (merge sonrası). README'de 2 saatlik bekleme süresi eksik (P3).
- **K9 kargo kaydı test senaryoları (S1-13 kabul kriterleri):** A kalıcılık (yenileme, pagehide, hiperatlama, gemi değişiminde kapasite aşımı); B kopya (sat→yenile, gümrük el koyma, ziyaretçi tüccar, yerdeki cevherin yeniden doğması, korsan düşürmesi); C bulut çakışması; D kayıt kodu (eski kod, bozuk değerleri 0..cargoCap'e sınırlama); E kaçak gizli bölme; F test modu ve QuotaExceeded. Geçme koşulu: kargo + kredi toplam değeri hiçbir senaryoda artmaz.

## 4. Game Designer ilk raporu
- Döngü: kalk → maden/av/sinyal → topla → sat → XP + kredi → yetenek → ana görev → kapı → yeni evren.
- Güçlü: evrene özgü cevher, tutarlı risk/ödül, 3 taraf gerçekten farklı, düzenli sinyaller.
- Zayıf: başlangıç kargosu 12 birim (sefer ≈ 240 kr); erken oyunda savaş ve madencilik kopuk; Bölüm 6 doruksuz; hikâye sonrası hedef yok; Efsane seviyeleri duvar gibi (3450 XP/seviye).
- Öneriler: (1) üs pasif gelir sınırı → S1-06 ölçümü: zaten tavanlı, değişiklik gerekmiyor; (2) yan görev ödülleri evrene göre → S1-06: av görevleri zaten tehlike çarpanlı; (3) yetenek sıfırlama (B-06); (4) Bölüm 6 final patronu (B-04); (5) Pilot Kütüğü + başarımlar (B-05).

## 5. Game Designer S1-07 denge analizi (K6, K7)
- Kaçakçılık bugün Korsan için zarar ettiriyor (Ankora'da sefer başı ≈ −340 kr); Korsan Bölüm 1 "5 birim kaçak sat" adımı zorunlu.
- K6: −50 öneri (−60 eşiğine 10 puan pay; devriye saldırısı, Ankora yanaşma ve ceza ödeme bu eşiğe bağlı). Onaylandı.
- K7a: gümrük %25 yalnız Korsan. Onaylandı. K7b: tarama %25. Onaylandı.
- K7c: 6 XP/birim → 500-900 XP/saat, üs + Kaçakçı yeteneğiyle ≈ 1.440 XP/saat; Usta Pilot'a ≈ 2 saat. Üs açığı yüzünden ertelendi.

## 6. Developer analizleri
- **Taraf mekanikleri (Aşama 1 önerisi):** A bölge tablosu, B `foe()` yalnız hedef rengi, C devriye karar mantığı (tespit → çağrı → tarama → takip → durdurma → saldırı; rüşvet; tüccar kaçışı), D taraf unvanları (rütbe + zincirden türetilir, RANKS değişmez). K12: Mehmet ayrı ayrı karar verecek.
- **S1-06 ölçümü:** Üs geliri tavanlı (500/1200/2500, 13-16 dk'da dolar, sonra durur). Av görevi ödülleri tehlikeye göre (Buzul 132-396, Kızıl 374-1122). `__skA` tek çarpan, en çok ×1,45; Filo itibarı bonusu da çarpana giriyor (bilgi). Değişiklik önerilmedi.

## 7. Asset Factory ölçümü (S1-02b)
- bc5ba4a'da kokpit payı Kaşif 28 doku / Şahin 7 doku, döngü başına Δ0. Daha önce görülen +4, açılıştan sonraki ilk ~40 sn'deki tembel yüklemeden geliyor. Bellek testlerinde taban çizgisi ≥ 40 sn sonra alınır (67efa36).
- Masaüstünde gemi değiştirmeden de 'diğer' dokular yavaşça artıyor (157 sn'de +8) → S1-03'te araştırılacak.

## 8. Devir notları (2026-11-20, K16)

### Game Designer
- **Bölüm 6 final patronu (B-04):** Bölüm 6'nın 6 adımının beşi üs adımı, doruk yok. Mevcut BOSS sistemiyle (3 aşama) Kadim Kapı ötesi bir "Bekçi" muhafızı; üs adımları Bölüm 5-6'ya yayılır. Dikkat: Filo zinciri `save.boss.length ≥ 6` istiyor; yeni patron ayrı bayrak kullanmalı.
- **Pilot Kütüğü (B-05):** `save.st`, `save.boss`, `kadim.n`, `expPct()` hazır; yalnız arayüz. Ödül kozmetik rozet (Asset Factory: 20-30 rozet, 160×160 webp). Ekonomi etkisi yok.
- **Efsane seviye duvarı:** Rütbeye dokunmadan, hikâye sonrası "Derin Sinyaller" içerik katmanı (derin kuşaklarda daha tehlikeli sinyaller).
- **Erken oyun kargosu 12 birim:** Başlangıç 16-18 ya da ilk ana görev ödülüne 1 "Sıkı istif" puanı. **Ekonomi etkisi var, onay gerekir.**
- **Diğer onay gerektiren öneriler:** ücretli yetenek sıfırlama; ölüm cezası (kredinin %10'u) üst sınırı; kozmetik mağaza (oyun sonu kredi harcaması). Üs geliri ve yan görev çarpanı S1-06 ile gereksiz bulundu.
- **Küçük içerik:** Pano şablonlarına taşıma/eskort/keşif; taraf zincirlerinin 2. adımına telsiz sahnesi; Filo Bülteni (P3).

### QA
- Playwright betiği: `tools/qa/qa_pr28.js`. Kurulum: test edilecek commit `git archive` ile ayrı klasöre, `python3 -m http.server 8766`, `node tools/qa/qa_pr28.js <çıktı> 8766` (~8 dk). Açılış akışı, ölçüm kancaları ve referans değerler betiğin başında.
- QA'nın iletmediği yeni bulgu yok.

### Developer
- Oturum 5 saatlik kullanım sınırına takıldı; devir notu gelmedi. `claude/bold-bardeen-oqf73o` dalında PR #30 sonrası push edilmiş yeni iş yok (9d93a58). S1-13 sıfırdan başlar.

### Asset Factory
- PR #28 main ile birleştirildi (fd6a7c5, sürüm 1.54.0, çakışma çözüldü, iPhone 13 testi geçti). Birleştirme Mehmet'te.
- Yük Devi PRODUCTION, fabrikanın Kapı 1 kaydını bekliyor: `cd tools/asset_factory && python3 factory.py approve yuk_cockpit --gate visual --by "Mehmet" --note "PREVIEW r007 onayı"` (Asset Factory oturumunda Mehmet'in izni gerekir).

## 9. Sürüm 1.55.0 test özeti (Lead Developer, PR #32)
Playwright, swiftshader, test kaydı. Betikler oturum geçici klasöründe; kokpit testi `tools/qa/qa_pr28.js`.

| Konu | Sonuç |
|---|---|
| K9 kargo kaydı: eski kayıt, yenileme, pagehide, satış sonrası, bozuk değerler, gemi değişimi kapasite engeli, gerçek kayıtta test kancası yok | Geçti |
| K13: Ankora satış var; Kara Liman ana istasyonu kara pazar; Kara Liman'daki üste pazar yok, zorla alım etkisiz | Geçti (Ankora'daki üsse yanaşma test ortamında tamamlanamadı) |
| K6 göç: temiz korsan −65 → −50; Filo gemisi düşürmüş (−65), hain (sideN, −65) ve kötüleşmiş (−80) kayıtlar değişmedi | Geçti |
| 1-B: Korsan'da devriye "wary" (mor), kargo/madenci "prey", korsan "ally"; Filo'da korsan "foe" | Geçti |
| 1-A: "Sıçrama tamamlandı: Kızıl Geçit · Çekişmeli bölge" | Geçti |
| S1-11: Filo + 3 patron, Morr yenilmemiş → "Ücra kapı → Kara Liman" işaretli; Morr yenilmişse işaret yok | Geçti |
| K14: model engelli → 30 sn sonra uyarı; engel kalkınca "Kokpit yüklendi" | Geçti |
| S1-03 hangar: 3 tur × 4 gemi, geometri 45 sabit, doku ilk turdan sonra 24 sabit | Geçti |
| Kokpit regresyonu (qa_pr28.js): K→Ş→K→Ş→K doku Δ0 (masaüstü 71/50, iPhone 54/33), engel kalkınca ~12 sn'de toparlanma, gerçek kayıtta `__ckb.swap` tanımsız | Geçti |
| Sayfa hatası | Hiçbiri |

Test edilmeyenler: gerçek iPhone/iPad, bulut kaydında iki cihaz çakışması, Firebase.

## 10. Sürüm 1.56.0 test özeti (Aşama 1-C)
| Konu | Sonuç |
|---|---|
| Karar tablosu: Ankora temiz/kaçak/★2/★3/itibar ≤ −60 → yok/çağrı/çağrı/saldırı/saldırı; Kızıl kaçak %50 çağrı, ★2/★3/düşük → çağrı; Zümrüt ★2 yok, ★3/düşük saldırı; Lonca Pazarı hiçbiri | Geçti |
| Filo, 4 kaçak, Ankora: çağrı kutusu → Uy → tarama (3 sn) → sonuç; aranma değişmedi | Geçti |
| Korsan, 10 kaçak, Ankora: kutuda "Rüşvet · 450 kredi"; rüşvet → −450 kredi, tarama yok, kaçak 10 kaldı | Geçti |
| Kaç: aranma 1 → 2 (tek artış; ikinci devriye 30 sn çağrı yapmaz), takip; süre sonunda yakındaysa devriye düşman | Geçti |
| Tüccar kaçışı: Korsan 250 m'ye girince kargo gemisi kaçıyor | Geçti |
| Önceki testler (göç, renkler, bölge mesajı, ücra kapı, K14, K13) | Geçti |
| Sayfa hatası | Hiçbiri |

Not: test ortamında (swiftshader) oyun saati gerçek zamanın yaklaşık 1/8'i hızında akıyor; zamanlı adımlar oyun saatine göre beklendi. Korsan selamı (itibar ≥ 60) ayrıca test edilmedi.

### iPhone 13 boyutunda oyun testi (dokunmatik, 750×342)
Senaryo: Korsan kaydı → Kara Liman'da dokunarak 10 kaçak al → Ankora → devriyenin yanına git → çağrı kutusu → dokunarak rüşvet.
Bulunan ve düzeltilen hatalar:
1. **Eski kural korsana koşulsuz ateş ettiriyordu** (`js/game.js` "Filo devriyeleri korsanı görünce ateş açar"): temiz korsan Ankora'ya girer girmez 800 m içindeki devriyeler saldırıyor, gemi ~10 sn'de parçalanıyordu. K6 (−50) ve K20 tablosunu geçersiz kılıyordu; önceki testler çaylak korumasıyla çalıştığı için görünmedi. Artık devriye kararına bağlı.
2. **Duran oyuncu seçim yapamıyordu:** çağrı 1 sn sonra kendiliğinden taramaya geçiyordu. Artık "Uy" ya da 3 sn yavaş kalma gerekir.
3. **Düğmeler her 0,25 sn yeniden oluşturuluyordu:** dokunuş kaybolabiliyordu. Kutu artık aşama başına bir kez kurulur; düğmeler `pointerdown` ile (uçuş düğmeleri gibi) çalışır, 42 px yüksekliğinde.
Sonuç: çağrı kutusu iPhone ekranında okunaklı; dokunarak rüşvet −450 kredi, tarama yok, kaçak korundu; hata yok.

## 12. Sprint 2 (1.58.0) test özeti
Regresyon seti artık depoda: `bash tools/qa/run.sh` (9 test; bekleme ~20 dk). Kokpit/bellek testi ayrı: `node tools/qa/qa_pr28.js`.
| Test | Sonuç |
|---|---|
| kargo_kaydi, kacak_uste, toplu_regresyon, devriye_akis, devriye_rusvet, telefon_devriye, hangar_bellek | PASS |
| bekci: görev adımı gelmeden aktif değil; adım gelince doğuyor; Filo ve Korsan'da düşman; faz 2 (takviye) ve faz 3 (öfke); ölünce `save.bekci`, `save.boss` 6'da kalıyor | PASS |
| kutuk: 10 rozet, kademeler, "Pilot Kütüğü · 9/30" başlığı, açılır bölüm | PASS |
**Bekçi ödülü:** yalnız rozet. Mevcut öldürme ödülü geçerli (test kaydında Filo +1.045 kredi / +30 XP, Korsan +80 kredi / +50 XP; normal bir patron gemisi öldürmeyle aynı sistem). Yeni ödül değeri eklenmedi.
Sınırlar: gerçek cihaz; Bekçi savaşının gerçek oynanış dengesi (gövde 2.600, salvo 24 hasar) elle denenmedi, yalnızca akış otomatik test edildi.

## 13. Sürüm 1.59.0 (Sprint 3) test özeti
| Konu | Sonuç |
|---|---|
| unvan_hata: 7 kademe × 3 taraf unvanı doğru; test kaydında ham hata metni, gerçek kayıtta "Küçük bir sorun oluştu, oyun devam ediyor." | PASS |
| hangar_bellek (hangar animasyon değişikliği sonrası) | PASS |
| Yaklaşma yazısı: Kaşif 3B kokpitinde üst orta kısımda (ekran görüntüsü), konsolu örtmüyor | Doğrulandı |
| Sayfa hatası | Yok |
Not: 120 Hz'de animasyon hızı gerçek ekranda denenmedi; yöntem zaman tabanlı (dt) olduğundan 60 Hz'de davranış aynıdır.

### 1.59.2 eki
- Hangar geri dönüş döngüsü (QA P2 "hiç durmayan rAF"): yalnız gemi bırakıldıktan sonra çalışır, bitince durur. Test `hangar_geri`: sürükleme hgYo 1,6 → bırakınca 4 sn içinde 0: PASS. `hangar_bellek`: PASS.

## 14. Sürüm 1.60.0 test özeti
| Test | Sonuç |
|---|---|
| ozel_ekonomi: Kaşif kargo kapasitesi 16; Filo unvan 2'de "Uzak devriye" teklifi, unvan 1'de yok; yakında öldürme 0 ilerleme, 9 km uzakta 1; Lonca "Toplu sipariş" (n=34); Korsan "Pusu"; kaçak satışı 4 birim → +20 XP | PASS |
| kargo_kaydi, kacak_uste, kutuk (kapasite 16 sonrası) | PASS |
Not: 3. ve 4. kademe görevleri yok; yalnız 2. kademe. Test ortamında oyun saati yavaş akar; zamanlı adımlar oyun saatine göre beklendi.

## 15. Sürüm 1.61.0 test özeti
| Test | Sonuç |
|---|---|
| bildirim: açılışta 0 bildirim (taban çizgisi sessiz kaydedilir); satış sayacı 40 → 60 ve unvan 1 → 2 sonrası sırayla "Başarım: Madenci · Bronz" ve "Yeni unvan: Devriye Subayı" | PASS |
| kutuk, unvan_hata | PASS |
Not: telsiz mesajı (unvan atlayınca) ve ses otomatik testte doğrulanmadı; metinler `ULINES` tablosunda.

## 16. Sürüm 1.62.0 test özeti
| Test | Sonuç |
|---|---|
| pano_yeni: Keşif şablonu (N 25-45, ödül 7N), Kargoyu doldur (100 kredi), keşif ilerlemesi (uzak noktaya gidince 4 kare), kargo dolunca görev biter | PASS |
| derin_sinyal: 14 km derinlikte zorla tetiklenen sinyal teklif eder, kabul edilince 5 muhafız doğar, hepsi düşünce ≥ 450 kredi ödül | PASS |
| ozel_ekonomi, bildirim (ctGen sarmalayıcılarıyla birlikte) | PASS |
Not: "yalnız derin kuşakta çıkar" kuralı (ağırlık fonksiyonu) otomatik testte doğrulanmadı; zorla tetikleme bu kuralı atlar. Kod incelemesiyle kontrol edildi.

## 17. Sürüm 1.62.3 test özeti
| Test | Sonuç |
|---|---|
| derin_kural: Kadim yankı ağırlığı 14 km'de 2; 7 km, 3 km ve 12,5 km'de 0; 12,7 km'de 2; Lonca'da 2; Korsan'da 0 | PASS |
| olum_hesap: ölüm bedeli 0→0, 30→30, 50→50, 200→50, 500→50, 600→60, 1000→100, 8000→800, 19999→2000, 25000→2000, 999999→2000 | PASS |
| derin_sinyal, olum_siniri, pano_yeni, bildirim, ozel_ekonomi, kutuk (olay seçicisi `evW` işlevine ayrıldı; davranış aynı) | PASS |
Not: `evW` ve `feeT` yalnızca `:test` kaydında dışarı verilir. Gerçek cihaz ve K37'nin gerçek oynanış dengesi test edilmedi.

## 18. Sürüm 1.63.0 test özeti
| Test | Sonuç |
|---|---|
| bulten: Filo, Lonca ve Korsan oyuncusu yanaşınca kendi önekli bülten satırı çıkar, `{u}` yer tutucusu kalmaz, sayfa hatası yok | PASS |
Not: seçim rastgele; her koşul satırı tek tek otomatik doğrulanmadı. Başlık yanındaki yerleşim ekran görüntüsüyle kontrol edildi.

## 19. Sürüm 1.63.1 test özeti
| Test | Sonuç |
|---|---|
| zincir_telsiz: `__chainSay` korsan 1. ve Filo 3. adımda telsiz satırı verir, çift adımda (Lonca 2) vermez, sayfa hatası yok | PASS |
Not: gerçek ana görev düğmesinden tetiklenme (kanca `S.src` kullanır) otomatik testte uçtan uca denenmedi; kanca tek satır ve `try/catch` içinde.

## 20. Sürüm 1.63.2 test özeti
| Test | Sonuç |
|---|---|
| hesap_kayit (taklit Firebase sunucusu): doğrulama e-postası bağlantı adresi yüzünden reddedilince önce adresli, sonra adressiz gönderilir ve kayıt "hesabı etkinleştir" ekranına geçer. Düzeltme öncesi aynı test "Bir sorun oldu: auth/unauthorized-continue-uri" ile FAIL | PASS |
Not: gerçek Firebase sunucusu, Google girişi (iOS PWA'da açılır pencere sorunu olabilir) ve e-postanın gerçekten gelmesi test edilmedi. Authorized domains ayarı Firebase konsolunda kontrol edilmeli (mtozg.github.io).

## 21. Sürüm 1.63.3 test özeti
| Test | Sonuç |
|---|---|
| sifirla: Ayarlar'da Kayıt bölümünde düğme; yanlış yazıda hata ve kayıt duruyor; "sıfırla" yazınca kayıt silinir, oyun yeniden açılır ve eski pilot yok | PASS |
Not: bulut silme gerçek Firebase'e karşı denenmedi (silme başarısız olursa yeni yerel kayıt daha yeni olduğu için buluta yazılır); gerçek cihaz test edilmedi. Arayüz ekran görüntüsüyle kontrol edildi.

## 22. Sürüm 1.64.0 test özeti (Şahin r014 + Yük r015 kokpitleri)
| Test | Sonuç |
|---|---|
| GLB sağlama: oyundaki 4 dosyanın SHA256 öneki teslim paketiyle aynı (Şahin d1305121 / 4a3626bb, Yük 590744a1 / 82517d0f) | Eşleşti |
| Kaşif → Şahin → Yük döngüsü ×4 (masaüstü): doku/geometri tur boyunca sabit (76/123, 55/113, 55/119), sayfa hatası yok | PASS |
| `qa_pr28.js` (Kaşif↔Şahin ×5 masaüstü ve iPhone 13 yatay boyutu): doku sabit (77→56→77→56→77; 62→41→62→41→62), engelli GLB'de toparlanma 10,4 sn, gerçek kayıtta `__ckb.swap` tanımsız | PASS |
| Oyun içi görsel kontrol (Kaşif / Şahin r014 / Yük r015): ekranlar köşelere oturuyor, HUD sırtı doğru, orta dikme yok | Ekran görüntüsüyle |
Not: swiftshader sayıları gerçek GPU'dan farklı olabilir; gerçek cihaz (iPhone/iPad) test edilmedi. Yük'te kıskaç statik. Resmî Kapı 2 kaydı (`factory.py approve/deliver`) Mehmet'in açık izni bekliyor.

## 23. Sürüm 1.64.1 test özeti (Hayalet r001 kokpiti)
| Test | Sonuç |
|---|---|
| GLB SHA256 öneki teslimle aynı (b7538903 / 3198e519) | Eşleşti |
| Kaşif → Şahin → Yük → Hayalet döngüsü ×3: doku/geometri sabit (75/128, 54/118, 54/124, 54/118), sayfa hatası yok | PASS |
| Oyun içi görsel kontrol: ekranlar oturuyor, HUD doğru, ortada dikme yok, koltuk büyük | Ekran görüntüsüyle |
Not: swiftshader; gerçek cihaz test edilmedi. Teslimdeki HUD sırtı sağ kenarı düzeltildi (alt kenara kaçan son üç nokta sol kenarın aynasıyla değiştirildi). Altıgen güverte parlak (Asset Factory'nin de bildirdiği 1. sorun).

## 24. Sürüm 1.65.0 test özeti (rozet çizimleri)
| Test | Sonuç |
|---|---|
| kutuk (Başarımlar listesi, 9/30, kademeler) ve ekran görüntüsü: ikonlar kademe rengiyle, kilitliler soluk | PASS |
| offline.json: 30 rozet ve 8 kokpit GLB'si (Hayalet dahil) listede | Doğrulandı |
Not: 1.64.1'deki `offline.json` Hayalet GLB'lerini içermiyordu; bu sürümde düzeltildi. Gerçek cihaz test edilmedi.

## 25. Sürüm 1.65.1 test özeti (Hayalet r003)
| Test | Sonuç |
|---|---|
| GLB SHA256 öneki teslimle aynı (3ce380c2 / 55f4cee1) | Eşleşti |
| Kaşif → Şahin → Yük → Hayalet döngüsü ×3: doku/geometri sabit (71/110, 50/100, 50/106, 50/100), sayfa hatası yok | PASS |
| offline.json: 8 kokpit GLB'si (git add sonrası üretildi) | Doğrulandı |
| Oyun içi görsel: ekranlar büyük ve çerçeveli, HUD doğru, ortada dikme yok | Ekran görüntüsüyle |
Not: swiftshader; gerçek cihaz test edilmedi.

## 26. Sürüm 1.65.2 test özeti (Kaşif ekranları)
| Test | Sonuç |
|---|---|
| Kaşif ekranları %7 büyük: ekran görüntüsüyle önce/sonra karşılaştırıldı, kenarlara taşma yok, sayfa hatası yok | Görsel |
Not: yalnız masaüstü boyutunda görüldü; iPhone yatay boyutunda ve gerçek cihazda ayrıca bakılmadı.

## 27. Sürüm 1.65.3 test özeti (Hayalet r004)
| Test | Sonuç |
|---|---|
| GLB SHA256 öneki teslimle aynı (e7ffaeb3 / 3dfc0848) | Eşleşti |
| Kaşif → Şahin → Yük → Hayalet döngüsü ×3: doku/geometri sabit (77/135, 56/125, 56/131, 56/125), sayfa hatası yok | PASS |
| offline.json: 8 kokpit GLB'si (git add sonrası üretildi) | Doğrulandı |
| Oyun içi görsel: sırt sade, katmanlı konsol, ekranlar bir tık küçük, ekran altı neon oturuyor; direk ve kemer neonları hâlâ kopuk | Ekran görüntüsüyle |
Not: swiftshader; gerçek cihaz test edilmedi.

## 28. Telefon boyutu kokpit kontrolü ve kokpit_dongu testi (1.65.3)
| Kontrol | Sonuç |
|---|---|
| 844×390 yatay boyutunda 4 kokpit (Kaşif, Şahin, Yük, Hayalet): ekranlar yerine oturuyor, HUD sırtı doğru, sayfa hatası yok (`docs/sabah/telefon_boyutu_kokpitler.webp`) | Görsel |
| Yeni test `kokpit_dongu` (4 kokpit ×3 tur, doku/geometri sabit, hata yok) `run.sh` listesinde | PASS |
Not: Kaşif'te canlı ekranlar telefon boyutunda en küçük görünenler (yazılar küçük). Emülasyon; gerçek cihaz test edilmedi.

## 29. Sürüm 1.66.0 test özeti (K50 ölüm bedeli yenilemeyle atlatılamaz)
| Test | Sonuç |
|---|---|
| olum_yenile: gemi parçalanınca kayıtta `dp` = 1; ekran açıkken sayfa yenilenince açılışta 2000 kredi (999999 → 997999), `dp` sıfırlanır | PASS |
| olum_siniri, olum_hesap | PASS |
Not: ölüm ekranında "Canlan"a basıp ödedikten sonra yenilemede ikinci kez alınmaması kod incelemesiyle doğrulandı (`dp = 0` ödeme anında yazılır), otomatik testte ayrıca denenmedi.

## 30. Sürüm 1.66.1 test özeti (veri ayırma)
| Test | Sonuç |
|---|---|
| Ayrılan veri birebir aynı: STSPEC3D, NPCSPEC3D(+patron) ve 20 ses kaydı (karşılaştırma betiği) | Eşit |
| kutuk, bildirim, bulten, derin_sinyal, devriye_akis, kargo_kaydi, ozel_ekonomi, hangar_bellek, bekci, unvan_hata | PASS |
Not: telefon/gerçek cihazda ilk açılış süresi ölçülmedi; iki ek betik dosyası aynı anda indirilir. Çevrimdışı: betikler sürüm adresiyle servis çalışanı tarafından saklanır (değişiklik gerekmedi).
