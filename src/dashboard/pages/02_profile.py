import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.db import (
    get_company_profile,
    get_latest_ratios,
    get_profit_loss_history,
    get_pros_cons,
    get_ratio_history,
    search_companies,
)


def format_value(value, suffix=""):
    """Format numeric values for display in the dashboard."""
    if value is None:
        return "N/A"
    try:
        if str(value).lower() == "nan":
            return "N/A"
        return f"{float(value):,.2f}{suffix}"
    except Exception:
        return "N/A"


st.title("🏢 Company Profile")

companies = search_companies()

company_map = {
    f"{row.company_name} ({row.id})": row.id for _, row in companies.iterrows()
}

selected = st.selectbox("🔍 Search Company", sorted(company_map.keys()))

ticker = company_map[selected]

profile = get_company_profile(ticker)

if profile.empty:
    st.warning("Ticker not found — please try another.")
    st.stop()

company = profile.iloc[0]

ratios = get_latest_ratios(ticker)

if ratios.empty:
    st.error("Financial ratios not available.")
    st.stop()

ratio = ratios.iloc[0]

st.subheader("Company Information")

left, right = st.columns(2)

with left:
    st.write(f"**Company Name:** {company.get('company_name','N/A')}")
    st.write(f"**Ticker:** {company.get('id','N/A')}")
    st.write(f"**Sector:** {company.get('broad_sector','N/A')}")

with right:
    st.write(f"**Sub Sector:** {company.get('sub_sector','N/A')}")
    if company.get("website"):
        st.write(f"**Website:** {company['website']}")

st.divider()

st.subheader("Latest Financial KPIs")

c1, c2, c3 = st.columns(3)
c1.metric("ROE", format_value(ratio.get("return_on_equity_pct"), "%"))
c2.metric("ROCE", format_value(ratio.get("return_on_capital_employed_pct"), "%"))
c3.metric("Net Profit Margin", format_value(ratio.get("net_profit_margin_pct"), "%"))

c4, c5, c6 = st.columns(3)
c4.metric("Debt / Equity", format_value(ratio.get("debt_to_equity")))
c5.metric("Revenue CAGR (5Y)", format_value(ratio.get("revenue_cagr_5yr"), "%"))
c6.metric("Free Cash Flow", format_value(ratio.get("free_cash_flow_cr"), " Cr"))

st.divider()

history = get_profit_loss_history(ticker)
st.subheader("Revenue & Net Profit (10 Years)")

if history.empty:
    st.info("Historical profit & loss data not available.")
else:
    fig = px.bar(
        history,
        x="year",
        y=["sales", "net_profit"],
        barmode="group",
        title="Revenue vs Net Profit",
    )
    st.plotly_chart(fig, width="stretch")

st.divider()

ratio_history = get_ratio_history(ticker)
st.subheader("ROE & ROCE Trend")

if ratio_history.empty:
    st.info("Historical ratio data not available.")
else:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ratio_history["year"],
            y=ratio_history["return_on_equity_pct"],
            mode="lines+markers",
            name="ROE",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=ratio_history["year"],
            y=ratio_history["return_on_capital_employed_pct"],
            mode="lines+markers",
            name="ROCE",
        )
    )
    fig.update_layout(xaxis_title="Year", yaxis_title="Percentage")
    st.plotly_chart(fig, width="stretch")

st.divider()

st.subheader("About Company")
about = company.get("about_company", "")

if str(about).strip():
    st.write(about)
else:
    st.info("No company description available.")

st.divider()

st.subheader("Pros & Cons")

try:
    pc = get_pros_cons(ticker)
    if pc.empty:
        st.info("Pros & Cons not available.")
    else:
        pcol, ccol = st.columns(2)

        with pcol:
            st.success("Pros")
            for item in str(pc.iloc[0].get("pros", "")).split("|"):
                if item.strip():
                    st.write("✅", item.strip())

        with ccol:
            st.error("Cons")
            for item in str(pc.iloc[0].get("cons", "")).split("|"):
                if item.strip():
                    st.write("❌", item.strip())
except Exception:
    st.info("Pros & Cons data unavailable.")

st.divider()

st.subheader("Useful Links")

l, r = st.columns(2)

with l:
    if company.get("nse_profile"):
        st.markdown(f"[📈 NSE Profile]({company['nse_profile']})")

with r:
    if company.get("bse_profile"):
        st.markdown(f"[📊 BSE Profile]({company['bse_profile']})")
