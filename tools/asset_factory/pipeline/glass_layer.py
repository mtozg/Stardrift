"""Kokpit cam katmanı DENEMESİ (registry dışı, yalnız görsel kıyas): bir kokpit GLB'sinin KOPYASINA şeffaf kanopi camı ekler.
Orijinal GLB'ye ve registry'ye dokunmaz. bpy gerekmez (GLB JSON + BIN düzenlenir).

Cam = pilot gözünden bakıldığında gözü saran elipsoit kabuk (kamera sözleşmesiyle aynı ışınlar); alt sınırı konsol sırtında biter, derinlik testi konsolun arkasına gizler.
Etki (kenarlardan merkeze):
  - fresnel: tepe noktası alfası bakış açısına göre (kenarlarda daha yansıtıcı)
  - ton: hafif mavi-yeşil
  - hayalet yansıma: ekranların ve iç ışıkların cama yumuşak, sabit yansıması (canlı ekranlar yansıtılmaz)
  - (belirgin) ince çizik, toz benekleri, lekeli alfa, alt sınırda cam kalınlığı şeridi
glTF: alphaMode BLEND (Three r128 GLTFLoader depthWrite=false yapar), COLOR_0 RGBA (tepe alfası), PNG baseColor dokusu (RGBA).
Kullanım: python pipeline/glass_layer.py <girdi.glb> <çıktı.glb> <hafif|belirgin> [doku=1024]"""
import io, json, math, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from qc import glb_checks

F, CX, CY = 435.2707, 800.0, 239.5
# Şahin için konsol sırtı (js/game.js CK3.sahin.ridge ile aynı, 1600x656 uzayı): cam bu çizginin altına inmez
RIDGE = [[-400, 300], [0, 300], [50, 304], [100, 326], [150, 388], [200, 412], [250, 414], [300, 410], [350, 404], [400, 400], [450, 394], [500, 390], [550, 386], [600, 382], [650, 380], [700, 378],
         [750, 370], [800, 366], [850, 370], [900, 378], [950, 380], [1000, 382], [1050, 386], [1100, 390], [1150, 394], [1200, 400], [1250, 406], [1300, 412], [1350, 414], [1400, 412], [1450, 388],
         [1500, 326], [1550, 304], [1600, 300], [2000, 300]]
# ekranlar (pilot görüşü piksel dörtgenleri) — hayalet yansıma konumları için
SCREENS = [[[390, 432], [620, 420], [626, 560], [400, 582]], [[660, 404], [940, 404], [940, 584], [660, 584]], [[980, 420], [1210, 432], [1200, 582], [974, 560]]]
U0, U1, V0 = -160, 1760, -140      # cam kapsamı (sallanma payı: kenarlarda 160 px, üstte 140 px)
VARIANTS = {
    'hafif':    dict(a_center=0.16, a_edge=0.55, t_clear=0.42, ghost=0.55, scratch=0.0, dust=0.0, rim=False, tint=(0.62, 0.80, 0.78)),
    'belirgin': dict(a_center=0.22, a_edge=0.75, t_clear=0.46, ghost=0.85, scratch=1.0, dust=1.0, rim=True, tint=(0.58, 0.78, 0.76)),
}


def ridge_v(u):
    xs = [p[0] for p in RIDGE]
    return float(np.interp(u, xs, [p[1] for p in RIDGE]))


def ray_dir_gltf(u, v):
    """Pilot piksel (u, v) → gözden çıkan ışın, glTF uzayı (+Y yukarı, ileri −Z)."""
    d = np.array([(u - CX) / F, -(v - CY) / F, -1.0])
    return d / np.linalg.norm(d)


