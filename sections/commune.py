"""
Commune-level analysis page: Municipal deep dive.
"""
import streamlit as st
import pandas as pd
import numpy as np
from utils.prep import prepare_commune_snapshot, classify_vacancy_level
from utils.viz import create_bar_chart, create_histogram, create_box_plot, format_number, DEFAULT_PLOTLY_CONFIG


def show(df_commune):
    """
    Display commune-level analysis.
    
    Args:
        df_commune: Commune-level DataFrame
    """
    
    st.title("Commune Deep Dive: Municipal Analysis")
    st.markdown("### Explore vacant housing at the local level (~35,000 communes)")
    
    st.info("""
    **Data Notice**: Analysis uses 2025 data which represents a partial year. Vacancy rates shown 
    are based on incomplete year data and should not be compared directly with historical full-year figures.
    """)
    
    # Prepare commune snapshot
    df_snap = prepare_commune_snapshot(df_commune, year='25')
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Region filter
    available_regions = sorted(df_snap['LIB_REG'].dropna().unique())
    selected_region = st.sidebar.selectbox(
        "Select Region",
        options=['All Regions'] + available_regions
    )
    
    # Department filter
    if selected_region != 'All Regions':
        available_depts = sorted(df_snap[df_snap['LIB_REG'] == selected_region]['LIB_DEP'].unique())
    else:
        available_depts = sorted(df_snap['LIB_DEP'].dropna().unique())
    
    selected_dept = st.sidebar.selectbox(
        "Select Department (optional)",
        options=['All Departments'] + available_depts
    )
    
    # Apply filters
    df_filtered = df_snap.copy()
    
    if selected_region != 'All Regions':
        df_filtered = df_filtered[df_filtered['LIB_REG'] == selected_region]
    
    if selected_dept != 'All Departments':
        df_filtered = df_filtered[df_filtered['LIB_DEP'] == selected_dept]
    
    # Remove rows with missing or invalid vacancy data (NaN and inf values)
    df_filtered = df_filtered[
        df_filtered['vacancy_rate'].notna() & 
        np.isfinite(df_filtered['vacancy_rate'])
    ]
    
    # Overview metrics
    st.markdown("---")
    st.header("Overview Statistics")
    
    filter_desc = selected_region if selected_region != 'All Regions' else "France"
    if selected_dept != 'All Departments':
        filter_desc = selected_dept
    
    st.markdown(f"**Analyzing**: {filter_desc} ({len(df_filtered):,} communes with data)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_communes = len(df_filtered)
        st.metric(
            "Communes",
            f"{total_communes:,}",
            "With data"
        )
    
    with col2:
        # Filter out inf and NaN values before calculating mean
        valid_rates = df_filtered['vacancy_rate'].replace([np.inf, -np.inf], np.nan).dropna()
        national_valid_rates = df_snap['vacancy_rate'].replace([np.inf, -np.inf], np.nan).dropna()
        
        if len(valid_rates) > 0:
            avg_rate = valid_rates.mean()
            avg_rate_str = f"{avg_rate:.2f}%"
        else:
            avg_rate = np.nan
            avg_rate_str = "N/A"
        
        if len(national_valid_rates) > 0:
            national_avg = national_valid_rates.mean()
        else:
            national_avg = np.nan
        
        # Handle NaN values in delta calculation
        if pd.notna(avg_rate) and pd.notna(national_avg) and np.isfinite(avg_rate) and np.isfinite(national_avg):
            delta = avg_rate - national_avg
            delta_str = f"{delta:+.2f}pp vs national"
        else:
            delta_str = None
        
        st.metric(
            "Avg Vacancy Rate",
            avg_rate_str,
            delta_str
        )
    
    with col3:
        total_vacant = df_filtered['vacant_properties'].sum()
        st.metric(
            "Total Vacant Units",
            format_number(total_vacant, decimals=1),
            "In selection"
        )
    
    with col4:
        # Filter out inf and NaN values before calculating median
        valid_rates_median = df_filtered['vacancy_rate'].replace([np.inf, -np.inf], np.nan).dropna()
        
        if len(valid_rates_median) > 0:
            median_rate = valid_rates_median.median()
            median_str = f"{median_rate:.2f}%"
        else:
            median_str = "N/A"
        
        st.metric(
            "Median Vacancy Rate",
            median_str,
            "50th percentile"
        )
    
    # Distribution analysis
    st.markdown("---")
    st.header("Distribution of Vacancy Rates")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Histogram")
        
        fig = create_histogram(
            df_filtered,
            x='vacancy_rate',
            title=f'Vacancy Rate Distribution ({filter_desc})',
            nbins=40,
            xlabel='Vacancy Rate (%)',
            height=400
        )
        st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
        
        # Classification
        df_filtered['vacancy_level'] = df_filtered['vacancy_rate'].apply(classify_vacancy_level)
        level_counts = df_filtered['vacancy_level'].value_counts().sort_index()
        
        st.dataframe(
            level_counts.reset_index(),
            hide_index=True,
            column_config={
                'vacancy_level': 'Vacancy Level',
                'count': 'Number of Communes'
            },
            width='stretch'
        )
    
    with col2:
        st.subheader("Box Plot Statistics")
        
        fig = create_box_plot(
            df_filtered,
            y='vacancy_rate',
            title=f'Vacancy Rate Statistics ({filter_desc})',
            ylabel='Vacancy Rate (%)',
            height=400
        )
        st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
        
        # Detailed statistics
        stats = df_filtered['vacancy_rate'].describe()
        st.dataframe(
            pd.DataFrame({
                'Statistic': ['Count', 'Mean', 'Std Dev', 'Min', '25%', 'Median', '75%', 'Max'],
                'Value': [
                    f"{stats['count']:.0f}",
                    f"{stats['mean']:.2f}%",
                    f"{stats['std']:.2f}%",
                    f"{stats['min']:.2f}%",
                    f"{stats['25%']:.2f}%",
                    f"{stats['50%']:.2f}%",
                    f"{stats['75%']:.2f}%",
                    f"{stats['max']:.2f}%"
                ]
            }),
            hide_index=True,
            width='stretch'
        )
    
    # Top and bottom communes
    st.markdown("---")
    st.header("Top Communes")
    
    tab1, tab2, tab3 = st.tabs(["Highest Vacancy", "Lowest Vacancy", "Largest Absolute"])
    
    with tab1:
        st.subheader("Communes with Highest Vacancy Rates")
        
        # Filter to communes with reasonable property counts (avoid tiny villages with high rates)
        min_properties = st.slider(
            "Minimum total properties (to filter small communes)",
            min_value=50,
            max_value=1000,
            value=100,
            step=50,
            key='high_filter'
        )
        
        df_min_filtered = df_filtered[df_filtered['total_properties'] >= min_properties]
        
        top_high = df_min_filtered.nlargest(20, 'vacancy_rate')
        
        if len(top_high) > 0:
            fig = create_bar_chart(
                top_high,
                x='vacancy_rate',
                y='LIBGEO_25',
                title='',
                orientation='h',
                height=600,
                text_auto='.1f'
            )
            st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
            
            st.dataframe(
                top_high[['LIBGEO_25', 'total_properties', 'vacant_properties', 'vacancy_rate', 'longterm_vacancy_rate']],
                hide_index=True,
                column_config={
                    'LIBGEO_25': 'Commune',
                    'total_properties': st.column_config.NumberColumn('Total Properties', format="%d"),
                    'vacant_properties': st.column_config.NumberColumn('Vacant', format="%d"),
                    'vacancy_rate': st.column_config.NumberColumn('Vacancy Rate (%)', format="%.2f"),
                    'longterm_vacancy_rate': st.column_config.NumberColumn('Long-term Rate (%)', format="%.2f")
                },
                width='stretch'
            )
        else:
            st.warning("No communes meet the minimum property threshold.")
    
    with tab2:
        st.subheader("Communes with Lowest Vacancy Rates")
        
        min_properties_low = st.slider(
            "Minimum total properties",
            min_value=50,
            max_value=1000,
            value=100,
            step=50,
            key='low_filter'
        )
        
        df_min_filtered_low = df_filtered[df_filtered['total_properties'] >= min_properties_low]
        
        top_low = df_min_filtered_low.nsmallest(20, 'vacancy_rate')
        
        if len(top_low) > 0:
            fig = create_bar_chart(
                top_low,
                x='vacancy_rate',
                y='LIBGEO_25',
                title='',
                orientation='h',
                height=600,
                text_auto='.1f'
            )
            st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
            
            st.dataframe(
                top_low[['LIBGEO_25', 'total_properties', 'vacant_properties', 'vacancy_rate', 'longterm_vacancy_rate']],
                hide_index=True,
                column_config={
                    'LIBGEO_25': 'Commune',
                    'total_properties': st.column_config.NumberColumn('Total Properties', format="%d"),
                    'vacant_properties': st.column_config.NumberColumn('Vacant', format="%d"),
                    'vacancy_rate': st.column_config.NumberColumn('Vacancy Rate (%)', format="%.2f"),
                    'longterm_vacancy_rate': st.column_config.NumberColumn('Long-term Rate (%)', format="%.2f")
                },
                width='stretch'
            )
        else:
            st.warning("No communes meet the minimum property threshold.")
    
    with tab3:
        st.subheader("Communes with Most Vacant Properties (Absolute)")
        
        top_absolute = df_filtered.nlargest(20, 'vacant_properties')
        
        fig = create_bar_chart(
            top_absolute,
            x='vacant_properties',
            y='LIBGEO_25',
            title='',
            orientation='h',
            height=600,
            text_auto=True
        )
        st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
        
        st.dataframe(
            top_absolute[['LIBGEO_25', 'total_properties', 'vacant_properties', 'vacancy_rate']],
            hide_index=True,
            column_config={
                'LIBGEO_25': 'Commune',
                'total_properties': st.column_config.NumberColumn('Total Properties', format="%d"),
                'vacant_properties': st.column_config.NumberColumn('Vacant', format="%d"),
                'vacancy_rate': st.column_config.NumberColumn('Vacancy Rate (%)', format="%.2f")
            },
            width='stretch'
        )
    
    # Size class analysis
    st.markdown("---")
    st.header("Analysis by Commune Size")
    
    # Classify communes by size
    df_filtered['size_class'] = pd.cut(
        df_filtered['total_properties'],
        bins=[0, 100, 500, 1000, 5000, 10000, 100000],
        labels=['Tiny (<100)', 'Small (100-500)', 'Medium (500-1K)', 'Large (1K-5K)', 'Very Large (5K-10K)', 'Major (>10K)']
    )
    
    size_stats = df_filtered.groupby('size_class', observed=True).agg({
        'CODGEO_25': 'count',
        'vacancy_rate': ['mean', 'median'],
        'vacant_properties': 'sum'
    }).round(2)
    
    size_stats.columns = ['Count', 'Mean Vacancy Rate (%)', 'Median Vacancy Rate (%)', 'Total Vacant']
    size_stats = size_stats.reset_index()
    size_stats.columns = ['Size Class', 'Number of Communes', 'Mean Vacancy Rate (%)', 'Median Vacancy Rate (%)', 'Total Vacant Properties']
    
    st.dataframe(
        size_stats,
        hide_index=True,
        width='stretch'
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = create_box_plot(
            df_filtered.dropna(subset=['size_class']),
            y='vacancy_rate',
            x='size_class',
            title='Vacancy Rate by Commune Size',
            ylabel='Vacancy Rate (%)',
            height=400
        )
        st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
    
    with col2:
        # Bar chart of mean rates by size
        fig = create_bar_chart(
            size_stats,
            x='Size Class',
            y='Mean Vacancy Rate (%)',
            title='Average Vacancy Rate by Size Class',
            height=400,
            text_auto='.1f'
        )
        st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG)
    
    st.info("""
    **Insight**: Smaller communes often have higher vacancy rates due to rural depopulation,
    while larger urban communes typically have tighter housing markets with lower vacancy.
    """)
    
    # Search functionality
    st.markdown("---")
    st.header("Search Communes")
    
    search_term = st.text_input("Search by commune name", "")
    
    if search_term:
        search_results = df_filtered[
            df_filtered['LIBGEO_25'].str.contains(search_term, case=False, na=False)
        ].sort_values('vacancy_rate', ascending=False)
        
        st.write(f"Found {len(search_results)} commune(s) matching '{search_term}'")
        
        if len(search_results) > 0:
            st.dataframe(
                search_results[[
                    'LIBGEO_25', 'LIB_DEP', 'total_properties', 
                    'vacant_properties', 'vacancy_rate', 'longterm_vacancy_rate'
                ]],
                hide_index=True,
                column_config={
                    'LIBGEO_25': 'Commune',
                    'LIB_DEP': 'Department',
                    'total_properties': st.column_config.NumberColumn('Total Properties', format="%d"),
                    'vacant_properties': st.column_config.NumberColumn('Vacant', format="%d"),
                    'vacancy_rate': st.column_config.NumberColumn('Vacancy Rate (%)', format="%.2f"),
                    'longterm_vacancy_rate': st.column_config.NumberColumn('Long-term Rate (%)', format="%.2f")
                },
                width='stretch'
            )
    
    # Data quality note
    st.markdown("---")
    st.warning("""
    **Data Quality Note**: 
    
    Many small communes have suppressed values (marked 's') to protect privacy. 
    This affects approximately {:.1f}% of commune records. Analysis focuses on 
    communes with available data.
    """.format(
        (df_commune['pp_vacant_25'].isna().sum() / len(df_commune) * 100)
    ))
    
    # Key insights
    st.markdown("---")
    st.header("Key Insights")
    
    st.success(f"""
    **Local Variation**
    
    Within {filter_desc}, vacancy rates vary from **{df_filtered['vacancy_rate'].min():.2f}%** 
    to **{df_filtered['vacancy_rate'].max():.2f}%**—showing significant local differences 
    even within the same region or department.
    
    **Median vs Mean**: The median vacancy rate ({median_rate:.2f}%) is 
    {'lower' if median_rate < avg_rate else 'higher'} than the mean ({avg_rate:.2f}%), 
    indicating {'a right-skewed distribution with some very high outliers' if median_rate < avg_rate else 'a relatively symmetric distribution'}.
    """)
