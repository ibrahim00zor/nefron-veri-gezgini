"""
egitim_icerigi.py — Eğitim katmanının içerik kaynağı.

NASIL DÜZENLENİR:
1. SEGMENT, TASIYICI, SOLUT sözlüklerinde her bir kayıt için "ozet" alanını
   kendi cümlelerinle doldur (paraphrase + cite modeli — birebir kopya değil).
2. "kaynak_sayfa" alanına Türkmen 2024'te ilgili sayfa numarasını yaz.
3. Boş "ozet" alanları Streamlit'te "henüz eklenmemiş" olarak görünür.

ATIF DİSİPLİNİ:
- Birebir alıntı YAPMA (kitap copyright'ı kısıtlı).
- Bilgiyi öğrenip kendi cümlenle özetle, sonuna "Türkmen 2024, s. X" notu ekle.
- İleride PubMed paper'larıyla zenginleştirilebilir.
"""

# =============================================================
#  ATIFLAR — merkezi referans listesi
# =============================================================
ATIFLAR = {
    "turkmen2024": {
        "kisa": "Türkmen 2024",
        "tam":  "Türkmen, K. (2024). İnsan Fizyolojisinin Temel Kuramları – "
                "Boşaltım, Dişi-Erkek Üreme ve Gebelik Fizyolojisi. 1. Basım. "
                "Konya: Dizgi Ofset. ISBN: 978-625-99451-0-1.",
        "tur":  "kitap",
    },
    "hu2021": {
        "kisa": "Hu et al. 2021",
        "tam":  "Hu, R., et al. (2021). Sex differences in solute and water handling "
                "in the human kidney. iScience 24(6):102694.",
        "url":  "https://www.sciencedirect.com/science/article/pii/S2589004221006350",
        "tur":  "makale",
    },
    "layton2019": {
        "kisa": "Layton & Layton 2019",
        "tam":  "Layton, A.T., Layton, H.E. (2019). A computational model of epithelial "
                "solute and water transport along a human nephron. PLOS Comp Biol.",
        "tur":  "makale",
    },
}


# =============================================================
#  SEGMENT İÇERİĞİ
#  Her segment için: özet (kullanıcı yazar), apikal/bazolateral
#  taşıyıcı listesi (yapısal), atıf kaynak sayfası.
# =============================================================
SEGMENT = {
    "PT": {
        "tam_ad": "Proksimal Kıvrımlı Tübül",
        "ozet": "",  # KULLANICI: Türkmen 2024'ten öğrenip kendi cümlelerinle özetle
        "apikal":      ["NHE3", "SGLT1", "SGLT2", "AQP1"],
        "bazolateral": ["NaKATPase", "GLUT2"],
        "kaynak_sayfa": "",  # KULLANICI: Türkmen 2024'te ilgili sayfa
        "kaynak_anahtar": "turkmen2024",
    },
    "S3": {
        "tam_ad": "Proksimal Düz Tübül (pars recta)",
        "ozet": "",
        "apikal":      ["NHE3", "SGLT1", "AQP1"],
        "bazolateral": ["NaKATPase", "GLUT1"],
        "kaynak_sayfa": "",
        "kaynak_anahtar": "turkmen2024",
    },
    "SDL": {
        "tam_ad": "Kısa İnen İnce Kol",
        "ozet": "",
        "apikal":      ["AQP1"],  # su geçirgen, solüt kapalı
        "bazolateral": [],
        "kaynak_sayfa": "",
        "kaynak_anahtar": "turkmen2024",
    },
    "LDL": {
        "tam_ad": "Uzun İnen İnce Kol (yalnız jukstamedüller)",
        "ozet": "",
        "apikal":      ["AQP1 (kısıtlı)", "urea geçirgen", "NH3 geçirgen"],
        "bazolateral": [],
        "kaynak_sayfa": "",
        "kaynak_anahtar": "turkmen2024",
        "not": "Modern anlayışta klasik 'sadece su geçirgen' tanımı geçerli değil — "
               "ürea-permeabl, paraselüler Na konvektif kaçağı var.",
    },
    "LAL": {
        "tam_ad": "Uzun Çıkan İnce Kol (yalnız jukstamedüller)",
        "ozet": "",
        "apikal":      ["pasif NaCl geri emilim"],
        "bazolateral": [],
        "kaynak_sayfa": "",
        "kaynak_anahtar": "turkmen2024",
    },
    "mTAL": {
        "tam_ad": "Medüller Kalın Çıkan Kol",
        "ozet": "",
        "apikal":      ["NKCC2", "ROMK", "NHE3"],
        "bazolateral": ["NaKATPase", "ClC-Kb", "KCC4"],
        "kaynak_sayfa": "",
        "kaynak_anahtar": "turkmen2024",
        "not": "Dilüsyon segmenti — su geçirmez, NKCC2 ile NaCl geri emer.",
    },
    "cTAL": {
        "tam_ad": "Kortikal Kalın Çıkan Kol",
        "ozet": "",
        "apikal":      ["NKCC2", "ROMK"],
        "bazolateral": ["NaKATPase", "ClC-Kb"],
        "kaynak_sayfa": "",
        "kaynak_anahtar": "turkmen2024",
        "not": "Sonunda makula densa (TGF feedback).",
    },
    "DCT": {
        "tam_ad": "Distal Kıvrımlı Tübül",
        "ozet": "",
        "apikal":      ["NCC"],
        "bazolateral": ["NaKATPase", "ClC-Kb"],
        "kaynak_sayfa": "",
        "kaynak_anahtar": "turkmen2024",
        "not": "NCC = tiyazid diüretik hedefi.",
    },
    "CNT": {
        "tam_ad": "Bağlantı Tübülü",
        "ozet": "",
        "apikal":      ["ENaC", "ROMK"],
        "bazolateral": ["NaKATPase", "AQP3/4"],
        "kaynak_sayfa": "",
        "kaynak_anahtar": "turkmen2024",
    },
    "CCD": {
        "tam_ad": "Kortikal Toplayıcı Kanal",
        "ozet": "",
        "apikal":      ["ENaC (PC)", "AQP2 (PC, ADH)",
                        "H-ATPase (IC-A)", "Pendrin (IC-B)"],
        "bazolateral": ["NaKATPase (PC)", "AE1 (IC-A)", "AQP3/4"],
        "kaynak_sayfa": "",
        "kaynak_anahtar": "turkmen2024",
        "not": "PC = ana hücre; IC-A/B = A/B tipi ara hücre (asit-baz).",
    },
    "OMCD": {
        "tam_ad": "Dış Medüller Toplayıcı Kanal",
        "ozet": "",
        "apikal":      ["ENaC", "AQP2", "H/K-ATPase", "H-ATPase"],
        "bazolateral": ["NaKATPase", "AE1"],
        "kaynak_sayfa": "",
        "kaynak_anahtar": "turkmen2024",
    },
    "IMCD": {
        "tam_ad": "İç Medüller Toplayıcı Kanal",
        "ozet": "",
        "apikal":      ["AQP2", "UT-A1 (üre)", "ENaC"],
        "bazolateral": ["NaKATPase", "AQP3/4", "UT-A3"],
        "kaynak_sayfa": "",
        "kaynak_anahtar": "turkmen2024",
        "not": "Üre geri dönüşümü buradan başlar — iç medulla ozmotik gradyanına katkı.",
    },
}


