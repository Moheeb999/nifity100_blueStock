from src.etl.normaliser import normalize_ticker


def test_tcs():
    assert normalize_ticker("tcs") == "TCS"

def test_spaces():
    assert normalize_ticker(" tcs ") == "TCS"

def test_ns():
    assert normalize_ticker("hdfcbank.ns") == "HDFCBANK"

def test_bo():
    assert normalize_ticker("reliance.bo") == "RELIANCE"

def test_upper():
    assert normalize_ticker("INFY") == "INFY"

def test_none():
    assert normalize_ticker(None) is None

def test_lowercase():
    assert normalize_ticker("reliance") == "RELIANCE"


def test_mixed_case():
    assert normalize_ticker("InFy") == "INFY"


def test_ticker_ns_lower():
    assert normalize_ticker("tcs.ns") == "TCS"


def test_ticker_bo_lower():
    assert normalize_ticker("infy.bo") == "INFY"


def test_empty_string():
    assert normalize_ticker("") == ""


def test_spaces_only():
    assert normalize_ticker("   ") == ""


def test_with_tabs():
    assert normalize_ticker("\ttcs\t") == "TCS"


def test_number_ticker():
    assert normalize_ticker("123") == "123"


def test_special_char():
    assert normalize_ticker("abc@") == "ABC@"