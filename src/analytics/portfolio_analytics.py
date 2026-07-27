import sqlite3
from collections import defaultdict
from pathlib import Path

from .portfolio_loader import PortfolioLoader


class PortfolioAnalytics:
    """Perform portfolio analysis using market and financial data."""

    def __init__(self, db_path: str):
        """Initialize the portfolio analytics engine."""
        self.conn = sqlite3.connect(Path(db_path))
        self.conn.row_factory = sqlite3.Row

    def get_company_data(self, ticker: str):
        """Retrieve the latest financial data for a company."""

        query = """
    SELECT

        c.id,
        c.company_name,

        sp.close_price,

        m.market_cap_crore,
        m.pe_ratio,
        m.pb_ratio,
        m.ev_ebitda,
        m.dividend_yield_pct,

        fr.return_on_equity_pct,
        fr.return_on_capital_employed_pct,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        fr.eps_cagr_5yr,
        fr.composite_quality_score,

        s.broad_sector,
        s.sub_sector,
        s.market_cap_category

    FROM companies c

    LEFT JOIN stock_prices sp
        ON sp.company_id = c.id
       AND sp.date = (
            SELECT MAX(date)
            FROM stock_prices
            WHERE company_id = c.id
       )

    LEFT JOIN market_cap m
        ON m.company_id = c.id
       AND m.year = (
            SELECT MAX(year)
            FROM market_cap
            WHERE company_id = c.id
       )

    LEFT JOIN financial_ratios fr
        ON fr.company_id = c.id
       AND fr.year = (
            SELECT MAX(year)
            FROM financial_ratios
            WHERE company_id = c.id
       )

    LEFT JOIN sectors s
        ON s.company_id = c.id

    WHERE c.id = ?
    """

        return self.conn.execute(query, (ticker,)).fetchone()

    def load_portfolio(self, csv_path: str):
        """Load and enrich portfolio holdings."""

        loader = PortfolioLoader(csv_path)

        holdings = loader.load()

        portfolio = []

        for holding in holdings:

            company = self.get_company_data(holding.ticker)

            if company is None:
                print(f"Warning: {holding.ticker} not found.")
                continue

            portfolio.append(
                {
                    "holding": holding,
                    "company": dict(company),
                }
            )

        return portfolio

    def calculate_portfolio_cost(self, portfolio):
        """Calculate the total acquisition cost."""

        total_cost = 0.0

        for stock in portfolio:

            holding = stock["holding"]

            total_cost += holding.shares * holding.buy_price

        return round(total_cost, 2)

    def calculate_current_value(self, portfolio):
        """Calculate the current market value."""

        total_value = 0.0

        for stock in portfolio:

            holding = stock["holding"]
            company = stock["company"]

            current_price = company["close_price"]

            total_value += holding.shares * current_price

        return round(total_value, 2)

    def calculate_profit_loss(self, portfolio):
        """Calculate the unrealized profit or loss."""

        total_cost = self.calculate_portfolio_cost(portfolio)
        current_value = self.calculate_current_value(portfolio)

        profit_loss = current_value - total_cost

        return round(profit_loss, 2)

    def calculate_return_percentage(self, portfolio):
        """Calculate the overall portfolio return percentage."""

        total_cost = self.calculate_portfolio_cost(portfolio)

        if total_cost == 0:
            return 0.0

        profit_loss = self.calculate_profit_loss(portfolio)

        return round((profit_loss / total_cost) * 100, 2)

    def calculate_sector_allocation(self, portfolio):
        """Calculate portfolio allocation by sector."""

        sector_values = defaultdict(float)
        total_value = self.calculate_current_value(portfolio)

        if total_value == 0:
            return {}

        for stock in portfolio:

            holding = stock["holding"]
            company = stock["company"]

            sector = company["broad_sector"] or "Unknown"

            current_value = holding.shares * company["close_price"]

            sector_values[sector] += current_value

        allocation = {}

        for sector, value in sector_values.items():
            allocation[sector] = round((value / total_value) * 100, 2)

        return dict(sorted(allocation.items(), key=lambda x: x[1], reverse=True))

    def calculate_weighted_quality_score(self, portfolio):
        """Calculate the weighted composite quality score."""

        return self.calculate_weighted_metric(
            portfolio,
            "composite_quality_score",
        )

    def calculate_weighted_pe_ratio(self, portfolio):
        """Calculate the weighted P/E ratio."""

        return self.calculate_weighted_metric(
            portfolio,
            "pe_ratio",
        )

    def calculate_weighted_pb_ratio(self, portfolio):
        """Calculate the weighted P/B ratio."""

        return self.calculate_weighted_metric(
            portfolio,
            "pb_ratio",
        )

    def calculate_weighted_roe(self, portfolio):
        """Calculate the weighted return on equity."""

        return self.calculate_weighted_metric(
            portfolio,
            "return_on_equity_pct",
        )

    def calculate_diversification_score(self, portfolio):
        """Calculate a diversification score based on sector count."""

        sector_allocation = self.calculate_sector_allocation(portfolio)

        sector_count = len(sector_allocation)

        if sector_count >= 8:
            return 100
        elif sector_count >= 6:
            return 85
        elif sector_count >= 4:
            return 70
        elif sector_count >= 3:
            return 55
        elif sector_count >= 2:
            return 40
        else:
            return 20

    def calculate_concentration_risk(self, portfolio):
        """Classify concentration risk based on the largest sector weight."""

        sector_allocation = self.calculate_sector_allocation(portfolio)

        largest_sector = max(sector_allocation.values())

        if largest_sector >= 60:
            return "High"
        elif largest_sector >= 40:
            return "Medium"
        else:
            return "Low"

    def calculate_portfolio_health_score(self, portfolio):
        """Calculate an overall portfolio health score."""

        quality = self.calculate_weighted_quality_score(portfolio)
        diversification = self.calculate_diversification_score(portfolio)

        health = quality * 0.7 + diversification * 0.3

        return round(health, 2)

    def calculate_weighted_metric(self, portfolio, metric_name):
        """Calculate a value-weighted average for the given metric."""

        total_value = self.calculate_current_value(portfolio)

        if total_value == 0:
            return 0.0

        weighted_value = 0.0

        for stock in portfolio:

            holding = stock["holding"]
            company = stock["company"]

            metric = company.get(metric_name)

            if metric is None:
                continue

            current_value = holding.shares * company["close_price"]
            weight = current_value / total_value

            weighted_value += metric * weight

        return round(weighted_value, 2)


