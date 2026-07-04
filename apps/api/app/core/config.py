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

    redis_url: str = "redis://localhost:6379/0"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]


settings = Settings()

