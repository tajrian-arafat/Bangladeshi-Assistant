"""Application settings loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the BDA backend."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: Literal["development", "staging", "production"] = "development"
    app_secret_key: str = Field(default="change-me-in-production", min_length=16)
    app_base_url: str = "http://localhost:8000"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    database_url: str = "sqlite+aiosqlite:///./data/bda.db"
    database_pool_size: int = 20
    database_echo: bool = False

    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str = Field(default="change-me-jwt-secret-key", min_length=16)
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_minutes: int = 15
    jwt_refresh_ttl_days: int = 7

    llm_base_url: str = "http://localhost:8080/v1"
    llm_model_primary: str = "qwen2.5-7b-instruct"
    llm_model_fallback: str = "qwen2.5-3b-instruct"
    llm_timeout_seconds: int = 60
    llm_max_tokens: int = 1024

    embedding_model: str = "BAAI/bge-m3"
    embedding_device: str = "cpu"

    feature_document_upload: bool = False
    feature_playwright_crawl: bool = False
    feature_llm_enabled: bool = False

    log_level: str = "INFO"
    prometheus_enabled: bool = False

    rate_limit_anonymous_per_min: int = 20
    rate_limit_auth_per_min: int = 60

    crawler_user_agent: str = "BDABot/1.0 (+https://example.org/bot; contact=admin@example.org)"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_postgres(self) -> bool:
        return "postgresql" in self.database_url or "postgres" in self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
