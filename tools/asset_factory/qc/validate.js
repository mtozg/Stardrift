// Khronos glTF Validator (npm gltf-validator). Kullanım: node qc/validate.js <glb> <çıktı.json>
const v = require('gltf-validator'); const fs = require('fs');
const [glb, out] = process.argv.slice(2);
v.validateBytes(new Uint8Array(fs.readFileSync(glb)), { maxIssues: 200 }).then(r => {
  fs.writeFileSync(out, JSON.stringify(r, null, 1));
  console.log('RESULT', JSON.stringify({ validator: r.validatorVersion, errors: r.issues.numErrors, warnings: r.issues.numWarnings, infos: r.issues.numInfos, hints: r.issues.numHints }));
}).catch(e => { console.error(e); process.exit(1); });
