"""6_Veri_Butunlugu.py — Veritabani envanteri + bilinen sinirlar."""
import os
import streamlit as st
from ui_kit import setup_page, render_sidebar, q, DB, PARQUET

setup_page("Veri Bütünlüğü")
senaryo = render_sidebar()

st.markdown("## Veri Bütünlüğü Paneli")
st.caption(f"Kaynak: `{os.path.basename(PARQUET)}` · "
           f"Tüm senaryolar tek tidy Parquet'te birleşik tutuluyor.")

# Senaryo dagilimi
st.markdown("**Senaryo dağılımı**")
by_cond = q(f"SELECT condition AS senaryo, COUNT(*) AS satir FROM {DB} GROUP BY condition ORDER BY condition")
st.dataframe(by_cond, use_container_width=True, hide_index=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown("**Değişken kategorileri**")
    by_var = q(f"""
        SELECT variable AS değişken, COUNT(*) AS satır,
               COUNT(DISTINCT solute) AS solüt, COUNT(DISTINCT compartment) AS kompartman
        FROM {DB} GROUP BY variable ORDER BY satır DESC
    """)
    st.dataframe(by_var, use_container_width=True, hide_index=True)
with c2:
    st.markdown("**Segment dağılımı**")
    by_seg = q(f"""
        SELECT segment, COUNT(DISTINCT nephron) AS nefron_tipi, COUNT(*) AS satır
        FROM {DB} GROUP BY segment ORDER BY satır DESC
    """)
    st.dataframe(by_seg, use_container_width=True, hide_index=True)

st.markdown("**Nefron tipi dağılımı**")
by_neph = q(f"SELECT nephron, COUNT(*) AS satır FROM {DB} GROUP BY nephron ORDER BY satır DESC")
st.dataframe(by_neph, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("### Bilinen açık konular")

st.markdown("""
<div style="border:1px solid #bbf7d0;background:#f0fdf4;padding:12px 14px;border-radius:6px;margin-bottom:10px;">
  <b style="color:#166534;">Çözüldü ✓ — Çok-membranlı flux dosyaları membran başına ayrıldı</b><br>
  <span style="color:#374151;">CNT / CCD / OMCD'de bazı taşıyıcılar (AE1 = 2 membran,
  HATPase / HKATPase = 3 membran, NHE1 = 2 membran) tek dosyaya, içe içe geçmiş
  (interleaved) yazılır. Loader artık bunları stride ile ayrıştırıp her profili doğru
  pozisyon eksenine oturtuyor ve <code>membrane</code> kolonunda anatomik kompartman
  çiftiyle (örn. Lumen-ICA = A-tipi ara hücre apikal) etiketliyor. 6 senaryoda 246 dosya
  ayrıştırıldı. Detay: <code>notlar/bulgular.md</code>.</span>
</div>
<div style="border:1px solid #bfdbfe;background:#eff6ff;padding:12px 14px;border-radius:6px;margin-bottom:10px;">
  <b style="color:#1e40af;">Senaryo kütüphanesi 6/10 başarılı</b><br>
  <span style="color:#374151;">4 senaryo (F_diab_severe, F_ACE, F_obese, F_UNX) Newton çözücüsünde
  sayısal yakınsama hatası (np.exp overflow) verdi. Bu modelin <b>bilinen sınırı</b>,
  projenin hatası değil. İleride model'in solver'ı yumuşatılabilir.</span>
</div>
<div style="border:1px solid #bfdbfe;background:#eff6ff;padding:12px 14px;border-radius:6px;margin-bottom:10px;">
  <b style="color:#1e40af;">Birim belirsizlikleri</b><br>
  <span style="color:#374151;">pressure / diameter / length için birim kaynaktan teyit edilmedi.
  Diğer birimler README'den.</span>
</div>
<div style="border:1px solid #bfdbfe;background:#eff6ff;padding:12px 14px;border-radius:6px;">
  <b style="color:#1e40af;">Gradyan tepe değeri ~734 mOsm vs literatür ~1200</b><br>
  <span style="color:#374151;">İç medulla konsantrasyon mekanizmasının (MİH) matematiksel
  modellerce tam üretilememesi — bilinen açık problem. Detay: <code>notlar/bulgular.md</code>.</span>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Veri yapısı + atıfları: README ve `notlar/versiyonlar.md` dosyalarında.")
