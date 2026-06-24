import sqlite3
import pandas as pd
from src.etl.loader import load_excel


def load_data():
    conn = sqlite3.connect("db/nifty100.db")
    conn.execute("PRAGMA foreign_keys = ON;")

    # Core files (header=1)
    companies = load_excel("data/raw/companies.xlsx")
    pnl = load_excel("data/raw/profitandloss.xlsx")
    bs = load_excel("data/raw/balancesheet.xlsx")
    cf = load_excel("data/raw/cashflow.xlsx")
    analysis = load_excel("data/raw/analysis.xlsx")
    documents = load_excel("data/raw/documents.xlsx")
    proscons = load_excel("data/raw/prosandcons.xlsx")

    # Remove duplicate company-year rows
    pnl = pnl.drop_duplicates(subset=["company_id", "year"])
    bs = bs.drop_duplicates(subset=["company_id", "year"])
    cf = cf.drop_duplicates(subset=["company_id", "year"])

    print("Rows after dedupe:")
    print("P&L:", len(pnl))
    print("Balance Sheet:", len(bs))
    print("Cash Flow:", len(cf))

    # Supporting files (header=0)
    stock_prices = pd.read_excel("data/raw/stock_prices.xlsx", header=0)
    sectors = pd.read_excel("data/raw/sectors.xlsx", header=0)
    peer_groups = pd.read_excel("data/raw/peer_groups.xlsx", header=0)
    market_cap = pd.read_excel("data/raw/market_cap.xlsx", header=0)
    financial_ratios = pd.read_excel("data/raw/financial_ratios.xlsx", header=0)

    # Insert companies first
    companies.to_sql("companies", conn, if_exists="append", index=False)

    valid_ids = set(companies["id"])

    # FK-safe filtering
    pnl = pnl[pnl["company_id"].isin(valid_ids)]
    bs = bs[bs["company_id"].isin(valid_ids)]
    cf = cf[cf["company_id"].isin(valid_ids)]
    analysis = analysis[analysis["company_id"].isin(valid_ids)]
    documents = documents[documents["company_id"].isin(valid_ids)]
    proscons = proscons[proscons["company_id"].isin(valid_ids)]
    stock_prices = stock_prices[stock_prices["company_id"].isin(valid_ids)]
    sectors = sectors[sectors["company_id"].isin(valid_ids)]
    peer_groups = peer_groups[peer_groups["company_id"].isin(valid_ids)]
    market_cap = market_cap[market_cap["company_id"].isin(valid_ids)]
    financial_ratios = financial_ratios[financial_ratios["company_id"].isin(valid_ids)]

    # Insert tables
    pnl.to_sql("profitandloss", conn, if_exists="append", index=False)
    bs.to_sql("balancesheet", conn, if_exists="append", index=False)
    cf.to_sql("cashflow", conn, if_exists="append", index=False)
    analysis.to_sql("analysis", conn, if_exists="append", index=False)
    documents.to_sql("documents", conn, if_exists="append", index=False)
    proscons.to_sql("prosandcons", conn, if_exists="append", index=False)
    stock_prices.to_sql("stock_prices", conn, if_exists="append", index=False)
    sectors.to_sql("sectors", conn, if_exists="append", index=False)
    peer_groups.to_sql("peer_groups", conn, if_exists="append", index=False)
    market_cap.to_sql("market_cap", conn, if_exists="append", index=False)
    financial_ratios.to_sql("financial_ratios", conn, if_exists="append", index=False)

    print("All 12 datasets loaded successfully")

    conn.close()


if __name__ == "__main__":
    load_data()