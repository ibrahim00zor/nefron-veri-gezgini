"""
8_Klinik.py — Faz 27: Klinik Dünya — Profesyonel Eğitim Arayüzü

Projenin "iki dünyalı" mimarisinin ikinci ayağı. Model dünyası (sayfa 1-7)
verileri inceler; bu sayfa klinik bağlam, örnek vaka, ilaç/doz ve
fizyolojik mekanizmayı birleştirir.

GÜVENLIK / ÇERÇEVE:
- EGITIM amaclidir; klinik karar-destek DEGILDIR.
- Ilac/doz YALNIZ dogrulanmis kaynaktan (KDIGO, EMPA-KIDNEY, FDA etiketi).
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
    "hasta bakimi karari icin kullanilamaz. Ilac ve doz bilgileri yalniz dogrulanmis "
    "kaynaklardan eklenir ve guncel klinik kilavuzlarin yerini tutmaz."
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
st.caption("Bir vaka secin — detayli mekanizma, ilac/doz ve model verileri acilir.")

if "klinik_vaka" not in st.session_state:
    st.session_state.klinik_vaka = "SGLT2"

k1, k2, k3 = st.columns(3)

with k1:
    if st.button("🩸 SGLT2 Inhibisyonu", use_container_width=True, 
                 type="primary" if st.session_state.klinik_vaka == "SGLT2" else "secondary"):
        st.session_state.klinik_vaka = "SGLT2"
        st.rerun()

with k2:
    if st.button("⚡ Diyabetik Hiperfiltrasyon", use_container_width=True, 
                 type="primary" if st.session_state.klinik_vaka == "Hiperfiltrasyon" else "secondary"):
        st.session_state.klinik_vaka = "Hiperfiltrasyon"
        st.rerun()

with k3:
    if st.button("🫀 Hipertansiyon", use_container_width=True, 
                 type="primary" if st.session_state.klinik_vaka == "Hipertansiyon" else "secondary"):
        st.session_state.klinik_vaka = "Hipertansiyon"
        st.rerun()

vaka = st.session_state.klinik_vaka
st.markdown("---")


# ================================================================
# VAKA 1: SGLT2 İnhibisyonu
# ================================================================
if "SGLT2" in vaka:
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
        cc1, cc2 = st.columns([3, 2])
        with cc1:
            st.markdown(
                "**Demografik:** 58 yasinda kadin  \n"
                "**Oykusu:** ~8 yillik tip 2 diyabet (metformin altinda). "
                "Idrar albumin/kreatinin orani yuksek, eGFR orta duzeyde azalmis; "
                "eslik eden hipertansiyon.  \n"
                "**Klinik odak:** Glisemik kontrolun otesinde nefroproteksiyon — SGLT2 "
                "inhibisyonunun tubuloglomeruler geri bildirim (TGF) uzerinden "
                "hiperfiltrasyonu azaltmasi."
            )
        with cc2:
            st.markdown(
                "**Model karsilastirmasi:**  \nSaglikli kadin (`F_normal`) vs SGLT2 "
                "inhibisyonu (`F_SGLT2`), yuzeyel nefron. Proksimal glukoz/sodyum "
                "islenisi ve makula densa yuku."
            )
        k1, k2, k3 = st.columns(3)
        k1.metric("Makula densaya Na yuku", f"{flw_s:,.0f} pmol/min",
                   f"{_yuzde(flw_s, flw_n):+.0f}%", delta_color="off")
        k2.metric("Makula densa Na konsantr.", f"{con_s:.0f} mM",
                   f"{_yuzde(con_s, con_n):+.0f}%", delta_color="off")
        k3.metric("PT glukoz cikisi", f"{glu_s:.1f} mM",
                   f"{glu_s - glu_n:+.1f} mM", delta_color="off")
        st.caption("Temsili (kurgusal) egitim vakasi — gercek hasta degildir. "
                   "Metrikler `F_SGLT2`'nin `F_normal`'a gore farkini verir.")

    # --- Anamnez / Halk agzi zinciri (literaturle dolu placeholder) ---
    with st.expander("Anamnez ve Klinik Ipuclari"):
        st.markdown("""
