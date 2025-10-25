"""
Data loading utilities for vacant housing data.
Handles data ingestion with caching and error handling.
"""
import pandas as pd
import streamlit as st
from pathlib import Path


@st.cache_data(show_spinner=False)
def load_department_data():
    """
    Load department-level vacant housing data.
    
    Returns:
        pd.DataFrame: Cleaned department data
    """
    data_path = Path(__file__).parent.parent / "data" / "lovac_opendata_dep.csv"
    
    try:
        df = pd.read_csv(
            data_path,
            sep=";",
            encoding="latin-1",  # French characters use Latin-1 encoding
            dtype={"DEP": str}
        )
        
        # Clean column names (remove spaces)
        df.columns = df.columns.str.strip()
        
        # Clean data values (remove spaces from numeric columns)
        for col in df.columns:
            if col not in ['DEP', 'LIB_DEP']:
                df[col] = df[col].astype(str).str.strip().str.replace(' ', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Clean text columns
        df['LIB_DEP'] = df['LIB_DEP'].str.strip()
        df['DEP'] = df['DEP'].str.strip()
        
        return df
    
    except Exception as e:
        st.error(f"Error loading department data: {str(e)}")
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_commune_data():
    """
    Load commune-level vacant housing data.
    
    Returns:
        pd.DataFrame: Cleaned commune data
    """
    data_path = Path(__file__).parent.parent / "data" / "lovac-opendata-communes.csv"
    
    try:
        df = pd.read_csv(
            data_path,
            sep=";",
            encoding="latin-1",  # French characters use Latin-1 encoding
            dtype={"CODGEO_25": str, "DEP": str, "EPCI_25": str}
        )
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Handle 's' (secret/suppressed) values - replace with NaN
        for col in df.columns:
            if col.startswith('pp_'):
                df[col] = df[col].replace('s', pd.NA)
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Clean text columns
        for col in ['LIBGEO_25', 'LIB_EPCI_25', 'LIB_DEP', 'LIB_REG']:
            if col in df.columns:
                df[col] = df[col].str.strip()
        
        df['DEP'] = df['DEP'].str.strip()
        df['CODGEO_25'] = df['CODGEO_25'].str.strip()
        
        return df
    
    except Exception as e:
        st.error(f"Error loading commune data: {str(e)}")
        return pd.DataFrame()


def get_data_license():
    """
    Return data license and attribution information.
    
    Returns:
        str: License text
    """
    return """
    **Data Source**: LOVAC (Logements Vacants) - French Open Data  
    **Portal**: data.gouv.fr  
    **License**: Open License 2.0 (Licence Ouverte)  
    **Attribution**: Data provided by the French government - freely reusable with attribution  
    **Last Updated**: 2025  
    
    This data is provided under the Open License 2.0, which allows for free reuse, 
    modification, and distribution with proper attribution.
    """


def get_data_description():
    """
    Return detailed data description and methodology.
    
    Returns:
        dict: Data description information
    """
    return {
        "title": "French Vacant Housing Observatory (LOVAC)",
        "description": """
        This dataset tracks vacant housing units across France from 2020 to 2025.
        Data is collected from tax records and census information, providing insights
        into housing availability and potential waste of housing resources.
        """,
        "metrics": {
            "pp_total": "Total number of properties (principal residences + secondary + vacant)",
            "pp_vacant": "Number of vacant properties",
            "pp_vacant_plus_2ans": "Number of properties vacant for 2+ years (structural vacancy)"
        },
        "granularity": {
            "department": "101 French departments (métropole + overseas)",
            "commune": "~35,000 French communes (municipalities)"
        },
        "time_period": "2020-2025 (annual data)",
        "limitations": [
            "Small values are suppressed with 's' to protect privacy",
            "Overseas territories may have incomplete data",
            "Vacancy definitions may vary slightly by jurisdiction",
            "Data relies on tax declarations which may lag actual occupancy"
        ]
    }
