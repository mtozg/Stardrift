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

## Ekip
| Ajan | Sorumluluk | Çalışma alanı |
|---|---|---|
| Developer | Oyun kodu, HUD, sistemler, sürüm, offline listesi | `js/game.js`, `index.html`, `sw.js`, `offline.json`, `README.md` |
| Asset Factory | Blender/GLB üretimi, QC, teslim paketi | `tools/asset_factory/`, `models/` (entegrasyon PR'ı hariç) |
| QA Engineer | İnceleme, test, kanıtlı hata raporu | Dosya değiştirmez |
| Game Designer | Tasarım ve denge analizi | Dosya değiştirmez |

## Durumlar
Backlog · Planlandı · Devam · İnceleme · Test · Tamam · Bloke

## Sprint 1
| ID | Görev | Ajan | Öncelik | Bağımlılık | Durum | Beklenen çıktı |
|---|---|---|---|---|---|---|
| S1-01 | PR #28 (Şahin 3B kokpiti 1.54.0) incelemesi | QA | P1 | — | Tamam: koşullu PASS | QA raporu |
| S1-01b | Filo oyuncusunun Morr'a erişimi | QA | P0 | — | Tamam: PASS (riskli) | QA raporu |
| S1-02a | PR #28: `__ckb.swap` ekonomi baypası (P1), dropB/PMREM dispose (P2) | Asset Factory | P1 | S1-01 | Tamam (bc5ba4a, QA PASS) | Commit SHA + test sonucu |
| S1-02b | PR #28 doku sızıntısı ölçümü | Asset Factory | P1 | S1-02a | Tamam: kokpit payı Δ=0 | Ölçüm raporu |
| S1-02 | PR #28 birleştirme | Mehmet | P1 | Gerçek telefon/tablet denemesi | Mehmet bekleniyor | `main` 1.54.0 |
| S1-03 | Bekçi otomatik duraklatma/menü sıfırlaması, hangar `hgSet` dispose, WebGL bağlam temizliği | Developer | P1 | S1-02 | Backlog | PR + QA |
| S1-04 | Kayıt sağlamlığı: şema sürümü, zaman damgası birliği, eski bulut anahtarı | Developer | P1 | S1-12 | Backlog | PR + QA |
| S1-06 | Ölçüm (K10): üs pasif geliri, yan görev ödülleri, ödül avcısı katlanması | Developer | P1 | — | Planlandı | Ölçüm raporu, kod değişikliği yok |
| S1-07 | Denge analizi (K6–K7): korsan itibarı, gümrük riski, yol taraması, kaçak satış XP | Game Designer | P2 | — | Planlandı | Ayrı ayrı değerlendirme |
| S1-08 | BUDGET MODE (Asset Factory süreç iyileştirmesi) | Asset Factory | P3 | — | Devam (53dfdf6 PR #28 içinde; sonrası `claude/asset-factory-budget-mode`) | `tools/asset_factory` değişiklikleri |
| S1-09 | ROADMAP ve karar günlüğü | HOD | P2 | K11 | İnceleme | Bu dosya |
| S1-10 | Kokpit GLB'lerinin offline paketine eklenmesi | Developer | P1 | S1-02 | Backlog | PR + QA |
| S1-11 | Morr erişimi: zincir ipucu, ücra kapının görev aktifken haritada işaretlenmesi, Kara Liman ret mesajında çıkış kapısı | Developer | P1 | — | Planlandı | PR + QA |
| S1-12 | Taraf değiştirme metni "Usta Pilot rütbesi" → "1200 XP" (K8) + README düzeltmesi | Developer | P2 | — | İnceleme (PR #30) | PR + QA |
| S1-14 | Üste gümrüksüz kaçak satışı doğrulaması | QA | P1 | — | Tamam: kanıtlı | QA raporu |
| S1-15 | K13: üste kaçak satışı kapatma, kara pazar yalnız Kara Liman ana istasyonu | Developer | P1 | S1-13 | Planlandı | PR + QA |
| S1-16 | K6, K7a, K7b: Korsan itibarı −50 (+ metin, tek seferlik göç), gümrük %25, tarama %25 | Developer | P2 | S1-11 | Planlandı | PR + QA |
| S1-17 | K14: kokpit modeli yüklenemezse durum satırı | Developer | P2 | S1-02 | Planlandı | PR + QA |
| S1-18 | Yük Devi kokpiti PRODUCTION (K15) | Asset Factory | P2 | — | Planlandı | Kapı 2 teslim paketi |
| S1-13 | Kargo kaydı (K9): yenileme/yeniden girişte korunur, kopya kargo/ödül yok | Developer | P1 | S1-12 | Planlandı | PR + QA |

### `js/game.js` birleşme sırası
PR #28 → S1-12 (PR #30) → S1-13 → S1-15 → S1-11 → S1-16 → S1-10 → S1-17 → S1-03 → S1-04

Developer PR #28 birleşmeden de dal açabilir; kokpit bölgelerine (kokpit yükleyici, `CK3`, `__ckb`) dokunmaz ve sıradaki PR'ını `main` üzerine güncelleyerek açar.

## Backlog (onay bekleyen ya da sonraki sprint)
| ID | Konu | Not |
|---|---|---|
| B-01 | Developer Aşama 1: bölge tablosu, hedef renkleri, devriye karar mantığı | K12: üç parça ayrı ayrı incelenecek |
| B-03 | Hayalet kokpiti | Yük Devi'den sonra |
| B-04 | Bölüm 6 final patron karşılaşması | Game Designer önerisi, ekonomi etkisi yok |
| B-05 | Pilot Kütüğü ve başarımlar | Game Designer önerisi, ekonomi etkisi yok |
| B-06 | Yetenek sıfırlama | Ücret Mehmet onayına bağlı |
| B-07 | Playwright smoke testi | QA + Developer |
| B-08 | Firebase kuralları ve kayıt kodu güvenliği | QA incelemesi |
| B-09 | `game.js` modülerleştirme | Büyük mimari değişiklik, Mehmet onayı gerekli |
