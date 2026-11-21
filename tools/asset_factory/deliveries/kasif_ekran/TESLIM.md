# Kaşif yan ekran düzeltmesi (Mehmet isteği; prototip turu değil)

Orijinal models/cockpit_kasif*.glb DEĞİŞMEDİ (salt okunur referans); bu klasördeki dosyalar türetilmiş kopyalardır.
Değişiklik (pipeline/screen_warp.py): SCR_SYS ve SCR_HULL ekran + çevre gövde tepe noktaları pilot kamera uzayında, eski dörtgen → yeni dörtgen homografisiyle (yumuşak ağırlık) taşındı: ekran %18 büyük, yamukluk %50 azaltıldı. RADAR ekranı ve diğer her şey aynı. SCR_* adları, köşe sırası, UV (sol-üst 0,0) aynı.

| Dosya | Boyut | SHA256 |
|---|---|---|
| cockpit_kasif.glb | 3912056 B | 47521199b5d9b64d5ff2ad9bd199a3a1537a9501be94ac7a85d5f7638cac4be7 |
| cockpit_kasif_m.glb | 2526456 B | a290cce318517c2e36dbfcb010a750565981f39fec557b2b94f9f932b927f625 |

Ekran köşeleri (1600×656; TL,TR,BR,BL), ESKİ → YENİ:
- SCR_SYS: [[393,411],[565,393],[558,504],[342,525]] → [[350,392],[583,382],[579,525],[320,537]]
- SCR_HULL: [[1032,393],[1206,411],[1257,525],[1042,504]] → [[1013,382],[1249,392],[1279,537],[1019,525]]
- SCR_RADAR: değişmedi [[628,369],[974,370],[975,508],[624,508]]
Oyunda Kaşif için hiza referansı (qc/ingame_cockpit.js REF) ve varsa CKP/scrK dörtgenleri bu yeni köşelere güncellenmeli (güncellenene dek hiza testi ~57 px sapma gösterir; görsel doğru).
