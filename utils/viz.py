from __future__ import annotations
from pathlib import Path
from typing import Optional

import pandas as pd
import altair as alt
import plotly.express as px

from .io import DEPARTEMENTS_GEOJSON


def _theme_chart(c: alt.Chart) -> alt.Chart:
    return (
        c.properties(width="container", height=320)
         .configure_axis(labelColor="#333", titleColor="#333")
         .configure_view(strokeOpacity=0)
    )


def line_chart_timeseries(df: pd.DataFrame, x: str, y: str, color: Optional[str] = None, tooltip: Optional[list] = None, title: str = ""):
    tooltip = tooltip or [x, y]
    base = alt.Chart(df)
    enc = {
        "x": alt.X(x, title="Year"),
        "y": alt.Y(y, title=title or y, scale=alt.Scale(zero=False)),
        "tooltip": tooltip,
    }
    if color:
        enc["color"] = color
    c = base.mark_line(point=True).encode(**enc)
    return _theme_chart(c)


def bar_chart(df: pd.DataFrame, x: str, y: str, color: Optional[str] = None, sort: str = "-y", title: str = ""):
    enc = {
        "x": alt.X(x, sort=sort, title=x),
        "y": alt.Y(y, title=title or y),
        "tooltip": [x, y] + ([color] if color else []),
    }
    if color:
        enc["color"] = color
    c = alt.Chart(df).mark_bar().encode(**enc)
    return _theme_chart(c)


def small_multiples(df: pd.DataFrame, facet: str, x: str, y: str, title: str = ""):
    c = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X(x, title=x),
        y=alt.Y(y, title=title or y, scale=alt.Scale(zero=False)),
        tooltip=[x, y, facet],
        facet=alt.Facet(facet, columns=4)
    )
    return _theme_chart(c)


def map_departements(df_latest_dep: pd.DataFrame, metric_col: str, color_continuous_scale: str = "Viridis"):
    """
    Plotly choropleth for departments. Requires assets/departements.geojson to exist.
    The df must have columns: dep_code (str), dep_name, <metric_col> and year.
    """
    if not DEPARTEMENTS_GEOJSON.exists():
        return None  # caller can handle fallback

    # Department codes in df are like '01', '2A', etc. Ensure string type
    df = df_latest_dep.copy()
    df["dep_code"] = df["dep_code"].astype(str)

    import json
    with open(DEPARTEMENTS_GEOJSON, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="dep_code",
        featureidkey="properties.code",
        color=metric_col,
        color_continuous_scale=color_continuous_scale,
        hover_name="dep_name",
        hover_data={metric_col: ":.2f" if "rate" in metric_col else True, "dep_code": False},
        projection="mercator",
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return fig
