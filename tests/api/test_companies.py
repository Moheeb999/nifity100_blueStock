from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_get_companies():
    response = client.get("/api/v1/companies")

    assert response.status_code == 200

    companies = response.json()

    assert len(companies) == 92


def test_get_company_profile():
    response = client.get("/api/v1/companies/TCS")

    assert response.status_code == 200

    data = response.json()

    assert data["company"]["id"] == "TCS"
    assert "latest_kpis" in data


def test_invalid_company():
    response = client.get("/api/v1/companies/INVALID")

    assert response.status_code == 404
