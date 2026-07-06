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