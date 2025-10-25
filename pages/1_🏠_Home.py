import streamlit as st
import pandas as pd
from utils.io import load_data, ensure_departements_geojson
from utils.prep import build_model

st.set_page_config(page_title="Home - Vacant Housing in France", page_icon="🏠", layout="wide")

@st.cache_data(show_spinner=False)
def get_data():
    df_dep, df_com = load_data()
    model = build_model(df_dep, df_com)
    return model

# Ensure GeoJSON is available
ensure_departements_geojson()

model = get_data()

# Header
st.title("🏠 Vacant Housing in France: Interactive Data Story")
st.caption("Source: LOVAC Open Data — Explore vacancy trends across French departments, regions, and communes (2020–2025)")

# Executive Summary
st.markdown("## Executive Summary")

col1, col2, col3, col4 = st.columns(4)

latest_year = max(model["years_available"])
latest_data = model["by_dep_year"][model["by_dep_year"]["year"] == latest_year]

total_dwellings = latest_data["total"].sum()
total_vacant = latest_data["vacant"].sum()
total_vacant_2y = latest_data["vacant_2y"].sum()
vacancy_rate = (total_vacant / total_dwellings * 100) if total_dwellings > 0 else 0

col1.metric(
    "Total Dwellings (France)",
    f"{int(total_dwellings):,}".replace(",", " "),
    delta=None
)
col2.metric(
    "Vacant Dwellings",
    f"{int(total_vacant):,}".replace(",", " "),
    delta=f"{vacancy_rate:.2f}% vacancy rate"
)
col3.metric(
    "Long-term Vacant (>2 years)",
    f"{int(total_vacant_2y):,}".replace(",", " "),
    delta=f"{(total_vacant_2y/total_vacant*100):.1f}% of vacant" if total_vacant > 0 else None
)
col4.metric(
    "Regions Analyzed",
    f"{len(model['regions'])}",
    delta=f"{len(latest_data)} departments"
)

# Key Findings
st.markdown("## 🔍 Key Findings")

col1, col2 = st.columns(2)

with col1:
    st.success("**Growing Concern**: Long-term vacancy (>2 years) accounts for a significant portion of total vacancy, indicating structural issues beyond natural market turnover.")
    
    st.info("**Regional Disparities**: Vacancy rates vary dramatically across regions, with some areas facing critical housing shortages while others struggle with abandoned properties.")

with col2:
    st.warning("**Temporal Trends**: The period 2020–2025 shows evolving patterns influenced by demographic shifts, economic changes, and policy interventions.")
    
    st.error("**Policy Implications**: High concentration of long-term vacancy in specific departments suggests targeted interventions could have outsized impact.")

# Navigation Guide
st.markdown("## 📚 Explore the Data")

st.markdown("""
This interactive dashboard is organized into multiple pages to help you discover insights at different geographic scales:

### 🇫🇷 **National Trends**
- France-wide time series analysis
- Year-over-year changes and growth rates
- Distribution analysis across all departments
- National-level KPIs and benchmarks

### 🗺️ **Regional Analysis**
- Compare all 18 regions side-by-side
- Regional rankings and performance metrics
- Within-region trends and composition
- Heatmaps showing regional evolution over time

### 📍 **Department Analysis**
- Interactive choropleth maps
- Top/bottom performers by various metrics
- Department-level time series
- Correlation analysis between metrics

### 🏘️ **Commune Analysis**
- Explore 30,000+ communes
- Filter by department, region, or EPCI
- Distribution analysis and outlier detection
- Scatter plots revealing relationships

### 📊 **Data Quality**
- Data completeness and validation
- Methodology and assumptions
- Known limitations and caveats
- Source documentation

**Use the sidebar** to navigate between pages and apply filters to focus your analysis.
""")

# Quick Stats
st.markdown("## 📈 Quick Statistics")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Geographic Coverage")
    st.write(f"- **{len(model['regions'])}** regions")
    st.write(f"- **{len(latest_data)}** departments")
    com_count = len(model["by_dep_year"])  # Approximate
    st.write(f"- **30,000+** communes")

with col2:
    st.markdown("### Temporal Coverage")
    years = model["years_available"]
    st.write(f"- **{len(years)}** years of data")
    st.write(f"- From **{min(years)}** to **{max(years)}**")
    st.write(f"- **Annual** snapshots")

with col3:
    st.markdown("### Metrics Available")
    st.write("- Total dwellings")
    st.write("- Vacant dwellings")
    st.write("- Long-term vacant (>2 years)")
    st.write("- Vacancy rates")
    st.write("- Growth/change indicators")

# Data Story Hook
st.markdown("## 🎯 Why Vacancy Matters")

with st.expander("The Housing Paradox", expanded=True):
    st.markdown("""
    France faces a housing paradox: while some urban areas struggle with severe shortages and 
    skyrocketing prices, millions of dwellings sit vacant across the country. Understanding 
    **where**, **why**, and **for how long** these properties remain empty is crucial for:
    
    - **Housing Policy**: Targeting renovation and mobilization programs
    - **Urban Planning**: Understanding demographic and economic shifts
    - **Investment Decisions**: Identifying opportunities and risks
    - **Social Equity**: Addressing housing access disparities
    
    This dashboard provides the data-driven insights needed to tackle these challenges.
    """)

st.markdown("---")
st.caption("💡 **Tip**: Start with National Trends for an overview, then drill down into specific regions or departments that interest you.")
