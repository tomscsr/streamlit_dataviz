"""
Data preprocessing and feature engineering utilities.
Transforms raw data into analysis-ready tables.
"""
import pandas as pd
import numpy as np


def calculate_vacancy_rate(df, year_suffix):
    """
    Calculate vacancy rate for a given year.
    
    Args:
        df: DataFrame with vacant and total columns
        year_suffix: Year suffix (e.g., '24', '25')
    
    Returns:
        Series: Vacancy rate (0-100)
    """
    vacant_col = f'pp_vacant_{year_suffix}'
    # For 2025, use 2024 total as pp_total_25 doesn't exist
    total_col = f'pp_total_{year_suffix}' if year_suffix != '25' else 'pp_total_24'
    
    if vacant_col in df.columns and total_col in df.columns:
        rate = (df[vacant_col] / df[total_col] * 100).round(2)
        return rate.replace([np.inf, -np.inf], np.nan)
    return pd.Series(np.nan, index=df.index)


def calculate_longterm_vacancy_rate(df, year_suffix):
    """
    Calculate long-term (2+ years) vacancy rate.
    
    Args:
        df: DataFrame with vacant 2+ years and total columns
        year_suffix: Year suffix (e.g., '24', '25')
    
    Returns:
        Series: Long-term vacancy rate (0-100)
    """
    longterm_col = f'pp_vacant_plus_2ans_{year_suffix}'
    # For 2025, use 2024 total as pp_total_25 doesn't exist
    total_col = f'pp_total_{year_suffix}' if year_suffix != '25' else 'pp_total_24'
    
    if longterm_col in df.columns and total_col in df.columns:
        rate = (df[longterm_col] / df[total_col] * 100).round(2)
        return rate.replace([np.inf, -np.inf], np.nan)
    return pd.Series(np.nan, index=df.index)


def prepare_department_timeseries(df_dept):
    """
    Transform department data into time series format.
    
    Args:
        df_dept: Department-level DataFrame
    
    Returns:
        pd.DataFrame: Long-format time series
    """
    years = ['20', '21', '22', '23', '24', '25']
    records = []
    
    for _, row in df_dept.iterrows():
        for year in years:
            year_full = f"20{year}"
            
            # Get values for this year
            total = row.get(f'pp_total_{year}', np.nan)
            vacant = row.get(f'pp_vacant_{year}', np.nan)
            vacant_2y = row.get(f'pp_vacant_plus_2ans_{year}', np.nan)
            
            # Calculate rates
            vacancy_rate = (vacant / total * 100) if pd.notna(total) and total > 0 else np.nan
            longterm_rate = (vacant_2y / total * 100) if pd.notna(total) and total > 0 else np.nan
            longterm_share = (vacant_2y / vacant * 100) if pd.notna(vacant) and vacant > 0 else np.nan
            
            records.append({
                'DEP': row['DEP'],
                'LIB_DEP': row['LIB_DEP'],
                'year': int(year_full),
                'total_properties': total,
                'vacant_properties': vacant,
                'vacant_2plus_years': vacant_2y,
                'vacancy_rate': round(vacancy_rate, 2) if pd.notna(vacancy_rate) else np.nan,
                'longterm_vacancy_rate': round(longterm_rate, 2) if pd.notna(longterm_rate) else np.nan,
                'longterm_share': round(longterm_share, 2) if pd.notna(longterm_share) else np.nan
            })
    
    return pd.DataFrame(records)


def prepare_national_aggregates(df_dept):
    """
    Calculate national-level aggregates from department data.
    
    Args:
        df_dept: Department-level DataFrame
    
    Returns:
        pd.DataFrame: National time series
    """
    years = ['20', '21', '22', '23', '24', '25']
    national_data = []
    
    for year in years:
        year_full = f"20{year}"
        
        # For 2025, use 2024 total as pp_total_25 doesn't exist
        total_col = f'pp_total_{year}' if year != '25' else 'pp_total_24'
        total = df_dept[total_col].sum() if total_col in df_dept.columns else np.nan
        vacant = df_dept[f'pp_vacant_{year}'].sum() if f'pp_vacant_{year}' in df_dept.columns else np.nan
        vacant_2y = df_dept[f'pp_vacant_plus_2ans_{year}'].sum() if f'pp_vacant_plus_2ans_{year}' in df_dept.columns else np.nan
        
        vacancy_rate = (vacant / total * 100) if total > 0 else np.nan
        longterm_rate = (vacant_2y / total * 100) if total > 0 else np.nan
        longterm_share = (vacant_2y / vacant * 100) if vacant > 0 else np.nan
        
        national_data.append({
            'year': int(year_full),
            'total_properties': total,
            'vacant_properties': vacant,
            'vacant_2plus_years': vacant_2y,
            'vacancy_rate': round(vacancy_rate, 2),
            'longterm_vacancy_rate': round(longterm_rate, 2),
            'longterm_share': round(longterm_share, 2)
        })
    
    return pd.DataFrame(national_data)


