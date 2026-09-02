"""Flask 应用工厂与路由冒烟测试。"""

from __future__ import annotations

import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app(env="testing")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["env"] == "testing"


def test_public_config_hides_secrets(client):
    resp = client.get("/api/config")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ENV"] == "testing"
    assert "PASSWORD" not in data["DATABASE"]
    assert "SECRET_KEY" not in data
