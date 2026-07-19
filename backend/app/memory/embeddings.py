import hashlib
import math
import httpx
from fastapi import HTTPException
from ..config import Settings


class EmbeddingProvider:
    name: str
    model: str

    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError


class LocalEmbeddingProvider(EmbeddingProvider):
    name = "local"

    def __init__(self, settings: Settings):
        self.model = "deterministic-hash"
        self.dimensions = settings.local_embedding_dimensions

    async def embed(self, text: str) -> list[float]:
        values = [0.0] * self.dimensions
        for token in text.lower().split():
            values[
                int(hashlib.sha256(token.encode()).hexdigest(), 16) % self.dimensions
            ] += 1
        magnitude = math.sqrt(sum(v * v for v in values)) or 1
        return [v / magnitude for v in values]


class OpenAIEmbeddingProvider(EmbeddingProvider):
    name = "openai"

    def __init__(self, settings: Settings):
        self.key, self.model = settings.openai_api_key, settings.openai_embedding_model

    async def embed(self, text: str) -> list[float]:
        if not self.key:
            raise HTTPException(503, "OpenAI embeddings are not configured")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {self.key}"},
                json={"model": self.model, "input": text},
            )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]


class GeminiEmbeddingProvider(EmbeddingProvider):
    name = "gemini"

    def __init__(self, settings: Settings):
        self.key, self.model = settings.gemini_api_key, settings.gemini_embedding_model

    async def embed(self, text: str) -> list[float]:
        if not self.key:
            raise HTTPException(503, "Gemini embeddings are not configured")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:embedContent?key={self.key}"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                url, json={"content": {"parts": [{"text": text}]}}
            )
        response.raise_for_status()
        return response.json()["embedding"]["values"]


class AnthropicEmbeddingProvider(EmbeddingProvider):
    name = "anthropic"

    def __init__(self, settings: Settings):
        self.model = "anthropic-compatible"
        self.settings = settings

    async def embed(self, text: str) -> list[float]:
        raise HTTPException(
            503,
            "Anthropic has no native embedding endpoint; configure a compatible embedding gateway or choose another provider",
        )


def build_embedding_providers(settings: Settings) -> dict[str, EmbeddingProvider]:
    return {
        p.name: p
        for p in (
            LocalEmbeddingProvider(settings),
            OpenAIEmbeddingProvider(settings),
            GeminiEmbeddingProvider(settings),
            AnthropicEmbeddingProvider(settings),
        )
    }
