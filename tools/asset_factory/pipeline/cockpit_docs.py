"""Kokpit ailesi teslim belgeleri: integration.md (kokpite özel, GEÇİCİ, kod yok), teslim_raporu.md, kasif_uyumluluk.md.
factory.py deliver tarafından çağrılır; yalnızca teslim klasörüne yazar."""
import os


def _p(v, d=1):
    return ('%%.%df' % d % v).replace('.', ',')


def write(out, asset_id, rev, glb_name, R, compat, reg, candidate=False):
    st, info, perf = R['stats'], R['three']['info'], R.get('perf') or {}
    items = {i['id']: i for i in R['items']}
    val = lambda k, d=None: items.get(k, {}).get('value', d)
    b = (compat or {}).get('butce', {})
    yn, ks = b.get('yeni', {}), b.get('kasif', {})
    frozen = reg.get('frozen') or {}

    # ---------- integration.md ----------
    scr = {i['id'].split('.')[1]: i for i in (compat or {}).get('items', []) if i['id'].endswith('boyut_px')}
    radar = scr.get('SCR_RADAR', {})
    open(os.path.join(out, 'integration.md'), 'w', encoding='utf-8').write("""# %(id)s r%(rev)03d — kokpit entegrasyon notu

> **GEÇİCİ · KOD YOK.** Bu belge oyuna hiçbir şey eklemez. Entegrasyon (Kapı 3) ayrı onayla, ana sohbette yapılır.
> Ana oyun kodu ve `main` dalı değiştirilmedi.

## Dosya
- `%(glb)s` — tek dosya, dokular gömülü (`EXT_texture_webp`). three r128 GLTFLoader okur.
- GLTFLoader şu an yalnızca `claude/bold-bardeen-oqf73o` dalında (Kaşif ?ck=b yolu); `main`de yok.

## Kamera sözleşmesi (Kaşif ile aynı — doğrulandı)
- Göz orijinde, ileri −Z, +Y yukarı, birim metre. Model ölçeklenmez/eğilmez/kaydırılmaz.
- Dikey FOV 74°, odak 435,27 px, asal nokta (800, 239,5) — 1600×656 referans çerçevesinde; three'de `setViewOffset(w, h, 0, −shift_y·h, w, h)`, shift_y = −(0,5 − 239,5/656).
- Göz salınımı (sway) Kaşif'teki gibi uygulanabilir; QC iki ek göz noktasında (sol −7 cm; sağ +7 cm / alt −4 cm) ölçüldü.

## Canlı ekranlar
- `SCR_SYS` → bars, `SCR_RADAR` → map, `SCR_HULL` → hull (dalın renderB/buildB'sindeki ada göre bağlama; traverse).
- Her biri tek dörtgen, 4 köşe; UV sol-üst (0,0), sağ-alt (1,1) → CanvasTexture `flipY=false`.
- Dosyadaki `MAT_screen` yer tutucudur (koyu camgöbeği emisyon); oyun MeshBasicMaterial + canvas ile değiştirir.
- **Dikkat — RADAR oranı:** Şahin RADAR %(rw)s×%(rh)s px (≈ %(ra)s:1), Kaşif %(kw)s×%(kh)s px (≈ %(ka)s:1). Kaşif'e göre çizilmiş canvas
  içeriği gerilebilir; entegrasyonda canvas boyutu ekran oranına göre seçilmeli (r008 tasarım kararı: daha büyük, yakın, yüksek ekranlar).

## Gemiye göre seçim
- Daldaki kod Kaşif'e bağlı (`save.ship === 'kasif'`, `models/cockpit_kasif.glb`). Şahin için gemi → GLB eşlemesi gerekir (ör. `models/cockpit_sahin.glb`).
  Bu genelleştirme Kapı 3'te, onayla yapılır.

## Malzeme ve ışık
- `MAT_body` (base 2048 + ORM 1024 + normal 1024), `MAT_emit` (düz emisyon ≤ 1; parlaklık bloom'dan — r128'de emissive_strength yok), `MAT_screen`.
- Oyun Kaşif'te envMapIntensity 0,9 atıyor; Şahin aynı ayarla QC'deki nötr ışıkta Blender'a ΔE ≈ 3 içinde.
- Tangent dosyada yok; three çalışma anında üretir (validator uyarısı; Kaşif'te de var).
- Model gözün arkasına uzanır (koltuk, z en çok +0,64 m): kamera önünde görünmez, zararsız.

## Fallback ve çevrimdışı
- GLB yüklenemezse mevcut kokpit davranışı korunmalı (eski 2D/parallax **yeni üretimde kullanılmaz**; yalnız mevcut oyunun kendi fallback'i).
- Dosya yerel paketle gelir; ağ gerektirmez.

## Test
- `qc/viewer/check.html` (otomatik, Three r128) ve `qc/viewer/bench.html?glb=…` (gerçek cihaz ölçümü — henüz yapılmadı).
""" % dict(id=asset_id, rev=rev, glb=glb_name, rw=radar.get('value', ['?', '?'])[0], rh=radar.get('value', ['?', '?'])[1],
           ra=_p(radar['value'][0] / radar['value'][1], 2) if radar else '?', kw=radar.get('kasif', ['?', '?'])[0], kh=radar.get('kasif', ['?', '?'])[1],
           ka=_p(radar['kasif'][0] / radar['kasif'][1], 2) if radar else '?'))

    # ---------- teslim_raporu.md ----------
    tex_rows = '\n'.join('| %s | %s | %s KB |' % (k, '×'.join(map(str, v['size'])), _p(v['kb'])) for k, v in st['textures'].items())
    cmp_rows = '\n'.join('| %s | %s %% | %s / %s | %s %% |' % (c, _p(v['lum_diff'] * 100), _p(v['deltaE_mean']), _p(v['deltaE_p95']), _p(v['silhouette_diff'] * 100, 2))
                         for c, v in R['three_vs_golden'].items())
    perf_rows = '\n'.join('| %s | %s ms |' % (k.split('.')[1], _p(v['value'])) for k, v in items.items()
                          if k.startswith('perf.') and k.endswith('.n1') and v.get('value') is not None)
    s = R['summary']
    open(os.path.join(out, 'teslim_raporu.md'), 'w', encoding='utf-8').write("""# %(id)s r%(rev)03d — teknik teslim raporu

**Durum:** %(state)s **Oyuna entegre edilmedi** — Kapı 3 ayrı onay bekliyor.

## Ana ölçüler
| Ölçü | Şahin r%(rev)03d | Kaşif (referans) | Bütçe (kokpit) |
|---|---|---|---|
| GLB dosya boyutu | %(kb)s KB (%(bytes)s bayt) | %(kkb)s KB | ≤ 4 MB |
| Üçgen (three, görünen) | %(tris)s | %(ktris)s | ≤ 60 bin |
| Draw call (three, sahnede) | %(calls)d | %(kcalls)s | — |
| ↳ statik gövde (ekranlar hariç) | %(calls0)d | — | — |
| Doku girişi / görsel | %(tex)s / %(img)s | %(ktex)s / %(kimg)s | giriş ≤ görsel |
| GPU doku belleği (RGBA8 + mip tahmini) | %(gpu)s MB | ≈ %(kgpu)s MB | ≤ 40 MB |
| Malzeme | %(mat)s | %(kmat)s | — |

Draw call: 2 statik gövde çağrısı (`MAT_body`, `MAT_emit`) + 3 canlı ekran (`SCR_*`, oyunun canvas'ı için ayrı kalmak zorunda) = %(calls)d.
GPU tahmini three r128 davranışına göredir: her doku girişi ayrı yüklenir (Source paylaşımı r138'de geldi). Kaşif'in 24 girişi 4 görseli paylaşıyor; r128'de bu ≈ %(kgpu)s MB'a çıkar.

## QC
- Karar: **%(verdict)s** — PASS %(p)d · WARN %(w)d · FAIL %(f)d · SKIP %(sk)d.
- WARN: `gltf.validator_warnings` (tangent yok; Kaşif'te de var) — Kapı 2'de kabul kararı kullanıcınındır.
- Kokpit: cam oranı %%%(glass)s · HUD bölgesi kapanma %%%(hud)s · ekran görünürlüğü SYS %(v1)s, RADAR %(v2)s, HULL %(v3)s · kamera sapması 0 px.
- Doku yoğunluğu (texel) hedef 240 px/m (Kaşif 239 px/m'den kalibre) üzerinde.

## Blender (Cycles, nötr ışık) ⟷ Three.js r128
| Kamera | Parlaklık farkı | ΔE ort. / p95 | Siluet farkı |
|---|---|---|---|
%(cmp)s

## Performans (Playwright swiftshader, n=1 — bilgi amaçlı, kapı değil)
| Profil | Kare süresi |
|---|---|
%(perf)s

Gerçek cihaz ölçümü yapılmadı (`bench.html` ile entegrasyon öncesi önerilir).

## Dokular
| Doku | Boyut | WebP |
|---|---|---|
%(texrows)s

## Kaşif uyumluluğu
%(cp)s PASS · %(cf)s FAIL · %(ci)s INFO — ayrıntı `kasif_uyumluluk.md`.

## Paket içeriği
- `%(glb)s`, `textures/` (GLB'deki WebP'lerin kopyası)
- `preview/` — Blender: `hero` (pilot), `hero_rear` (çapraz), `closeup` (konsol), `koltuk`, `dis`, `ortho_6` (plan); nötr altın `blender_notr_*`;
  Three r128: `three_r128_*`; yan yana `three_vs_blender_*`
- `qc_report.json/html`, `kasif_uyumluluk.json/md`, `manifest.json`, `source.json`, `spec_sheet.md`, `integration.md`
- Süreler: model %(tm)s s · hazırlık %(tp)s s · QC %(tq)s s
""" % dict(id=asset_id, rev=rev, state=('Görsel: %s **TESLİM ADAYI** — Kapı 2 teknik onayı kullanıcıdan bekleniyor; bu paket onay yerine geçmez.' if candidate
                                  else 'Görsel: %s Teknik onaylı teslim paketi.') % frozen.get('not', 'dondurma kaydı yok'), kb=_p(st['glb_bytes'] / 1024), bytes='{:,}'.format(st['glb_bytes']).replace(',', '.'),
           kkb=_p(ks.get('bayt', 0) / 1024, 0), tris='{:,}'.format(info['triangles']).replace(',', '.'), ktris='{:,}'.format(ks.get('ucgen', 0)).replace(',', '.'),
           calls=info['calls'], kcalls='%s primitive' % ks.get('primitive', '?'), calls0=st['calls_lod0'], tex=yn.get('doku_girisi'), img=yn.get('gorsel'),
           ktex=ks.get('doku_girisi'), kimg=ks.get('gorsel'), gpu=_p(st['tex_gpu_bytes_est'] / 1048576), kgpu=_p(ks.get('gpu_mb_tahmin', 0), 0),
           mat=yn.get('malzeme'), kmat=ks.get('malzeme'), verdict=R['verdict'], p=s['PASS'], w=s['WARN'], f=s['FAIL'], sk=s.get('SKIP', 0),
           glass=_p(val('cockpit.glass_ratio', 0)), hud=_p(val('cockpit.hud_zone_block', 0)), v1=val('cockpit.screen_visible.SCR_SYS'),
           v2=val('cockpit.screen_visible.SCR_RADAR'), v3=val('cockpit.screen_visible.SCR_HULL'), cmp=cmp_rows, perf=perf_rows or '| — | — |', texrows=tex_rows,
           cp=(compat or {}).get('ozet', {}).get('PASS', '?'), cf=(compat or {}).get('ozet', {}).get('FAIL', '?'), ci=(compat or {}).get('ozet', {}).get('INFO', '?'),
           glb=glb_name, tm=R['timings'].get('model'), tp=R['timings'].get('prepare'), tq=R['timings'].get('qc')))

    # ---------- kasif_uyumluluk.md ----------
    if compat:
        rows = '\n'.join('| `%s` | %s | %s | %s | %s |' % (i['id'], i['status'], str(i['value'])[:70], str(i['kasif'])[:70], i['note']) for i in compat['items'])
        open(os.path.join(out, 'kasif_uyumluluk.md'), 'w', encoding='utf-8').write("""# %s r%03d ⟷ Kaşif — sözleşme uyumluluğu

Kaşif GLB'si (`models/cockpit_kasif.glb`, dal `claude/bold-bardeen-oqf73o`) yalnızca okundu; değiştirilmedi.
Karşılaştırma oyunun `?ck=b` yolunun beklentilerine göredir (ekran adları, UV yönü, kamera, ölçek, uzantılar, malzeme).
Tasarım kopyalanmadı: ekran boyutu/konumu farkları INFO olarak kayıtlıdır.

**Özet:** %s

| Kontrol | Durum | Şahin | Kaşif | Not |
|---|---|---|---|---|
%s
""" % (asset_id, rev, ' · '.join('%s %s' % (k, v) for k, v in compat['ozet'].items()), rows))
