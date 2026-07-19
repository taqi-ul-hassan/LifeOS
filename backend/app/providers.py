from abc import ABC, abstractmethod
import httpx
from fastapi import HTTPException
from .config import Settings


class Provider(ABC):
    name: str
    model: str

    @abstractmethod
    async def generate(self, system_prompt: str, prompt: str) -> str: ...


class OpenAIProvider(Provider):
    name = "openai"

    def __init__(self, settings: Settings):
        self.key, self.model = settings.openai_api_key, settings.openai_model

    async def generate(self, system_prompt: str, prompt: str) -> str:
        if not self.key:
            raise HTTPException(503, "OpenAI provider is not configured")
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers={"Authorization": f"Bearer {self.key}"},
                json={
                    "model": self.model,
                    "instructions": system_prompt,
                    "input": prompt,
                    "store": False,
                },
            )
        response.raise_for_status()
        data = response.json()
        return data.get("output_text") or "".join(
            part.get("text", "")
            for item in data.get("output", [])
            for part in item.get("content", [])
        )


class GeminiProvider(Provider):
    name = "gemini"

    def __init__(self, settings: Settings):
        self.key, self.model = settings.gemini_api_key, settings.gemini_model

    async def generate(self, system_prompt: str, prompt: str) -> str:
        if not self.key:
            raise HTTPException(503, "Gemini provider is not configured")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.key}"
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                url,
                json={
                    "systemInstruction": {"parts": [{"text": system_prompt}]},
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                },
            )
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]


class AnthropicProvider(Provider):
    name = "anthropic"

    def __init__(self, settings: Settings):
        self.key, self.model = settings.anthropic_api_key, settings.anthropic_model

    async def generate(self, system_prompt: str, prompt: str) -> str:
        if not self.key:
            raise HTTPException(503, "Anthropic provider is not configured")
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": self.key, "anthropic-version": "2023-06-01"},
                json={
                    "model": self.model,
                    "max_tokens": 1024,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
        response.raise_for_status()
        return "".join(
            item["text"]
            for item in response.json()["content"]
            if item["type"] == "text"
        )


class LocalLLMProvider(Provider):
    name = "local"

    def __init__(self, settings: Settings):
        self.base_url, self.model = (
            settings.local_llm_base_url.rstrip("/"),
            settings.local_llm_model,
        )

    async def generate(self, system_prompt: str, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                },
            )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


def build_providers(settings: Settings) -> dict[str, Provider]:
    return {
        provider.name: provider
        for provider in (
            OpenAIProvider(settings),
            GeminiProvider(settings),
            AnthropicProvider(settings),
            LocalLLMProvider(settings),
        )
    }
