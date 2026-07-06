# AI Customer Support Triage

Monorepo for the MVP application.

## Apps

- `apps/web`: Next.js frontend with TypeScript.
- `apps/api`: FastAPI backend with Python.

## Local Development

Copy the environment templates:

```powershell
Copy-Item apps/api/.env.example apps/api/.env
Copy-Item apps/web/.env.example apps/web/.env.local
```

Install dependencies:

```powershell
npm install
cd apps/api
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Run with Docker Compose:

```powershell
docker compose up --build
```

Run locally without Docker:

```powershell
pnpm run dev:web
cd apps/api
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Database Migrations

New shared or production databases should use Alembic migrations:

```powershell
cd apps/api
alembic upgrade head
```

Local SQLite development still starts automatically, but Supabase/Postgres environments should be migrated explicitly.

## Health Checks

- API: `GET http://localhost:8000/health`
- API status: `GET http://localhost:8000/v1/status`

## Docs

- `docs/ENVIRONMENT.md`: local and production environment variables.
- `docs/DEPLOYMENT.md`: deployment layout, commands, and production checklist.