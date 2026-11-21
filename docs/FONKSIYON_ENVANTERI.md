# İşlev yeniden atama envanteri (T7)

Bu belge `python3 tools/fonksiyon_envanteri.py` ile üretilir (salt okunur analiz). Hiçbir işlev yeniden düzenlenmedi.
Kaynak: `js/game.js` (sürüm 1.66.4, 10817 satır). Satır numaraları o sürümden.

## 1. Sayılar

Önceki bir denetimde geçen "64" rakamı yalnız satır başındaki kalıbı sayıyordu; eksikti. Bu envanter bütün atamaları sayar.

| Sınıf | Atama | Önceki işlevi saran | Saran olmayan (değiştiren ya da ilk tanım) | İşlev adı |
|---|---|---|---|---|
| Yerel işlev | 165 | 145 | 20 | 60 |
| `window.__...` kancaları | 25 | 7 | 18 | 19 |
| **Toplam** | **190** | 152 | 38 | 79 |

"Saran olmayan" sayısı `function` bildirimi olmayan 17 adın **ilk tanımını** da içerir; hepsi hata değildir. Dinamik atama, nesne özellikleri ve ok işlevleri sayıya dahil değil.

## 2. Dört ana işlev

Kural: **atama sırası = dosya sırası.** En son atanan en dış katmandır: çağrıldığında önce o çalışır, saran ise bir önceki katmanı çağırır. Saran olmayan bir atama önceki katmanı çağırmaz; ondan önceki sarmalayıcılar o noktada atlanır.

### `renderExtras` (10 atama)
| # | Satır | Tür | Bölüm / amaç (yakın yorumdan) |
|---|---|---|---|
| 1 | 4071 | sarar | telefonda hangar gemisi saniyede 30 kare: akıcı görünür, yarı yük |
| 2 | 6001 | sarar | ---- ses: müzik + ek efektler |
| 3 | 6374 | sarar | ---- şeffaflık ayarı + üs modülleri + akıllı istasyonlar |
| 4 | 6495 | sarar | çok evrenli üs |
| 5 | 7023 | sarar | ---- üs modülleri: kredi + cevher + parça |
| 6 | 7136 | sarar | Diğer sekmesinden Ses ve Görünüm bölümleri kalktı: hepsi ayarlar panelinde |
| 7 | 7783 | sarar | ilerleme: Diğer sekmesinde |
| 8 | 8217 | sarar | Diğer: önce yolculuk ve keşif, en altta pilot/ayar/hesap |
| 9 | 9760 | sarar | rütbe çipi |
| 10 | 10037 | sarar | bulut kaydı yalnızca Claude içinde çalışır; GitHub Pages'te gizle |

### `renderDock` (11 atama)
| # | Satır | Tür | Bölüm / amaç (yakın yorumdan) |
|---|---|---|---|
| 1 | 4688 | sarar | ---------- İstasyon gelişimi ---------- |
| 2 | 4718 | sarar | ---------- Tamirhane ---------- |
| 3 | 6126 | sarar | ---- düzen: tamirhane gemi sekmesine, fiyat tablosu cevher satışının içine |
| 4 | 6528 | sarar | ---- tek, ayrıntılı ticaret tablosu |
| 5 | 7004 | sarar | ağır korsanlar (Kurt, Yağmacı) fazladan parça bırakır |
| 6 | 7794 | sarar | ---- ticaret: tek tek satış |
| 7 | 8641 | sarar | 1.63.0: İstasyon bülteni (Game Designer P3). Yalnız bilgi satırı; kredi, XP ve kayıt değer |
| 8 | 9449 | sarar | Geliştir sekmesinde gemi geliştirme yerine yetenek ağacına yönlendirme |
| 9 | 9761 | sarar | rütbe çipi |
| 10 | 10036 | sarar | bulut kaydı yalnızca Claude içinde çalışır; GitHub Pages'te gizle |
| 11 | 10114 | sarar | istasyon alt yazısı (hangi cevheri alır, fiyat farkı) başlığa/sekmelere binmesin: İstasyon |

