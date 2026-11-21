# Tanılama ve ölçüm paneli (T1/T2)

Sürüm 1.66.5. Amaç: gerçek cihazda (iPhone/iPad) kare hızı, çizim yükü ve açılış süresini **Mac olmadan** okumak.
Panel yalnız adrese `?tani=1` eklenince açılır. Normal oyuncu hiçbir şey görmez ve `js/tani.js` dosyası hiç indirilmez.

## Nasıl açılır
- `https://mtozg.github.io/Stardrift/?tani=1`: panel ekranın sol altında belirir (dokunmaya kapalı, `pointer-events:none`).
- `?tani=1&yukSifirla=1`: kayıtlı yükleme geçmişini siler.
- Mevcut `?tani=1` üst orta paneli (hareket/ateş/olay durumu) olduğu gibi çalışmaya devam eder; yeni panel ondan ayrıdır.

## T1: panel alanları ve hesaplama
| Alan | Anlamı | Nasıl hesaplanır |
|---|---|---|
| `fps` | Anlık kare hızı | Son 30 karenin ortalama süresinin tersi (1000 / ms) |
| `medyan` | Medyan kare hızı | Son **600 karenin** (60 Hz'de ≈10 sn) medyan kare süresi → 1000 / ms |
| `düşük%5` | En kötü %5'in kare hızı | Aynı 600 karenin **%95'lik** kare süresi (p95) → 1000 / ms. "Her 20 karenin en yavaşı bu hızın altında" demektir |
| `kare ms med / p95` | Kare süreleri | Yukarıdaki medyan ve p95, milisaniye |
| `takılma>100ms` | Uzun kare sayısı | Oturum boyunca 100 ms'yi aşan kare sayısı (`requestAnimationFrame` aralığı) |
| `çizim` (`med`) | Karedeki çizim çağrısı (draw call) | Bir karede yapılan **bütün** `renderer.render()` çağrılarının `info.render.calls` toplamı (ana sahne + bloom geçişleri + ek renderer'lar). Medyan: son 600 kare |
| `üçgen` | Karedeki üçgen sayısı | Aynı yöntem, `info.render.triangles` toplamı |
| `doku`, `geo`, `prog` | GPU'daki doku, geometri, shader programı sayısı | Ana renderer'ın `info.memory.textures/geometries` ve `info.programs.length` değeri |
| `heap` | JS bellek kullanımı (MB) | `performance.memory` varsa (Chrome). **iOS Safari'de yok, panelde görünmez** |
| `WebGL oluşturulan / kayıp / geri` | WebGL bağlamları | `canvas.getContext('webgl'...)` çağrıları sarmalanır: her yeni canvas bir "oluşturulan"; `webglcontextlost` olayı "kayıp", `webglcontextrestored` "geri". `renderer` = oluşturulan `THREE.WebGLRenderer` sayısı |

**Bilinen sınırlar**
- Çizim ve üçgen sayısı yalnız `THREE.WebGLRenderer` üzerinden geçenleri sayar. Kokpit/HUD'un 2B tuvalleri (canvas 2D) ve CSS çizimi dahil değil.
- Kare hızı, tarayıcının `requestAnimationFrame` hızıdır (iOS'ta Düşük Güç Modu 30 fps'e düşürebilir; bu panelde fps'in kendisi düşer).
- Pil ve ısınma **ölçülmüyor** (iOS Safari'de ilgili arayüz yok); bunlar elle (Ayarlar > Pil, dokunarak) kaydedilir (`docs/QA_GERCEK_CIHAZ.md`).
- Ölçüm paneli kendisi küçük bir maliyet getirir (her karede birkaç toplama; 500 ms'de bir sıralama). Karşılaştırmalı performans testleri paneli **açık** halde de **kapalı** halde de yapılmalı; kapalıyken hiçbir ölçüm kodu çalışmaz.

## T2: açılış süresi
Zaman, `performance.now()` ile sayfa gezinme başlangıcına göre milisaniyedir (`performance.mark('sd:...')` ile de işaretlenir).
| Aşama | Anlamı |
|---|---|
| `three` | `vendor/three.min.js` indirme bitişi (`resource timing responseEnd`) |
| `bloom`, `gemi`, `ses`, `game` | Sırasıyla `three-bloom.js`, `js/data_gemi.js`, `js/data_ses.js`, `js/game.js` indirme bitişi |
| `başla` (`game-basla`) | `game.js` çalışmaya başladı (ilk satır) |
| `motor` | Oyun motoru kuruldu: `game-hazir` − `game-basla` (süre, ms) |
| `hazır` (`sd-ready`) | Açılış perdesi kalktı |
| `menü` (`menu`) | Menü ilk kez çizildi (`sd-ready`'den sonraki ilk kare) |
**Soğuk / sıcak:** `game.js` gövdesi ağdan tam indiyse "soğuk", tarayıcı önbelleğinden ya da 304 doğrulamasıyla geldiyse "sıcak".
**Tekrarlanabilirlik:** her yükleme `localStorage` içinde saklanır (en çok son 10). Panel soğuk ve sıcak için ayrı **medyanı** gösterir (`medyan soğuk(n) ... sıcak(n) ...`). 5 yükleme medyanı için aşağıdaki yöntem.

### 5 yükleme medyan yöntemi
1. Yeni yükleme: `...?tani=1&yukSifirla=1` aç, menü gelsin (≥3 sn bekle), ilk satırdaki `hazır` ve `menü` değerlerini yaz.
2. **Her yükleme arasında en az 21 saniye bekle**, sonra `...?tani=1` ile yeniden yükle (4 kez). Bu bekleme zorunlu: aşağıya bakın.
3. Soğuk ölçüm için yüklemeler arasında Safari'de siteyi/önbelleği temizle. Panelde `medyan soğuk(5)` yazana kadar tekrar et.

## Dikkat: açılış çökme koruması
`index.html` içindeki kurtarma kodu, sayfa **20 sn içinde 3. kez** yüklenirse "çökme" sayar: service worker ve önbelleği siler, `?tani=1`'i adresten atar ve cihazda **çevrimdışı paket indirmesini kalıcı olarak kapatır** (`sd_nosync=1`; kodda bu bayrağı geri açan bir yol yok). Bu yüzden:
- Hızlı art arda yenileme ölçüm sonuçlarını bozar ve çevrimdışı paketi o cihazda kapatabilir.
- Gerçek oyuncuda da, kötü bağlantıda üst üste yenileyen biri bu duruma düşebilir (ayrı bulgu; düzeltme T-listesinde onay bekliyor).
Cihazda çevrimdışı paketi tekrar açmak için tarayıcı site verisini silmek gerekir.

## Kapalıyken etki
- `js/tani.js` yüklenmez; `window.__sdm`, `window.__tani`, panel ve getContext/renderer sarmalayıcıları **oluşmaz**.
- `game.js` içinde yalnız 3 satır `window.__sdm && window.__sdm('...')` var (tanımsızsa tek özellik denetimi).
- Otomatik test `tools/qa/tani.js` bunları doğrular (kapalıyken dosya istenmez, panel yok, `getContext` yerel).

## Kod konumları
`js/tani.js` (tüm ölçüm), `index.html` (`?tani=1` iken yükleme satırı), `js/game.js` (3 işaret satırı), `tools/qa/tani.js` (test).
