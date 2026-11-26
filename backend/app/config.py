"""Application configuration loaded from environment variables."""
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Optional


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

    # Security & Access Control (OWASP Top 10:2025 & API Security Top 10:2023)
    admin_api_key: str = ""
    require_admin_key: bool = False
    allowed_origin_regex: str = r"^https://easyfineprint(?:-[a-zA-Z0-9-]+)*\.vercel\.app$"
    enable_api_docs: Optional[bool] = None
    rate_limit_enabled: bool = True
    trust_proxy_headers: bool = False
    max_json_body_bytes: int = 10 * 1024 * 1024
    max_tunnel_body_bytes: int = 262144  # 256 KB
    max_discovery_body_bytes: int = 65536  # 64 KB

    @field_validator("enable_api_docs", mode="before")
    @classmethod
    def _empty_str_to_none(cls, v: Any) -> Any:
        if isinstance(v, str) and not v.strip():
            return None
        return v

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

    def docs_enabled(self) -> bool:
        """Return True if interactive OpenAPI docs should be exposed."""
        if self.enable_api_docs is not None:
            return bool(self.enable_api_docs)
        return (self.environment or "").strip().lower() != "production"


settings = Settings()
