from src.etl.normaliser import normalize_year


def test_mar_24():
    assert normalize_year("Mar-24") == 2024

def test_mar_23():
    assert normalize_year("Mar-23") == 2023

def test_string_2024():
    assert normalize_year("2024") == 2024

def test_int_2022():
    assert normalize_year(2022) == 2022

def test_spaces():
    assert normalize_year(" 2021 ") == 2021

def test_fy20():
    assert normalize_year("FY20") == 2020

def test_fy49():
    assert normalize_year("FY49") == 2049

def test_fy99():
    assert normalize_year("FY99") == 1999

def test_none():
    assert normalize_year(None) is None

def test_empty():
    assert normalize_year("") is None

def test_year_2000():
    assert normalize_year("Mar-00") == 2000


def test_year_1999():
    assert normalize_year("Mar-99") == 1999


def test_fy01():
    assert normalize_year("FY01") == 2001


def test_fy50():
    assert normalize_year("FY50") == 1950


def test_invalid_string():
    assert normalize_year("abcd") is None


def test_special_chars():
    assert normalize_year("@@@") is None


def test_spaces_only():
    assert normalize_year("   ") is None


def test_numeric_float_string():
    assert normalize_year("2022") == 2022


def test_short_year():
    assert normalize_year("24") == 2024


def test_random_text():
    assert normalize_year("Revenue2024") == 2024