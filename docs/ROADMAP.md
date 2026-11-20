# Stardrift — Yol Haritası ve Görev Kaydı

Sahibi: HOD (Head of Development). Proje sahibi: Mehmet.
Son güncelleme: 2026-11-20 · Temel sürüm: `main` 1.53.1 (bdda9b9)

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
| S1-03 | Bekçi otomatik duraklatma/menü sıfırlaması, hangar `hgSet` dispose, WebGL bağlam temizliği | Lead Developer | P1 | S1-02 | Backlog | PR + QA |
| S1-04 | Kayıt sağlamlığı: şema sürümü, zaman damgası birliği, eski bulut anahtarı | Lead Developer | P1 | S1-12 | Backlog | PR + QA |
| S1-06 | Ölçüm (K10): üs pasif geliri, yan görev ödülleri, ödül avcısı katlanması | Lead Developer | P1 | — | Tamam: değişiklik gerekmiyor | Ölçüm raporu, kod değişikliği yok |
| S1-07 | Denge analizi (K6–K7): korsan itibarı, gümrük riski, yol taraması, kaçak satış XP | Lead Developer | P2 | — | Tamam (Game Designer) | Ayrı ayrı değerlendirme |
| S1-08 | BUDGET MODE (Asset Factory süreç iyileştirmesi) | Asset Factory | P3 | — | Devam (53dfdf6 PR #28 içinde; sonrası `claude/asset-factory-budget-mode`) | `tools/asset_factory` değişiklikleri |
| S1-09 | ROADMAP, karar günlüğü, rapor arşivi | Lead Developer | P2 | K11 | Tamam (PR #29) | Bu dosya |
| S1-10 | Kokpit GLB'lerinin offline paketine eklenmesi | Lead Developer | P1 | S1-02 | Backlog | PR + QA |
| S1-11 | Morr erişimi: zincir ipucu, ücra kapının görev aktifken haritada işaretlenmesi, Kara Liman ret mesajında çıkış kapısı | Lead Developer | P1 | — | Planlandı | PR + QA |
| S1-12 | Taraf değiştirme metni "Usta Pilot rütbesi" → "1200 XP" (K8) + README düzeltmesi | Lead Developer | P2 | — | Tamam (PR #30 birleşti, QA PASS) | PR + QA |
| S1-14 | Üste gümrüksüz kaçak satışı doğrulaması | Lead Developer | P1 | — | Tamam: kanıtlı | QA raporu |
| S1-15 | K13: üste kaçak satışı kapatma, kara pazar yalnız Kara Liman ana istasyonu | Lead Developer | P1 | S1-13 | Planlandı | PR + QA |
| S1-16 | K6, K7a, K7b: Korsan itibarı −50 (+ metin, tek seferlik göç), gümrük %25, tarama %25 | Lead Developer | P2 | S1-11 | Planlandı | PR + QA |
| S1-17 | K14: kokpit modeli yüklenemezse durum satırı | Lead Developer | P2 | S1-02 | Planlandı | PR + QA |
| S1-18 | Yük Devi kokpiti PRODUCTION (K15) | Asset Factory | P2 | — | Devam (Kapı 1 kaydı geçti) | Kapı 2 teslim paketi |
| S1-13 | Kargo kaydı (K9): yenileme/yeniden girişte korunur, kopya kargo/ödül yok | Lead Developer | P1 | S1-12 | İnceleme (1.54.1) | PR + QA |

### `js/game.js` birleşme sırası
S1-12 (PR #30, birleşti) → PR #28 → S1-13 → S1-15 → S1-11 → S1-16 → S1-10 → S1-17 → S1-03 → S1-04

Lead Developer işleri tek dalda (`claude/stardrift-hod-system-np3akq`) sırayla yürütür; aynı anda tek açık kod PR'ı. Kokpit bölgelerine (`CK3`, kokpit yükleyici, `__ckb`) PR #28 birleşene kadar dokunulmaz.

## Backlog (onay bekleyen ya da sonraki sprint)
| ID | Konu | Not |
|---|---|---|
| B-01a | Aşama 1-A bölge tablosu + 1-B hedef renkleri | K12b onaylı; S1-11 sonrası |
| B-01c | Aşama 1-C devriye karar mantığı | Önce tasarım notu, sonra Mehmet kararı |
| B-01d | Aşama 1-D taraf unvanları | C sonrası |
| B-03 | Hayalet kokpiti | Yük Devi'den sonra |
| B-04 | Bölüm 6 final patron karşılaşması | Game Designer önerisi, ekonomi etkisi yok |
| B-05 | Pilot Kütüğü ve başarımlar | Game Designer önerisi, ekonomi etkisi yok |
| B-06 | Yetenek sıfırlama | Ücret Mehmet onayına bağlı |
| B-07 | Playwright smoke testi (QA'nın qa_pr28.js betiği temel alınır) | Lead Developer |
| B-08 | Firebase kuralları ve kayıt kodu güvenliği | QA incelemesi |
| B-09 | `game.js` modülerleştirme | Büyük mimari değişiklik, Mehmet onayı gerekli |
