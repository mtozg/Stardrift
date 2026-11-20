# hayalet_cockpit r003 — aday teslim dosyaları (Mehmet geri bildirimi; r001/r002 dosyalarına dokunulmadı)

Kapsam: ekranlar büyütüldü ve ekran bandı alta/koltuğa yaklaştırıldı; kabartma çerçeveli oyuklu ekran yuvaları; 3 kademeli konsol yüzü (ekran bandı, orta basamak, alt şerit); omuz blokları ve havalandırma ızgaraları; kablo kanalları; oluklu kemer/direkler (kalınlık+gölge); altıgen güverte koyu/alçak; koltuk r002 ile aynı (~140 px). Resmi Kapı/registry kaydı YOK.

| Dosya | Boyut | SHA256 |
|---|---|---|
| sd_hayalet_cockpit_r003.glb (masaüstü/tablet) | 1179132 B | 3ce380c2c472c239cf4c5d9cbf1d749a3045f5b26da8e1565836c10b3e9bbd7c |
| sd_hayalet_cockpit_r003_m.glb (telefon) | 1003420 B | 55f4cee1867ded69f4d0853ad188aa43cc16954e47fc103cd85d777d251f1ae2 |

Oyunda: models/cockpit_hayalet.glb, models/cockpit_hayalet_m.glb. CK3 girdisi: ck3_hayalet.json (top 358, q, ridge; ridge sağ-sol simetrik).
YENİ ekran köşeleri (SYS, RADAR, HULL; 1600×656): q = [[[300, 388], [590, 372], [590, 514], [290, 552]], [[620, 366], [980, 366], [994, 506], [606, 506]], [[1010, 372], [1300, 388], [1310, 552], [1010, 514]]]
Oranlar: SYS 1,94 · RADAR 2,66 (oyunda 2,657; kabul 2,2–2,8) · HULL 1,94.
Teknik: 13.389 üçgen, 5 draw call, GPU 32 MB, HUD bölgesi %7,5 (probe; hedef ≤%8), ekran hizası 0,03–0,05 px (oyun içi), verify 12/12, ortada dikme yok.
