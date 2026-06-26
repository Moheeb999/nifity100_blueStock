from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    roe,
    roce,
    roa,
    opm_crosscheck
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
