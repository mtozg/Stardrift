# NPC sert-yüzey r2 — 8 tür (STD kademesi, her biri 12,3 MB GPU)
Dosyalar: sd_npc_{raider,brute,reaver,corvette,courier,cargo,tanker,mining}.glb (+ pano.png, <tür>_{on34,arka34,ust,yan}.png). Khronos 0 hata. Konseptleri referansa (endüstriyel modüler: kafes motor kuleleri, silindirik tanklar, açık çerçeve, turuncu yamalar) uygun AF seçti.
Lead'in oyun içi karanlık geri bildirimine göre düzeltmeler:
- ORM ölçülen ortalamalar (AO / pürüzlülük / metal): yeni 0,90 / 0,87 / 0,02 — mevcut raider 0,99 / 0,82 / 0,02. (Önceki r1: 0,65 / 0,64 / 0,24 → yüksek metal ve güçlü AO oyunda koyu uzayı yansıtıp siyaha düşüyordu.) Malzemeler pir_*: metal 0, rough 0,74–0,92; hi-poly kenar metali 0; AO yalnız çatlakta (lift 0,75, albedoya gömme 0,1).
- Albedo ort. 0,36–0,49 (mevcut raider 0,16 atlas ortalaması, boş alan dahil); gölge tarafı için açık gri/turuncu.
- Emissive: nav ışıkları 0,05→0,14 m, pencere ışıkları büyütüldü, yan ince ışık şeritleri, kokpit camı emissive (pir_glass), motor çekirdeği.
- Akbaba radyatörü "masa" yerine dikey kanatçıklar + ısı borusu.
Tür özeti: raider (çalıntı çekirdek+kafes kule), brute (zırhlı kama gambot, 3 kule), reaver (asimetrik kurtarma mavnası+vinç), corvette (devriye: sensör direği+radar, hangar), courier (küçük sivil: çanak anten, çift nacelle), cargo (konteyner çerçevesi), tanker (4 silindirik tank + boru), mining (ön matkap kolları + hazne).
DÜRÜST zayıf yanlar: (1) çoğu türde turuncu çizgili burun konisi tekrar ediyor → aile benzerliği fazla; (2) nav küpleri bazı türlerde gövdeden hafif havada; (3) cargo UV doluluğu %15, texel yoğunluğu 61 px/m (diğerleri 115–167) → daha bulanık; (4) oyun içi NPC kıyası yapılmadı (AF harness'ı NPC kadrajlayamıyor) — Lead ölçsün. Puanlama (a–g) tür başına ~27/35.
