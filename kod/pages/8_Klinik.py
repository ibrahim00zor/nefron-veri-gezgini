"""
8_Klinik.py — Klinik Dünya — Profesyonel Eğitim Arayüzü

Projenin "iki dünyalı" mimarisinin ikinci ayağı. Model dünyası (sayfa 1-7)
verileri inceler; bu sayfa klinik bağlam, örnek vaka ve model verisini
birleştirir.

GÜVENLIK / ÇERÇEVE:
- EGITIM amaclidir; klinik karar-destek DEGILDIR.
- Ilac/doz/mekanizma bilgisi YALNIZ dogrulanmis makaleden cekilecek.
- Klinisyen/hoca dogrulamasi beklemekte.
- Bilim-denetimi: "yuk/emilim" -> AKI (flow); makula densa = cTAL.
"""
import streamlit as st
import plotly.express as px
from ui_kit import (
    setup_page, render_sidebar, q, DB, cite_footer, kaynaklar_kutusu
)

setup_page("Klinik")
render_sidebar()

# ================================================================
# BANNER — Klinik Dünya Kimliği
# ================================================================
st.markdown(
    """<div style="
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        color: white;
        padding: 24px 28px;
        border-radius: 10px;
        margin-bottom: 16px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <div style="font-size: 1.5rem; font-weight: 700; letter-spacing: 0.02em;">
                    Klinik Egitim Arayuzu
                </div>
                <div style="font-size: 0.88rem; opacity: 0.85; margin-top: 4px;">
                    Ornek vakalar, mekanizma, ilac/doz ve model verisi — tek catida
                </div>
            </div>
            <div style="font-size: 0.78rem; opacity: 0.7; text-align: right;">
                Egitim amaclidir — tibbi tavsiye degildir
            </div>
        </div>
    </div>""",
    unsafe_allow_html=True,
)

st.warning(
    "**Egitim amaclidir — tibbi tavsiye degildir.** Buradaki grafikler bir matematik "
    "modelin (Hu et al. 2021) ciktisidir; gercek hasta verisi degildir. Tani, tedavi veya "
    "hasta bakimi karari icin kullanilamaz."
)

# ================================================================
# YARDIMCI FONKSİYONLAR
# ================================================================

def plot_case_metric(df, x_col, y_col, color_col, title, y_title, colors):
    fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title,
                  color_discrete_map=colors)
    fig.update_layout(hovermode="x unified", height=350,
                      margin=dict(l=10, r=10, t=40, b=10))
    fig.update_traces(line=dict(width=3))
    return fig


def _giris(df, etiket):
    s = df.loc[df["condition"] == etiket, "value"]
    return float(s.iloc[0]) if len(s) else float("nan")

def _cikis(df, etiket):
    s = df.loc[df["condition"] == etiket, "value"]
    return float(s.iloc[-1]) if len(s) else float("nan")

def _emilen(df, etiket):
    s = df.loc[df["condition"] == etiket, "value"]
    return float(s.iloc[0] - s.iloc[-1]) if len(s) else float("nan")

def _yuzde(yeni, baz):
    return 100.0 * (yeni - baz) / baz if baz else float("nan")


# ================================================================
# VAKA SEÇİM KARTLARI (BUTONLAR)
# ================================================================
st.markdown("### Klinik Vakalar")
st.caption("Bir vaka secin — model verileri acilir. Klinik icerik makale yuklendikten sonra doldurulacak.")

if "klinik_vaka" not in st.session_state:
    st.session_state.klinik_vaka = "SGLT2"

k1, k2, k3 = st.columns(3)

with k1:
    if st.button("SGLT2 Inhibisyonu", use_container_width=True,
                 type="primary" if st.session_state.klinik_vaka == "SGLT2" else "secondary"):
        st.session_state.klinik_vaka = "SGLT2"
        st.rerun()

with k2:
    if st.button("Diyabetik Hiperfiltrasyon", use_container_width=True,
                 type="primary" if st.session_state.klinik_vaka == "Hiperfiltrasyon" else "secondary"):
        st.session_state.klinik_vaka = "Hiperfiltrasyon"
        st.rerun()

with k3:
    if st.button("Hipertansiyon", use_container_width=True,
                 type="primary" if st.session_state.klinik_vaka == "Hipertansiyon" else "secondary"):
        st.session_state.klinik_vaka = "Hipertansiyon"
        st.rerun()

vaka = st.session_state.klinik_vaka
st.markdown("---")


