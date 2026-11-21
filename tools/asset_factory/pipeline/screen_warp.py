"""Kokpit GLB'sinde yan ekran (SCR_SYS / SCR_HULL) büyütme + yamukluk azaltma (bpy gerektirmez; GLB konum verisi doğrudan düzenlenir).
Yöntem: pilot kamera sözleşmesiyle (göz orijinde, f=435,27 px, merkez (800;239,5)) her tepe noktası piksele izdüşürülür; ekran dörtgeninin
çevresindeki tepe noktalarına yumuşak ağırlıkla "eski dörtgen → yeni dörtgen" homografisi uygulanır; yeni konum aynı ışın ve aynı derinlik üzerinde yeniden kurulur.
Orta (RADAR) ekran ve diğer her şey değişmez. SCR_* adları, köşe sırası ve UV yönü korunur. Girdi GLB'ye yazılmaz.
Kullanım: python pipeline/screen_warp.py <girdi.glb> <çıktı.glb> [ölçek=1.18] [yamukluk_azaltma=0.5]"""
import os, sys, json, struct
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import glbpack
from qc import glb_checks

F, CX, CY = 435.27, 800.0, 239.5


def homography(src, dst):
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y, -u])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y, -v])
    _, _, Vt = np.linalg.svd(np.array(A, float))
    return Vt[-1].reshape(3, 3)


def apply_h(H, p):
    q = np.concatenate([p, np.ones((len(p), 1))], 1) @ H.T
    return q[:, :2] / q[:, 2:3]


def new_quad(q, k, relax):
    q = np.array(q, float)
    c = q.mean(0)
    s = c + (q - c) * k
    bb = np.array([[s[:, 0].min(), s[:, 1].min()], [s[:, 0].max(), s[:, 1].min()], [s[:, 0].max(), s[:, 1].max()], [s[:, 0].min(), s[:, 1].max()]])
    # köşe sırası TL, TR, BR, BL: sol/sağ ayrımı için köşeleri x'e göre eşleştir
    order = [0, 1, 2, 3]
    tl = s[0]; tr = s[1]; br = s[2]; bl = s[3]
    rect = np.array([[min(tl[0], bl[0]), min(tl[1], tr[1])], [max(tr[0], br[0]), min(tl[1], tr[1])], [max(tr[0], br[0]), max(bl[1], br[1])], [min(tl[0], bl[0]), max(bl[1], br[1])]])
    return (1 - relax) * s + relax * rect


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def main(src, dst, k=1.18, relax=0.5):
    j, b, _ = glb_checks.read_glb(src)
    # ekran köşeleri (px) ve derinlik: SCR_* düğümlerinden
    views = []
    for i, bv in enumerate(j['bufferViews']):
        o = bv.get('byteOffset', 0)
        views.append(bytearray(b[o:o + bv['byteLength']]))

    def pos_accessor(mesh_idx):
        outs = []
        for p in j['meshes'][mesh_idx]['primitives']:
            outs.append(p['attributes']['POSITION'])
        return outs

    def read_pos(ai):
        a = j['accessors'][ai]
        bv = j['bufferViews'][a['bufferView']]
        o = a.get('byteOffset', 0)
        n = a['count']
        stride = bv.get('byteStride', 12)
        buf = views[a['bufferView']]
        arr = np.frombuffer(bytes(buf), dtype=np.uint8)
        out = np.zeros((n, 3), np.float32)
        for c in range(3):
            pass
        raw = np.ndarray((n, 3), dtype='<f4', buffer=bytes(buf), offset=o, strides=(stride, 4))
        return raw.copy()

    def write_pos(ai, arr):
        a = j['accessors'][ai]
        bv = j['bufferViews'][a['bufferView']]
        o = a.get('byteOffset', 0)
        stride = bv.get('byteStride', 12)
        buf = views[a['bufferView']]
        for i in range(a['count']):
            buf[o + i * stride:o + i * stride + 12] = arr[i].astype('<f4').tobytes()
        a['min'] = [float(x) for x in arr.min(0)]
        a['max'] = [float(x) for x in arr.max(0)]

    names = {n.get('name'): n for n in j['nodes']}
    scr_mesh = {nm: names[nm]['mesh'] for nm in ('SCR_SYS', 'SCR_RADAR', 'SCR_HULL')}
    # mevcut köşeler
    corners = {}
    depth = {}
    for nm, mi in scr_mesh.items():
        ai = pos_accessor(mi)[0]
        P = read_pos(ai)
        d = -P[:, 2]
        corners[nm] = np.stack([CX + F * P[:, 0] / d, CY - F * P[:, 1] / d], 1)
        depth[nm] = float(d.mean())
    report = {'eski': {k: corners[k].round(1).tolist() for k in corners}}
    jobs = {}
    for nm in ('SCR_SYS', 'SCR_HULL'):
        q = corners[nm]
        # köşe sırasını TL, TR, BR, BL'e getir (y'ye göre iki üst/iki alt, sonra x'e göre)
        idx = np.argsort(q[:, 1])
        top = sorted(idx[:2], key=lambda i: q[i, 0])
        bot = sorted(idx[2:], key=lambda i: q[i, 0])
        order = [top[0], top[1], bot[1], bot[0]]
        qo = q[order]
        nq = new_quad(qo, k, relax)
        H = homography(qo, nq)
        Hin = homography(qo, np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float))
        jobs[nm] = (qo, nq, H, Hin, order)
        report.setdefault('yeni', {})[nm] = nq.round(1).tolist()
    # tüm mesh'ler: RADAR hariç ekran düğümleri hariç; gövde ve şeritler uyarlanır
    done = set()
    moved = 0
    for ni, nd in enumerate(j['nodes']):
        if 'mesh' not in nd:
            continue
        if nd.get('name') == 'SCR_RADAR':
            continue
        mi = nd['mesh']
        tr = np.array(nd.get('translation', [0, 0, 0]), float)
        for ai in pos_accessor(mi):
            if ai in done:
                continue
            done.add(ai)
            P = read_pos(ai).astype(float) + tr
            d = -P[:, 2]
            ok = d > 0.05
            uv = np.stack([CX + F * P[:, 0] / np.where(ok, d, 1), CY - F * P[:, 1] / np.where(ok, d, 1)], 1)
            newP = P.copy()
            for nm, (qo, nq, H, Hin, order) in jobs.items():
                st = apply_h(Hin, uv)              # (s,t) eski dörtgen içinde 0..1
                r = np.maximum(np.abs(st[:, 0] - 0.5), np.abs(st[:, 1] - 0.5)) * 2
                w = 1 - smoothstep(1.0, 2.1, r)
                w = np.where(np.abs(d - depth[nm]) < 0.45, w, 0.0)
                if nd.get('name') == nm:
                    w = np.ones(len(P))            # ekran mesh'i: tam dönüşüm
                w = np.where(ok, w, 0.0)
                if not w.any():
                    continue
                tgt = apply_h(H, uv)
                uv2 = uv + (tgt - uv) * w[:, None]
                x = (uv2[:, 0] - CX) / F * d
                y = -(uv2[:, 1] - CY) / F * d
                m = w > 0
                newP[m, 0] = x[m]
                newP[m, 1] = y[m]
                moved += int(m.sum())
            write_pos(ai, (newP - tr).astype(np.float32))
    glbpack.write(dst, j, [bytes(v) for v in views])
    report['tepe_tasinan'] = moved
    return report


if __name__ == '__main__':
    k = float(sys.argv[3]) if len(sys.argv) > 3 else 1.18
    rl = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
    print('RESULT', json.dumps(main(sys.argv[1], sys.argv[2], k, rl)))
