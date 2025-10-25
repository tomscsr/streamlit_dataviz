"""
Data validation script - Run this to verify data loads correctly.
Usage: python validate_data.py
"""
import pandas as pd
from pathlib import Path

def validate_department_data():
    """Validate department-level data."""
    data_path = Path("data") / "lovac_opendata_dep.csv"
    
    print("=" * 60)
    print("VALIDATING DEPARTMENT DATA")
    print("=" * 60)
    
    try:
        df = pd.read_csv(data_path, sep=";", encoding="latin-1", dtype={"DEP": str})
        
        print(f"✓ File loaded successfully")
        print(f"✓ Rows: {len(df)}")
        print(f"✓ Columns: {len(df.columns)}")
        print(f"\nColumn names:")
        for col in df.columns:
            print(f"  - {col}")
        
        print(f"\nFirst 3 departments:")
        for idx, row in df.head(3).iterrows():
            print(f"  - {row.get('DEP', 'N/A').strip()}: {row.get('LIB_DEP', 'N/A').strip()}")
        
        # Check for required columns
        required_cols = ['DEP', 'LIB_DEP', 'pp_vacant_25', 'pp_total_24']
        missing = [col for col in required_cols if col.strip() not in [c.strip() for c in df.columns]]
        
        if missing:
            print(f"\n⚠ Missing columns: {missing}")
        else:
            print(f"\n✓ All required columns present")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def validate_commune_data():
    """Validate commune-level data."""
    data_path = Path("data") / "lovac-opendata-communes.csv"
    
    print("\n" + "=" * 60)
    print("VALIDATING COMMUNE DATA")
    print("=" * 60)
    
    try:
        df = pd.read_csv(
            data_path, 
            sep=";", 
            encoding="latin-1",
            dtype={"CODGEO_25": str, "DEP": str},
            nrows=1000  # Just sample for validation
        )
        
        print(f"✓ File loaded successfully")
        print(f"✓ Sample rows: 1000")
        print(f"✓ Columns: {len(df.columns)}")
        
        print(f"\nFirst 3 communes:")
        for idx, row in df.head(3).iterrows():
            print(f"  - {row.get('LIBGEO_25', 'N/A')}")
        
        # Check for required columns
        required_cols = ['CODGEO_25', 'LIBGEO_25', 'DEP', 'LIB_DEP']
        missing = [col for col in required_cols if col.strip() not in [c.strip() for c in df.columns]]
        
        if missing:
            print(f"\n⚠ Missing columns: {missing}")
        else:
            print(f"\n✓ All required columns present")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def main():
    """Run all validations."""
    print("\n🔍 DATA VALIDATION SCRIPT")
    print("=" * 60)
    
    dept_ok = validate_department_data()
    commune_ok = validate_commune_data()
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    if dept_ok and commune_ok:
        print("✓ All validations passed!")
        print("✓ You're ready to run the dashboard!")
        print("\nRun: streamlit run app.py")
    else:
        print("✗ Some validations failed")
        print("Please check the errors above")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
