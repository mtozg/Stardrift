# Sabah kontrol listesi (aşama aşama)

Her aşama ayrı bir commit (ya da ayrı PR). Beğenmediğin aşamayı söylemen yeter; yalnız o aşamanın commit'ini geri alırım (`git revert <sha>`), diğerleri kalır. Ekran görüntüleri `docs/sabah/` altında.
Ekonomi (rütbe, XP, kredi, fiyat) bu aşamaların hiçbirinde değişmez. Ekonomi etkisi olan bir şey çıkarsa buraya "ONAY GEREKİR" diye yazarım ve yapmam.

| Aşama | İş | Durum | Commit / PR | Geri alma |
|---|---|---|---|---|
| 1 | Şahin r014 ve Yük Devi r015 3B kokpitleri oyunda | Hazır, PR #42 senin onayını bekliyor | 9d92f6f / PR #42 | `git revert 9d92f6f` |
| 2 | Hayalet 3B kokpit (Asset Factory production → oyuna `CK3.hayalet`) | Asset Factory çalışıyor | - | - |
| 3 | Başarım rozet çizimleri (10 rozet × 3 kademe) ve oyuna bağlama | Sırada | - | - |

## Nasıl bakarsın
- Aşama 1: Hangarda Şahin ve Yük Devi'yi seç, kokpite gir.
- Aşama 2 ve 3: Hazır olunca bu tabloya işlenecek.
