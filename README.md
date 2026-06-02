# Nefron Veri Gezgini

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20489610.svg)](https://doi.org/10.5281/zenodo.20489610)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: CC BY 4.0](https://img.shields.io/badge/Content-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Streamlit App](https://img.shields.io/badge/Live-Streamlit%20App-FF4B4B?logo=streamlit&logoColor=white)](https://nefron-veri-gezgini.streamlit.app)

İnsan nefronu epitelyal transport modelinin (Layton/Hu) çıktılarını, doktorlar ve
araştırmacılar için **atıf yapılabilir, interaktif bir bilim/görselleştirme aracına**
dönüştürme projesi.

**📌 Atıf:** Zor, İ. (2026). *Nefron Veri Gezgini.* Zenodo. https://doi.org/10.5281/zenodo.20489610

> Bu klasör senin "ana üssün". Kafan karışınca buraya dön — her şeyin yeri burada yazılı.

---

## Klasör haritası

```
Nefron-Projesi/
├── README.md          <- BU DOSYA (her şeyin haritası)
├── BASLA_BURADAN.md   <- Yeni oturum açış prompt'u (bağlam aktarımı)
├── LICENSE / LICENSE-CONTENT / CITATION.cff   <- Akademik altyapı
├── veri/
│   ├── ham_scenarios/ <- Senaryo başına ham txt çıktıları (repo dışı, .gitignore)
│   └── nephron_veritabani.parquet  <- 6 senaryo tek tidy tablo (6.198.390 satır)
├── kod/
│   ├── app.py             <- Anasayfa (Streamlit landing)
│   ├── ui_kit.py          <- Paylaşılan: sidebar, sorgu, grafik, atıf footer'ı
│   ├── egitim_icerigi.py  <- Eğitim içeriği (Türkmen 2024 paraphrase + cite)
│   ├── yorum_motoru.py    <- Otomatik kütle/hacim yorum ayrıştırıcı
│   ├── build_database.py  <- Ham txt -> tidy Parquet (çoklu senaryo)
│   ├── run_scenarios.py   <- Senaryo üretici (resumable)
│   └── pages/             <- 1 Segment · 2 Tüm Nefron · 3 Tipler · 4 Karşılaştırma
│                             5 Doğrulamalar · 6 Veri Bütünlüğü
├── notlar/
│   ├── gunluk.md      <- Kronolojik proje hikayesi (faz faz)
│   ├── bulgular.md    <- Bilimsel bulgular + kararlar
│   ├── terminoloji.md <- Segment / taşıyıcı / solüt sözlüğü
│   └── versiyonlar.md <- Reprodüksiyon için sabit sürümler
└── yedekler/          <- Zaman damgalı yedekler ("sıfır noktaları")
```

**Modelin kendisi (hesaplama motoru) burada DEĞİL:** `~/nephron/` klasöründe.
Orası yeni simülasyonların çalıştığı yer. Bu proje, oradan çıkan veriyi işler.

---

## Mimari kararı (neden böyle)

- **Dil:** Python (model zaten Python).
- **Veri biçimi:** tidy/long tablo (veri düzensiz olduğu için doğru seçim).
- **Depolama:** Parquet (sıkıştırılmış, hızlı, dil-bağımsız, atıf'a uygun).
- **Sorgu:** DuckDB (SQL) — ölçekte hızlı + aynı sorgular ileride tarayıcıda (DuckDB-WASM) çalışır.
- **Arayüz:** Önce Streamlit (öğrenilebilir, doğrulanabilir) → sonra Observable + D3 (atıf'lı interaktif görsel).

---

## Sık kullanılan komutlar

Yeni simülasyon çalıştırmak (motor klasöründe, TEMİZ bir hedefe):
```
cd ~/nephron
python3 parallel_simulate.py --sex female --species human --type multiple
```

Çıktıyı projeye almak + veritabanını yeniden kurmak:
```
cp ~/nephron/female_hum_normal/*.txt ~/Desktop/Nefron-Projesi/veri/ham/
cd ~/Desktop/Nefron-Projesi
python3 kod/build_database.py
```

Veritabanını SQL ile sorgulamak (örnek):
```
python3 -c "import duckdb; print(duckdb.sql(\"SELECT DISTINCT segment FROM 'veri/nephron_veritabani.parquet'\").df())"
```

---

## Önemli uyarılar (unutma)

1. **Append-bug:** Modelin taşıyıcı akı dosyaları 'ekleme' modunda yazılır. Aynı klasöre
   iki kez simülasyon çalıştırırsan bozulur. **Her zaman temiz/boş klasöre çalıştır.**
2. **Çok-membranlı flux dosyaları (ÇÖZÜLDÜ):** CNT/CCD/OMCD'de bazı taşıyıcılar
   (AE1, HATPase, HKATPase, NHE1) birden çok hücre membranına aittir; model bunları tek
   dosyaya içe içe geçmiş (interleaved) yazar. Loader artık stride ile ayrıştırıp her profili
   doğru pozisyon eksenine oturtuyor ve `membrane` kolonunda anatomik kompartman çiftiyle
   etiketliyor. (bkz. notlar/bulgular.md)

---

## Lisans

İkili lisanslama (akademik standart — PLOS, eLife, NIH gibi):

- **Kod** (`kod/` içindekiler) → [**MIT License**](LICENSE)
  - Kullan, değiştir, dağıt, ticari kullan — atıf'la
- **İçerik / veri / figürler** (`notlar/`, `veri/*.parquet`, ekran görüntüleri) →
  [**Creative Commons Attribution 4.0 (CC-BY 4.0)**](LICENSE-CONTENT)
  - Paylaş, uyarla, ticari kullan — atıf'la

## Atıf (Citation)

Bu projeyi akademik çalışmada kullanıyorsan, [`CITATION.cff`](CITATION.cff) dosyasındaki
formatı kullan. Kısa biçim:

> Zor, İ. (2026). *Nefron Veri Gezgini* (Computer software).
> https://github.com/ibrahim00zor/nefron-veri-gezgini

**Önemli:** Bu projenin verisi Hu et al. 2021 modelinden türetilmiştir. Verimize atıf
yaparken **orijinal makaleyi de** referans göster:

> Hu, R., et al. (2021). *Sex differences in solute and water handling in the
> human kidney.* iScience 24(6):102694.
> https://doi.org/10.1016/j.isci.2021.102694

## Mevcut durum (Faz 19.1 — 2026-06)

Tamamlanan:
- [x] Model bulundu, kuruldu, çalıştı (sup + jux1-5 + merged)
- [x] Ham veri tidy Parquet'e çevrildi (6 senaryo, 6.198.390 satır, 0 hata)
- [x] Fizyolojik doğrulamalar yapıldı (bkz. bulgular.md)
- [x] 6 senaryo: F_normal, M_normal, F_diab_mod, F_HT, F_SGLT2, M_SGLT2
- [x] Multi-page Streamlit + paylaşılan ui_kit + eğitim katmanı + otomatik yorum
- [x] Akademik altyapı: MIT + CC-BY 4.0 + CITATION.cff + Zenodo DOI
- [x] Streamlit Cloud canlı: nefron-veri-gezgini.streamlit.app
- [x] Çok-membranlı flux dosyaları membran başına ayrıldı (Görev #4 — `membrane` kolonu)

Açık / sonraki:
- [ ] `egitim_icerigi.py` özet alanlarını doldur (Türkmen 2024 paraphrase + cite)
- [ ] Hu et al. 2021 ile gradyan (~734 mOsm) karşılaştırması
- [ ] 4 başarısız senaryo (Newton overflow): F_diab_severe, F_ACE, F_obese, F_UNX
- [ ] Faz 4 (Observable + D3 interaktif görsel) · Faz 5 (hekim eğitici araç)

---

## Sıfır noktaları (geri dönülebilir checkpoint disiplini)

Proje istenmeyen yöne kayarsa **bilinen-iyi bir noktaya** dönmek için iki katmanlı sistem:

1. **Git tag** (asıl sıfır noktası — hafif, isimli, GitHub'da):
   - `v1.0.0` — Zenodo DOI release
   - `v-fazNN` — her milestone kapanışında (örn. `v-faz19.1`)
   - Geri dönüş: `git checkout v-faz19.1` (incele) · sıfırlamak için `git reset --hard v-faz19.1`
   - Liste: `git tag -l`
2. **Zip yedek** (lokal, veri dahil — `yedekler/`):
   - `yedek_lite_*` (kod+notlar+parquet, ~5-35MB) — her milestone
   - `yedek_FULL_*` (her şey + ham veri) — ayda 1-2 kez
   - Komut README altındaki "yedek alma" kuralında.

**Kural:** Her faz kapanışında → commit + `v-fazNN` tag + lite yedek + `gunluk.md`'ye giriş.
