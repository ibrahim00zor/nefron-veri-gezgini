"""1_Segment_Profili.py — Tek segment, tek solut profili."""
import streamlit as st
from ui_kit import (
    setup_page, render_sidebar, q, DB, chart_yap, cite_footer, neph_for,
    secenekler, NEPHRONS, gecerli_veri, segment_bozuk_mu,
)
from egitim_icerigi import segment_info, atif_kisa
from yorum_motoru import yorumla

setup_page("Segment Profili")
senaryo = render_sidebar()

st.markdown("## Segment Profili")
st.caption("Tek segmentte tek solütün pozisyon boyunca değişimi. Lumen + Bath bindirilebilir; "
           "her grafiğin altında otomatik kütle/hacim yorumu görünür.")

segs, solutes = secenekler()

c1, c2, c3, c4 = st.columns([1, 1, 1, 1.2])
solute      = c1.selectbox("Solüt",  solutes, index=solutes.index("Na"))
segment     = c2.selectbox("Segment", segs)
nephron_req = c3.selectbox("Nefron",  NEPHRONS)
show_bath   = c4.checkbox("Bath bindir", value=True)
nephron     = neph_for(segment, nephron_req)

if nephron != nephron_req:
    st.info(f"`{segment}` toplayıcı kanal segmenti → nefron otomatik **merged**.")

comps = ["Lumen", "Bath"] if show_bath else ["Lumen"]
df = q(
    f"""SELECT position, value, compartment FROM {DB}
        WHERE condition=? AND variable='con' AND solute=? AND segment=? AND nephron=?
              AND compartment IN ({','.join(['?']*len(comps))})
        ORDER BY position""",
    [senaryo, solute, segment, nephron, *comps],
)

df_raw = df
seg_bozuk = segment_bozuk_mu(senaryo, segment)
atilan = 0
if seg_bozuk:
    df = df.iloc[0:0]          # tum segment gizlenir (kesik egri birakma)
else:
    df, atilan = gecerli_veri(df, "con")

if df.empty:
    if seg_bozuk:
        st.warning(f"`{segment}` bu senaryoda sayısal olarak **yakınsamadı** — veri gizlendi. "
                   f"(Toplayıcı kanal çözüm hatası; bu segment için temiz bir senaryo seç. "
                   f"Detay: Veri Bütünlüğü sayfası.)")
    else:
        st.warning(f"Veri yok: `{segment}` segmenti `{nephron}` nefronda yok "
                   f"(LDL/LAL yalnız jux nefronlarda var).")
else:
    if atilan:
        st.warning(f"{atilan} geçersiz nokta (yakınsama hatası) gizlendi; "
                   f"aşağıda gösterilen veri güvenilir.")
    lumen = df[df.compartment == "Lumen"]
    if not lumen.empty:
        g, c = lumen["value"].iloc[0], lumen["value"].iloc[-1]
        m1, m2, m3 = st.columns(3)
        m1.metric(f"{solute} giriş", f"{g:.2f} mM")
        m2.metric(f"{solute} çıkış", f"{c:.2f} mM", f"{(c-g)/g*100:+.1f} %")
        m3.metric("Dilim", f"{len(lumen)}")

    fig = chart_yap(df, "position", "value", "compartment",
                    f"{segment} — {solute} ({nephron})",
                    "Segment-içi pozisyon (0 = giriş, 1 = çıkış)",
                    f"{solute} (mM)", color_label="Kompartman")
    st.plotly_chart(fig, use_container_width=True)

    # Otomatik fizyolojik yorum
    if len(lumen) >= 2:
        vol_df = q(
            f"""SELECT position, value FROM {DB}
                WHERE condition=? AND variable='water_volume' AND segment=? AND nephron=?
                      AND compartment='Lumen' ORDER BY position""",
            [senaryo, segment, nephron],
        )
        if len(vol_df) >= 2:
            yorum = yorumla(
                con_giris=float(lumen["value"].iloc[0]),
                con_cikis=float(lumen["value"].iloc[-1]),
                vol_giris=float(vol_df["value"].iloc[0]),
                vol_cikis=float(vol_df["value"].iloc[-1]),
                solut=solute,
            )
            st.info(f"**Otomatik fizyolojik yorum:** {yorum}")

    cite_footer()

    # Eğitim içeriği expander
    with st.expander(f"{segment} hakkında — bilgi ve atıf"):
        seg = segment_info(segment)
        if seg:
            st.markdown(f"#### {seg.get('tam_ad', segment)}")
            ozet = seg.get("ozet", "").strip()
            if ozet:
                st.markdown(ozet)
            else:
                st.caption("_Özet henüz yazılmadı — `kod/egitim_icerigi.py` içinden doldurulacak._")
            if seg.get("not"):
                st.info(f"Not: {seg['not']}")
            a, b = st.columns(2)
            with a:
                st.markdown("**Apikal (lümen)**")
                for t in seg.get("apikal", []) or ["—"]:
                    st.markdown(f"- {t}")
            with b:
                st.markdown("**Bazolateral (kan)**")
                for t in seg.get("bazolateral", []) or ["—"]:
                    st.markdown(f"- {t}")
            sayfa = seg.get("kaynak_sayfa") or "?"
            st.caption(f"Kaynak: {atif_kisa(seg.get('kaynak_anahtar','turkmen2024'), sayfa)}")

    with st.expander("CSV indir ve özet tablo"):
        ozet = df.groupby("compartment")["value"].agg(["min", "max", "mean"]).round(3)
        st.dataframe(ozet)
        st.download_button("CSV indir", df.to_csv(index=False).encode("utf-8"),
                           file_name=f"{senaryo}_{segment}_{solute}_{nephron}.csv",
                           mime="text/csv")
