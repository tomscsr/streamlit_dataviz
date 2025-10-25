"""
Conclusions page: Key findings and policy implications.
"""
import streamlit as st
import pandas as pd
from utils.prep import prepare_national_aggregates


def show(df_dept):
    """
    Display conclusions with key findings and implications.
    
    Args:
        df_dept: Department-level DataFrame
    """
    
    st.title("Conclusions: Insights & Policy Implications")
    st.markdown("### What we learned and what it means for housing policy")
    
    st.warning("""
    **Important Methodological Note**: All conclusions in this section are based on data through 2025, 
    which represents a partial year. Year-over-year comparisons involving 2025 should be interpreted 
    with caution as they do not reflect complete annual cycles.
    """)
    
    # Prepare summary data
    national_ts = prepare_national_aggregates(df_dept)
    latest_year = national_ts['year'].max()
    latest = national_ts[national_ts['year'] == latest_year].iloc[0]
    earliest = national_ts[national_ts['year'] == 2020].iloc[0]
    full_years = national_ts[national_ts['year'] <= 2024]
    if not full_years.empty:
        latest_full_year = full_years['year'].max()
        latest_full = national_ts[national_ts['year'] == latest_full_year].iloc[0]
    else:
        latest_full_year = latest_year
        latest_full = latest
    
    # Executive Summary
    st.markdown("---")
    st.header("Executive Summary")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
          This analysis examined **France's vacant housing landscape from 2020-2025**, 
        covering all 101 departments and ~35,000 communes.
        
        **Key Findings:**
        
          1. **Scale**: France recorded approximately **{latest_full['vacant_properties']:,.0f} vacant properties** 
              in {latest_full_year}, representing **{latest_full['vacancy_rate']:.2f}%** of the total housing stock 
              (2025 figures are a partial-year snapshot of **{latest['vacant_properties']:,.0f} vacant units**).
        
          2. **Trend**: Vacancy has {'increased' if latest_full['vacant_properties'] > earliest['vacant_properties'] else 'decreased'} 
              by **{abs(latest_full['vacant_properties'] - earliest['vacant_properties']):,.0f} units** 
              ({abs((latest_full['vacant_properties'] - earliest['vacant_properties']) / earliest['vacant_properties'] * 100):.1f}%) 
              since 2020.
        
          3. **Structural Problem**: **{latest_full['longterm_share']:.1f}%** of vacant properties were 
              empty for 2+ years in {latest_full_year}, indicating chronic rather than transitional vacancy 
              (2025 snapshot: **{latest['longterm_share']:.1f}%**).
        
        4. **Geographic Inequality**: Vacancy rates vary dramatically—from under 5% in growing urban 
           areas to over 15% in declining rural regions
        
        5. **Local Context Matters**: Even within the same department, commune-level vacancy can 
           differ by 10+ percentage points
        """)
    
    with col2:
        st.info(f"""
    **Core Metrics ({latest_full_year} full year)**
        
    **Total Properties:**  
    **{latest_full['total_properties']:,.0f}**
        
    **Vacant:**  
    **{latest_full['vacant_properties']:,.0f}**
        
    **Vacancy Rate:**  
    **{latest_full['vacancy_rate']:.2f}%**
        
    **Vacant 2+ Years:**  
    **{latest_full['vacant_2plus_years']:,.0f}**
        
    **Long-term Rate:**  
    **{latest_full['longterm_vacancy_rate']:.2f}%**
        
    **2025 Snapshot (partial year):**
    {latest['vacant_properties']:,.0f} vacant units | {latest['vacant_2plus_years']:,.0f} vacant 2+ years
        """)
    
    # Major Insights
    st.markdown("---")
    st.header("Major Insights")
    
    insights = [
        {
            "title": "The Two Frances: Urban Shortage vs. Rural Surplus",
            "content": """
            France exhibits a **dual housing crisis**:
            - **Growing urban areas** (Paris region, Lyon, Toulouse, etc.) face housing shortages with vacancy rates below 7%
            - **Declining rural areas** suffer from excess vacant housing (>12% vacancy), often in poor condition
            
            **Implication**: One-size-fits-all policies won't work. Urban areas need new construction and 
            renovation incentives, while rural areas need demolition programs and adaptive reuse strategies.
            """
        },
        {
            "title": "Chronic Vacancy Indicates Market Failure",
            "content": """
            Over **half of vacant properties** have been empty for 2+ years. This isn't normal market 
            churn—it's structural dysfunction caused by:
            - Properties in poor condition requiring expensive renovations
            - Unclear ownership (inheritance disputes, multiple heirs)
            - Speculative holding in anticipation of price increases
            - Mismatch between property characteristics and market demand
            
            **Implication**: Tax incentives for long-term vacancy and streamlined renovation permitting 
            could mobilize these properties back to the market.
            """
        },
        {
            "title": "Vacancy Growing Faster Than Housing Stock",
            "content": f"""
            While France's housing stock grew steadily from 2020 through {latest_full_year}, vacant properties increased 
            at a faster rate in many regions—suggesting market inefficiencies are worsening.
            
            **Implication**: New construction alone won't solve housing shortages if properties keep 
            falling vacant. Focus on utilization rates, not just supply.
            """
        },
        {
            "title": "Small Communes Face Greatest Challenges",
            "content": """
            Communes with fewer than 500 properties show the highest vacancy rates, often exceeding 15%.
            These are typically rural villages experiencing:
            - Population decline and aging demographics
            - Loss of local services (schools, shops, doctors)
            - Poor transportation connectivity
            - Limited employment opportunities
            
            **Implication**: Regional development policies must address root causes (economic vitality, 
            services) rather than just housing supply.
            """
        }
    ]
    
    for i, insight in enumerate(insights, 1):
        with st.expander(f"**Insight {i}: {insight['title']}**", expanded=True):
            st.markdown(insight['content'])
    
    # Policy Recommendations
    st.markdown("---")
    st.header("Policy Recommendations")
    
    st.markdown("""
    Based on this analysis, we recommend a **differentiated policy approach** targeting 
    different types of vacancy:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("For Urban Areas (Low Vacancy)")
        
        st.markdown("""
        **Challenge**: Housing shortages, affordability crisis
        
        **Recommended Actions**:
        1. **Accelerate new construction** with streamlined permitting
        2. **Convert non-residential** buildings (offices, hotels) to housing
        3. **Incentivize density** through zoning reforms
        4. **Combat speculation** with vacancy taxes in tight markets
        5. **Expand public/social housing** stock
        6. **Improve transportation** to unlock peripheral areas
        
        **Expected Impact**: Reduce competition, improve affordability
        """)
        
        st.success("""
        **Success Metric**: Keep vacancy rates between 5-7% (healthy market turnover) 
        while expanding total housing supply.
        """)
    
    with col2:
        st.subheader("For Rural Areas (High Vacancy)")
        
        st.markdown("""
        **Challenge**: Oversupply, deteriorating housing stock, population decline
        
        **Recommended Actions**:
        1. **Strategic demolition** of uninhabitable properties
        2. **Renovation subsidies** for habitable but outdated stock
        3. **Tax penalties** for long-term vacancy (2+ years)
        4. **Simplify ownership** (inheritance law reforms)
        5. **Repurpose vacant buildings** (community centers, co-working)
        6. **Economic revitalization** (remote work incentives, tourism)
        
        **Expected Impact**: Reduce blight, stabilize remaining communities
        """)
        
        st.warning("""
        **Realistic Expectation**: Some rural areas will continue to decline. 
        Focus on managed transition, not reversal.
        """)
    
    # For High Long-term Vacancy
    st.subheader("Specific Measures for Long-term Vacant Properties")
    
    st.markdown("""
    Properties vacant for **2+ years** require targeted interventions:
    
    - **Graduated vacancy tax**: Increases with duration of vacancy
    - **Fast-track renovation permitting**: Remove bureaucratic barriers
    - **Ownership identification programs**: Help resolve inheritance issues
    - **Acquisition powers**: Allow municipalities to purchase chronically vacant properties
    - **Renovation grants**: Subsidize return to habitability
    - **Legal reforms**: Simplify partition sales for co-owned properties
    
    **Goal**: Reduce 2+ year vacancy by 20% within 5 years
    """)
    
    # Data Limitations
    st.markdown("---")
    st.header("Limitations & Future Research")
    
    st.warning("""
    **This Analysis Has Limitations**:
    
    - **Causality**: We describe patterns but cannot establish causation (correlation ≠ causation)
    - **Privacy suppression**: Small communes have missing data, potentially biasing results
    - **Administrative lag**: Tax-based data may not reflect real-time occupancy
    - **Quality indicators**: No information on property condition, habitability
    - **Economic context**: Missing integration with employment, income, demographic data
    - **Second homes**: Not distinguished from investment/speculative vacancy
    
    **Recommended Further Research**:
    1. Integrate with INSEE demographic data for migration patterns
    2. Analyze property condition surveys where available
    3. Study correlation with local economic indicators (unemployment, wages)
    4. Compare second home concentrations with vacancy rates
    5. Conduct qualitative case studies in high-vacancy communes
    6. Model scenarios for different policy interventions
    """)
    
    # Call to Action
    st.markdown("---")
    st.header("Call to Action")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **For Policymakers**
        
        Use this data to:
        - Target interventions geographically
        - Differentiate urban vs. rural strategies
        - Monitor policy effectiveness over time
        - Allocate renovation subsidies efficiently
        """)
    
    with col2:
        st.markdown("""
        **For Local Officials**
        
        Use this data to:
        - Benchmark against similar communes
        - Identify properties for acquisition
        - Prioritize renovation programs
        - Make the case for regional support
        """)
    
    with col3:
        st.markdown("""
        **For Researchers**
        
        Use this data to:
        - Study housing market dynamics
        - Evaluate policy impacts
        - Identify research gaps
        - Develop predictive models
        """)
    
    # Final Takeaway
    st.markdown("---")
    st.success("""
    ### Bottom Line
    
    France has a **significant vacant housing problem**, but it's not uniform. The solution requires:
    
    1. **Geographic targeting**: Different policies for urban vs. rural contexts
    2. **Time-sensitive action**: Prioritize properties vacant 2+ years
    3. **Root cause focus**: Address economic and demographic drivers, not just housing supply
    4. **Data-driven monitoring**: Track metrics over time to evaluate effectiveness
    5. **Multi-stakeholder collaboration**: National frameworks with local implementation
    
    **With approximately {:.0f} properties sitting empty—including {:.0f} vacant for 2+ years (full-year {latest_full_year} figures)—
    there's enormous potential to address housing needs without new construction** if the right 
    incentives and interventions are deployed strategically.
    """.format(
        latest_full['vacant_properties'],
        latest_full['vacant_2plus_years'],
        latest_full_year=latest_full_year
    ))
    
    # Acknowledgments
    st.markdown("---")
    st.caption("""
    **Data Source**: LOVAC (Logements Vacants) Open Data, French Government (data.gouv.fr)  
    **License**: Open License 2.0  
    **Last Updated**: 2025
    """)
