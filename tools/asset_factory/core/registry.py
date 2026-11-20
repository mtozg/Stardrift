"""Varlık kaydı ve onay kapıları (bpy gerektirmez).
Durumlar: draft → modeled → visual_approved → prepared → qc_pass|qc_fail → tech_approved → delivered → integrated"""
import datetime, os
from .paths import FACTORY, load_json, save_json

PATH = os.path.join(FACTORY, 'registry.json')
ORDER = ['draft', 'modeled', 'visual_approved', 'prepared', 'qc_fail', 'qc_pass', 'tech_approved', 'delivered', 'integrated']


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def load():
    if os.path.exists(PATH):
        return load_json(PATH)
    return {'version': 1, 'assets': {}}


def save(reg):
    save_json(PATH, reg)


def get(asset_id, create=False):
    reg = load()
    a = reg['assets'].get(asset_id)
    if a is None and create:
        a = {'state': 'draft', 'rev': 1, 'history': [], 'timings': {}, 'approvals': []}
        reg['assets'][asset_id] = a
        save(reg)
    return a


def update(asset_id, **fields):
    reg = load()
    a = reg['assets'].setdefault(asset_id, {'state': 'draft', 'rev': 1, 'history': [], 'timings': {}, 'approvals': []})
    a.update(fields)
    save(reg)
    return a


def transition(asset_id, state, reason='', **extra):
    reg = load()
    a = reg['assets'][asset_id]
    a['history'].append({'t': _now(), 'from': a['state'], 'to': state, 'reason': reason, **extra})
    a['state'] = state
    save(reg)


def record_timing(asset_id, stage, seconds):
    reg = load()
    reg['assets'][asset_id].setdefault('timings', {})[stage] = round(seconds, 1)
    save(reg)


def approve(asset_id, gate, by, note, accept_warn=None):
    reg = load()
    a = reg['assets'][asset_id]
    need = {'visual': 'modeled', 'tech': 'qc_pass'}[gate]
    if a['state'] != need:
        raise SystemExit('ONAY REDDİ: %s kapısı için durum "%s" olmalı, şu an "%s"' % (gate, need, a['state']))
    a['approvals'].append({'t': _now(), 'gate': gate, 'by': by, 'note': note, 'accept_warn': accept_warn or []})
    save(reg)
    transition(asset_id, {'visual': 'visual_approved', 'tech': 'tech_approved'}[gate], 'onay: ' + note, by=by)


def require(asset_id, *states):
    a = get(asset_id)
    if a is None or a['state'] not in states:
        raise SystemExit('KAPI: bu adım için durum %s olmalı; şu an %s' % ('/'.join(states), a and a['state']))
    return a
