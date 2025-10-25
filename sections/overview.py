# sections/overview.py
import streamlit as st
import pandas as pd
from utils.viz import line_chart, bar_chart, tile_map

def render(tables: dict, selected_regions: list[str] | None, metric: str):
    st.header("Panorama : évolutions et écarts régionaux")

    # Timeseries (filtrée éventuellement par régions)
    st.subheader("Évolution temporelle (moyenne pondérée)")
    ts = tables["timeseries_all"].copy()
    if selected_regions:
        # recalcul léger côté front : on pourrait aussi préparer côté prep
        pass
    st.altair_chart(line_chart(ts, y=metric, title="Tendance nationale"), use_container_width=True)

    # Classement barres (dernière année dispo)
    st.subheader("Comparaison des régions (dernière année)")
    last_year = int(ts["ANNEE"].dropna().max()) if ts["ANNEE"].notna().any() else None
    reg = tables["by_region"].copy()
    if last_year is not None:
        reg = reg[reg["ANNEE"] == last_year]
    reg = reg.rename(columns={"REGION": "REGION"})  # déjà présent via merge
    st.altair_chart(
        bar_chart(
            reg.sort_values(metric, ascending=False)[["REGION", metric, "IPONDI"]],
            y=metric, title=f"Rang régional — {last_year}"
        ),
        use_container_width=True,
    )

    # Carte tuiles
    st.subheader("Carte (grille tuiles des régions)")
    map_df = reg[["REG_RESID", "REGION", "tx", "ty", metric]].dropna()
    st.altair_chart(tile_map(map_df, value_col=metric, title="Niveaux par région"), use_container_width=True)
