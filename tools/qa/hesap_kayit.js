// Hesap açma (taklit Firebase sunucusuyla): doğrulama e-postası bağlantı adresi yüzünden reddedilse bile kayıt "doğrula" ekranına geçmeli.
const boot = require('./_boot');
const b64 = o => Buffer.from(JSON.stringify(o)).toString('base64url');
const jwt = () => b64({ alg: 'none' }) + '.' + b64({ iss: 'x', aud: 'x', sub: 'u1', user_id: 'u1', email: 'a@b.co', email_verified: false, iat: Math.floor(Date.now() / 1000), exp: Math.floor(Date.now() / 1000) + 3600, firebase: { sign_in_provider: 'password', identities: {} } }) + '.x';
(async () => {
  const { p, b, errs } = await boot(); const R = { oob: [] };
  await p.route(/googleapis\.com/, async route => {
    const u = route.request().url(), body = route.request().postData() || ''; const j = o => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(o) });
    if (/accounts:signUp/.test(u)) return j({ idToken: jwt(), refreshToken: 'r', expiresIn: '3600', localId: 'u1', email: 'a@b.co' });
    if (/accounts:lookup/.test(u)) return j({ users: [{ localId: 'u1', email: 'a@b.co', emailVerified: false, displayName: 'Deneme', providerUserInfo: [{ providerId: 'password', email: 'a@b.co' }], lastLoginAt: '1', createdAt: '1' }] });
    if (/accounts:update/.test(u)) return j({ localId: 'u1', email: 'a@b.co', displayName: 'Deneme', idToken: jwt(), refreshToken: 'r', expiresIn: '3600', providerUserInfo: [] });
    if (/accounts:sendOobCode/.test(u)){ const url = /continueUrl/.test(body); R.oob.push(url ? 'url' : 'duz'); if (url) return route.fulfill({ status: 400, contentType: 'application/json', body: JSON.stringify({ error: { code: 400, message: 'UNAUTHORIZED_DOMAIN : Domain not allowlisted by project', errors: [{ message: 'UNAUTHORIZED_DOMAIN' }] } }) }); return j({ email: 'a@b.co' }); }
    return route.fulfill({ status: 404, contentType: 'application/json', body: '{}' });
  });
  await p.evaluate(() => window.__cloudAccount('reg'));
  await p.waitForSelector('#cE', { timeout: 15000 });
  await p.fill('#cE', 'a@b.co'); await p.fill('#cN', 'Deneme'); await p.fill('#cP', 'sifre123'); await p.fill('#cP2', 'sifre123');
  await p.click('#cloudBox .go');
  await p.waitForFunction(() => { const h = document.querySelector('#cloudBox .h'); return h && /ETKİNLEŞTİR/.test(h.textContent); }, null, { timeout: 20000 }).catch(() => {});
  R.dogrulaEkrani = await p.evaluate(() => { const h = document.querySelector('#cloudBox .h'); return !!h && /ETKİNLEŞTİR/.test(h.textContent); });
  R.hata = await p.evaluate(() => { const e = document.querySelector('#cloudBox .er'); return e ? e.textContent.slice(0, 120) : ''; });
  R.errs = errs; console.log('@@' + JSON.stringify(R)); await b.close();
})();