def build_mesh(var, nu=48, nv=16):
    C = np.array([0.0, -0.10, -0.15])      # glTF: x, y(yukarı), z(ileri = −z)
    R = np.array([1.35, 0.95, 1.10])       # elipsoit yarı eksenleri (x, y, z)
    us = np.linspace(U0, U1, nu + 1)
    verts, norms, uvs, cols, rows = [], [], [], [], []
    for j in range(nv + 1):
        row = []
        for i in range(nu + 1):
            u = us[i]
            vmax = ridge_v(min(max(u, 0), 1600)) + 6
            v = V0 + (vmax - V0) * j / nv
            d = ray_dir_gltf(u, v)
            # (t d − C)² / R² = 1 → far root
            A = np.sum((d / R) ** 2)
            B = -2 * np.sum(d * C / R ** 2)
            Cc = np.sum((C / R) ** 2) - 1
            t = (-B + math.sqrt(max(B * B - 4 * A * Cc, 0.0))) / (2 * A)
            p = t * d
            n = -(p - C) / R ** 2      # içe bakan normal
            n /= np.linalg.norm(n)
            cos = abs(float(np.dot(d, n)))
            f = (1 - cos) ** 2.2
            f = min(1.0, f * 3.2)
            alpha = var['a_center'] + (var['a_edge'] - var['a_center']) * f
            verts.append(p)
            norms.append(n)
            uvs.append(((u - U0) / (U1 - U0), (v - V0) / (480 - V0)))
            cols.append((1.0, 1.0, 1.0, alpha))
            row.append(len(verts) - 1)
        rows.append(row)
    idx = []
    for j in range(nv):
        for i in range(nu):
            a, b, c, d = rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]
            idx += [a, d, c, a, c, b]      # pilota (içe) bakan sarım
    if var['rim']:      # alt sınırda cam kalınlığı: son sıranın iki kat ince şeridi (koyu yeşil, daha opak)
        base = len(verts)
        for i in range(nu + 1):
            p = verts[rows[-1][i]]
            n = norms[rows[-1][i]]
            verts.append(p + n * -0.012)
            norms.append(n)
            uvs.append((uvs[rows[-1][i]][0], 0.999))
            cols.append((1.0, 1.0, 1.0, 0.95))
        for i in range(nu):
            a, b = rows[-1][i], rows[-1][i + 1]
            c, d = base + i + 1, base + i
            idx += [a, d, c, a, c, b]
    return (np.array(verts, np.float32), np.array(norms, np.float32), np.array(uvs, np.float32), np.array(cols, np.float32), np.array(idx, np.uint32))


