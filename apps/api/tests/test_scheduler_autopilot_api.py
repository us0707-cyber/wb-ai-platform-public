from fastapi.testclient import TestClient
from src.main import app

def test_scheduler_and_autopilot_routes_are_in_openapi():
    paths=TestClient(app).get("/openapi.json").json()["paths"]
    for path in ["/api/v1/schedules","/api/v1/schedules/{schedule_id}","/api/v1/schedules/{schedule_id}/trigger","/api/v1/autopilot/rules","/api/v1/autopilot/evaluate"]:
        assert path in paths
