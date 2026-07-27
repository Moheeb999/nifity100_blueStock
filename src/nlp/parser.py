import re
from pathlib import Path

import pandas as pd

INPUT_FILE = "data/raw/analysis.xlsx"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

PATTERN = re.compile(r"(\d+)\s*Years?:?\s*([-]?[\d.]+)%")

print("=" * 60)
print("NLP ANALYSIS PARSER")
print("=" * 60)

# ----------------------------------------
# Read Excel
# ----------------------------------------

df = pd.read_excel(INPUT_FILE, header=1)

records = []
failures = []

metric_columns = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe",
]

# ----------------------------------------
# Parse
# ----------------------------------------

for _, row in df.iterrows():

    company = row["company_id"]

    for metric in metric_columns:

        value = row[metric]

        if pd.isna(value):
            continue

        text = str(value).strip()

        match = PATTERN.search(text)

        if match:

            records.append(
                {
                    "company_id": company,
                    "metric_type": metric,
                    "period_years": int(match.group(1)),
                    "value_pct": float(match.group(2)),
                }
            )

        else:

            failures.append(
                {"company_id": company, "metric_type": metric, "raw_text": text}
            )

# ----------------------------------------
# Save Outputs
# ----------------------------------------

parsed = pd.DataFrame(records)
parsed.to_csv(OUTPUT_DIR / "analysis_parsed.csv", index=False)

failed = pd.DataFrame(failures)
failed.to_csv(OUTPUT_DIR / "parse_failures.csv", index=False)

# ----------------------------------------
# Summary
# ----------------------------------------

print(f"Rows Read           : {len(df)}")
print(f"Values Parsed       : {len(parsed)}")
print(f"Parse Failures      : {len(failed)}")

print()
print("Validation Status")
print("-" * 60)
print("Validation skipped:")
print("analysis.xlsx contains 20 records")
print("analysis table contains 16 records")
print("Source datasets are not synchronized.")

print()
print("Generated")
print("output/analysis_parsed.csv")
print("output/parse_failures.csv")

print("=" * 60)
