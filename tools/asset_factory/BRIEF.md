# Asset Factory: proje özeti (görev başında bunu oku)

Güncel durum için: `python factory.py brief` (kayıt defterinden). Bu dosya yalnız değişmeyen kuralları ve yolları taşır.
Dört ana belgeyi (ARCHITECTURE, STANDARDS, QC, INVENTORY) baştan okuma; gerekirse yalnız ilgili bölümü aç (aşağıdaki tablo).

## Ne bu
Oyundan bağımsız 3B varlık fabrikası: Blender bpy modelleme → GLB + PBR doku → Three r128 ve mobil doğrulama → teslim paketi.
Çalışma dalı `claude/awesome-cannon-qb1ro2`. Oyun koduna ve `main`e yalnız kullanıcının ayrı onayıyla dokunulur.

## Değişmez kurallar (STANDARDS §0)
- Akış: PREVIEW → **Kapı 1** (kullanıcı görsel onayı) → PRODUCTION → **Kapı 2** (kullanıcı teknik onayı) → **Kapı 3** (entegrasyon, ayrı onay).
- Onayları yalnız kullanıcı verir. Claude yalnız `test_asset` nesnelerini onaylayabilir. `factory.py approve` engellenirse çözümü kullanıcıya bırak.
- Kaşif dosyaları (`models/cockpit_kasif*.glb`, `tools/cockpit/`) salt okunur referanstır. Eski 2B kokpit çizimleri ve paralaks yeni üretimde kullanılmaz.
- Dondurulmuş/entegre varlık yeniden üretilmez (`factory.py` reddeder). Her kokpit özgün tasarlanır; Kaşif'in tasarımı kopyalanmaz.
- Kıskaç (Yük Devi): ilk modelde statik; `ART_claw_*` hiyerarşisi ve pivotlar animasyona hazır.
- Hazır model (Sketchfab vb.) yalnız lisans/kalite/uyum incelemesi ve kullanıcı onayıyla.
- 3B kokpitte çizim kokpitine geri dönüş (yedek) YOK; model gelmezse sessiz yeniden deneme (kullanıcı kararı).

## Üretim sırası
Oyuncu gemileri (Kaşif ✔, Şahin ✔ entegre, Yük Devi, Hayalet) → cevher ve toplanabilirler → NPC gemileri → istasyonlar (Ankora) → kapılar/kalıntılar → boss'lar → yer tutucu ortam → küçük nesneler → iç mekanlar.

## Nereye bakılır
| İhtiyaç | Dosya |
|---|---|
| Boru hattı, klasörler, aşamalar | ARCHITECTURE.md (ilgili aşama) |
| Bütçeler, adlandırma, pivot, malzeme kuralları | STANDARDS.md §7 bütçe, §0 kararlar |
| QC katmanları ve eşikler | QC.md, `qc/rules.json`, `qc/budgets.json` |
| Hangi gemi/nesne nasıl görünüyor, kaynak satırlar | INVENTORY.md |
| Kamera/ekran sözleşmesi (kokpit) | `families/cockpit/build.py` başlık, `qc/cockpit_compat.py` |
| Oyunda gemi başına 3B kokpit tablosu | `js/game.js` `CK3` (yeni gemi = 1 satır + 2 GLB) |
| BUDGET MODE iş akışı | BUDGET.md |

## Komutlar
`brief` · `model <id> [--probe|--fast]` · `note` · `verify` · `qc` · `deliver` · `cost` — ayrıntı BUDGET.md.
Oyun içi test: `node tools/asset_factory/qc/ingame_cockpit.js <çıktı> ["<cihaz>"]` (repo kökünde `python3 -m http.server 8765` açıkken).

## Kokpit teknik sözleşmesi (özet)
Göz orijinde, ileri −Z, FOV 74°, odak 435,27 px, asal nokta (800; 239,5) / 1600×656. `SCR_SYS/SCR_RADAR/SCR_HULL` tek dörtgen, UV sol-üst (0,0).
Bütçe: ≤ 60 bin üçgen, ≤ 4 MB, GPU ≤ 40 MB, tek gövde malzemesi, WebP, emisyon ≤ 1 (r128).
