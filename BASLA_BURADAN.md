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

Devam etmeden önce şu üç dosyayı OKU:
1. ~/Desktop/Nefron-Projesi/README.md
   (mimari, klasör yapısı, komutlar)
2. ~/Desktop/Nefron-Projesi/notlar/gunluk.md
   (kronolojik proje hikayesi — özellikle EN SON faz)
3. ~/Desktop/Nefron-Projesi/notlar/bulgular.md
   (bilimsel kararlar ve doğrulamalar)

İsteğe bağlı: ~/Desktop/Nefron-Projesi/notlar/terminoloji.md (sözlük).

Çalışma kuralları (önceki oturumlardan):
- Türkçe konuş, dürüst ol, fabrikasyon yapma.
- Kullanıcı tıp öğrencisi: fizyolojisini koz olarak kullan, sezgilerini sorgulamasını teşvik et.
- Veri doğrulama refleksi şart: ne grafik çizersen önce fizyolojiden bekle, sonra veriyle test et.
- Kritik karar veya bilimsel bulgu olursa notlar/bulgular.md'ye işle.
- Önemli milestone'larda yedekler/ klasörüne zaman damgalı zip yedek al
  (komut: cd ~/Desktop/Nefron-Projesi && TS=$(date +%Y%m%d_%H%M) && zip -r -q yedekler/yedek_${TS}_<aciklama>.zip README.md kod notlar veri)
- gunluk.md'yi kronolojik olarak güncel tut, her önemli adımı "## TARİH · Faz N: başlık" formatında en alta ekle.

Görev panosu önceki oturumdan:
- Tüm-nefron grafiği: tamamlandı (Sekme 2)
- Streamlit interaktif keşif: kullanıcı devam ediyor
- Hu et al. 2021 ile ~734 mOsm tepe karşılaştırması: bekliyor
- Çok-membranlı flux dosyalarını ayırma: bekliyor

Şimdi yukarıdaki üç dosyayı oku, ardından bana "hazırım, nereden devam edelim" diye söyle ve mevcut durumu kısaca özetle.
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
