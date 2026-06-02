"""4_Karsilastirma.py — Coklu senaryo overlay (Faz A).
Birden cok senaryoyu ayni grafikte gosterir; fark tablosu uretir."""
import pandas as pd
import streamlit as st
import plotly.express as px
from ui_kit import (
    setup_page, render_sidebar, q, DB, cite_footer, neph_for,
    secenekler, senaryo_listesi, SENARYO_AD, NEPHRONS, gecerli_veri, segment_bozuk_mu,
)

setup_page("Karşılaştırma")
senaryo_aktif = render_sidebar()  # sidebar yine aktif kalır ama bu sayfa tüm senaryolarda

st.markdown("## Senaryo Karşılaştırma")
st.caption("2–4 senaryoyu üst üste seç, aynı grafikte gör. "
           "Bu sekme **6 senaryolu kütüphanenin asıl gücünü** ortaya çıkarır — "
           "diyabette mTAL nasıl değişir, SGLT2 hangi etkiyi geri çevirir, vb.")

tum_senaryolar = senaryo_listesi()

# Üst seçiciler
c1, c2, c3 = st.columns(3)
solute = c1.selectbox("Solüt", ["Na", "K", "Cl", "urea", "glu", "HCO3", "NH3", "NH4"], index=0)
segs, _ = secenekler()
segment = c2.selectbox("Segment", segs, index=segs.index("mTAL") if "mTAL" in segs else 0)
compartment = c3.selectbox("Kompartman", ["Lumen", "Cell", "Bath"], index=0)

nephron_req = st.selectbox(
    "Nefron tipi (CD segmentlerinde otomatik 'merged' olur)",
    NEPHRONS,
    index=NEPHRONS.index("sup"),
)
nephron = neph_for(segment, nephron_req)

# Çoklu senaryo seçimi
varsayilan = [s for s in ["F_normal", "F_diab_mod", "F_SGLT2"] if s in tum_senaryolar][:3]
secilenler = st.multiselect(
    "Karşılaştırılacak senaryolar (2–4 önerilir)",
    tum_senaryolar,
    default=varsayilan or tum_senaryolar[:2],
    format_func=lambda s: SENARYO_AD.get(s, s),
)

if len(secilenler) < 2:
    st.warning("En az 2 senaryo seç.")
    st.stop()

# Veri çekme
placeholders = ",".join(["?"] * len(secilenler))
df = q(
    f"""SELECT condition, position, value FROM {DB}
        WHERE condition IN ({placeholders})
              AND variable='con' AND solute=? AND segment=?
              AND compartment=? AND nephron=?
        ORDER BY condition, position""",
    [*secilenler, solute, segment, compartment, nephron],
)

# Bu segmentte yakinsamayan senaryolari tumuyle cikar; sonra NaN emniyet agi.
bozuk = [s for s in secilenler if segment_bozuk_mu(s, segment)]
if bozuk:
    df = df[~df["condition"].isin(bozuk)]
    ad = ", ".join(SENARYO_AD.get(s, s) for s in bozuk)
    st.warning(f"**{ad}** bu segmentte ({segment}) sayısal olarak **yakınsamadı**; "
               f"karşılaştırmadan çıkarıldı. Distal/idrar yalnız temiz senaryolarda güvenilir.")
df, _ = gecerli_veri(df, "con")

if df.empty:
    st.warning(f"Seçili kombinasyonda geçerli veri yok (örn: LDL yalnız jux nefronlarda, "
               f"ya da seçili senaryolar bu segmentte yakınsamadı).")
    st.stop()

# Renk paleti — F kırmızı tonları, M mavi tonları
COLOR_MAP = {
    "F_normal":   "#dc2626",
    "F_diab_mod": "#ea580c",
    "F_HT":       "#a16207",
    "F_SGLT2":    "#be185d",
    "M_normal":   "#1e40af",
    "M_SGLT2":    "#0891b2",
}

fig = px.line(
    df, x="position", y="value", color="condition",
    title=f"{segment} — {solute} ({compartment}, {nephron})",
    labels={"position": "Pozisyon (0 = giriş, 1 = çıkış)",
            "value": f"{solute} (mM)", "condition": "Senaryo"},
    color_discrete_map=COLOR_MAP,
)
fig.update_layout(hovermode="x unified", height=500,
                  legend=dict(title_text="Senaryo"))
fig.update_traces(line=dict(width=2.6))
st.plotly_chart(fig, use_container_width=True)
cite_footer()

# ============================================================
#  Fark tablosu — her senaryo icin giris/cikis ve referansa gore fark
# ============================================================
st.markdown("### Senaryolar arası farklar")

ozet = (df.groupby("condition")
          .agg(giris=("value", "first"),
               cikis=("value", "last"),
               min=("value", "min"),
               max=("value", "max"))
          .round(2))
ozet["değişim_%"] = ((ozet["cikis"] - ozet["giris"]) / ozet["giris"] * 100).round(1)

# Referans senaryoyu kullanıcıya seçtir
ref = st.selectbox("Referans senaryo (farklar buna göre hesaplanır)",
                   secilenler, format_func=lambda s: SENARYO_AD.get(s, s))
if ref in ozet.index:
    ref_cikis = ozet.loc[ref, "cikis"]
    ozet["referansa_göre_%"] = ((ozet["cikis"] - ref_cikis) / ref_cikis * 100).round(1)

st.dataframe(ozet, use_container_width=True)

# Otomatik gözlem
if len(ozet) >= 2 and "referansa_göre_%" in ozet.columns:
    farklar = ozet["referansa_göre_%"].abs().sort_values(ascending=False)
    en_buyuk = farklar.index[0] if farklar.iloc[0] > 0 else None
    if en_buyuk and en_buyuk != ref:
        oran = ozet.loc[en_buyuk, "referansa_göre_%"]
        st.info(
            f"**Gözlem:** `{ref}` referans alındığında, **`{en_buyuk}`** "
            f"({SENARYO_AD.get(en_buyuk, en_buyuk)}) en büyük sapmaya sahip — "
            f"`{segment}` segmenti çıkışında **{solute} %{oran:+.1f}** farklı. "
            f"Bu pertürbasyonun bu segmente etkisi belirgindir."
        )

# CSV indir
st.download_button(
    "Bu karşılaştırma verisini CSV indir",
    df.to_csv(index=False).encode("utf-8"),
    file_name=f"karsilastirma_{'_vs_'.join(secilenler)}_{segment}_{solute}.csv",
    mime="text/csv",
)
