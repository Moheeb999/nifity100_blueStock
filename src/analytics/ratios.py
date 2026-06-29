def net_profit_margin(net_profit, sales):
    """
    Net Profit Margin = net_profit / sales * 100
    Return None if sales == 0
    """
    if sales == 0:
        return None
    return (net_profit / sales) * 100


def operating_profit_margin(operating_profit, sales):
    """
    Operating Profit Margin = operating_profit / sales * 100
    Return None if sales == 0
    """
    if sales == 0:
        return None
    return (operating_profit / sales) * 100


def roe(net_profit, equity_capital, reserves):
    """
    Return on Equity
    Return None if equity <= 0
    """
    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return (net_profit / equity) * 100


def roce(ebit, equity_capital, reserves, borrowings):
    """
    Return on Capital Employed
    Return None if capital employed <= 0
    """
    capital_employed = equity_capital + reserves + borrowings

    if capital_employed <= 0:
        return None

    return (ebit / capital_employed) * 100


def roa(net_profit, total_assets):
    """
    Return on Assets
    Return None if total_assets == 0
    """
    if total_assets == 0:
        return None

    return (net_profit / total_assets) * 100

def opm_crosscheck(computed_opm, stored_opm):
    """
    Return True if OPM mismatch > 1%
    """
    if computed_opm is None or stored_opm is None:
        return False

    return abs(computed_opm - stored_opm) > 1

def debt_to_equity(borrowings, equity_capital, reserves):
    if borrowings == 0:
        return 0

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return borrowings / equity


def high_leverage_flag(de_ratio, is_financial=False):
    if is_financial:
        return False

    if de_ratio is None:
        return False

    return de_ratio > 5


def interest_coverage_ratio(operating_profit, other_income, interest):
    if interest == 0:
        return None

    return (operating_profit + other_income) / interest


def icr_label(icr):
    if icr is None:
        return "Debt Free"
    return "Normal"


def icr_warning(icr):
    if icr is None:
        return False
    return icr < 1.5


def net_debt(borrowings, investments):
    return borrowings - investments


def asset_turnover(sales, total_assets):
    if total_assets == 0:
        return None
    return sales / total_assets