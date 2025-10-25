# sections/intro.py
import streamlit as st
from utils.io import LICENSE

def render():
    st.header("Pourquoi s’intéresser aux trajets domicile-travail ?")
    st.write(
        "Les déplacements domicile-travail représentent une part significative des émissions "
        "de gaz à effet de serre liées à la mobilité quotidienne. Cette application explore "
        "les **distances parcourues**, les **durées de trajet** et les **émissions hebdomadaires de CO₂ par personne**, "
        "en s’appuyant sur la base Insee/SDES (champ « mobilité locale »)."
    )
    with st.expander("Hypothèses & limites des données"):
        st.markdown(
            "- Les émissions sont calculées *du réservoir à la roue* (pas d’émissions amont).\n"
            "- Champ limité aux trajets < **100 km** et à la France métropolitaine (volet ultramarin indicatif à partir de 2022).\n"
            "- Les indicateurs affichés sont des **moyennes pondérées par IPONDI** (actifs représentés).\n"
            "- L’année **2020** est atypique (crise sanitaire) et peut être absente selon le millésime.\n"
            "- Les valeurs par mode dépendent du **mode principal déclaré**."
        )
    st.caption(LICENSE)
