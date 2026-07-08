import sqlite3
import pandas as pd
import yaml

from src.analytics.composite_score import compute_composite_score


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
            """
            SELECT
                company_id,
                broad_sector
            FROM sectors
            """,
            self.conn
        )

        market = pd.read_sql(
            "SELECT * FROM market_cap",
            self.conn
        )

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

        # ----------------------------
        # Merge datasets
        # ----------------------------
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

        # ----------------------------
        # Keep latest year only
        # ----------------------------
        df = df.sort_values(
            ["company_id", "year"]
        )

        df = (
            df.groupby("company_id")
            .tail(1)
            .reset_index(drop=True)
        )

        # ----------------------------
        # Compute Composite Score
        # ----------------------------
        df = compute_composite_score(df)

        return df

    def apply_preset(self, df, preset_name):

        if preset_name not in self.config["presets"]:
            raise ValueError(
                f"Unknown preset: {preset_name}"
            )

        preset = self.config["presets"].get(preset_name)

        if preset is None:
            raise ValueError(
                f"Preset '{preset_name}' is missing or empty."
            )

        # ----------------------------
        # ROE
        # ----------------------------
        if "roe_min" in preset:
            df = df[
                df["return_on_equity_pct"] >=
                preset["roe_min"]
            ]

        # ----------------------------
        # Debt to Equity
        # Financial carve-out
        # ----------------------------
        if "debt_to_equity_max" in preset:

            non_financial = (
                (df["broad_sector"] != "Financials") &
                (
                    df["debt_to_equity"] <=
                    preset["debt_to_equity_max"]
                )
            )

            financial = (
                df["broad_sector"] == "Financials"
            )

            df = df[
                non_financial | financial
            ]

        # ----------------------------
        # Free Cash Flow
        # ----------------------------
        if "free_cash_flow_min" in preset:
            df = df[
                df["free_cash_flow_cr"] >=
                preset["free_cash_flow_min"]
            ]

        # ----------------------------
        # Revenue CAGR
        # ----------------------------
        if "revenue_cagr_5yr_min" in preset:
            df = df[
                df["revenue_cagr_5yr"] >=
                preset["revenue_cagr_5yr_min"]
            ]

        # ----------------------------
        # PAT CAGR
        # ----------------------------
        if "pat_cagr_5yr_min" in preset:
            df = df[
                df["pat_cagr_5yr"] >=
                preset["pat_cagr_5yr_min"]
            ]

        # ----------------------------
        # Dividend Yield
        # ----------------------------
        if "dividend_yield_min" in preset:
            df = df[
                df["dividend_yield_pct"].isna() |
                (
                    df["dividend_yield_pct"] >=
                    preset["dividend_yield_min"]
                )
            ]

        # ----------------------------
        # PE Ratio
        # ----------------------------
        if "pe_max" in preset:
            df = df[
                df["pe_ratio"].isna() |
                (
                    df["pe_ratio"] <=
                    preset["pe_max"]
                )
            ]

        # ----------------------------
        # PB Ratio
        # ----------------------------
        if "pb_max" in preset:
            df = df[
                df["pb_ratio"].isna() |
                (
                    df["pb_ratio"] <=
                    preset["pb_max"]
                )
            ]

        # ----------------------------
        # Sales
        # ----------------------------
        if "sales_min" in preset:
            df = df[
                df["sales"] >=
                preset["sales_min"]
            ]

        # ----------------------------
        # Dividend Payout
        # ----------------------------
        if "dividend_payout_max" in preset:
            df = df[
                df["dividend_payout_ratio_pct"] <=
                preset["dividend_payout_max"]
            ]

        # ----------------------------
        # Sort by Composite Score
        # ----------------------------
        df = df.sort_values(
            by="composite_quality_score",
            ascending=False
        )

        return df


def main():

    engine = ScreenerEngine()

    df = engine.load_data()

    presets = [
        "quality_compounder",
        "value_pick",
        "growth_accelerator",
        "dividend_champion",
        "debt_free_blue_chip",
        "turnaround_watch"
    ]

    for preset in presets:

        print("=" * 70)
        print(f"Preset: {preset}")

        result = engine.apply_preset(
            df.copy(),
            preset
        )

        print(result.head())

        print("\nCompanies:", len(result))
        print("=" * 70)

    engine.conn.close()


if __name__ == "__main__":
    main()