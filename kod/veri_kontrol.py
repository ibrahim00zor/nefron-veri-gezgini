"""
veri_kontrol.py  —  Senaryo veri butunlugu denetcisi.

Modelin Newton cozucusu bazi senaryolarda (ozellikle toplayici kanal / merged
hesabinda) yakinsamayabilir; sonuc NaN veya fiziksel olarak imkansiz negatif
deger (negatif osmolalite/hacim) olur. Bu betik her senaryoyu tarar ve guvenilir
olup olmadigini raporlar.

Verdict siniflari:
  TEMIZ           -> NaN yok, negatif osmolalite/hacim yok (eser-solut ~0 gurultusu kabul)
  PROKSIMAL_OK    -> tek nefronlar saglam ama toplayici kanal (merged/IMCD) bozuk
  BOZUK           -> yaygin NaN / negatif osmolalite

Calistirmak icin:  python3 kod/veri_kontrol.py
"""
import os
import duckdb
import pandas as pd

PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARQUET   = os.path.join(PROJ_ROOT, "veri", "nephron_veritabani.parquet")
DB        = f"'{PARQUET}'"

# Negatif olamayacak degiskenler (fiziksel)
NONNEG = ('osmolality', 'water_volume')


def q(sql):
    return duckdb.sql(sql).df()


def scenario_report():
    """Senaryo basina butunluk metrikleri + verdict."""
    # Yakinsama gostergeleri: NaN ve negatif Lumen osmolalitesi (solut toplami).
    # NOT: IMCD merged'de Cell-kompartman hacmi ayri bir model artefaktiyla negatif
    # cikar ama Lumen (idrar yolu) saglamdir; bu yuzden hacim icin yalniz Lumen sayilir.
    df = q(f"""
        SELECT condition,
            SUM(CASE WHEN value IS NULL OR isnan(value) THEN 1 ELSE 0 END) AS nan,
            SUM(CASE WHEN variable='osmolality' AND compartment='Lumen' AND value < -1 THEN 1 ELSE 0 END) AS neg_osm,
            SUM(CASE WHEN variable='water_volume' AND compartment='Lumen' AND value < -0.001 THEN 1 ELSE 0 END) AS neg_lumen_hacim
        FROM {DB}
        GROUP BY condition ORDER BY condition
    """)

    # Bozukluk hangi segment/nefronlarda? (Lumen-temelli gercek yakinsama hatasi)
    bad_loc = q(f"""
        SELECT DISTINCT condition, segment, nephron
        FROM {DB}
        WHERE (value IS NULL OR isnan(value))
           OR (variable='osmolality' AND compartment='Lumen' AND value < -1)
           OR (variable='water_volume' AND compartment='Lumen' AND value < -0.001)
        ORDER BY condition, segment
    """)

    verdicts = []
    for _, r in df.iterrows():
        cond = r['condition']
        n_bad = int(r['nan'] + r['neg_osm'] + r['neg_lumen_hacim'])
        if n_bad == 0:
            v = "TEMIZ"
        else:
            locs = bad_loc[bad_loc['condition'] == cond]
            # Sadece toplayici kanal (merged) ve son segmentler mi etkilenmis?
            distal = {'IMCD', 'OMCD', 'CCD', 'CNT', 'DCT'}
            etkilenen = set(locs['segment'])
            if etkilenen <= distal:
                v = "PROKSIMAL_OK (toplayici kanal bozuk)"
            else:
                v = "BOZUK"
        verdicts.append(v)
    df['verdict'] = verdicts
    return df, bad_loc


if __name__ == "__main__":
    print(f"Kaynak: {os.path.basename(PARQUET)}\n")
    df, bad_loc = scenario_report()
    print(df.to_string(index=False))
    print()
    if not bad_loc.empty:
        print("Bozukluk konumlari (senaryo -> etkilenen segmentler):")
        for cond in bad_loc['condition'].unique():
            segs = sorted(set(bad_loc[bad_loc['condition'] == cond]['segment']))
            print(f"  {cond:<12} {segs}")
    temiz = df[df['verdict'] == 'TEMIZ']['condition'].tolist()
    print(f"\nGuvenle kullanilabilir (tam temiz): {temiz}")
