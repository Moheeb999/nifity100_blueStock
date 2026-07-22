from dataclasses import dataclass


@dataclass
class PortfolioHolding:
    """
    Represents a single holding in the portfolio.
    """

    ticker: str
    shares: int
    buy_price: float