"""
app.py — Nefron Veri Gezgini (profesyonel surum v2)
Calistir:  cd ~/Desktop/Nefron-Projesi && streamlit run kod/app.py
"""
import os
import sys
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.io as pio

# Kendi modüllerimiz (kod/ klasöründen)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from egitim_icerigi import segment_info, atif_kisa, atif_tam, ATIFLAR
from yorum_motoru import yorumla

# ============================================================
#  Sayfa kurulumu + tema
# ============================================================
st.set_page_config(
    page_title="Nefron Veri Gezgini",
    page_icon="◐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Plotly icin temiz, klinik gorunumlu sablon
pio.templates["nefron"] = pio.templates["simple_white"]
pio.templates["nefron"].layout.update(
    font=dict(family="Inter, system-ui, -apple-system, sans-serif", size=13, color="#1f2937"),
    title=dict(font=dict(size=15, color="#111827")),
    colorway=["#2563eb", "#dc2626", "#059669", "#d97706", "#7c3aed", "#0891b2", "#be185d"],
    hoverlabel=dict(bgcolor="white", bordercolor="#e5e7eb", font=dict(size=12)),
    margin=dict(l=50, r=20, t=50, b=50),
    xaxis=dict(gridcolor="#f3f4f6", zerolinecolor="#e5e7eb"),
    yaxis=dict(gridcolor="#f3f4f6", zerolinecolor="#e5e7eb"),
)
pio.templates.default = "nefron"

# Hafif CSS rotuslari
st.markdown("""
<style>
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }
  h1, h2, h3 { letter-spacing: -0.01em; }
  div[data-testid="stMetricValue"] { font-size: 1.4rem; }
  div[data-testid="stMetricLabel"] { font-size: 0.85rem; color: #4b5563; }
  .stTabs [data-baseweb="tab-list"] { gap: 4px; }
  .stTabs [data-baseweb="tab"] { padding: 0.5rem 1rem; }
  hr { margin: 1rem 0; border-color: #e5e7eb; }
</style>
""", unsafe_allow_html=True)

# ============================================================
#  Yollar + sabitler
# ============================================================
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARQUET = os.path.join(PROJ, "veri", "nephron_veritabani.parquet")
DB = f"read_parquet('{PARQUET}')"

SEG_ORDER_SUP = ["PT", "S3", "SDL", "mTAL", "cTAL", "DCT", "CNT", "CCD", "OMCD", "IMCD"]
SEG_ORDER_JUX = ["PT", "S3", "SDL", "LDL", "LAL", "mTAL", "cTAL", "DCT", "CNT", "CCD", "OMCD", "IMCD"]
NEPHRONS = ["sup", "jux1", "jux2", "jux3", "jux4", "jux5", "merged"]
CD_SEGMENTS = {"CCD", "OMCD", "IMCD"}

# Senaryo etiketleri — insan-okunabilir görünüm
SENARYO_AD = {
    "F_normal":   "👩 Sağlıklı kadın (baseline)",
    "M_normal":   "👨 Sağlıklı erkek (baseline)",
    "F_diab_mod": "👩 + Diyabet (orta)",
    "F_HT":       "👩 + Hipertansiyon",
    "F_SGLT2":    "👩 + SGLT2 inhibitörü (gliflozin)",
    "M_SGLT2":    "👨 + SGLT2 inhibitörü (gliflozin)",
}

# Eski SEG_INFO dict kaldırıldı — içerik artık kod/egitim_icerigi.py'de
# (yapılandırılmış, kullanıcının kendi cümlelerini doldurabileceği biçimde)


def render_segment_info(segment_kod):
    """Bir segmentin tüm eğitim içeriğini Streamlit'te gösterir."""
    seg = segment_info(segment_kod)
    if not seg:
        st.caption("_Bu segment için içerik henüz tanımlanmadı._")
        return
    st.markdown(f"### {seg.get('tam_ad', segment_kod)}")
    ozet = seg.get("ozet", "").strip()
    if ozet:
        st.markdown(ozet)
    else:
        st.caption("_Özet henüz yazılmadı — `kod/egitim_icerigi.py` içinden doldurulacak "
                   "(kendi cümlelerinle, Türkmen 2024'ten paraphrase)._")
    if seg.get("not"):
        st.info(f"💡 {seg['not']}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Apikal (lümen tarafı)**")
        items = seg.get("apikal", [])
        if items:
            for t in items:
                st.markdown(f"- {t}")
        else:
            st.caption("—")
    with c2:
        st.markdown("**Bazolateral (kan tarafı)**")
        items = seg.get("bazolateral", [])
        if items:
            for t in items:
                st.markdown(f"- {t}")
        else:
            st.caption("—")

    sayfa = seg.get("kaynak_sayfa") or "?"
    anahtar = seg.get("kaynak_anahtar", "turkmen2024")
    st.caption(f"📖 Kaynak: {atif_kisa(anahtar, sayfa)}")

# ============================================================
#  Sorgu yardimcilari
# ============================================================
@st.cache_data
def q(sql, params=None):
    return duckdb.connect().execute(sql, params or []).df()

@st.cache_data
def secenekler():
    seg = q(f"SELECT DISTINCT segment FROM {DB}")["segment"].tolist()
    sol = q(f"SELECT DISTINCT solute FROM {DB} WHERE solute IS NOT NULL")["solute"].tolist()
    return sorted(seg), sorted(sol)

@st.cache_data
def saglik_metrikleri():
    return q(f"""
        SELECT COUNT(*) AS satir,
               COUNT(DISTINCT segment) AS segment,
               (SELECT COUNT(DISTINCT solute) FROM {DB} WHERE solute IS NOT NULL) AS solut,
               COUNT(DISTINCT variable) AS degisken,
               COUNT(DISTINCT nephron) AS nefron
        FROM {DB}
    """).iloc[0]

def neph_for(segment, requested):
    return "merged" if segment in CD_SEGMENTS else requested

def chart_yap(df, x, y, color, title, xlab, ylab, color_label="Seri", category_orders=None, height=460):
    fig = px.line(df, x=x, y=y, color=color,
                  title=title,
                  labels={x: xlab, y: ylab, color: color_label},
                  category_orders=category_orders or {})
    fig.update_layout(hovermode="x unified", height=height, legend=dict(title_text=color_label))
    fig.update_traces(line=dict(width=2.5))
    return fig

# ============================================================
#  Yan panel — proje baglami
# ============================================================
with st.sidebar:
    st.markdown("### Nefron Veri Gezgini")
    st.caption("Layton/Hu insan nefron modeli üzerine inşa edilmiş interaktif veri arayüzü.")

    # === SENARYO SEÇİCİ ===
    senaryolar_listesi = q(f"SELECT DISTINCT condition FROM {DB} ORDER BY condition")["condition"].tolist()
    senaryo = st.selectbox(
        "🧪 Aktif senaryo",
        senaryolar_listesi,
        format_func=lambda s: SENARYO_AD.get(s, s),
        index=senaryolar_listesi.index("F_normal") if "F_normal" in senaryolar_listesi else 0,
        key="senaryo_secimi",
        help="Tüm grafikler ve doğrulamalar bu senaryo için filtrelenir.",
    )
    st.caption(f"📋 Senaryo kodu: `{senaryo}` — bu seçim tüm sekmelerde aktif.")
    st.markdown("---")

    st.warning(
        "**Doğrulanmamış: `flux` (taşıyıcı akı) verisi**\n\n"
        "CCD'deki bazı taşıyıcılar (AE1, HATPase, HKATPase) birden çok hücre tipi "
        "membranı barındırır; bu dosyalar tek profil olarak yorumlanıyor → pozisyon "
        "ekseninde yanlış görüntülenebilir. Düzeltilene dek `flux` çıktılarını "
        "**doğrulama referansı olarak kullanma.** Detay: `Veri Bütünlüğü` sekmesi."
    )

    sb = saglik_metrikleri()
    c1, c2 = st.columns(2)
    c1.metric("Satır", f"{sb['satir']:,}")
    c2.metric("Değişken", f"{sb['degisken']}")
    c1.metric("Segment", f"{sb['segment']}")
    c2.metric("Nefron tipi", f"{sb['nefron']}")

    st.markdown("---")
    with st.expander("Veri kaynağı"):
        st.markdown(
            "**Model:** Layton Lab — `github.com/mstadt/nephron`\n\n"
            "**Atıf:** Hu et al. 2021. *Sex differences in solute and water handling "
            "in the human kidney.* iScience 24(6):102694.\n\n"
            "**Veri:** Kadın, insan, normal (sup + jux1–5 + merged toplayıcı kanal)."
        )
    with st.expander("Proje notları"):
        st.markdown(
            "- `notlar/gunluk.md` — kronolojik proje günlüğü\n"
            "- `notlar/bulgular.md` — bilimsel kararlar\n"
            "- `notlar/terminoloji.md` — sözlük\n"
            "- `yedekler/` — zaman damgalı yedekler"
        )
    with st.expander("Birimler"):
        st.markdown(
            "Konsantrasyon: **mM** · Akı: **pmol/min** · Hacim: **nl/min** · "
            "Ozmolalite: **mOsm** · Potansiyel: **mV**"
        )

# ============================================================
#  Ust kismi: baslik
# ============================================================
st.title("Nefron Veri Gezgini")
st.caption(f"Layton/Hu insan nefron modeli  ·  veri: `{os.path.basename(PARQUET)}`")
st.markdown("---")

segs, solutes = secenekler()

tab_segment, tab_full, tab_neph, tab_verify, tab_integrity = st.tabs([
    "Segment Profili",
    "Tüm Nefron",
    "Nefron Tipleri",
    "Doğrulamalar",
    "Veri Bütünlüğü",
])

# ============================================================
#  SEKME 1: Segment Profili
# ============================================================
with tab_segment:
    st.markdown("### Tek segment boyunca konsantrasyon profili")

    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.2])
    solute = c1.selectbox("Solüt", solutes, index=solutes.index("Na"), key="s1_sol")
    segment = c2.selectbox("Segment", segs, key="s1_seg")
    nephron_req = c3.selectbox("Nefron", NEPHRONS, key="s1_neph")
    show_bath = c4.checkbox("Bath (interstisyum) üstüne bindir", value=True, key="s1_bath")

    nephron = neph_for(segment, nephron_req)
    if nephron != nephron_req:
        st.info(f"`{segment}` toplayıcı kanal segmenti — nefron otomatik **merged** alındı.")

    comps = ["Lumen", "Bath"] if show_bath else ["Lumen"]
    df = q(
        f"""SELECT position, value, compartment FROM {DB}
            WHERE condition=? AND variable='con' AND solute=? AND segment=? AND nephron=?
                  AND compartment IN ({','.join(['?']*len(comps))})
            ORDER BY position""",
        [senaryo, solute, segment, nephron, *comps],
    )

    if df.empty:
        st.warning(f"Veri yok: `{segment}` segmenti `{nephron}` nefronda mevcut değil "
                   f"(örn: LDL/LAL yalnız jux nefronlarda).")
    else:
        # Mini-ozet ust kart
        lumen = df[df.compartment == "Lumen"]
        if not lumen.empty:
            g, c = lumen["value"].iloc[0], lumen["value"].iloc[-1]
            m1, m2, m3 = st.columns(3)
            m1.metric(f"{solute} giriş", f"{g:.2f} mM")
            m2.metric(f"{solute} çıkış", f"{c:.2f} mM", f"{(c-g)/g*100:+.1f} %")
            m3.metric("Dilim sayısı", f"{len(lumen)}")

        fig = chart_yap(df, "position", "value", "compartment",
                        f"{segment} — {solute} ({nephron})",
                        "Segment-içi pozisyon  (0 = giriş, 1 = çıkış)",
                        f"{solute} (mM)", color_label="Kompartman")
        st.plotly_chart(fig, use_container_width=True)

        # --- Otomatik fizyolojik yorum (kütle vs hacim analizi) ---
        lumen_df = df[df["compartment"] == "Lumen"].sort_values("position")
        if len(lumen_df) >= 2:
            vol_df = q(
                f"""SELECT position, value FROM {DB}
                    WHERE condition=? AND variable='water_volume' AND segment=? AND nephron=?
                          AND compartment='Lumen'
                    ORDER BY position""",
                [senaryo, segment, nephron],
            )
            if len(vol_df) >= 2:
                yorum = yorumla(
                    con_giris=float(lumen_df["value"].iloc[0]),
                    con_cikis=float(lumen_df["value"].iloc[-1]),
                    vol_giris=float(vol_df["value"].iloc[0]),
                    vol_cikis=float(vol_df["value"].iloc[-1]),
                    solut=solute,
                )
                st.info(f"🔬 **Otomatik fizyolojik yorum:** {yorum}")
                st.caption(
                    "_Bu yorum, konsantrasyon = kütle / hacim ilişkisinden hesaplanır. "
                    "LDL'deki gibi sezgi-aksi durumları yakalar._"
                )

        # --- Eğitim içeriği expander ---
        with st.expander(f"📚 Bu segment hakkında — {segment}", expanded=False):
            render_segment_info(segment)

        with st.expander("📥 Veriyi indir / özet tablo"):
            ozet = df.groupby("compartment")["value"].agg(["min", "max", "mean"]).round(3)
            st.dataframe(ozet, use_container_width=False)
            st.download_button("CSV indir", df.to_csv(index=False).encode("utf-8"),
                               file_name=f"{segment}_{solute}_{nephron}.csv", mime="text/csv")

