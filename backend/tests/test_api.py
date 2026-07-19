import os
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite:///./test_lifeos.db"
os.environ["JWT_SECRET"] = "test-secret-only-not-for-production"
import pytest
from fastapi.testclient import TestClient
from app.db import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def schema():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


def test_public_system_and_openapi_contracts():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        spec = client.get("/openapi.json").json()
        expected = {
            "/v1/auth/register",
            "/v1/auth/token",
            "/v1/tasks",
            "/v1/goals",
            "/v1/daily-brief",
            "/v1/ai/respond",
        }
        assert expected <= set(spec["paths"])
        assert client.get("/v1/tasks").status_code == 401
        assert client.get("/v1/auth/oauth/google/login").status_code == 503


def test_jwt_authentication_and_resource_endpoints():
    with TestClient(app) as client:
        email = f"ayesha-{uuid4().hex}@example.com"
        registration = {
            "email": email,
            "password": "correct-horse-battery",
            "display_name": "Ayesha",
        }
        assert client.post("/v1/auth/register", json=registration).status_code == 201
        assert client.post("/v1/auth/register", json=registration).status_code == 409
        assert (
            client.post(
                "/v1/auth/token", json={"email": email, "password": "wrong-password"}
            ).status_code
            == 401
        )
        token = client.post(
            "/v1/auth/token",
            json={"email": email, "password": registration["password"]},
        ).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        created = client.post(
            "/v1/tasks", headers=headers, json={"title": "Ship Phase 2", "priority": 1}
        )
        assert created.status_code == 201
        updated = client.patch(
            f"/v1/tasks/{created.json()['id']}",
            headers=headers,
            json={"status": "completed"},
        )
        assert updated.status_code == 200 and updated.json()["completed_at"] is not None
        brief = client.get("/v1/daily-brief", headers=headers)
        assert brief.status_code == 200 and brief.json()["open_tasks"] == 0
        assert (
            client.post(
                "/v1/goals",
                headers=headers,
                json={"title": "Launch LifeOS", "horizon": "year"},
            ).status_code
            == 201
        )
        assert [
            item["title"] for item in client.get("/v1/goals", headers=headers).json()
        ] == ["Launch LifeOS"]
        response = client.post(
            "/v1/ai/respond", headers=headers, json={"prompt": "Plan my day"}
        )
        assert response.status_code == 503
