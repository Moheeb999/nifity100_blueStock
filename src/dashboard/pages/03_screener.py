import streamlit as st
from utils.db import get_screener_data

st.title("📊 Nifty 100 Stock Screener")

df = get_screener_data().copy()

preset = st.sidebar.selectbox(
    "Preset",
    [
        "Custom",
        "Quality Compounder",
        "Value Pick",
        "Growth Accelerator",
        "Dividend Champion",
        "Debt-Free Blue Chip",
        "Turnaround Watch",
    ],
)

sector = "All"
if "broad_sector" in df.columns:
    sector = st.sidebar.selectbox(
        "Sector", ["All"] + sorted(df["broad_sector"].dropna().unique())
    )

roe = st.sidebar.slider("Minimum ROE", 0.0, 100.0, 15.0)
de = st.sidebar.slider("Maximum Debt/Equity", 0.0, 5.0, 1.0)
pe = st.sidebar.slider("Maximum P/E", 0.0, 200.0, 40.0)

if preset == "Quality Compounder":
    roe, de = 20.0, 0.5
elif preset == "Value Pick":
    pe = 20.0

if sector != "All":
    df = df[df["broad_sector"] == sector]

if "return_on_equity_pct" in df.columns:
    df = df[df["return_on_equity_pct"].fillna(-1) >= roe]
if "debt_to_equity" in df.columns:
    df = df[df["debt_to_equity"].fillna(999) <= de]
if "pe_ratio" in df.columns:
    df = df[df["pe_ratio"].fillna(999) <= pe]

st.subheader(f"{len(df)} Companies Match")

st.dataframe(df, width="stretch")

st.download_button(
    "📥 Download CSV",
    df.to_csv(index=False).encode("utf-8"),
    "screener_results.csv",
    "text/csv",
)
