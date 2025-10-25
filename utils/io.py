from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Tuple

import pandas as pd

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DEPARTEMENTS_GEOJSON = ASSETS_DIR / "departements.geojson"


def _coerce_number(x):
    """
    Convert French-formatted numbers like "1 234" to int, handle 's' or blanks as NaN.
    """
    if pd.isna(x):
        return pd.NA
    if isinstance(x, str):
        xs = x.strip()
        if xs.lower() in {"s", "", "nan", "na"}:
            return pd.NA
        # remove spaces used as thousands separators
        xs = xs.replace("\xa0", " ").replace(" ", "")
        xs = xs.replace(",", ".")  # just in case
        if xs == "":
            return pd.NA
        try:
            if "." in xs:
                return float(xs)
            return int(xs)
        except Exception:
            return pd.NA
    return x


def read_csv_safely(path: Path) -> pd.DataFrame:
    encodings = ["cp1252", "latin-1", "utf-8"]
    last_err = None
    for enc in encodings:
        try:
            df = pd.read_csv(path, sep=";", encoding=enc, dtype=str)
            return df
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"Failed to read {path}: {last_err}")


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load department and commune CSVs from data/ and return raw dataframes (string dtypes).
    This function does not mutate files and is cached by Streamlit at call site.
    """
    dep_path = DATA_DIR / "lovac_opendata_dep.csv"
    com_path = DATA_DIR / "lovac-opendata-communes.csv"

    if not dep_path.exists():
        raise FileNotFoundError(f"Missing file: {dep_path}")
    if not com_path.exists():
        raise FileNotFoundError(f"Missing file: {com_path}")

    df_dep_raw = read_csv_safely(dep_path)
    df_com_raw = read_csv_safely(com_path)

    # Normalize column names: strip spaces and unify case
    df_dep_raw.columns = [c.strip().replace(" ", "_") for c in df_dep_raw.columns]
    df_com_raw.columns = [c.strip().replace(" ", "_") for c in df_com_raw.columns]

    # Strip whitespace in all string cells (element-wise)
    df_dep_raw = df_dep_raw.map(lambda v: v.strip() if isinstance(v, str) else v)
    df_com_raw = df_com_raw.map(lambda v: v.strip() if isinstance(v, str) else v)

    return df_dep_raw, df_com_raw


def ensure_departements_geojson() -> Path | None:
    """
    Ensure we have a departments GeoJSON locally. If missing, attempt to download
    from a well-known public mirror. If download fails, return None.
    """
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    if DEPARTEMENTS_GEOJSON.exists():
        return DEPARTEMENTS_GEOJSON

    # Lazy import to avoid hard dependency on requests when not needed
    try:
        import requests  # type: ignore
    except Exception:
        return None

    url = "https://france-geojson.gregoiredavid.fr/repo/departements.geojson"
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        with open(DEPARTEMENTS_GEOJSON, "wb") as f:
            f.write(resp.content)
        return DEPARTEMENTS_GEOJSON
    except Exception:
        return None
