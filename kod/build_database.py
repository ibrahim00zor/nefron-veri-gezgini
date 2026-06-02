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

# Segment grid (dilim) boyutlari — modelden sabit. Geri kalan hepsi 200.
SEGMENT_GRID = {'PT': 181, 'S3': 20}
DEFAULT_GRID = 200

# --- Cok-membranli flux dosyalari (Gorev #4) ---
# Bazi tasiyicilar (AE1, HATPase, HKATPase, NHE1) bir segmentte birden cok hucre
# membranina aittir; model bunlarin akisini TEK dosyaya, dosya adinda membran
# kimligi OLMADAN, append modunda yazar. Sonuc: N*grid satirlik dosya, ve veri
# pozisyon-bazli DEGIL, membran-bazli IC ICE GECMIS (interleaved):
#     [poz0_m0, poz0_m1, poz0_m2, poz1_m0, poz1_m1, poz1_m2, ...]
# Yani membran m'nin profili = values[m::membran_sayisi] (stride ile ayristirilir).
# Membran sirasi modelin parametre dosyalarindaki (datafiles/<SEG>params_*_hum.dat)
# transport_ satir sirasidir; asagidaki tablo o siradan, sex-filtreli, dosya
# uzunluklariyla dogrulanarak cikarilmistir. Etiket = kompartman cifti.
#   Kompartmanlar: Cell=principal, ICA=A-tipi ara hucre, ICB=B-tipi ara hucre,
#   LIS=lateral hucrelerarasi bosluk, Bath=interstisyum, Lumen=tubul lumeni.
MEMBRANE_ORDER = {
    ('CNT',  'HATPase'):  ['Lumen-ICA', 'ICB-LIS', 'ICB-Bath'],
    ('CNT',  'HKATPase'): ['Lumen-Cell', 'Lumen-ICA', 'Lumen-ICB'],
    ('CNT',  'AE1'):      ['ICA-LIS', 'ICA-Bath'],
    ('CCD',  'HATPase'):  ['Lumen-ICA', 'ICB-LIS', 'ICB-Bath'],
    ('CCD',  'HKATPase'): ['Lumen-Cell', 'Lumen-ICA', 'Lumen-ICB'],
    ('CCD',  'AE1'):      ['ICA-LIS', 'ICA-Bath'],
    ('OMCD', 'HKATPase'): ['Lumen-Cell', 'Lumen-ICA'],
    ('OMCD', 'AE1'):      ['ICA-LIS', 'ICA-Bath'],
    ('OMCD', 'NHE1'):     ['Cell-LIS', 'Cell-Bath'],
}


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


def make_frame(rec, condition, profile, membrane):
    """Tek bir (membran) profilini tidy DataFrame parcasina cevirir."""
    n = len(profile)
    return pd.DataFrame({
        "sex": rec['sex'], "species": rec['species'], "condition": condition,
        "nephron": rec['nephron'], "segment": rec['segment'],
        "position": np.linspace(0, 1, n),
        "variable": rec['variable'], "solute": rec['solute'],
        "compartment": rec['compartment'], "transporter": rec['transporter'],
        "membrane": membrane,
        "value": profile, "unit": UNITS.get(rec['variable'], 'unknown'),
        "source": condition,
    })


def load_scenario(scenario_dir, condition):
    """Tek bir senaryo klasoru yukler, condition kolonu ekler.
    Cok-membranli flux dosyalarini membran basina ayristirir (bkz. MEMBRANE_ORDER)."""
    files = sorted(glob.glob(os.path.join(scenario_dir, "*.txt")))
    if not files:
        return pd.DataFrame(), [], []
    frames, unknown, suspicious = [], [], []
    for path in files:
        stem = os.path.basename(path)[:-4]
        rec = parse_filename(stem)
        if rec is None:
            unknown.append(stem); continue
        values = pd.read_csv(path, header=None)[0].values
        n = len(values)
        grid = SEGMENT_GRID.get(rec['segment'], DEFAULT_GRID)

        # Cok-membranli flux dosyasi mi? (uzunluk grid'in tam kati ve > grid)
        if rec['variable'] == 'flux' and n > grid and n % grid == 0:
            k = n // grid
            labels = MEMBRANE_ORDER.get((rec['segment'], rec['transporter']))
            if labels is None or len(labels) != k:
                # Eslestirme tablosunda yok -> yine de DOGRU ayristir (stride),
                # ama anatomik etiket veremiyoruz; indeksle etiketle ve isaretle.
                labels = [f"m{m}" for m in range(k)]
                suspicious.append((stem, n, k))
            for m in range(k):
                # interleaved: membran m = her k'inci deger
                frames.append(make_frame(rec, condition, values[m::k], labels[m]))
        else:
            frames.append(make_frame(rec, condition, values, None))
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
    n_multi = int((table['membrane'].notna()).sum())
    n_memb_files = table[table['membrane'].notna()][
        ['condition','segment','transporter','solute','nephron']].drop_duplicates().shape[0]
    print(f"Cok-membranli flux: {n_memb_files} dosya membran basina ayristirildi "
          f"({n_multi:,} satir membran etiketli)")
    if suspicious:
        print(f"UYARI - eslestirme tablosunda OLMAYAN cok-membranli dosya: {len(suspicious)} adet "
              f"(stride ile dogru ayristirildi ama anatomik etiket yok; MEMBRANE_ORDER'a ekle):")
        for item in suspicious[:10]:
            print(f"    {item}")
    table.to_parquet(OUTPUT, index=False)
    print(f"\nYazildi -> {OUTPUT}")
