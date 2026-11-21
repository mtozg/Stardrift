# Şahin — modelleme turu m001 (Kapı 1 onaylı: ikiz motor; kanopi oyundaki Şahin kokpiti gibi damla fanus)
`sd_ship_sahin.glb`: burun +Z, L=1,0, merkez orijin, LOD0/LOD1, 1 malzeme (base 1024 / ORM 512 / normal 512 / emissive 1024), normal haritası VAR, ANCH_ENG_1..2 (çan içi çekirdek, yön −Z), ANCH_NAV_1..3, ANCH_MUZ_1..2. Üretim yolu Yük ile aynı (prosedürel malzeme → UV → bake → LOD).
Sayılar: LOD0 2162 / LOD1 634 üçgen (≤6k; Yük kadar ayrıntı eklenebilir), dosya 0,37 MB, texel ≈ 64 px/m (Yük'ün 2 katı), UV doluluğu %49.
Kanopi: geniş cam kabarcık + 3 enine koyu kemer + boyuna orta kemer + kırmızı kenar şeridi (cockpit_sahin r012/r014'teki fanus kemerleri ve kırmızı kenar çizgisine göre). Cam çerçeve şekli birebir referans alınmadı (kokpit GLB'sinde dış kabuk yok; pilot görüşündeki kemer geometrisinden uyarlandı).
## Ölçüt durumu
1 panel/pah/mikro ayrıntı: KISMEN (panel+aşınma dokuda; kapak, menteşe, panjur, flap/aileron, pylon geometride; cıvata sıraları yok, pah az) · 2 malzeme: VAR (beyaz/gri boya, orta gri, koyu, kırmızı, çelik, gunmetal, lastik, cam, is, emissive) · 3 aşınma/kir: VAR dokuda, nozul çevresinde is bellerde, gövdede zayıf · 4 cam: KISMEN (büyük kabarcık, iç yansıma yok) · 6 küçük parçalar: KISMEN (pitot, kanat ucu lambaları, top namluları, kapak menteşeleri).
## Dürüst zayıflıklar
Kanatlar hâlâ düz levha gibi (kök kaplaması/nervür az, uç kalın kenarlı), gövde yan yüzleri sade, kokpit camı düz mavi, panel çizgileri yapay düzgün. Hayalet/Kaşif ile aynı hat; oyun içi hangar karşılaştırması Lead'in sahnesinde yapılacak (ben denemedim).
Not: Yük'ün m001 GLB'si ince levha normal yönü hatası düzeltmesinden ÖNCE üretildi (kuyruk/kanat levhaları etkilenmemiş olabilir); Yük düzeltme turunda aynı düzeltme uygulanacak.
