from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_healthcheck():
    response = client.get("/health", headers={"X-Agent-Token": "dummy"})
    assert response.status_code in (200, 503)
