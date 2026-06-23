"""
ui_kit.py — Paylasilan UI bileSenleri.

Anasayfa ve tum pages/ dosyalari bu modulu import eder. Tutarli sidebar, sorgu helper,
grafik tema, atif footer hep buradan gelir. Pages dosyalari sadece kendi
mantiklarini icerir — boilerplate burada.
"""
import os
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.io as pio

# ============================================================
#  Yollar (proje koklerine gore)
# ============================================================
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARQUET = os.path.join(PROJ, "veri", "nephron_veritabani.parquet")
DB = f"read_parquet('{PARQUET}')"

# ============================================================
#  Sabitler
# ============================================================
SEG_ORDER_SUP = ["PT", "S3", "SDL", "mTAL", "cTAL", "DCT", "CNT", "CCD", "OMCD", "IMCD"]
SEG_ORDER_JUX = ["PT", "S3", "SDL", "LDL", "LAL", "mTAL", "cTAL", "DCT", "CNT", "CCD", "OMCD", "IMCD"]
NEPHRONS = ["sup", "jux1", "jux2", "jux3", "jux4", "jux5", "merged"]
CD_SEGMENTS = {"CCD", "OMCD", "IMCD"}

SENARYO_AD = {
    "F_normal":   "♀ Sağlıklı kadın (baseline)",
    "M_normal":   "♂ Sağlıklı erkek (baseline)",
    "F_diab_mod": "♀ + Diyabet (orta)",
    "F_HT":       "♀ + Hipertansiyon",
    "F_SGLT2":    "♀ + SGLT2 inhibitörü",
    "M_SGLT2":    "♂ + SGLT2 inhibitörü",
}
SENARYO_DETAY = {
    "F_normal":   "Sağlıklı yetişkin kadın, normal hidrasyon. **Tüm karşılaştırmaların referansı.**",
    "M_normal":   "Sağlıklı yetişkin erkek. Cinsiyet farkı analizleri için referans.",
    "F_diab_mod": "Orta dereceli diyabet. PT'de glukoz yükü artar.",
    "F_HT":       "Hipertansiyon. Tubuler basınç ve renal kan akımı baseline'dan sapar.",
    "F_SGLT2":    "Gliflozin. PT'de glukoz reabsorpsiyonu bloke; natriürez beklenir.",
    "M_SGLT2":    "Gliflozin, erkek. F_SGLT2 ile cinsiyet × ilaç karşılaştırması.",
}

