"""UV üçgen rasterleme (numpy, bpy gerektirmez). Piksel MERKEZİ üçgenin kesin içindeyse sayılır
(kenar fonksiyonu > eps). Ortak kenar üzerindeki pikseller iki üçgene birden sayılmaz; böylece çakışma sayımı
yalnızca gerçek ada çakışmalarını gösterir. uv: (n,2) 0..1, görüntü satırı v ile aşağı doğru (glTF düzeni)."""
import numpy as np


def raster(uv, tris, size, eps=1e-6):
    """Döndürür: count (size×size uint16) — her pikselin kaç üçgenin içinde olduğu."""
    acc = np.zeros((size, size), np.uint16)
    P = uv * size
    for t in tris:
        a, b, c = P[t[0]], P[t[1]], P[t[2]]
        area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        if abs(area) < 1e-12:
            continue
        x0, x1 = int(max(0, np.floor(min(a[0], b[0], c[0])))), int(min(size, np.ceil(max(a[0], b[0], c[0]))))
        y0, y1 = int(max(0, np.floor(min(a[1], b[1], c[1])))), int(min(size, np.ceil(max(a[1], b[1], c[1]))))
        if x1 <= x0 or y1 <= y0:
            continue
        xs, ys = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        s = 1.0 if area > 0 else -1.0
        e0 = s * ((b[0] - a[0]) * (ys - a[1]) - (b[1] - a[1]) * (xs - a[0]))
        e1 = s * ((c[0] - b[0]) * (ys - b[1]) - (c[1] - b[1]) * (xs - b[0]))
        e2 = s * ((a[0] - c[0]) * (ys - c[1]) - (a[1] - c[1]) * (xs - c[0]))
        acc[y0:y1, x0:x1] += ((e0 > eps) & (e1 > eps) & (e2 > eps)).astype(np.uint16)
    return acc
