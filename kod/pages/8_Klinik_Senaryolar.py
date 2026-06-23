"""
8_Klinik_Senaryolar.py — Faz 5: Hekim Eğitici Aracı
Bu sayfa, model ciktilarini "Vaka Analizi" formatiyla, hekimler ve
tip ogrencileri icin hikayelestirerek sunar.

BILIM-DENETIMI NOTU (Faz 25 duzeltmesi):
- "Yuk / emilim / distal iletim" anlatiminda KONSANTRASYON degil AKI (flow, pmol/min)
  cizilir. Altin kural (segment_atlasi.md): emilim/sekresyon icin daima KUTLE.
- Makula densa anatomik olarak TAL'in KORTIKAL ucundadir (cTAL cikisi), mTAL'de degil.
- Metindeki sayisal iddialar elle yazilmaz; asagidaki yardimcilarla VERIDEN hesaplanir.
"""
import streamlit as st
import plotly.express as px
from ui_kit import (
    setup_page, render_sidebar, q, DB, cite_footer
)

setup_page("Klinik Senaryolar")
# Sidebar'daki senaryo secimi bu sayfada override edilecek, o yuzden degiskeni tutmuyoruz.
render_sidebar()

st.markdown("## Eğitim Araç Kutusu: Klinik Vakalar")
st.caption(
    "Bu sayfa, Layton insan nefron modelinin (Hu et al. 2021) çıktılarını kullanarak "
    "belirli patolojik durumların ve farmakolojik müdahalelerin fizyolojik mekanizmalarını açıklar."
)
st.markdown("---")

vaka_secimi = st.selectbox(
    "İncelenecek Klinik Vakayı Seçin",
    [
        "Vaka 1: SGLT2 İnhibitörlerinin (Gliflozinler) Etki Mekanizması",
        "Vaka 2: Diyabetin Hemodinamik Yükü ve Tübüler Hipertrofi",
        "Vaka 3: Hipertansiyonda Tübüler Sodyum Yükü"
    ]
)


# Helper function for quick line charts
def plot_case_metric(df, x_col, y_col, color_col, title, y_title, colors):
    fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title,
                  color_discrete_map=colors)
    fig.update_layout(hovermode="x unified", height=350, margin=dict(l=10, r=10, t=40, b=10))
    fig.update_traces(line=dict(width=3))
    return fig


# --- Veriden dinamik deger okuyucular (metindeki sayilar elle yazilmasin) ---
# df, "condition" kolonuna gore filtrelenir; satirlar position'a gore artan sirali
# oldugundan ilk satir = giris, son satir = cikis.
def _giris(df, etiket):
    s = df.loc[df["condition"] == etiket, "value"]
    return float(s.iloc[0]) if len(s) else float("nan")

def _cikis(df, etiket):
    s = df.loc[df["condition"] == etiket, "value"]
    return float(s.iloc[-1]) if len(s) else float("nan")

def _emilen(df, etiket):
    """Geri emilen kutle = giris akisi - cikis akisi (flow degiskeni icin anlamli)."""
    s = df.loc[df["condition"] == etiket, "value"]
    return float(s.iloc[0] - s.iloc[-1]) if len(s) else float("nan")

def _yuzde(yeni, baz):
    return 100.0 * (yeni - baz) / baz if baz else float("nan")

