from __future__ import annotations
import pandas as pd
import streamlit as st

from utils.viz import line_chart_timeseries, bar_chart, map_departements


def _format_kpi(val, is_rate=False):
    if pd.isna(val):
        return "—"
    if is_rate:
        return f"{val:.2f}%"
    return f"{int(val):,}".replace(",", " ")


def render_overview(st, model, scope):
    st.markdown("## Overview")

    by_dep_year = model["by_dep_year"]
    by_reg_year = model["by_reg_year"]
    metric = scope["metric"]
    y0, y1 = scope["year_min"], scope["year_max"]

    # Scope filter
    dep_filtered = by_dep_year.query("@y0 <= year <= @y1").copy()
    reg_filtered = by_reg_year.query("@y0 <= year <= @y1").copy()
    if scope["region"]:
        reg_filtered = reg_filtered[reg_filtered["reg_name"] == scope["region"]]

    # KPI row — National totals over selected years (latest year primary)
    latest_year = y1
    nat_latest = by_dep_year[by_dep_year["year"] == latest_year].sum(numeric_only=True)
    nat_base = by_dep_year[by_dep_year["year"] == y0].sum(numeric_only=True)

    kpi_value = nat_latest[metric]
    kpi_rate = nat_latest.get("vacancy_rate", pd.NA) if metric == "vacant" else (nat_latest[metric] if "rate" in metric else pd.NA)
    delta = None
    if metric in ("vacant", "vacant_2y"):
        delta_val = nat_latest[metric] - nat_base[metric]
        delta = f"{int(delta_val):+,}".replace(",", " ")
    elif "rate" in metric:
        delta_val = (nat_latest[metric] - nat_base[metric])
        delta = f"{delta_val:+.2f} pp"

    c1, c2, c3 = st.columns(3)
    c1.metric("Latest value (France)", _format_kpi(kpi_value, is_rate=False), delta)
    c2.metric("Vacancy rate (France, latest)", _format_kpi(nat_latest.get("vacancy_rate", pd.NA), is_rate=True))
    c3.metric(
        "Long-term vacancy rate (France, latest)", _format_kpi(nat_latest.get("vacancy_2y_rate", pd.NA), is_rate=True)
    )

    st.subheader("Trends over time")
    # National trend
    nat_trend = (
        by_dep_year.groupby("year", as_index=False).sum(numeric_only=True)
        .assign(region="France (sum of departments)")
    )

    chart = line_chart_timeseries(
        nat_trend[["year", metric, "region"]], x="year", y=metric, color="region", title=metric
    )
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Compare regions")
    # Compare regions at latest year by chosen metric
    reg_latest = by_reg_year[by_reg_year["year"] == latest_year][["reg_name", metric]].dropna()
    reg_latest = reg_latest.sort_values(metric, ascending=False)
    st.altair_chart(bar_chart(reg_latest, x="reg_name", y=metric, sort="-y", title=metric), use_container_width=True)

    st.subheader("Map view (departments, latest year)")
    latest_dep = model["latest_dep"][["dep_code", "dep_name", metric, "year"]]
    fig = map_departements(latest_dep, metric)
    if fig is None:
        st.warning("Department GeoJSON not available (no internet or file missing). Showing small multiples by region instead.")
        # fallback: small multiples per region time series
        fallback = by_reg_year[["reg_name", "year", metric]].dropna()
        fallback = fallback.sort_values(["reg_name", "year"])  # tidy
        st.altair_chart(
            line_chart_timeseries(fallback, x="year", y=metric, color="reg_name", title=metric),
            use_container_width=True,
        )
    else:
        st.plotly_chart(fig, use_container_width=True)
