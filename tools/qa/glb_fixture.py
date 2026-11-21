#!/usr/bin/env python3
"""Test için küçük sahte GLB dosyaları üretir (Asset Factory modeli değil). Kullanım: python3 tools/qa/glb_fixture.py <çıktı_klasörü>
npc_raider.glb (LOD0/LOD1 + ANCH_*), ast_titan.glb (AST_titan_1..3 + PICK_titan), st_ankora.glb (LOD0/LOD1), index.json"""
import json, os, struct, sys
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
def octa(sx, sy, sz):
    v = [(sx,0,0),(-sx,0,0),(0,sy,0),(0,-sy,0),(0,0,sz),(0,0,-sz)]
    f = [(0,2,4),(2,1,4),(1,3,4),(3,0,4),(2,0,5),(1,2,5),(3,1,5),(0,3,5)]
    return v, [i for t in f for i in t]
def glb(path, nodes, meshes):
    buf = bytearray(); views = []; accs = []; mdefs = []
    for (v, idx) in meshes:
        pb = b''.join(struct.pack('<3f', *p) for p in v); o = len(buf); buf += pb; views.append({'buffer': 0, 'byteOffset': o, 'byteLength': len(pb), 'target': 34962})
        ib = struct.pack('<%dH' % len(idx), *idx); ib += b'\0' * (-len(ib) % 4); o2 = len(buf); buf += ib; views.append({'buffer': 0, 'byteOffset': o2, 'byteLength': len(idx) * 2, 'target': 34963})
        xs = [p[0] for p in v]; ys = [p[1] for p in v]; zs = [p[2] for p in v]; k = len(accs)
        accs.append({'bufferView': len(views) - 2, 'componentType': 5126, 'count': len(v), 'type': 'VEC3', 'min': [min(xs), min(ys), min(zs)], 'max': [max(xs), max(ys), max(zs)]})
        accs.append({'bufferView': len(views) - 1, 'componentType': 5123, 'count': len(idx), 'type': 'SCALAR'})
        mdefs.append({'name': 'm%d' % len(mdefs), 'primitives': [{'attributes': {'POSITION': k}, 'indices': k + 1, 'material': 0}]})
    j = {'asset': {'version': '2.0'}, 'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': nodes, 'meshes': mdefs, 'accessors': accs, 'bufferViews': views,
         'buffers': [{'byteLength': len(buf)}], 'materials': [{'pbrMetallicRoughness': {'baseColorFactor': [0.7, 0.75, 0.85, 1], 'metallicFactor': 0.3, 'roughnessFactor': 0.6}}]}
    js = json.dumps(j, separators=(',', ':')).encode(); js += b' ' * (-len(js) % 4); buf += b'\0' * (-len(buf) % 4)
    data = struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(js) + 8 + len(buf)) + struct.pack('<I4s', len(js), b'JSON') + js + struct.pack('<I4s', len(buf), b'BIN\0') + bytes(buf)
    open(path, 'wb').write(data)
# NPC: burun +Z, uzunluk ~1
glb(os.path.join(out, 'npc_raider.glb'),
    [{'name': 'SD_fix_npc', 'children': [1, 2, 3, 4, 6]}, {'name': 'ANCH_ENG_0', 'translation': [0, 0, -0.5]}, {'name': 'ANCH_NAV_0', 'translation': [0.3, 0.05, 0.1]},
     {'name': 'ANCH_MUZ_0', 'translation': [0, 0, 0.5]}, {'name': 'LOD0', 'children': [5]}, {'name': 'LOD0_body', 'mesh': 0}, {'name': 'LOD1', 'children': [7]}, {'name': 'LOD1_body', 'mesh': 1}],
    [octa(0.3, 0.1, 0.5), octa(0.3, 0.1, 0.5)[0:1] and ([(0.3,0,0),(-0.3,0,0),(0,0.1,0),(0,0,0.5)], [0,2,3, 2,1,3, 1,0,3, 0,1,2])])
# Asteroit
glb(os.path.join(out, 'ast_titan.glb'),
    [{'name': 'SD_fix_ast', 'children': [1, 2, 3, 4]}, {'name': 'AST_titan_1', 'mesh': 0}, {'name': 'AST_titan_2', 'mesh': 1}, {'name': 'AST_titan_3', 'mesh': 2}, {'name': 'PICK_titan', 'mesh': 3}],
    [octa(0.5, 0.45, 0.5), octa(0.5, 0.5, 0.4), octa(0.45, 0.5, 0.5), octa(0.1, 0.1, 0.1)])
# İstasyon
glb(os.path.join(out, 'st_ankora.glb'),
    [{'name': 'SD_fix_st', 'children': [1, 3]}, {'name': 'LOD0', 'children': [2]}, {'name': 'LOD0_body', 'mesh': 0}, {'name': 'LOD1', 'children': [4]}, {'name': 'LOD1_body', 'mesh': 1}],
    [octa(0.5, 0.1, 0.5), octa(0.5, 0.1, 0.5)])
json.dump({'npc_raider': {'url': 'models/glb/npc_raider.glb'}, 'ast_titan': {'url': 'models/glb/ast_titan.glb'}, 'st_ankora': {'url': 'models/glb/st_ankora.glb'}}, open(os.path.join(out, 'index.json'), 'w'))
print('tamam', out)
