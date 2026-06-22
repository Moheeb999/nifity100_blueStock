import pandas as pd
from src.etl.normaliser import normalize_ticker, normalize_year


def load_excel(path, header=1):
    """
    Load Excel file and normalize columns.
    """

    df = pd.read_excel(path, header=header)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # Normalize ticker columns
    if "id" in df.columns:
        df["id"] = df["id"].apply(normalize_ticker)

    if "company_id" in df.columns:
        df["company_id"] = df["company_id"].apply(normalize_ticker)

    # Normalize year column
    if "year" in df.columns:
        df["year"] = df["year"].apply(normalize_year)
        df = df[df["year"].notna()]
    return df    


if __name__ == "__main__":
    companies = load_excel("data/raw/companies.xlsx")
    pnl = load_excel("data/raw/profitandloss.xlsx")
    bs = load_excel("data/raw/balancesheet.xlsx")
    cf = load_excel("data/raw/cashflow.xlsx")

    print("Companies:", companies.shape)
    print("Profit & Loss:", pnl.shape)
    print("Balance Sheet:", bs.shape)
    print("Cash Flow:", cf.shape)