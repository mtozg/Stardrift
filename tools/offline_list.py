#!/usr/bin/env python3
"""Çevrimdışı paket listesi: offline.json'u yeniden üretir.
Görsel, ses, müzik, yazı tipi ya da vendor dosyası eklediğinde/değiştirdiğinde çalıştır:
    python3 tools/offline_list.py
Service worker (sw.js) bu listeye bakıp eksik ya da içeriği değişmiş dosyaları indirir."""
import hashlib, json, os, subprocess
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = subprocess.run(['git', 'ls-files', 'assets', 'vendor', 'manifest.webmanifest'], cwd=root, capture_output=True, text=True).stdout.split()
files += sorted(f for f in os.listdir(root) if f.startswith('muzik_') and f.endswith('.mp3'))
out = {}
for f in sorted(set(files)):
    p = os.path.join(root, f)
    if os.path.isfile(p) and not f.endswith(('.md', '.txt')):
        out[f] = hashlib.sha1(open(p, 'rb').read()).hexdigest()[:10]
json.dump({'files': out}, open(os.path.join(root, 'offline.json'), 'w'), separators=(',', ':'))
print(len(out), 'dosya,', round(sum(os.path.getsize(os.path.join(root, f)) for f in out) / 1048576, 1), 'MB')
