import sqlite3
from pathlib import Path

import pandas as pd

DB = "db/nifty100.db"
OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

conn = sqlite3.connect(DB)

query = """
SELECT
    c.id AS company_id,
    c.company_name,
    s.broad_sector,
    mc.year,
    fr.free_cash_flow_cr,
    mc.market_cap_crore,
    mc.pe_ratio,
    mc.pb_ratio,
    mc.ev_ebitda
FROM market_cap mc
LEFT JOIN financial_ratios fr
ON mc.company_id = fr.company_id
AND mc.year = fr.year
LEFT JOIN companies c
ON mc.company_id = c.id
LEFT JOIN sectors s
ON mc.company_id = s.company_id
WHERE mc.year=2024
"""

df = pd.read_sql(query, conn)

conn.close()

df["fcf_yield_pct"] = (df["free_cash_flow_cr"] / df["market_cap_crore"]) * 100

sector_pe = (
    df.groupby("broad_sector")["pe_ratio"]
    .median()
    .reset_index()
    .rename(columns={"pe_ratio": "sector_median_pe"})
)

df = df.merge(sector_pe, on="broad_sector", how="left")

df["pe_vs_sector_median_pct"] = (df["pe_ratio"] / df["sector_median_pe"]) * 100


def classify(r):
    """Classify valuation relative to the sector median."""

    if pd.isna(r["pe_ratio"]):
        return "N/A"

    if r["pe_ratio"] > r["sector_median_pe"] * 1.5:
        return "Caution"

    if r["pe_ratio"] < r["sector_median_pe"] * 0.7:
        return "Discount"

    return "Fair"


df["flag"] = df.apply(classify, axis=1)

summary = df[
    [
        "company_id",
        "company_name",
        "broad_sector",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "fcf_yield_pct",
        "sector_median_pe",
        "pe_vs_sector_median_pct",
        "flag",
    ]
]

summary.to_excel(OUTPUT / "valuation_summary.xlsx", index=False)

summary[summary["flag"] != "Fair"].to_csv(OUTPUT / "valuation_flags.csv", index=False)

print("=" * 50)
print("Valuation Module Complete")
print("=" * 50)
print(f"Companies : {len(summary)}")
print(f"Discount : {(summary.flag=='Discount').sum()}")
print(f"Caution : {(summary.flag=='Caution').sum()}")
print(f"Fair : {(summary.flag=='Fair').sum()}")
print()
print("Generated:")
print("output/valuation_summary.xlsx")
print("output/valuation_flags.csv")
print("=" * 50)