def prepare_department_snapshot(df_dept, year='25'):
    """
    Prepare department snapshot for a specific year.
    
    Args:
        df_dept: Department-level DataFrame
        year: Year suffix (default '25')
    
    Returns:
        pd.DataFrame: Department metrics for the year
    """
    df_snap = df_dept[['DEP', 'LIB_DEP']].copy()
    
    # For 2025, use 2024 total as pp_total_25 doesn't exist
    total_col = f'pp_total_{year}' if year != '25' else 'pp_total_24'
    
    # Add raw values
    df_snap['total_properties'] = df_dept[total_col] if total_col in df_dept.columns else np.nan
    df_snap['vacant_properties'] = df_dept[f'pp_vacant_{year}'] if f'pp_vacant_{year}' in df_dept.columns else np.nan
    df_snap['vacant_2plus_years'] = df_dept[f'pp_vacant_plus_2ans_{year}'] if f'pp_vacant_plus_2ans_{year}' in df_dept.columns else np.nan
    
    # Calculate rates
    df_snap['vacancy_rate'] = calculate_vacancy_rate(df_dept, year)
    df_snap['longterm_vacancy_rate'] = calculate_longterm_vacancy_rate(df_dept, year)
    
    # Share of vacant that are long-term
    df_snap['longterm_share'] = (
        df_snap['vacant_2plus_years'] / df_snap['vacant_properties'] * 100
    ).round(2)
    
    # Year-over-year change (vs previous year)
    prev_year = str(int(year) - 1)
    if prev_year in ['20', '21', '22', '23', '24']:
        prev_vacant = df_dept[f'pp_vacant_{prev_year}']
        df_snap['vacant_change'] = df_dept[f'pp_vacant_{year}'] - prev_vacant
        df_snap['vacant_change_pct'] = (
            (df_dept[f'pp_vacant_{year}'] - prev_vacant) / prev_vacant * 100
        ).round(2)
    
    return df_snap


def prepare_commune_snapshot(df_commune, year='25'):
    """
    Prepare commune snapshot for a specific year.
    
    Args:
        df_commune: Commune-level DataFrame
        year: Year suffix (default '25')
    
    Returns:
        pd.DataFrame: Commune metrics for the year
    """
    cols_to_keep = [
        'CODGEO_25', 'LIBGEO_25', 'DEP', 'LIB_DEP', 
        'REG', 'LIB_REG', 'EPCI_25', 'LIB_EPCI_25'
    ]
    
    df_snap = df_commune[cols_to_keep].copy()
    
    # For 2025, use 2024 total as pp_total_25 doesn't exist
    total_col = f'pp_total_{year}' if year != '25' else 'pp_total_24'
    
    # Add metrics for selected year
    df_snap['total_properties'] = df_commune.get(total_col, np.nan)
    df_snap['vacant_properties'] = df_commune.get(f'pp_vacant_{year}', np.nan)
    df_snap['vacant_2plus_years'] = df_commune.get(f'pp_vacant_plus_2ans_{year}', np.nan)
    
    # Calculate rates
    df_snap['vacancy_rate'] = (
        df_snap['vacant_properties'] / df_snap['total_properties'] * 100
    ).round(2)
    
    df_snap['longterm_vacancy_rate'] = (
        df_snap['vacant_2plus_years'] / df_snap['total_properties'] * 100
    ).round(2)
    
    df_snap['longterm_share'] = (
        df_snap['vacant_2plus_years'] / df_snap['vacant_properties'] * 100
    ).round(2)
    
    return df_snap


def get_top_departments(df_snap, metric='vacancy_rate', n=10, ascending=False):
    """
    Get top N departments by a specific metric.
    
    Args:
        df_snap: Department snapshot DataFrame
        metric: Metric column name
        n: Number of departments to return
        ascending: Sort order (False = highest first)
    
    Returns:
        pd.DataFrame: Top N departments
    """
    return (
        df_snap
        .dropna(subset=[metric])
        .nlargest(n, metric) if not ascending else 
        df_snap.dropna(subset=[metric]).nsmallest(n, metric)
    )


def classify_vacancy_level(rate):
    """
    Classify vacancy rate into categories.
    
    Args:
        rate: Vacancy rate (percentage)
    
    Returns:
        str: Category label
    """
    if pd.isna(rate):
        return 'Unknown'
    elif rate < 5:
        return 'Very Low (<5%)'
    elif rate < 7:
        return 'Low (5-7%)'
    elif rate < 9:
        return 'Moderate (7-9%)'
    elif rate < 12:
        return 'High (9-12%)'
    else:
        return 'Very High (>12%)'


def identify_data_quality_issues(df):
    """
    Identify data quality issues in the dataset.
    
    Args:
        df: DataFrame to check
    
    Returns:
        dict: Data quality report
    """
    report = {
        'total_rows': len(df),
        'missing_by_column': df.isna().sum().to_dict(),
        'missing_percentage': (df.isna().sum() / len(df) * 100).round(2).to_dict(),
        'duplicates': df.duplicated().sum()
    }
    
    return report
