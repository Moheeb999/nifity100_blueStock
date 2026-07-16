import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import get_capital_allocation_data

st.title("🌳 Capital Allocation Map")

df = get_capital_allocation_data()

if df.empty:
    st.warning("No capital allocation data available.")
    st.stop()


def classify(row):

    if row["debt_to_equity"] <= 0.30 and row["return_on_equity_pct"] >= 20:
        return "Quality Compounder"

    elif row["revenue_cagr_5yr"] >= 15:
        return "Growth"

    elif row["free_cash_flow_cr"] > 0:
        return "Cash Generator"

    elif row["debt_to_equity"] >= 2:
        return "Highly Leveraged"

    else:
        return "Balanced"


df["allocation_pattern"] = df.apply(classify, axis=1)

fig = px.treemap(
    df,
    path=["allocation_pattern", "company_name"],
    values="free_cash_flow_cr",
    color="return_on_equity_pct",
    hover_data=[
        "debt_to_equity",
        "revenue_cagr_5yr"
    ]
)

st.plotly_chart(fig, width="stretch")

st.subheader("Allocation Summary")

summary = (
    df.groupby("allocation_pattern")
      .size()
      .reset_index(name="Companies")
)

st.dataframe(summary, width="stretch")

pattern = st.selectbox(
    "Select Pattern",
    sorted(df["allocation_pattern"].unique())
)

companies = df[df["allocation_pattern"] == pattern]

st.subheader(f"{pattern} Companies")

st.dataframe(
    companies[
        [
            "company_name",
            "broad_sector",
            "return_on_equity_pct",
            "debt_to_equity",
            "free_cash_flow_cr",
            "revenue_cagr_5yr"
        ]
    ],
    width="stretch"
)