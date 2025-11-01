# Repository Guidelines

## Project Structure & Module Organization
- `documentation/` hosts the strategic plans (`concept.md`, `phase.md`) and should be updated alongside any scope change.
- Backend services will live in `backend/` (Django + DRF). Core apps include `users/`, `students/`, `courses/`, `subjects/`, `sections/`, `enrollments/`, `grades/`, `terms/`, `archive/`, `audit/`, and shared utilities in `core/`.
- Frontend atomic components belong in `frontend/` with `components/`, `pages/`, and `styles/` sub-folders. Static assets stay in `frontend/public/` or Django `static/` depending on the chosen renderer.
- Mirror the module tree when adding tests: `backend/*/tests/` for Python suites, `frontend/__tests__/` for UI units, and `e2e/` for cross-layer scenarios.

## Build, Test, and Development Commands
- Create a virtual environment with `python -m venv .venv`, activate it, then install dependencies via `pip install -r requirements.txt`.
- Typical backend workflow: `python manage.py migrate`, `python manage.py runserver`, `python manage.py createsuperuser`, and `python manage.py seed_demo` for demo data.
- Run backend tests using `pytest` (preferred) or `python manage.py test`.
- For the frontend: `cd frontend && npm install`, then `npm run dev` for local development, `npm run test` for unit checks, and `npm run build` for production bundles.

## Coding Style & Naming Conventions
- Python code follows PEP 8 (4-space indent). Format with `black`, sort imports with `isort`, lint with `flake8`, and keep modules snake_case while models and serializers use PascalCase.
- DRF viewsets should expose plural resource names and group shared mixins in `core/`.
- JavaScript/TypeScript uses the project `eslint` + `prettier` presets. Components adopt PascalCase, hooks use camelCase with a `use` prefix, and test files end in `.test.tsx`.
- CSS or Tailwind utility stacks align with the design tokens documented in `documentation/concept.md`; prefer BEM-like class names for handcrafted styles.

## Testing Guidelines
- Target >=80% coverage on changed backend lines and always add regression cases for archive/restore and audit logging behaviours.
- Backend tests rely on `pytest`, `pytest-django`, and `factory_boy`; name files `test_<feature>.py` and structure fixtures in `conftest.py`.
- Frontend tests use Jest + Testing Library with emphasis on behaviour over snapshots; snapshot only atomic components.
- Playwright end-to-end suites in `e2e/` should exercise enrollment, grade encoding, and archive restore flows; regenerate artifacts when UI states move.

## Commit & Pull Request Guidelines
- Branch from `develop` using `feature/<short-scope>` or `hotfix/<issue-id>` and keep `main` release-only.
- Use Conventional Commits (`feat: add archive restore flow`, `fix: handle INC grade validation`) and squash incidental fixups before review.
- Pull requests must link to the tracking ticket, summarise intent, list test evidence, and add screenshots or recordings when UI changes occur.
- Complete the PR checklist: migrations generated, tests updated, security review logged, changelog touched, and no secrets committed.

## Security & Configuration Tips
- Store secrets in `.env` (excluded from version control) and document required keys in `.env.example`. Configure `SECRET_KEY`, database URLs, and CDN credentials via environment variables.
- Enforce DRF throttling and role-based permissions on new endpoints; never bypass archive filters without explicit restore intent.
- Ensure every mutation records an `AuditTrail` entry and that the no-delete policy is preserved through service-layer helpers.
