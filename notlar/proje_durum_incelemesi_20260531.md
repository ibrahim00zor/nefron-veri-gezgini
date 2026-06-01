# Proje Durum İncelemesi — 2026-05-31

Bu dosya, projenin o günkü kapsamlı kesidini saklar. Sonraki incelemeler için
yeni dosya açılır (örn. `proje_durum_incelemesi_20260815.md`); eski olanlar arşivlenir.

## Misyon (tek cümle)

**En iyi peer-reviewed nefron modelini (Layton/Hu) doktorlar ve araştırmacılar için
atıf yapılabilir, interaktif bir bilim aracına dönüştürmek.**
Yeni matematik yazmıyoruz; var olanı erişilebilir kılıyoruz.

## Kuzey yıldızları (öncelik sırasıyla)

| Sıra | Hedef |
|---|---|
| #1 | BioRender-üstü atıf yapılabilir interaktif bilim görseli |
| #2 | Doktor/araştırmacı senaryo dashboard'u (ilaç etkisi simülasyonu) |
| #3 | Klinik karar desteği |

## Mimari kararlar (yerinde, değişmedi)

| Katman | Seçim | Gerekçe |
|---|---|---|
| Hesaplama motoru | Layton/Hu Python modeli (`mstadt/nephron`) | Peer-reviewed, en iyi insan modeli |
| Veri biçimi | Tidy/long Parquet | Ragged veri için doğru, atıf'a uygun |
| Sorgu | DuckDB (SQL) | Hızlı + ileride tarayıcıda WASM |
| Arayüz (Faz 1) | Streamlit | Python-native, doğrulanabilir |
| Arayüz (Faz 2, hedef) | Observable Framework + D3 | Yayın kalitesi, statik site |
| Sunucu | YOK (statik + pre-compute) | Jux 2h sürer → canlı imkânsız |

## Fazlar (kronolojik özet)

| Faz | Tarih | Konu | Sonuç |
|---|---|---|---|
| 0 | 05-24 | Strateji + mimari | Stack onaylandı |
| 1 | 05-24 | Model kuruldu, ilk koşu | 15 dk, 1076 txt (yalnız sup) |
| 2 | 05-25 | Modeli + veriyi öğrenme | NKCC2 1:2 stokiyometri doğrulandı |
| 3 | 05-25 | Loader v1 (yalnız konsantrasyon) | 81k satır → ilk Parquet |
| 4 | 05-25 | SQL tartışması — liyakat mi alışkanlık mı | DuckDB liyakaten korundu |
| 5 | 05-29 | Tam veri + 14 kategori loader | 5731 dosya → 1.033.065 satır |
| 6 | 05-29 | Gradyan doğrulaması | 300 → 734 mOsm (literatür ~1200) |
| 7 | 05-29 | Masaüstüne taşıma + ilk Streamlit | Düzen + ilk UI |
| 8 | 05-29 | LDL doğrulaması (sezgi vs modern fizyoloji) | Ürea geri dönüşümü modelde canlı |
| 9 | 05-29 | Streamlit profesyonelleştirildi | 5 sekme + Plotly |
| 10 | 05-29 | LDL Na matematik kapanışı + UI v2 | Kütle/hacim mantığı kanıtlandı |
| 11 | 05-31 | GitHub + Streamlit Cloud deploy (yan kol) | Canlı public URL, iPad'de erişim |
| 12 | 05-31 | **Proje durum incelemesi + flux uyarısı + versiyon kaydı** (bu dosya) | Disiplin pekiştirildi |

## Bilimsel olarak doğrulanmış (9/9 ✓)

- Filtrat ≈ 298 mOsm
- PT izoozmotik (298.5 → 300.9)
- mTAL dilüsyon (lumen Na 262 → 102)
- NKCC2 stokiyometri Cl/Na = 2.00 (kusursuz 1:2)
- Üre geri dönüşümü ×5.1 (LDL jux5 lumen)
- NH3 lümen↔bath denge (LDL jux5 çıkışı)
- Segment zincirleme (mTAL çıkış = cTAL giriş, Na)
- İdrar 619 mOsm > plazma → ADH etkin
- Kortikomedüller gradyan CCD→IMCD interstisyum 298 → 734 mOsm

