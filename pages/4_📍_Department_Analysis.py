import streamlit as st
import pandas as pd
import numpy as np
from utils.io import load_data, ensure_departements_geojson
from utils.prep import build_model
from utils.viz import (
    line_chart_timeseries, bar_chart, horizontal_bar_chart,
    map_departements, scatter_plot, histogram, box_plot
)

st.set_page_config(page_title="Department Analysis - Vacant Housing", page_icon="📍", layout="wide")

@st.cache_data(show_spinner=False)
def get_data():
    df_dep, df_com = load_data()
    model = build_model(df_dep, df_com)
    return model

# Ensure GeoJSON
ensure_departements_geojson()

model = get_data()

st.title("📍 Department Analysis")
st.caption("Granular insights across 100+ French departments")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    years = sorted(model["years_available"])
    selected_year = st.select_slider("Year for maps/rankings", options=years, value=max(years))
    
    year_range = st.slider(
        "Time series range",
        min_value=min(years),
        max_value=max(years),
        value=(min(years), max(years))
    )
    
    # Region filter
    regions = ["All"] + sorted(model["regions"])
    selected_region = st.selectbox("Filter by region", regions)
    
    # Department selector
    by_dep_year = model["by_dep_year"]
    if selected_region != "All" and "reg_name" in by_dep_year.columns:
        # Prefer explicit region field when available
        region_deps = by_dep_year[by_dep_year["reg_name"] == selected_region]["dep_name"].unique().tolist()
    elif selected_region != "All":
        # Fallback: best-effort text match
        region_deps = by_dep_year[
            by_dep_year["dep_name"].str.contains(selected_region, case=False, na=False)
        ]["dep_name"].unique().tolist()
    else:
        region_deps = sorted(by_dep_year["dep_name"].unique())
    
    selected_departments = st.multiselect(
        "Focus on specific departments",
        options=sorted(region_deps),
        default=[]
    )
    
    metric = st.selectbox(
        "Map metric",
        ["vacancy_rate", "vacancy_2y_rate", "vacant", "vacant_2y"],
        index=0
    )

# Filter data
filtered = by_dep_year[by_dep_year["year"].between(year_range[0], year_range[1])].copy()

if selected_departments:
    filtered = filtered[filtered["dep_name"].isin(selected_departments)]

latest_dep = filtered[filtered["year"] == selected_year].copy()

# Ensure numeric for safety
for col in ["total", "vacant", "vacant_2y", "vacancy_rate", "vacancy_2y_rate"]:
    if col in latest_dep.columns:
        latest_dep[col] = pd.to_numeric(latest_dep[col], errors='coerce')
    if col in filtered.columns:
        filtered[col] = pd.to_numeric(filtered[col], errors='coerce')

# Overview metrics
st.markdown("## 📊 Department Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Departments",
    len(latest_dep),
    delta=None
)

if len(latest_dep) > 0 and "vacancy_rate" in latest_dep.columns:
    col2.metric(
        "Avg Vacancy Rate",
        f"{latest_dep['vacancy_rate'].mean():.2f}%",
        delta=f"σ={latest_dep['vacancy_rate'].std():.2f}%"
    )
    
    col3.metric(
        "Highest",
        latest_dep.nlargest(1, "vacancy_rate")["dep_name"].iloc[0],
        delta=f"{latest_dep['vacancy_rate'].max():.2f}%"
    )
    
    col4.metric(
        "Lowest",
        latest_dep.nsmallest(1, "vacancy_rate")["dep_name"].iloc[0],
        delta=f"{latest_dep['vacancy_rate'].min():.2f}%"
    )