# ============================================================
#  SEKME 2: Tum Nefron
# ============================================================
with tab_full:
    st.markdown("### Tüm nefron boyunca akış (PT → IMCD)")
    st.caption("Segmentler fizyolojik sırada yan yana çizilir. Dikey kesik çizgiler segment sınırlarıdır.")

    c1, c2, c3 = st.columns(3)
    solute = c1.selectbox("Solüt", solutes, index=solutes.index("Na"), key="s2_sol")
    compartment = c2.selectbox("Kompartman", ["Lumen", "Cell", "Bath"], key="s2_comp")
    nephron = c3.selectbox("Nefron tipi", ["sup", "jux1", "jux2", "jux3", "jux4", "jux5"], key="s2_neph")

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
        if d.empty: continue
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

        with st.expander("Segment-bazlı özet (giriş → çıkış)"):
            ozet = (full.sort_values(["segment", "x"])
                       .groupby("segment").agg(giris=("value", "first"),
                                              cikis=("value", "last")).round(2)
                       .reindex(order).dropna())
            ozet["oran"] = (ozet["cikis"] / ozet["giris"]).round(2)
            st.dataframe(ozet, use_container_width=True)

# ============================================================
#  SEKME 3: Nefron Tipleri
# ============================================================
with tab_neph:
    st.markdown("### Nefron tiplerini yan yana karşılaştır")
    st.caption("Aynı segment + solüt + kompartman için sup ve jux1–5 üst üste çizilir. "
               "Derin nefronlar (jux5) medullaya en çok inenler.")

    c1, c2, c3 = st.columns(3)
    solute = c1.selectbox("Solüt", solutes, index=solutes.index("Na"), key="s3_sol")
    karsi_segs = [s for s in segs if s not in CD_SEGMENTS]
    segment = c2.selectbox("Segment", karsi_segs, key="s3_seg")
    compartment = c3.selectbox("Kompartman", ["Lumen", "Cell", "Bath"], key="s3_comp")

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
        # Renkleri jux1→jux5 derinlik sirasinda azalan koyulukta kullanmak icin
        # bagimsiz renkler atanir; sup kirmizi, jux mavi tonlari.
        color_map = {"sup":"#dc2626", "jux1":"#93c5fd", "jux2":"#60a5fa",
                     "jux3":"#3b82f6", "jux4":"#2563eb", "jux5":"#1e3a8a"}
        fig = px.line(df, x="position", y="value", color="nephron",
                      title=f"{segment} — {solute} ({compartment}) — nefron tipine göre",
                      labels={"position":"Pozisyon (0 – 1)", "value":f"{solute} (mM)",
                              "nephron":"Nefron"},
                      color_discrete_map=color_map,
                      category_orders={"nephron":["sup","jux1","jux2","jux3","jux4","jux5"]})
        fig.update_layout(hovermode="x unified", height=480)
        fig.update_traces(line=dict(width=2.5))
        st.plotly_chart(fig, use_container_width=True)

        with st.expander(f"📚 Bu segment hakkında — {segment}"):
            render_segment_info(segment)