# ================================================================
# VAKA 1: SGLT2 İnhibisyonu
# ================================================================
if vaka == "SGLT2":
    st.markdown("### Vaka 1: SGLT2 Inhibisyonu ve TGF Restorasyonu")
    cmap1 = {"Normal": "#dc2626", "SGLT2 Inhibisyonu": "#be185d"}

    # --- Veri sorgulari ---
    df_glu = q(f"""
        SELECT position, value, condition FROM {DB}
        WHERE condition IN ('F_normal', 'F_SGLT2')
          AND variable='con' AND solute='glu' AND segment='PT' AND compartment='Lumen' AND nephron='sup'
        ORDER BY condition, position
    """)
    df_glu["condition"] = df_glu["condition"].map({"F_normal": "Normal", "F_SGLT2": "SGLT2 Inhibisyonu"})
    df_na_con = q(f"""
        SELECT position, value, condition FROM {DB}
        WHERE condition IN ('F_normal', 'F_SGLT2')
          AND variable='con' AND solute='Na' AND segment='cTAL' AND compartment='Lumen' AND nephron='sup'
        ORDER BY condition, position
    """)
    df_na_con["condition"] = df_na_con["condition"].map({"F_normal": "Normal", "F_SGLT2": "SGLT2 Inhibisyonu"})
    df_na_flow = q(f"""
        SELECT position, value, condition FROM {DB}
        WHERE condition IN ('F_normal', 'F_SGLT2')
          AND variable='flow' AND solute='Na' AND segment='cTAL' AND compartment='Lumen' AND nephron='sup'
        ORDER BY condition, position
    """)
    df_na_flow["condition"] = df_na_flow["condition"].map({"F_normal": "Normal", "F_SGLT2": "SGLT2 Inhibisyonu"})
    con_n, con_s = _cikis(df_na_con, "Normal"), _cikis(df_na_con, "SGLT2 Inhibisyonu")
    flw_n, flw_s = _cikis(df_na_flow, "Normal"), _cikis(df_na_flow, "SGLT2 Inhibisyonu")
    glu_n, glu_s = _cikis(df_glu, "Normal"), _cikis(df_glu, "SGLT2 Inhibisyonu")

    # --- Hasta ozeti karti ---
    with st.container(border=True):
        st.markdown("##### Hasta Ozeti")
        st.info("Hasta profili ve klinik baglam makale yuklendikten sonra doldurulacak.")
        k1, k2, k3 = st.columns(3)
        k1.metric("Makula densaya Na yuku", f"{flw_s:,.0f} pmol/min",
                   f"{_yuzde(flw_s, flw_n):+.0f}%", delta_color="off")
        k2.metric("Makula densa Na konsantr.", f"{con_s:.0f} mM",
                   f"{_yuzde(con_s, con_n):+.0f}%", delta_color="off")
        k3.metric("PT glukoz cikisi", f"{glu_s:.1f} mM",
                   f"{glu_s - glu_n:+.1f} mM", delta_color="off")
        st.caption("Metrikler `F_SGLT2`'nin `F_normal`'a gore farkini verir.")

    # --- 4 Sekme ---
    t_mek, t_ilac, t_model, t_kaynak = st.tabs(
        ["Mekanizma ve Fizyoloji", "Ilac ve Doz Yaklasimi", "Model Verileri", "Kaynaklar"]
    )

    with t_mek:
        st.info("Mekanizma aciklamasi makale yuklendikten sonra doldurulacak.")

    with t_ilac:
        st.info("Ilac ve doz bilgisi makale yuklendikten sonra doldurulacak.")

    with t_model:
        st.markdown("#### 1. Proksimal tubulde glukoz atilimi")
        st.plotly_chart(
            plot_case_metric(df_glu, "position", "value", "condition",
                             "PT Lumen Glukoz Konsantrasyonu (mM)",
                             "Glukoz (mM)", cmap1),
            use_container_width=True,
        )
        st.markdown("#### 2. Makula densaya (cTAL cikisi) gelen sodyum")
        st.caption("Makula densa = kalin cikan kolun kortikal ucu (cTAL cikisi).")
        g1, g2 = st.columns(2)
        with g1:
            st.plotly_chart(
                plot_case_metric(df_na_con, "position", "value", "condition",
                                 "cTAL Lumen Na+ Konsantrasyonu", "Na+ (mM)", cmap1),
                use_container_width=True,
            )
        with g2:
            st.plotly_chart(
                plot_case_metric(df_na_flow, "position", "value", "condition",
                                 "cTAL Lumen Na+ Akisi", "Na+ akisi (pmol/min)", cmap1),
                use_container_width=True,
            )
        st.success(
            f"**Model verisi:** Makula densaya ulasan yuk = +%{_yuzde(flw_s, flw_n):.0f} "
            f"(aki: {flw_n:,.0f} -> {flw_s:,.0f} pmol/min); konsantrasyon = +%{_yuzde(con_s, con_n):.0f} "
            f"({con_n:.0f} -> {con_s:.0f} mM)."
        )
        st.markdown("---")
        st.page_link("pages/4_Karsilastirma.py",
                      label="Karsilastirma sayfasinda F_normal vs F_SGLT2 yan yana incele",
                      icon=":material/search:")

    with t_kaynak:
        kaynaklar_kutusu(
            ["hu2021"],
            baslik="Kaynaklar — Vaka 1", acik=True,
        )
        st.info("Ek kaynaklar makale yuklendikten sonra eklenecek.")


