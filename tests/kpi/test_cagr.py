from src.analytics.cagr import calculate_cagr


def test_cagr_normal():
    cagr, flag = calculate_cagr(100, 200, 5)
    assert round(cagr, 2) == 14.87
    assert flag is None


def test_decline_to_loss():
    cagr, flag = calculate_cagr(100, -50, 5)
    assert cagr is None
    assert flag == "DECLINE_TO_LOSS"


def test_turnaround():
    cagr, flag = calculate_cagr(-100, 50, 5)
    assert cagr is None
    assert flag == "TURNAROUND"


def test_both_negative():
    cagr, flag = calculate_cagr(-100, -50, 5)
    assert cagr is None
    assert flag == "BOTH_NEGATIVE"


def test_zero_base():
    cagr, flag = calculate_cagr(0, 100, 5)
    assert cagr is None
    assert flag == "ZERO_BASE"


def test_insufficient_years():
    cagr, flag = calculate_cagr(100, 200, 0)
    assert cagr is None
    assert flag == "INSUFFICIENT"


def test_growth_3yr():
    cagr, flag = calculate_cagr(100, 150, 3)
    assert flag is None


def test_growth_5yr():
    cagr, flag = calculate_cagr(100, 180, 5)
    assert flag is None


def test_growth_10yr():
    cagr, flag = calculate_cagr(100, 300, 10)
    assert flag is None


def test_same_values():
    cagr, flag = calculate_cagr(100, 100, 5)
    assert round(cagr, 2) == 0