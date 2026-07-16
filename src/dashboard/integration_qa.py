import sqlite3
import pandas as pd

DB = "db/nifty100.db"

conn = sqlite3.connect(DB)

print("=" * 60)
print("SPRINT 4 INTEGRATION QA")
print("=" * 60)

tables = [
    "companies",
    "financial_ratios",
    "market_cap",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "peer_groups",
    "peer_percentiles",
    "documents",
    "sectors"
]

print("\nTABLE COUNTS\n")

for table in tables:

    count = pd.read_sql(
        f"SELECT COUNT(*) c FROM {table}",
        conn
    ).iloc[0]["c"]

    print(f"{table:<22} {count}")

print("\n")

companies = pd.read_sql(
    """
    SELECT
        id,
        company_name
    FROM companies
    ORDER BY RANDOM()
    LIMIT 10
    """,
    conn
)

print("=" * 60)
print("TEST COMPANIES")
print("=" * 60)

print(companies)

print("\n")

missing = pd.read_sql(
    """
    SELECT
        c.id,
        c.company_name
    FROM companies c

    LEFT JOIN financial_ratios f

    ON c.id=f.company_id

    WHERE f.company_id IS NULL
    """,
    conn
)

print("=" * 60)
print("COMPANIES WITHOUT RATIOS")
print("=" * 60)

print(missing)

print("\n")

print("=" * 60)
print("QA COMPLETE")
print("=" * 60)

conn.close()