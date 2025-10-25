import streamlit as st
import pandas as pd
import numpy as np
from utils.io import load_data
from utils.prep import build_model
from utils.viz import (
    line_chart_timeseries, bar_chart, horizontal_bar_chart, 
    heatmap, area_chart, scatter_plot, small_multiples
)

st.set_page_config(page_title="Regional Analysis - Vacant Housing", page_icon="🗺️", layout="wide")

@st.cache_data(show_spinner=False)
def get_data():
    df_dep, df_com = load_data()
    model = build_model(df_dep, df_com)
    return model

model = get_data()

st.title("🗺️ Regional Analysis")
st.caption("Compare vacancy patterns across France's 18 regions")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    years = sorted(model["years_available"])
    year_range = st.select_slider("Year range", options=years, value=(min(years), max(years)))
    
    regions = sorted(model["regions"])
    selected_regions = st.multiselect(
        "Focus on specific regions",
        options=regions,
        default=[]
    )
    
    metric = st.selectbox(
        "Primary metric",
        ["vacant", "vacant_2y", "vacancy_rate", "vacancy_2y_rate"]
    )

# Filter data
by_reg_year = model["by_reg_year"]
filtered = by_reg_year[by_reg_year["year"].between(year_range[0], year_range[1])].copy()

# Ensure numeric types for key metrics early (avoids dtype object issues)
for col in ["total", "vacant", "vacant_2y", "vacancy_rate", "vacancy_2y_rate"]:
    if col in filtered.columns:
        filtered[col] = pd.to_numeric(filtered[col], errors="coerce")

if selected_regions:
    filtered = filtered[filtered["reg_name"].isin(selected_regions)]
    display_regions = selected_regions
else:
    display_regions = regions

# Regional overview
st.markdown("## 📊 Regional Overview (Latest Year)")

latest_year = year_range[1]
latest_regional = filtered[filtered["year"] == latest_year].copy()

# Coerce numerics on the latest-year slice as well
for col in ["total", "vacant", "vacant_2y", "vacancy_rate", "vacancy_2y_rate"]:
    if col in latest_regional.columns:
        latest_regional[col] = pd.to_numeric(latest_regional[col], errors="coerce")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Regions Analyzed",
    len(latest_regional),
    delta=None
)

if len(latest_regional) > 0:
    # Ensure vacancy_rate is numeric
    if "vacancy_rate" in latest_regional.columns:
        latest_regional["vacancy_rate"] = pd.to_numeric(latest_regional["vacancy_rate"], errors='coerce')
    
    col2.metric(
        "Highest Vacancy Rate",
        latest_regional.nlargest(1, "vacancy_rate")["reg_name"].iloc[0] if "vacancy_rate" in latest_regional.columns and len(latest_regional) > 0 else "N/A",
        delta=f"{latest_regional['vacancy_rate'].max():.2f}%" if "vacancy_rate" in latest_regional.columns else None
    )
    
    col3.metric(
        "Lowest Vacancy Rate",
        latest_regional.nsmallest(1, "vacancy_rate")["reg_name"].iloc[0] if "vacancy_rate" in latest_regional.columns and len(latest_regional) > 0 else "N/A",
        delta=f"{latest_regional['vacancy_rate'].min():.2f}%" if "vacancy_rate" in latest_regional.columns else None
    )

# Regional Rankings
st.markdown("## 🏆 Regional Rankings")

tab1, tab2, tab3 = st.tabs(["Vacancy Rate", "Absolute Count", "Long-term Vacancy"])