if __name__ == "__main__":

    analytics = PortfolioAnalytics("db/nifty100.db")

    portfolio = analytics.load_portfolio("data/raw/sample_portfolio.csv")

    total_cost = analytics.calculate_portfolio_cost(portfolio)
    current_value = analytics.calculate_current_value(portfolio)
    profit_loss = analytics.calculate_profit_loss(portfolio)
    return_pct = analytics.calculate_return_percentage(portfolio)
    sector_allocation = analytics.calculate_sector_allocation(portfolio)
    quality_score = analytics.calculate_weighted_quality_score(portfolio)

    weighted_pe = analytics.calculate_weighted_pe_ratio(portfolio)
    weighted_pb = analytics.calculate_weighted_pb_ratio(portfolio)
    weighted_roe = analytics.calculate_weighted_roe(portfolio)

    diversification = analytics.calculate_diversification_score(portfolio)
    risk = analytics.calculate_concentration_risk(portfolio)
    health = analytics.calculate_portfolio_health_score(portfolio)

    print(f"Portfolio Cost          : ₹{total_cost:,.2f}")
    print(f"Current Portfolio Value : ₹{current_value:,.2f}")
    print(f"Profit / Loss           : ₹{profit_loss:,.2f}")
    print(f"Return                  : {return_pct:.2f}%")

    print("\nSector Allocation")
    for sector, pct in sector_allocation.items():
        print(f"{sector:<25} {pct:>6}%")

    print(f"\nPortfolio Quality Score : {quality_score}/100")
    print(f"Weighted PE Ratio       : {weighted_pe}")
    print(f"Weighted PB Ratio       : {weighted_pb}")
    print(f"Weighted ROE            : {weighted_roe:.2f}%")

    print(f"\nDiversification Score   : {diversification}/100")
    print(f"Concentration Risk      : {risk}")
    print(f"Portfolio Health Score  : {health}/100")
