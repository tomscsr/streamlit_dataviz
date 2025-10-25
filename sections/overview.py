"""
National overview page: High-level KPIs and trends.
"""
import streamlit as st
import pandas as pd
import numpy as np
from utils.prep import (
    calculate_longterm_vacancy_rate,
    calculate_vacancy_rate,
    prepare_department_timeseries,
    prepare_national_aggregates,
)
from utils.viz import (
    COLORS,
    create_bar_chart,
    create_choropleth_map,
    create_line_chart,
    format_number,
    DEFAULT_PLOTLY_CONFIG,
)


def show(df_dept):
    """
    Display national overview with KPIs and trends.
    
    Args:
        df_dept: Department-level DataFrame
    """
    
    st.title("🇫🇷 National Overview: France's Vacant Housing Landscape")
    st.markdown("### High-level trends and key performance indicators (2020-2025)")
    
    # Prepare national data
    national_ts = prepare_national_aggregates(df_dept)
    
    # Get latest year data
    latest_year = national_ts['year'].max()
    latest_data = national_ts[national_ts['year'] == latest_year].iloc[0]
    previous_data = national_ts[national_ts['year'] == latest_year - 1].iloc[0]
    
    # KPI Header
    st.markdown("---")
    st.header(f"Key Metrics ({latest_year})")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = latest_data['total_properties']
        prev_total = previous_data['total_properties']
        
        if pd.notna(total) and pd.notna(prev_total):
            delta_total = total - prev_total
            delta_str = f"{delta_total:+,.0f} vs {latest_year-1}"
        else:
            delta_str = "N/A"
        
        st.metric(
            "Total Properties",
            format_number(total, decimals=1) if pd.notna(total) else "N/A",
            delta_str,
            delta_color="normal"
        )
    
    with col2:
        vacant = latest_data['vacant_properties']
        prev_vacant = previous_data['vacant_properties']
        
        if pd.notna(vacant) and pd.notna(prev_vacant):
            delta_vacant = vacant - prev_vacant
            delta_str = f"{delta_vacant:+,.0f} vs {latest_year-1}"
        else:
            delta_str = "N/A"
        
        st.metric(
            "Vacant Properties",
            format_number(vacant, decimals=1) if pd.notna(vacant) else "N/A",
            delta_str,
            delta_color="inverse"
        )
    
    with col3:
        rate = latest_data['vacancy_rate']
        prev_rate = previous_data['vacancy_rate']
        
        if pd.notna(rate) and pd.notna(prev_rate):
            delta_rate = rate - prev_rate
            delta_str = f"{delta_rate:+.2f}pp"
        else:
            delta_str = "N/A"
        
        st.metric(
            "National Vacancy Rate",
            f"{rate:.2f}%" if pd.notna(rate) else "N/A",
            delta_str,
            delta_color="inverse"
        )
    
    with col4:
        longterm = latest_data['vacant_2plus_years']
        prev_longterm = previous_data['vacant_2plus_years']
        
        if pd.notna(longterm) and pd.notna(prev_longterm):
            delta_longterm = longterm - prev_longterm
            delta_str = f"{delta_longterm:+,.0f}"
        else:
            delta_str = "N/A"
        
        st.metric(
            "Vacant 2+ Years",
            format_number(longterm, decimals=1) if pd.notna(longterm) else "N/A",
            delta_str,
            delta_color="inverse"
        )
    
    # Additional context metrics
    st.markdown("")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        longterm_rate = latest_data['longterm_vacancy_rate']
        st.metric(
            "Long-term Vacancy Rate",
            f"{longterm_rate:.2f}%" if pd.notna(longterm_rate) else "N/A",
            "Of all properties"
        )
    
    with col2:
        longterm_share = latest_data['longterm_share']
        st.metric(
            "Structural Vacancy Share",
            f"{longterm_share:.1f}%" if pd.notna(longterm_share) else "N/A",
            "Of vacant properties"
        )
    
    with col3:
        # Calculate absolute change from 2020 to latest
        first_data = national_ts[national_ts['year'] == 2020].iloc[0]
        
        if pd.notna(latest_data['vacant_properties']) and pd.notna(first_data['vacant_properties']):
            total_change = latest_data['vacant_properties'] - first_data['vacant_properties']
            change_str = format_number(total_change, decimals=1, prefix="+") if total_change >= 0 else format_number(total_change, decimals=1)
            change_pct = (total_change/first_data['vacant_properties']*100)
            delta_str = f"{change_pct:+.1f}%"
        else:
            change_str = "N/A"
            delta_str = None
        
        st.metric(
            "Change Since 2020",
            change_str,
            delta_str
        )
    
    # Geographic Distribution Map
    st.markdown("---")
    st.header("Geographic Distribution of Vacancy")

    available_years = sorted(
        int(f"20{suffix}")
        for suffix in ['20', '21', '22', '23', '24', '25']
        if f'pp_vacant_{suffix}' in df_dept.columns
    )
    default_year = latest_year if latest_year in available_years else available_years[-1]

    selected_year = st.select_slider(
        "Select the year to visualize",
        options=available_years,
        value=default_year
    )

    year_suffix = str(selected_year)[-2:]
    df_map = df_dept.copy()
    df_map['dep_code'] = df_map['DEP'].astype(str).str.zfill(2)
    vacancy_col = f'pp_vacant_{year_suffix}'
    longterm_col = f'pp_vacant_plus_2ans_{year_suffix}'
    df_map['vacant_count'] = df_map[vacancy_col]
    df_map['longterm_vacant_count'] = df_map[longterm_col]
    df_map['vacancy_rate'] = calculate_vacancy_rate(df_map, year_suffix)
    df_map['longterm_vacancy_rate'] = calculate_longterm_vacancy_rate(df_map, year_suffix)

    metric_type = st.select_slider(
        "Choose the metric type",
        options=["Total number", "Vacancy rate"],
        value="Total number"
    )

    vacancy_scope = st.select_slider(
        "Choose the vacancy scope",
        options=["All vacant", "Vacant 2+ years"],
        value="All vacant"
    )

    if metric_type == "Total number" and vacancy_scope == "All vacant":
        metric_col = "vacant_count"
        metric_title = "Vacant Properties"
        hover_format = ":,.0f"
        value_formatter = lambda v: f"{v:,.0f}" if pd.notna(v) else "N/A"
        std_formatter = value_formatter
    elif metric_type == "Total number" and vacancy_scope == "Vacant 2+ years":
        metric_col = "longterm_vacant_count"
        metric_title = "Vacant 2+ Years"
        hover_format = ":,.0f"
        value_formatter = lambda v: f"{v:,.0f}" if pd.notna(v) else "N/A"
        std_formatter = value_formatter
    elif metric_type == "Vacancy rate" and vacancy_scope == "All vacant":
        metric_col = "vacancy_rate"
        metric_title = "Vacancy Rate"
        hover_format = ":.2f"
        value_formatter = lambda v: f"{v:.2f}%" if pd.notna(v) else "N/A"
        std_formatter = lambda v: f"{v:.2f}pp" if pd.notna(v) else "N/A"
    else:
        metric_col = "longterm_vacancy_rate"
        metric_title = "Long-term Vacancy Rate"
        hover_format = ":.2f"
        value_formatter = lambda v: f"{v:.2f}%" if pd.notna(v) else "N/A"
        std_formatter = lambda v: f"{v:.2f}pp" if pd.notna(v) else "N/A"


    df_map_valid = df_map[
        pd.notna(df_map[metric_col]) &
        np.isfinite(df_map[metric_col])
    ].copy()

    if len(df_map_valid) > 0:
        note_lines = [
            "Use the selectors above to compare overall vacancy and long-term structural vacancy snapshots."
        ]
        if selected_year == 2025:
            note_lines.insert(0, "Note: 2025 figures are based on partial-year data and may appear lower than prior years.")
        st.info("\n".join(note_lines))

        hover_data = {'dep_code': False, metric_col: hover_format}
        fig = create_choropleth_map(
            df_map_valid,
            locations='dep_code',
            values=metric_col,
            title=f'{metric_title} by Department ({selected_year})',
            height=700,
            color_scale='Reds',
            hover_name='LIB_DEP',
            hover_data=hover_data
        )
        
        st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
        
        # Summary stats for map
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            max_idx = df_map_valid[metric_col].idxmax()
            st.metric(
                f"Highest {metric_title}",
                value_formatter(df_map_valid.loc[max_idx, metric_col]),
                df_map_valid.loc[max_idx, 'LIB_DEP']
            )
        
        with col2:
            min_idx = df_map_valid[metric_col].idxmin()
            st.metric(
                f"Lowest {metric_title}",
                value_formatter(df_map_valid.loc[min_idx, metric_col]),
                df_map_valid.loc[min_idx, 'LIB_DEP']
            )
        
        with col3:
            st.metric(
                "National Average", 
                value_formatter(df_map_valid[metric_col].mean())
            )
        
        with col4:
            st.metric("Std. Deviation", std_formatter(df_map_valid[metric_col].std()))
    else:
        st.warning(f"Insufficient data available for {metric_title.lower()} visualization.")
    
    # Trend Analysis
    st.markdown("---")
    st.header("Trends Over Time")
    
    st.warning("""
    **Important**: 2025 data represents a partial year only. Comparing 2025 vacancy metrics with 
    previous full-year data (2020-2024) may show misleading trends. Exercise caution when interpreting 
    year-over-year changes involving 2025.
    """)
    
    tab1, tab2, tab3 = st.tabs(["Vacancy Trends", "Rates & Composition", "Year-over-Year Changes"])
    
    with tab1:
        st.subheader("Total and Vacant Properties (2020-2025)")
        
        fig = create_line_chart(
            national_ts,
            x='year',
            y=['total_properties', 'vacant_properties', 'vacant_2plus_years'],
            title='Evolution of Property Counts',
            xlabel='Year',
            ylabel='Number of Properties',
            height=450
        )
        st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
        
        st.markdown("""
        **Key Observations:**
        - Total housing stock shows steady growth
        - Vacant properties trend indicates structural patterns
        - Long-term vacancy (2+ years) reveals chronic issues
        """)
    
    with tab2:
        st.subheader("Vacancy Rates and Composition")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = create_line_chart(
                national_ts,
                x='year',
                y=['vacancy_rate', 'longterm_vacancy_rate'],
                title='Vacancy Rate Trends (%)',
                xlabel='Year',
                ylabel='Vacancy Rate (%)',
                height=400
            )
            st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
        
        with col2:
            fig = create_line_chart(
                national_ts,
                x='year',
                y='longterm_share',
                title='Share of Long-term Vacancy',
                xlabel='Year',
                ylabel='% of Vacant Properties',
                height=400
            )
            st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
        
        st.info("""
        **Interpretation**: 
        - Vacancy rates normalize for housing stock growth
        - Long-term share indicates whether vacancies are temporary or structural
        - A rising long-term share suggests persistent market problems
        """)
    
    with tab3:
        st.subheader("Year-over-Year Changes")
        
        # Calculate YoY changes
        national_ts_sorted = national_ts.sort_values('year')
        national_ts_sorted['vacant_yoy_change'] = national_ts_sorted['vacant_properties'].diff()
        national_ts_sorted['vacant_yoy_pct'] = (
            national_ts_sorted['vacant_properties'].pct_change() * 100
        )
        
        # Remove first row (no comparison)
        yoy_data = national_ts_sorted[national_ts_sorted['year'] > 2020].copy()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = create_bar_chart(
                yoy_data,
                x='year',
                y='vacant_yoy_change',
                title='Annual Change in Vacant Properties',
                xlabel='Year',
                ylabel='Change in Units',
                height=400,
                text_auto=True
            )
            st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
        
        with col2:
            fig = create_bar_chart(
                yoy_data,
                x='year',
                y='vacant_yoy_pct',
                title='Annual Growth Rate (%)',
                xlabel='Year',
                ylabel='Percentage Change',
                height=400,
                text_auto=True
            )
            st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
    
    # National Summary Statistics
    st.markdown("---")
    st.header("Summary Statistics (2020-2025)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Vacancy Rate Statistics")
        
        stats_df = pd.DataFrame({
            'Metric': ['Minimum', 'Maximum', 'Average', 'Current (2025)', 'Std. Deviation'],
            'Value (%)': [
                f"{national_ts['vacancy_rate'].min():.2f}",
                f"{national_ts['vacancy_rate'].max():.2f}",
                f"{national_ts['vacancy_rate'].mean():.2f}",
                f"{latest_data['vacancy_rate']:.2f}",
                f"{national_ts['vacancy_rate'].std():.2f}"
            ]
        })
        st.dataframe(stats_df, hide_index=True, width='stretch')
    
    with col2:
        st.subheader("Long-term Vacancy Statistics")
        
        lt_stats_df = pd.DataFrame({
            'Metric': ['Minimum', 'Maximum', 'Average', 'Current (2025)', 'Std. Deviation'],
            'Value (%)': [
                f"{national_ts['longterm_vacancy_rate'].min():.2f}",
                f"{national_ts['longterm_vacancy_rate'].max():.2f}",
                f"{national_ts['longterm_vacancy_rate'].mean():.2f}",
                f"{latest_data['longterm_vacancy_rate']:.2f}",
                f"{national_ts['longterm_vacancy_rate'].std():.2f}"
            ]
        })
        st.dataframe(lt_stats_df, hide_index=True, width='stretch')
    
    # Insights
    st.markdown("---")
    st.header("Key Insights")
    
    # Calculate some insights with NaN handling
    # Use last complete year (<=2024) for historical comparisons
    full_years = national_ts[national_ts['year'] <= 2024]
    comparison_year = full_years['year'].max() if not full_years.empty else latest_year
    comparison_data = national_ts[national_ts['year'] == comparison_year].iloc[0]

    if (pd.notna(comparison_data['total_properties']) and pd.notna(first_data['total_properties']) and
        first_data['total_properties'] > 0):
        total_growth = (
            (comparison_data['total_properties'] - first_data['total_properties']) /
            first_data['total_properties'] * 100
        )
    else:
        total_growth = np.nan

    if (pd.notna(comparison_data['vacant_properties']) and pd.notna(first_data['vacant_properties']) and
        first_data['vacant_properties'] > 0):
        vacant_growth = (
            (comparison_data['vacant_properties'] - first_data['vacant_properties']) /
            first_data['vacant_properties'] * 100
        )
    else:
        vacant_growth = np.nan
    
    col1, col2 = st.columns(2)
    
    with col1:
        if pd.notna(total_growth) and pd.notna(comparison_data['total_properties']) and pd.notna(first_data['total_properties']):
            property_change = comparison_data['total_properties'] - first_data['total_properties']
            st.success(f"""
            **Housing Stock Growth**
            
            From 2020 to {comparison_year}, France's total housing stock grew by **{total_growth:.1f}%**, 
            adding approximately **{format_number(property_change)}** 
            new properties to the market.
            """)
        else:
            st.info("Housing stock growth data not available.")
    
    with col2:
        if pd.notna(vacant_growth):
            if vacant_growth > 0:
                st.warning(f"""
                **Vacancy Growth Concern**
                
                Vacant properties increased by **{vacant_growth:.1f}%** between 2020 and {comparison_year}—
                outpacing housing stock growth and suggesting structural market issues.
                """)
            else:
                st.success(f"""
                **Vacancy Improvement**
                
                Vacant properties decreased by **{abs(vacant_growth):.1f}%** between 2020 and {comparison_year}—
                a positive trend indicating improved housing market efficiency.
                """)
        else:
            st.info("Vacancy growth data not available.")
    
    # What comes next
    st.markdown("---")
    st.info("""
    **Next Steps**: 
    - Explore **Departmental Analysis** to see geographic variations
    - Dive into **Commune-level** data for local patterns
    - Review **Conclusions** for policy implications
    """)
