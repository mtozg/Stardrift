// Asset Factory görüntüleyici — Three r128 (oyunun /vendor/three.min.js dosyası, salt okunur) + sabitlenmiş GLTFLoader r128.
// check.html (otomatik QC, Playwright) ve bench.html (gerçek cihaz) aynı kodu kullanır.
// Işık: Blender "neutral" düzeninin birebir karşılığı — ortam = float düz equirect (radyans C),
// DirectionalLight yoğunluğu = güneş gücü / π (r128, physicallyCorrectLights=false). Deneyle doğrulandı.
'use strict';
const SDV = {};

SDV.renderer = function (w, h, canvas) {
  const r = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true, canvas });
  r.setPixelRatio(1); r.setSize(w, h, false);
  r.outputEncoding = THREE.sRGBEncoding; r.toneMapping = THREE.NoToneMapping; r.physicallyCorrectLights = false;
  r.setClearColor(0x000000, 0);
  return r;
};

SDV.neutralScene = function (r, N) {
  const S = new THREE.Scene();
  const d = new Float32Array(16 * 8 * 4);
  for (let i = 0; i < d.length; i += 4) { d[i] = N.ambient[0]; d[i + 1] = N.ambient[1]; d[i + 2] = N.ambient[2]; d[i + 3] = 1; }
  const t = new THREE.DataTexture(d, 16, 8, THREE.RGBAFormat, THREE.FloatType); t.mapping = THREE.EquirectangularReflectionMapping; t.needsUpdate = true;
  const pm = new THREE.PMREMGenerator(r); S.environment = pm.fromEquirectangular(t).texture; pm.dispose();
  const L = new THREE.DirectionalLight(new THREE.Color(...N.sun_color), N.sun_strength / Math.PI);
  const sd = new THREE.Vector3(...N.sun_dir_game).normalize(); L.position.copy(sd.clone().multiplyScalar(-10)); L.target.position.set(0, 0, 0);
  S.add(L); S.add(L.target);
  return S;
};

SDV.load = function (url) {
  return new Promise((res, rej) => { const t0 = performance.now(); new THREE.GLTFLoader().load(url, g => res({ gltf: g, ms: performance.now() - t0 }), undefined, rej); });
};

SDV.lod = function (root, i) { root.traverse(o => { if (/^LOD\d$/.test(o.name)) o.visible = (o.name === 'LOD' + i); }); };

SDV.camera = function (c) {
  const cam = new THREE.PerspectiveCamera(c.fovy, c.width / c.height, 0.01, 1000);
  cam.position.set(...c.position); cam.up.set(...c.up); cam.lookAt(new THREE.Vector3(...c.target));
  if (c.shift_y) cam.setViewOffset(c.width, c.height, 0, -c.shift_y * c.height, c.width, c.height);   // pilot kamerası asal noktası
  cam.updateMatrixWorld();
  return cam;
};

SDV.inspect = function (gltf) {
  const root = gltf.scene.children.find(o => o.name.startsWith('SD_')) || gltf.scene.children[0];
  const out = { root: root ? root.name : null, extras: root ? root.userData : null, nodes: [], meshes: [], materials: {}, sockets: [] };
  gltf.scene.traverse(o => {
    out.nodes.push(o.name);
    if (o.name.startsWith('SOCK_')) out.sockets.push({ name: o.name, position: o.getWorldPosition(new THREE.Vector3()).toArray().map(v => +v.toFixed(4)), dir: new THREE.Vector3(0, 0, -1).applyQuaternion(o.getWorldQuaternion(new THREE.Quaternion())).toArray().map(v => +v.toFixed(4)), extras: o.userData });
    if (o.isMesh) {
      out.meshes.push({ name: o.name, tris: o.geometry.index ? o.geometry.index.count / 3 : o.geometry.attributes.position.count / 3, attrs: Object.keys(o.geometry.attributes) });
      const m = o.material, tx = k => m[k] && m[k].image ? [m[k].image.width, m[k].image.height] : null;
      out.materials[m.name] = { type: m.type, side: m.side, map: tx('map'), normalMap: tx('normalMap'), roughnessMap: tx('roughnessMap'), metalnessMap: tx('metalnessMap'), aoMap: tx('aoMap'), emissiveMap: tx('emissiveMap'), emissive: m.emissive ? m.emissive.toArray() : null, metalness: m.metalness, roughness: m.roughness, transparent: m.transparent };
    }
  });
  return out;
};

