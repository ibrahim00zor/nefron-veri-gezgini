"""5_Dogrulamalar.py — Otomatik fizyoloji kontrolleri."""
import streamlit as st
from ui_kit import setup_page, render_sidebar, DB, scalar, SENARYO_AD

setup_page("Doğrulamalar", "✅")
senaryo = render_sidebar()

st.markdown("## ✅ Otomatik Fizyoloji Doğrulamaları")
st.caption(f"Aktif senaryo: **{SENARYO_AD.get(senaryo, senaryo)}**. "
           f"Bazı kontroller hastalık/ilaç senaryosunda farklı sonuç verebilir — "
           f"bu **bilgi**, hata değil.")

checks = []
add = checks.append

# 1. Filtrat ~ plazma
v = scalar(f"SELECT value FROM {DB} WHERE variable='osmolality' AND segment='PT' "
           f"AND compartment='Lumen' AND nephron='sup' AND position=0", senaryo)
if v: add(("Glomerül filtratı ≈ plazma", f"{v:.1f} mOsm", "Hedef: 290–310", 290 <= v <= 310))

# 2. PT izoozmotik
a = scalar(f"SELECT value FROM {DB} WHERE variable='osmolality' AND segment='PT' "
           f"AND compartment='Lumen' AND nephron='sup' AND position=0", senaryo)
b = scalar(f"SELECT value FROM {DB} WHERE variable='osmolality' AND segment='PT' "
           f"AND compartment='Lumen' AND nephron='sup' AND position=1", senaryo)
if a and b: add(("PT izoozmotik", f"{a:.1f} → {b:.1f}", "|fark| < 10", abs(b-a) < 10))

# 3. mTAL dilüsyon
a = scalar(f"SELECT value FROM {DB} WHERE variable='con' AND solute='Na' AND segment='mTAL' "
           f"AND compartment='Lumen' AND nephron='sup' AND position=0", senaryo)
b = scalar(f"SELECT value FROM {DB} WHERE variable='con' AND solute='Na' AND segment='mTAL' "
           f"AND compartment='Lumen' AND nephron='sup' AND position=1", senaryo)
if a and b: add(("mTAL dilüsyon (lümen Na)", f"{a:.0f} → {b:.0f} mM", "çıkış < giriş", b < a))

# 4. NKCC2 stokiyometri
a = scalar(f"SELECT value FROM {DB} WHERE variable='flux' AND transporter='NKCC2A' AND solute='Na' "
           f"AND segment='mTAL' AND nephron='sup' AND position=0", senaryo)
b = scalar(f"SELECT value FROM {DB} WHERE variable='flux' AND transporter='NKCC2A' AND solute='Cl' "
           f"AND segment='mTAL' AND nephron='sup' AND position=0", senaryo)
if a and b and a != 0:
    r = b / a
    add(("NKCC2A stokiyometri", f"Cl/Na = {r:.2f}", "Hedef: 1.8–2.2", 1.8 < r < 2.2))

# 5. Kortikomedüller gradyan
a = scalar(f"SELECT value FROM {DB} WHERE variable='osmolality' AND segment='CCD' "
           f"AND compartment='Bath' AND nephron='merged' AND position=0", senaryo)
b = scalar(f"SELECT value FROM {DB} WHERE variable='osmolality' AND segment='IMCD' "
           f"AND compartment='Bath' AND nephron='merged' AND position=1", senaryo)
if a and b:
    add(("Kortikomedüller gradyan (Bath)", f"{a:.0f} → {b:.0f} (×{b/a:.2f})",
         "Hedef: en az ×2", b > 2*a))

# 6. İdrar hiperozmolar
v = scalar(f"SELECT value FROM {DB} WHERE variable='osmolality' AND segment='IMCD' "
           f"AND compartment='Lumen' AND nephron='merged' AND position=1", senaryo)
if v: add(("İdrar hiperozmolar", f"{v:.0f} mOsm", "> plazma (300)", v > 300))

# 7. Üre geri dönüşümü
a = scalar(f"SELECT value FROM {DB} WHERE variable='con' AND solute='urea' AND segment='LDL' "
           f"AND compartment='Lumen' AND nephron='jux5' AND position=0", senaryo)
b = scalar(f"SELECT value FROM {DB} WHERE variable='con' AND solute='urea' AND segment='LDL' "
           f"AND compartment='Lumen' AND nephron='jux5' AND position=1", senaryo)
if a and b: add(("Üre geri dönüşümü (LDL jux5)", f"{a:.1f} → {b:.1f} (×{b/a:.1f})",
                 "Hedef: en az ×2", b > 2*a))

# 8. NH3 lümen=Bath denge
a = scalar(f"SELECT value FROM {DB} WHERE variable='con' AND solute='NH3' AND segment='LDL' "
           f"AND compartment='Lumen' AND nephron='jux5' AND position=1", senaryo)
b = scalar(f"SELECT value FROM {DB} WHERE variable='con' AND solute='NH3' AND segment='LDL' "
           f"AND compartment='Bath' AND nephron='jux5' AND position=1", senaryo)
if a and b: add(("NH3 lümen ≈ Bath (LDL çıkış)", f"L={a:.3f} · B={b:.3f}",
                 "fark < %15", abs(a-b)/max(a,b) < 0.15))

# 9. Segment zincirleme
a = scalar(f"SELECT value FROM {DB} WHERE variable='con' AND solute='Na' AND segment='mTAL' "
           f"AND compartment='Lumen' AND nephron='sup' AND position=1", senaryo)
b = scalar(f"SELECT value FROM {DB} WHERE variable='con' AND solute='Na' AND segment='cTAL' "
           f"AND compartment='Lumen' AND nephron='sup' AND position=0", senaryo)
if a and b and a != 0:
    add(("Segment zincirleme (mTAL → cTAL)", f"{a:.1f} = {b:.1f}",
         "fark < %2", abs(a-b)/a < 0.02))

# Üst metrikler
passed = sum(1 for *_, ok in checks if ok)
total = len(checks)
m1, m2, m3 = st.columns(3)
m1.metric("Geçen", f"{passed} / {total}")
m2.metric("Başarı", f"{passed/total*100:.0f} %" if total else "—")
m3.metric("Senaryo", senaryo)

st.markdown("---")

# 2 sutunlu kart grid
cols = st.columns(2)
for i, (ad, deger, hedef, ok) in enumerate(checks):
    with cols[i % 2]:
        icon = "✓" if ok else "✗"
        renk = "#059669" if ok else "#dc2626"
        st.markdown(f"""
        <div style="border:1px solid #e5e7eb;border-left:4px solid {renk};
                    padding:10px 14px;border-radius:6px;margin-bottom:10px;background:white;">
          <div style="display:flex;justify-content:space-between;align-items:start;">
            <div style="font-weight:600;color:#111827;">{ad}</div>
            <div style="color:{renk};font-weight:700;font-size:1.1rem;">{icon}</div>
          </div>
          <div style="margin-top:4px;color:#374151;font-family:ui-monospace,monospace;">{deger}</div>
          <div style="margin-top:2px;color:#6b7280;font-size:0.8rem;">{hedef}</div>
        </div>
        """, unsafe_allow_html=True)
