from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Typed, validated environment config.
    Equivalent to reading process.env through a zod/envalid schema in Node —
    except pydantic-settings parses os.environ automatically by field name.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    environment: str = "development"

    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"

    max_upload_size_mb: int = 5
    max_input_tokens: int = 6000
    request_timeout_seconds: int = 30

    cors_origin: str = "http;//localhost:5173"
    log_level: str = "INFO"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Cached singleton - Settings() is only constructed once per process.
    Use as a FastAPI dependency: `settings: Settings = Depends(get_settings)`.
    """
    return Settings()
