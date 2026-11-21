#!/usr/bin/env python3
"""T7: js/game.js içindeki işlev yeniden atamalarının envanterini üretir (salt okunur analiz).
Kullanım: python3 tools/fonksiyon_envanteri.py > docs/FONKSIYON_ENVANTERI.md
`ad = function(...) {` ve `window.ad = function(...) {` atamalarını bulur; gövdede önceki işlevin çağrılıp çağrılmadığına bakarak
"saran" (öncekini çağırır) ile "diğer" (ilk tanım ya da değiştiren) ayırır. Statik analizdir; nadiren yanlış sınıflayabilir."""
import bisect, collections, os, re, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(root, 'js', 'game.js'), encoding='utf-8').read(); L = src.split('\n')
ver = re.search(r"SD_VERSION = '([0-9.]+)'", open(os.path.join(root, 'index.html'), encoding='utf-8').read())
offs = [0]
for l in L: offs.append(offs[-1] + len(l) + 1)
line_of = lambda pos: bisect.bisect_right(offs, pos)
pat = re.compile(r'(?:(?:const|let|var)\s+(_\w+)\s*=\s*(?:window\.)?(\w+)\s*;\s*)?(?:window\.)?(\b[A-Za-z_]\w*)\s*=\s*function\b\s*\([^)]*\)\s*\{')
res = collections.defaultdict(list)
def header(i):
    for j in range(i - 1, max(0, i - 45), -1):
        m = re.search(r'//\s*([^\n]{8,90})|/\*\s*([^*]{8,90})', L[j - 1])
        if m: return (m.group(1) or m.group(2)).strip()
    return ''
for m in pat.finditer(src):
    saved, orig, name = m.group(1), m.group(2), m.group(3)
    i = m.end(); d = 1; n = len(src)
    while i < n and d > 0:
        c = src[i]
        if c == '{': d += 1
        elif c == '}': d -= 1
        elif c in '"\'`':
            q = c; i += 1
            while i < n and src[i] != q:
                if src[i] == '\\': i += 1
                i += 1
        i += 1
        if i - m.end() > 60000: break
    body = src[m.end():i]; ln = line_of(m.start())
    call = lambda v: re.search(r'\b' + re.escape(v) + r'\b\s*(\(|\.apply|\.call)', body)
    kind = 'D'
    if saved and orig == name and call(saved): kind = 'S'
    else:
        prev = src[max(0, m.start() - 200):m.start()]
        mm = re.findall(r'(?:const|let|var)\s+(_\w+)\s*=\s*(?:window\.)?' + re.escape(name) + r'\b', prev)
        if mm and call(mm[-1]): kind = 'S'
    res[name].append((ln, kind, header(ln)))
decl = set(re.findall(r'^\s*(?:async\s+)?function\s+(\w+)\s*\(', src, re.M))
loc = {n: v for n, v in res.items() if not n.startswith('__')}; hk = {n: v for n, v in res.items() if n.startswith('__')}
cnt = lambda d: (sum(len(v) for v in d.values()), sum(1 for v in d.values() for _, k, _h in v if k == 'S'))
a = cnt(loc); b = cnt(hk); ilk = sum(1 for n, v in res.items() if n not in decl and v[0][1] == 'D')
w = lambda s='': print(s)
w('# İşlev yeniden atama envanteri (T7)'); w()
w('Bu belge `python3 tools/fonksiyon_envanteri.py` ile üretilir (salt okunur analiz). Hiçbir işlev yeniden düzenlenmedi.')
w('Kaynak: `js/game.js` (sürüm %s, %d satır). Satır numaraları o sürümden.' % (ver.group(1) if ver else '?', len(L))); w()
w('## 1. Sayılar'); w()
w('Önceki bir denetimde geçen "64" rakamı yalnız satır başındaki kalıbı sayıyordu; eksikti. Bu envanter bütün atamaları sayar.'); w()
w('| Sınıf | Atama | Önceki işlevi saran | Saran olmayan (değiştiren ya da ilk tanım) | İşlev adı |'); w('|---|---|---|---|---|')
w('| Yerel işlev | %d | %d | %d | %d |' % (a[0], a[1], a[0] - a[1], len(loc)))
w('| `window.__...` kancaları | %d | %d | %d | %d |' % (b[0], b[1], b[0] - b[1], len(hk)))
w('| **Toplam** | **%d** | %d | %d | %d |' % (a[0] + b[0], a[1] + b[1], a[0] + b[0] - a[1] - b[1], len(res))); w()
w('"Saran olmayan" sayısı `function` bildirimi olmayan %d adın **ilk tanımını** da içerir; hepsi hata değildir. Dinamik atama, nesne özellikleri ve ok işlevleri sayıya dahil değil.' % ilk); w()
w('## 2. Dört ana işlev'); w()
w('Kural: **atama sırası = dosya sırası.** En son atanan en dış katmandır: çağrıldığında önce o çalışır, saran ise bir önceki katmanı çağırır. Saran olmayan bir atama önceki katmanı çağırmaz; ondan önceki sarmalayıcılar o noktada atlanır.'); w()
for nme in ['renderExtras', 'renderDock', 'dockLayout', 'killNpc']:
    w('### `%s` (%d atama)' % (nme, len(res[nme]))); w('| # | Satır | Tür | Bölüm / amaç (yakın yorumdan) |'); w('|---|---|---|---|')
    for k, (ln, kind, h) in enumerate(res[nme], 1): w('| %d | %d | %s | %s |' % (k, ln, 'sarar' if kind == 'S' else '**ilk tanım / değiştirir**', h.replace('|', '/')))
    w()
w('Bağımlılık notları:')
w('- `renderExtras` ve `renderDock` istasyon menüsünü, `dockLayout` ekran düzenini, `killNpc` öldürme sonrası etkileri (XP, itibar, görev sayaçları, aranma, yetenekler) üst üste ekler. **Katman sırası değişirse** düzen ya da ödül/sayaç sırası değişir.')
w("- `killNpc` katmanlarının çoğu `by === 'player'`, düşman olma ve `npcs.indexOf(n) >= 0` (zaten silinmiş mi) koşullarını kontrol eder. **Yeni katman eklerken bu desen korunmalı**; aksi halde aynı öldürme için ikinci kez ödül yazılır (çift gelir).")
w('- Bazı `renderDock`/`renderExtras` katmanları `try/catch` içinde; bir katmanın hatası alttakileri çalıştırmayabilir.'); w()
w('## 3. Saran olmayan atamalar'); w('| İşlev | Satırlar | Toplam atama |'); w('|---|---|---|')
for nme, v in sorted(res.items(), key=lambda x: -sum(1 for _, k, _h in x[1] if k == 'D')):
    ds = [ln for ln, k, _h in v if k == 'D']
    if ds: w('| `%s` | %s | %d |' % (nme, ', '.join(map(str, ds)), len(v)))
w(); w('## 4. Bütün işlevler'); w('| İşlev | Atama | Sarar | Diğer | İlk-son satır |'); w('|---|---|---|---|---|')
for nme, v in sorted(res.items(), key=lambda x: -len(x[1])):
    s = sum(1 for _, k, _h in v if k == 'S'); w('| `%s` | %d | %d | %d | %d-%d |' % (nme, len(v), s, len(v) - s, v[0][0], v[-1][0]))
