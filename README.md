#  France's Vacant Housing Crisis - Data Storytelling Dashboard

An interactive data storytelling application analyzing vacant housing patterns across France from 2020 to 2025. This Streamlit dashboard provides comprehensive insights into the geography, trends, and policy implications of France's vacant housing landscape.

##  Overview

France faces a housing paradox: while millions struggle to find affordable housing, hundreds of thousands of properties sit empty—some for years. This dashboard explores:

- **The Scale**: How many vacant properties exist and where?
- **The Trend**: Is vacancy increasing or decreasing over time?
- **The Geography**: Which regions are most affected?
- **The Chronicity**: How many properties are vacant long-term (2+ years)?
- **The Implications**: What does this mean for housing policy?

##  Features

### Multiple Interactive Pages

1. ** Introduction**
   - Context and background on housing vacancy
   - Data description and methodology
   - Limitations and ethical considerations

2. ** National Overview**
   - High-level KPIs and trends (2020-2025)
   - Time series analysis of vacancy patterns
   - Year-over-year change analysis
   - National summary statistics

3. ** Departmental Analysis**
   - Compare all 101 French departments
   - Rankings by vacancy rate and absolute numbers
   - Distribution analysis and outlier detection
   - Interactive filtering and time selection
   - Department-to-department comparisons

4. ** Commune Deep Dive**
   - Municipal-level insights (~35,000 communes)
   - Filter by region and department
   - Analysis by commune size class
   - Search functionality for specific communes
   - Top/bottom performers

5. ** Conclusions**
   - Key findings and insights
   - Policy recommendations (urban vs. rural)
   - Targeted interventions for long-term vacancy
   - Limitations and future research directions

### Visualization Types

- **Line charts**: Time series trends
- **Bar charts**: Rankings and comparisons
- **Scatter plots**: Correlation analysis
- **Histograms**: Distribution analysis
- **Box plots**: Statistical summaries
- **Interactive filters**: Dynamic data exploration

### Data Quality

- Transparent handling of suppressed values
- Data quality reports and validation
- Clear documentation of limitations
- Privacy-preserving aggregation

##  Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download this repository**

```bash
cd streamlit_dataviz
```

2. **Install dependencies (pinned)**

```bash
pip install -r requirements.txt
```

3. **Get the data (download or verify existing)**

Option A — download with script (recommended):

```powershell
# Set dataset URLs
$env:LOVAC_DEPT_URL = "https://.../lovac_opendata_dep.csv"
$env:LOVAC_COMMUNE_URL = "https://.../lovac-opendata-communes.csv"
python scripts/data_download.py
```

Option B — manual: place the CSVs into `data/` yourself.

Ensure the following files are in the `data/` folder:
- `lovac_opendata_dep.csv` (Department-level data)
- `lovac-opendata-communes.csv` (Commune-level data)

4. **Run the application**

```bash
streamlit run app.py
```

5. **Open in browser**

The app will automatically open in your default browser at `http://localhost:8501`

##  Reproducibility & Packaging