SDV.texBytes = function (root) {   // GPU doku belleği tahmini: RGBA8 + mipmap (×4/3)
  const seen = new Set(); let b = 0;
  root.traverse(o => { if (!o.isMesh) return; const m = o.material; ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap', 'emissiveMap'].forEach(k => { const t = m[k]; if (t && t.image && !seen.has(t.image)) { seen.add(t.image); b += t.image.width * t.image.height * 4 * 4 / 3; } }); });
  return Math.round(b);
};

SDV.alphaMask = function (r, w, h) {
  const gl = r.getContext(), px = new Uint8Array(w * h * 4); gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, px);
  const m = new Uint8Array(w * h); for (let i = 0; i < w * h; i++) m[i] = px[i * 4 + 3] > 127 ? 1 : 0; return m;
};

SDV.maskDiff = function (a, b) { let x = 0, u = 0; for (let i = 0; i < a.length; i++) { if (a[i] || b[i]) u++; if (a[i] !== b[i]) x++; } return u ? x / u : 0; };

SDV.perf = async function (r, S, gltf, cam, n, frames) {
  const grp = new THREE.Group(); S.add(grp);
  const R = gltf.scene.userData.radius || 1.2;
  const k = Math.ceil(Math.sqrt(n));
  for (let i = 0; i < n; i++) { const c = gltf.scene.clone(true); SDV.lod(c, 0); c.position.set(((i % k) - (k - 1) / 2) * R * 2.4, 0, -Math.floor(i / k) * R * 2.4); grp.add(c); }
  const gl = r.getContext(), px = new Uint8Array(4);
  for (let i = 0; i < 5; i++) r.render(S, cam);
  gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
  const t = [];
  for (let i = 0; i < frames; i++) { const t0 = performance.now(); r.render(S, cam); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); t.push(performance.now() - t0); }
  r.info.reset(); r.render(S, cam);
  const info = { calls: r.info.render.calls, triangles: r.info.render.triangles };
  S.remove(grp);
  t.sort((a, b) => a - b);
  return { n, frames, ms_avg: +(t.reduce((a, b) => a + b, 0) / t.length).toFixed(2), ms_p50: +t[Math.floor(t.length * 0.5)].toFixed(2), ms_p95: +t[Math.floor(t.length * 0.95)].toFixed(2), ...info };
};

