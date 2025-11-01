# Richwell Portal Monorepo

This repository contains the backend and frontend applications for the Richwell academic portal.
Phase 0 establishes the foundational tooling, containerization, and health monitoring endpoints
referenced in the delivery roadmap.

## Repository layout

- `backend/` — Django project exposing `/healthz/` and ready for JWT auth work.
- `frontend/` — Vite + React shell prepared for future authentication flows.
- `documentation/` — Product briefs, schema drafts, and project phases.

## Getting started

```bash
cp .env.example .env
pip install -e backend[dev]
python backend/manage.py migrate
python backend/manage.py runserver
```

The backend health check is available at http://localhost:8000/healthz/.

For the frontend:

```bash
cd frontend
npm install
npm run dev
```

This launches the client shell at http://localhost:5173.

## Docker workflow

```bash
docker compose up --build
```

The compose stack provides PostgreSQL and runs the Django development server with auto-reload.
