import streamlit as st
import pandas as pd
import numpy as np
from utils.io import load_data
from utils.prep import build_model
from utils.viz import line_chart_timeseries, bar_chart, histogram

st.set_page_config(page_title="National Trends - Vacant Housing", page_icon="🇫🇷", layout="wide")

@st.cache_data(show_spinner=False)
def get_data():
    df_dep, df_com = load_data()
    model = build_model(df_dep, df_com)
    return model

model = get_data()

st.title("🇫🇷 National Trends Analysis")
st.caption("France-wide vacancy patterns and temporal evolution (2020–2025)")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    years = sorted(model["years_available"])
    year_range = st.select_slider("Year range", options=years, value=(min(years), max(years)))

# Aggregate national data
by_dep_year = model["by_dep_year"]
national_trend = by_dep_year.groupby("year", as_index=False).sum(numeric_only=True)
national_trend = national_trend[national_trend["year"].between(year_range[0], year_range[1])]

# Calculate rates safely
national_trend["vacancy_rate"] = np.where(
    national_trend["total"] > 0,
    (national_trend["vacant"] / national_trend["total"]) * 100,
    np.nan,
)
national_trend["vacancy_2y_rate"] = np.where(
    national_trend["total"] > 0,
    (national_trend["vacant_2y"] / national_trend["total"]) * 100,
    np.nan,
)

st.markdown("## 📊 Key Performance Indicators")

# KPIs row
col1, col2, col3, col4 = st.columns(4)

latest = national_trend.iloc[-1]
earliest = national_trend.iloc[0]

total_change = latest["vacant"] - earliest["vacant"]
rate_change = latest["vacancy_rate"] - earliest["vacancy_rate"]
lt_change = latest["vacant_2y"] - earliest["vacant_2y"]

col1.metric(
    "Total Dwellings (Latest)",
    f"{int(latest['total']):,}".replace(",", " "),
    delta=f"+{int(latest['total'] - earliest['total']):,}".replace(",", " ")
)

col2.metric(
    "Vacant Dwellings",
    f"{int(latest['vacant']):,}".replace(",", " "),
    delta=f"{int(total_change):+,}".replace(",", " ")
)

col3.metric(
    "Vacancy Rate",
    f"{latest['vacancy_rate']:.2f}%",
    delta=f"{rate_change:+.2f} pp"
)

col4.metric(
    "Long-term Vacant (>2y)",
    f"{int(latest['vacant_2y']):,}".replace(",", " "),
    delta=f"{int(lt_change):+,}".replace(",", " ")
)

# Time Series Analysis
st.markdown("## 📈 Time Series: National Totals")

tab1, tab2 = st.tabs(["Absolute Values", "Rates"])

with tab1:
    st.subheader("Total Dwellings and Vacancy (Count)")
    
    # Prepare data for multi-line chart
    plot_data = national_trend[["year", "total", "vacant", "vacant_2y"]].melt(
        id_vars="year", var_name="Metric", value_name="Count"
    )
    
    chart = line_chart_timeseries(
        plot_data, 
        x="year", 
        y="Count", 
        color="Metric",
        title="National Housing Stock Evolution"
    )
    st.altair_chart(chart, use_container_width=True)
    
    st.info(f"""
    **Insight**: Over {year_range[1] - year_range[0]} years, total dwellings grew by 
    {int(latest['total'] - earliest['total']):,} while vacant properties changed by 
    {int(total_change):+,}.
    """.replace(",", " "))

with tab2:
    st.subheader("Vacancy Rates (% of Total)")
    
    rate_data = national_trend[["year", "vacancy_rate", "vacancy_2y_rate"]].melt(
        id_vars="year", var_name="Rate Type", value_name="Percentage"
    )
    
    chart = line_chart_timeseries(
        rate_data,
        x="year",
        y="Percentage",
        color="Rate Type",
        title="Vacancy Rate Evolution"
    )
    st.altair_chart(chart, use_container_width=True)
    
    lt_pct = (latest["vacant_2y"] / latest["vacant"] * 100) if latest["vacant"] > 0 else 0
    st.warning(f"""
    **Long-term vacancy concern**: {lt_pct:.1f}% of all vacant dwellings have been 
    vacant for more than 2 years, suggesting structural rather than transitional vacancy.
    """)

##
# YoY change section removed to simplify and focus on core trends.

# Distribution Analysis
st.markdown("## 📉 Distribution Analysis Across Departments")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Vacancy Rate Distribution (Latest Year)")
    
    latest_dep = by_dep_year[by_dep_year["year"] == year_range[1]].copy()
    # Ensure numeric and compute rate safely
    for c in ["total", "vacant", "vacant_2y"]:
        if c in latest_dep.columns:
            latest_dep[c] = pd.to_numeric(latest_dep[c], errors='coerce')
    latest_dep["vacancy_rate"] = np.where(
        latest_dep["total"] > 0,
        (latest_dep["vacant"] / latest_dep["total"]) * 100,
        np.nan,
    )
    
    hist_chart = histogram(latest_dep, "vacancy_rate", bins=25, title="Distribution of Vacancy Rates")
    st.altair_chart(hist_chart, use_container_width=True)
    
    median_rate = latest_dep["vacancy_rate"].median()
    mean_rate = latest_dep["vacancy_rate"].mean()
    st.caption(f"Median: {median_rate:.2f}% | Mean: {mean_rate:.2f}%")

with col2:
    st.subheader("Long-term Vacancy Distribution")
    
    latest_dep["lt_vacancy_rate"] = np.where(
        latest_dep["total"] > 0,
        (latest_dep["vacant_2y"] / latest_dep["total"]) * 100,
        np.nan,
    )
    
    hist_chart = histogram(latest_dep, "lt_vacancy_rate", bins=25, title="Distribution of LT Vacancy Rates")
    st.altair_chart(hist_chart, use_container_width=True)
    
    median_lt = latest_dep["lt_vacancy_rate"].median()
    mean_lt = latest_dep["lt_vacancy_rate"].mean()
    st.caption(f"Median: {median_lt:.2f}% | Mean: {mean_lt:.2f}%")

##
# Composition section removed to streamline visuals.

##
# Growth/Cumulative change sections removed for clarity.

# Top/Bottom Performers
st.markdown("## 🏆 Department Rankings (Latest Year)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Highest Vacancy Rates")
    
    top_10 = latest_dep.nlargest(10, "vacancy_rate")[["dep_name", "vacancy_rate", "vacant"]]
    
    chart = bar_chart(top_10, x="dep_name", y="vacancy_rate", sort="-y", title="Highest Vacancy %")
    st.altair_chart(chart, use_container_width=True)

with col2:
    st.subheader("Top 10 Lowest Vacancy Rates")
    
    bottom_10 = latest_dep.nsmallest(10, "vacancy_rate")[["dep_name", "vacancy_rate", "vacant"]]
    
    chart = bar_chart(bottom_10, x="dep_name", y="vacancy_rate", sort="y", title="Lowest Vacancy %")
    st.altair_chart(chart, use_container_width=True)

##
# Correlation section removed to keep the narrative focused.

st.markdown("---")
st.caption("💡 Navigate to Regional or Department Analysis for more granular insights.")