# ================================================================
# VAKA 2: Diyabetik Hiperfiltrasyon
# ================================================================
elif vaka == "Hiperfiltrasyon":
    st.markdown("### Vaka 2: Diyabetik Hiperfiltrasyon")
    cmap2 = {"Normal": "#dc2626", "Diyabet": "#ea580c"}

    df_flow_pt = q(f"""
        SELECT position, value, condition FROM {DB}
        WHERE condition IN ('F_normal', 'F_diab_mod')
          AND variable='water_volume' AND segment='PT' AND compartment='Lumen' AND nephron='sup'
        ORDER BY condition, position
    """)
    df_flow_pt["condition"] = df_flow_pt["condition"].map({"F_normal": "Normal", "F_diab_mod": "Diyabet"})
    df_na_flow_pt = q(f"""
        SELECT position, value, condition FROM {DB}
        WHERE condition IN ('F_normal', 'F_diab_mod')
          AND variable='flow' AND solute='Na' AND segment='PT' AND compartment='Lumen' AND nephron='sup'
        ORDER BY condition, position
    """)
    df_na_flow_pt["condition"] = df_na_flow_pt["condition"].map({"F_normal": "Normal", "F_diab_mod": "Diyabet"})
    qg_n, qg_d = _giris(df_flow_pt, "Normal"), _giris(df_flow_pt, "Diyabet")
    reab_n, reab_d = _emilen(df_na_flow_pt, "Normal"), _emilen(df_na_flow_pt, "Diyabet")

    # --- Hasta ozeti karti ---
    with st.container(border=True):
        st.markdown("##### Hasta Ozeti")
        st.info("Hasta profili ve klinik baglam makale yuklendikten sonra doldurulacak.")
        k1, k2 = st.columns(2)
        k1.metric("PT giris su akisi (filtrasyon)", f"{qg_d:.0f} nl/min",
                   f"{_yuzde(qg_d, qg_n):+.0f}%", delta_color="off")
        k2.metric("PT'de geri emilen Na (kutle)", f"{reab_d:,.0f} pmol/min",
                   f"{_yuzde(reab_d, reab_n):+.0f}%", delta_color="off")
        st.caption("Metrikler `F_diab_mod`'un `F_normal`'a gore farkini verir.")

    # --- 4 Sekme ---
    t_mek, t_ilac, t_model, t_kaynak = st.tabs(
        ["Mekanizma ve Fizyoloji", "Ilac ve Doz Yaklasimi", "Model Verileri", "Kaynaklar"]
    )

    with t_mek:
        st.info("Mekanizma aciklamasi makale yuklendikten sonra doldurulacak.")

    with t_ilac:
        st.info("Ilac ve doz bilgisi makale yuklendikten sonra doldurulacak.")

    with t_model:
        st.markdown("#### 1. Proksimal tubule giren artmis hacim yuku")
        st.plotly_chart(
            plot_case_metric(df_flow_pt, "position", "value", "condition",
                             "PT Su Hacmi Akisi (nl/min)",
                             "Hacim (nl/min)", cmap2),
            use_container_width=True,
        )
        st.caption(f"Diyabette PT giris su akisi: {qg_n:.0f} -> {qg_d:.0f} nl/min "
                   f"(= +%{_yuzde(qg_d, qg_n):.0f}).")
        st.markdown("#### 2. Sodyum geri emilimi (kutle)")
        st.caption("PT'de Na+ konsantrasyonu ~140 mM'de neredeyse sabittir (iso-ozmotik); emilim "
                   "**akida (kutle)** gorunur.")
        st.plotly_chart(
            plot_case_metric(df_na_flow_pt, "position", "value", "condition",
                             "PT Lumen Na+ Akisi (yuk)",
                             "Na+ akisi (pmol/min)", cmap2),
            use_container_width=True,
        )
        st.warning(
            f"**Kutle:** PT'de geri emilen Na+ Normal **{reab_n:,.0f}** -> Diyabet **{reab_d:,.0f} pmol/min** "
            f"(= +%{_yuzde(reab_d, reab_n):.0f})."
        )
        st.markdown("---")
        st.page_link("pages/4_Karsilastirma.py",
                      label="Karsilastirma sayfasinda F_normal vs F_diab_mod yan yana incele",
                      icon=":material/search:")

    with t_kaynak:
        kaynaklar_kutusu(
            ["hu2021"],
            baslik="Kaynaklar — Vaka 2", acik=True,
        )
        st.info("Ek kaynaklar makale yuklendikten sonra eklenecek.")


