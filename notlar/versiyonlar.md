# Reprodüksiyon — Versiyon Notları

Bu proje şu kesin sürümlerle üretildi. Yeniden üretmek isteyen biri bu sürümleri kullanmalı.

## Hesaplama ortamı

| Bileşen | Sürüm |
|---|---|
| macOS | 26.5 (25F71) |
| Mimari | arm64 (Apple Silicon M4) |
| Python | 3.14.2 |

## Python kütüphaneleri (Streamlit + veri katmanı)

| Paket | Sürüm | Rol |
|---|---|---|
| streamlit | 1.52.2 | Arayüz |
| duckdb | 1.5.3 | SQL motoru |
| pandas | 2.3.3 | DataFrame |
| plotly | 6.5.0 | Grafik |
| pyarrow | 22.0.0 | Parquet I/O |
| numpy | 1.26.4 | Sayısal |

`requirements.txt` daha gevşek alt sınırlarla tanımlıdır (Streamlit Cloud uyumluluğu için).

## Hesaplama motoru (Layton/Hu modeli)

| Bilgi | Değer |
|---|---|
| Repo | `github.com/mstadt/nephron` |
| Commit hash | `761ab729092e1fefcd82cb84ba0b2a56e04be951` |
| Tarih | 2022-07-05 |
| Mesaj | "Merge pull request #179 from mstadt/fixROMK" |
| Yerel yol | `~/nephron` |

> Layton modeli numpy < 2.0 ile çalışır (uyumsuzluk vardı). Bizim Streamlit appimiz
> bundan etkilenmez (modeli çalıştırmıyor, çıktısını okuyor).

## Veri seti

| Bilgi | Değer |
|---|---|
| Senaryo | Kadın, insan, "normal" (baseline) |
| Komut | `python3 parallel_simulate.py --sex female --species human --type multiple` |
| Nefron tipleri | sup + jux1 + jux2 + jux3 + jux4 + jux5 + merged (CD) |
| Üretilen txt | 5731 dosya, ~25 MB |
| Tidy Parquet | 1.033.065 satır, ~8 MB (`veri/nephron_veritabani.parquet`) |
| Hesaplama süresi | ~2 saat (multiprocessing, tüm çekirdekler) |

## Atıflar

- **Model (insan, cinsiyet-spesifik):** Hu R. et al. "Sex differences in solute and water handling in the human kidney: Modeling and functional implications." *iScience* 24(6):102694, 2021.
- **Model kodu:** Stadt M., Layton A.T. — `github.com/mstadt/nephron`
- **Önceki sürümler:** Layton A.T., Layton H.E. — `github.com/uwrhu`
