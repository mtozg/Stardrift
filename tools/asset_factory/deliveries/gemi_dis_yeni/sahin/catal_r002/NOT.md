# Şahin Çatal catal_r002 — İLK ARA SONUÇ (Konsept B, Mehmet onayı 2026-11-27)
- STD (oyun içi varsayılan): base1024/normal1024/ORM512/emissive256 → 12,3 MB GPU. HD (yalnız hangar, opsiyonel): base2048/normal1024/ORM1024/emissive512 → 33,3 MB. İkisi de ≤40 MB.
- 13 397 üçgen (LOD0), 3 039 (LOD1), 1 malzeme, 2 draw call. Khronos validator: 0 hata. ANCH_ENG×2, ANCH_NAV×3, ANCH_MUZ×3.
- Oyun içi kıyas: ingame_simdiki_vs_yeni.png (hangar, izole kopya; oyun dosyası değişmedi).
- Bilinen eksikler: radyatör plakası ayrıntısı, kiriş-kapsül bağlantı kirişleri ince, seramik/titanyum kontrastı; sıradaki turda düzeltilecek.
- Üretim: families/ship/sahin_catal.py + specs/ship/sahin_catal.json + library/materials/cat_*.json; kademe üretimi pipeline/mobile_variant.py <glb> <out> std|hd.
