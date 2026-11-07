import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

LEAK_MARKER = "leak-marker-internal-detail"


def add_failing_route(app: FastAPI) -> None:
    """A route that fails unexpectedly — exists only inside these tests."""

    @app.get("/api/test-only/boom")
    def boom() -> None:
        raise RuntimeError(f"{LEAK_MARKER} in C:/srv/app/internal.py")

    # The static mount catches every path; move the new route in front of it.
    app.router.routes.insert(0, app.router.routes.pop())


@pytest.mark.parametrize("path", ["/does-not-exist", "/api/does-not-exist"])
def test_unknown_path_returns_problem_details_404(client: TestClient, path: str) -> None:
    response = client.get(path)

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json() == {
        "type": "not-found",
        "title": "Not Found",
        "status": 404,
        "detail": "İstenen adres bulunamadı.",
    }


def test_unexpected_error_returns_generic_problem_details_500(
    app: FastAPI, client: TestClient
) -> None:
    add_failing_route(app)

    response = client.get("/api/test-only/boom")

    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json() == {
        "type": "internal-error",
        "title": "Internal Server Error",
        "status": 500,
        "detail": "Beklenmeyen bir hata oluştu. Lütfen daha sonra tekrar deneyin.",
    }
    assert LEAK_MARKER not in response.text
    assert "Traceback" not in response.text
    assert "internal.py" not in response.text
    assert "RuntimeError" not in response.text


def test_method_not_allowed_keeps_allow_header(client: TestClient) -> None:
    response = client.post("/api/health")

    assert response.status_code == 405
    assert response.headers.get("allow") == "GET, HEAD"  # Starlette adds HEAD to GET routes
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["type"] == "http-error"
