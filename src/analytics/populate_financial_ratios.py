import sqlite3

import pandas as pd

from src.analytics.cagr import eps_cagr, pat_cagr, revenue_cagr
from src.analytics.cashflow_kpis import free_cash_flow
from src.analytics.ratios import (
    asset_turnover,
    debt_to_equity,
    interest_coverage_ratio,
    net_profit_margin,
    operating_profit_margin,
    roe,
)


def composite_quality_score(roe_value, npm, de, revenue_cagr_value):
    """Calculate a rule-based composite quality score."""
    score = 0

    # ROE (30 points)
    if roe_value is not None:
        if roe_value > 20:
            score += 30
        elif roe_value >= 10:
            score += 20
        else:
            score += 10

    # Net Profit Margin (25 points)
    if npm is not None:
        if npm > 15:
            score += 25
        elif npm >= 5:
            score += 15
        else:
            score += 5

    # Debt-to-Equity (20 points)
    if de is not None:
        if de < 1:
            score += 20
        elif de <= 2:
            score += 10

    # Revenue CAGR (25 points)
    if revenue_cagr_value is not None:
        if revenue_cagr_value > 15:
            score += 25
        elif revenue_cagr_value >= 5:
            score += 15
        else:
            score += 5

    return score


def main():
    """Populate the financial_ratios table with calculated metrics."""
    conn = sqlite3.connect("db/nifty100.db")

    pnl = pd.read_sql("SELECT * FROM profitandloss", conn)
    bs = pd.read_sql("SELECT * FROM balancesheet", conn)
    cf = pd.read_sql("SELECT * FROM cashflow", conn)

    merged = pnl.merge(bs, on=["company_id", "year"], suffixes=("_pnl", "_bs")).merge(
        cf, on=["company_id", "year"]
    )

    rows = []

    for _, row in merged.iterrows():

        npm = net_profit_margin(row["net_profit"], row["sales"])

        opm = operating_profit_margin(row["operating_profit"], row["sales"])

        roe_value = roe(row["net_profit"], row["equity_capital"], row["reserves"])

        de = debt_to_equity(row["borrowings"], row["equity_capital"], row["reserves"])

        icr = interest_coverage_ratio(
            row["operating_profit"], row["other_income"], row["interest"]
        )

        turnover = asset_turnover(row["sales"], row["total_assets"])

        fcf = free_cash_flow(row["operating_activity"], row["investing_activity"])

        capex = abs(row["investing_activity"])

        # CAGR calculations
        company_history = merged[merged["company_id"] == row["company_id"]].sort_values(
            "year"
        )

        revenue_cagr_5yr = None
        pat_cagr_5yr_value = None
        eps_cagr_5yr_value = None

        current_year = row["year"]

        past_data = company_history[company_history["year"] == current_year - 5]

        if not past_data.empty:
            past_row = past_data.iloc[0]

            revenue_cagr_5yr, _ = revenue_cagr(past_row["sales"], row["sales"], 5)

            pat_cagr_5yr_value, _ = pat_cagr(
                past_row["net_profit"], row["net_profit"], 5
            )

            eps_cagr_5yr_value, _ = eps_cagr(past_row["eps"], row["eps"], 5)

        quality_score = composite_quality_score(roe_value, npm, de, revenue_cagr_5yr)

        rows.append(
            {
                "company_id": row["company_id"],
                "year": row["year"],
                "net_profit_margin_pct": npm,
                "operating_profit_margin_pct": opm,
                "return_on_equity_pct": roe_value,
                "debt_to_equity": de,
                "interest_coverage": icr,
                "asset_turnover": turnover,
                "free_cash_flow_cr": fcf,
                "capex_cr": capex,
                "earnings_per_share": row["eps"],
                "book_value_per_share": None,
                "dividend_payout_ratio_pct": row["dividend_payout"],
                "total_debt_cr": row["borrowings"],
                "cash_from_operations_cr": row["operating_activity"],
                "revenue_cagr_5yr": revenue_cagr_5yr,
                "pat_cagr_5yr": pat_cagr_5yr_value,
                "eps_cagr_5yr": eps_cagr_5yr_value,
                "composite_quality_score": quality_score,
            }
        )

    ratio_df = pd.DataFrame(rows)

    # Clear existing rows but preserve schema
    conn.execute("DELETE FROM financial_ratios")
    conn.commit()

    ratio_df.to_sql("financial_ratios", conn, if_exists="append", index=False)

    print("financial_ratios populated")
    print("Rows:", len(ratio_df))

    conn.close()


if __name__ == "__main__":
    main()
