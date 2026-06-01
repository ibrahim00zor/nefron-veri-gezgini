"""
app.py — Nefron Veri Gezgini · Anasayfa

Streamlit multi-page mimaride ana dosya. Soldaki sayfa menusunden
"Segment Profili", "Tum Nefron", "Karsilastirma", "Dogrulamalar",
"Veri Butunlugu" sayfalarina gecilir.
"""
import streamlit as st
import plotly.express as px

from ui_kit import (
    setup_page, render_sidebar, q, DB,
    SENARYO_AD,
)

setup_page("Anasayfa", "🏠")
senaryo = render_sidebar()

# ============================================================
#  Baslik + DOI karti
# ============================================================
st.title("Nefron Veri Gezgini")
st.caption("İnsan nefronu epitelyal transport modelinin interaktif veri gezgini")

st.markdown("""
<div style="background:linear-gradient(90deg,#eff6ff,#f0fdf4);
            border:1px solid #c7d2fe;border-radius:10px;
            padding:14px 18px;margin:1rem 0;">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
    <div>
      <div style="font-size:0.78rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;">
        Atıf yapılabilir bilim aracı
      </div>
      <div style="font-weight:600;color:#1f2937;font-size:1.02rem;margin-top:2px;">
        Zor, İ. (2026). Nefron Veri Gezgini.
      </div>
    </div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;">
      <a href="https://doi.org/10.5281/zenodo.20489610" target="_blank"
         style="background:#1e40af;color:white;padding:6px 12px;border-radius:6px;
                font-size:0.82rem;text-decoration:none;font-weight:500;">
        DOI: 10.5281/zenodo.20489610
      </a>
      <a href="https://github.com/ibrahim00zor/nefron-veri-gezgini" target="_blank"
         style="background:#374151;color:white;padding:6px 12px;border-radius:6px;
                font-size:0.82rem;text-decoration:none;font-weight:500;">
        GitHub
      </a>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
#  Bu arac ne yapar?
# ============================================================
st.markdown("### Bu araç ne yapar?")
st.markdown(
    "Layton/Hu insan nefron modelinin (Hu et al. 2021, iScience) çıktılarını "
    "**6 senaryo** için (sağlıklı kadın/erkek, diyabet, hipertansiyon, SGLT2 inhibitörü) "
    "interaktif görselleştirir. Her segment boyunca konsantrasyon profilini çıkarır, "
    "kütle/hacim ayrıştırması yapar, fizyolojik yorumu otomatik üretir."
)

# ============================================================
#  Hizli bakis: 3 sutunlu kart
# ============================================================
st.markdown("### 🔎 Hangi soruları cevaplar — örnekler")

q1, q2, q3 = st.columns(3)

# Kart 1: Cinsiyet farkı
with q1:
    df = q(
        f"""SELECT position, value, nephron AS seri FROM {DB}
            WHERE variable='con' AND solute='Na' AND segment='mTAL'
                  AND compartment='Lumen' AND condition='F_normal' AND nephron='sup'
            UNION ALL
            SELECT position, value, 'sup (♂)' AS seri FROM {DB}
            WHERE variable='con' AND solute='Na' AND segment='mTAL'
                  AND compartment='Lumen' AND condition='M_normal' AND nephron='sup'
            ORDER BY 3, 1""",
        [],
    )
    df["seri"] = df["seri"].replace({"sup": "sup (♀)"})
    fig = px.line(df, x="position", y="value", color="seri", height=180,
                  color_discrete_map={"sup (♀)": "#dc2626", "sup (♂)": "#2563eb"})
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=True,
                      legend=dict(orientation="h", y=-0.2),
                      xaxis_title=None, yaxis_title=None)
    fig.update_traces(line=dict(width=2))
    st.markdown("**👫 Cinsiyet farkı**")
    st.caption("mTAL'da lümen Na — ♀ vs ♂")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("→ Sol menü: **Nefron Tipleri** veya **Karşılaştırma**")

# Kart 2: Diyabet etkisi
with q2:
    df = q(
        f"""SELECT position, value, condition AS seri FROM {DB}
            WHERE variable='con' AND solute='glu' AND segment='PT'
                  AND compartment='Lumen' AND nephron='sup'
                  AND condition IN ('F_normal','F_diab_mod')
            ORDER BY condition, position""",
        [],
    )
    fig = px.line(df, x="position", y="value", color="seri", height=180,
                  color_discrete_map={"F_normal": "#059669", "F_diab_mod": "#d97706"})
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10),
                      legend=dict(orientation="h", y=-0.2),
                      xaxis_title=None, yaxis_title=None)
    fig.update_traces(line=dict(width=2))
    st.markdown("**🩸 Diyabet etkisi**")
    st.caption("PT'de lümen glukozu — normal vs diyabet")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("→ **Karşılaştırma** sekmesinde detaylı")

# Kart 3: Gradyan hikayesi
with q3:
    df = q(
        f"""SELECT position, value, segment FROM {DB}
            WHERE variable='osmolality' AND compartment='Bath' AND nephron='merged'
                  AND condition='F_normal' AND segment IN ('CCD','OMCD','IMCD')
            ORDER BY segment, position""",
        [],
    )
    fig = px.line(df, x="position", y="value", color="segment", height=180,
                  category_orders={"segment": ["CCD", "OMCD", "IMCD"]})
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10),
                      legend=dict(orientation="h", y=-0.2),
                      xaxis_title=None, yaxis_title=None)
    fig.update_traces(line=dict(width=2))
    st.markdown("**🌡 Medüller gradyan**")
    st.caption("İnterstisyum osmolalitesi CCD → IMCD")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("→ **Tüm Nefron** sekmesinde uçtan uca")

# ============================================================
#  Nasil kullanilir
# ============================================================
st.markdown("---")
st.markdown("### 🧭 Nasıl kullanılır")
st.markdown("""
1. **Sol panelden** _Aktif senaryo_ seç (varsayılan: sağlıklı kadın). Sayfa değiştirsen bile seçim korunur.
2. **Sol menüden sayfa** seç:
   - **Segment Profili** — tek segmentte tek solüt, Lumen+Bath bindirme, otomatik kütle/hacim yorumu
   - **Tüm Nefron** — PT → IMCD zincirli akış grafiği
   - **Nefron Tipleri** — sup vs jux1–5 (derinliğin etkisi)
   - **Karşılaştırma** — birden çok senaryoyu üst üste (örn. normal vs diyabet)
   - **Doğrulamalar** — modelin ders kitabıyla uyumu otomatik test
   - **Veri Bütünlüğü** — kategoriler, bilinen sınırlar
3. Her grafiğin altında atıf footer'ı (kaynak + DOI) hazır — kopyala kullan.
""")

# ============================================================
#  Sinirlar (durust)
# ============================================================
st.markdown("---")
st.markdown("### ⚠️ Bilinen sınırlar (dürüstlük)")
c1, c2 = st.columns(2)
with c1:
    st.markdown("""
**Model sınırı**
- İç medulla osmotik gradyanı ~734 mOsm
- Literatür ~1200 mOsm (maks ADH)
- "İç medulla konsantrasyon mekanizması" matematiksel modellerce **tam üretilemiyor** — bilinen açık problem
""")
with c2:
    st.markdown("""
**Senaryo kütüphanesi**
- 6 senaryo (10 hedeflenmişti)
- 4 senaryo Newton overflow ile yakınsamadı: F_diab_severe, F_ACE, F_obese, F_UNX
- Bunlar **modelin sayısal sınırı**, projenin hatası değil
""")

# ============================================================
#  Footer atif
# ============================================================
st.markdown("---")
st.caption(
    "📖 Model: Hu R., et al. (2021). *Sex differences in solute and water handling in the human kidney.* "
    "iScience 24(6):102694. · "
    "Bu araç: Zor İ. (2026). Nefron Veri Gezgini. Zenodo. doi:10.5281/zenodo.20489610 · "
    "Kod: MIT · İçerik: CC-BY 4.0"
)
