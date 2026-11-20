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

## Önceden geçerli olan kurallar
- Rütbeler: Çaylak 0 · Pilot 970 · Usta Pilot 2790 · Kaptan 5830 · Komodor 10780 · Efsane 18620 XP (`js/game.js` RANKS). Mehmet onayı olmadan değişmez.
- Kapı ücretleri 250 / 600 / 1200 kredi; taraf değiştirme 1200 XP + 4000 kredi + Dost itibar. Mehmet onayı olmadan değişmez.
- Asset Factory BUDGET MODE planı Mehmet tarafından onaylandı (Asset Factory'nin bildirimi).
