"""
build_database.py  —  Nefron-Projesi veri yukleyicisi (coklu senaryo).
veri/ham_scenarios/<senaryo>/*.txt -> tek tidy Parquet (condition kolonu ile).
Tasarim: 'classify-then-route' -> dosya turunu belirle, sonra dogru kuralla coz.

Calistirmak icin:  python3 kod/build_database.py
"""
import glob
import os
import pandas as pd
import numpy as np

# --- Yollar ---
KOD_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJ_ROOT  = os.path.dirname(KOD_DIR)
SCENARIOS_ROOT = os.path.join(PROJ_ROOT, "veri", "ham_scenarios")
OUTPUT     = os.path.join(PROJ_ROOT, "veri", "nephron_veritabani.parquet")

# Bilinen sabitler (modelin output.py / driver.py ile birebir ayni)
SOLUTES = ['Na','K','Cl','HCO3','H2CO3','CO2','HPO4','H2PO4','urea','NH3','NH4','H','HCO2','H2CO2','glu']
SOLUTES_BY_LEN = sorted(SOLUTES, key=len, reverse=True)
NEPHS = {'sup','jux1','jux2','jux3','jux4','jux5'}
TRANSPORTERS = {'NaKATPase','NHE3','KCC4','NKCC2A','NKCC2B','NKCC2F','HKATPase','AE1',
                'HATPase','Pendrin','ENaC','SGLT2','SGLT1','NHE1','NCC','GLUT2','GLUT1','NKCC1'}

UNITS = {'con':'mM', 'flow':'pmol/min', 'water_volume':'nl/min', 'flux':'pmol/min',
         'osmolality':'mOsm', 'pH':'', 'potential':'mV',
         'pressure':'unknown', 'diameter':'unknown', 'length':'unknown'}


def split_solute_membid(token):
    """ 'Na11'->('Na','11') ; 'HCO311'->('HCO3','11') ; 'Cl'->('Cl','') """
    for s in SOLUTES_BY_LEN:
        if token.startswith(s):
            return s, token[len(s):]
    return token, ''


def parse_filename(stem):
    """Dosya adini (uzantisiz) -> kayit sozlugu. Taninmazsa None."""
    parts = stem.split('_')
    if len(parts) < 4:
        return None
    sex, species, segment = parts[0], parts[1], parts[2]
    rest = parts[3:]

    if rest and rest[-1] in NEPHS:
        nephron = rest[-1]; rest = rest[:-1]
    else:
        nephron = 'merged'

    rec = dict(sex=sex, species=species, segment=segment, nephron=nephron,
               solute=None, compartment=None, transporter=None)
    if not rest:
        return None
    head = rest[0]

    try:
        if head in ('con', 'flow'):
            rec['variable'] = head; rec['solute'] = rest[2]; rec['compartment'] = rest[4]
        elif head in ('osmolality', 'pressure', 'pH'):
            rec['variable'] = head; rec['compartment'] = rest[2]
        elif head == 'water':
            rec['variable'] = 'water_volume'; rec['compartment'] = rest[3]
        elif head in ('length', 'diameter'):
            rec['variable'] = head
        elif head == 'potential':
            rec['variable'] = 'potential'; rec['compartment'] = rest[2] + '-' + rest[3]
        elif head in ('apical', 'paracellular'):
            rec['variable'] = 'flux'; rec['transporter'] = head
            rec['solute'], _ = split_solute_membid(rest[1])
        elif head in TRANSPORTERS:
            rec['variable'] = 'flux'; rec['transporter'] = head
            rec['solute'], _ = split_solute_membid(rest[1])
        else:
            return None
    except IndexError:
        return None
    return rec


def load_scenario(scenario_dir, condition):
    """Tek bir senaryo klasoru yukler, condition kolonu ekler."""
    files = sorted(glob.glob(os.path.join(scenario_dir, "*.txt")))
    if not files:
        return pd.DataFrame(), [], []
    frames, unknown, suspicious = [], [], []
    for path in files:
        stem = os.path.basename(path)[:-4]
        rec = parse_filename(stem)
        if rec is None:
            unknown.append(stem); continue
        values = pd.read_csv(path, header=None)[0]
        n = len(values)
        if n > 205:
            suspicious.append((stem, n))
        frames.append(pd.DataFrame({
            "sex": rec['sex'], "species": rec['species'], "condition": condition,
            "nephron": rec['nephron'], "segment": rec['segment'],
            "position": np.linspace(0, 1, n),
            "variable": rec['variable'], "solute": rec['solute'],
            "compartment": rec['compartment'], "transporter": rec['transporter'],
            "value": values.values, "unit": UNITS.get(rec['variable'], 'unknown'),
            "source": condition,
        }))
    return (pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()), unknown, suspicious


def load_all():
    """ham_scenarios/ altindaki tum alt-klasorleri yukler."""
    if not os.path.isdir(SCENARIOS_ROOT):
        raise FileNotFoundError(f"Senaryo kokukune yok: {SCENARIOS_ROOT}")
    scenarios = sorted([d for d in os.listdir(SCENARIOS_ROOT)
                        if os.path.isdir(os.path.join(SCENARIOS_ROOT, d))])
    print(f"{len(scenarios)} senaryo bulundu: {scenarios}")

    all_frames, all_unknown, all_suspicious = [], [], []
    for scn in scenarios:
        path = os.path.join(SCENARIOS_ROOT, scn)
        print(f"  yukleniyor: {scn}", end=" ... ", flush=True)
        df, unk, susp = load_scenario(path, scn)
        if df.empty:
            print("BOS (atlandi)")
            continue
        print(f"{len(df):,} satir")
        all_frames.append(df)
        all_unknown.extend([(scn, u) for u in unk])
        all_suspicious.extend([(scn, s) for s in susp])
    if not all_frames:
        raise RuntimeError("Hicbir senaryo yuklenemedi.")
    return pd.concat(all_frames, ignore_index=True), all_unknown, all_suspicious


if __name__ == "__main__":
    table, unknown, suspicious = load_all()
    print(f"\nToplam satir: {len(table):,}")
    print(f"Senaryolar: {sorted(table['condition'].unique())}")
    print(f"Parse edilemeyen dosya: {len(unknown)}")
    if suspicious:
        print(f"NOT - cok-membranli flux dosyalari: {len(suspicious)} adet (flux kategorisinde pozisyon-yanlis riski; bkz. notlar/bulgular.md)")
    table.to_parquet(OUTPUT, index=False)
    print(f"\nYazildi -> {OUTPUT}")
