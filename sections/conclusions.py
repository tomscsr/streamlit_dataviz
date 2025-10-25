# sections/conclusions.py
import streamlit as st

def render(kpis: dict):
    st.header("Enseignements & pistes d’action")
    st.markdown(
        f"""
- **Niveau moyen actuel** (dernière année) : **{kpis.get('co2_mean_g', '…')} gCO₂e** par personne et par semaine,
  pour **{kpis.get('dist_mean_km', '…')} km** hebdomadaires en moyenne.
- **Écarts territoriaux marqués** : certaines régions affichent des distances et intensités plus élevées.
- **Modes de transport** : la structure modale pèse fortement sur les émissions.
        """
    )
    st.subheader("Implications / Next steps")
    st.markdown(
        "- Accélérer l’offre de transports collectifs et les alternatives (vélo, covoiturage).\n"
        "- Agir sur l’**organisation du travail** (télétravail adapté aux métiers). \n"
        "- **Aménagement** : rapprocher emploi–logement, densification autour des pôles en transport collectif.\n"
        "- Suivre les tendances annuelles pour mesurer l’efficacité des politiques publiques."
    )
