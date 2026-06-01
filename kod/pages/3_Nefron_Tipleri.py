"""3_Nefron_Tipleri.py — sup vs jux1-5 karSilaStirma."""
import streamlit as st
import plotly.express as px
from ui_kit import (
    setup_page, render_sidebar, q, DB, cite_footer, secenekler, CD_SEGMENTS,
)
from egitim_icerigi import segment_info, atif_kisa

setup_page("Nefron Tipleri", "📐")
senaryo = render_sidebar()

st.markdown("## 📐 Nefron Tiplerini Karşılaştır")
st.caption("Aynı segment + solüt + kompartman için sup ve jux1–5 üst üste çizilir. "
           "Derin nefronlar (jux5) medullaya en çok inenler — gradyan onlardan dogar.")

segs, solutes = secenekler()
karsi_segs = [s for s in segs if s not in CD_SEGMENTS]

c1, c2, c3 = st.columns(3)
solute = c1.selectbox("Solüt", solutes, index=solutes.index("Na"))
segment = c2.selectbox("Segment", karsi_segs)
compartment = c3.selectbox("Kompartman", ["Lumen", "Cell", "Bath"])

df = q(
    f"""SELECT position, value, nephron FROM {DB}
        WHERE condition=? AND variable='con' AND solute=? AND segment=? AND compartment=?
              AND nephron IN ('sup','jux1','jux2','jux3','jux4','jux5')
        ORDER BY nephron, position""",
    [senaryo, solute, segment, compartment],
)

if df.empty:
    st.warning(f"`{segment}` segmenti yalnız tek tip nefronda var.")
else:
    color_map = {"sup": "#dc2626", "jux1": "#93c5fd", "jux2": "#60a5fa",
                 "jux3": "#3b82f6", "jux4": "#2563eb", "jux5": "#1e3a8a"}
    fig = px.line(df, x="position", y="value", color="nephron",
                  title=f"{segment} — {solute} ({compartment}) — nefron tipine göre",
                  labels={"position": "Pozisyon (0–1)", "value": f"{solute} (mM)",
                          "nephron": "Nefron"},
                  color_discrete_map=color_map,
                  category_orders={"nephron": ["sup","jux1","jux2","jux3","jux4","jux5"]})
    fig.update_layout(hovermode="x unified", height=480)
    fig.update_traces(line=dict(width=2.5))
    st.plotly_chart(fig, use_container_width=True)
    cite_footer()

    with st.expander(f"📚 {segment} hakkında — bilgi & atıf"):
        seg = segment_info(segment)
        if seg:
            st.markdown(f"#### {seg.get('tam_ad', segment)}")
            if seg.get("ozet"):
                st.markdown(seg["ozet"])
            if seg.get("not"):
                st.info(f"💡 {seg['not']}")
            sayfa = seg.get("kaynak_sayfa") or "?"
            st.caption(f"📖 Kaynak: {atif_kisa(seg.get('kaynak_anahtar','turkmen2024'), sayfa)}")
