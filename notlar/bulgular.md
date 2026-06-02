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

## Senaryo karşılaştırma bulguları

Senaryo kütüphanesinin (6 başarılı senaryo) asıl bilimsel değeri: ilaç/hastalık
pertürbasyonlarının nefron boyunca etkisini normal ile yan yana okumak. Her bulgu önce
fizyolojiden beklenir, sonra veride test edilir. **Kural: konsantrasyon yanıltır, kütle
(akı = konsantrasyon × hacim) ve hacim ayrı ayrı bakılmalı.**

### 0. KRİTİK: Senaryo veri bütünlüğü — "6 başarılı" aslında 4 temiz + 2 yarı-bozuk (2026-06-02)

SGLT2 analizine başlarken veride şüpheli değerler (negatif idrar glukozu, negatif osmolalite)
çıktı → sistematik tarama yapıldı (`kod/veri_kontrol.py`, yeniden kullanılabilir denetçi).

**Yakınsama göstergeleri:** NaN değer + negatif Lumen osmolalitesi (osm = solüt toplamı,
fiziksel olarak negatif olamaz). Sonuç:

| Senaryo | NaN | Neg osm | Verdict |
|---|---|---|---|
| F_normal | 0 | 0 | **TEMİZ** |
| F_SGLT2 | 0 | 0 | **TEMİZ** |
| M_SGLT2 | 0 | 0 | **TEMİZ** |
| F_HT | 0 | 0 | **TEMİZ** |
| **M_normal** | 4047 | 0 | ✗ Toplayıcı kanal (IMCD merged) NaN — distal güvenilmez |
| **F_diab_mod** | 796 | 199 | ✗ Toplayıcı kanal çöktü (osm min -13694) — distal geçersiz |

**Sonuç:** "6 başarılı senaryo" aşırı iyimserdi. Tam temiz **4**; M_normal ve F_diab_mod'un
**toplayıcı kanal (IMCD merged) hesabı yakınsamamış.** Her ikisinde de sorun yalnız IMCD'de;
proksimal + Henle + erken distal (PT→DCT) sağlam. Bu, Faz 15'teki Newton instabilitesi
temasının devamı — modelin merged/toplayıcı-kanal çözümü kırılgan.

**Çalışma kuralı:** Distal/idrar (CCD, OMCD, IMCD merged) iddiaları **yalnız TEMİZ
senaryolardan**. M_normal ve F_diab_mod yalnız proksimal-orta segmentler için kullanılır.
Yeni her senaryoda `python3 kod/veri_kontrol.py` çalıştırılır.

**Yan artefakt (zararsız):** IMCD merged'de Cell-kompartman hacmi tüm senaryolarda büyük
negatif (-79024) çıkar; Lumen (idrar yolu) hacmi sağlam. IMCD Cell hacmini kullanma.

**App davranışı (cerrahi gizleme, Faz 22):** Streamlit'te 6 senaryo da kalır ama bozuk
(senaryo, segment) kombinasyonu **tümüyle gizlenir** — kesik/yanıltıcı eğri bırakılmaz.
Mekanizma `ui_kit.py`: `butunluk_haritasi()` (NaN + negatif Lumen osm → bozuk segment
haritası), `segment_bozuk_mu()` (segment-düzeyi gizleme), `gecerli_veri()` (satır-düzeyi
NaN/negatif emniyet ağı). Sidebar'da senaryo seçilince uyarı banner'ı çıkar. Sayfa 1/2/4
guard'lı. Karar gerekçesi: M_normal ve F_diab_mod'un proksimal verisi GEÇERLİ ve değerli
(erkek temeli + diyabet hiperfiltrasyonu); tümüyle silmek iyi veriyi de gizlemek olurdu.

### 1. SGLT2 inhibisyonu (gliflozinler) — F_SGLT2 vs F_normal (2026-06-02)

**Veri bütünlüğü:** Her iki senaryo da TEMİZ (idrar dahil güvenilir).

**Fizyolojik beklenti:** SGLT2 erken proksimal tübülde (S1-S2) filtre edilen glukozun
~%90'ını Na ile birlikte (kotransport) geri emer. İnhibe edilince → glukozüri, Na'nın
PT'de daha az emilimi → distale daha fazla Na → ozmotik diürez. Distal Na yükü artışı
tübüloglomerüler geri bildirimi (TGF) tetikleyip GFR'yi düşürür (nefroproteksiyon mekanizması).

**Veride test (sup nefron, lümen):**

