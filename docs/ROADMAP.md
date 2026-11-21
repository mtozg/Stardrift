# Stardrift — Yol Haritası ve Görev Kaydı

Sahibi: HOD (Head of Development). Proje sahibi: Mehmet.
Son güncelleme: 2026-11-20 · `main` 1.61.0 (a963370) · açık PR #39 (1.62.3: K36, K37, K38; Mehmet kararı bekliyor)

Kararlar için: [DECISIONS.md](DECISIONS.md)

## Çalışma kuralları
1. Her görev ayrı dal ve ayrı PR. PR açıklamasında **değişen dosyalar listesi** zorunlu.
2. Her PR birleşmeden önce QA kontrolünden geçer (PASS/FAIL raporu).
3. Birleştirme kararı Mehmet'te. Ajanlar merge yapmaz, force-push yapmaz.
4. Rütbe, XP ve kredi ekonomisi Mehmet'in açık onayı olmadan değişmez.
5. Aynı dosyada çakışan işler sıralanır. `js/game.js` için birleşme sırası HOD tarafından belirlenir.
6. Sürüm numarası (`index.html`) her PR'da artırılır; önceki PR birleşince dal `main` üzerine güncellenir.

## Ekip (2026-11-20'den itibaren, K16)
| Ajan | Sorumluluk | Çalışma alanı |
|---|---|---|
| Lead Developer (ana oturum) | Proje yönetimi, oyun kodu, hata düzeltme, QA ve regresyon testleri, oyun tasarımı ve denge analizi, dal/PR/sürüm yönetimi, Mehmet'e tek muhatap | `js/`, `index.html`, `sw.js`, `offline.json`, `README.md`, `docs/` |
| Asset Factory | Blender/GLB üretimi, gemi ve kokpit modelleri, optimizasyon, görsel QC; ayrı dal ve PR ile teslim | `tools/asset_factory/`, `models/` |

Pasif (silinmedi, yeni görev yok): Developer, QA Engineer ve Game Designer oturumları. Raporları: [REPORTS.md](REPORTS.md).

## Durumlar
Backlog · Planlandı · Devam · İnceleme · Test · Tamam · Bloke

