from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.integration.test_errors import add_failing_route

EXPECTED_HEADERS = {
    "content-security-policy": "default-src 'self'",
    "x-content-type-options": "nosniff",
    "referrer-policy": "same-origin",
}


def test_security_headers_on_page_health_404_and_500(app: FastAPI, client: TestClient) -> None:
    add_failing_route(app)
    responses = {
        "page": client.get("/"),
        "health": client.get("/api/health"),
        "404": client.get("/does-not-exist"),
        "500": client.get("/api/test-only/boom"),
    }

    assert [r.status_code for r in responses.values()] == [200, 200, 404, 500]
    for name, response in responses.items():
        for header, value in EXPECTED_HEADERS.items():
            assert response.headers.get(header) == value, f"{name}: {header}"