**Tipik basvuru:** Hasta genellikle "seker hastaligi" deyimiyle bilinen tip 2 diyabet
ile takipte; "idrarim cok kopuruyor", "ayaklarim sisiyor" gibi ifadelerle gelebilir.

**Halk agzi -> Tibbi isaret -> Bilimsel karsilik:**

| Hasta ifadesi (halk agzi) | Tibbi isaret | Bilimsel karsilik |
|---|---|---|
| "Idrarim kopuruyor/bulanik" | Proteinuri / albuminuri | Glomeruler bariyer hasari, hiperfiltrasyon |
| "Ayaklarim sisiyor" | Periferik odem | Sodyum retansiyonu, azalmis GFR |
| "Sekerimi olcturdugumde yuksek ama iyi hissediyorum" | Asemptomatik hiperglisemi | Tubuler hiperyuk, SGLT2 upregulasyonu |
| "Tansiyon ilacimi duzgun aliyorum ama tansiyonum dusmedi" | Direncli hipertansiyon | Tubuler sodyum geri emilim artisi, TGF bozulmasi |

> *Bu katman gelistirme asamasindadir. Icerik, klinisyen/hoca geri bildirimiyle
> zenginlestirilecektir. Literatur: Vallon 2022; KDIGO 2022.*
        """)

    # --- 4 Sekme ---
    t_mek, t_ilac, t_model, t_kaynak = st.tabs(
        ["Mekanizma ve Fizyoloji", "Ilac ve Doz Yaklasimi", "Model Verileri", "Kaynaklar"]
    )

    with t_mek:
        st.markdown("""
**Mekanizma:** SGLT2 inhibisyonu proksimal tubulde (S1/S2) glukoz ve sodyumun birlikte
geri emilimini azaltir. Emilemeyen sodyum distale tasar, makula densaya (cTAL cikisi)
ulasir; artmis NaCl sinyali TGF ile afferent vazokonstriksiyon tetikler, glomeruler
basinc duser ve hiperfiltrasyon frenlenir.

**Fizyolojik zincir:**
1. SGLT2 blokaji -> glukoz + Na geri emilimi azalir
2. Glukozun osmotik su tutmasi -> diurez
3. Distale artmis Na yukü -> makula densa NKCC2 sinyali artar
4. TGF aktivasyonu -> afferent arteriyol daraltilir -> GFR duser
5. Hiperfiltrasyon duzeltilir -> uzun vadede nefroproteksiyon

*(bkz. Kaynaklar: Vallon 2022; Upadhyay 2024.)*
        """)

    with t_ilac:
        st.markdown("""
**Ilac sinifi:** SGLT2 inhibitorleri (gliflozinler)

**Onaylanan ilaclar ve dozlari (egitim amacli, kaynakli):**

| Ilac | Doz | Kaynak |
|---|---|---|
| **Empagliflozin** | **10 mg, gunde 1 kez** | EMPA-KIDNEY (Herrington ve ark., 2023) |
| **Dapagliflozin** | **10 mg, gunde 1 kez** | DAPA-CKD (Heerspink ve ark., 2020) |
| **Kanagliflozin** | **100 mg, gunde 1 kez** | CREDENCE (Perlman ve ark., 2019) |

**Renal baslama esigi:** KDIGO 2022, tip 2 diyabet + KBH'de eGFR **>=20 mL/dk/1,73 m2**
iken SGLT2 inhibitoru baslatilmasini onerir. Baslandiktan sonra eGFR dusse bile
**diyaliz/transplanta dek surdurilmeli.**

**Zemin tedavi:** RAS inhibisyonu (ACEi/ARB) standart bakiminin uzerine eklenir.
ACEi/ARB tolere edilen en yuksek onayli doza titre edilmeli (KDIGO 2022).

