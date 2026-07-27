from src.etl.normaliser import normalize_year


def test_none():
    assert normalize_year(None) is None


def test_integer_year():
    assert normalize_year(2024) == 2024


def test_string_year():
    assert normalize_year("2023") == 2023


def test_year_with_spaces():
    assert normalize_year(" 2022 ") == 2022


def test_mar_24():
    assert normalize_year("Mar-24") == 2024


def test_apr_23():
    assert normalize_year("Apr-23") == 2023


def test_fy24():
    assert normalize_year("FY24") == 2024


def test_24():
    assert normalize_year("24") == 2024


def test_49():
    assert normalize_year("49") == 2049


def test_50():
    assert normalize_year("50") == 1950


def test_99():
    assert normalize_year("99") == 1999


def test_00():
    assert normalize_year("00") == 2000


def test_dec_99():
    assert normalize_year("Dec-99") == 1999


def test_invalid_text():
    assert normalize_year("Hello") is None


def test_empty_string():
    assert normalize_year("") is None


def test_spaces_only():
    assert normalize_year("   ") is None


def test_special_characters():
    assert normalize_year("@@@") is None


def test_year_with_suffix():
    assert normalize_year("FY2024") == 2024


def test_numeric_suffix():
    assert normalize_year("Year24") == 2024


def test_float_string():
    assert normalize_year("2024.0") is None
