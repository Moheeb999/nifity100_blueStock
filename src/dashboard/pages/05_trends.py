import plotly.graph_objects as go
import streamlit as st
from utils.db import get_trend_data, search_companies

st.title("📈 Trend Analysis")

# -----------------------------
# Company Selection
# -----------------------------

companies = search_companies()

company_map = {
    f"{row.company_name} ({row.id})": row.id for _, row in companies.iterrows()
}

selected_company = st.selectbox("Select Company", sorted(company_map.keys()))

ticker = company_map[selected_company]

# -----------------------------
# Load Trend Data
# -----------------------------

df = get_trend_data(ticker)

if df.empty:
    st.warning("No trend data available.")
    st.stop()

# -----------------------------
# Metric Selection
# -----------------------------

metric_options = {
    "ROE": "return_on_equity_pct",
    "ROCE": "return_on_capital_employed_pct",
    "Revenue CAGR": "revenue_cagr_5yr",
    "PAT CAGR": "pat_cagr_5yr",
    "Net Profit Margin": "net_profit_margin_pct",
    "Operating Profit Margin": "operating_profit_margin_pct",
    "Debt / Equity": "debt_to_equity",
    "Interest Coverage": "interest_coverage",
    "Free Cash Flow": "free_cash_flow_cr",
}

selected_metrics = st.multiselect(
    "Select up to 3 Metrics",
    list(metric_options.keys()),
    default=["ROE"],
    max_selections=3,
)

# -----------------------------
# Plotly Chart
# -----------------------------

fig = go.Figure()

for metric in selected_metrics:

    column = metric_options[metric]

    fig.add_trace(
        go.Scatter(x=df["year"], y=df[column], mode="lines+markers", name=metric)
    )

fig.update_layout(
    title="Financial Trend Analysis",
    xaxis_title="Year",
    yaxis_title="Metric Value",
    template="plotly_white",
    hovermode="x unified",
    height=600,
)

st.plotly_chart(fig, width="stretch")

# -----------------------------
# Trend Data Table
# -----------------------------

st.subheader("Historical Financial Data")

st.dataframe(df, width="stretch")
