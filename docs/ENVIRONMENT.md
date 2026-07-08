# Environment Configuration

Use the checked-in `.env.example` files as templates only. Real secrets stay in local `.env` files or deployment secret stores.

## Local files

Create these files before running the app locally:

```powershell
Copy-Item apps/api/.env.example apps/api/.env
Copy-Item apps/web/.env.example apps/web/.env.local
```

Do not commit either generated file. They are already ignored by `.gitignore`.

## Backend variables

`apps/api/.env` controls the FastAPI app, worker, database, Gmail OAuth, Gemini, and Supabase Auth verification.

Required for full local testing:

- `DATABASE_URL`: use Supabase Session Pooler for shared testing, or SQLite for quick local-only tests.
- `ENCRYPTION_KEY`: strong random value used to encrypt Gmail refresh tokens.
- `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_JWKS_URL`: Supabase Auth verification settings.
- `SUPABASE_SECRET_KEY`: server-only admin key. Keep this out of frontend env files.
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`: Gmail OAuth settings.
- `GEMINI_API_KEY`, `GEMINI_MODEL`: AI triage settings.
- `REDIS_URL`: Redis connection used by Celery.
- `CELERY_TASK_ALWAYS_EAGER`: `false` when using Redis/worker, `true` only for simple local backend tests without Redis.

Generate a local encryption key with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Frontend variables

`apps/web/.env.local` controls browser-safe frontend settings.

Required:

- `NEXT_PUBLIC_API_BASE_URL`: local default is `http://localhost:8000`.
- `NEXT_PUBLIC_SUPABASE_URL`: public Supabase project URL.
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`: public Supabase browser key.

Never add backend-only secrets to the frontend env file.

## Google OAuth redirect URI

For local development, configure this redirect URI in Google Cloud Console:

```text
http://localhost:8000/v1/gmail/oauth/callback
```

For deployment, add the deployed API callback URL as an additional authorized redirect URI.

## Database migrations

New databases should be created through Alembic migrations:

```powershell
cd apps/api
alembic upgrade head
```

The app still supports local SQLite startup for development, but production and shared Supabase databases should use migrations explicitly.

## Environment separation

Use three separate environment profiles:

| Environment | Purpose | Required separation |
|---|---|---|
| Development | Local engineering and tests | Local `.env`, local SQLite only for quick testing, local Redis or Docker Redis |
| Staging | Production-like release validation | Separate Supabase project or isolated staging database, separate Redis, separate Google OAuth redirect, separate Pub/Sub topic and subscription |
| Production | Pilot and customer traffic | Production Supabase database, production Redis, production Google OAuth app/resources, production-only secret store |

Staging must not share Gmail Pub/Sub topics, subscriptions, OAuth credentials, database, Redis, or encryption keys with production.

## Startup validation

The API and worker validate production-like settings when `APP_ENV` is `staging` or `production`. Startup fails fast when required values are missing or unsafe values are present.

Required in staging and production:

- `DATABASE_URL`: Supabase/Postgres connection string. SQLite is rejected outside local development.
- `REDIS_URL`: worker broker/backend connection.
- `ENCRYPTION_KEY`: production-managed secret, not `dev-only-change-me`.
- `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY`.
- `SUPABASE_JWKS_URL` or `SUPABASE_JWT_SECRET`.
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`.
- `GOOGLE_CLOUD_PROJECT_ID`, `GOOGLE_PUBSUB_TOPIC`, `GOOGLE_PUBSUB_SUBSCRIPTION`.
- `PUBSUB_EXPECTED_AUDIENCE`, `PUBSUB_SERVICE_ACCOUNT_EMAIL`.
- `GEMINI_API_KEY`, `GEMINI_MODEL`.
- `FRONTEND_ORIGIN`, `API_CORS_ORIGINS`.
- `WORKER_CONCURRENCY`, `SYNC_FALLBACK_INTERVAL_MINUTES`, `WATCH_RENEWAL_SCHEDULE`.
- `RELEASE_VERSION`, `OPERATIONS_ALERT_OWNER`.

Forbidden in staging and production:

- `DEBUG=true`
- `AUTH_ALLOW_UNVERIFIED_JWT=true`
- `CELERY_TASK_ALWAYS_EAGER=true`
- `API_CORS_ORIGINS=*`
- SQLite `DATABASE_URL`
- Development encryption keys

M5 operations and observability settings:

- `SERVICE_NAME`: log service label, usually `api` or `worker`.
- `RELEASE_VERSION`: release identifier emitted in status responses and logs.
- `OPERATIONS_ALERT_OWNER`: owner label included on failed jobs.
- `OPERATIONS_INTERNAL_TOKEN`: optional token for internal system-wide operations endpoints.
- `OPERATIONS_RUNBOOK_BASE_URL`: optional base URL used to populate job runbook links.
- `OPERATIONS_FAILURE_ALERT_THRESHOLD`: repeated-failure threshold for alerting policy.

`ERROR_TRACKING_DSN` remains optional until an external error tracking provider is connected, but the app captures API and worker exception context in structured logs now.

## Migration validation

Every schema change must include an Alembic migration. CI validates migrations with:

```powershell
cd apps/api
alembic upgrade head
alembic downgrade base
alembic upgrade head
```

Production deployments should run:

```powershell
cd apps/api
alembic upgrade head
```

before starting the new API and worker release.

## Gmail Push Notification Foundation

M1 adds the backend foundation for Gmail push notifications and Gmail watch renewal.

Configured non-secret Google Cloud values for the current staging project:

- `GOOGLE_CLOUD_PROJECT_ID`: `customer-support-triage-501408`
- `GOOGLE_PUBSUB_TOPIC`: `projects/customer-support-triage-501408/topics/gmail-notifications`
- `GOOGLE_PUBSUB_SUBSCRIPTION`: `gmail-notifications-sub`
- `PUBSUB_EXPECTED_AUDIENCE`: `https://ai-customer-support-triage-response.onrender.com/v1/webhooks/google/gmail`
- `PUBSUB_SERVICE_ACCOUNT_EMAIL`: `pub-sub-push-invoker@customer-support-triage-501408.iam.gserviceaccount.com`

The Gmail API publisher principal must have `Pub/Sub Publisher` on the topic:

```text
gmail-api-push@system.gserviceaccount.com
```

The webhook endpoint is:

```text
POST https://ai-customer-support-triage-response.onrender.com/v1/webhooks/google/gmail
```

This milestone acknowledges authenticated Pub/Sub notifications and records a sync event. Gmail history processing and ticket ingestion from Pub/Sub notifications are intentionally left for M2.
