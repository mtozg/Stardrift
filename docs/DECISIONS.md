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

## Önceden geçerli olan kurallar
- Rütbeler: Çaylak 0 · Pilot 970 · Usta Pilot 2790 · Kaptan 5830 · Komodor 10780 · Efsane 18620 XP (`js/game.js` RANKS). Mehmet onayı olmadan değişmez.
- Kapı ücretleri 250 / 600 / 1200 kredi; taraf değiştirme 1200 XP + 4000 kredi + Dost itibar. Mehmet onayı olmadan değişmez.
- Asset Factory BUDGET MODE planı Mehmet tarafından onaylandı (Asset Factory'nin bildirimi).
