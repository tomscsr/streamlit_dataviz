# utils/viz.py
from __future__ import annotations
import altair as alt
import pandas as pd

# Style Altair cohérent
alt.themes.enable("opaque")

TOOLTIP_NUM = [
    alt.Tooltip("ANNEE:O", title="Année"),
    alt.Tooltip("CO2_HEBDO:Q", title="CO₂ hebdo (g)"),
    alt.Tooltip("DIST_HEBDO:Q", title="Distance hebdo (km)"),
    alt.Tooltip("DUREE:Q", title="Durée A/R (min)"),
]

def line_chart(df: pd.DataFrame, y: str, title: str):
    return (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("ANNEE:O", title="Année"),
            y=alt.Y(f"{y}:Q", title={
                "CO2_HEBDO": "CO₂ hebdomadaire par pers. (gCO₂e)",
                "DIST_HEBDO": "Distance hebdomadaire par pers. (km)",
                "DUREE": "Durée moyenne A/R (min)"
            }.get(y, y)),
            tooltip=TOOLTIP_NUM
        )
        .properties(title=title, height=280)
        .interactive()
    )

def bar_chart(df: pd.DataFrame, y: str, color: str | None = None, title: str = ""):
    enc_color = alt.Color(color, legend=None) if color else alt.value("#4C78A8")
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("REGION:N", sort="-y", title="Région (résidence)"),
            y=alt.Y(f"{y}:Q", title={
                "CO2_HEBDO": "CO₂ hebdomadaire par pers. (gCO₂e)",
                "DIST_HEBDO": "Distance hebdomadaire par pers. (km)",
                "CO2_KM_U": "Intensité CO₂ par km (gCO₂e/km)"
            }.get(y, y)),
            color=enc_color,
            tooltip=[
                alt.Tooltip("REGION:N", title="Région"),
                alt.Tooltip(f"{y}:Q", title="Valeur"),
                alt.Tooltip("IPONDI:Q", title="Actifs pondérés", format=",.0f")
            ],
        )
        .properties(title=title, height=300)
        .interactive()
    )

def mode_share_chart(df: pd.DataFrame, title: str = ""):
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("MODTRANS:N", title="Mode de transport"),
            y=alt.Y("PART:Q", axis=alt.Axis(format="%"), title="Part des actifs (pondérée)"),
            tooltip=[
                alt.Tooltip("MODTRANS:N", title="Mode"),
                alt.Tooltip("PART:Q", title="Part", format=".1%"),
                alt.Tooltip("IPONDI:Q", title="Actifs pondérés", format=",.0f"),
            ],
            color=alt.Color("MODTRANS:N", legend=None),
        )
        .properties(title=title, height=300)
        .interactive()
    )

def tile_map(df: pd.DataFrame, value_col: str, title: str):
    """
    Carte tuiles des régions métropolitaines + DROM (grille 2D).
    Colonnes attendues: REG_RESID, REGION, tx, ty, value_col.
    """
    d = df.copy()
    d["tile"] = 1  # pour dessiner un carré
    chart = (
        alt.Chart(d)
        .mark_rect(stroke="white")
        .encode(
            x=alt.X("tx:O", axis=None),
            y=alt.Y("ty:O", sort="ascending", axis=None),
            color=alt.Color(f"{value_col}:Q",
                            title={
                                "CO2_HEBDO":"CO₂ hebdo (gCO₂e)",
                                "DIST_HEBDO":"Distance hebdo (km)",
                                "CO2_KM_U":"gCO₂e par km"
                            }.get(value_col, value_col),
                            scale=alt.Scale(scheme="blues")),
            tooltip=[
                alt.Tooltip("REGION:N", title="Région"),
                alt.Tooltip(f"{value_col}:Q", title="Valeur"),
            ]
        )
        .properties(title=title, height=320)
        .interactive()
    )
    # Libellés région
    labels = (
        alt.Chart(d)
        .mark_text(baseline="middle", align="center", dy=0, size=10)
        .encode(x="tx:O", y="ty:O", text="REG_RESID:N")
    )
    return chart + labels
