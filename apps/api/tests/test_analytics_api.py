from fastapi.testclient import TestClient

from src.main import app


def test_analytics_routes_are_in_openapi():
    schema = TestClient(app).get("/openapi.json").json()
    for path in [
        "/api/v1/analytics/overview",
        "/api/v1/analytics/trends",
        "/api/v1/analytics/abc-xyz",
        "/api/v1/analytics/forecast",
        "/api/v1/analytics/demo/generate",
    ]:
        assert path in schema["paths"]
