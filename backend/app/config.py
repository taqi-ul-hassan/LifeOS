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

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
