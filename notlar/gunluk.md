# Proje Günlüğü

Kronolojik kayıt. **Sonradan döndüğünde sıralamayı buradan takip et.**
Her giriş: tarih · ne yapıldı · neden · dosyalardaki etkisi.

> Bu dosya şu üçünden farklıdır:
> - `bulgular.md` → yapısal bilimsel bulgular ve kararlar
> - `terminoloji.md` → sözlük (statik)
> - `gunluk.md` → **bu dosya** = zaman serisi, ne zaman ne oldu

---

## 2026-05-24 · Faz 0: Strateji ve mimari kararı

**Soru:** Pyramis ürineri tam fizyolojik+matematik modelleyen bir sistem var mı?
**Bulgu:** Var ama tam değil. İç medulla konsantrasyon mekanizması (MİH) hâlâ açık problem.
Boşluk modelin kendisinde değil, **erişilebilir + atıf yapılabilir araçta.**
**Karar:** Sıfırdan matematik yazmayacağız → **var olan en iyi modeli (Layton/Hu) kullanılabilir
araca çevireceğiz.**

**Stack kararı (liyakat bazlı):**
- Dil: Python (model Python).
- Veri: tidy/long Parquet (ragged veri için doğru, dil-bağımsız, atıf'a uygun).
- Sorgu: DuckDB (SQL → ileride DuckDB-WASM ile tarayıcıda da çalışır).
- UI: Önce Streamlit (öğren+doğrula) → sonra Observable+D3 (BioRender-üstü).
- Pre-computation (jux 2h sürüyor → canlı sim imkânsız, batch + DB).

**Kuzey yıldızı (öncelik):** 1) Atıf'lı interaktif bilim görseli → 2) Doktor dashboard'u → 3) Klinik karar.

---

## 2026-05-24 · Faz 1: Model kuruldu ve ilk veri

- `mstadt/nephron` indirildi, NumPy uyumsuzluğu çözüldü.
- İlk koşu: `--type superficial` (15 dk). Sonuç: 1076 txt, `female_hum_normal/`.
- **Eksiklik tespit edildi:** SDL 580 mOsm, mTAL 253 — gradyan yok çünkü jux yok.
- Gece koşusu için plan: `--type multiple` (sup + jux1-5, ~2h).

---

## 2026-05-25 · Faz 2: Modeli ve veriyi öğrendik (kod okuma + sınav)

- Layton modelin nasıl çalıştığı (driver/compute/output) öğrenildi.
- Dosya isim formülü çıkarıldı: `sex_species_segment_VARIABLE[_neph].txt`.
- Pandas + DuckDB + tidy/long temelleri öğretildi, mini sınavlarla doğrulandı.
- mTAL Na 261→102 doğrulandı, NKCC2 1:2 stokiyometrisi onaylandı.
- **Append-bug tespit edildi:** taşıyıcı flux dosyaları 'a' modunda → re-run bozar.

---

## 2026-05-25 · Faz 3: Loader v1 (sadece konsantrasyon)

- `build_database.py` yazıldı: tidy/long DataFrame → Parquet.
- 450 con_of dosyası → 81.045 satır → `nephron_data.parquet`.
- DuckDB sorgusu ile zincirleme doğrulandı (her segmentin çıkışı = sonrakinin girişi).

---

## 2026-05-25 · Faz 4: SQL tartışması — liyakat vs. alışkanlık

- Kullanıcı SQL'in **liyakat sebebiyle mi yoksa kolayına geldiği için mi** seçildiğini sordu.
- Dürüst gözden geçirme: DuckDB, browser-WASM yolu ve kuzey yıldızına hizmet için
  **objektif olarak güçlü**, sadece SQL bilgisi nedeniyle değil. Karar korundu.

---

## 2026-05-29 · Faz 5: Tam veri + 14 kategori loader

- Eski `female_hum_normal` yedeklendi (`_suponly_bak`) → append-bug önlendi.
- `--type multiple` çalıştırıldı, sup + jux1-5 + merged tamamlandı.
- Loader genişletildi: **classify-then-route** tasarımı, 14 kategori (con/flow/osmolality/
  flux/water_volume/pH/pressure/potential/diameter/length/apical/paracellular/transporter).
- Sonuç: 5731 dosya → **1.033.065 satır**, 0 parse hatası.
- **Append-bug kontrolü** sürpriz keşif: 41 CCD flux dosyası 400-600 satır.
  Düzeltme: bu re-run bozulması değil, **modelin içsel çok-membran yapısı** (A/B tipi
  ara hücreler farklı membranlarda aynı taşıyıcı). Loader şimdilik tek profil sayıyor;
  membran başına ayırma görev #4'te yapılacak.

---

## 2026-05-29 · Faz 6: Gradyan doğrulaması (asıl ödül)

