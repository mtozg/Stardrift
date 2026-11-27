/* Stardrift GLB yükleyici (prototip hazırlığı). VARSAYILAN KAPALI: yalnız adrese ?glb=1 eklenince (ya da localStorage sd_glb=1) index.html tarafından yüklenir; ?glb=0 kapatır.
   Kapalıyken bu dosya hiç indirilmez ve oyun bugünkü gibi çalışır. Model bulunamaz/yüklenemezse oyun mevcut kabuk modelle (çizimden üretilen 3B, sprite) devam eder.
   Sözleşme (docs/GLB_YUKLEYICI.md): burun +Z, yukarı +Y, uzunluk 1,0 birim; çapa düğümleri ANCH_ENG_*, ANCH_NAV_*, ANCH_MUZ_*; LOD0/LOD1 grupları;
   asteroit: AST_<tür>_<n> ve PICK_<tür>. Model listesi: models/glb/index.json (yoksa hiçbir şey denenmez). */
(function(){
  'use strict';
  var T = window.THREE; if (!T || window.__glb) return;
  var v = '?v=' + (window.SD_VERSION || '');
  var G = window.__glb = { index: {}, stats: { yuklenen: 0, basarisiz: 0, npc: 0, kayaOrnek: 0, kayaKumeleri: 0, lodDegisim: 0, istasyon: 0 }, kapali: false };
  var cache = {}, RETRY = 60000;

  // ---------- model listesi ----------
  G.ready = fetch('models/glb/index.json' + v).then(function(r){ return r.ok ? r.json() : {}; }).catch(function(){ return {}; }).then(function(j){ G.index = j || {}; return G.index; });

  // ---------- yükleyici (tek örnek, gerekirse GLTFLoader betiği tembel yüklenir) ----------
  var loaderP = null;
  function loader(){
    return loaderP || (loaderP = new Promise(function(res, rej){
      var go = function(){ try { res(new T.GLTFLoader()); } catch (e) { rej(e); } };
      if (T.GLTFLoader) return go();
      var s = document.createElement('script'); s.src = 'vendor/GLTFLoader.js' + v; s.onload = go; s.onerror = function(){ loaderP = null; rej(new Error('GLTFLoader yüklenemedi')); }; document.head.appendChild(s);
    }));
  }
  function url(key){
    var m = G.index[key]; if (!m) return null;
    return ((m.urlM && matchMedia('(pointer:coarse)').matches && Math.min(screen.width, screen.height) < 600) ? m.urlM : m.url) + v;
  }
  function byName(root, name){ var r = null; root.traverse(function(o){ if (!r && o.name === name) r = o; }); return r; }
  function prep(key, gltf){
    var root = gltf.scene; root.updateMatrixWorld(true);
    var anch = { eng: [], nav: [], muz: [] }, rm = [];
    root.traverse(function(o){
      if (/^ANCH_(ENG|NAV|MUZ)_/.test(o.name)){ var p = new T.Vector3(); o.getWorldPosition(p); anch[o.name.slice(5, 8).toLowerCase()].push(p); rm.push(o); }
    });
    rm.forEach(function(o){ if (o.parent) o.parent.remove(o); });
    var lod0 = byName(root, 'LOD0') || root, lod1 = byName(root, 'LOD1');
    var m = G.index[key] || {};
    return { key: key, root: root, lod0: lod0, lod1: lod1, anch: anch, rot: m.rot || null, s: m.s || 1, gltf: gltf };
  }
  /* karanlık görünüm düzeltmesi: GLB malzemelerine oyunun uzay yansıma haritası verilir (yalnız bu modeller; sahne ortamı değişmez). Dosyada kendi haritası varsa dokunulmaz. Metallik yalnız metalik doku yoksa düşürülür. */
  function envVer(root){
    var env = window.__spaceEnv && window.__spaceEnv(); if (!env) return;
    root.traverse(function(o){ if (!o.isMesh || !o.material) return; (Array.isArray(o.material) ? o.material : [o.material]).forEach(function(m){ if (m.isMeshStandardMaterial && !m.envMap){ m.envMap = env; m.envMapIntensity = 1.2; if (!m.metalnessMap) m.metalness = Math.min(m.metalness, 0.4); m.needsUpdate = true; } }); });   /* tam metal (1,0) + koyu uzay haritası = simsiyah: yansıma haritası + metalliği 0,4'e indirme (oyun içi 4 değişken denemesinde okunur biçim veren en sade ayar) */
  }
  /* kaya: metal değil (ORM haritasındaki metal kanalı yüzünden koyu/siyah çıkıyordu): metalik 0, mat; doku (renk) aynen kalır */
  function kayaMat(root){
    root.traverse(function(o){ if (!o.isMesh || !o.material) return; (Array.isArray(o.material) ? o.material : [o.material]).forEach(function(m){ if (!m.isMeshStandardMaterial) return; m.metalness = 0.02; m.metalnessMap = null; m.roughness = 1; m.envMapIntensity = 3.0; m.emissiveMap = null; m.emissive.setHex(0x2e3440); m.emissiveIntensity = 1; m.needsUpdate = true; }); });
  }
  G.load = function(key){
    return G.ready.then(function(){
      if (!G.index[key]) return Promise.reject(new Error('model listede yok: ' + key));
      var c = cache[key];
      if (c){ if (c.p) return c.p; if (c.fail && performance.now() - c.fail < RETRY) return Promise.reject(c.err); }
      c = cache[key] = {};
      c.p = loader().then(function(L){ return new Promise(function(res, rej){ L.load(url(key), function(g){ try { var p = prep(key, g); envVer(p.root); if (/^ast_/.test(key)) kayaMat(p.root); G.stats.yuklenen++; res(p); } catch (e) { rej(e); } }, undefined, rej); }); })
        .catch(function(e){ G.stats.basarisiz++; c.p = null; c.fail = performance.now(); c.err = e; try { console.warn('[glb] ' + key + ': ' + ((e && e.message) || e)); } catch (x) {} throw e; });
      return c.p;
    });
  };
  function inst(p){ var r = p.root.clone(true); if (p.rot) r.rotation.set(p.rot[0] || 0, p.rot[1] || 0, p.rot[2] || 0); return r; }

  // ---------- NPC ----------
  var npcs = [];
  // game.js dressNpcs sonunda çağırır: GLB hazırsa kabuk modelin yerine geçer; yoksa hiçbir şey olmaz
  G.npc = function(n, def){
    var key = 'npc_' + n.type;
    G.ready.then(function(){ if (!G.index[key]) return; return G.load(key); }).then(function(p){
      if (!p || !n.g.parent || n._glb) return;
      var L = def.L, r = inst(p), fb = [];
      r.scale.setScalar(L * p.s); n.g.children.forEach(function(c){ if (!c.isSprite && !c.userData.glb) fb.push(c); });
      r.userData.glb = true; n.g.add(r);
      var a = p.anch.eng[0]; if (a && n.eng) n.eng.position.set(a.x * L, a.y * L, a.z * L);
      a = p.anch.nav[0]; if (a && n.nav) n.nav.position.set(a.x * L, a.y * L, a.z * L);
      n._glb = { r: r, lod0: null, lod1: null, fb: fb, mode: -1, L: L, p: p };
      // klonda LOD gruplarını bul (ad ile)
      n._glb.lod0 = byName(r, 'LOD0') || r; n._glb.lod1 = byName(r, 'LOD1');
      npcs.push(n); G.stats.npc++; setMode(n, 0, true);
    }).catch(function(){});
  };
  function setMode(n, mode, force){
    var g = n._glb; if (!g || (g.mode === mode && !force)) return;
    g.mode = mode; G.stats.lodDegisim++;
    if (g.lod1 && g.lod1 !== g.lod0){ g.lod0.visible = mode === 0; g.lod1.visible = mode === 1; } else { g.lod0.visible = mode <= 1; }
    g.r.visible = mode <= 1;
    for (var i = 0; i < g.fb.length; i++) g.fb[i].visible = mode === 2;
  }

  // ---------- asteroit örnekleme ----------
  var rocks = [], ims = {}, ROCK_K = 1.35, CAP = 128, rockProto = {};
  function rockModel(type){
    if (rockProto[type] !== undefined) return rockProto[type];
    rockProto[type] = null;
    G.ready.then(function(){ var k = 'ast_' + type; if (!G.index[k]) return; return G.load(k); }).then(function(p){
      if (!p) return; var vars = [];
      p.root.traverse(function(o){ if (o.isMesh && new RegExp('^AST_' + type + '_\\d+$').test(o.name)) vars.push(o); });
      if (!vars.length) return;
      var out = vars.map(function(o){ o.geometry.computeBoundingSphere(); var bs = o.geometry.boundingSphere; return { geo: o.geometry, mat: o.material, rad: Math.max(0.001, bs.radius), name: o.name }; });
      rockProto[type] = out;
    }).catch(function(){});
    return null;
  }
  // game.js rockMesh sprite'ı oluşturunca çağırır: sprite yedek olarak kalır, yakındayken gizlenir ve örnekli model çizilir
  G.rock = function(sp, type, r){ rocks.push({ o: sp, type: type, r: r, vi: Math.random() }); rockModel(type); };
  function imFor(type, vi, parent){
    var protos = rockProto[type]; if (!protos) return null; var i = Math.min(protos.length - 1, Math.floor(vi * protos.length)), id = type + '#' + i;
    var e = ims[id];
    if (!e){ var pr = protos[i]; var m = new T.InstancedMesh(pr.geo, pr.mat, CAP); m.frustumCulled = false; m.count = 0; m.name = 'AST_inst_' + id; parent.add(m); e = ims[id] = { m: m, rad: pr.rad, n: 0 }; G.stats.kayaKumeleri++; }
    return e;
  }

  // ---------- kırılan kaya parçaları: cevher alınan parça (PICK_<tür>) ve enkaz (prop_debris0..3) ----------
  // parent'a (sprite/mesh) çocuk olarak eklenir; parent'ın kendi görünümü GLB hazırsa gizlenir. size: dünya boyutu (parent ölçeğine göre göreli).
  var pickProto = {};
  function pickOf(type){
    return G.load('ast_' + type).then(function(p){
      if (pickProto[type]) return pickProto[type];
      var n = byName(p.root, 'PICK_' + type); if (!n) return null;
      var c = n.clone(true); c.position.set(0, 0, 0); c.rotation.set(0, 0, 0); c.scale.set(1, 1, 1);
      var bb = new T.Box3().setFromObject(c), sz = bb.getSize(new T.Vector3()), mx = Math.max(sz.x, sz.y, sz.z, 1e-4), ctr = bb.getCenter(new T.Vector3());
      var w = new T.Group(); c.position.sub(ctr); w.add(c); w.userData.unit = 1 / mx; return (pickProto[type] = w);
    });
  }
  function hideVis(o){ if (o.isSprite || o.isMesh){ if (!invis) invis = new T.MeshBasicMaterial({ visible: false }); if (o.isSprite) o.material.visible = false; else { o.userData.glbMat = o.material; o.material = invis; } } }
  G.pick = function(parent, type, size){
    if (G.kapali || !G.index['ast_' + type]) return;
    pickOf(type).then(function(w){ if (!w || !parent) return; var r = w.clone(true), ps = parent.scale, u = size * w.userData.unit; r.scale.set(u / ps.x, u / ps.y, u / ps.z); r.userData.glb = true;   // parent ölçeği iptal edilir: dünya boyutu = size
       r.traverse(function(o){ o.userData.shared = true; }); parent.add(r); hideVis(parent); }).catch(function(){});
  };
  var debrisN = ['debris0', 'debris1', 'debris2', 'debris3'];
  G.debris = function(parent, type, size){   // type: 'hurda' ise enkaz çeşitleri, değilse o cevherin PICK parçası
    if (G.kapali) return;
    if (type === 'hurda'){ var k = debrisN[(Math.random() * debrisN.length) | 0]; if (!G.index['prop_' + k]) return;
      G.load('prop_' + k).then(function(p){ if (!p || !parent) return; var r = inst(p), ps = parent.scale, u = size * p.s; r.scale.set(u / ps.x, u / ps.y, u / ps.z); r.userData.glb = true; r.traverse(function(o){ o.userData.shared = true; }); parent.add(r); hideVis(parent); }).catch(function(){}); }
    else G.pick(parent, type, size);
  };

  // ---------- küçük nesneler (prop): roket, kaçak yük, sonda, buz devi, monolit, ini, uydu, lav kayası, enkaz ----------
  // Sözleşme (AF): ölçek = EN BÜYÜK boyut 1,0; merkez orijin; yukarı +Y; uzun eksen +Z; çapa yok. Anahtar: prop_<ad> (sd_prop_<ad>.glb).
  // spec: { pos: Vector3 (yerel), rot: Euler, size: en büyük boyut (dünya birimi), hide: [Mesh] (kabuk parçaları, GLB hazırsa görünmez olur) }
  var invis = null;
  G.prop = function(key, parent, spec){
    var k = 'prop_' + key;
    G.ready.then(function(){ if (!G.index[k]) return; return G.load(k); }).then(function(p){
      if (!p || !parent || G.kapali) return;
      var r = inst(p); r.userData.glb = true; r.scale.setScalar(spec.size * p.s);
      if (spec.pos) r.position.copy(spec.pos); if (spec.rot) r.rotation.copy(spec.rot); if (spec.yaw) r.rotation.y += spec.yaw;
      var l1 = byName(r, 'LOD1'), l0 = byName(r, 'LOD0'); if (l1 && l0 && l1 !== l0) l1.visible = false;
      r.traverse(function(o){ o.userData.shared = true; });
      parent.add(r); G.stats.prop = (G.stats.prop || 0) + 1; (G.props || (G.props = [])).push({ key: key, obj: r });   // props: test için konum listesi
      (spec.hide || []).forEach(function(o){ if (!o) return; if (o.isMesh){ if (!invis) invis = new T.MeshBasicMaterial({ visible: false }); o.userData.glbMat = o.material; o.material = invis; } else o.visible = false; });
      if (spec.done) spec.done(r);
    }).catch(function(){});
  };

  // ---------- oyuncu gemisi (hangar, sinema, hiper atlama: mkShip grubu) ----------
  // game.js mkShip sonunda çağırır: GLB hazırsa kabuk gövdenin yerine geçer; yoksa hiçbir şey olmaz. Boyut: oyundaki gemi boyu (SPECS3D len; GLB L=1).
  G.ship = function(g, id, len){
    var key = 'ship_' + id;
    G.ready.then(function(){ if (!G.index[key]) return; return G.load(key); }).then(function(p){
      if (!p || g.userData.glb || g.userData.gone) return;
      var r = inst(p); r.scale.setScalar(len * p.s); r.userData.glb = true;
      r.rotation.y = window.__glbShipYaw !== undefined ? window.__glbShipYaw : (id === 'kasif' ? 0 : Math.PI);   // AF modeli burun +Z, oyun gövdesi tersi: 180 derece
      r.traverse(function(o){ o.userData.shared = true; });   // game.js hgFree önbellekteki geometri/malzemeyi atmasın
      var th = g.userData.thr, keep = new Set(); if (th){ th.parts.forEach(function(q){ keep.add(q.outer); keep.add(q.inner); keep.add(q.halo); keep.add(q.hot); }); if (th.pl) keep.add(th.pl); }
      var fb = []; g.children.forEach(function(c){ if (keep.has(c)) return; fb.push(c); c.visible = false; });
      g.add(r);
      // motor alevi: kabuk gövdenin nozul konumları yerine modelin ANCH_ENG çapaları (yön: modelde -Z = kuyruk)
      if (th && p.anch.eng.length){
        var Y = new T.Vector3(0, 1, 0), ang = r.rotation.y, d = new T.Vector3(0, 0, -1).applyAxisAngle(Y, ang), rot = Math.atan2(d.z, -d.x) + (window.__glbFlameFlip ? Math.PI : 0);   // alev yerel -X yönüne uzar (kabuk gövdede kuyruk -X)
        th.parts.forEach(function(q, i){
          var a = p.anch.eng[i], os = [q.outer, q.inner, q.halo, q.hot];
          os.forEach(function(o){ o.visible = !!a; }); if (!a) return;
          var v = a.clone().multiplyScalar(len * p.s).applyAxisAngle(Y, ang); q.r = Math.max(0.02, len * 0.045);
          q.outer.position.copy(v); q.inner.position.copy(v); q.halo.position.copy(v); q.hot.position.copy(v);
          q.outer.rotation.y = q.inner.rotation.y = rot;
        });
        if (th.pl && p.anch.eng[0]) th.pl.position.copy(p.anch.eng[0].clone().multiplyScalar(len * p.s).applyAxisAngle(Y, ang)).addScaledVector(d, len * 0.1);
      } g.userData.glb = { r: r, fb: fb, p: p, lod0: byName(r, 'LOD0') || r, lod1: byName(r, 'LOD1') };
      if (g.userData.glb.lod1 && g.userData.glb.lod1 !== g.userData.glb.lod0) g.userData.glb.lod1.visible = false;
      G.stats.gemi = (G.stats.gemi || 0) + 1;
    }).catch(function(){});
  };

  // ---------- istasyon ----------
  var stations = [];
  G.station = function(st, key, w, prev){
    G.ready.then(function(){ if (!G.index['st_' + key]) return; return G.load('st_' + key); }).then(function(p){
      if (!p || !st.group || st._glb) return;
      var r = inst(p); r.scale.setScalar(w * p.s); st.group.add(r);
      st._glb = { r: r, prev: prev, lod0: byName(r, 'LOD0') || r, lod1: byName(r, 'LOD1'), mode: -1 };
      stations.push(st); G.stats.istasyon++; setSt(st, 0, true);
    }).catch(function(){});
  };
  function setSt(st, mode, force){
    var g = st._glb; if (!g || (g.mode === mode && !force)) return; g.mode = mode; G.stats.lodDegisim++;
    if (g.lod1 && g.lod1 !== g.lod0){ g.lod0.visible = mode === 0; g.lod1.visible = mode === 1; } else g.lod0.visible = mode <= 1;
    g.r.visible = mode <= 1; if (g.prev) g.prev.visible = mode === 2;
  }

  // ---------- kare başına iş (game.js EXTRA'dan): LOD seçimi ve asteroit matrisleri ----------
  var acc = 0, tmpP = new T.Vector3(), tmpV = new T.Vector3(), tmpQ = new T.Quaternion(), tmpE = new T.Euler(), tmpM = new T.Matrix4(), tmpS = new T.Vector3(), tmpC = new T.Color();
  G.frame = function(dt, camera){
    if (G.kapali || !camera) return;
    var q = window.__qLevel, low = q === 0;   // "Performans" kalitesinde mesafeler kısalır
    var cp = camera.getWorldPosition(tmpP);   /* kamera oyuncu gemisinin çocuğu olabilir: dünya konumu */
    // NPC ve istasyon LOD'u: 0,1 sn'de bir
    acc += dt;
    if (acc > 0.1){
      acc = 0;
      for (var i = npcs.length - 1; i >= 0; i--){
        var n = npcs[i]; if (!n.g.parent){ npcs.splice(i, 1); continue; }
        var d = n.g.position.distanceTo(cp) / n._glb.L, m = n._glb.mode, k = low ? 0.5 : 1;
        var t0 = 12 * k * (m === 0 ? 1.1 : 0.9), t1 = 40 * k * (m === 2 ? 0.9 : 1.1);
        setMode(n, d < t0 ? 0 : (d < t1 ? 1 : 2));
      }
      for (var j = 0; j < stations.length; j++){
        var st = stations[j], dd = st.group.getWorldPosition(tmpV).distanceTo(cp), mm = st._glb.mode;
        setSt(st, dd < (mm === 0 ? 3300 : 3000) ? 0 : (dd < (mm === 2 ? 9000 : 10000) ? 1 : 2));
      }
    }
    // asteroit: her karede örnek matrisleri (230 kaya, ucuz)
    if (rocks.length || G.stats.kayaOrnek){   /* kayalar bitince örnek sayıları da sıfırlanır (hayalet örnek kalmasın) */
      var range = low ? 600 : 1200, key;
      for (key in ims){ ims[key].n = 0; }
      for (var r = rocks.length - 1; r >= 0; r--){
        var o = rocks[r].o;
        if (!o.parent){ rocks.splice(r, 1); continue; }
        if (!rockProto[rocks[r].type]){ o.visible = true; continue; }
        var dist = o.position.distanceTo(cp), e = dist < range ? imFor(rocks[r].type, rocks[r].vi, o.parent) : null;
        if (!e || e.n >= CAP){ o.visible = true; continue; }
        o.visible = false;
        tmpE.copy(o.rotation); tmpQ.setFromEuler(tmpE);
        var sc = rocks[r].r * ROCK_K / e.rad; tmpS.set(sc, sc, sc);
        tmpM.compose(o.position, tmpQ, tmpS); e.m.setMatrixAt(e.n, tmpM);
        if (o.material && o.material.color){ tmpC.copy(o.material.color); e.m.setColorAt(e.n, tmpC); }
        e.n++;
      }
      var tot = 0;
      for (key in ims){ var x = ims[key]; x.m.count = x.n; x.m.instanceMatrix.needsUpdate = true; if (x.m.instanceColor) x.m.instanceColor.needsUpdate = true; tot += x.n; }
      G.stats.kayaOrnek = tot;
    }
  };

  // test/tanı için kısa durum
  G.kayaMalzemeleri = function(){ return Object.keys(ims).map(function(k){ return ims[k].m.material; }); };   // yalnız test için
  G.durum = function(){
    var modes = [0, 0, 0]; npcs.forEach(function(n){ if (n._glb) modes[n._glb.mode] = (modes[n._glb.mode] || 0) + 1; });
    return { npcGlb: npcs.length, lod: modes, kayaOrnek: G.stats.kayaOrnek, kayaKumeleri: G.stats.kayaKumeleri, yuklenen: G.stats.yuklenen, basarisiz: G.stats.basarisiz, istasyon: stations.length, model: Object.keys(G.index) };
  };
})();