# ============================================================
#  SEKME 4: Dogrulamalar
# ============================================================
with tab_verify:
    st.markdown("### Otomatik fizyoloji doğrulamaları")
    st.caption("Veri açıldığında ders kitabı beklentileri otomatik test edilir.")

    def scalar(sql, params=None):
        # Otomatik condition filtresi (seçili senaryoyu zorunlu kılar)
        if "condition=" not in sql:
            sql = sql.replace("WHERE ", f"WHERE condition='{senaryo}' AND ", 1)
        r = q(sql, params or [])
        return None if r.empty else float(r["value"].iloc[0])

    st.caption(f"_Doğrulamalar **{SENARYO_AD.get(senaryo, senaryo)}** senaryosu için yapılıyor. "
               f"Bazı kontroller hastalık/ilaç senaryosunda farklı sonuç verebilir — bu **bilgi**, hata değil._")

    checks = []
    add = checks.append

    v = scalar(f"SELECT value FROM {DB} WHERE variable='osmolality' AND segment='PT' "
               f"AND compartment='Lumen' AND nephron='sup' AND position=0")
    add(("Glomerül filtratı ≈ plazma", f"{v:.1f} mOsm", "Hedef: 290–310", 290 <= v <= 310)) if v else None

    a = scalar(f"SELECT value FROM {DB} WHERE variable='osmolality' AND segment='PT' "
               f"AND compartment='Lumen' AND nephron='sup' AND position=0")
    b = scalar(f"SELECT value FROM {DB} WHERE variable='osmolality' AND segment='PT' "
               f"AND compartment='Lumen' AND nephron='sup' AND position=1")
    add(("PT izoozmotik", f"{a:.1f} → {b:.1f}", "|fark| < 10", abs(b-a) < 10)) if a and b else None

    a = scalar(f"SELECT value FROM {DB} WHERE variable='con' AND solute='Na' AND segment='mTAL' "
               f"AND compartment='Lumen' AND nephron='sup' AND position=0")
    b = scalar(f"SELECT value FROM {DB} WHERE variable='con' AND solute='Na' AND segment='mTAL' "
               f"AND compartment='Lumen' AND nephron='sup' AND position=1")
    add(("mTAL dilüsyon (lümen Na)", f"{a:.0f} → {b:.0f} mM", "çıkış < giriş", b < a)) if a and b else None

    a = scalar(f"SELECT value FROM {DB} WHERE variable='flux' AND transporter='NKCC2A' AND solute='Na' "
               f"AND segment='mTAL' AND nephron='sup' AND position=0")
    b = scalar(f"SELECT value FROM {DB} WHERE variable='flux' AND transporter='NKCC2A' AND solute='Cl' "
               f"AND segment='mTAL' AND nephron='sup' AND position=0")
    if a and b and a != 0:
        r = b / a
        add(("NKCC2A stokiyometri", f"Cl/Na = {r:.2f}", "Hedef: 1.8–2.2", 1.8 < r < 2.2))

    a = scalar(f"SELECT value FROM {DB} WHERE variable='osmolality' AND segment='CCD' "
               f"AND compartment='Bath' AND nephron='merged' AND position=0")
    b = scalar(f"SELECT value FROM {DB} WHERE variable='osmolality' AND segment='IMCD' "
               f"AND compartment='Bath' AND nephron='merged' AND position=1")
    if a and b:
        add(("Kortikomedüller gradyan (Bath)", f"{a:.0f} → {b:.0f} (×{b/a:.2f})",
             "Hedef: en az ×2", b > 2*a))

    v = scalar(f"SELECT value FROM {DB} WHERE variable='osmolality' AND segment='IMCD' "
               f"AND compartment='Lumen' AND nephron='merged' AND position=1")
    add(("İdrar hiperozmolar (ADH etkin)", f"{v:.0f} mOsm", "> plazma (300)", v > 300)) if v else None

    a = scalar(f"SELECT value FROM {DB} WHERE variable='con' AND solute='urea' AND segment='LDL' "
               f"AND compartment='Lumen' AND nephron='jux5' AND position=0")
    b = scalar(f"SELECT value FROM {DB} WHERE variable='con' AND solute='urea' AND segment='LDL' "
               f"AND compartment='Lumen' AND nephron='jux5' AND position=1")
    if a and b:
        add(("Üre geri dönüşümü (LDL jux5)", f"{a:.1f} → {b:.1f} (×{b/a:.1f})",
             "Hedef: en az ×2", b > 2*a))

    a = scalar(f"SELECT value FROM {DB} WHERE variable='con' AND solute='NH3' AND segment='LDL' "
               f"AND compartment='Lumen' AND nephron='jux5' AND position=1")
    b = scalar(f"SELECT value FROM {DB} WHERE variable='con' AND solute='NH3' AND segment='LDL' "
               f"AND compartment='Bath' AND nephron='jux5' AND position=1")
    if a and b:
        add(("NH3 lümen ≈ Bath (LDL çıkış)", f"L={a:.3f} · B={b:.3f}",
             "fark < %15", abs(a-b)/max(a,b) < 0.15))

    a = scalar(f"SELECT value FROM {DB} WHERE variable='con' AND solute='Na' AND segment='mTAL' "
               f"AND compartment='Lumen' AND nephron='sup' AND position=1")
    b = scalar(f"SELECT value FROM {DB} WHERE variable='con' AND solute='Na' AND segment='cTAL' "
               f"AND compartment='Lumen' AND nephron='sup' AND position=0")
    if a and b and a != 0:
        add(("Segment zincirleme (mTAL → cTAL)", f"{a:.1f} = {b:.1f}",
             "fark < %2", abs(a-b)/a < 0.02))

    # Ust metrik
    passed = sum(1 for *_, ok in checks if ok)
    total = len(checks)
    pct = passed/total*100 if total else 0
    m1, m2, m3 = st.columns(3)
    m1.metric("Geçen", f"{passed} / {total}")
    m2.metric("Başarı", f"{pct:.0f} %")
    m3.metric("Senaryo", senaryo)

    st.markdown("---")
    # Kontroller 2 sutunlu kart gridi
    cols = st.columns(2)
    for i, (ad, deger, hedef, ok) in enumerate(checks):
        with cols[i % 2]:
            icon = "✓" if ok else "✗"
            renk = "#059669" if ok else "#dc2626"
            st.markdown(f"""
            <div style="border: 1px solid #e5e7eb; border-left: 4px solid {renk};
                        padding: 10px 14px; border-radius: 6px; margin-bottom: 10px;
                        background: white;">
              <div style="display:flex; justify-content:space-between; align-items:start;">
                <div style="font-weight: 600; color: #111827;">{ad}</div>
                <div style="color:{renk}; font-weight: 700; font-size: 1.1rem;">{icon}</div>
              </div>
              <div style="margin-top:4px; color:#374151; font-family: ui-monospace, monospace;">{deger}</div>
              <div style="margin-top:2px; color:#6b7280; font-size: 0.8rem;">{hedef}</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
#  SEKME 5: Veri Butunlugu
# ============================================================
with tab_integrity:
    st.markdown("### Veri bütünlüğü paneli")
    st.caption(f"Kaynak: `{os.path.basename(PARQUET)}`  ·  Veri Layton/Hu modelinin tek koşusundan üretildi.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Değişken kategorileri**")
        by_var = q(f"""
            SELECT variable, COUNT(*) AS satir,
                   COUNT(DISTINCT solute) AS solut,
                   COUNT(DISTINCT compartment) AS kompartman
            FROM {DB} GROUP BY variable ORDER BY satir DESC
        """)
        st.dataframe(by_var, use_container_width=True, hide_index=True)
    with c2:
        st.markdown("**Segment dağılımı**")
        by_seg = q(f"""
            SELECT segment, COUNT(DISTINCT nephron) AS nefron_tipi, COUNT(*) AS satir
            FROM {DB} GROUP BY segment ORDER BY satir DESC
        """)
        st.dataframe(by_seg, use_container_width=True, hide_index=True)

    st.markdown("**Nefron tipi dağılımı**")
    by_neph = q(f"SELECT nephron, COUNT(*) AS satir FROM {DB} GROUP BY nephron ORDER BY satir DESC")
    st.dataframe(by_neph, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### Bilinen açık konular")

    st.markdown("""
    <div style="border:1px solid #fde68a; background:#fffbeb; padding:12px 14px; border-radius:6px; margin-bottom:10px;">
      <b style="color:#92400e;">Çok-membranlı flux dosyaları</b><br>
      <span style="color:#374151;">CCD'de bazı taşıyıcılar (AE1 = 2 membran, HATPase/HKATPase = 3 membran)
      tek dosyada birden çok membran profili barındırır. Loader şu an bu 41 dosyayı tek profil
      sayıyor; membran başına ayırma görev #4'te yapılacak.</span>
    </div>
    <div style="border:1px solid #bfdbfe; background:#eff6ff; padding:12px 14px; border-radius:6px; margin-bottom:10px;">
      <b style="color:#1e40af;">Birim belirsizlikleri</b><br>
      <span style="color:#374151;">pressure / diameter / length için birim kaynaktan teyit edilmedi
      (etiket = 'unknown'). Diğer birimler README'den.</span>
    </div>
    <div style="border:1px solid #bfdbfe; background:#eff6ff; padding:12px 14px; border-radius:6px;">
      <b style="color:#1e40af;">Gradyan tepe değeri ~734 mOsm vs literatür ~1200</b><br>
      <span style="color:#374151;">İç medulla konsantrasyon mekanizmasının (MİH) matematiksel
      modellerce tam üretilememesi — bilinen açık problem. Detay: <code>notlar/bulgular.md</code>.</span>
    </div>
    """, unsafe_allow_html=True)
