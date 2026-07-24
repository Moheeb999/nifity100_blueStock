import pandas as pd

# -----------------------------------------
# Read Files
# -----------------------------------------

cashflow = pd.read_csv("output/cashflow_intelligence.csv")
capital = pd.read_csv("output/capital_allocation.csv")

# -----------------------------------------
# Latest Capital Allocation
# -----------------------------------------

latest_year = capital["year"].max()

capital_latest = (
    capital[capital["year"] == latest_year]
    [["company_id", "pattern_label"]]
    .rename(columns={
        "pattern_label": "capital_allocation"
    })
)

# -----------------------------------------
# Build Company Summary
# -----------------------------------------

summary = (
    cashflow
    .groupby("company_id")
    .agg(
        categories=("category",
                    lambda x: ", ".join(sorted(set(x)))),

        insights=("insight",
                  lambda x: " | ".join(x)),

        confidence_pct=("confidence_pct", "max")
    )
    .reset_index()
)

# -----------------------------------------
# Merge Capital Allocation
# -----------------------------------------

summary = summary.merge(
    capital_latest,
    on="company_id",
    how="left"
)

# -----------------------------------------
# Save
# -----------------------------------------

summary.to_excel(
    "output/cashflow_intelligence.xlsx",
    index=False
)

print("Cashflow Intelligence Summary Generated")
print(f"Companies : {summary.company_id.nunique()}")
print(f"Rows      : {len(summary)}")