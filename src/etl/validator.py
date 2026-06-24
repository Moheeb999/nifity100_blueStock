import pandas as pd
from src.etl.loader import load_excel


def normalize_columns(df):
    df.columns = [
        str(col).strip().lower().replace(" ", "_")
        for col in df.columns
    ]
    return df


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
        (abs(bs_df["total_assets"] - bs_df["total_liabilities"])
         / bs_df["total_assets"]) > 0.01
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
    invalid_rows = pnl_df[abs(calc_opm - pnl_df["opm_percentage"]) > 1]

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
    invalid_rows = pnl_df[pnl_df["sales"] < 0]

    for _, row in invalid_rows.iterrows():
        failures.append({
            "rule_id": "DQ-06",
            "severity": "CRITICAL",
            "table_name": "profitandloss",
            "row_id": f"{row['company_id']}_{row['year']}",
            "message": "Negative sales"
        })
    return failures


def validate_net_cash(cf_df):
    failures = []
    calc_net = (
        cf_df["operating_activity"] +
        cf_df["investing_activity"] +
        cf_df["financing_activity"]
    )

    invalid_rows = cf_df[abs(calc_net - cf_df["net_cash_flow"]) > 1]

    for _, row in invalid_rows.iterrows():
        failures.append({
            "rule_id": "DQ-07",
            "severity": "WARNING",
            "table_name": "cashflow",
            "row_id": f"{row['company_id']}_{row['year']}",
            "message": "Net cash mismatch"
        })
    return failures


def validate_tax_rate(pnl_df):
    failures = []
    invalid_rows = pnl_df[
        (pnl_df["tax_percentage"] < 0) |
        (pnl_df["tax_percentage"] > 100)
    ]

    for _, row in invalid_rows.iterrows():
        failures.append({
            "rule_id": "DQ-08",
            "severity": "WARNING",
            "table_name": "profitandloss",
            "row_id": f"{row['company_id']}_{row['year']}",
            "message": "Invalid tax %"
        })
    return failures


def validate_dividend_cap(pnl_df):
    failures = []
    invalid_rows = pnl_df[pnl_df["dividend_payout"] > 100]

    for _, row in invalid_rows.iterrows():
        failures.append({
            "rule_id": "DQ-09",
            "severity": "WARNING",
            "table_name": "profitandloss",
            "row_id": f"{row['company_id']}_{row['year']}",
            "message": "Dividend payout > 100%"
        })
    return failures


def validate_urls(companies_df):
    failures = []
    for col in ["website", "nse_profile", "bse_profile"]:
        invalid_rows = companies_df[
            ~companies_df[col].astype(str).str.startswith(("http://", "https://"))
        ]

        for _, row in invalid_rows.iterrows():
            failures.append({
                "rule_id": "DQ-10",
                "severity": "WARNING",
                "table_name": "companies",
                "row_id": row["id"],
                "message": f"Invalid URL in {col}"
            })
    return failures


def validate_eps_sign(pnl_df):
    failures = []
    invalid_rows = pnl_df[
        (pnl_df["net_profit"] < 0) &
        (pnl_df["eps"] > 0)
    ]

    for _, row in invalid_rows.iterrows():
        failures.append({
            "rule_id": "DQ-11",
            "severity": "WARNING",
            "table_name": "profitandloss",
            "row_id": f"{row['company_id']}_{row['year']}",
            "message": "Negative profit but positive EPS"
        })
    return failures


def validate_profiles(companies_df):
    failures = []
    invalid_rows = companies_df[
        companies_df["nse_profile"].isna() |
        companies_df["bse_profile"].isna()
    ]

    for _, row in invalid_rows.iterrows():
        failures.append({
            "rule_id": "DQ-12",
            "severity": "WARNING",
            "table_name": "companies",
            "row_id": row["id"],
            "message": "Missing NSE/BSE profile"
        })
    return failures


def validate_year_coverage(pnl_df):
    failures = []
    counts = pnl_df.groupby("company_id").size()

    for company_id, count in counts[counts < 5].items():
        failures.append({
            "rule_id": "DQ-13",
            "severity": "WARNING",
            "table_name": "profitandloss",
            "row_id": company_id,
            "message": f"Only {count} years of data"
        })
    return failures


def validate_annual_reports(doc_df):
    failures = []
    invalid_rows = doc_df[doc_df["annual_report"].isna()]

    for _, row in invalid_rows.iterrows():
        failures.append({
            "rule_id": "DQ-14",
            "severity": "WARNING",
            "table_name": "documents",
            "row_id": row["company_id"],
            "message": "Annual report missing"
        })
    return failures


def validate_market_cap(market_df):
    failures = []
    invalid_rows = market_df[market_df["market_cap_crore"] <= 0]

    for _, row in invalid_rows.iterrows():
        failures.append({
            "rule_id": "DQ-15",
            "severity": "WARNING",
            "table_name": "market_cap",
            "row_id": f"{row['company_id']}_{row['year']}",
            "message": "Invalid market cap"
        })
    return failures


def validate_financial_ratios(ratio_df):
    failures = []
    invalid_rows = ratio_df[ratio_df["return_on_equity_pct"].isna()]

    for _, row in invalid_rows.iterrows():
        failures.append({
            "rule_id": "DQ-16",
            "severity": "WARNING",
            "table_name": "financial_ratios",
            "row_id": f"{row['company_id']}_{row['year']}",
            "message": "Missing ROE ratio"
        })
    return failures


def main():
    companies = load_excel("data/raw/companies.xlsx")
    pnl = load_excel("data/raw/profitandloss.xlsx")
    bs = load_excel("data/raw/balancesheet.xlsx")
    cf = load_excel("data/raw/cashflow.xlsx")
    documents = load_excel("data/raw/documents.xlsx")

    market_cap = normalize_columns(pd.read_excel("data/raw/market_cap.xlsx"))
    financial_ratios = normalize_columns(pd.read_excel("data/raw/financial_ratios.xlsx"))

    failures = []

    failures.extend(validate_pk_uniqueness(companies, "companies", "id"))
    failures.extend(validate_composite_pk(pnl, "profitandloss"))
    failures.extend(validate_composite_pk(bs, "balancesheet"))
    failures.extend(validate_composite_pk(cf, "cashflow"))
    failures.extend(validate_fk(pnl, companies, "profitandloss"))
    failures.extend(validate_fk(bs, companies, "balancesheet"))
    failures.extend(validate_fk(cf, companies, "cashflow"))
    failures.extend(validate_balance_sheet(bs))
    failures.extend(validate_opm(pnl))
    failures.extend(validate_positive_sales(pnl))
    failures.extend(validate_net_cash(cf))
    failures.extend(validate_tax_rate(pnl))
    failures.extend(validate_dividend_cap(pnl))
    failures.extend(validate_urls(companies))
    failures.extend(validate_eps_sign(pnl))
    failures.extend(validate_profiles(companies))
    failures.extend(validate_year_coverage(pnl))
    failures.extend(validate_annual_reports(documents))
    failures.extend(validate_market_cap(market_cap))
    failures.extend(validate_financial_ratios(financial_ratios))

    failure_df = pd.DataFrame(failures)
    failure_df.to_csv("output/validation_failures.csv", index=False)

    print("Validation complete")
    print("Total Failures:", len(failures))

    if len(failure_df) > 0:
        print("\nFailures by Rule:")
        print(failure_df.groupby("rule_id").size())


if __name__ == "__main__":
    main()