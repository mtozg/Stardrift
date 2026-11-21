# Tier 3–4 unvan görevleri: tasarım (A modeli) — KOD YOK

**Durum:** tasarım ve test senaryoları. Kodlama bu belgeye ve Mehmet'in onayına bağlı değil ama değişiklik küçük adımlarla ve ayrı PR'larla yapılacak.
**Bağlam (koddan):** unvan = taraf zincirinde tamamlanan adım sayısı (`save.lq[taraf]`, 0–6). `__unvanN`: 0 (adım 0–1) · 1 (≥2) · 2 (≥4) · 3 (≥6). Bugün yalnız **1. kademe** (unvanN ≥ 1) panodaki 2. teklifin yerine geçen özel görev getiriyor: Filo "Uzak devriye", Korsan "Pusu", Lonca "Toplu sipariş" (ödül formülleri mevcutlarla aynı, yeni değer yok). **Tier 3 = unvanN 2, Tier 4 = unvanN 3.**

## A modeli: ilke
- Görev, **zaten olan bir olayı sayar** (düşman düşürme, eskort, teslimat, patron). Olayın kendi kredi/XP'si aynen kalır.
- Görevin **kendisi kredi ya da XP vermez.** Ek ödül yalnızca: itibar (`save.fac`), unvan ilerlemesi (`save.lq`) ve kozmetik (rozet, ünvan satırı).
- Böylece K35'teki "aynı olaydan iki kez gelir" hatası yapısal olarak olamaz: görev ödemesi yok, yalnız sayaç ve itibar var.

## Öneri: olaylar
| Taraf | Tier 3 (unvanN 2) | Tier 4 (unvanN 3) |
|---|---|---|
| **Filo** | **Eskort zinciri:** 3 mürettebat eskortu tamamla (mevcut eskort olayı) | **Patron avı:** 2 farklı korsan reisini yen (`save.boss` farklı sayısı) |
| **Lonca** | **Fiyat avı:** 3 farklı istasyonda en iyi fiyattan sat (mevcut fiyat karşılaştırma verisi) | **Aranmasız sevk:** aranma yok (`save.wanted == 0`) iken 2 teslimat ve 1 acil sipariş |
| **Korsan** | **Kaçak sevkiyat:** 20 birim kaçak mal sat (`save.st.kacak`) | **Ödül avcısı avı:** 3 Filo avcısı (`hunter`) düşür |

Her görev: sayaç (mevcut `save.st.*` ya da `save.ct` alanı), **ödül = itibar +4..+8** ve unvan adımı için `lq` ilerlemesi. Ekranda: panoda ilerleme çubuğu, tamamlanınca bildirim (mevcut `kzSay` kanalı).

## Kayıt uyumluluğu
Yeni alan yok: görev `save.ct.offers` içinde bugünkü `type:'ozel'` yapısıyla durur; yalnız `kademe` etiketi eklenir. Eski kayıtta alan yoksa Tier 1 davranışı aynen sürer. Şema (`save.sv`) değişmez; **kayıt şeması değişikliği gerekmez**, gerekirse ayrıca onay istenir.

## Test senaryoları (yazılacak)
1. unvanN 2'de Filo: eskort 3 kez tamamlanınca görev ilerler, **kredi/XP tam eskort olayının değeri kadar** artar (ikinci ödeme yok): `__ledger` farkı ölçümü.
2. Aynı olay iki kez sayılmaz (tek eskort = tek ilerleme).
3. unvanN 1'e düşen/eski kayıtta Tier 3 görevi **çıkmaz**; Tier 1 aynen çalışır.
4. Korsan: kaçak satışı 20 birimde tamamlanır, kredi yalnız satış kadar (K35 çifte gelir yok).
5. Lonca: aranma varken "aranmasız sevk" ilerlemez.
6. Eski kayıt yükle: hata yok, `save.ct` bozulmaz.
7. Ekonomi testleri (`ozel_ekonomi`, `olum_hesap`) değişmeden geçer.

## Riskler
- Sayaç kaynakları (eskort, fiyat karşılaştırma) koddan tek tek doğrulanmalı; tabloda adı geçen olaylardan biri bugün sayılmıyorsa o olay için sayaç eklemek gerekir (küçük, ama kayıt alanı sayılır → onay).
- Görev çok kolay olursa unvan ilerlemesi hızlanır: sayılar ölçümle (süre başına olay) ayarlanacak.

## Sonraki adım
Sayaç kaynaklarını doğrula, sonra Tier 3 (3 taraf) kodla, ardından Tier 4; her biri ayrı PR ve test.
