"""Başarım rozetleri: 10 rozet x 3 kademe (Bronz/Gümüş/Altın), 160x160 saydam webp, a8_i_* neon çizgi stilinde.
Kullanım: python pipeline/badges.py <çıktı_klasörü> [rozet_adı ...]   (adsız: hepsi)
Çıktı adı: rozet_<ad>_<1|2|3>.webp"""
import math, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops

S = 4                    # süper örnekleme
N = 160 * S
C = N // 2
TIER = [((201, 138, 90), (255, 206, 160)), ((197, 210, 226), (240, 247, 255)), ((255, 201, 77), (255, 238, 170))]      # (ana, çekirdek) Bronz, Gümüş, Altın (oyundaki TCOL)
LW = int(2.6 * S)


def P(x, y):             # 160 uzayı → süper örneklenmiş
    return (C + x * S, C + y * S)


def line(d, pts, col, w=LW):
    d.line([P(*p) for p in pts], fill=col, width=w, joint='curve')


def poly(d, pts, col, w=LW, close=True):
    q = [P(*p) for p in pts]
    if close:
        q.append(q[0])
    d.line(q, fill=col, width=w, joint='curve')


def circ(d, cx, cy, r, col, w=LW):
    x, y = P(cx, cy)
    d.ellipse((x - r * S, y - r * S, x + r * S, y + r * S), outline=col, width=w)


def arc(d, cx, cy, r, a0, a1, col, w=LW):
    x, y = P(cx, cy)
    d.arc((x - r * S, y - r * S, x + r * S, y + r * S), a0, a1, fill=col, width=w)


