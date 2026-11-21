"""Oyuncu gemisi dış modeli ailesi: spec.params.layout → families.ship.<layout>.build(spec, mats)."""
import importlib


def build(spec, mats):
    return importlib.import_module('families.ship.' + spec['params']['layout']).build(spec, mats)
