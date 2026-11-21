#!/usr/bin/env python3
"""Çevrimdışı liste güvenlik denetimi (T9), salt okunur.
offline_list.py `git ls-files` kullandığı için henüz `git add` edilmemiş yeni dosyalar listeye girmez (Hayalet GLB'lerinde yaşandı).
Bu betik DİSKİ tarar, Git'in izlediği dosyalarla ve offline.json ile karşılaştırır, sorunları raporlar. Hiçbir dosyayı değiştirmez.
Kullanım: python3 offline_kontrol.py [repo_kökü]   Çıkış kodu: 0 sorun yok, 1 sorun var."""
import hashlib, json, os, subprocess, sys
root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
ROOTS = ('assets', 'vendor', 'models')                      # offline_list.py ile aynı köklerle uyumlu
EXTRA_FILES = ('manifest.webmanifest',)
SKIP_EXT = ('.md', '.txt')
def under_roots(p): return p.split('/')[0] in ROOTS or p in EXTRA_FILES or (p.startswith('muzik_') and p.endswith('.mp3') and '/' not in p)
def ok(p): return under_roots(p) and not p.endswith(SKIP_EXT)
# 1) diskteki dosyalar
disk = set()
for r in ROOTS:
    for d, _, fs in os.walk(os.path.join(root, r)):
        for f in fs: disk.add(os.path.relpath(os.path.join(d, f), root).replace(os.sep, '/'))
for f in os.listdir(root):
    if (f in EXTRA_FILES) or (f.startswith('muzik_') and f.endswith('.mp3')): disk.add(f)
disk = {p for p in disk if ok(p)}
# 2) Git'in izlediği dosyalar
git = set(subprocess.run(['git', 'ls-files'], cwd=root, capture_output=True, text=True).stdout.split('\n'))
git = {p for p in git if ok(p)}
# 3) mevcut liste
lst = json.load(open(os.path.join(root, 'offline.json')))['files']
h = lambda p: hashlib.sha1(open(os.path.join(root, p), 'rb').read()).hexdigest()[:10]
untracked = sorted(disk - git)                              # diskte var, Git izlemiyor: offline_list.py bunu listeye KOYMAZ
tracked_missing = sorted((disk & git) - set(lst))           # Git izliyor ama liste eski: offline_list.py yeniden çalıştırılmalı
extra = sorted(set(lst) - disk)                             # listede var, diskte yok
stale = sorted(p for p in lst if p in disk and h(p) != lst[p])   # özet eski
bad = 0
def show(title, items, hint):
    global bad
    if items:
        bad += 1; print('UYARI:', title, '(%d)' % len(items)); [print('   ', p) for p in items[:20]]; print('    →', hint)
show('Diskte var ama Git izlemiyor (çevrimdışı listeye GİRMEZ)', untracked, 'önce `git add` yap, sonra tools/offline_list.py çalıştır')
show('Git izliyor ama offline.json\'da yok', tracked_missing, 'tools/offline_list.py çalıştır')
show('offline.json\'da var ama diskte yok', extra, 'tools/offline_list.py çalıştır (liste yenilenir)')
show('offline.json özeti dosya içeriğiyle uyuşmuyor', stale, 'tools/offline_list.py çalıştır')
print('SONUÇ:', 'TEMİZ' if not bad else 'SORUN VAR', '| disk', len(disk), 'git', len(git), 'liste', len(lst))
sys.exit(1 if bad else 0)
