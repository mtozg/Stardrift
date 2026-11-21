# Oyun sonu: iki yön ve karşılaştırma (TASARIM, kod yok)

**Durum:** tasarım. Hiçbir şey kodlanmadı; kayıt şeması ve ekonomi değişikliği içeren her adım ayrıca onaya sunulur. Mevcut kayıtlar hiçbir koşulda silinmez ya da sıfırlanmaz.

## Bugünkü "son" (koddan)
Rütbe: Çaylak → … → **Efsane** (18.620 XP), seviye 30 üst sınır (32.420 XP). Unvan: taraf başına 4 kademe (zincir 6 adım). Başarımlar (Bronz/Gümüş/Altın rozetler), **Kapı Bekçisi** bir kez yenilir (`save.bekci`), Kadim yankılar (16), üs 3 seviye, 6 sistem. Efsane + seviye 30 + tüm unvanlar sonrası yeni hedef yok; geç oyunda kredi fazlası (H1, ölçülecek) ve ayrı bir "devam etme nedeni" eksik.

## E1: Kozmetik ve prestij (hafif)
**Ne verir:** Kadim Atlas (keşfedilen kalıntı ve sistemlerin kayıt defteri; yalnız görüntü), **Bekçi Bronz/Gümüş/Altın** (Bekçi'yi tekrar yenme zorlukları; rozet), benzersiz ünvan satırları (ör. taraf ve rozet kombinasyonları), **Efsane+** (Efsane sonrası kozmetik kademe, XP eşikleri yalnız sayaç), istatistik paneli (toplam kazanç, düşürülen gemi, kat edilen mesafe).
**Kayıt:** yeni isteğe bağlı alanlar (örn. `save.pr` nesnesi); yoksa varsayılan; eski kayıt etkilenmez; şema sürümü artırmak gerekmeyebilir (eksik alan = 0).
**Ekonomi:** etkisi yok (ödül yok ya da yalnız kozmetik).
**Maliyet:** düşük-orta (arayüz + sayaçlar + rozet görselleri; görseller Asset Factory kalemi).
**Risk:** düşük. Tekrar oynama nedeni sınırlı (yalnız koleksiyon).

## E2: Yeni Döngü (New Game+)
**Ne olur:** Oyuncu Efsane'ye ulaşınca isteğe bağlı "Yeni Döngü" başlatır.
- **Sıfırlanır:** kredi (bir kısmı korunur), cevher/kargo, üs seviyesi, açık sistemler (yeniden açılır), görev zincirleri, aranma.
- **Kalır:** rütbe adı/rozetler, başarımlar, kozmetik, gemiler (dönem başında seçilir), yetenek puanlarının bir kısmı, Kadim Atlas kayıtları.
- **Zorluk:** düşman hasar/dayanıklılık ×1,25 her döngüde (üst sınır ×2), tehdit artışı.
- **Ödül çarpanı:** kredi ve XP ×1,2 / döngü (üst sınır ×2); bu **ekonomi değişikliğidir**, önce/sonra tablosu ve test gerektirir.
**Kayıt:** `save.cycle` (sayı, 0 varsayılan) + döngü başında korunacak alanların yedeği. **Şema değişikliği** sayılır: Mehmet onayı şart. Geri alma: döngüye girmeden önce otomatik yedek (`save` kopyası) ve "önceki döngüye dön" yolu.
**Ekonomi etkisi:** orta-yüksek (çarpanlar, sıfırlanan kredi/üs, geç oyun fazlası H1 ile etkileşir); 3 profil (P1 yeni, P2 orta, P3 geç) için süre başına kazanç ölçümü gerekir.
**Maliyet:** yüksek (sıfırlama mantığı, yedek/geri alma, denge, çok sayıda test, arayüz).
**Risk:** **yüksek**: yanlış sıfırlama oyuncu emeğini siler. Her adım yedekle başlamalı, testle doğrulanmalı.

## Karşılaştırma
| | E1 Kozmetik/prestij | E2 Yeni Döngü |
|---|---|---|
| Tekrar oynama değeri | Düşük-orta | Yüksek |
| Kayıt riski | Çok düşük | Yüksek (sıfırlama) |
| Ekonomi etkisi | Yok | Orta-yüksek |
| Maliyet | Düşük-orta | Yüksek |
| Asset ihtiyacı | Rozet görselleri | Az (kozmetik ek) |
| Geri alınabilirlik | Kolay | Yedek şart |

## Önerilen sıra (karar Mehmet'te)
1. **E1'i önce yap:** düşük risk, hemen değer (Atlas, Bekçi rozetleri, istatistik paneli, Efsane+). Ekonomi ve şema değişmez.
2. **E2'yi E1'in verisiyle tasarla:** ekonomi ölçümleri (H1, süre başına kazanç) bitince sayılar netleşir; Yeni Döngü yedekli ve kademeli (önce yalnız "isteğe bağlı, geri alınabilir" sürüm).
3. Her adım ayrı PR, eski kayıt yükleme testi zorunlu.

## Test planı (E2 için, kodlanmadan önce)
Eski kaydı yükle → döngüye gir → yedek var mı → döngü içi ekonomi tablosu (before/after) → "önceki döngüye dön" → kayıt değişmedi mi → hata yok.