**Onemli uyarilar:**
- Genital mantar enfeksiyonu riski artar (glukozuri nedeniyle)
- Euglisemik diyabetik ketoasidoz nadir ama ciddi (ozellikle tip 1 diyabette)
- Ilk haftalarda eGFR'de fizyolojik dusus (haemodinamik etki) beklenir — bu nefroproteksiyonun isaretidir
        """)
        st.info(
            "Bu doz bilgileri dogrulanmis kaynaklara dayanir ancak **klinisyen/hoca dogrulamasi "
            "beklemektedir** ve egitim amaclidir — recete/doz karari icin guncel ilac etiketi ve "
            "klinik degerlendirme gerekir."
        )

    with t_model:
        st.markdown("#### 1. Proksimal tubulde glukoz atilimi")
        st.plotly_chart(
            plot_case_metric(df_glu, "position", "value", "condition",
                             "PT Lumen Glukoz Konsantrasyonu (mM)",
                             "Glukoz (mM)", cmap1),
            use_container_width=True,
        )
        st.caption("SGLT2 inhibisyonunda glukoz emilemez, konsantrasyon artar (osmotik diureze katki).")
        st.markdown("#### 2. Makula densaya (cTAL cikisi) gelen sodyum")
        st.caption("Makula densa = kalin cikan kolun kortikal ucu (cTAL cikisi). NKCC2 lumen NaCl "
                   "**konsantrasyonunu** algilar; ulasan toplam sodyum **yuk (aki)** ile olculur.")
        g1, g2 = st.columns(2)
        with g1:
            st.plotly_chart(
                plot_case_metric(df_na_con, "position", "value", "condition",
                                 "cTAL Lumen Na+ Konsantrasyonu (NKCC2 sensoru)", "Na+ (mM)", cmap1),
                use_container_width=True,
            )
        with g2:
            st.plotly_chart(
                plot_case_metric(df_na_flow, "position", "value", "condition",
                                 "cTAL Lumen Na+ Akisi (makula densaya yuk)", "Na+ akisi (pmol/min)", cmap1),
                use_container_width=True,
            )
        st.success(
            f"""**TGF etkisi (model verisi):** Makula densaya ulasan **yuk = +%{_yuzde(flw_s, flw_n):.0f}**
(aki: {flw_n:,.0f} -> {flw_s:,.0f} pmol/min); NKCC2'nin algiladigi **konsantrasyon = +%{_yuzde(con_s, con_n):.0f}**
({con_n:.0f} -> {con_s:.0f} mM). Artmis NaCl sinyali -> afferent vazokonstriksiyon -> hiperfiltrasyonun frenlenmesi."""
        )
        st.markdown("---")
        st.markdown("**Model dunyasinda derinles:**")
        st.page_link("pages/4_Karsilastirma.py",
                      label="Karsilastirma sayfasinda F_normal vs F_SGLT2 yan yana incele",
                      icon=":material/search:")

    with t_kaynak:
        kaynaklar_kutusu(
            ["vallon2022", "upadhyay2024", "empakidney2023", "kdigo2022diabetes", "hu2021"],
            baslik="Kaynaklar — Vaka 1 (SGLT2i ve TGF)", acik=True,
        )


# ================================================================
# VAKA 2: Diyabetik Hiperfiltrasyon
# ================================================================
elif "Hiperfiltrasyon" in vaka:
    st.markdown("### Vaka 2: Diyabetik Hiperfiltrasyon ve Tubuler Hipotez")
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
        cc1, cc2 = st.columns([3, 2])
        with cc1:
            st.markdown(
                "**Demografik:** 24 yasinda erkek  \n"
                "**Oykusu:** Kisa sure once tip 1 diyabet tanisi almis. Henuz "
                "albuminuri yok; olculen GFR yuksek-normal (hiperfiltrasyon) sinirinda.  \n"
                "**Klinik odak:** Erken diyabette glomeruler hiperfiltrasyonun tubuler "
                "kokeni (tubuler hipotez) ve uzun vadeli bobrek riski acisindanki onemi."
            )
        with cc2:
            st.markdown(
                "**Model karsilastirmasi:**  \nSaglikli kadin (`F_normal`) vs orta diyabet "
                "(`F_diab_mod`), yuzeyel nefron. Proksimal hacim akisi ve sodyum geri emilimi.  \n"
                "**Veri butunlugu notu:** F_diab_mod'un toplayici kanali (IMCD) yakinsamamis; "
                "yalniz proksimal-orta segment verileri gecerlidir."
            )
        k1, k2 = st.columns(2)
        k1.metric("PT giris su akisi (filtrasyon)", f"{qg_d:.0f} nl/min",
                   f"{_yuzde(qg_d, qg_n):+.0f}%", delta_color="off")
        k2.metric("PT'de geri emilen Na (kutle)", f"{reab_d:,.0f} pmol/min",
                   f"{_yuzde(reab_d, reab_n):+.0f}%", delta_color="off")
        st.caption("Temsili (kurgusal) egitim vakasi — gercek hasta degildir. "
                   "Metrikler `F_diab_mod`'un `F_normal`'a gore farkini verir.")

    # --- Anamnez / Halk agzi zinciri ---
    with st.expander("Anamnez ve Klinik Ipuclari"):
        st.markdown("""
