"""
app.py — Nefron Veri Gezgini · Anasayfa

Streamlit multi-page mimaride ana dosya. Soldaki sayfa menusunden alt sayfalara gecilir.
"""
import streamlit as st
import plotly.express as px

from ui_kit import setup_page, render_sidebar, q, DB

setup_page("Anasayfa")
senaryo = render_sidebar()

# ============================================================
#  Baslik + atif kart
# ============================================================
st.markdown(
    "<h1 style='margin-bottom:0.2rem;letter-spacing:-0.02em;'>Nefron Veri Gezgini</h1>"
    "<div style='color:#6b7280;font-size:1.02rem;margin-bottom:1.2rem;'>"
    "İnsan nefronu epitelyal transport modelinin interaktif veri gezgini"
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("""
<div style="background:#f9fafb;border:1px solid #e5e7eb;border-left:4px solid #1e40af;
            border-radius:6px;padding:14px 18px;margin:0.5rem 0 1.5rem 0;">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
    <div>
      <div style="font-size:0.74rem;color:#6b7280;text-transform:uppercase;
                  letter-spacing:0.08em;font-weight:600;">
        Atıf yapılabilir bilim aracı
      </div>
      <div style="font-weight:500;color:#1f2937;font-size:1rem;margin-top:4px;
                  font-family:Georgia,serif;">
        Zor, İ. (2026). Nefron Veri Gezgini. <i>Zenodo</i>.
      </div>
    </div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;">
      <a href="https://doi.org/10.5281/zenodo.20489610" target="_blank"
         style="background:#1e40af;color:white;padding:5px 11px;border-radius:4px;
                font-size:0.78rem;text-decoration:none;font-weight:500;
                font-family:ui-monospace,SFMono-Regular,monospace;">
        DOI 10.5281/zenodo.20489610
      </a>
      <a href="https://github.com/ibrahim00zor/nefron-veri-gezgini" target="_blank"
         style="background:#374151;color:white;padding:5px 11px;border-radius:4px;
                font-size:0.78rem;text-decoration:none;font-weight:500;">
        GitHub
      </a>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
#  Tanitim
# ============================================================
st.markdown("#### Bu araç ne yapar")
st.markdown(
    "Layton/Hu insan nefron modelinin (Hu et al. 2021, *iScience*) çıktılarını "
    "**6 senaryo** için &mdash; sağlıklı kadın ve erkek, orta diyabet, hipertansiyon, "
    "SGLT2 inhibitörü (♀ ve ♂) &mdash; interaktif olarak görselleştirir. "
    "Her segment boyunca konsantrasyon profilini çıkarır, kütle ve hacim ayrıştırması "
    "yapar, fizyolojik yorumu otomatik üretir."
)
st.markdown("")

# ============================================================
#  Ornek sorular
# ============================================================
st.markdown("#### Örnek sorular")
st.caption("Aşağıdaki üç kartın her biri bir araştırma sorusunu somut grafikle temsil eder. "
           "Detaylı analiz için sol menüden ilgili sayfaya geç.")

q1, q2, q3 = st.columns(3)

# Kart 1: Cinsiyet farki
with q1:
    df = q(
        f"""SELECT position, value, condition AS seri FROM {DB}
            WHERE variable='con' AND solute='Na' AND segment='mTAL'
                  AND compartment='Lumen' AND nephron='sup'
                  AND condition IN ('F_normal','M_normal')
            ORDER BY condition, position""",
        [],
    )
    df["seri"] = df["seri"].map({"F_normal": "♀", "M_normal": "♂"})
    fig = px.line(df, x="position", y="value", color="seri", height=170,
                  color_discrete_map={"♀": "#dc2626", "♂": "#1e40af"})
    fig.update_layout(margin=dict(l=10, r=10, t=5, b=5),
                      legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center",
                                  title_text=""),
                      xaxis_title=None, yaxis_title=None)
    fig.update_traces(line=dict(width=2.2))
    st.markdown(
        "<div style='border-left:3px solid #dc2626;padding-left:10px;margin-bottom:4px;'>"
        "<b>Cinsiyet farkı</b><br>"
        "<span style='color:#6b7280;font-size:0.85rem;'>mTAL lümen Na &mdash; ♀ vs ♂</span>"
        "</div>", unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("→ Detay: **Nefron Tipleri** veya **Karşılaştırma**")

# Kart 2: Diyabet
with q2:
    df = q(
        f"""SELECT position, value, condition AS seri FROM {DB}
            WHERE variable='con' AND solute='glu' AND segment='PT'
                  AND compartment='Lumen' AND nephron='sup'
                  AND condition IN ('F_normal','F_diab_mod')
            ORDER BY condition, position""",
        [],
    )
    df["seri"] = df["seri"].map({"F_normal": "Normal", "F_diab_mod": "Diyabet"})
    fig = px.line(df, x="position", y="value", color="seri", height=170,
                  color_discrete_map={"Normal": "#059669", "Diyabet": "#d97706"})
    fig.update_layout(margin=dict(l=10, r=10, t=5, b=5),
                      legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center",
                                  title_text=""),
                      xaxis_title=None, yaxis_title=None)
    fig.update_traces(line=dict(width=2.2))
    st.markdown(
        "<div style='border-left:3px solid #d97706;padding-left:10px;margin-bottom:4px;'>"
        "<b>Diyabet etkisi</b><br>"
        "<span style='color:#6b7280;font-size:0.85rem;'>PT lümen glukoz &mdash; normal vs diyabet</span>"
        "</div>", unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("→ Detay: **Karşılaştırma**")

# Kart 3: Medulla gradyani
with q3:
    df = q(
        f"""SELECT position, value, segment FROM {DB}
            WHERE variable='osmolality' AND compartment='Bath' AND nephron='merged'
                  AND condition='F_normal' AND segment IN ('CCD','OMCD','IMCD')
            ORDER BY segment, position""",
        [],
    )
    fig = px.line(df, x="position", y="value", color="segment", height=170,
                  category_orders={"segment": ["CCD", "OMCD", "IMCD"]})
    fig.update_layout(margin=dict(l=10, r=10, t=5, b=5),
                      legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center",
                                  title_text=""),
                      xaxis_title=None, yaxis_title=None)
    fig.update_traces(line=dict(width=2.2))
    st.markdown(
        "<div style='border-left:3px solid #1e40af;padding-left:10px;margin-bottom:4px;'>"
        "<b>Medüller gradyan</b><br>"
        "<span style='color:#6b7280;font-size:0.85rem;'>İnterstisyum osmolalite, CCD → IMCD</span>"
        "</div>", unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("→ Detay: **Tüm Nefron**")

# ============================================================
#  Kullanim klavuzu
# ============================================================
st.markdown("---")
st.markdown("#### Nasıl kullanılır")
st.markdown("""
1. **Sol panelden** *Aktif senaryo* seç (varsayılan: sağlıklı kadın). Sayfa değiştirsen bile seçim korunur.
2. **Sol menüden sayfa** seç:
   - **Segment Profili** — tek segmentte tek solüt, Lumen+Bath bindirme, otomatik kütle/hacim yorumu
   - **Tüm Nefron** — PT → IMCD zincirli akış grafiği
   - **Nefron Tipleri** — sup ve jux1–5 (derinliğin etkisi)
   - **Karşılaştırma** — birden çok senaryoyu üst üste (örn. normal vs diyabet)
   - **Doğrulamalar** — modelin ders kitabıyla uyumu otomatik test
   - **Veri Bütünlüğü** — kategoriler, bilinen sınırlar
3. Her grafiğin altında atıf bilgisi (kaynak + DOI) hazır.
""")

# ============================================================
#  Sinirlar
# ============================================================
st.markdown("---")
st.markdown("#### Bilinen sınırlar")
c1, c2 = st.columns(2)
with c1:
    st.markdown(
        "<div style='border:1px solid #e5e7eb;border-left:3px solid #6b7280;"
        "padding:10px 14px;border-radius:4px;'>"
        "<b style='color:#374151;'>Model sınırı</b><br>"
        "<span style='color:#4b5563;font-size:0.92rem;'>"
        "İç medulla osmotik gradyanı ~734 mOsm; literatür ~1200 mOsm (maks ADH). "
        "İç medulla konsantrasyon mekanizması matematiksel modellerce "
        "<b>tam üretilemiyor</b> — açık problem.</span>"
        "</div>", unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        "<div style='border:1px solid #e5e7eb;border-left:3px solid #6b7280;"
        "padding:10px 14px;border-radius:4px;'>"
        "<b style='color:#374151;'>Senaryo kütüphanesi</b><br>"
        "<span style='color:#4b5563;font-size:0.92rem;'>"
        "6 senaryo başarılı (10 hedeflenmişti). 4 senaryo Newton overflow ile "
        "yakınsamadı: F_diab_severe, F_ACE, F_obese, F_UNX. "
        "Modelin <b>sayısal sınırı</b>.</span>"
        "</div>", unsafe_allow_html=True,
    )

# ============================================================
#  Footer
# ============================================================
st.markdown("---")
st.caption(
    "Model: Hu R., et al. (2021). *Sex differences in solute and water handling in "
    "the human kidney.* iScience 24(6):102694. &nbsp;·&nbsp; "
    "Bu araç: Zor İ. (2026). *Nefron Veri Gezgini.* Zenodo. "
    "doi:10.5281/zenodo.20489610 &nbsp;·&nbsp; "
    "Lisans: MIT (kod) + CC-BY 4.0 (içerik)"
)
