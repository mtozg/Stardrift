// Stardrift bulut hesap sunucusu (Cloudflare Worker + D1)
// - E-posta + şifre ile kayıt, e-postaya gelen 6 haneli kodla aktivasyon, giriş, şifre sıfırlama
// - Hesaba bağlı bulut kaydı (oku / yaz)
// - Hesapsız kısa cihaz kodu: kaydı yükle → kod al; başka cihazda kodu gir → kaydı indir (30 gün)
// E-postalar Brevo üzerinden gider (BREVO_KEY gizli değişkeni, MAIL_FROM gönderen adresi).

const ORIGINS = ['https://mtozg.github.io', 'http://localhost:8765'];
const DAY = 86400000, TOKEN_TTL = 180 * DAY, CODE_TTL = 30 * 60000, DEVICE_TTL = 30 * DAY, MAX_SAVE = 1500000;
const ALPHA = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';

const enc = new TextEncoder();
const hex = b => [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join('');
const rnd = n => { const a = new Uint8Array(n); crypto.getRandomValues(a); return a; };
const sha = async s => hex(await crypto.subtle.digest('SHA-256', enc.encode(s)));
async function pwHash(pw, salt){
  const k = await crypto.subtle.importKey('raw', enc.encode(pw), 'PBKDF2', false, ['deriveBits']);
  return hex(await crypto.subtle.deriveBits({ name: 'PBKDF2', hash: 'SHA-256', salt: enc.encode(salt), iterations: 5000 }, k, 256));
}
const okEmail = e => typeof e === 'string' && e.length <= 120 && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(e);
const normEmail = e => String(e || '').trim().toLowerCase();
const sixDigits = () => String(100000 + (new Uint32Array(rnd(4).buffer)[0] % 900000));
const deviceCode = () => { const b = rnd(8); let s = ''; for (let i = 0; i < 8; i++) s += ALPHA[b[i] % ALPHA.length]; return s.slice(0, 4) + '-' + s.slice(4); };

function cors(req){
  const o = req.headers.get('Origin') || '';
  return { 'Access-Control-Allow-Origin': ORIGINS.includes(o) ? o : ORIGINS[0], 'Access-Control-Allow-Methods': 'GET,POST,PUT,OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type,Authorization', 'Access-Control-Max-Age': '86400', 'Vary': 'Origin' };
}
const json = (req, body, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json; charset=utf-8', ...cors(req) } });
const fail = (req, msg, status = 400, extra) => json(req, Object.assign({ ok: false, error: msg }, extra || {}), status);

// IP başına basit sınır: dakikada n istek
async function limited(env, req, key, n){
  const ip = req.headers.get('CF-Connecting-IP') || 'yerel', k = key + ':' + ip, now = Date.now(), win = Math.floor(now / 60000);
  const row = await env.DB.prepare('SELECT n, t FROM hits WHERE k = ?').bind(k).first();
  if (row && row.t === win){ if (row.n >= n) return true; await env.DB.prepare('UPDATE hits SET n = n + 1 WHERE k = ?').bind(k).run(); return false; }
  await env.DB.prepare('INSERT INTO hits (k, n, t) VALUES (?, 1, ?) ON CONFLICT(k) DO UPDATE SET n = 1, t = excluded.t').bind(k, win).run();
  return false;
}

async function sendMail(env, to, subject, code, kind){
  const text = kind === 'reset'
    ? 'Stardrift şifre sıfırlama kodun: ' + code + '\n\nKod 30 dakika geçerli. Bu isteği sen yapmadıysan bu e-postayı yok say.'
    : 'Stardrift hesabını etkinleştirme kodun: ' + code + '\n\nOyunda kodu girince hesabın açılır. Kod 30 dakika geçerli.';
  const html = '<div style="font-family:Arial,sans-serif;background:#060b16;color:#e6edf8;padding:28px;text-align:center"><div style="letter-spacing:.3em;color:#ffc477;font-weight:700">STARDRIFT</div><p>' + (kind === 'reset' ? 'Şifre sıfırlama kodun:' : 'Hesabını etkinleştirme kodun:') + '</p><div style="font-size:34px;letter-spacing:.3em;font-weight:700;color:#7fd8ff">' + code + '</div><p style="color:#8ea2b6;font-size:13px">Kod 30 dakika geçerli.' + (kind === 'reset' ? ' Bu isteği sen yapmadıysan bu e-postayı yok say.' : '') + '</p></div>';
  if (!env.BREVO_KEY){ if (env.DEV === '1') return { dev: code }; throw new Error('E-posta servisi ayarlı değil'); }
  const r = await fetch('https://api.brevo.com/v3/smtp/email', { method: 'POST', headers: { 'api-key': env.BREVO_KEY, 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify({ sender: { name: 'Stardrift', email: env.MAIL_FROM }, to: [{ email: to }], subject, textContent: text, htmlContent: html }) });
  if (!r.ok) throw new Error('E-posta gönderilemedi (' + r.status + ')');
  return {};
}

// kod üret, özetini sakla, e-postayla gönder (saatte en çok 5)
async function issueCode(env, email, kind){
  const u = await env.DB.prepare('SELECT code_t, code_n FROM users WHERE email = ?').bind(email).first(), now = Date.now();
  const n = u && u.code_t && now - u.code_t < 3600000 ? u.code_n : 0;
  if (n >= 5) return { error: 'Çok fazla kod istendi. Bir saat sonra tekrar dene.' };
  const code = sixDigits();
  await env.DB.prepare('UPDATE users SET code = ?, code_kind = ?, code_t = ?, code_n = ?, code_tries = 0 WHERE email = ?').bind(await sha(email + ':' + code), kind, now, n + 1, email).run();
  return await sendMail(env, email, kind === 'reset' ? 'Stardrift şifre sıfırlama kodu' : 'Stardrift hesap etkinleştirme kodu', code, kind);
}
async function checkCode(env, email, code, kind){
  const u = await env.DB.prepare('SELECT * FROM users WHERE email = ?').bind(email).first();
  if (!u || u.code_kind !== kind || !u.code) return 'Kod bulunamadı. Yeni kod iste.';
  if (Date.now() - u.code_t > CODE_TTL) return 'Kodun süresi doldu. Yeni kod iste.';
  if (u.code_tries >= 5) return 'Çok fazla yanlış deneme. Yeni kod iste.';
  if (u.code !== await sha(email + ':' + String(code || '').trim())){ await env.DB.prepare('UPDATE users SET code_tries = code_tries + 1 WHERE email = ?').bind(email).run(); return 'Kod yanlış.'; }
  return null;
}
async function newToken(env, email){
  const t = hex(rnd(32)); await env.DB.prepare('INSERT INTO tokens (token, email, t) VALUES (?, ?, ?)').bind(t, email, Date.now()).run(); return t;
}
async function who(env, req){
  const a = req.headers.get('Authorization') || '', t = a.startsWith('Bearer ') ? a.slice(7) : '';
  if (!/^[0-9a-f]{64}$/.test(t)) return null;
  const r = await env.DB.prepare('SELECT email, t FROM tokens WHERE token = ?').bind(t).first();
  if (!r || Date.now() - r.t > TOKEN_TTL) return null;
  return r.email;
}

export default {
  async fetch(req, env){
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors(req) });
    const url = new URL(req.url), p = url.pathname.replace(/\/+$/, '') || '/';
    let body = {};
    if (req.method === 'POST' || req.method === 'PUT'){
      const len = +(req.headers.get('Content-Length') || 0); if (len > MAX_SAVE + 4096) return fail(req, 'Veri çok büyük', 413);
      try { body = await req.json(); } catch (e) { return fail(req, 'Geçersiz istek'); }
    }
    try {
      if (p === '/' ) return json(req, { ok: true, service: 'stardrift' });

      // ---- hesap
      if (p === '/register' && req.method === 'POST'){
        if (await limited(env, req, 'reg', 5)) return fail(req, 'Çok fazla deneme, biraz bekle.', 429);
        const email = normEmail(body.email), pw = String(body.password || ''), pilot = String(body.pilot || '').trim().slice(0, 14);
        if (!okEmail(email)) return fail(req, 'Geçerli bir e-posta gir.');
        if (pw.length < 6 || pw.length > 128) return fail(req, 'Şifre en az 6 karakter olmalı.');
        const u = await env.DB.prepare('SELECT verified FROM users WHERE email = ?').bind(email).first();
        if (u && u.verified) return fail(req, 'Bu e-postayla zaten bir hesap var. Giriş yap.', 409);
        const salt = hex(rnd(16)), h = await pwHash(pw, salt);
        if (u) await env.DB.prepare('UPDATE users SET pw_salt = ?, pw_hash = ?, pilot = ? WHERE email = ?').bind(salt, h, pilot, email).run();
        else await env.DB.prepare('INSERT INTO users (email, pilot, pw_salt, pw_hash, verified, created) VALUES (?, ?, ?, ?, 0, ?)').bind(email, pilot, salt, h, Date.now()).run();
        const r = await issueCode(env, email, 'verify'); if (r.error) return fail(req, r.error, 429);
        return json(req, Object.assign({ ok: true, need: 'verify' }, r.dev ? { dev: r.dev } : {}));
      }
      if (p === '/verify' && req.method === 'POST'){
        if (await limited(env, req, 'ver', 10)) return fail(req, 'Çok fazla deneme, biraz bekle.', 429);
        const email = normEmail(body.email), e = await checkCode(env, email, body.code, 'verify'); if (e) return fail(req, e);
        await env.DB.prepare('UPDATE users SET verified = 1, code = NULL, code_kind = NULL WHERE email = ?').bind(email).run();
        const u = await env.DB.prepare('SELECT pilot FROM users WHERE email = ?').bind(email).first();
        return json(req, { ok: true, token: await newToken(env, email), email, pilot: u ? u.pilot : '' });
      }
      if (p === '/resend' && req.method === 'POST'){
        if (await limited(env, req, 'res', 3)) return fail(req, 'Çok fazla deneme, biraz bekle.', 429);
        const email = normEmail(body.email), kind = body.kind === 'reset' ? 'reset' : 'verify', u = await env.DB.prepare('SELECT verified FROM users WHERE email = ?').bind(email).first();
        if (!u || (kind === 'verify' && u.verified)) return json(req, { ok: true });   // var/yok bilgisi sızdırma
        const r = await issueCode(env, email, kind); if (r.error) return fail(req, r.error, 429);
        return json(req, Object.assign({ ok: true }, r.dev ? { dev: r.dev } : {}));
      }
      if (p === '/login' && req.method === 'POST'){
        if (await limited(env, req, 'log', 8)) return fail(req, 'Çok fazla deneme, biraz bekle.', 429);
        const email = normEmail(body.email), u = await env.DB.prepare('SELECT * FROM users WHERE email = ?').bind(email).first();
        if (!u || u.pw_hash !== await pwHash(String(body.password || ''), u.pw_salt)) return fail(req, 'E-posta ya da şifre yanlış.', 401);
        if (!u.verified){ const r = await issueCode(env, email, 'verify'); return fail(req, 'Hesabın henüz etkin değil. E-postana yeni kod gönderdik.', 403, Object.assign({ need: 'verify' }, r.dev ? { dev: r.dev } : {})); }
        return json(req, { ok: true, token: await newToken(env, email), email, pilot: u.pilot || '' });
      }
      if (p === '/forgot' && req.method === 'POST'){
        if (await limited(env, req, 'fgt', 3)) return fail(req, 'Çok fazla deneme, biraz bekle.', 429);
        const email = normEmail(body.email), u = await env.DB.prepare('SELECT verified FROM users WHERE email = ?').bind(email).first();
        let dev; if (u && u.verified){ const r = await issueCode(env, email, 'reset'); if (r.error) return fail(req, r.error, 429); dev = r.dev; }
        return json(req, Object.assign({ ok: true }, dev ? { dev } : {}));   // hesap yoksa da aynı yanıt
      }
      if (p === '/reset' && req.method === 'POST'){
        if (await limited(env, req, 'rst', 10)) return fail(req, 'Çok fazla deneme, biraz bekle.', 429);
        const email = normEmail(body.email), pw = String(body.password || ''); if (pw.length < 6 || pw.length > 128) return fail(req, 'Şifre en az 6 karakter olmalı.');
        const e = await checkCode(env, email, body.code, 'reset'); if (e) return fail(req, e);
        const salt = hex(rnd(16));
        await env.DB.prepare('UPDATE users SET pw_salt = ?, pw_hash = ?, code = NULL, code_kind = NULL WHERE email = ?').bind(salt, await pwHash(pw, salt), email).run();
        await env.DB.prepare('DELETE FROM tokens WHERE email = ?').bind(email).run();   // eski oturumlar kapanır
        const u = await env.DB.prepare('SELECT pilot FROM users WHERE email = ?').bind(email).first();
        return json(req, { ok: true, token: await newToken(env, email), email, pilot: u ? u.pilot : '' });
      }
      if (p === '/logout' && req.method === 'POST'){
        const a = req.headers.get('Authorization') || ''; if (a.startsWith('Bearer ')) await env.DB.prepare('DELETE FROM tokens WHERE token = ?').bind(a.slice(7)).run();
        return json(req, { ok: true });
      }

      // ---- hesaba bağlı bulut kaydı
      if (p === '/save'){
        const email = await who(env, req); if (!email) return fail(req, 'Oturum geçersiz. Yeniden giriş yap.', 401);
        if (req.method === 'GET'){ const r = await env.DB.prepare('SELECT data, t FROM saves WHERE email = ?').bind(email).first(); return json(req, { ok: true, data: r ? r.data : null, t: r ? r.t : 0 }); }
        if (req.method === 'PUT'){ const d = body.data; if (typeof d !== 'string' || d.length > MAX_SAVE) return fail(req, 'Kayıt geçersiz ya da çok büyük.'); const t = Date.now();
          await env.DB.prepare('INSERT INTO saves (email, data, t) VALUES (?, ?, ?) ON CONFLICT(email) DO UPDATE SET data = excluded.data, t = excluded.t').bind(email, d, t).run(); return json(req, { ok: true, t }); }
      }

      // ---- hesapsız cihaz kodu
      if (p === '/code' && req.method === 'POST'){
        if (await limited(env, req, 'cod', 4)) return fail(req, 'Çok fazla deneme, biraz bekle.', 429);
        const d = body.data; if (typeof d !== 'string' || d.length > MAX_SAVE) return fail(req, 'Kayıt geçersiz ya da çok büyük.');
        let code = ''; for (let i = 0; i < 5; i++){ code = deviceCode(); const ex = await env.DB.prepare('SELECT 1 FROM codes WHERE code = ?').bind(code).first(); if (!ex) break; }
        const now = Date.now(); await env.DB.prepare('DELETE FROM codes WHERE t < ?').bind(now - DEVICE_TTL).run();
        await env.DB.prepare('INSERT INTO codes (code, data, t) VALUES (?, ?, ?)').bind(code, d, now).run();
        return json(req, { ok: true, code, days: 30 });
      }
      if (p.startsWith('/code/') && req.method === 'GET'){
        if (await limited(env, req, 'cog', 10)) return fail(req, 'Çok fazla deneme, biraz bekle.', 429);
        const code = decodeURIComponent(p.slice(6)).toUpperCase().replace(/[^A-Z0-9]/g, ''), c = code.slice(0, 4) + '-' + code.slice(4, 8);
        const r = await env.DB.prepare('SELECT data, t FROM codes WHERE code = ?').bind(c).first();
        if (!r || Date.now() - r.t > DEVICE_TTL) return fail(req, 'Kod bulunamadı ya da süresi dolmuş.', 404);
        return json(req, { ok: true, data: r.data, t: r.t });
      }
      return fail(req, 'Bulunamadı', 404);
    } catch (e) {
      return fail(req, 'Sunucu hatası: ' + (e && e.message || e), 500);
    }
  }
};
