from __future__ import annotations
import pandas as pd
import streamlit as st

from utils.viz import bar_chart, line_chart_timeseries


def render_deep_dives(st, model, scope):
    st.markdown("## Deep Dives")

    metric = scope["metric"]
    y0, y1 = scope["year_min"], scope["year_max"]
    region = scope["region"]
    top_n = int(scope.get("top_n", 10))

    by_dep_year = model["by_dep_year"].query("@y0 <= year <= @y1").copy()
    by_reg_year = model["by_reg_year"].query("@y0 <= year <= @y1").copy()

    # 1) Rankings: Top/Bottom N departments at latest year
    st.subheader("Rankings — departments (latest year)")
    latest_year = by_dep_year["year"].max()
    dep_latest = by_dep_year[by_dep_year["year"] == latest_year][["dep_name", metric]].dropna()
    dep_top = dep_latest.nlargest(top_n, metric)
    dep_bottom = dep_latest.nsmallest(top_n, metric)

    c1, c2 = st.columns(2)
    with c1:
        st.caption(f"Top {top_n} departments by {metric} ({latest_year})")
        st.altair_chart(bar_chart(dep_top, x="dep_name", y=metric, sort="-y"), use_container_width=True)
    with c2:
        st.caption(f"Bottom {top_n} departments by {metric} ({latest_year})")
        st.altair_chart(bar_chart(dep_bottom, x="dep_name", y=metric, sort="y"), use_container_width=True)

    # 2) Distribution over time for a chosen region (sum of its departments)
    st.subheader("Within-region trend (sum of departments)")
    if region:
        reg_trend = by_reg_year[by_reg_year["reg_name"] == region][["year", metric, "reg_name"]]
        st.altair_chart(line_chart_timeseries(reg_trend, x="year", y=metric, color="reg_name"), use_container_width=True)
    else:
        st.info("Pick a region in the sidebar to see its internal trend.")

    # 3) Inequality snapshot: Gini-like indicator proxy (top share vs. bottom share)
    st.subheader("Inequality snapshot — concentration across departments")
    dep_latest_sorted = dep_latest.sort_values(metric, ascending=False)
    n = len(dep_latest_sorted)
    top_share = dep_latest_sorted.head(max(1, n // 10))[metric].sum() / dep_latest_sorted[metric].sum()
    bottom_share = dep_latest_sorted.tail(max(1, n // 10))[metric].sum() / dep_latest_sorted[metric].sum()
    st.write(
        f"Top 10% departments account for {top_share*100:.1f}% of {metric}; "
        f"bottom 10% for {bottom_share*100:.1f}%."
    )
