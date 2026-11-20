# Aşama 1-C: Devriye karar mantığı (tasarım notu)

Durum: **onaylandı (K20) ve 1.56.0'da uygulandı.** Rüşvet bedeli: `max(150, kaçak × 45 + aranma × 120)` kredi, yalnız Korsan. Çağrılar arasında 30 sn bekleme var (art arda aranma artışını önler). Klavye kısayolu eklenmedi (Q/E yuvarlanmada kullanılıyor); çağrı düğmelerle yanıtlanır.
Dayanak: Developer'ın Aşama 1 önerisi (K12), Game Designer'ın S1-07 analizi, 1.55.0'da gelen bölge tablosu (Aşama 1-A) ve hedef renkleri (Aşama 1-B).

## Sorun
Bugün devriyelerin iki hâli var: görmezden gelmek ya da ateş açmak.
- Filo itibarı −60'ın altına inince devriye 900 m içinde doğrudan saldırıyor.
- Aranma ★3 ve üstünde de doğrudan saldırıyor.
- Arada uyarı, durdurma ya da teslim olma yok. Korsan ve aranan oyuncu için devriye bir bilmece değil, düz bir tehlike.

## Önerilen akış
```
TESPİT ─► ÇAĞRI ─┬─► (uyar) TARAMA ─┬─► temiz: serbest
                 │                   └─► kaçak var: el koyma + ceza (bugünkü kural)
                 ├─► (kaç) TAKİP ─► 20 sn içinde 1,5 km açılırsa kurtulur; yoksa SALDIRI
                 └─► (ateş et) SALDIRI + aranma +1, çevredeki devriyeler katılır
```

| Aşama | Ne olur | Süre |
|---|---|---|
| Tespit | Devriye 900 m içinde oyuncuyu fark eder (bugünkü mesafe) | — |
| Çağrı | Telsiz: "Motorunu kes, tarama yapacağız." Ekranda iki seçenek: **Uy** / **Kaç** | 8 sn karar süresi |
| Tarama | Oyuncu yavaşlarsa (hız < 40) bugünkü %30 / %25 / %20 tarama kuralı uygulanır | 3 sn |
| Takip | Oyuncu hızlanırsa devriye peşine düşer, aranma +1 | En çok 20 sn |
| Saldırı | Bugünkü saldırı davranışı | — |

## Kimler çağrılır, kimler doğrudan saldırıya uğrar
| Durum | Güvenli bölge (Ankora) | Çekişmeli (Kızıl, Buzul) | Kanunsuz (Zümrüt) | Lonca / Korsan bölgesi |
|---|---|---|---|---|
| Temiz pilot | Yok | Yok | Yok | Yok |
| Kaçak taşıyan | Çağrı | %50 çağrı | Yok | Yok |
| Aranma ★1-2 | Çağrı | Çağrı | Yok | Yok |
| Aranma ★3+ | Saldırı | Çağrı, uymazsa saldırı | Saldırı | Yok |
| Filo itibarı ≤ −60 | Saldırı | Çağrı | Saldırı | Yok |

Kanunsuz bölgede devriye azdır ve konuşmaz. Lonca ve Korsan bölgelerinde Filo devriyesi yoktur (bugünkü durum).

## Diğer davranışlar (aynı paket)
- **Tüccar kaçışı:** Korsan oyuncu 600 m'ye girince kargo ve tanker gemileri hızlanıp en yakın istasyona kaçar. Bugün yerinde duruyorlar.
- **Korsan dostluğu:** Korsan itibarı ≥ 60 olan oyuncuya korsan NPC'ler selam verir. Patronlar ve "rakip çete" olarak işaretlenen gemiler istisnadır.

## Ekonomi etkisi (onay gerektirenler)
| Madde | Etki | Öneri |
|---|---|---|
| **Rüşvet** (Developer önerisi): Korsan oyuncu taramadan önce kredi verip kurtulabilir | **Yeni kredi harcaması.** Fiyat onay ister | İlk sürümde **yok**; sonra ayrı karar |
| Tarama oranları | Değişmiyor (K7b ile %30 / %25 / %20) | — |
| El koyma ve ceza | Değişmiyor (birim başına 60 kredi, aranma +1) | — |
| Kaçınca aranma +1 | Mevcut aranma sistemi; yeni ödül ya da ceza değeri yok | Kabul |

## Uygulama planı
1. `patrolAI` içinde yeni durumlar (`hail`, `scan`, `chase`) ve 8 sn karar penceresi. Mevcut `attack` aynen kalır.
2. Çağrı arayüzü: mevcut `gateAsk` kalıbıyla iki düğme (Uy / Kaç), klavyede E / Q.
3. Bölge tablosu (`ZONE`) ve yukarıdaki karar tablosu tek bir `patrolDecide(n)` fonksiyonunda.
4. Tüccar kaçışı: `trader` rolüne `flee` durumu.
5. Test: her bölge × durum kombinasyonu için Playwright senaryosu, korsan / filo / lonca kayıtlarıyla.

Tahmini iş: 1 PR, `js/game.js` içinde yaklaşık 120-180 satır.

## Riskler
- Devriye "konuşan" bir sisteme dönüşünce savaş müziği ve tehdit sayacı da bu durumlara göre ayarlanmalı.
- 8 sn karar penceresi dokunmatik ekranda oyunu durdurmamalı; çağrı sırasında oyun akmaya devam eder.
- Bugün ★3 aranan oyuncuya doğrudan saldırı bekleyen oyuncular için davranış değişir. Önce Ankora'da sert, uzak bölgelerde yumuşak kalması bu yüzden önerildi.

## Mehmet'ten istenen kararlar
1. Akış ve bölge tablosu bu hâliyle uygun mu?
2. Rüşvet ilk sürüme girsin mi? Girerse fiyat ne olsun?
3. Tüccar kaçışı ve korsan dostluğu aynı pakette mi, ayrı mı?
