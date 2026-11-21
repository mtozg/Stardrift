# hayalet_cockpit r005 = r004 + NEON HİZALAMA düzeltmesi (r004 klasörü korunur)

Mehmet: "neon ışıklar tam oturmamış". Değişen yalnız neon: (1) çapraz direk neonu direğin iç kenarını izleyen şerit, direk ucundan ucuna aynı nokta dizisiyle; (2) üst kemer neonları kemerin eğrisini izleyen şeritler (merkez hattan ofsetli); (3) ekran alt kenarı neonu ön yüz şeridinde köşeden köşeye (radar hariç: koltuk başlığı örtüyordu); (4) havada kalan alt köşe şeritleri ve gizli parçalar kaldırıldı; tavan çentiği ve radar kepi V'si kirişe/kepe oturtuldu. Diğer her şey r004 ile aynı (sade sırt, katmanlı yüzey, %7 küçük ekranlar). Resmi Kapı/registry kaydı YOK.

Neon kontrolü (qc/neon_check.py): her neon yüzeyi için gözden ışın; gizli/havada (arkada yüzey >12 mm) parça sayısı = 0 (12 parça). Ekran örtme (qc/screen_occlusion.py) = 0.

| Dosya | Boyut | SHA256 |
|---|---|---|
| sd_hayalet_cockpit_r005.glb | 1348388 B | 08d5e10bc51af67406a0449566fcb0c86e64a45cbf3c318e7aaec482841a1e91 |
| sd_hayalet_cockpit_r005_m.glb (telefon) | 1154644 B | 4c3e8731857f820c03dc2bf0a3067ebf4366caef3c4735d7e64df431cac9b2e9 |

CK3: ck3_hayalet.json (top 358; q r004 ile AYNI: [[[310, 393], [580, 378], [580, 510], [301, 545]], [[633, 371], [967, 371], [980, 501], [620, 501]], [[1020, 378], [1290, 393], [1299, 545], [1020, 510]]]; ridge simetrik).
Teknik: 14.622 üçgen, 5 draw call, GPU 32 MB, HUD %7,3, hiza 0,03–0,05 px, RADAR 2,65, verify 12/12.
