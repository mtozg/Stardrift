# GLB yükleyici (prototip hazırlığı, varsayılan KAPALI)

Sürüm 1.67.0. Amaç: Asset Factory'nin gerçek 3B modelleri (NPC, asteroit, istasyon) geldiğinde oyunda hemen denenebilsin. **Bu sürümde oyun deneyimi değişmez:** yükleyici varsayılan olarak kapalıdır ve hiçbir model oyuna eklenmedi.

## Açma / kapama
- `?glb=1` açar (ve bu cihazda hatırlar), `?glb=0` kapatır. Kapalıyken `js/glb.js` hiç indirilmez.
- Model listesi `models/glb/index.json` dosyasından okunur. Dosya yoksa ya da liste boşsa hiçbir şey denenmez; oyun bugünkü gibi çalışır.

## Yedek zinciri
GLB → mevcut kabuk model (`npc3D`/istasyon kabuğu) → iki düzlem çizim → ilkel gövde. GLB yüklenemezse (dosya yok, bozuk, ağ hatası) o model oturum boyunca denenmez (60 sn sonra tek yeniden deneme) ve oyun mevcut modelle devam eder. NPC hemen doğar; GLB hazır olunca kabuğun yerine geçer (yükleme oyunu bekletmez).

## Model sözleşmesi
- Burun **+Z**, yukarı **+Y**, uzunluk **1,0 birim** (oyun `NPC_DEF.L` ile ölçekler; çarpışma yarıçapı değişmez).
- Çapa düğümleri: `ANCH_ENG_*` (motor alevi), `ANCH_NAV_*` (seyir ışığı), `ANCH_MUZ_*` (namlu). Eksikse mevcut varsayılan konumlar.
- Detay kademeleri: `LOD0` ve `LOD1` grupları (LOD1 yoksa LOD0 kullanılır).
- Asteroit: `AST_<tür>_<n>` (varyasyonlar) ve `PICK_<tür>`; tür adları oyundakiyle aynı (`titan`, `demir`, `buz`, `kristal`, `hurda`).
- `index.json` anahtarları: `npc_<tür>` (örn. `npc_raider`), `ast_<tür>`, `st_<istasyon>` (örn. `st_ankora`); her giriş `{ "url": "...", "urlM": "... (telefon için isteğe bağlı)", "rot": [x,y,z], "s": ölçek }`.

## LOD (detay kademesi)
- **NPC:** gemi uzunluğuna oranla: yakın (<12×L) LOD0; orta (<40×L) LOD1; uzak mevcut kabuk. Geçişte %10 histerezis. "Performans" kalitesinde mesafeler yarıya iner.
- **İstasyon:** <3 km LOD0; <10 km LOD1; ötesi mevcut kabuk.
- **Asteroit:** ≤1200 m (Performans'ta 600 m) örnekli model; ötesi bugünkü sprite.

## Asteroit örnekleme (instancing)
Her asteroit için mevcut sprite yedek olarak kalır (oyun kodu `a.mesh` ile aynı şekilde çalışır). Yakındaki asteroitlerde sprite gizlenir ve çok sayıdaki kaya tür/varyasyon başına tek `InstancedMesh` ile çizilir (varyasyon başına en çok 128 örnek, kalan sprite kalır). Her karede örnek matrisleri yeniden yazılır (≈230 kaya). Vuruş parlaması sprite rengini örnek rengine yansıtır. Kaya kalmayınca örnekler sıfırlanır.

## Bilinen sınırlar (dürüst)
- Test edilenler: sahte model dosyaları (otomatik test) ve Asset Factory prototip dosyalarının oyunda bir kez ekran görüntüsüyle denenmesi. **Gerçek cihazda ve performans olarak ölçülmedi.**
- Prototip modeller oyunda **karanlık** görünüyor (sahnede ortam yansıması yok, malzemeler metalik); malzeme/ışık ayarı prototip değerlendirmesinde ele alınacak. Bu PR malzemeyi değiştirmez.
- NPC'de vuruş/hasar parlaması paylaşılan malzemede yok (yalnız sprite asteroitlerde yansıtılıyor).
- Pickup (`PICK_*`) henüz kullanılmıyor.
- İstasyon yönü model dosyasındaki `rot` ile ayarlanır; gerçek Ankora modeli için doğrulanmadı.

## Test
`tools/qa/glb_yukleyici.js` (sahte modellerle): kapalıyken iz yok; model listesi yokken yedek zincir ve hata yok; model varken NPC değişimi, LOD geçişi, asteroit örnekleme (uzaktayken sıfırlanma dahil), istasyon, 60 doğma/ölme sonrası geometri sayısının GLB kapalıyken ölçülen tabanı aşmaması; `?glb=0` kapatması. Sahte dosyalar `tools/qa/glb_fixture.py` ile test sırasında üretilir (depoya ikili dosya eklenmedi).
