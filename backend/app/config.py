"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # Cloudflare Workers AI Configuration
    cloudflare_api_token: str = ""
    cloudflare_api_key: str = ""  # alias for cloudflare_api_token
    cloudflare_account_id: str = ""
    cloudflare_ai_model: str = "@cf/google/gemma-4-26b-a4b-it"

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "easyfineprint"
    frontend_origin: str = "http://localhost:5173"
    environment: str = "development"

    max_fetch_bytes: int = 5000000
    fetch_timeout_seconds: int = 20
    max_policy_chars: int = 500000
    sentry_dsn: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
