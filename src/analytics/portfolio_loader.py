from pathlib import Path

import pandas as pd

from .portfolio import PortfolioHolding


class PortfolioLoader:
    """
    Loads and validates a portfolio CSV.
    """

    REQUIRED_COLUMNS = {"ticker", "shares", "buy_price"}

    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)

    def load(self) -> list[PortfolioHolding]:
        """
        Load portfolio holdings from CSV.
        """

        if not self.csv_path.exists():
            raise FileNotFoundError(f"Portfolio file not found: {self.csv_path}")

        df = pd.read_csv(self.csv_path)

        # Validate required columns
        missing = self.REQUIRED_COLUMNS - set(df.columns)

        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        holdings = []

        for _, row in df.iterrows():

            ticker = str(row["ticker"]).strip().upper()
            shares = int(row["shares"])
            buy_price = float(row["buy_price"])

            if shares <= 0:
                raise ValueError(f"{ticker}: Shares must be greater than zero.")

            if buy_price <= 0:
                raise ValueError(f"{ticker}: Buy price must be greater than zero.")

            holdings.append(
                PortfolioHolding(
                    ticker=ticker,
                    shares=shares,
                    buy_price=buy_price,
                )
            )

        return holdings


if __name__ == "__main__":

    loader = PortfolioLoader("data/raw/sample_portfolio.csv")

    holdings = loader.load()

    print("\nPortfolio Loaded Successfully\n")

    for holding in holdings:
        print(holding)
