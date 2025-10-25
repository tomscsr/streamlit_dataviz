import streamlit as st

def render_conclusions(st):
    st.markdown("## Key Insights & Next Steps")
    st.success(
        "Across 2020–2025, vacancy trends diverge by region. Some high-growth areas saw stable vacancy rates, "
        "while others show rising long-term vacancy. Targeted policies (renovation incentives, mobilization of "
        "long-vacant stock) could have outsized impact in top-concentration departments."
    )
    st.caption("Next steps: enrich with price/rent data to study correlations; add commune-level map when centroids are available.")
