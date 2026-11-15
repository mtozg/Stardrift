"""Deterministik rastgelelik: her alt sistem kendi adıyla ana seed'den türetilmiş bağımsız bir üreteç alır.
Böylece bir parçaya yeni rastgele çağrı eklemek diğer parçaların sonucunu kaydırmaz."""
import hashlib, random


def rng(seed, *names):
    key = ('%d|' % int(seed)) + '|'.join(str(n) for n in names)
    return random.Random(int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], 'big'))
