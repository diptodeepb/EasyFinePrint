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

    def get_frontend_base_url(self) -> str:
        """Return canonical frontend URL based on current environment (deployed state vs localhost)."""
        origin = (self.frontend_origin or "").strip().rstrip("/")
        if origin and "localhost" not in origin:
            return origin
        if self.environment.lower() == "production":
            return "https://easyfineprint.vercel.app"
        return origin or "http://localhost:5173"


settings = Settings()