def pts_circ(cx, cy, r, n, a0=0.0):
    return [(cx + r * math.cos(a0 + 2 * math.pi * i / n), cy + r * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]


# ---- motifler (160 uzayı, merkez (0,0), yarıçap ≈ 52 içinde)
def m_madenci(d, c):
    poly(d, [(-30, 28), (-10, 14), (14, 22), (30, 4), (24, -20), (2, -30), (-22, -22), (-34, 0)], c)       # kaya/cevher
    line(d, [(-10, 14), (-6, -6), (2, -30)], c); line(d, [(-34, 0), (-6, -6), (24, -20)], c); line(d, [(-6, -6), (14, 22)], c)
    line(d, [(-50, 44), (26, -34)], c)                                                                  # kazma sapı
    poly(d, [(4, -50), (30, -52), (50, -34), (56, -10)], c, close=False)                                # kazma başı (dış eğri)
    poly(d, [(4, -50), (26, -40), (44, -22), (56, -10)], c, close=False)                                # iç eğri
    line(d, [(-50, 44), (-42, 50)], c)


def m_avci(d, c):
    circ(d, 0, 0, 40, c); circ(d, 0, 0, 24, c)
    for a in (0, 90, 180, 270):
        r = math.radians(a); line(d, [(48 * math.cos(r), 48 * math.sin(r)), (30 * math.cos(r), 30 * math.sin(r))], c)
    poly(d, [(0, -16), (11, 10), (4, 7), (0, 15), (-4, 7), (-11, 10)], c)                               # küçük gemi


def m_devriye(d, c):
    poly(d, [(0, -48), (36, -34), (36, 6), (0, 46), (-36, 6), (-36, -34)], c)                           # kalkan
    circ(d, 0, -4, 22, c); circ(d, 0, -4, 11, c)
    line(d, [(0, -4), (17, -17)], c); arc(d, 0, -4, 22, 290, 350, c, LW + S)
    line(d, [(-22, -4), (22, -4)], c); line(d, [(0, -26), (0, 18)], c)


def m_kacakci(d, c):
    poly(d, [(-34, -14), (0, -30), (34, -14), (34, 22), (0, 38), (-34, 22)], c)                         # sandık
    line(d, [(-34, -14), (0, 2), (34, -14)], c); line(d, [(0, 2), (0, 38)], c)
    for i in range(6):                                                                                  # kesik çizgili gizli dış hat
        a = math.radians(i * 60 + 15); b = math.radians(i * 60 + 45)
        line(d, [(46 * math.cos(a), 46 * math.sin(a) + 4), (46 * math.cos(b), 46 * math.sin(b) + 4)], c)
    circ(d, 0, -42, 6, c)


def m_siparis(d, c):
    circ(d, 0, 4, 34, c); circ(d, 0, 4, 28, c)
    line(d, [(0, 4), (0, -16)], c); line(d, [(0, 4), (14, 12)], c)
    line(d, [(-8, -36), (8, -36)], c); line(d, [(0, -36), (0, -30)], c)
    line(d, [(26, -26), (32, -32)], c)
    poly(d, [(-50, 34), (-36, 34), (-43, 44)], c, close=True)                                           # aciliyet oku
    line(d, [(-43, 34), (-43, 20)], c)


def m_patron(d, c):
    poly(d, [(-28, -12), (-34, 4), (-24, 16), (-24, 28), (24, 28), (24, 16), (34, 4), (28, -12), (20, -30), (0, -36), (-20, -30)], c)   # kafatası
    circ(d, -12, 0, 8, c); circ(d, 12, 0, 8, c)
    poly(d, [(0, 8), (-4, 16), (4, 16)], c)
    for x in (-12, -4, 4, 12):
        line(d, [(x, 22), (x, 28)], c)
    poly(d, [(-30, -34), (-22, -50), (-12, -40), (0, -56), (12, -40), (22, -50), (30, -34)], c, close=False)   # taç


def m_kadim(d, c):
    circ(d, 0, 0, 14, c); circ(d, 0, 0, 5, c)
    for r in (26, 38, 50):
        arc(d, 0, 0, r, -40, 40, c); arc(d, 0, 0, r, 140, 220, c)
    for i in range(12):
        a = math.radians(i * 30 + 15); line(d, [(46 * math.cos(a) * 0.01 + 0, 0), (0, 0)], c, 1)
    for p in pts_circ(0, 0, 50, 8, 0.4):
        line(d, [p, (p[0] * 0.9, p[1] * 0.9)], c)


def m_gezgin(d, c):
    circ(d, 0, 0, 22, c)
    arc(d, 0, 0, 22, 200, 340, c)
    poly(d, [(-50, 12), (-30, 24), (0, 28), (32, 22), (50, 8)], c, close=False)                         # yörünge halkası
    poly(d, [(-50, 12), (-30, 0), (0, -6), (30, 0), (50, 8)], c, close=False)
    line(d, [(-14, -10), (-4, -14)], c); line(d, [(-18, 4), (6, -4)], c)
    for p, r in (((-36, -34), 5), ((38, -32), 4), ((30, 38), 3)):
        line(d, [(p[0] - r, p[1]), (p[0] + r, p[1])], c); line(d, [(p[0], p[1] - r), (p[0], p[1] + r)], c)


def m_us(d, c):
    poly(d, pts_circ(0, 6, 34, 6, math.pi / 6), c)
    poly(d, pts_circ(0, 6, 20, 6, math.pi / 6), c)
    line(d, [(0, -28), (0, -48)], c); poly(d, [(-8, -48), (8, -48), (0, -58)], c)
    for p in pts_circ(0, 6, 34, 6, math.pi / 6):
        line(d, [p, (p[0] * 1.0, p[1] * 1.0 + 0.1 * 0 + (p[1] - 6) * 0.0)], c)
    for a in (0, 60, 120, 180, 240, 300):
        r = math.radians(a + 30); line(d, [(20 * math.cos(r), 6 + 20 * math.sin(r)), (34 * math.cos(r), 6 + 34 * math.sin(r))], c)
    circ(d, 0, 6, 6, c)


def m_bekci(d, c):
    poly(d, [(-34, 46), (-34, -6), (-24, -30), (0, -44), (24, -30), (34, -6), (34, 46)], c, close=False)   # kapı kemeri
    poly(d, [(-22, 46), (-22, -2), (-14, -20), (0, -28), (14, -20), (22, -2), (22, 46)], c, close=False)
    line(d, [(-34, 46), (34, 46)], c)
    poly(d, [(-14, 4), (0, -6), (14, 4), (0, 14)], c); circ(d, 0, 4, 4, c)                              # bekçi gözü
    line(d, [(-46, 46), (-46, -20)], c); line(d, [(46, 46), (46, -20)], c)


MOTIFS = {'madenci': m_madenci, 'avci': m_avci, 'devriye': m_devriye, 'kacakci': m_kacakci, 'siparisci': m_siparis,
          'patron': m_patron, 'kadim': m_kadim, 'gezgin': m_gezgin, 'us': m_us, 'bekci': m_bekci}


def frame(d, tier, c):
    circ(d, 0, 0, 74, c, LW)
    if tier >= 2:
        circ(d, 0, 0, 68, c, LW)
    if tier == 3:
        for i in range(16):
            a = math.radians(i * 22.5)
            line(d, [(74 * math.cos(a), 74 * math.sin(a)), (79 * math.cos(a), 79 * math.sin(a))], c)
    else:
        for i in range(4):
            a = math.radians(i * 90 + 45)
            line(d, [(74 * math.cos(a), 74 * math.sin(a)), (78 * math.cos(a), 78 * math.sin(a))], c)
    for i in range(tier):                                                                               # kademe elmasları
        x = (i - (tier - 1) / 2) * 11
        poly(d, [(x, 56), (x + 4, 60), (x, 64), (x - 4, 60)], c)


def render(name, tier):
    main, core = TIER[tier - 1]
    line_l = Image.new('RGBA', (N, N), (0, 0, 0, 0)); d = ImageDraw.Draw(line_l)
    MOTIFS[name](d, main + (255,))
    frame(d, tier, main + (255,))
    core_l = Image.new('RGBA', (N, N), (0, 0, 0, 0)); dc = ImageDraw.Draw(core_l)
    # çekirdek: aynı çizimi açık tonda, ince
    global LW
    old = LW; LW = max(S, 1)
    MOTIFS[name](dc, core + (255,)); frame(dc, tier, core + (255,))
    LW = old
    glow = line_l.filter(ImageFilter.GaussianBlur(3.2 * S))
    glow2 = line_l.filter(ImageFilter.GaussianBlur(1.2 * S))
    out = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    for layer, k in ((glow, 1.8), (glow2, 1.2), (line_l, 1.0), (core_l, 1.0)):
        if k != 1.0:
            a = layer.split()[3].point(lambda v: min(255, int(v * k))); layer = Image.merge('RGBA', (*layer.split()[:3], a))
        out = Image.alpha_composite(out, layer)
    return out.resize((160, 160), Image.LANCZOS)


if __name__ == '__main__':
    out = sys.argv[1]; names = sys.argv[2:] or list(MOTIFS)
    os.makedirs(out, exist_ok=True)
    for n in names:
        for t in (1, 2, 3):
            render(n, t).save(os.path.join(out, 'rozet_%s_%d.webp' % (n, t)), quality=92, method=6)
    print('RESULT', len(names) * 3)
