import pandas as pd

from src.etl.validator import (
    validate_pk_uniqueness,
    validate_composite_pk,
    validate_fk,
    validate_balance_sheet,
    validate_opm,
    validate_positive_sales,
    validate_net_cash,
    validate_tax_rate,
    validate_dividend_cap,
    validate_urls,
    validate_eps_sign,
    validate_profiles,
    validate_year_coverage,
    validate_annual_reports,
    validate_market_cap,
    validate_financial_ratios,
)


def test_validate_pk_uniqueness():
    df = pd.DataFrame({"id": ["TCS", "TCS"]})

    failures = validate_pk_uniqueness(df, "companies", "id")

    assert len(failures) == 2
    assert failures[0]["rule_id"] == "DQ-01"
    assert failures[0]["severity"] == "CRITICAL"


def test_validate_composite_pk():
    df = pd.DataFrame({
        "company_id": ["TCS", "TCS"],
        "year": [2024, 2024]
    })

    failures = validate_composite_pk(df, "profitandloss")

    assert len(failures) == 2
    assert failures[0]["rule_id"] == "DQ-02"
    assert failures[0]["severity"] == "CRITICAL"


def test_validate_fk():
    companies = pd.DataFrame({"id": ["TCS"]})

    pnl = pd.DataFrame({
        "company_id": ["INFY"]
    })

    failures = validate_fk(pnl, companies, "profitandloss")

    assert len(failures) == 1
    assert failures[0]["rule_id"] == "DQ-03"


def test_validate_balance_sheet():
    df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": [2024],
        "total_assets": [100],
        "total_liabilities": [90]
    })

    failures = validate_balance_sheet(df)

    assert len(failures) == 1
    assert failures[0]["rule_id"] == "DQ-04"


def test_validate_opm():
    df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": [2024],
        "operating_profit": [20],
        "sales": [100],
        "opm_percentage": [10]
    })

    failures = validate_opm(df)

    assert len(failures) == 1
    assert failures[0]["rule_id"] == "DQ-05"


def test_validate_positive_sales():
    df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": [2024],
        "sales": [-100]
    })

    failures = validate_positive_sales(df)

    assert len(failures) == 1
    assert failures[0]["rule_id"] == "DQ-06"


def test_validate_net_cash():
    df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": [2024],
        "operating_activity": [100],
        "investing_activity": [-20],
        "financing_activity": [-30],
        "net_cash_flow": [100]
    })

    failures = validate_net_cash(df)

    assert len(failures) == 1
    assert failures[0]["rule_id"] == "DQ-07"


def test_validate_tax_rate():
    df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": [2024],
        "tax_percentage": [120]
    })

    failures = validate_tax_rate(df)

    assert len(failures) == 1
    assert failures[0]["rule_id"] == "DQ-08"


def test_validate_dividend_cap():
    df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": [2024],
        "dividend_payout": [150]
    })

    failures = validate_dividend_cap(df)

    assert len(failures) == 1
    assert failures[0]["rule_id"] == "DQ-09"


def test_validate_urls():
    df = pd.DataFrame({
        "id": ["TCS"],
        "website": ["invalid"],
        "nse_profile": ["invalid"],
        "bse_profile": ["invalid"]
    })

    failures = validate_urls(df)

    assert len(failures) == 3
    assert failures[0]["rule_id"] == "DQ-10"


def test_validate_eps_sign():
    df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": [2024],
        "net_profit": [-100],
        "eps": [10]
    })

    failures = validate_eps_sign(df)

    assert len(failures) == 1
    assert failures[0]["rule_id"] == "DQ-11"


def test_validate_profiles():
    df = pd.DataFrame({
        "id": ["TCS"],
        "nse_profile": [None],
        "bse_profile": ["https://bse.com"]
    })

    failures = validate_profiles(df)

    assert len(failures) == 1
    assert failures[0]["rule_id"] == "DQ-12"


def test_validate_year_coverage():
    df = pd.DataFrame({
        "company_id": ["TCS"] * 4,
        "year": [2021, 2022, 2023, 2024]
    })

    failures = validate_year_coverage(df)

    assert len(failures) == 1
    assert failures[0]["rule_id"] == "DQ-13"


def test_validate_annual_reports():
    df = pd.DataFrame({
        "company_id": ["TCS"],
        "annual_report": [None]
    })

    failures = validate_annual_reports(df)

    assert len(failures) == 1
    assert failures[0]["rule_id"] == "DQ-14"


def test_validate_market_cap():
    df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": [2024],
        "market_cap_crore": [0]
    })

    failures = validate_market_cap(df)

    assert len(failures) == 1
    assert failures[0]["rule_id"] == "DQ-15"


def test_validate_financial_ratios():
    df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": [2024],
        "return_on_equity_pct": [None]
    })

    failures = validate_financial_ratios(df)

    assert len(failures) == 1
    assert failures[0]["rule_id"] == "DQ-16"