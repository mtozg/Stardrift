# Stardrift kokpit modelleme (Blender / bpy)

Parametrik, yeniden üretilebilir kokpit hattı. Oyun dosyalarına dokunmaz.

```
python tools/cockpit/anchors/build_anchors.py kasif                 # onaylı çizimden cam çokgenleri + ekran düzlemleri
python tools/cockpit/blender/build_cockpit.py --ship kasif --stage all --views pilot,oblique,close --verify --export
```
Gereksinim: `pip install bpy scikit-image scipy pillow numpy` (bpy 5.3 ile denendi).

* `anchors/<gemi>.json` — pilot kamerası (74° dikey FOV, asal nokta 800,239.5 / 1600x656), cam çokgenleri, ekran 3B köşeleri.
* `params/<gemi>.json` — ölçüler ve parça ayarları.
* `blender/lib/` — canopy (kabuk+cam açıklıkları), dash (dashboard+ekran yuvaları+ekran mesh'leri), seat, detail, materials, render, bake, verify.
* Ekranlar `SCR_SYS`, `SCR_RADAR`, `SCR_HULL` adlı boş, ayrı mesh'ler; camların önünde/arkasında geometri yoktur (verify: göz→cam ışın testi).
* Çıktılar `out/` (git dışı).