## Bilinen sınırlar

1. **Gradyan tavanı ~734 vs literatür ~1200:** İç medulla konsantrasyon mekanizmasının (MİH)
   matematiksel modellerce tam üretilememesi — bilinen açık problem (renal modelleme alanı).
2. **Çok-membranlı flux dosyaları:** CCD'de 41 dosya (AE1=2, HATPase/HKATPase=3 membran)
   tek profil olarak yorumlanıyor → flux ekseninde yanlış görüntü riski. **Streamlit'te
   yan panelde uyarı eklendi (Faz 12).** Tam düzeltme: Görev #4.
3. **Birim belirsizlikleri:** pressure / diameter / length birimleri kaynaktan teyit edilmedi.
4. **Tek senaryo:** Veri seti yalnız "normal kadın insan". Faz 2 için ilaç-pertürbasyonu
   ve hastalık senaryoları üretilmeli.

## Açık görevler

| # | Konu | Aciliyet | Sahibi |
|---|---|---|---|
| 2 | Hu et al. 2021 ile gradyan/değer karşılaştırması | Aktif | Kullanıcı (kendi ders kitabı + paper okuma) |
| 4 | 41 çok-membranlı flux dosyasını ayır | Bekliyor (uyarı eklendi) | Bizim |
| — | Senaryo kütüphanesini ~10'a çıkar (hastalık, cinsiyet, inhibisyon, vb.) | Sıradaki | Bizim — arka plan |
| — | Faz 2 görsel tasarımı (hangi hero görseller?) | Senaryo kütüphanesi sonrası | Bizim — strateji |
| — | Versiyon notu | ✓ Tamamlandı (Faz 12) | — |

## Gözden geçirme — eleştirel notlar

1. **Senaryo kütüphanesi 1/N:** Şu an tek senaryo (normal kadın insan). Faz 2'nin asıl
   gücü ilaç-pertürbasyonu karşılaştırması olacak (örn. SGLT2 inhibisyonu önce/sonra).
2. **Faz 2 hâlâ yazılı niyet:** Observable + D3 + DuckDB-WASM kararı sağlam, ama hangi
   spesifik görselleri kuracağımız tanımlı değil.
3. **Görev #4 risk azaltıldı:** Yan panel uyarısı eklendi, ama tam düzeltme borç olarak duruyor.
4. **Bağımsız bilimsel doğrulama:** Kullanıcı Hu paper ve nefroloji ders kitabı ile şu an
   yapıyor. Tamamlandığında bu doküman güncellenecek.
5. **Reprodüksiyon ✓:** Bu adımda `versiyonlar.md` yazıldı. Python 3.14.2 + Layton commit
   `761ab729092e1fefcd82cb84ba0b2a56e04be951` sabit referansımız.

## Kararlar (bu inceleme turundan)

- Mimari yerinde, değişmiyor (kullanıcı yazılım dünyasında AI'ye bağımlı, mevcut kararlar
  liyakat bazlı, korunuyor).
- Flux uyarısı app'in yan paneline eklendi — kullanıcıyı yanıltma riski azaltıldı.
- Hu et al. 2021 karşılaştırmasını kullanıcı kendi inisiyatifiyle yapacak (nefroloji
  profesörü ders kitabıyla); biz Faz 2 ön hazırlığı (senaryo kütüphanesi) ile devam edeceğiz.
- Senaryo kütüphanesi ~10 senaryo: cinsiyet (M/F), hastalık (diyabet),
  inhibisyon (ACE, SGLT2), obezite, hipertansiyon, ünineprektomi varyasyonları.
- Versiyon notu (`versiyonlar.md`) eklendi.
