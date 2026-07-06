# Deployment Notes

This milestone prepares the project for deployment, but does not deploy it automatically.

## Recommended production layout

- Frontend: Vercel, running `pnpm run build:web` from the monorepo root.
- Backend API: Railway or Render using `apps/api/Dockerfile` or a Python service command.
- Worker: separate Railway or Render worker service using the same backend image and Celery command.
- Redis: managed Redis from Railway, Render, Upstash, or another provider.
- Database: Supabase Postgres using the Session Pooler connection string.
- Auth: Supabase Auth.
- Email: Google OAuth app with production callback URL.

## Backend deployment commands

Install dependencies:

```bash
pip install -e .
```

Run migrations before starting a new release:

```bash
alembic upgrade head
```

Run API:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Run worker:

```bash
celery -A app.worker.celery_app.celery_app worker --loglevel=info
```

## Docker local validation

From the monorepo root:

```powershell
docker compose up --build
```

Expected services:

- `web`: Next.js on `http://localhost:3000`
- `api`: FastAPI on `http://localhost:8000`
- `worker`: Celery worker processing Redis jobs
- `redis`: local Redis

## CI coverage

GitHub Actions now checks:

- backend linting with Ruff
- Alembic migration application against SQLite
- backend tests with Pytest
- frontend typecheck
- frontend production build
- Docker Compose config validation

## Production checklist

Before a real launch:

- Rotate any secrets that were pasted into chat or logs.
- Store `GOOGLE_CLIENT_SECRET`, `GEMINI_API_KEY`, `SUPABASE_SECRET_KEY`, and `ENCRYPTION_KEY` only in deployment secret stores.
- Use Supabase Postgres for `DATABASE_URL`; do not use SQLite in production.
- Confirm `GOOGLE_REDIRECT_URI` exactly matches the deployed API callback URL.
- Set `CELERY_TASK_ALWAYS_EAGER=false` and run a separate worker service.
- Restrict `API_CORS_ORIGINS` to the deployed frontend domain.
- Run `alembic upgrade head` before starting the deployed API and worker.