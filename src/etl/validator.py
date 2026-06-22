import pandas as pd
from src.etl.loader import load_excel


def validate_pk_uniqueness(df, table_name, pk_column):
    failures = []
    duplicates = df[df.duplicated(subset=[pk_column], keep=False)]

    for _, row in duplicates.iterrows():
        failures.append({
            "rule_id": "DQ-01",
            "severity": "CRITICAL",
            "table_name": table_name,
            "row_id": row[pk_column],
            "message": f"Duplicate primary key: {row[pk_column]}"
        })

    return failures


def validate_composite_pk(df, table_name):
    failures = []
    duplicates = df[df.duplicated(subset=["company_id", "year"], keep=False)]

    for _, row in duplicates.iterrows():
        failures.append({
            "rule_id": "DQ-02",
            "severity": "CRITICAL",
            "table_name": table_name,
            "row_id": f"{row['company_id']}_{row['year']}",
            "message": "Duplicate composite key"
        })

    return failures


def validate_fk(df, companies_df, table_name):
    failures = []
    valid_ids = set(companies_df["id"])

    invalid_rows = df[~df["company_id"].isin(valid_ids)]

    for _, row in invalid_rows.iterrows():
        failures.append({
            "rule_id": "DQ-03",
            "severity": "CRITICAL",
            "table_name": table_name,
            "row_id": row["company_id"],
            "message": "Foreign key missing"
        })

    return failures


def validate_balance_sheet(bs_df):
    failures = []

    invalid_rows = bs_df[
        (
            abs(bs_df["total_assets"] - bs_df["total_liabilities"])
            / bs_df["total_assets"]
        ) > 0.01
    ]

    for _, row in invalid_rows.iterrows():
        failures.append({
            "rule_id": "DQ-04",
            "severity": "WARNING",
            "table_name": "balancesheet",
            "row_id": f"{row['company_id']}_{row['year']}",
            "message": "Balance sheet mismatch > 1%"
        })

    return failures


def validate_opm(pnl_df):
    failures = []

    calc_opm = (pnl_df["operating_profit"] / pnl_df["sales"]) * 100

    invalid_rows = pnl_df[
        abs(calc_opm - pnl_df["opm_percentage"]) > 1
    ]

    for _, row in invalid_rows.iterrows():
        failures.append({
            "rule_id": "DQ-05",
            "severity": "WARNING",
            "table_name": "profitandloss",
            "row_id": f"{row['company_id']}_{row['year']}",
            "message": "OPM mismatch > 1%"
        })

    return failures


def validate_positive_sales(pnl_df):
    failures = []

    invalid_rows = pnl_df[pnl_df["sales"] <= 0]

    for _, row in invalid_rows.iterrows():
        failures.append({
            "rule_id": "DQ-06",
            "severity": "CRITICAL",
            "table_name": "profitandloss",
            "row_id": f"{row['company_id']}_{row['year']}",
            "message": "Sales must be positive"
        })

    return failures


def main():
    companies = load_excel("data/raw/companies.xlsx")
    pnl = load_excel("data/raw/profitandloss.xlsx")
    bs = load_excel("data/raw/balancesheet.xlsx")
    cf = load_excel("data/raw/cashflow.xlsx")

    failures = []

    # DQ-01
    failures.extend(validate_pk_uniqueness(companies, "companies", "id"))

    # DQ-02
    failures.extend(validate_composite_pk(pnl, "profitandloss"))
    failures.extend(validate_composite_pk(bs, "balancesheet"))
    failures.extend(validate_composite_pk(cf, "cashflow"))

    # DQ-03
    failures.extend(validate_fk(pnl, companies, "profitandloss"))
    failures.extend(validate_fk(bs, companies, "balancesheet"))
    failures.extend(validate_fk(cf, companies, "cashflow"))

    # DQ-04
    failures.extend(validate_balance_sheet(bs))

    # DQ-05
    failures.extend(validate_opm(pnl))

    # DQ-06
    failures.extend(validate_positive_sales(pnl))

    failure_df = pd.DataFrame(failures)
    failure_df.to_csv("output/validation_failures.csv", index=False)

    print("Validation complete")
    print("Total Failures:", len(failures))

    if len(failure_df) > 0:
        print("\nFailures by Rule:")
        print(failure_df.groupby("rule_id").size())


if __name__ == "__main__":
    main()