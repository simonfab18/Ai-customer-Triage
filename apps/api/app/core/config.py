from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "AI Customer Support Triage API"
    app_env: str = "local"
    debug: bool = True

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: str = Field(default="http://localhost:3000")

    database_url: str = "sqlite:///./support_triage.db"
    redis_url: str = "redis://localhost:6379/0"
    celery_task_always_eager: bool = False
    encryption_key: str | None = None

    supabase_url: str | None = None
    supabase_publishable_key: str | None = None
    supabase_secret_key: str | None = None
    supabase_jwks_url: str | None = None
    supabase_jwt_secret: str | None = None
    auth_allow_unverified_jwt: bool = False

    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str | None = "http://localhost:8000/v1/gmail/oauth/callback"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.5-flash"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]


settings = Settings()
