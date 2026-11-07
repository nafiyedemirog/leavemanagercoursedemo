from fastapi.testclient import TestClient


def test_health_without_session_returns_only_status(client: TestClient) -> None:
    assert not client.cookies  # no session of any kind

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
