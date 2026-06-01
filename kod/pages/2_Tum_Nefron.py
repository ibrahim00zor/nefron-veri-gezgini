"""2_Tum_Nefron.py — PT->IMCD zincirli butun nefron grafigi."""
import pandas as pd
import streamlit as st
from ui_kit import (
    setup_page, render_sidebar, q, DB, chart_yap, cite_footer, neph_for,
    secenekler, SEG_ORDER_SUP, SEG_ORDER_JUX,
)

setup_page("Tüm Nefron")
senaryo = render_sidebar()

st.markdown("## Tüm Nefron Boyunca")
st.caption("Segmentler fizyolojik sırada yan yana çizilir. Dikey kesik çizgiler segment sınırlarıdır. "
           "Toplayıcı kanal (CCD/OMCD/IMCD) otomatik 'merged' nefron altında.")

segs, solutes = secenekler()

c1, c2, c3 = st.columns(3)
solute = c1.selectbox("Solüt", solutes, index=solutes.index("Na"))
compartment = c2.selectbox("Kompartman", ["Lumen", "Cell", "Bath"])
nephron = c3.selectbox("Nefron tipi", ["sup", "jux1", "jux2", "jux3", "jux4", "jux5"])

order = SEG_ORDER_JUX if nephron.startswith("jux") else SEG_ORDER_SUP
parts = []
for i, seg in enumerate(order):
    eff = neph_for(seg, nephron)
    d = q(
        f"""SELECT position, value FROM {DB}
            WHERE condition=? AND variable='con' AND solute=? AND segment=? AND compartment=? AND nephron=?
            ORDER BY position""",
        [senaryo, solute, seg, compartment, eff],
    )
    if d.empty:
        continue
    parts.append(d.assign(x=i + d["position"], segment=seg))

if not parts:
    st.warning("Veri yok.")
else:
    full = pd.concat(parts, ignore_index=True)
    fig = chart_yap(full, "x", "value", "segment",
                    f"{nephron} nefronu — {solute} ({compartment})",
                    "Segment sırası (akış yönü)",
                    f"{solute} (mM)", color_label="Segment",
                    category_orders={"segment": order}, height=520)
    for i in range(1, len(order)):
        fig.add_vline(x=i, line_dash="dot", opacity=0.2)
    fig.update_xaxes(tickmode="array",
                     tickvals=[i + 0.5 for i in range(len(order))],
                     ticktext=order)
    st.plotly_chart(fig, use_container_width=True)
    cite_footer()

    with st.expander("Segment-bazlı özet (giriş → çıkış)"):
        ozet = (full.sort_values(["segment", "x"])
                    .groupby("segment").agg(giris=("value", "first"),
                                            cikis=("value", "last")).round(2)
                    .reindex(order).dropna())
        ozet["oran"] = (ozet["cikis"] / ozet["giris"]).round(2)
        st.dataframe(ozet, use_container_width=True)
