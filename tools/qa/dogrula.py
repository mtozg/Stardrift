#!/usr/bin/env python3
"""Stardrift oyun içi regresyon testlerinin çıktısını (@@JSON satırı) beklenen değerlerle karşılaştırır.
Kullanım: python3 tools/qa/dogrula.py <test_adı> < çıktı   (run.sh bunu kendisi çağırır)"""
import sys, json
ad = sys.argv[1]
satir = [l for l in sys.stdin.read().splitlines() if l.startswith('@@')]
if not satir: print('FAIL', ad, '(çıktı yok)'); sys.exit(1)
R = json.loads(satir[-1][2:])
def get(p):
    v = R
    for k in p.split('.'):
        v = v[k] if isinstance(v, dict) and k in v else (v[int(k)] if isinstance(v, list) else None)
        if v is None: return None
    return v
BEKLE = {
 'kargo_kaydi': [('eski.cargo.titan', 0), ('yenile.cargo.titan', 5), ('yenile.cargo.demir', 2), ('pagehide.cargo.hurda', 3), ('satYenile.cargo.titan', 0),
                 ('gemi.ship', 'kasif'), ('gemi2.ship', 'sahin'), ('bozuk.cargo.kristal', 200), ('bozuk.cargo.titan', 0), ('bozukFoo', False), ('gercekHook', 'undefined'), ('errs', [])],
 'kacak_uste': [('forceBuy.kacakOnce', 4), ('forceBuy.kacakSonra', 4), ('forceBuy.krediDegisti', False), ('s5baseBox.btns', []), ('errs', [])],
 'toplu_regresyon': [('gocTemiz', -50), ('gocAvci', -65), ('gocHain', -65), ('gocKotu', -80), ('ucraIsaret', ['Ücra kapı → Kara Liman']), ('ucraIsaretMorrYenik', []), ('k14Hazir', True), ('errs', [])],
 'devriye_akis': [('tablo.0:kacak', 'hail'), ('tablo.0:w3', 'attack'), ('tablo.4:w3', 'none'), ('tablo.3:w2', 'none'), ('kacHemen.chase', True), ('errs', [])],
 'devriye_rusvet': [('rs.krediFark', -450), ('rs.kacak', 10), ('tuccar.state', 'flee'), ('errs', [])],
 'telefon_devriye': [('tapSonra.fark', -450), ('tapSonra.kacak', 10), ('errs', [])],
 'bekci': [(f'{t}.{k}', v) for t in ('filo', 'korsan') for k, v in (('dogdu.foe', 'foe'), ('faz_60.gph', 2), ('faz_30.gph', 3), ('bitis.bekci', 1), ('bitis.aktifSonra', False), ('bitis.boss', 6))] + [('errs', [])],
 'kutuk': [('kutuk.0', 'Madenci:2'), ('kutuk.1', 'Avcı:1'), ('kutuk.5', 'Patron avcısı:2'), ('kutuk.7', 'Gezgin:1'), ('kutuk.9', 'Kapı Bekçisi:3'), ('errs', [])],
 'hangar_bellek': [('cycles.0.mem.geometries', 45), ('cycles.2.mem.geometries', 45), ('cycles.1.mem.textures', 24), ('errs', [])],
}
hata = [(k, got, exp) for k, exp in BEKLE[ad] for got in [get(k)] if got != exp]
for k, got, exp in hata: print('  BEKLENEN', k, '=', exp, '| GELEN', got)
print('PASS' if not hata else 'FAIL', ad); sys.exit(1 if hata else 0)
