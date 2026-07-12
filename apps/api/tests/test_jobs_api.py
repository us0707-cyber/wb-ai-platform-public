from fastapi.testclient import TestClient

from src.main import app


def test_job_routes_are_in_openapi():
    schema = TestClient(app).get('/openapi.json').json()
    for path in [
        '/api/v1/jobs',
        '/api/v1/jobs/{job_id}',
        '/api/v1/jobs/{job_id}/retry',
    ]:
        assert path in schema['paths']
