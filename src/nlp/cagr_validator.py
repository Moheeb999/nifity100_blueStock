import sqlite3
from pathlib import Path

import pandas as pd


# ============================================
# Paths
# ============================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"
PARSED_FILE = BASE_DIR / "output" / "analysis_parsed.csv"
OUTPUT_FILE = BASE_DIR / "output" / "cagr_validation.csv"


# ============================================
# Load Parsed CSV
# ============================================

print("Loading parsed CAGR data...")

parsed = pd.read_csv(PARSED_FILE)

parsed = parsed[
    (
        parsed["metric_type"].isin(
            [
                "compounded_sales_growth",
                "compounded_profit_growth",
            ]
        )
    )
    &
    (parsed["period_years"] == 5)
].copy()

print(f"Parsed rows selected : {len(parsed)}")


# ============================================
# Load Database Values
# ============================================

print("Loading computed CAGR values from database...")

conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    company_id,
    revenue_cagr_5yr,
    pat_cagr_5yr
FROM financial_ratios
WHERE year = (
    SELECT MAX(fr2.year)
    FROM financial_ratios fr2
    WHERE fr2.company_id = financial_ratios.company_id
)
"""

ratios = pd.read_sql(query, conn)

conn.close()

print(f"Companies loaded : {len(ratios)}")


# ============================================
# Merge
# ============================================

merged = parsed.merge(
    ratios,
    on="company_id",
    how="left"
)

print(f"Rows after merge : {len(merged)}")


# ============================================
# Validation
# ============================================

results = []

for _, row in merged.iterrows():

    if row["metric_type"] == "compounded_sales_growth":
        computed_value = row["revenue_cagr_5yr"]
        metric_name = "Revenue CAGR"

    else:
        computed_value = row["pat_cagr_5yr"]
        metric_name = "PAT CAGR"

    parsed_value = row["value_pct"]

    if pd.isna(computed_value):

        difference = None
        status = "NO DATA"

    else:

        difference = abs(parsed_value - computed_value)

        if difference <= 5:
            status = "PASS"
        else:
            status = "REVIEW"

    results.append(
        {
            "company_id": row["company_id"],
            "metric_type": metric_name,
            "parsed_value": parsed_value,
            "computed_value": computed_value,
            "difference": difference,
            "status": status,
        }
    )


# ============================================
# Save Output
# ============================================

validation = pd.DataFrame(results)

validation.to_csv(
    OUTPUT_FILE,
    index=False,
)

# ============================================
# Summary
# ============================================

total = len(validation)

passed = (validation["status"] == "PASS").sum()

review = (validation["status"] == "REVIEW").sum()

nodata = (validation["status"] == "NO DATA").sum()

print("\n" + "=" * 45)
print("        CAGR VALIDATION SUMMARY")
print("=" * 45)

print(f"Rows Compared      : {total}")
print(f"PASS               : {passed}")
print(f"REVIEW             : {review}")
print(f"NO DATA            : {nodata}")

print("\nValidation file saved to:")
print(OUTPUT_FILE)

print("=" * 45)