# ==========================================================
# VAKA 1: SGLT2 İnhibisyonu
# ==========================================================
if "SGLT2" in vaka_secimi:
    st.markdown("### Vaka 1: SGLT2 İnhibisyonu ve TGF Restorasyonu")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        **Fizyolojik Bağlam (Türkmen, 2024):**
        SGLT2 inhibitörleri (Gliflozinler), proksimal tübülde glukoz ve sodyumun geri emilimini bloke eder.
        Beklenen ilk etki olan **glukozüri** (idrarda şeker) haricinde, asıl nefroprotektif etki **Tübüloglomerüler Geribildirim (TGF)** üzerinden gerçekleşir.

        Proksimalde emilemeyen sodyum distale taşar ve *Makula Densa*'ya — yani kalın çıkan kolun **kortikal ucuna (cTAL çıkışı)** — ulaşır. Makula Densa'daki artmış NaCl sinyali, afferent arteriyolde vazokonstriksiyona neden olarak glomerüler içi basıncı düşürür ve **hiperfiltrasyonu** önler.
        """)
    with col2:
        st.info("**Hedeflenen Karşılaştırma:**\n\nSağlıklı Kadın (`F_normal`) vs SGLT2 İnhibisyonu (`F_SGLT2`)")

    st.markdown("#### 1. Proksimal Tübülde Glukoz Atılımı")
    # Glukoz konsantrasyonu PT boyunca
    df_glu = q(f"""
        SELECT position, value, condition
        FROM {DB}
        WHERE condition IN ('F_normal', 'F_SGLT2')
          AND variable='con' AND solute='glu' AND segment='PT' AND compartment='Lumen' AND nephron='sup'
        ORDER BY condition, position
    """)
    df_glu["condition"] = df_glu["condition"].map({"F_normal": "Normal", "F_SGLT2": "SGLT2 İnhibisyonu"})

    st.plotly_chart(
        plot_case_metric(df_glu, "position", "value", "condition", "PT Lümen Glukoz Konsantrasyonu (mM)", "Glukoz (mM)",
                         {"Normal": "#dc2626", "SGLT2 İnhibisyonu": "#be185d"}),
        use_container_width=True
    )
    st.caption("SGLT2 inhibisyonunda glukoz proksimal tübülde emilemez ve konsantrasyon hızla artar (Ozmotik diüreze katkı).")

    st.markdown("#### 2. Makula Densa'ya (cTAL Çıkışı) Gelen Sodyum")
    st.caption(
        "Makula densa, kalın çıkan kolun **kortikal** ucunda (cTAL çıkışı, pozisyon 1.0) yer alır — "
        "kendi glomerülünün vasküler kutbuna komşu. NKCC2 taşıyıcısı buradaki lümen NaCl "
        "**konsantrasyonunu** algılar; ulaşan toplam sodyum ise **yük (akı)** ile ölçülür. "
        "Her ikisini de gösteriyoruz."
    )

    cmap1 = {"Normal": "#dc2626", "SGLT2 İnhibisyonu": "#be185d"}
    # cTAL Na konsantrasyonu (makula densa NKCC2 sensoru)
    df_na_con = q(f"""
        SELECT position, value, condition
        FROM {DB}
        WHERE condition IN ('F_normal', 'F_SGLT2')
          AND variable='con' AND solute='Na' AND segment='cTAL' AND compartment='Lumen' AND nephron='sup'
        ORDER BY condition, position
    """)
    df_na_con["condition"] = df_na_con["condition"].map({"F_normal": "Normal", "F_SGLT2": "SGLT2 İnhibisyonu"})
    # cTAL Na akisi (makula densa'ya ulasan YUK)
    df_na_flow = q(f"""
        SELECT position, value, condition
        FROM {DB}
        WHERE condition IN ('F_normal', 'F_SGLT2')
          AND variable='flow' AND solute='Na' AND segment='cTAL' AND compartment='Lumen' AND nephron='sup'
        ORDER BY condition, position
    """)
    df_na_flow["condition"] = df_na_flow["condition"].map({"F_normal": "Normal", "F_SGLT2": "SGLT2 İnhibisyonu"})

    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(
            plot_case_metric(df_na_con, "position", "value", "condition",
                             "cTAL Lümen Na+ Konsantrasyonu (NKCC2 sensörü)", "Na+ (mM)", cmap1),
            use_container_width=True
        )
    with g2:
        st.plotly_chart(
            plot_case_metric(df_na_flow, "position", "value", "condition",
                             "cTAL Lümen Na+ Akısı (makula densaya yük)", "Na+ akısı (pmol/min)", cmap1),
            use_container_width=True
        )

    # Cikis (makula densa) degerleri veriden
    con_n, con_s = _cikis(df_na_con, "Normal"), _cikis(df_na_con, "SGLT2 İnhibisyonu")
    flw_n, flw_s = _cikis(df_na_flow, "Normal"), _cikis(df_na_flow, "SGLT2 İnhibisyonu")
    st.success(
        f"""**TGF Etkisi (model verisi):**