# ============================================================
#  Sayfa kurulumu (her sayfa cagirir)
# ============================================================
def setup_page(page_title, page_icon="◐"):
    st.set_page_config(
        page_title=f"{page_title} · Nefron Veri Gezgini",
        page_icon=page_icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    # Plotly tema
    if "nefron" not in pio.templates:
        pio.templates["nefron"] = pio.templates["simple_white"]
        pio.templates["nefron"].layout.update(
            font=dict(family="Inter, system-ui, -apple-system, sans-serif", size=13, color="#1f2937"),
            title=dict(font=dict(size=15, color="#111827")),
            colorway=["#2563eb", "#dc2626", "#059669", "#d97706", "#7c3aed", "#0891b2", "#be185d"],
            hoverlabel=dict(bgcolor="white", bordercolor="#e5e7eb", font=dict(size=12)),
            margin=dict(l=50, r=20, t=50, b=50),
            xaxis=dict(gridcolor="#f3f4f6", zerolinecolor="#e5e7eb"),
            yaxis=dict(gridcolor="#f3f4f6", zerolinecolor="#e5e7eb"),
        )
    pio.templates.default = "nefron"
    # Global CSS
    st.markdown("""
    <style>
      .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }
      h1, h2, h3 { letter-spacing: -0.01em; }
      div[data-testid="stMetricValue"] { font-size: 1.35rem; }
      div[data-testid="stMetricLabel"] { font-size: 0.82rem; color: #4b5563; }
      hr { margin: 1rem 0; border-color: #e5e7eb; }
      .cite-footer { font-size:0.78rem; color:#6b7280; padding-top:0.4rem;
                     border-top:1px solid #f3f4f6; margin-top:0.5rem; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
#  Sorgu helper (cache'li)
# ============================================================
@st.cache_data
def q(sql, params=None):
    return duckdb.connect().execute(sql, params or []).df()

def scalar(sql, senaryo, params=None):
    """condition filtresini otomatik ekler, tek deger dondurur."""
    if "condition=" not in sql:
        sql = sql.replace("WHERE ", f"WHERE condition='{senaryo}' AND ", 1)
    r = q(sql, params or [])
    return None if r.empty else float(r["value"].iloc[0])

# ============================================================
#  Yardimcilar
# ============================================================
def neph_for(segment, requested):
    return "merged" if segment in CD_SEGMENTS else requested

@st.cache_data
def secenekler():
    seg = q(f"SELECT DISTINCT segment FROM {DB}")["segment"].tolist()
    sol = q(f"SELECT DISTINCT solute FROM {DB} WHERE solute IS NOT NULL")["solute"].tolist()
    return sorted(seg), sorted(sol)

@st.cache_data
def saglik_metrikleri():
    return q(f"""
        SELECT COUNT(*) AS satir, COUNT(DISTINCT segment) AS segment,
               (SELECT COUNT(DISTINCT solute) FROM {DB} WHERE solute IS NOT NULL) AS solut,
               COUNT(DISTINCT variable) AS degisken,
               COUNT(DISTINCT nephron) AS nefron,
               COUNT(DISTINCT condition) AS senaryo_sayisi
        FROM {DB}
    """).iloc[0]

@st.cache_data
def senaryo_listesi():
    return q(f"SELECT DISTINCT condition FROM {DB} ORDER BY condition")["condition"].tolist()

# Fiziksel olarak negatif olamayan degiskenler (yakinsama hatasi tespiti icin)
NONNEG_VARS = {"con", "osmolality", "water_volume"}

@st.cache_data
def butunluk_haritasi():
    """Hangi (senaryo -> segment kumesi) sayisal olarak yakinsamadi?
    Gosterge: NaN deger veya negatif Lumen osmolalitesi (solut toplami negatif olamaz).
    Modelin Newton cozucusu bazi senaryolarda toplayici kanalda coker (bkz. bulgular.md #0)."""
    df = q(f"""
        SELECT condition, segment,
            SUM(CASE WHEN value IS NULL OR isnan(value) THEN 1 ELSE 0 END) AS nan,
            SUM(CASE WHEN variable='osmolality' AND compartment='Lumen' AND value < -1
                     THEN 1 ELSE 0 END) AS neg_osm
        FROM {DB} GROUP BY condition, segment
    """)
    bozuk = {}
    for _, r in df.iterrows():
        if r["nan"] > 0 or r["neg_osm"] > 0:
            bozuk.setdefault(r["condition"], set()).add(r["segment"])
    return bozuk

def gecerli_veri(df, variable, value_col="value"):
    """Fiziksel olarak imkansiz satirlari (NaN; non-neg degiskenlerde negatif) ayiklar.
    Yakinsamayan senaryolarda cop egrilerin cizilmesini onler (evrensel emniyet agi).
    Dondurur: (temiz_df, atilan_satir_sayisi)."""
    n0 = len(df)
    mask = df[value_col].notna()
    if variable in NONNEG_VARS:
        mask = mask & (df[value_col] >= -1e-9)
    temiz = df[mask]
    return temiz, n0 - len(temiz)

def segment_bozuk_mu(senaryo, segment):
    """Bu (senaryo, segment) sayisal olarak yakinsamadi mi? True ise tum segment gizlenir
    (kesik/yaniltici egri birakmamak icin). Cozum sonlara dogru cokse bile guvenmeyiz."""
    return segment in butunluk_haritasi().get(senaryo, set())

# ============================================================
#  Sidebar (her sayfa cagirir)
# ============================================================
def render_sidebar():
    senaryolar = senaryo_listesi()
    with st.sidebar:
        st.markdown("### Nefron Veri Gezgini")
        st.caption("Layton/Hu modeli — interaktif veri arayüzü")

        senaryo = st.selectbox(
            "Aktif senaryo",
            senaryolar,
            format_func=lambda s: SENARYO_AD.get(s, s),
            index=senaryolar.index("F_normal") if "F_normal" in senaryolar else 0,
            key="senaryo_secimi_sidebar",
            help="Bu sayfanın grafikleri/sorguları seçilen senaryoya göre filtrelenir.",
        )
        detay = SENARYO_DETAY.get(senaryo, "")
        if detay:
            st.markdown(
                f"<div style='background:#eff6ff;border:1px solid #bfdbfe;padding:8px 12px;"
                f"border-radius:6px;font-size:0.82rem;color:#1e3a8a;'>{detay}</div>",
                unsafe_allow_html=True,
            )
        st.caption(f"Kod: `{senaryo}` · {len(senaryolar)} senaryolu kütüphane")

        bozuk = butunluk_haritasi()
        if senaryo in bozuk:
            segs = ", ".join(sorted(bozuk[senaryo]))
            st.warning(
                f"**Veri uyarısı:** Bu senaryonun **{segs}** segment(ler)i sayısal olarak "
                f"yakınsamadı (toplayıcı kanal). Bu segmentlerin verisi geçersizdir ve "
                f"grafiklerde gizlenir. Proksimal–DCT arası güvenilir. Detay: Veri Bütünlüğü."
            )

        st.markdown("---")
        sb = saglik_metrikleri()
        c1, c2 = st.columns(2)
        c1.metric("Bu senaryo", f"{sb['satir'] // max(sb['senaryo_sayisi'],1):,} satır")
        c2.metric("Kütüphane", f"{sb['senaryo_sayisi']} senaryo")
        st.caption(
            f"Model yapısı: **{sb['segment']}** segment · **{sb['solut']}** solüt · "
            f"**{sb['nefron']}** nefron · **{sb['degisken']}** değişken"
        )

        st.markdown("---")
        with st.expander("Veri kaynağı & atıf"):
            st.markdown(
                "**Model:** Layton/Hu (`mstadt/nephron`)\n\n"
                "**Atıf:** Hu R., et al. (2021). *Sex differences in solute and water "
                "handling in the human kidney.* iScience 24(6):102694. "
                "[doi:10.1016/j.isci.2021.102694](https://doi.org/10.1016/j.isci.2021.102694)\n\n"
                "**Bu proje:** Zor, İ. (2026). *Nefron Veri Gezgini.* Zenodo. "
                "[doi:10.5281/zenodo.20489610](https://doi.org/10.5281/zenodo.20489610)"
            )
        with st.expander("Birimler"):
            st.markdown(
                "Konsantrasyon: **mM** · Akı: **pmol/min** · Hacim: **nl/min** · "
                "Ozmolalite: **mOsm** · Potansiyel: **mV**"
            )
    return senaryo

# ============================================================
#  Grafik helper
# ============================================================
def chart_yap(df, x, y, color, title, xlab, ylab, color_label="Seri",
              category_orders=None, height=460, color_map=None):
    if color_map:
        fig = px.line(df, x=x, y=y, color=color, title=title,
                      labels={x: xlab, y: ylab, color: color_label},
                      category_orders=category_orders or {},
                      color_discrete_map=color_map)
    else:
        fig = px.line(df, x=x, y=y, color=color, title=title,
                      labels={x: xlab, y: ylab, color: color_label},
                      category_orders=category_orders or {})
    fig.update_layout(hovermode="x unified", height=height,
                      legend=dict(title_text=color_label))
    fig.update_traces(line=dict(width=2.5))
    return fig

# ============================================================
#  Atif footer (her grafiğin altina)
# ============================================================
def cite_footer():
    st.markdown(
        "<div class='cite-footer'>"
        "<b>Kaynak:</b> Hu et al. 2021, <i>iScience</i> 24:102694 &nbsp;·&nbsp; "
        "<b>Bu araç:</b> Zor 2026, "
        "<a href='https://doi.org/10.5281/zenodo.20489610' target='_blank' "
        "style='color:#1e40af;text-decoration:none;'>doi:10.5281/zenodo.20489610</a> &nbsp;·&nbsp; "
        "<b>Birimler:</b> konsantrasyon mM, hacim nl/min, ozmolalite mOsm"
        "</div>",
        unsafe_allow_html=True,
    )

# ============================================================
#  Kaynak / atif sistemi (akademik referans kartlari)
# ============================================================
# KURAL: Buraya YALNIZ gercek, kunyesi/DOI'si dogrulanmis kaynaklar girer
# (CITATION.cff ile tutarli). Uydurma atif/DOI/baslik KESINLIKLE yok.
# Birincil klinik literatur (RCT, KDIGO vb.) ancak cift-dogrulama sonrasi eklenir.
# NOT: Türkmen 2024 (ders kitabi) kasten burada DEGIL — ona atif kullanicinin kendi
# notlarinda, kendi cumleleriyle yapilir (kitaba erisim yalniz onda).
KAYNAKLAR = {
    "hu2021": {
        "tip": "Makale",
        "yazarlar": "Hu R., Layton A.T.",
        "yil": 2021,
        "baslik": "Sex differences in solute and water handling in the human kidney: "
                  "Modeling and functional implications",
        "kaynak": "iScience 24(6):102694",
        "doi": "10.1016/j.isci.2021.102694",
        "not": "Bu uygulamadaki tüm verinin türetildiği matematik model (birincil kaynak).",
    },
    "model_stadt": {
        "tip": "Yazılım",
        "yazarlar": "Stadt M., Layton A.T.",
        "yil": None,
        "baslik": "nephron — matematik model uygulaması",
        "kaynak": "github.com/mstadt/nephron",
        "url": "https://github.com/mstadt/nephron",
        "not": "Senaryoların üretildiği açık kaynak model kodu.",
    },
    # --- Klinik literatur (PubMed; kullanici 2026-06'da dogruladi) ---
    "vallon2022": {
        "tip": "Makale",
        "yazarlar": "Vallon V.",
        "yil": 2022,
        "baslik": "Renoprotective Effects of SGLT2 Inhibitors",
        "kaynak": "Heart Failure Clinics 18(4):539-549",
        "doi": "10.1016/j.hfc.2022.03.005",
        "not": "SGLT2i'nin TGF restorasyonu ve nefroprotektif mekanizmasının mekanistik incelemesi.",
    },
    "upadhyay2024": {
        "tip": "Makale",
        "yazarlar": "Upadhyay A.",
        "yil": 2024,
        "baslik": "SGLT2 Inhibitors and Kidney Protection: Mechanisms Beyond Tubuloglomerular Feedback",
        "kaynak": "Kidney360 5(5):771-782",
        "doi": "10.34067/KID.0000000000000425",
        "not": "TGF ve ötesi nefroprotektif mekanizmalar (güncel inceleme).",
    },
    "empakidney2023": {
        "tip": "RCT",
        "yazarlar": "EMPA-KIDNEY Collaborative Group (Herrington WG, Staplin N, ve ark.)",
        "yil": 2023,
        "baslik": "Empagliflozin in Patients with Chronic Kidney Disease",
        "kaynak": "N Engl J Med 388(2):117-127 (online 2022)",
        "doi": "10.1056/NEJMoa2204233",
        "not": "Landmark randomize çalışma: empagliflozinin renal sonuçlara klinik etkisi.",
    },
    "vallon_thomson2020": {
        "tip": "Makale",
        "yazarlar": "Vallon V., Thomson S.C.",
        "yil": 2020,
        "baslik": "The tubular hypothesis of nephron filtration and diabetic kidney disease",
        "kaynak": "Nature Reviews Nephrology 16(6):317-336",
        "doi": "10.1038/s41581-020-0256-y",
        "not": "Diyabetik hiperfiltrasyonun tübüler hipotezinin referans incelemesi.",
    },
    "ivy_bailey2014": {
        "tip": "Makale",
        "yazarlar": "Ivy J.R., Bailey M.A.",
        "yil": 2014,
        "baslik": "Pressure natriuresis and the renal control of arterial blood pressure",
        "kaynak": "The Journal of Physiology 592(18):3955-3967",
        "doi": "10.1113/jphysiol.2014.271676",
        "not": "Basınç natriürezi ve renal kan basıncı kontrolünün yetkili incelemesi.",
    },
    "kdigo2022diabetes": {
        "tip": "Kılavuz",
        "yazarlar": "KDIGO Diabetes Work Group",
        "yil": 2022,
        "baslik": "KDIGO 2022 Clinical Practice Guideline for Diabetes Management in Chronic Kidney Disease",
        "kaynak": "Kidney International 102(5S):S1-S127",
        "doi": "10.1016/j.kint.2022.06.008",
        "not": "Diyabet + KBH'de SGLT2i, RAS blokajı ve glisemik yönetim için klinik kılavuz.",
    },
    # --- Faz 27: Vaka 2-3 doz kaynakları ---
    "kdigo2021bp": {
        "tip": "Kılavuz",
        "yazarlar": "KDIGO Blood Pressure Work Group (Cheung AK, Chang TI, ve ark.)",
        "yil": 2021,
        "baslik": "KDIGO 2021 Clinical Practice Guideline for the Management of Blood Pressure "
                  "in Chronic Kidney Disease",
        "kaynak": "Kidney International 99(3S):S1-S87",
        "doi": "10.1016/j.kint.2020.11.003",
        "not": "KBH'de kan basıncı yönetimi: hedef <120 mmHg sistolik, ACEi/ARB albüminüride "
              "birinci basamak, tolere edilen en yüksek onaylı doza titre edilmeli.",
    },
    "agarwal2021click": {
        "tip": "RCT",
        "yazarlar": "Agarwal R., Sinha A.D., Cramer A.E., ve ark.",
        "yil": 2021,
        "baslik": "Chlorthalidone for Hypertension in Advanced Chronic Kidney Disease",
        "kaynak": "N Engl J Med 385(27):2507-2519",
        "doi": "10.1056/NEJMoa2110730",
        "not": "CLICK çalışması: klortalidone ileri KBH'de (eGFR <30) etkili kan basıncı düşüşü sağladı.",
    },
}

def kaynak_karti(ref):
    """Tek bir referansi akademik bir bilgi kutusu olarak render eder."""
    yil = f" ({ref['yil']})" if ref.get("yil") else ""
    alt_satir = [s for s in (ref.get("kaynak"), (f"ISBN {ref['isbn']}" if ref.get("isbn") else None)) if s]
    if ref.get("doi"):
        link = (f"<a href='https://doi.org/{ref['doi']}' target='_blank' "
                f"style='color:#1e40af;text-decoration:none;'>doi:{ref['doi']}</a>")
    elif ref.get("url"):
        link = (f"<a href='{ref['url']}' target='_blank' "
                f"style='color:#1e40af;text-decoration:none;'>{ref['url']}</a>")
    else:
        link = ""
    st.markdown(
        "<div style='border:1px solid #e5e7eb;border-left:3px solid #1e3a8a;"
        "background:#f8fafc;border-radius:6px;padding:10px 14px;margin:6px 0;font-size:0.84rem;'>"
        "<span style='display:inline-block;background:#1e3a8a;color:white;font-size:0.66rem;"
        f"padding:1px 8px;border-radius:10px;letter-spacing:0.03em;'>{ref.get('tip','Kaynak')}</span> "
        f"<b style='color:#111827;'>{ref.get('yazarlar','')}{yil}.</b> {ref.get('baslik','')}. "
        f"<i style='color:#4b5563;'>{' · '.join(alt_satir)}</i>"
        + (f"<br>{link}" if link else "")
        + (f"<div style='color:#6b7280;font-size:0.78rem;margin-top:4px;'>{ref['not']}</div>"
           if ref.get("not") else "")
        + "</div>",
        unsafe_allow_html=True,
    )

def kaynaklar_kutusu(anahtarlar, baslik="Kaynaklar", ek_not=None, acik=False):
    """Verilen kaynak anahtarlari icin akademik 'Kaynaklar' bolumu (expander).
    Tanimsiz anahtari sessizce atlar — asla uydurma kart cizmez."""
    with st.expander(baslik, expanded=acik):
        for k in anahtarlar:
            ref = KAYNAKLAR.get(k)
            if ref:
                kaynak_karti(ref)
        if ek_not:
            st.caption(ek_not)
