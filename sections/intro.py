import streamlit as st

def render_intro(st):
    with st.expander("Why this matters — the housing vacancy puzzle", expanded=True):
        st.markdown(
            "Vacant homes are a growing concern for affordability and urban vitality. "
            "This dashboard explores where vacancies concentrate, how they evolve over time, "
            "and what share remain long-term vacant (>2 years)."
        )
        st.caption("Headline: Vacancy has shifted unevenly across departments and regions since 2020.")
