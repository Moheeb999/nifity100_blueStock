from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    expected_tables = {
        "analysis",
        "balancesheet",
        "cashflow",
        "companies",
        "documents",
        "financial_ratios",
        "market_cap",
        "peer_groups",
        "peer_percentiles",
        "profitandloss",
        "prosandcons",
        "sectors",
        "stock_prices",
    }

    assert expected_tables.issubset(set(data["db_row_counts"].keys()))
