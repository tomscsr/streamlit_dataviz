"""
Introduction page: Context, objectives, and data description.
"""
import streamlit as st
from utils.io import get_data_license, get_data_description


def show():
    """Display the introduction page."""
    
    st.title("🏠 France's Vacant Housing Crisis")
    st.markdown("### Understanding the Scale and Impact of Empty Homes Across France")
    
    # Hook - Why this matters
    st.markdown("---")
    st.header("💡 Why This Matters")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **France faces a housing paradox**: while millions struggle to find affordable housing, 
        hundreds of thousands of properties sit empty—some for years. This data story explores:
        
        - 📊 **The scale**: How many vacant properties exist and where?
        - 📈 **The trend**: Is vacancy increasing or decreasing over time?
        - 🗺️ **The geography**: Which regions are most affected?
        - ⏱️ **The chronicity**: How many properties are vacant long-term (2+ years)?
        - 💼 **The implications**: What does this mean for housing policy?
        
        Understanding vacant housing is crucial for urban planning, social equity, and 
        environmental sustainability. Empty homes represent wasted resources and missed 
        opportunities to address housing shortages.
        """)
    
    with col2:
        st.info("""
        **Key Questions**
        
        1. Where is vacancy highest?
        2. Is the problem getting worse?
        3. Are vacancies temporary or structural?
        4. What patterns emerge by region?
        """)
    
    # Context & Background
    st.markdown("---")
    st.header("📚 Background & Context")
    
    st.markdown("""
    ### What is Housing Vacancy?
    
    A property is considered **vacant** when it is:
    - Not occupied as a primary or secondary residence
    - Available for sale or rent, but currently empty
    - Awaiting renovation or demolition
    - Held vacant for other reasons (inheritance disputes, speculation, etc.)
    
    ### Why Do Properties Become Vacant?
    
    Common reasons include:
    - **Economic factors**: Rural depopulation, urban-rural migration
    - **Market dynamics**: Properties too expensive or in poor condition
    - **Regulatory issues**: Complex inheritance, administrative delays
    - **Speculation**: Investors holding properties for value appreciation
    - **Structural problems**: Buildings requiring major renovations
    
    ### The 2+ Year Threshold
    
    Properties vacant for **more than 2 years** are considered **structurally vacant**—
    indicating deeper issues beyond temporary market transitions. These represent the 
    most problematic cases from a policy perspective.
    """)
    
    # Data Description
    st.markdown("---")
    st.header("📊 About the Data")
    
    desc = get_data_description()
    
    st.markdown(f"""
    **Dataset**: {desc['title']}
    
    {desc['description']}
    
    ### Metrics Tracked
    """)
    
    for key, value in desc['metrics'].items():
        st.markdown(f"- **{key}**: {value}")
    
    st.markdown("### Data Coverage")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Time Period", "2020-2025", "6 years")
    with col2:
        st.metric("Departments", "101", "Full coverage")
    with col3:
        st.metric("Communes", "~35,000", "Municipal level")
    
    # Data Quality & Limitations
    st.markdown("---")
    st.header("⚠️ Data Quality & Limitations")
    
    st.warning("""
    **Important Considerations:**
    
    This analysis is based on administrative data with inherent limitations:
    """)
    
    for limitation in desc['limitations']:
        st.markdown(f"- {limitation}")
    
    st.markdown("- **Note**: 2025 data only includes vacancy counts; total property count uses 2024 baseline")
    
    st.info("""
    **Privacy Protection**: Small values (typically < 11 units) are suppressed with 's' 
    to prevent identification of individual properties. This affects some commune-level 
    statistics but not department or national aggregates.
    """)
    
    # Data License
    st.markdown("---")
    st.header("📜 Data Source & License")
    
    st.markdown(get_data_license())
    
    # Methodology Note
    st.markdown("---")
    st.header("🔬 Analytical Approach")
    
    st.markdown("""
    This dashboard uses **exploratory data analysis (EDA)** and **descriptive statistics** to:
    
    1. **Aggregate** national-level trends from department data
    2. **Compare** vacancy rates across departments and regions
    3. **Identify** outliers and patterns in the data
    4. **Visualize** geographic and temporal distributions
    5. **Classify** departments by vacancy severity
    
    All calculations are transparent and reproducible. Code is available in the repository.
    """)
    
    # Navigation hint
    st.markdown("---")
    st.success("""
    **Ready to explore?** Use the sidebar to navigate through different sections:
    - 🇫🇷 **National Overview**: High-level trends and KPIs
    - 🗺️ **Departmental Analysis**: Compare departments and regions
    - 🏘️ **Commune Deep Dive**: Municipal-level insights
    - 📋 **Conclusions**: Key findings and policy implications
    """)
