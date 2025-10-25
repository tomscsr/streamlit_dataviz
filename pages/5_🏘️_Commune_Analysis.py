import streamlit as st
import pandas as pd
import numpy as np
from utils.io import load_data
from utils.prep import build_model
from utils.viz import (
    scatter_plot, histogram, box_plot, bar_chart,
    horizontal_bar_chart, line_chart_timeseries
)

st.set_page_config(page_title="Commune Analysis - Vacant Housing", page_icon="🏘️", layout="wide")

@st.cache_data(show_spinner=False)
def get_data():
    df_dep, df_com = load_data()
    model = build_model(df_dep, df_com)
    return model

model = get_data()

st.title("🏘️ Commune-Level Analysis")
st.caption("Explore vacancy patterns across 30,000+ French communes")

# Prepare commune data
com_long = model["df_com_long"]

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    
    years = sorted(com_long["year"].dropna().unique())
    selected_year = st.selectbox("Year", years, index=len(years)-1)
    
    # Region filter
    regions = ["All"] + sorted(com_long["reg_name"].dropna().unique())
    selected_region = st.selectbox("Region", regions)
    
    # Department filter
    if selected_region != "All":
        departments = ["All"] + sorted(
            com_long[com_long["reg_name"] == selected_region]["dep_name"].dropna().unique()
        )
    else:
        departments = ["All"] + sorted(com_long["dep_name"].dropna().unique())
    
    selected_department = st.selectbox("Department", departments)
    
    # EPCI filter
    if selected_department != "All":
        epcis = ["All"] + sorted(
            com_long[com_long["dep_name"] == selected_department]["epci_name"].dropna().unique()
        )
    else:
        epcis = ["All"]
    
    selected_epci = st.selectbox("EPCI (inter-commune)", epcis)
    
    # Metric
    metric = st.selectbox(
        "Primary metric",
        ["vacant", "vacant_2y", "total"],
        index=0
    )
    
    # Min threshold for filtering small communes
    min_total = st.slider(
        "Minimum total dwellings (filter small communes)",
        min_value=0,
        max_value=1000,
        value=50,
        step=50
    )

# Filter data
filtered = com_long[com_long["year"] == selected_year].copy()

if selected_region != "All":
    filtered = filtered[filtered["reg_name"] == selected_region]

if selected_department != "All":
    filtered = filtered[filtered["dep_name"] == selected_department]

if selected_epci != "All":
    filtered = filtered[filtered["epci_name"] == selected_epci]

# Pivot to wide format for easier analysis
commune_data = filtered.pivot_table(
    index=["com_code", "com_name", "dep_name", "reg_name", "epci_name"],
    columns="metric",
    values="value",
    aggfunc="sum"
).reset_index()

# Ensure columns exist
for c in ["total", "vacant", "vacant_2y"]:
    if c not in commune_data.columns:
        commune_data[c] = 0

# Convert to numeric to avoid dtype issues
commune_data["total"] = pd.to_numeric(commune_data["total"], errors='coerce').fillna(0)
commune_data["vacant"] = pd.to_numeric(commune_data["vacant"], errors='coerce').fillna(0)
commune_data["vacant_2y"] = pd.to_numeric(commune_data["vacant_2y"], errors='coerce').fillna(0)

# Calculate rates (avoid division by zero)
commune_data["vacancy_rate"] = commune_data.apply(
    lambda row: (row["vacant"] / row["total"] * 100) if row["total"] > 0 else 0,
    axis=1
)
commune_data["vacancy_2y_rate"] = commune_data.apply(
    lambda row: (row["vacant_2y"] / row["total"] * 100) if row["total"] > 0 else 0,
    axis=1
)

# Apply minimum threshold
commune_data = commune_data[commune_data["total"] >= min_total]

# If no data after filters, stop early to avoid empty-chart warnings
if len(commune_data) == 0:
    st.warning("No communes match the selected filters. Try widening the filters or lowering the minimum dwellings.")
    st.stop()

# Overview
st.markdown("## 📊 Commune Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Communes Analyzed",
    f"{len(commune_data):,}".replace(",", " "),
    delta=None
)

if len(commune_data) > 0:
    col2.metric(
        "Total Dwellings",
        f"{int(commune_data['total'].sum()):,}".replace(",", " "),
        delta=None
    )
    
    col3.metric(
        "Total Vacant",
        f"{int(commune_data['vacant'].sum()):,}".replace(",", " "),
        delta=(
            f"{commune_data['vacant'].sum() / commune_data['total'].sum() * 100:.2f}%"
            if commune_data['total'].sum() > 0 else None
        )
    )
    
    col4.metric(
        "Avg Vacancy Rate",
        f"{commune_data['vacancy_rate'].mean():.2f}%",
        delta=f"σ={commune_data['vacancy_rate'].std():.2f}%"
    )

# Distribution Analysis
st.markdown("## 📊 Distribution Analysis")

tab1, tab2 = st.tabs(["Vacancy Rate", "Dwelling Count"])

