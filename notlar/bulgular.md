# Bulgular ve Kararlar

## Model kimliği
- **Kaynak:** Layton Lab — `github.com/mstadt/nephron` (Python 3)
- **Atıf:** Hu et al. 2021 (insan, cinsiyete özgü çoklu nefron); Layton & Layton 2019 (insan).
- **Ne yapar:** Nefron boyunca **dilim dilim çözülen korunum denklemleri** (Newton/Broyden).
  Her segment, bir öncekinin çıkışını (outlet) giriş sınır koşulu olarak alır.

## Veri kapsamı (bu sürüm)
- Kadın, insan, "normal" durum, çoklu nefron: **sup + jux1–jux5 + merged (toplayıcı kanal)**
- Segmentler: PT, S3, SDL, (LDL, LAL: sadece jux), mTAL, cTAL, DCT, CNT, CCD, OMCD, IMCD
- Tidy tablo: **1.033.065 satır**, 14 değişken kategorisi, 0 parse hatası
- Grid (dilim) sayısı segmente göre değişir: PT=181, S3=20, gerisi=200 → pozisyon **0–1 normalize** edilir

## Fizyolojik doğrulamalar (✓ = veri beklentiyle uyuştu)
- ✓ **Glomerül filtratı ≈ 298 mOsm** (≈ plazma) — izotonik filtrat
- ✓ **PT izoozmotik:** giriş ~298 → çıkış ~300 (Na+su birlikte emilir, konsantrasyon sabit)
- ✓ **mTAL dilüsyon segmenti:** lümen Na 261.6 → 102.3 mM (NKCC2 tuz çeker, su gelemez)
- ✓ **NKCC2 stokiyometrisi:** Na akısı 17.3, Cl akısı 34.7 ≈ **1 Na : 2 Cl** (ders kitabı)
- ✓ **Segment zincirleme:** her segmentin çıkışı = sonrakinin girişi (veride görünür)

## Ana bilimsel bulgu: gradyan var ama eksik
| Konum (interstisyum) | mOsm |
|---|---|
| Korteks (CCD) | ~300 |
| Dış medulla (OMCD) | ~688 |
| İç medulla (IMCD tepe) | **~734** |
| Final idrar (IMCD lümen) | 619 |
| Henle kulpu dibi (jux5) | 730 |

- **Beklenen (literatür):** insan papilla tepesinde **~1200 mOsm** (korteks ~290 → iç medulla ~1200).
- **Modelin tavanı:** ~730 mOsm → **~470 mOsm açık.**

### Açığın sebebi (önemli)
- **Düşük ADH DEĞİL.** Kanıt: idrar 619 > plazma 300 → idrar konsantre ediliyor → ADH **etkin**.
  (Model zaten ADH'yi parametre olarak almıyor; su geçirgenliği datafile'da sabit: Pf_female=0.33 cm/s.)
- **Gerçek sebep:** **Renal Medüller İnterstisyel Hipertonisite (MİH)** matematiksel modellerce
  tam üretilemiyor. İç medulla konsantrasyon mekanizması fizyolojinin **çözülememiş açık problemi.**
