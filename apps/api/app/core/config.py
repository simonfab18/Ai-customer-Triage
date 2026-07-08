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
    frontend_origin: str | None = None
    error_tracking_dsn: str | None = None
    logging_level: str = "INFO"
    service_name: str = "api"
    release_version: str = "0.1.0"
    operations_internal_token: str | None = None
    operations_alert_owner: str = "platform"
    operations_runbook_base_url: str | None = None
    operations_failure_alert_threshold: int = 3
    worker_concurrency: int = 2
    sync_fallback_interval_minutes: int = 15
    watch_renewal_schedule: str = "0 3 * * *"

    supabase_url: str | None = None
    supabase_publishable_key: str | None = None
    supabase_secret_key: str | None = None
    supabase_jwks_url: str | None = None
    supabase_jwt_secret: str | None = None
    auth_allow_unverified_jwt: bool = False

    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str | None = "http://localhost:8000/v1/gmail/oauth/callback"
    google_cloud_project_id: str | None = None
    google_pubsub_topic: str | None = None
    google_pubsub_subscription: str | None = None
    pubsub_expected_audience: str | None = None
    pubsub_service_account_email: str | None = None

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.5-flash"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]

    @property
    def normalized_app_env(self) -> str:
        return self.app_env.lower().strip()

    @property
    def is_production_like(self) -> bool:
        return self.normalized_app_env in {"staging", "production"}

    def validate_runtime_settings(self) -> None:
        """Fail fast for staging/production instead of starting with unsafe defaults."""
        allowed_envs = {"local", "development", "test", "staging", "production"}
        if self.normalized_app_env not in allowed_envs:
            raise RuntimeError(
                "APP_ENV must be one of local, development, test, staging, or production."
            )

        if not self.is_production_like:
            return

        required_values = {
            "DATABASE_URL": self.database_url,
            "REDIS_URL": self.redis_url,
            "ENCRYPTION_KEY": self.encryption_key,
            "SUPABASE_URL": self.supabase_url,
            "SUPABASE_PUBLISHABLE_KEY": self.supabase_publishable_key,
            "SUPABASE_SECRET_KEY": self.supabase_secret_key,
            "SUPABASE_JWKS_URL or SUPABASE_JWT_SECRET": self.supabase_jwks_url
            or self.supabase_jwt_secret,
            "GOOGLE_CLIENT_ID": self.google_client_id,
            "GOOGLE_CLIENT_SECRET": self.google_client_secret,
            "GOOGLE_REDIRECT_URI": self.google_redirect_uri,
            "GOOGLE_CLOUD_PROJECT_ID": self.google_cloud_project_id,
            "GOOGLE_PUBSUB_TOPIC": self.google_pubsub_topic,
            "GOOGLE_PUBSUB_SUBSCRIPTION": self.google_pubsub_subscription,
            "PUBSUB_EXPECTED_AUDIENCE": self.pubsub_expected_audience,
            "PUBSUB_SERVICE_ACCOUNT_EMAIL": self.pubsub_service_account_email,
            "GEMINI_API_KEY": self.gemini_api_key,
            "GEMINI_MODEL": self.gemini_model,
            "FRONTEND_ORIGIN": self.frontend_origin,
            "API_CORS_ORIGINS": self.api_cors_origins,
            "WORKER_CONCURRENCY": self.worker_concurrency,
            "SYNC_FALLBACK_INTERVAL_MINUTES": self.sync_fallback_interval_minutes,
            "WATCH_RENEWAL_SCHEDULE": self.watch_renewal_schedule,
            "RELEASE_VERSION": self.release_version,
            "OPERATIONS_ALERT_OWNER": self.operations_alert_owner,
        }
        missing = [name for name, value in required_values.items() if not value]
        if missing:
            raise RuntimeError(
                "Missing required production settings: " + ", ".join(sorted(missing))
            )

        if self.database_url.startswith("sqlite"):
            raise RuntimeError("DATABASE_URL must not use SQLite outside local development.")
        if self.debug:
            raise RuntimeError("DEBUG must be false in staging and production.")
        if self.auth_allow_unverified_jwt:
            raise RuntimeError("AUTH_ALLOW_UNVERIFIED_JWT must be false in staging and production.")
        if self.celery_task_always_eager:
            raise RuntimeError("CELERY_TASK_ALWAYS_EAGER must be false in staging and production.")
        if "*" in self.cors_origins:
            raise RuntimeError("API_CORS_ORIGINS must not contain '*' in staging or production.")
        if self.encryption_key == "dev-only-change-me":
            raise RuntimeError("ENCRYPTION_KEY must be replaced outside local development.")


settings = Settings()
