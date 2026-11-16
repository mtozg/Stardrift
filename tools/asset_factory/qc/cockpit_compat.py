"""Kokpit GLB'sinin onaylı Kaşif GLB'siyle (oyunun ?ck=b yolu) sözleşme uyumluluğu. bpy gerektirmez; iki dosya yalnızca okunur.
Kaynak beklentiler (dal claude/bold-bardeen-oqf73o, js/game.js renderB/buildB):
  - ekranlar: ağacın herhangi bir yerinde SCR_SYS / SCR_RADAR / SCR_HULL adlı mesh'ler (traverse + ad), CanvasTexture flipY=false
  - kamera: göz orijinde, ileri −Z, odak 435,3 px (1600×656 uzayı), asal nokta (800, 239,5) setViewOffset ile; model ölçeklenmez/eğilmez
  - malzemeler: MeshStandardMaterial (envMapIntensity 0,9 atanır); ekran malzemesi oyun tarafından MeshBasicMaterial ile değiştirilir
Kullanım: python qc/cockpit_compat.py <yeni.glb> <kasif.glb> <çıktı.json>"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from qc import glb_checks

F, CX, CY, W, H = 435.27, 800.0, 239.5, 1600, 656
SCR = ('SCR_SYS', 'SCR_RADAR', 'SCR_HULL')


def world_mats(j):
    """Düğüm dünya matrisleri (kökten)."""
    def local(n):
        if 'matrix' in n:
            return np.array(n['matrix'], float).reshape(4, 4).T
        M = np.eye(4)
        t = n.get('translation', [0, 0, 0])
        q = n.get('rotation', [0, 0, 0, 1])
        s = n.get('scale', [1, 1, 1])
        x, y, z, w = q
        R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                      [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                      [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        M[:3, :3] = R * np.array(s)
        M[:3, 3] = t
        return M
    out = {}

    def walk(i, P):
        Mi = P @ local(j['nodes'][i])
        out[i] = Mi
        for c in j['nodes'][i].get('children', []):
            walk(c, Mi)
    for r in j['scenes'][j.get('scene', 0)]['nodes']:
        walk(r, np.eye(4))
    return out


def screens(path):
    j, b, size = glb_checks.read_glb(path)
    WM = world_mats(j)
    res = {}
    for i, n in enumerate(j['nodes']):
        if n.get('name') in SCR and 'mesh' in n:
            pr = j['meshes'][n['mesh']]['primitives'][0]
            P = glb_checks.accessor(j, b, pr['attributes']['POSITION']).astype(float)
            P = (WM[i] @ np.c_[P, np.ones(len(P))].T).T[:, :3]
            U = glb_checks.accessor(j, b, pr['attributes']['TEXCOORD_0']).astype(float)
            px = [(CX + F * p[0] / -p[2], CY - F * p[1] / -p[2]) for p in P]
            # UV ↔ ekran köşesi: görüntüde sol-üst köşedeki köşenin UV'si (0,0) olmalı (flipY=false, glTF v aşağı)
            tl = int(np.argmin([x + y for x, y in px]))
            br = int(np.argmax([x + y for x, y in px]))
            res[n['name']] = {'prims': len(j['meshes'][n['mesh']]['primitives']), 'verts': len(P), 'uv_tl': U[tl].round(3).tolist(), 'uv_br': U[br].round(3).tolist(),
                              'px': [[round(x), round(y)] for x, y in px], 'in_front': bool((P[:, 2] < 0).all()),
                              'w_px': round(max(x for x, _ in px) - min(x for x, _ in px)), 'h_px': round(max(y for _, y in px) - min(y for _, y in px))}
    allp = []
    for i, n in enumerate(j['nodes']):
        if 'mesh' in n:
            for pr in j['meshes'][n['mesh']]['primitives']:
                P = glb_checks.accessor(j, b, pr['attributes']['POSITION']).astype(float)
                allp.append((WM[i] @ np.c_[P, np.ones(len(P))].T).T[:, :3])
    A = np.concatenate(allp)
    mats = [m.get('name') for m in j.get('materials', [])]
    return j, size, res, A.min(0).round(3).tolist(), A.max(0).round(3).tolist(), mats


def budget(path):
    """Bütçe ölçüleri: üçgen, primitive (≈ statik draw call), doku girişleri ve r128 GPU tahmini (RGBA8 + mip, her giriş ayrı yüklenir)."""
    j, b, size = glb_checks.read_glb(path)
    tris = prims = 0
    for n in j['nodes']:
        if 'mesh' in n:
            for pr in j['meshes'][n['mesh']]['primitives']:
                prims += 1
                tris += (j['accessors'][pr['indices']]['count'] if 'indices' in pr else j['accessors'][pr['attributes']['POSITION']]['count']) // 3
    gpu = 0
    for t in j.get('textures', []):
        src = t.get('source', t.get('extensions', {}).get('EXT_texture_webp', {}).get('source'))
        w, h = glb_checks.image(j, b, src)[0].size
        gpu += w * h * 4 * 4 // 3
    return {'bayt': size, 'ucgen': tris, 'primitive': prims, 'doku_girisi': len(j.get('textures', [])), 'gorsel': len(j.get('images', [])),
            'gpu_mb_tahmin': round(gpu / 1048576, 1), 'malzeme': len(j.get('materials', []))}


def main(new, ref, out):
    jn, sn, scn, lon, hin, mn = screens(new)
    jr, sr, scr, lor, hir, mr = screens(ref)
    items = []
    add = lambda tid, ok, v, ref_v, note: items.append({'id': tid, 'status': 'PASS' if ok else 'FAIL', 'value': v, 'kasif': ref_v, 'note': note})
    for nm in SCR:
        a, k = scn.get(nm), scr.get(nm)
        add('ekran.%s.var' % nm, a is not None, bool(a), bool(k), 'oyun ekranı ada göre bağlar (traverse)')
        if not a:
            continue
        add('ekran.%s.tek_primitive' % nm, a['prims'] == 1 and a['verts'] == 4, [a['prims'], a['verts']], [k['prims'], k['verts']], 'tek dörtgen')
        add('ekran.%s.uv_yonu' % nm, a['uv_tl'] == [0.0, 0.0] and a['uv_br'] == [1.0, 1.0], {'sol_ust': a['uv_tl'], 'sag_alt': a['uv_br']}, {'sol_ust': k['uv_tl'], 'sag_alt': k['uv_br']}, 'CanvasTexture flipY=false: görüntünün sol-üstü UV (0,0)')
        add('ekran.%s.gozun_onunde' % nm, a['in_front'], a['in_front'], k['in_front'], 'göz orijinde, ileri −Z')
        inside = all(0 <= x <= W and 0 <= y <= H for x, y in a['px'])
        add('ekran.%s.cerceve_ici' % nm, inside, a['px'], k['px'], 'pilot çerçevesinde (1600×656)')
        items.append({'id': 'ekran.%s.boyut_px' % nm, 'status': 'INFO', 'value': [a['w_px'], a['h_px']], 'kasif': [k['w_px'], k['h_px']], 'note': 'tasarım farkı (r008 kararı: daha büyük, yakın, yüksek)'})
    add('birim.olcek', abs((hin[0] - lon[0]) - (hir[0] - lor[0])) < 1.5, {'min': lon, 'max': hin}, {'min': lor, 'max': hir}, 'metre; aynı ölçek düzeyi (genişlik farkı < 1,5 m)')
    add('uzanti.r128', set(jn.get('extensionsUsed', [])) <= {'EXT_texture_webp', 'KHR_mesh_quantization', 'KHR_materials_unlit', 'KHR_texture_transform'}, jn.get('extensionsUsed', []), jr.get('extensionsUsed', []),
        'r128 GLTFLoader tanır; Kaşif\'teki emissive_strength r128\'de yok sayılıyor')
    add('malzeme.standart', all(m for m in mn), mn, mr, 'MeshStandardMaterial\'a dönüşür; oyun envMapIntensity 0,9 atar')
    res = {'yeni': os.path.basename(new), 'kasif': os.path.basename(ref), 'bayt': {'yeni': sn, 'kasif': sr}, 'butce': {'yeni': budget(new), 'kasif': budget(ref)}, 'items': items,
           'ozet': {k: sum(1 for i in items if i['status'] == k) for k in ('PASS', 'FAIL', 'INFO')}}
    json.dump(res, open(out, 'w'), indent=1, ensure_ascii=False)
    print('RESULT', json.dumps(res['ozet']))


if __name__ == '__main__':
    main(*sys.argv[1:4])
