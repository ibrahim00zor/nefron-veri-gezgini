"""7_Interaktif_Anatomi_BETA.py — Faz 4 D3.js Entegrasyon (v2)
Anatomik nefron diagrami: ozmolalite gradyan arka plani, akisa gore dinamik
kalinlik, ve konsantrasyon isi haritasi."""
import os
import json
import streamlit as st
import streamlit.components.v1 as components

from ui_kit import (
    setup_page, render_sidebar, q, DB,
    secenekler, NEPHRONS, segment_bozuk_mu, PROJ, CD_SEGMENTS
)

setup_page("İnteraktif Anatomi (BETA)")
senaryo_aktif = render_sidebar()

st.markdown("## İnteraktif Anatomi (BETA)")
st.caption(
    "D3.js tabanlı anatomik nefron çizimi. "
    "Segment renkleri seçilen solütün konsantrasyonunu (üstteki düğmeyle solüt **yüküne / akıya** çevrilebilir), "
    "segment kalınlıkları tübüler su akışını (hacim), "
    "arka plan gradyanı interstisyum ozmolalitesini yansıtır. "
    "Akış animasyonu parçacık hızıyla su akışını verir; bir segmente tıklayınca profili grafiğe sabitlenir."
)

# --- Ust seciciler ---
c1, c2, c3 = st.columns(3)
_, sol = secenekler()
solute = c1.selectbox("Solüt", sol, index=sol.index("Na") if "Na" in sol else 0)
compartment = c2.selectbox("Kompartman", ["Lumen", "Cell", "Bath"], index=0)
nephron_req = c3.selectbox(
    "Nefron tipi (CD segmentleri otomatik 'merged' olur)",
    NEPHRONS,
    index=NEPHRONS.index("sup"),
)

st.markdown("---")

# ============================================================
# 1) Konsantrasyon verisi (segment renkleri icin)
# ============================================================
cd_segs = CD_SEGMENTS
segments_data = {}

all_segs_raw = q(
    f"""SELECT DISTINCT segment FROM {DB}
        WHERE condition = ? AND variable='con' AND solute=?
        AND compartment=?""",
    [senaryo_aktif, solute, compartment]
)

for segment in all_segs_raw['segment'].tolist():
    target_nephron = "merged" if segment in cd_segs else nephron_req
    df_seg = q(
        f"""SELECT position, value FROM {DB}
            WHERE condition=? AND variable='con' AND solute=? AND compartment=?
            AND segment=? AND nephron=? ORDER BY position""",
        [senaryo_aktif, solute, compartment, segment, target_nephron]
    )
    if df_seg.empty or segment_bozuk_mu(senaryo_aktif, segment):
        continue
    if df_seg['value'].isna().any():
        continue
    segments_data[segment] = {
        "entry": float(df_seg['value'].iloc[0]),
        "exit": float(df_seg['value'].iloc[-1]),
        "mean": float(df_seg['value'].mean()),
        "profile": list(zip(
            df_seg['position'].round(4).tolist(),
            df_seg['value'].round(4).tolist()
        )),
    }

if not segments_data:
    st.warning("Seçilen filtreler için geçerli veri bulunamadı.")
    st.stop()

# Global min/max for color scale
all_vals = [v for s in segments_data.values() for v in (s["entry"], s["exit"])]
con_min = min(all_vals)
con_max = max(all_vals)

# ============================================================
# 2) Su hacmi (flow) verisi (segment kalinliklari icin)
# ============================================================
flow_data = {}
for segment in segments_data.keys():
    target_nephron = "merged" if segment in cd_segs else nephron_req
    df_flow = q(
        f"""SELECT position, value FROM {DB}
            WHERE condition=? AND variable='water_volume' AND compartment='Lumen'
            AND segment=? AND nephron=? ORDER BY position""",
        [senaryo_aktif, segment, target_nephron]
    )
    if not df_flow.empty and df_flow['value'].notna().all():
        flow_data[segment] = {
            "entry": float(df_flow['value'].iloc[0]),
            "exit": float(df_flow['value'].iloc[-1]),
            "mean": float(df_flow['value'].mean()),
        }

# Global flow min/max for thickness scale
all_flows = [v for s in flow_data.values() for v in (s["entry"], s["exit"])]
flow_min = min(all_flows) if all_flows else 0
flow_max = max(all_flows) if all_flows else 100

