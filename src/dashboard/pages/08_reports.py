import streamlit as st
import pandas as pd
import sqlite3

from utils.db import search_companies

DB_PATH = "db/nifty100.db"

st.title("📄 Annual Reports")

# -------------------------------------
# Company Selection
# -------------------------------------

companies = search_companies()

company_map = {
    f"{row.company_name} ({row.id})": row.id
    for _, row in companies.iterrows()
}

selected = st.selectbox(
    "Select Company",
    sorted(company_map.keys())
)

ticker = company_map[selected]

# -------------------------------------
# Load Reports
# -------------------------------------

conn = sqlite3.connect(DB_PATH)

reports = pd.read_sql(
    """
    SELECT
        year,
        annual_report
    FROM documents
    WHERE company_id = ?
    ORDER BY year DESC
    """,
    conn,
    params=[ticker]
)

conn.close()

# -------------------------------------
# Display Reports
# -------------------------------------

if reports.empty:

    st.info(
        "No annual reports available."
    )

else:

    st.subheader("Available Reports")

    for _, row in reports.iterrows():

        year = row["year"]
        url = row["annual_report"]

        if (
            pd.isna(url)
            or str(url).strip() == ""
        ):

            st.error(
                f"{year} — Report unavailable"
            )

        else:

            st.markdown(
                f"📄 **{year}** — [Open Annual Report]({url})"
            )

# -------------------------------------
# Summary
# -------------------------------------

st.divider()

st.metric(
    "Reports Available",
    len(reports)
)