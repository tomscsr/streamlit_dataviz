# Quick Start Guide - France's Vacant Housing Dashboard

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

Open PowerShell in the project folder and run:

```powershell
pip install -r requirements.txt
```

This will install:
- Streamlit (web framework)
- Pandas (data processing)
- Plotly (interactive charts)
- NumPy (numerical computing)

### Step 2: Verify Data Files

Make sure these files exist in the `data/` folder:
- ✅ `lovac_opendata_dep.csv` (101 rows - departments)
- ✅ `lovac-opendata-communes.csv` (~35,000 rows - communes)

Both files should already be there!

### Step 3: Run the Dashboard

```powershell
streamlit run app.py
```

The dashboard will open automatically in your browser at:
**http://localhost:8501**

---

## 📱 Using the Dashboard

### Navigation
Use the **sidebar** to switch between pages:
1. 🏠 **Introduction** - Start here for context
2. 🇫🇷 **National Overview** - See France-wide trends
3. 🗺️ **Departmental Analysis** - Compare departments
4. 🏘️ **Commune Deep Dive** - Explore municipal data
5. 📋 **Conclusions** - Read key insights

### Filters & Interactions
- **Sliders**: Select time periods
- **Dropdowns**: Choose regions/departments
- **Multiselect**: Compare multiple items
- **Search**: Find specific communes
- **Hover**: See detailed tooltips on charts

### Tips for Best Experience
- Start with Introduction to understand the data
- Use filters to focus on areas of interest
- Hover over charts for detailed information
- Charts are interactive - click, zoom, pan!
- All tables can be sorted by clicking headers

---

## 🔍 What You'll Discover

### National Level (Overview Page)
- How many properties are vacant in France?
- Is vacancy increasing or decreasing?
- What percentage are long-term (2+ years)?
- Year-over-year trends and changes

### Department Level (Departmental Page)
- Which departments have highest vacancy?
- How do rates vary across France?
- Rural vs. urban patterns
- Time series comparisons

### Commune Level (Commune Page)
- Municipal-level vacancy patterns
- Filter by region or department
- Search for specific towns
- Size class analysis (small vs. large)

### Policy Insights (Conclusions Page)
- What do the patterns mean?
- Targeted recommendations
- Urban vs. rural strategies
- Next steps for policymakers

---

## ⚡ Keyboard Shortcuts

While the app is running:
- **Ctrl+C** in PowerShell: Stop the server
- **F5** in browser: Refresh the page
- **R** in Streamlit: Rerun the app (if you edit code)

---

## 🆘 Troubleshooting

### App won't start?
```powershell
# Check Python version (need 3.8+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Data not loading?
- Verify CSV files are in `data/` folder
- Check file names match exactly (case-sensitive)
- Ensure files aren't corrupted or empty

### Charts not showing?
- Refresh the browser (F5)
- Clear browser cache
- Try a different browser (Chrome recommended)

### Port already in use?
```powershell
# Run on different port
streamlit run app.py --server.port 8502
```

---

## 📊 Sample Exploration Flow

**Beginner Path** (15 minutes):
1. Read Introduction
2. Check National Overview KPIs
3. Look at top 10 departments in Departmental Analysis
4. Read Conclusions

**Detailed Path** (45 minutes):
1. Introduction - understand context
2. National Overview - all tabs
3. Departmental Analysis - explore rankings, trends, correlations
4. Commune Deep Dive - filter your region, search your city
5. Conclusions - policy recommendations

**Power User Path** (1+ hour):
1. All pages in detail
2. Compare multiple departments over time
3. Analyze your specific region/department
4. Export findings (screenshots)
5. Cross-reference with other sources

---

## 💡 Pro Tips

1. **Use filters strategically**: Don't overwhelm yourself - focus on one region at a time
2. **Follow the narrative**: Pages are ordered to tell a story (national → department → commune)
3. **Compare thoughtfully**: Use relative metrics (rates) not just absolute numbers
4. **Context matters**: Read the data limitations in Introduction
5. **Take notes**: Jot down interesting findings as you explore

---

## 📸 Taking Screenshots

To save visualizations:
- **Plotly charts**: Hover → camera icon → download PNG
- **Full page**: Browser screenshot (Windows: Win+Shift+S)
- **Tables**: Select → copy → paste to Excel

---

## 🎓 Learning Objectives Checklist

After exploring, you should understand:
- ✅ What housing vacancy is and why it matters
- ✅ National vacancy trends (2020-2025)
- ✅ Geographic variation across departments
- ✅ Difference between temporary and structural vacancy
- ✅ Policy implications for different contexts
- ✅ Data limitations and research opportunities

---

## 🔗 Next Steps

**Want to go deeper?**
- Export data from tables
- Cross-reference with INSEE demographics
- Correlate with economic indicators
- Propose additional analyses
- Suggest dashboard improvements

**Want to modify?**
- Code is well-documented
- Edit files in `sections/` for content changes
- Modify `utils/viz.py` for chart styling
- Add new pages by creating new section files

---

## 📞 Getting Help

- **README.md**: Full project documentation
- **Code comments**: Every function is documented
- **Streamlit docs**: https://docs.streamlit.io
- **Plotly docs**: https://plotly.com/python

---

**Enjoy exploring France's vacant housing landscape!** 🏠📊🇫🇷
