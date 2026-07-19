import asyncio
import os
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite:///./test_memory.db"
os.environ["JWT_SECRET"] = "test-secret-only-not-for-production"

import pytest
from fastapi.testclient import TestClient
from app.db import Base, SessionLocal, engine
from app.memory.embeddings import LocalEmbeddingProvider
from app.memory.embeddings import (
    AnthropicEmbeddingProvider,
    GeminiEmbeddingProvider,
    OpenAIEmbeddingProvider,
)
from app.memory.retrieval import cosine
from app.memory.models import KnowledgeEdge, KnowledgeNode
from app.memory.scorer import ImportanceScorer
from app.main import app


@pytest.fixture(autouse=True)
def schema():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


def auth_headers(client: TestClient) -> dict[str, str]:
    email = f"memory-{uuid4().hex}@example.com"
    client.post(
        "/v1/auth/register",
        json={
            "email": email,
            "password": "correct-horse-battery",
            "display_name": "Memory Test",
        },
    )
    token = client.post(
        "/v1/auth/token", json={"email": email, "password": "correct-horse-battery"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_memory_crud_hybrid_retrieval_and_stats():
    with TestClient(app) as client:
        headers = auth_headers(client)
        created = client.post(
            "/v1/memory",
            headers=headers,
            json={
                "title": "Running preference",
                "content": "I prefer running outside before breakfast.",
                "memory_type": "semantic",
                "tags": ["health", "habit"],
                "metadata": {"explicit_preference": True},
            },
        )
        assert created.status_code == 201
        memory_id = created.json()["id"]
        retrieved = client.post(
            "/v1/memory/retrieve",
            headers=headers,
            json={"query": "morning running", "tags": ["health"]},
        )
        assert (
            retrieved.status_code == 200
            and retrieved.json()["memories"][0]["id"] == memory_id
        )
        assert (
            client.patch(
                f"/v1/memory/{memory_id}",
                headers=headers,
                json={"title": "Outdoor running preference"},
            ).json()["title"]
            == "Outdoor running preference"
        )
        assert client.get("/v1/memory/stats", headers=headers).json()["active"] == 1
        assert (
            client.delete(f"/v1/memory/{memory_id}", headers=headers).status_code == 204
        )
        assert client.get("/v1/memory/stats", headers=headers).json()["archived"] == 1


def test_memory_remaining_endpoints_and_consolidation():
    with TestClient(app) as client:
        headers = auth_headers(client)
        payload = {
            "title": "Duplicate",
            "content": "I like structured planning.",
            "tags": ["planning"],
        }
        first = client.post("/v1/memory", headers=headers, json=payload).json()["id"]
        client.post("/v1/memory", headers=headers, json=payload)
        assert client.get("/v1/memory", headers=headers).status_code == 200
        assert client.get(f"/v1/memory/{first}", headers=headers).status_code == 200
        assert (
            client.post(
                "/v1/memory/search",
                headers=headers,
                json={"query": "structured planning"},
            ).status_code
            == 200
        )
        assert client.post("/v1/memory/summarize", headers=headers).json()["summary"]
        assert (
            client.post("/v1/memory/consolidate", headers=headers).json()["archived"]
            == 1
        )


def test_scoring_embedding_and_knowledge_graph():
    assert (
        ImportanceScorer().score(
            "I decided this is important",
            {"explicit_preference": True, "decision_impact": 1},
        )
        > 0.5
    )
    provider = LocalEmbeddingProvider(
        type("Settings", (), {"local_embedding_dimensions": 8})()
    )
    vector = asyncio.run(provider.embed("health health habits"))
    assert len(vector) == 8 and round(sum(value * value for value in vector), 4) == 1
    session = SessionLocal()
    try:
        node_a = KnowledgeNode(user_id="user", label="Ayesha", node_type="person")
        node_b = KnowledgeNode(user_id="user", label="LifeOS", node_type="project")
        session.add_all([node_a, node_b])
        session.flush()
        session.add(
            KnowledgeEdge(
                user_id="user",
                source_id=node_a.id,
                target_id=node_b.id,
                relation="works_on",
            )
        )
        session.commit()
        assert session.query(KnowledgeEdge).filter_by(relation="works_on").count() == 1
    finally:
        session.close()


def test_embedding_provider_contracts_and_edge_cases(monkeypatch):
    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "data": [{"embedding": [0.1, 0.2]}],
                "embedding": {"values": [0.1, 0.2]},
            }

    class Client:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, *args, **kwargs):
            return Response()

    import app.memory.embeddings as embeddings

    monkeypatch.setattr(embeddings.httpx, "AsyncClient", Client)
    settings = type(
        "Settings",
        (),
        {
            "openai_api_key": "key",
            "openai_embedding_model": "model",
            "gemini_api_key": "key",
            "gemini_embedding_model": "model",
        },
    )()
    assert asyncio.run(OpenAIEmbeddingProvider(settings).embed("x")) == [0.1, 0.2]
    assert asyncio.run(GeminiEmbeddingProvider(settings).embed("x")) == [0.1, 0.2]
    assert cosine([1], [1, 2]) == 0
    with pytest.raises(Exception):
        asyncio.run(AnthropicEmbeddingProvider(settings).embed("x"))
