import streamlit as st
import plotly.express as px

from utils.db import get_sector_analysis

st.title("🫧 Sector Analysis")

# -----------------------------------------
# Load Data
# -----------------------------------------

df = get_sector_analysis()

if df.empty:
    st.warning("No sector data available.")
    st.stop()

# -----------------------------------------
# Sector Dropdown
# -----------------------------------------

sector_list = sorted(
    df["broad_sector"].dropna().unique()
)

selected_sector = st.selectbox(
    "Select Sector",
    sector_list
)

filtered = df[
    df["broad_sector"] == selected_sector
]

# -----------------------------------------
# Bubble Chart
# -----------------------------------------

fig = px.scatter(
    filtered,
    x="sales",
    y="return_on_equity_pct",
    size="market_cap_crore",
    color="sub_sector",
    hover_name="company_name",
    hover_data=[
        "market_cap_crore",
        "sales",
        "return_on_equity_pct"
    ],
    title=f"{selected_sector} Companies",
    labels={
        "sales": "Revenue (Cr)",
        "return_on_equity_pct": "ROE (%)",
        "market_cap_crore": "Market Cap (Cr)"
    }
)

fig.update_layout(
    template="plotly_white",
    height=650
)

st.plotly_chart(
    fig,
    width="stretch"
)

# -----------------------------------------
# Sector KPIs
# -----------------------------------------

st.subheader("Sector Summary")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Companies",
    len(filtered)
)

col2.metric(
    "Average ROE",
    f"{filtered['return_on_equity_pct'].mean():.2f}%"
)

col3.metric(
    "Average Revenue",
    f"{filtered['sales'].mean():,.0f} Cr"
)

# -----------------------------------------
# Sub-sector Summary
# -----------------------------------------

st.subheader("Sub-sector Breakdown")

summary = (
    filtered
    .groupby("sub_sector")
    .agg(
        Companies=("company_name", "count"),
        Average_ROE=("return_on_equity_pct", "mean"),
        Average_Revenue=("sales", "mean"),
        Average_Market_Cap=("market_cap_crore", "mean")
    )
    .round(2)
    .reset_index()
)

st.dataframe(
    summary,
    width="stretch"
)

# -----------------------------------------
# Company Table
# -----------------------------------------

st.subheader("Companies")

display = filtered[
    [
        "company_name",
        "sub_sector",
        "sales",
        "return_on_equity_pct",
        "market_cap_crore"
    ]
].sort_values(
    by="market_cap_crore",
    ascending=False
)

st.dataframe(
    display,
    width="stretch"
)