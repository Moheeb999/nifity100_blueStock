import streamlit as st

st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📈 Nifty 100 Analytics Dashboard")

st.markdown("""
    ## Welcome

    This dashboard provides:

    - Stock Screener
    - Company Profile
    - Peer Comparison
    - Trend Analysis
    - Sector Analysis
    - Capital Allocation
    - Annual Reports
    - Valuation Analytics
    """)

st.success("Select a page from the sidebar to begin.")
