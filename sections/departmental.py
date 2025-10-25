"""
Departmental analysis page: Compare departments with maps and rankings.
"""
import streamlit as st
import pandas as pd
import numpy as np
from utils.prep import (
    prepare_department_snapshot, 
    prepare_department_timeseries,
    classify_vacancy_level,
    get_top_departments
)
from utils.viz import (
    create_bar_chart, 
    create_scatter_plot, 
    create_box_plot,
    create_histogram,
    format_number,
    DEFAULT_PLOTLY_CONFIG
)


def show(df_dept):
    """
    Display departmental analysis with comparisons and rankings.
    
    Args:
        df_dept: Department-level DataFrame
    """
    
    st.title("Departmental Analysis: Geographic Patterns")
    st.markdown("### Compare vacancy rates across France's 101 departments")
    
    st.info("""
    **Data Notice**: 2025 represents partial year data only. When comparing departments or analyzing trends, 
    be aware that 2025 vacancy rates are not directly comparable to complete annual data from 2020-2024.
    """)
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Year selection
    available_years = ['20', '21', '22', '23', '24', '25']
    year_labels = [f"20{y}" for y in available_years]
    selected_year = st.sidebar.select_slider(
        "Select Year",
        options=available_years,
        value='25',
        format_func=lambda x: f"20{x}"
    )
    
    # Prepare data
    df_snap = prepare_department_snapshot(df_dept, year=selected_year)
    df_ts = prepare_department_timeseries(df_dept)
    
    # Department selection for filtering
    all_depts = sorted(df_snap['LIB_DEP'].unique())
    selected_depts = st.sidebar.multiselect(
        "Filter Departments (optional)",
        options=all_depts,
        default=[]
    )
    
    # Apply filter if departments selected
    if selected_depts:
        df_snap_filtered = df_snap[df_snap['LIB_DEP'].isin(selected_depts)]
    else:
        df_snap_filtered = df_snap.copy()
    
    # Overview metrics for selected year
    st.markdown("---")
    st.header(f"Department Statistics (20{selected_year})")
    
    # Remove rows with NaN vacancy rates for statistics
    df_snap_filtered_valid = df_snap_filtered.dropna(subset=['vacancy_rate'])
    
    if len(df_snap_filtered_valid) == 0:
        st.error("No valid data available for the selected filters. Please adjust your selection.")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_rate = df_snap_filtered_valid['vacancy_rate'].mean()
        st.metric(
            "Average Vacancy Rate",
            f"{avg_rate:.2f}%",
            f"Across {len(df_snap_filtered_valid)} depts"
        )
    
    with col2:
        max_rate = df_snap_filtered_valid['vacancy_rate'].max()
        max_idx = df_snap_filtered_valid['vacancy_rate'].idxmax()
        max_dept = df_snap_filtered_valid.loc[max_idx, 'LIB_DEP']
        st.metric(
            "Highest Rate",
            f"{max_rate:.2f}%",
            max_dept
        )
    
    with col3:
        min_rate = df_snap_filtered_valid['vacancy_rate'].min()
        min_idx = df_snap_filtered_valid['vacancy_rate'].idxmin()
        min_dept = df_snap_filtered_valid.loc[min_idx, 'LIB_DEP']
        st.metric(
            "Lowest Rate",
            f"{min_rate:.2f}%",
            min_dept
        )
    
    with col4:
        std_rate = df_snap_filtered_valid['vacancy_rate'].std()
        st.metric(
            "Std. Deviation",
            f"{std_rate:.2f}pp",
            "Variability"
        )
    
    # Rankings and Comparisons
    st.markdown("---")
    st.header("Department Rankings")
    
    tab1, tab2, tab3 = st.tabs(["Vacancy Rate", "Long-term Vacancy", "Absolute Numbers"])
    
    with tab1:
        st.subheader("Top 20 Departments by Vacancy Rate")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Highest Vacancy Rates")
            top_vacant = get_top_departments(df_snap, 'vacancy_rate', n=20, ascending=False)
            
            fig = create_bar_chart(
                top_vacant.head(20),
                x='vacancy_rate',
                y='LIB_DEP',
                title='',
                orientation='h',
                height=600,
                text_auto='.2f'
            )
            st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
            
            st.dataframe(
                top_vacant[['LIB_DEP', 'vacancy_rate', 'vacant_properties']].head(10),
                hide_index=True,
                column_config={
                    'LIB_DEP': 'Department',
                    'vacancy_rate': st.column_config.NumberColumn('Rate (%)', format="%.2f"),
                    'vacant_properties': st.column_config.NumberColumn('Vacant Units', format="%d")
                }
            )
        
        with col2:
            st.markdown("##### Lowest Vacancy Rates")
            low_vacant = get_top_departments(df_snap, 'vacancy_rate', n=20, ascending=True)
            
            fig = create_bar_chart(
                low_vacant.head(20),
                x='vacancy_rate',
                y='LIB_DEP',
                title='',
                orientation='h',
                height=600,
                text_auto='.2f'
            )
            st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
            
            st.dataframe(
                low_vacant[['LIB_DEP', 'vacancy_rate', 'vacant_properties']].head(10),
                hide_index=True,
                column_config={
                    'LIB_DEP': 'Department',
                    'vacancy_rate': st.column_config.NumberColumn('Rate (%)', format="%.2f"),
                    'vacant_properties': st.column_config.NumberColumn('Vacant Units', format="%d")
                }
            )
    
    with tab2:
        st.subheader("Long-term Vacancy (2+ Years)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Highest Long-term Vacancy Rates")
            top_longterm = get_top_departments(df_snap, 'longterm_vacancy_rate', n=15, ascending=False)
            
            fig = create_bar_chart(
                top_longterm,
                x='longterm_vacancy_rate',
                y='LIB_DEP',
                title='',
                orientation='h',
                height=500,
                text_auto='.2f'
            )
            st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
        
        with col2:
            st.markdown("##### Share of Vacancy That Is Long-term")
            
            # Get departments with highest share of long-term
            top_share = get_top_departments(df_snap, 'longterm_share', n=15, ascending=False)
            
            fig = create_bar_chart(
                top_share,
                x='longterm_share',
                y='LIB_DEP',
                title='',
                orientation='h',
                height=500,
                text_auto='.1f'
            )
            st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
        
        st.info("""
        **Interpretation**: Departments with high long-term vacancy share face structural problems—
        not just temporary market transitions. These areas may need targeted policy interventions.
        """)
    
    with tab3:
        st.subheader("Absolute Vacancy Numbers")
        
        # Total vacant properties
        top_absolute = df_snap.nlargest(20, 'vacant_properties')[['LIB_DEP', 'vacant_properties', 'vacancy_rate']]
        
        fig = create_bar_chart(
            top_absolute,
            x='vacant_properties',
            y='LIB_DEP',
            title='Top 20 Departments by Total Vacant Properties',
            orientation='h',
            height=600,
            text_auto=True
        )
        st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
        
        st.warning("""
        **Note**: Large departments naturally have more vacant properties in absolute terms. 
        Focus on **vacancy rates** for fair comparisons.
        """)
    
    # Distribution Analysis
    st.markdown("---")
    st.header("Distribution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Vacancy Rate Distribution")
        
        fig = create_histogram(
            df_snap.dropna(subset=['vacancy_rate']),
            x='vacancy_rate',
            title='',
            nbins=25,
            xlabel='Vacancy Rate (%)',
            height=400
        )
        st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
        
        # Add classification
        df_snap['vacancy_level'] = df_snap['vacancy_rate'].apply(classify_vacancy_level)
        level_counts = df_snap['vacancy_level'].value_counts()
        
        st.dataframe(
            level_counts.reset_index(),
            hide_index=True,
            column_config={
                'vacancy_level': 'Vacancy Level',
                'count': 'Number of Departments'
            }
        )
    
    with col2:
        st.subheader("Box Plot: Vacancy Statistics")
        
        fig = create_box_plot(
            df_snap.dropna(subset=['vacancy_rate']),
            y='vacancy_rate',
            title='',
            ylabel='Vacancy Rate (%)',
            height=400
        )
        st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
        
        # Summary statistics
        stats = df_snap['vacancy_rate'].describe()
        st.dataframe(
            pd.DataFrame({
                'Statistic': ['Mean', 'Median', '25th Percentile', '75th Percentile', 'Min', 'Max'],
                'Value (%)': [
                    f"{stats['mean']:.2f}",
                    f"{stats['50%']:.2f}",
                    f"{stats['25%']:.2f}",
                    f"{stats['75%']:.2f}",
                    f"{stats['min']:.2f}",
                    f"{stats['max']:.2f}"
                ]
            }),
            hide_index=True,
            width='stretch'
        )
    
    # Correlation Analysis
    st.markdown("---")
    st.header("Relationship Between Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Vacancy Rate vs. Housing Stock Size")
        
        fig = create_scatter_plot(
            df_snap.dropna(subset=['total_properties', 'vacancy_rate']),
            x='total_properties',
            y='vacancy_rate',
            title='',
            xlabel='Total Properties',
            ylabel='Vacancy Rate (%)',
            height=400
        )
        st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
        
        st.caption("Are larger housing markets more or less efficient?")
    
    with col2:
        st.subheader("Overall Vacancy vs. Long-term Vacancy")
        
        fig = create_scatter_plot(
            df_snap.dropna(subset=['vacancy_rate', 'longterm_vacancy_rate']),
            x='vacancy_rate',
            y='longterm_vacancy_rate',
            title='',
            xlabel='Total Vacancy Rate (%)',
            ylabel='Long-term Vacancy Rate (%)',
            height=400,
            trendline='ols'
        )
        st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
        
        st.caption("Strong correlation suggests systemic issues in high-vacancy areas.")
    
    # Time series comparison
    st.markdown("---")
    st.header("Trends Over Time: Compare Departments")
    
    # Allow selection of specific departments to compare
    compare_depts = st.multiselect(
        "Select departments to compare (up to 10)",
        options=sorted(df_ts['LIB_DEP'].unique()),
        default=sorted(df_ts['LIB_DEP'].unique())[:5],
        max_selections=10
    )
    
    if compare_depts:
        df_compare = df_ts[df_ts['LIB_DEP'].isin(compare_depts)]
        
        from utils.viz import create_line_chart
        
        fig = create_line_chart(
            df_compare,
            x='year',
            y='vacancy_rate',
            title='Vacancy Rate Trends by Department',
            xlabel='Year',
            ylabel='Vacancy Rate (%)',
            color='LIB_DEP',
            height=500
        )
        st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
    
    # Full data explorer
    st.markdown("---")
    st.header("Data Explorer")
    
    st.subheader(f"All Departments (20{selected_year})")
    
    # Sortable table
    display_cols = [
        'DEP', 'LIB_DEP', 'total_properties', 'vacant_properties', 
        'vacant_2plus_years', 'vacancy_rate', 'longterm_vacancy_rate', 'longterm_share'
    ]
    
    st.dataframe(
        df_snap[display_cols].sort_values('vacancy_rate', ascending=False),
        hide_index=True,
        column_config={
            'DEP': 'Code',
            'LIB_DEP': 'Department',
            'total_properties': st.column_config.NumberColumn('Total Properties', format="%d"),
            'vacant_properties': st.column_config.NumberColumn('Vacant', format="%d"),
            'vacant_2plus_years': st.column_config.NumberColumn('Vacant 2+ Years', format="%d"),
            'vacancy_rate': st.column_config.NumberColumn('Vacancy Rate (%)', format="%.2f"),
            'longterm_vacancy_rate': st.column_config.NumberColumn('Long-term Rate (%)', format="%.2f"),
            'longterm_share': st.column_config.NumberColumn('Long-term Share (%)', format="%.1f")
        },
        width='stretch',
        height=400
    )
    
    # Key insights
    st.markdown("---")
    st.header("Key Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Filter out NaN values for accurate statistics
        valid_rates = df_snap['vacancy_rate'].dropna()
        
        if len(valid_rates) > 0:
            min_rate = valid_rates.min()
            max_rate = valid_rates.max()
            spread = max_rate - min_rate
            
            st.success(f"""
            **Geographic Variation**
            
            Vacancy rates vary significantly across France, from **{min_rate:.2f}%** 
            to **{max_rate:.2f}%**—a spread of **{spread:.2f} percentage points**.
            
            This suggests **local factors** (economic vitality, demographics, tourism) matter greatly.
            """)
        else:
            st.warning("Insufficient data for geographic variation analysis.")
    
    with col2:
        # Calculate correlation
        corr = df_snap[['vacancy_rate', 'longterm_vacancy_rate']].corr().iloc[0, 1]
        st.info(f"""
        **Structural vs. Temporary Vacancy**
        
        Correlation between overall and long-term vacancy: **{corr:.2f}**
        
        High correlation indicates that departments with high vacancy also face 
        **chronic, structural problems**—not just temporary market adjustments.
        """)
