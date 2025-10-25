# utils/io.py
from __future__ import annotations
import os
import glob
import pandas as pd
from typing import Dict, List

# Dtypes d'après l'exemple fourni (séparateur ; dans les CSV officiels)
DTYPES: Dict[str, str] = {
    "LIEU_RESID": "string", "LIEU_TRAV": "string",
    "MODTRANS": "string", "AGEREVQ": "string", "CS1": "string",
    "DIPL": "string", "EMPL": "string", "ILT": "string", "ILTUU": "string",
    "IMMI": "string", "INATC": "string", "INEEM": "string", "INPOM": "string",
    "MOCO": "string", "NA5": "string", "NPERR": "string", "SEXE": "string",
    "STAT": "string", "STOCD": "string", "TP": "string", "TYPL": "string",
    "TYPMR": "string", "VOIT": "string",
    "DEP_RESID": "string", "REG_RESID": "string", "CATEAAV20_RESID": "string",
    "TAAV2017_RESID": "string", "DENS7_2025_RESID": "string", "EPCI_EPT_RESID": "string",
    "ZE2020_RESID": "string", "AAV20_RESID": "string",
    "DEP_TRAV": "string", "REG_TRAV": "string", "CATEAAV20_TRAV": "string",
    "TAAV2017_TRAV": "string", "DENS7_2025_TRAV": "string", "EPCI_EPT_TRAV": "string",
    "ZE2020_TRAV": "string", "AAV20_TRAV": "string",
}

NUM_DTYPES = {
    "IPONDI": "float64", "DIST": "float64", "DUREE": "float64",
    "DIST_HEBDO": "float64", "CARBU_HEBDO": "float64", "CO2_HEBDO": "float64"
}

BOOL_DTYPES = {"CHAMP_CO2": "boolean"}

def _read_one_csv(path: str, year_from_name: bool = True) -> pd.DataFrame:
    # Les fichiers officiels utilisent ; et virgule comme séparateur décimal
    df = pd.read_csv(path, sep=";", dtype=DTYPES, low_memory=False, decimal=",")
    
    # Conversion manuelle des colonnes numériques
    for col, dtype in NUM_DTYPES.items():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(dtype)
    
    # Tolérance si certains champs bool viennent en 0/1
    if "CHAMP_CO2" in df.columns:
        if df["CHAMP_CO2"].dtype != "boolean":
            df["CHAMP_CO2"] = df["CHAMP_CO2"].astype("Int64").astype("boolean", errors="ignore")

    # Détecte l'année à partir du nom (ex: ..._2022.csv). Sinon essaie une colonne ANNEE si présente.
    year = None
    if year_from_name:
        for token in os.path.basename(path).split("_"):
            if token.isdigit() and len(token) in (4,):
                year = int(token)
    if "ANNEE" in df.columns and df["ANNEE"].notna().any():
        df["ANNEE"] = df["ANNEE"].astype("Int64")
    else:
        df["ANNEE"] = year if year is not None else pd.NA
    return df

def load_data(data_dir: str = "data") -> pd.DataFrame:
    """
    Charge 1..N fichiers. Si aucun n'est trouvé, essaie un échantillon déposé par toi.
    Concatène proprement et retourne un DataFrame unique.
    """
    patterns: List[str] = [
        os.path.join(data_dir, "depl_dom_trav_co2_*.csv"),
        os.path.join(data_dir, "depl_dom_trav_co2.csv"),
    ]
    paths: List[str] = []
    for pat in patterns:
        paths.extend(sorted(glob.glob(pat)))

    # Fallback vers l'échantillon de l'espace de travail (utile en dev local / notebook)
    if not paths:
        sample = "/mnt/data/sample_depl_dom_trav_co2_2022.csv"
        if os.path.exists(sample):
            paths = [sample]
        else:
            raise FileNotFoundError(
                "Aucun CSV trouvé dans ./data. Place au moins un fichier 'depl_dom_trav_co2_YYYY.csv'."
            )

    frames = [_read_one_csv(p) for p in paths]
    df = pd.concat(frames, ignore_index=True)
    # Normalise les codes région à 2 chiffres (ex: '11', '84', etc.)
    if "REG_RESID" in df.columns:
        df["REG_RESID"] = df["REG_RESID"].astype("string").str.zfill(2)
    if "REG_TRAV" in df.columns:
        df["REG_TRAV"] = df["REG_TRAV"].astype("string").str.zfill(2)
    return df

LICENSE = "© Insee & SDES — Données publiques, diffusion selon leurs conditions. CO₂ exprimé en gCO₂e."