with tab1:
    st.subheader("Regions by Vacancy Rate (Latest Year)")
    
    if "vacancy_rate" in latest_regional.columns and latest_regional["vacancy_rate"].notna().any():
        ranked = latest_regional[["reg_name", "vacancy_rate", "vacant", "total"]].sort_values(
            "vacancy_rate", ascending=False
        )
        
        chart = horizontal_bar_chart(
            ranked,
            x="vacancy_rate",
            y="reg_name",
            sort="-x",
            title="Vacancy Rate (%)"
        )
        st.altair_chart(chart, use_container_width=True)
        
        st.dataframe(
            ranked.style.format({
                "vacancy_rate": "{:.2f}%",
                "vacant": "{:,.0f}",
                "total": "{:,.0f}"
            }),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No vacancy rate data available for the selected period.")

with tab2:
    st.subheader("Regions by Vacant Dwellings Count")
    
    if "vacant" in latest_regional.columns and latest_regional["vacant"].notna().any():
        ranked = latest_regional[["reg_name", "vacant", "total", "vacancy_rate"]].sort_values(
            "vacant", ascending=False
        )
        chart = horizontal_bar_chart(
            ranked,
            x="vacant",
            y="reg_name",
            sort="-x",
            title="Vacant Dwellings (Count)"
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No vacant dwellings data available for the selected period.")

with tab3:
    st.subheader("Regions by Long-term Vacancy Rate")
    
    if "vacancy_2y_rate" in latest_regional.columns and latest_regional["vacancy_2y_rate"].notna().any():
        ranked = latest_regional[["reg_name", "vacancy_2y_rate", "vacant_2y"]].sort_values(
            "vacancy_2y_rate", ascending=False
        )
        
        chart = horizontal_bar_chart(
            ranked,
            x="vacancy_2y_rate",
            y="reg_name",
            sort="-x",
            title="Long-term Vacancy Rate (%)"
        )
        st.altair_chart(chart, use_container_width=True)

# Time Series Comparison
st.markdown("## 📈 Regional Trends Over Time")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Evolution of {metric}")
    
    # Select top regions for clarity
    trend_data = filtered
    if metric in latest_regional.columns and latest_regional[metric].notna().any() and len(display_regions) > 10:
        # Guard nlargest with numeric coercion
        try:
            top_regions = latest_regional.nlargest(10, metric)["reg_name"].tolist()
            trend_data = filtered[filtered["reg_name"].isin(top_regions)]
            st.caption("Showing top 10 regions by selected metric for clarity")
        except Exception:
            # Fallback to all selected regions
            pass
    
    if len(trend_data) > 0:
        chart = line_chart_timeseries(
            trend_data[["year", metric, "reg_name"]],
            x="year",
            y=metric,
            color="reg_name",
            title=f"{metric} by Region"
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No data available to plot trends for the selected settings.")

with col2:
    st.subheader("Growth Rate Analysis")
    
    earliest_year = year_range[0]
    earliest_regional = filtered[filtered["year"] == earliest_year].copy()
    for col in ["total", "vacant", "vacant_2y", "vacancy_rate", "vacancy_2y_rate"]:
        if col in earliest_regional.columns:
            earliest_regional[col] = pd.to_numeric(earliest_regional[col], errors="coerce")
    
    # Calculate change
    change_data = latest_regional.merge(
        earliest_regional[["reg_name", metric]],
        on="reg_name",
        suffixes=("_latest", "_earliest")
    )
    
    if len(change_data) > 0 and change_data[f"{metric}_earliest"].notna().any():
        change_data["pct_change"] = (
            (change_data[f"{metric}_latest"] / change_data[f"{metric}_earliest"] - 1) * 100
        )
        # Drop inf/-inf from division by zero
        change_data["pct_change"] = change_data["pct_change"].replace([np.inf, -np.inf], np.nan)
        change_data = change_data.dropna(subset=["pct_change"]) 
        top_growth = change_data.nlargest(5, "pct_change")[ ["reg_name", "pct_change"] ]
        
        st.markdown("**Top 5 Growth**")
        st.dataframe(
            top_growth.style.format({"pct_change": "{:+.1f}%"}),
            hide_index=True
        )

# Heatmap: Regional Evolution
st.markdown("## 🔥 Heatmap: Regional Evolution")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Vacancy Rate Over Time")
    
    # Pivot for heatmap
    if "vacancy_rate" in filtered.columns and filtered["vacancy_rate"].notna().any():
        heatmap_data = filtered.pivot_table(
            index="reg_name",
            columns="year",
            values="vacancy_rate",
            aggfunc="mean"
        ).reset_index()
        
        # Melt back for Altair
        heatmap_melted = heatmap_data.melt(
            id_vars="reg_name",
            var_name="year",
            value_name="vacancy_rate"
        )
        
        chart = heatmap(
            heatmap_melted,
            x="year",
            y="reg_name",
            color="vacancy_rate",
            title="Vacancy Rate Heatmap"
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No vacancy rate data available to build the heatmap for the selected period.")

with col2:
    st.subheader("Long-term Vacancy Rate Over Time")
    
    if "vacancy_2y_rate" in filtered.columns and filtered["vacancy_2y_rate"].notna().any():
        heatmap_data = filtered.pivot_table(
            index="reg_name",
            columns="year",
            values="vacancy_2y_rate",
            aggfunc="mean"
        ).reset_index()
        
        heatmap_melted = heatmap_data.melt(
            id_vars="reg_name",
            var_name="year",
            value_name="vacancy_2y_rate"
        )
        
        chart = heatmap(
            heatmap_melted,
            x="year",
            y="reg_name",
            color="vacancy_2y_rate",
            title="LT Vacancy Rate Heatmap"
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No long-term vacancy rate data available to build the heatmap for the selected period.")

##
# Composition and scatter sections removed to keep only coherent, robust visuals.

# Detailed Regional Comparison
st.markdown("## 📋 Detailed Regional Comparison Table")

if len(latest_regional) > 0:
    comparison_cols = ["reg_name", "total", "vacant", "vacant_2y"]
    if "vacancy_rate" in latest_regional.columns:
        comparison_cols.append("vacancy_rate")
    if "vacancy_2y_rate" in latest_regional.columns:
        comparison_cols.append("vacancy_2y_rate")
    
    comparison_table = latest_regional[comparison_cols].sort_values("vacant", ascending=False)
    
    format_dict = {
        "total": "{:,.0f}",
        "vacant": "{:,.0f}",
        "vacant_2y": "{:,.0f}",
    }
    if "vacancy_rate" in comparison_cols:
        format_dict["vacancy_rate"] = "{:.2f}%"
    if "vacancy_2y_rate" in comparison_cols:
        format_dict["vacancy_2y_rate"] = "{:.2f}%"
    
    st.dataframe(
        comparison_table.style.format(format_dict),
        hide_index=True,
        use_container_width=True
    )

# Statistical Summary
st.markdown("## 📊 Statistical Summary by Region")

summary_stats = latest_regional[["vacant", "vacancy_rate", "vacant_2y"]].describe()

st.dataframe(
    summary_stats.style.format("{:.2f}"),
    use_container_width=True
)

st.markdown("---")
st.caption("💡 Explore specific departments within regions in the Department Analysis page.")
