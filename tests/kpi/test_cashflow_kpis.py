from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern
)


def test_free_cash_flow():
    assert free_cash_flow(1000, -300) == 700


def test_cfo_quality_high():
    assert cfo_quality_score(1200, 1000) == "High Quality"


def test_cfo_quality_moderate():
    assert cfo_quality_score(700, 1000) == "Moderate"


def test_cfo_quality_accrual():
    assert cfo_quality_score(300, 1000) == "Accrual Risk"


def test_cfo_quality_zero_pat():
    assert cfo_quality_score(1000, 0) is None


def test_capex_asset_light():
    assert capex_intensity(-20, 1000) == "Asset Light"


def test_capex_capital_intensive():
    assert capex_intensity(-200, 1000) == "Capital Intensive"


def test_fcf_conversion():
    assert fcf_conversion_rate(500, 1000) == 50


def test_fcf_conversion_zero_op():
    assert fcf_conversion_rate(500, 0) is None


def test_capital_pattern_reinvestor():
    assert capital_allocation_pattern(100, -50, -10) == "Reinvestor"


def test_capital_pattern_distress():
    assert capital_allocation_pattern(-100, 50, 80) == "Distress Signal"