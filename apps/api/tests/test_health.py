from fastapi.testclient import TestClient

from app.main import create_app


client = TestClient(create_app())


def test_health_check_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_status_returns_service_status() -> None:
    response = client.get("/v1/status")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"]