**Tipik basvuru:** Genc hastalar genellikle rutin kontrollerde "sekerimin yuksek oldugunu
soylemisler" seklinde gelir. Erken diyabetik nefropati belirtileri sinsidir.

**Halk agzi -> Tibbi isaret -> Bilimsel karsilik:**

| Hasta ifadesi (halk agzi) | Tibbi isaret | Bilimsel karsilik |
|---|---|---|
| "Cok su iciyorum, cok isiyorum" | Polidipsi + poliuri | Osmotik diurez (glukozuri), hiperfiltrasyon |
| "Tahlillerimde bobrek degerleri normalmis" | Normal kreatinin ile gizli hiperfiltrasyon | Artmis SNGFR, tubuler hiperyuk |
| "Sekerimi kontrol ediyorum ama bobreklerim kotu gidebilir mi?" | Erken nefropati riski | Tubuler hipotez: SGLT2 upregulasyonu -> TGF bozulmasi |

> *Bu katman gelistirme asamasindadir. Icerik, klinisyen/hoca geri bildirimiyle
> zenginlestirilecektir. Literatur: Vallon ve Thomson 2020.*
        """)

    # --- 4 Sekme ---
    t_mek, t_ilac, t_model, t_kaynak = st.tabs(
        ["Mekanizma ve Fizyoloji", "Ilac ve Doz Yaklasimi", "Model Verileri", "Kaynaklar"]
    )

    with t_mek:
        st.markdown("""
**Mekanizma (tubuler hipotez):** Diyabette hiperglisemi filtre glukoz yukunu artirir.
Bobrek, SGLT2 ve SGLT1 aktivitesini upregule eder (glukoz emilimini artirir). Bu,
proksimalde Na+ geri emilimini de artirir -> makula densaya **az** sodyum ulasir -> TGF
bunu "dusuk basinc" okur -> afferent arteriyol genisley -> GFR daha da artar (hiperfiltrasyon).

**Fizyolojik zincir:**
1. Hiperglisemi -> artmis filtre glukoz yuku
2. SGLT2/SGLT1 upregulasyonu -> artmis proksimal Na+/glukoz geri emilimi
3. Makula densaya azalmis Na+ iletimi
4. TGF "dusuk basinc" sinyali -> afferent vazodilatasyon
5. GFR artisi (hiperfiltrasyon) -> uzun vadede glomeruler hasar

*(bkz. Kaynaklar: Vallon ve Thomson 2020.)*
        """)

    with t_ilac:
        st.markdown("""
**Yaklasim baglami:** Bu vaka oncelikle bir **patofizyoloji** vakasidirr;
hiperfiltrasyonun erken bir belirtec oldugunu anlamak klinik onlem icin kritiktir.

**Ilac sinifi ve dozlar (egitim amacli, kaynakli):**

