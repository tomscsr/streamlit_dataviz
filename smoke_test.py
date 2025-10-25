# Quick smoke test to validate data loading and model building
from utils.io import load_data
from utils.prep import build_model


df_dep, df_com = load_data()
model = build_model(df_dep, df_com)

years = model.get("years_available", [])
regions = model.get("regions", [])
latest_dep = model.get("latest_dep")

print({
    "years_count": len(years),
    "years_range": (min(years) if years else None, max(years) if years else None),
    "regions_count": len(regions),
    "latest_year": int(latest_dep["year"].max()) if latest_dep is not None and not latest_dep.empty else None,
})
