# Multi-Page Streamlit App - Vacant Housing in France

## 🎉 What's New

Your Streamlit app has been completely reorganized into a **multi-page structure** with comprehensive visualizations for data storytelling!

## 📁 Project Structure

```
streamlit_dataviz/
├── app.py                          # Entry point (welcome page)
├── pages/                          # Multi-page structure
│   ├── 1_🏠_Home.py               # Executive summary
│   ├── 2_🇫🇷_National_Trends.py   # France-wide analysis
│   ├── 3_🗺️_Regional_Analysis.py  # Regional comparisons
│   ├── 4_📍_Department_Analysis.py # Department insights + maps
│   ├── 5_🏘️_Commune_Analysis.py   # Commune-level exploration
│   └── 6_📊_Data_Quality.py       # Data validation & methodology
├── utils/
│   ├── io.py                       # Data loading
│   ├── prep.py                     # Data processing
│   └── viz.py                      # Visualization functions (EXTENDED)
├── data/                           # CSV data files
├── assets/                         # GeoJSON files
└── sections/                       # Legacy sections (can be archived)
```

## 🚀 Running the App

```powershell
# From the project directory
streamlit run app.py
```

The app will open at `http://localhost:8501` (or 8502 if 8501 is busy)

## 📊 Pages Overview

### 1. 🏠 Home
- **Purpose**: Landing page with executive summary
- **Features**:
  - Key metrics (total dwellings, vacancy rates, etc.)
  - Navigation guide to all pages
  - Quick statistics
  - Data story introduction

### 2. 🇫🇷 National Trends
- **Purpose**: France-wide analysis
- **Visualizations**:
  - Time series (absolute values, rates, YoY changes)
  - Distribution histograms
  - Composition area charts
  - Growth rate analysis (CAGR)
  - Correlation scatter plots
  - Top/bottom department rankings
- **Filters**: Year range

### 3. 🗺️ Regional Analysis
- **Purpose**: Compare France's 18 regions
- **Visualizations**:
  - Regional rankings (horizontal bar charts)
  - Time series comparisons
  - Heatmaps (regional evolution over time)
  - Stacked area charts (composition)
  - Scatter plots (relationships)
  - Detailed comparison tables
- **Filters**: Year range, specific regions, metric selection

### 4. 📍 Department Analysis
- **Purpose**: Department-level insights
- **Visualizations**:
  - **Interactive choropleth maps** (Plotly)
  - Top/bottom performers
  - Biggest changes over time
  - Time series for selected departments
  - Distribution histograms
  - Correlation analysis
  - Detailed data tables with CSV download
- **Filters**: Year, region, department selection, metric

### 5. 🏘️ Commune Analysis
- **Purpose**: Explore 30,000+ communes
- **Visualizations**:
  - Distribution analysis (vacancy rates, dwelling counts)
  - Outlier detection (IQR-based)
  - Top/bottom rankings
  - Scatter plots (size vs vacancy)
  - Box plots (comparative analysis)
  - Search functionality
  - Detailed tables with filters
- **Filters**: Year, region, department, EPCI, minimum dwelling threshold

### 6. 📊 Data Quality
- **Purpose**: Methodology and validation
- **Content**:
  - Data source documentation
  - Completeness analysis
  - Missing value reports
  - Validation checks
  - Methodology explanation
  - Known limitations
  - Technical specifications
  - Data dictionary

## 🎨 New Visualization Functions

Added to `utils/viz.py`:

1. **`scatter_plot()`** - Scatter plots with color/size encoding
2. **`histogram()`** - Distribution analysis
3. **`heatmap()`** - Matrix-style temporal data
4. **`area_chart()`** - Stacked composition charts
5. **`box_plot()`** - Distribution comparisons
6. **`horizontal_bar_chart()`** - Better label readability

All use consistent theming and are optimized for Streamlit.

## 🔧 Bug Fixes Applied

1. **SettingWithCopyWarning**: Fixed by using `.copy()` on DataFrame slices
2. **TypeError (dtype object)**: Added `pd.to_numeric()` conversions
3. **ZeroDivisionError**: Implemented safe division with zero checks

## 💡 Features

### Interactive Filters
- Each page has relevant sidebar filters
- Filters update all visualizations instantly
- Smart defaults for better UX

### Data Export
- CSV download buttons on multiple pages
- Filtered data exports
- Department and commune-level data

### Responsive Design
- Wide layout for better chart visibility
- Column layouts for side-by-side comparisons
- Tabs for organized content

### Performance
- `@st.cache_data` for data loading
- Efficient pandas operations
- Sampling for large scatter plots

## 📈 Storytelling Structure

The pages follow a narrative flow:

1. **Home** → Set context and hook the user
2. **National** → Establish baseline and trends
3. **Regional** → Show geographic variation
4. **Department** → Drill down to actionable insights
5. **Commune** → Granular exploration
6. **Quality** → Build trust with methodology

## 🎯 Next Steps

### Potential Enhancements:
1. Add time-based animations for trends
2. Include demographic correlations (if data available)
3. Add prediction/forecasting models
4. Create custom Altair themes
5. Add user annotations/bookmarks
6. Export full reports as PDF
7. Add commune-level maps (requires geocoding)

### Content Ideas:
- Policy recommendation page
- Regional deep-dive case studies
- Comparative international analysis
- Economic impact analysis

## 📝 Usage Tips

### For Presentations:
- Start with Home for context
- Use National Trends for overview
- Deep dive into specific regions/departments
- Reference Data Quality for credibility

### For Analysis:
- Use filters to focus on specific geographies
- Download filtered data for external analysis
- Cross-reference multiple pages
- Check outliers in Commune Analysis

### For Reporting:
- Screenshot key visualizations
- Download CSV for custom charts
- Reference methodology from Data Quality page
- Use KPIs from each page

## 🐛 Troubleshooting

**App won't start:**
```powershell
pip install -r requirements.txt
```

**Missing GeoJSON:**
- First run downloads automatically
- Requires internet connection
- Falls back to bar charts if unavailable

**Slow performance:**
- Reduce year range in filters
- Select specific regions/departments
- The app caches data automatically

## 📄 License

- **Data**: LOVAC Open Data (verify license on official portal)
- **Code**: MIT License

## 🙏 Attribution

Data source: LOVAC Open Data - Logements Vacants
Built with: Streamlit, Pandas, Altair, Plotly

---

**Your multi-page app is now live!** 🎊

Access it at: http://localhost:8502
