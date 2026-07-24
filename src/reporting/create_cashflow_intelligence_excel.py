import pandas as pd

# Read existing files
cashflow = pd.read_csv("output/cashflow_intelligence.csv")
capital = pd.read_csv("output/capital_allocation.csv")

# Keep only the latest year's capital allocation
latest_year = capital["year"].max()

capital_latest = (
    capital[capital["year"] == latest_year]
    [["company_id", "pattern_label"]]
    .rename(columns={"pattern_label": "capital_allocation"})
)

# Merge
output = cashflow.merge(
    capital_latest,
    on="company_id",
    how="left"
)

# Save as Excel
output.to_excel(
    "output/cashflow_intelligence.xlsx",
    index=False
)

print("cashflow_intelligence.xlsx generated successfully.")
print(f"Rows: {len(output)}")