| Yaklasim | Ilac ornekleri | Doz | Kaynak |
|---|---|---|---|
| **SGLT2 inhibisyonu** | Empagliflozin | 10 mg/gun | KDIGO 2022; EMPA-KIDNEY 2023 |
| | Dapagliflozin | 10 mg/gun | KDIGO 2022 |
| **RAS blokaji (albuminuri varsa)** | Enalapril | 10-20 mg/gun (titre et) | KDIGO 2021 BP; KDIGO 2022 |
| | Losartan | 50-100 mg/gun (titre et) | KDIGO 2021 BP |
| | Ramipril | 5-10 mg/gun (titre et) | KDIGO 2021 BP |

**KDIGO 2022 onerileri:**
- Tip 2 diyabet + KBH: SGLT2i, eGFR >=20 iken basla; eGFR dusse bile surdurebilirsin.
- ACEi/ARB: albuminuri varsa baslat, **tolere edilen en yuksek onayli doza** titre et.
- Basladiktan sonra **2-4 hafta icinde** kan basinci, kreatinin ve potasyum izle.
- eGFR'de <%30 dusus fizyolojik kabul edilir; >%30 ise dozu azalt veya kes.
- ACEi + ARB kombinasyonundan KACIN.

**Erken diyabette ozel not:**
Hiperfiltrasyon genc hastalarda genellikle asemptomatiktir. eGFR "normal" bile olsa,
"yuksek-normal" deger (>130 mL/dk/1,73 m2) hiperfiltrasyon isareti olabilir.
SGLT2i, TGF'yi yeniden etkinlestirerek bu hiperfiltrasyonu duzeltir.
        """)
        st.info(
            "Bu doz bilgileri dogrulanmis kaynaklara dayanir ancak **klinisyen/hoca dogrulamasi "
            "beklemektedir** ve egitim amaclidir — recete/doz karari icin guncel ilac etiketi ve "
            "klinik degerlendirme gerekir."
        )

    with t_model:
        st.markdown("#### 1. Proksimal tubule giren artmis hacim yuku")
        st.plotly_chart(
            plot_case_metric(df_flow_pt, "position", "value", "condition",
                             "PT Su Hacmi Akisi (nl/min)",
                             "Hacim (nl/min)", cmap2),
            use_container_width=True,
        )
        st.caption(f"Diyabette PT giris su akisi daha yuksek: {qg_n:.0f} -> {qg_d:.0f} nl/min "
                   f"(= +%{_yuzde(qg_d, qg_n):.0f}, hiperfiltrasyon).")
        st.markdown("#### 2. Sodyum geri emilimi (kutle — konsantrasyon degil)")
        st.caption("PT'de Na+ konsantrasyonu ~140 mM'de neredeyse sabittir (iso-ozmotik); emilim "
                   "**akida (kutle)** gorunur: geri emilen = giris akisi - cikis akisi.")
        st.plotly_chart(
            plot_case_metric(df_na_flow_pt, "position", "value", "condition",
                             "PT Lumen Na+ Akisi (yuk)",
                             "Na+ akisi (pmol/min)", cmap2),
            use_container_width=True,
        )
        st.warning(
            f"""**Kutle:** PT'de geri emilen Na+ Normal **{reab_n:,.0f}** -> Diyabet **{reab_d:,.0f} pmol/min**