- MİH'i oluşturan/sürdüren mekanizmalar (ders bağlamı):
  1. **Karşıt akım çoğaltıcı** (Henle kulpu)
  2. **Üre geri dönüşüm mekanizması** (IMCD ↔ interstisyum)
  3. **Vasa recta** (karşıt akım değiştirici — MİH'in sürdürülebilirliği)
- Bu model bu mekanizmaları içerse de iç medulla tepe değerini ~700–800'de bırakıyor.
  → En gelişmiş model bile MİH'i tam hesaplayamıyor. Bu, projenin özgün katkı alanı olabilir.

## LDL doğrulaması (jux5) — üre geri dönüşümü çalışıyor

Kullanıcı "LDL yalnız su geçirgen, NH3 neden düşüyor?" diye sordu. İnceleme:

**LDLparams_F_hum.dat geçirgenlikleri:**
- Na, Cl, K, NH4: 0 (yüklü iyonlar transselüler kapalı)
- Urea: 80, NH3: 85, CO2: 1200 (uncharged/gas → yüksek)
- Su: Pf_Lumen_LIS_female=440 (paraselüler yüksek)

**LDL jux5 Lumen verisi (giriş→çıkış):**
| Solüt | Giriş | Çıkış | Oran | Yorum |
|---|---|---|---|---|
| Urea | 38.4 | 196.0 | ×5.1 | **Üre geri dönüşümü** — interstisyumdan lümene |
| NH3 | 0.142 | 0.120 | ×0.84 | Gaz → interstisyumla dengeleniyor |
| NH4 | 8.3 | 8.4 | ×1.02 | Yüklü, kapalı → sabit |
| Na/Cl | ~290 | ~240 | ×0.81 | Paraselüler çıkış |
| Su hacmi | 16.92 | 18.44 | ×1.09 | Ürea+su birlikte içeri |

**Bilimsel sonuç:** Model, MİH'in iki temel mekanizmasından biri olan **üre geri dönüşümünü**
doğru implemente ediyor. NH3 lümen-interstisyum denge dağıtımıyla (gaz difüzyonu) hareket
ediyor. "İnen kol = sadece su geçirgen" SDL için doğru, LDL (iç medulla) için modern
anlayışta yanlış — model modern anlayışı yansıtıyor.

### Ek: Na konsantrasyonu düşüşünün matematik kapanışı (jux5)

Kullanıcı sezgisi: "LDL Na geçirgen değil, su azalır → Na yükselir." İki varsayım da yanlış.

**Varsayım A — Su azalır:** YANLIŞ. Veri (water_volume Lumen): jux1: 16.92→17.35 (+%2.5),
jux5: 16.92→18.44 (+%9.0). Su lümene GİRER (urea+su tuzağı).

**Varsayım B — Na kütlesi sabit:** Kısmen yanlış. `perm_Na_Lumen_Cell=0` (transselüler doğru),
ama paraselüler Na akısı (model çıktısı `paracellular_Na`): LDL jux5 ortalama 0.127 pmol/min,
max 0.564. Konvektif sürüklenme (solvent-drag) ile Na lümenden çıkar.

Na kütlesi (konsantrasyon × hacim): jux1: 5110→5040 (×0.99, sabit), jux5: 5110→4484 (×0.88).

**Matematik kapanış (jux5):**
```
cikis_Na = cikis_kutle / cikis_hacim = 4484 / 18.44 = 243.2 mM  ✓ veride birebir
302 → 243 düşüş: kütle ×0.88, hacim ×1.09 → konsantrasyon ×0.805 (≈ %19.5 azalış)
```

Klasik DTL teorisi (sadece su geçirgen, solüt korunur) SDL için geçerli; LDL (iç medulla)
modern anlayışta urea-su tuzağı + paraselüler konvektif Na kaçağı + transcelüler kapalı.

## Çok-membranlı flux ayrıştırması (Görev #4 — ÇÖZÜLDÜ, 2026-06-02)

Kullanıcı sorusu zinciri değil, kod borcuydu: CNT/CCD/OMCD'de AE1, HATPase, HKATPase,
NHE1 gibi taşıyıcılar bir segmentte **birden çok hücre membranında** bulunur. Model
(output.py) bunların akısını **tek dosyaya, dosya adında membran kimliği OLMADAN,
append modunda** yazar. Sonuç: N×grid satırlık dosyalar (grid=200 → 400 veya 600 satır).

**Kritik keşif — veri bloklu değil, interleaved:** Yazım döngüsü dıştan pozisyon (`for j`),
içten membran. Yani değerler `[poz0_m0, poz0_m1, poz0_m2, poz1_m0, ...]` sırasında. Önceki
loader tek profil sayıp `position=linspace(0,1,n)` veriyordu → **pozisyon ekseni anlamsızdı.**

Ampirik doğrulama (CCD HKATPase K, 600 satır): stride-3 ayrıştırması pürüzsüzlük 0.0001
(kusursuz profil), bloklu varsayım 1.15 (gürültü). → Ayrıştırma: `membran m = values[m::k]`.

**Membran sırası modelin parametre dosyalarından** (`datafiles/<SEG>params_*_hum.dat`,
`transport_` satır sırası, sex-filtreli) çıkarıldı, dosya uzunluklarıyla doğrulandı.
Etiket = kompartman çifti (`build_database.py` → `MEMBRANE_ORDER`):

| Segment·Taşıyıcı | Membran sırası | Anlam |
|---|---|---|
| CNT/CCD HATPase | Lumen-ICA, ICB-LIS, ICB-Bath | A-tipi apikal + B-tipi bazolateral |
| CNT/CCD HKATPase | Lumen-Cell, Lumen-ICA, Lumen-ICB | principal + A/B-tipi apikal |
| CNT/CCD AE1 | ICA-LIS, ICA-Bath | A-tipi bazolateral (Cl/HCO3) |
| OMCD HKATPase | Lumen-Cell, Lumen-ICA | principal + A-tipi apikal |
| OMCD AE1 | ICA-LIS, ICA-Bath | A-tipi bazolateral |
| OMCD NHE1 | Cell-LIS, Cell-Bath | principal bazolateral |

**Fizyolojik doğrulama:** CCD HKATPase K → Lumen-Cell=0, Lumen-ICA=1.31, Lumen-ICB=0
(H/K-ATPaz yalnız A-tipi ara hücre apikalinde aktif ✓). CCD HATPase H → Lumen-ICA negatif
(A-tipi apikalden asit sekresyonu), ICB-LIS/Bath pozitif (B-tipi bazolateralden ters
polarite ✓). Model intercalated hücre kutuplaşmasını doğru veriyor.

**Sonuç:** Tidy tabloya `membrane` kolonu eklendi (tek-membranlı satırlar NULL). 6 senaryoda
246 dosya ayrıştırıldı, toplam satır değişmedi (6.198.390 — değerler yeniden dağıtıldı).
Eski apikal/paracellular Na flux'ları tek-membran olduğundan etkilenmedi; NKCC2A stokiyometri
doğrulaması (Cl/Na=2.00) korundu.

**Açık alt-konu (küçük):** NaKATPase/KCC4/SGLT1/GLUT gibi taşıyıcılar memb_id'yi dosya
ADINDA taşıdığından zaten ayrı dosyalara yazılıyor (interleaved değil) — ama loader memb_id'yi
şu an `membrane` kolonuna geçirmiyor (NULL kalıyor), aynı (taşıyıcı,solüt) anahtarında birden
çok membran dosyası birleşebilir. Düşük öncelik; gerekirse ileride compart_id reverse-map ile.

## Açık teknik konular
1. ✓ **Çok-membranlı flux dosyaları** — ÇÖZÜLDÜ (yukarı bakınız, 2026-06-02).
2. **Doğrulama:** ~734 tepe değeri Hu et al. 2021 makalesinin bildirdiği değerle uyuşuyor mu?
3. **Belirsiz birimler:** pressure / diameter / length birimleri kaynaktan teyit edilmeli (şu an 'unknown').
