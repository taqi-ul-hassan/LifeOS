import os
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite:///./test_integrations.db"
os.environ["JWT_SECRET"] = "test-secret-only-not-for-production"
import pytest
from fastapi.testclient import TestClient
from app.db import Base, engine
from app.integrations.encryption import decrypt, encrypt
from app.integrations.registry import ProviderRegistry
from app.integrations.providers import Connector
from app.integrations.webhook import verify
from app.main import app


@pytest.fixture(autouse=True)
def schema():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


def test_registry_crypto_webhook_and_api():
    registry = ProviderRegistry()
    registry.register(Connector("demo"))
    assert registry.get("demo").health()["status"] == "healthy"
    assert decrypt(encrypt({"token": "secret"}))["token"] == "secret"
    import hashlib
    import hmac

    body = b"payload"
    signature = hmac.new(b"hook", body, hashlib.sha256).hexdigest()
    assert verify("hook", body, signature)
    with TestClient(app) as client:
        email = f"integration-{uuid4().hex}@example.com"
        client.post(
            "/v1/auth/register",
            json={
                "email": email,
                "password": "correct-horse-battery",
                "display_name": "Integration",
            },
        )
        headers = {
            "Authorization": f"Bearer {client.post('/v1/auth/token', json={'email': email, 'password': 'correct-horse-battery'}).json()['access_token']}"
        }
        connected = client.post(
            "/v1/integrations/connect",
            headers=headers,
            json={
                "provider": "github",
                "scopes": ["read"],
                "credentials": {"access_token": "never-plaintext"},
            },
        )
        assert connected.status_code == 200
        assert (
            client.post(
                "/v1/integrations/github/sync", headers=headers, json={"mode": "manual"}
            ).json()["status"]
            == "completed"
        )
        assert client.get("/v1/integrations/health", headers=headers).status_code == 200
        assert (
            client.post(
                "/v1/integrations/disconnect",
                headers=headers,
                json={"provider": "github"},
            ).json()["status"]
            == "disconnected"
        )