# =============================================================
#  TAŞIYICI İÇERİĞİ
# =============================================================
TASIYICI = {
    "NHE3":    {"tam_ad": "Sodyum-Hidrojen Değiştirici 3",   "stokiyometri": "1 Na⁺ ↔ 1 H⁺",
                "lokasyon": "PT/S3/mTAL apikal", "ilac": "", "ozet": "", "kaynak_sayfa": ""},
    "NKCC2":   {"tam_ad": "Na-K-2Cl Kotransporter Tip 2",     "stokiyometri": "1 Na⁺ + 1 K⁺ + 2 Cl⁻",
                "lokasyon": "TAL apikal", "ilac": "Loop diüretik (furosemid, bumetanid)",
                "ozet": "", "kaynak_sayfa": ""},
    "NCC":     {"tam_ad": "Na-Cl Kotransporter",              "stokiyometri": "1 Na⁺ + 1 Cl⁻",
                "lokasyon": "DCT apikal", "ilac": "Tiyazid diüretik",
                "ozet": "", "kaynak_sayfa": ""},
    "ENaC":    {"tam_ad": "Epitelyal Sodyum Kanalı",          "stokiyometri": "Na⁺ kanalı",
                "lokasyon": "CNT/CD apikal", "ilac": "Amilorid, triamteren; aldosteron düzenler",
                "ozet": "", "kaynak_sayfa": ""},
    "SGLT2":   {"tam_ad": "Sodyum-Glukoz Kotransporter 2",    "stokiyometri": "1 Na⁺ + 1 glukoz",
                "lokasyon": "PT (S1/S2) apikal", "ilac": "Gliflozinler (dapagliflozin, empagliflozin)",
                "ozet": "", "kaynak_sayfa": ""},
    "SGLT1":   {"tam_ad": "Sodyum-Glukoz Kotransporter 1",    "stokiyometri": "2 Na⁺ + 1 glukoz",
                "lokasyon": "S3 apikal", "ilac": "",
                "ozet": "", "kaynak_sayfa": ""},
    "NaKATPase": {"tam_ad": "Sodyum-Potasyum ATPaz",          "stokiyometri": "3 Na⁺ dışarı / 2 K⁺ içeri (ATP)",
                "lokasyon": "Tüm hücreler bazolateral", "ilac": "Digoksin",
                "ozet": "", "kaynak_sayfa": ""},
    "AE1":     {"tam_ad": "Anyon Değiştirici 1 (Band 3)",     "stokiyometri": "1 Cl⁻ ↔ 1 HCO₃⁻",
                "lokasyon": "CD IC-A bazolateral", "ilac": "",
                "ozet": "", "kaynak_sayfa": ""},
    "Pendrin": {"tam_ad": "Pendrin (SLC26A4)",                "stokiyometri": "1 Cl⁻ ↔ 1 HCO₃⁻",
                "lokasyon": "CD IC-B apikal", "ilac": "",
                "ozet": "", "kaynak_sayfa": ""},
    "HATPase": {"tam_ad": "V-tipi H⁺-ATPaz",                  "stokiyometri": "H⁺ pompası (ATP)",
                "lokasyon": "CD IC-A apikal", "ilac": "",
                "ozet": "", "kaynak_sayfa": ""},
    "HKATPase": {"tam_ad": "H⁺-K⁺ ATPaz",                     "stokiyometri": "H⁺ dışarı / K⁺ içeri (ATP)",
                "lokasyon": "CD IC-A apikal", "ilac": "",
                "ozet": "", "kaynak_sayfa": ""},
    "ROMK":    {"tam_ad": "Renal Outer Medullary K Channel",  "stokiyometri": "K⁺ kanalı",
                "lokasyon": "TAL/CD apikal", "ilac": "",
                "ozet": "", "kaynak_sayfa": ""},
    "AQP1":    {"tam_ad": "Akuaporin 1",                       "stokiyometri": "su kanalı",
                "lokasyon": "PT/SDL/LDL apikal+bazolateral", "ilac": "",
                "ozet": "", "kaynak_sayfa": ""},
    "AQP2":    {"tam_ad": "Akuaporin 2 (ADH-bağımlı)",         "stokiyometri": "su kanalı",
                "lokasyon": "CD PC apikal", "ilac": "Vaptanlar (ADH antagonisti)",
                "ozet": "", "kaynak_sayfa": ""},
}


