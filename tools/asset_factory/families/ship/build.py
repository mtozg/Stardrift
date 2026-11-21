"""Oyuncu gemisi dış modeli ailesi: spec.params.layout → families.ship.<layout>.build(spec, mats)."""
import importlib


def build(spec, mats):
    return importlib.import_module('families.ship.' + spec['params']['layout']).build(spec, mats)


def preview(spec, out, fast, obs, probe=False):
    """gemi ailesi: model.py yalnız geometriyi kurar ve model.blend'e yazar (görünümler prepare sonrası qc/ship_views.py ile alınır)"""
    return {'note': 'ship family: lookdev yok'}
