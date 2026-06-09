import pytest

pytest.importorskip("flask")

from app import app


def test_health_route():
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"
