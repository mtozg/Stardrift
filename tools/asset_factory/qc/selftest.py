"""QC öz-testi: sağlam bir GLB'yi bilerek bozar ve her bozulmanın ilgili testte FAIL verdiğini doğrular.
Kullanım: python qc/selftest.py <sağlam.glb> <spec_id> <çalışma_klasörü>
QC'nin "geçti" demesinin anlamlı olması için, bozuk dosyalarda "kaldı" demesi gerekir."""
import copy, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from core import glbpack
from core.paths import QC, load_json, load_spec
from qc import glb_checks

good, sid, wd = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(wd, exist_ok=True)
spec = load_spec(sid)
budgets, rules = load_json(os.path.join(QC, 'budgets.json')), load_json(os.path.join(QC, 'rules.json'))
J, BIN = glbpack.read(good)
VIEWS = [BIN[bv.get('byteOffset', 0): bv.get('byteOffset', 0) + bv['byteLength']] for bv in J['bufferViews']]


def mutate(name, fn):
    j, views = copy.deepcopy(J), list(VIEWS)
    fn(j, views)
    p = os.path.join(wd, 'bad_%s.glb' % name)
    glbpack.write(p, j, views)
    return p


def body_prim(j, lod=0):
    i = [k for k, n in enumerate(j['nodes']) if n.get('name') == 'LOD%d_body' % lod][0]
    return j['meshes'][j['nodes'][i]['mesh']]['primitives'][0]


def flip_winding(j, views):
    p = body_prim(j)
    a = j['accessors'][p['indices']]
    bv = a['bufferView']
    dt = {5123: np.uint16, 5125: np.uint32}[a['componentType']]
    idx = np.frombuffer(views[bv], dt).reshape(-1, 3).copy()
    views[bv] = idx[:, ::-1].copy().tobytes()
    na = j['accessors'][p['attributes']['NORMAL']]
    nb = na['bufferView']
    n = np.frombuffer(views[nb], np.float32).copy() * -1
    views[nb] = n.tobytes()


def emissive_strength(j, views):
    m = [m for m in j['materials'] if m['name'] == 'MAT_emit'][0]
    m['emissiveFactor'] = [1.0, 1.0, 1.0]
    m.setdefault('extensions', {})['KHR_materials_emissive_strength'] = {'emissiveStrength': 4.0}
    j.setdefault('extensionsUsed', []).append('KHR_materials_emissive_strength')


def bad_names(j, views):
    for n in j['nodes']:
        if n.get('name') == 'SOCK_engine_0':
            n['name'] = 'Engine'
        if n.get('name') == 'LOD0_body':
            n['name'] = 'Cube.001'


def extra_material(j, views):
    for k in range(3):
        j['materials'].append({'name': 'Material.%03d' % k, 'doubleSided': True})


CASES = {
    'flip_winding': (flip_winding, ['geom.backface_visible']),
    'emissive_strength': (emissive_strength, ['ext.allowed']),
    'bad_names': (bad_names, ['contract.names', 'contract.sockets', 'contract.mesh_roles']),
    'extra_material': (extra_material, ['mat.count', 'mat.names']),
}
res, ok_all = {}, True
for name, (fn, expect) in CASES.items():
    p = mutate(name, fn)
    items, _ = glb_checks.run(p, spec, budgets, rules)
    fails = {it['id'] for it in items if it['status'] == 'FAIL'}
    if name == 'flip_winding':
        out = subprocess.run([sys.executable, os.path.join(QC, 'blender_checks.py'), p, '1024', p + '.json'], capture_output=True, text=True)
        bc = json.load(open(p + '.json'))
        if bc['backface_visible'] > rules['backface_visible_fail']:
            fails.add('geom.backface_visible')
        res[name + '_backface'] = bc['backface_visible']
    caught = [e for e in expect if e in fails]
    ok = len(caught) == len(expect)
    ok_all &= ok
    res[name] = {'expected_fail': expect, 'caught': caught, 'ok': ok}
    print('%-18s %s  beklenen=%s  yakalanan=%s' % (name, 'YAKALANDI' if ok else 'KAÇTI', expect, caught))
json.dump(res, open(os.path.join(wd, 'selftest.json'), 'w'), indent=1)
print('RESULT', json.dumps({'selftest_ok': ok_all, **{k: v['ok'] for k, v in res.items() if isinstance(v, dict)}}))
