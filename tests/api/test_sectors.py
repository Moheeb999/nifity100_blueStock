from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_get_sectors():
    response = client.get("/api/v1/sectors")

    assert response.status_code == 200

    sectors = response.json()

    assert len(sectors) == 10


def test_sector_companies():
    response = client.get("/api/v1/sectors/Information Technology/companies")

    assert response.status_code == 200

    companies = response.json()

    assert len(companies) > 0

    for company in companies:
        assert company["broad_sector"].lower() == "information technology"
