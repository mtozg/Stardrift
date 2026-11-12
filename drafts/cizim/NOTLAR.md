# Üs eklenti çizimi denemesi — ücretsiz servisler (2026-11-12)

Referans: https://mtozg.github.io/Stardrift/assets/img/olay_us_top.webp (repoda `assets/img/olay_us_top.webp`).
Promptlar: görevdeki A (3x2 sprite sheet) ve B (tek güneş paneli kanadı), birebir.

## Sonuç tablosu

| Deneme | URL / uç nokta | Sonuç |
|---|---|---|
| Pollinations klasik, `model=kontext` + `image=` (referanslı) | `https://image.pollinations.ai/prompt/{p}?model=kontext&image={ref}&width=1024&height=1024&seed=7&nologo=true` | **HTTP 403** `FORBIDDEN`: "kontext isn't part of the Classic API. Use it with a pollen key at https://enter.pollinations.ai/?ref=classic" |
| Pollinations gen, `model=kontext` | `https://gen.pollinations.ai/image/{p}?model=kontext&image={ref}&...` | **HTTP 401** `UNAUTHORIZED`: "A valid API key is required. Get one at https://enter.pollinations.ai/keys ..." |
| Pollinations gen, `model=flux` | `https://gen.pollinations.ai/image/{p}?model=flux&...` | **HTTP 401**, aynı mesaj (gen.pollinations.ai'de anahtarsız görsel üretimi yok) |
| Pollinations klasik, `model=flux` (referanssız) | `https://image.pollinations.ai/prompt/{p}?model=flux&width=1024&height=1024&seed=7&nologo=true` | **HTTP 200** ama EXIF'e göre gerçek model **`sana`**, boyut **768x768** (1024 istenmesine rağmen), `nologo=true` olmasına rağmen köşede "pollinations.ai" logosu var. `https://image.pollinations.ai/models` → `["sana"]`: klasik API'de artık yalnızca sana var. → `A_pollinations_classic_flux-sana.png`, `B_pollinations_classic_flux-sana.png` |
| AI Horde, Python urllib ile | `POST https://aihorde.net/api/v2/generate/async` | **HTTP 403**, "error code: 1010" (Cloudflare tarayıcı imzası engeli; Python User-Agent'ı reddediliyor) |
| AI Horde, curl ile, txt2img (anonim `apikey: 0000000000`, 512x512, 25 adım, seed 7) | `POST .../generate/async` → `GET .../generate/check/{id}` → `GET .../generate/status/{id}` | **HTTP 202** → birkaç dakika içinde bitti. Model: `stable_diffusion` (SD 1.5). → `A_aihorde_sd15_txt.png`, `B_aihorde_sd15_txt.png` |
| AI Horde, curl ile, img2img (referans 512x512'ye küçültülüp `source_image` olarak verildi, denoise 0.75) | aynı | **HTTP 202** → bitti, SD 1.5. → `A_aihorde_sd15_img2img.png`, `B_aihorde_sd15_img2img.png` |

## Kalite değerlendirmesi (kısa)

Hiçbiri oyunda doğrudan kullanılabilecek kalitede değil:
- **Pollinations/sana A:** gri, bulanık, 2x2 ızgara; modüller tanınmıyor; yazıya benzer bozuntular ve logo var.
- **Pollinations/sana B:** güneş paneli değil, mavi bir uzay gemisine benzeyen bir şey; perspektif yanlış.
- **Horde SD1.5 txt A:** 2x2 izometrik kutular, açık mavi arka plan; 3x2 ve siyah zemin isteğine uyulmamış.
- **Horde SD1.5 img2img A:** referansın mavi tonları alınmış, ama karışık bir kule/kolaj; ızgara yok.
- **Horde SD1.5 txt B:** gerçekçi fotoğraf gibi bir güneş paneli; tepeden değil, siyah zemin değil.
- **Horde SD1.5 img2img B:** panel ve kafes kol fikri var, mavi blueprint zemin üzerinde; en yakın sonuç, ama tarz ve arka plan tutmuyor.

## Çıkarımlar

- Referans görselle stil aktarımı yapan ücretsiz bir yol, Pollinations'ta anahtarsız artık **yok** (kontext → 403/401).
- AI Horde anonim kullanılabiliyor ama yalnızca 512px'lik SD 1.5 sınıfı modeller geliyor ve sprite sheet / ızgara düzeni / siyah zemin gibi kurallara uyulmuyor.
- Daha iyi sonuç için seçenekler: (1) enter.pollinations.ai'den ücretsiz "pollen" anahtarı alıp `kontext` modelini denemek; (2) Horde'a kayıtlı anahtarla SDXL/Flux modeli istemek (`"models": [...]`); (3) sheet yerine her modülü tek tek üretmek, arka planı sonradan siyaha/şeffafa çevirmek.
