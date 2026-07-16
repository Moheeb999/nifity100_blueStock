import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.db import (
    get_peer_groups,
    get_peer_companies,
    get_peer_metrics
)

st.title("🤝 Peer Comparison")

# --------------------------------------------------
# Peer Group Selection
# --------------------------------------------------

groups = get_peer_groups()

if groups.empty:
    st.warning("No peer groups available.")
    st.stop()

group = st.selectbox(
    "Peer Group",
    groups["peer_group_name"]
)

# --------------------------------------------------
# Company Selection
# --------------------------------------------------

companies = get_peer_companies(group)

if companies.empty:
    st.warning("No companies available.")
    st.stop()

mapping = {
    f"{r.company_name} ({r.company_id})": r.company_id
    for _, r in companies.iterrows()
}

ticker = mapping[
    st.selectbox(
        "Company",
        list(mapping.keys())
    )
]

# --------------------------------------------------
# Metrics
# --------------------------------------------------

metrics = get_peer_metrics(group)

if metrics.empty:
    st.warning("No peer metrics found.")
    st.stop()

row = metrics[
    metrics.company_id == ticker
]

if row.empty:
    st.warning("Company metrics unavailable.")
    st.stop()

row = row.iloc[0]

# --------------------------------------------------
# Radar Chart
# --------------------------------------------------

cols = [
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "composite_quality_score"
]

labels = [
    "ROE",
    "ROCE",
    "NPM",
    "OPM",
    "D/E",
    "Revenue CAGR",
    "PAT CAGR",
    "Quality"
]

peer_average = metrics[
    cols
].mean(
    numeric_only=True
)

company_values = [
    0 if pd.isna(row[c]) else float(row[c])
    for c in cols
]

peer_values = [
    0 if pd.isna(peer_average[c]) else float(peer_average[c])
    for c in cols
]

company_values.append(company_values[0])
peer_values.append(peer_values[0])

theta = labels + [labels[0]]

fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=company_values,
        theta=theta,
        fill="toself",
        name=row["company_name"]
    )
)

fig.add_trace(
    go.Scatterpolar(
        r=peer_values,
        theta=theta,
        fill="toself",
        name="Peer Average"
    )
)

fig.update_layout(

    title="Company vs Peer Average",

    polar=dict(

        bgcolor="white",

        radialaxis=dict(

            visible=True,
            showline=True,
            linewidth=1,
            gridcolor="lightgray"

        )

    ),

    legend=dict(

        orientation="h",
        y=1.10

    ),

    template="plotly_white"

)

st.plotly_chart(
    fig,
    width="stretch"
)

# --------------------------------------------------
# Benchmark Cards
# --------------------------------------------------

st.subheader("Peer Benchmark")

left, right = st.columns(2)

with left:

    st.metric(
        "Selected Company",
        row["company_name"]
    )

with right:

    best = metrics.loc[
        metrics[
            "composite_quality_score"
        ].idxmax()
    ]

    st.metric(
        "Best Quality Score",
        best["company_name"]
    )

# --------------------------------------------------
# Peer KPI Table
# --------------------------------------------------

st.subheader("Peer KPI Table")

display = metrics.copy()

display = display.rename(
    columns={
        "company_name": "Company",
        "return_on_equity_pct": "ROE",
        "return_on_capital_employed_pct": "ROCE",
        "net_profit_margin_pct": "NPM",
        "operating_profit_margin_pct": "OPM",
        "debt_to_equity": "D/E",
        "revenue_cagr_5yr": "Revenue CAGR",
        "pat_cagr_5yr": "PAT CAGR",
        "composite_quality_score": "Quality Score"
    }
)


def highlight_company(r):

    if r["Company"] == row["company_name"]:

        return [
            "background-color:#C8F7C5;font-weight:bold"
        ] * len(r)

    return [
        ""
    ] * len(r)


styled = (
    display
    .style
    .format(precision=2)
    .apply(
        highlight_company,
        axis=1
    )
)

st.dataframe(
    styled,
    width="stretch"
)

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.caption(
    f"""
Peer Group : {group}

Companies : {len(metrics)}
"""
)   