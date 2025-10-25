import streamlit as st
import pandas as pd
import numpy as np
from utils.io import load_data
from utils.prep import build_model
from utils.viz import bar_chart, heatmap, histogram

st.set_page_config(page_title="Data Quality - Vacant Housing", page_icon="📊", layout="wide")

@st.cache_data(show_spinner=False)
def get_data():
    df_dep, df_com = load_data()
    model = build_model(df_dep, df_com)
    return model

model = get_data()

st.title("📊 Data Quality & Methodology")
st.caption("Validation, completeness, and technical documentation")

# Data Sources
st.markdown("## 📚 Data Sources")

st.info("""
**LOVAC Open Data** - Logements Vacants (Vacant Housing Observatory)

- **Department-level data**: `lovac_opendata_dep.csv`
- **Commune-level data**: `lovac-opendata-communes.csv`
- **Geographic reference**: `departements.geojson` (France GeoJSON mirror)
- **License**: Presumed Open Data (verify on official portal)
- **Update frequency**: Annual snapshots
- **Coverage**: 2020–2025 (6 years)
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Department Data")
    st.write("- 100+ departments")
    st.write("- Annual totals by metric")
    st.write("- Direct aggregation")
    
with col2:
    st.markdown("### Commune Data")
    st.write("- 30,000+ communes")
    st.write("- Includes EPCI, region, department")
    st.write("- Raw counts per commune")

# Quality Notes
st.markdown("## ✅ Data Quality Summary")

st.success(model["quality_notes"])

# Completeness Analysis
st.markdown("## 📈 Data Completeness")

tab1, tab2, tab3 = st.tabs(["Missing Values", "Coverage", "Validation Checks"])

with tab1:
    st.subheader("Missing Value Analysis")
    
    # Analyze missingness in long-form data
    dep_long = model["df_dep_long"]
    com_long = model["df_com_long"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Department-Level")
        
        dep_missing = dep_long.groupby(["year", "metric"])["value"].apply(
            lambda x: x.isna().sum()
        ).reset_index(name="missing_count")
        
        # Pivot for display
        dep_pivot = dep_missing.pivot(index="year", columns="metric", values="missing_count")
        
        st.dataframe(
            dep_pivot.style.format("{:.0f}"),
            use_container_width=True
        )
        
        total_dep_rows = len(dep_long)
        total_dep_missing = dep_long["value"].isna().sum()
        pct_missing_dep = (total_dep_missing / total_dep_rows * 100)
        
        st.metric(
            "Overall Missingness",
            f"{pct_missing_dep:.2f}%",
            delta=f"{total_dep_missing:,} / {total_dep_rows:,}".replace(",", " ")
        )
    
    with col2:
        st.markdown("### Commune-Level")
        
        com_missing = com_long.groupby(["year", "metric"])["value"].apply(
            lambda x: x.isna().sum()
        ).reset_index(name="missing_count")
        
        com_pivot = com_missing.pivot(index="year", columns="metric", values="missing_count")
        
        st.dataframe(
            com_pivot.style.format("{:.0f}"),
            use_container_width=True
        )
        
        total_com_rows = len(com_long)
        total_com_missing = com_long["value"].isna().sum()
        pct_missing_com = (total_com_missing / total_com_rows * 100)
        
        st.metric(
            "Overall Missingness",
            f"{pct_missing_com:.2f}%",
            delta=f"{total_com_missing:,} / {total_com_rows:,}".replace(",", " ")
        )
    
    st.info("""
    **Note**: Missing values marked as 's' in source data represent **statistical suppression** 
    for privacy protection (typically small communes with few dwellings). These are treated as NA.
    """)

with tab2:
    st.subheader("Geographic Coverage")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Regions")
        st.metric("Total Regions", len(model["regions"]))
        st.caption("All 18 French regions covered")
    
    with col2:
        st.markdown("### Departments")
        by_dep_year = model["by_dep_year"]
        unique_depts = by_dep_year["dep_code"].nunique()
        st.metric("Total Departments", unique_depts)
        st.caption("Mainland + overseas")
    
    with col3:
        st.markdown("### Communes")
        unique_communes = com_long["com_code"].nunique()
        st.metric("Total Communes", f"{unique_communes:,}".replace(",", " "))
        st.caption("All commune-level data")
    
    # Coverage by year
    st.markdown("### Temporal Coverage")
    
    coverage_by_year = by_dep_year.groupby("year").agg({
        "dep_code": "nunique",
        "total": "sum",
        "vacant": "sum"
    }).reset_index()
    
    coverage_by_year.columns = ["Year", "Departments", "Total Dwellings", "Vacant Dwellings"]
    
    st.dataframe(
        coverage_by_year.style.format({
            "Year": "{:.0f}",
            "Departments": "{:.0f}",
            "Total Dwellings": "{:,.0f}",
            "Vacant Dwellings": "{:,.0f}"
        }),
        hide_index=True,
        use_container_width=True
    )

with tab3:
    st.subheader("Validation Checks")
    
    st.markdown("### Logical Consistency")
    
    # Check: vacant <= total
    by_dep_year = model["by_dep_year"]
    invalid_vacant = (by_dep_year["vacant"] > by_dep_year["total"]).sum()
    
    # Check: vacant_2y <= vacant
    invalid_2y = (by_dep_year["vacant_2y"] > by_dep_year["vacant"]).sum()
    
    # Check: negative values
    negative_total = (by_dep_year["total"] < 0).sum()
    negative_vacant = (by_dep_year["vacant"] < 0).sum()
    
    validation_results = pd.DataFrame({
        "Check": [
            "Vacant > Total",
            "Long-term Vacant > Vacant",
            "Negative Total",
            "Negative Vacant"
        ],
        "Violations": [
            invalid_vacant,
            invalid_2y,
            negative_total,
            negative_vacant
        ],
        "Status": [
            "✅ PASS" if invalid_vacant == 0 else "⚠️ WARNING",
            "✅ PASS" if invalid_2y == 0 else "⚠️ WARNING",
            "✅ PASS" if negative_total == 0 else "❌ FAIL",
            "✅ PASS" if negative_vacant == 0 else "❌ FAIL"
        ]
    })
    
    st.dataframe(validation_results, hide_index=True, use_container_width=True)
    
    if invalid_vacant > 0 or invalid_2y > 0:
        st.warning("""
        Some rows show logical inconsistencies (likely due to data suppression or measurement timing).
        These are flagged but retained in the dataset.
        """)

# Methodology
st.markdown("## 🔬 Methodology")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Data Processing")
    
    st.code("""
    1. Load raw CSV files (CP1252 encoding)
    2. Strip whitespace, normalize columns
    3. Parse French number format:
       - Remove spaces (thousand separators)
       - Convert 's' to NA (suppressed)
    4. Wide-to-long transformation
    5. Calculate derived metrics:
       - vacancy_rate = vacant / total × 100
       - vacancy_2y_rate = vacant_2y / total × 100
    6. Aggregate by geography and year
    """, language="python")

with col2:
    st.markdown("### Calculations")
    
    st.latex(r"""
    \text{Vacancy Rate} = \frac{\text{Vacant Dwellings}}{\text{Total Dwellings}} \times 100
    """)
    
    st.latex(r"""
    \text{LT Vacancy Rate} = \frac{\text{Vacant} > 2 \text{ years}}{\text{Total Dwellings}} \times 100
    """)
    
    st.latex(r"""
    \text{CAGR} = \left(\frac{\text{Value}_{\text{end}}}{\text{Value}_{\text{start}}}\right)^{\frac{1}{n}} - 1
    """)

# Limitations
st.markdown("## ⚠️ Known Limitations")

st.warning("""
### Data Limitations

1. **Statistical Suppression**: Small communes may have suppressed values (marked 's') for privacy
2. **Temporal Lag**: Data may reflect prior-year census information
3. **Definition Variance**: 'Vacant' definition may vary slightly by data collection method
4. **Commune Mergers**: Some communes have merged; historical data may not reflect current boundaries
5. **Missing GeoJSON**: Map requires internet on first run to download department boundaries

### Analytical Limitations

1. **Correlation ≠ Causation**: Observed patterns may not indicate causal relationships
2. **Aggregation Effects**: Regional/department totals may hide within-area variation
3. **No Price Data**: Cannot correlate with housing prices or rents
4. **No Demographic Data**: Missing population, income, or employment context
""")

# Technical Specifications
st.markdown("## ⚙️ Technical Specifications")

with st.expander("Show technical details"):
    st.markdown("""
    ### File Formats
    - **CSV Encoding**: CP1252 / Latin-1
    - **Separator**: Semicolon (`;`)
    - **Decimal**: Period (`.`)
    - **Thousands**: Space (` `) - removed during parsing
    
    ### Schema
    
    **Department CSV columns**:
    - `DEP`, `LIB_DEP`: Department code and name
    - `pp_total_YY`, `pp_vacant_YY`, `pp_vacant_plus_2ans_YY`: Metrics by year (YY = 20-25)
    
    **Commune CSV columns**:
    - `CODGEO_25`, `LIBGEO_25`: Commune code and name
    - `DEP`, `LIB_DEP`: Department
    - `REG`, `LIB_REG`: Region
    - `EPCI_25`, `LIB_EPCI_25`: Inter-commune structure
    - Metric columns same pattern as department
    
    ### Dependencies
    ```
    streamlit==1.38.0
    pandas==2.2.3
    numpy==1.26.4
    altair==5.4.1
    plotly==5.24.0
    requests==2.32.3
    ```
    """)

# Data Dictionary
st.markdown("## 📖 Data Dictionary")

data_dict = pd.DataFrame({
    "Column": [
        "total", "vacant", "vacant_2y", "vacancy_rate", "vacancy_2y_rate",
        "dep_code", "dep_name", "reg_code", "reg_name", "com_code", "com_name",
        "epci_code", "epci_name", "year"
    ],
    "Description": [
        "Total number of dwellings",
        "Number of vacant dwellings",
        "Number of dwellings vacant for more than 2 years",
        "Percentage of dwellings that are vacant",
        "Percentage of dwellings that are long-term vacant",
        "Department code (01, 02, ..., 2A, 2B, etc.)",
        "Department name",
        "Region code",
        "Region name",
        "Commune code (INSEE)",
        "Commune name",
        "EPCI code (inter-commune structure)",
        "EPCI name",
        "Year of observation (2020-2025)"
    ],
    "Type": [
        "Integer", "Integer", "Integer", "Float", "Float",
        "String", "String", "String", "String", "String", "String",
        "String", "String", "Integer"
    ]
})

st.dataframe(data_dict, hide_index=True, use_container_width=True)

# Contact and Attribution
st.markdown("## 📧 Attribution & License")

st.info("""
### Data Attribution
- **Source**: LOVAC Open Data Portal
- **Provider**: French government open data initiative
- **License**: Verify on official portal (presumed Open Data / ODbL)

### Code License
- **Repository**: (add your repo link)
- **License**: MIT
- **Author**: (your name)

### Citations
When using this dashboard or data, please cite:
```
LOVAC Open Data (2020-2025). Logements Vacants en France. 
Retrieved from [official portal URL]
```
""")

st.markdown("---")
st.caption("For questions or issues, please refer to the repository documentation.")
