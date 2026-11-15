# test_box r002 — entegrasyon notu

> **GEÇİCİ.** Oyunun koordinat, ölçek, ışık ve yükleyici sözleşmesi (`contracts/game_contract.md`) henüz gelmedi.
> Bu belge kod içermez; oyuna hiçbir şey eklenmedi.
> **Test nesnesi: oyuna entegre edilmeyecek.**

- **Dosya:** `sd_test_box_r002.glb` (tek dosya; dokular gömülü, `EXT_texture_webp` gerekli — three r128 GLTFLoader destekler; oyunda GLTFLoader şu an main dalında yok).
- **Yön/ölçek (geçici):** metre, +Y yukarı, burun −Z. Kök düğüm `SD_test_box`; `userData` = kök extras.
- **LOD:** `LOD0/LOD1/LOD2` kardeş düğümler; hepsi dosyada. Oyun LOD kullanmıyorsa yalnızca `LOD0` görünür bırakılmalı.
- **Malzemeler:** `MAT_body` (base + ORM + normal + emissive harita), `MAT_emit` (canlı emisyon, düz renk ≤ 1 — parlaklık bloom ile).
- **Soketler:** `SOCK_*` boş düğümler; yön düğümün −Z ekseni. extras: amaç, renk vb.
- **Normal haritası:** tangent dosyada yok; three çalışma anında üretir (validator uyarısı). Görsel fark QC'de ölçüldü (ΔE).
- **Gölge:** gerçek zamanlı gölge varsayılmadı; temas gölgesi AO haritasında.
- **Fallback (öneri):** GLB yüklenemezse mevcut model kalır.
- **Test:** `qc/viewer/check.html` (otomatik) ve `qc/viewer/bench.html?glb=…` (gerçek cihaz).
