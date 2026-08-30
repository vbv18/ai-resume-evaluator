from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.lib.constants import (
    DEFAULT_AI_PROVIDER,
    DEFAULT_GROQ_MODEL,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_REQUEST_TIMEOUT_SECONDS,
    MAX_INPUT_TOKENS,
    STORAGE_BUCKET_JOB_DESCRIPTIONS,
    STORAGE_BUCKET_RESUMES,
)


class Settings(BaseSettings):
    """
    Typed, validated environment config.
    Parses environment variables and .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    environment: str = "development"
    port: int = 8000
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Database
    database_url: str = ""
    database_pool_size: int = 10
    database_max_overflow: int = 5
    database_pool_timeout: int = 30

    # Supabase Auth & JWT
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    # Storage Buckets
    storage_bucket_resumes: str = STORAGE_BUCKET_RESUMES
    storage_bucket_job_descriptions: str = STORAGE_BUCKET_JOB_DESCRIPTIONS

    # AI Configuration
    ai_provider: str = DEFAULT_AI_PROVIDER
    groq_api_key: str = ""
    groq_model: str = DEFAULT_GROQ_MODEL
    openai_api_key: str = ""
    openai_model: str = DEFAULT_OPENAI_MODEL
    anthropic_api_key: str = ""
    gemini_api_key: str = ""

    # Limits & Timeouts
    max_upload_size_mb: int = 10
    max_input_tokens: int = MAX_INPUT_TOKENS
    request_timeout_seconds: int = DEFAULT_REQUEST_TIMEOUT_SECONDS

    # Worker Settings
    worker_poll_interval_seconds: float = 1.5
    worker_max_concurrent_jobs: int = 2

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def async_database_url(self) -> str:
        url = self.database_url.strip()
        if not url:
            # Fallback for lightweight local development if no Postgres URL is provided
            return "sqlite+aiosqlite:///./ai_resume.db"
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith(
            "postgresql+asyncpg://"
        ):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    """
    Cached singleton - Settings() is only constructed once per process.
    """
    return Settings()
