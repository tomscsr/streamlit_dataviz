"""
France's Vacant Housing Crisis - Data Storytelling Dashboard

A comprehensive analysis of vacant housing patterns across France (2020-2025),
examining national trends, departmental variations, and commune-level insights
to inform housing policy and urban planning decisions.

Author: Data Storytelling Project
Data Source: LOVAC Open Data (data.gouv.fr)
License: Open License 2.0
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import utilities
from utils.io import load_department_data, load_commune_data, get_data_license
from utils.prep import identify_data_quality_issues

# Import section pages
import sections.intro as intro
import sections.overview as overview
import sections.departmental as departmental
import sections.commune as commune
import sections.conclusions as conclusions


# Page configuration
st.set_page_config(
    page_title="France's Vacant Housing Crisis",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stAlert {
        margin-top: 1rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading data...")
def load_all_data():
    """
    Load and cache all datasets.
    
    Returns:
        tuple: (df_dept, df_commune, data_quality_report)
    """
    # Load datasets
    df_dept = load_department_data()
    df_commune = load_commune_data()
    
    # Generate data quality reports
    dept_quality = identify_data_quality_issues(df_dept)
    commune_quality = identify_data_quality_issues(df_commune)
    
    quality_report = {
        'department': dept_quality,
        'commune': commune_quality
    }
    
    return df_dept, df_commune, quality_report


def main():
    """Main application entry point."""
    
    # Load data
    with st.spinner("Loading datasets..."):
        df_dept, df_commune, quality_report = load_all_data()
    
    # Sidebar navigation
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Flag_of_France.svg/320px-Flag_of_France.svg.png", width=100)
    st.sidebar.title("Navigation")
    st.sidebar.markdown("### France's Vacant Housing")
    
    # Page selection
    page = st.sidebar.radio(
        "Select a section:",
        [
            "🏠 Introduction",
            "🇫🇷 National Overview",
            "🗺️ Departmental Analysis",
            "🏘️ Commune Deep Dive",
            "📋 Conclusions"
        ],
        label_visibility="collapsed"
    )
    
    # Data quality indicator
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Data Status")
    st.sidebar.success(f"""
    ✅ Department data: {quality_report['department']['total_rows']} rows  
    ✅ Commune data: {quality_report['commune']['total_rows']:,} rows  
    ℹ️ Last update: 2025
    """)
    
    # Display data quality details in expander
    with st.sidebar.expander("Data Quality Details"):
        st.markdown("**Department Data**")
        st.write(f"- Total departments: {quality_report['department']['total_rows']}")
        st.write(f"- Duplicates: {quality_report['department']['duplicates']}")
        
        st.markdown("**Commune Data**")
        st.write(f"- Total communes: {quality_report['commune']['total_rows']:,}")
        st.write(f"- Duplicates: {quality_report['commune']['duplicates']}")
        st.write(f"- Records with suppressed data: ~{(df_commune['pp_vacant_25'].isna().sum() / len(df_commune) * 100):.1f}%")
    
    # About section in sidebar
    st.sidebar.markdown("---")
    with st.sidebar.expander("ℹ️ About This Dashboard"):
        st.markdown("""
        This interactive dashboard analyzes **vacant housing data** across France 
        from 2020 to 2025, covering:
        
        - 🇫🇷 National trends and KPIs
        - 🗺️ Department-level comparisons  
        - 🏘️ Commune-level deep dives
        - 📊 Data-driven policy insights
        
        **Built with**: Streamlit, Plotly, Pandas  
        **Data**: LOVAC Open Data (data.gouv.fr)
        """)
    
    # Quick stats in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Quick Stats (2025)")
    
    # Calculate quick stats (use 2024 total as 2025 total doesn't exist)
    total_vacant_2025 = df_dept['pp_vacant_25'].sum()
    total_properties_2024 = df_dept['pp_total_24'].sum()  # Use 2024 total
    national_rate_2025 = (total_vacant_2025 / total_properties_2024 * 100)
    
    st.sidebar.metric("National Vacancy Rate", f"{national_rate_2025:.2f}%")
    st.sidebar.metric("Total Vacant Units", f"{total_vacant_2025:,.0f}")
    st.sidebar.metric("Departments Analyzed", len(df_dept))
    
    # Download section
    st.sidebar.markdown("---")
    with st.sidebar.expander("⬇️ Download Data"):
        st.markdown("""
        **Data Sources**:
        - [LOVAC Department Data](https://www.data.gouv.fr)
        - [LOVAC Commune Data](https://www.data.gouv.fr)
        
        **License**: Open License 2.0  
        Free to use with attribution
        """)
    
    # Main content area - route to selected page
    st.sidebar.markdown("---")
    
    # Page routing
    if page == "🏠 Introduction":
        intro.show()
    
    elif page == "🇫🇷 National Overview":
        overview.show(df_dept)
    
    elif page == "🗺️ Departmental Analysis":
        departmental.show(df_dept)
    
    elif page == "🏘️ Commune Deep Dive":
        commune.show(df_commune)
    
    elif page == "📋 Conclusions":
        conclusions.show(df_dept)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("""
    **Built with** ❤️ using Streamlit  
    **Data**: French Open Data (data.gouv.fr)  
    **License**: Open License 2.0  
    © 2025 Data Storytelling Project
    """)


if __name__ == "__main__":
    # Error handling
    try:
        main()
    except Exception as e:
        st.error(f"""
        **An error occurred**: {str(e)}
        
        Please check:
        - Data files are in the `data/` folder
        - Required packages are installed
        - File paths are correct
        """)
        
        # Show detailed error in expander
        with st.expander("Show detailed error"):
            import traceback
            st.code(traceback.format_exc())