- Kortikomedüller gradyan: korteks ~300 → IMCD interstisyum ~734 mOsm.
- İdrar 619 mOsm > plazma 300 → idrar **konsantre ediliyor** → ADH etkin (düşük değil).
- Literatür: insan papilla tepesi ~1200 mOsm. **Açık: ~470 mOsm.**
- Sebep: **iç medulla konsantrasyon mekanizmasının (MİH)** matematiksel modellerce
  tam üretilememesi — bilinen açık problem.

---

## 2026-05-29 · Faz 7: Proje masaüstüne taşındı + ilk Streamlit

- `~/Desktop/Nefron-Projesi/` kuruldu (README, kod, veri, notlar, yedekler).
- Ham veri ve Parquet projeye kopyalandı.
- İlk yedek: `yedek_20260525_1647.zip` (15M, sıfır noktası).
- İlk **Streamlit arayüzü** (`kod/app.py`): solüt/segment/kompartman/nefron seç → SQL → çizgi grafik.
- Streamlit mantığı öğretildi: "her değişimde betik baştan koşar".

---

## 2026-05-29 · Faz 8: LDL doğrulaması (sezgi vs. modern fizyoloji)

- Kullanıcı sordu: "LDL yalnız su geçirgen, NH3 neden düşüyor?"
- Veri+parametre incelemesi:
  - LDL apikal geçirgenlikleri: Na/Cl/K/NH4 = 0, urea = 80, **NH3 = 85**, CO2 = 1200.
  - LDL jux5 lumen verisi: **urea ×5.1**, NH3 ×0.84 (lumen↔bath dengelendi), Na/Cl ×0.81.
- **Sonuç:** Model "klasik su-permeabl basit DTL" değil, **modern iç medulla biyolojisini**
  (urea recycling + NH3 gaz difüzyonu) doğru implemente ediyor. Kullanıcının dediği
  **üre geri dönüşümü mekanizması** veride canlı.
- Detay: `bulgular.md` → "LDL doğrulaması (jux5)" bölümü.
- Yedek: `yedek_20260529_1738_ldl_dogrulama.zip`.

---

## 2026-05-29 · Faz 9: Streamlit profesyonelleştirildi

- App yeniden yazıldı: 5 sekme + Plotly + otomatik fizyoloji doğrulamaları + veri bütünlüğü paneli.
- Sekmeler:
  1. Segment Profili (Lumen+Bath overlay)
  2. Tüm Nefron (PT→IMCD zincirli)
  3. Nefron Tipleri Karşılaştırma (sup vs jux1-5)
  4. Fizyoloji Doğrulamaları (otomatik check'ler)
  5. Veri Bütünlüğü (kategoriler, bilinen sorunlar)
- Yedek: `yedek_20260529_1748_app_profesyonel.zip`.

---

## 2026-05-29 · Faz 10: LDL Na düşüşünün matematik kapanışı + UI v2

Kullanıcı LDL jux1'de Na'nın 302→290 düşmesini sorguladı. İki klasik varsayım çürütüldü:

- **"Su azalıyor" YANLIŞ** — Veri: jux1 su akısı 16.92→17.35 (+%2.5), jux5 16.92→18.44 (+%9).
  Su lümene GİRER (urea+su tuzağı).
- **"Na kütlesi sabit" kısmen yanlış** — perm_Na_Lumen_Cell=0 doğru (transselüler kapalı),
  ama paraselüler `paracellular_Na` akısı sıfır değil (jux5 ort 0.127, max 0.564 pmol/min).
  Konvektif sürüklenme (solvent-drag) Na'yı dışarı taşır.
- **Matematik kapanış (jux5):** 4484/18.44 = 243.2 mM ✓. Konsantrasyon = kütle/hacim formülü
  tamamen tutarlı. Kütle ×0.88, hacim ×1.09 → konsantrasyon ×0.805 = %19.5 düşüş.
- Bulgular: `bulgular.md` → "Ek: Na konsantrasyonu düşüşünün matematik kapanışı (jux5)".

**UI v2 — daha profesyonel:**
- Plotly için `nefron` özel temasi (simple_white tabanlı, klinik renk paleti, Inter fontu).
- Yan panel: proje bağlamı + veri kaynağı + atıf + birim referansı.
- Sekme 1: üst kart (giriş/çıkış metrikleri + dilim sayısı), segment hakkında expander.
- Sekme 3: nefron tipleri için derinlik-renk paleti (sup kırmızı, jux1→jux5 mavi gradyanı).
- Sekme 4: doğrulamalar kart-grid (border-left renkli, ✓/✗ rozetli, hedef belirtimli).
- Sekme 5: bilinen açık konular renkli uyarı kartlarında.
- Yedek: bu fazın sonunda alınacak.

---

<!-- Buraya yeni girişler ekle (en üste değil, en alta — kronolojik) -->
