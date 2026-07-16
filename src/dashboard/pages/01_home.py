import streamlit as st
import plotly.express as px

from utils.db import (
    get_home_kpis,
    get_sector_breakdown,
    get_top_quality_companies
)

st.title("🏠 Nifty 100 Dashboard")

# -----------------------------
# Sidebar
# -----------------------------
year = st.sidebar.selectbox(
    "Select Year",
    [2019, 2020, 2021, 2022, 2023, 2024],
    index=5
)

# -----------------------------
# Load Data
# -----------------------------
kpis = get_home_kpis(year)

sector_df = get_sector_breakdown()

top5 = get_top_quality_companies(year)

# -----------------------------
# KPI Cards
# -----------------------------
c1, c2, c3 = st.columns(3)

c1.metric(
    "Average ROE",
    f"{kpis['avg_roe']:.2f}%"
)

c2.metric(
    "Median P/E",
    f"{kpis['median_pe']:.2f}"
)

c3.metric(
    "Median D/E",
    f"{kpis['median_de']:.2f}"
)

c4, c5, c6 = st.columns(3)

c4.metric(
    "Companies",
    kpis["total_companies"]
)

c5.metric(
    "Median Revenue CAGR",
    f"{kpis['median_revenue_cagr']:.2f}%"
)

c6.metric(
    "Debt-Free Companies",
    kpis["debt_free_companies"]
)

st.divider()

# -----------------------------
# Donut Chart
# -----------------------------
st.subheader("Sector Distribution")

fig = px.pie(
    sector_df,
    names="broad_sector",
    values="companies",
    hole=0.5
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

# -----------------------------
# Top Quality Companies
# -----------------------------
st.subheader("Top 5 Companies by Composite Quality Score")

st.dataframe(
    top5,
    use_container_width=True
)