# =============================================================
#  SOLÜT İÇERİĞİ
# =============================================================
SOLUT = {
    "Na":   {"tam_ad": "Sodyum (Na⁺)",
             "rol": "Ana ekstraselüler katyon; ozmotik basınç, hücre dışı sıvı hacmi.",
             "geri_emilim": {"PT": "~%67", "TAL": "~%25", "DCT": "~%5", "CD": "~%3"},
             "ozet": "", "kaynak_sayfa": ""},
    "K":    {"tam_ad": "Potasyum (K⁺)",
             "rol": "Ana hücre içi katyon; membran potansiyeli; kardiyak ritim.",
             "ozet": "", "kaynak_sayfa": ""},
    "Cl":   {"tam_ad": "Klorür (Cl⁻)",
             "rol": "Ana ekstraselüler anyon; Na ile beraber hareket.",
             "ozet": "", "kaynak_sayfa": ""},
    "HCO3": {"tam_ad": "Bikarbonat (HCO₃⁻)",
             "rol": "Ana plazma tamponu; asit-baz dengesi.",
             "ozet": "", "kaynak_sayfa": ""},
    "urea": {"tam_ad": "Üre",
             "rol": "Protein metabolizması son ürünü; iç medulla osmotik gradyan oluşumunda kritik.",
             "ozet": "", "kaynak_sayfa": ""},
    "glu":  {"tam_ad": "Glukoz",
             "rol": "Tüm filtrat normalde geri emilir; diyabette eşik aşılınca glukozüri.",
             "ozet": "", "kaynak_sayfa": ""},
    "NH3":  {"tam_ad": "Amonyak (NH₃)",
             "rol": "Yüksüz gaz, membrandan serbest geçer; renal asit atılımı.",
             "ozet": "", "kaynak_sayfa": ""},
    "NH4":  {"tam_ad": "Amonyum (NH₄⁺)",
             "rol": "Yüklü, membrana geçirmez; NKCC2 üzerinden K yerine taşınabilir.",
             "ozet": "", "kaynak_sayfa": ""},
}


# =============================================================
#  Yardımcı fonksiyonlar
# =============================================================
def segment_info(kod):
    return SEGMENT.get(kod, {})

def tasiyici_info(kod):
    return TASIYICI.get(kod, {})

def solut_info(kod):
    return SOLUT.get(kod, {})

def atif_kisa(anahtar, sayfa=None):
    a = ATIFLAR.get(anahtar, {})
    s = a.get("kisa", anahtar)
    if sayfa:
        s += f", s. {sayfa}"
    return s

def atif_tam(anahtar):
    return ATIFLAR.get(anahtar, {}).get("tam", anahtar)
