from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "LifeOS API"
    database_url: str = "sqlite:///./lifeos.db"
    jwt_secret: str = "change-me-in-production-use-a-strong-secret"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    oauth_google_client_id: str | None = None
    oauth_google_client_secret: str | None = None
    oauth_redirect_base_url: str = "http://localhost:8000"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:5500"
    ai_default_provider: str = "openai"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-20250514"
    local_llm_base_url: str = "http://localhost:11434/v1"
    local_llm_model: str = "llama3.2"
    embedding_default_provider: str = "local"
    openai_embedding_model: str = "text-embedding-3-small"
    gemini_embedding_model: str = "gemini-embedding-001"
    local_embedding_dimensions: int = 64

    @property
    def origins(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
