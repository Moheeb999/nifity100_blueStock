from fastapi.testclient import TestClient

from src.api.main import app
from src.dashboard.utils.db import get_screener_data

client = TestClient(app)


def test_dashboard_matches_api():
    # Dashboard data
    dashboard_df = get_screener_data()

    # API data
    response = client.get("/api/v1/screener")

    assert response.status_code == 200

    api_df = response.json()

    # Same number of rows
    assert len(dashboard_df) == len(api_df)

    # Same companies
    dashboard_ids = set(dashboard_df["company_id"])

    api_ids = {row["id"] for row in api_df}

    assert dashboard_ids == api_ids
