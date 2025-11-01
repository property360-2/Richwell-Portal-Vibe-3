# Repository Guidelines

## Project Structure & Module Organization
Core directories are `backend/`, `frontend/`, and `documentation/`. Settings live in `backend/config/`; each domain app (users, courses, enrollments, audit, archive) stays in its own folder with shared mixins in `backend/core/`. The React client lives under `frontend/src/atomic/` with screens in `frontend/src/pages/`. Update product briefs in `documentation/`, and maintain root infra files (`docker-compose.yml`, `.env.example`, CI configs) alongside code changes.

## Build, Test, and Development Commands
Run the stack with `docker compose up --build`. Apply migrations and seed data through `docker compose exec backend python manage.py migrate` and `docker compose exec backend python manage.py seed_demo`. Execute backend tests via `docker compose exec backend pytest` and frontend checks with `docker compose exec frontend npm test`. Standardize formatting by running `pre-commit run --all-files` before every push.

## Coding Style & Naming Conventions
Back-end code follows Black (88 columns, 4 spaces) and Ruff; add type hints on public APIs. Django modules use singular nouns, service helpers sit in `backend/core/services.py`, and database fields stay snake_case. React components use PascalCase filenames, hooks follow `useThing`, and styling tokens remain kebab-case. Treat archive awareness as default: filter for `archived=False` unless a restore feature is intentional.

## Testing Guidelines
Target 80% coverage on touched lines. Place unit and API tests beside each app in `backend/<app>/tests/` and run `pytest --cov=backend --cov-report=term-missing` for reporting. Frontend specs belong in `frontend/src/__tests__/` using React Testing Library; add snapshots only for atomic components and prefer behavioral assertions elsewhere. Refresh seed fixtures whenever serializers or permissions shift.

## Commit & Pull Request Guidelines
Existing history uses concise sentence-case summaries ("Add comprehensive repository guidelines, project structure, and development commands"). Follow the same voice, optionally prefixed with scope (`backend:`, `frontend:`), and wrap detail lines at 72 characters. Pull requests should describe intent, list verification steps, link issues, and flag migrations, seeds, or new environment variables. Include screenshots for UI work and state which roles were exercised during QA.

## Security & Configuration Tips
Copy `.env.example` when provisioning environments and document every new key there. Keep secrets in Docker overrides or orchestrator vaults; never commit live credentials. Lock down archive and audit endpoints with role checks, ensure JWT settings rotate refresh tokens, and validate CDN or S3 uploads with signed URLs before promotion.
