#!/usr/bin/env bash
# Stardrift oyun içi regresyon seti. Repo kökünden: bash tools/qa/run.sh [test_adı ...]
# Gereksinim: Playwright (node), python3. Oyunu kendisi sunar (python3 -m http.server 8771); test kaydı ':test' anahtarıyla çalışır.
# Tam set ~15 dk (swiftshader). Kokpit/bellek testi ayrı: node tools/qa/qa_pr28.js <çıktı_klasörü> <port>
cd "$(dirname "$0")/../.." || exit 1
TESTLER=${@:-"kargo_kaydi kacak_uste toplu_regresyon devriye_akis devriye_rusvet telefon_devriye hangar_bellek bekci kutuk unvan_hata hangar_geri ozel_ekonomi bildirim pano_yeni derin_sinyal olum_siniri derin_kural olum_hesap bulten acilis_koruma tani glb_yukleyici olum_yenile kokpit_dongu sifirla hesap_kayit zincir_telsiz korsan_karargah menu_yetenek guvenli_mod ipad_kokpit ipad_hiz"}
python3 tools/offline_kontrol.py || echo 'UYARI: çevrimdışı liste denetimi sorun buldu (testleri etkilemez)'
python3 -m http.server 8771 >/dev/null 2>&1 & SRV=$!; trap 'kill $SRV 2>/dev/null' EXIT; sleep 1
OUT=${OUT:-/tmp/stardrift_qa}; mkdir -p "$OUT"; FAIL=0
for t in $TESTLER; do
  echo "== $t"; timeout 600 node tools/qa/$t.js "$OUT" > "$OUT/$t.log" 2>&1
  python3 tools/qa/dogrula.py "$t" < "$OUT/$t.log" || FAIL=1
done
exit $FAIL
