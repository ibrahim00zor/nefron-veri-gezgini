# Yeni Claude oturumu kickstart promptu

Bağlam penceresi dolup yeni oturuma geçtiğinde:
1. Bu dosyayı aç
2. Aşağıdaki ÜÇ BACKTICK arasındaki metni kopyala (Cmd+A → Cmd+C dosyada içinde değil, sadece blok)
3. Yeni Claude Code oturumunda ilk mesaj olarak yapıştır

---

```
Bu projeyi seninle önceki Claude oturumlarında birlikte kurduk.
Proje kökü: ~/Desktop/Nefron-Projesi
Konuşma dili: Türkçe.

Devam etmeden önce şu üç dosyayı OKU (en güncel hâlleri lokalde):
1. ~/Desktop/Nefron-Projesi/README.md
   (mimari, klasör yapısı, komutlar, DOI)
2. ~/Desktop/Nefron-Projesi/notlar/gunluk.md
   (kronolojik proje hikayesi — Faz 19 ve 19.1 en son durum)
3. ~/Desktop/Nefron-Projesi/notlar/bulgular.md
   (bilimsel kararlar ve doğrulamalar — LDL Na matematik kapanışı dahil)

İsteğe bağlı:
- ~/Desktop/Nefron-Projesi/notlar/terminoloji.md (sözlük)
- ~/Desktop/Nefron-Projesi/notlar/versiyonlar.md (reprodüksiyon)
- ~/Desktop/Nefron-Projesi/notlar/proje_durum_incelemesi_20260531.md (yapısal genel inceleme)

PROJE MİMARİSİ (Streamlit multi-page):
- kod/app.py = Anasayfa (landing)
- kod/ui_kit.py = paylaşılan sidebar / sorgu / chart / cite_footer
- kod/egitim_icerigi.py = içerik (kullanıcı parça parça dolduruyor; Türkmen 2024'e paraphrase + cite modeli)
- kod/yorum_motoru.py = otomatik kütle/hacim ayrıştırması
- kod/build_database.py = txt -> Parquet loader (çoklu senaryo)
- kod/run_scenarios.py = senaryo üretici (resumable)
- kod/pages/1..6 = Segment Profili, Tüm Nefron, Nefron Tipleri, Karşılaştırma, Doğrulamalar, Veri Bütünlüğü

VERİ:
- 6 senaryo başarılı: F_normal, M_normal, F_diab_mod, F_HT, F_SGLT2, M_SGLT2
- 4 başarısız (Newton overflow, modelin sayısal sınırı): F_diab_severe, F_ACE, F_obese, F_UNX
- 6,198,390 satırlık tek Parquet
- Canlı app: https://nefron-veri-gezgini.streamlit.app
- GitHub: https://github.com/ibrahim00zor/nefron-veri-gezgini
- DOI: 10.5281/zenodo.20489610

LİSANS:
- Kod: MIT  ·  İçerik/veri: CC-BY 4.0  ·  CITATION.cff repo'da

KURALLAR:
- Türkçe konuş, dürüst ol, fabrikasyon yapma.
- Kullanıcı tıp öğrencisi: fizyolojisini koz yap, sezgilerini sorgulamasını teşvik et.
- Veri doğrulama refleksi: önce fizyolojiden bekle, sonra veride test et.
- Kritik bulgu olursa notlar/bulgular.md'ye işle.
- Önemli milestone'larda yedek al:
  cd ~/Desktop/Nefron-Projesi && TS=$(date +%Y%m%d_%H%M) && zip -r -q yedekler/yedek_lite_${TS}_<ad>.zip README.md BASLA_BURADAN.md LICENSE LICENSE-CONTENT CITATION.cff .gitignore requirements.txt kod notlar veri/nephron_veritabani.parquet
- gunluk.md'yi kronolojik tut, her milestone "## TARİH · Faz N: başlık" formatında en alta.
- UI'da emoji KULLANMA — sade akademik ton. Yalnız ♀ ♂ ✓ ✗ → kalır.

AÇIK İŞLER:
- Kullanıcı egitim_icerigi.py'a notlar yazıyor (kendi temposu, toplu olarak yapıştıracak)
- Kullanıcı Hu 2021 paper'ı kendi nefroloji kitabıyla karşılaştırıyor
- Görev #4 (kod borcu): CCD multi-membran flux dosyalarını ayır (loader update)
- Faz 20+ ufukta: Faz 4 (Observable + D3 görsel tasarımı) ve Faz 5 (hekim eğitici aracı)

Şimdi yukarıdaki üç dosyayı (README, gunluk, bulgular) oku, ardından bana
"hazırım, nereden devam edelim" diye söyle ve mevcut durumu kısaca özetle.
```

---

## Notlar (sadece kullanıcı için)

- Bu prompt bir AI'yi sıfırdan bu projeye getirir; özellikle Claude Code için tasarlandı ama herhangi bir uzun-bağlamlı AI işe yarar.
- Projeye yeni bir şey eklediğinde `gunluk.md` güncelse, prompt'u değiştirmeye gerek yok — AI gunluk'u okuyup öğreniyor.
- Yedeklerin (`yedekler/`) GitHub'da yok, sadece lokalde. iCloud Drive'a kopyalamak istersen `~/Desktop/Nefron-Projesi/yedekler/`'i oraya sürükle.

## Ne zaman yeni oturum açmalıyım?

Şu işaretlerden biri olduğunda:
- Yanıtlar belirgin yavaşladı
- Claude eski bir şeyi unutuyor / yanlış hatırlıyor
- Kendine "aman dikkat çok şey biriktirdik, kapatalım" demek istiyorsun
- Büyük bir milestone bitti, doğal mola noktası
