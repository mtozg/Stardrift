# Stardrift — Karar Günlüğü

Kararlar Mehmet (proje sahibi) tarafından verilir. HOD kaydeder ve ilgili ajanlara iletir.
Biçim: ID · tarih · karar · kapsam · etkilenen ajan.

## 2026-11-20

| ID | Karar | Kapsam / kısıt | Ajan |
|---|---|---|---|
| K3 | Yük Devi PREVIEW r007 görsel onayı geçerli. | PRODUCTION'a başlanmaz; tam modelleme için ayrı onay gerekir. | Asset Factory |
| K5 | PR #28 henüz birleştirilmeyecek. | S1-02a düzeltmeleri, QA PASS raporu ve gerçek iPhone/iPad testi beklenir. | Asset Factory, QA |
| K6–K7 | Korsan itibarı, gümrük riski, yol taraması ve kaçak satış XP önerileri için Game Designer denge analizi yapacak. | Her biri ayrı değerlendirilir. Kod değişmez. Uygulama kararı sonra. | Game Designer |
| K8 | Taraf değiştirme ekranındaki "Usta Pilot rütbesi" ifadesi "1200 XP" olacak. README'deki yanlış ifade de düzeltilebilir. | Gereken XP miktarı (1200) değişmez. | Developer |
| K9 | Kargo kaydedilecek. | Sayfa yenilenince ya da oyuna yeniden girilince kargo korunur. Kopya kargo veya ödül oluşmaz. | Developer, QA |
| K10 | Üs pasif geliri ve yan görev ödülleri yalnızca ölçülecek. | Hiçbir ekonomi değişikliği yapılmaz. | Developer, Game Designer |
| K11 | `docs/ROADMAP.md` ve karar günlüğü oluşturulacak. | — | HOD |
| K12 | Developer Aşama 1 planına genel onay verilmedi. | Bölge tablosu, hedef renkleri ve devriye karar mantığı ayrı ayrı incelenecek. | Developer |
| M-1 | QA'nın Morr erişimi için üç iyileştirmesi Developer'a görev olarak verilir. | Ekonomi değişmez. | Developer, QA |
| M-2 | QA'nın Playwright tarayıcı testleri için komut izni Mehmet tarafından onaylanacak. | İzin istendiğinde. | QA |
| G-1 | Tüm görevlerde ayrı dal/PR, QA kontrolü ve değişen dosyalar listesi zorunlu. | Rütbe, XP ve kredi ekonomisi izinsiz değişmez. | Tüm ekip |

## 2026-11-20 (2)

Mehmet: "Hepsi önerin gibi. Yük Devi tam modelleme başlasın."

| ID | Karar | Kapsam / kısıt | Ajan |
|---|---|---|---|
| K5b | PR #28 Mehmet'in gerçek telefon/tablet denemesinden sonra birleştirilecek. | QA PASS (bc5ba4a), doku ölçümü Δ=0. | Mehmet |
| K6 | Korsan başlangıç Filo itibarı −65 → **−50**. | Seçim ekranındaki dezavantaj metni güncellenir. Mevcut kayıtlara tek seferlik göç: yalnız Korsan, devriye/avcı düşürmemiş (save.st.avci === 0), aranmayan (wanted 0), Filo itibarı −50'nin altında; bayrakla bir kez. Taraf değiştirmedeki −65 ihanet bedeli korunur. | Developer |
| K7a | Gümrük riski Korsan için %40 → **%25**. | Filo %40'ta kalır, Lonca %25. | Developer |
| K7b | Yol taraması riski Korsan için %30 → **%25**. | Lonca %20 kalır. | Developer |
| K7c | Kaçak satışından XP **ertelendi**. | K13 düzeltilip QA'dan geçtikten sonra yeniden karar. | — |
| K13 | Oyuncu üssünde kaçak satışı **kapatılır**; kara pazar (alım, kayıt sildirme) yalnız Kara Liman ana istasyonunda çalışır. | Fiyat, ceza ve ödül değerleri değişmez. | Developer, QA |
| K14 | Kokpit modeli kalıcı olarak yüklenemezse oyuncuya durum bilgisi gösterilir (Ayarlar veya tanı paneli satırı). | Sessiz yeniden deneme sürer; çizim kokpitine dönüş yok. PR #28 birleştikten sonra. | Developer |
| K15 | Yük Devi kokpiti **PRODUCTION başlasın**. | Kapı 2 (teknik) ve Kapı 3 (entegrasyon) onayları ayrıca alınır. | Asset Factory |
| G-2 | Developer oturumu yalnız `claude/bold-bardeen-oqf73o` dalına push edebiliyor: işler bu dalda sırayla, aynı anda tek açık PR, her PR birleşince dal `main`'den tazelenir. | G-1 kuralının uyarlaması. | Developer |

