#!/usr/bin/env python3
"""
run_scenarios.py — Senaryo kutuphanesi otonom uretici.

Her senaryoyu sirayla calistirir, basariliysa proje klasorune kopyalar.
Daha onceden tamamlanan senaryolari atlar (resumable).

Calistirma (terminalden):
    caffeinate -is nohup python3 ~/Desktop/Nefron-Projesi/kod/run_scenarios.py \\
        > ~/Desktop/Nefron-Projesi/yedekler/scenario_run.log 2>&1 &

Sonra `tail -f ~/Desktop/Nefron-Projesi/yedekler/scenario_run.log` ile ilerlemeyi izle.

Tahmini sure: 9 senaryo x ~2h = ~18 saat. MacBook acik+fis+caffeinate sart.
"""

import os
import sys
import subprocess
import shutil
import time
from datetime import datetime

# Senaryolar — (etiket, args, model_yaza_klasor_adi)
# Modelin parallel_simulate.py'sinde file_to_save mantigi:
#   diabetes -> {sex}_hum_{Severity}_diab_N_unx
#   inhibition -> {inhib}_{sex}_hum
#   obese -> {sex}_hum_Y_obese
#   HT -> {sex}_hum_HT
#   normal -> {sex}_hum_normal
SCENARIOS = [
    # F_normal zaten var — atlanir
    ("M_normal",      ["--sex","male","--species","human","--type","multiple"],
                      "male_hum_normal"),
    ("F_diab_mod",    ["--sex","female","--species","human","--type","multiple","--diabetes","Moderate"],
                      "female_hum_Moderate_diab_N_unx"),
    ("F_diab_severe", ["--sex","female","--species","human","--type","multiple","--diabetes","Severe"],
                      "female_hum_Severe_diab_N_unx"),
    ("F_SGLT2",       ["--sex","female","--species","human","--type","multiple","--inhibition","SGLT2"],
                      "SGLT2_female_hum"),
    ("F_ACE",         ["--sex","female","--species","human","--type","multiple","--inhibition","ACE"],
                      "ACE_female_hum"),
    ("F_obese",       ["--sex","female","--species","human","--type","multiple","--obese","Y"],
                      "female_hum_Y_obese"),
    ("F_HT",          ["--sex","female","--species","human","--type","multiple","--HT","Y"],
                      "female_hum_HT"),
    ("M_SGLT2",       ["--sex","male","--species","human","--type","multiple","--inhibition","SGLT2"],
                      "SGLT2_male_hum"),
    # F_UNX: model klasoru `female_hum_normal` olarak yaziyor (parametre sistemi sinirli)
    # Mevcut F_normal'i gecici yedekleyip, sonra geri yukluyoruz.
    ("F_UNX",         ["--sex","female","--species","human","--type","multiple","--unx","Y"],
                      "female_hum_normal"),
]

MODEL_DIR = os.path.expanduser("~/nephron")
PROJECT_DIR = os.path.expanduser("~/Desktop/Nefron-Projesi")
SCENARIOS_DIR = os.path.join(PROJECT_DIR, "veri", "ham_scenarios")


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def run_scenario(label, args, model_folder):
    """Tek bir senaryoyu calistir. Resumable: cikti varsa atla."""
    dest = os.path.join(SCENARIOS_DIR, label)
    if os.path.isdir(dest) and len(os.listdir(dest)) > 1000:
        log(f"⏭  {label}: zaten var ({len(os.listdir(dest))} dosya), atlandi")
        return True

    # UNX standalone: female_hum_normal'a yazar -> mevcut F_normal'i yedekle
    is_unx = "--unx" in args and "Y" in args
    backup_path = None
    if is_unx:
        existing = os.path.join(MODEL_DIR, "female_hum_normal")
        if os.path.isdir(existing):
            backup_path = os.path.join(MODEL_DIR, "female_hum_normal__UNX_SAVE")
            log(f"   UNX hazirligi: female_hum_normal -> female_hum_normal__UNX_SAVE")
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.move(existing, backup_path)

    # Onceki ayni-isimli cikti varsa sil (append-bug onlemi)
    src = os.path.join(MODEL_DIR, model_folder)
    if os.path.isdir(src):
        log(f"   Eski {model_folder} bulundu, siliniyor")
        shutil.rmtree(src)

    # Simulasyonu calistir
    log(f"▶  {label}: BASLADI — {' '.join(args)}")
    t0 = time.time()
    try:
        subprocess.run(["python3", "parallel_simulate.py"] + args,
                       cwd=MODEL_DIR, check=True)
    except subprocess.CalledProcessError as e:
        log(f"❌ {label}: simulasyon hatasi (exit {e.returncode})")
        if backup_path and os.path.isdir(backup_path):
            shutil.move(backup_path, os.path.join(MODEL_DIR, "female_hum_normal"))
        return False
    except KeyboardInterrupt:
        log(f"⏸  {label}: kullanici durdurdu")
        if backup_path and os.path.isdir(backup_path):
            shutil.move(backup_path, os.path.join(MODEL_DIR, "female_hum_normal"))
        sys.exit(130)
    dt = time.time() - t0
    log(f"   simulasyon bitti ({dt/60:.1f} dk = {dt/3600:.2f} h)")

    # Kopyala -> projeye
    if not os.path.isdir(src):
        log(f"❌ {label}: beklenen cikti yok: {src}")
        if backup_path and os.path.isdir(backup_path):
            shutil.move(backup_path, os.path.join(MODEL_DIR, "female_hum_normal"))
        return False
    os.makedirs(SCENARIOS_DIR, exist_ok=True)
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    log(f"✅ {label}: {len(os.listdir(dest))} dosya kopyalandi -> {dest}")

    # UNX: model klasorunu temizle + F_normal'i geri yukle
    if is_unx and backup_path:
        if os.path.isdir(src):
            shutil.rmtree(src)
        if os.path.isdir(backup_path):
            shutil.move(backup_path, os.path.join(MODEL_DIR, "female_hum_normal"))
            log(f"   UNX temizleme: F_normal geri yuklendi")

    return True


def main():
    log("=" * 60)
    log(f"Senaryo kutuphanesi uretimi — {len(SCENARIOS)} senaryo (F_normal zaten var)")
    log(f"Model dizini: {MODEL_DIR}")
    log(f"Hedef:        {SCENARIOS_DIR}")
    log(f"Tahmini sure: ~{len(SCENARIOS)*2:.0f} saat")
    log("=" * 60)

    if not os.path.isdir(MODEL_DIR):
        log(f"HATA: Model dizini yok: {MODEL_DIR}")
        sys.exit(1)

    os.makedirs(SCENARIOS_DIR, exist_ok=True)
    results = []
    for i, (label, args, folder) in enumerate(SCENARIOS, 1):
        log("")
        log(f"--- [{i}/{len(SCENARIOS)}] {label} ---")
        ok = run_scenario(label, args, folder)
        results.append((label, ok))

    log("")
    log("=" * 60)
    log("HEPSI TAMAMLANDI")
    for label, ok in results:
        log(f"  {'✅' if ok else '❌'} {label}")
    log("=" * 60)
    log("Sonraki adim: python3 kod/build_database.py (parquet'i yeniden uret)")


if __name__ == "__main__":
    main()
