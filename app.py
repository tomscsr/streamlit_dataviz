# app.py
from __future__ import annotations
import streamlit as st
import pandas as pd

from utils.io import load_data, LICENSE
from utils.prep import make_tables
from sections import intro, overview, deep_dives, conclusions
from utils.viz import line_chart

st.set_page_config(page_title="Data Storytelling — Domicile ⇄ Travail (CO₂)",
                   layout="wide", page_icon="🚌")

@st.cache_data(show_spinner=False)
def get_data():
    df_raw = load_data()
    tables = make_tables(df_raw)
    return df_raw, tables

# --- Titre / source
st.title("Mobilité domicile-travail : distances, durées et CO₂")
st.caption("Source : Insee & SDES — Mobilités professionnelles / EMP / RSVERO — "
           "calculs hebdomadaires pondérés par IPONDI. " + LICENSE)

# --- Chargement
raw, tables = get_data()

# --- Sidebar
with st.sidebar:
    st.header("Filtres")
    years = sorted([int(y) for y in tables["by_region"]["ANNEE"].dropna().unique()])
    year = st.select_slider("Année", options=years, value=years[-1]) if years else None

    all_regions = tables["by_region"]["REGION"].dropna().unique().tolist()
    sel_regions = st.multiselect("Régions (affinage de certaines vues)", options=all_regions, default=[])

    metric_map = {
        "CO₂ hebdo (gCO₂e)": "CO2_HEBDO",
        "Distance hebdo (km)": "DIST_HEBDO",
        "Durée A/R (min)": "DUREE"
    }
    metric_label = st.selectbox("Indicateur principal", options=list(metric_map.keys()), index=0)
    metric = metric_map[metric_label]

# --- KPIs (dernière année)
latest = tables["timeseries_all"].copy()
if latest.shape[0] > 0 and latest["ANNEE"].notna().any():
    last_year = int(latest["ANNEE"].dropna().max())
    k = latest[latest["ANNEE"] == last_year].iloc[0]
    kpi1 = f"{k['CO2_HEBDO']:,.0f} g"
    kpi2 = f"{k['DIST_HEBDO']:,.1f} km"
    kpi3 = f"{k['DUREE']:,.1f} min"
else:
    last_year, kpi1, kpi2, kpi3 = None, "…", "…", "…"
    k = {}

c1, c2, c3 = st.columns(3)
c1.metric("CO₂ hebdo moyen / pers.", kpi1)
c2.metric("Distance hebdo / pers.", kpi2)
c3.metric("Durée A/R moyenne", kpi3)

# --- Sections
intro.render()
overview.render(tables, selected_regions=sel_regions, metric=metric)
deep_dives.render(tables, year=year if years else None, metric=metric)

st.markdown("### Qualité des données")
dq = tables["dq"]
st.dataframe(dq, use_container_width=True)
st.info(
    "Moyennes pondérées par IPONDI. Les trajets >100 km ne sont pas inclus dans le champ CO₂. "
    "Les DOM sont indicatifs (à partir de 2022). Les codes région sont normalisés à 2 chiffres."
)

# --- Conclusions
conclusions.render({
    "co2_mean_g": f"{k.get('CO2_HEBDO', 0):,.0f}" if k else "…",
    "dist_mean_km": f"{k.get('DIST_HEBDO', 0):,.1f}" if k else "…",
})