| Ölçüm | F_normal | F_SGLT2 | Yorum |
|---|---|---|---|
| SGLT2 akısı (ort) | 61.4 | 18.0 | İnhibisyon çalışıyor (~%70 ↓) |
| **SGLT1 akısı (ort)** | 10.1 | **480** | **Telafi:** glukoz geç PT/S3'e kaçınca SGLT1 tavan yapar (~48×) |
| GLUT2 (bazolateral) | 30.7 | 9.2 | Daha az transselüler glukoz → daha az bazolateral çıkış |
| PT giriş glukoz (mM) | 5.00 | 5.00 | Filtrat aynı |
| PT çıkış glukoz (mM) | 0.07 | 8.52 | Normalde %99 emilir; SGLT2'de su çekildikçe **konsantre olur** |
| **İdrar glukozu (mM)** | 0.32 | **99.6** | **Masif glukozüri — gliflozinin terapötik imzası** |
| PT çıkış Na (mM, konsantrasyon) | 137.5 | 132.7 | TUZAK: düşük görünür çünkü glukoz su tutar (seyreltir) |
| **S3 çıkış Na AKISI (pmol/min, kütle)** | 4553 | **4870** | **Gerçek natriürez: +%7 kütle distale** |
| S3 çıkış su akısı (nl/min) | 27.6 | 30.6 | Ozmotik diürez (+%11) |
| **İdrar akışı (nl/min)** | 0.86 | **1.51** | **Diürez +%76** |

**Bilimsel sonuç:** Model SGLT2 inhibisyonunun tüm klasik zincirini doğru üretiyor:
(1) glukoz emilimi bloke → (2) SGLT1 telafisi (tam yakalayamaz) → glukozüri →
(3) glukozun ozmotik su tutması → diürez → (4) SGLT2-Na kotransport kaybı → distale
artmış Na kütlesi (natriürez). Bu, EMPA-KIDNEY/DAPA-CKD/CREDENCE çalışmalarındaki
nefroproteksiyonun tübüler temeli.

**Konsantrasyon-kütle dersi (yine!):** PT çıkış Na *konsantrasyonu* SGLT2'de DÜŞÜK
(132.7 < 137.5) — saf sezgi "Na lümende kalmalı, yükselmeli" der ve yanılır. Çünkü glukozun
ozmotik tuttuğu su Na'yı seyreltir. *Akı* (kütle) bakınca natriürez netçe görünür (+%7).

**Model sınırı (dürüstlük):** Bu tek-nefron model GFR'yi sabit sınır koşulu olarak alır;
TGF→afferent vazokonstriksiyon→GFR düşüşü adımını **modellemez**. Veri tübüler sonuçları
(glukoz/Na/su delivery) gösterir; GFR geri bildirimi fizyolojik yorumdur, veri bulgusu değil.

### 2. Diyabet (orta) — F_diab_mod vs F_normal — YALNIZ PROKSİMAL (2026-06-02)

**Veri bütünlüğü uyarısı:** F_diab_mod'un toplayıcı kanalı (IMCD) çökmüş (bkz. #0).
Yalnız proksimal–orta segment bulguları geçerli; idrar/distal iddiaları **kullanılamaz.**

**Fizyolojik beklenti:** Diyabette hiperglisemi → artmış filtre glukoz yükü; böbrek SGLT2/SGLT1
aktivitesini upregüle eder (glukoz emilimini artırır). Erken diyabette tipik bulgu
**glomerüler hiperfiltrasyon** (artmış SNGFR).

**Veride test (geçerli, proksimal):**

| Ölçüm | F_normal | F_diab_mod | Yorum |
|---|---|---|---|
| **PT giriş su akısı (nl/min)** | 100 | **117** | **Hiperfiltrasyon +%17** (model SNGFR'yi sınır koşulu olarak yükseltir) |
| PT giriş Na akısı (pmol/min) | 14000 | 16380 | Orantılı (+%17) artmış filtre Na yükü |
| PT giriş glukoz (mM) | 5.0 | 8.6 | Hiperglisemi (artmış filtrat) |
| PT çıkış glukoz (mM) | 0.070 | 0.027 | Diyabetik PT glukozu daha tam emer (upregüle SGLT2) |
| SGLT2 akısı (ort, PT+S3) | 61.4 | 102.8 | **SGLT2 upregülasyonu (+%68)** |
| S3 çıkış Na akısı (pmol/min) | 4553 | 5508 | +%21 — hiperfiltrasyondan ileri gelen artmış distal yük |

**Bilimsel sonuç:** Model erken/orta diyabetin iki temel proksimal imzasını doğru üretiyor:
(1) hiperfiltrasyon (giriş akısı +%17), (2) glukoz taşıyıcı upregülasyonu → hiperglisemiye
rağmen glukozüri yok (orta diyabette beklenen; eşik aşılmadıkça SGLT2 kapasitesi yetişir).
Bu, SGLT2 inhibisyonu bulgusunun (#1) **ayna görüntüsü** — diyabet glukoz/Na emilimini
artırır, gliflozin azaltır. Klinik bağ: gliflozinler hiperfiltrasyonu tam bu mekanizmayla
(distal Na ↑ → TGF → afferent kısılma) düzeltir; ama TGF→GFR adımı bu modelde yok (bkz. #1).

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
