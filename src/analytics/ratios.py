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