# AI Customer Support Triage

Monorepo for the MVP application.

## Apps

- `apps/web`: Next.js frontend with TypeScript.
- `apps/api`: FastAPI backend with Python.

## Local Development

Copy the environment templates:

```bash
cp .env.example .env
cp apps/web/.env.example apps/web/.env.local
cp apps/api/.env.example apps/api/.env
```

Install dependencies:

```bash
npm install
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run with Docker Compose:

```bash
docker compose up --build
```

Run locally without Docker:

```bash
npm run dev --workspace apps/web
cd apps/api
uvicorn app.main:app --reload
```

## Health Checks

- API: `GET http://localhost:8000/health`
- API status: `GET http://localhost:8000/v1/status`

