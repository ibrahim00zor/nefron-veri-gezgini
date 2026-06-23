"""7_Interaktif_Anatomi_BETA.py — Faz 4 D3.js Entegrasyon Prototipi
D3.js ile cizilmis topolojik nefron anatomi diagrami, isı haritasi olarak gosterilir."""
import os
import json
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

from ui_kit import (
    setup_page, render_sidebar, q, DB, neph_for,
    secenekler, NEPHRONS, segment_bozuk_mu, PROJ
)

setup_page("İnteraktif Anatomi (BETA)")
senaryo_aktif = render_sidebar()

st.markdown("## İnteraktif Anatomi (BETA)")
st.caption("Faz 4 prototipi: D3.js tabanlı anatomik çizim üzerinde ısı haritası.")

# Ust seciciler
c1, c2, c3 = st.columns(3)
_, sol = secenekler()
solute = c1.selectbox("Solüt", sol, index=sol.index("Na") if "Na" in sol else 0)
compartment = c2.selectbox("Kompartman", ["Lumen", "Cell", "Bath"], index=0)
nephron_req = c3.selectbox(
    "Nefron tipi (CD segmentleri otomatik 'merged' olur)",
    NEPHRONS,
    index=NEPHRONS.index("sup"),
)

# DuckDB Sorgusu
# Tum segmentler icin secilen solut, senaryo, ve kompartmanin konsantrasyonunu alalim
st.markdown("---")

# Segmentleri sirayla veya hepsini birden cekelim
df = q(
    f"""SELECT segment, position, value FROM {DB}
        WHERE condition = ?
          AND variable='con' AND solute=?
          AND compartment=?
        ORDER BY segment, position""",
    [senaryo_aktif, solute, compartment]
)

if df.empty:
    st.warning("Seçilen filtreler için veri bulunamadı.")
    st.stop()

# Nefron filtresi: CD segmentleri icin merged, digerleri icin nephron_req
# DuckDB sorgusuna nephron eklemedik, cunku segment bazli degisiyor. Pandas'ta filtreleyelim.
cd_segs = {"CCD", "OMCD", "IMCD"}
df_filtered = []
for segment in df['segment'].unique():
    target_nephron = "merged" if segment in cd_segs else nephron_req
    # Ana tablodan sadece o nefron tipini alalim (sorguyu hafifletmek icin yeniden q yapalim)
    df_seg = q(
        f"""SELECT segment, position, value FROM {DB}
            WHERE condition = ? AND variable='con' AND solute=? AND compartment=? 
            AND segment=? AND nephron=? ORDER BY position""",
        [senaryo_aktif, solute, compartment, segment, target_nephron]
    )
    if not df_seg.empty and not segment_bozuk_mu(senaryo_aktif, segment):
        # NaN kontrolu
        if df_seg['value'].notna().all():
            df_filtered.append(df_seg)

if not df_filtered:
    st.warning("Geçerli/yakınsamış veri bulunamadı.")
    st.stop()

df_clean = pd.concat(df_filtered)

# Segmentlere gore giris, cikis ve ortalama bulma
segments_data = {}
min_val = float(df_clean['value'].min())
max_val = float(df_clean['value'].max())

for segment, group in df_clean.groupby('segment'):
    entry_val = float(group['value'].iloc[0])
    exit_val = float(group['value'].iloc[-1])
    mean_val = float(group['value'].mean())
    
    segments_data[segment] = {
        "entry": entry_val,
        "exit": exit_val,
        "mean": mean_val
    }

# JSON yapisini hazirla
injected_data = {
    "solute": solute,
    "min_val": min_val,
    "max_val": max_val,
    "segments": segments_data
}

# D3.js HTML sablonunu oku
html_path = os.path.join(PROJ, "kod", "d3_components", "nephron_diagram.html")
try:
    with open(html_path, "r", encoding="utf-8") as f:
        html_template = f.read()
except FileNotFoundError:
    st.error(f"HTML şablonu bulunamadı: {html_path}")
    st.stop()

# JSON'i yerlestir
json_str = json.dumps(injected_data)
# Replace existing placeholder
html_rendered = html_template.replace(
    '/*DATA_PLACEHOLDER*/ {"solute": "Na", "min_val": 0, "max_val": 300}', 
    json_str
)

# Render
components.html(html_rendered, height=900, scrolling=False)

st.info("Bu anatomik çizim, segmentlerin fiziksel yapısını basitleştirerek D3.js üzerinde 2 boyutlu haritalar.")
