import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"


class DashboardQATest:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

        self.total = 0
        self.passed = 0
        self.failed = []

    def check_company(self, ticker):

        # ----------------------------
        # Company Profile
        # ----------------------------

        company = pd.read_sql(
            """
            SELECT *
            FROM companies
            WHERE id = ?
            """,
            self.conn,
            params=[ticker]
        )

        if company.empty:
            raise Exception("Company profile missing")

        # ----------------------------
        # Financial Ratios
        # ----------------------------

        ratios = pd.read_sql(
            """
            SELECT *
            FROM financial_ratios
            WHERE company_id = ?
            ORDER BY year DESC
            LIMIT 1
            """,
            self.conn,
            params=[ticker]
        )

        if ratios.empty:
            raise Exception("Financial ratios missing")

        # ----------------------------
        # Profit & Loss
        # ----------------------------

        pl = pd.read_sql(
            """
            SELECT *
            FROM profitandloss
            WHERE company_id = ?
            """,
            self.conn,
            params=[ticker]
        )

        if pl.empty:
            raise Exception("Profit & Loss missing")

        # ----------------------------
        # Balance Sheet
        # ----------------------------

        bs = pd.read_sql(
            """
            SELECT *
            FROM balancesheet
            WHERE company_id = ?
            """,
            self.conn,
            params=[ticker]
        )

        if bs.empty:
            print(f"⚠ {ticker}: Balance Sheet missing")

        # ----------------------------
        # Cash Flow
        # ----------------------------

        cf = pd.read_sql(
            """
            SELECT *
            FROM cashflow
            WHERE company_id = ?
            """,
            self.conn,
            params=[ticker]
        )

        if cf.empty:
            print(f"⚠ {ticker}: Cash Flow missing")

        # ----------------------------
        # Sector
        # ----------------------------

        sector = pd.read_sql(
            """
            SELECT *
            FROM sectors
            WHERE company_id = ?
            """,
            self.conn,
            params=[ticker]
        )

        if sector.empty:
            print(f"⚠ {ticker}: Sector missing")

        # ----------------------------
        # Peer Group
        # ----------------------------

        peer = pd.read_sql(
            """
            SELECT *
            FROM peer_groups
            WHERE company_id = ?
            """,
            self.conn,
            params=[ticker]
        )

        if peer.empty:
            print(f"⚠ {ticker}: Peer group missing")

        # ----------------------------
        # Market Cap
        # ----------------------------

        market = pd.read_sql(
            """
            SELECT *
            FROM market_cap
            WHERE company_id = ?
            """,
            self.conn,
            params=[ticker]
        )

        if market.empty:
            print(f"⚠ {ticker}: Market Cap missing")

        # ----------------------------
        # Pros & Cons
        # ----------------------------

        try:

            pc = pd.read_sql(
                """
                SELECT *
                FROM prosandcons
                WHERE company_id = ?
                """,
                self.conn,
                params=[ticker]
            )

            if pc.empty:
                print(f"⚠ {ticker}: Pros & Cons missing")

        except Exception:

            print("⚠ prosandcons table not found")

    def run(self):

        companies = pd.read_sql(
            """
            SELECT
                id,
                company_name
            FROM companies
            ORDER BY company_name
            """,
            self.conn
        )

        self.total = len(companies)

        print("\n" + "=" * 70)
        print("NIFTY 100 DASHBOARD QA")
        print("=" * 70)

        for _, row in companies.iterrows():

            ticker = row["id"]

            try:

                self.check_company(ticker)

                self.passed += 1

            except Exception as e:

                self.failed.append(
                    (
                        ticker,
                        str(e)
                    )
                )

        print("\n" + "=" * 70)
        print("QA SUMMARY")
        print("=" * 70)

        print(f"Total Companies : {self.total}")
        print(f"Passed          : {self.passed}")
        print(f"Failed          : {len(self.failed)}")

        if self.failed:

            print("\nFAILED COMPANIES\n")

            for ticker, error in self.failed:

                print(
                    f"{ticker:<15} {error}"
                )

        else:

            print("\n🎉 All companies passed QA.")

        print("=" * 70)

        self.conn.close()


def main():

    DashboardQATest().run()


if __name__ == "__main__":

    main()