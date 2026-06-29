from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    roe,
    roce,
    roa,
    opm_crosscheck,
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    icr_label,
    icr_warning,
    net_debt,
    asset_turnover
)

def test_net_profit_margin_normal():
    assert net_profit_margin(100, 1000) == 10


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(100, 0) is None


def test_operating_profit_margin_normal():
    assert operating_profit_margin(250, 1000) == 25


def test_operating_profit_margin_zero_sales():
    assert operating_profit_margin(100, 0) is None


def test_roe_normal():
    assert roe(100, 200, 300) == 20


def test_roe_negative_equity():
    assert roe(100, -500, 100) is None


def test_roce_normal():
    result = roce(100, 200, 300, 500)
    assert round(result, 2) == 10.0


def test_roa_zero_assets():
    assert roa(100, 0) is None


def test_opm_crosscheck_match():
    assert opm_crosscheck(25.2, 25.5) is False


def test_opm_crosscheck_mismatch():
    assert opm_crosscheck(25.0, 27.5) is True

def test_debt_to_equity_normal():
    assert debt_to_equity(500, 200, 300) == 1


def test_debt_to_equity_debt_free():
    assert debt_to_equity(0, 200, 300) == 0


def test_debt_to_equity_negative_equity():
    assert debt_to_equity(500, -600, 50) is None


def test_high_leverage_flag():
    assert high_leverage_flag(6) is True


def test_interest_coverage_normal():
    assert interest_coverage_ratio(1000, 200, 100) == 12


def test_interest_coverage_debt_free():
    assert interest_coverage_ratio(1000, 100, 0) is None


def test_icr_label():
    assert icr_label(None) == "Debt Free"


def test_asset_turnover_zero_assets():
    assert asset_turnover(1000, 0) is None

def test_icr_warning_true():
    assert icr_warning(1.2) is True


def test_icr_warning_false():
    assert icr_warning(3.5) is False    