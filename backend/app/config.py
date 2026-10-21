"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemma_model: str = "gemma-4-26b-a4b-it"
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "easyfineprint"
    frontend_origin: str = "http://localhost:5173"
    environment: str = "development"

    serpapi_api_key: str = ""
    serpapi_enabled: bool = False
    serpapi_monthly_cap: int = 200
    serpapi_hourly_cap: int = 40

    max_fetch_bytes: int = 2000000
    fetch_timeout_seconds: int = 15
    max_policy_chars: int = 120000
    sentry_dsn: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
