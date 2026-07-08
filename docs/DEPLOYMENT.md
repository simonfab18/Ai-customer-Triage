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

## Release control

Use pull requests for changes to `main`, require CI to pass, and tag deployable releases. Date-based tags are acceptable for the current project stage, for example:

```powershell
git tag release-2026-07-08.1
git push origin release-2026-07-08.1
```

A release candidate is ready for staging only after:

- Backend Ruff passes.
- Backend tests pass.
- Alembic upgrade, downgrade, and upgrade validation passes.
- Frontend lint, typecheck, and production build pass.
- Backend and frontend container images build.
- Docker Compose configuration validates.
- Staging environment variables are confirmed separate from production.

## Deployment order

1. Confirm the release tag or commit SHA.
2. Confirm staging or production secret-store values.
3. Build the frontend and backend images from the repository.
4. Run `alembic upgrade head` against the target database.
5. Deploy the API.
6. Deploy the worker.
7. Deploy the frontend.
8. Check `/health` and `/v1/status`.
9. Run a smoke test: sign in, load organizations, view Gmail status, list tickets.

## Rollback procedure

Frontend rollback:

1. Promote the previous known-good Vercel deployment.
2. Confirm `NEXT_PUBLIC_API_BASE_URL` still points at the intended API environment.
3. Smoke test login and the app shell.

API rollback:

1. Redeploy the previous known-good backend image or release tag.
2. Confirm the API starts with the current environment settings.
3. Check `/health` and `/v1/status`.
4. Review logs for startup validation failures.

Worker rollback:

1. Stop the current worker release.
2. Start the previous known-good worker image or release tag.
3. Confirm it uses the same Redis and database as the API environment.
4. Watch job logs for retry storms or repeated failures.

Database rollback:

1. Prefer forward fixes for non-destructive migrations.
2. If rollback is required, back up the target database first.
3. Run the specific Alembic downgrade only after confirming data-loss risk.
4. Redeploy API and worker versions compatible with the downgraded schema.

## Branch and ownership controls

- Protect `main` in the repository host.
- Require pull requests and passing CI before merge.
- Use `OWNERS.md` to identify reviewers for critical modules.
- Do not deploy directly from unreviewed local changes.

## Gmail Push Deployment Setup

Before validating M1 in staging:

1. Confirm the backend API is deployed at `https://ai-customer-support-triage-response.onrender.com`.
2. Confirm the Pub/Sub push endpoint is configured as `https://ai-customer-support-triage-response.onrender.com/v1/webhooks/google/gmail`.
3. Configure the push subscription to use OIDC authentication with `pub-sub-push-invoker@customer-support-triage-501408.iam.gserviceaccount.com`.
4. Set the push audience to the full webhook URL.
5. Confirm the Gmail publisher service account has `Pub/Sub Publisher` on `projects/customer-support-triage-501408/topics/gmail-notifications`.
6. Deploy the API and worker after running `alembic upgrade head`.
7. Connect or reconnect Gmail; the OAuth callback should register a Gmail watch and store the returned `historyId` and expiration.

M1 does not import Gmail history from notifications. A successful push notification should receive a fast `200` response and create a `gmail_sync_events` record for known active connections.
