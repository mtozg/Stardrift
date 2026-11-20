# Taraf unvanıyla açılan özel görevler (tasarım notu)

Durum: **öneri, Mehmet'in kararını bekliyor.** Kod yazılmadı.
Dayanak: Aşama 1-D (taraf unvanları, 1.59.0) ve Game Designer'ın "taraflar gerçekten farklı oynanmalı" bulgusu.

## Amaç
Unvanlar şu an yalnızca bir yazı. Unvan yükseldikçe oyuncunun tarafına özgü yeni bir görev türü açılsın; böylece taraf zincirinde ilerlemenin oyun içi karşılığı olsun.

## Ekonomiyi koruma kuralı (önerim)
- Özel görev, panodaki üç tekliften **birinin yerine** geçer (Lonca'nın acil siparişinin bugün yaptığı gibi). Panodaki teklif sayısı artmaz.
- Ödül hesabı **mevcut formüllerle aynı**: `av` 110 × n × tehlike; `teslim` 60 + n × fiyat × 0,45-0,7; `kaya` 9 × n; `ziyaret` 160; `kalıntı` 450. Yeni kredi ya da XP değeri yok.
- Özel görevin farkı ödülü değil **türü ve hedefidir** (daha özel, daha çeşitli).
- Aynı anda en fazla 2 aktif görev kuralı aynen geçerli.

## Kademeler
| Taraf | 2. unvan (zincir 2+ adım) | 3. unvan (zincir 4+ adım) | 4. unvan (zincir 6 adım) |
|---|---|---|---|
| **Filo** (Devriye Subayı, Operasyon Lideri, Filo Komutanı) | **Kuşak devriyesi:** belirli bir kuşakta N korsan düşür (`av` ödülü) | **Eskort:** bir kargo gemisini istasyona 3 km korumak (mevcut eskort sinyalinin görev hâli; `teslim` ödülü) | **Patron avı:** bir korsan reisini yen (mevcut patron ödülü zaten var; ek ödül yok, yalnız rozet ve itibar) |
| **Lonca** (Pazar Ustası, Sözleşme Lideri, Ticaret Lideri) | **Toplu sipariş:** tek istasyona 2 cevher türünden teslimat (`teslim` ödülü) | **Fiyat avı:** en pahalı istasyona belirli cevher teslimi (`teslim` ödülü) | **Kaçak karşıtı sevk:** aranma olmadan teslim; yakalanırsan görev düşer (ödül aynı) |
| **Korsan** (Akıncı, Çete Reisi, Korsan Lordu) | **Pusu:** belirli bir kuşakta N kargo gemisi düşür (`av` ödülü, Korsan'da kargo av) | **Kaçak sevkiyat:** gizli bölmedeki malı Kara Liman dışında bir istasyona sat (mevcut 150 kredi fiyatı, gümrük riski aynı) | **Ödül avcısı avı:** bir Filo avcısını düşür (mevcut ödül aralığı) |

## Neden bu kadar
- Üç taraf için aynı iskelet: her kademede bir görev türü. Toplam 9 yeni görev şablonu, hepsi mevcut sayaçlarla ölçülür (`save.st.kill/avci/sell/kacak/sip`, `save.boss`).
- Yeni sayaç, yeni kayıt alanı ya da yeni ekonomi değeri gerektirmez.

## Etki ve risk
| Madde | Etki |
|---|---|
| Kredi ve XP | **Değişmez** (mevcut formüller; teklif sayısı sabit) |
| Oyuncu deneyimi | Taraf zinciri ilerledikçe panoda tarafa özgü hedefler çıkar |
| Kod | `js/game.js` içinde `ctGen` sarmalayıcısı (Lonca ve Korsan için zaten iki örnek var); yaklaşık 80-120 satır |
| Test | Her taraf × kademe için şablon üretimi ve ilerleme sayacı (Playwright, mevcut `kargo_kaydi` kalıbı) |
| Risk | "Eskort" ve "Kaçak sevkiyat" mevcut sinyal ve gümrük sistemine bağlanır; ilk sürümde en basit üçünü (kuşak devriyesi, toplu sipariş, pusu) yapıp kalanını sonraya bırakmak daha güvenli |

## Önerilen uygulama
1. **İlk sürüm:** 2. kademeler (kuşak devriyesi, toplu sipariş, pusu). Düşük risk.
2. **İkinci sürüm:** 3. ve 4. kademeler.

## Mehmet'ten istenen karar
1. Bu yaklaşım (teklif yerine geçen özel görev, mevcut ödül formülleri) uygun mu?
2. İlk sürümde yalnız 2. kademeler mi, hepsi mi?
