"""Kavisli dashboard: pencere altı sırtı (ridge) çizimdeki cam sınırını izler; üç ekran yuvası (bezel + oyuk) ve ayrı ekran mesh'leri.
Ekran mesh'leri (SCR_SYS/RADAR/HULL) anchors'taki 3B köşelerde durur ve pilot kamerasında CKP dörtgenine birebir izdüşer."""
import bpy, bmesh, math
from mathutils import Vector
from .common import *

class Face:
    """Dashboard yüzü: üç ekran düzleminin x boyunca yumuşak birleşimi; yanlarda pilota doğru kıvrılır."""
    def __init__(self, a, P):
        self.P = P; self.planes = []
        for s in a['screens']:
            n = Vector(s['normal']); c = Vector(s['center']); self.planes.append((n, n.dot(c)))
        self.cam = Cam(a)
        self.vb = self._ridge_table(a)
    def z(self, x, y):
        wL = 1 - smoothstep(-0.52, -0.36, x); wR = smoothstep(0.36, 0.52, x); wC = 1 - wL - wR; z = 0
        for w, (n, d) in zip((wL, wC, wR), self.planes): z += w * (d - n.x * x - n.y * y) / n.z
        ex = max(0.0, abs(x) - self.P['cheek_x0'])
        return z + self.P['cheek_k'] * ex * ex
    def normal(self, x, y):
        e = 1e-3; dzdx = (self.z(x + e, y) - self.z(x - e, y)) / (2 * e); dzdy = (self.z(x, y + e) - self.z(x, y - e)) / (2 * e)
        n = Vector((dzdx, dzdy, -1.0)); n.normalize(); return -n if n.z < 0 else n   # pilota bakan (+z)
    def _ridge_table(self, a):
        """Üç alt pencerenin en alt sınırı v_b(u) (piksel). Aralıklar doğrusal doldurulur; uçlarda dik düşer."""
        wins = [w for w in a['windows'] if w['cy'] > 100]; us = list(range(-300, 1901, 4)); tab = {}
        for u in us:
            best = None
            for w in wins:
                p = w['poly']; n = len(p)
                for i in range(n):
                    (x1, y1), (x2, y2) = p[i], p[(i + 1) % n]
                    if (x1 <= u <= x2 or x2 <= u <= x1) and abs(x2 - x1) > 1e-6:
                        t = (u - x1) / (x2 - x1); v = y1 + t * (y2 - y1)
                        if best is None or v > best: best = v
            tab[u] = best
        known = [(u, tab[u]) for u in us if tab[u] is not None]
        out = {}
        for u in us:
            if tab[u] is not None: out[u] = tab[u]; continue
            if u < known[0][0]: out[u] = known[0][1] - (known[0][0] - u) * 0.0
            elif u > known[-1][0]: out[u] = known[-1][1]
            else:
                l = max(k for k in known if k[0] < u); r = min(k for k in known if k[0] > u); out[u] = l[1] + (r[1] - l[1]) * (u - l[0]) / (r[0] - l[0])
        return out
    def ridge_y(self, x):
        z = self.z(x, -0.3)
        for _ in range(3):
            u = self.cam.cx + self.cam.f * x / -z; uk = int(round(max(-300, min(1900, u)) / 4) * 4); v = self.vb[uk]
            y = (self.cam.cy - v) / self.cam.f * -z; z = self.z(x, y)
        return y - self.P['ridge_margin']

def build(a, P, mats):
    cam = Cam(a); face = Face(a, P); objs = []
    # ---- dashboard gövdesi
    xs = [x / 100.0 for x in range(-int(P['dash_half'] * 100), int(P['dash_half'] * 100) + 1, int(P['dash_step'] * 100))]
    S = P['dash_rows']
    bm = bmesh.new(); grid = []
    for x in xs:
        yr = face.ridge_y(x); col = []
        for s in S:
            y = yr - s; z = face.z(x, y) + P['fascia_curl'] * max(0.0, s - 0.55) ** 2
            pp = Vector((x, y, z)); off = P['dash_back'] - P.get('row_off', {}).get('%g' % s, 0.0)   # + geriye, - pilota doğru (kabarık şerit / oluk)
            pp = pp * (1 + off / pp.length); col.append(bm.verts.new(g2b(pp)))
        grid.append(col)
    for i in range(len(xs) - 1):
        for j in range(len(S) - 1): bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    solidify_radial(bm, P['dash_thk'])
    dash = obj_from_bm('Dash_Body', bm, mats['gunmetal'], smooth=False)
    bevel(dash, P['bevel'], 2, 30); objs.append(dash)
    # ---- ekran yuvaları
    for s in a['screens']:
        Pn = [Vector(p) for p in s['corners3d']]; n = Vector(s['normal'])
        front = [p * (1 - P['bezel_depth'] / p.length) for p in Pn]; cf = sum(front, Vector()) / 4
        outer = []
        for q in front:
            d = q - cf; d -= n * d.dot(n); d.normalize(); outer.append(q + d * P['bezel_w'])
        base = [q * (1 + P['bezel_depth'] / q.length) for q in outer]
        bm = bmesh.new(); L0 = [bm.verts.new(g2b(p)) for p in front]; L1 = [bm.verts.new(g2b(p)) for p in outer]; L2 = [bm.verts.new(g2b(p)) for p in base]
        S0 = [bm.verts.new(g2b(p)) for p in Pn]
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new((L0[i], L0[j], L1[j], L1[i])); bm.faces.new((L1[i], L1[j], L2[j], L2[i])); bm.faces.new((S0[j], S0[i], L0[i], L0[j]))
        bz = obj_from_bm('Bezel_' + s['name'][4:], bm, mats['titanium'], smooth=False); bevel(bz, P['bevel'] * 0.5, 1, 30); objs.append(bz)
        # ekran mesh'i (boş, ayrı, UV 0..1): TL TR BR BL
        bm = bmesh.new(); vs = [bm.verts.new(g2b(p)) for p in Pn]; f = bm.faces.new(vs); uv = bm.loops.layers.uv.new('UVMap')
        for lp, (uu, vv) in zip(f.loops, ((0, 1), (1, 1), (1, 0), (0, 0))): lp[uv].uv = (uu, vv)
        sm = materials_screen(); scr = obj_from_bm(s['name'], bm, sm, collection='Cockpit'); objs.append(scr)
    return objs

def materials_screen():
    from . import materials
    return bpy.data.materials.get('M_screen') or materials.screen_mat(None, 1.2)
