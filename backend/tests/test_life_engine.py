import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite:///./test_life_engine.db"
os.environ["JWT_SECRET"] = "test-secret-only-not-for-production"

import pytest
from fastapi.testclient import TestClient
from app.db import Base, SessionLocal, engine
from app.models import LearningSession, Project, Task, User
from app.main import app


@pytest.fixture(autouse=True)
def schema():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


def headers(client: TestClient) -> tuple[dict[str, str], str]:
    email = f"engine-{uuid4().hex}@example.com"
    client.post(
        "/v1/auth/register",
        json={
            "email": email,
            "password": "correct-horse-battery",
            "display_name": "Engine Test",
        },
    )
    token = client.post(
        "/v1/auth/token", json={"email": email, "password": "correct-horse-battery"}
    ).json()["access_token"]
    session = SessionLocal()
    try:
        user_id = session.query(User).filter_by(email=email).one().id
    finally:
        session.close()
    return {"Authorization": f"Bearer {token}"}, user_id


def test_context_plans_review_and_recommendations():
    with TestClient(app) as client:
        auth, user_id = headers(client)
        session = SessionLocal()
        try:
            project = Project(
                user_id=user_id,
                name="LifeOS",
                status="active",
                due_at=datetime.now(timezone.utc).replace(tzinfo=None)
                + timedelta(days=2),
            )
            session.add(project)
            session.flush()
            session.add_all(
                [
                    Task(
                        user_id=user_id,
                        project_id=project.id,
                        title="Ship planning engine",
                        priority=1,
                        status="open",
                    ),
                    Task(
                        user_id=user_id, title="Triage inbox", priority=4, status="open"
                    ),
                ]
            )
            session.add(
                LearningSession(
                    user_id=user_id,
                    topic="German",
                    started_at=datetime.now(timezone.utc).replace(tzinfo=None)
                    - timedelta(days=4),
                    minutes=20,
                )
            )
            session.commit()
        finally:
            session.close()
        context = client.get("/v1/context", headers=auth)
        assert (
            context.status_code == 200
            and context.json()["current_task"] == "Ship planning engine"
        )
        daily = client.post("/v1/planning/daily", headers=auth)
        assert (
            daily.status_code == 200
            and daily.json()["items"][0]["title"] == "Ship planning engine"
        )
        weekly = client.post("/v1/planning/weekly", headers=auth)
        assert weekly.status_code == 200 and weekly.json()["horizon"] == "weekly"
        review = client.post(
            "/v1/planning/review", headers=auth, json={"period": "weekly"}
        )
        assert review.status_code == 200 and review.json()["period"] == "weekly"
        recommendations = client.post("/v1/planning/recommend", headers=auth)
        assert recommendations.status_code == 200 and any(
            item["category"] == "learning"
            for item in recommendations.json()["recommendations"]
        )
