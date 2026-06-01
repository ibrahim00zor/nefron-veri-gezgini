# Nefron Projesi

İnsan nefronu epitelyal transport modelinin (Layton/Hu) çıktılarını, doktorlar ve
araştırmacılar için **atıf yapılabilir, interaktif bir bilim/görselleştirme aracına**
dönüştürme projesi.

> Bu klasör senin "ana üssün". Kafan karışınca buraya dön — her şeyin yeri burada yazılı.

---

## Klasör haritası

```
Nefron-Projesi/
├── README.md          <- BU DOSYA (her şeyin haritası)
├── veri/
│   ├── ham/           <- Modelin ürettiği ham txt çıktıları (5731 dosya)
│   └── nephron_veritabani.parquet  <- Hepsinin tek tidy tablo hâli (~1M satır)
├── kod/
│   └── build_database.py   <- Ham txt'leri -> tidy Parquet'e çeviren yükleyici
├── notlar/
│   ├── bulgular.md    <- Şimdiye kadarki bilimsel bulgular + kararlar
│   └── terminoloji.md <- Segment / taşıyıcı / solüt sözlüğü
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
2. **Çok-membranlı flux dosyaları:** CCD'de bazı taşıyıcılar (AE1=400, HATPase=600 satır)
   birden çok hücre membranına aittir; tek profil değil. Loader bunları şimdilik işaretliyor,
   ileride membran başına ayrılacak. (bkz. notlar/bulgular.md)

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

## Mevcut durum

- [x] Model bulundu, kuruldu, çalıştı (sup + jux1-5 + merged)
- [x] Ham veri tidy Parquet'e çevrildi (1.033.065 satır, 0 hata)
- [x] Fizyolojik doğrulamalar yapıldı (bkz. bulgular.md)
- [ ] Çok-membranlı flux dosyalarını membran başına ayır
- [ ] ~734 mOsm tepe değerini Hu et al. 2021 ile karşılaştır
- [ ] Streamlit ile ilk görselleştirme arayüzü
