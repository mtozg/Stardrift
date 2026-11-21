# Durum ve devam notu (geliştirme duraklatıldı; öncelik asset)

**Tarih:** 2026-11-21 · **Karar (Mehmet):** oyun sonu dilimleri bitince geliştirme tarafı duraklar, öncelik Asset Factory'ye verilir ve tüm çizimler bitirilir; sonra geliştirmeye dönülür. **Nerede kaldığımızı unutma: bu belge.**

## Ana koda alınanlar (main, ≈1.67.9)
Ölçüm paneli (`?tani=1`), açılış çökme koruması düzeltmesi, bakım araçları (işlev envanteri, çevrimdışı liste denetimi), 3B model yükleyici (varsayılan KAPALI, `?glb=1`), Korsan karargahı (Kara Liman'da siviller kaçmaz), Kaşif yan ekranları (Asset Factory düzeltmesi), menü (yetenek ağacı sekmelerin altında, uçuştan kalan uyarılar temizlenir), ekonomi ölçüm aracı, Hayalet hangar oranı, güvenli mod (`?q=0|1|2`), iPad çökme önlemleri (hafif kokpit modeli, piksel sınırı, küçük gökyüzü).

## Açık PR / dallar (Mehmet birleştirir; ben birleştirmem)
- **#60** iPad hızı (piksel bütçesi + büyük dokunmatikte parlama kapalı). **Geçici çözüm**, kalite düşürür; kalıcı çözüm bekliyor (aşağıda).
- **#61** Oyun sonu E1 1. dilim (İstatistikler, Efsane+). **Oyun sonu 2. ve 3. dilim PR'ı** (Bekçi meydan okuması, Kadim Atlas) `claude/stardrift-oyun-sonu2` dalında; #61'i içerir.
- Dallar (PR yok): `claude/stardrift-gemi-glb` ve `claude/stardrift-hangar-glb` (yükleyici: oyuncu gemisi ve hangar koridoru desteği, varsayılan KAPALI; model dosyaları repoda YOK), `claude/stardrift-ekonomi-tur2/3` (ekonomi belgeleri), `claude/stardrift-ipad-arastirma` (Tier 3–4 tasarımı).

## Geliştirme tarafında BEKLEYENLER (sırayla)
1. **iPad hızı, kalıcı çözüm:** akıllı çözünürlük (yalnız yavaşlayınca düşsün) + hafif parlama; gerçek iPad'de `?tani=1` ölçümü (Mehmet'ten ekran görüntüsü) darboğazı gösterir. Şüpheli: kokpit camı gölge bulanıklığı, her karede ekran dokusu yükleme, 4x MSAA'lı parlama.
2. **Tier 3–4 unvan görevleri (A modeli):** tasarım hazır (`docs/TIER34_TASARIM.md`). Kod yok. Kural: görev kredi/XP vermez; yalnız itibar, unvan ilerlemesi, kozmetik. Önce sayaç kaynakları doğrulanacak.
3. **Ekonomi:** ölçüm belgesi `docs/EKONOMI_OLCUM.md` (Tur 1–3 kısmi). Eksik: süre başına kazanç botu, kaçak mal ölçümü, görevler, kalıntı, ölüm ücreti. Bulgu: öldürme kredisi düşman türünden bağımsız (`rand(90,160)`); öneri türe bağlamak, **uygulanmadı**, H1 (geç oyun kredi fazlası) ölçülmeden uygulanmayacak. **Ekonomide hiçbir değer değişmedi.**
4. **Oyun sonu E2 (Yeni Döngü):** tasarım `docs/OYUN_SONU_TASARIM.md`; **kayıt şeması değişikliği içerir, Mehmet onayı şart**, yedek ve geri alma zorunlu. E1 dilimleri (İstatistikler, Efsane+, Bekçi meydan okuması, Kadim Atlas) bitti.
5. **Firebase ve gerçek cihaz testleri:** `docs/FIREBASE_KONTROL.md` ve `docs/QA_GERCEK_CIHAZ.md` hazır; Mehmet'ten Firebase Console ekran görüntüleri ve iPad/iPhone testleri bekliyor. **Hiçbir test gerçek cihazda PASS işaretlenmedi.**
6. **Menü/iPad bellek:** iPad kökeni belirsiz (Safari sekmeyi bellek yüzünden öldürüyordu); #59 sonrası çalışıyor, nedeni %100 doğrulanmadı.
7. **Kara Liman benzeri bölge mekaniği:** başka sınıfın ana haritasına giren oyuncuya devriye uyarısı/kovma: **tasarım notu yazılacak**, sertlik (uyarı/kovma/ceza) Mehmet'in kararı.
8. Ertelenenler (onaylı değil): T3 (ses verisi ertele), T4 (kayıt göçü), T5, T6, T8, T10, T11.

## Asset tarafı (öncelik)
Asset Factory dalı `claude/asset-factory-budget-mode`. Güncel durum ve karar noktaları ayrıca asset yol haritasında; özet:
- **Kaşif kokpit seviyesi pilotu** onaylı (hi-poly + bake hattı, ≈4 derleme, toplam sert üst 22; harcanan ≈16,5). Sonuç şimdiki gemiden iyi değilse teslim sayılmaz.
- Gemi dış modelleri: Şahin m002 ve Hayalet m001 aday, Yük m003 aday (hâlâ şimdikinin turuncu-kahve pas/kontrastından geride), Kaşif reddedildi.
- Hangar koridoru r5 ve kapı: oyunda denendi (r3/r4 şimdikinden kötüydü), r5 henüz oyunda denenmedi. Hangar devamı (iç kapı, iç kabuk) onaylı DEĞİL.
- Aşama 1 grup 1 (NPC, asteroit, Ankora) teslim edildi; oyunda yükleyiciyle görüntülendi, kalan gruplar için onay/plan bekliyor.
- 3. prototip turu kapalı.

## Kurallar (hatırlatma)
Asset Factory talimatları yalnız Mehmet'in kararlarını iletmekle sınırlı; 3B çizim sunmadan önce oyun içi görüntü alınıp gönderilir (K24); gerçek cihazda denenmeyen hiçbir test PASS yazılmaz; PR'ları Mehmet birleştirir; kayıt şeması, Firebase kuralları, veri silme ayrı onay ister.
