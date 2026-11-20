"""Görüntü karşılaştırma (bpy gerektirmez): altın referans (Cycles, nötr ışık) ⟷ Three r128 render.
Ölçüler: siluet farkı (XOR / birleşim), ortak alanda göreli ortalama parlaklık farkı, ortalama ΔE (CIE76, Lab)."""
import numpy as np
from PIL import Image


def _load(p):
    a = np.asarray(Image.open(p).convert('RGBA'), dtype=np.float32) / 255.0
    return a[..., :3], a[..., 3]


def _srgb_to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _lab(rgb):
    lin = _srgb_to_lin(rgb)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = lin @ M.T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def _dil(m, k=1):
    """k piksellik (8 komşuluk) genişletme."""
    o = m.copy()
    for _ in range(k):
        p = np.pad(o, 1)
        o = (p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:] | p[:-2, :-2] | p[:-2, 2:] | p[2:, :-2] | p[2:, 2:])
    return o


def silhouette_tol(gm, tm, k=1):
    """1 px toleranslı siluet uyuşmazlığı (birleşim alanına oran): bir maskenin diğerinin k piksel genişletilmişinin DIŞINA taştığı pikseller.
    Cycles ⟷ Three kenar yumuşatma/örnekleme farkı (≤ 1 px) sayılmaz; eksik/yanlış yerleşmiş geometri sayılır. Kenar uzunluğundan ve kapalı alandan büyük ölçüde bağımsızdır."""
    union = (gm | tm).sum()
    return float(((gm & ~_dil(tm, k)) | (tm & ~_dil(gm, k))).sum() / max(union, 1))


def compare(golden, test, diff_out=None):
    g, ga = _load(golden)
    t, ta = _load(test)
    gm, tm = ga > 0.5, ta > 0.5
    union = gm | tm
    sil = float((gm ^ tm).sum() / max(union.sum(), 1))
    both = gm & tm
    lum = lambda c: (_srgb_to_lin(c) @ np.array([0.2126, 0.7152, 0.0722]))
    lg, lt = lum(g)[both].mean(), lum(t)[both].mean()
    lum_diff = float(abs(lt - lg) / max(lg, 1e-6))
    de = np.linalg.norm(_lab(g) - _lab(t), axis=-1)
    de_mean = float(de[both].mean())
    de_p95 = float(np.percentile(de[both], 95))
    if diff_out:
        h = np.clip(de / 20.0, 0, 1)
        img = np.zeros(g.shape, np.float32)
        img[..., 0] = h
        img[..., 1] = np.where(both, 0.15 * (1 - h), 0)
        img[..., 2] = np.where(gm ^ tm, 1.0, 0)
        Image.fromarray((img * 255).astype(np.uint8)).save(diff_out)
    return {'silhouette_diff': round(sil, 5), 'silhouette_tol': round(silhouette_tol(gm, tm), 5), 'lum_golden': round(float(lg), 4), 'lum_three': round(float(lt), 4),
            'lum_diff': round(lum_diff, 4), 'deltaE_mean': round(de_mean, 2), 'deltaE_p95': round(de_p95, 2)}
