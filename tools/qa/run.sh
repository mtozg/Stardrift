#!/usr/bin/env bash
# Stardrift oyun içi regresyon seti. Repo kökünden: bash tools/qa/run.sh [test_adı ...]
# Gereksinim: Playwright (node), python3. Oyunu kendisi sunar (python3 -m http.server 8771); test kaydı ':test' anahtarıyla çalışır.
# Tam set ~15 dk (swiftshader). Kokpit/bellek testi ayrı: node tools/qa/qa_pr28.js <çıktı_klasörü> <port>
cd "$(dirname "$0")/../.." || exit 1
TESTLER=${@:-"kargo_kaydi kacak_uste toplu_regresyon devriye_akis devriye_rusvet telefon_devriye hangar_bellek bekci kutuk unvan_hata"}
python3 -m http.server 8771 >/dev/null 2>&1 & SRV=$!; trap 'kill $SRV 2>/dev/null' EXIT; sleep 1
OUT=${OUT:-/tmp/stardrift_qa}; mkdir -p "$OUT"; FAIL=0
for t in $TESTLER; do
  echo "== $t"; timeout 600 node tools/qa/$t.js "$OUT" > "$OUT/$t.log" 2>&1
  python3 tools/qa/dogrula.py "$t" < "$OUT/$t.log" || FAIL=1
done
exit $FAIL
