import os
from uuid import uuid4
os.environ["DATABASE_URL"] = "sqlite:///./test_lifeos.db"
os.environ["JWT_SECRET"] = "test-secret-only-not-for-production"
from fastapi.testclient import TestClient
from app.main import app

def test_auth_task_and_daily_brief():
    with TestClient(app) as client:
        email = f"ayesha-{uuid4().hex}@example.com"
        registered = client.post("/v1/auth/register", json={"email":email, "password":"correct-horse-battery", "display_name":"Ayesha"})
        assert registered.status_code == 201
        token = client.post("/v1/auth/token", json={"email":email, "password":"correct-horse-battery"}).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        created = client.post("/v1/tasks", headers=headers, json={"title":"Ship Phase 2", "priority":1})
        assert created.status_code == 201
        updated = client.patch(f"/v1/tasks/{created.json()['id']}", headers=headers, json={"status":"completed"})
        assert updated.json()["completed_at"] is not None
        brief = client.get("/v1/daily-brief", headers=headers)
        assert brief.status_code == 200 and brief.json()["open_tasks"] == 0
