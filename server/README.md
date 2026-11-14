# Stardrift bulut hesap sunucusu

Cloudflare Worker + D1. Oyundaki e-postayla kayıt/giriş, bulut kaydı ve kısa cihaz kodu bu sunucuyu kullanır.

- `worker.js`: sunucu kodu (kayıt, e-posta kodu ile etkinleştirme, giriş, şifre sıfırlama, `/save`, `/code`)
- `schema.sql`: D1 tabloları
- Ayarlar (Cloudflare panelinde, Worker → Settings → Variables and Secrets):
  - `MAIL_FROM` (metin): Brevo'da doğrulanmış gönderen e-posta adresi
  - `BREVO_KEY` (gizli): Brevo API anahtarı
- Oyun tarafı: `index.html` içindeki `window.SD_API` sunucunun adresidir (örn. `https://stardrift-api.<hesap>.workers.dev`). Boşsa bulut özellikleri kapalıdır.

Yerel deneme: `npx wrangler d1 execute stardrift --local --file=schema.sql`, sonra `DEV=1` değişkeniyle `npx wrangler dev --local` (e-posta yerine kod yanıtta döner). Oyunda `localStorage.sd_api = 'http://localhost:8787'`.
