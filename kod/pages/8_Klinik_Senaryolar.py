"""
8_Klinik_Senaryolar.py — Faz 5: Hekim Eğitici Aracı
Bu sayfa, model ciktilarini "Vaka Analizi" formatiyla, hekimler ve 
tip ogrencileri icin hikayelestirerek sunar.
"""
import streamlit as st
import pandas as pd
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
        
        Proksimalde emilemeyen sodyum, *Makula Densa*'ya (mTAL çıkışı) ulaşır. Makula Densa'daki artmış sodyum yükü, afferent arteriyolde vazokonstriksiyona neden olarak glomerüler içi basıncı düşürür ve **hiperfiltrasyonu** önler.
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

    st.markdown("#### 2. Makula Densa'ya (mTAL Çıkışı) Gelen Sodyum Yükü")
    df_na_mtal = q(f"""
        SELECT position, value, condition 
        FROM {DB} 
        WHERE condition IN ('F_normal', 'F_SGLT2')
          AND variable='con' AND solute='Na' AND segment='mTAL' AND compartment='Lumen' AND nephron='sup'
        ORDER BY condition, position
    """)
    df_na_mtal["condition"] = df_na_mtal["condition"].map({"F_normal": "Normal", "F_SGLT2": "SGLT2 İnhibisyonu"})
    
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(
            plot_case_metric(df_na_mtal, "position", "value", "condition", "mTAL Lümen Sodyum Konsantrasyonu (mM)", "Na+ (mM)",
                             {"Normal": "#dc2626", "SGLT2 İnhibisyonu": "#be185d"}),
            use_container_width=True
        )
    with c4:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.success("""
        **TGF Etkisi Kanıtı:**
        mTAL segmentinin çıkış noktası (pozisyon 1.0), Makula Densa'ya karşılık gelir.
        Grafikte görebileceğiniz gibi, SGLT2 inhibisyonu altında Makula Densa'ya ulaşan sodyum konsantrasyonu belirgin şekilde **yüksektir**.
        Bu yüksek Na+ sinyali, böbreğin "filtrasyon hızını yavaşlat" komutu vermesini sağlar.
        """)

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
    # Akı (flow) üzerinden kütle hesaplayacağız veya doğrudan flow gösterebiliriz.
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
    st.caption("Diyabet senaryosunda glomerüler filtrasyonun (PT giriş değeri) belirgin şekilde yüksek olduğunu görebilirsiniz (Hiperfiltrasyon). Ancak PT sonunda daha agresif bir su emilimi (eğim) gerçekleşir.")

    st.markdown("#### 2. Artmış Oksijen Talebi: Sodyum Emilimi")
    df_na_pt = q(f"""
        SELECT position, value, condition 
        FROM {DB} 
        WHERE condition IN ('F_normal', 'F_diab_mod')
          AND variable='con' AND solute='Na' AND segment='PT' AND compartment='Lumen' AND nephron='sup'
        ORDER BY condition, position
    """)
    df_na_pt["condition"] = df_na_pt["condition"].map({"F_normal": "Normal", "F_diab_mod": "Diyabet"})
    
    st.plotly_chart(
        plot_case_metric(df_na_pt, "position", "value", "condition", "PT Lümen Sodyum Konsantrasyonu (mM)", "Na+ (mM)",
                         {"Normal": "#dc2626", "Diyabet": "#ea580c"}),
        use_container_width=True
    )
    st.warning("""
    **Hipertrofi Sinyali:** 
    Diyabette artmış SGLT2 aktivitesi, sodyum reabsorpsiyonunu olağanüstü hızlandırır. Sodyum pompalarının (Na-K-ATPase) bu aşırı mesaisi, böbrekte oksijen tüketimini ve hipoksi riskini artırır.
    """)

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
    
    df_na_tal = q(f"""
        SELECT position, value, condition 
        FROM {DB} 
        WHERE condition IN ('F_normal', 'F_HT')
          AND variable='con' AND solute='Na' AND segment='mTAL' AND compartment='Lumen' AND nephron='sup'
        ORDER BY condition, position
    """)
    df_na_tal["condition"] = df_na_tal["condition"].map({"F_normal": "Normal", "F_HT": "Hipertansiyon"})
    
    st.plotly_chart(
        plot_case_metric(df_na_tal, "position", "value", "condition", "mTAL Lümen Sodyum Konsantrasyonu (mM)", "Na+ (mM)",
                         {"Normal": "#dc2626", "Hipertansiyon": "#a16207"}),
        use_container_width=True
    )
    st.caption("""
    Hipertansiyonda mTAL segmentine gelen sodyum konsantrasyonu normalin altındadır ancak akış hızı (flow) yüksek olduğundan *toplam kütle yükü* değişir. Çıkışta ise sodyum konsantrasyonu daha yüksektir; bu da distal sodyum iletiminin arttığını ve basınç natriürezinin çalıştığını gösterir.
    """)

cite_footer()