- Dependencies are pinned in `requirements.txt` for deterministic installs.
- Simple run instructions are provided above (no Makefile required). If you prefer a one-liner workflow, you can:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; python scripts/data_download.py; streamlit run app.py
```

- A small `scripts/data_download.py` fetches the CSVs using environment variables or CLI flags and caches to `data/` (skips if files already exist).
- `seeds.json` contains deterministic constants (e.g., random seed) should you add any sampling or randomized examples later.

##  Project Structure

```
streamlit_dataviz/
├── app.py                          # Main application entry point
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── data/                           # Data files (CSV)
│   ├── lovac_opendata_dep.csv      # Department-level data
│   └── lovac-opendata-communes.csv # Commune-level data
│
├── sections/                       # Page modules
│   ├── intro.py                    # Introduction page
│   ├── overview.py                 # National overview
│   ├── departmental.py             # Department analysis
│   ├── commune.py                  # Commune analysis
│   └── conclusions.py              # Conclusions & insights
│
├── utils/                          # Utility modules
│   ├── io.py                       # Data loading functions
│   ├── prep.py                     # Data preprocessing
│   └── viz.py                      # Visualization functions
│
└── assets/                         # Static assets (optional)
```

##  Data Source

**Dataset**: LOVAC (Logements Vacants) - French Vacant Housing Observatory  
**Portal**: [data.gouv.fr](https://www.data.gouv.fr)  
> Please replace the placeholders in `scripts/data_download.py` or environment variables with the official dataset resource URLs from data.gouv.fr for full reproducibility.
**License**: Open License 2.0 (Licence Ouverte)  
**Coverage**: 2020-2025 (annual data)  
**Granularity**: 
- 101 departments (métropole + overseas)
- ~35,000 communes (municipalities)

### Metrics Tracked

- `pp_total`: Total number of properties
- `pp_vacant`: Number of vacant properties
- `pp_vacant_plus_2ans`: Properties vacant for 2+ years (structural vacancy)

### Data Limitations

- Small values suppressed with 's' to protect privacy
- Overseas territories may have incomplete data
- Data relies on tax declarations (potential lag)
- Vacancy definitions may vary by jurisdiction

##  Key Insights

1. **The Two Frances**: Urban shortage vs. rural surplus
2. **Chronic Vacancy**: Over 50% vacant for 2+ years
3. **Growing Problem**: Vacancy increasing faster than housing stock
4. **Local Variation**: Significant differences even within regions
5. **Size Matters**: Smaller communes face greatest challenges

##  Technical Details

### Performance Optimizations

- **Caching**: `@st.cache_data` for expensive operations
- **Pre-aggregation**: National/department summaries computed once
- **Efficient filtering**: Pandas operations optimized
- **Lazy loading**: Data loaded only when needed

### Best Practices Implemented

 Modular code structure (sections, utils)  
 Consistent styling (centralized color scheme)  
 Error handling and user feedback  
 Responsive design (works on desktop/tablet)  
 Accessible visualizations (alt text, labels)  
 Reproducible analysis (deterministic)  
 Documented assumptions and limitations  

##  Usage Examples

### Explore National Trends
Navigate to "🇫🇷 National Overview" to see:
- 6-year trend of vacancy rates
- KPIs with year-over-year changes
- Growth rate analysis

### Compare Departments
Go to " Departmental Analysis" to:
- Rank departments by vacancy
- Compare multiple departments over time
- Identify outliers and patterns

### Find Specific Communes
Use " Commune Deep Dive" to:
- Filter by region/department
- Search by commune name
- Analyze by population size

### Understand Policy Context
Read " Conclusions" for:
- Evidence-based recommendations
- Differentiated strategies (urban/rural)
- Future research directions

##  Contributing

This is an academic project. Suggestions for improvements:

- Additional visualizations (maps with geographic boundaries)
- Integration with demographic/economic data
- Predictive modeling features
- Export functionality (reports, charts)
- Multi-language support

##  License

**Code**: This application code is provided for educational purposes.  
**Data**: LOVAC data is licensed under Open License 2.0 (Licence Ouverte)  
**Attribution**: Data provided by the French government via data.gouv.fr

##  Acknowledgments

- **Data Provider**: French Government Open Data Portal
- **Framework**: Streamlit community
- **Visualization**: Plotly team
- **Inspiration**: Data storytelling best practices

##  Contact

For questions or feedback about this dashboard, please open an issue in the repository.

---

**Built with**  **Streamlit**  
**Last Updated**: 2025

##  Educational Context

This dashboard was created as part of a data storytelling project with the following learning objectives:

- Frame a data question and turn it into a story arc
- Ingest, clean, and validate open data
- Build interactive dashboards with clear UX
- Apply EDA and analytics techniques
- Communicate insights visually
- Package and ship reproducible applications

**Key Narrative Pattern**: Before/After change over time + Geographic comparison + Rankings & distribution
