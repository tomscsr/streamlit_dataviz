# sections/deep_dives.py
import streamlit as st
import pandas as pd
from utils.viz import mode_share_chart, bar_chart

def render(tables: dict, year: int, metric: str):
    st.header("Explorations détaillées")

    # Parts modales (année choisie)
    st.subheader("Modes de transport (parts pondérées)")
    m = tables["by_mode"].copy()
    if "ANNEE" in m.columns and year is not None:
        m = m[m["ANNEE"] == year]
    st.altair_chart(mode_share_chart(m, title=f"Répartition par mode — {year}"), use_container_width=True)

    # Intensité CO₂ par km vs régions
    st.subheader("Intensité CO₂ par km (gCO₂e/km)")
    reg = tables["by_region"].copy()
    if year is not None:
        reg = reg[reg["ANNEE"] == year]
    reg = reg.sort_values("CO2_KM_U", ascending=False)
    st.altair_chart(
        bar_chart(reg[["REGION", "CO2_KM_U", "IPONDI"]], y="CO2_KM_U",
                  title=f"Intensité régionale — {year}"),
        use_container_width=True
    )

    with st.expander("Notes méthodologiques"):
        st.markdown(
            "- Les parts par mode utilisent la somme de `IPONDI` par mode sur l’année.\n"
            "- Les intensités `CO2_KM_U = CO2_HEBDO / DIST_HEBDO`."
        )
