from fastapi.testclient import TestClient
from rubix.main import app

client = TestClient(app)


def test_liveness():
    response = client.get("/api/v1/health/liveness")
    assert response.status_code == 200
    assert response.json().get("message") == "alive"
    assert response.json().get("success") is True


def test_readiness():
    response = client.get("/api/v1/health/readiness")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