// Otomatik QC: render, sadakat girdileri, LOD silueti, yüz yönü, renderer.info, performans
SDV.check = async function (cfg) {
  const R = { cfg: cfg.name };
  const { gltf, ms } = await SDV.load(cfg.glb); R.load_ms = +ms.toFixed(1);
  R.inspect = SDV.inspect(gltf);
  const root = gltf.scene; SDV.lod(root, 0);
  root.userData.radius = (R.inspect.extras && R.inspect.extras.radius) || 1.2;
  R.renders = {};
  for (const c of (cfg.only_perf ? [] : cfg.cameras)) {
    const cv = document.createElement('canvas'); const r = SDV.renderer(c.width, c.height, cv); const S = SDV.neutralScene(r, cfg.neutral); S.add(root);
    const cam = SDV.camera(c); r.render(S, cam); R.renders[c.name] = cv.toDataURL('image/png');
    if (c === cfg.cameras[0]) {
      r.info.reset(); r.render(S, cam); R.info = { calls: r.info.render.calls, triangles: r.info.render.triangles, textures: r.info.memory.textures, geometries: r.info.memory.geometries };
      // yüz yönü: FrontSide vs DoubleSide
      const A = SDV.alphaMask(r, c.width, c.height); const gl = r.getContext();
      const px = () => { const p = new Uint8Array(c.width * c.height * 4); gl.readPixels(0, 0, c.width, c.height, gl.RGBA, gl.UNSIGNED_BYTE, p); return p; };
      const a = px(); const mats = []; root.traverse(o => { if (o.isMesh) mats.push(o.material); });
      const sides = mats.map(m => m.side); mats.forEach(m => { m.side = THREE.DoubleSide; m.needsUpdate = true; }); r.render(S, cam); const b = px();
      mats.forEach((m, i) => { m.side = sides[i]; m.needsUpdate = true; });
      let diff = 0, tot = 0; const dc = document.createElement('canvas'); dc.width = c.width; dc.height = c.height; const dx = dc.getContext('2d'); const di = dx.createImageData(c.width, c.height);
      for (let i = 0; i < a.length; i += 4) { const y = c.height - 1 - Math.floor(i / 4 / c.width), x = (i / 4) % c.width, j = (y * c.width + x) * 4; di.data[j + 3] = 255; if (a[i + 3] < 8 && b[i + 3] < 8) continue; tot++; di.data[j] = di.data[j + 1] = di.data[j + 2] = 40;
        if (Math.abs(a[i] - b[i]) + Math.abs(a[i + 1] - b[i + 1]) + Math.abs(a[i + 2] - b[i + 2]) + Math.abs(a[i + 3] - b[i + 3]) > 30) { diff++; di.data[j] = 255; di.data[j + 1] = 40; di.data[j + 2] = 40; } }
      dx.putImageData(di, 0, 0); R.renders['normal_side_diff'] = dc.toDataURL('image/png');
      // kenar yumuşatma artığı tek piksellik çizgiler üretir; gerçek delik/ters yüz leke üretir → 3×3 erozyon sonrası say
      const W = c.width, H = c.height, D = new Uint8Array(W * H); for (let i = 0; i < W * H; i++) D[i] = di.data[i * 4] === 255 ? 1 : 0;
      let ero = 0; for (let y = 1; y < H - 1; y++) for (let x = 1; x < W - 1; x++) { const k = y * W + x; if (D[k] && D[k - 1] && D[k + 1] && D[k - W] && D[k + W]) ero++; }
      R.normal_side_diff_raw = tot ? +(diff / tot).toFixed(5) : 0;
      R.normal_side_diff = tot ? +(ero / tot).toFixed(5) : 0;
      // LOD silueti: LODi'nin tasarlandığı uzaklıkta (nesne yüksekliği ~ 96 / 40 px) LOD0 ile maske farkı
      R.lod = [];
      const lw = 256, lh = 256; r.setSize(lw, lh, false);
      const hasLod = i => { let f = false; root.traverse(o => { if (o.name === 'LOD' + i) f = true; }); return f; };
      for (const [i, px_h] of [[1, 96], [2, 40]].filter(x => hasLod(x[0]))) {
        const lc = Object.assign({}, c, { width: lw, height: lh }); const cm = SDV.camera(lc);
        const dir = new THREE.Vector3().subVectors(cm.position, new THREE.Vector3(...c.target)).normalize();
        const dist = root.userData.radius * 2 / (2 * Math.tan(c.fovy * Math.PI / 360)) * (lh / px_h);
        cm.position.copy(new THREE.Vector3(...c.target).add(dir.multiplyScalar(dist))); cm.lookAt(new THREE.Vector3(...c.target)); cm.updateMatrixWorld();
        SDV.lod(root, 0); r.render(S, cm); const m0 = SDV.alphaMask(r, lw, lh);
        SDV.lod(root, i); r.render(S, cm); const m1 = SDV.alphaMask(r, lw, lh);
        R.lod.push({ lod: i, object_px: px_h, silhouette_diff: +SDV.maskDiff(m0, m1).toFixed(4) });
      }
      SDV.lod(root, 0);
    }
    S.remove(root); r.dispose();
  }
  R.tex_gpu_bytes = SDV.texBytes(root);
  if (cfg.perf) {
    const cv = document.createElement('canvas'); const r = SDV.renderer(cfg.perf.width, cfg.perf.height, cv); const S = SDV.neutralScene(r, cfg.neutral);
    const c = cfg.cameras[0]; const cam = new THREE.PerspectiveCamera(50, cfg.perf.width / cfg.perf.height, 0.05, 2000);
    const rad = root.userData.radius; cam.position.set(0, rad * 3, rad * 9); cam.lookAt(0, 0, -rad * 4);
    R.perf = []; for (const n of cfg.perf.counts) R.perf.push(await SDV.perf(r, S, gltf, cam, n, cfg.perf.frames));
    r.dispose();
  }
  R.done = 1; return R;
};