# ================================================================
# VAKA 3: Hipertansiyon
# ================================================================
elif vaka == "Hipertansiyon":
    st.markdown("### Vaka 3: Hipertansiyon")
    cmap3 = {"Normal": "#dc2626", "Hipertansiyon": "#a16207"}

    df_na_con_tal = q(f"""
        SELECT position, value, condition FROM {DB}
        WHERE condition IN ('F_normal', 'F_HT')
          AND variable='con' AND solute='Na' AND segment='mTAL' AND compartment='Lumen' AND nephron='sup'
        ORDER BY condition, position
    """)
    df_na_con_tal["condition"] = df_na_con_tal["condition"].map({"F_normal": "Normal", "F_HT": "Hipertansiyon"})
    df_na_flow_tal = q(f"""
        SELECT position, value, condition FROM {DB}
        WHERE condition IN ('F_normal', 'F_HT')
          AND variable='flow' AND solute='Na' AND segment='mTAL' AND compartment='Lumen' AND nephron='sup'
        ORDER BY condition, position
    """)
    df_na_flow_tal["condition"] = df_na_flow_tal["condition"].map({"F_normal": "Normal", "F_HT": "Hipertansiyon"})
    cin_n, cin_h = _giris(df_na_con_tal, "Normal"), _giris(df_na_con_tal, "Hipertansiyon")
    cout_n, cout_h = _cikis(df_na_con_tal, "Normal"), _cikis(df_na_con_tal, "Hipertansiyon")
    fout_n, fout_h = _cikis(df_na_flow_tal, "Normal"), _cikis(df_na_flow_tal, "Hipertansiyon")

    # --- Hasta ozeti karti ---
    with st.container(border=True):
        st.markdown("##### Hasta Ozeti")
        st.info("Hasta profili ve klinik baglam makale yuklendikten sonra doldurulacak.")
        k1, k2 = st.columns(2)
        k1.metric("mTAL cikis Na yuku", f"{fout_h:,.0f} pmol/min",
                   f"{_yuzde(fout_h, fout_n):+.0f}%", delta_color="off")
        k2.metric("mTAL cikis Na konsantr.", f"{cout_h:.0f} mM",
                   f"{cout_h - cout_n:+.0f} mM", delta_color="off")
        st.caption("Metrikler `F_HT`'nin `F_normal`'a gore farkini verir.")

    # --- 4 Sekme ---
    t_mek, t_ilac, t_model, t_kaynak = st.tabs(
        ["Mekanizma ve Fizyoloji", "Ilac ve Doz Yaklasimi", "Model Verileri", "Kaynaklar"]
    )

    with t_mek:
        st.info("Mekanizma aciklamasi makale yuklendikten sonra doldurulacak.")

    with t_ilac:
        st.info("Ilac ve doz bilgisi makale yuklendikten sonra doldurulacak.")

    with t_model:
        st.markdown("#### Kalin cikan kol (TAL) sodyum yonetimi")
        st.caption("Sol: lumen konsantrasyonu. Sag: lumen akisi (distale iletilen yuk).")
        h1, h2 = st.columns(2)
        with h1:
            st.plotly_chart(
                plot_case_metric(df_na_con_tal, "position", "value", "condition",
                                 "mTAL Lumen Na+ Konsantrasyonu (mM)", "Na+ (mM)", cmap3),
                use_container_width=True,
            )
        with h2:
            st.plotly_chart(
                plot_case_metric(df_na_flow_tal, "position", "value", "condition",
                                 "mTAL Lumen Na+ Akisi (yuk)", "Na+ akisi (pmol/min)", cmap3),
                use_container_width=True,
            )
        st.caption(
            f"mTAL cikisinda hipertansiyonda yuk: {fout_n:,.0f} -> {fout_h:,.0f} pmol/min "
            f"(= +%{_yuzde(fout_h, fout_n):.0f})."
        )
        st.markdown("---")
        st.page_link("pages/4_Karsilastirma.py",
                      label="Karsilastirma sayfasinda F_normal vs F_HT yan yana incele",
                      icon=":material/search:")

    with t_kaynak:
        kaynaklar_kutusu(
            ["hu2021"],
            baslik="Kaynaklar — Vaka 3", acik=True,
        )
        st.info("Ek kaynaklar makale yuklendikten sonra eklenecek.")

cite_footer()