## 2026-11-20 (3) — Ekip yapısı

| ID | Karar | Kapsam / kısıt | Ajan |
|---|---|---|---|
| K16 | Aktif ekip 2 ajan: **Lead Developer** (HOD + Developer + QA + Game Design, ana oturum) ve **Asset Factory** (bağımsız 3D uzmanı). | QA Engineer, Game Designer ve Developer oturumlarına yeni görev atanmaz; oturumlar silinmez (Mehmet'in son onayına kadar). Açık PR, dal ve dosya silinmez. Gereksiz paralel oturum açılmaz; işler ana oturumda sırayla yürür. Rütbe, XP ve kredi onay kuralları aynen geçerli. | Tümü |

## 2026-11-20 (4)

| ID | Karar | Kapsam / kısıt | Ajan |
|---|---|---|---|
| K17 | PR'ları Lead Developer açar, **Mehmet elle birleştirir**. | Lead Developer hiçbir PR'ı birleştirmez. | Lead Developer |
| K18 | Pasif oturumlar (Developer, QA Engineer, Game Designer) **silinmeyecek**. | Yeni görev yok. | — |
| K19 | Asset Factory'nin Yük Devi Kapı 1 kayıt komutuna izin verildi. | Kayıt geçti (r007 visual_approved); PRODUCTION başladı. | Asset Factory |
| K12b | Aşama 1: **A bölge tablosu ve B hedef renkleri onaylandı.** C devriye karar mantığı için önce tasarım notu hazırlanacak, karar Mehmet'te. D taraf unvanları C'den sonra planlanacak. | Rütbe, XP ve kredi değerleri değişmez. | Lead Developer |

## 2026-11-20 (5)

| ID | Karar | Kapsam / kısıt | Ajan |
|---|---|---|---|
| K20 | **Aşama 1-C onaylandı:** devriye akışı (tespit → çağrı → uy/kaç → tarama ya da takip → saldırı) ve bölge tablosu tasarım notundaki gibi. **Rüşvet** girsin; ücreti Lead Developer ekonomiye uygun belirler. **Tüccar kaçışı** ve korsan selamı aynı pakette. | Rüşvet: yalnız Korsan, `max(150, kaçak × 45 + aranma × 120)` kredi. Kaçak yakalanma kaybına (mal + birim başı 60 ceza + aranma) yakın, taramadan biraz ucuz. Tarama oranları, el koyma ve ceza değişmez. | Lead Developer |
| K21 | Yük Devi r008 beğenildi; **Kapı 2 henüz onaylanmadı**: sağ ve sol dikmeler inceltilecek. | Diğer her şey aynı. | Asset Factory |
| — | PR #32 yalnız ilk commit'le (K13) birleşti; kalan 8 commit PR #33'e taşındı. | — | Lead Developer |

## 2026-11-20 (6)

| ID | Karar | Kapsam / kısıt | Ajan |
|---|---|---|---|
| K22 | Yük Devi r009: Kapı 2 (teknik) onayı verilmişti, ama oyunda **görsel olarak Şahin'in çok gerisinde** (düz yüzeyler, detay ve malzeme yok) bulundu. Oyuna eklenme geri alındı; **r010 revizyonu** (panel derzi, bulon, uyarı şeritleri, 3-4 malzeme, anahtar blokları) istendi. | Dikme inceltmesi aynen kalır. Görsel onay yeniden Mehmet'te. | Asset Factory |
| K23 | Kokpit siluet QC ölçütü 1 px toleranslı yapıldı; eşik Kaşif, Şahin, Yük Devi ölçümleriyle kalibre (FAIL > %0,4, WARN > %0,25). Eski ölçüt raporda bilgi olarak duruyor. | Ölçüm artefaktı düzeltmesi; kalite eşiği düşürülmedi. | Asset Factory |
| K24 | Model politikası: varsayılan Sonnet; Opus yalnız Mehmet onayıyla. **PR "hazır" denince birleştirilir; hazır denen PR'a commit eklenmez.** **Bir model oyuna girmeden önce Kaşif ve Şahin ile yan yana ekran görüntüsüne bakılır ve Mehmet'e gösterilir** (yalnız ölçüm yetmez). | — | Tüm ekip |
| K25 | **Sprint 2 başladı.** Ana görev Bölüm 6'ya yeni son adım: **Kadim Kapı'nın Bekçisi** (Ankora). Ödül yalnızca rozet; kredi, XP, parça yok. Mevcut öldürme ödülü (normal düşman bounty'si) geçerli. `save.boss`'a yazılmaz, ayrı bayrak `save.bekci`. Korsan dahil herkese düşman. | Ekonomi değerleri değişmedi. | Lead Developer |

## 2026-11-20 (7)

| ID | Karar | Kapsam / kısıt | Ajan |
|---|---|---|---|
| K26 | **Ana görsel referans artık Kaşif** (oyun içi onaylı 3B kokpit). Yük Devi r012 ve **Şahin r013** (yeni revizyon) Kaşif düzeyine çekilecek: pişirilmiş AO, kir, aşınma, derin panel yüzeyi. | Şahin r012 donmuş ve oyunda; r013 ayrı aday, Mehmet'in görsel onayına kadar oyundaki dosyalara dokunulmaz. Yük Devi r010 ve r011 görsel olarak reddedildi. | Asset Factory |
| K27 | Kokpit **cam denemesi**: Şahin kopyasında 3 varyant (camsız, hafif, belirgin), yalnız görsel kıyas. | Oyuna girmez; beğenilirse yayma ayrı onay. | Asset Factory |

## 2026-11-20 (8)

| ID | Karar | Kapsam / kısıt | Ajan |
|---|---|---|---|
| K28 | Sprint 3 başladı (Lead Developer, onay gerektirmeyen işler): **Aşama 1-D taraf unvanları** (zincir ilerlemesinden türetilir, ekonomi yok), hangar animasyonu kare hızından bağımsız (120 Hz hatası), oyuncuya ham hata metni yerine sade uyarı (ayrıntı yalnız `?tani=1` ve test kaydında), yaklaşma yazısı 3B kokpitte üst orta kısma taşındı. | Rütbe, XP, kredi değişmedi. | Lead Developer |

| K29 | Kokpit **cam hissi oyun tarafında** (Mehmet: "yeterli"): pencere alanında hafif soğuk pus perdesi + güneşe bakınca ışıma; varsayılan açık, `?cam=0` ile kapanır. Asset Factory'nin model içi cam yüzeyi denemesi (K27) kapatıldı: referansın yaptığı şey yüzey değil, atmosfer. | Kokpit modellerine dokunmaz, tüm gemilere uygulanır, ek çizim çağrısı yok. | Lead Developer |

## 2026-11-20 (9) — "Evet, ayarla": ekonomi ve unvan görevleri

Mehmet: "Evet ayarla, sonra da diğer işlere devam et." Değerler Lead Developer tarafından belirlendi; itiraz edilirse geri alınır.

| ID | Karar | Değer / kısıt | Ajan |
|---|---|---|---|
| K30 | **Başlangıç kargosu 12 → 16** (Game Designer önerisi 16-18; alt uç seçildi). | Gemi katsayısıyla çarpılır: Kaşif 16, Şahin 11, Yük Devi 32, Hayalet 19. Yetenek ve mürettebat eklemeleri aynı. Sefer geliri yaklaşık +%33 (erken oyun). | Lead Developer |
| K31 | **Kaçak satışından XP: birim başına 5** (Designer önerisi 6; biraz kısıldı). | Yalnız gümrüklü istasyonda satışta (üste satış zaten kapalı). Saatte yaklaşık 450-560 XP; yalnız kaçakla Usta Pilot yaklaşık 5-6 saat. Rütbe eşikleri değişmedi. | Lead Developer |
| K32 | **Unvanla açılan özel görevler, 2. kademe**: Filo "Uzak devriye", Korsan "Pusu" (istasyondan 3 km ötede N düşman), Lonca "Toplu sipariş" (28-40 birim). 3. ve 4. kademe sonra. | Panodaki ikinci teklifin yerine geçer; ödül formülleri mevcutlarla aynı; yeni değer yok. | Lead Developer |
| — | **Yetenek sıfırlama zaten var** (300 kredi + harcanan puan başına 100). Game Designer'ın "sıfırlama yok" bulgusu yanlıştı; yeni iş yok. | — | — |

## Önceden geçerli olan kurallar
- Rütbeler: Çaylak 0 · Pilot 970 · Usta Pilot 2790 · Kaptan 5830 · Komodor 10780 · Efsane 18620 XP (`js/game.js` RANKS). Mehmet onayı olmadan değişmez.
- Kapı ücretleri 250 / 600 / 1200 kredi; taraf değiştirme 1200 XP + 4000 kredi + Dost itibar. Mehmet onayı olmadan değişmez.
- Asset Factory BUDGET MODE planı Mehmet tarafından onaylandı (Asset Factory'nin bildirimi).
