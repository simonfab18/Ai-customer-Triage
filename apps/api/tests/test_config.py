import pytest

from app.core.config import Settings


def production_settings(**overrides):
    values = {
        "app_env": "production",
        "debug": False,
        "api_cors_origins": "https://app.example.com",
        "database_url": "postgresql+psycopg://user:password@db.example.com:5432/app",
        "redis_url": "redis://redis.example.com:6379/0",
        "celery_task_always_eager": False,
        "encryption_key": "prod-secret-key",
        "frontend_origin": "https://app.example.com",
        "supabase_url": "https://project.supabase.co",
        "supabase_publishable_key": "publishable-key",
        "supabase_secret_key": "secret-key",
        "supabase_jwks_url": "https://project.supabase.co/auth/v1/.well-known/jwks.json",
        "google_client_id": "google-client-id",
        "google_client_secret": "google-client-secret",
        "google_redirect_uri": "https://api.example.com/v1/gmail/oauth/callback",
        "google_cloud_project_id": "support-triage-prod",
        "google_pubsub_topic": "gmail-notifications-prod",
        "google_pubsub_subscription": "gmail-notifications-prod-push",
        "pubsub_expected_audience": "https://api.example.com/v1/webhooks/google/gmail",
        "pubsub_service_account_email": "pubsub-push@example.iam.gserviceaccount.com",
        "gemini_api_key": "gemini-key",
        "gemini_model": "gemini-3.5-flash",
        "worker_concurrency": 2,
        "sync_fallback_interval_minutes": 15,
        "watch_renewal_schedule": "0 3 * * *",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_local_settings_allow_development_defaults():
    settings = Settings(_env_file=None, app_env="local")

    settings.validate_runtime_settings()


def test_production_settings_pass_when_required_values_are_present():
    settings = production_settings()

    settings.validate_runtime_settings()


def test_production_settings_require_pubsub_identity_values():
    settings = production_settings(pubsub_service_account_email=None)

    with pytest.raises(RuntimeError, match="PUBSUB_SERVICE_ACCOUNT_EMAIL"):
        settings.validate_runtime_settings()


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("database_url", "sqlite:///./prod.db", "SQLite"),
        ("debug", True, "DEBUG"),
        ("auth_allow_unverified_jwt", True, "AUTH_ALLOW_UNVERIFIED_JWT"),
        ("celery_task_always_eager", True, "CELERY_TASK_ALWAYS_EAGER"),
        ("api_cors_origins", "*", "API_CORS_ORIGINS"),
        ("encryption_key", "dev-only-change-me", "ENCRYPTION_KEY"),
    ],
)
def test_production_settings_reject_unsafe_values(field, value, message):
    settings = production_settings(**{field: value})

    with pytest.raises(RuntimeError, match=message):
        settings.validate_runtime_settings()


def test_unknown_environment_is_rejected():
    settings = Settings(_env_file=None, app_env="preview")

    with pytest.raises(RuntimeError, match="APP_ENV"):
        settings.validate_runtime_settings()
