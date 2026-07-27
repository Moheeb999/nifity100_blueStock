import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = "db/nifty100.db"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    c.company_id,
    c.operating_activity,
    c.investing_activity,
    c.financing_activity,
    c.net_cash_flow
FROM cashflow c
WHERE c.year = (
    SELECT MAX(year)
    FROM cashflow c2
    WHERE c2.company_id = c.company_id
);
"""

df = pd.read_sql(query, conn)
conn.close()

results = []


def add(company, category, insight, confidence):
    results.append(
        {
            "company_id": company,
            "category": category,
            "insight": insight,
            "confidence_pct": confidence,
        }
    )


for _, row in df.iterrows():

    op = row["operating_activity"]
    inv = row["investing_activity"]
    fin = row["financing_activity"]
    net = row["net_cash_flow"]

    # Rule 1 - Healthy Cash Flow
    if op > 0 and inv < 0 and fin < 0:
        add(
            row["company_id"],
            "Healthy Cash Flow",
            "Strong operating cash flow while investing for growth and reducing financing obligations.",
            95,
        )

    # Rule 2 - Growing Business
    if op > 0 and inv < 0 and fin > 0:
        add(
            row["company_id"],
            "Growing Business",
            "Business is generating cash and raising capital to support expansion.",
            90,
        )

    # Rule 3 - Cash Rich
    if op > 0 and net > 0:
        add(
            row["company_id"],
            "Cash Rich",
            "Positive operating and overall cash flow indicate healthy liquidity.",
            92,
        )

    # Rule 4 - Operational Weakness
    if op < 0:
        add(
            row["company_id"],
            "Operational Weakness",
            "Negative operating cash flow indicates weak core business performance.",
            95,
        )

    # Rule 5 - Heavy Borrowing
    if fin > 0 and op < 0:
        add(
            row["company_id"],
            "Heavy Borrowing",
            "Business depends on external financing instead of operations.",
            94,
        )

    # Rule 6 - Cash Burn
    if net < 0 and op < 0:
        add(
            row["company_id"],
            "Cash Burn",
            "Negative operating and net cash flow indicate sustained cash burn.",
            96,
        )
    # Rule 7 - Mixed Cash Flow
    if not (
        (op > 0 and inv < 0 and fin < 0)
        or (op > 0 and inv < 0 and fin > 0)
        or (op > 0 and net > 0)
        or (op < 0)
        or (fin > 0 and op < 0)
        or (net < 0 and op < 0)
    ):
        add(
            row["company_id"],
            "Mixed Cash Flow",
            "Cash flow pattern does not clearly match the predefined categories and requires further analysis.",
            75,
        )

output = pd.DataFrame(results)

output.to_csv(OUTPUT_DIR / "cashflow_intelligence.csv", index=False)

print("=" * 60)
print("CASH FLOW INTELLIGENCE")
print("=" * 60)
print(f"Companies Processed : {df.company_id.nunique()}")
print(f"Insights Generated  : {len(output)}")
print("Generated")
print("output/cashflow_intelligence.csv")
print("=" * 60)
