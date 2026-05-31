"""
build_database.py  —  Nefron-Projesi veri yukleyicisi.
TUM ham txt dosyalarini tek bir tidy (long) tabloya cevirir ve Parquet yazar.
Tasarim: 'classify-then-route' -> once dosya turunu belirle, sonra dogru kuralla coz.

Yollar, betigin konumundan proje kokune gore otomatik bulunur.
Calistirmak icin:  python3 kod/build_database.py
"""
import glob
import os
import pandas as pd
import numpy as np

# --- Yollar (betigin yerine gore otomatik) ---
KOD_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJ_ROOT  = os.path.dirname(KOD_DIR)
SOURCE_DIR = os.path.join(PROJ_ROOT, "veri", "ham")
OUTPUT     = os.path.join(PROJ_ROOT, "veri", "nephron_veritabani.parquet")
CONDITION  = "normal"   # bu veri setinin fizyolojik durumu

# Bilinen sabitler (modelin output.py / driver.py ile birebir ayni)
SOLUTES = ['Na','K','Cl','HCO3','H2CO3','CO2','HPO4','H2PO4','urea','NH3','NH4','H','HCO2','H2CO2','glu']
SOLUTES_BY_LEN = sorted(SOLUTES, key=len, reverse=True)   # uzun once: 'HCO3' -> 'H' yanlisini onler
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
    sex, species, segment = parts[0], parts[1], parts[2]
    rest = parts[3:]

    if rest and rest[-1] in NEPHS:
        nephron = rest[-1]; rest = rest[:-1]
    else:
        nephron = 'merged'

    rec = dict(sex=sex, species=species, segment=segment, nephron=nephron,
               solute=None, compartment=None, transporter=None)
    head = rest[0]

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
    return rec


def load_all():
    files = sorted(glob.glob(os.path.join(SOURCE_DIR, "*.txt")))
    print(f"{len(files)} dosya taranacak ({SOURCE_DIR})")

    frames, unknown, suspicious = [], [], []
    for path in files:
        stem = os.path.basename(path)[:-4]
        rec = parse_filename(stem)
        if rec is None:
            unknown.append(stem); continue

        values = pd.read_csv(path, header=None)[0]
        n = len(values)
        if n > 205:
            suspicious.append((stem, n))   # cok-membranli flux dosyalari burada cikar

        frames.append(pd.DataFrame({
            "sex": rec['sex'], "species": rec['species'], "condition": CONDITION,
            "nephron": rec['nephron'], "segment": rec['segment'],
            "position": np.linspace(0, 1, n),
            "variable": rec['variable'], "solute": rec['solute'],
            "compartment": rec['compartment'], "transporter": rec['transporter'],
            "value": values.values, "unit": UNITS.get(rec['variable'], 'unknown'),
            "source": CONDITION,
        }))

    return pd.concat(frames, ignore_index=True), unknown, suspicious


if __name__ == "__main__":
    table, unknown, suspicious = load_all()
    print(f"Toplam satir: {len(table):,}")
    print(f"Parse edilemeyen dosya: {len(unknown)}")
    if suspicious:
        print(f"NOT - cok-membranli flux dosyalari (split gerekecek): {len(suspicious)} adet, ornek {suspicious[:3]}")
    table.to_parquet(OUTPUT, index=False)
    print(f"Yazildi -> {OUTPUT}")