with tab1:
    st.subheader("Distribution of Vacancy Rates Across Communes")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        chart = histogram(
            commune_data,
            "vacancy_rate",
            bins=40,
            title="Vacancy Rate Distribution"
        )
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.markdown("### Statistics")
        st.metric("Mean", f"{commune_data['vacancy_rate'].mean():.2f}%")
        st.metric("Median", f"{commune_data['vacancy_rate'].median():.2f}%")
        st.metric("Std Dev", f"{commune_data['vacancy_rate'].std():.2f}%")
        st.metric("Min", f"{commune_data['vacancy_rate'].min():.2f}%")
        st.metric("Max", f"{commune_data['vacancy_rate'].max():.2f}%")
        
        # Percentiles
        p25 = commune_data['vacancy_rate'].quantile(0.25)
        p75 = commune_data['vacancy_rate'].quantile(0.75)
        st.caption(f"P25: {p25:.2f}% | P75: {p75:.2f}%")

with tab2:
    st.subheader("Distribution of Total Dwellings")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        chart = histogram(
            commune_data,
            "total",
            bins=40,
            title="Total Dwellings Distribution"
        )
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.markdown("### Size Categories")
        
        # Categorize communes by size
        commune_data["size_category"] = pd.cut(
            commune_data["total"],
            bins=[0, 100, 500, 1000, 5000, float('inf')],
            labels=["Very Small (<100)", "Small (100-500)", "Medium (500-1k)", "Large (1k-5k)", "Very Large (5k+)"]
        )
        
        size_dist = commune_data["size_category"].value_counts().sort_index()
        
        st.dataframe(
            pd.DataFrame({
                "Category": size_dist.index,
                "Count": size_dist.values,
                "Percentage": (size_dist.values / len(commune_data) * 100)
            }).style.format({"Percentage": "{:.1f}%"}),
            hide_index=True
        )

##
# Outlier detection section removed to simplify and avoid edge-case noise.

# Rankings
st.markdown("## 🏆 Top/Bottom Communes")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 20 Highest Vacancy Rates")
    
    top_20 = commune_data.nlargest(20, "vacancy_rate")[
        ["com_name", "dep_name", "vacancy_rate", "vacant", "total"]
    ]
    
    chart = horizontal_bar_chart(
        top_20,
        x="vacancy_rate",
        y="com_name",
        sort="-x",
        title="Highest Vacancy Rates"
    )
    st.altair_chart(chart, use_container_width=True)

with col2:
    st.subheader("Top 20 by Absolute Vacant Count")
    
    top_20_abs = commune_data.nlargest(20, "vacant")[
        ["com_name", "dep_name", "vacant", "vacancy_rate", "total"]
    ]
    
    chart = horizontal_bar_chart(
        top_20_abs,
        x="vacant",
        y="com_name",
        sort="-x",
        title="Most Vacant Dwellings"
    )
    st.altair_chart(chart, use_container_width=True)

##
# Relationship (scatter) analysis removed to focus on core, interpretable visuals.

##
# Comparative analysis section removed to reduce complexity and avoid sparse-category issues.

# Search and Explore
st.markdown("## 🔍 Search and Explore")

search_term = st.text_input(
    "Search commune by name",
    placeholder="Enter commune name..."
)

if search_term:
    search_results = commune_data[
        commune_data["com_name"].str.contains(search_term, case=False, na=False)
    ]
    
    st.write(f"Found {len(search_results)} matching commune(s)")
    
    if len(search_results) > 0:
        display_cols = ["com_name", "dep_name", "total", "vacant", "vacant_2y", "vacancy_rate", "vacancy_2y_rate"]
        
        st.dataframe(
            search_results[display_cols].style.format({
                "total": "{:,.0f}",
                "vacant": "{:,.0f}",
                "vacant_2y": "{:,.0f}",
                "vacancy_rate": "{:.2f}%",
                "vacancy_2y_rate": "{:.2f}%"
            }),
            hide_index=True,
            use_container_width=True
        )

# Detailed Table with Filters
st.markdown("## 📋 Detailed Commune Data")

col1, col2, col3 = st.columns(3)

with col1:
    sort_by = st.selectbox(
        "Sort by",
        ["com_name", "vacancy_rate", "vacant", "total"],
        index=1
    )

with col2:
    sort_order = st.radio("Order", ["Descending", "Ascending"])

with col3:
    max_rows = st.number_input("Max rows to display", min_value=10, max_value=1000, value=100)

ascending = (sort_order == "Ascending")
display_data = commune_data.sort_values(sort_by, ascending=ascending).head(max_rows)

display_cols = ["com_name", "dep_name", "epci_name", "total", "vacant", "vacant_2y", "vacancy_rate", "vacancy_2y_rate"]
available_cols = [c for c in display_cols if c in display_data.columns]

st.dataframe(
    display_data[available_cols].style.format({
        "total": "{:,.0f}",
        "vacant": "{:,.0f}",
        "vacant_2y": "{:,.0f}",
        "vacancy_rate": "{:.2f}%",
        "vacancy_2y_rate": "{:.2f}%"
    }),
    hide_index=True,
    use_container_width=True,
    height=400
)

# Download
csv = display_data[available_cols].to_csv(index=False)
st.download_button(
    label="📥 Download filtered data as CSV",
    data=csv,
    file_name=f"commune_data_{selected_year}.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("💡 Use filters in the sidebar to narrow your analysis to specific regions, departments, or EPCIs.")
