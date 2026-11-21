# Hayalet — modelleme turu m001 (Kapı 1 onaylı: ikiz motor, cam yönü konsepttekiyle)
`sd_ship_hayalet.glb`: burun +Z, L=1,0, merkez orijin, LOD0/LOD1, 1 malzeme, normal VAR (oyuncu gemileri için onaylı), ANCH_ENG_1..2 (çan içi çekirdek, yön −Z), ANCH_NAV_1..3, ANCH_MUZ_1. LOD0 1481 / LOD1 428 üçgen, 0,28 MB, texel ≈120 px/m (gemi küçük, 6 m), UV doluluğu %51.
İnce/alçak yüzeyli gövde (sekizgen kesit), mor tonlu yüzeyli kokpit camı + çelik kemerler, yarı-delta kanatlar (mor kenar şeridi, panel/flap, uç finler), ikiz mor çekirdekli kaburgalı çan, küçük kuyruk, yan hava girişleri, panjur/kapaklar.
## Oyun içi hangar karşılaştırması (AF kendi testi; deliveries/gemi_dis_yeni/karsilastirma/hangar_hayalet.webp, sol şimdiki / sağ yeni)
Şimdiki gemi: gri metalik, 4 küçük motor, gerçekçi panel dokusu. Yeni: koyu, ince, mor ışık çizgileri + ikiz mor alev; silüet ince/kısa-orantılı doğru okunuyor; ayrıntı yoğunluğu şimdikinden GERİ (düz paneller, belirgin mor şeritler kalın). Karar: ADAY (kimlik/motor sayısı kararına uygun), 'şimdikinden iyi' denemez — ayrıntı için aynı hi-poly bake hattı gerekir.
## Ölçüt durumu
Malzeme çeşitliliği VAR (gunmetal/gri, panel, koyu, çelik, lastik, cam, is, mor emissive); panel/mikro ayrıntı KISMEN; cam KISMEN (iç yansıma yok); küçük parçalar KISMEN (pitot, kuyruk lambası, panjur).
Zayıf: mor şeritler fazla parlak/kalın, gövde yan yüzü sade, kanat düz levha, mor çekirdek lookdev'de soluk.