### `dockLayout` (10 atama)
| # | Satır | Tür | Bölüm / amaç (yakın yorumdan) |
|---|---|---|---|
| 1 | 4268 | **ilk tanım / değiştirir** |  |
| 2 | 5541 | sarar | alçak ekran (telefon yatay): sıkı panel |
| 3 | 5636 | sarar | kullanılmayan başlık |
| 4 | 6149 | sarar | ---- satın alma düğmeleri: gücün yetiyorsa altın, yetmiyorsa gri; yeşil yalnızca "takılı/s |
| 5 | 6402 | sarar | üste inince Diğer sekmesi "Üs" olur ve ilk açılışta o açılır |
| 6 | 7289 | sarar | ilerleme kancaları |
| 7 | 8194 | sarar | =====================  v2 istasyon menüsü: tam ekran, sade, uzay arayüzü  ================ |
| 8 | 8982 | sarar | 1.60.0 (K31): kaçak satışı birim başına 5 XP (üste satış kapalı, yalnız gümrüklü istasyonl |
| 9 | 9370 | sarar | ---- Görevler sekmesi: seviye rozeti, rütbe dizisi, yetenek düğmesi |
| 10 | 9758 | sarar | rütbe çipi |

### `killNpc` (11 atama)
| # | Satır | Tür | Bölüm / amaç (yakın yorumdan) |
|---|---|---|---|
| 1 | 2937 | sarar | kimlik: her gemi bir kayıt taşır |
| 2 | 3371 | sarar |  |
| 3 | 5694 | sarar | Korsan'ın vurduğu devriye ve yakındakiler karşılık verir |
| 4 | 7286 | sarar | ilerleme kancaları |
| 5 | 7426 | sarar | etkiler |
| 6 | 7590 | sarar | Filo "Uzak devriye" / Korsan "Pusu": istasyondan 3 km ötede N düşman (Korsan'da Filo ya da |
| 7 | 8652 | sarar | avantajlar |
| 8 | 8856 | sarar | ---- aranma ve başa konan ödül |
| 9 | 9444 | sarar | ---------- yetenek etkileri: hasar azaltma, ödül avcısı, zengin damar, diplomat, tamir ind |
| 10 | 9459 | sarar | ---- sayaçlar |
| 11 | 10630 | sarar | eski "dost ateşi" uyarısı atlanır |

Bağımlılık notları:
- `renderExtras` ve `renderDock` istasyon menüsünü, `dockLayout` ekran düzenini, `killNpc` öldürme sonrası etkileri (XP, itibar, görev sayaçları, aranma, yetenekler) üst üste ekler. **Katman sırası değişirse** düzen ya da ödül/sayaç sırası değişir.
- `killNpc` katmanlarının çoğu `by === 'player'`, düşman olma ve `npcs.indexOf(n) >= 0` (zaten silinmiş mi) koşullarını kontrol eder. **Yeni katman eklerken bu desen korunmalı**; aksi halde aynı öldürme için ikinci kez ödül yazılır (çift gelir).
- Bazı `renderDock`/`renderExtras` katmanları `try/catch` içinde; bir katmanın hatası alttakileri çalıştırmayabilir.

## 3. Saran olmayan atamalar
| İşlev | Satırlar | Toplam atama |
|---|---|---|
| `persist` | 7102, 9141, 10488 | 6 |
| `__hzDraw` | 5295, 8422 | 2 |
| `__xProps` | 5640, 6289 | 4 |
| `renderHg` | 6461 | 5 |
| `dockLayout` | 4268 | 10 |
| `commTarget` | 4851 | 1 |
| `__drawFr` | 5143 | 1 |
| `showAwayCard` | 5404 | 1 |
| `damageNpc` | 5668 | 3 |
| `evNpcThink` | 5869 | 1 |
| `__sfxWarp` | 5964 | 1 |
| `addFlames` | 6261 | 2 |
| `renderJump` | 6447 | 1 |
| `renderMk` | 6551 | 1 |
| `__hyper3d` | 6699 | 1 |
| `__hyperCockpit` | 6828 | 1 |
| `__hyperGate` | 6888 | 1 |
| `__dropParts` | 6996 | 1 |
| `ctGen` | 7250 | 5 |
| `ctProgress` | 7266 | 2 |
| `ctAct` | 7267 | 2 |
| `renderCt` | 7273 | 7 |
| `__leaderDrop` | 7821 | 2 |
| `__olayModel` | 7690 | 1 |
| `__thrust` | 7873 | 1 |
| `__xFlames` | 7913 | 1 |
| `__sfxBolt` | 7970 | 1 |
| `__sfxRocket` | 7987 | 1 |
| `sfxLaunch` | 7994 | 1 |
| `__sfxExpl` | 7996 | 1 |
| `__warnSnd` | 8064 | 1 |
| `toast` | 8586 | 4 |
| `wreck` | 10165 | 1 |
| `error` | 10791 | 1 |

## 4. Bütün işlevler
| İşlev | Atama | Sarar | Diğer | İlk-son satır |
|---|---|---|---|---|
| `killNpc` | 11 | 11 | 0 | 2937-10630 |
| `renderDock` | 11 | 11 | 0 | 4688-10114 |
| `renderExtras` | 10 | 10 | 0 | 4071-10037 |
| `dockLayout` | 10 | 9 | 1 | 4268-9758 |
| `renderCt` | 7 | 6 | 1 | 7273-9759 |
| `persist` | 6 | 3 | 3 | 3223-10488 |
| `applyWorld` | 6 | 6 | 0 | 4800-9165 |
| `thinkPirate` | 5 | 5 | 0 | 3353-10644 |
| `renderHg` | 5 | 4 | 1 | 4213-6461 |
| `ctGen` | 5 | 4 | 1 | 7250-10658 |
| `fireMissile` | 4 | 4 | 0 | 4904-10248 |
| `__xProps` | 4 | 2 | 2 | 5640-6665 |
| `applyShip` | 4 | 4 | 0 | 6079-9596 |
| `breakAsteroid` | 4 | 4 | 0 | 7287-9445 |
| `toast` | 4 | 3 | 1 | 8586-10618 |
| `radio` | 3 | 3 | 0 | 3276-10619 |
| `tryDock` | 3 | 3 | 0 | 4432-8952 |
| `hgSet` | 3 | 3 | 0 | 4700-7910 |
| `damageNpc` | 3 | 2 | 1 | 5668-10621 |
| `hurt` | 3 | 3 | 0 | 5977-10164 |
| `drawHud` | 3 | 3 | 0 | 9027-10739 |
| `thinkPatrol` | 2 | 2 | 0 | 3361-8936 |
| `npcThink` | 2 | 2 | 0 | 4526-5684 |
| `npcShoot` | 2 | 2 | 0 | 4896-7180 |
| `spawnFx` | 2 | 2 | 0 | 5073-5248 |
| `__hzDraw` | 2 | 0 | 2 | 5295-8422 |
| `renderWp` | 2 | 2 | 0 | 5452-9641 |
| `devHtml` | 2 | 2 | 0 | 6097-6410 |
| `addFlames` | 2 | 1 | 1 | 6261-7937 |
| `spawnRole` | 2 | 2 | 0 | 7200-7446 |
| `ctProgress` | 2 | 1 | 1 | 7266-9460 |
| `ctAct` | 2 | 1 | 1 | 7267-9112 |
| `onRuinFound` | 2 | 2 | 0 | 7288-7736 |
| `crewCargo` | 2 | 2 | 0 | 7478-8651 |
| `__leaderDrop` | 2 | 1 | 1 | 7482-7821 |
| `fireBolts` | 2 | 2 | 0 | 7978-9679 |
| `audioUpdate` | 2 | 2 | 0 | 8070-10390 |
| `__openSet` | 2 | 2 | 0 | 9871-9998 |
| `update` | 2 | 2 | 0 | 10769-10792 |
| `spawnNpc` | 1 | 1 | 0 | 2918-2918 |
| `undock` | 1 | 1 | 0 | 4441-4441 |
| `unloadAt` | 1 | 1 | 0 | 4678-4678 |
| `npcSteer` | 1 | 1 | 0 | 4725-4725 |
| `commOpen` | 1 | 1 | 0 | 4829-4829 |
| `commTarget` | 1 | 0 | 1 | 4851-4851 |
| `npcBeam` | 1 | 1 | 0 | 4897-4897 |
| `__drawFr` | 1 | 0 | 1 | 5143-5143 |
| `enterSystem` | 1 | 1 | 0 | 5163-5163 |
| `showAwayCard` | 1 | 0 | 1 | 5404-5404 |
| `setLock` | 1 | 1 | 0 | 5430-5430 |
| `evNpcThink` | 1 | 0 | 1 | 5869-5869 |
| `__sfxWarp` | 1 | 0 | 1 | 5964-5964 |
| `devAdd` | 1 | 1 | 0 | 6417-6417 |
| `renderJump` | 1 | 0 | 1 | 6447-6447 |
| `renderMk` | 1 | 0 | 1 | 6551-6551 |
| `__hyper3d` | 1 | 0 | 1 | 6699-6699 |
| `__hyperCockpit` | 1 | 0 | 1 | 6828-6828 |
| `__hyperGate` | 1 | 0 | 1 | 6888-6888 |
| `__dropParts` | 1 | 0 | 1 | 6996-6996 |
| `__olayModel` | 1 | 0 | 1 | 7690-7690 |
| `__thrust` | 1 | 0 | 1 | 7873-7873 |
| `__xFlames` | 1 | 0 | 1 | 7913-7913 |
| `initAudio` | 1 | 1 | 0 | 7963-7963 |
| `__sfxBolt` | 1 | 0 | 1 | 7970-7970 |
| `__sfxRocket` | 1 | 0 | 1 | 7987-7987 |
| `sfxLaunch` | 1 | 0 | 1 | 7994-7994 |
| `sfxBoom` | 1 | 1 | 0 | 7995-7995 |
| `__sfxExpl` | 1 | 0 | 1 | 7996-7996 |
| `stationAnim` | 1 | 1 | 0 | 8062-8062 |
| `__warnSnd` | 1 | 0 | 1 | 8064-8064 |
| `repMul` | 1 | 1 | 0 | 9264-9264 |
| `__fac` | 1 | 1 | 0 | 9446-9446 |
| `wreck` | 1 | 0 | 1 | 10165-10165 |
| `setBanner` | 1 | 1 | 0 | 10207-10207 |
| `__oreGot` | 1 | 1 | 0 | 10208-10208 |
| `explodeMissile` | 1 | 1 | 0 | 10264-10264 |
| `updateNpc` | 1 | 1 | 0 | 10267-10267 |
| `renderMain` | 1 | 1 | 0 | 10760-10760 |
| `error` | 1 | 0 | 1 | 10791-10791 |