# Interactive Map
st.markdown("## 🗺️ Interactive Department Map")

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader(f"{metric} - {selected_year}")
    
    map_data = latest_dep[["dep_code", "dep_name", metric, "year"]].dropna()
    
    if len(map_data) > 0:
        fig = map_departements(map_data, metric)
        
        if fig is None:
            st.warning("Map unavailable. Showing bar chart instead.")
            chart = horizontal_bar_chart(
                map_data.sort_values(metric, ascending=False).head(20),
                x=metric,
                y="dep_name",
                title=f"Top 20 Departments by {metric}"
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for selected filters")

with col2:
    st.markdown("### Map Legend")
    st.info("""
    **Darker colors** indicate higher values.
    
    Hover over departments to see exact values.
    
    Use filters to focus on specific regions or time periods.
    """)
    
    if len(map_data) > 0:
        st.markdown("### Quick Stats")
        st.metric("Max", f"{map_data[metric].max():.2f}")
        st.metric("Median", f"{map_data[metric].median():.2f}")
        st.metric("Min", f"{map_data[metric].min():.2f}")

# Rankings
st.markdown("## 🏆 Department Rankings")

tab1, tab2, tab3 = st.tabs(["Top Performers", "Bottom Performers", "Biggest Changes"])

with tab1:
    st.subheader("Top 15 Departments by Selected Metric")
    
    top_15 = latest_dep.nlargest(15, metric)[["dep_name", metric, "vacant", "total"]]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        chart = horizontal_bar_chart(
            top_15,
            x=metric,
            y="dep_name",
            sort="-x",
            title=f"Top 15 by {metric}"
        )
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.dataframe(
            top_15.style.format({
                metric: "{:.2f}" if "rate" in metric else "{:,.0f}",
                "vacant": "{:,.0f}",
                "total": "{:,.0f}"
            }),
            hide_index=True,
            height=400
        )

with tab2:
    st.subheader("Bottom 15 Departments")
    
    bottom_15 = latest_dep.nsmallest(15, metric)[["dep_name", metric, "vacant", "total"]]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        chart = horizontal_bar_chart(
            bottom_15,
            x=metric,
            y="dep_name",
            sort="x",
            title=f"Bottom 15 by {metric}"
        )
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.dataframe(
            bottom_15.style.format({
                metric: "{:.2f}" if "rate" in metric else "{:,.0f}",
                "vacant": "{:,.0f}",
                "total": "{:,.0f}"
            }),
            hide_index=True,
            height=400
        )

with tab3:
    st.subheader("Biggest Changes Over Selected Period")
    
    earliest_dep = filtered[filtered["year"] == year_range[0]]
    latest_comp = filtered[filtered["year"] == year_range[1]]
    
    change_data = latest_comp.merge(
        earliest_dep[["dep_name", metric]],
        on="dep_name",
        suffixes=("_latest", "_earliest")
    )
    
    if len(change_data) > 0:
        change_data["absolute_change"] = (
            change_data[f"{metric}_latest"] - change_data[f"{metric}_earliest"]
        )
        change_data["pct_change"] = (
            (change_data[f"{metric}_latest"] / change_data[f"{metric}_earliest"] - 1) * 100
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Top 10 Increases**")
            increases = change_data.nlargest(10, "absolute_change")[
                ["dep_name", "absolute_change", "pct_change"]
            ]
            
            chart = bar_chart(
                increases,
                x="dep_name",
                y="absolute_change",
                sort="-y",
                title="Largest Increases"
            )
            st.altair_chart(chart, use_container_width=True)
        
        with col2:
            st.markdown("**Top 10 Decreases**")
            decreases = change_data.nsmallest(10, "absolute_change")[
                ["dep_name", "absolute_change", "pct_change"]
            ]
            
            chart = bar_chart(
                decreases,
                x="dep_name",
                y="absolute_change",
                sort="y",
                title="Largest Decreases"
            )
            st.altair_chart(chart, use_container_width=True)

# Time Series for Selected Departments
st.markdown("## 📈 Time Series Analysis")

if selected_departments:
    st.subheader(f"Trends for Selected Departments")
    
    dept_trends = filtered[filtered["dep_name"].isin(selected_departments)]
    
    col1, col2 = st.columns(2)
    
    with col1:
        chart = line_chart_timeseries(
            dept_trends[["year", "vacancy_rate", "dep_name"]],
            x="year",
            y="vacancy_rate",
            color="dep_name",
            title="Vacancy Rate Over Time"
        )
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        chart = line_chart_timeseries(
            dept_trends[["year", "vacant", "dep_name"]],
            x="year",
            y="vacant",
            color="dep_name",
            title="Vacant Count Over Time"
        )
        st.altair_chart(chart, use_container_width=True)
else:
    st.info("Select specific departments in the sidebar to see their time series")

# Distribution Analysis
st.markdown("## 📊 Distribution Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Vacancy Rate Distribution")
    
    if "vacancy_rate" in latest_dep.columns:
        chart = histogram(
            latest_dep,
            "vacancy_rate",
            bins=30,
            title="Distribution of Vacancy Rates"
        )
        st.altair_chart(chart, use_container_width=True)
        
        st.caption(f"""
        Mean: {latest_dep['vacancy_rate'].mean():.2f}% | 
        Median: {latest_dep['vacancy_rate'].median():.2f}% | 
        Std: {latest_dep['vacancy_rate'].std():.2f}%
        """)

with col2:
    st.subheader("Vacant Dwellings Distribution")
    
    if "vacant" in latest_dep.columns and len(latest_dep) > 0:
        chart = histogram(
            latest_dep,
            "vacant",
            bins=30,
            title="Distribution of Vacant Counts"
        )
        st.altair_chart(chart, use_container_width=True)
    
    if len(latest_dep) > 0:
        st.caption(f"""
        Mean: {latest_dep['vacant'].mean():,.0f} | 
        Median: {latest_dep['vacant'].median():,.0f} | 
        Std: {latest_dep['vacant'].std():,.0f}
        """.replace(",", " "))

##
# Correlation section removed to keep the analysis concise and robust.

# Detailed Table
st.markdown("## 📋 Detailed Department Data")

if len(latest_dep) > 0:
    display_cols = ["dep_name", "total", "vacant", "vacant_2y"]
    if "vacancy_rate" in latest_dep.columns:
        display_cols.append("vacancy_rate")
    if "vacancy_2y_rate" in latest_dep.columns:
        display_cols.append("vacancy_2y_rate")
    
    table_data = latest_dep[display_cols].sort_values("dep_name")
    
    format_dict = {
        "total": "{:,.0f}",
        "vacant": "{:,.0f}",
        "vacant_2y": "{:,.0f}",
    }
    if "vacancy_rate" in display_cols:
        format_dict["vacancy_rate"] = "{:.2f}%"
    if "vacancy_2y_rate" in display_cols:
        format_dict["vacancy_2y_rate"] = "{:.2f}%"
    
    st.dataframe(
        table_data.style.format(format_dict),
        hide_index=True,
        use_container_width=True,
        height=400
    )
    
    # Download button
    csv = table_data.to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"department_data_{selected_year}.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("💡 Drill down to commune-level data in the Commune Analysis page.")