(= +%{_yuzde(reab_d, reab_n):.0f}). Artmis pompa mesaisi oksijen tuketimini ve hipoksi riskini artirir.
(Konsantrasyonla bakilsaydi iki egri ust uste duser, etki gorunmezdi.)"""
        )
        st.markdown("---")
        st.markdown("**Model dunyasinda derinles:**")
        st.page_link("pages/4_Karsilastirma.py",
                      label="Karsilastirma sayfasinda F_normal vs F_diab_mod yan yana incele",
                      icon=":material/search:")

    with t_kaynak:
        kaynaklar_kutusu(
            ["vallon_thomson2020", "kdigo2022diabetes", "kdigo2021bp", "hu2021"],
            baslik="Kaynaklar — Vaka 2 (diyabetik hiperfiltrasyon)", acik=True,
        )


# ================================================================
# VAKA 3: Hipertansiyon
# ================================================================
elif "Hipertansiyon" in vaka:
    st.markdown("### Vaka 3: Hipertansiyon ve Basinc Natriurezi")
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
        cc1, cc2 = st.columns([3, 2])
        with cc1:
            st.markdown(
                "**Demografik:** 50 yasinda kadin  \n"
                "**Oykusu:** Yillardir yuksek kan basinci; tuz aliminina duyarli "
                "oldugu izlenimi var. Tek ilac (ACEi) altinda yeterli basinc "
                "kontrolu saglanamamis.  \n"
                "**Klinik odak:** Yuksek perfuzyon basincinin distal sodyum iletimine "
                "etkisi ve basinc natriurezi mekanizmasi."
            )
        with cc2:
            st.markdown(
                "**Model karsilastirmasi:**  \nSaglikli kadin (`F_normal`) vs "
                "hipertansiyon (`F_HT`), yuzeyel nefron. Kalin cikan kolda sodyum "
                "konsantrasyonu ve yuku."
            )
        k1, k2 = st.columns(2)
        k1.metric("mTAL cikis Na yuku", f"{fout_h:,.0f} pmol/min",
                   f"{_yuzde(fout_h, fout_n):+.0f}%", delta_color="off")
        k2.metric("mTAL cikis Na konsantr.", f"{cout_h:.0f} mM",
                   f"{cout_h - cout_n:+.0f} mM", delta_color="off")
        st.caption("Temsili (kurgusal) egitim vakasi — gercek hasta degildir. "
                   "Metrikler `F_HT`'nin `F_normal`'a gore farkini verir.")

    # --- Anamnez / Halk agzi zinciri ---
    with st.expander("Anamnez ve Klinik Ipuclari"):
        st.markdown("""
**Tipik basvuru:** Hasta "tansiyonum yuksek cikiyor", "basim agriyor, ensem tutuyor"
gibi ifadelerle gelir. Ozellikle tuzlu yemeklerden sonra sikayetlerin artmasi
tuz duyarliligi isareti olabilir.

**Halk agzi -> Tibbi isaret -> Bilimsel karsilik:**

| Hasta ifadesi (halk agzi) | Tibbi isaret | Bilimsel karsilik |
|---|---|---|
| "Tansiyonum yuksek, ilacimi aliyorum ama dusmedi" | Direncli hipertansiyon | Basinc natriurezi bozulmasi, artmis tubuler Na geri emilimi |
| "Tuzlu yedigimde basim agriyor" | Tuz-duyarli hipertansiyon | Basinc natriurezi egrisinin saga kaymasi |
| "Bobreklerim de etkilenmis diyorlar" | Hipertansif nefropati | Kronik glomeruler basinc artisi, tubuler hasar |
| "Idrar sokturdugu ilac verdiler" | Diuretik kullanimi | Tubuler Na geri emiliminin farmakolojik azaltilmasi |

> *Bu katman gelistirme asamasindadir. Icerik, klinisyen/hoca geri bildirimiyle
> zenginlestirilecektir. Literatur: Ivy ve Bailey 2014; KDIGO 2021.*
        """)

    # --- 4 Sekme ---
    t_mek, t_ilac, t_model, t_kaynak = st.tabs(
        ["Mekanizma ve Fizyoloji", "Ilac ve Doz Yaklasimi", "Model Verileri", "Kaynaklar"]
    )

    with t_mek:
        st.markdown("""
**Mekanizma (basinc natriurezi):** Artan renal perfuzyon basinci proksimal Na+ geri
emilimini azaltir; daha cok sodyum distale iletilir. Bu, uzun donem kan basincini
stabilize eden guclu bir mekanizmadir. Kronik hipertansiyonda bu egri saga kayar —
ayni kan basincinda daha az sodyum atilir, hacim genisler.

**Fizyolojik zincir:**
1. Kronik hipertansiyon -> artmis renal perfuzyon basinci
2. Proksimal Na+ geri emilimi azalir (basinc natriurezi)
3. TAL'e artmis sodyum iletimi
4. NKCC2 ile artmis emilim denemesine ragmen cikista artmis yuk
5. Distal iletim artar -> sodyum atilimi ile denge aranir

