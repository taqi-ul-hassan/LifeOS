import os
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite:///./test_automation.db"
os.environ["JWT_SECRET"] = "test-secret-only-not-for-production"
import pytest
from fastapi.testclient import TestClient
from app.automation.conditions import evaluate
from app.automation.event_bus import EventBus
from app.automation.events import Event
from app.automation.parser import parse
from app.db import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def schema():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


def auth(client):
    email = f"automation-{uuid4().hex}@example.com"
    client.post(
        "/v1/auth/register",
        json={
            "email": email,
            "password": "correct-horse-battery",
            "display_name": "Automation",
        },
    )
    return {
        "Authorization": f"Bearer {client.post('/v1/auth/token', json={'email': email, 'password': 'correct-horse-battery'}).json()['access_token']}"
    }


def test_event_bus_conditions_parser_and_api_execution():
    received = []
    bus = EventBus()
    bus.subscribe("TaskCreated", lambda event: received.append(event.id))
    event = Event("TaskCreated", "user", {"status": "open"})
    bus.publish(event)
    assert received == [event.id] and evaluate(
        {
            "op": "and",
            "items": [
                {"op": "equals", "field": "status", "value": "open"},
                {"op": "contains", "field": "tags", "value": "work"},
            ],
        },
        {"status": "open", "tags": ["work"]},
    )
    assert parse("Every Friday summarize my week.")["trigger"]["type"] == "cron"
    with TestClient(app) as client:
        headers = auth(client)
        created = client.post(
            "/v1/automation",
            headers=headers,
            json={
                "name": "Capture task",
                "trigger": {"type": "manual"},
                "actions": [{"type": "create_task", "title": "Generated task"}],
            },
        )
        assert created.status_code == 201
        rule_id = created.json()["id"]
        run = client.post(
            "/v1/automation/run",
            headers=headers,
            json={"rule_id": rule_id, "idempotency_key": "once"},
        )
        assert run.status_code == 200 and run.json()["status"] == "succeeded"
        assert (
            client.post(
                "/v1/automation/run",
                headers=headers,
                json={"rule_id": rule_id, "idempotency_key": "once"},
            ).json()["id"]
            == run.json()["id"]
        )
        assert client.get("/v1/automation/history", headers=headers).json()
        assert client.get("/v1/automation/logs", headers=headers).json()
        assert (
            client.get("/v1/automation/metrics", headers=headers).json()["succeeded"]
            == 1
        )
