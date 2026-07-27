from pathlib import Path

import pandas as pd

INPUT = Path("output/capital_allocation.csv")
OUTPUT = Path("output/pattern_changes.csv")

# Read capital allocation history
df = pd.read_csv(INPUT)

# Ensure chronological order
df = df.sort_values(["company_id", "year"])

records = []

for company, group in df.groupby("company_id"):
    first = group.iloc[0]
    last = group.iloc[-1]

    records.append(
        {
            "company_id": company,
            "start_year": first["year"],
            "end_year": last["year"],
            "from_pattern": first["pattern_label"],
            "to_pattern": last["pattern_label"],
            "changed": first["pattern_label"] != last["pattern_label"],
        }
    )

result = pd.DataFrame(records)

# Save CSV
result.to_csv(OUTPUT, index=False)

print("=" * 60)
print("PATTERN CHANGE REPORT")
print("=" * 60)
print(f"Companies Analysed : {len(result)}")
print(f"Changed Patterns   : {result['changed'].sum()}")
print(f"Unchanged Patterns : {(~result['changed']).sum()}")
print(f"Output             : {OUTPUT}")
print("=" * 60)
