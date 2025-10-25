# Streamlit Data Storytelling — Vacant Housing in France

This app explores vacancy trends across French departments and regions using LOVAC open data (commune-level and department-level CSVs).

## What you get
- Narrative-driven dashboard (hook → analysis → insights → implications)
- Sidebar filters (region, year range, metric)
- 3+ interactive visuals:
  - Line trends (national and within-region)
  - Regional comparison bars (latest year)
  - Department map (choropleth) — auto-downloads GeoJSON on first run; falls back to small multiples if offline
- KPI header tied to filters
- Data quality panel (missingness, validation)
- Cached data and efficient pre-aggregation

## Run locally

1. Create a Python environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Launch the app:

```powershell
streamlit run app.py
```

If you see a warning about missing `departements.geojson`, the app will download it automatically (internet required). Without it, a small-multiples fallback is shown.

## Data
- `data/lovac_opendata_dep.csv` — department-level counts of total dwellings, vacant dwellings, and long-term vacant (>2 years) across 2020–2025.
- `data/lovac-opendata-communes.csv` — commune-level counts with region and department labels.

CSV specifics:
- Separator: `;`
- Encoding: cp1252/latin-1 (the app auto-detects)
- Missing values: `s` means suppressed; treated as NA
- Numbers may include spaces as thousands separators; the app normalizes those.

## Accessibility
- Clear axes, labels, and consistent color scales
- Alt text via captions and chart titles

## License and attribution
- Data source: LOVAC Open Data (public portal). Please verify license on the portal before redistribution.
- Code: MIT (adapt as needed).

## Notes
- Map uses Plotly choropleth with a public France departments GeoJSON (`assets/departements.geojson`).
- For a full commune-level map, provide latitude/longitude or a communes GeoJSON and extend `utils/viz.py` accordingly.
