"""Fabrika yolları ve JSON yardımcıları (bpy gerektirmez)."""
import json, os, hashlib

FACTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_ROOT = os.path.abspath(os.path.join(FACTORY, '..', '..'))   # yalnızca OKUNUR (vendor/three.min.js, assets/img referansları)
WORK = os.path.join(FACTORY, 'work')
DELIVERIES = os.path.join(FACTORY, 'deliveries')
LIBRARY = os.path.join(FACTORY, 'library')
SPECS = os.path.join(FACTORY, 'specs')
QC = os.path.join(FACTORY, 'qc')


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def find_spec(asset_id):
    for root, _, files in os.walk(SPECS):
        if asset_id + '.json' in files:
            return os.path.join(root, asset_id + '.json')
    raise FileNotFoundError('spec bulunamadı: ' + asset_id)


def load_spec(asset_id):
    return load_json(find_spec(asset_id))


def file_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def json_hash(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def work_dir(asset_id, rev, stage=None):
    d = os.path.join(WORK, asset_id, 'r%03d' % rev)
    if stage:
        d = os.path.join(d, stage)
    os.makedirs(d, exist_ok=True)
    return d
