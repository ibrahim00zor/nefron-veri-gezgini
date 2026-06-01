"""
yorum_motoru.py — Konsantrasyon profili icin otomatik fizyolojik yorum.

Kullanim:
    from yorum_motoru import yorumla
    yorumla(con_giris, con_cikis, vol_giris, vol_cikis, solut="Na")

Mantik:
    konsantrasyon = kutle / hacim
    Konsantrasyon degisimini iki bilesene ayirir:
      - Kutle degisimi (cozunmus madde gercekten girdi/cikti mi)
      - Hacim degisimi (su geri emildi/eklendi mi)
    Bu sayede LDL Na yaniligisi gibi sezgi hatalarini otomatik onler.
"""

def yorumla(con_giris, con_cikis, vol_giris, vol_cikis, solut="solüt"):
    """
    Bir segmentin giris/cikis konsantrasyon + hacim verisinden, konsantrasyon
    degisiminin fizyolojik nedenlerini acikliyan bir cumle dondurur.
    """
    if con_giris == 0 or vol_giris == 0:
        return "Yorum yapilamadi (giris degerleri sifir)."

    kutle_giris = con_giris * vol_giris
    kutle_cikis = con_cikis * vol_cikis

    dk_pct = (kutle_cikis - kutle_giris) / kutle_giris * 100   # kutle %
    dv_pct = (vol_cikis  - vol_giris)  / vol_giris  * 100      # hacim %
    dc_pct = (con_cikis  - con_giris)  / con_giris  * 100      # konsantrasyon %

    esik = 3.0   # %3 altinda "sabit" sayariz

    # Sabit konsantrasyon
    if abs(dc_pct) < 2:
        return (f"**{solut} konsantrasyonu neredeyse sabit** (%{dc_pct:+.1f}). "
                f"Kutle %{dk_pct:+.1f}, hacim %{dv_pct:+.1f} — degisimler birbirini "
                f"dengeliyor (orn. izoozmotik geri emilim).")

    # Konsantrasyon ARTTI
    if dc_pct > 0:
        if abs(dk_pct) < esik and dv_pct < -esik:
            return (f"**{solut} konsantrasyonu %{dc_pct:+.1f} artti.** "
                    f"Su geri emildi (hacim %{dv_pct:+.1f}), {solut} kutlesi sabit "
                    f"(%{dk_pct:+.1f}). _Su kaybindan kaynakli yogunlasma._")
        if dk_pct > esik and abs(dv_pct) < esik:
            return (f"**{solut} konsantrasyonu %{dc_pct:+.1f} artti.** "
                    f"{solut} lumene salgilandi (kutle %{dk_pct:+.1f}), hacim sabit "
                    f"(%{dv_pct:+.1f}). _Aktif sekresyon._")
        if dk_pct > esik and dv_pct > esik:
            return (f"**{solut} konsantrasyonu %{dc_pct:+.1f} artti.** "
                    f"Hem {solut} girdi (%{dk_pct:+.1f}) hem hacim arti (%{dv_pct:+.1f}) — "
                    f"net yogunlasma. _LDL'deki urea-su tuzagi gibi etki._")
        if dk_pct < -esik and dv_pct < -esik:
            return (f"**{solut} konsantrasyonu %{dc_pct:+.1f} artti** (ama nadiren). "
                    f"Hem {solut} (%{dk_pct:+.1f}) hem su (%{dv_pct:+.1f}) cikti; "
                    f"su daha hizli cikti, kalan yogun.")

    # Konsantrasyon AZALDI
    else:
        if abs(dk_pct) < esik and dv_pct > esik:
            return (f"**{solut} konsantrasyonu %{dc_pct:+.1f} azaldi.** "
                    f"Lumene su girdi (hacim %{dv_pct:+.1f}), {solut} kutlesi sabit "
                    f"(%{dk_pct:+.1f}). _Net dilusyon._")
        if dk_pct < -esik and abs(dv_pct) < esik:
            return (f"**{solut} konsantrasyonu %{dc_pct:+.1f} azaldi.** "
                    f"{solut} geri emildi (kutle %{dk_pct:+.1f}), hacim sabit "
                    f"(%{dv_pct:+.1f}). _Klasik geri emilim (orn. mTAL Na)._")
        if dk_pct < -esik and dv_pct > esik:
            return (f"**{solut} konsantrasyonu %{dc_pct:+.1f} azaldi.** "
                    f"{solut} cikti (%{dk_pct:+.1f}) **VE** lumene su girdi "
                    f"(%{dv_pct:+.1f}). _Cift etki — LDL urea-su tuzagi tarzi modern "
                    f"ic medulla davranisi._")
        if dk_pct < -esik and dv_pct < -esik:
            return (f"**{solut} konsantrasyonu %{dc_pct:+.1f} azaldi.** "
                    f"Hem {solut} (%{dk_pct:+.1f}) hem su (%{dv_pct:+.1f}) geri emildi; "
                    f"{solut} kaybi su kaybindan fazla.")

    # Genel kacis
    return (f"**{solut} konsantrasyonu %{dc_pct:+.1f} degisti.** "
            f"Kutle %{dk_pct:+.1f}, hacim %{dv_pct:+.1f}. "
            f"(Karmasik durum — detayli inceleme gerekir.)")
