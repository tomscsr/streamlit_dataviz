# utils/prep.py
from __future__ import annotations
import pandas as pd
from typing import Dict, Tuple

# Grille tuiles pour 18 régions (métropole + DROM) — simple cartogramme
REGION_TILE_GRID = pd.DataFrame([
    # code, nom court, x, y (y croît vers le bas)
    ("11", "Île-de-France", 5, 3),
    ("24", "Centre-Val de Loire", 5, 4),
    ("27", "Bourgogne-Fr-Comté", 6, 4),
    ("28", "Normandie", 3, 4),
    ("32", "Hauts-de-France", 4, 2),
    ("44", "Grand Est", 7, 3),
    ("52", "Pays de la Loire", 3, 5),
    ("53", "Bretagne", 2, 5),
    ("75", "Nouvelle-Aquitaine", 3, 6),
    ("76", "Occitanie", 5, 6),
    ("84", "Auvergne-Rh-Alpes", 6, 5),
    ("93", "Provence-Alpes-Côte d’Azur", 7, 6),
    ("94", "Corse", 8, 7),
    # DROM placés à part
    ("01", "Guadeloupe", 1, 8),
    ("02", "Martinique", 2, 8),
    ("03", "Guyane", 1, 9),
    ("04", "La Réunion", 3, 8),
    ("06", "Mayotte", 4, 8),
], columns=["REG_RESID", "REGION", "tx", "ty"])

def _wmean(s: pd.Series, w: pd.Series) -> float:
    return (s * w).sum() / w.sum() if w.sum() != 0 else float("nan")

def aggregate_by_region(df: pd.DataFrame, only_champ_co2: bool = True) -> pd.DataFrame:
    d = df.copy()
    if only_champ_co2 and "CHAMP_CO2" in d.columns:
        d = d[d["CHAMP_CO2"] == True]
    g = d.groupby(["ANNEE", "REG_RESID"], dropna=False)
    out = g.apply(lambda x: pd.Series({
        "DIST": _wmean(x["DIST"], x["IPONDI"]),
        "DUREE": _wmean(x["DUREE"], x["IPONDI"]),
        "DIST_HEBDO": _wmean(x["DIST_HEBDO"], x["IPONDI"]),
        "CO2_HEBDO": _wmean(x["CO2_HEBDO"], x["IPONDI"]),
        "CARBU_HEBDO": _wmean(x["CARBU_HEBDO"], x["IPONDI"]),
        "IPONDI": x["IPONDI"].sum()
    })).reset_index()

    out["CO2_KM_U"] = out["CO2_HEBDO"] / out["DIST_HEBDO"]
    out = out.merge(REGION_TILE_GRID, on="REG_RESID", how="left")
    return out

def aggregate_by_mode(df: pd.DataFrame, only_champ_co2: bool = True) -> pd.DataFrame:
    d = df.copy()
    if only_champ_co2 and "CHAMP_CO2" in d.columns:
        d = d[d["CHAMP_CO2"] == True]
    g = d.groupby(["ANNEE", "MODTRANS"], dropna=False)
    out = g.apply(lambda x: pd.Series({
        "CO2_HEBDO": _wmean(x["CO2_HEBDO"], x["IPONDI"]),
        "DIST_HEBDO": _wmean(x["DIST_HEBDO"], x["IPONDI"]),
        "IPONDI": x["IPONDI"].sum()
    })).reset_index()
    out["PART"] = out["IPONDI"] / out.groupby("ANNEE")["IPONDI"].transform("sum")
    return out

def aggregate_timeseries(df: pd.DataFrame, region_filter: list[str] | None = None) -> pd.DataFrame:
    d = df.copy()
    if region_filter:
        d = d[d["REG_RESID"].isin(region_filter)]
    if "CHAMP_CO2" in d.columns:
        d = d[d["CHAMP_CO2"] == True]
    g = d.groupby(["ANNEE"], dropna=False)
    out = g.apply(lambda x: pd.Series({
        "CO2_HEBDO": _wmean(x["CO2_HEBDO"], x["IPONDI"]),
        "DIST_HEBDO": _wmean(x["DIST_HEBDO"], x["IPONDI"]),
        "DUREE": _wmean(x["DUREE"], x["IPONDI"]),
        "IPONDI": x["IPONDI"].sum()
    })).reset_index()
    return out

def data_quality_summary(df: pd.DataFrame) -> pd.DataFrame:
    q = pd.DataFrame({
        "col": df.columns,
        "missing": df.isna().sum().values,
        "pct_missing": (df.isna().mean() * 100).round(2).values
    })
    q["dtype"] = [str(t) for t in df.dtypes.values]
    return q.sort_values("pct_missing", ascending=False)

def make_tables(df_raw: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    return {
        "by_region": aggregate_by_region(df_raw, True),
        "by_mode": aggregate_by_mode(df_raw, True),
        "timeseries_all": aggregate_timeseries(df_raw, None),
        "dq": data_quality_summary(df_raw),
        "region_grid": REGION_TILE_GRID.copy(),
    }
