from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd


METRIC_BASES = {
    "pp_total": "total",
    "pp_vacant": "vacant",
    "pp_vacant_plus_2ans": "vacant_2y",
}

YEAR_PATTERN = re.compile(r"^(pp_total|pp_vacant|pp_vacant_plus_2ans)_(\d{2})$")


@dataclass
class Model:
    df_dep_long: pd.DataFrame
    df_com_long: pd.DataFrame
    by_dep_year: pd.DataFrame
    by_reg_year: pd.DataFrame
    latest_dep: pd.DataFrame
    years_available: List[int]
    regions: List[str]
    quality_notes: str


def _coerce_numbers_in_wide(df: pd.DataFrame) -> pd.DataFrame:
    def parse_cell(x):
        if pd.isna(x):
            return pd.NA
        if isinstance(x, str):
            s = x.strip()
            if s.lower() in {"s", "", "na", "nan"}:
                return pd.NA
            s = s.replace("\xa0", " ").replace(" ", "")
            s = s.replace(",", ".")
            try:
                if "." in s:
                    return float(s)
                return int(s)
            except Exception:
                return pd.NA
        return x

    cols_num = [c for c in df.columns if YEAR_PATTERN.match(c)]
    df[cols_num] = df[cols_num].map(parse_cell)
    return df


def _wide_to_long(df: pd.DataFrame, geo_cols: List[str]) -> pd.DataFrame:
    # Identify value columns
    val_cols = [c for c in df.columns if YEAR_PATTERN.match(c)]
    long_df = df.melt(id_vars=geo_cols, value_vars=val_cols, var_name="var", value_name="value")
    # Extract metric and year 2-digit
    long_df[["var_base", "yy"]] = long_df["var"].str.extract(r"^(pp_total|pp_vacant|pp_vacant_plus_2ans)_(\d{2})$")
    # Convert YY to 20YY assumption
    long_df["year"] = 2000 + long_df["yy"].astype(int)
    # Map base to shorter names
    long_df["metric"] = long_df["var_base"].map(METRIC_BASES)
    long_df = long_df.drop(columns=["var", "yy", "var_base"]).dropna(subset=["metric"])  # safety
    return long_df


def build_model(df_dep_raw: pd.DataFrame, df_com_raw: pd.DataFrame) -> Dict:
    # Department-level cleaning
    dep = df_dep_raw.copy()
    # Standardize known geo columns
    rename_dep = {
        "DEP": "dep_code",
        "LIB_DEP": "dep_name",
    }
    dep = dep.rename(columns=rename_dep)
    dep = _coerce_numbers_in_wide(dep)
    dep_long = _wide_to_long(dep, ["dep_code", "dep_name"])  # columns: dep_code, dep_name, metric, value, year

    # Commune-level cleaning
    com = df_com_raw.copy()
    rename_com = {
        "CODGEO_25": "com_code",
        "LIBGEO_25": "com_name",
        "EPCI_25": "epci_code",
        "LIB_EPCI_25": "epci_name",
        "DEP": "dep_code",
        "LIB_DEP": "dep_name",
        "REG": "reg_code",
        "LIB_REG": "reg_name",
    }
    com = com.rename(columns=rename_com)
    com = _coerce_numbers_in_wide(com)
    com_long = _wide_to_long(com, [
        "com_code", "com_name", "epci_code", "epci_name", "dep_code", "dep_name", "reg_code", "reg_name"
    ])

    # Compute rates at each row where total is available
    def compute_rates(df: pd.DataFrame, group_cols: List[str]) -> pd.DataFrame:
        out = df.pivot_table(index=group_cols + ["year"], columns="metric", values="value", aggfunc="sum").reset_index()
        # Ensure columns exist
        for c in ["total", "vacant", "vacant_2y"]:
            if c not in out.columns:
                out[c] = 0
        out["vacancy_rate"] = (out["vacant"] / out["total"]) * 100
        out["vacancy_2y_rate"] = (out["vacant_2y"] / out["total"]) * 100
        return out

    by_dep_year = compute_rates(dep_long, ["dep_code", "dep_name"])  # department totals by year
    by_reg_year = compute_rates(com_long, ["reg_code", "reg_name"])  # region totals by year (sum of communes)

    # Latest year snapshot for department map
    years = sorted(by_dep_year["year"].dropna().unique())
    latest_year = max(years)
    latest_dep = by_dep_year[by_dep_year["year"] == latest_year].copy()

    # Quality checks
    # Missing counts: number of NaNs in long frames for values
    miss_dep = dep_long["value"].isna().sum()
    miss_com = com_long["value"].isna().sum()
    # Sanity: vacancies should not exceed totals at dep level per year
    invalid_dep = (by_dep_year["vacant"] > by_dep_year["total"]).sum()

    quality_notes = (
        f"Missing values — departments: {miss_dep:,}; communes: {miss_com:,}.\n"
        f"Validation — rows with vacant > total (dept-year): {invalid_dep}.\n"
        "Numbers parsed from French-formatted CSV ('s' treated as missing; spaces removed)."
    )

    model = {
        "df_dep_long": dep_long,
        "df_com_long": com_long,
        "by_dep_year": by_dep_year,
        "by_reg_year": by_reg_year,
        "latest_dep": latest_dep,
        "years_available": years,
        "regions": sorted(by_reg_year["reg_name"].dropna().unique()),
        "quality_notes": quality_notes,
    }
    return model
