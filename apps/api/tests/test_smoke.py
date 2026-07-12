from fastapi.testclient import TestClient

from src.main import app


def test_home_page():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "WB AI" in response.text


def test_openapi_contains_core_routes():
    client = TestClient(app)
    payload = client.get("/openapi.json").json()
    paths = payload["paths"]
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/stores" in paths
    assert "/api/v1/products" in paths
    assert "/api/v1/ai/title" in paths
    assert "/api/v1/ai/improve-card" in paths
