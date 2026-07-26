import pandas as pd
import pytest

from src.etl.loader import load_excel


def test_returns_dataframe(tmp_path):
    df = pd.DataFrame({"id": ["TCS"], "year": [2024]})
    file = tmp_path / "sample.xlsx"
    df.to_excel(file, index=False)

    result = load_excel(file, header=0)

    assert isinstance(result, pd.DataFrame)


def test_row_count(tmp_path):
    df = pd.DataFrame({"id": ["TCS", "INFY"], "year": [2024, 2023]})
    file = tmp_path / "sample.xlsx"
    df.to_excel(file, index=False)

    result = load_excel(file, header=0)

    assert len(result) == 2


def test_column_names_lowercase(tmp_path):
    df = pd.DataFrame({"ID": ["TCS"], "Year": [2024]})
    file = tmp_path / "sample.xlsx"
    df.to_excel(file, index=False)

    result = load_excel(file, header=0)

    assert "id" in result.columns
    assert "year" in result.columns


def test_column_names_trimmed(tmp_path):
    df = pd.DataFrame({" ID ": ["TCS"], " Year ": [2024]})
    file = tmp_path / "sample.xlsx"
    df.to_excel(file, index=False)

    result = load_excel(file, header=0)

    assert "id" in result.columns
    assert "year" in result.columns


def test_ticker_normalized(tmp_path):
    df = pd.DataFrame({"id": [" tcs "], "year": [2024]})
    file = tmp_path / "sample.xlsx"
    df.to_excel(file, index=False)

    result = load_excel(file, header=0)

    assert result.iloc[0]["id"] == "TCS"


def test_company_id_normalized(tmp_path):
    df = pd.DataFrame({"company_id": [" infy "], "year": [2024]})
    file = tmp_path / "sample.xlsx"
    df.to_excel(file, index=False)

    result = load_excel(file, header=0)

    assert result.iloc[0]["company_id"] == "INFY"


def test_year_normalized(tmp_path):
    df = pd.DataFrame({"id": ["TCS"], "year": ["Mar-24"]})
    file = tmp_path / "sample.xlsx"
    df.to_excel(file, index=False)

    result = load_excel(file, header=0)

    assert result.iloc[0]["year"] == 2024


def test_invalid_year_removed(tmp_path):
    df = pd.DataFrame(
        {
            "id": ["TCS", "INFY"],
            "year": ["Hello", "2024"],
        }
    )

    file = tmp_path / "sample.xlsx"
    df.to_excel(file, index=False)

    result = load_excel(file, header=0)

    assert len(result) == 1
    assert result.iloc[0]["id"] == "INFY"


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        load_excel("missing_file.xlsx")


def test_no_year_column(tmp_path):
    df = pd.DataFrame({"id": ["TCS"]})
    file = tmp_path / "sample.xlsx"
    df.to_excel(file, index=False)

    result = load_excel(file, header=0)

    assert len(result) == 1