# ============================================================
# 2b) Solut YUKU (load = molar aki, pmol/min) — renk modu icin
# ============================================================
# Konsantrasyon yaniltir; emilim/iletim icin KUTLE (aki) bakilir. Bu mod, sayfa 8
# bilim-denetimindeki "altin kural"i diagramda gorsel kilar.
load_data = {}
for segment in segments_data.keys():
    target_nephron = "merged" if segment in cd_segs else nephron_req
    df_load = q(
        f"""SELECT position, value FROM {DB}
            WHERE condition=? AND variable='flow' AND solute=? AND compartment='Lumen'
            AND segment=? AND nephron=? ORDER BY position""",
        [senaryo_aktif, solute, segment, target_nephron]
    )
    if not df_load.empty and df_load['value'].notna().all():
        load_data[segment] = {
            "entry": float(df_load['value'].iloc[0]),
            "exit": float(df_load['value'].iloc[-1]),
            "mean": float(df_load['value'].mean()),
            "profile": list(zip(
                df_load['position'].round(4).tolist(),
                df_load['value'].round(2).tolist()
            )),
        }

all_loads = [v for s in load_data.values() for v in (s["entry"], s["exit"])]
load_min = min(all_loads) if all_loads else 0
load_max = max(all_loads) if all_loads else 100

# ============================================================
# 3) Interstisyum (Bath) ozmolalite gradyani (arka plan icin)
# ============================================================
# Kortikal segmentler (sup), medullar segmentler (sup veya merged CD)
# Amac: derinlige (y-koordinatina) gore ozmolalite gradyani
gradient_segments = [
    ("PT",   "sup",    0.0),   # Korteks ust
    ("cTAL", "sup",    0.15),  # Korteks alt
    ("S3",   "sup",    0.28),  # Dis medulla ust siniri
    ("mTAL", "sup",    0.40),  # Dis medulla orta
    ("SDL",  "sup",    0.55),  # Dis medulla alt
    ("OMCD", "merged", 0.55),  # Dis-ic medulla siniri
    ("IMCD", "merged", 1.0),   # Papilla (en dip)
]

gradient_stops = []
for seg, neph, frac in gradient_segments:
    df_osm = q(
        f"""SELECT AVG(value) as avg_osm FROM {DB}
            WHERE condition=? AND variable='osmolality' AND compartment='Bath'
            AND segment=? AND nephron=?""",
        [senaryo_aktif, seg, neph]
    )
    if not df_osm.empty and df_osm['avg_osm'].notna().iloc[0]:
        gradient_stops.append({
            "frac": frac,
            "osm": round(float(df_osm['avg_osm'].iloc[0]), 1),
        })

# ============================================================
# 4) JSON paketini hazirla
# ============================================================
injected_data = {
    "solute": solute,
    "con_min": round(con_min, 2),
    "con_max": round(con_max, 2),
    "flow_min": round(flow_min, 2),
    "flow_max": round(flow_max, 2),
    "load_min": round(load_min, 2),
    "load_max": round(load_max, 2),
    "segments": segments_data,
    "flow": flow_data,
    "load": load_data,
    "gradient_stops": gradient_stops,
    "nephron_type": nephron_req,
}

# ============================================================
# 5) D3.js HTML sablonunu oku ve veriyi enjekte et
# ============================================================
html_path = os.path.join(PROJ, "kod", "d3_components", "nephron_diagram.html")
try:
    with open(html_path, "r", encoding="utf-8") as f:
        html_template = f.read()
except FileNotFoundError:
    st.error(f"HTML şablonu bulunamadı: {html_path}")
    st.stop()

json_str = json.dumps(injected_data, ensure_ascii=False)
html_rendered = html_template.replace("__INJECTED_DATA__", json_str)

components.html(html_rendered, height=870, scrolling=False)

# Model siniri notu (kullanicinin istegi: kisa, belirgin olmasin, uzerine dusen bulsun)
st.caption(
    "ℹ Arka plan gradyanı modelin hesapladığı interstisyum ozmolalitesine dayanır. "
    "Layton/Hu modelinde papilla ozmolalitesi ~734 mOsm ile sınırlıdır; "
    "in vivo değer ~1200 mOsm'dir (bilinen model sınırı, bkz. bulgular.md §0)."
)
