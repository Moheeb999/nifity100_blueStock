from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_screener_min_roe():
    response = client.get("/api/v1/screener?min_roe=15")

    assert response.status_code == 200

    companies = response.json()

    for company in companies:
        assert company["return_on_equity_pct"] >= 15


def test_screener_invalid_parameter():
    response = client.get("/api/v1/screener?min_roe=-1")

    assert response.status_code == 422