def build_texture(var, size):
    S = size * 2
    rng = np.random.RandomState(7)
    r, g, b = [int(255 * c) for c in var['tint']]
    img = Image.new('RGBA', (S, S), (r, g, b, int(255 * var['t_clear'])))
    sx, sy = S / (U1 - U0), S / (480 - V0)
    P = lambda u, v: ((u - U0) * sx, (v - V0) * sy)
    # hayalet ekran yansıması: ekranlar dikey çevrilir ve yukarı taşınır (cam eğimi), yumuşatılır
    ghost = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(ghost)
    for q in SCREENS:
        pts = [P(u, 2 * 300 - v + 40) for (u, v) in q]      # v ekseninde 300'e göre ayna, 40 px yukarı
        gd.polygon(pts, fill=(120, 215, 235, int(255 * 0.80 * var['ghost'])))
    for (u, v, c) in ((800, 8, (255, 170, 110)), (420, 40, (255, 120, 100)), (1180, 40, (255, 120, 100))):      # iç ışıklar (kırmızı şerit, amber) nokta yansıması
        x, y = P(u, v)
        gd.ellipse((x - 30, y - 14, x + 30, y + 14), fill=c + (int(255 * 0.7 * var['ghost']),))
    ghost = ghost.filter(ImageFilter.GaussianBlur(S * 0.012))
    img = Image.alpha_composite(img, ghost)
    d = ImageDraw.Draw(img)
    if var['scratch'] > 0:
        for _ in range(70):      # ince çizikler
            x0, y0 = rng.uniform(0, S), rng.uniform(0, S)
            L = rng.uniform(S * 0.03, S * 0.20)
            a = rng.uniform(-0.6, 0.6) + (math.pi / 2 if rng.rand() < 0.2 else 0)
            d.line((x0, y0, x0 + L * math.cos(a), y0 + L * math.sin(a)), fill=(235, 245, 245, int(255 * rng.uniform(0.35, 0.8))), width=max(1, S // 900))
        for _ in range(26):      # dairesel sürtme izi (ince yay)
            cx, cy, rr = rng.uniform(0, S), rng.uniform(0, S), rng.uniform(S * 0.05, S * 0.18)
            a0 = rng.uniform(0, 360)
            d.arc((cx - rr, cy - rr, cx + rr, cy + rr), a0, a0 + rng.uniform(12, 40), fill=(235, 245, 245, int(255 * rng.uniform(0.25, 0.5))), width=max(1, S // 1100))
    if var['dust'] > 0:
        for _ in range(900):      # toz benekleri
            x, y = rng.uniform(0, S), rng.uniform(0, S)
            rr = rng.uniform(0.6, 2.4) * S / 1024
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(240, 240, 235, int(255 * rng.uniform(0.25, 0.7))))
        sm = Image.fromarray((rng.rand(S // 32, S // 32) * 255).astype(np.uint8)).resize((S, S), Image.BICUBIC).filter(ImageFilter.GaussianBlur(S * 0.02))      # leke
        a = np.asarray(img, np.float32)
        a[..., 3] = np.clip(a[..., 3] * (0.85 + 0.30 * np.asarray(sm, np.float32) / 255.0), 0, 255)
        img = Image.fromarray(a.astype(np.uint8))
    img = img.resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, 'PNG', optimize=True)
    return buf.getvalue()


def add_glass(src, dst, name, size=1024):
    var = VARIANTS[name]
    j, b, _ = glb_checks.read_glb(src)
    V, N, UV, C, I = build_mesh(var)
    png = build_texture(var, size)
    blob = bytearray(b)

    def put(data, target=None):
        while len(blob) % 4:
            blob.append(0)
        off = len(blob)
        blob.extend(data)
        j['bufferViews'].append({'buffer': 0, 'byteOffset': off, 'byteLength': len(data), **({'target': target} if target else {})})
        return len(j['bufferViews']) - 1
    acc = lambda bv, ct, cnt, ty, **kw: (j['accessors'].append({'bufferView': bv, 'componentType': ct, 'count': cnt, 'type': ty, **kw}), len(j['accessors']) - 1)[1]
    aP = acc(put(V.tobytes(), 34962), 5126, len(V), 'VEC3', min=V.min(0).tolist(), max=V.max(0).tolist())
    aN = acc(put(N.tobytes(), 34962), 5126, len(N), 'VEC3')
    aT = acc(put(UV.tobytes(), 34962), 5126, len(UV), 'VEC2')
    aC = acc(put(C.tobytes(), 34962), 5126, len(C), 'VEC4')
    aI = acc(put(I.tobytes(), 34963), 5125, len(I), 'SCALAR')
    img_bv = put(png)
    j.setdefault('images', []).append({'bufferView': img_bv, 'mimeType': 'image/png', 'name': 'sd_glass_' + name})
    j.setdefault('samplers', []).append({'magFilter': 9729, 'minFilter': 9987, 'wrapS': 33071, 'wrapT': 33071})
    j.setdefault('textures', []).append({'source': len(j['images']) - 1, 'sampler': len(j['samplers']) - 1})
    j['materials'].append({'name': 'MAT_glass', 'alphaMode': 'BLEND', 'doubleSided': True,
                           'pbrMetallicRoughness': {'baseColorFactor': [1, 1, 1, 1], 'baseColorTexture': {'index': len(j['textures']) - 1}, 'metallicFactor': 0.0, 'roughnessFactor': 0.06}})
    j['meshes'].append({'name': 'GLASS_canopy', 'primitives': [{'attributes': {'POSITION': aP, 'NORMAL': aN, 'TEXCOORD_0': aT, 'COLOR_0': aC}, 'indices': aI, 'material': len(j['materials']) - 1}]})
    j['nodes'].append({'name': 'GLASS_canopy', 'mesh': len(j['meshes']) - 1})
    root = j['scenes'][j.get('scene', 0)]['nodes'][0]
    j['nodes'][root].setdefault('children', []).append(len(j['nodes']) - 1)
    j['buffers'][0]['byteLength'] = len(blob) + (-len(blob) % 4)
    while len(blob) % 4:
        blob.append(0)
    js = json.dumps(j, separators=(',', ':')).encode()
    js += b' ' * ((4 - len(js) % 4) % 4)
    glb = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob)) + struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(blob), 0x004E4942) + bytes(blob)
    open(dst, 'wb').write(glb)
    return {'out': dst, 'bytes': len(glb), 'glass_verts': len(V), 'glass_tris': len(I) // 3, 'png_bytes': len(png), 'tex': size}


if __name__ == '__main__':
    print('RESULT', json.dumps(add_glass(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 1024)))