## Sprint 1
| ID | Görev | Ajan | Öncelik | Bağımlılık | Durum | Beklenen çıktı |
|---|---|---|---|---|---|---|
| S1-01 | PR #28 (Şahin 3B kokpiti 1.54.0) incelemesi | Lead Developer | P1 | — | Tamam: koşullu PASS | QA raporu |
| S1-01b | Filo oyuncusunun Morr'a erişimi | Lead Developer | P0 | — | Tamam: PASS (riskli) | QA raporu |
| S1-02a | PR #28: `__ckb.swap` ekonomi baypası (P1), dropB/PMREM dispose (P2) | Asset Factory | P1 | S1-01 | Tamam (bc5ba4a, QA PASS) | Commit SHA + test sonucu |
| S1-02b | PR #28 doku sızıntısı ölçümü | Asset Factory | P1 | S1-02a | Tamam: kokpit payı Δ=0 | Ölçüm raporu |
| S1-02c | PR #28: main ile birleştirme, index.html sürüm çakışması (1.54.0) | Asset Factory | P1 | PR #30 | Tamam (fd6a7c5) | Merge commit SHA |
| S1-02 | PR #28 birleştirme | Mehmet | P1 | S1-02c; QA Playwright PASS | Tamam (8eef9d7, 1.54.0) | `main` 1.54.0 |
| S1-03 | Bekçi otomatik duraklatma/menü sıfırlaması, hangar `hgSet` dispose, WebGL bağlam temizliği | Lead Developer | P1 | S1-02 | Tamam (PR #32/#33 birleşti) | PR + QA |
| S1-04 | Kayıt sağlamlığı: şema sürümü, zaman damgası birliği, eski bulut anahtarı | Lead Developer | P1 | S1-12 | Tamam (PR #32/#33 birleşti) | PR + QA |
| S1-06 | Ölçüm (K10): üs pasif geliri, yan görev ödülleri, ödül avcısı katlanması | Lead Developer | P1 | — | Tamam: değişiklik gerekmiyor | Ölçüm raporu, kod değişikliği yok |
| S1-07 | Denge analizi (K6–K7): korsan itibarı, gümrük riski, yol taraması, kaçak satış XP | Lead Developer | P2 | — | Tamam (Game Designer) | Ayrı ayrı değerlendirme |
| S1-08 | BUDGET MODE (Asset Factory süreç iyileştirmesi) | Asset Factory | P3 | — | Devam (BUDGET MODE; yeni çalışma kuralı: tek plan, üretim sınırı, kısa rapor) | `tools/asset_factory` değişiklikleri |
| S1-09 | ROADMAP, karar günlüğü, rapor arşivi | Lead Developer | P2 | K11 | Tamam (PR #29) | Bu dosya |
| S1-10 | Kokpit GLB'lerinin offline paketine eklenmesi | Lead Developer | P1 | S1-02 | Tamam (PR #32/#33 birleşti) | PR + QA |
| S1-11 | Morr erişimi: zincir ipucu, ücra kapının görev aktifken haritada işaretlenmesi, Kara Liman ret mesajında çıkış kapısı | Lead Developer | P1 | — | Tamam (PR #32/#33 birleşti) | PR + QA |
| S1-12 | Taraf değiştirme metni "Usta Pilot rütbesi" → "1200 XP" (K8) + README düzeltmesi | Lead Developer | P2 | — | Tamam (PR #30 birleşti, QA PASS) | PR + QA |
| S1-14 | Üste gümrüksüz kaçak satışı doğrulaması | Lead Developer | P1 | — | Tamam: kanıtlı | QA raporu |
| S1-15 | K13: üste kaçak satışı kapatma, kara pazar yalnız Kara Liman ana istasyonu | Lead Developer | P1 | S1-13 | Tamam (PR #32/#33 birleşti) | PR + QA |
| S1-16 | K6, K7a, K7b: Korsan itibarı −50 (+ metin, tek seferlik göç), gümrük %25, tarama %25 | Lead Developer | P2 | S1-11 | Tamam (PR #32/#33 birleşti) | PR + QA |
| S1-17 | K14: kokpit modeli yüklenemezse durum satırı | Lead Developer | P2 | S1-02 | Tamam (PR #32/#33 birleşti) | PR + QA |
| S1-18 | Yük Devi kokpiti PRODUCTION (K15) | Asset Factory | P2 | — | Tamam: Yük Devi r015 oyunda (1.64.0), Kapı 1 Mehmet onaylı | Kapı 2 teslim paketi |
| S1-13 | Kargo kaydı (K9): yenileme/yeniden girişte korunur, kopya kargo/ödül yok | Lead Developer | P1 | S1-12 | Tamam (PR #31) | PR + QA |

### Açık kalanlar (gerçek cihaz bekleyenler aşağıdaki ayrı bölümde)
- Masaüstünde gemi değişmeden "diğer" doku sayısının yavaş artışı (S1-02b gözlemi): çözülmedi, gözlem.
- Bekçi `paused`: yalnız ekran yönünden geliyor, otomatik düzeltme doğru; `__menuOn` sezgisi cihazda gözlenecek.

Lead Developer işleri tek dalda (`claude/stardrift-hod-system-np3akq`) sırayla yürütür; aynı anda tek açık kod PR'ı. Sprint 1 birleşme sırası tamamlandı (PR #28-#33). Kokpit kodu (`CK3`, `__ckb`) yalnızca yeni kokpit entegrasyonu PR'ında değişir.

## Açık PR
| PR | İçerik | Durum |
|---|---|---|
| #40 (1.63.3, K40-K43) | İstasyon bülteni, zincir telsiz sahnesi, hesap açma hatası düzeltmesi, Oyunu sıfırla, test listesi ve onay notları | PR açılacak/açık; Mehmet incelemesi bekliyor |

## Tamamlananlar (main 1.62.3 ve öncesi)
Aşama 1-A/1-B/1-C/1-D (bölgeler, hedef renkleri, devriye çağrısı, rüşvet, taraf unvanları), K13 kaçak kapatma, K9 kargo kaydı, Kadim Bekçi (B-04), Başarımlar (B-05), regresyon seti (B-07), kokpit cam hissi (K29), K36 yeni pano görevleri, K37 Kadim yankı (450-750), K38 ölüm bedeli sınırı 2000 (hepsi Mehmet onaylı, PR #39), unvan görevleri 2. kademe (K32), başlangıç kargosu 16 (K30), kaçak XP (K31), bildirimler (K34), yetenek sıfırlama (B-06: zaten vardı, değişiklik gerekmedi).

## Backlog (onay bekleyen ya da sonraki sprint)
| ID | Konu | Durum |
|---|---|---|
| B-01e | Unvan görevleri 3. ve 4. kademe | Ertelendi (K35): eskort ve patron avı mevcut sistemlerle çakışıyor; çift gelir olmayacak şekilde yeniden tasarım gerekir |
| B-02 | Yük Devi r015 ve Şahin r014 kokpitleri | Tamam: oyunda (1.64.0, PR bekliyor). Resmî Kapı 2 kaydı (`factory.py approve/deliver`) Mehmet'in açık izni bekliyor |
| B-03 | Hayalet kokpiti | r006 oyunda (1.66.2, K52); Kapı 1 Mehmet onayladı; r007 (dikme gerçekçiliği) Asset Factory'de |
| B-05b | Başarım rozet çizimleri (10 rozet × 3 kademe) | Tamam: oyunda (1.65.0, K46); Gezgin ikonu küçükte göz gibi okunuyor (isteğe bağlı düzeltme) |
| B-08 | Firebase kuralları ve kayıt kodu güvenliği | Mehmet'in konsol ekran görüntüsü gerekli |
| B-09 | `game.js` modülerleştirme | 1. adım tamam (1.66.1, K51: veri dosyaları ayrıldı). Mantığın bölünmesi yüksek risk, ayrı onay gerekir |
| B-10 | Game Designer içerikleri | Filo Bülteni (1.63.0) ve zincir telsiz sahnesi (1.63.1) tamam; taşıma/eskort şablonları: mevcut `teslim` görevi ve `eskort` sinyaliyle çakıştığı için önerilmiyor (K35'teki çift gelir sorunu); düşürüldü |
| B-12 | **Tüm oyun içi varlıkların gerçekçi yenilenmesi** (NPC gemileri, istasyonlar, kapılar, gezegenler/evrenler, gökyüzü, asteroit, efektler) | Denetim aşaması (Asset Factory); program: [ASSET_PROGRAMI.md](ASSET_PROGRAMI.md); öncelik onayı Mehmet'te |
| B-11 | Ölüm ekranı açıkken sayfa yenilenirse bedel alınmıyor | Tamam: 1.66.0 (K50, ekonomi, Mehmet onaylı) |

## Gerçek cihaz testleri (iPhone / iPad; henüz yapılmadı)
Liste: [QA_GERCEK_CIHAZ.md](QA_GERCEK_CIHAZ.md). Kapsam: WebGL bağlam sayısı ve hangar↔oyun geçişi, bellek (arka plana atma, 30 sn sonra dönüş), 3B kokpit (Kaşif, Şahin), dokunmatik kontroller (devriye çağrı düğmeleri dahil), iPad 120 Hz hangar animasyonu, 15-30 dk oyun oturumu (ısınma, kare hızı, pil). Test edilmemiş sayılır: bütün performans ve bellek bilgisi swiftshader emülasyonundan.

## Ekonomi kararları
K36, K37 (450-750 kredi korunur) ve K38 (üst sınır 2000) Mehmet tarafından kabul edildi (PR #39, birleşti). Bekleyen ekonomi kararı yok.
