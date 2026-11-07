from fastapi.testclient import TestClient


def test_index_page_is_turkish_leave_manager_html(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert '<html lang="tr">' in response.text
    assert "<title>Leave Manager</title>" in response.text