Makula densa = cTAL çıkışı (pozisyon 1.0). SGLT2 inhibisyonunda proksimalde emilemeyen sodyum
distale taşar: makula densaya **ulaşan yük ≈ +%{_yuzde(flw_s, flw_n):.0f} artar**
(akı: {flw_n:,.0f} → {flw_s:,.0f} pmol/min). NKCC2'nin algıladığı **konsantrasyon ise ≈ +%{_yuzde(con_s, con_n):.0f}**
yükselir ({con_n:.0f} → {con_s:.0f} mM). Bu artmış NaCl sinyali afferent vazokonstriksiyon →
glomerüler basınç düşüşü → hiperfiltrasyonun frenlenmesi ile sonuçlanır."""
    )

# ==========================================================
# VAKA 2: Diyabetin Hemodinamik Yükü
# ==========================================================
elif "Diyabet" in vaka_secimi:
    st.markdown("### Vaka 2: Diyabetin Hemodinamik Yükü ve Tübüler Hipertrofi")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        **Fizyolojik Bağlam (Türkmen, 2024):**
        Erken evre diyabette, artmış filtre edilmiş glukoz yükü, proksimal tübüldeki SGLT2 taşıyıcılarının **upregülasyonuna** (aşırı çalışmasına) neden olur.
        SGLT2, glukozu sodyum ile *birlikte* emdiği için, aşırı sodyum geri emilimi gerçekleşir.
        Bunun sonucunda Makula Densa'ya giden sodyum azalır, TGF sistemi bunu "kan basıncı düşük" olarak algılayıp filtrasyon hızını (GFR) daha da artırır (**Hiperfiltrasyon**).
        """)
    with col2:
        st.info("**Hedeflenen Karşılaştırma:**\n\nSağlıklı Kadın (`F_normal`) vs Orta Diyabet (`F_diab_mod`)")

    st.markdown("#### 1. Proksimal Tübüle Giren Artmış Yük")
    df_flow_pt = q(f"""
        SELECT position, value, condition
        FROM {DB}
        WHERE condition IN ('F_normal', 'F_diab_mod')
          AND variable='water_volume' AND segment='PT' AND compartment='Lumen' AND nephron='sup'
        ORDER BY condition, position
    """)
    df_flow_pt["condition"] = df_flow_pt["condition"].map({"F_normal": "Normal", "F_diab_mod": "Diyabet"})

    st.plotly_chart(
        plot_case_metric(df_flow_pt, "position", "value", "condition", "PT Su Hacmi Akışı (nl/min)", "Hacim (nl/min)",
                         {"Normal": "#dc2626", "Diyabet": "#ea580c"}),
        use_container_width=True
    )
    qg_n, qg_d = _giris(df_flow_pt, "Normal"), _giris(df_flow_pt, "Diyabet")
    st.caption(
        f"Diyabette glomerüler filtrasyon (PT giriş su akışı) daha yüksektir: "
        f"{qg_n:.0f} → {qg_d:.0f} nl/min (≈ +%{_yuzde(qg_d, qg_n):.0f}, hiperfiltrasyon)."
    )

    st.markdown("#### 2. Artmış Oksijen Talebi: Sodyum Geri Emilimi (Kütle)")
    st.caption(
        "Proksimal tübülde Na+ **konsantrasyonu** ~140 mM'de neredeyse sabittir (iso-ozmotik emilim: "
        "su, sodyumu izler). Bu yüzden emilim hikâyesi konsantrasyonda görünmez — **akıda (kütle)** "
        "görünür. Geri emilen kütle = giriş akısı − çıkış akısı."
    )
    df_na_flow_pt = q(f"""
        SELECT position, value, condition
        FROM {DB}
        WHERE condition IN ('F_normal', 'F_diab_mod')
          AND variable='flow' AND solute='Na' AND segment='PT' AND compartment='Lumen' AND nephron='sup'
        ORDER BY condition, position
    """)
    df_na_flow_pt["condition"] = df_na_flow_pt["condition"].map({"F_normal": "Normal", "F_diab_mod": "Diyabet"})

    st.plotly_chart(
        plot_case_metric(df_na_flow_pt, "position", "value", "condition", "PT Lümen Na+ Akısı (yük)", "Na+ akısı (pmol/min)",
                         {"Normal": "#dc2626", "Diyabet": "#ea580c"}),
        use_container_width=True
    )
    reab_n, reab_d = _emilen(df_na_flow_pt, "Normal"), _emilen(df_na_flow_pt, "Diyabet")
    st.warning(
        f"""**Hipertrofi Sinyali (kütle):**
Diyabette glomerüler yük arttığı için PT'ye daha çok Na+ girer ve daha çoğu geri emilir:
geri emilen Na+ kütlesi Normal **{reab_n:,.0f}** → Diyabet **{reab_d:,.0f} pmol/min**
(≈ +%{_yuzde(reab_d, reab_n):.0f}). Na-K-ATPaz'ın bu fazla mesaisi oksijen tüketimini ve hipoksi riskini artırır.
(Aynı veriye konsantrasyonla bakılsaydı iki eğri neredeyse üst üste düşer ve bu etki görünmezdi.)"""
    )

