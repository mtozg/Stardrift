# Firebase doğrulama kontrol listesi

> Console erişimi ve gerçek hesap gerektiren maddeler Mehmet'ten bekleniyor; hiçbiri doğrulanmış sayılmaz.

Durum: **hazırlık.** Firebase güvenlik kurallarını veya hesap sistemini **değiştirmedim**; Console'a erişimim yok. Aşağıda üç ayrı sınıf var; hiçbir Console ayarını doğrulanmış gibi göstermiyorum.
Proje (koddan): `stardrift-617de` (web anahtarı herkese açık olur; güvenlik **kurallara ve yetkili alan adlarına** bağlıdır).

## A. Kodda doğrulananlar (istemci ne yapıyor)
Kaynak: `js/game.js`, "BULUT HESAP (Firebase)" bloğu. Kütüphane `vendor/firebase/*-compat.js`, yalnız hesap ekranı açılınca yüklenir.

| İşlem | Çağrı | Etkilenen veri |
|---|---|---|
| E-posta ile kayıt | `createUserWithEmailAndPassword` → `updateProfile` (pilot adı) → `sendEmailVerification` (önce `continueUrl` = `location.origin + pathname`, reddedilirse adressiz tekrar; 1.63.2) | Auth kullanıcısı |
| Giriş | `signInWithEmailAndPassword`; doğrulanmamışsa yeni doğrulama gönderir ve girişi **reddeder** (`emailVerified` şart) | - |
| Şifre sıfırlama | `sendPasswordResetEmail` (aynı `continueUrl` yedeği); `auth/user-not-found` sessizce yutulur (hesap var/yok sızdırmaz) | - |
| Google girişi | `signInWithPopup(GoogleAuthProvider, prompt: select_account)` | Auth kullanıcısı |
| Çıkış | `signOut` | - |
| Kayıt yükle/güncelle | `saves/{uid}`: `get` ve `set({ data: <JSON metni>, t: <zaman> })` (en çok 700 bin karaktere kırpılıyor; başarıda `lastPut`) | `saves/{uid}` |
| **Oyunu sıfırla** | `saves/{uid}`: **`delete`** (başarısız olursa sessiz geçer; yeni yerel kayıt daha yeni olduğu için buluta yazılır) | `saves/{uid}` |
| Kayıt kodu al | `signInAnonymously` (oturum yoksa) → `codes/{AAAA-BBBB}`: `set({ data, t, uid })`. Kod: 8 karakter, 31 harflik alfabe (I, L, O, 0, 1 yok) ≈ 2^39,6 olasılık | `codes/*` |
| Kayıt kodu gir | `signInAnonymously` (oturum yoksa) → `codes/{kod}`: `get`; **süre kontrolü yalnız istemcide** (`Date.now() - t > 30 gün` → "bulunamadı") | `codes/*` |
| Açılış eşitlemesi | Oturum varsa `saves/{uid}` `get`; `_t` yerelden >5 sn yeniyse "Buluttaki kayıt daha yeni" sorar; aksi halde yereli buluta yazar (`push`: her 60 sn ve sayfa gizlenince; içerik değişmediyse yazmaz) | `saves/{uid}` |

