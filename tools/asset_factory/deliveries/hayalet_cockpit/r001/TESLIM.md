# hayalet_cockpit r001 — PRODUCTION aday teslim dosyaları (entegrasyon için)

Durum: Mehmet PREVIEW onayı (Lead aktarımı) sonrası tek PRODUCTION derlemesi (+1 düzeltme turu kullanıldı). **Resmi Kapı 1 (production) / Kapı 2 / registry kaydı YOK**; yalnız GLB + CK3 verisi.

| Dosya | Boyut | SHA256 |
|---|---|---|
| sd_hayalet_cockpit_r001.glb (masaüstü/tablet, 2048 base) | 1426780 B | b7538903e84c60fd125898b424b3a3319e21d5c48022e7ee1c3d5c934cece652 |
| sd_hayalet_cockpit_r001_m.glb (telefon, 1024 base) | 1224508 B | 3198e5195e6374cf7923cdca4b827d70a30b318ade3ec7294dcb596942edbe3a |

Oyunda: models/cockpit_hayalet.glb ve models/cockpit_hayalet_m.glb; CK3.hayalet girdisi ck3_hayalet.json ({top, q, ridge}).

Ekran köşeleri (1600×656; SYS, RADAR, HULL): q = [[[376, 382], [596, 381], [596, 486], [330, 522]], [[644, 374], [956, 374], [972, 490], [628, 490]], [[1002, 381], [1224, 384], [1272, 522], [1002, 488]]]
RADAR oranı 2,80:1 (oyunda tuval 2,798). Ekran adları SCR_SYS/SCR_RADAR/SCR_HULL, UV sol-üst (0,0).
Sırt (ridge): pilot görüşü alfa maskesinden (yöntem: Şahin/Yük teslim notları). top = 358.
Teknik: 15.223 üçgen, 5 draw call, GPU 32 MB, HUD bölgesi %9,0 (probe), ekran hizası 0,02–0,04 px (oyun içi), verify 12/12. Statik (ART/SOCK yok).
