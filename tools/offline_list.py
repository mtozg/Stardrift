#!/usr/bin/env python3
"""Çevrimdışı paket listesi: offline.json'u yeniden üretir.
Görsel, ses, müzik, yazı tipi, 3B model (models/) ya da vendor dosyası eklediğinde/değiştirdiğinde çalıştır:
    python3 tools/offline_list.py
Service worker (sw.js) bu listeye bakıp eksik ya da içeriği değişmiş dosyaları indirir."""
import hashlib, json, os, subprocess
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = subprocess.run(['git', 'ls-files', 'assets', 'vendor', 'models', 'manifest.webmanifest'], cwd=root, capture_output=True, text=True).stdout.split()
files += sorted(f for f in os.listdir(root) if f.startswith('muzik_') and f.endswith('.mp3'))
# T9: Git'in izlemediği (henüz `git add` edilmemiş) dosyalar listeye girmez; sessizce atlanmasın diye uyar. Çıktı (offline.json) değişmez.
_tracked = set(files)
_untracked = []
for _r in ('assets', 'vendor', 'models'):
    for _d, _, _fs in os.walk(os.path.join(root, _r)):
        for _f in _fs:
            _p = os.path.relpath(os.path.join(_d, _f), root).replace(os.sep, '/')
            if _p not in _tracked and not _p.endswith(('.md', '.txt')): _untracked.append(_p)
if _untracked:
    import sys
    print('UYARI: %d dosya Git tarafından izlenmiyor, çevrimdışı listeye GİRMEDİ (önce `git add` yap, sonra bu betiği yeniden çalıştır):' % len(_untracked), file=sys.stderr)
    for _p in sorted(_untracked)[:20]: print('   ', _p, file=sys.stderr)
out = {}
for f in sorted(set(files)):
    p = os.path.join(root, f)
    if os.path.isfile(p) and not f.endswith(('.md', '.txt')):
        out[f] = hashlib.sha1(open(p, 'rb').read()).hexdigest()[:10]
json.dump({'files': out}, open(os.path.join(root, 'offline.json'), 'w'), separators=(',', ':'))
print(len(out), 'dosya,', round(sum(os.path.getsize(os.path.join(root, f)) for f in out) / 1048576, 1), 'MB')