**Kodda doğrulanan eksikler/riskler (Console'a bakmadan):**
1. **Sunucu tarafı süre dolumu yok:** kayıt kodları 30 gün sonra istemcide "bulunamadı" görünür ama Firestore'da **silinmez** (TTL politikası ve zaman damgası alanı yok).
2. `t` alanı sayı (`Date.now()`); Firestore TTL için `Timestamp` türünde alan gerekir.
3. Kod tahmin güvenliği (39,6 bit) **tek başına** yeterli sayılmaz: kurallar `list`/sorguyu kapatmazsa kodlar taranabilir (aşağıda kontrol).
4. Oyunun kendi 5 sn / 30 gün mantığı sunucuda uygulanmıyor; kurallar yoksa istemci kandırılabilir.

## B. Firebase Console'dan **ekran görüntüsü** gereken (erişimim yok → DOĞRULANAMADI)
Her biri için Console yolu ve **ne aranacağı**:

| # | Console yolu | Aranan | Beklenen / yorum |
|---|---|---|---|
| B1 | Firestore Database > **Rules** (tam metin) | `saves/{uid}` kuralı | Yalnız `request.auth.uid == uid` olan kullanıcıya `read`, `write`; **`delete` dahil** (Oyunu sıfırla için); e-postası doğrulanmış ya da Google kullanıcısı şartı; belge boyutu sınırı |
| B2 | Aynı sayfa | `codes/{kod}` kuralı | Oturum açmış (anonim dahil) kullanıcıya `get` ve `create`; **`list` kapalı**; `update`/`delete` kapalı ya da yalnız sahibine (`resource.data.uid == request.auth.uid`) |
| B3 | Aynı sayfa | Genel kural | `allow read, write: if true;` ya da son kullanma tarihli test kuralı **olmamalı** (süresi geçince tüm erişim kapanır) |
| B4 | Authentication > Settings > **Authorized domains** | `mtozg.github.io` listede mi | **Olmalı.** Yoksa Google girişi (`auth/unauthorized-domain`) ve doğrulama bağlantısının dönüş adresi çalışmaz. `localhost` yalnız yerel test için |
| B5 | Authentication > **Sign-in method** | Etkin sağlayıcılar | E-posta/Şifre **etkin**; Google **etkin**; **Anonim etkin** (kayıt kodu için şart: kapalıysa "Kodla aktarım henüz açılmadı" görünür) |
| B6 | Authentication > Settings > **User actions / Email enumeration protection** | Açık mı | Açık olması önerilir; sızdırmaz. Açıksa kayıtta/girişte bazı hata kodları değişebilir, uygulama metinleri (Türkçe) buna göre kontrol edilmeli |
| B7 | Authentication > **Templates** | Doğrulama ve şifre sıfırlama şablonu dili ve gönderen adı | Türkçe, gönderen ve bağlantı adresi doğru (aksi halde spam'e düşme riski) |
| B8 | **App Check** | Etkin mi, Firestore/Auth zorunlu mu | Etkin değilse not et (web anahtarı herkese açık; kötüye kullanıma karşı ek katman) |
| B9 | Firestore > **Usage** ve Billing planı | Belge sayısı, günlük okuma/yazma, plan (Spark/Blaze), bütçe uyarısı | Kullanım kotası ve beklenmedik fatura riski |
| B10 | Firestore > **Indexes / TTL** | `codes` için TTL politikası var mı | Yok beklenir (A-1) |
| B11 | Project settings > **Your apps** | Web uygulamasının kayıtlı adresleri/anahtar kısıtı (Google Cloud > Credentials > API key > Application restrictions) | Anahtar HTTP yönlendiren kısıtı (`mtozg.github.io/*`) ile sınırlı mı |

**Rules Playground ile kural testi** (Console > Firestore > Rules > Rules Playground; kuralları değiştirmeden okuma/yazma denemesi): her satır için **beklenen sonuç** yazılı; sonuçları sütuna işle.
| # | Simülasyon | Beklenen | Gerçek |
|---|---|---|---|
| P1 | Oturumsuz `get saves/X` | **Reddet** | |
| P2 | Kullanıcı A, `get saves/A` | İzin | |
| P3 | Kullanıcı A, `get saves/B` | **Reddet** | |
| P4 | Kullanıcı A, `set saves/A` (küçük belge) | İzin | |
| P5 | Kullanıcı A, `delete saves/A` | İzin (Oyunu sıfırla için) | |
| P6 | Oturumsuz `get codes/ABCD-EFGH` | **Reddet** | |
| P7 | Anonim kullanıcı, `create codes/ABCD-EFGH` | İzin | |
| P8 | Anonim kullanıcı, `get codes/ABCD-EFGH` (varsa) | İzin | |
| P9 | Anonim kullanıcı, **`list codes`** | **Reddet** | |
| P10 | Başka kullanıcı `update`/`delete codes/ABCD-EFGH` | **Reddet** | |
| P11 | `set saves/A` ile >1 MiB belge | **Reddet** | |

## C. **Gerçek test hesabıyla** doğrulanması gerekenler (Console erişimi gerekmez, internetli cihaz)
Test için tek kullanımlık bir e-posta kutusu ve ayrı bir Google hesabı kullan. Sonuçları tabloya işle (PASS yalnız gerçekten denendiyse).
| ID | Senaryo | Beklenen | Sonuç |
|---|---|---|---|
| F1 | Yeni e-postayla kayıt; doğrulama e-postası gelir, bağlantıya dokun, oyunda "Etkinleştirdim" | Giriş yapılır; kayıt buluta yazılır; bağlantı oyun adresine döner | |
| F1b | E-posta **gelmezse** (Authorized domains/spam) | Oyun "doğrula" ekranında kalır; "Yeniden gönder" çalışır | |
| F2 | Çıkış, yanlış şifre, doğru şifre, şifre sıfırlama e-postası | Türkçe, anlaşılır hata; sıfırlama e-postası gelir | |
| F3 | Google girişi: Safari sekmesinde **ve** ana ekran uygulamasında (PWA) | Safari'de çalışır. PWA'da açılır pencere engellenebilir (bilinen risk): sonucu not et | |
| F4 | İki cihazda aynı hesap: A'da oyna, B'den gir | "Hangi kayıt?" ya da "Buluttaki daha yeni" doğru çıkar; veri kaybı yok | |
| F5 | **Oyunu sıfırla** (hesaplı) | Yerel ve bulut kaydı silinir; yeniden açılışta bulut eski kaydı geri getirmez; hesap oturumu açık kalır | |
| F6 | Kayıt kodu: A'da kod al (anonim), B'de gir | 8 haneli kod çalışır; yanlış kod "bulunamadı"; 30 günden eski kod reddedilir (zamanı elle ayarlamadan denenemez: not et) | |
| F7 | Çevrimdışı oyna (uçak modu), sonra internete bağlan | Eşitleme sessiz, kayıp yok, hata penceresi yok | |
| F8 | Çok büyük kayıt (uzun oyun, ≥500 KB JSON) | Buluta yazılır ya da anlaşılır uyarı; çökme yok | |
| F9 | Hesap açıkken tarayıcı site verisini sil, tekrar giriş yap | Buluttaki kayıt geri gelir | |

## D. Mehmet'ten istenenler (sırayla)
1. B1-B5'in ekran görüntüleri (en önemlisi B1 ve B4).
2. Rules Playground P1-P11 sonuçları (ya da yalnız B1'in tam metni; testi ben tablolarım).
3. Test e-postası ve hesabıyla F1-F7; her biri için sonuç.
4. Kurallar açıksa ya da `codes` taranabiliyorsa **önce kuralları kapat, sonra test**; ben kural metni **taslağını** hazırlayabilirim (uygulama senin onayınla, Console'dan).

## E. Bilinen açık sorular
- Eski **"Claude hesabına bağlı" bulut modülü** (`js/game.js` ~6015-6060, `save.ts`) bu yayında etkin mi? Etkinse aynı kaydı iki sistem yazar (T5).
- Anonim oturumlar zamanla birikir (her kod alımı için bir kullanıcı); temizleme politikası yok **[doğrulanamadı]**.
