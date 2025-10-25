import streamlit as st
import pandas as pd
from utils.io import load_data, ensure_departements_geojson
from utils.prep import build_model
from sections.intro import render_intro
from sections.overview import render_overview
from sections.deep_dives import render_deep_dives
from sections.conclusions import render_conclusions

st.set_page_config(page_title="Vacant Housing in France — Data Storytelling", layout="wide")

@st.cache_data(show_spinner=False)
def get_data():
    df_dep, df_com = load_data()
    model = build_model(df_dep, df_com)
    return model

# Title and caption
st.title("Vacant Housing in France: Trends, Places, and Implications")
st.caption("Source: LOVAC Open Data — public data portal — license presumed Open Data (verify on portal).")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    st.write("Tune the scope and metrics; all charts update instantly.")

model = get_data()

# Compute available filter values
years = sorted(model["years_available"])  # e.g., [2020, 2021, ...]
regions = ["All"] + sorted(model["regions"])  # LIB_REG values
metrics = {
    "Vacant dwellings (count)": "vacant",
    "Vacant >2 years (count)": "vacant_2y",
    "Vacancy rate (% of total)": "vacancy_rate",
    "Long-term vacancy rate (% of total)": "vacancy_2y_rate",
}

with st.sidebar:
    year_range = st.select_slider("Year range", options=years, value=(min(years), max(years)))
    region_choice = st.selectbox("Region", regions)
    metric_choice = st.selectbox("Metric", list(metrics.keys()))
    top_n = st.slider("Top/Bottom N (for rankings)", min_value=5, max_value=25, value=10)

# Ensure map asset if user wants map (may download on demand)
ensure_departements_geojson()  # will no-op if already present

# KPI + Sections
render_intro(st)

kpi_scope = {
    "region": None if region_choice == "All" else region_choice,
    "year_min": year_range[0],
    "year_max": year_range[1],
    "metric": metrics[metric_choice],
}

render_overview(st, model, kpi_scope)

render_deep_dives(st, model, {
    "region": kpi_scope["region"],
    "metric": metrics[metric_choice],
    "year_min": kpi_scope["year_min"],
    "year_max": kpi_scope["year_max"],
    "top_n": top_n,
})

render_conclusions(st)

# Data quality and limitations block (always at bottom)
st.markdown("### Data Quality & Limitations")
st.info(model["quality_notes"])