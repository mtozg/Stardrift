# Yük Devi — modelleme turu m001 (Kapı 1 onaylı konsept c001 üzerinden)
Dosya: `sd_ship_yuk.glb` (nihai GLB sözleşmesi: burun +Z, uzunluk 1,0, merkez orijin, LOD0/LOD1, tek malzeme, ANCH_ENG_1..6 / ANCH_NAV_1..4 / ANCH_MUZ_1). Görseller: `pano.png` + `v_*.png` (Blender lookdev; oyun içi karşılaştırma Lead'in sahnesinde).
Üretim: kokpit hattının prosedürel malzeme kütüphanesi (boya/çelik/lastik/cam/konteyner varyantları/is) → UV → bake (base + ORM + normal + emissive) → LOD.

## Sayılar
LOD0 5166 / LOD1 1505 üçgen (≤6k) · 1 malzeme · normal haritası VAR (kokpit GLB'leri gibi; NPC sözleşmesindeki "normal yok" bu gemi için esnetildi — Lead onayı gerek) · dosya 0,68 MB · doku 1024 base / 512 ORM / 512 normal / 1024 emissive · GPU ≈ 14 MB (emissive 256'ya inerse ≈ 8,4 MB; bir sonraki turda yapılır) · texel yoğunluğu ≈ 30 px/m (model 15,6 m) ≈ 0,5 px/cm: yakın planda yumuşak.

## Kabul ölçütü durumu (Lead 2026-11-21)
1. Düz renk bloklar yok / panel dikişleri / pah / mikro ayrıntı: KISMEN — prosedürel panel+aşınma+kir haritası ve geometrik ayrıntı (kapak, menteşe, panjur, boru, korkuluk, lamba, kelepçe) var; cıvata sıraları çoğunlukla dokuda noktalar halinde; pah yalnız birkaç parçada gerçek geometri. Gövde alt yüzü detaylandı (servis kapakları, panjur) ama hâlâ sade.
2. Malzeme çeşitliliği: VAR — boya, çıplak çelik, lastik/conta, cam, turuncu zırh, uyarı boyası, is; roughness/metalness değişimi ve aşınma/kir/yağ izi dokuda. Nozul çevresi is: bellerin arka yarısı is malzemesi; çevre gövdede belirgin is lekesi YOK.
3. Konteynerler farklı/kullanılmış: KISMEN — 5 farklı renk/pas varyantı, kaburga, bağlama kayışı, kimlik plakası; renk solması/işaret yazısı yok.
4. Cam şeritler büyük/kokpitle tutarlı: KISMEN — yanlarda 3 geniş pano + üst ön cam + ön cephe cam, lastik conta ve çelik dikmeli; içte yansıma yok (tek malzeme sınırı), cam düz mavi.
5. Kıskaç mekanik ayrıntı: KISMEN — piston, hidrolik gövde, kablo, bilek halkası, diş; hâlâ ince/kaba, eklemler tek parça (ART_ eklemli hareket yok).
6. Ölçek hissi küçük parçalar: VAR — anten, seyir lambaları, korkuluk, merdiven/panjur, kelepçe, sensör braketi.
Nozul çekirdekleri: ANCH_ENG_1..6 çan içi çekirdek diskin (emissive) hemen arkasında, yön −Z (geri); oyunda alev bu noktalara bağlanabilir.

## Dürüst zayıflıklar
- Oyuncak izlenimi azaldı ama bitmedi: gövde düz yüzeyli büyük kutular, panel çizgileri düzgün/yapay; texel yoğunluğu düşük.
- Dokularda UV doluluğu %39 (verimsiz); 2048 base seçeneği GPU ≈ 34 MB yapar — mobil için uygun değil, karar sende/Mehmet'te.
- Cıvata/rivet geometrisi yok (üçgen bütçesi).
- Oyun içi hangar yakın plan karşılaştırması Lead'in sahnesinde yapılacak (ben denemedim).
