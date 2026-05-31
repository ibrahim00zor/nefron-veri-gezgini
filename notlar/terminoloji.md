# Terminoloji Sözlüğü

## Segmentler (idrarın akış sırasına göre)
| Kod | Açılım | Not |
|---|---|---|
| PT | Proksimal kıvrımlı tübül | İzoozmotik kütle geri emilimi (~%67) |
| S3 | Proksimal düz tübül (pars recta) | PT'nin devamı |
| SDL | Kısa inen ince kol | Su geçirgen; yüzeysel + jux |
| LDL | Uzun inen ince kol | **Sadece jukstamedüller**; medullaya derin dalar |
| LAL | Uzun çıkan ince kol | **Sadece jukstamedüller** |
| mTAL | Medüller kalın çıkan kol | Dilüsyon segmenti (NKCC2), su geçirmez |
| cTAL | Kortikal kalın çıkan kol | Dilüsyona devam; sonunda makula densa |
| DCT | Distal kıvrımlı tübül | NCC (tiyazid hedefi) |
| CNT | Bağlantı tübülü | ENaC başlar; çok hücre tipli |
| CCD | Kortikal toplayıcı kanal | ENaC, AQP2, ara hücreler (A/B) |
| OMCD | Dış medüller toplayıcı kanal | |
| IMCD | İç medüller toplayıcı kanal | Üre, AQP2, son konsantrasyon |

## Nefron tipleri
- **sup** (superficial / yüzeysel): kısa kulp; insanda ~%85. Sadece SDL+mTAL.
- **jux1–jux5** (juxtamedullary / jukstamedüller): uzun kulp (LDL+LAL), medullaya dalar; ~%15.
  jux5 en derin. **Medüller gradyanı bunlar yaratır.**
- **merged**: toplayıcı kanal (CCD/OMCD/IMCD) — tüm nefronlar burada birleşir, ek almaz.

## Taşıyıcılar (pompalar)
| Kod | Açılım | Bulunduğu yer / ilaç |
|---|---|---|
| NaKATPase | Na/K-ATPaz | Tüm hücrelerde bazolateral (motor) |
| NHE3 | Na/H değiştirici 3 | PT apikal |
| SGLT1/2 | Na-glukoz kotransport | PT apikal; **SGLT2 = gliflozin hedefi** |
| GLUT1/2 | Glukoz taşıyıcı | Bazolateral |
| NKCC2 (A/B/F) | Na-K-2Cl kotransport | TAL apikal; **loop diüretik hedefi** |
| ROMK (apical_K) | K kanalı | TAL; K geri dönüşümü |
| NCC | Na-Cl kotransport | DCT apikal; **tiyazid hedefi** |
| ENaC | Epitelyal Na kanalı | CNT/CD apikal; **aldosteron / amilorid hedefi** |
| KCC4 | K-Cl kotransport | |
| AE1 | Anyon değiştirici (Cl/HCO3) | A tipi ara hücre |
| Pendrin | Cl/HCO3 değiştirici | B tipi ara hücre |
| HATPase | H-ATPaz | Ara hücre (asit atılımı) |
| HKATPase | H/K-ATPaz | Ara hücre |
| NHE1 / NKCC1 | bazolateral değiştirici/kotransport | |

## Solütler (15, sabit sıra)
Na, K, Cl, HCO3, H2CO3, CO2, HPO4, H2PO4, urea (üre), NH3, NH4, H, HCO2, H2CO2, glu (glukoz)

## Kompartmanlar
| Kod | Açılım |
|---|---|
| Lumen | Tübül sıvısı (idrar) |
| Cell | Epitel hücre içi |
| Bath | İnterstisyum / peritübüler (çevre doku) |
| LIS | Lateral hücreler arası boşluk |
| ICA / ICB | A / B tipi ara hücre (sadece toplayıcı kanal) |

## Değişken kategorileri (tidy tabloda `variable`)
con (konsantrasyon, mM) · flow (akı, pmol/min) · flux (taşıyıcı/yol akısı, pmol/min) ·
osmolality (mOsm) · water_volume (nl/min) · potential (mV) · pH · pressure · diameter · length

## Birimler
Konsantrasyon: **mM (mmol/L)** · Akı: **pmol/min** · Hacim: **nl/min**
(pressure/diameter/length birimleri henüz kaynaktan teyit edilmedi)
