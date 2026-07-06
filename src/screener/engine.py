import sqlite3
import pandas as pd
import yaml


class ScreenerEngine:

    def __init__(self):
        self.conn = sqlite3.connect("db/nifty100.db")

        with open("config/screener_config.yaml", "r") as f:
            self.config = yaml.safe_load(f)

    def load_data(self):

        ratios = pd.read_sql(
            "SELECT * FROM financial_ratios",
            self.conn
        )

        sectors = pd.read_sql(
            "SELECT company_id, broad_sector FROM sectors",
            self.conn
        )

        market = pd.read_sql(
            "SELECT * FROM market_cap",
            self.conn
        )

        # Load Profit & Loss for Sales and Net Profit
        pnl = pd.read_sql(
            """
            SELECT
                company_id,
                year,
                sales,
                net_profit
            FROM profitandloss
            """,
            self.conn
        )

        df = ratios.merge(
            sectors,
            on="company_id",
            how="left"
        )

        df = df.merge(
            market,
            on=["company_id", "year"],
            how="left"
        )

        df = df.merge(
            pnl,
            on=["company_id", "year"],
            how="left"
        )

        return df

    def apply_filters(self, df):

        filters = self.config["filters"]

        # ------------------------------------------------
        # ROE
        # ------------------------------------------------
        df = df[
            df["return_on_equity_pct"] >= filters["roe_min"]
        ]

        # ------------------------------------------------
        # Debt to Equity
        # Skip Financial companies
        # ------------------------------------------------
        non_financial = (
            (df["broad_sector"] != "Financials") &
            (df["debt_to_equity"] <= filters["debt_to_equity_max"])
        )

        financial = (
            df["broad_sector"] == "Financials"
        )

        df = df[
            non_financial | financial
        ]

        # ------------------------------------------------
        # Free Cash Flow
        # ------------------------------------------------
        df = df[
            df["free_cash_flow_cr"] >= filters["free_cash_flow_min"]
        ]

        # ------------------------------------------------
        # Revenue CAGR
        # ------------------------------------------------
        df = df[
            df["revenue_cagr_5yr"] >= filters["revenue_cagr_5yr_min"]
        ]

        # ------------------------------------------------
        # PAT CAGR
        # ------------------------------------------------
        df = df[
            df["pat_cagr_5yr"] >= filters["pat_cagr_5yr_min"]
        ]

        # ------------------------------------------------
        # Operating Profit Margin
        # ------------------------------------------------
        df = df[
            df["operating_profit_margin_pct"] >=
            filters["operating_profit_margin_min"]
        ]

        # ------------------------------------------------
        # Interest Coverage
        # Debt-free (NULL) automatically passes
        # ------------------------------------------------
        df = df[
            df["interest_coverage"].isna() |
            (
                df["interest_coverage"] >=
                filters["interest_coverage_min"]
            )
        ]

        # ------------------------------------------------
        # Asset Turnover
        # ------------------------------------------------
        df = df[
            df["asset_turnover"] >=
            filters["asset_turnover_min"]
        ]

        # ------------------------------------------------
        # EPS CAGR
        # ------------------------------------------------
        df = df[
            df["eps_cagr_5yr"] >=
            filters["eps_cagr_min"]
        ]

        # ------------------------------------------------
        # Sales
        # ------------------------------------------------
        df = df[
            df["sales"] >=
            filters["sales_min"]
        ]

        # ------------------------------------------------
        # Net Profit
        # ------------------------------------------------
        df = df[
            df["net_profit"] >=
            filters["net_profit_min"]
        ]

        # ------------------------------------------------
        # Market Cap
        # Apply only where data exists
        # ------------------------------------------------
        df = df[
            df["market_cap_crore"].isna() |
            (
                df["market_cap_crore"] >=
                filters["market_cap_min"]
            )
        ]

        # ------------------------------------------------
        # PE Ratio
        # ------------------------------------------------
        df = df[
            df["pe_ratio"].isna() |
            (
                df["pe_ratio"] <=
                filters["pe_max"]
            )
        ]

        # ------------------------------------------------
        # PB Ratio
        # ------------------------------------------------
        df = df[
            df["pb_ratio"].isna() |
            (
                df["pb_ratio"] <=
                filters["pb_max"]
            )
        ]

        # ------------------------------------------------
        # Dividend Yield
        # ------------------------------------------------
        df = df[
            df["dividend_yield_pct"].isna() |
            (
                df["dividend_yield_pct"] >=
                filters["dividend_yield_min"]
            )
        ]

        # Sort by quality score
        df = df.sort_values(
            by="composite_quality_score",
            ascending=False
        )

        return df


def main():

    engine = ScreenerEngine()

    df = engine.load_data()

    filtered = engine.apply_filters(df)

    print(filtered.head())

    print("\nFiltered Rows:", len(filtered))


if __name__ == "__main__":
    main()