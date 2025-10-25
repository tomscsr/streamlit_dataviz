"""
Streamlit Multi-Page App - Vacant Housing in France

This is the entry point for the multi-page Streamlit application.
Navigate using the sidebar to explore different analysis pages:

- 🏠 Home: Overview and executive summary
- 🇫🇷 National Trends: France-wide analysis
- 🗺️ Regional Analysis: Compare regions
- 📍 Department Analysis: Department-level insights with maps
- 🏘️ Commune Analysis: Commune-level deep dive
- 📊 Data Quality: Methodology and validation

The app automatically redirects to the Home page.
"""

import streamlit as st

st.set_page_config(
    page_title="Vacant Housing in France",
    page_icon="🏠",
    layout="wide"
)

# Redirect to Home page
st.info("👈 **Please use the sidebar to navigate between pages**")

st.markdown("""
# Welcome to Vacant Housing in France Dashboard

This application has been reorganized into **multiple pages** for better storytelling and analysis.

## 📚 Navigate Using the Sidebar

Use the **sidebar on the left** to access:

- **🏠 Home** - Executive summary and navigation guide
- **🇫🇷 National Trends** - France-wide analysis with time series and distributions
- **🗺️ Regional Analysis** - Regional comparisons and heatmaps
- **📍 Department Analysis** - Interactive maps and department rankings
- **🏘️ Commune Analysis** - Explore 30,000+ communes with advanced filters
- **📊 Data Quality** - Methodology, validation, and technical documentation

## 🎯 Quick Start

1. Click on **"🏠 Home"** in the sidebar to start
2. Use filters on each page to customize your analysis
3. Download data from various pages as CSV

---

### 💡 Pro Tips

- Each page has **multiple tabs** with different visualizations
- Use **filters in the sidebar** to focus on specific regions or time periods
- **Hover over charts** for detailed tooltips
- **Download buttons** are available on most pages

Start exploring now! 👈
""")

st.markdown("---")
st.caption("Source: LOVAC Open Data | Built with Streamlit")