# ==========================================================
# VAKA 3: Hipertansiyon
# ==========================================================
elif "Hipertansiyon" in vaka_secimi:
    st.markdown("### Vaka 3: Hipertansiyonda Tübüler Sodyum Yükü")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        **Fizyolojik Bağlam (Türkmen, 2024):**
        Sistemik hipertansiyon, böbreğe gelen perfüzyon basıncını artırır (Basınç natriürezi).
        Proksimal tübül gibi bölgelerde fraksiyonel sodyum geri emilimi düşebilir; bu da daha distal segmentlerin (özellikle TAL) sodyum ile başa çıkma kapasitesini sınar.
        """)
    with col2:
        st.info("**Hedeflenen Karşılaştırma:**\n\nSağlıklı Kadın (`F_normal`) vs Hipertansiyon (`F_HT`)")

    st.markdown("#### Kalın Çıkan Kol (TAL) Sodyum Yönetimi")
    st.caption(
        "Sol: lümen konsantrasyonu. Sağ: lümen akısı (distale iletilen sodyum yükü). "
        "Distal iletimin değişimi konsantrasyonda değil, asıl **akıda** okunur."
    )

    cmap3 = {"Normal": "#dc2626", "Hipertansiyon": "#a16207"}
    df_na_con_tal = q(f"""
        SELECT position, value, condition
        FROM {DB}
        WHERE condition IN ('F_normal', 'F_HT')
          AND variable='con' AND solute='Na' AND segment='mTAL' AND compartment='Lumen' AND nephron='sup'
        ORDER BY condition, position
    """)
    df_na_con_tal["condition"] = df_na_con_tal["condition"].map({"F_normal": "Normal", "F_HT": "Hipertansiyon"})
    df_na_flow_tal = q(f"""
        SELECT position, value, condition
        FROM {DB}
        WHERE condition IN ('F_normal', 'F_HT')
          AND variable='flow' AND solute='Na' AND segment='mTAL' AND compartment='Lumen' AND nephron='sup'
        ORDER BY condition, position
    """)
    df_na_flow_tal["condition"] = df_na_flow_tal["condition"].map({"F_normal": "Normal", "F_HT": "Hipertansiyon"})

    h1, h2 = st.columns(2)
    with h1:
        st.plotly_chart(
            plot_case_metric(df_na_con_tal, "position", "value", "condition",
                             "mTAL Lümen Na+ Konsantrasyonu (mM)", "Na+ (mM)", cmap3),
            use_container_width=True
        )
    with h2:
        st.plotly_chart(
            plot_case_metric(df_na_flow_tal, "position", "value", "condition",
                             "mTAL Lümen Na+ Akısı (yük)", "Na+ akısı (pmol/min)", cmap3),
            use_container_width=True
        )

    cin_n, cin_h = _giris(df_na_con_tal, "Normal"), _giris(df_na_con_tal, "Hipertansiyon")
    cout_n, cout_h = _cikis(df_na_con_tal, "Normal"), _cikis(df_na_con_tal, "Hipertansiyon")
    fout_n, fout_h = _cikis(df_na_flow_tal, "Normal"), _cikis(df_na_flow_tal, "Hipertansiyon")
    st.caption(
        f"mTAL **girişinde** konsantrasyon iki senaryoda da benzerdir ({cin_n:.0f} ≈ {cin_h:.0f} mM). "
        f"**Çıkışta** ise hipertansiyonda hem konsantrasyon ({cout_n:.0f} → {cout_h:.0f} mM) hem de "
        f"daha belirleyici olarak **akı/yük** ({fout_n:,.0f} → {fout_h:,.0f} pmol/min, ≈ +%{_yuzde(fout_h, fout_n):.0f}) "
        f"daha yüksektir. Bu, distal sodyum iletiminin arttığını ve basınç natriürezinin çalıştığını gösterir."
    )

cite_footer()