*(bkz. Kaynaklar: Ivy ve Bailey 2014.)*
        """)

    with t_ilac:
        st.markdown("""
**Ilac siniflari ve dozlari (egitim amacli, kaynakli):**

| Yaklasim | Ilac ornekleri | Doz | Kaynak |
|---|---|---|---|
| **RAS blokaji (1. basamak, albuminuri varsa)** | Enalapril | 5-20 mg/gun (titre et) | KDIGO 2021 BP |
| | Losartan | 50-100 mg/gun (titre et) | KDIGO 2021 BP |
| | Ramipril | 2.5-10 mg/gun (titre et) | KDIGO 2021 BP |
| **Diuretik (ek ajan)** | Klortalidone | 12.5-25 mg/gun | CLICK calismasi (Agarwal 2021) |
| | Hidroklorotiyazid | 12.5-25 mg/gun | KDIGO 2021 BP |
| **Kalsiyum kanal blokoru (alternatif)** | Amlodipin | 5-10 mg/gun | KDIGO 2021 BP |

**KDIGO 2021 onerileri (KBH'de kan basinci):**
- **Hedef:** Sistolik <120 mmHg (standartlastirilmis ofis olcumu ile)
- **Birinci basamak (albuminuri varsa):** ACEi veya ARB; **tolere edilen en yuksek onayli doza** titre et
- **Ek ajan:** Kalsiyum kanal blokoru (CCB) veya tiyazid/tiyazid-benzeri diuretik
- **ACEi + ARB kombinasyonundan KACIN** (faydasi gosterilmemis, yan etki riski artar)
- **Hacim yukunde:** Loop diuretik tercih edilebilir (ozellikle ileri KBH'de)
- **Klortalidone:** CLICK calismasi (Agarwal 2021) ileri KBH'de (eGFR <30) bile etkili
  kan basinci dususu gostermistir
- Basladiktan sonra **2-4 hafta icinde** kreatinin ve potasyum izle

**Tubuler mekanizma baglantisi:** Tiyazid diuretikler DCT'deki NCC'yi inhibe ederek
sodyum geri emilimini azaltir; loop diuretikler TAL'deki NKCC2'yi inhibe eder. Her iki
sinif da basinc natriurezini farmakolojik olarak destekler.
        """)
        st.info(
            "Bu doz bilgileri dogrulanmis kaynaklara dayanir ancak **klinisyen/hoca dogrulamasi "
            "beklemektedir** ve egitim amaclidir — recete/doz karari icin guncel ilac etiketi ve "
            "klinik degerlendirme gerekir."
        )

    with t_model:
        st.markdown("#### Kalin cikan kol (TAL) sodyum yonetimi")
        st.caption("Sol: lumen konsantrasyonu. Sag: lumen akisi (distale iletilen yuk). "
                   "Distal iletim degisimi asil **akida** okunur.")
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
            f"mTAL **girisinde** konsantrasyon benzerdir ({cin_n:.0f} = {cin_h:.0f} mM). **Cikista** "
            f"hipertansiyonda hem konsantrasyon ({cout_n:.0f} -> {cout_h:.0f} mM) hem de daha belirleyici "
            f"olarak **aki/yuk** ({fout_n:,.0f} -> {fout_h:,.0f} pmol/min, = +%{_yuzde(fout_h, fout_n):.0f}) "
            f"daha yuksektir -> artmis distal sodyum iletimi (basinc natriurezi)."
        )
        st.markdown("---")
        st.markdown("**Model dunyasinda derinles:**")
        st.page_link("pages/4_Karsilastirma.py",
                      label="Karsilastirma sayfasinda F_normal vs F_HT yan yana incele",
                      icon=":material/search:")

    with t_kaynak:
        kaynaklar_kutusu(
            ["ivy_bailey2014", "kdigo2021bp", "agarwal2021click", "kdigo2022diabetes", "hu2021"],
            baslik="Kaynaklar — Vaka 3 (basinc natriurezi)", acik=True,
        )

cite_footer()
